"""Página de la app de Ojo de Águila (portada + explorar con barra lateral), llena con un caso.

Recrea la estructura del handoff de diseño (branding/exportados/app_maximalismo: encabezado con
patrón de rombos y navegación, portada editorial, barra lateral de filtros y panel "Cómo leerla")
con la paleta de la marca (azul, dorado y blanco) y el contenido de un caso puntual (ojo.salidas.caso).

NOTA1: es una maqueta con un caso real: los filtros de la barra cambian de estado pero todavía no
recalculan la vista; eso llega con resumenes.json (contexto/resumenes.md).
IMPOR1: con datos reales la página es un resultado para la competencia: va a outputs/ (fuera de git).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape

import pandas as pd
from matplotlib.figure import Figure

from ojo.salidas.caso import Jugada, figura_jugada, figura_principal, svg
from ojo.salidas.estilo import ARCHIVO_TOKENS


@dataclass
class Barra:
    """Lo que muestra la barra lateral (estado seleccionado incluido)."""

    rival: str
    partidos_rival: int
    rivales: list[tuple[str, int]]
    entrenadores: list[tuple[str, bool]]
    torneos: list[tuple[str, bool, bool]]  # (id, activo, es de prueba)
    partidos: list[tuple[str, str, str, bool]]  # (fecha, etapa, marcador, activo)
    situaciones: list[tuple[str, list[tuple[str, bool]]]]  # (grupo, [(etiqueta, activa)])
    condicion: str
    muestra: str
    resumen: list[tuple[str, str]]


@dataclass
class Caso:
    """Contenido de la página: portada, encabezado de explorar, panel y secciones del caso."""

    titulo: str
    antetitulo: str
    equipo: str
    rival: str
    ejemplo: str  # pie de la portada, p. ej. "América vs Guadalajara, la expulsión de Fidalgo"
    filtros: list[str]
    que_muestra: str
    lectura: str
    metodo: str
    chips: list[tuple[str, str]]
    quiebres: list[tuple[str, str, bool]]
    linea_tiempo: Figure
    tabla_antes: pd.DataFrame
    cadena_texto: list[tuple[str, str, bool]]
    jugadas: list[Jugada]
    principal: Jugada
    protagonista: str
    figura_protagonista: Figure
    resumen_protagonista: list[str]
    cierre: list[str]
    barra: Barra
    notas: list[str] = field(default_factory=list)


# Patrón 4c del handoff (rombos con chevrones anidados), con la paleta de la marca.
PATRON = ("%3Csvg xmlns='http://www.w3.org/2000/svg' width='96' height='96'%3E%3Crect width='96' height='96' fill='%230B2545'/%3E"
          "%3Cpath d='M4.75 52.75 L48 9.50 L91.25 52.75 M14.25 62.25 L48 28.50 L81.75 62.25 M23.75 71.75 L48 47.50 L72.25 71.75 "
          "M33.25 81.25 L48 66.50 L62.75 81.25 M42.75 90.75 L48 85.50 L53.25 90.75 M-43.25 4.75 L0 -38.50 L43.25 4.75 "
          "M-33.75 14.25 L0 -19.50 L33.75 14.25 M-24.25 23.75 L0 -0.50 L24.25 23.75 M-14.75 33.25 L0 18.50 L14.75 33.25 "
          "M-5.25 42.75 L0 37.50 L5.25 42.75 M52.75 4.75 L96 -38.50 L139.25 4.75 M62.25 14.25 L96 -19.50 L129.75 14.25 "
          "M71.75 23.75 L96 -0.50 L120.25 23.75 M81.25 33.25 L96 18.50 L110.75 33.25 M90.75 42.75 L96 37.50 L101.25 42.75 "
          "M-43.25 100.75 L0 57.50 L43.25 100.75 M-33.75 110.25 L0 76.50 L33.75 110.25 M-24.25 119.75 L0 95.50 L24.25 119.75 "
          "M-14.75 129.25 L0 114.50 L14.75 129.25 M-5.25 138.75 L0 133.50 L5.25 138.75 M52.75 100.75 L96 57.50 L139.25 100.75 "
          "M62.25 110.25 L96 76.50 L129.75 110.25 M71.75 119.75 L96 95.50 L120.25 119.75 M81.25 129.25 L96 114.50 L110.75 129.25 "
          "M90.75 138.75 L96 133.50 L101.25 138.75' fill='none' stroke='%23E8B100' stroke-width='10' stroke-linejoin='miter'/%3E%3C/svg%3E")

# Marcador de ojo para la leyenda (mismas formas que ojo.salidas.marcador).
OJO_SVG = ('<svg viewBox="0 14 102 70" width="34" height="24" aria-hidden="true"><defs><clipPath id="{id}">'
           '<path d="M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z"/></clipPath></defs>'
           '<polygon points="12,19.6 86,30.8 99,46.7 95.4,50.6 24.1,29.2" fill="#E8B100" stroke="#E8B100" stroke-width="2" stroke-linejoin="round"/>'
           '<path d="M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z" fill="#0B2545" stroke="#E8B100" stroke-width="6" stroke-linejoin="round"/>'
           '<g clip-path="url(#{id})"><circle cx="54" cy="54" r="24" fill="#E8B100"/>'
           '<path d="M49.3 47.5L58.7 47.5L61.6 56.5L54 62L46.4 56.5Z" fill="#0B2545" stroke="#0B2545" stroke-width="3" stroke-linejoin="round"/></g></svg>')


# El nombre del rival cabe en la placa: tamaño de letra según su largo (también en el JS al cambiar de rival).
PLACA_ANCHO_PX, PLACA_EM_LETRA, PLACA_MAX_PX = 228, 0.8, 30


def tamano_nombre(nombre: str) -> int:
    """Tamaño (px) para que el nombre del rival quepa en una línea de la placa."""
    return min(PLACA_MAX_PX, int(PLACA_ANCHO_PX / (PLACA_EM_LETRA * max(len(nombre), 1))))


def _leyenda(caso: Caso, sufijo: str, en_columna: bool) -> str:
    clase = "leyenda columna" if en_columna else "leyenda"
    return (f'<ul class="{clase}"><li><span class="pastilla">{OJO_SVG.format(id="iris-" + sufijo)}</span>{escape(caso.equipo)}</li>'
            f'<li><span class="pastilla"><span class="punto"></span></span>{escape(caso.rival)}</li>'
            '<li><span class="pastilla"><span class="raya"></span></span>Frontera entre equipos</li></ul>')


def _chip(texto: str, activo: bool, extra: str = "", titulo: str = "") -> str:
    t = f' title="{escape(titulo)}"' if titulo else ""
    return f'<button type="button" class="chip-t {extra}" data-toggle aria-pressed="{str(activo).lower()}"{t}>{escape(texto)}</button>'


def _barra(b: Barra) -> str:
    rivales = "".join(f'<li><button type="button" class="rival-btn" data-rival="{escape(n)}" data-n="{k}">'
                      f'<span>{escape(n)}</span><span class="n">{k}</span></button></li>' for n, k in b.rivales)
    entrenadores = "".join(_chip(n, a) for n, a in b.entrenadores)
    torneos = "".join(_chip(t, a, "prueba" if p else "", "Torneo de prueba: el modelo no lo vio" if p else "")
                      for t, a, p in b.torneos)
    partidos = "".join(f'<li><button type="button" class="partido-btn" aria-pressed="{str(a).lower()}">'
                       f'<span class="fecha">{escape(f)}</span><span>{escape(e)}</span><strong>{escape(m)}</strong></button></li>'
                       for f, e, m, a in b.partidos)
    situaciones = "".join(f'<p class="sub">{escape(g)}</p><div class="chips-s">'
                          + "".join(_chip(s, a, "redondo") for s, a in lista) + "</div>" for g, lista in b.situaciones)
    condicion = "".join(f'<button type="button" role="radio" aria-checked="{str(c == b.condicion).lower()}" '
                        f'class="seg">{c}</button>' for c in ("Todos", "Local", "Visita"))
    resumen = "".join(f"<div><span>{escape(k)}</span><strong>{escape(v)}</strong></div>" for k, v in b.resumen)
    return f"""
