"""Pruebas de las situaciones por minuto (ojo.lentes.situaciones)."""

import pandas as pd
import pytest

from ojo.lentes import situaciones


def test_estado_por_minuto_con_goles_y_expulsiones() -> None:
    ev = pd.DataFrame({
        "match_id": 1, "indice": range(6), "periodo": [1, 1, 1, 2, 2, 2], "minuto": [5, 10, 20, 50, 60, 70],
        "equipo_id": [1, 1, 2, 2, 1, 1], "tipo": ["Pass", "Shot", "Bad Behaviour", "Pass", "Shot", "Pass"],
        "tiro_resultado": [None, "Goal", None, None, "Goal", None], "tarjeta": [None, None, "Red Card", None, None, None],
    })
    est = situaciones.por_minuto(ev, 1).set_index("minuto")
    assert est.loc[10, "dif_goles"] == 0 and est.loc[20, "dif_goles"] == 1   # el gol cuenta desde el evento siguiente
    assert est.loc[20, "dif_jugadores"] == 0 and est.loc[50, "dif_jugadores"] == 1  # la roja también
    assert est.loc[70, "dif_goles"] == 2


def test_estado_se_reinicia_en_cada_partido() -> None:
    ev = pd.DataFrame({"match_id": [1, 1, 2, 2], "indice": [0, 1, 0, 1], "periodo": 1, "minuto": [5, 10, 5, 10],
                       "equipo_id": 1, "tipo": ["Shot", "Pass", "Pass", "Pass"], "tiro_resultado": ["Goal", None, None, None],
                       "tarjeta": None})
    est = situaciones.por_minuto(ev, 1).set_index(["match_id", "minuto"])
    assert est.loc[(1, 10), "dif_goles"] == 1 and est.loc[(2, 5), "dif_goles"] == 0 and est.loc[(2, 10), "dif_goles"] == 0


def test_asignar_prioriza_jugadores_y_separa_el_empate_por_tiempo() -> None:
    est = pd.DataFrame({"dif_goles": [0, 0, 1, 3, -1, -2, 0, 2], "dif_jugadores": [0, 0, 0, 0, 0, 0, 1, -1],
                        "periodo": [1, 2, 2, 2, 1, 2, 2, 2]})
    assert situaciones.asignar(est).tolist() == ["empata_1t", "empata_2t", "gana_1", "gana_2", "pierde_1", "pierde_2",
                                                 "uno_mas", "uno_menos"]


def test_resumir_usa_sumas_por_minuto() -> None:
    t = pd.DataFrame({"match_id": [1, 1, 2], "situacion": "gana_1", "xg_favor": [.1, .2, 0.0], "xg_contra": [0.0, .1, 0.0],
                      "tercio_favor": [3, 1, 0], "tercio_contra": [1, 1, 2], "pases_rival_zona": [10, 0, 6],
                      "acciones_def": [1, 1, 2], "rec_n": [1, 0, 1], "rec_x": [60, 0, 40],
                      "indice_favor": [70, 60, 50], "indice_rival": [30, 40, 50]})
    r = situaciones.resumir(t, ["situacion"]).iloc[0]
    assert r["minutos"] == 3 and r["partidos"] == 2
    assert r["xg_dif_90"] == pytest.approx(90 * (.3 - .1) / 3)
    assert r["field_tilt"] == pytest.approx(4 / 8) and r["ppda"] == pytest.approx(16 / 4)
    assert r["altura_recuperacion"] == pytest.approx(50) and r["indice"] == pytest.approx(60)
