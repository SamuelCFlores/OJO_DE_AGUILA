"""Largo de los pases por partido: la medida del principio "sale jugando corto".

REF1: notebooks/03_barrido_estilo.ipynb, celda 5 (misma definición; ahí se prueba con los 4 filtros).
NOTA1: pases del equipo en juego abierto (sin reanudaciones, `juego.es_juego_abierto`); el largo es la distancia en
yardas de StatsBomb entre el inicio y el final del pase. La página lo muestra en metros (`campo.yarda_m`).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.framework import juego

COLUMNAS = ["match_id", "equipo_id", "tipo", "patron", "x", "y", "fin_x", "fin_y"]


def largo_por_partido(eventos: pd.DataFrame, equipo_id: int) -> pd.Series:
    """Largo medio (yardas) de los pases en juego abierto del equipo, uno por match_id."""
    pases = eventos[(eventos["equipo_id"] == equipo_id) & (eventos["tipo"] == "Pass") & juego.es_juego_abierto(eventos)]
    largo = np.hypot(pases["fin_x"] - pases["x"], pases["fin_y"] - pases["y"])
    return largo.groupby(pases["match_id"]).mean().rename("largo_pase")
