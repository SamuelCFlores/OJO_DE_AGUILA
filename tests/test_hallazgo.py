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


# ---------- criterio v2 (18 oct): p del bootstrap, FDR y placebo ----------

def test_p_bootstrap_dos_colas() -> None:
    assert hallazgo.p_bootstrap(np.full(999, 0.5)) == pytest.approx(2 / 1000)  # nunca cruza 0: p mínimo, no 0
    mitad = np.r_[np.full(500, -1.0), np.full(500, 1.0)]
    assert hallazgo.p_bootstrap(mitad) == pytest.approx(1.0)
    assert np.isnan(hallazgo.p_bootstrap(np.array([np.nan])))


def test_fdr_bh_igual_a_la_definicion() -> None:
    p = np.array([0.01, 0.04, 0.03, 0.20, np.nan])
    q = hallazgo.fdr_bh(p)
    # ordenados: 0.01, 0.03, 0.04, 0.20 con m = 4 → crudos 0.04, 0.06, 0.0533, 0.20 → monótonos 0.04, 0.0533, 0.0533, 0.20
    assert q[0] == pytest.approx(0.04)
    assert q[2] == pytest.approx(0.04 * 4 / 3)  # p = 0.03 toma el q del siguiente (monotonía)
    assert q[1] == pytest.approx(0.04 * 4 / 3)
    assert q[3] == pytest.approx(0.20)
    assert np.isnan(q[4])


def test_con_fdr_exige_las_cuatro_condiciones() -> None:
    tabla = pd.DataFrame({"p": [0.001, 0.04, 0.002], "pasa": [True, True, False]})
    t = hallazgo.con_fdr(tabla, {"fdr_q": 0.05})
    assert t["pasa_1a3"].tolist() == [True, True, False]
    assert t["fdr"].tolist() == [True, True, True]  # q: 0.003, 0.04, 0.003
    assert t["pasa"].tolist() == [True, True, False]
    estricto = hallazgo.con_fdr(tabla, {"fdr_q": 0.01})
    assert estricto["pasa"].tolist() == [True, False, False]


def test_placebo_usa_el_primer_control_contra_los_demas() -> None:
    c = pd.DataFrame({
        "quiebre_id": ["q1"] * 3 + ["q2"],
        "id": ["q1|c0", "q1|c1", "q1|c2", "q2|c0"],
        "lado": "propio", "metrica": "xg",
        "cambio": [0.9, 0.1, 0.3, 0.5],
    })
    p = hallazgo.efectos_placebo(c)
    assert len(p) == 1  # q2 tiene un solo control: no sirve de placebo
    assert p.loc[0, "id"] == "q1|c0"
    assert p.loc[0, "efecto"] == pytest.approx(0.9 - 0.2)
