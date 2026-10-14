"""Maqueta 3: la narrativa de Jardine (principio → evidencia → caso confirmador) con el reproductor del partido.

Portada: "Jardine en 90 segundos" (índice Proactivo–Reactivo por torneo y principios candidatos) y un
ejemplo destacado. Explorar: barra lateral, el principio, el caso que lo confirma, el reproductor minuto
a minuto (Voronoi + índice + radar al pausar), el Monte Carlo explicativo y lo que está en construcción.
Usa la envoltura de ojo.salidas.app (encabezado, entrada, barra y paleta).

REF1: contexto/framework.md, "Índice Proactivo–Reactivo (propuesta)" y "Lectura del partido por puntos de quiebre".
IMPOR1: con datos reales la página es un resultado para la competencia: va a outputs/ (fuera de git).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from html import escape

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from ojo.config import params
from ojo.lentes.simulacion import Simulacion
from ojo.salidas.app import Barra, OJO_SVG, _barra, _con_colores, envolver
from ojo.salidas.caso import Jugada, figura_principal, svg
from ojo.salidas.estilo import color, rgba


@dataclass
class Principio:
    """Tarjeta de un principio candidato, con números ya formateados para leer."""

    titulo: str
    frase: str
    significa: str
    uso: str
    jardine: str
    previos: str
    diferencia: str
    intervalo: str
    torneos: str
    estado: str
    caso: str = ""  # p. ej. "Caso: final AP23" si la página lo confirma


@dataclass
class Montecarlo:
    """Una simulación explicada: qué se simuló y qué salió."""

    titulo: str
    texto: str
    resultado: Simulacion


@dataclass
class Narrativa:
    """Todo lo que lleva la maqueta 3."""

    titulo: str
    equipo: str
    rival: str
    antetitulo: str
    filtros: list[str]
    barra: Barra
    kpis: list[tuple[str, str, str]]  # (etiqueta, valor, detalle)
    figura_torneos: Figure
    principios: list[Principio]
    principio_caso: Principio
    ejemplo: str
    principal: Jugada
    que_muestra: str
    chips: list[tuple[str, str]]
    quiebres: list[tuple[str, str, bool]]
    datos_reproductor: dict
    montecarlo: list[Montecarlo]
    lectura: str
    metodo: str
    pendientes: list[tuple[str, str, str]]  # (título, qué mostrará, requisito que cubre)
    notas: list[str] = field(default_factory=list)


def figura_indice_torneos(resumen: pd.DataFrame, nuevo: str) -> Figure:
    """Barras del índice medio del equipo por torneo (acento con el entrenador nuevo) y puntos del rival.

    resumen: una fila por torneo, en orden, con columnas torneo, entrenador, propio y rival.
    """
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    fig.patch.set_facecolor(color("azul"))
    ax.set_facecolor(color("azul"))
    x = np.arange(len(resumen))
    colores = [color("dorado") if e == nuevo else rgba("blanco", .45) for e in resumen["entrenador"]]
    ax.bar(x, resumen["propio"], color=colores, width=.62, zorder=2)
    ax.scatter(x, resumen["rival"], s=46, color=color("blanco"), edgecolors=color("azul"), linewidths=1.2, zorder=3)
    for xi, v in zip(x, resumen["propio"]):
        ax.text(xi, v + 1.5, f"{v:.0f}", ha="center", color=color("blanco"), fontsize=9, fontweight="bold")
    ax.axhline(50, color=rgba("blanco", .35), lw=1, ls=":")
    ax.set_ylim(0, 100)
    ax.set_xticks(x, [f"{t}\n{e}" for t, e in zip(resumen["torneo"], resumen["entrenador"])], fontsize=8)
    ax.tick_params(colors=rgba("blanco", .75), labelsize=8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(rgba("blanco", .3))
    return fig


def _tarjeta(p: Principio, grande: bool = False) -> str:
    caso = f'<span class="insignia">{escape(p.caso)}</span>' if p.caso else ""
    detalle = (f'<dl class="cifras"><div><dt>Jardine</dt><dd>{escape(p.jardine)}</dd></div>'
               f'<div><dt>Solari y Ortiz</dt><dd>{escape(p.previos)}</dd></div>'
               f'<div><dt>Diferencia</dt><dd>{escape(p.diferencia)}<small>{escape(p.intervalo)}</small></dd></div>'
               f'<div><dt>Torneos en la misma dirección</dt><dd>{escape(p.torneos)}</dd></div></dl>')
    extra = (f'<p><strong>Qué significa.</strong> {escape(p.significa)}</p>'
             f'<p><strong>Lectura para el cuerpo técnico (hipótesis).</strong> {escape(p.uso)}</p>') if grande else ""
    return (f'<article class="tarjeta{" grande" if grande else ""}"><header><h3>{escape(p.titulo)}</h3>{caso}</header>'
            f'<p class="frase">{escape(p.frase)}</p>{detalle}{extra}<span class="estado">{escape(p.estado)}</span></article>')


def _montecarlo(m: Montecarlo, equipo: str, rival: str) -> str:
    r = m.resultado
    marcadores = " · ".join(f"{escape(k)} ({v:.0%})" for k, v in r.marcadores[:3])
    return (f'<article class="mc"><h3>{escape(m.titulo)}</h3><p>{escape(m.texto)}</p>'
            f'<div class="mc-barra" role="img" aria-label="Gana {r.gana:.0%}, empata {r.empata:.0%}, pierde {r.pierde:.0%}">'
            f'<span class="g" style="width:{r.gana * 100:.1f}%">{r.gana:.0%}</span>'
            f'<span class="e" style="width:{r.empata * 100:.1f}%">{r.empata:.0%}</span>'
            f'<span class="p" style="width:{r.pierde * 100:.1f}%">{r.pierde:.0%}</span></div>'
            f'<p class="mc-ley"><span class="cg"></span>Gana {escape(equipo)} <span class="ce"></span>Empate '
            f'<span class="cp"></span>Gana {escape(rival)}</p>'
            f'<p class="nota">Goles esperados: {r.goles_favor:.2f} – {r.goles_contra:.2f}. Marcadores más frecuentes: {marcadores}.</p></article>')


def _leyenda(n: Narrativa, sufijo: str) -> str:
    ojo = _con_colores(OJO_SVG.format(id="iris-" + sufijo))
    return (f'<ul class="leyenda"><li><span class="pastilla">{ojo}</span>{escape(n.equipo)}</li>'
            f'<li><span class="pastilla"><span class="punto"></span></span>{escape(n.rival)}</li>'
            '<li><span class="pastilla"><span class="raya"></span></span>Frontera entre equipos</li></ul>')


def pagina(n: Narrativa, ruta_marca: str) -> str:
    """HTML completo de la maqueta 3 con la paleta activa."""
    kpis = "".join(f'<div class="kpi"><span>{escape(a)}</span><strong>{escape(b)}</strong><small>{escape(c)}</small></div>'
                   for a, b, c in n.kpis)
    tarjetas = "".join(_tarjeta(p) for p in n.principios)
    chips = "".join(f'<div class="dato"><span>{escape(k)}</span><strong>{escape(v)}</strong></div>' for k, v in n.chips)
    quiebres = "".join(f'<li class="{"caso" if es else ""}"><span class="min">{escape(m)}</span>{escape(t)}</li>'
                       for m, t, es in n.quiebres)
    filtros = "".join(f'<button type="button" class="filtro">{escape(f)}<span aria-hidden="true">×</span></button>'
                      for f in n.filtros)
    mc = "".join(_montecarlo(m, n.equipo, n.rival) for m in n.montecarlo)
    pendientes = "".join(f'<article class="pendiente"><span class="estado">En construcción · {escape(r)}</span>'
                         f'<h3>{escape(t)}</h3><p>{escape(q)}</p></article>' for t, q, r in n.pendientes)
    notas = "".join(f'<p class="nota">{escape(x)}</p>' for x in n.notas)
    datos = json.dumps(n.datos_reproductor, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    bandas = params()["indice"]["bandas"]
    cuerpo = CUERPO
    for clave, valor in {
        "TITULO": escape(n.titulo), "ANTETITULO": escape(n.antetitulo), "EQUIPO": escape(n.equipo),
        "EQUIPO_MAYUS": escape(n.equipo.upper()), "RIVAL": escape(n.rival), "RIVAL_MAYUS": escape(n.rival.upper()),
        "KPIS": kpis, "FIGURA_TORNEOS": svg(n.figura_torneos), "TARJETAS": tarjetas,
        "TARJETA_CASO": _tarjeta(n.principio_caso, grande=True), "EJEMPLO": escape(n.ejemplo),
        "FIGURA_EJEMPLO": svg(figura_principal(n.principal)), "LEYENDA_P": _leyenda(n, "p"),
        "LEYENDA_E": _leyenda(n, "e"), "QUE_MUESTRA": escape(n.que_muestra), "BARRA": _barra(n.barra),
        "FILTROS": filtros, "CHIPS": chips, "QUIEBRES": quiebres, "MONTECARLO": mc, "LECTURA": escape(n.lectura),
        "METODO": escape(n.metodo), "PENDIENTES": pendientes, "NOTAS": notas, "DATOS": datos,
        "BANDA_BAJA": str(bandas[0]), "BANDA_ALTA": str(bandas[1]),
    }.items():
        cuerpo = cuerpo.replace(f"@@{clave}@@", valor)
    return envolver(n.titulo, ruta_marca, len(n.filtros), cuerpo, css_extra=CSS, js_extra=JS)


CUERPO = r"""
<div class="vista" id="portada">
  <section class="titulo">
    <div><span class="ante">Hackathon ISAC 2026 · La historia de un entrenador a través de los datos</span>
      <h1>André Jardine en el <span class="club">América</span>, leído frente a cada rival</h1></div>
    <button type="button" class="btn-explorar" data-vista="explorar">Explorar por rival<span>→</span></button>
  </section>
  <section class="noventa">
    <div class="noventa-cab"><span class="ante">Jardine en 90 segundos</span>
      <h2>Un equipo que propone, que sale jugando corto y que, cuando el partido se rompe, se instala arriba</h2></div>
    <div class="kpis">@@KPIS@@</div>
    <div class="dos-col">
      <div><h3 class="sub-h">Índice Proactivo–Reactivo por torneo</h3>
        <div class="figura">@@FIGURA_TORNEOS@@</div>
        <p class="pie">0 = reactivo (directo, en transición) · 100 = proactivo (posesión asentada, arriba). Barras: América; puntos: sus rivales. Índice provisional (definición del 14 oct, pendiente de confirmar).</p></div>
      <div><h3 class="sub-h">Principios candidatos</h3><div class="tarjetas">@@TARJETAS@@</div></div>
    </div>
  </section>
  <section class="ejemplo">
    <div class="col"><span class="etq-p">Caso confirmador</span><p>@@EJEMPLO@@</p><span class="uno" aria-hidden="true">1</span></div>
    <div class="cont">
      <h2>Así se ve un principio en un partido</h2>
      <div class="figura">@@FIGURA_EJEMPLO@@</div>
      @@LEYENDA_P@@
      <p class="pie">@@QUE_MUESTRA@@</p>
    </div>
  </section>
  <section class="pilares">
    <div class="pilar"><span class="n">1</span><h3>Identidad</h3><p>Índice Proactivo–Reactivo y Voronoi: cómo juega, minuto a minuto, frente a cada rival.</p></div>
    <div class="pilar"><span class="n">2</span><h3>Evidencia</h3><p>Cada principio con su número, su intervalo y un partido que lo confirma; validado en el Clausura 2026.</p></div>
    <div class="pilar"><span class="n">3</span><h3>Decisión</h3><p>Qué hacer en cada situación: matriz, ficha de 10 segundos y riesgo en el momento.</p></div>
  </section>
  <section class="cierre-p"><strong>Elige un rival y mira el mismo análisis</strong>
    <button type="button" class="btn-explorar" data-vista="explorar">Explorar por rival<span>→</span></button></section>
