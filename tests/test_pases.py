"""Pruebas del largo de pase por partido (principio "sale jugando corto")."""

import pandas as pd

from ojo.lentes import pases


def _evento(match_id: int, equipo_id: int, tipo: str, patron: str, largo: float) -> dict:
    return {"match_id": match_id, "equipo_id": equipo_id, "tipo": tipo, "patron": patron,
            "x": 10.0, "y": 40.0, "fin_x": 10.0 + largo, "fin_y": 40.0}


def test_largo_medio_solo_pases_del_equipo_en_juego_abierto() -> None:
    ev = pd.DataFrame([
        _evento(1, 7, "Pass", "Regular Play", 10.0),
        _evento(1, 7, "Pass", "From Keeper", 30.0),
        _evento(1, 7, "Pass", "From Corner", 50.0),   # balón parado: no cuenta
        _evento(1, 7, "Carry", "Regular Play", 99.0),  # no es pase
        _evento(1, 8, "Pass", "Regular Play", 99.0),   # rival
        _evento(2, 7, "Pass", "From Counter", 12.0),
    ])
    largo = pases.largo_por_partido(ev, 7)
    assert largo.to_dict() == {1: 20.0, 2: 12.0}
