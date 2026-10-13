"""Recrea el Voronoi de una jugada real paso a paso en un HTML (evento, cámara, jugadores, celdas, recorte, control).

Por defecto elige, en el partido dado, el pase completo del equipo de params.yaml en juego abierto y
en el tercio medio con más jugadores visibles que se pueda analizar. Escribe
outputs/reportes/voronoi_paso_a_paso.html (fuera de git: lleva posiciones reales).

Cómo correrlo (PowerShell, desde la raíz del repo y con el entorno activado; antes 03):
    python scripts/06_paso_a_paso.py --partido 4057783
    python scripts/06_paso_a_paso.py --evento <uuid del evento>
"""

from __future__ import annotations

import argparse
import re
import sys

import pandas as pd

from ojo.config import DIR_SALIDAS, params
from ojo.datos import almacen
from ojo.framework import juego
from ojo.lentes import voronoi
from ojo.salidas import paso_a_paso

SALIDA = DIR_SALIDAS / "reportes" / "voronoi_paso_a_paso.html"


def candidatos(eventos: pd.DataFrame, frames: pd.DataFrame) -> pd.DataFrame:
    """Pases completos del equipo en juego abierto y en el tercio medio, de más a menos jugadores visibles."""
    team_id, tercio = params()["equipo"]["team_id"], params()["tercios"]
    filtro = (juego.es_pase_completo(eventos) & juego.es_juego_abierto(eventos) & (eventos["equipo_id"] == team_id)
              & eventos["x"].between(tercio["defensivo_max_x"], tercio["final_min_x"]) & eventos["id"].isin(frames.index))
    elegidos = eventos[filtro]
    return elegidos.assign(n=elegidos["id"].map(frames["n_visibles"])).sort_values("n", ascending=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--partido", type=int, metavar="MATCH_ID", help="elige la jugada dentro de ese partido")
    grupo.add_argument("--evento", metavar="UUID", help="usa exactamente ese evento")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if args.evento:
        if not re.fullmatch(r"[0-9a-fA-F-]{36}", args.evento):
            print("✗ --evento debe ser el uuid de un evento de StatsBomb.")
            return 1
        encontrado = almacen.consultar(f"SELECT match_id FROM eventos WHERE id = '{args.evento}'")
        if encontrado.empty:
            print("✗ Ese evento no está en los datos procesados.")
            return 1
        match_id = int(encontrado["match_id"].iloc[0])
    else:
        match_id = args.partido
    ids = [match_id]
    eventos = almacen.cargar("eventos", ids)
    frames = almacen.cargar("frames", ids).set_index("event_uuid")
    jugadores = almacen.cargar("frames_jugadores", ids)
    lista = eventos[eventos["id"] == args.evento] if args.evento else candidatos(eventos, frames)
    for e in lista.itertuples():
        todos = voronoi.jugadores_de_frame(jugadores[jugadores["event_uuid"] == e.id])
        if e.id in frames.index and voronoi.analizar_frame(todos, frames.loc[e.id, "area_visible"]) is not None:
            break
    else:
        print("✗ No hay una jugada analizable con esos filtros.")
        return 1

    equipo = params()["equipo"]["nombre"] if e.equipo_id == params()["equipo"]["team_id"] else "el rival"
    jugada = paso_a_paso.Jugada(tipo={"Pass": "Pase"}.get(e.tipo, e.tipo), minuto=int(e.minuto), segundo=int(e.segundo),
                                equipo=equipo, x=e.x, y=e.y,
                                fin_x=None if pd.isna(e.fin_x) else e.fin_x, fin_y=None if pd.isna(e.fin_y) else e.fin_y)
    pasos = paso_a_paso.pasos(jugada, todos, frames.loc[e.id, "area_visible"])
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(paso_a_paso.html(pasos, "El Voronoi paso a paso",
                                       "Cómo se mide el control del espacio en una jugada real"), encoding="utf-8")
    print(f"Reporte: {SALIDA.relative_to(DIR_SALIDAS.parent)} (datos reales: no se publica ni se sube a git)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
