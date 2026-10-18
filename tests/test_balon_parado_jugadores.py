"""Pruebas de balón parado (envíos, zonas, por partido), uso de jugadores y la comparación por partido del criterio v2."""

import numpy as np
import pandas as pd
import pytest

from ojo.lentes import balon_parado, hallazgo, jugadores


def _ev(indice: int, posesion: int, equipo: int, pos_equipo: int, tipo: str, patron: str, x: float, y: float = 40,
        xg: float | None = None, resultado: str | None = None) -> dict:
    return {"match_id": 1, "periodo": 1, "indice": indice, "posesion": posesion, "equipo_id": equipo,
            "posesion_equipo_id": pos_equipo, "tipo": tipo, "patron": patron, "x": x, "y": y,
            "tiro_xg": xg, "tiro_resultado": resultado}


def test_envios_y_tiros_de_balon_parado() -> None:
    eventos = pd.DataFrame([
        _ev(1, 1, 1, 1, "Pass", "From Corner", 120, 0),            # córner del equipo 1
        _ev(2, 1, 1, 1, "Shot", "From Corner", 115, 40, .3, "Goal"),
        _ev(3, 2, 2, 2, "Pass", "From Throw In", 30, 0),           # lateral lejos: no amenaza
        _ev(4, 3, 2, 2, "Pass", "From Throw In", 95, 80),          # lateral en zona de peligro
        _ev(5, 3, 2, 2, "Shot", "From Throw In", 105, 20, .05),
        _ev(6, 4, 1, 1, "Pass", "Regular Play", 50),               # juego abierto
    ])
    env = balon_parado.envios(eventos)
    assert sorted(env["tipo"].tolist()) == ["Córner", "Lateral"]
    tir = balon_parado.tiros(eventos, env)
    assert tir["zona"].tolist() == ["Área chica", "Área: costados"]
    pp = balon_parado.por_partido(env, tir, equipo_id=1, partidos=pd.Series([1])).iloc[0]
    assert pp["envios_favor"] == 1 and pp["goles_favor"] == 1 and pp["xg_contra"] == pytest.approx(.05)
    assert pp["xg_por_envio_favor"] == pytest.approx(.3)


def test_zonas_de_remate() -> None:
    x = pd.Series([116, 105, 105, 90])
    y = pd.Series([40, 40, 20, 40])
    assert balon_parado.zona(x, y).tolist() == balon_parado.ZONAS


def test_sustituciones_por_partido() -> None:
    eventos = pd.DataFrame({
        "match_id": [1, 1, 1, 1], "periodo": [2, 2, 2, 2], "minuto": [55, 70, 80, 85], "tipo": "Substitution",
        "equipo_id": [1, 1, 1, 2], "sustitucion_resultado": ["Tactical", "Injury", "Tactical", "Tactical"],
        "posicion_id": [23, 3, 14, 23]})
    subs = jugadores.sustituciones(eventos, 1)
    assert subs["linea"].tolist() == ["Ataque", "Defensa", "Medio"]
    pp = jugadores.por_partido(subs, pd.Series([1, 2]), minuto_temprano=60).set_index("match_id")
    assert pp.loc[1, "cambios"] == 3 and pp.loc[1, "cambios_lesion"] == 1
    assert pp.loc[1, "primer_cambio_tactico"] == 55 and pp.loc[1, "tacticos_tempranos"] == 1
    assert pp.loc[2, "cambios"] == 0 and np.isnan(pp.loc[2, "primer_cambio_tactico"])


def test_comparar_por_partido_detecta_una_diferencia_clara() -> None:
    rng = np.random.default_rng(0)
    filas = [{"match_id": i, "grupo": "N" if i < 60 else "P", "torneo_corto": f"T{i % 5}",
              "m": (1.0 if i < 60 else 0.0) + rng.normal(scale=.3)} for i in range(120)]
    cfg = {"tamano_min_de": .5, "min_torneos_misma_direccion": 4, "partidos_aviso": 10, "fdr_q": .1}
    r = hallazgo.comparar(pd.DataFrame(filas), ["m"], "N", "P", np.random.default_rng(1), cfg).iloc[0]
    assert r["pasa"] and r["diferencia"] == pytest.approx(1.0, abs=.15)
