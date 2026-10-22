"""Regla del partido clave de cada rival (ojo.salidas.partido_clave)."""

import pandas as pd
import pytest

from ojo.salidas import partido_clave as pc


@pytest.mark.parametrize("etapa, esperado", [
    ("Clausura - Final", 4), ("Finals", 4), ("Apertura - Semi-finals", 3), ("Semi-finals", 3),
    ("Clausura - Quarter-finals", 2), ("Quarter-finals", 2), ("Play-offs - Semi-Finals", 1),
    ("Apertura", 0), (None, 0),
])
def test_fase(etapa, esperado):
    assert pc.fase(etapa) == esperado


def _partidos(filas):
    return pd.DataFrame(filas, columns=["match_id", "etapa", "fecha"]).assign(fecha=lambda d: pd.to_datetime(d["fecha"]))


def test_liguilla_gana_y_se_elige_la_vuelta_de_la_fase_mas_avanzada():
    p = _partidos([(1, "Apertura", "2024-09-01"), (2, "Apertura - Semi-finals", "2024-12-06"),
                   (3, "Apertura - Semi-finals", "2024-12-09"), (4, "Clausura - Quarter-finals", "2025-05-11")])
    assert pc.elegir_partido(p, {1: {"expulsion_favor"}}) == 3


def test_sin_liguilla_gana_el_peso_y_en_empate_el_mas_reciente():
    p = _partidos([(1, "Apertura", "2024-09-01"), (2, "Clausura", "2025-02-01"), (3, "Apertura", "2025-08-01")])
    tipos = {1: {"expulsion_contra"}, 2: {"gol_contra", "cambio_sistema_propio"}, 3: {"expulsion_favor"}}
    assert pc.elegir_partido(p, tipos) == 3          # expulsión (3) en 1 y 3: el más reciente
    tipos[1] = {"expulsion_contra", "gol_contra"}    # 3 + 2 = 5 supera a los demás
    assert pc.elegir_partido(p, tipos) == 1


def test_sin_partidos_avisa():
    with pytest.raises(ValueError):
        pc.elegir_partido(_partidos([]), {})


def test_momento_por_prioridad_y_primero_por_orden():
    q = pd.DataFrame({"tipo": ["gol_favor", "gol_contra", "cambio_sistema_propio", "gol_contra"], "indice": [10, 50, 30, 20]})
    assert pc.elegir_momento(q)["indice"] == 20      # gol en contra antes que cambio de sistema; el primero de ellos
    assert pc.elegir_momento(q[q["tipo"] == "gol_favor"])["indice"] == 10
    assert pc.elegir_momento(q.iloc[0:0]) is None
