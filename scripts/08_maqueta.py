"""Datos de la maqueta 3 (app/maqueta.html): la narrativa de Jardine (principio → caso → reproductor).

Arma: el índice Proactivo–Reactivo de todos los partidos (escala con los torneos de entrenamiento), los
principios candidatos (outputs/hallazgos, notebooks 02 y 03), el caso confirmador (un partido y un
quiebre), el reproductor minuto a minuto con su Voronoi y el Monte Carlo explicativo de los tiros.
Escribe solo datos: outputs/app/datos.js (fuera de git: lleva posiciones y nombres reales). El diseño vive en
app/ (maqueta.html, app.css y app.js) y se edita directo, sin Python.

Cómo correrlo (desde la raíz del repo y con el entorno activado; antes 03, 04, 05 y los notebooks 02 y 03):
    python scripts/08_maqueta.py --partido 3918375 --tipo expulsion_favor
y abrir app/maqueta.html (doble clic, o con el servidor de .claude/launch.json en /app/maqueta.html).
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

import numpy as np
import pandas as pd

from ojo.config import DIR_SALIDAS, RAIZ, params
from ojo.datos import almacen, crudo
from ojo.framework import contexto, quiebres
from ojo.framework import partidos as fp
from ojo.lentes import indice, minuto, simulacion, voronoi
from ojo.salidas import barra as sb
from ojo.salidas import caso as sc
from ojo.salidas import datos_app, reproductor

DIR_HALLAZGOS = DIR_SALIDAS / "hallazgos"
COLUMNAS_INDICE = ["match_id", "periodo", "minuto", "equipo_id", "tipo", "duracion", "es_transicion", "directness",
                   "x", "y", "fin_x", "fin_y"]
FORMATOS = {"control": "pct", "posesion": "pct", "field_tilt": "pct", "control_campo_rival": "pct",
            "altura_sin_balon": "yd", "presion_alta": "num", "directness": "num", "largo_pase": "yd"}
CLAVES_CORTAS = {"gol_favor": "Gol", "gol_contra": "Gol rival", "expulsion_favor": "Roja rival",
                 "expulsion_contra": "Roja", "cambio_sistema_propio": "Sistema", "cambio_sistema_rival": "Sistema rival"}
# Principios candidatos: de dónde sale cada número y cómo se lee (notebooks 02 y 03, criterio v1).
PRINCIPIOS = [
    {"archivo": "estilo", "filtro": {"metrica": "largo_pase"}, "escala": 1, "unidad": " yd", "dec": 1, "cambio": False,
     "titulo": "Sale jugando corto",
     "frase": "Con Jardine, los pases del América miden {jardine} en promedio; con Solari y Ortiz, {previos}.",
     "significa": "Cambia el pelotazo por circulación corta, también desde su propio campo.",
     "uso": "Si el rival presiona alto, el plan del América es tocar para salir, no rifar el balón: la presión rival pone a prueba este principio."},
    {"archivo": "quiebres_contra_predecesores", "filtro": {"tipo": "expulsion_favor", "lado": "propio", "metrica": "field_tilt"},
     "escala": 100, "unidad": " pts", "dec": 0, "cambio": True, "tipo_caso": "expulsion_favor",
     "titulo": "Con uno más, se instala arriba",
     "frase": "Tras una expulsión del rival, el field tilt del América cambia {jardine} con Jardine; con Solari y Ortiz, {previos}.",
     "significa": "Con superioridad numérica no administra: se muda a campo rival y empuja al rival hacia su área.",
     "uso": "Con un jugador más, esperar un América volcado arriba; lo que hay que vigilar es la transición en contra."},
    {"archivo": "quiebres_contra_predecesores", "filtro": {"tipo": "gol_favor", "lado": "propio", "metrica": "tiros_transicion_contra"},
     "escala": 10, "unidad": " por 10 min", "dec": 2, "cambio": True, "tipo_caso": "gol_favor",
     "titulo": "Ganando, cierra la transición",
     "frase": "Tras anotar, los tiros en transición que concede cambian {jardine} con Jardine; con Solari y Ortiz, {previos}.",
     "significa": "Después de un gol a favor no se parte: protege la pérdida y le quita al rival el contragolpe.",
     "uso": "Cuando el América gana, el rival tiene que atacar en estático: la ficha debe decir cómo le va a ese rival sin transiciones."},
    {"archivo": "quiebres_contra_predecesores", "filtro": {"tipo": "gol_contra", "lado": "propio", "metrica": "obv"},
     "escala": 10, "unidad": " por 10 min", "dec": 3, "cambio": True, "tipo_caso": "gol_contra",
     "titulo": "Reacciona al gol en contra",
     "frase": "Tras recibir gol, el valor de sus acciones (OBV) cambia {jardine} con Jardine; con Solari y Ortiz, {previos}.",
     "significa": "Recibir gol no lo desordena: aumenta lo que produce con el balón.",
     "uso": "Si el América recibe gol, esperar más volumen con balón y no un repliegue; el rival que se adelanta debe prepararse para defender cerca de su área."},
    {"archivo": "quiebres_contra_predecesores", "filtro": {"tipo": "sustitucion_tactica_propia", "lado": "propio", "metrica": "control_campo_rival"},
     "escala": 100, "unidad": " pts", "dec": 1, "cambio": True, "tipo_caso": "sustitucion_tactica_propia",
     "titulo": "Sus cambios ganan espacio arriba",
     "frase": "Tras sus sustituciones tácticas, el espacio que controla en campo rival cambia {jardine} con Jardine; con Solari y Ortiz, {previos}.",
     "significa": "Sus cambios empujan al equipo hacia adelante, no lo repliegan.",
     "uso": "Los cambios de Jardine son para ganar territorio: el rival puede buscar la espalda justo después de ellos."},
]


def principios(caso_tipo: str, caso_texto: str) -> tuple[list[datos_app.Principio], datos_app.Principio | None]:
    """Tarjetas de los principios candidatos con sus números (si los notebooks ya se corrieron)."""
    tarjetas, del_caso = [], None
    for d in PRINCIPIOS:
        ruta = DIR_HALLAZGOS / f"{d['archivo']}.parquet"
        if not ruta.exists():
            continue
        t = pd.read_parquet(ruta)
        for k, v in d["filtro"].items():
            t = t[t[k] == v]
        if t.empty:
            continue
        f = t.iloc[0]
        nuevo, previo = (f["efecto_nuevo"], f["efecto_previos"]) if d["cambio"] else (f["nuevo"], f["previos"])
        fmt = (lambda v: f"{v * d['escala']:+.{d['dec']}f}{d['unidad']}") if d["cambio"] else (lambda v: f"{v * d['escala']:.{d['dec']}f}{d['unidad']}")
        dif = lambda v: f"{v * d['escala']:+.{d['dec']}f}{d['unidad']}"  # noqa: E731
        estado = "Candidato · pasa el criterio v1" if f["pasa"] else "No pasa el criterio v1"
        if f.get("muestra_chica", False):
            estado += " · muestra chica"
        p = datos_app.Principio(
            titulo=d["titulo"], frase=d["frase"].format(jardine=fmt(nuevo), previos=fmt(previo)), significa=d["significa"],
            uso=d["uso"], jardine=fmt(nuevo), previos=fmt(previo), diferencia=dif(f["diferencia"]),
            intervalo=f"IC 95 %: {dif(f['ic_bajo'])} a {dif(f['ic_alto'])}", torneos=f"{int(f['torneos_misma_direccion'])} de 5",
            estado=estado + " · falta v2 y placebo")
        if d.get("tipo_caso") == caso_tipo:
            p.caso = caso_texto
            del_caso = p
        tarjetas.append(p)
    return tarjetas, del_caso


def tabla_indice(partidos: pd.DataFrame) -> pd.DataFrame:
    """Índice por minuto y equipo de todos los partidos, con la escala de los torneos de entrenamiento."""
    ids = partidos["match_id"].astype(int).tolist()
    piezas = indice.piezas_por_minuto(almacen.cargar("eventos", ids, columnas=COLUMNAS_INDICE))
    comp = indice.componentes(minuto.cargar_panel("minuto").query("match_id in @ids"), piezas)
    entrenamiento = comp[comp["match_id"].isin(partidos.loc[~partidos["prueba"], "match_id"])]
    return indice.calcular(comp, indice.ajustar(entrenamiento))


def datos_reproductor(tab: pd.DataFrame, ev: pd.DataFrame, fotos: dict, jugada: dict | None, todos_q: pd.DataFrame,
                      equipo: str, rival: str, team: int, q: pd.Series) -> dict:
    """JSON del reproductor: un paso por minuto (índice, radar, componentes, marcador y foto) y la jugada."""
    comps = list(params()["indice"]["componentes"])
    a = tab[tab["lado"] == minuto.PROPIO].set_index(["periodo", "minuto"])
    r = tab[tab["lado"] == minuto.RIVAL].set_index(["periodo", "minuto"])
    marcador = contexto.marcador(ev, team).join(ev[["periodo", "minuto"]]).groupby(["periodo", "minuto"]).last()
    claves = sorted(set(a.index) | set(r.index))
    lista_fotos, minutos = [], []
    redondo = lambda v: None if pd.isna(v) else round(float(v), 3)  # noqa: E731
    for k, (p, m) in enumerate(claves):
        fa, fr = (a.loc[(p, m)] if (p, m) in a.index else None), (r.loc[(p, m)] if (p, m) in r.index else None)
        foto_k = None
        if (p, m) in fotos:
            lista_fotos.append(fotos[(p, m)])
            foto_k = len(lista_fotos) - 1
        g = marcador.loc[(p, m)] if (p, m) in marcador.index else None
        minutos.append({
            "p": int(p), "m": int(m), "etq": f"{m}'" if p <= 2 else f"{m}' (prórroga)",
            "ia": None if fa is None else redondo(fa["indice"]), "ir": None if fr is None else redondo(fr["indice"]),
            "za": [None if fa is None else redondo(fa[f"z_{c}"]) for c in comps],
            "zr": [None if fr is None else redondo(fr[f"z_{c}"]) for c in comps],
            "va": [None if fa is None else redondo(fa[c]) for c in comps],
            "vr": [None if fr is None else redondo(fr[c]) for c in comps],
            "marcador": "—" if g is None else f"{int(g['goles_favor'])}-{int(g['goles_contra'])}", "foto": foto_k,
        })
    pos = {c: k for k, c in enumerate(claves)}
    marcas = [{"k": pos[(r_.periodo, r_.minuto)], "corto": CLAVES_CORTAS[r_.tipo],
               "favor": r_.tipo.endswith(("favor", "propio", "propia")), "fuerte": r_.tipo.startswith(("gol", "expulsion"))}
              for r_ in todos_q.itertuples() if r_.tipo in CLAVES_CORTAS and (r_.periodo, r_.minuto) in pos]
    nombres_periodo = {1: "1T", 2: "2T", 3: "PR1", 4: "PR2"}
    etiquetas, vistos = [], set()
    for k, (p, m) in enumerate(claves):
        if p not in vistos:
            vistos.add(p)
            etiquetas.append({"k": k, "etq": f"{nombres_periodo.get(p, p)} {m}'", "periodo": True})
        elif m % 15 == 0 and m < contexto.FIN_PERIODO.get(p, 999) and m != contexto.INICIO_PERIODO.get(p):
            etiquetas.append({"k": k, "etq": f"{m}'", "periodo": False})
    if jugada is not None:
        jugada["minuto"] = pos.get(jugada.pop("clave"), 0)
    return {"equipo": equipo, "rival": rival, "componentes": [{"id": c, "nombre": indice.NOMBRES[c], "radar": indice.NOMBRES_RADAR[c], "formato": FORMATOS[c]} for c in comps],
            "minutos": minutos, "fotos": lista_fotos, "quiebres": marcas, "etiquetasX": etiquetas, "jugada": jugada,
            "inicio": pos.get((int(q["periodo"]), int(q["minuto"])), 0)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--partido", type=int, required=True, metavar="MATCH_ID")
    parser.add_argument("--tipo", choices=quiebres.TIPOS, default="expulsion_favor", metavar="TIPO")
    parser.add_argument("--n", type=int, default=1, help="cuál quiebre de ese tipo (1 = el primero)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    return generar(args)


def generar(args: argparse.Namespace) -> int:
    """Arma el contrato de datos de la maqueta 3 y escribe outputs/app/datos.js."""
    p = params()
    team, equipo = p["equipo"]["team_id"], p["equipo"]["nombre"]
    nuevo = sb.corto(p["entrenador"]["nombre"])
    partidos = fp.con_torneo(fp.del_equipo(fp.validos(almacen.cargar("partidos")), team))
    partidos = partidos[partidos["entrenador_id"].isin([d["manager_id"] for d in [*p["predecesores"], p["entrenador"]]])].copy()
    partidos["prueba"] = fp.es_prueba(partidos)
    partidos["entrenador_corto"] = partidos["entrenador_id"].map(sb.nombres_entrenadores())
    if args.partido not in set(partidos["match_id"]):
        print("✗ Ese partido no es un partido válido del equipo con Solari, Ortiz o Jardine.")
        return 1
    info = partidos[partidos["match_id"] == args.partido].iloc[0]
    rival = info["rival"]
    print("Calculando el índice de todos los partidos (unos 20 s)…")
    tab_todos = tabla_indice(partidos)

    # Portada: índice por torneo (sin el torneo de prueba) y cifras clave
    entr = tab_todos.merge(partidos[["match_id", "torneo_corto", "entrenador_corto", "prueba", "fecha"]], on="match_id")
    entr = entr[~entr["prueba"]]
    por_torneo = (entr.groupby(["torneo_corto", "entrenador_corto", "lado"])["indice"].mean().unstack("lado").reset_index()
                  .merge(partidos.groupby("torneo_corto")["fecha"].min().rename("inicio"), on="torneo_corto").sort_values("inicio"))
    por_torneo = por_torneo.rename(columns={"torneo_corto": "torneo", "entrenador_corto": "entrenador",
                                            minuto.PROPIO: "propio", minuto.RIVAL: "rival"})
    por_torneo = por_torneo.groupby("torneo", sort=False).agg(entrenador=("entrenador", "last"), propio=("propio", "mean"),
                                                             rival=("rival", "mean")).reset_index()
    medias = entr.groupby([entr["entrenador_corto"] == nuevo, "lado"])["indice"].mean().unstack("lado")
    n_nuevo = partidos[(partidos["entrenador_corto"] == nuevo) & ~partidos["prueba"]].shape[0]
    n_previos = partidos[(partidos["entrenador_corto"] != nuevo) & ~partidos["prueba"]].shape[0]

    # Caso: quiebre, marcador, global y protagonista
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
    marcador = contexto.marcador(ev, team).loc[e.name]
    gf, gc = int(marcador["goles_favor"]), int(marcador["goles_contra"])
    ida = sb.ida_de(partidos, info)
    etapa = sb.etapa_legible(info["etapa"], ida is not None)
    fecha = pd.Timestamp(info["fecha"]).strftime("%d/%m/%Y")
    chips = [("En ese momento", f"{equipo} {gf}-{gc} {rival}")]
    if ida is not None:
        chips.append(("Global en ese momento", f"{gf + int(ida['goles_favor'])}-{gc + int(ida['goles_contra'])}"))
        chips.append(("Global final", f"{int(info['goles_favor']) + int(ida['goles_favor'])}-{int(info['goles_contra']) + int(ida['goles_contra'])}"))
    chips += [("Final del partido", f"{int(info['goles_favor'])}-{int(info['goles_contra'])}"), ("Minuto", sc.reloj(e["minuto"], e["segundo"])),
              ("En la banca", info["entrenador_corto"])]
    clave_q = {"gol", "expulsion", "cambio_sistema"}
    lista_quiebres = [(f"{r.minuto}'", sc.etiqueta_quiebre(r, equipo, rival)
                       + (f" ({noms.get(ev.loc[ev['indice'] == r.indice, 'jugador_id'].iloc[0], '')})" if r.tipo.startswith(("gol", "expulsion")) else ""),
                       r.indice == q["indice"]) for r in todos_q.itertuples() if r.tipo.rsplit("_", 1)[0] in clave_q]

    # Reproductor: foto por minuto, jugada del primer gol a favor después del quiebre
    frames = almacen.cargar("frames", [args.partido])
    jugadores = almacen.cargar("frames_jugadores", [args.partido])
    describir = lambda x: sc.describir(x, noms, nombre_equipo)  # noqa: E731
    fotos = reproductor.por_minuto(ev, frames, jugadores, team, describir)
    tab = tab_todos[tab_todos["match_id"] == args.partido]
    goles = todos_q[(todos_q["tipo"] == "gol_favor") & (todos_q["indice"] > q["indice"])]
    jugada = None
    frames_i = frames.set_index("event_uuid")
    if not goles.empty:
        g0 = goles.iloc[0]
        cadena = sc.cadena(ev, g0["indice"])
        por_uuid = dict(tuple(jugadores.groupby("event_uuid")))
        lista = []
        for c in cadena.itertuples():
            if c.id in por_uuid and c.id in frames_i.index:
                todos, area = sc.frame_del_equipo(por_uuid[c.id], frames_i.loc[c.id, "area_visible"], c.equipo_id == team)
                res = voronoi.analizar_frame(todos, area)
                if res is not None:
                    lista.append(reproductor.foto(res, sc.reloj(c.minuto, c.segundo), describir(c), c.equipo_id == team))
        autor = noms.get(ev.loc[ev["indice"] == g0["indice"], "jugador_id"].iloc[0], "")
        jugada = {"titulo": f"El gol del {g0['minuto']}' ({autor})", "fotos": lista[-p["casos"]["max_jugadas"]:],
                  "clave": (int(g0["periodo"]), int(g0["minuto"]))}
    repro = datos_reproductor(tab, ev, fotos, jugada, todos_q, equipo, rival, team, q)

    # Foto destacada: la acción del equipo con más control en campo rival en la ventana después del quiebre
    ventana = ev[(ev["periodo"] == q["periodo"]) & ev["minuto"].between(q["despues_desde"], q["despues_hasta"])
                 & (ev["equipo_id"] == team) & ev["id"].isin(frames_i.index) & (ev["x"] >= p["presion"]["campo_rival_min_x"])]
    por_uuid = dict(tuple(jugadores[jugadores["event_uuid"].isin(ventana["id"])].groupby("event_uuid")))
    principal, mejor = None, -1.0
    for c in ventana.itertuples():
        if c.id not in por_uuid:
            continue
        todos, area = sc.frame_del_equipo(por_uuid[c.id], frames_i.loc[c.id, "area_visible"], True)
        res = voronoi.analizar_frame(todos, area)
        if res is not None and res.control > mejor:
            principal = reproductor.foto(res, sc.reloj(c.minuto, c.segundo), describir(c), True, reproductor.flecha_de(c, True))
            mejor = res.control
    if principal is None:
        print("✗ No hay una foto analizable del equipo en campo rival después del quiebre.")
        return 1

    # Lectura: índice y field tilt antes y después del quiebre
    def media(lado: str, desde: int, hasta: int, col: str) -> float:
        sel = tab[(tab["lado"] == lado) & (tab["periodo"] == q["periodo"]) & tab["minuto"].between(desde, hasta)]
        return float(sel[col].mean())
    antes = (q["antes_desde"], q["antes_hasta"])
    despues = (q["despues_desde"], q["despues_hasta"])
    ia0, ia1 = media(minuto.PROPIO, *antes, "indice"), media(minuto.PROPIO, *despues, "indice")
    ft0, ft1 = media(minuto.PROPIO, *antes, "field_tilt"), media(minuto.PROPIO, *despues, "field_tilt")
    sistema = todos_q[(todos_q["tipo"] == "cambio_sistema_rival") & (todos_q["indice"] > q["indice"])]
    respuesta = (f" {rival} respondió con un {sc.etiqueta_quiebre(sistema.iloc[0], equipo, rival).split('(')[-1].rstrip(')')} "
                 f"al {sistema.iloc[0]['minuto']}'." if not sistema.empty else "")
    goles_txt = ", ".join(f"{g.minuto}'" for g in goles.itertuples())
    lectura = (f"Al {q['minuto']}', con {gf}-{gc}, {sc.etiqueta_quiebre(q, equipo, rival).lower()} ({protagonista}). "
               f"En los minutos siguientes el índice del {equipo} pasó de {ia0:.0f} a {ia1:.0f} y su field tilt de "
               f"{ft0:.0%} a {ft1:.0%}.{respuesta}" + (f" Goles del {equipo} después: {goles_txt}." if goles_txt else "")
               + " Es lo que dice el principio: con uno más, se instala arriba.")
    que_muestra = (f"Foto 360 del {principal['reloj']}, después de la expulsión: {principal['texto']}. Crema: zonas del {equipo}; "
                   f"blanco: de {rival}; la línea blanca marca dónde chocan los equipos. El {equipo} ataca hacia la derecha.")
    v = p["voronoi"]
    metodo = (f"Índice Proactivo–Reactivo por minuto (ventana de {p['indice']['ventana_min']} minutos, 8 componentes con el "
              f"mismo peso, percentil frente a los minutos de AP21–AP25; propuesta del 14 oct). Voronoi sobre el 360, recortado al "
              f"área visible y a {v['alcance_max_yd']:g} yd por jugador. Una foto por minuto: la acción con más jugadores visibles. "
              "Principios: diferencia en diferencias frente a ventanas de control (notebook 02) y estilo frente a la liga (notebook 03).")

    # Monte Carlo explicativo
    tiros = ev[(ev["tipo"] == "Shot") & (ev["periodo"] != contexto.PERIODO_PENALES)]
    antes_q = tiros[tiros["indice"] < q["indice"]]
    sim_antes = simulacion.simular(antes_q.loc[antes_q["equipo_id"] == team, "tiro_xg"].fillna(0),
                                   antes_q.loc[antes_q["equipo_id"] != team, "tiro_xg"].fillna(0))
    sim_total = simulacion.simular(tiros.loc[tiros["equipo_id"] == team, "tiro_xg"].fillna(0),
                                   tiros.loc[tiros["equipo_id"] != team, "tiro_xg"].fillna(0))
    xg_desp = tiros[tiros["indice"] > q["indice"]].groupby(tiros["equipo_id"] == team)["tiro_xg"].sum()
    montecarlo = [
        datos_app.montecarlo(f"Hasta el {q['minuto']}' (antes de la roja)",
                             "Con los tiros de los dos equipos hasta ese momento, ¿qué marcador era el más probable?", sim_antes),
        datos_app.montecarlo("El partido completo", f"Con todos los tiros (incluida la prórroga), ¿qué tan merecido fue el "
                             f"{int(info['goles_favor'])}-{int(info['goles_contra'])}? Después de la roja, el {equipo} generó "
                             f"{xg_desp.get(True, 0):.2f} de xG y {rival} {xg_desp.get(False, 0):.2f}.", sim_total),
    ]

    # Principios, barra y textos de la página
    fase = sb.minuscula(sb.etiqueta_partido(partidos, info)).replace(" · ", " de ")
    caso_texto = f"Caso: {fase} {info['torneo_corto']}"
    tarjetas, del_caso = principios(args.tipo, caso_texto)
    if del_caso is None:
        print("✗ Faltan los resultados de los notebooks 02 y 03 (outputs/hallazgos) o el principio del caso.")
        return 1
    barra = sb.compacta(partidos, info, q["tipo"], q["estado_antes"],
                        f"1 partido · {len(repro['fotos'])} minutos con foto 360")
    kpis = [
        (f"Índice con {nuevo}", f"{medias.loc[True, minuto.PROPIO]:.0f}", f"rivales {medias.loc[True, minuto.RIVAL]:.0f} · {n_nuevo} partidos"),
        ("Índice con Solari y Ortiz", f"{medias.loc[False, minuto.PROPIO]:.0f}", f"rivales {medias.loc[False, minuto.RIVAL]:.0f} · {n_previos} partidos"),
    ] + [(t.titulo, t.diferencia, "frente a Solari y Ortiz") for t in tarjetas[:2]]
    titulo = (f"La expulsión de {protagonista} y lo que vino después" if args.tipo.startswith("expulsion")
              else f"{sc.etiqueta_quiebre(q, equipo, rival)} y lo que vino después")
    pendientes = [
        ("Modelo de riesgo", "Probabilidad de recibir peligro en los próximos 10 minutos según el índice y el contexto; "
         "evaluado en el Clausura 2026 con log-loss y calibración.", "predictivo"),
        ("Balón parado", "Cómo se ubican y qué espacio cubren en córners y tiros libres (Voronoi en el envío) y desde dónde "
         "rematan o les rematan.", "componente del reto"),
        ("Costo de progresión", "Grafo de pases dirigido: qué tan caro le resulta llegar al último tercio, con la "
         "probabilidad de éxito de cada pase.", "innovación"),
        ("Matriz de situaciones y ficha", "Qué hace Jardine y qué le funciona en cada situación; ficha de 10 segundos por rival.",
         "decisión"),
    ]
    notas = ["Índice provisional: definición del 14 oct en contexto/framework.md, pendiente de confirmar (pesos iguales, falta la verificación con PCA).",
             "Principios: candidatos con el criterio v1; la auditoría del 14 oct pide la versión 2 (escala de las ventanas de control, FDR) y la prueba placebo.",
             "Página con datos reales de StatsBomb: solo para la competencia; no se sube a git ni se publica."]
    datos = {
        "meta": {"generado": date.today().isoformat(), "partido": int(args.partido), "tipo": args.tipo,
                 "aviso": "Datos reales de StatsBomb: solo para la competencia; no se suben a git ni se publican."},
        "titulo": titulo, "equipo": equipo, "rival": rival, "nuevo": nuevo,
        "portada": {
            "kpis": [{"etq": a_, "valor": b_, "detalle": c_} for a_, b_, c_ in kpis],
            "torneos": [{"torneo": r_.torneo, "entrenador": r_.entrenador, "propio": round(float(r_.propio), 1),
                         "rival": round(float(r_.rival), 1), "nuevo": r_.entrenador == nuevo} for r_ in por_torneo.itertuples()],
            "principios": [datos_app.principio(x) for x in tarjetas],
            "ejemplo": {"texto": f"{equipo} vs {rival}, {fase} del {info['torneo']} {pd.Timestamp(info['fecha']).year}: "
                                 f"{sb.minuscula(titulo)}.", "foto": principal, "que_muestra": que_muestra},
        },
        "explorar": {
            "antetitulo": f"Principio → caso · {info['torneo_corto']} · {etapa} · {fecha}",
            "filtros": [info["torneo_corto"], sb.etiqueta_partido(partidos, info), sb.MOMENTOS.get(args.tipo, args.tipo),
                        sb.condicion(info["localia"])],
            "principio": datos_app.principio(del_caso),
            "caso": {"titulo": titulo, "chips": [[k_, v_] for k_, v_ in chips],
                     "quiebres": [[m_, x_, bool(e_)] for m_, x_, e_ in lista_quiebres]},
            "montecarlo": montecarlo, "lectura": lectura, "metodo": metodo, "que_muestra": que_muestra,
            "pendientes": [{"titulo": a_, "texto": b_, "requisito": c_} for a_, b_, c_ in pendientes], "notas": notas,
        },
        "barra": barra, "reproductor": repro,
    }
    ruta = datos_app.escribir(datos)
    print(f"Maqueta 3: {titulo}\nDatos: {ruta.relative_to(RAIZ)} ({ruta.stat().st_size // 1024} KB; reales: no se publican ni se suben a git)\n"
          "Página: app/maqueta.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
