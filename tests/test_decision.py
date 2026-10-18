"""Pruebas de los textos de decisión (ojo.salidas.decision)."""

import pandas as pd

from ojo.salidas import decision

CFG = {"dif_indice": 5, "dif_ppda": 2, "minutos_min": 300}
BASE = pd.Series({"indice": 57, "ppda": 16.0})


def _fila(**kw) -> pd.Series:
    base = {"nombre": "Ganando por 1", "indice": 49, "indice_rival": 55, "ppda": 17.4, "minutos": 1982, "partidos": 70,
            "xg_dif_90": .31, "xg_dif_bajo": -.04, "xg_dif_alto": .66, "previos_xg_dif_90": .38}
    base.update(kw)
    return pd.Series(base)


def test_replegado_y_parejo_pide_no_regalar_la_iniciativa() -> None:
    f = decision.fila_matriz(_fila(), BASE, cfg=CFG)
    assert f["nivel"] == decision.PAREJO
    assert "se repliega" in f["hace"]
    assert f["recomendacion"].startswith("No regalar la iniciativa")
    assert "con Solari y Ortiz, +0.38" in f["evidencia"] and not f["muestra_chica"]


def test_domina_con_presion_y_muestra_chica() -> None:
    f = decision.fila_matriz(_fila(indice=65, ppda=13.0, xg_dif_bajo=.7, xg_dif_alto=2.5, xg_dif_90=1.5, minutos=76), BASE, cfg=CFG)
    assert f["nivel"] == decision.DOMINA and "presiona más" in f["hace"] and "más iniciativa" in f["hace"]
    assert f["recomendacion"].startswith("Sostener el plan") and f["muestra_chica"]


def test_registro_de_resultados() -> None:
    t = pd.DataFrame({"goles_favor": [2, 1, 0], "goles_contra": [0, 1, 1], "xg_neto": [1.0, 0.2, -0.3]})
    r = decision.registro(t)
    assert (r["g"], r["e"], r["p"]) == (1, 1, 1) and abs(r["puntos"] - 4 / 3) < 1e-9
    assert decision.texto_registro(r).startswith("3 partidos: 1 ganado, 1 empate, 1 perdido")
    assert decision.texto_riesgo(.004) == "menos de 1 %" and decision.texto_riesgo(.064) == "6 %"


def test_con_uno_menos_replegarse_es_lo_esperado() -> None:
    f = decision.fila_matriz(_fila(situacion="uno_menos", nombre="Con uno menos", indice=44, minutos=76), BASE, cfg=CFG)
    assert f["recomendacion"].startswith("Con uno menos, replegarse es lo esperado")
