"""Definiciones de juego: juego abierto, balón parado y valores de resultado de StatsBomb.

REF1: contexto/framework.md, tabla "Objetos"; catálogos en contexto/api/events.md.
"""

from __future__ import annotations

import pandas as pd

# Juego abierto: todo menos córner, tiro libre y lateral (framework.md, "Juego abierto")
PATRONES_JUEGO_ABIERTO = frozenset(
    {"Regular Play", "From Counter", "From Keeper", "From Goal Kick", "From Kick Off", "Other"}
)
PATRONES_BALON_PARADO = frozenset({"From Corner", "From Free Kick", "From Throw In"})

# Recuperaciones (framework.md, "Altura de recuperación"); ids 4, 15, 16 de Interception.outcome
INTERCEPCION_GANADA = frozenset({"Won", "Success", "Success In Play"})
# Acciones defensivas del PPDA según la definición de StatsBomb (Team Match Stats): entrada, intercepción, falta
DUELO_ENTRADA = "Tackle"
# Pases que reanudan el juego (Pass.type): no cuentan como pases "permitidos" en el PPDA por tramo (framework.md, "PPDA")
PASES_REANUDACION = frozenset({"Throw-in", "Goal Kick", "Corner", "Free Kick", "Kick Off"})


def es_juego_abierto(eventos: pd.DataFrame) -> pd.Series:
    """True para eventos en juego abierto según su play_pattern."""
    return eventos["patron"].isin(PATRONES_JUEGO_ABIERTO)


def es_pase_completo(eventos: pd.DataFrame) -> pd.Series:
    """Pase sin outcome = pase completo (contexto/api/events.md)."""
    return (eventos["tipo"] == "Pass") & eventos["pase_resultado"].isna()


def es_recuperacion(eventos: pd.DataFrame) -> pd.Series:
    """Recuperación del balón: Ball Recovery exitosa o Interception ganada."""
    recuperacion = (eventos["tipo"] == "Ball Recovery") & ~eventos["recuperacion_fallida"]
    intercepcion = (eventos["tipo"] == "Interception") & eventos["intercepcion_resultado"].isin(INTERCEPCION_GANADA)
    return recuperacion | intercepcion
