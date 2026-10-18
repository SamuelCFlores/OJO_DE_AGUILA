"""Pruebas del índice Proactivo–Reactivo, del Monte Carlo explicativo y de la foto del reproductor (sintéticas)."""

import numpy as np
import pandas as pd
import pytest

from ojo.lentes import indice, simulacion
from ojo.lentes.voronoi import Jugador, analizar_frame
from ojo.salidas import reproductor

SIGNOS = {"control": 1, "largo_pase": -1}


def test_indice_ordena_de_reactivo_a_proactivo() -> None:
    comp = pd.DataFrame({"control": [0.2, 0.5, 0.8], "largo_pase": [30.0, 22.0, 15.0]})
    escala = indice.ajustar(comp, SIGNOS)
    tabla = indice.calcular(comp, escala, SIGNOS)
    assert list(tabla["indice"]) == sorted(tabla["indice"])  # más control y pases más cortos = más proactivo
    assert tabla["z_largo_pase"].iloc[0] < 0 < tabla["z_largo_pase"].iloc[2]  # el signo invierte el pase largo
    assert tabla["indice"].iloc[2] == pytest.approx(100)


def test_indice_ignora_componentes_faltantes() -> None:
    comp = pd.DataFrame({"control": [0.2, 0.8, np.nan], "largo_pase": [25.0, 20.0, 18.0]})
    tabla = indice.calcular(comp, indice.ajustar(comp, SIGNOS), SIGNOS)
    assert tabla["compuesto"].notna().all()


def test_piezas_por_minuto_separan_control_y_transicion() -> None:
    ev = pd.DataFrame({"match_id": [1, 1, 1], "periodo": [1, 1, 1], "minuto": [3, 3, 3], "equipo_id": [7, 7, 7],
                       "tipo": ["Pass", "Carry", "Pressure"], "duracion": [2.0, 3.0, 1.0], "es_transicion": [False, True, None],
                       "directness": [0.4, 0.6, None], "x": [50.0, 60.0, 70.0], "y": [40.0, 40.0, 40.0],
                       "fin_x": [70.0, 65.0, np.nan], "fin_y": [40.0, 40.0, np.nan]})
    p = indice.piezas_por_minuto(ev).iloc[0]
    assert (p["dur_balon"], p["dur_fase"], p["dur_control"]) == (5.0, 5.0, 2.0)
    assert p["largo_suma"] == 20 and p["pases_n"] == 1


def test_montecarlo_reproducible_y_con_probabilidades_validas() -> None:
    a = simulacion.simular([0.9, 0.9], [0.05], repeticiones=5000, semilla=1)
    b = simulacion.simular([0.9, 0.9], [0.05], repeticiones=5000, semilla=1)
    assert a == b
    assert a.gana + a.empata + a.pierde == pytest.approx(1)
    assert a.gana > 0.9 and a.goles_favor == pytest.approx(1.8, abs=0.05)
    assert simulacion.simular([], [], repeticiones=100, semilla=1, base=(1, 0)).gana == 1


def test_foto_del_reproductor_es_liviana_y_completa() -> None:
    jugadores = [Jugador(50, 40, True, actor=True), Jugador(60, 25, True), Jugador(60, 55, True),
                 Jugador(70, 40, False), Jugador(75, 20, False), Jugador(75, 60, False)]
    resultado = analizar_frame(jugadores, [30, 10, 90, 10, 90, 70, 30, 70, 30, 10])
    f = reproductor.foto(resultado, "12:05", "Uno pasa a Dos", True)
    assert len(f["celdas"]) == len(f["propias"]) == 6 and len(f["jugadores"]) == 6
    assert f["frontera"] and f["visible"] and 0 < f["control"] < 1
    assert all(round(v, 1) == v for celda in f["celdas"] for v in celda)


def test_pca_reconoce_un_eje_comun() -> None:
    """Si todos los componentes salen de un mismo factor (con su signo), la PCA lo encuentra y coincide con el promedio."""
    rng = np.random.default_rng(0)
    factor = rng.normal(size=2000)
    signos = {"a": 1, "b": 1, "c": -1, "d": -1}
    comp = pd.DataFrame({c: s * factor + rng.normal(scale=.6, size=2000) for c, s in signos.items()})
    v = indice.verificar_pca(comp, signos)
    assert v.mismo_signo
    assert v.varianza > .6
    assert v.correlacion > .95
    assert v.minutos == 2000
