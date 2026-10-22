"""Uso de jugadores: sustituciones (cuántas, cuándo, de qué tipo y de qué línea) y rotación por torneo.

REF1: contexto/framework.md, fila "Uso de jugadores". Catálogos en contexto/api/events.md (Substitution: outcome
102 Injury, 103 Tactical; posiciones 1–25).
NOTA1: el minuto es el del reloj de StatsBomb (el segundo tiempo arranca en 45), así que "antes del 60'" es de reloj.
"""

from __future__ import annotations

import pandas as pd

from ojo.config import params
from ojo.framework import contexto

LINEAS = {1: "Portero", **{i: "Defensa" for i in range(2, 9)}, **{i: "Medio" for i in range(9, 17)},
          **{i: "Ataque" for i in range(17, 26)}}
LESION = "Injury"
NOMBRES = {"cambios": "Cambios por partido", "cambios_tacticos": "Cambios tácticos", "cambios_lesion": "Cambios por lesión",
           "primer_cambio_tactico": "Minuto del primer cambio táctico", "tacticos_tempranos": "Cambios tácticos tempranos",
           "tacticos_defensa": "Cambios tácticos de defensas", "tacticos_medio": "Cambios tácticos de mediocampistas",
           "tacticos_ataque": "Cambios tácticos de delanteros"}


def sustituciones(eventos: pd.DataFrame, equipo_id: int) -> pd.DataFrame:
    """Una fila por cambio del equipo: match_id, minuto, lesion (bool) y linea de quien sale."""
    ev = eventos[(eventos["tipo"] == "Substitution") & (eventos["equipo_id"] == equipo_id)
                 & (eventos["periodo"] != contexto.PERIODO_PENALES)]
    return pd.DataFrame({"match_id": ev["match_id"], "minuto": ev["minuto"],
                         "lesion": ev["sustitucion_resultado"] == LESION,
                         "linea": ev["posicion_id"].map(LINEAS)}).reset_index(drop=True)


def por_partido(subs: pd.DataFrame, partidos: pd.Series, minuto_temprano: int | None = None) -> pd.DataFrame:
    """Por partido: cambios, tácticos, por lesión, minuto del primer cambio táctico y tácticos antes de minuto_temprano."""
    minuto_temprano = minuto_temprano or params()["jugadores"]["cambio_temprano_min"]
    tac = subs[~subs["lesion"]]
    tabla = pd.DataFrame({
        "cambios": subs.groupby("match_id").size(),
        "cambios_tacticos": tac.groupby("match_id").size(),
        "cambios_lesion": subs[subs["lesion"]].groupby("match_id").size(),
        "primer_cambio_tactico": tac.groupby("match_id")["minuto"].min(),
        "tacticos_tempranos": tac[tac["minuto"] < minuto_temprano].groupby("match_id").size(),
    }).reindex(pd.Index(partidos.unique(), name="match_id"))
    conteos = ["cambios", "cambios_tacticos", "cambios_lesion", "tacticos_tempranos"]
    tabla[conteos] = tabla[conteos].fillna(0)
    return tabla.reset_index()


def rotacion(eventos: pd.DataFrame, equipo_id: int, torneo_de: pd.Series) -> pd.DataFrame:
    """Por torneo: partidos, jugadores distintos con eventos y jugadores por partido (torneo_de: match_id → torneo)."""
    ev = eventos[(eventos["equipo_id"] == equipo_id) & eventos["jugador_id"].notna()]
    ev = ev.assign(torneo=ev["match_id"].map(torneo_de))
    por_partido_ = ev.groupby(["torneo", "match_id"])["jugador_id"].nunique()
    return pd.DataFrame({"partidos": por_partido_.groupby("torneo").size(),
                         "jugadores_distintos": ev.groupby("torneo")["jugador_id"].nunique(),
                         "jugadores_por_partido": por_partido_.groupby("torneo").mean()}).reset_index()
