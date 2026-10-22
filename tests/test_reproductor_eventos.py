"""Eventos que se animan en el reproductor (ojo.salidas.reproductor.eventos_por_minuto)."""

import pandas as pd

from ojo.salidas import reproductor

EQUIPO, RIVAL = 1, 2
NOMBRES = {10: "Henry Martín", 11: "Fidalgo", 20: "Gignac", 21: "Quiñones"}
EQUIPOS = {EQUIPO: "América", RIVAL: "Tigres UANL"}
COLUMNAS = ["indice", "periodo", "minuto", "segundo", "equipo_id", "jugador_id", "tipo", "tiro_resultado", "pase_tipo",
            "x", "y", "sustitucion_entra_id", "tarjeta"]


def _eventos(filas):
    return pd.DataFrame(filas, columns=COLUMNAS)


def test_clasifica_cada_tipo_y_orienta_al_rival():
    ev = _eventos([
        (1, 1, 3, 10, EQUIPO, 11, "Pass", None, "Corner", 120.0, 0.1, None, None),
        (2, 1, 3, 40, RIVAL, 20, "Pass", None, "Throw-in", 30.0, 80.0, None, None),
        (3, 1, 5, 0, RIVAL, 20, "Pass", None, "Goal Kick", 6.0, 40.0, None, None),
        (4, 1, 7, 5, EQUIPO, 11, "Foul Committed", None, None, 50.0, 20.0, None, "Yellow Card"),
        (5, 1, 8, 1, EQUIPO, 11, "Pass", None, None, 60.0, 40.0, None, None),   # pase normal: no se anima
        (6, 2, 60, 0, RIVAL, 21, "Substitution", None, None, None, None, 20, None),
    ])
    salida = reproductor.eventos_por_minuto(ev, EQUIPO, NOMBRES, EQUIPOS)
    assert [e["t"] for e in salida[(1, 3)]] == ["corner", "banda"]
    banda = salida[(1, 3)][1]
    assert banda["f"] == 0 and (banda["x"], banda["y"]) == (90.0, 0.0)   # el rival se refleja: ataca hacia la izquierda
    assert salida[(1, 5)][0]["t"] == "meta" and salida[(1, 5)][0]["x"] == 114.0
    falta = salida[(1, 7)][0]
    assert falta["t"] == "falta" and falta["f"] == 1 and falta["txt"] == "Falta de Fidalgo (amarilla)"
    assert (1, 8) not in salida
    cambio = salida[(2, 60)][0]
    assert cambio["t"] == "cambio" and cambio["x"] is None and cambio["txt"] == "Cambio de Tigres UANL: sale Quiñones, entra Gignac"


def test_goles_con_marcador_despues_del_gol_y_sin_penales():
    ev = _eventos([
        (1, 1, 20, 0, EQUIPO, 10, "Shot", "Goal", None, 110.0, 40.0, None, None),
        (2, 2, 70, 0, RIVAL, 20, "Shot", "Goal", None, 108.0, 38.0, None, None),
        (3, 2, 80, 0, EQUIPO, 10, "Shot", "Saved", None, 100.0, 40.0, None, None),   # atajado: no es gol
        (4, 5, 121, 0, EQUIPO, 10, "Shot", "Goal", None, 108.0, 40.0, None, None),  # tanda de penales: fuera
    ])
    salida = reproductor.eventos_por_minuto(ev, EQUIPO, NOMBRES, EQUIPOS)
    gol, del_rival = salida[(1, 20)][0], salida[(2, 70)][0]
    assert gol == {"t": "gol", "f": 1, "x": 110.0, "y": 40.0, "s": 0, "txt": "Gol de Henry Martín", "m": "1-0"}
    assert del_rival["f"] == 0 and del_rival["m"] == "1-1" and del_rival["x"] == 12.0
    assert (2, 80) not in salida and (5, 121) not in salida
