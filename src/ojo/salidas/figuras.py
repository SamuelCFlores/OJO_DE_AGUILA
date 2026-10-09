"""Figuras de cancha con la identidad de Ojo de Águila.

IMPOR1: las figuras con datos reales son resultados para el equipo; no se publican fuera de
la competencia ni se suben a git (van a outputs/).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Polygon as PoligonoMpl
from mplsoccer import Pitch

from ojo.config import params
from ojo.lentes.voronoi import ResultadoFrame, cancha
from ojo.salidas.estilo import color, rgba

ALFA_PROPIO, ALFA_RIVAL = 0.82, 0.16


def _poligonos(geometria):
    """Partes poligonales de una geometría de shapely (Polygon o MultiPolygon)."""
    for g in getattr(geometria, "geoms", [geometria]):
        if g.geom_type == "Polygon" and g.area > 0:
            yield g


def cancha_marca(alto_pulgadas: float = 8.2) -> tuple[Figure, plt.Axes, Pitch]:
    """Cancha azul marino con líneas blancas tenues, en coordenadas de StatsBomb."""
    pitch = Pitch(pitch_type="statsbomb", pitch_color=color("azul"), line_color=rgba("blanco", 0.35),
                  linewidth=1.2, line_zorder=3)
    c = params()["campo"]
    fig, ax = pitch.draw(figsize=(alto_pulgadas * c["largo"] / c["ancho"] * 0.9, alto_pulgadas))
    fig.patch.set_facecolor(color("azul"))
    return fig, ax, pitch


def dibujar_voronoi(resultado: ResultadoFrame, titulo: str | None = None, subtitulo: str | None = None,
                    destino_pase: tuple[float, float] | None = None) -> Figure:
    """Voronoi de un frame: celdas propias en dorado, rivales en blanco, frontera y apoyos del actor."""
    fig, ax, pitch = cancha_marca()
    for g in _poligonos(cancha().difference(resultado.visible)):
        ax.add_patch(PoligonoMpl(list(g.exterior.coords), closed=True, facecolor=rgba("blanco", 0.04),
                                 edgecolor=rgba("blanco", 0.10), hatch="xx", lw=0, zorder=2))
    for celda, jugador in zip(resultado.celdas, resultado.jugadores):
        relleno = rgba("dorado", ALFA_PROPIO) if jugador.propio else rgba("blanco", ALFA_RIVAL)
        for g in _poligonos(celda):
            ax.add_patch(PoligonoMpl(list(g.exterior.coords), closed=True, facecolor=relleno,
                                     edgecolor=rgba("blanco", 0.25), lw=0.5, zorder=1))
    for a, b in resultado.aristas:
        if resultado.jugadores[a].propio == resultado.jugadores[b].propio:
            continue
        borde = resultado.celdas[a].intersection(resultado.celdas[b])
        for parte in getattr(borde, "geoms", [borde]):
            if parte.length > 0 and hasattr(parte, "coords"):
                xs, ys = zip(*parte.coords)
                ax.plot(xs, ys, color=color("blanco"), lw=2.4, solid_capstyle="round", zorder=4)
    actor = resultado.indice_actor
    if actor is not None:
        pa = resultado.jugadores[actor]
        for v in resultado.vecinos(actor):
            if resultado.jugadores[v].propio:
                pb = resultado.jugadores[v]
                ax.plot([pa.x, pb.x], [pa.y, pb.y], color=color("dorado"), lw=2.2, ls=(0, (2, 2)), zorder=5)
        ax.scatter(pa.x, pa.y, s=620, zorder=5, facecolors="none", edgecolors=color("dorado"), linewidths=2)
        if destino_pase is not None:
            pitch.arrows(pa.x, pa.y, *destino_pase, ax=ax, color=color("dorado"), width=2.4, headwidth=5, zorder=7)
    for j in resultado.jugadores:
        ax.scatter(j.x, j.y, s=120, zorder=6, c=color("dorado") if j.propio else color("blanco"),
                   edgecolors=color("azul"), linewidths=1.6)
    if titulo:
        fig.text(0.04, 0.975, titulo, color=color("blanco"), fontsize=19, fontweight="bold", ha="left")
    if subtitulo:
        fig.text(0.04, 0.938, subtitulo, color=rgba("blanco", 0.72), fontsize=11.5, ha="left")
    return fig
