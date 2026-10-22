"""Pruebas de las lentes del panel por minuto: forma del bloque, red por posición y métricas de ventana."""

import pandas as pd
import pytest

from ojo.lentes import forma, minuto, redes


def test_forma_refleja_al_otro_equipo_y_quita_porteros() -> None:
    eventos = pd.DataFrame({"id": ["e1", "e2"], "match_id": [1, 1], "equipo_id": [1, 2], "posesion_equipo_id": [1, 1]})
    puntos = [(60, 40, True, False), (70, 20, True, False), (70, 60, True, False), (80, 40, True, False),
              (10, 40, True, True),  # portero: no cuenta
              (100, 40, False, False), (90, 30, False, False), (90, 50, False, False), (95, 40, False, False)]
    jugadores = pd.DataFrame([{"match_id": 1, "event_uuid": "e1", "x": x, "y": y, "companero": c, "actor": False,
                               "portero": p} for x, y, c, p in puntos])
    f = forma.por_frame(jugadores, eventos, min_jugadores=4).set_index("equipo_id")
    assert (f.loc[1, "altura"], f.loc[1, "ancho"], f.loc[1, "largo"]) == (70, 40, 20)
    assert f.loc[1, "compactacion"] == pytest.approx(100)  # rombo de 400 yd² entre 4
    assert f.loc[2, "altura"] == pytest.approx(26.25)  # 120 − x: el rival ataca hacia x = 120 en su perspectiva
    assert f.loc[2, "compactacion"] == pytest.approx(25)
    assert bool(f.loc[1, "con_balon"]) and not bool(f.loc[2, "con_balon"])


def test_centralizacion_de_la_red_por_posicion() -> None:
    # Jugadores 10 (posición 1), 20 (5) y 30 (10): 10→20, 20→30 dos veces y 30→20.
    filas = [(10, 1, 20), (20, 5, 30), (20, 5, 30), (30, 10, 20)]
    eventos = pd.DataFrame([{"match_id": 1, "periodo": 1, "minuto": 3, "equipo_id": 1, "tipo": "Pass",
                             "pase_resultado": None, "jugador_id": j, "posicion_id": p, "pase_receptor_id": r}
                            for j, p, r in filas])
    aristas = redes.aristas_por_minuto(eventos)
    assert aristas["pases"].sum() == 4
    c = redes.centralizacion(aristas, por=["match_id"])
    # grados 1, 4 y 3 de 8 → s_max = 0.5 → (3·0.5 − 1) / 2
    assert c.loc[0, "centralizacion"] == pytest.approx(0.25)


def _eventos_panel() -> pd.DataFrame:
    base = {"match_id": 1, "periodo": 1, "contrapresion": False, "tiro_xg": None, "obv_total_net": 0.0,
            "pase_resultado": None, "es_transicion": None, "patron": "Regular Play", "tiro_resultado": None}
    filas = [
        {"id": "a", "indice": 1, "minuto": 1, "tipo": "Pass", "equipo_id": 1, "x": 90, "posesion": 1, "posesion_equipo_id": 1},
        {"id": "b", "indice": 2, "minuto": 2, "tipo": "Pass", "equipo_id": 2, "x": 85, "posesion": 2,
         "posesion_equipo_id": 2, "patron": "From Counter"},
        {"id": "c", "indice": 3, "minuto": 3, "tipo": "Shot", "equipo_id": 2, "x": 100, "posesion": 2,
         "posesion_equipo_id": 2, "tiro_xg": 0.2, "es_transicion": True, "patron": "From Counter"},
        {"id": "d", "indice": 4, "minuto": 3, "tipo": "Pressure", "equipo_id": 1, "x": 70, "posesion": 2,
         "posesion_equipo_id": 2, "patron": "From Counter"},
    ]
    return pd.DataFrame([base | f for f in filas])


def test_panel_y_metricas_de_una_ventana_a_dos_bandas() -> None:
    panel = minuto.panel_partido(_eventos_panel(), equipo_id=1)
    assert set(panel["lado"]) == {"propio", "rival"}
    ventanas = pd.DataFrame({"ventana_id": ["v"], "match_id": [1], "periodo": [1], "desde": [1], "hasta": [4]})
    m = minuto.metricas(minuto.sumar(panel, minuto.expandir(ventanas), "ventana_id"), "ventana_id").set_index("lado")
    assert m.loc["propio", "n_min"] == 4
    assert m.loc["propio", "field_tilt"] == pytest.approx(0.5)
    assert m.loc["propio", "tiros_transicion_contra"] == pytest.approx(0.25)  # el tiro del rival es riesgo propio
    assert m.loc["propio", "contragolpes_contra"] == pytest.approx(0.25)  # una posesión From Counter del rival
    assert m.loc["propio", "presiones_campo_rival"] == pytest.approx(0.25)
    assert m.loc["rival", "xg"] == pytest.approx(0.05)
    assert pd.isna(m.loc["propio", "control_campo_rival"])  # sin Voronoi no hay control


def test_expandir_da_un_minuto_por_fila() -> None:
    v = pd.DataFrame({"ventana_id": ["a", "b"], "match_id": [1, 1], "periodo": [1, 2], "desde": [10, 50],
                      "hasta": [12, 50]})
    e = minuto.expandir(v)
    assert list(e["minuto"]) == [10, 11, 12, 50]
    assert list(e["ventana_id"]) == ["a", "a", "a", "b"]