</div>

<div class="vista" id="explorar">
  <div class="explorar">
    <aside class="barra" aria-label="Filtros">@@BARRA@@</aside>
    <div class="velo" data-cajon></div>
    <div class="contenido">
      <span class="ante chico">@@ANTETITULO@@</span>
      <h1>@@EQUIPO_MAYUS@@ vs @@RIVAL_MAYUS@@</h1>
      <div class="filtros">@@FILTROS@@</div>
      <p class="maqueta">Maqueta con datos reales: los filtros todavía no recalculan; el índice es provisional y los principios son candidatos (criterio v1, falta la versión 2 y la prueba placebo).</p>

      <section class="bloque"><span class="ante chico">1 · El principio</span>@@TARJETA_CASO@@</section>

      <section class="bloque"><span class="ante chico">2 · El caso que lo confirma</span>
        <h2>@@TITULO@@</h2><div class="datos">@@CHIPS@@</div><ul class="quiebres">@@QUIEBRES@@</ul></section>

      <section class="bloque repro" id="repro" aria-label="Reproductor del partido">
        <span class="ante chico">3 · El partido, minuto a minuto</span>
        <div class="repro-cab"><h2>Pausa en cualquier momento para leerlo</h2>
          <div class="modos" role="group" aria-label="Qué reproducir">
            <button type="button" data-modo="partido" aria-pressed="true">Partido completo</button>
            <button type="button" data-modo="jugada" aria-pressed="false" id="btn-jugada">La jugada</button></div></div>
        <div class="repro-grid">
          <div class="repro-izq">
            <div class="figura cancha-js">
              <svg id="cancha" viewBox="-3 -3 126 86" role="img" aria-label="Foto 360 con el Voronoi del momento">
                <defs><clipPath id="clip-almendra"><path d="M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z"/></clipPath>
                  <pattern id="fuera" width="2" height="2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="2" style="stroke:rgba(255,255,255,.07);stroke-width:.6"/></pattern></defs>
                <rect x="0" y="0" width="120" height="80" style="fill:url(#fuera)"/>
                <g id="capa-foto"></g>
                <g class="lineas"><rect x="0" y="0" width="120" height="80"/><line x1="60" y1="0" x2="60" y2="80"/><circle cx="60" cy="40" r="10"/>
                  <rect x="0" y="18" width="18" height="44"/><rect x="102" y="18" width="18" height="44"/><rect x="0" y="30" width="6" height="20"/><rect x="114" y="30" width="6" height="20"/></g>
                <text id="sin-foto" x="60" y="42" text-anchor="middle">Sin foto 360 en este minuto</text>
              </svg>
              <div class="controles">
                <button type="button" id="play" aria-label="Reproducir">▶</button>
                <input type="range" id="tiempo" min="0" max="0" value="0" aria-label="Momento del partido">
                <span id="reloj">0'</span>
              </div>
              <p id="accion" class="accion"></p>
            </div>
            <div class="figura linea-js"><svg id="linea" viewBox="0 0 640 210" role="img" aria-label="Índice minuto a minuto de ambos equipos"></svg></div>
          </div>
          <aside class="panel momento" aria-live="polite">
            <header>El momento<i aria-hidden="true"></i></header>
            <section><span class="etq-p">Índice Proactivo–Reactivo</span>
              <div class="indicador"><div class="pista"><span id="m-a" class="marca-a"></span><span id="m-r" class="marca-r"></span></div>
                <div class="extremos"><span>Reactivo</span><span>Proactivo</span></div></div>
              <p id="frase-momento" class="frase-momento"></p></section>
            <section class="detalle"><span class="etq-p">Por qué (radar de componentes)</span>
              <svg id="radar" viewBox="0 0 320 230" role="img" aria-label="Radar de componentes del índice"></svg>
              <p class="nota">Hacia afuera = más proactivo. Cada eje en desviaciones frente a lo habitual (el anillo del medio es lo normal). Dorado: @@EQUIPO@@; blanco: @@RIVAL@@.</p></section>
            <section class="detalle"><span class="etq-p">A dos bandas (últimos 5 minutos)</span><table id="tabla-momento"></table></section>
            <p class="pausa">Pausa para ver el detalle del momento.</p>
          </aside>
        </div>
      </section>

      <section class="bloque"><span class="ante chico">4 · ¿Qué tan merecido? (Monte Carlo explicativo)</span>
        <h2>Lo que valían los tiros de cada equipo</h2><div class="mcs">@@MONTECARLO@@</div>
        <p class="nota">Cada tiro se repite 10,000 veces como un intento que entra con probabilidad igual a su xG. Explica el resultado; no predice partidos.</p></section>

      <section class="bloque"><span class="ante chico">5 · Cómo leerla</span>
        <div class="panel lectura-panel"><header>Cómo leerla<i aria-hidden="true"></i></header>
          <section><span class="etq-p">Leyenda</span>@@LEYENDA_E@@</section>
          <section><span class="etq-p">Qué muestra</span><p>@@QUE_MUESTRA@@</p></section>
          <section><span class="etq-p lectura">Lectura frente a @@RIVAL@@</span><div class="espacio">@@LECTURA@@</div></section>
          <section><span class="etq-p">Cómo se calcula</span><div class="espacio">@@METODO@@</div></section></div></section>

      <section class="bloque"><span class="ante chico">6 · Lo que sigue</span><h2>En construcción</h2><div class="pendientes">@@PENDIENTES@@</div></section>
      <section class="bloque">@@NOTAS@@</section>
    </div>
  </div>
