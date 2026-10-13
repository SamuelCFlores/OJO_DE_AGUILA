"""Caso puntual: un partido leído hasta un punto de quiebre, en una página con la identidad (maqueta_2).

Arma cuatro piezas a partir de las tablas de un partido: la línea de tiempo a dos bandas hasta el
quiebre, la cadena de jugadas que lleva a él (con el Voronoi de cada una), las acciones del
protagonista antes del quiebre y una tabla de los últimos minutos frente al partido hasta ahí.

REF1: contexto/framework.md, "Lectura del partido por puntos de quiebre" y "Control territorial".
NOTA1: todo se dibuja en la perspectiva del equipo de referencia (ataca hacia la derecha): las
acciones y los frames del rival se reflejan (120 − x, 80 − y) y "propio" pasa a ser el equipo.
IMPOR1: la página lleva posiciones y nombres reales: es un resultado para la competencia, va a
outputs/ (fuera de git) y no se publica fuera del hackathon.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from html import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from ojo.config import params
from ojo.framework import contexto
from ojo.lentes import minuto, voronoi
from ojo.salidas.estilo import ARCHIVO_TOKENS, color, rgba
from ojo.salidas.figuras import cancha_marca
from ojo.salidas.paso_a_paso import _celdas, _jugadores, _visible

ALTO_JUGADA = 3.1  # pulgadas de cada cancha chica
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
    "gol_favor": "gol {e}", "gol_contra": "gol {r}", "expulsion_favor": "expulsión en {r}",
    "expulsion_contra": "expulsión en {e}", "cambio_sistema_propio": "{e} cambia de sistema",
    "cambio_sistema_rival": "{r} cambia de sistema", "sustitucion_tactica_propia": "cambio táctico de {e}",
    "sustitucion_tactica_rival": "cambio táctico de {r}", "sustitucion_lesion_propia": "cambio por lesión de {e}",
    "sustitucion_lesion_rival": "cambio por lesión de {r}",
}


@dataclass
class Jugada:
    """Una acción de la cadena que lleva al quiebre, con su Voronoi si el frame se puede analizar."""

    reloj: str
    texto: str
    del_equipo: bool
    control: float | None = None
    figura: Figure | None = None


@dataclass
class Caso:
    """Todo lo que lleva la página de un caso."""

    titulo: str
    subtitulo: str
    equipo: str
    chips: list[tuple[str, str]]
    quiebres: list[tuple[str, str, bool]]  # (minuto, texto, es el quiebre del caso)
    linea_tiempo: Figure
    tabla_antes: pd.DataFrame
    cadena_texto: list[tuple[str, str, bool]]  # (reloj, texto, del equipo)
    jugadas: list[Jugada]
    protagonista: str
    figura_protagonista: Figure
    resumen_protagonista: list[str]
    cierre: list[str]
    notas: list[str] = field(default_factory=list)


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


def figura_jugada(resultado: voronoi.ResultadoFrame, e, del_equipo: bool) -> Figure:
    """Cancha chica con el Voronoi de una jugada en la perspectiva del equipo; e ya viene orientado."""
    fig, ax, pitch = cancha_marca(ALTO_JUGADA)
    _celdas(ax, resultado.celdas, resultado.jugadores)
    for a, b in resultado.aristas:
        if resultado.jugadores[a].propio != resultado.jugadores[b].propio:
            borde = resultado.celdas[a].intersection(resultado.celdas[b])
            for parte in getattr(borde, "geoms", [borde]):
                if parte.geom_type in ("LineString", "LinearRing") and parte.length > 0:
                    xs, ys = zip(*parte.coords)
                    ax.plot(xs, ys, color=color("blanco"), lw=1.8, solid_capstyle="round", zorder=4)
    _visible(ax, resultado.visible, relleno=False)
    _jugadores(ax, resultado.jugadores)
    i = resultado.indice_actor
    if i is not None:
        actor = resultado.jugadores[i]
        ax.scatter(actor.x, actor.y, s=520, zorder=5, facecolors="none", linewidths=2.2,
                   edgecolors=color("dorado") if del_equipo else color("blanco"))
    if e.tipo in {"Pass", "Carry"} and pd.notna(e.fin_x):
        pitch.arrows(e.x, e.y, e.fin_x, e.fin_y, ax=ax, width=2, headwidth=5, zorder=8,
                     color=color("dorado") if del_equipo else color("blanco"))
    _acercar(ax, resultado.visible)
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


def _svg(figura: Figure) -> str:
    buffer = io.StringIO()
    figura.savefig(buffer, format="svg", facecolor=figura.get_facecolor(), bbox_inches="tight", pad_inches=.08)
    plt.close(figura)
    texto = buffer.getvalue()
    return texto[texto.index("<svg"):]


def html(caso: Caso, ruta_marca: str) -> str:
    """Página del caso con la barra, la entrada y el ícono de la maqueta (ruta_marca: carpeta branding/)."""
    chips = "".join(f'<div class="chip"><span>{escape(k)}</span><strong>{escape(v)}</strong></div>' for k, v in caso.chips)
    quiebres = "".join(
        f'<li class="{"caso" if es else ""}"><span class="min">{escape(m)}</span>{escape(t)}</li>' for m, t, es in caso.quiebres)
    filas = "".join(
        f'<li class="{"eq" if eq else "riv"}"><span class="min">{escape(r)}</span>{escape(t)}</li>' for r, t, eq in caso.cadena_texto)
    jugadas = "".join(
        f'<figure class="jugada {"eq" if j.del_equipo else "riv"}"><div class="cancha">{_svg(j.figura)}</div>'
        f'<figcaption><span class="min">{escape(j.reloj)}</span>{escape(j.texto)}'
        f'<span class="ctl">Control del {escape(caso.equipo)}: {j.control:.0%}</span></figcaption></figure>'
        for j in caso.jugadas if j.figura is not None)
    t = caso.tabla_antes
    tabla = "".join(f"<tr><th>{escape(str(i))}</th>" + "".join(f"<td>{v}</td>" for v in fila) + "</tr>"
                    for i, fila in zip(t.index, t.to_numpy()))
    cabecera = "".join(f"<th>{escape(str(c))}</th>" for c in t.columns)
    resumen = "".join(f"<li>{escape(x)}</li>" for x in caso.resumen_protagonista)
    cierre = "".join(f"<li>{escape(x)}</li>" for x in caso.cierre)
    notas = "".join(f"<p class=\"nota\">{escape(x)}</p>" for x in caso.notas)
    return PLANTILLA.format(
        tokens=ARCHIVO_TOKENS.read_text(encoding="utf-8"), marca=ruta_marca, titulo=escape(caso.titulo), subtitulo=escape(caso.subtitulo), chips=chips,
        quiebres=quiebres, linea_tiempo=_svg(caso.linea_tiempo), cabecera=cabecera, tabla=tabla, cadena=filas,
        jugadas=jugadas, protagonista=escape(caso.protagonista), figura_protagonista=_svg(caso.figura_protagonista),
        resumen=resumen, cierre=cierre, notas=notas)


PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ojo de Águila · {titulo}</title>
<link rel="icon" href="{marca}/fuente/marca-2a/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{marca}/dist/marca.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800;900&display=swap">
<style>
{tokens}
  /* NOTA1: misma barra, entrada e ícono que branding/maqueta.html; el contenido es de un caso real.
     Los tokens van incrustados para que colores y fuente no dependan de que cargue dist/marca.css. */
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; }}
  body {{ background: var(--oda-gris-fondo); color: var(--oda-azul); font-family: var(--oda-fuente); line-height: 1.55; }}
  html.con-intro {{ overflow: hidden; }}
  #intro {{ position: fixed; inset: 0; z-index: 1000; background: var(--oda-azul); transition: opacity .6s ease; cursor: pointer; }}
  #intro.oculto {{ display: none; }}
  #intro.saliendo {{ opacity: 0; pointer-events: none; }}
  #intro-lienzo {{ position: absolute; inset: 0; }}
  #intro-saltar {{ position: absolute; right: 24px; bottom: 22px; font: 500 13px/1 var(--oda-fuente); letter-spacing: .06em;
    color: rgba(255,255,255,.7); background: transparent; border: 1px solid rgba(255,255,255,.35); border-radius: 999px;
    padding: 9px 16px; cursor: pointer; opacity: 0; animation: aparecer .4s ease 1.2s forwards; }}
  @keyframes aparecer {{ to {{ opacity: 1; }} }}
  #banda-espacio {{ height: 242px; }}
  header.banda {{ position: fixed; top: 0; left: 0; right: 0; z-index: 10; background-color: var(--oda-azul);
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 22 22'%3E%3Cg fill='none' stroke='%23E8B100' stroke-width='3.6'%3E%3Cpath d='M-1 12 L11 0 L23 12'/%3E%3Cpath d='M-1 23 L11 11 L23 23'/%3E%3C/g%3E%3C/svg%3E");
    background-size: 22px 22px; padding-block: 28px 64px; box-shadow: 0 2px 0 rgba(11,37,69,.25); transition: padding-block .35s ease; }}
  .banda-in {{ position: relative; max-width: 1120px; margin: 0 auto; padding-inline: 16px; }}
  .placa {{ display: flex; align-items: center; gap: 16px; padding: 12px 22px 34px 12px; background: var(--oda-dorado);
    border-radius: 8px; transition: padding .35s ease, gap .35s ease; }}
  #loop-icono {{ position: relative; width: 104px; height: 104px; flex: none; border-radius: 14px; overflow: hidden;
    transition: width .35s ease, height .35s ease, border-radius .35s ease; }}
  .marca-texto {{ font-family: var(--oda-fuente); font-weight: 900; text-transform: uppercase; font-size: clamp(34px, 8vw, 96px);
    line-height: 1; letter-spacing: -.01em; color: var(--oda-azul); white-space: nowrap; transition: font-size .35s ease; }}
  header.banda.compacta {{ padding-block: 8px; }}
  header.banda.compacta .placa {{ padding: 6px 16px 6px 6px; gap: 12px; }}
  header.banda.compacta #loop-icono {{ width: 52px; height: 52px; border-radius: 10px; }}
  header.banda.compacta .marca-texto {{ font-size: clamp(22px, 3.4vw, 38px); }}
  header.banda.compacta .cinta {{ opacity: 0; transform: translateY(-10px); visibility: hidden; pointer-events: none; }}
  .a-acento {{ position: relative; display: inline-block; }}
  .a-acento .tilde {{ position: absolute; left: .33em; top: -.16em; width: .26em; height: .18em; background: var(--oda-blanco);
    clip-path: polygon(52% 0, 100% 0, 40% 100%, 0 100%); }}
  .solo-lector {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }}
  .cinta {{ position: absolute; right: 40px; top: calc(100% - 22px); max-width: min(52%, 520px); padding: 9px 16px; border-radius: 8px;
    background: var(--oda-azul); box-shadow: 0 0 0 3px var(--oda-dorado); font-weight: 800; text-transform: uppercase;
    font-size: clamp(10.5px, 1.1vw, 14px); line-height: 1.2; letter-spacing: .04em; color: var(--oda-dorado);
    transition: opacity .25s ease, transform .25s ease, visibility .25s; }}
  main {{ max-width: 1120px; margin: 0 auto; padding: 48px 16px 72px; display: grid; gap: 56px; }}
  .eyebrow {{ font-size: 12px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--oda-gris-texto); }}
  h1 {{ font-size: clamp(30px, 5vw, 50px); line-height: 1.06; margin: 8px 0 12px; text-wrap: balance; }}
  h2 {{ font-size: clamp(22px, 3vw, 28px); margin: 4px 0 10px; }}
  p {{ max-width: 70ch; margin: 0 0 10px; }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }}
  .chip {{ background: var(--oda-azul); color: #fff; border-radius: 10px; padding: 10px 14px; display: grid; min-width: 120px; }}
  .chip span {{ font-size: 11px; letter-spacing: .1em; text-transform: uppercase; opacity: .7; }}
  .chip strong {{ font-size: 20px; color: var(--oda-dorado); }}
  .quiebres {{ list-style: none; padding: 0; margin: 14px 0 0; display: flex; flex-wrap: wrap; gap: 8px; }}
  .quiebres li {{ background: #fff; border-radius: 999px; padding: 6px 14px; box-shadow: inset 0 0 0 1px rgba(11,37,69,.15); font-size: 14px; }}
  .quiebres li.caso {{ background: var(--oda-azul); color: #fff; box-shadow: 0 0 0 3px var(--oda-dorado); font-weight: 600; }}
  .min {{ font-weight: 800; margin-right: 8px; font-variant-numeric: tabular-nums; }}
  .figura {{ background: var(--oda-azul); border-radius: 12px; padding: 12px; overflow: hidden; }}
  .figura svg, .cancha svg {{ display: block; width: 100%; height: auto; }}
  table {{ border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; font-size: 14px; width: 100%; max-width: 760px; }}
  th, td {{ padding: 8px 12px; text-align: right; border-bottom: 1px solid rgba(11,37,69,.08); font-variant-numeric: tabular-nums; }}
  th:first-child {{ text-align: left; }}
  thead th {{ background: var(--oda-azul); color: #fff; font-weight: 600; }}
  .tabla-scroll {{ overflow-x: auto; }}
  .cadena {{ list-style: none; padding: 0; margin: 0 0 18px; display: grid; gap: 4px; }}
  .cadena li {{ padding: 6px 12px; border-left: 4px solid var(--oda-dorado); background: #fff; border-radius: 0 8px 8px 0; font-size: 14px; }}
  .cadena li.riv {{ border-left-color: var(--oda-azul); }}
  .jugadas {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }}
  .jugada {{ margin: 0; background: var(--oda-azul); color: #fff; border-radius: 12px; overflow: hidden; }}
  .jugada figcaption {{ padding: 10px 12px 12px; font-size: 13px; display: grid; gap: 2px; }}
  .jugada.eq figcaption {{ border-top: 3px solid var(--oda-dorado); }}
  .jugada.riv figcaption {{ border-top: 3px solid #fff; }}
  .jugada .ctl {{ color: var(--oda-dorado); font-size: 12px; }}
  .dos {{ display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 20px; align-items: start; }}
  .cierre {{ background: var(--oda-azul); color: #fff; border-radius: 12px; padding: 22px 24px; }}
  .cierre h2 {{ color: var(--oda-dorado); }}
  ul.lista {{ margin: 0; padding-left: 20px; display: grid; gap: 6px; }}
  .nota {{ font-size: 13px; color: var(--oda-gris-texto); }}
  @media (max-width: 760px) {{
    .placa {{ padding: 10px 14px 10px 10px; gap: 12px; }}
    #loop-icono {{ width: 60px; height: 60px; border-radius: 10px; }}
    .cinta {{ position: relative; right: auto; top: auto; max-width: none; margin: -10px 18px 0 auto; width: fit-content; }}
    header.banda {{ padding-block: 14px 18px; }}
    header.banda.compacta {{ padding-block: 6px; }}
    header.banda.compacta #loop-icono {{ width: 40px; height: 40px; border-radius: 8px; }}
    header.banda.compacta .cinta {{ position: absolute; }}
    .dos {{ grid-template-columns: minmax(0, 1fr); }}
  }}
  @media (prefers-reduced-motion: reduce) {{ header.banda, .placa, #loop-icono, .marca-texto, .cinta {{ transition: none; }} }}
</style>
</head>
<body>
<div id="intro" role="img" aria-label="Animación de entrada de Ojo de Águila"><div id="intro-lienzo"></div>
  <button id="intro-saltar" type="button">Saltar ›</button></div>
<script>
  (function () {{
    var reducir = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.__ojoMostrarIntro = !reducir;
    if (window.__ojoMostrarIntro) document.documentElement.classList.add('con-intro');
    else document.getElementById('intro').classList.add('oculto');
  }})();
</script>
<div id="banda-espacio" aria-hidden="true"></div>
<header class="banda"><div class="banda-in">
  <div class="placa"><div id="loop-icono" aria-hidden="true"></div>
    <span class="marca-texto"><span class="solo-lector">Ojo de Águila</span><span aria-hidden="true">Ojo de <span class="a-acento">A<span class="tilde"></span></span>guila</span></span></div>
  <div class="cinta">La intuición del entrenador, convertida en evidencia</div>
</div></header>

<main>
  <section>
    <span class="eyebrow">{subtitulo}</span>
    <h1>{titulo}</h1>
    <div class="chips">{chips}</div>
  </section>

  <section>
    <span class="eyebrow">1 · El partido hasta aquí</span>
    <h2>Los quiebres que llevaron a este momento</h2>
    <ul class="quiebres">{quiebres}</ul>
  </section>

  <section>
    <span class="eyebrow">2 · A dos bandas</span>
    <h2>Quién mandaba, tramo a tramo</h2>
    <p>Dorado: el América. Blanco: el rival. Cada punto es un tramo de 5 minutos; las líneas verticales son los quiebres (continuas: goles y expulsiones).</p>
    <div class="figura">{linea_tiempo}</div>
  </section>

  <section>
    <span class="eyebrow">3 · Los minutos previos</span>
    <h2>Los últimos minutos frente a todo el partido</h2>
    <p>Los 10 minutos antes del quiebre contra todo lo jugado hasta ahí, a dos bandas. Tasas por minuto.</p>
    <div class="tabla-scroll"><table><thead><tr><th></th>{cabecera}</tr></thead><tbody>{tabla}</tbody></table></div>
  </section>

  <section>
    <span class="eyebrow">4 · La jugada</span>
    <h2>Los segundos que llevan al quiebre</h2>
    <ul class="cadena">{cadena}</ul>
    <p>Cada cancha es la foto 360 de esa acción, siempre con el América atacando hacia la derecha. El anillo marca a quien ejecuta; la línea blanca, dónde chocan los equipos.</p>
    <div class="jugadas">{jugadas}</div>
  </section>

  <section>
    <span class="eyebrow">5 · El protagonista</span>
    <h2>{protagonista} antes del quiebre</h2>
    <div class="dos"><div class="figura">{figura_protagonista}</div>
      <div><ul class="lista">{resumen}</ul>
        <p class="nota">Puntos grandes: acciones sin balón (presión, duelos, recuperaciones, faltas). Chicos: con balón. Resaltados: los últimos minutos. X: faltas.</p></div></div>
  </section>

  <section class="cierre">
    <h2>Hasta aquí</h2>
    <ul class="lista">{cierre}</ul>
  </section>
  <section>{notas}</section>
</main>

<script src="{marca}/dist/vendor/react.production.min.js"></script>
<script src="{marca}/dist/vendor/react-dom.production.min.js"></script>
<script src="{marca}/dist/marca.js"></script>
<script>
  (function () {{
    var reducir = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (window.OjoMarca) OjoMarca.loop(document.getElementById('loop-icono'), {{ estatico: reducir }});
    var banda = document.querySelector('header.banda');
    var espacio = document.getElementById('banda-espacio');
    function medirBanda() {{ if (!banda.classList.contains('compacta')) espacio.style.height = banda.offsetHeight + 'px'; }}
    function revisarScroll() {{ banda.classList.toggle('compacta', window.scrollY > 24); }}
    var pendiente = false;
    window.addEventListener('scroll', function () {{
      if (pendiente) return; pendiente = true;
      requestAnimationFrame(function () {{ pendiente = false; revisarScroll(); }});
    }}, {{ passive: true }});
    window.addEventListener('resize', medirBanda);
    banda.addEventListener('transitionend', medirBanda);
    if (document.fonts) document.fonts.ready.then(medirBanda);
    medirBanda(); revisarScroll();
    var intro = document.getElementById('intro');
    if (!window.__ojoMostrarIntro || !window.OjoMarca) {{ intro.remove(); document.documentElement.classList.remove('con-intro'); return; }}
    var control = null, cerrada = false;
    function cerrar() {{
      if (cerrada) return; cerrada = true;
      intro.classList.add('saliendo'); document.documentElement.classList.remove('con-intro');
      setTimeout(function () {{ if (control) control.detener(); intro.remove(); }}, 650);
    }}
    control = OjoMarca.intro(document.getElementById('intro-lienzo'), {{ segundos: 5, alTerminar: cerrar }});
    intro.addEventListener('click', cerrar);
    window.addEventListener('keydown', function (e) {{ if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') cerrar(); }});
  }})();
</script>
</body>
</html>
"""
