"""Datos de la maqueta 3 (app/maqueta.html): la narrativa de Jardine (principio → caso → reproductor).

Arma: el índice Proactivo–Reactivo de todos los partidos (escala con los torneos de entrenamiento), los
principios (criterio v2; outputs/hallazgos, notebooks 02 y 03), el caso confirmador (un partido y un
quiebre), el reproductor minuto a minuto con su Voronoi y el Monte Carlo explicativo de los tiros.
Escribe solo datos: outputs/app/datos.js (fuera de git: lleva posiciones y nombres reales). El diseño vive en
app/ (maqueta.html, app.css y app.js) y se edita directo, sin Python.

Cómo correrlo (desde la raíz del repo y con el entorno activado; antes 03, 04, 05 y los notebooks 02 y 03):
    python scripts/08_maqueta.py --partido 3918375 --tipo expulsion_favor
y abrir app/maqueta.html (doble clic, o con el servidor de .claude/launch.json en /app/maqueta.html).
Además arma el partido clave de cada rival (ojo.salidas.partido_clave; unos minutos). Con --sin-rivales se salta.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from datetime import date

import numpy as np
import pandas as pd

from ojo.config import DIR_SALIDAS, RAIZ, params
from ojo.datos import almacen, crudo
from ojo.framework import contexto, quiebres
from ojo.framework import partidos as fp
from ojo.lentes import balon_parado, indice, jugadores, minuto, pases, rivales, simulacion, voronoi
from ojo.salidas import barra as sb
from ojo.salidas import caso as sc
from ojo.salidas import datos_app, decision, partido_clave, reproductor

DIR_HALLAZGOS = DIR_SALIDAS / "hallazgos"
COLUMNAS_INDICE = ["match_id", "periodo", "minuto", "equipo_id", "tipo", "duracion", "es_transicion", "directness",
                   "x", "y", "fin_x", "fin_y"]
YARDA_M = params()["campo"]["yarda_m"]  # StatsBomb mide en yardas; la página muestra metros (contexto/terminologia.md)
FORMATOS = {"control": "pct", "posesion": "pct", "field_tilt": "pct", "control_campo_rival": "pct",
            "altura_sin_balon": "m", "presion_alta": "num", "directness": "num", "largo_pase": "m"}
SITUACION_DEL_CASO = {"expulsion_favor": "uno_mas", "expulsion_contra": "uno_menos"}  # tipo de quiebre → fila de la matriz
CLAVES_CORTAS = {"gol_favor": "Gol", "gol_contra": "Gol rival", "expulsion_favor": "Roja rival",
                 "expulsion_contra": "Roja", "cambio_sistema_propio": "Sistema", "cambio_sistema_rival": "Sistema rival"}
# Principios: de dónde sale cada número y cómo se lee (notebooks 02 y 03, criterio v2 del 18 oct).
PRINCIPIOS = [
    {"archivo": "estilo", "filtro": {"metrica": "largo_pase"}, "escala": YARDA_M, "unidad": " m", "dec": 1, "cambio": False,
     "clave": "salida_corta", "titulo": "Sale jugando corto",
     "frase": "Con Jardine, los pases del América miden {jardine} en promedio; con Solari y Ortiz, {previos}.",
     "significa": "Cambia el pelotazo por circulación corta, también desde su propio campo.",
     "uso": "Si el rival presiona alto, el plan del América es tocar para salir, no rifar el balón: la presión rival pone a prueba este principio."},
    {"archivo": "quiebres_contra_predecesores", "filtro": {"tipo": "expulsion_favor", "lado": "rival", "metrica": "altura_sin_balon"},
     "escala": YARDA_M, "unidad": " m", "dec": 1, "cambio": True, "tipo_caso": "expulsion_favor",
     "clave": "uno_mas", "casos": "expulsiones del rival", "titulo": "Con uno más, hunde al rival",
     "frase": "Tras una expulsión del rival, el rival se mete atrás: su altura sin balón cambia {jardine} contra Jardine; contra Solari y Ortiz, {previos}.",
     "significa": "Con superioridad numérica no administra: se instala en campo rival, mete al rival en su área y además concede menos contragolpes.",
     "uso": "Con un jugador más, esperar al América volcado arriba; el rival que se queda con diez tiene que preparar la salida desde su área."},
    {"archivo": "quiebres_contra_predecesores", "filtro": {"tipo": "sustitucion_lesion_propia", "lado": "propio", "metrica": "presiones"},
     "escala": 10, "unidad": " cada 10 min", "dec": 1, "cambio": True, "tipo_caso": "sustitucion_lesion_propia",
     "clave": "lesion", "casos": "cambios por lesión", "titulo": "Una lesión no lo frena",
     "frase": "Tras una sustitución por lesión, sus presiones cambian {jardine} con Jardine; con Solari y Ortiz, {previos}.",
     "significa": "Un cambio obligado no lo hace recular: sale a presionar más.",
     "uso": "Tras una lesión del América no esperar un repliegue: el rival tiene que preparar la salida ante más presión."},
    {"archivo": "quiebres_contra_predecesores", "filtro": {"tipo": "gol_contra", "lado": "rival", "metrica": "contrapresiones"},
     "escala": 10, "unidad": " cada 10 min", "dec": 1, "cambio": True, "tipo_caso": "gol_contra",
     "clave": "gol_contra", "casos": "goles en contra", "titulo": "Tras recibir gol, el rival no lo aprieta",
     "frase": "Después de que el América recibe gol, la presión del rival tras perder el balón cambia {jardine} contra Jardine; contra Solari y Ortiz, {previos}.",
     "significa": "El rival que se adelanta en el marcador se repliega en lugar de seguir presionando la salida.",
     "uso": "El rival que anota tiene que decidir si se mete atrás: contra Jardine suele hacerlo y le cede el balón."},
    {"archivo": "quiebres_contra_predecesores", "filtro": {"tipo": "cambio_sistema_propio", "lado": "propio", "metrica": "xg"},
     "escala": 10, "unidad": " xG cada 10 min", "dec": 2, "cambio": True, "tipo_caso": "cambio_sistema_propio",
     "clave": "cambio_sistema", "casos": "cambios de sistema", "titulo": "Alerta: cambiar el sistema le cuesta",
     "frase": "Tras sus cambios de sistema, los goles esperados (xG) del América cambian {jardine} con Jardine; con Solari y Ortiz, {previos}.",
     "significa": "Los 10 minutos que siguen a un cambio de sistema produce menos. Puede ser porque el cambio responde a algo que ya iba mal: es una pista, no una causa.",
     "uso": "Para el cuerpo técnico: cuidar el paso al nuevo sistema. Para el rival: es una ventana para atacar."},
    {"archivo": "jugadores_lineas_criterio", "filtro": {"metrica": "tacticos_defensa"}, "escala": 1, "unidad": " por partido",
     "dec": 2, "cambio": False,
     "clave": "bandas", "titulo": "Refresca las bandas",
     "frase": "Con Jardine, los cambios tácticos de defensas son {jardine}; con Solari y Ortiz, {previos}.",
     "significa": "Mueve laterales y centrales (mediana del minuto 76) más que mediocampistas: gestión de piernas más que golpe táctico.",
     "uso": "Desde el minuto 70, esperar laterales frescos del América: el rival puede preparar sus cambios de banda para ese momento."},
]


def principios(caso_tipo: str, caso_texto: str, n_torneos: int, nombre_nuevo: str,
               n_partidos: tuple[int, int]) -> tuple[list[datos_app.Principio], datos_app.Principio | None]:
    """Tarjetas de los principios candidatos con sus números (si los notebooks ya se corrieron).

    n_torneos: torneos de entrenamiento del entrenador nuevo (el denominador de la constancia).
    n_partidos: partidos de entrenamiento del nuevo y de los previos (la muestra de los principios por partido).
    """
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
        sin_unidad = lambda v: f"{v * d['escala']:+.{d['dec']}f}"  # noqa: E731
        dif = lambda v: sin_unidad(v) + d["unidad"]  # noqa: E731
        estado = (f"Pasa los 4 parámetros · riesgo de falso hallazgo: {decision.texto_riesgo(f['q'])}" if f["pasa"]
                  else "No pasa los 4 parámetros")
        if f.get("muestra_chica", False):
            estado += " · muestra chica"
        p = datos_app.Principio(
            titulo=d["titulo"], frase=d["frase"].format(jardine=fmt(nuevo), previos=fmt(previo)), significa=d["significa"],
            uso=d["uso"], jardine=fmt(nuevo), previos=fmt(previo), diferencia=dif(f["diferencia"]),
            intervalo=f"Rango probable: {sin_unidad(f['ic_bajo'])} a {dif(f['ic_alto'])}", torneos=f"{int(f['torneos_misma_direccion'])} de {n_torneos}",
            estado=estado, clave=d["clave"])
        # Muestra: momentos clave de cada grupo (principios de quiebres) o partidos (principios por partido)
        p.n_nuevo, p.n_previos = ((int(f["quiebres_nuevo"]), int(f["quiebres_previos"])) if "quiebres_nuevo" in f else n_partidos)
        p.muestra = f"{p.n_nuevo} {d.get('casos', 'partidos')} con {nombre_nuevo} · {p.n_previos} con Solari y Ortiz"
        if d.get("tipo_caso") == caso_tipo:
            p.caso = caso_texto
            del_caso = p
        tarjetas.append(p)
    return tarjetas, del_caso


def tabla_indice(partidos: pd.DataFrame) -> tuple[pd.DataFrame, indice.VerificacionPCA]:
    """Índice por minuto y equipo de todos los partidos (escala de los torneos de entrenamiento) y su verificación con PCA."""
    ids = partidos["match_id"].astype(int).tolist()
    piezas = indice.piezas_por_minuto(almacen.cargar("eventos", ids, columnas=COLUMNAS_INDICE))
    comp = indice.componentes(minuto.cargar_panel("minuto").query("match_id in @ids"), piezas)
    entrenamiento = comp[comp["match_id"].isin(partidos.loc[~partidos["prueba"], "match_id"])]
    return indice.calcular(comp, indice.ajustar(entrenamiento)), indice.verificar_pca(entrenamiento)


def datos_reproductor(tab: pd.DataFrame, ev: pd.DataFrame, fotos: dict, jugadas: list[dict], todos_q: pd.DataFrame,
                      equipo: str, rival: str, team: int, q: pd.Series, eventos_min: dict | None = None) -> dict:
    """JSON del reproductor: un paso por minuto (índice, radar, componentes, marcador, foto y los eventos que se animan:
    goles, cambios, faltas, tiros de esquina y saques) y la jugada."""
    eventos_min = eventos_min or {}
    comps = list(params()["indice"]["componentes"])
    a_metros = [YARDA_M if FORMATOS[c] == "m" else 1 for c in comps]  # los valores en yardas se muestran en metros
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
            "va": [None if fa is None else redondo(fa[c] * k_) for c, k_ in zip(comps, a_metros)],
            "vr": [None if fr is None else redondo(fr[c] * k_) for c, k_ in zip(comps, a_metros)],
            "marcador": "—" if g is None else f"{int(g['goles_favor'])}-{int(g['goles_contra'])}", "foto": foto_k,
            "ev": eventos_min.get((int(p), int(m)), []),
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
    for jugada in jugadas:
        jugada["minuto"] = pos.get(jugada.pop("clave"), 0)
    anim = params()["animacion"]
    return {"equipo": equipo, "rival": rival, "componentes": [{"id": c, "nombre": indice.NOMBRES[c], "radar": indice.NOMBRES_RADAR[c], "formato": FORMATOS[c]} for c in comps],
            "minutos": minutos, "fotos": lista_fotos, "quiebres": marcas, "etiquetasX": etiquetas, "jugadas": jugadas,
            "animacion": {"escala": anim["escala_tiempo"], "duracion": anim["duracion_s"], "pausa_foto": anim["pausa_foto_s"],
                          "alcance": params()["voronoi"]["alcance_max_yd"], "cuartos_circulo": voronoi.CUARTOS_CIRCULO},
            "bandas": params()["indice"]["bandas"],
            "inicio": pos.get((int(q["periodo"]), int(q["minuto"])), 0)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--partido", type=int, required=True, metavar="MATCH_ID")
    parser.add_argument("--tipo", choices=quiebres.TIPOS, default="expulsion_favor", metavar="TIPO")
    parser.add_argument("--n", type=int, default=1, help="cuál quiebre de ese tipo (1 = el primero)")
    parser.add_argument("--sin-rivales", action="store_true", help="no arma el partido clave de cada rival (más rápido)")
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
    tab_todos, pca = tabla_indice(partidos)

    # Portada: índice por torneo (sin el torneo de prueba) y cifras clave
    entr = tab_todos.merge(partidos[["match_id", "torneo_corto", "entrenador_corto", "prueba", "fecha"]], on="match_id")
    entr = entr[~entr["prueba"]]
    por_torneo = (entr.groupby(["torneo_corto", "entrenador_corto", "lado"])["indice"].mean().unstack("lado").reset_index()
                  .merge(partidos.groupby("torneo_corto")["fecha"].min().rename("inicio"), on="torneo_corto").sort_values("inicio"))
    por_torneo = por_torneo.rename(columns={"torneo_corto": "torneo", "entrenador_corto": "entrenador",
                                            minuto.PROPIO: "propio", minuto.RIVAL: "rival"})
    por_torneo = por_torneo.groupby("torneo", sort=False).agg(entrenador=("entrenador", "last"), propio=("propio", "mean"),
                                                             rival=("rival", "mean")).reset_index()
    n_nuevo = partidos[(partidos["entrenador_corto"] == nuevo) & ~partidos["prueba"]].shape[0]
    n_previos = partidos[(partidos["entrenador_corto"] != nuevo) & ~partidos["prueba"]].shape[0]

    # Caso: el quiebre elegido del partido
    ev = almacen.cargar("eventos", [args.partido]).sort_values("indice").reset_index(drop=True)
    todos_q = quiebres.ventanas(quiebres.detectar(ev, team), quiebres.limites_periodo(ev))
    del_tipo = todos_q[todos_q["tipo"] == args.tipo]
    if len(del_tipo) < args.n:
        print(f"✗ El partido tiene {len(del_tipo)} quiebres de tipo {args.tipo}.")
        return 1
    q = del_tipo.iloc[args.n - 1]

    # Principios (la tarjeta del caso lleva su insignia "Caso: …")
    fase = sb.minuscula(sb.etiqueta_partido(partidos, info)).replace(" · ", " de ")
    caso_texto = f"Caso: {fase} {info['torneo_corto']}"
    n_torneos = partidos.loc[(partidos["entrenador_corto"] == nuevo) & ~partidos["prueba"], "torneo_corto"].nunique()
    tarjetas, del_caso = principios(args.tipo, caso_texto, n_torneos, nuevo, (n_nuevo, n_previos))
    if del_caso is None:
        print("✗ Faltan los resultados de los notebooks 02 y 03 (outputs/hallazgos) o el principio del caso.")
        return 1
    decidir = datos_decidir(p, team)
    notas = [f"Pesos del índice comprobados (PCA): {'las 8 señales empujan' if pca.mismo_signo else 'no todas las señales empujan'} en la "
             f"dirección esperada ({pca.varianza * 100:.0f} % de la variación) y el promedio con pesos iguales coincide en "
             f"{pca.correlacion:.2f} (correlación) con la combinación que sale de los datos.",
             ("Cada principio pasa" if all(t.estado.startswith("Pasa") for t in tarjetas) else "Un principio es hallazgo si pasa")
             + " los 4 parámetros: rango probable sin cero, tamaño mayor que lo que cambia el partido solo, "
             f"misma dirección en {p['hallazgo']['min_torneos_misma_direccion']} de los torneos de {nuevo} y riesgo de falso hallazgo de "
             f"{p['hallazgo']['fdr_q'] * 100:.0f} % o menos. La prueba en falso (placebo) se hizo con los momentos clave de {nuevo}.",
             "Página con datos reales de StatsBomb: solo para la competencia; no se sube a git ni se publica."]
    caso = armar_caso(p, partidos, info, tab_todos, pca, q, ev, todos_q, del_caso, decidir, notas,
                      antetitulo="Principio → caso", etiqueta="Un partido donde se ve", regla=None)
    if caso["principal"] is None:
        print("✗ No hay una foto analizable del equipo en campo rival después del quiebre.")
        return 1
    principal, d0, titulo, repro = caso["principal"], caso["d0"], caso["titulo"], caso["reproductor"]

    # El partido de cada rival (regla fija de ojo.salidas.partido_clave; Tigres conserva la final del caso)
    partidos_rival = {} if args.sin_rivales else partidos_por_rival(p, partidos, tab_todos, pca, tarjetas, decidir, notas, rival)

    # Barra y textos de la página
    barra = sb.compacta(partidos, info, q["tipo"], q["estado_antes"],
                        f"1 partido · {len(repro['fotos'])} minutos con foto de posiciones (360)")
    kpis = cuadros_resumen(partidos, entr, tarjetas, nuevo, team)
    ejemplo_datos = datos_del_ejemplo(principal, ev, d0, q, args.tipo, equipo, rival, team)
    ejemplo_lectura = lectura_hasta(tab_todos[tab_todos["match_id"] == args.partido], ev, d0, q, equipo, rival, team)
    datos = {
        "meta": {"generado": date.today().isoformat(), "partido": int(args.partido), "tipo": args.tipo,
                 "aviso": "Datos reales de StatsBomb: solo para la competencia; no se suben a git ni se publican."},
        "titulo": titulo, "equipo": equipo, "rival": rival, "nuevo": nuevo,
        "portada": {
            "kpis": kpis,
            "torneos": [{"torneo": r_.torneo, "entrenador": r_.entrenador, "propio": round(float(r_.propio), 1),
                         "rival": round(float(r_.rival), 1), "nuevo": r_.entrenador == nuevo} for r_ in por_torneo.itertuples()],
            "principios": [datos_app.principio(x) for x in tarjetas],
            "ejemplo": {"texto": f"{equipo} vs {rival}, {fase} del {info['torneo']} {pd.Timestamp(info['fecha']).year}: "
                                 f"{sb.minuscula(titulo)}.", "foto": principal, "que_muestra": caso["explorar"]["que_muestra"],
                         "datos": ejemplo_datos, "lectura": ejemplo_lectura, "local": info["localia"] == "local"},
        },
        "explorar": caso["explorar"],
        "barra": barra, "reproductor": repro, "decidir": decidir,
        "metodo": datos_metodo(partidos, pca, nuevo),
        "partidos": partidos_rival,
    }
    ruta = datos_app.escribir(datos)
    print(f"Maqueta 3: {titulo} · {len(partidos_rival)} partidos de rivales\nDatos: {ruta.relative_to(RAIZ)} "
          f"({ruta.stat().st_size // 1024} KB; reales: no se publican ni se suben a git)\nPágina: app/maqueta.html")
    return 0


# Cómo se nombra cada tipo de momento en el caso: (antes, Después, después, título de la jugada destacada)
TEXTO_MOMENTO = {
    "expulsion_favor": ("antes de la roja", "Después de la roja", "después de la expulsión", "Con uno más, arriba"),
    "expulsion_contra": ("antes de la roja", "Después de la roja", "después de la expulsión", "Con uno menos"),
    "gol_contra": ("antes del gol rival", "Después del gol rival", "después del gol rival", "Tras el gol rival"),
    "cambio_sistema_propio": ("antes del cambio de sistema", "Después del cambio", "después del cambio de sistema", "Con el nuevo sistema"),
    "gol_favor": ("antes del gol", "Después del gol", "después del gol", "Tras el gol"),
}
CLAVE_DEL_TIPO = {d["tipo_caso"]: d["clave"] for d in PRINCIPIOS if "tipo_caso" in d}  # momento → principio relacionado


def armar_caso(p: dict, partidos: pd.DataFrame, info: pd.Series, tab_todos: pd.DataFrame, pca: indice.VerificacionPCA,
               q: pd.Series, ev: pd.DataFrame, todos_q: pd.DataFrame, tarjeta: datos_app.Principio | None, decidir: dict,
               notas: list[str], antetitulo: str, etiqueta: str, regla: str | None) -> dict:
    """El caso de un partido alrededor de un momento clave: textos de El partido, reproductor y foto destacada."""
    team, equipo = p["equipo"]["team_id"], p["equipo"]["nombre"]
    mid, rival, tipo = int(info["match_id"]), info["rival"], q["tipo"]
    antes_txt, despues_may, despues_min, titulo_jugada = TEXTO_MOMENTO.get(
        tipo, ("antes del momento", "Después del momento", "después del momento", "Después del momento"))
    e = ev[ev["indice"] == q["indice"]].iloc[0]
    noms = sc.nombres(crudo.leer("lineups", match_id=mid))
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

    # Reproductor: foto por minuto y jugadas (la destacada, el gol del momento y el primer gol a favor después)
    frames = almacen.cargar("frames", [mid])
    jugadores_f = almacen.cargar("frames_jugadores", [mid])
    describir = lambda x: sc.describir(x, noms, nombre_equipo)  # noqa: E731
    fotos = reproductor.por_minuto(ev, frames, jugadores_f, team, describir)
    tab = tab_todos[tab_todos["match_id"] == mid]
    goles = todos_q[(todos_q["tipo"] == "gol_favor") & (todos_q["indice"] > q["indice"])]
    jugadas = []
    frames_i = frames.set_index("event_uuid")
    if tipo in ("gol_favor", "gol_contra"):
        autor = noms.get(e["jugador_id"], "")
        jugadas.append({"titulo": (f"El gol del {q['minuto']}'" + (f" ({autor})" if autor else "")) if tipo == "gol_favor"
                        else f"El gol de {rival} ({q['minuto']}')",
                        "fotos": reproductor.secuencia(ev, int(q["indice"]), frames, jugadores_f, team, describir, noms),
                        "clave": (int(q["periodo"]), int(q["minuto"]))})
    if not goles.empty:
        g0 = goles.iloc[0]
        autor = noms.get(ev.loc[ev["indice"] == g0["indice"], "jugador_id"].iloc[0], "")
        jugadas.append({"titulo": f"El gol del {g0['minuto']}' ({autor})",
                        "fotos": reproductor.secuencia(ev, int(g0["indice"]), frames, jugadores_f, team, describir, noms),
                        "clave": (int(g0["periodo"]), int(g0["minuto"]))})

    # Foto destacada: la acción del equipo con más control en campo rival en la ventana después del quiebre
    ventana = ev[(ev["periodo"] == q["periodo"]) & ev["minuto"].between(q["despues_desde"], q["despues_hasta"])
                 & (ev["equipo_id"] == team) & ev["id"].isin(frames_i.index) & (ev["x"] >= p["presion"]["campo_rival_min_x"])]
    por_uuid = dict(tuple(jugadores_f[jugadores_f["event_uuid"].isin(ventana["id"])].groupby("event_uuid")))
    principal, mejor, indice_destacada, d0 = None, -1.0, None, None
    for c in ventana.itertuples():
        if c.id not in por_uuid:
            continue
        todos, area = sc.frame_del_equipo(por_uuid[c.id], frames_i.loc[c.id, "area_visible"], True)
        res = voronoi.analizar_frame(todos, area)
        if res is not None and res.control > mejor:
            principal = reproductor.foto(res, sc.reloj(c.minuto, c.segundo), describir(c), True, reproductor.flecha_de(c, True))
            principal["nombre"] = noms.get(c.jugador_id, "")
            mejor, indice_destacada = res.control, int(c.indice)
    if principal is not None:
        d0 = ev[ev["indice"] == indice_destacada].iloc[0]
        jugadas.insert(0, {"titulo": f"{titulo_jugada} ({d0['minuto']}')",
                           "fotos": reproductor.secuencia(ev, indice_destacada, frames, jugadores_f, team, describir, noms),
                           "clave": (int(d0["periodo"]), int(d0["minuto"]))})
    eventos_min = reproductor.eventos_por_minuto(ev, team, noms, nombre_equipo)
    repro = datos_reproductor(tab, ev, fotos, [j for j in jugadas if len(j["fotos"]) > 1], todos_q, equipo, rival, team, q,
                              eventos_min)

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
    quiebre_txt = sc.etiqueta_quiebre(q, equipo, rival)
    quien_txt = f" ({protagonista})" if protagonista and protagonista not in (equipo, rival) else ""
    hay_cambio = not any(pd.isna(x) for x in (ia0, ia1, ft0, ft1))
    lectura = (f"Al {q['minuto']}', con {gf}-{gc}, {quiebre_txt[0].lower() + quiebre_txt[1:]}{quien_txt}."
               + (f" En los minutos siguientes, el índice de iniciativa del {equipo} pasó de {ia0:.0f} a {ia1:.0f} y su dominio "
                  f"del último tercio, de {ft0 * 100:.0f} % a {ft1 * 100:.0f} %." if hay_cambio else "")
               + respuesta + (f" Goles del {equipo} después: {goles_txt}." if goles_txt else "")
               + (" Es lo que dice el principio: con uno más, se instala arriba." if tipo == "expulsion_favor" and hay_cambio and ft1 > ft0 else ""))
    que_muestra = ((f"Foto de posiciones (360) del {principal['reloj']}, {despues_min}: {principal['texto']}. " if principal else "")
                   + f"Crema: zonas del {equipo}; blanco: de {rival}; la línea blanca marca dónde chocan los equipos. El {equipo} ataca hacia la derecha.")
    v = p["voronoi"]
    metodo = (f"Índice de iniciativa por minuto: ocho señales de los últimos {p['indice']['ventana_min']} minutos, con el mismo peso, "
              f"de 0 (espera) a 100 (propone), frente a los minutos de AP21–AP25. Comprobación de los pesos (PCA): correlación de "
              f"{pca.correlacion:.2f}. Mapa de control del espacio (Voronoi) sobre cada foto de posiciones (360), recortado a lo que "
              f"ve la cámara y a {v['alcance_max_yd'] * YARDA_M:.0f} m por jugador. Una foto por minuto: la acción con más jugadores "
              "visibles. Principios: cambio neto frente a tramos de comparación y estilo frente a la liga.")

    # Monte Carlo explicativo
    tiros = ev[(ev["tipo"] == "Shot") & (ev["periodo"] != contexto.PERIODO_PENALES)]
    antes_q = tiros[tiros["indice"] < q["indice"]]
    sim_antes = simulacion.simular(antes_q.loc[antes_q["equipo_id"] == team, "tiro_xg"].fillna(0),
                                   antes_q.loc[antes_q["equipo_id"] != team, "tiro_xg"].fillna(0))
    sim_total = simulacion.simular(tiros.loc[tiros["equipo_id"] == team, "tiro_xg"].fillna(0),
                                   tiros.loc[tiros["equipo_id"] != team, "tiro_xg"].fillna(0))
    xg_desp = tiros[tiros["indice"] > q["indice"]].groupby(tiros["equipo_id"] == team)["tiro_xg"].sum()
    prorroga = " (incluida la prórroga)" if ev["periodo"].isin([3, 4]).any() else ""
    montecarlo = [
        datos_app.montecarlo(f"Hasta el {q['minuto']}' ({antes_txt})",
                             "Con los tiros de los dos equipos hasta ese momento, ¿qué marcador era el más probable?", sim_antes),
        datos_app.montecarlo("El partido completo", f"Con todos los tiros{prorroga}, ¿qué tan merecido fue el "
                             f"{int(info['goles_favor'])}-{int(info['goles_contra'])}? {despues_may}, el {equipo} generó "
                             f"{xg_desp.get(True, 0):.2f} goles esperados (xG) y {rival}, {xg_desp.get(False, 0):.2f}.", sim_total),
    ]
    if tipo.startswith("expulsion"):
        titulo = f"La expulsión de {protagonista} y lo que vino después"
    elif tipo.startswith("gol") and quien_txt:
        titulo = f"El gol de {protagonista} y lo que vino después"
    else:
        titulo = f"{quiebre_txt} y lo que vino después"
    explorar = {
        "antetitulo": f"{antetitulo} · {info['torneo_corto']} · {etapa} · {fecha}",
        "filtros": [info["torneo_corto"], sb.etiqueta_partido(partidos, info), sb.MOMENTOS.get(tipo, tipo), sb.condicion(info["localia"])],
        "principio": datos_app.principio(tarjeta) if tarjeta is not None else None,
        "caso": {"titulo": titulo, "chips": [[k_, v_] for k_, v_ in chips], "quiebres": [[m_, x_, bool(e_)] for m_, x_, e_ in lista_quiebres],
                 "etiqueta": etiqueta, "regla": regla},
        "montecarlo": montecarlo, "simulaciones": p["simulacion"]["repeticiones"], "lectura": lectura, "metodo": metodo,
        "que_muestra": que_muestra, "siguiente": siguiente_paso(decidir, tipo, rival, tarjeta), "notas": notas,
    }
    return {"titulo": titulo, "explorar": explorar, "reproductor": repro, "principal": principal, "d0": d0,
            "local": info["localia"] == "local"}


def partidos_por_rival(p: dict, partidos: pd.DataFrame, tab_todos: pd.DataFrame, pca: indice.VerificacionPCA,
                       tarjetas: list[datos_app.Principio], decidir: dict, notas: list[str], rival_del_caso: str) -> dict:
    """El partido clave de cada rival de las fichas con el entrenador nuevo (ojo.salidas.partido_clave), torneo reservado incluido."""
    team = p["equipo"]["team_id"]
    nuevo = sb.corto(p["entrenador"]["nombre"])
    con_fotos = set(almacen.cargar("frames", columnas=["match_id"])["match_id"].unique())
    suyos = partidos[(partidos["entrenador_corto"] == nuevo) & partidos["match_id"].isin(con_fotos)]
    por_clave = {t.clave: t for t in tarjetas}
    salida = {}
    for f in decidir["fichas"]:
        nombre = f["rival"]
        g = suyos[suyos["rival"] == nombre]
        if nombre == rival_del_caso or g.empty:
            continue
        eventos, tipos = {}, {}
        for mid in g["match_id"].astype(int):
            eventos[mid] = almacen.cargar("eventos", [mid]).sort_values("indice").reset_index(drop=True)
            tipos[mid] = set(quiebres.detectar(eventos[mid], team)["tipo"])
        elegido = partido_clave.elegir_partido(g, tipos)
        ev = eventos[elegido]
        todos_q = quiebres.ventanas(quiebres.detectar(ev, team), quiebres.limites_periodo(ev))
        q = partido_clave.elegir_momento(todos_q)
        if q is None:
            print(f"  · {nombre}: sin momento clave en el partido elegido; queda fuera")
            continue
        info = g[g["match_id"] == elegido].iloc[0]
        tarjeta = por_clave.get(CLAVE_DEL_TIPO.get(q["tipo"]))
        tarjeta = replace(tarjeta, caso="") if tarjeta is not None else None
        caso = armar_caso(p, partidos, info, tab_todos, pca, q, ev, todos_q, tarjeta, decidir, notas,
                          antetitulo="Partido clave", etiqueta=f"Su partido clave con {nuevo}",
                          regla=f"Elegido con una regla fija: {partido_clave.razon(g, elegido)}.")
        salida[nombre] = {"rival": nombre, "local": caso["local"], "explorar": caso["explorar"], "reproductor": caso["reproductor"]}
        print(f"  · {nombre}: {info['torneo_corto']} {sb.etapa_legible(info['etapa'], False) or 'fase regular'} — {caso['titulo']}")
    return salida


def cuadros_resumen(partidos: pd.DataFrame, entr: pd.DataFrame, tarjetas: list[datos_app.Principio], nuevo: str,
                    team: int) -> list[dict]:
    """Cuadros del Resumen: cada medida con el entrenador nuevo arriba y debajo sus predecesores.

    Índice y largo de pase van por entrenador (cada uno tiene decenas de partidos); el principio de la expulsión va con
    los predecesores juntos, porque por separado quedarían muy pocas expulsiones por entrenador.
    """
    def fila(quien: str, valor: str, nota: str, es_nuevo: bool = False) -> dict:
        return {"quien": quien, "valor": valor, "nota": nota, "nuevo": es_nuevo}

    entrenamiento = partidos[~partidos["prueba"]]
    n_coach = entrenamiento.groupby("entrenador_corto").size()
    previos = (entrenamiento[entrenamiento["entrenador_corto"] != nuevo].groupby("entrenador_corto")["fecha"].min()
               .sort_values(ascending=False).index.tolist())  # el más reciente primero
    idx = entr.groupby(["entrenador_corto", "lado"])["indice"].mean().unstack("lado")
    cuadros = [{"etq": "Índice de iniciativa", "clave": "indice",
                "que": "De 0 (espera al rival y sale al contragolpe) a 100 (tiene el balón y presiona arriba). Promedio de sus partidos.",
                "filas": [fila(c, f"{idx.loc[c, minuto.PROPIO]:.0f}", f"sus rivales: {idx.loc[c, minuto.RIVAL]:.0f} · {int(n_coach[c])} partidos",
                               c == nuevo) for c in [nuevo, *previos]]}]
    por_clave = {t.clave: t for t in tarjetas}
    if "salida_corta" in por_clave:
        ev = almacen.cargar("eventos", entrenamiento["match_id"].tolist(), columnas=pases.COLUMNAS)
        largo = entrenamiento.assign(largo=entrenamiento["match_id"].map(pases.largo_por_partido(ev, team)) * YARDA_M)
        por_coach = largo.groupby("entrenador_corto")["largo"].mean()
        menos = largo.loc[largo["entrenador_corto"] != nuevo, "largo"].mean() - por_coach[nuevo]
        cuadros.append({"etq": por_clave["salida_corta"].titulo, "clave": "salida_corta",
                        "que": "Largo medio de sus pases en juego abierto: toca corto desde atrás en lugar de rifar el balón.",
                        "filas": [fila(nuevo, f"{por_coach[nuevo]:.1f} m", f"{abs(menos):.1f} m {'menos' if menos > 0 else 'más'} que con Solari y Ortiz", True)]
                        + [fila(c, f"{por_coach[c]:.1f} m", f"{int(n_coach[c])} partidos") for c in previos]})
    if "uno_mas" in por_clave:
        t = por_clave["uno_mas"]
        cuadros.append({"etq": t.titulo, "clave": "uno_mas",
                        "que": "Tras una expulsión del rival: cuánto cambia la altura sin balón del rival que se queda con diez. "
                               "En negativo, se mete atrás, más cerca de su portería.",
                        "filas": [fila(nuevo, t.jardine, f"{t.n_nuevo} expulsiones del rival", True),
                                  fila("Solari y Ortiz", t.previos, f"{t.n_previos} expulsiones; por separado serían muy pocas")]})
    return cuadros


def datos_del_ejemplo(foto: dict, ev: pd.DataFrame, evento: pd.Series, q: pd.Series, tipo: str, equipo: str, rival: str,
                      team: int) -> list[list[str]]:
    """Lo que dice la foto del caso ilustrativo, en datos: minuto, marcador, espacio, jugadores a la vista y la jugada.

    NOTA1: no se muestra la altura del rival en la foto: la cámara ve pocos jugadores cerca del balón y el principio se
    mide con el cambio entre tramos, no con una foto.
    """
    m = contexto.marcador(ev, team).loc[evento.name]
    propios = [j for j in foto["jugadores"] if j[2]]
    ajenos = [j for j in foto["jugadores"] if not j[2]]
    salida = [["Minuto", foto["reloj"]],
              ["Marcador", f"{equipo} {int(m['goles_favor'])}-{int(m['goles_contra'])} {rival}"]]
    if tipo == "expulsion_favor":
        salida.append(["Con uno más", f"desde el {q['minuto']}'"])
    salida += [[f"Espacio del {equipo}", f"{foto['control'] * 100:.0f} % de lo que ve la cámara"],
               ["Jugadores a la vista", f"{len(propios)} del {equipo} · {len(ajenos)} de {rival}"]]
    salida.append(["La jugada", foto["texto"]])
    return salida


# Cómo se nombra el momento clave en la lectura de la foto del Resumen ("Desde la expulsión (79')…")
DESDE_MOMENTO = {"expulsion_favor": "la expulsión", "expulsion_contra": "la expulsión", "gol_favor": "el gol",
                 "gol_contra": "el gol rival", "cambio_sistema_propio": "el cambio de sistema"}


def lectura_hasta(tab: pd.DataFrame, ev: pd.DataFrame, evento: pd.Series, q: pd.Series, equipo: str, rival: str,
                  team: int) -> str:
    """Lectura del juego hasta la foto del Resumen: marcador, quién propuso más, qué cambió desde el momento clave y
    los goles esperados (xG) de cada equipo hasta ese instante. Solo con lo que ya había pasado."""
    m = contexto.marcador(ev, team).loc[evento.name]
    hasta = (int(evento["periodo"]), int(evento["minuto"]))
    clave = list(zip(tab["periodo"].astype(int), tab["minuto"].astype(int)))
    jugado = tab[[c <= hasta for c in clave]]
    def media(sel: pd.DataFrame, lado: str, col: str) -> float:
        return float(sel.loc[sel["lado"] == lado, col].mean())
    ia, ir = media(jugado, minuto.PROPIO, "indice"), media(jugado, minuto.RIVAL, "indice")
    texto = f"Hasta el {sc.reloj(evento['minuto'], evento['segundo'])} iba {int(m['goles_favor'])}-{int(m['goles_contra'])}."
    if not np.isnan(ia) and not np.isnan(ir):
        quien = f"el {equipo} propuso más que {rival}" if ia >= ir else f"{rival} propuso más que el {equipo}"
        texto += f" En el partido, {quien}: índice de iniciativa {ia:.0f} contra {ir:.0f}."
    desde = (int(q["periodo"]), int(q["minuto"]))
    tras = jugado[[desde <= c for c in zip(jugado["periodo"].astype(int), jugado["minuto"].astype(int))]]
    if desde <= hasta and not tras.empty and q["tipo"] in DESDE_MOMENTO:
        ia1, ir1, ft1 = media(tras, minuto.PROPIO, "indice"), media(tras, minuto.RIVAL, "indice"), media(tras, minuto.PROPIO, "field_tilt")
        if not any(np.isnan(v) for v in (ia1, ir1, ft1)):
            texto += (f" Desde {DESDE_MOMENTO[q['tipo']]} ({q['minuto']}'), el índice queda {ia1:.0f} contra {ir1:.0f} y el dominio del "
                      f"último tercio del {equipo} es de {ft1 * 100:.0f} %.")
    tiros = ev[(ev["tipo"] == "Shot") & (ev["indice"] < evento["indice"]) & (ev["periodo"] != contexto.PERIODO_PENALES)]
    xg = tiros.groupby(tiros["equipo_id"] == team)["tiro_xg"].sum()
    texto += (f" Goles esperados (xG) hasta ese momento: {equipo} {xg.get(True, 0):.2f}, {rival} {xg.get(False, 0):.2f}.")
    return texto


def siguiente_paso(decidir: dict, tipo: str, rival: str, principio: datos_app.Principio | None) -> list[dict]:
    """Bloque 6 de El partido: del caso a la decisión (la fila de la matriz, lo que dice el motor del rival y qué tan sólido es)."""
    salida = []
    fila = next((m for m in decidir["matriz"] if m.get("clave") == SITUACION_DEL_CASO.get(tipo)), None)
    if fila:
        salida.append({"titulo": f"{fila['situacion']}: qué conviene", "texto": fila["recomendacion"],
                       "boton": "Ver la matriz de situaciones", "vista": "decidir", "ancla": "sec-matriz", "situacion": fila["situacion"]})
    ficha = next((f for f in decidir["fichas"] if f["rival"] == rival), None)
    if ficha:
        rasgos = lambda lista: ", ".join(x[0].lower() + x[1:] for x in lista)  # noqa: E731  (a media frase, en minúscula)
        salida.append({"titulo": f"Si el rival es {rival}", "texto": f"Progresa: {rasgos(ficha['progresa'])}. Defiende: "
                       f"{rasgos(ficha['defiende'])}. Concede: {rasgos(ficha['concede'])}.",
                       "boton": "Ver la lectura del motor", "vista": "decidir", "ancla": "ficha", "rival": rival})
    if principio is None:
        return salida
    val = next((v for v in decidir["validacion"] if v["principio"] == principio.titulo), None)
    salida.append({"titulo": "¿Qué tan sólido es?", "texto": f"{principio.titulo}: {principio.estado[0].lower() + principio.estado[1:]}."
                   + (f" En el Clausura 2026, que el análisis no vio: {val['texto'][0].lower() + val['texto'][1:]}." if val else ""),
                   "boton": "Ver la evidencia", "vista": "metodo", "ancla": "met-evidencia"})
    return salida


def _num(v: float, dec: int = 2) -> float | None:
    """Número para el JSON (los vacíos van como null)."""
    return None if v is None or pd.isna(v) else round(float(v), dec)


def fichas_rivales(p: dict, team: int) -> list[dict]:
    """Ficha de 10 segundos de cada rival del América en los torneos de entrenamiento de Jardine (sin el de prueba)."""
    liga = fp.con_torneo(fp.validos(almacen.cargar("partidos")))
    liga["prueba"] = fp.es_prueba(liga)
    america = fp.del_equipo(liga, team)
    ventana = set(america.loc[(america["entrenador_id"] == p["entrenador"]["manager_id"]) & ~america["prueba"], "torneo_corto"])
    liga_v = liga[liga["torneo_corto"].isin(ventana) & ~liga["prueba"]]
    ids = set(liga_v["match_id"])
    tms = almacen.cargar("estadisticas_equipo", columnas=["match_id", "team_id", "team_match_np_xgd", *rivales.COLUMNAS])
    tms = tms[tms["match_id"].isin(ids)]
    medias, z = rivales.perfiles(tms)
    nombres = pd.concat([liga_v.set_index("local_id")["local"], liga_v.set_index("visitante_id")["visitante"]])
    nombres = nombres[~nombres.index.duplicated()]
    xg_neto = tms[tms["team_id"] == team].set_index("match_id")["team_match_np_xgd"]
    am = america[america["match_id"].isin(ids)].assign(xg_neto=lambda d: d["match_id"].map(xg_neto))
    salida = []
    for rid, g in am.groupby("rival_id"):
        if rid not in z.index:
            continue
        parecidos = rivales.similares(z, rid, excluir=(team,))
        f = decision.ficha(rid, nombres.get(rid, g["rival"].iloc[0]), z, medias, decision.registro(g),
                           [nombres.get(x, str(x)) for x in parecidos], decision.registro(am[am["rival_id"].isin(parecidos)]))
        f["partidos"] = int(len(g))
        salida.append(f)
    return sorted(salida, key=lambda f: (-f["partidos"], f["rival"]))


def datos_metodo(partidos: pd.DataFrame, pca: indice.VerificacionPCA, nuevo: str) -> dict:
    """Números de la vista Método: datos usados, verificación del índice, criterio v2 (placebo y tabla final)."""
    liga = fp.validos(almacen.cargar("partidos"))
    grupos = partidos.assign(grupo=np.where(partidos["prueba"], "prueba", np.where(partidos["entrenador_corto"] == nuevo, "nuevo", "previos")))
    conteo = grupos.groupby("grupo").size()
    torneos = grupos.groupby("grupo")["torneo_corto"].agg(lambda s: ", ".join(dict.fromkeys(s)))
    salida = {"datos": {"liga": int(len(liga)), "nuevo": int(conteo.get("nuevo", 0)), "previos": int(conteo.get("previos", 0)),
                        "prueba": int(conteo.get("prueba", 0)), "torneos_nuevo": torneos.get("nuevo", ""),
                        "torneos_previos": torneos.get("previos", ""), "torneos_prueba": torneos.get("prueba", "")},
              "pca": {"varianza": _num(pca.varianza, 3), "correlacion": _num(pca.correlacion, 3), "mismo_signo": bool(pca.mismo_signo),
                      "minutos": int(pca.minutos)},
              "criterio": None}
    placebo, final = DIR_HALLAZGOS / "placebo.parquet", DIR_HALLAZGOS / "tabla_final.parquet"
    if placebo.exists() and final.exists():
        pl, tf = pd.read_parquet(placebo), pd.read_parquet(final)
        v1 = 0
        for archivo in ("quiebres_jardine", "quiebres_contra_predecesores", "agresividad", "estilo", "huella"):
            ruta = DIR_HALLAZGOS / f"{archivo}.parquet"
            if ruta.exists():
                t = pd.read_parquet(ruta)
                if archivo == "agresividad":
                    t = t[t["grupo"] == nuevo]
                v1 += int((t["pasa_v1"] if "pasa_v1" in t else t["pasa_1a3"]).sum())
        salida["criterio"] = {"placebo_pruebas": int(len(pl)), "placebo_v1": int(pl["pasa_v1"].sum()), "placebo_v2": int(pl["pasa"].sum()),
                              "pruebas": int(len(tf)), "pasan_v1": v1, "pasan_v2": int(tf["pasa"].sum()),
                              "placebo_1a3": int(pl["pasa_1a3"].sum()), "reales_1a3": None, "reales_pruebas": None}
        reales = DIR_HALLAZGOS / "quiebres_jardine.parquet"  # la misma familia del placebo (auditoría del 19 oct, N3)
        if reales.exists():
            qj = pd.read_parquet(reales)
            salida["criterio"].update({"reales_1a3": int(qj["pasa_1a3"].sum()), "reales_pruebas": int(len(qj))})
    return salida


def datos_decidir(p: dict, team: int) -> dict:
    """Matriz de situaciones (notebook 05), fichas de 10 segundos, balón parado y uso de jugadores (notebook 04)."""
    salida: dict = {"matriz": [], "base": None, "fichas": fichas_rivales(p, team), "balon_parado": None, "jugadores": None,
                    "casos": [], "validacion": []}
    casos = DIR_HALLAZGOS / "casos_cl26.json"  # notebook 07
    if casos.exists():
        salida["casos"] = json.loads(casos.read_text(encoding="utf-8"))
    val = DIR_HALLAZGOS / "validacion_cl26.parquet"  # notebook 06
    if val.exists():
        formato = {d["titulo"]: d for d in PRINCIPIOS}

        def fmt(titulo: str, v: float) -> str | None:
            d = formato.get(titulo, {"escala": 1, "dec": 3, "unidad": ""})
            return None if pd.isna(v) else f"{v * d['escala']:+.{d['dec']}f}{d['unidad']}"

        salida["validacion"] = [{"principio": r.principio, "veredicto": r.veredicto, "texto": r.veredicto_texto,
                                 "entrenamiento": fmt(r.principio, r.dif_entrenamiento), "prueba": fmt(r.principio, r.dif_prueba),
                                 "bajo": fmt(r.principio, r.bajo), "alto": fmt(r.principio, r.alto), "partidos": int(r.partidos_prueba)}
                                for r in pd.read_parquet(val).itertuples()]
    rm, rb = DIR_HALLAZGOS / "matriz.parquet", DIR_HALLAZGOS / "matriz_base.parquet"
    if rm.exists() and rb.exists():
        base = pd.read_parquet(rb).iloc[0]
        salida["matriz"] = [decision.fila_matriz(r, base) for _, r in pd.read_parquet(rm).iterrows()]
        salida["base"] = {"indice": _num(base["indice"], 0), "ppda": _num(base["ppda"], 1), "xg_dif_90": _num(base["xg_dif_90"])}

    def resumen(archivo: str, nombres: dict, dec: int) -> list[dict]:
        ruta = DIR_HALLAZGOS / f"{archivo}.parquet"
        if not ruta.exists():
            return []
        t = pd.read_parquet(ruta)
        return [{"etq": nombres.get(r.metrica, r.metrica), "jardine": _num(r.nuevo, dec), "previos": _num(r.previos, dec),
                 "q": _num(r.q, 3), "pasa": bool(r.pasa)} for r in t.itertuples()]

    rz = DIR_HALLAZGOS / "balon_parado_zonas.parquet"
    if rz.exists():
        zt = pd.read_parquet(rz).pivot_table(index=["lado", "zona"], columns="grupo", values="xg_por_partido")
        salida["balon_parado"] = {
            "resumen": resumen("balon_parado", balon_parado.NOMBRES, 2),
            "zonas": [{"lado": lado, "zona": zona, "jardine": _num(f.get("Jardine")), "previos": _num(f.get("Predecesores"))}
                      for (lado, zona), f in zt.iterrows()]}
    if (DIR_HALLAZGOS / "jugadores.parquet").exists():
        salida["jugadores"] = {"resumen": resumen("jugadores", jugadores.NOMBRES, 2) + resumen("jugadores_lineas_criterio", jugadores.NOMBRES, 2)}
    return salida


if __name__ == "__main__":
    sys.exit(main())
