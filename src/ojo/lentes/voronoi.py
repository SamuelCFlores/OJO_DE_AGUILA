"""Control territorial con Voronoi sobre el 360 y su grafo de vecindad.

Cada jugador visible "controla" la zona de la cancha más cercana a él. Las celdas se
recortan a cancha ∩ área visible ∩ alcance (radio máximo alrededor de cada jugador), y
dos jugadores son vecinos si sus celdas comparten borde: es el dual de la triangulación
de Delaunay, calculado solo dentro de lo que se ve.

REF1: contexto/framework.md, objetos "Control territorial" y "Grafo de vecindad".
NOTA1: todo está en la perspectiva del evento (el equipo del actor ataca hacia x = 120);
"propio" significa del equipo del actor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

import numpy as np
import pandas as pd
import shapely
from scipy.spatial import Delaunay, QhullError
from shapely.geometry import MultiPoint, Point, Polygon, box

from ojo.config import params

MIN_JUGADORES_POR_EQUIPO = 2  # sin dos jugadores de cada lado no hay "control" que comparar
CUARTOS_CIRCULO = 8  # PERF3: segmentos por cuarto de círculo del alcance (error < 0.2 yd con 20 yd)


@dataclass
class Jugador:
    """Jugador visible en un frame 360."""

    x: float
    y: float
    propio: bool
    actor: bool = False
    portero: bool = False

    @property
    def punto(self) -> Point:
        return Point(self.x, self.y)


@dataclass
class ResultadoFrame:
    """Voronoi de un frame y las métricas que salen de él y de su grafo."""

    jugadores: list[Jugador]
    celdas: list[Polygon]
    visible: Polygon
    aristas: list[tuple[int, int]] = field(default_factory=list)
    largo_bordes: list[float] = field(default_factory=list)  # yd de borde compartido por arista

    @property
    def area_propia(self) -> float:
        return sum(c.area for c, j in zip(self.celdas, self.jugadores) if j.propio)

    @property
    def area_total(self) -> float:
        return sum(c.area for c in self.celdas)

    @property
    def control(self) -> float:
        """Fracción del espacio alcanzado que controla el equipo del actor (0 a 1)."""
        return self.area_propia / self.area_total if self.area_total else np.nan

    @property
    def frontera(self) -> float:
        """Largo (yd) de los bordes compartidos entre una celda propia y una rival."""
        return float(sum(
            largo for (a, b), largo in zip(self.aristas, self.largo_bordes)
            if self.jugadores[a].propio != self.jugadores[b].propio
        ))

    @property
    def indice_actor(self) -> int | None:
        return next((i for i, j in enumerate(self.jugadores) if j.actor), None)

    def vecinos(self, i: int) -> list[int]:
        return [b if a == i else a for a, b in self.aristas if i in (a, b)]

    @property
    def apoyos(self) -> float:
        """Compañeros vecinos del actor: opciones cercanas (NaN si no hay actor)."""
        i = self.indice_actor
        return np.nan if i is None else sum(self.jugadores[v].propio for v in self.vecinos(i))

    @property
    def rivales_cerca(self) -> float:
        """Rivales vecinos del actor: presión inmediata (NaN si no hay actor)."""
        i = self.indice_actor
        return np.nan if i is None else sum(not self.jugadores[v].propio for v in self.vecinos(i))

    @property
    def distancia_companeros(self) -> float:
        """Distancia media (yd) entre compañeros vecinos: qué tan junto está el bloque propio."""
        distancias = [
            np.hypot(self.jugadores[a].x - self.jugadores[b].x, self.jugadores[a].y - self.jugadores[b].y)
            for a, b in self.aristas
            if self.jugadores[a].propio and self.jugadores[b].propio
        ]
        return float(np.mean(distancias)) if distancias else np.nan

    def metricas(self) -> dict[str, float]:
        return {
            "control": self.control, "frontera": self.frontera, "apoyos": self.apoyos,
            "rivales_cerca": self.rivales_cerca, "distancia_companeros": self.distancia_companeros,
            "n_jugadores": len(self.jugadores), "area_visible": self.visible.area,
        }


def cancha() -> Polygon:
    c = params()["campo"]
    return box(0, 0, c["largo"], c["ancho"])


def poligono_visible(area_visible: list[float] | np.ndarray | None) -> Polygon | None:
    """Polígono del área visible (lista plana x1, y1, x2, y2, ...) recortado a la cancha."""
    if area_visible is None or len(area_visible) < 6:
        return None
    coords = list(zip(area_visible[0::2], area_visible[1::2]))
    poligono = Polygon(coords).buffer(0).intersection(cancha())
    return poligono if poligono.area > 0 else None


def _puntos(jugadores: list[Jugador]) -> np.ndarray:
    return shapely.points([(j.x, j.y) for j in jugadores])


def filtrar_jugadores(jugadores: list[Jugador], visible: Polygon, min_dist_borde: float) -> list[Jugador]:
    """Jugadores dentro del área visible y lejos de su borde; el actor se conserva siempre.

    OBS2: un jugador pegado al borde de la toma puede tener rivales fuera de cámara que le
    quitarían espacio; por eso se excluye. El actor se conserva para poder medir sus vecinos.
    """
    if not jugadores:
        return []
    puntos = _puntos(jugadores)
    dentro = shapely.contains(visible.buffer(1e-6), puntos)
    lejos = shapely.distance(visible.boundary, puntos) >= min_dist_borde
    elegidos, vistos = [], set()
    for j, d, l in zip(jugadores, dentro, lejos):
        clave = (round(j.x, 2), round(j.y, 2))
        if clave in vistos or not d or not (l or j.actor):
            continue
        vistos.add(clave)
        elegidos.append(j)
    return elegidos


def celdas(jugadores: list[Jugador], visible: Polygon, alcance: float | None) -> list[Polygon]:
    """Celda de Voronoi de cada jugador, recortada a cancha ∩ visible ∩ su radio de alcance."""
    limite = cancha()
    puntos = _puntos(jugadores)
    # PERF1: ordered=True devuelve las celdas en el orden de los jugadores, y las operaciones van
    # vectorizadas sobre arreglos de shapely (una llamada a GEOS por lote, no por celda).
    diagrama = shapely.voronoi_polygons(shapely.multipoints(puntos), extend_to=limite, ordered=True)
    resultado = shapely.intersection(shapely.get_parts(diagrama), limite.intersection(visible))
    if alcance:
        resultado = shapely.intersection(resultado, shapely.buffer(puntos, alcance, quad_segs=CUARTOS_CIRCULO))
    return list(resultado)


def _pares_delaunay(jugadores: list[Jugador]) -> list[tuple[int, int]]:
    """Pares candidatos a vecinos: aristas de la triangulación de Delaunay (o todos si son pocos)."""
    todos = list(combinations(range(len(jugadores)), 2))
    if len(jugadores) < 4:
        return todos
    try:
        tri = Delaunay(np.array([[j.x, j.y] for j in jugadores]))
    except QhullError:  # jugadores alineados: no hay triangulación, se revisan todos los pares
        return todos
    return sorted({tuple(sorted((int(a), int(b)))) for s in tri.simplices for a, b in combinations(s, 2)})


def grafo_vecindad(jugadores: list[Jugador], lista_celdas: list[Polygon],
                   min_borde: float) -> tuple[list[tuple[int, int]], list[float]]:
    """Pares de jugadores cuyas celdas comparten al menos min_borde yardas de borde, y ese largo.

    PERF2: solo se revisan las aristas de Delaunay; dos celdas de Voronoi que se tocan siempre
    son vecinas en Delaunay, así que no se pierde ningún par.
    """
    pares = _pares_delaunay(jugadores)
    if not pares:
        return [], []
    arreglo = np.array(lista_celdas, dtype=object)
    a, b = np.array(pares).T
    largos = shapely.length(shapely.intersection(arreglo[a], arreglo[b]))
    elegidos = [(par, float(largo)) for par, largo in zip(pares, largos) if largo >= min_borde]
    return [p for p, _ in elegidos], [largo for _, largo in elegidos]


def analizar_frame(jugadores: list[Jugador], area_visible: list[float] | np.ndarray | None) -> ResultadoFrame | None:
    """Voronoi y grafo de un frame; None si no hay área visible o faltan jugadores de algún equipo."""
    cfg = params()["voronoi"]
    visible = poligono_visible(area_visible)
    if visible is None:
        return None
    validos = filtrar_jugadores(jugadores, visible, cfg["min_dist_borde"])
    propios = sum(j.propio for j in validos)
    if propios < MIN_JUGADORES_POR_EQUIPO or len(validos) - propios < MIN_JUGADORES_POR_EQUIPO:
        return None
    lista_celdas = celdas(validos, visible, cfg.get("alcance_max_yd"))
    resultado = ResultadoFrame(validos, lista_celdas, visible)
    resultado.aristas, resultado.largo_bordes = grafo_vecindad(validos, lista_celdas, cfg["min_borde_arista_yd"])
    return resultado


def jugadores_de_frame(tabla: pd.DataFrame) -> list[Jugador]:
    """Convierte las filas de frames_jugadores de un evento en objetos Jugador."""
    return [
        Jugador(float(f.x), float(f.y), bool(f.companero), bool(f.actor), bool(f.portero))
        for f in tabla.itertuples(index=False)
    ]


def por_evento(eventos: pd.DataFrame, frames: pd.DataFrame, frames_jugadores: pd.DataFrame) -> pd.DataFrame:
    """Métricas de Voronoi para cada evento con frame 360 analizable.

    Devuelve una fila por evento: id, match_id, equipo_id (del actor) y las métricas de
    ResultadoFrame.metricas(). Los eventos sin frame, sin área visible o con pocos
    jugadores visibles no aparecen.
    """
    visibles = frames.set_index("event_uuid")["area_visible"]
    por_uuid = dict(tuple(frames_jugadores.groupby("event_uuid")))
    filas = []
    for e in eventos[eventos["id"].isin(visibles.index)].itertuples(index=False):
        tabla = por_uuid.get(e.id)
        if tabla is None:
            continue
        resultado = analizar_frame(jugadores_de_frame(tabla), visibles[e.id])
        if resultado is None:
            continue
        filas.append({"id": e.id, "match_id": e.match_id, "equipo_id": e.equipo_id, **resultado.metricas()})
    return pd.DataFrame(filas)
