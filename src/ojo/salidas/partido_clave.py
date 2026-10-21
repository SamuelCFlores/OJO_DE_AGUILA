"""Partido clave de cada rival en El partido: una regla fija, escrita antes de mirar los partidos (21 oct, chamuel).

1. Si hubo liguilla contra ese rival con el entrenador nuevo: la fase más avanzada (final, semifinal, cuartos,
   repechaje) y, dentro de esa fase, el partido de vuelta (el más reciente).
2. Si no hubo: el partido de fase regular con el momento clave de más peso. Cada tipo presente suma su peso
   (params.yaml, partido_clave.peso_momento: expulsión, gol en contra, cambio de sistema propio); en empate, el más reciente.
Dentro del partido se resalta el primer momento del tipo con más prioridad (partido_clave.prioridad_momento).

Incluye el torneo reservado: ya se abrió una vez para validar, y aquí solo se muestra un partido, no se ajusta nada.
REF1: CAMBIOS/C10_2110.md, "Regla del partido por rival".
"""

from __future__ import annotations

import pandas as pd

from ojo.config import params

FASES = {"Final": 4, "Finals": 4, "Semi-finals": 3, "Semi-Finals": 3, "Quarter-finals": 2, "Play-offs": 1}  # etapas de Matches


def fase(etapa: str | None) -> int:
    """"Clausura - Final" → 4, "Semi-finals" → 3, "Quarter-finals" → 2, "Play-offs - Semi-Finals" (repechaje) → 1, regular → 0."""
    partes = [p.strip() for p in str(etapa or "").split(" - ")]
    if "Play-offs" in partes:
        return FASES["Play-offs"]
    return max((FASES.get(p, 0) for p in partes), default=0)


def peso(tipos: set[str]) -> int:
    """Peso de un partido de fase regular: suma del peso de cada tipo de momento clave presente."""
    pesos = params()["partido_clave"]["peso_momento"]
    return (pesos["expulsion"] * any(t.startswith("expulsion") for t in tipos)
            + pesos["gol_contra"] * ("gol_contra" in tipos)
            + pesos["cambio_sistema_propio"] * ("cambio_sistema_propio" in tipos))


def elegir_partido(partidos: pd.DataFrame, tipos_por_partido: dict[int, set[str]]) -> int:
    """match_id del partido clave entre los partidos contra un rival (columnas match_id, etapa y fecha)."""
    if partidos.empty:
        raise ValueError("No hay partidos contra ese rival.")
    t = partidos.assign(fase=partidos["etapa"].map(fase),
                        peso=partidos["match_id"].map(lambda m: peso(tipos_por_partido.get(int(m), set()))))
    orden = ["fase", "fecha"] if t["fase"].max() > 0 else ["peso", "fecha"]
    return int(t.sort_values(orden, ascending=False).iloc[0]["match_id"])


def elegir_momento(quiebres: pd.DataFrame) -> pd.Series | None:
    """El momento clave que se resalta: el primero (por orden de eventos) del tipo con más prioridad."""
    for tipo in params()["partido_clave"]["prioridad_momento"]:
        del_tipo = quiebres[quiebres["tipo"] == tipo]
        if not del_tipo.empty:
            return del_tipo.sort_values("indice").iloc[0]
    return None


def razon(partidos: pd.DataFrame, elegido: int) -> str:
    """Por qué se eligió ese partido, en palabras para la página."""
    etapa = partidos.loc[partidos["match_id"] == elegido, "etapa"].iloc[0]
    if fase(etapa) > 0:
        return "la liguilla más avanzada contra este rival (el partido de vuelta)"
    return "sin liguilla contra este rival: el partido con el momento clave de más peso (expulsión, gol en contra o cambio de sistema)"
