"""Caso puntual: lee un partido hasta un punto de quiebre y lo deja en una página con la identidad (maqueta_2).

Elige el quiebre por partido y tipo (el primero de ese tipo, o el n-ésimo con --n) y construye la
página hasta ese momento: quiebres previos, línea de tiempo a dos bandas, minutos previos frente al
partido, la cadena de jugadas con su Voronoi y las acciones del protagonista. Escribe
outputs/reportes/maqueta_2.html (fuera de git: lleva posiciones y nombres reales); la barra, la
entrada y el ícono salen de branding/dist, igual que branding/maqueta.html.

Cómo correrlo (desde la raíz del repo y con el entorno activado; antes 03, 04 y 05):
    python scripts/07_caso.py --partido 3886547 --tipo expulsion_contra
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

from ojo.config import DIR_SALIDAS, RAIZ, params
from ojo.datos import almacen, crudo
from ojo.framework import contexto, quiebres
from ojo.framework import partidos as fp
from ojo.lentes import minuto, voronoi
from ojo.salidas import app
from ojo.salidas import caso as sc
from ojo.salidas.resumenes import SITUACIONES

SALIDA = DIR_SALIDAS / "reportes" / "maqueta_2.html"
ETAPAS = {"Semi-finals": "Semifinal", "Quarter-finals": "Cuartos de final", "Final": "Final", "Play-offs": "Repechaje"}
METRICAS_TABLA = {  # métrica de ojo.lentes.minuto → (nombre, formato)
    "presiones": ("Presiones/min", "{:.2f}"), "presiones_campo_rival": ("Presiones en campo rival/min", "{:.2f}"),
    "faltas": ("Faltas/min", "{:.2f}"), "xg": ("xG/min", "{:.3f}"), "field_tilt": ("Field tilt", "{:.0%}"),
    "control_campo_rival": ("Control en campo rival (Voronoi)", "{:.0%}"),
    "tiros_transicion_contra": ("Tiros en transición en contra/min", "{:.3f}"),
}


GRUPOS_SITUACION = {"todas": "General", "fase": "Fase", "marcador": "Marcador", "balon_parado": "Balón parado"}
ESTADO_SITUACION = {"gana": "Ganando", "empata": "Empatando", "pierde": "Perdiendo"}
# Situaciones "tras un quiebre" (propuesta para el contrato de resumenes.json): una por tipo, sin separar propio/rival
# salvo en goles y expulsiones, donde importa quién lo sufre.
ETIQUETA_SITUACION = {
    "gol_favor": "Tras gol a favor", "gol_contra": "Tras gol en contra", "expulsion_favor": "Expulsión a favor",
    "expulsion_contra": "Expulsión en contra", "cambio_sistema_propio": "Cambio de sistema",
    "cambio_sistema_rival": "Cambio de sistema", "sustitucion_tactica_propia": "Cambio táctico",
    "sustitucion_tactica_rival": "Cambio táctico", "sustitucion_lesion_propia": "Cambio por lesión",
    "sustitucion_lesion_rival": "Cambio por lesión",
}
MAX_RIVALES_LISTA = 6  # rivales en la lista de la barra, además del seleccionado (presentación)


def corto(nombre: str) -> str:
    """"Fernando Ortiz" → "Ortiz"; "André Soares Jardine" → "Jardine"."""
    return str(nombre).split(" ")[-1]


def condicion(localia: str) -> str:
    return {"local": "Local", "visitante": "Visita"}.get(str(localia), "Todos")


def etiqueta_partido(partidos: pd.DataFrame, fila: pd.Series) -> str:
    """"Semifinal · vuelta", "Semifinal · ida" o "Fase regular" para la lista de partidos de la barra."""
    partes = [ETAPAS.get(x.strip(), x.strip()) for x in str(fila["etapa"] or "").split(" - ")]
    fase = next((x for x in partes if x in ETAPAS.values()), None)
    if fase is None:
        return "Fase regular"
    misma = partidos[(partidos["rival_id"] == fila["rival_id"]) & (partidos["torneo_corto"] == fila["torneo_corto"])
                     & (partidos["etapa"] == fila["etapa"])]
    if len(misma) < 2:
        return fase
    return f"{fase} · {'vuelta' if fila['fecha'] == misma['fecha'].max() else 'ida'}"


def armar_barra(partidos: pd.DataFrame, info: pd.Series, q: pd.Series, eliminatoria: bool, control: float,
                xg: pd.Series, gfg: int | None, gcg: int | None, n_jugadas: int, equipo: str, team: int) -> app.Barra:
    """Barra lateral con el estado del caso: rival, entrenador, torneo, partido, situación y condición."""
    p = params()
    ids = {d["manager_id"]: corto(d["nombre"]) for d in [*p["predecesores"], p["entrenador"]]}
    conteo = partidos.groupby("rival").size().sort_values(ascending=False)
    rivales = [(r, int(n)) for r, n in conteo.items() if r != info["rival"]][:MAX_RIVALES_LISTA]
    torneos = partidos.sort_values("fecha").drop_duplicates("torneo_corto")
    lista_torneos = [(t, t == info["torneo_corto"], bool(pr)) for t, pr in zip(torneos["torneo_corto"], fp.es_prueba(torneos))]
    del_rival = partidos[(partidos["rival_id"] == info["rival_id"]) & (partidos["torneo_corto"] == info["torneo_corto"])]
    lista_partidos = [(pd.Timestamp(r.fecha).strftime("%d/%m"), etiqueta_partido(partidos, pd.Series(r._asdict())),
                       f"{int(r.goles_favor)}-{int(r.goles_contra)}", r.match_id == info["match_id"])
                      for r in del_rival.sort_values("fecha").itertuples()]
    activa = ETIQUETA_SITUACION.get(q["tipo"])
    estado = ESTADO_SITUACION.get(q["estado_antes"])
    grupos: dict[str, list[tuple[str, bool]]] = {}
    for s in SITUACIONES:
        grupos.setdefault(GRUPOS_SITUACION.get(s["grupo"], s["grupo"]), []).append((s["etiqueta"], s["etiqueta"] == estado))
    grupos["Tras un quiebre"] = [(x, x == activa) for x in dict.fromkeys(ETIQUETA_SITUACION.values())]
    resumen = [("Control en la foto", f"{control:.0%} · {1 - control:.0%}"),
               (f"xG hasta el {q['minuto']}'", f"{xg.get(team, 0):.2f} · {xg.get(info['rival_id'], 0):.2f}")]
    if gfg is not None:
        resumen.append(("Global en ese momento", f"{gfg}-{gcg}"))
    return app.Barra(
        rival=info["rival"], partidos_rival=int(conteo.get(info["rival"], 0)), rivales=rivales,
        entrenadores=[(n, i == info["entrenador_id"]) for i, n in ids.items()], torneos=lista_torneos,
        partidos=lista_partidos, situaciones=list(grupos.items()), condicion=condicion(info["localia"]),
        muestra=f"1 partido · {n_jugadas} jugadas con foto 360 en la cadena", resumen=resumen)


def lectura_del_caso(texto_cadena: list[tuple[str, str, bool]], e: pd.Series, noms: dict, nombre_equipo: dict,
                     protagonista: str, control: float, equipo: str, reloj_caso: str) -> str:
    """Lectura corta del momento: la pérdida previa, la jugada del rival y la acción del protagonista."""
    inicios = [i for i, (r, _, _) in enumerate(texto_cadena) if not r]
    ultima = inicios[-1] if inicios else 0
    previas = [t for r, t, _ in texto_cadena[:ultima] if r]
    jugada = [t for r, t, _ in texto_cadena[ultima + 1:]]
    propias = [t[len(protagonista) + 1:] for t in jugada if t.startswith(protagonista + " ")]
    ajenas = [t for t in jugada if not t.startswith(protagonista + " ") and " presiona" not in t]
    partes = [f"{reloj_caso}."]
    if previas:
        partes.append(f"Tras «{previas[-1]}»,")
    if len(ajenas) > 1:  # la primera y la última acción del rival cuentan la jugada sin listarla toda
        partes.append(f"{ajenas[0]} y, después, {ajenas[-1]}.")
    elif ajenas:
        partes.append(f"{ajenas[0]}.")
    if propias:
        partes.append(f"{protagonista} " + " y ".join(propias) + ".")
    partes.append(f"En esa foto, el {equipo} controlaba el {control:.0%} del espacio que se disputaba.")
    return " ".join(partes)


def minuscula(texto: str) -> str:
    """Primera letra en minúscula, sin tocar nombres propios."""
    return texto[:1].lower() + texto[1:]


def plural(n: int, singular: str, varios: str) -> str:
    return f"{n} {singular if n == 1 else varios}"


def etapa_legible(etapa: str | None, vuelta: bool) -> str:
    """"Clausura - Semi-finals" → "Clausura · Semifinal de vuelta"."""
    partes = [p.strip() for p in (etapa or "").split(" - ")]
    texto = " · ".join(ETAPAS.get(p, p) for p in partes if p)
    return texto + (" de vuelta" if vuelta else "")


def ida_de(partidos: pd.DataFrame, info: pd.Series) -> pd.Series | None:
    """Partido de ida de una eliminatoria: mismo rival, torneo y etapa, jugado antes."""
    if not any(k in (info["etapa"] or "") for k in ETAPAS):
        return None
    previos = partidos[(partidos["rival_id"] == info["rival_id"]) & (partidos["torneo_corto"] == info["torneo_corto"])
                       & (partidos["etapa"] == info["etapa"]) & (partidos["fecha"] < info["fecha"])]
    return previos.iloc[-1] if not previos.empty else None


def tabla_minutos_previos(panel: pd.DataFrame, q: pd.Series, desde: int, equipo: str, rival: str) -> pd.DataFrame:
    """Tabla para la página: métricas de los minutos [desde, minuto del quiebre − 1] y del partido hasta él.

    NOTA1: a diferencia del notebook 02, aquí la ventana no se corta en el quiebre anterior: se quiere
    ver todo el tramo que lleva al momento, aunque incluya un gol.
    """
    m = sc.antes_frente_al_partido(panel, (q["periodo"], desde, q["minuto"] - 1), q["periodo"], q["minuto"])
    m = m.set_index(["clave", "lado"])
    ventana = f"{desde}'–{q['minuto'] - 1}'"
    columnas = {(ventana, minuto.PROPIO): f"{equipo} · {ventana}", ("partido hasta ahí", minuto.PROPIO): f"{equipo} · partido",
                (ventana, minuto.RIVAL): f"{rival} · {ventana}", ("partido hasta ahí", minuto.RIVAL): f"{rival} · partido"}
    m = m.rename(index={"últimos minutos": ventana}, level="clave")
    filas = {}
    for metrica, (nombre, formato) in METRICAS_TABLA.items():
        filas[nombre] = [formato.format(m.loc[k, metrica]) if k in m.index and pd.notna(m.loc[k, metrica]) else "—"
                         for k in columnas]
    return pd.DataFrame.from_dict(filas, orient="index", columns=list(columnas.values()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--partido", type=int, required=True, metavar="MATCH_ID")
    parser.add_argument("--tipo", choices=quiebres.TIPOS, default="expulsion_contra", metavar="TIPO",
                        help=f"tipo de quiebre: {', '.join(quiebres.TIPOS)}")
    parser.add_argument("--n", type=int, default=1, help="cuál quiebre de ese tipo (1 = el primero)")
    parser.add_argument("--titulo", help="título de la página (por defecto se arma con el quiebre)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    p = params()
    team, equipo = p["equipo"]["team_id"], p["equipo"]["nombre"]
    partidos = fp.con_torneo(fp.del_equipo(fp.validos(almacen.cargar("partidos")), team))
    if args.partido not in set(partidos["match_id"]):
        print("✗ Ese partido no es un partido válido del equipo de params.yaml.")
        return 1
    info = partidos[partidos["match_id"] == args.partido].iloc[0]
    rival = info["rival"]
    ev = almacen.cargar("eventos", [args.partido]).sort_values("indice").reset_index(drop=True)
    todos_q = quiebres.ventanas(quiebres.detectar(ev, team), quiebres.limites_periodo(ev))
    del_tipo = todos_q[todos_q["tipo"] == args.tipo]
    if len(del_tipo) < args.n:
        print(f"✗ El partido tiene {len(del_tipo)} quiebres de tipo {args.tipo}.")
        return 1
    q = del_tipo.iloc[args.n - 1]
    e = ev[ev["indice"] == q["indice"]].iloc[0]
    noms = sc.nombres(crudo.leer("lineups", match_id=args.partido))
    nombre_equipo = {team: equipo, info["rival_id"]: rival}
    protagonista = noms.get(e["jugador_id"], nombre_equipo.get(e["equipo_id"], ""))

    # Marcador y global en el momento del quiebre
    marcador = contexto.marcador(ev, team).loc[e.name]
    gf, gc = int(marcador["goles_favor"]), int(marcador["goles_contra"])
    ida = ida_de(partidos, info)
    chips = [("Marcador", f"{equipo} {gf}-{gc} {rival}")]
    if ida is not None:
        gfg, gcg = gf + int(ida["goles_favor"]), gc + int(ida["goles_contra"])
        chips.append(("Global", f"{equipo} {gfg}-{gcg} {rival}"))
    chips += [("Minuto", sc.reloj(e["minuto"], e["segundo"])), ("En la banca", str(info["entrenador"]).split(" ")[0] + " "
               + str(info["entrenador"]).split(" ")[-1]), ("Localía", str(info["localia"]).capitalize())]

    previos = todos_q[todos_q["indice"] <= q["indice"]]
    lista_quiebres = [(f"{r.minuto}'", sc.etiqueta_quiebre(r, equipo, rival) + (f" ({noms.get(ev.loc[ev['indice'] == r.indice, 'jugador_id'].iloc[0], '')})"
                       if r.tipo.startswith(("gol", "expulsion")) else ""), r.indice == q["indice"])
                      for r in previos.itertuples()]

    # Panel por minuto (05); sin él se arma sin 360
    archivo = minuto.DIR_PANEL / "minuto" / f"{args.partido}.parquet"
    panel = pd.read_parquet(archivo) if archivo.exists() else minuto.panel_partido(ev, team)
    hasta_quiebre = panel[(panel["periodo"] < q["periodo"]) | ((panel["periodo"] == q["periodo"]) & (panel["minuto"] <= q["minuto"]))]
    figura_tiempo = sc.linea_tiempo(hasta_quiebre, previos, equipo, rival)
    inicio_periodo = int(ev.loc[ev["periodo"] == q["periodo"], "minuto"].min())
    desde_tabla = max(int(q["minuto"]) - p["quiebres"]["ventana_min"], inicio_periodo)
    tabla = tabla_minutos_previos(panel, q, desde_tabla, equipo, rival)

    # Cadena de jugadas con su Voronoi
    cadena = sc.cadena(ev, q["indice"])
    orientada = contexto.orientar(cadena, team)
    frames = almacen.cargar("frames", [args.partido]).set_index("event_uuid")
    jugadores = almacen.cargar("frames_jugadores", [args.partido])
    texto_cadena, jugadas, posesion, principal = [], [], None, None
    for c, o in zip(cadena.itertuples(), orientada.itertuples()):
        del_equipo = c.equipo_id == team
        if c.posesion != posesion:
            duena = nombre_equipo.get(c.posesion_equipo_id, "")
            # Si la posesión arranca con una recuperación, el play_pattern hereda la jugada anterior (p. ej. el saque de banda rival).
            como = ("recupera el balón" if c.tipo in {"Ball Recovery", "Interception", "Duel"}
                    else sc.PATRONES.get(c.patron, c.patron))
            texto_cadena.append(("", f"Posesión de {duena}: {como}", c.posesion_equipo_id == team))
            posesion = c.posesion
        texto = sc.describir(c, noms, nombre_equipo)
        texto_cadena.append((sc.reloj(c.minuto, c.segundo), texto, del_equipo))
        if c.id in frames.index:
            todos, area = sc.frame_del_equipo(jugadores[jugadores["event_uuid"] == c.id], frames.loc[c.id, "area_visible"], del_equipo)
            resultado = voronoi.analizar_frame(todos, area)
            if resultado is not None:
                jugada = sc.Jugada(sc.reloj(c.minuto, c.segundo), texto, del_equipo, resultado, o)
                jugadas.append(jugada)
                if c.indice == q["indice"]:
                    principal = jugada
    if not jugadas:
        print("✗ Ninguna jugada de la cadena tiene un frame 360 analizable.")
        return 1
    jugadas = jugadas[-p["casos"]["max_jugadas"]:]
    if principal is None:  # sin frame analizable del quiebre, la última jugada que sí lo tiene
        principal = jugadas[-1]

    # Protagonista: sus acciones hasta el quiebre
    acciones = ev[(ev["jugador_id"] == e["jugador_id"]) & (ev["indice"] <= q["indice"]) & ev["tipo"].isin(sc.VERBOS)]
    acciones_o = contexto.orientar(acciones, team)
    # Reciente = desde el quiebre que corta anterior (si cayó en la ventana) o los últimos ventana_min minutos.
    cortes = todos_q[todos_q["corta"] & (todos_q["periodo"] == q["periodo"]) & (todos_q["indice"] < q["indice"])
                     & (todos_q["minuto"] >= q["minuto"] - p["quiebres"]["ventana_min"])]
    if not cortes.empty:
        c0 = cortes.iloc[-1]
        desde_reciente, texto_reciente = int(c0["minuto"]), f"Desde el {minuscula(sc.etiqueta_quiebre(c0, equipo, rival))} ({c0['minuto']}')"
    else:
        desde_reciente, texto_reciente = desde_tabla, f"En los últimos {int(q['minuto']) - desde_tabla} minutos"
    reciente = (acciones["periodo"] == q["periodo"]) & (acciones["minuto"] >= desde_reciente)
    sin_balon = acciones["tipo"].isin(sc.SIN_BALON)
    minutos_recientes = int(q["minuto"]) - desde_reciente + 1
    inicio = acciones.iloc[0]
    minutos_totales = (sum(contexto.FIN_PERIODO[pp] - contexto.INICIO_PERIODO[pp] for pp in range(int(inicio["periodo"]), int(q["periodo"])))
                       + q["minuto"] - contexto.INICIO_PERIODO[int(q["periodo"])] - (inicio["minuto"] - contexto.INICIO_PERIODO[int(inicio["periodo"])]) + 1)
    tasa_reciente = (reciente & sin_balon).sum() / minutos_recientes * 10
    tasa_antes = (~reciente & sin_balon).sum() / max(minutos_totales - minutos_recientes, 1) * 10
    conteo = acciones[sin_balon]["tipo"].value_counts()
    resumen = [
        f"{int(sin_balon.sum())} acciones sin balón hasta el {q['minuto']}': {conteo.get('Pressure', 0)} presiones, "
        f"{conteo.get('Duel', 0)} duelos, {conteo.get('Ball Recovery', 0) + conteo.get('Interception', 0)} recuperaciones "
        f"y {plural(conteo.get('Foul Committed', 0), 'falta', 'faltas')}.",
        f"{texto_reciente}: {int((reciente & sin_balon).sum())} acciones sin balón en {minutos_recientes} minutos, "
        f"{tasa_reciente:.1f} cada 10 minutos frente a {tasa_antes:.1f} antes.",
    ]
    if (reciente & sin_balon).any() and (~reciente & sin_balon).any():
        delta = acciones_o.loc[reciente & sin_balon, "x"].mean() - acciones_o.loc[~reciente & sin_balon, "x"].mean()
        resumen.append(f"Sus acciones sin balón recientes fueron {abs(delta):.0f} yd más {'arriba' if delta > 0 else 'atrás'} "
                       "que en el resto del partido.")
    eo = contexto.orientar(ev[ev["indice"] == q["indice"]], team).iloc[0]
    campo = p["campo"]
    resumen.append(f"La acción del quiebre fue en {'campo rival' if eo['x'] >= campo['largo'] / 2 else 'campo propio'}, "
                   f"a {np.hypot(campo['largo'] - eo['x'], campo['ancho'] / 2 - eo['y']):.0f} yd de la portería rival.")
    figura_prot = sc.figura_protagonista(acciones_o, (int(q["periodo"]), desde_reciente), e["equipo_id"] == team)

    # Cierre
    xg = ev[(ev["indice"] <= q["indice"]) & (ev["tipo"] == "Shot")].groupby("equipo_id")["tiro_xg"].sum()
    siguiente = ev[(ev["indice"] > q["indice"]) & ~ev["tipo"].isin(["Foul Won", "Injury Stoppage", "Bad Behaviour",
                                                                    "Substitution", "Tactical Shift", "Player Off",
                                                                    "Player On"])]
    cierre = [f"Marcador {equipo} {gf}-{gc} {rival}" + (f"; global {gfg}-{gcg}." if ida is not None else ".")]
    fin = contexto.FIN_PERIODO.get(int(q["periodo"]))
    if fin and q["minuto"] < fin:
        extra = " con 10 jugadores" if args.tipo == "expulsion_contra" else (" contra 10" if args.tipo == "expulsion_favor" else "")
        cierre.append(f"Quedan unos {fin - q['minuto']} minutos más el añadido{extra}.")
    cierre.append(f"xG hasta aquí: {equipo} {xg.get(team, 0):.2f} · {rival} {xg.get(info['rival_id'], 0):.2f}.")
    notas = []
    if not siguiente.empty:
        s = siguiente.iloc[0]
        pausa = (s["minuto"] * 60 + s["segundo"]) - (e["minuto"] * 60 + e["segundo"])
        if s["periodo"] == e["periodo"] and pausa >= 60:
            cierre.append(f"El juego estuvo detenido {pausa // 60} min {pausa % 60:02d} s: se reanudó en el "
                          f"{sc.reloj(s['minuto'], s['segundo'])}.")
            notas.append(f"El minuto es el de StatsBomb para la acción ({sc.reloj(e['minuto'], e['segundo'])}); "
                         "la tarjeta o la reanudación pueden verse más tarde en la transmisión.")
    cierre.append("Siguiente paso: qué pasó después y qué decía la lectura por quiebres en ese momento.")
    notas.append("Página con datos reales de StatsBomb: solo para la competencia; no se sube a git ni se publica.")

    if args.titulo:
        titulo = args.titulo
    elif args.tipo.startswith("expulsion"):
        titulo = f"La expulsión de {protagonista}: cómo se llegó al {q['minuto']}'"
    elif args.tipo.startswith("gol"):
        titulo = f"El gol de {protagonista}: cómo se llegó al {q['minuto']}'"
    else:
        titulo = f"{sc.etiqueta_quiebre(q, equipo, rival)}: cómo se llegó al {q['minuto']}'"
    fecha = pd.Timestamp(info["fecha"]).strftime("%d/%m/%Y")
    etapa = etapa_legible(info["etapa"], ida is not None)
    reloj_caso = sc.reloj(e["minuto"], e["segundo"])

    # Textos del panel "Cómo leerla"
    que_muestra = (f"La foto 360 del momento del quiebre ({reloj_caso}): cada zona es del jugador que la tiene más cerca. "
                   f"Dorado: {equipo}; blanco: {rival}; la línea blanca marca dónde chocan los equipos. "
                   f"El anillo señala a quien ejecuta y {equipo} ataca hacia la derecha.")
    lectura = lectura_del_caso(texto_cadena, e, noms, nombre_equipo, protagonista, principal.control, equipo, reloj_caso)
    lectura += " " + resumen[1]
    v = p["voronoi"]
    area_cancha = p["campo"]["largo"] * p["campo"]["ancho"]
    metodo = (f"Foto 360 de StatsBomb de la acción ({reloj_caso}). Se ve el {principal.resultado.visible.area / area_cancha:.0%} "
              f"de la cancha y cuentan {len(principal.resultado.jugadores)} jugadores (se quitan los que están a menos de "
              f"{v['min_dist_borde']:g} yd del borde de la toma). Cada zona llega hasta {v['alcance_max_yd']:g} yd de su jugador. "
              f"Control = área de {equipo} ÷ área que se disputa. {len(jugadas)} fotos analizadas en la cadena; la línea de "
              f"tiempo usa el panel por minuto en tramos de {p['casos']['tramo_min']} minutos.")

    barra = armar_barra(partidos, info, q, ida is not None, principal.control, xg, gfg if ida is not None else None,
                        gcg if ida is not None else None, len(jugadas), equipo, team)
    filtros = [corto(info["entrenador"]), info["torneo_corto"], etiqueta_partido(partidos, info),
               ETIQUETA_SITUACION.get(args.tipo, sc.etiqueta_quiebre(q, equipo, rival)), condicion(info["localia"])]
    caso = app.Caso(
        titulo=titulo, antetitulo=f"Pilar 1 · Espacio · {info['torneo_corto']} · {etapa} · {fecha}", equipo=equipo,
        rival=rival, ejemplo=f"{equipo} vs {rival}: {minuscula(titulo.split(':')[0])}, {minuscula(etiqueta_partido(partidos, info)).replace(' · ', ' de ')} "
                                f"del {info['torneo']} {pd.Timestamp(info['fecha']).year}",
        filtros=filtros, que_muestra=que_muestra, lectura=lectura, metodo=metodo, chips=chips, quiebres=lista_quiebres,
        linea_tiempo=figura_tiempo, tabla_antes=tabla, cadena_texto=texto_cadena, jugadas=jugadas, principal=principal,
        protagonista=protagonista, figura_protagonista=figura_prot, resumen_protagonista=resumen, cierre=cierre,
        barra=barra, notas=notas)
    pagina = app.pagina(caso, ruta_marca=os.path.relpath(RAIZ / "branding", SALIDA.parent).replace(os.sep, "/"))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(pagina, encoding="utf-8")
    print(f"Caso: {titulo}\nPágina: {SALIDA.relative_to(RAIZ)} (datos reales: no se publica ni se sube a git)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
