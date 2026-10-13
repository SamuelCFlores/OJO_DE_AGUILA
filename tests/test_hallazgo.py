"""Pruebas del criterio de hallazgo y del bootstrap por partido."""

import numpy as np
import pandas as pd
import pytest

from ojo.lentes import hallazgo

CFG = {"tamano_min_de": 0.5, "min_torneos_misma_direccion": 4}


def test_bootstrap_remuestrea_partidos_completos() -> None:
    # Un partido con 9 filas de valor 1 y otro con 1 fila de valor 0: la media pondera filas, no partidos.
    tabla = pd.DataFrame({"match_id": [1] * 9 + [2], "efecto": [1.0] * 9 + [0.0]})
    medias = hallazgo.medias_bootstrap(tabla, "efecto", np.random.default_rng(0), repeticiones=500)
    assert set(np.round(np.unique(medias), 2)) <= {0.0, 0.9, 1.0}
    bajo, alto = hallazgo.intervalo(medias, 0.95)
    assert bajo <= 0.9 <= alto


def test_criterio_exige_las_tres_condiciones() -> None:
    assert hallazgo.evaluar(0.6, 0.2, 1.0, 1.0, 4, CFG)["pasa"]
    assert not hallazgo.evaluar(0.6, -0.1, 1.0, 1.0, 5, CFG)["pasa"]  # el intervalo cruza 0
    assert not hallazgo.evaluar(0.3, 0.1, 0.5, 1.0, 5, CFG)["pasa"]  # 0.3 DE: pequeño
    resultado = hallazgo.evaluar(-0.8, -1.2, -0.4, 1.0, 3, CFG)  # solo 3 torneos en la misma dirección
    assert not resultado["pasa"] and resultado["ic_sin_cero"] and resultado["tamano_suficiente"]
    assert resultado["tamano_de"] == pytest.approx(-0.8)


def test_direcciones_cuenta_torneos_con_el_mismo_signo() -> None:
    por_torneo = pd.Series({"AP23": 0.2, "CL24": -0.1, "AP24": 0.3, "CL25": np.nan, "AP25": 0.1})
    assert hallazgo.direcciones(por_torneo, 0.15) == 3
    assert hallazgo.direcciones(por_torneo, -0.15) == 1
