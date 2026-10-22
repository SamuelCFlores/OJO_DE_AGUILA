"""Pruebas del veredicto de validación en el torneo de prueba (ojo.lentes.validacion)."""

import numpy as np
import pandas as pd

from ojo.lentes import validacion


def test_veredictos() -> None:
    assert validacion.veredicto(-1.5, -1.2, -2.0, -0.4, 19, 3) == "se_sostiene"
    assert validacion.veredicto(-1.5, -0.3, -1.0, 0.4, 19, 3) == "misma_direccion"
    assert validacion.veredicto(-1.5, 0.5, -0.2, 1.1, 19, 3) == "no_se_sostiene"
    assert validacion.veredicto(-1.5, -2.0, -3.0, -1.0, 2, 3) == "sin_muestra"
    assert validacion.veredicto(-1.5, np.nan, np.nan, np.nan, 5, 3) == "sin_muestra"


def test_diferencia_con_bootstrap() -> None:
    rng = np.random.default_rng(0)
    prueba = pd.DataFrame({"match_id": range(10), "v": 2.0 + rng.normal(scale=.1, size=10)})
    previos = pd.DataFrame({"match_id": range(100, 130), "v": 1.0 + rng.normal(scale=.1, size=30)})
    d = validacion.diferencia(prueba, previos, "v", np.random.default_rng(1))
    assert abs(d["dif"] - 1.0) < .1 and d["bajo"] > .8 and d["alto"] < 1.2 and d["partidos"] == 10
    vacio = validacion.diferencia(prueba.iloc[:0], previos, "v", np.random.default_rng(1))
    assert vacio["partidos"] == 0 and np.isnan(vacio["dif"])
