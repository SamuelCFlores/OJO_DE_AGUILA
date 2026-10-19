"""Pruebas de la lente Voronoi con frames sintéticos (geometría verificable a mano)."""

import math

import pandas as pd
import pytest

from ojo.lentes import voronoi
from ojo.lentes.voronoi import Jugador

CANCHA_COMPLETA = [0, 0, 120, 0, 120, 80, 0, 80, 0, 0]


@pytest.fixture(autouse=True)
def sin_alcance(monkeypatch):
    """Parámetros fijos para que las cuentas se puedan hacer a mano."""
    base = voronoi.params()
    fijos = dict(base, voronoi=dict(base["voronoi"], min_dist_borde=2.0, alcance_max_yd=None, min_borde_arista_yd=0.5))
    monkeypatch.setattr(voronoi, "params", lambda: fijos)


def _simetrico() -> list[Jugador]:
    # Dos propios a la izquierda y dos rivales a la derecha, espejados en x = 60.
    return [Jugador(40, 20, True, actor=True), Jugador(40, 60, True), Jugador(80, 20, False), Jugador(80, 60, False)]


def test_control_simetrico_es_la_mitad() -> None:
    r = voronoi.analizar_frame(_simetrico(), CANCHA_COMPLETA)
    assert r.control == pytest.approx(0.5)
    assert r.area_total == pytest.approx(120 * 80)
    assert r.frontera == pytest.approx(80)  # la frontera es la línea x = 60 de punta a punta


def test_grafo_vecindad_y_metricas_del_actor() -> None:
    r = voronoi.analizar_frame(_simetrico(), CANCHA_COMPLETA)
    # El actor (40, 20) toca a su compañero (40, 60) y al rival de enfrente (80, 20);
    # con el rival en diagonal (80, 60) solo comparte el punto (60, 40): no es vecino.
    assert r.apoyos == 1
    assert r.rivales_cerca == 1
    assert r.distancia_companeros == pytest.approx(40)


def test_recorte_al_area_visible() -> None:
    mitad_izquierda = [0, 0, 70, 0, 70, 80, 0, 80, 0, 0]
    jugadores = [Jugador(30, 20, True, actor=True), Jugador(30, 60, True), Jugador(65, 20, False), Jugador(65, 60, False)]
    r = voronoi.analizar_frame(jugadores, mitad_izquierda)
    # Rivales a 5 yd del borde visible (>= 2): se conservan. Frontera en x = 47.5.
    assert r.area_total == pytest.approx(70 * 80)
    assert r.control == pytest.approx(47.5 / 70)


def test_excluye_jugadores_pegados_al_borde_salvo_el_actor() -> None:
    jugadores = _simetrico() + [Jugador(119, 40, False), Jugador(1, 40, True, actor=False)]
    r = voronoi.analizar_frame(jugadores, CANCHA_COMPLETA)
    assert len(r.jugadores) == 4  # los dos que están a 1 yd del borde quedan fuera
    actor_en_borde = [Jugador(1, 40, True, actor=True)] + _simetrico()[1:]
    r2 = voronoi.analizar_frame(actor_en_borde, CANCHA_COMPLETA)
    assert r2.indice_actor is not None


def test_alcance_limita_las_zonas_vacias(monkeypatch) -> None:
    base = voronoi.params()
    con_alcance = dict(base, voronoi=dict(base["voronoi"], alcance_max_yd=10))
    monkeypatch.setattr(voronoi, "params", lambda: con_alcance)
    r = voronoi.analizar_frame(_simetrico(), CANCHA_COMPLETA)
    circulo = math.pi * 10**2
    assert r.area_total == pytest.approx(4 * circulo, rel=0.01)  # cuatro círculos completos, sin traslape
    assert r.control == pytest.approx(0.5, abs=0.01)
    assert r.aristas == []  # círculos de 10 yd separados 40 yd: nadie es vecino


def test_sin_area_visible_o_con_pocos_jugadores_no_hay_resultado() -> None:
    assert voronoi.analizar_frame(_simetrico(), []) is None
    assert voronoi.analizar_frame(_simetrico()[:3], CANCHA_COMPLETA) is None


def test_por_evento_une_eventos_y_frames() -> None:
    eventos = pd.DataFrame({"id": ["e1", "e2"], "match_id": [7, 7], "equipo_id": [1, 1]})
    frames = pd.DataFrame({"event_uuid": ["e1"], "area_visible": [CANCHA_COMPLETA]})
    jugadores = pd.DataFrame([
        {"event_uuid": "e1", "x": j.x, "y": j.y, "companero": j.propio, "actor": j.actor, "portero": False}
        for j in _simetrico()
    ])
    tabla = voronoi.por_evento(eventos, frames, jugadores)
    assert list(tabla["id"]) == ["e1"]
    assert tabla.loc[0, "control"] == pytest.approx(0.5)


def test_actor_con_coordenadas_repetidas_se_conserva() -> None:
    """Auditoría B1: si otro jugador comparte coordenadas con el actor y llega antes, se queda el actor."""
    repetido = [Jugador(40, 20, False)] + _simetrico()
    r = voronoi.analizar_frame(repetido, CANCHA_COMPLETA)
    assert r.indice_actor is not None and r.jugadores[r.indice_actor].actor
