"""Balón parado ofensivo y defensivo: envíos, tiros, xG y zonas de remate, a dos bandas.

REF1: contexto/framework.md, filas "Balón parado" y "Envío a balón parado".
NOTA1: la jugada se toma por posesión: su tipo es el patrón del primer evento y su punto de saque es el del primer
evento del equipo que la tiene. Un lateral cuenta solo si se saca en zona de peligro.
NOTA2: las zonas de remate se leen en la orientación de quien tira (portería rival a la derecha), así que "dónde
concede" el equipo es dónde rematan sus rivales.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.config import params
from ojo.framework import contexto, juego

TIPOS = {"From Corner": "Córner", "From Free Kick": "Tiro libre", "From Throw In": "Lateral"}
ZONAS = ["Área chica", "Área: centro", "Área: costados", "Fuera del área"]
GOL = "Goal"
NOMBRES = {"envios_favor": "Envíos a favor", "xg_favor": "xG a favor", "xg_por_envio_favor": "xG por envío a favor",
           "goles_favor": "Goles a favor", "envios_contra": "Envíos en contra", "xg_contra": "xG en contra",
           "xg_por_envio_contra": "xG por envío en contra", "goles_contra": "Goles en contra"}


def envios(eventos: pd.DataFrame) -> pd.DataFrame:
    """Una fila por posesión de balón parado que amenaza: match_id, posesion, equipo_id, tipo, x0."""
    cfg = params()["balon_parado"]
    ev = eventos[eventos["periodo"] != contexto.PERIODO_PENALES].sort_values(["match_id", "indice"])
    primero = ev.drop_duplicates(["match_id", "posesion"])
    bp = primero[primero["patron"].isin(juego.PATRONES_BALON_PARADO)][["match_id", "posesion", "posesion_equipo_id", "patron"]]
    propios = (ev[ev["equipo_id"] == ev["posesion_equipo_id"]].drop_duplicates(["match_id", "posesion"])
               [["match_id", "posesion", "x"]])
    bp = bp.merge(propios, on=["match_id", "posesion"], how="left").rename(columns={"posesion_equipo_id": "equipo_id", "x": "x0"})
    bp["tipo"] = bp["patron"].map(TIPOS)
    amenaza = (bp["tipo"] != TIPOS["From Throw In"]) | (bp["x0"] >= cfg["lateral_peligro_min_x"])
    return bp[amenaza].drop(columns="patron").reset_index(drop=True)


def zona(x: pd.Series, y: pd.Series) -> pd.Series:
    """Zona de remate en la orientación de quien tira (ZONAS)."""
    c = params()["campo"]
    en_area = (x >= c["area_min_x"]) & y.between(*c["area_y"])
    centro = y.between(*c["area_chica_y"])
    chica = (x >= c["area_chica_min_x"]) & centro
    return pd.Series(np.select([chica, en_area & centro, en_area], ZONAS[:3], ZONAS[3]), index=x.index)


def tiros(eventos: pd.DataFrame, env: pd.DataFrame) -> pd.DataFrame:
    """Tiros dentro de los envíos de balón parado: match_id, equipo_id, tipo, xg, gol, zona."""
    claves = env[["match_id", "posesion", "equipo_id", "tipo"]].rename(columns={"tipo": "tipo_bp"})
    t = eventos[eventos["tipo"] == "Shot"].merge(claves, on=["match_id", "posesion", "equipo_id"])
    return pd.DataFrame({"match_id": t["match_id"], "equipo_id": t["equipo_id"], "tipo": t["tipo_bp"],
                         "xg": t["tiro_xg"].fillna(0.0), "gol": (t["tiro_resultado"] == GOL).astype(int),
                         "zona": zona(t["x"], t["y"])}).reset_index(drop=True)


def por_partido(env: pd.DataFrame, tir: pd.DataFrame, equipo_id: int, partidos: pd.Series) -> pd.DataFrame:
    """Por partido, a favor y en contra del equipo: envíos, tiros, xG, goles y xG por envío."""
    filas = {}
    for sufijo, propio in (("favor", True), ("contra", False)):
        e = env[(env["equipo_id"] == equipo_id) == propio]
        t = tir[(tir["equipo_id"] == equipo_id) == propio]
        filas[f"envios_{sufijo}"] = e.groupby("match_id").size()
        filas[f"tiros_{sufijo}"] = t.groupby("match_id").size()
        filas[f"xg_{sufijo}"] = t.groupby("match_id")["xg"].sum()
        filas[f"goles_{sufijo}"] = t.groupby("match_id")["gol"].sum()
    tabla = pd.DataFrame(filas).reindex(pd.Index(partidos.unique(), name="match_id")).fillna(0.0)
    for sufijo in ("favor", "contra"):
        envios_ = tabla[f"envios_{sufijo}"]
        tabla[f"xg_por_envio_{sufijo}"] = tabla[f"xg_{sufijo}"] / envios_.where(envios_ > 0)
    return tabla.reset_index()
