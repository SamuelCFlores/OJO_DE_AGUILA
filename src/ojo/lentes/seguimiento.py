"""Seguimiento estimado de jugadores entre fotos 360 consecutivas, para animar el Voronoi.

El 360 no identifica a los jugadores de una foto a otra (solo marca al que ejecuta el evento). Para
animar se estima la correspondencia: en cada equipo se empareja a cada jugador con el de la foto
siguiente que minimiza el desplazamiento total (asignación de costo mínimo), y solo se aceptan
parejas físicamente posibles: distancia ≤ velocidad_max × tiempo + tolerancia (ruido de la foto).
Los que no se emparejan entran o salen de cámara.

REF1: contexto/framework.md, "Animación del Voronoi (seguimiento estimado)"; umbrales en params.yaml (animacion).
OBS1: es una estimación para dibujar, no un dato de StatsBomb: no se usa para ninguna métrica.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from ojo.config import params


def emparejar(a: list[tuple[float, float, bool]], b: list[tuple[float, float, bool]], dt: float,
              cfg: dict | None = None) -> list[tuple[int, int]]:
    """Parejas (i de a, j de b) del mismo equipo con desplazamiento posible en dt segundos.

    a, b: jugadores como (x, y, propio).
    """
    cfg = cfg or params()["animacion"]
    limite = cfg["velocidad_max_yd_s"] * max(dt, 0.0) + cfg["tolerancia_yd"]
    parejas = []
    for equipo in (True, False):
        ia = [i for i, j in enumerate(a) if bool(j[2]) == equipo]
        ib = [i for i, j in enumerate(b) if bool(j[2]) == equipo]
        if not ia or not ib:
            continue
        pa = np.array([a[i][:2] for i in ia], dtype=float)
        pb = np.array([b[i][:2] for i in ib], dtype=float)
        costo = np.linalg.norm(pa[:, None, :] - pb[None, :, :], axis=2)
        filas, columnas = linear_sum_assignment(costo)
        parejas += [(ia[f], ib[c]) for f, c in zip(filas, columnas) if costo[f, c] <= limite]
    return sorted(parejas)


def pistas(fotos: list[list[tuple[float, float, bool]]], tiempos: list[float], cfg: dict | None = None) -> list[list[int]]:
    """Identificador de pista de cada jugador en cada foto: el mismo número = el mismo jugador estimado."""
    if not fotos:
        return []
    siguiente = len(fotos[0])
    ids = [list(range(siguiente))]
    for k in range(1, len(fotos)):
        actual = [-1] * len(fotos[k])
        for i, j in emparejar(fotos[k - 1], fotos[k], tiempos[k] - tiempos[k - 1], cfg):
            actual[j] = ids[k - 1][i]
        for j, v in enumerate(actual):
            if v == -1:
                actual[j], siguiente = siguiente, siguiente + 1
        ids.append(actual)
    return ids
