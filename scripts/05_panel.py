"""Arma el panel por minuto a dos bandas y las aristas de la red de pases de cada partido, sin red.

Lee las tablas procesadas (03) y las métricas de Voronoi (04) de los partidos del equipo de
config/params.yaml y escribe, por partido (fuera de git):
    outputs/panel/minuto/{match_id}.parquet    sumas por minuto y equipo (ojo.lentes.minuto)
    outputs/panel/aristas/{match_id}.parquet   pases entre posiciones por minuto (ojo.lentes.redes)
    outputs/panel/forma/{match_id}.parquet     forma de cada equipo en cada frame (ojo.lentes.forma)
Es incremental: los partidos ya hechos se saltan (usa --forzar para rehacerlos).

Cómo correrlo (PowerShell, desde la raíz del repo y con el entorno activado; antes 03 y 04):
    python scripts/05_panel.py --procesos 4
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
from tqdm import tqdm

from ojo.config import DIR_SALIDAS, params
from ojo.datos import almacen
from ojo.framework import partidos as fp
from ojo.lentes import forma, minuto, redes

DIR_PANEL = minuto.DIR_PANEL
DIR_VORONOI = DIR_SALIDAS / "voronoi" / "metricas"


def procesar(match_id: int) -> int:
    """Panel, aristas y forma de un partido; devuelve las filas del panel."""
    team_id = params()["equipo"]["team_id"]
    ids = [match_id]
    eventos = almacen.cargar("eventos", ids)
    archivo_voronoi = DIR_VORONOI / f"{match_id}.parquet"
    vor = pd.read_parquet(archivo_voronoi) if archivo_voronoi.exists() else None
    try:
        jugadores = almacen.cargar("frames_jugadores", ids)
    except FileNotFoundError:
        jugadores = pd.DataFrame()
    tabla_forma = forma.por_frame(jugadores, eventos) if not jugadores.empty else None
    panel = minuto.panel_partido(eventos, team_id, vor, tabla_forma)
    aristas = redes.aristas_por_minuto(eventos)
    aristas["lado"] = (aristas["equipo_id"] == team_id).map({True: minuto.PROPIO, False: minuto.RIVAL})
    for nombre, tabla in zip(minuto.SALIDAS, (panel, aristas, tabla_forma)):
        if tabla is not None:
            (DIR_PANEL / nombre).mkdir(parents=True, exist_ok=True)
            tabla.to_parquet(DIR_PANEL / nombre / f"{match_id}.parquet", index=False)
    return len(panel)


def partidos_del_equipo() -> list[int]:
    """Partidos válidos del equipo de params.yaml que ya tienen eventos procesados."""
    tabla = fp.validos(almacen.cargar("partidos"))
    candidatos = fp.del_equipo(tabla, params()["equipo"]["team_id"])["match_id"].astype(int)
    con_eventos = set(almacen.consultar("SELECT DISTINCT match_id FROM eventos")["match_id"].astype(int))
    return [m for m in candidatos if m in con_eventos]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--procesos", type=int, default=1, help="partidos en paralelo (por defecto 1)")
    parser.add_argument("--forzar", action="store_true", help="rehace también los partidos ya hechos")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        ids = partidos_del_equipo()
    except FileNotFoundError as error:
        print(f"✗ {error}")
        return 1
    pendientes = [m for m in ids if args.forzar or not (DIR_PANEL / "minuto" / f"{m}.parquet").exists()]
    print(f"Partidos del equipo con eventos: {len(ids)}; por armar: {len(pendientes)}")
    if args.procesos > 1:
        with ProcessPoolExecutor(max_workers=args.procesos) as pool:
            list(tqdm(pool.map(procesar, pendientes), total=len(pendientes), unit="partido"))
    else:
        for m in tqdm(pendientes, unit="partido"):
            procesar(m)
    panel = minuto.cargar_panel("minuto")
    print(f"Panel: {len(panel):,} filas (minuto × equipo) de {panel['match_id'].nunique()} partidos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
