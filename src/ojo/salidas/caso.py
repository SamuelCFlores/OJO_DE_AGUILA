"""Caso puntual: un partido leído hasta un punto de quiebre (datos y figuras de la página del caso).

Arma las piezas a partir de las tablas de un partido: la línea de tiempo a dos bandas hasta el
quiebre, la cadena de jugadas que lleva a él (con el Voronoi de cada una), las acciones del
protagonista antes del quiebre y una tabla de los últimos minutos frente al partido hasta ahí.
La página (portada + explorar con barra lateral) la arma ojo.salidas.app.

REF1: contexto/framework.md, "Lectura del partido por puntos de quiebre" y "Control territorial".
REF2: especificación de la figura Voronoi en el handoff de diseño (branding/exportados/app_maximalismo),
con la paleta de la marca (azul, dorado y blanco).
NOTA1: todo se dibuja en la perspectiva del equipo de referencia (ataca hacia la derecha): las
acciones y los frames del rival se reflejan (120 − x, 80 − y) y "propio" pasa a ser el equipo.
IMPOR1: la página lleva posiciones y nombres reales: es un resultado para la competencia, va a
outputs/ (fuera de git) y no se publica fuera del hackathon.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from ojo.config import params
from ojo.framework import contexto
from ojo.lentes import minuto, voronoi
from ojo.salidas import marcador
from ojo.salidas.estilo import color, rgba
from ojo.salidas.figuras import _poligonos, cancha_marca

ALTO_JUGADA = 3.1  # pulgadas de cada cancha chica
ALTO_PRINCIPAL = 6.8  # pulgadas de la figura principal
ALFA_PROPIO, ALFA_RIVAL = 0.82, 0.08  # relleno de las celdas (handoff: equipo al 82 %, rival al 8 %)
TARJETAS = {"Red Card": "roja directa", "Second Yellow": "segunda amarilla", "Yellow Card": "amarilla"}
VERBOS = {
    "Pass": "pasa", "Carry": "conduce", "Miscontrol": "pierde el control", "Ball Recovery": "recupera el balón",
    "Pressure": "presiona", "Foul Committed": "comete falta", "Dispossessed": "pierde el balón", "Duel": "va al duelo",
    "Interception": "intercepta", "Clearance": "despeja", "Shot": "remata", "Dribble": "encara", "Block": "bloquea",
    "Goal Keeper": "interviene",
}
PATRONES = {"From Throw In": "saque de banda", "From Free Kick": "tiro libre", "From Corner": "tiro de esquina",
            "From Goal Kick": "saque de meta", "From Keeper": "saque del portero", "From Kick Off": "saque de centro",
            "From Counter": "contragolpe", "Regular Play": "juego abierto", "Other": "otro"}
SIN_BALON = frozenset({"Pressure", "Duel", "Foul Committed", "Ball Recovery", "Interception", "Block", "Clearance"})
ETIQUETAS_QUIEBRE = {
    "gol_favor": "gol del {e}", "gol_contra": "gol del {r}", "expulsion_favor": "expulsión en el {r}",
    "expulsion_contra": "expulsión en el {e}", "cambio_sistema_propio": "el {e} cambia de sistema",
    "cambio_sistema_rival": "el {r} cambia de sistema", "sustitucion_tactica_propia": "cambio táctico del {e}",
    "sustitucion_tactica_rival": "cambio táctico del {r}", "sustitucion_lesion_propia": "cambio por lesión del {e}",
    "sustitucion_lesion_rival": "cambio por lesión del {r}",
}


@dataclass
class Jugada:
    """Una acción de la cadena que lleva al quiebre, con su Voronoi en la perspectiva del equipo."""

    reloj: str
    texto: str
    del_equipo: bool
    resultado: voronoi.ResultadoFrame
    evento: object  # fila del evento ya orientada al equipo (x, y, fin_x, fin_y, tipo)

    @property
    def control(self) -> float:
        return self.resultado.control


def nombres(lineups: list[dict]) -> dict[int, str]:
    """Nombre corto de cada jugador (player_nickname de Lineups o, si falta, player_name)."""
    return {j["player_id"]: j.get("player_nickname") or j.get("player_name")
            for equipo in lineups for j in equipo.get("lineup") or []}


def formacion(valor) -> str:
    """4141 → "4-1-4-1"."""
    return "-".join(str(int(valor)))


def reloj(minuto_: int, segundo: int) -> str:
    return f"{int(minuto_)}:{int(segundo):02d}"


def etiqueta_quiebre(q, equipo: str, rival: str) -> str:
    """Texto corto de un quiebre, p. ej. "Guadalajara cambia de sistema (3-5-2 → 4-1-4-1)"."""
    texto = ETIQUETAS_QUIEBRE[q.tipo].format(e=equipo, r=rival)
    if q.tipo.startswith("cambio_sistema") and q.detalle:
        antes, despues = q.detalle.split("→")
        texto += f" ({formacion(antes)} → {formacion(despues)})"
    return texto[0].upper() + texto[1:]


def describir(e, nombres_: dict[int, str], nombre_equipo: dict[int, str]) -> str:
    """Una acción en lenguaje de cancha: "Zendejas pierde el control bajo presión"."""
    quien = nombres_.get(e.jugador_id, nombre_equipo.get(e.equipo_id, ""))
    texto = f"{quien} {VERBOS.get(e.tipo, e.tipo.lower())}"
    if e.tipo == "Pass" and pd.notna(e.pase_receptor_id):
        texto += f" a {nombres_.get(e.pase_receptor_id, 'un compañero')}"
        if pd.notna(e.pase_resultado):
            texto += " (no llega)"
    if e.tipo == "Carry" and pd.notna(e.fin_x):
        texto += f" {np.hypot(e.fin_x - e.x, e.fin_y - e.y):.0f} yd"
    if e.tipo == "Foul Committed" and pd.notna(e.tarjeta):
        texto += f": {TARJETAS.get(e.tarjeta, e.tarjeta)}"
    if e.bajo_presion and e.tipo in {"Pass", "Carry", "Miscontrol", "Dispossessed"}:
        texto += " bajo presión"
    return texto


def cadena(eventos: pd.DataFrame, indice_caso: int, posesiones_previas: int = 1) -> pd.DataFrame:
    """Eventos de la posesión del quiebre y de las anteriores, hasta el quiebre (sin recepciones)."""
    ev = eventos.sort_values("indice")
    posesion = ev.loc[ev["indice"] == indice_caso, "posesion"].iloc[0]
    sel = ev[ev["posesion"].between(posesion - posesiones_previas, posesion) & (ev["indice"] <= indice_caso)]
    return sel[sel["tipo"].isin(VERBOS)]


def frame_del_equipo(jugadores: pd.DataFrame, area: list[float] | np.ndarray, actor_es_del_equipo: bool,
                     ) -> tuple[list[voronoi.Jugador], list[float]]:
    """Jugadores y área visible de un frame en la perspectiva del equipo (propio = equipo)."""
    campo = params()["campo"]
    lista = voronoi.jugadores_de_frame(jugadores)
    if actor_es_del_equipo:
        return lista, list(area)
    reflejados = [voronoi.Jugador(campo["largo"] - j.x, campo["ancho"] - j.y, not j.propio, j.actor, j.portero)
                  for j in lista]
    area = np.asarray(area, dtype=float)
    plano = np.empty_like(area)
    plano[0::2], plano[1::2] = campo["largo"] - area[0::2], campo["ancho"] - area[1::2]
    return reflejados, list(plano)


def _voronoi(ax, pitch, j: Jugada, ancho_ojo: float, grosor: float) -> None:
    """Celdas, frontera, jugadores (ojo para el equipo, punto blanco para el rival), actor y flecha."""
    r = j.resultado
    for g in _poligonos(voronoi.cancha().difference(r.visible)):
        ax.add_patch(plt.Polygon(list(g.exterior.coords), closed=True, facecolor=rgba("blanco", .03),
                                 edgecolor=rgba("blanco", .08), hatch="xx", lw=0, zorder=1))
    for celda, jugador in zip(r.celdas, r.jugadores):
        relleno = rgba("dorado", ALFA_PROPIO) if jugador.propio else rgba("blanco", ALFA_RIVAL)
        for g in _poligonos(celda):
            ax.add_patch(plt.Polygon(list(g.exterior.coords), closed=True, facecolor=relleno, edgecolor=color("azul"),
                                     lw=grosor, zorder=2))
    for a, b in r.aristas:
        if r.jugadores[a].propio != r.jugadores[b].propio:
            borde = r.celdas[a].intersection(r.celdas[b])
            for parte in getattr(borde, "geoms", [borde]):
                if parte.geom_type in ("LineString", "LinearRing") and parte.length > 0:
                    xs, ys = zip(*parte.coords)
                    ax.plot(xs, ys, color=color("blanco"), lw=grosor * 2.2, solid_capstyle="round", zorder=4)
    for g in _poligonos(r.visible):
        xs, ys = g.exterior.xy
        ax.plot(xs, ys, color=rgba("blanco", .5), lw=grosor * .7, ls=(0, (4, 3)), zorder=4)
    e = j.evento
    if e.tipo in {"Pass", "Carry"} and pd.notna(e.fin_x):
        pitch.arrows(e.x, e.y, e.fin_x, e.fin_y, ax=ax, width=grosor * 1.6, headwidth=5, zorder=7,
                     color=color("dorado") if j.del_equipo else color("blanco"))
    i = r.indice_actor
    if i is not None:
        actor = r.jugadores[i]
        ax.add_patch(plt.Circle((actor.x, actor.y), ancho_ojo * .62, fill=False, lw=grosor * 1.6, zorder=8,
                                ec=color("dorado") if j.del_equipo else color("blanco")))
    for jugador in r.jugadores:
        if jugador.propio:
            marcador.dibujar(ax, jugador.x, jugador.y, ancho_ojo, zorder=9)
        else:
            ax.add_patch(plt.Circle((jugador.x, jugador.y), ancho_ojo * .2, facecolor=color("blanco"),
                                    edgecolor=color("azul"), lw=grosor * 1.3, zorder=9))


def figura_jugada(j: Jugada) -> Figure:
    """Cancha chica con el Voronoi de una jugada, encuadrada en lo que ve la cámara."""
    fig, ax, pitch = cancha_marca(ALTO_JUGADA)
    _voronoi(ax, pitch, j, ancho_ojo=5.5, grosor=1.0)
    _acercar(ax, j.resultado.visible)
    return fig


def figura_principal(j: Jugada) -> Figure:
    """La foto del quiebre en grande, con la misma especificación que las canchas chicas."""
    fig, ax, pitch = cancha_marca(ALTO_PRINCIPAL)
    _voronoi(ax, pitch, j, ancho_ojo=4.6, grosor=1.6)
    _acercar(ax, j.resultado.visible, margen=5.0)
    return fig


def _acercar(ax, visible, margen: float = 3.0) -> None:
    """Encuadra toda el área visible (más un margen en yd) con la misma proporción que la cancha."""
    campo = params()["campo"]
    proporcion = campo["largo"] / campo["ancho"]
    x_min, y_min, x_max, y_max = visible.bounds
    ancho, alto = x_max - x_min + 2 * margen, y_max - y_min + 2 * margen
    ancho, alto = max(ancho, alto * proporcion), max(alto, ancho / proporcion)
    ancho, alto = min(ancho, campo["largo"]), min(alto, campo["ancho"])
    cx, cy = (x_min + x_max) / 2, (y_min + y_max) / 2
    x0 = min(max(cx - ancho / 2, 0), campo["largo"] - ancho)
    y0 = min(max(cy - alto / 2, 0), campo["ancho"] - alto)
    ax.set_xlim(x0, x0 + ancho)
    ax.set_ylim((y0 + alto, y0) if ax.yaxis_inverted() else (y0, y0 + alto))


def _tramos(panel: pd.DataFrame, tramo_min: int) -> pd.DataFrame:
    """Índice de tramo de cada minuto del panel dentro de su periodo (el añadido es un tramo propio)."""
    inicio, fin = panel["periodo"].map(contexto.INICIO_PERIODO), panel["periodo"].map(contexto.FIN_PERIODO)
    k = (np.minimum(panel["minuto"], fin) - inicio) // tramo_min
    etiqueta = np.where(panel["minuto"] >= fin, fin.astype(str) + "+", (inicio + k * tramo_min).astype(str))
    return panel.assign(k=k, etiqueta=etiqueta)


def linea_tiempo(panel: pd.DataFrame, quiebres_previos: pd.DataFrame, equipo: str, rival: str) -> Figure:
    """Cuatro bandas por tramo hasta el quiebre: presión, field tilt, xG acumulado y control en campo rival."""
    tramo_min = params()["casos"]["tramo_min"]
    p = _tramos(panel, tramo_min)
    claves = ["periodo", "k", "etiqueta"]
    sumas = p.groupby([*claves, "lado"])[list(minuto.SUMAS)].sum().unstack("lado", fill_value=0)
    n_min = p.groupby(claves)["minuto"].nunique()
    orden = sumas.index.to_frame(index=False)
    x = np.arange(len(orden))
    s = lambda col, lado: sumas[(col, lado)].to_numpy(float)  # noqa: E731
    presion = {l: s("presiones", l) / n_min.to_numpy() for l in (minuto.PROPIO, minuto.RIVAL)}
    tercio = s("pases_ultimo_tercio", minuto.PROPIO), s("pases_ultimo_tercio", minuto.RIVAL)
    tilt = np.divide(tercio[0], tercio[0] + tercio[1], out=np.full(len(x), np.nan), where=(tercio[0] + tercio[1]) > 0)
    xg = {l: np.cumsum(s("xg", l)) for l in (minuto.PROPIO, minuto.RIVAL)}
    control = {l: np.divide(s("control_campo_rival_suma", l), s("control_campo_rival_n", l), out=np.full(len(x), np.nan),
                            where=s("control_campo_rival_n", l) > 0) for l in (minuto.PROPIO, minuto.RIVAL)}

    fig, ejes = plt.subplots(4, 1, figsize=(11, 8.2), sharex=True, gridspec_kw={"hspace": .35})
    fig.patch.set_facecolor(color("azul"))
    colores = {minuto.PROPIO: color("dorado"), minuto.RIVAL: color("blanco")}
    nombres_lado = {minuto.PROPIO: equipo, minuto.RIVAL: rival}
    for eje in ejes:
        eje.set_facecolor(color("azul"))
        eje.tick_params(colors=rgba("blanco", .7), labelsize=8)
        for lado in ("top", "right"):
            eje.spines[lado].set_visible(False)
        for lado in ("left", "bottom"):
            eje.spines[lado].set_color(rgba("blanco", .3))
    for lado in (minuto.PROPIO, minuto.RIVAL):
        ejes[0].plot(x, presion[lado], color=colores[lado], lw=2.2, marker="o", ms=3.5, label=nombres_lado[lado])
        ejes[2].step(x, xg[lado], where="mid", color=colores[lado], lw=2.2)
        ejes[3].plot(x, control[lado], color=colores[lado], lw=2.2, marker="o", ms=3.5)
    ejes[1].bar(x, tilt, color=[color("dorado") if v >= .5 else rgba("blanco", .75) for v in np.nan_to_num(tilt, nan=.5)],
                width=.75)
    ejes[1].axhline(.5, color=rgba("blanco", .4), lw=1, ls=":")
    ejes[1].set_ylim(0, 1)
    titulos = ["Presiones por minuto", f"Field tilt de {equipo} (pases en el último tercio)", "xG acumulado",
               "Control en campo rival (Voronoi)"]
    for eje, t in zip(ejes, titulos):
        eje.set_title(t, loc="left", color=color("blanco"), fontsize=10, fontweight="bold")
    ejes[0].legend(frameon=False, labelcolor=color("blanco"), fontsize=9, loc="upper right", ncol=2)
    # Descanso y quiebres previos
    pos = {(int(f.periodo), int(f.k)): i for i, f in enumerate(orden.itertuples())}
    cambio = next((i for i, f in enumerate(orden.itertuples()) if f.periodo > 1), None)
    for eje in ejes:
        if cambio is not None:
            eje.axvline(cambio - .5, color=rgba("blanco", .5), lw=1)
        for q in quiebres_previos.itertuples():
            k = (min(q.minuto, contexto.FIN_PERIODO[q.periodo]) - contexto.INICIO_PERIODO[q.periodo]) // tramo_min
            i = pos.get((int(q.periodo), int(k)))
            if i is None:
                continue
            gol = q.tipo.startswith("gol") or q.tipo.startswith("expulsion")
            eje.axvline(i, color=color("dorado") if q.tipo.endswith(("favor", "propio", "propia")) else color("blanco"),
                        lw=1.6 if gol else .8, ls="-" if gol else ":", alpha=.9 if gol else .6, zorder=0)
    ejes[-1].set_xticks(x, orden["etiqueta"])
    ejes[-1].set_xlabel("Minuto (tramos de 5; la línea gris es el descanso; las verticales, los quiebres)",
                        color=rgba("blanco", .7), fontsize=8)
    return fig


def figura_protagonista(acciones: pd.DataFrame, desde_reciente: tuple[int, int], del_equipo: bool) -> Figure:
    """Acciones del protagonista hasta el quiebre: sin balón grandes, con balón chicas; las recientes resaltadas.

    acciones: eventos ya orientados al equipo, con columnas periodo, minuto, tipo, x, y.
    desde_reciente: (periodo, minuto) desde el que una acción cuenta como reciente.
    """
    fig, ax, _ = cancha_marca(4.6)
    tono = "dorado" if del_equipo else "blanco"
    reciente = (acciones["periodo"] > desde_reciente[0]) | (
        (acciones["periodo"] == desde_reciente[0]) & (acciones["minuto"] >= desde_reciente[1]))
    sin_balon = acciones["tipo"].isin(SIN_BALON)
    for mask, s, alfa in ((~reciente & ~sin_balon, 18, .25), (~reciente & sin_balon, 70, .35),
                          (reciente & ~sin_balon, 30, .9), (reciente & sin_balon, 150, 1)):
        sub = acciones[mask]
        ax.scatter(sub["x"], sub["y"], s=s, c=[rgba(tono, alfa)], edgecolors=color("azul"), linewidths=.8, zorder=5)
    faltas = acciones[acciones["tipo"] == "Foul Committed"]
    ax.scatter(faltas["x"], faltas["y"], s=260, marker="X", c=color("blanco") if del_equipo else color("dorado"),
               edgecolors=color("azul"), linewidths=1, zorder=6)
    return fig


def antes_frente_al_partido(panel: pd.DataFrame, ventana: tuple[int, int, int], periodo_caso: int,
                            minuto_caso: int) -> pd.DataFrame:
    """Métricas a dos bandas en una ventana antes del quiebre y en todo el partido hasta él.

    ventana: (periodo, desde, hasta) en minutos enteros, límites inclusivos.
    """
    previo = panel[(panel["periodo"] < periodo_caso) | ((panel["periodo"] == periodo_caso) & (panel["minuto"] < minuto_caso))]
    minutos = previo[minuto.CLAVES_MINUTO].drop_duplicates().assign(clave="partido hasta ahí")
    p, desde, hasta = ventana
    en_ventana = minutos[(minutos["periodo"] == p) & minutos["minuto"].between(desde, hasta)].assign(clave="últimos minutos")
    sumas = minuto.sumar(panel, pd.concat([minutos, en_ventana], ignore_index=True), "clave")
    return minuto.metricas(sumas, "clave")


def svg(figura: Figure) -> str:
    """Figura como SVG en línea (cierra la figura)."""
    buffer = io.StringIO()
    figura.savefig(buffer, format="svg", facecolor=figura.get_facecolor(), bbox_inches="tight", pad_inches=.08)
    plt.close(figura)
    texto = buffer.getvalue()
    return texto[texto.index("<svg"):]
