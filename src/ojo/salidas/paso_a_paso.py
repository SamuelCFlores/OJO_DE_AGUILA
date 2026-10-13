"""El Voronoi de una jugada, paso a paso: del evento al control del espacio, en HTML.

Recrea cada paso del cálculo de ojo.lentes.voronoi sobre un frame 360 real: el evento, lo que
ve la cámara, quién cuenta, las celdas, el recorte y el control. Sirve para el reporte y el video.

REF1: contexto/framework.md, objetos "Control territorial" y "Grafo de vecindad".
IMPOR1: con datos reales el HTML es un resultado para la competencia: va a outputs/ (fuera de git)
y no lleva nombres de jugadores.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from html import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from matplotlib.patches import Polygon as PoligonoMpl

from ojo.config import params
from ojo.lentes import voronoi
from ojo.salidas.estilo import color, rgba
from ojo.salidas.figuras import ALFA_PROPIO, ALFA_RIVAL, _poligonos, cancha_marca, dibujar_voronoi

ALTO_FIGURA = 5.4  # pulgadas: cabe en una columna del reporte


@dataclass
class Paso:
    """Un paso del recorrido: título, explicación en lenguaje de cancha y su figura."""

    titulo: str
    texto: str
    figura: Figure


@dataclass
class Jugada:
    """Lo que se sabe del evento elegido (sin nombres)."""

    tipo: str
    minuto: int
    segundo: int
    equipo: str
    x: float
    y: float
    fin_x: float | None = None
    fin_y: float | None = None
    contexto: str = ""  # p. ej. "3 min después de una sustitución táctica"


def _jugadores(ax, jugadores: list[voronoi.Jugador], excluidos: list[voronoi.Jugador] = ()) -> None:
    for j in jugadores:
        ax.scatter(j.x, j.y, s=110, zorder=6, c=color("dorado") if j.propio else color("blanco"),
                   edgecolors=color("azul"), linewidths=1.5)
        if j.portero:
            ax.scatter(j.x, j.y, s=260, zorder=5, facecolors="none", edgecolors=rgba("blanco", 0.6), linewidths=1)
    for j in excluidos:
        ax.scatter(j.x, j.y, s=110, zorder=6, facecolors="none", linewidths=1.5,
                   edgecolors=color("dorado") if j.propio else color("blanco"))
        ax.scatter(j.x, j.y, s=60, zorder=7, marker="x", color=rgba("blanco", 0.8), linewidths=1.2)


def _visible(ax, visible, relleno: bool = True) -> None:
    for g in _poligonos(visible):
        xs, ys = g.exterior.xy
        if relleno:
            ax.fill(xs, ys, color=rgba("blanco", 0.07), zorder=1)
        ax.plot(xs, ys, color=rgba("blanco", 0.85), lw=1.6, ls=(0, (4, 3)), zorder=4)


def _celdas(ax, celdas, jugadores, alfa_propio: float = ALFA_PROPIO, alfa_rival: float = ALFA_RIVAL) -> None:
    for celda, j in zip(celdas, jugadores):
        relleno = rgba("dorado", alfa_propio) if j.propio else rgba("blanco", alfa_rival)
        for g in _poligonos(celda):
            ax.add_patch(PoligonoMpl(list(g.exterior.coords), closed=True, facecolor=relleno,
                                     edgecolor=rgba("blanco", 0.35), lw=0.6, zorder=2))


def _flecha(ax, pitch, jugada: Jugada) -> None:
    if jugada.fin_x is not None and jugada.fin_y is not None:
        pitch.arrows(jugada.x, jugada.y, jugada.fin_x, jugada.fin_y, ax=ax, color=color("dorado"), width=2.4,
                     headwidth=5, zorder=8)


def pasos(jugada: Jugada, todos: list[voronoi.Jugador], area_visible) -> list[Paso]:
    """Los seis pasos del cálculo para un frame; falla si el frame no se puede analizar."""
    cfg, campo = params()["voronoi"], params()["campo"]
    visible = voronoi.poligono_visible(area_visible)
    resultado = voronoi.analizar_frame(todos, area_visible)
    if visible is None or resultado is None:
        raise ValueError("Ese frame no se puede analizar (sin área visible o con pocos jugadores de un equipo).")
    validos = resultado.jugadores
    excluidos = [j for j in todos if not any(j is v for v in validos)]
    sin_recorte = voronoi.celdas(validos, voronoi.cancha(), None)
    recortadas = resultado.celdas
    pct_visible = visible.area / (campo["largo"] * campo["ancho"])
    lista = []

    fig, ax, pitch = cancha_marca(ALTO_FIGURA)
    ax.scatter(jugada.x, jugada.y, s=160, zorder=6, c=color("dorado"), edgecolors=color("azul"), linewidths=1.5)
    _flecha(ax, pitch, jugada)
    lista.append(Paso("1 · El evento", (
        f"{escape(jugada.tipo)} de {escape(jugada.equipo)} en el minuto {jugada.minuto}:{jugada.segundo:02d}"
        f"{' (' + escape(jugada.contexto) + ')' if jugada.contexto else ''}. "
        "Todo se dibuja en la perspectiva de quien ejecuta: ataca de izquierda a derecha. StatsBomb registra dónde "
        "empieza y dónde termina la acción; el 360 agrega una foto de ese instante."), fig))

    fig, ax, pitch = cancha_marca(ALTO_FIGURA)
    _visible(ax, visible)
    _jugadores(ax, todos)
    _flecha(ax, pitch, jugada)
    lista.append(Paso("2 · Lo que ve la cámara", (
        f"La foto 360 solo trae a los jugadores que salen en la toma: aquí {len(todos)} (dorado: el equipo que ejecuta; "
        f"blanco: el rival). La línea punteada es el área visible, {pct_visible:.0%} de la cancha. Fuera de ella no "
        "sabemos quién está, y por eso nunca se mide."), fig))

    fig, ax, pitch = cancha_marca(ALTO_FIGURA)
    _visible(ax, visible)
    _jugadores(ax, validos, excluidos)
    lista.append(Paso("3 · Quién cuenta", (
        f"Se quitan los jugadores a menos de {cfg['min_dist_borde']:g} yd del borde de la toma (tachados): podría haber "
        f"un rival fuera de cámara quitándoles espacio. El que ejecuta se queda siempre. Cuentan {len(validos)}. "
        "Sin identidad ni velocidad: cada punto es una posición, no un nombre."), fig))

    fig, ax, pitch = cancha_marca(ALTO_FIGURA)
    _celdas(ax, sin_recorte, validos, alfa_propio=0.55, alfa_rival=0.12)
    _visible(ax, visible, relleno=False)
    _jugadores(ax, validos)
    lista.append(Paso("4 · Cada jugador, su zona", (
        "Voronoi: cada punto de la cancha pertenece al jugador que tiene más cerca. Así se reparte el campo entre "
        "los que cuentan. Todavía sin recortar: las celdas de las orillas se estiran hasta zonas que la cámara no ve."),
        fig))

    fig, ax, pitch = cancha_marca(ALTO_FIGURA)
    _celdas(ax, recortadas, validos)
    for j in validos:
        ax.add_patch(Circle((j.x, j.y), cfg["alcance_max_yd"], fill=False, ec=rgba("blanco", 0.18), lw=0.8, zorder=3))
    _visible(ax, visible, relleno=False)
    _jugadores(ax, validos)
    lista.append(Paso("5 · El recorte", (
        f"Cada celda se recorta a lo que se ve (área visible) y a {cfg['alcance_max_yd']:g} yd alrededor de su jugador "
        "(círculos): un hueco enorme lejos de todos no lo controla nadie. Lo que queda es el espacio que de verdad "
        "se puede disputar en esa foto."), fig))

    fig = dibujar_voronoi(resultado, destino_pase=(jugada.fin_x, jugada.fin_y) if jugada.fin_x is not None else None)
    fig.set_size_inches(ALTO_FIGURA * campo["largo"] / campo["ancho"] * 0.9, ALTO_FIGURA)
    lista.append(Paso("6 · El control", (
        f"<strong>Control: {resultado.control:.0%}</strong> del espacio disputable es del equipo que ejecuta. "
        f"La línea blanca ({resultado.frontera:.0f} yd) es donde chocan los dos equipos. Quien ejecuta tiene "
        f"<strong>{resultado.apoyos:.0f} compañeros</strong> con celda vecina (líneas punteadas: opciones de pase "
        f"cercanas) y <strong>{resultado.rivales_cerca:.0f} rivales</strong> encima. Estas cuatro cifras son las que "
        "se promedian en cada ventana antes y después de un quiebre."), fig))
    return lista


def _svg(figura: Figure) -> str:
    buffer = io.StringIO()
    figura.savefig(buffer, format="svg", facecolor=figura.get_facecolor(), bbox_inches="tight", pad_inches=0.1)
    plt.close(figura)
    texto = buffer.getvalue()
    return texto[texto.index("<svg"):]


def html(lista: list[Paso], titulo: str, subtitulo: str) -> str:
    """Página autocontenida (figuras en SVG) con la identidad de Ojo de Águila."""
    secciones = "\n".join(
        f'<section class="paso"><div class="figura">{_svg(p.figura)}</div>'
        f'<div class="texto"><h2>{escape(p.titulo)}</h2><p>{p.texto}</p></div></section>'
        for p in lista)
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root {{ --azul: {color("azul")}; --dorado: {color("dorado")}; --blanco: {color("blanco")}; --gris: {color("gris-texto")}; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--azul); color: var(--blanco); font-family: Poppins, system-ui, sans-serif; }}
header {{ padding: 32px 16px 8px; max-width: 1100px; margin: 0 auto; }}
header h1 {{ margin: 0; font-size: clamp(1.6rem, 4vw, 2.4rem); }}
header h1 span {{ color: var(--dorado); }}
header p {{ margin: 8px 0 0; opacity: .75; }}
main {{ max-width: 1100px; margin: 0 auto; padding: 8px 16px 48px; }}
.paso {{ display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 24px; align-items: center;
         padding: 24px 0; border-bottom: 1px solid rgba(255,255,255,.12); }}
.figura svg {{ width: 100%; height: auto; display: block; }}
.texto h2 {{ margin: 0 0 8px; color: var(--dorado); font-size: 1.15rem; }}
.texto p {{ margin: 0; line-height: 1.55; opacity: .9; }}
footer {{ max-width: 1100px; margin: 0 auto; padding: 0 16px 32px; font-size: .8rem; opacity: .6; }}
@media (max-width: 760px) {{ .paso {{ grid-template-columns: 1fr; }} }}
</style></head>
<body><header><h1>Ojo de <span>Águila</span> · {escape(titulo)}</h1><p>{escape(subtitulo)}</p></header>
<main>{secciones}</main>
<footer>Datos: StatsBomb (eventos y 360), solo para el Hackathon ISAC 2026. Definiciones en contexto/framework.md.</footer>
</body></html>"""
