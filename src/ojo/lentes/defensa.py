"""Presión y defensa por minuto, tramo o partido: PPDA y altura de recuperación, a dos bandas.

REF1: contexto/framework.md, filas "PPDA" y "Altura de recuperación" de la tabla de objetos.
NOTA1: como el panel, se guardan sumas aditivas por minuto y equipo; un tramo o un partido se arma sumando minutos.
NOTA2: orientación de StatsBomb: cada evento viene en la perspectiva de quien lo ejecuta (x = 0 en su portería).
Los pases del rival dentro de su 60 % defensivo son x < presion.ppda_zona_max_x en SU orientación; las acciones
defensivas propias en esa misma zona son x ≥ campo.largo − ppda_zona_max_x en la orientación propia.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.config import params
from ojo.framework import contexto, juego

CLAVES = ["match_id", "periodo", "minuto", "equipo_id"]
SUMAS = ["pases_zona_propia", "acciones_def_zona", "recuperaciones_n", "recuperaciones_x_suma"]
ACCION_DEFENSIVA = "Foul Committed", "Interception"  # más las entradas (Duel de tipo Tackle)


def piezas_por_minuto(eventos: pd.DataFrame) -> pd.DataFrame:
    """Sumas por minuto y equipo: pases en su 60 % defensivo, acciones defensivas en el 60 % del rival y recuperaciones.

    Los pases que reanudan el juego (laterales, saques de meta, tiros libres, córners, saques de centro) no cuentan:
    es la variante que mejor sigue a team_match_ppda al agregarla al partido (framework.md, "PPDA").
    """
    cfg = params()
    zona = cfg["presion"]["ppda_zona_max_x"]
    largo = cfg["campo"]["largo"]
    ev = eventos[eventos["periodo"] != contexto.PERIODO_PENALES]
    pase = (ev["tipo"] == "Pass") & ~ev["pase_tipo"].isin(juego.PASES_REANUDACION)
    defensiva = ev["tipo"].isin(ACCION_DEFENSIVA) | ((ev["tipo"] == "Duel") & (ev["duelo_tipo"] == juego.DUELO_ENTRADA))
    recupera = juego.es_recuperacion(ev) & juego.es_juego_abierto(ev)
    piezas = pd.DataFrame({
        "pases_zona_propia": pase & (ev["x"] < zona),
        "acciones_def_zona": defensiva & (ev["x"] >= largo - zona),
        "recuperaciones_n": recupera,
        "recuperaciones_x_suma": ev["x"].where(recupera, 0.0),
    }, index=ev.index).astype(float).fillna(0.0)
    return pd.concat([ev[CLAVES], piezas], axis=1).groupby(CLAVES).sum().reset_index()


def con_tramo(piezas: pd.DataFrame, minutos_tramo: int | None = None) -> pd.DataFrame:
    """Agrega la columna tramo (0, 1, 2… dentro de cada periodo; el añadido queda en un tramo propio)."""
    t = minutos_tramo or params()["tramos_min"]
    p = piezas.copy()
    inicio, fin = p["periodo"].map(contexto.INICIO_PERIODO), p["periodo"].map(contexto.FIN_PERIODO)
    p["tramo"] = ((np.minimum(p["minuto"], fin) - inicio) // t).astype(int)
    return p


def metricas(piezas: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    """PPDA y altura de recuperación de cada (por…, equipo_id), con el otro equipo del mismo partido como rival.

    por: claves de agregación sin equipo_id, por ejemplo ["match_id"] (partido) o ["match_id", "periodo", "tramo"].
    PPDA = pases del rival en su 60 % defensivo / acciones defensivas propias en esa zona (más bajo = presiona más).
    """
    s = piezas.groupby([*por, "equipo_id"])[SUMAS].sum()
    total = s.groupby(level=por).transform("sum")
    pases_rival = total["pases_zona_propia"] - s["pases_zona_propia"]
    tabla = pd.DataFrame({
        "ppda": pases_rival / s["acciones_def_zona"].where(s["acciones_def_zona"] > 0),
        "altura_recuperacion": s["recuperaciones_x_suma"] / s["recuperaciones_n"].where(s["recuperaciones_n"] > 0),
        "recuperaciones": s["recuperaciones_n"],
    })
    return tabla.reset_index()
