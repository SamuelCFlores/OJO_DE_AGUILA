"""Recrea el Voronoi de una jugada real paso a paso en un HTML (evento, cámara, jugadores, celdas, recorte, control).

Tres formas de elegir la jugada (pases completos del equipo de params.yaml en juego abierto, de más a
menos jugadores visibles, y que se puedan analizar):
    --partido MATCH_ID   la mejor jugada del tercio medio de ese partido
    --quiebre TIPO       la mejor jugada en los minutos después de ese tipo de quiebre, en los partidos
                         de entrenamiento del entrenador de params.yaml (p. ej. sustitucion_tactica_propia)
    --evento UUID        exactamente ese evento (el uuid sale de --listar); junto con --quiebre o --partido
                         conserva el contexto del quiebre en el reporte
Con --listar no genera nada: imprime las mejores candidatas con su uuid y el comando para generar una.
Escribe outputs/reportes/voronoi_paso_a_paso.html (fuera de git: lleva posiciones reales).

Cómo correrlo (desde la raíz del repo y con el entorno activado; antes 03):
    python scripts/06_paso_a_paso.py --listar --quiebre sustitucion_tactica_propia
    python scripts/06_paso_a_paso.py --quiebre sustitucion_tactica_propia
    python scripts/06_paso_a_paso.py --partido 4057783
El uuid para --evento se copia de la tabla de --listar (al final imprime el comando completo).
"""

from __future__ import annotations

import argparse
import re
import sys

import pandas as pd

from ojo.config import DIR_SALIDAS, params
from ojo.datos import almacen
from ojo.framework import juego, quiebres
from ojo.framework import partidos as fp
from ojo.lentes import voronoi
from ojo.salidas import paso_a_paso

SALIDA = DIR_SALIDAS / "reportes" / "voronoi_paso_a_paso.html"
COLUMNAS = ["id", "match_id", "indice", "periodo", "minuto", "segundo", "tipo", "equipo_id", "patron", "x", "y",
            "fin_x", "fin_y", "pase_resultado"]
UUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


def _pases_del_equipo(eventos: pd.DataFrame, frames: pd.DataFrame) -> pd.DataFrame:
    """Pases completos del equipo en juego abierto con frame 360, con sus jugadores visibles (n)."""
    team_id = params()["equipo"]["team_id"]
    filtro = (juego.es_pase_completo(eventos) & juego.es_juego_abierto(eventos) & (eventos["equipo_id"] == team_id)
              & eventos["id"].isin(frames.index))
    elegidos = eventos[filtro]
    return elegidos.assign(n=elegidos["id"].map(frames["n_visibles"]))


def etiqueta_quiebre(tipo: str) -> str:
    """Tipo de quiebre en lenguaje de cancha, p. ej. "una sustitución táctica del América"."""
    equipo = params()["equipo"]["nombre"]
    lado = {"favor": f"del {equipo}", "contra": "del rival", "propio": f"del {equipo}", "propia": f"del {equipo}",
            "rival": "del rival"}
    base, sufijo = tipo.rsplit("_", 1)
    if base == "expulsion":  # una expulsión a favor es del rival
        return f"una expulsión {lado['rival' if sufijo == 'favor' else 'propio']}"
    nombres = {"gol": "un gol", "cambio_sistema": "un cambio de sistema", "sustitucion_tactica": "una sustitución táctica",
               "sustitucion_lesion": "un cambio por lesión"}
    return f"{nombres[base]} {lado[sufijo]}"


def _ordenar(pases: pd.DataFrame) -> pd.DataFrame:
    """De más a menos jugadores visibles; los empates, por partido y orden del evento (siempre igual)."""
    return pases.sort_values(["n", "match_id", "indice"], ascending=[False, True, True], kind="stable")


def candidatos_partido(match_id: int) -> pd.DataFrame:
    """Pases del equipo en el tercio medio de un partido, de más a menos jugadores visibles."""
    tercio = params()["tercios"]
    eventos = almacen.cargar("eventos", [match_id], columnas=COLUMNAS)
    frames = almacen.cargar("frames", [match_id], columnas=["event_uuid", "n_visibles"]).set_index("event_uuid")
    pases = _pases_del_equipo(eventos, frames)
    pases = pases[pases["x"].between(tercio["defensivo_max_x"], tercio["final_min_x"])]
    return _ordenar(pases.assign(contexto=""))


def candidatos_quiebre(tipo: str) -> pd.DataFrame:
    """Pases del equipo en la ventana después de cada quiebre de ese tipo (entrenador de params.yaml, sin prueba)."""
    p = params()
    tabla = fp.con_torneo(fp.del_equipo(fp.validos(almacen.cargar("partidos")), p["equipo"]["team_id"]))
    tabla = tabla[(tabla["entrenador_id"] == p["entrenador"]["manager_id"]) & ~fp.es_prueba(tabla)]
    ids = tabla["match_id"].astype(int).tolist()
    eventos = almacen.cargar("eventos", ids, columnas=COLUMNAS + ["tiro_resultado", "tarjeta", "formacion",
                                                                  "sustitucion_resultado"])
    q = quiebres.ventanas(quiebres.detectar(eventos, p["equipo"]["team_id"]), quiebres.limites_periodo(eventos))
    q = q[(q["tipo"] == tipo) & q["valida"]]
    frames = almacen.cargar("frames", ids, columnas=["event_uuid", "n_visibles"]).set_index("event_uuid")
    pases = _pases_del_equipo(eventos, frames).merge(
        q[["match_id", "periodo", "minuto", "despues_desde", "despues_hasta"]].rename(columns={"minuto": "minuto_quiebre"}),
        on=["match_id", "periodo"])
    pases = pases[pases["minuto"].between(pases["despues_desde"], pases["despues_hasta"])]
    rivales = tabla.set_index("match_id")["rival"]
    texto = etiqueta_quiebre(tipo)
    pases["contexto"] = [f"{m - mq} min después de {texto} en el {mq}', contra {rivales.get(mid, 'el rival')}"
                         for m, mq, mid in zip(pases["minuto"], pases["minuto_quiebre"], pases["match_id"])]
    return _ordenar(pases).drop_duplicates("id")


