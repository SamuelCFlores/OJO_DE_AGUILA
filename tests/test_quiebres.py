"""Pruebas de los puntos de quiebre, sus ventanas y las ventanas de control (datos sintéticos)."""

import pandas as pd

from ojo.framework import quiebres

CFG = {"ventana_min": 10, "exclusion_min": 1, "min_ventana_min": 4, "tolerancia_control_min": 5, "max_controles": 20}


def _evento(indice, periodo, minuto, tipo, equipo, **extra) -> dict:
    base = {"match_id": 1, "indice": indice, "periodo": periodo, "minuto": minuto, "tipo": tipo, "equipo_id": equipo,
            "tiro_resultado": None, "tarjeta": None, "formacion": None, "sustitucion_resultado": None}
    return base | extra


def _partido() -> pd.DataFrame:
    """El equipo 1 (referencia) anota en el 20; el rival cambia de sistema, se queda con 10 y empata en el 80."""
    return pd.DataFrame([
        _evento(1, 1, 0, "Starting XI", 1, formacion=4231),
        _evento(2, 1, 0, "Starting XI", 2, formacion=442),
        _evento(3, 1, 20, "Shot", 1, tiro_resultado="Goal"),
        _evento(4, 1, 30, "Substitution", 2, sustitucion_resultado="Tactical"),
        _evento(5, 1, 31, "Tactical Shift", 2, formacion=442),  # misma formación: no es quiebre
        _evento(6, 1, 33, "Tactical Shift", 2, formacion=433),
        _evento(7, 1, 46, "Pass", 1),
        _evento(8, 2, 45, "Pass", 2),
        _evento(9, 2, 60, "Foul Committed", 2, tarjeta="Red Card"),
        _evento(10, 2, 70, "Substitution", 1, sustitucion_resultado="Injury"),
        _evento(11, 2, 80, "Own Goal For", 2),
        _evento(12, 2, 93, "Pass", 1),
        _evento(13, 5, 121, "Shot", 1, tiro_resultado="Goal"),  # tanda de penales: no cuenta
    ])


def test_detecta_cada_tipo_desde_el_equipo_de_referencia() -> None:
    q = quiebres.detectar(_partido(), equipo_id=1)
    assert list(q["tipo"]) == ["gol_favor", "sustitucion_tactica_rival", "cambio_sistema_rival",
                               "expulsion_favor", "sustitucion_lesion_propia", "gol_contra"]
    assert list(q["estado_antes"]) == ["empata", "gana", "gana", "gana", "gana", "gana"]
    assert list(q["corta"]) == [True, False, False, True, False, True]
    assert q.loc[2, "detalle"] == "442→433"
    assert q["quiebre_id"].is_unique


def test_ventanas_se_truncan_en_el_quiebre_que_corta_y_en_el_periodo() -> None:
    eventos = _partido()
    q = quiebres.detectar(eventos, 1)
    v = quiebres.ventanas(q, quiebres.limites_periodo(eventos), CFG).set_index("tipo")
    columnas = ["antes_desde", "antes_hasta", "despues_desde", "despues_hasta"]
    assert list(v.loc["gol_favor", columnas]) == [10, 18, 22, 30]
    assert list(v.loc["sustitucion_tactica_rival", columnas]) == [22, 28, 32, 40]  # tras el gol del 20 y su exclusión
    assert list(v.loc["sustitucion_lesion_propia", columnas]) == [62, 68, 72, 78]  # entre la expulsión y el gol del 80
    assert v["valida"].all()


def test_segmentos_libres_llevan_el_estado_del_marcador() -> None:
    eventos = _partido()
    q = quiebres.detectar(eventos, 1)
    s = quiebres.segmentos_libres(q, quiebres.limites_periodo(eventos), CFG)
    assert [tuple(f) for f in s[["periodo", "desde", "hasta", "estado"]].itertuples(index=False)] == [
        (1, 0, 18, "empata"), (1, 22, 46, "gana"), (2, 45, 58, "gana"), (2, 62, 78, "gana"), (2, 82, 93, "empata"),
    ]


def test_controles_vienen_de_otro_partido_con_el_mismo_estado() -> None:
    eventos = _partido()
    otro = pd.DataFrame([_evento(1, 1, 0, "Pass", 1) | {"match_id": 2}, _evento(2, 1, 47, "Pass", 3) | {"match_id": 2}])
    todos = pd.concat([eventos, otro], ignore_index=True)
    q = quiebres.ventanas(quiebres.detectar(todos, 1), quiebres.limites_periodo(todos), CFG)
    seg = quiebres.segmentos_libres(q, quiebres.limites_periodo(todos), CFG)
    c = quiebres.controles(q, seg, cfg=CFG, semilla=0)
    del_gol = c[c["quiebre_id"] == "1-3"]
    assert len(del_gol) == 1 and del_gol.iloc[0]["match_id"] == 2
    assert list(del_gol.iloc[0][["antes_desde", "antes_hasta", "despues_desde", "despues_hasta"]]) == [10, 18, 22, 30]
    # El partido 2 siempre va empatado: no sirve de control para quiebres con el equipo ganando.
    assert set(c["quiebre_id"]) == {"1-3"}
