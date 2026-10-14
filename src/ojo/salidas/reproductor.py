"""Datos del reproductor: fotos 360 con su Voronoi, livianas para dibujarlas y animarlas en el navegador.

El "Voronoi en movimiento" es una secuencia de fotos (una por minuto, o una por acción en una jugada):
el 360 no identifica a los jugadores entre fotos, así que no se inventan trayectorias entre ellas.

REF1: contexto/framework.md, "Control territorial"; perspectiva del equipo como en ojo.salidas.caso.
IMPOR1: lleva posiciones reales: solo va en páginas de outputs/ (fuera de git).
"""

from __future__ import annotations

import pandas as pd
import shapely

from ojo.config import params
from ojo.lentes import voronoi
from ojo.salidas import caso as sc

DECIMALES = 1  # coordenadas en yardas con un decimal: suficiente para dibujar


def _plano(geometria) -> list[float]:
    """Anillo exterior de un polígono como lista plana [x1, y1, x2, y2, ...] redondeada."""
    return [round(v, DECIMALES) for xy in geometria.exterior.coords for v in xy]


def foto(resultado: voronoi.ResultadoFrame, reloj: str, texto: str, del_equipo: bool,
         flecha: tuple[float, float, float, float] | None = None) -> dict:
    """Una foto lista para el navegador: celdas, a quién pertenecen, frontera, jugadores y área visible.

    flecha: (x, y, fin_x, fin_y) del pase o la conducción, ya en la perspectiva del equipo.
    """
    tolerancia = params()["casos"]["simplificar_yd"]
    celdas, propias = [], []
    for celda, jugador in zip(resultado.celdas, resultado.jugadores):
        for g in sc._poligonos(shapely.simplify(celda, tolerancia)):
            celdas.append(_plano(g))
            propias.append(int(jugador.propio))
    frontera = []
    for a, b in resultado.aristas:
        if resultado.jugadores[a].propio != resultado.jugadores[b].propio:
            borde = resultado.celdas[a].intersection(resultado.celdas[b])
            for parte in getattr(borde, "geoms", [borde]):
                if parte.geom_type in ("LineString", "LinearRing") and parte.length > 0:
                    frontera.append([round(v, DECIMALES) for xy in parte.coords for v in xy])
    visibles = [_plano(g) for g in sc._poligonos(resultado.visible)]
    jugadores = [[round(j.x, DECIMALES), round(j.y, DECIMALES), int(j.propio), int(j.actor)] for j in resultado.jugadores]
    return {"reloj": reloj, "texto": texto, "eq": int(del_equipo), "control": round(resultado.control, 3),
            "celdas": celdas, "propias": propias, "frontera": frontera, "visible": visibles, "jugadores": jugadores,
            "flecha": None if flecha is None else [round(float(v), DECIMALES) for v in flecha]}


def flecha_de(e, del_equipo: bool) -> tuple[float, float, float, float] | None:
    """Flecha de un pase o una conducción en la perspectiva del equipo (las del rival se reflejan)."""
    if e.tipo not in {"Pass", "Carry"} or pd.isna(e.fin_x) or pd.isna(e.x):
        return None
    if del_equipo:
        return (e.x, e.y, e.fin_x, e.fin_y)
    campo = params()["campo"]
    return (campo["largo"] - e.x, campo["ancho"] - e.y, campo["largo"] - e.fin_x, campo["ancho"] - e.fin_y)


def por_minuto(eventos: pd.DataFrame, frames: pd.DataFrame, jugadores: pd.DataFrame, equipo_id: int,
               describir) -> dict[tuple[int, int], dict]:
    """La foto más completa de cada minuto (más jugadores visibles y analizable), en la perspectiva del equipo.

    describir(e) → texto de la acción. Devuelve {(periodo, minuto): foto}.
    """
    visibles = frames.set_index("event_uuid")["n_visibles"]
    areas = frames.set_index("event_uuid")["area_visible"]
    por_uuid = dict(tuple(jugadores.groupby("event_uuid")))
    candidatos = eventos[eventos["id"].isin(visibles.index) & (eventos["periodo"] != 5)].copy()
    candidatos["n"] = candidatos["id"].map(visibles)
    candidatos = candidatos.sort_values(["periodo", "minuto", "n", "indice"], ascending=[True, True, False, True])
    fotos: dict[tuple[int, int], dict] = {}
    for e in candidatos.itertuples():
        clave = (int(e.periodo), int(e.minuto))
        if clave in fotos or e.id not in por_uuid:
            continue
        del_equipo = e.equipo_id == equipo_id
        todos, area = sc.frame_del_equipo(por_uuid[e.id], areas[e.id], del_equipo)
        resultado = voronoi.analizar_frame(todos, area)
        if resultado is not None:
            fotos[clave] = foto(resultado, sc.reloj(e.minuto, e.segundo), describir(e), del_equipo, flecha_de(e, del_equipo))
    return fotos


def segundos(timestamp: str) -> float:
    """"00:44:12.345" (reloj de StatsBomb dentro del periodo) → 2652.345 segundos."""
    h, m, s = str(timestamp).split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def secuencia(eventos: pd.DataFrame, indice_final: int, frames: pd.DataFrame, jugadores: pd.DataFrame, equipo_id: int,
              describir, nombres: dict[int, str], posesiones_previas: int = 1) -> list[dict]:
    """Fotos de una jugada para animarla: todas las acciones con 360 de la posesión (y la anterior) hasta indice_final.

    Cada foto agrega t (segundos desde la primera), ids (pista estimada de cada jugador, ojo.lentes.seguimiento)
    y nombre (quien ejecuta, de Events + Lineups; el 360 no trae nombres).
    """
    from ojo.lentes import seguimiento  # import local: la lente solo se usa al animar

    cfg = params()["animacion"]
    ev = eventos.sort_values("indice")
    fila = ev[ev["indice"] == indice_final].iloc[0]
    sel = ev[ev["posesion"].between(fila["posesion"] - posesiones_previas, fila["posesion"]) & (ev["indice"] <= indice_final)
             & (ev["periodo"] == fila["periodo"]) & ev["id"].isin(frames["event_uuid"])]
    areas = frames.set_index("event_uuid")["area_visible"]
    por_uuid = dict(tuple(jugadores[jugadores["event_uuid"].isin(sel["id"])].groupby("event_uuid")))
    lista, tiempos, ultimo = [], [], None
    for e in sel.itertuples():
        t = segundos(e.timestamp)
        if e.id not in por_uuid:
            continue
        del_equipo = e.equipo_id == equipo_id
        todos, area = sc.frame_del_equipo(por_uuid[e.id], areas[e.id], del_equipo)
        resultado = voronoi.analizar_frame(todos, area)
        if resultado is None:
            continue
        f = foto(resultado, sc.reloj(e.minuto, e.segundo), describir(e), del_equipo, flecha_de(e, del_equipo))
        f["nombre"] = nombres.get(e.jugador_id, "")
        if ultimo is not None and t - ultimo < cfg["min_dt_s"]:  # casi el mismo instante: se queda la más reciente
            lista.pop()
            tiempos.pop()
        lista.append(f)
        tiempos.append(t)
        ultimo = t
    lista, tiempos = lista[-cfg["max_fotos"]:], tiempos[-cfg["max_fotos"]:]
    pistas = seguimiento.pistas([[(j[0], j[1], bool(j[2])) for j in f["jugadores"]] for f in lista], tiempos)
    for f, t, ids in zip(lista, tiempos, pistas):
        f["t"], f["ids"] = round(t - tiempos[0], 2), ids
    return lista
