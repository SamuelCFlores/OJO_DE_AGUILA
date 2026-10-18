"""Pruebas de PPDA y altura de recuperación (ojo.lentes.defensa)."""

import pandas as pd
import pytest

from ojo.lentes import defensa


def _evento(equipo: int, tipo: str, x: float, minuto: int = 10, **extra) -> dict:
    base = {"match_id": 1, "periodo": 1, "minuto": minuto, "equipo_id": equipo, "tipo": tipo, "x": x,
            "patron": "Regular Play", "pase_tipo": None, "duelo_tipo": None, "recuperacion_fallida": False, "intercepcion_resultado": None}
    base.update(extra)
    return base


def test_ppda_usa_la_zona_de_cada_orientacion() -> None:
    eventos = pd.DataFrame([
        # El rival (2) pasa en su 60 % defensivo (x < 72 en su orientación): 4 pases; uno fuera de la zona
        *[_evento(2, "Pass", 30) for _ in range(4)], _evento(2, "Pass", 90),
        _evento(2, "Pass", 10, pase_tipo="Goal Kick"),  # un saque de meta no es un pase "permitido"
        # El equipo 1 defiende en el 60 % del rival (x ≥ 48 en su orientación): entrada + falta; una intercepción atrás no cuenta
        _evento(1, "Duel", 70, duelo_tipo="Tackle"), _evento(1, "Foul Committed", 60), _evento(1, "Interception", 20),
        _evento(1, "Duel", 70, duelo_tipo="Aerial Lost"),  # un duelo aéreo no es acción defensiva del PPDA
    ])
    m = defensa.metricas(defensa.piezas_por_minuto(eventos), ["match_id"]).set_index("equipo_id")
    assert m.loc[1, "ppda"] == pytest.approx(4 / 2)


def test_altura_de_recuperacion_solo_juego_abierto_y_exitosas() -> None:
    eventos = pd.DataFrame([
        _evento(1, "Ball Recovery", 40), _evento(1, "Interception", 80, intercepcion_resultado="Won"),
        _evento(1, "Ball Recovery", 100, recuperacion_fallida=True),         # fallida: no cuenta
        _evento(1, "Ball Recovery", 110, patron="From Corner"),              # balón parado: no cuenta
        _evento(2, "Pass", 50),
    ])
    m = defensa.metricas(defensa.piezas_por_minuto(eventos), ["match_id"]).set_index("equipo_id")
    assert m.loc[1, "altura_recuperacion"] == pytest.approx(60)
    assert m.loc[1, "recuperaciones"] == 2


def test_tramos_dentro_de_cada_periodo() -> None:
    piezas = pd.DataFrame({"match_id": 1, "periodo": [1, 1, 1, 2], "minuto": [0, 14, 47, 45], "equipo_id": 1,
                           "pases_zona_propia": 0.0, "acciones_def_zona": 0.0, "recuperaciones_n": 0.0,
                           "recuperaciones_x_suma": 0.0})
    t = defensa.con_tramo(piezas, 15)
    assert t["tramo"].tolist() == [0, 0, 3, 0]  # el añadido del primer tiempo (47') queda en su propio tramo
