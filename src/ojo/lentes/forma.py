"""Forma del bloque de cada equipo en cada frame 360: altura, ancho, largo y compactación.

REF1: contexto/framework.md, "Lectura del partido por puntos de quiebre" (bloque de estructura).
NOTA1: el 360 viene en la perspectiva del actor; los jugadores del otro equipo se reflejan
(120 − x, 80 − y) para que cada equipo ataque hacia x = 120.
OBS1: solo se ven los jugadores dentro de la toma (área visible media ≈ 27 % de la cancha), así que
la forma es la de los visibles; por eso se compara dentro del mismo partido y no entre partidos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import shapely

from ojo.config import params

METRICAS = ("altura", "ancho", "largo", "compactacion")


def por_frame(frames_jugadores: pd.DataFrame, eventos: pd.DataFrame, min_jugadores: int | None = None) -> pd.DataFrame:
    """Forma de cada equipo en cada frame: una fila por (evento, equipo) con sus métricas.

    Columnas: id (del evento), match_id, equipo_id, con_balon (el equipo tiene la posesión),
    n (jugadores de campo visibles), altura (x media), ancho (rango de y), largo (rango de x) y
    compactacion (área de la envolvente convexa entre n). Sin porteros. Se descartan los
    equipos con menos de min_jugadores visibles en ese frame.
    """
    min_jugadores = min_jugadores or params()["forma"]["min_jugadores_equipo"]
    campo = params()["campo"]
    info = eventos[["id", "match_id", "equipo_id", "posesion_equipo_id"]].rename(
        columns={"id": "event_uuid", "equipo_id": "actor_equipo_id"})
    # Con dos equipos por partido, el otro equipo es (suma de ids − actor).
    suma_ids = eventos.groupby("match_id")["equipo_id"].agg(lambda s: s.dropna().unique().sum())
    j = frames_jugadores[~frames_jugadores["portero"]].merge(info, on=["event_uuid", "match_id"])
    if j.empty:
        return pd.DataFrame(columns=["id", "match_id", "equipo_id", "con_balon", "n", *METRICAS])
    otro = j["match_id"].map(suma_ids) - j["actor_equipo_id"]
    j["equipo_id"] = np.where(j["companero"], j["actor_equipo_id"], otro)
    j.loc[~j["companero"], "x"] = campo["largo"] - j.loc[~j["companero"], "x"]
    j.loc[~j["companero"], "y"] = campo["ancho"] - j.loc[~j["companero"], "y"]

    claves = ["event_uuid", "match_id", "equipo_id"]
    j = j.sort_values(claves).reset_index(drop=True)
    grupos = j.groupby(claves, sort=False)
    tabla = grupos.agg(n=("x", "size"), altura=("x", "mean"), x_min=("x", "min"), x_max=("x", "max"),
                       y_min=("y", "min"), y_max=("y", "max"), posesion=("posesion_equipo_id", "first")).reset_index()
    # Envolvente convexa vectorizada: un multipunto por grupo (las filas ya están ordenadas por grupo).
    puntos = shapely.multipoints(j[["x", "y"]].to_numpy(), indices=grupos.ngroup().to_numpy())
    tabla["compactacion"] = shapely.area(shapely.convex_hull(puntos)) / tabla["n"]
    tabla["ancho"] = tabla["y_max"] - tabla["y_min"]
    tabla["largo"] = tabla["x_max"] - tabla["x_min"]
    tabla["con_balon"] = tabla["posesion"] == tabla["equipo_id"]
    tabla = tabla[tabla["n"] >= min_jugadores].rename(columns={"event_uuid": "id"})
    return tabla[["id", "match_id", "equipo_id", "con_balon", "n", *METRICAS]].reset_index(drop=True)
