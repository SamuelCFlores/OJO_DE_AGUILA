"""Descarga completa con caché (la corre Samuel con sus credenciales).

Qué baja, por niveles (ids y temporadas salen de config/params.yaml):
    1. Competitions y Matches de cada temporada.
    2. Team Season Stats y Player Season Stats de cada temporada.
    3. Team Match Stats de todos los partidos válidos de la liga (línea base, Monte Carlo, relevos).
    4. Partidos válidos del equipo del caso: Events, 360 (si está disponible), Lineups y
       Player Match Stats.
    5. Solo con --liga-completa: Events, 360 y Lineups del resto de la liga.

Todo pasa por el cliente con caché: lo ya descargado no se vuelve a pedir, así que el script
se puede interrumpir (Ctrl+C) y retomar cuando sea. Errores puntuales no detienen la
descarga: quedan en logs/descarga_fallidas.txt y se reintentan en la siguiente corrida.

Cómo correrlo (PowerShell, desde la raíz del repo y con el entorno activado):
    python scripts/02_descarga.py --plan            # cuántas solicitudes faltan, sin red
    python scripts/02_descarga.py                   # descarga los niveles 1 a 4
    python scripts/02_descarga.py --liga-completa   # además el nivel 5 (varias horas)
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections import Counter
from dataclasses import dataclass, field

import pandas as pd
import requests
from tqdm import tqdm

from ojo.config import DIR_LOGS, params
from ojo.datos import crudo, tablas
from ojo.framework import partidos as fp
from ojo.ingesta.cliente import ClienteStatsBomb, ErrorAPI, ErrorAutenticacion
from ojo.ingesta.endpoints import PAUSA_S

SEGUNDOS_POR_SOLICITUD = PAUSA_S + 0.6  # pausa más tiempo de respuesta típico (estimado)


@dataclass(frozen=True)
class Tarea:
    """Una solicitud a la API: qué API, con qué parámetros y en qué nivel del plan."""

    nivel: int
    api: str
    parametros: tuple[tuple[str, int], ...] = field(default_factory=tuple)

    @property
    def kwargs(self) -> dict[str, int]:
        return dict(self.parametros)

    def pendiente(self) -> bool:
        return not crudo.existe(self.api, **self.kwargs)


def tareas_de_temporada(competition_id: int, season_ids: list[int]) -> list[Tarea]:
    """Niveles 1 y 2: catálogo y estadísticas por temporada."""
    lista = [Tarea(1, "competitions")]
    for s in season_ids:
        clave = (("competition_id", competition_id), ("season_id", s))
        lista += [Tarea(1, "matches", clave), Tarea(2, "team_season_stats", clave),
                  Tarea(2, "player_season_stats", clave)]
    return lista


def tareas_de_partidos(liga: pd.DataFrame, team_id: int, liga_completa: bool) -> list[Tarea]:
    """Niveles 3 a 5 a partir de la tabla de partidos válidos de la liga."""
    lista = []
    del_equipo = set(fp.del_equipo(liga, team_id)["match_id"])
    for _, p in liga.iterrows():
        mid = (("match_id", int(p["match_id"])),)
        lista.append(Tarea(3, "team_match_stats", mid))
        nivel = 4 if p["match_id"] in del_equipo else 5
        if nivel == 5 and not liga_completa:
            continue
        lista += [Tarea(nivel, "events", mid), Tarea(nivel, "lineups", mid)]
        if p["match_status_360"] == fp.DISPONIBLE:
            lista.append(Tarea(nivel, "frames_360", mid))
        if nivel == 4:
            lista.append(Tarea(nivel, "player_match_stats", mid))
    return lista


def liga_valida(competition_id: int, season_ids: list[int]) -> pd.DataFrame | None:
    """Partidos válidos de todas las temporadas, si Matches ya está en la caché."""
    tablas_temporada = []
    for s in season_ids:
        if not crudo.existe("matches", competition_id=competition_id, season_id=s):
            return None
        tablas_temporada.append(tablas.partidos(crudo.leer("matches", competition_id=competition_id, season_id=s)))
    return fp.validos(pd.concat(tablas_temporada, ignore_index=True))


def resumir(lista: list[Tarea], titulo: str) -> None:
    """Imprime cuántas solicitudes hay y cuántas faltan por nivel y API."""
    pendientes = [t for t in lista if t.pendiente()]
    print(f"\n{titulo}: {len(lista):,} solicitudes, {len(pendientes):,} pendientes "
          f"(~{len(pendientes) * SEGUNDOS_POR_SOLICITUD / 60:.0f} min)")
    conteo = Counter((t.nivel, t.api) for t in pendientes)
    for (nivel, api), n in sorted(conteo.items()):
        print(f"  nivel {nivel}  {api:<20} {n:>6,}")


def descargar(cliente: ClienteStatsBomb, lista: list[Tarea], fallidas: list[str]) -> None:
    """Descarga las tareas pendientes; un error puntual se registra y la descarga sigue."""
    pendientes = [t for t in lista if t.pendiente()]
    for tarea in tqdm(pendientes, desc="Descargando", unit="sol"):
        try:
            cliente.obtener(tarea.api, **tarea.kwargs)
        except ErrorAutenticacion:
            raise
        except (ErrorAPI, requests.RequestException) as error:
            logging.getLogger(__name__).warning("falló %s %s: %s", tarea.api, tarea.kwargs, error)
            fallidas.append(f"{tarea.api} {tarea.kwargs} — {type(error).__name__}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", action="store_true", help="solo muestra lo que falta, sin red")
    parser.add_argument("--liga-completa", action="store_true", help="incluye eventos y 360 de toda la liga")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    DIR_LOGS.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                        handlers=[logging.FileHandler(DIR_LOGS / "descarga.log", encoding="utf-8")])

    p = params()
    competition_id, season_ids = p["liga"]["competition_id"], p["liga"]["season_ids"]
    team_id = p["equipo"]["team_id"]
    fallidas: list[str] = []
    inicio = time.monotonic()

    try:
        cliente = None if args.plan else ClienteStatsBomb.desde_entorno()
        temporada = tareas_de_temporada(competition_id, season_ids)
        resumir(temporada, "Niveles 1-2 (temporadas)")
        if cliente:
            descargar(cliente, temporada, fallidas)

        liga = liga_valida(competition_id, season_ids)
        if liga is None:
            print("\nFaltan respuestas de Matches en la caché: corre sin --plan para conocer los partidos.")
            return 0
        partidos = tareas_de_partidos(liga, team_id, args.liga_completa)
        n_equipo = len(fp.del_equipo(liga, team_id))
        print(f"\nPartidos válidos: {len(liga):,} en la liga, {n_equipo} del equipo {team_id}")
        resumir(partidos, "Niveles 3-5 (partidos)")
        if cliente:
            descargar(cliente, partidos, fallidas)
    except ErrorAutenticacion as error:
        print(f"\n✗ {error}")
        return 1
    except KeyboardInterrupt:
        print("\nInterrumpido. Lo descargado quedó en la caché; vuelve a correr el script para seguir.")
        return 130

    if args.plan:
        return 0
    minutos = (time.monotonic() - inicio) / 60
    print(f"\nListo en {minutos:.1f} min. Solicitudes fallidas: {len(fallidas)}")
    if fallidas:
        (DIR_LOGS / "descarga_fallidas.txt").write_text("\n".join(fallidas), encoding="utf-8")
        print("  Detalle en logs/descarga_fallidas.txt; vuelve a correr el script para reintentarlas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