def candidato_evento(uuid: str) -> pd.DataFrame:
    """El evento pedido (vacío si no está en los datos procesados)."""
    encontrado = almacen.consultar(f"SELECT match_id FROM eventos WHERE id = '{uuid}'")
    if encontrado.empty:
        return pd.DataFrame(columns=[*COLUMNAS, "contexto"])
    match_id = int(encontrado["match_id"].iloc[0])
    eventos = almacen.cargar("eventos", [match_id], columnas=COLUMNAS)
    frames = almacen.cargar("frames", [match_id], columnas=["event_uuid", "n_visibles"]).set_index("event_uuid")
    elegido = eventos[eventos["id"] == uuid]
    return elegido.assign(n=elegido["id"].map(frames["n_visibles"]), contexto="")


def analizables(candidatas: pd.DataFrame, cuantas: int):
    """Recorre las candidatas en orden y entrega (fila, jugadores, área visible) de las que se pueden analizar."""
    cache: dict[int, tuple[pd.DataFrame, pd.DataFrame]] = {}
    entregadas = 0
    for e in candidatas.itertuples():
        if e.match_id not in cache:
            cache[e.match_id] = (almacen.cargar("frames", [e.match_id]).set_index("event_uuid"),
                                 almacen.cargar("frames_jugadores", [e.match_id]))
        frames, jugadores = cache[e.match_id]
        if e.id not in frames.index:
            continue
        todos = voronoi.jugadores_de_frame(jugadores[jugadores["event_uuid"] == e.id])
        area = frames.loc[e.id, "area_visible"]
        resultado = voronoi.analizar_frame(todos, area)
        if resultado is None:
            continue
        yield e, todos, area, resultado
        entregadas += 1
        if entregadas >= cuantas:
            return


def generar(e, todos: list, area) -> None:
    """Escribe el HTML paso a paso de una jugada."""
    p = params()
    equipo = p["equipo"]["nombre"] if e.equipo_id == p["equipo"]["team_id"] else "el rival"
    jugada = paso_a_paso.Jugada(tipo={"Pass": "Pase"}.get(e.tipo, e.tipo), minuto=int(e.minuto), segundo=int(e.segundo),
                                equipo=equipo, x=e.x, y=e.y,
                                fin_x=None if pd.isna(e.fin_x) else e.fin_x, fin_y=None if pd.isna(e.fin_y) else e.fin_y,
                                contexto=e.contexto)
    pasos = paso_a_paso.pasos(jugada, todos, area)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(paso_a_paso.html(pasos, "El Voronoi paso a paso",
                                       "Cómo se mide el control del espacio en una jugada real"), encoding="utf-8")
    print(f"Reporte: {SALIDA.relative_to(DIR_SALIDAS.parent)} (datos reales: no se publica ni se sube a git)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--partido", type=int, metavar="MATCH_ID", help="elige la jugada dentro de ese partido")
    grupo.add_argument("--quiebre", choices=quiebres.TIPOS, metavar="TIPO",
                       help=f"elige la jugada tras ese tipo de quiebre: {', '.join(quiebres.TIPOS)}")
    parser.add_argument("--evento", metavar="UUID", help="usa exactamente ese evento (uuid de --listar)")
    parser.add_argument("--listar", action="store_true", help="solo imprime las mejores candidatas con su uuid")
    parser.add_argument("--top", type=int, default=10, help="cuántas candidatas imprime --listar (por defecto 10)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if not (args.partido or args.quiebre or args.evento):
        parser.error("indica --partido, --quiebre o --evento")
    if args.evento and not UUID.fullmatch(args.evento):
        print("✗ --evento debe ser el uuid de un evento (36 caracteres, como los que imprime --listar).")
        return 1
    if args.quiebre:
        candidatas = candidatos_quiebre(args.quiebre)
    elif args.partido:
        candidatas = candidatos_partido(args.partido)
    else:
        candidatas = candidato_evento(args.evento)
    if args.evento:
        candidatas = candidatas[candidatas["id"] == args.evento]
        if candidatas.empty:
            print("✗ Ese evento no está en los datos procesados o no cumple el filtro de --quiebre/--partido.")
            return 1

    if args.listar:
        filas = [{"uuid": e.id, "partido": e.match_id, "minuto": f"{e.minuto}:{e.segundo:02d}", "visibles": e.n,
                  "control": f"{r.control:.0%}", "contexto": e.contexto}
                 for e, _, _, r in analizables(candidatas, args.top)]
        if not filas:
            print("✗ No hay jugadas analizables con esos filtros.")
            return 1
        print(pd.DataFrame(filas).to_string(index=False))
        filtro = f"--quiebre {args.quiebre} " if args.quiebre else (f"--partido {args.partido} " if args.partido else "")
        print(f"\nPara generar una, copia su uuid en --evento. Por ejemplo, la primera:\n"
              f"    python scripts/06_paso_a_paso.py {filtro}--evento {filas[0]['uuid']}")
        return 0

    elegida = next(analizables(candidatas, 1), None)
    if elegida is None:
        print("✗ No hay una jugada analizable con esos filtros.")
        return 1
    e, todos, area, _ = elegida
    generar(e, todos, area)
    return 0


if __name__ == "__main__":
    sys.exit(main())
