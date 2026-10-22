"""Marcador de ojo para los jugadores del equipo en las figuras de cancha (el isotipo, simplificado).

Toma la forma del handoff de diseño (branding/exportados/app_maximalismo, assets/marcador-club.svg):
ceja, almendra con contorno, iris recortado por la almendra y pupila pentagonal, sin las líneas
Voronoi internas del logo. Los colores salen de los tokens de la marca (ojo.salidas.estilo).

NOTA1: las coordenadas del SVG van con y hacia abajo, igual que la cancha de StatsBomb en mplsoccer
(eje y invertido); si el eje no está invertido, la forma se refleja para no dibujarse de cabeza.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from matplotlib.patches import Polygon as PoligonoMpl
from shapely.geometry import Point, Polygon

from ojo.salidas.estilo import color

CENTRO_IRIS = (54.0, 54.0)  # la posición del jugador es el centro del iris
ANCHO_SVG = 102.0  # ancho del viewBox del marcador
CEJA = [(12, 19.6), (86, 30.8), (99, 46.7), (95.4, 50.6), (24.1, 29.2)]
PUPILA = [(49.3, 47.5), (58.7, 47.5), (61.6, 56.5), (54, 62), (46.4, 56.5)]
RADIO_IRIS = 24.0
TRAZO_ALMENDRA, TRAZO_CEJA, TRAZO_PUPILA = 6.0, 2.0, 3.0  # grosores del SVG (unidades del viewBox)
PUNTOS_ARCO = 24


def _arco(p1: tuple[float, float], p2: tuple[float, float], r: float, grande: bool, horario: bool) -> list[tuple[float, float]]:
    """Puntos de un arco circular de SVG (comando A con rx = ry y sin rotación), sin el punto inicial."""
    (x1, y1), (x2, y2) = p1, p2
    xp, yp = (x1 - x2) / 2, (y1 - y2) / 2
    r = max(r, math.hypot(xp, yp))
    signo = -1 if grande == horario else 1
    coef = signo * math.sqrt(max(0.0, (r * r - xp * xp - yp * yp) / (xp * xp + yp * yp)))
    cxp, cyp = coef * yp, -coef * xp
    cx, cy = cxp + (x1 + x2) / 2, cyp + (y1 + y2) / 2
    t1 = math.atan2((yp - cyp) / r, (xp - cxp) / r)
    dt = math.atan2((-yp - cyp) / r, (-xp - cxp) / r) - t1
    if horario and dt < 0:
        dt += 2 * math.pi
    elif not horario and dt > 0:
        dt -= 2 * math.pi
    return [(cx + r * math.cos(t1 + dt * k / PUNTOS_ARCO), cy + r * math.sin(t1 + dt * k / PUNTOS_ARCO))
            for k in range(1, PUNTOS_ARCO + 1)]


@lru_cache(maxsize=1)
def formas() -> dict[str, Polygon]:
    """Las piezas del marcador como polígonos de shapely, en unidades del viewBox del SVG."""
    # Almendra: M4 52 A50.3 0 1 → 24.1 29.2, L 95.4 50.6, A50.3 0 1 → 96 52, A51.8 0 1 → 4 52 Z
    puntos = [(4.0, 52.0)]
    puntos += _arco(puntos[-1], (24.1, 29.2), 50.3, False, True)
    puntos.append((95.4, 50.6))
    puntos += _arco(puntos[-1], (96.0, 52.0), 50.3, False, True)
    puntos += _arco(puntos[-1], (4.0, 52.0), 51.8, False, True)
    almendra = Polygon(puntos).buffer(0)
    iris = Point(CENTRO_IRIS).buffer(RADIO_IRIS, quad_segs=16).intersection(almendra)
    return {
        "ceja": Polygon(CEJA).buffer(TRAZO_CEJA / 2, join_style="round"),
        "contorno": almendra.buffer(TRAZO_ALMENDRA / 2, join_style="round"),
        "almendra": almendra,
        "iris": iris,
        "pupila": Polygon(PUPILA).buffer(TRAZO_PUPILA / 2, join_style="round").intersection(almendra),
    }


def dibujar(ax, x: float, y: float, ancho_yd: float, claro: str = "dorado", oscuro: str = "azul", zorder: int = 6) -> None:
    """Dibuja el ojo con el iris centrado en (x, y) y ancho_yd yardas de ancho total."""
    escala = ancho_yd / ANCHO_SVG
    signo = 1 if ax.yaxis_inverted() else -1
    for nombre, tono in (("ceja", claro), ("contorno", claro), ("almendra", oscuro), ("iris", claro), ("pupila", oscuro)):
        geometria = formas()[nombre]
        for parte in getattr(geometria, "geoms", [geometria]):
            if parte.is_empty or parte.geom_type != "Polygon":
                continue
            coords = np.asarray(parte.exterior.coords)
            xs = x + (coords[:, 0] - CENTRO_IRIS[0]) * escala
            ys = y + signo * (coords[:, 1] - CENTRO_IRIS[1]) * escala
            ax.add_patch(PoligonoMpl(np.column_stack([xs, ys]), closed=True, facecolor=color(tono), edgecolor="none",
                                     zorder=zorder))