<div class="grupo"><div class="fila-t"><span class="etq">Rival</span><button type="button" class="enlace" data-volver>Restablecer</button></div>
  <div class="placa-rival"><span class="sel">Seleccionado</span><strong id="rival-nombre" style="font-size: {tamano_nombre(b.rival)}px">{escape(b.rival)}</strong>
    <span class="cinta-n" id="rival-n">{b.partidos_rival} partidos</span></div>
  <ul class="lista-rivales">{rivales}</ul></div>
<hr>
<div class="grupo"><span class="etq">Entrenador</span><div class="rejilla-3">{entrenadores}</div></div>
<div class="grupo"><span class="etq">Torneo</span><div class="rejilla-3">{torneos}</div>
  <p class="aviso-prueba">Línea punteada: torneo de prueba (CL26).</p></div>
<div class="grupo"><span class="etq">Partido</span><ul class="lista-partidos">{partidos}</ul></div>
<hr>
<div class="grupo"><span class="etq">Situación</span>{situaciones}</div>
<div class="grupo"><span class="etq">Condición</span><div class="segmentado" role="radiogroup" aria-label="Condición">{condicion}</div></div>
<hr>
<div class="grupo"><span class="etq">Muestra</span><p class="muestra">{escape(b.muestra)}</p></div>
<div class="grupo"><span class="etq">Resumen rápido</span><div class="resumen">{resumen}</div></div>
<div class="grupo acciones"><button type="button" class="btn-borde" disabled title="Llega con resumenes.json">Ficha de 10 segundos · pronto</button>
  <button type="button" class="btn-borde" data-volver>Volver al caso principal</button></div>"""


def pagina(caso: Caso, ruta_marca: str) -> str:
    """HTML completo de la app con el caso; ruta_marca es la carpeta branding/ relativa a la página."""
    chips = "".join(f'<div class="dato"><span>{escape(k)}</span><strong>{escape(v)}</strong></div>' for k, v in caso.chips)
    quiebres = "".join(f'<li class="{"caso" if es else ""}"><span class="min">{escape(m)}</span>{escape(t)}</li>'
                       for m, t, es in caso.quiebres)
    cadena = "".join(f'<li class="{"eq" if eq else "riv"}{" pos" if not r else ""}"><span class="min">{escape(r)}</span>{escape(t)}</li>'
                     for r, t, eq in caso.cadena_texto)
    jugadas = "".join(f'<figure class="jugada {"eq" if j.del_equipo else "riv"}"><div class="cancha">{svg(figura_jugada(j))}</div>'
                      f'<figcaption><span class="min">{escape(j.reloj)}</span>{escape(j.texto)}'
                      f'<span class="ctl">Control del {escape(caso.equipo)}: {j.control:.0%}</span></figcaption></figure>'
                      for j in caso.jugadas)
    t = caso.tabla_antes
    tabla = ("<thead><tr><th></th>" + "".join(f"<th>{escape(str(c))}</th>" for c in t.columns) + "</tr></thead><tbody>"
             + "".join(f"<tr><th>{escape(str(i))}</th>" + "".join(f"<td>{escape(str(v))}</td>" for v in fila) + "</tr>"
                       for i, fila in zip(t.index, t.to_numpy())) + "</tbody>")
    filtros = "".join(f'<button type="button" class="filtro">{escape(f)}<span aria-hidden="true">×</span></button>'
                      for f in caso.filtros)
    lista = lambda xs: "".join(f"<li>{escape(x)}</li>" for x in xs)  # noqa: E731
    reemplazos = {
        "TOKENS": ARCHIVO_TOKENS.read_text(encoding="utf-8"), "MARCA": ruta_marca, "PATRON": PATRON,
        "TITULO": escape(caso.titulo), "ANTETITULO": escape(caso.antetitulo), "EQUIPO": escape(caso.equipo),
        "EQUIPO_MAYUS": escape(caso.equipo.upper()), "RIVAL_MAYUS": escape(caso.rival.upper()), "RIVAL": escape(caso.rival),
        "EJEMPLO": escape(caso.ejemplo), "FIGURA_PORTADA": svg(figura_principal(caso.principal)),
        "FIGURA_EXPLORAR": svg(figura_principal(caso.principal)), "LEYENDA_FILA": _leyenda(caso, "p", False),
        "LEYENDA_COLUMNA": _leyenda(caso, "e", True), "QUE_MUESTRA": escape(caso.que_muestra),
        "LECTURA": escape(caso.lectura), "METODO": escape(caso.metodo), "FILTROS": filtros,
        "N_FILTROS": str(len(caso.filtros)), "BARRA": _barra(caso.barra), "CHIPS": chips, "QUIEBRES": quiebres,
        "LINEA_TIEMPO": svg(caso.linea_tiempo), "TABLA": tabla, "CADENA": cadena, "JUGADAS": jugadas,
        "PROTAGONISTA": escape(caso.protagonista), "FIGURA_PROTAGONISTA": svg(caso.figura_protagonista),
        "RESUMEN_PROTAGONISTA": lista(caso.resumen_protagonista), "CIERRE": lista(caso.cierre),
        "NOTAS": "".join(f'<p class="nota">{escape(x)}</p>' for x in caso.notas),
        "PLACA_MAX": str(PLACA_MAX_PX), "PLACA_ANCHO": str(PLACA_ANCHO_PX), "PLACA_EM": str(PLACA_EM_LETRA),
    }
    texto = PLANTILLA
    for clave, valor in reemplazos.items():
        texto = texto.replace(f"@@{clave}@@", valor)
    return texto


PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ojo de Águila · @@TITULO@@</title>
<link rel="icon" href="@@MARCA@@/fuente/marca-2a/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="@@MARCA@@/dist/marca.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap">
<style>
@@TOKENS@@
  /* NOTA1: estructura del handoff de diseño (app_maximalismo) con la paleta de la marca; los tokens van
     incrustados para que colores y fuente no dependan de que cargue dist/marca.css. */
  :root { --alto-enc: 72px; --borde: rgba(11,37,69,.12); --sep: rgba(255,255,255,.14); --anillo: rgba(255,255,255,.4); }
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  body { background: var(--oda-gris-fondo); color: var(--oda-azul); font-family: var(--oda-fuente); line-height: 1.5; }
  html.con-intro { overflow: hidden; }
  button { font: inherit; color: inherit; cursor: pointer; }
  :focus-visible { outline: 2px solid var(--oda-dorado); outline-offset: 2px; }
  main :focus-visible { outline-color: var(--oda-azul); }

  #intro { position: fixed; inset: 0; z-index: 1000; background: var(--oda-azul); transition: opacity .6s ease; cursor: pointer; }
  #intro.oculto { display: none; }
  #intro.saliendo { opacity: 0; pointer-events: none; }
  #intro-lienzo { position: absolute; inset: 0; }
  #intro-saltar { position: absolute; right: 24px; bottom: 22px; font: 500 13px/1 var(--oda-fuente); letter-spacing: .06em;
    color: rgba(255,255,255,.7); background: transparent; border: 1px solid rgba(255,255,255,.35); border-radius: 999px;
    padding: 9px 16px; opacity: 0; animation: aparecer .4s ease 1.2s forwards; }
  @keyframes aparecer { to { opacity: 1; } }

  /* Encabezado: patrón 4c, placa del logotipo y navegación */
  header.enc { position: sticky; top: 0; z-index: 10; min-height: var(--alto-enc); padding: 10px 24px; display: flex;
    align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px 12px; background: var(--oda-azul) url("data:image/svg+xml,@@PATRON@@");
    background-size: 96px 96px; }
  .placa { display: flex; align-items: center; gap: 12px; padding: 6px 18px 6px 6px; background: var(--oda-dorado); border-radius: 8px; }
  #loop-icono { position: relative; width: 48px; height: 48px; flex: none; border-radius: 10px; overflow: hidden; background: var(--oda-azul); }
  .marca-texto { font-weight: 900; font-size: 34px; line-height: 1; text-transform: uppercase; color: var(--oda-azul); white-space: nowrap; }
  .a-acento { position: relative; display: inline-block; }
  .a-acento .tilde { position: absolute; left: .33em; top: -.16em; width: .26em; height: .18em; background: var(--oda-blanco);
    clip-path: polygon(52% 0, 100% 0, 40% 100%, 0 100%); }
  .solo-lector { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
  nav.vistas { display: flex; gap: 6px; padding: 6px; background: var(--oda-dorado); border-radius: 10px; }
  nav.vistas button { border: 0; border-radius: 6px; padding: 9px 14px; font-size: 13px; font-weight: 800; letter-spacing: .06em;
    text-transform: uppercase; background: var(--oda-azul); color: #fff; box-shadow: inset 0 0 0 2px var(--oda-dorado); }
  nav.vistas button:hover { color: var(--oda-dorado); }
  nav.vistas button[aria-current="page"] { background: #fff; color: var(--oda-azul); box-shadow: none; }
  nav.vistas .solo-movil { display: none; }

  /* Portada */
  .vista { display: none; }
  body[data-vista="portada"] #portada, body[data-vista="explorar"] #explorar { display: block; }
  .titulo { padding: 40px clamp(20px, 4vw, 56px) 32px; border-bottom: 6px solid var(--oda-dorado); display: grid;
    grid-template-columns: 1fr auto; align-items: end; gap: 24px; }
  .ante { font-size: 13px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--oda-gris-texto); }
  .titulo h1 { margin: 10px 0 0; font-weight: 900; font-size: clamp(36px, 4.6vw, 62px); line-height: .94; letter-spacing: -.02em;
    text-transform: uppercase; max-width: 18ch; }
  .titulo h1 .club { color: var(--oda-dorado); -webkit-text-stroke: 2px var(--oda-azul); }
  .btn-explorar { border: 0; border-radius: 8px; padding: 14px 20px; font-size: 15px; font-weight: 800; letter-spacing: .04em;
    text-transform: uppercase; background: var(--oda-azul); color: #fff; box-shadow: 6px 6px 0 var(--oda-dorado); white-space: nowrap; }
  .btn-explorar span { color: var(--oda-dorado); margin-left: 8px; }
  .btn-explorar:hover { transform: translate(-1px, -1px); box-shadow: 7px 7px 0 var(--oda-dorado); }
  .ejemplo { display: grid; grid-template-columns: 240px 1fr; }
  .ejemplo .col { background: var(--oda-dorado); padding: 24px; display: flex; flex-direction: column; gap: 10px; }
  .ejemplo .col .etq-p { font-size: 13px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
  .ejemplo .col p { margin: 0; font-size: 15px; font-weight: 600; }
  .ejemplo .col .uno { margin-top: auto; font-size: 180px; font-weight: 900; line-height: .8; color: transparent; -webkit-text-stroke: 3px var(--oda-azul); }
  .ejemplo .cont { padding: 28px clamp(20px, 4vw, 56px); display: grid; gap: 14px; }
  .ejemplo h2 { margin: 0; font-size: 28px; font-weight: 800; line-height: 1.15; }
  .figura { background: var(--oda-azul); border-radius: 12px; overflow: hidden; padding: 10px; }
  .figura svg, .cancha svg { display: block; width: 100%; height: auto; }
  .pie { font-size: 14px; color: var(--oda-gris-texto); margin: 0; max-width: 80ch; }
  .leyenda { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 14px; font-size: 13px; font-weight: 600; }
  .leyenda li { display: flex; align-items: center; gap: 8px; }
  .leyenda.columna { flex-direction: column; align-items: flex-start; gap: 10px; }
  .pastilla { display: inline-grid; place-items: center; width: 46px; height: 30px; border-radius: 8px; background: var(--oda-azul); }
  .pastilla .punto { width: 12px; height: 12px; border-radius: 50%; background: #fff; box-shadow: 0 0 0 2px var(--oda-azul); }
  .pastilla .raya { width: 28px; height: 4px; border-radius: 2px; background: #fff; }
  .pilares { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); border-top: 6px solid var(--oda-azul); }
  .pilar { padding: 24px 28px 28px; display: grid; gap: 8px; align-content: start; }
  .pilar:not(:last-child) { border-right: 2px solid var(--oda-azul); }
  .pilar:last-child { background: var(--oda-azul); color: #fff; }
  .pilar .n { font-size: 72px; font-weight: 900; line-height: .9; color: transparent; -webkit-text-stroke: 2px var(--oda-azul); }
  .pilar:last-child .n { color: var(--oda-dorado); -webkit-text-stroke: 0; }
  .pilar h3 { margin: 0; font-size: 20px; font-weight: 900; text-transform: uppercase; }
  .pilar p { margin: 0; font-size: 14px; }
  .cierre-p { background: var(--oda-azul); color: #fff; padding: 32px clamp(20px, 4vw, 56px); display: flex; flex-wrap: wrap;
    align-items: center; justify-content: space-between; gap: 18px; }
  .cierre-p strong { font-size: clamp(22px, 2.6vw, 32px); font-weight: 900; text-transform: uppercase; }
  .cierre-p .btn-explorar { background: var(--oda-dorado); color: var(--oda-azul); box-shadow: none; }
  .cierre-p .btn-explorar span { color: var(--oda-azul); }
  .cierre-p .btn-explorar:hover { background: #fff; transform: none; }

  /* Explorar: barra lateral + contenido */
  .explorar { display: grid; grid-template-columns: 300px minmax(0, 1fr); }
  aside.barra { position: sticky; top: var(--alto-enc); height: calc(100vh - var(--alto-enc)); overflow-y: auto; background: var(--oda-azul);
    color: #fff; border-top: 4px solid var(--oda-dorado); padding: 20px 18px 32px; }
  aside.barra hr { border: 0; border-top: 1px solid var(--sep); margin: 22px 0; }
  .grupo { display: grid; gap: 10px; margin-bottom: 18px; }
  .etq { font-size: 12px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: var(--oda-dorado); }
  .fila-t { display: flex; justify-content: space-between; align-items: baseline; }
  .enlace { background: none; border: 0; padding: 0; font-size: 13px; text-decoration: underline; color: #fff; }
  .placa-rival { position: relative; background: var(--oda-dorado); color: var(--oda-azul); border-radius: 8px; padding: 12px 16px 24px; margin-bottom: 14px; }
  .placa-rival .sel { display: block; font-size: 11px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
  .placa-rival strong { display: block; font-size: 30px; font-weight: 900; line-height: 1.05; text-transform: uppercase; white-space: nowrap; }
  .cinta-n { position: absolute; right: 14px; top: calc(100% - 14px); background: var(--oda-azul); color: var(--oda-dorado); font-size: 11px;
    font-weight: 800; letter-spacing: .1em; text-transform: uppercase; padding: 4px 10px; border-radius: 6px; box-shadow: 0 0 0 2px var(--oda-dorado); }
  .lista-rivales, .lista-partidos { list-style: none; margin: 0; padding: 0; }
  .rival-btn { width: 100%; display: flex; justify-content: space-between; background: none; border: 0; border-bottom: 1px solid var(--sep);
    padding: 9px 2px; font-size: 15px; font-weight: 700; text-transform: uppercase; text-align: left; color: #fff; }
  .rival-btn .n { color: var(--oda-dorado); }
  .rival-btn:hover span:first-child { color: var(--oda-dorado); }
  .rejilla-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
  .chip-t { border: 0; border-radius: 6px; padding: 8px 4px; font-size: 13px; font-weight: 800; background: transparent; color: #fff;
    box-shadow: inset 0 0 0 1.5px var(--anillo); }
  .chip-t[aria-pressed="true"] { background: var(--oda-dorado); color: var(--oda-azul); box-shadow: none; }
  .chip-t.prueba { box-shadow: none; outline: 1.5px dashed var(--anillo); outline-offset: -1.5px; }
  .chip-t.prueba[aria-pressed="true"] { outline-color: var(--oda-azul); }
  .chip-t.redondo { border-radius: 999px; padding: 7px 12px; font-size: 12.5px; font-weight: 700; }
  .chip-t.redondo[aria-pressed="true"] { background: #fff; color: var(--oda-azul); }
  .chips-s { display: flex; flex-wrap: wrap; gap: 6px; }
  .sub { margin: 4px 0 0; font-size: 11px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: rgba(255,255,255,.6); }
  .aviso-prueba { margin: 0; font-size: 11.5px; color: rgba(255,255,255,.6); }
  .partido-btn { width: 100%; display: grid; grid-template-columns: auto 1fr auto; gap: 8px; align-items: center; text-align: left;
    background: none; border: 0; border-bottom: 1px solid var(--sep); padding: 8px 6px; font-size: 13px; color: #fff; border-radius: 6px; }
  .partido-btn .fecha { font-weight: 700; color: rgba(255,255,255,.7); font-variant-numeric: tabular-nums; }
  .partido-btn[aria-pressed="true"] { background: #fff; color: var(--oda-azul); border-bottom-color: transparent; }
  .partido-btn[aria-pressed="true"] .fecha { color: var(--oda-azul); }
  .segmentado { display: grid; grid-template-columns: repeat(3, 1fr); border-radius: 8px; box-shadow: inset 0 0 0 1.5px var(--anillo); padding: 3px; gap: 3px; }
  .seg { border: 0; border-radius: 6px; padding: 7px 0; font-size: 13px; font-weight: 800; background: none; color: #fff; }
  .seg[aria-checked="true"] { background: var(--oda-dorado); color: var(--oda-azul); }
  .muestra { margin: 0; font-size: 14px; font-weight: 600; }
  .resumen { display: grid; gap: 6px; }
  .resumen div { display: flex; justify-content: space-between; gap: 10px; font-size: 13px; border-bottom: 1px solid var(--sep); padding-bottom: 6px; }
  .resumen strong { color: var(--oda-dorado); }
  .acciones { gap: 8px; }
  .btn-borde { border: 0; border-radius: 8px; padding: 10px 12px; font-size: 13px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase;
    background: none; color: #fff; box-shadow: inset 0 0 0 2px var(--oda-dorado); }
  .btn-borde:hover:not(:disabled) { background: var(--oda-dorado); color: var(--oda-azul); }
  .btn-borde:disabled { opacity: .5; cursor: not-allowed; }

  .contenido { padding: 28px clamp(20px, 3vw, 48px) 64px; max-width: 1480px; display: grid; gap: 20px; align-content: start; }
  .contenido h1 { margin: 2px 0 0; font-size: clamp(26px, 2.8vw, 38px); font-weight: 900; text-transform: uppercase; line-height: 1.05; }
  .ante.chico { font-size: 12px; }
  .filtros { display: flex; flex-wrap: wrap; gap: 6px; }
  .filtro { border: 0; border-radius: 6px; padding: 6px 10px; background: var(--oda-azul); color: #fff; font-size: 13px; font-weight: 600; }
  .filtro span { color: var(--oda-dorado); margin-left: 8px; font-weight: 800; }
  .filtro:hover { background: #13335c; }
  .maqueta { margin: 0; font-size: 13px; color: var(--oda-gris-texto); border: 1.5px dashed rgba(11,37,69,.25); border-radius: 8px; padding: 8px 12px; }
  .principal { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 20px; align-items: start; }
  .panel { background: #fff; border-radius: 12px; border: 1px solid var(--borde); overflow: hidden; }
  .panel header { background: var(--oda-azul); color: var(--oda-dorado); padding: 12px 20px; display: flex; justify-content: space-between;
    align-items: center; font-size: 13px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
  .panel header i { width: 10px; height: 10px; border-radius: 50%; background: var(--oda-dorado); }
  .panel section { padding: 18px 20px; border-top: 1px solid var(--borde); display: grid; gap: 10px; }
  .panel section:first-of-type { border-top: 0; }
  .panel .etq-p { font-size: 12px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: var(--oda-gris-texto); }
  .panel .etq-p.lectura { color: var(--oda-azul); }
  .panel .etq-p.lectura::before { content: "●"; color: var(--oda-dorado); margin-right: 6px; }
  .panel p { margin: 0; font-size: 14px; }
  .espacio { box-shadow: inset 0 0 0 1.5px rgba(11,37,69,.25); border-radius: 8px; padding: 12px 14px; font-size: 14px; }

  .bloque { display: grid; gap: 12px; margin-top: 18px; }
  .bloque h2 { margin: 0; font-size: clamp(20px, 2.2vw, 26px); font-weight: 800; }
  .datos { display: flex; flex-wrap: wrap; gap: 10px; }
  .dato { background: var(--oda-azul); color: #fff; border-radius: 10px; padding: 10px 14px; display: grid; min-width: 120px; }
  .dato span { font-size: 11px; letter-spacing: .1em; text-transform: uppercase; opacity: .7; }
  .dato strong { font-size: 18px; color: var(--oda-dorado); }
  .quiebres { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 8px; }
  .quiebres li { background: #fff; border-radius: 999px; padding: 6px 14px; box-shadow: inset 0 0 0 1px var(--borde); font-size: 14px; }
  .quiebres li.caso { background: var(--oda-azul); color: #fff; box-shadow: 0 0 0 3px var(--oda-dorado); font-weight: 600; }
  .min { font-weight: 800; margin-right: 8px; font-variant-numeric: tabular-nums; }
  .tabla-scroll { overflow-x: auto; }
  table { border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; font-size: 14px; width: 100%; max-width: 820px; }
  th, td { padding: 8px 12px; text-align: right; border-bottom: 1px solid rgba(11,37,69,.08); font-variant-numeric: tabular-nums; }
  th:first-child { text-align: left; }
  thead th { background: var(--oda-azul); color: #fff; font-weight: 600; }
  .cadena { list-style: none; padding: 0; margin: 0; display: grid; gap: 4px; }
  .cadena li { padding: 6px 12px; border-left: 4px solid var(--oda-dorado); background: #fff; border-radius: 0 8px 8px 0; font-size: 14px; }
  .cadena li.riv { border-left-color: var(--oda-azul); }
  .cadena li.pos { background: none; font-size: 12px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: var(--oda-gris-texto); }
  .jugadas { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 14px; }
  .jugada { margin: 0; background: var(--oda-azul); color: #fff; border-radius: 12px; overflow: hidden; }
  .jugada figcaption { padding: 10px 12px 12px; font-size: 13px; display: grid; gap: 2px; }
  .jugada.eq figcaption { border-top: 3px solid var(--oda-dorado); }
  .jugada.riv figcaption { border-top: 3px solid #fff; }
  .jugada .ctl { color: var(--oda-dorado); font-size: 12px; }
  .dos { display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 20px; align-items: start; }
  ul.lista { margin: 0; padding-left: 20px; display: grid; gap: 6px; font-size: 14px; }
  .hasta { background: var(--oda-azul); color: #fff; border-radius: 12px; padding: 20px 24px; display: grid; gap: 10px; }
  .hasta h2 { color: var(--oda-dorado); }
  .nota { margin: 0; font-size: 12.5px; color: var(--oda-gris-texto); }
  .velo { display: none; }

  @media (max-width: 1200px) {
    .principal { grid-template-columns: minmax(0, 1fr); }
    .panel { display: grid; grid-template-columns: 1fr 1fr; }
    .panel header { grid-column: 1 / -1; }
    .panel section:first-of-type { border-top: 1px solid var(--borde); }
  }
  @media (max-width: 900px) {
    .marca-texto { font-size: 22px; }
    #loop-icono { width: 40px; height: 40px; }
    header.enc { padding: 8px 12px; }
    nav.vistas button { padding: 8px 10px; font-size: 12px; }
    body[data-vista="explorar"] nav.vistas .solo-movil { display: inline-block; }
    .titulo { grid-template-columns: 1fr; }
    .ejemplo { grid-template-columns: 1fr; }
    .ejemplo .col .uno { display: none; }
    .pilar:not(:last-child) { border-right: 0; border-bottom: 2px solid var(--oda-azul); }
    .explorar { grid-template-columns: minmax(0, 1fr); }
    aside.barra { position: fixed; top: 0; left: 0; bottom: 0; height: 100vh; width: min(320px, 88vw); z-index: 30;
      transform: translateX(-105%); transition: transform .25s ease; }
    body.cajon aside.barra { transform: none; }
    body.cajon .velo { display: block; position: fixed; inset: 0; z-index: 25; background: rgba(11,37,69,.45); }
    .panel { grid-template-columns: minmax(0, 1fr); }
    .dos { grid-template-columns: minmax(0, 1fr); }
  }
  @media (max-width: 520px) {
    .marca-texto { font-size: 17px; } .placa { padding-right: 10px; gap: 8px; } #loop-icono { width: 34px; height: 34px; }
    nav.vistas { width: 100%; } nav.vistas button { flex: 1; padding: 7px 6px; font-size: 11px; }
    .titulo h1 { font-size: 34px; } .btn-explorar { white-space: normal; }
  }
  @media (prefers-reduced-motion: reduce) { aside.barra { transition: none; } .btn-explorar:hover { transform: none; } }
</style>
</head>
<body data-vista="portada">
<div id="intro" role="img" aria-label="Animación de entrada de Ojo de Águila"><div id="intro-lienzo"></div>
  <button id="intro-saltar" type="button">Saltar ›</button></div>
<script>
  (function () {
    var reducir = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.__ojoMostrarIntro = !reducir;
    if (window.__ojoMostrarIntro) document.documentElement.classList.add('con-intro');
    else document.getElementById('intro').classList.add('oculto');
  })();
</script>

<header class="enc">
  <div class="placa"><div id="loop-icono" aria-hidden="true"></div>
    <span class="marca-texto"><span class="solo-lector">Ojo de Águila</span><span aria-hidden="true">Ojo de <span class="a-acento">A<span class="tilde"></span></span>guila</span></span></div>
  <nav class="vistas" aria-label="Vistas">
    <button type="button" data-vista="portada" aria-current="page">Portada</button>
    <button type="button" data-vista="explorar">Explorar</button>
    <button type="button" class="solo-movil" data-cajon>Filtros · @@N_FILTROS@@</button>
  </nav>
</header>

<main>
<div class="vista" id="portada">
  <section class="titulo">
    <div><span class="ante">Hackathon ISAC 2026 · La historia de un entrenador a través de los datos</span>
      <h1>André Jardine en el <span class="club">América</span>, leído frente a cada rival</h1></div>
    <button type="button" class="btn-explorar" data-vista="explorar">Explorar por rival<span>→</span></button>
  </section>
  <section class="ejemplo">
    <div class="col"><span class="etq-p">Pilar 1 · Espacio</span><p>Ejemplo: @@EJEMPLO@@</p><span class="uno" aria-hidden="true">1</span></div>
    <div class="cont">
      <h2>Así se ve un dato con la identidad de Ojo de Águila</h2>
      <div class="figura">@@FIGURA_PORTADA@@</div>
      @@LEYENDA_FILA@@
      <p class="pie">@@QUE_MUESTRA@@</p>
    </div>
  </section>
  <section class="pilares">
    <div class="pilar"><span class="n">1</span><h3>Espacio</h3><p>Voronoi sobre el 360: qué zona controla cada equipo en cada acción clave.</p></div>
    <div class="pilar"><span class="n">2</span><h3>Validación</h3><p>Lo aprendido en AP23–AP25 se prueba en el Clausura 2026, que el modelo no vio.</p></div>
    <div class="pilar"><span class="n">3</span><h3>Decisión</h3><p>Matriz de situaciones y ficha de 10 segundos por rival.</p></div>
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
      <p class="maqueta">Maqueta con un caso real: los filtros cambian de estado, pero todavía no recalculan la vista. Se muestra «@@TITULO@@».</p>
      <div class="principal">
        <div class="figura">@@FIGURA_EXPLORAR@@</div>
        <aside class="panel" aria-label="Cómo leerla">
          <header>Cómo leerla<i aria-hidden="true"></i></header>
          <section><span class="etq-p">Leyenda</span>@@LEYENDA_COLUMNA@@</section>
          <section><span class="etq-p">Qué muestra</span><p>@@QUE_MUESTRA@@</p></section>
          <section><span class="etq-p lectura">Lectura frente a @@RIVAL@@</span><div class="espacio">@@LECTURA@@</div></section>
          <section><span class="etq-p">Cómo se calcula</span><div class="espacio">@@METODO@@</div></section>
        </aside>
      </div>

      <section class="bloque"><div class="datos">@@CHIPS@@</div></section>
      <section class="bloque"><span class="ante chico">1 · El partido hasta aquí</span>
        <h2>Los quiebres que llevaron a este momento</h2><ul class="quiebres">@@QUIEBRES@@</ul></section>
      <section class="bloque"><span class="ante chico">2 · A dos bandas</span><h2>Quién mandaba, tramo a tramo</h2>
        <p class="pie">Dorado: @@EQUIPO@@. Blanco: @@RIVAL@@. Tramos de 5 minutos; las verticales son los quiebres (continuas: goles y expulsiones).</p>
        <div class="figura">@@LINEA_TIEMPO@@</div></section>
      <section class="bloque"><span class="ante chico">3 · Los minutos previos</span><h2>Los últimos 10 minutos frente a todo el partido</h2>
        <div class="tabla-scroll"><table>@@TABLA@@</table></div></section>
      <section class="bloque"><span class="ante chico">4 · La jugada</span><h2>Los segundos que llevan al quiebre</h2>
        <ul class="cadena">@@CADENA@@</ul>
        <p class="pie">Cada cancha es la foto 360 de esa acción, con @@EQUIPO@@ atacando hacia la derecha. El anillo marca a quien ejecuta; la línea blanca, dónde chocan los equipos.</p>
        <div class="jugadas">@@JUGADAS@@</div></section>
      <section class="bloque"><span class="ante chico">5 · El protagonista</span><h2>@@PROTAGONISTA@@ antes del quiebre</h2>
        <div class="dos"><div class="figura">@@FIGURA_PROTAGONISTA@@</div>
          <div class="bloque" style="margin:0"><ul class="lista">@@RESUMEN_PROTAGONISTA@@</ul>
            <p class="nota">Puntos grandes: acciones sin balón (presión, duelos, recuperaciones, faltas). Chicos: con balón. Resaltados: los minutos recientes. X: faltas.</p></div></div></section>
      <section class="bloque hasta"><h2>Hasta aquí</h2><ul class="lista">@@CIERRE@@</ul></section>
      <section class="bloque">@@NOTAS@@</section>
    </div>
  </div>
</div>
</main>

<script src="@@MARCA@@/dist/vendor/react.production.min.js"></script>
<script src="@@MARCA@@/dist/vendor/react-dom.production.min.js"></script>
<script src="@@MARCA@@/dist/marca.js"></script>
<script>
  (function () {
    var cuerpo = document.body;
    var reducir = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (window.OjoMarca) OjoMarca.loop(document.getElementById('loop-icono'), { estatico: reducir });

    // Vistas: portada / explorar (también desde el hash, para poder compartir el enlace)
    function mostrar(vista) {
      cuerpo.dataset.vista = vista;
      document.querySelectorAll('nav.vistas [data-vista]').forEach(function (b) {
        if (b.dataset.vista === vista) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current');
      });
      if (location.hash !== '#' + vista) history.replaceState(null, '', '#' + vista);
      cerrarCajon();
      window.scrollTo(0, 0);
    }
    document.querySelectorAll('[data-vista]').forEach(function (b) {
      if (b.tagName === 'BUTTON') b.addEventListener('click', function () { mostrar(b.dataset.vista); });
    });
    mostrar(location.hash === '#explorar' ? 'explorar' : 'portada');

    // Barra lateral (maqueta): los controles cambian de estado sin recalcular la vista
    document.querySelectorAll('[data-toggle]').forEach(function (b) {
      b.addEventListener('click', function () { b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); });
    });
    document.querySelectorAll('.partido-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        document.querySelectorAll('.partido-btn').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      });
    });
    document.querySelectorAll('.seg').forEach(function (b) {
      b.addEventListener('click', function () {
        document.querySelectorAll('.seg').forEach(function (o) { o.setAttribute('aria-checked', o === b ? 'true' : 'false'); });
      });
    });
    var nombre = document.getElementById('rival-nombre'), conteo = document.getElementById('rival-n');
    document.querySelectorAll('.rival-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        var antes = [nombre.textContent, parseInt(conteo.textContent, 10)];
        nombre.textContent = b.dataset.rival; conteo.textContent = b.dataset.n + ' partidos';
        nombre.style.fontSize = Math.min(@@PLACA_MAX@@, Math.floor(@@PLACA_ANCHO@@ / (@@PLACA_EM@@ * b.dataset.rival.length))) + 'px';
        b.dataset.rival = antes[0]; b.dataset.n = antes[1];
        b.firstElementChild.textContent = antes[0]; b.lastElementChild.textContent = antes[1];
        cerrarCajon();
      });
    });
    document.querySelectorAll('[data-volver]').forEach(function (b) { b.addEventListener('click', function () { location.reload(); }); });
    document.querySelectorAll('.filtro').forEach(function (b) { b.addEventListener('click', function () { b.remove(); }); });

    // Cajón de filtros en pantallas chicas
    function cerrarCajon() { cuerpo.classList.remove('cajon'); }
    document.querySelectorAll('[data-cajon]').forEach(function (b) {
      b.addEventListener('click', function () { cuerpo.classList.toggle('cajon'); });
    });
    window.addEventListener('keydown', function (e) { if (e.key === 'Escape') cerrarCajon(); });

    // Entrada animada
    var intro = document.getElementById('intro');
    if (!window.__ojoMostrarIntro || !window.OjoMarca) { intro.remove(); document.documentElement.classList.remove('con-intro'); return; }
    var control = null, cerrada = false;
    function cerrar() {
      if (cerrada) return; cerrada = true;
      intro.classList.add('saliendo'); document.documentElement.classList.remove('con-intro');
      setTimeout(function () { if (control) control.detener(); intro.remove(); }, 650);
    }
    control = OjoMarca.intro(document.getElementById('intro-lienzo'), { segundos: 5, alTerminar: cerrar });
    intro.addEventListener('click', cerrar);
    window.addEventListener('keydown', function (e) { if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') cerrar(); });
  })();
</script>
</body>
</html>
"""