</div>
<script type="application/json" id="datos-repro">@@DATOS@@</script>
<script>window.__bandas = [@@BANDA_BAJA@@, @@BANDA_ALTA@@];</script>
"""

CSS = r"""
  /* Maqueta 3: principio → caso → reproductor (ojo.salidas.narrativa) */
  .noventa { padding: 32px clamp(20px, 4vw, 56px) 40px; display: grid; gap: 20px; border-bottom: 6px solid var(--c-azul); }
  .noventa h2 { margin: 6px 0 0; font-size: clamp(22px, 2.6vw, 32px); font-weight: 900; line-height: 1.1; max-width: 32ch; }
  .sub-h { margin: 0 0 10px; font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
  .kpi { background: var(--c-azul); color: #fff; border-radius: 10px; padding: 14px 16px; display: grid; gap: 2px; }
  .kpi span { font-size: 11px; letter-spacing: .12em; text-transform: uppercase; opacity: .75; }
  .kpi strong { font-size: 30px; font-weight: 900; color: var(--c-acento); line-height: 1.05; }
  .kpi small { font-size: 12.5px; opacity: .85; }
  .dos-col { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 24px; align-items: start; }
  .tarjetas { display: grid; gap: 10px; }
  .tarjeta { background: #fff; border-radius: 12px; box-shadow: inset 0 0 0 1px var(--borde); padding: 14px 16px; display: grid; gap: 8px; }
  .tarjeta header { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
  .tarjeta h3 { margin: 0; font-size: 17px; font-weight: 900; text-transform: uppercase; }
  .tarjeta .frase { margin: 0; font-size: 14px; }
  .tarjeta p { margin: 0; font-size: 14px; }
  .tarjeta.grande { padding: 20px 22px; box-shadow: inset 0 0 0 2px var(--c-azul); }
  .tarjeta.grande h3 { font-size: 24px; }
  .tarjeta.grande .frase { font-size: 17px; font-weight: 600; }
  .insignia { background: var(--c-acento); color: var(--c-azul); font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; border-radius: 6px; padding: 3px 8px; white-space: nowrap; }
  .estado { justify-self: start; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--oda-gris-texto); border: 1.5px dashed rgba(11,37,69,.3); border-radius: 6px; padding: 3px 8px; }
  .cifras { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin: 0; }
  .cifras div { background: var(--oda-gris-fondo); border-radius: 8px; padding: 6px 8px; }
  .cifras dt { font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--oda-gris-texto); }
  .cifras dd { margin: 0; font-size: 15px; font-weight: 800; }
  .cifras small { display: block; font-size: 11px; font-weight: 500; color: var(--oda-gris-texto); }
  .tarjetas .cifras { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .tarjetas .cifras div:nth-child(n+3) { display: none; }

  .repro-cab { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; }
  .modos { display: flex; gap: 6px; }
  .modos button { border: 0; border-radius: 6px; padding: 8px 12px; font-size: 13px; font-weight: 800; background: #fff; color: var(--c-azul); box-shadow: inset 0 0 0 1.5px var(--c-azul); }
  .modos button[aria-pressed="true"] { background: var(--c-azul); color: #fff; }
  .repro-grid { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 16px; align-items: start; }
  .repro-izq { display: grid; gap: 12px; }
  #cancha { display: block; width: 100%; height: auto; background: var(--c-azul); border-radius: 8px; }
  #cancha .lineas * { fill: none; stroke: rgba(255,255,255,.35); stroke-width: .35; }
  #sin-foto { fill: rgba(255,255,255,.6); font: 600 3px var(--oda-fuente); display: none; }
  #cancha.vacia #sin-foto { display: block; }
  .controles { display: grid; grid-template-columns: auto 1fr auto; gap: 12px; align-items: center; padding: 10px 4px 2px; color: #fff; }
  #play { width: 40px; height: 40px; border-radius: 50%; border: 0; background: var(--c-acento); color: var(--c-azul); font-size: 16px; font-weight: 900; }
  #tiempo { width: 100%; accent-color: var(--c-acento); }
  #reloj { font-weight: 800; font-variant-numeric: tabular-nums; min-width: 92px; text-align: right; }
  .accion { margin: 6px 4px 2px; color: rgba(255,255,255,.85); font-size: 13px; min-height: 1.4em; }
  #linea { display: block; width: 100%; height: auto; cursor: pointer; }
  .momento .indicador { display: grid; gap: 4px; }
  .momento .pista { position: relative; height: 14px; border-radius: 999px; background: linear-gradient(90deg, rgba(11,37,69,.12), rgba(11,37,69,.04) 50%, rgba(11,37,69,.12)); }
  .momento .pista span { position: absolute; top: 50%; width: 18px; height: 18px; border-radius: 50%; transform: translate(-50%, -50%); transition: left .25s ease; }
  .marca-a { background: var(--c-acento); box-shadow: 0 0 0 3px var(--c-azul); z-index: 2; }
  .marca-r { background: #fff; box-shadow: 0 0 0 3px var(--c-azul); }
  .extremos { display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--oda-gris-texto); }
  .frase-momento { font-size: 14px !important; }
  #radar { display: block; width: 100%; height: auto; background: var(--c-azul); border-radius: 8px; }
  #tabla-momento { font-size: 13px; }
  #tabla-momento th, #tabla-momento td { padding: 5px 8px; }
  .pausa { display: none; margin: 0; padding: 12px 20px; font-size: 13px; font-weight: 700; color: var(--oda-gris-texto); }
  .repro.reproduciendo .momento .detalle { display: none; }
  .repro.reproduciendo .pausa { display: block; }
  .mcs { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; }
  .mc { background: #fff; border-radius: 12px; box-shadow: inset 0 0 0 1px var(--borde); padding: 16px; display: grid; gap: 8px; }
  .mc h3 { margin: 0; font-size: 16px; font-weight: 900; }
  .mc p { margin: 0; font-size: 14px; }
  .mc-barra { display: flex; height: 30px; border-radius: 8px; overflow: hidden; font-size: 12px; font-weight: 800; }
  .mc-barra span { display: grid; place-items: center; min-width: 0; overflow: hidden; white-space: nowrap; }
  .mc-barra .g, .mc-ley .cg { background: var(--c-acento); color: var(--c-azul); }
  .mc-barra .e, .mc-ley .ce { background: #c9cfd8; color: var(--c-azul); }
  .mc-barra .p, .mc-ley .cp { background: var(--c-azul); color: #fff; }
  .mc-ley { font-size: 12px !important; color: var(--oda-gris-texto); display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: center; }
  .mc-ley span { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; }
  .lectura-panel { display: grid; grid-template-columns: 1fr 1fr; }
  .lectura-panel header { grid-column: 1 / -1; }
  .lectura-panel section:first-of-type { border-top: 1px solid var(--borde); }
  .pendientes { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
  .pendiente { border: 2px dashed rgba(11,37,69,.25); border-radius: 12px; padding: 14px 16px; display: grid; gap: 6px; }
  .pendiente h3 { margin: 0; font-size: 16px; font-weight: 900; }
  .pendiente p { margin: 0; font-size: 13.5px; }
  @media (max-width: 1200px) { .repro-grid { grid-template-columns: minmax(0, 1fr); } .dos-col { grid-template-columns: minmax(0, 1fr); } }
  @media (max-width: 900px) { .cifras { grid-template-columns: repeat(2, minmax(0, 1fr)); } .lectura-panel { grid-template-columns: minmax(0, 1fr); } }
"""

JS = r"""
<script>
(function () {
  var D = JSON.parse(document.getElementById('datos-repro').textContent);
  var BANDAS = window.__bandas || [40, 60];
  var NS = 'http://www.w3.org/2000/svg';
  var capa = document.getElementById('capa-foto'), cancha = document.getElementById('cancha');
  var repro = document.getElementById('repro'), tiempo = document.getElementById('tiempo');
  var reloj = document.getElementById('reloj'), accion = document.getElementById('accion'), play = document.getElementById('play');
  var modo = 'partido', i = 0, timer = null;
  var VEL = { partido: 650, jugada: 1100 };  // ms por paso (solo presentación)
  if (!D.jugada || !D.jugada.fotos.length) document.getElementById('btn-jugada').hidden = true;
  else document.getElementById('btn-jugada').textContent = D.jugada.titulo;

  function el(tag, attrs, padre) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (padre) padre.appendChild(e);
    return e;
  }
  function pares(plano) { var s = []; for (var k = 0; k < plano.length; k += 2) s.push(plano[k] + ',' + plano[k + 1]); return s.join(' '); }
  function ojo(x, y, padre) {
    var s = 4.6 / 102, g = el('g', { transform: 'translate(' + (x - 54 * s) + ',' + (y - 54 * s) + ') scale(' + s + ')' }, padre);
    el('polygon', { points: '12,19.6 86,30.8 99,46.7 95.4,50.6 24.1,29.2', style: 'fill:var(--c-acento);stroke:var(--c-acento);stroke-width:2' }, g);
    el('path', { d: 'M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z', style: 'fill:var(--c-azul);stroke:var(--c-acento);stroke-width:6' }, g);
    var iris = el('g', { 'clip-path': 'url(#clip-almendra)' }, g);
    el('circle', { cx: 54, cy: 54, r: 24, style: 'fill:var(--c-acento)' }, iris);
    el('path', { d: 'M49.3 47.5L58.7 47.5L61.6 56.5L54 62L46.4 56.5Z', style: 'fill:var(--c-azul);stroke:var(--c-azul);stroke-width:3' }, iris);
  }
  function dibujar(f) {
    while (capa.firstChild) capa.removeChild(capa.firstChild);
    cancha.classList.toggle('vacia', !f);
    if (!f) { accion.textContent = ''; return; }
    f.visible.forEach(function (v) { el('polygon', { points: pares(v), style: 'fill:var(--c-azul)' }, capa); });
    f.celdas.forEach(function (c, k) {
      el('polygon', { points: pares(c), style: f.propias[k] ? 'fill:var(--c-acento);fill-opacity:.82;stroke:var(--c-azul);stroke-width:.35'
                                                         : 'fill:#fff;fill-opacity:.08;stroke:var(--c-azul);stroke-width:.35' }, capa);
    });
    f.frontera.forEach(function (l) { el('polyline', { points: pares(l), style: 'fill:none;stroke:#fff;stroke-width:.8;stroke-linecap:round' }, capa); });
    f.visible.forEach(function (v) { el('polygon', { points: pares(v), style: 'fill:none;stroke:rgba(255,255,255,.5);stroke-width:.3;stroke-dasharray:1.2 .9' }, capa); });
    f.jugadores.forEach(function (j) {
      if (j[3]) el('circle', { cx: j[0], cy: j[1], r: 2.8, style: 'fill:none;stroke-width:.5;stroke:' + (f.eq ? 'var(--c-acento)' : '#fff') }, capa);
      if (j[2]) ojo(j[0], j[1], capa);
      else el('circle', { cx: j[0], cy: j[1], r: .95, style: 'fill:#fff;stroke:var(--c-azul);stroke-width:.35' }, capa);
    });
    accion.textContent = f.reloj + ' · ' + f.texto + ' · control del ' + D.equipo + ': ' + Math.round(f.control * 100) + ' %';
  }
  function etiquetaIndice(v) { return v >= BANDAS[1] ? 'proactivo' : (v <= BANDAS[0] ? 'reactivo' : 'equilibrado'); }
  function radar(m) {
    var svg = document.getElementById('radar'); while (svg.firstChild) svg.removeChild(svg.firstChild);
    var cx = 160, cy = 114, R = 76, n = D.componentes.length;
    function punto(k, z) { var a = -Math.PI / 2 + 2 * Math.PI * k / n, r = R * (Math.max(-2.5, Math.min(2.5, z == null ? 0 : z)) + 2.5) / 5; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
    [-2.5, 0, 2.5].forEach(function (z) {
      var ps = []; for (var k = 0; k < n; k++) ps.push(punto(k, z).join(','));
      el('polygon', { points: ps.join(' '), style: 'fill:none;stroke:rgba(255,255,255,' + (z === 0 ? .45 : .15) + ');stroke-width:' + (z === 0 ? 1.2 : .8) }, svg);
    });
    D.componentes.forEach(function (c, k) {
      var p = punto(k, 2.5), a = -Math.PI / 2 + 2 * Math.PI * k / n;
      el('line', { x1: cx, y1: cy, x2: p[0], y2: p[1], style: 'stroke:rgba(255,255,255,.15)' }, svg);
      var t = el('text', { x: cx + (R + 12) * Math.cos(a), y: cy + (R + 12) * Math.sin(a) + 3, 'text-anchor': Math.abs(Math.cos(a)) < .2 ? 'middle' : (Math.cos(a) > 0 ? 'start' : 'end'),
                           style: 'fill:rgba(255,255,255,.85);font:600 9px Poppins, sans-serif' }, svg);
      t.textContent = c.radar;
    });
    [['zr', 'fill:#fff;fill-opacity:.12;stroke:#fff;stroke-width:1.4'], ['za', 'fill:var(--c-acento);fill-opacity:.35;stroke:var(--c-acento);stroke-width:2']].forEach(function (par) {
      var ps = []; for (var k = 0; k < n; k++) ps.push(punto(k, m[par[0]][k]).join(','));
      el('polygon', { points: ps.join(' '), style: par[1] }, svg);
    });
  }
  function formato(c, v) {
    if (v == null) return '—';
    if (c.formato === 'pct') return Math.round(v * 100) + ' %';
    if (c.formato === 'yd') return v.toFixed(1) + ' yd';
    return v.toFixed(2);
  }
  function panelMinuto(m) {
    document.getElementById('m-a').style.left = (m.ia == null ? 50 : m.ia) + '%';
    document.getElementById('m-r').style.left = (m.ir == null ? 50 : m.ir) + '%';
    var fa = m.ia == null ? '—' : Math.round(m.ia), fr = m.ir == null ? '—' : Math.round(m.ir);
    document.getElementById('frase-momento').innerHTML = '<strong>' + D.equipo + ' ' + fa + '</strong> (' + (m.ia == null ? 'sin dato' : etiquetaIndice(m.ia)) +
      ') · ' + D.rival + ' ' + fr + ' (' + (m.ir == null ? 'sin dato' : etiquetaIndice(m.ir)) + '). Marcador ' + m.marcador + '.';
    radar(m);
    var filas = '<thead><tr><th></th><th>' + D.equipo + '</th><th>' + D.rival + '</th></tr></thead><tbody>';
    D.componentes.forEach(function (c, k) { filas += '<tr><th>' + c.nombre + '</th><td>' + formato(c, m.va[k]) + '</td><td>' + formato(c, m.vr[k]) + '</td></tr>'; });
    document.getElementById('tabla-momento').innerHTML = filas + '</tbody>';
  }
  function lista() { return modo === 'partido' ? D.minutos : D.jugada.fotos; }
  function actualizar() {
    var L = lista(); i = Math.max(0, Math.min(i, L.length - 1)); tiempo.max = L.length - 1; tiempo.value = i;
    if (modo === 'partido') {
      var m = D.minutos[i]; dibujar(m.foto == null ? null : D.fotos[m.foto]); reloj.textContent = m.etq + ' · ' + m.marcador;
      panelMinuto(m); marcarLinea();
    } else {
      var f = D.jugada.fotos[i]; dibujar(f); reloj.textContent = f.reloj;
      var mm = D.minutos[D.jugada.minuto]; if (mm) panelMinuto(mm);
    }
  }
  function detener() { if (timer) clearInterval(timer); timer = null; play.textContent = '▶'; play.setAttribute('aria-label', 'Reproducir'); repro.classList.remove('reproduciendo'); }
  function reproducir() {
    if (i >= lista().length - 1) i = 0;
    play.textContent = '❚❚'; play.setAttribute('aria-label', 'Pausar'); repro.classList.add('reproduciendo');
    timer = setInterval(function () { if (i >= lista().length - 1) { detener(); return; } i++; actualizar(); }, VEL[modo]);
  }
  play.addEventListener('click', function () { timer ? detener() : reproducir(); });
  tiempo.addEventListener('input', function () { detener(); i = +tiempo.value; actualizar(); });
  repro.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'INPUT') return;
    if (e.key === ' ') { e.preventDefault(); timer ? detener() : reproducir(); }
    if (e.key === 'ArrowRight') { detener(); i++; actualizar(); }
    if (e.key === 'ArrowLeft') { detener(); i--; actualizar(); }
  });
  document.querySelectorAll('.modos button').forEach(function (b) {
    b.addEventListener('click', function () {
      detener(); modo = b.dataset.modo; i = 0;
      document.querySelectorAll('.modos button').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      document.querySelector('.linea-js').hidden = modo !== 'partido'; actualizar();
    });
  });
  // Línea de tiempo del índice (modo partido): clic para saltar
  var linea = document.getElementById('linea'), W = 640, H = 210, M = { i: 34, d: 8, a: 40, b: 24 }, cursor;
  function xDe(k) { return M.i + (W - M.i - M.d) * k / Math.max(D.minutos.length - 1, 1); }
  function yDe(v) { return M.a + (H - M.a - M.b) * (1 - v / 100); }
  function dibujarLinea() {
    el('rect', { x: 0, y: 0, width: W, height: H, rx: 8, style: 'fill:var(--c-azul)' }, linea);
    [BANDAS[0], 50, BANDAS[1]].forEach(function (v) {
      el('line', { x1: M.i, x2: W - M.d, y1: yDe(v), y2: yDe(v), style: 'stroke:rgba(255,255,255,' + (v === 50 ? .3 : .12) + ');stroke-dasharray:3 3' }, linea);
      var t = el('text', { x: M.i - 6, y: yDe(v) + 3, 'text-anchor': 'end', style: 'fill:rgba(255,255,255,.6);font:600 9px Poppins, sans-serif' }, linea); t.textContent = v;
    });
    D.etiquetasX.forEach(function (e) { if (e.periodo && e.k > 0) el('line', { x1: xDe(e.k) - .5, x2: xDe(e.k) - .5, y1: M.a, y2: H - M.b, style: 'stroke:rgba(255,255,255,.35)' }, linea); });
    var nivel = 0;
    D.quiebres.forEach(function (q) {
      el('line', { x1: xDe(q.k), x2: xDe(q.k), y1: M.a, y2: H - M.b, style: 'stroke:' + (q.favor ? 'var(--c-acento)' : '#fff') + ';stroke-width:' + (q.fuerte ? 1.6 : .8) + ';opacity:' + (q.fuerte ? .9 : .45) }, linea);
      if (!q.fuerte) return;  // solo goles y expulsiones llevan etiqueta; escalonadas para no encimarse
      var t = el('text', { x: xDe(q.k), y: 12 + 11 * (nivel++ % 3), 'text-anchor': 'middle', style: 'fill:' + (q.favor ? 'var(--c-acento)' : '#fff') + ';font:700 9px Poppins, sans-serif' }, linea);
      t.textContent = q.corto;
    });
    [['ir', '#fff', 1.4], ['ia', 'var(--c-acento)', 2.2]].forEach(function (s) {
      var ps = []; D.minutos.forEach(function (m, k) { if (m[s[0]] != null) ps.push(xDe(k) + ',' + yDe(m[s[0]])); });
      el('polyline', { points: ps.join(' '), style: 'fill:none;stroke:' + s[1] + ';stroke-width:' + s[2] }, linea);
    });
    D.etiquetasX.forEach(function (e) { var t = el('text', { x: xDe(e.k), y: H - 8, 'text-anchor': e.periodo ? 'start' : 'middle', style: 'fill:rgba(255,255,255,' + (e.periodo ? .9 : .6) + ');font:' + (e.periodo ? 700 : 600) + ' 9px Poppins, sans-serif' }, linea); t.textContent = e.etq; });
    cursor = el('line', { y1: M.a - 4, y2: H - M.b + 4, style: 'stroke:#fff;stroke-width:1.2' }, linea);
    linea.addEventListener('click', function (ev) {
      var r = linea.getBoundingClientRect(), x = (ev.clientX - r.left) * W / r.width;
      detener(); i = Math.round((x - M.i) / (W - M.i - M.d) * (D.minutos.length - 1)); actualizar();
    });
  }
  function marcarLinea() { if (cursor) { cursor.setAttribute('x1', xDe(i)); cursor.setAttribute('x2', xDe(i)); } }
  dibujarLinea();
  i = D.inicio || 0;
  actualizar();
})();
</script>
"""
