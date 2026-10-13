"""Pruebas de las piezas del caso puntual (sin datos reales)."""

from types import SimpleNamespace

import pandas as pd

from ojo.lentes import voronoi
from ojo.salidas import caso


def test_frame_del_rival_se_refleja_y_cambia_de_bando() -> None:
    jugadores = pd.DataFrame({"x": [100.0, 90.0], "y": [10.0, 30.0], "companero": [True, False],
                              "actor": [True, False], "portero": [False, False]})
    lista, area = caso.frame_del_equipo(jugadores, [0, 0, 120, 0, 120, 80, 0, 80], actor_es_del_equipo=False)
    assert (lista[0].x, lista[0].y, lista[0].propio, lista[0].actor) == (20, 70, False, True)
    assert (lista[1].x, lista[1].propio) == (30, True)
    assert area[:4] == [120, 80, 0, 80]
    propios, _ = caso.frame_del_equipo(jugadores, [0, 0, 1, 1, 0, 1], actor_es_del_equipo=True)
    assert isinstance(propios[0], voronoi.Jugador) and propios[0].propio


def test_textos_en_lenguaje_de_cancha() -> None:
    assert caso.formacion(4141) == "4-1-4-1"
    q = SimpleNamespace(tipo="cambio_sistema_rival", detalle="352→4141")
    assert caso.etiqueta_quiebre(q, "América", "Guadalajara") == "Guadalajara cambia de sistema (3-5-2 → 4-1-4-1)"
    falta = SimpleNamespace(tipo="Foul Committed", jugador_id=7, equipo_id=1, pase_receptor_id=None, pase_resultado=None,
                            x=80.0, y=60.0, fin_x=None, fin_y=None, tarjeta="Red Card", bajo_presion=False)
    assert caso.describir(falta, {7: "Fidalgo"}, {1: "América"}) == "Fidalgo comete falta: roja directa"
    conduce = SimpleNamespace(tipo="Carry", jugador_id=9, equipo_id=2, pase_receptor_id=None, pase_resultado=None,
                              x=20.0, y=10.0, fin_x=37.0, fin_y=10.0, tarjeta=None, bajo_presion=True)
    assert caso.describir(conduce, {}, {2: "Rival"}) == "Rival conduce 17 yd bajo presión"
