"""Almacén en parquet: convierte la caché cruda en tablas y las consulta con DuckDB.

Estructura en data/processed/ (fuera de git):
    partidos/{competition_id}_{season_id}.parquet
    eventos/{match_id}.parquet
    frames/{match_id}.parquet            área visible de cada frame 360
    frames_jugadores/{match_id}.parquet  jugadores visibles de cada frame
    formaciones/{match_id}.parquet
    estadisticas_equipo/{match_id}.parquet

Un archivo por partido permite procesar de forma incremental: lo ya convertido se salta.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import duckdb
import pandas as pd

from ojo.config import DIR_PROCESADO, DIR_RAW
from ojo.datos import crudo, tablas

TABLAS_PARTIDO = ("eventos", "frames", "frames_jugadores", "formaciones", "estadisticas_equipo")
TABLAS = ("partidos",) + TABLAS_PARTIDO


def _escribir(tabla: pd.DataFrame, ruta: Path) -> None:
    """Escribe un parquet de forma atómica."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(ruta.name + ".tmp")
    tabla.to_parquet(temporal, index=False)
    temporal.replace(ruta)


def procesar_temporada(competition_id: int, season_id: int, dir_raw: Path = DIR_RAW,
                       dir_procesado: Path = DIR_PROCESADO) -> Path:
    """Convierte Matches de una temporada en partidos/{c}_{s}.parquet (siempre se rehace: es chico)."""
    tabla = tablas.partidos(crudo.leer("matches", dir_raw=dir_raw, competition_id=competition_id, season_id=season_id))
    ruta = dir_procesado / "partidos" / f"{competition_id}_{season_id}.parquet"
    _escribir(tabla, ruta)
    return ruta


def procesar_partido(match_id: int, forzar: bool | Iterable[str] = False, dir_raw: Path = DIR_RAW,
                     dir_procesado: Path = DIR_PROCESADO) -> list[str]:
    """Convierte las APIs en caché de un partido a parquet; devuelve las tablas escritas.

    forzar=True rehace todas las tablas; una lista de nombres rehace solo esas (p. ej. ["eventos"]).
    """
    rehacer = set(TABLAS_PARTIDO) if forzar is True else set(forzar or ())
    escritas = []

    def destino(nombre: str) -> Path:
        return dir_procesado / nombre / f"{match_id}.parquet"

    def hacer(nombre: str) -> bool:
        return nombre in rehacer or not destino(nombre).exists()

    if hacer("eventos") and crudo.existe("events", dir_raw=dir_raw, match_id=match_id):
        _escribir(tablas.eventos(crudo.leer("events", dir_raw=dir_raw, match_id=match_id), match_id), destino("eventos"))
        escritas.append("eventos")
    if (hacer("frames") or hacer("frames_jugadores")) and crudo.existe("frames_360", dir_raw=dir_raw, match_id=match_id):
        frames, jugadores = tablas.frames_360(crudo.leer("frames_360", dir_raw=dir_raw, match_id=match_id), match_id)
        _escribir(frames, destino("frames"))
        _escribir(jugadores, destino("frames_jugadores"))
        escritas += ["frames", "frames_jugadores"]
    if hacer("formaciones") and crudo.existe("lineups", dir_raw=dir_raw, match_id=match_id):
        _escribir(tablas.formaciones(crudo.leer("lineups", dir_raw=dir_raw, match_id=match_id), match_id),
                  destino("formaciones"))
        escritas.append("formaciones")
    if hacer("estadisticas_equipo") and crudo.existe("team_match_stats", dir_raw=dir_raw, match_id=match_id):
        _escribir(tablas.estadisticas_equipo(crudo.leer("team_match_stats", dir_raw=dir_raw, match_id=match_id)),
                  destino("estadisticas_equipo"))
        escritas.append("estadisticas_equipo")
    return escritas


def _patron(tabla: str, dir_procesado: Path) -> str:
    if tabla not in TABLAS:
        raise ValueError(f"Tabla desconocida: {tabla}. Opciones: {', '.join(TABLAS)}")
    carpeta = dir_procesado / tabla
    if not any(carpeta.glob("*.parquet")):
        raise FileNotFoundError(f"No hay datos procesados de {tabla}. Corre scripts/03_procesar.py.")
    return (carpeta / "*.parquet").as_posix()


def cargar(tabla: str, match_ids: Iterable[int] | None = None, columnas: Iterable[str] | None = None,
           dir_procesado: Path = DIR_PROCESADO) -> pd.DataFrame:
    """Carga una tabla procesada, opcionalmente solo algunos partidos y columnas."""
    patron = _patron(tabla, dir_procesado)
    seleccion = ", ".join(f'"{c}"' for c in columnas) if columnas else "*"
    sql = f"SELECT {seleccion} FROM read_parquet('{patron}', union_by_name = true)"
    parametros: list = []
    if match_ids is not None:
        ids = [int(m) for m in match_ids]
        if not ids:
            return cargar(tabla, columnas=columnas, dir_procesado=dir_procesado).head(0)
        sql += f" WHERE match_id IN ({', '.join('?' for _ in ids)})"
        parametros = ids
    with duckdb.connect() as con:
        return con.execute(sql, parametros).df()


def consultar(sql: str, dir_procesado: Path = DIR_PROCESADO) -> pd.DataFrame:
    """SQL libre sobre las tablas procesadas; cada tabla existente queda como vista con su nombre."""
    with duckdb.connect() as con:
        for tabla in TABLAS:
            if any((dir_procesado / tabla).glob("*.parquet")):
                patron = (dir_procesado / tabla / "*.parquet").as_posix()
                con.execute(f"CREATE VIEW {tabla} AS SELECT * FROM read_parquet('{patron}', union_by_name = true)")
        return con.execute(sql).df()
