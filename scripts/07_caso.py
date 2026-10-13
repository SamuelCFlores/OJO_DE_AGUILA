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
from ojo.salidas import caso as sc

SALIDA = DIR_SALIDAS / "reportes" / "maqueta_2.html"
ETAPAS = {"Semi-finals": "Semifinal", "Quarter-finals": "Cuartos de final", "Final": "Final", "Play-offs": "Repechaje"}
METRICAS_TABLA = {  # métrica de ojo.lentes.minuto → (nombre, formato)
    "presiones": ("Presiones/min", "{:.2f}"), "presiones_campo_rival": ("Presiones en campo rival/min", "{:.2f}"),
    "faltas": ("Faltas/min", "{:.2f}"), "xg": ("xG/min", "{:.3f}"), "field_tilt": ("Field tilt", "{:.0%}"),
    "control_campo_rival": ("Control en campo rival (Voronoi)", "{:.0%}"),
    "tiros_transicion_contra": ("Tiros en transición en contra/min", "{:.3f}"),
}


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
    texto_cadena, jugadas, posesion = [], [], None
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
                jugadas.append(sc.Jugada(sc.reloj(c.minuto, c.segundo), texto, del_equipo, resultado.control,
                                         sc.figura_jugada(resultado, o, del_equipo)))
    jugadas = jugadas[-p["casos"]["max_jugadas"]:]

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
    subtitulo = f"Caso · {etapa_legible(info['etapa'], ida is not None)} · {info['local']} vs {info['visitante']} · {fecha}"

    pagina = sc.html(sc.Caso(titulo, subtitulo, equipo, chips, lista_quiebres, figura_tiempo, tabla, texto_cadena, jugadas,
                             protagonista, figura_prot, resumen, cierre, notas),
                     ruta_marca=os.path.relpath(RAIZ / "branding", SALIDA.parent).replace(os.sep, "/"))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(pagina, encoding="utf-8")
    print(f"Caso: {titulo}\nPágina: {SALIDA.relative_to(RAIZ)} (datos reales: no se publica ni se sube a git)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
