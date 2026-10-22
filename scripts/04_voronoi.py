"""Calcula el control territorial (Voronoi) y su grafo para cada evento con 360, sin red.

Lee las tablas procesadas (scripts/03_procesar.py) de los partidos del equipo de
config/params.yaml y escribe una tabla por partido en outputs/voronoi/metricas/ (fuera de git).
Es incremental: los partidos ya calculados se saltan (usa --forzar para rehacerlos).
Con --figura MATCH_ID dibuja un ejemplo con la identidad en outputs/voronoi/.

Tarda unos 17 s por partido; --procesos reparte los partidos entre núcleos.

Cómo correrlo (PowerShell, desde la raíz del repo y con el entorno activado):
    python scripts/04_voronoi.py --procesos 4
    python scripts/04_voronoi.py --figura 4057783
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor

import matplotlib

matplotlib.use("Agg")
import pandas as pd
from tqdm import tqdm

from ojo.config import DIR_SALIDAS, params
from ojo.datos import almacen
from ojo.framework import juego
from ojo.framework import partidos as fp
from ojo.lentes import voronoi
from ojo.salidas.figuras import dibujar_voronoi

DIR_VORONOI = DIR_SALIDAS / "voronoi"
DIR_METRICAS = DIR_VORONOI / "metricas"
TERCIO_MEDIO = (40, 80)  # x del tercio medio, para elegir el ejemplo (tercios en params.yaml)


def calcular_partido(match_id: int) -> int:
    """Métricas de Voronoi de un partido; devuelve cuántos eventos se pudieron analizar."""
    ids = [match_id]
    tabla = voronoi.por_evento(almacen.cargar("eventos", ids), almacen.cargar("frames", ids),
                               almacen.cargar("frames_jugadores", ids))
    DIR_METRICAS.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(DIR_METRICAS / f"{match_id}.parquet", index=False)
    return len(tabla)


def partidos_del_equipo() -> list[int]:
    """Partidos válidos con 360 del equipo de params.yaml que ya tienen frames procesados."""
    p = params()
    tabla = fp.validos(almacen.cargar("partidos"), con_360=True)
    candidatos = fp.del_equipo(tabla, p["equipo"]["team_id"])["match_id"].astype(int)
    con_frames = set(almacen.consultar("SELECT DISTINCT match_id FROM frames")["match_id"].astype(int))
    return [m for m in candidatos if m in con_frames]


def figura_ejemplo(match_id: int) -> None:
    """Dibuja el pase completo del equipo en el tercio medio con más jugadores visibles."""
    ids = [match_id]
    eventos = almacen.cargar("eventos", ids)
    frames = almacen.cargar("frames", ids).set_index("event_uuid")
    jugadores = almacen.cargar("frames_jugadores", ids)
    team_id = params()["equipo"]["team_id"]
    tercio = params()["tercios"]
    pases = eventos[juego.es_pase_completo(eventos) & juego.es_juego_abierto(eventos)
                    & (eventos["equipo_id"] == team_id) & eventos["x"].between(tercio["defensivo_max_x"], tercio["final_min_x"])
                    & eventos["id"].isin(frames.index)]
    if pases.empty:
        print("Ese partido no tiene pases del equipo con frame 360 en el tercio medio.")
        return
    pases = pases.assign(n=pases["id"].map(frames["n_visibles"])).sort_values("n", ascending=False)
    for pase in pases.itertuples():
        resultado = voronoi.analizar_frame(voronoi.jugadores_de_frame(jugadores[jugadores["event_uuid"] == pase.id]),
                                           frames.loc[pase.id, "area_visible"])
        if resultado is not None:
            break
    else:
        print("Ningún frame de ese partido se pudo analizar.")
        return
    fig = dibujar_voronoi(
        resultado,
        titulo=f"Controla el {resultado.control:.0%} del espacio que se ve",
        subtitulo=(f"Pase del minuto {pase.minuto}  ·  {resultado.apoyos:.0f} compañeros cerca y "
                   f"{resultado.rivales_cerca:.0f} rivales encima  ·  línea blanca: dónde chocan los equipos"),
        destino_pase=(pase.fin_x, pase.fin_y),
    )
    DIR_VORONOI.mkdir(parents=True, exist_ok=True)
    salida = DIR_VORONOI / f"ejemplo_{match_id}.png"
    fig.savefig(salida, dpi=130, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.25)
    print(f"Figura: {salida.relative_to(DIR_SALIDAS.parent)} (datos reales: no se publica ni se sube a git)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--procesos", type=int, default=1, help="partidos en paralelo (por defecto 1)")
    parser.add_argument("--forzar", action="store_true", help="recalcula también los partidos ya hechos")
    parser.add_argument("--figura", type=int, metavar="MATCH_ID", help="solo dibuja un ejemplo de ese partido")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if args.figura:
        figura_ejemplo(args.figura)
        return 0
    try:
        ids = partidos_del_equipo()
    except FileNotFoundError as error:
        print(f"✗ {error}")
        return 1
    pendientes = [m for m in ids if args.forzar or not (DIR_METRICAS / f"{m}.parquet").exists()]
    print(f"Partidos del equipo con 360 procesados: {len(ids)}; por calcular: {len(pendientes)}")
    if args.procesos > 1:
        with ProcessPoolExecutor(max_workers=args.procesos) as pool:
            list(tqdm(pool.map(calcular_partido, pendientes), total=len(pendientes), unit="partido"))
    else:
        for m in tqdm(pendientes, unit="partido"):
            calcular_partido(m)
    if any(DIR_METRICAS.glob("*.parquet")):
        todo = pd.concat([pd.read_parquet(f) for f in DIR_METRICAS.glob("*.parquet")], ignore_index=True)
        print(f"Eventos analizados: {len(todo):,} en {todo['match_id'].nunique()} partidos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
