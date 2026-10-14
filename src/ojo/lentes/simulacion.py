"""Monte Carlo explicativo: qué tan probable fue un resultado dado lo que cada equipo generó.

Cada tiro se simula como un intento independiente que entra con probabilidad igual a su xG; se
repite el partido muchas veces y se cuenta cuántas veces gana, empata o pierde cada equipo.
Responde "¿qué tan merecido fue?" o "¿qué tan probable era con lo generado hasta aquí?"; no predice
partidos futuros (la convocatoria pide simulación para explicar, no para predecir).

REF1: contexto/framework.md, "Validación, causalidad y decisión" (Monte Carlo explicativo).
OBS1: los tiros de una misma jugada (rebotes) no son independientes; tratarlos como tales infla
un poco la probabilidad de anotar. Es la simplificación estándar de este tipo de simulación.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import numpy as np

from ojo.config import params


@dataclass
class Simulacion:
    """Probabilidades del resultado y marcadores más frecuentes."""

    gana: float
    empata: float
    pierde: float
    goles_favor: float  # goles esperados (media de la simulación)
    goles_contra: float
    marcadores: list[tuple[str, float]]  # los más frecuentes: ("1-0", 0.23)


def simular(xg_favor: list[float] | np.ndarray, xg_contra: list[float] | np.ndarray, repeticiones: int | None = None,
            semilla: int | None = None, base: tuple[int, int] = (0, 0), top: int = 5) -> Simulacion:
    """Simula los tiros de cada lado; base suma goles ya marcados antes de esos tiros."""
    cfg = params()["simulacion"]
    repeticiones = repeticiones or cfg["repeticiones"]
    rng = np.random.default_rng(cfg["semilla"] if semilla is None else semilla)
    favor = base[0] + (rng.random((repeticiones, len(xg_favor))) < np.asarray(xg_favor, float)).sum(axis=1)
    contra = base[1] + (rng.random((repeticiones, len(xg_contra))) < np.asarray(xg_contra, float)).sum(axis=1)
    conteo = Counter(zip(favor.tolist(), contra.tolist()))
    marcadores = [(f"{a}-{b}", n / repeticiones) for (a, b), n in conteo.most_common(top)]
    return Simulacion(float((favor > contra).mean()), float((favor == contra).mean()), float((favor < contra).mean()),
                      float(favor.mean()), float(contra.mean()), marcadores)
