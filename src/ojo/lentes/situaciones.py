"""Situaciones de juego por minuto y su resumen a dos bandas: la base de la matriz de situaciones.

REF1: contexto/framework.md, "Matriz de situaciones" (18 oct).
NOTA1: cada minuto cae en una sola situación, según el estado al empezar el minuto. Primero el número de jugadores
(con uno más o con uno menos), después el marcador. El empate se separa en primer y segundo tiempo porque se juega distinto.
NOTA2: la expulsión se detecta por la tarjeta (quiebres.TARJETAS_EXPULSION). La auditoría B2 advierte que algunas
rojas por mala conducta pueden ser de la banca: es una limitación conocida.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.framework import contexto
from ojo.framework.quiebres import TARJETAS_EXPULSION

SITUACIONES = {
    "uno_mas": "Con uno más", "uno_menos": "Con uno menos",
    "gana_2": "Ganando por 2 o más", "gana_1": "Ganando por 1",
    "empata_1t": "Empatando, primer tiempo", "empata_2t": "Empatando, segundo tiempo",
    "pierde_1": "Perdiendo por 1", "pierde_2": "Perdiendo por 2 o más",
}
SUMAS = ["xg_favor", "xg_contra", "tercio_favor", "tercio_contra", "pases_rival_zona", "acciones_def", "rec_n", "rec_x"]


def por_minuto(eventos: pd.DataFrame, equipo_id: int) -> pd.DataFrame:
    """Estado al empezar cada minuto: match_id, periodo, minuto, dif_goles y dif_jugadores (+ = ventaja propia)."""
    ev = eventos[eventos["periodo"] != contexto.PERIODO_PENALES].sort_values(["match_id", "indice"])
    # contexto.marcador acumula un solo partido: se aplica partido por partido
    m = pd.concat([contexto.marcador(g, equipo_id) for _, g in ev.groupby("match_id", sort=False)]).loc[ev.index]
    roja = ev["tarjeta"].isin(TARJETAS_EXPULSION)
    propia, rival = roja & (ev["equipo_id"] == equipo_id), roja & (ev["equipo_id"] != equipo_id)
    # expulsiones ANTES de cada evento (la del propio evento cuenta desde el siguiente)
    antes = lambda s: s.astype(int).groupby(ev["match_id"]).cumsum() - s.astype(int)  # noqa: E731
    tabla = pd.DataFrame({"match_id": ev["match_id"], "periodo": ev["periodo"], "minuto": ev["minuto"],
                          "dif_goles": m["goles_favor"] - m["goles_contra"],
                          "dif_jugadores": antes(rival) - antes(propia)})
    return tabla.drop_duplicates(["match_id", "periodo", "minuto"]).reset_index(drop=True)


def asignar(estado: pd.DataFrame) -> pd.Series:
    """Situación de cada minuto (claves de SITUACIONES)."""
    d, j, p = estado["dif_goles"], estado["dif_jugadores"], estado["periodo"]
    condiciones = [j > 0, j < 0, d >= 2, d == 1, (d == 0) & (p == 1), d == 0, d == -1]
    claves = list(SITUACIONES)
    return pd.Series(np.select(condiciones, claves[:-1], claves[-1]), index=estado.index)


def resumir(tabla: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    """Métricas de cada grupo a partir de sumas por minuto (SUMAS) y el índice por minuto de los dos equipos.

    xG por 90 a favor, en contra y diferencia; field tilt; PPDA propio; altura de recuperación; índice medio propio y del rival.
    """
    g = tabla.groupby(por)
    s, n = g[SUMAS].sum(), g.size()
    div = lambda a, b: a / b.where(b > 0)  # noqa: E731
    out = pd.DataFrame({
        "minutos": n, "partidos": g["match_id"].nunique(),
        "xg_favor_90": 90 * s["xg_favor"] / n, "xg_contra_90": 90 * s["xg_contra"] / n,
        "field_tilt": div(s["tercio_favor"], s["tercio_favor"] + s["tercio_contra"]),
        "ppda": div(s["pases_rival_zona"], s["acciones_def"]),
        "altura_recuperacion": div(s["rec_x"], s["rec_n"]),
        "indice": g["indice_favor"].mean(), "indice_rival": g["indice_rival"].mean(),
    })
    out["xg_dif_90"] = out["xg_favor_90"] - out["xg_contra_90"]
    return out.reset_index()
