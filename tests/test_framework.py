"""Pruebas del framework (tramos, marcador, orientación, torneo, partidos y relevos) con datos sintéticos."""

import pandas as pd

from ojo.framework import contexto, juego, partidos


def test_tramos_de_15_minutos_y_anadido_propio() -> None:
    periodo = pd.Series([1, 1, 1, 1, 2, 2, 2])
    minuto = pd.Series([0, 14, 44, 47, 45, 89, 93])
    assert list(contexto.tramo(periodo, minuto, 15)) == [
        "1T 0-15", "1T 0-15", "1T 30-45", "1T 45+", "2T 45-60", "2T 75-90", "2T 90+",
    ]


def _eventos_con_goles() -> pd.DataFrame:
    # Local (1) anota en el evento 2; la visita (2) gana con un autogol a favor en el 4.
    return pd.DataFrame({
        "indice": [1, 2, 3, 4, 5, 6],
        "periodo": [1, 1, 1, 2, 2, 5],
        "tipo": ["Pass", "Shot", "Pass", "Own Goal For", "Pass", "Shot"],
        "tiro_resultado": [None, "Goal", None, None, None, "Goal"],
        "equipo_id": [1, 1, 2, 2, 1, 2],
    })


def test_marcador_cuenta_antes_de_cada_evento_y_excluye_penales() -> None:
    m = contexto.marcador(_eventos_con_goles(), equipo_id=1)
    assert list(m["goles_favor"]) == [0, 0, 1, 1, 1, 1]
    assert list(m["goles_contra"]) == [0, 0, 0, 0, 1, 1]  # el tiro de la tanda (periodo 5) no cuenta
    assert list(m["estado"]) == ["empata", "empata", "gana", "gana", "empata", "empata"]


def test_orientar_refleja_solo_las_acciones_del_rival() -> None:
    ev = pd.DataFrame({"equipo_id": [1, 2], "x": [100.0, 100.0], "y": [10.0, 10.0],
                       "fin_x": [110.0, 110.0], "fin_y": [20.0, 20.0]})
    o = contexto.orientar(ev, equipo_id=1)
    assert (o.loc[0, "x"], o.loc[0, "y"]) == (100, 10)
    assert (o.loc[1, "x"], o.loc[1, "y"], o.loc[1, "fin_x"]) == (20, 70, 10)


def test_torneo_por_prefijo_o_por_fecha() -> None:
    assert partidos.torneo("Apertura - Quarter-finals", pd.Timestamp("2023-11-20")) == "Apertura"
    assert partidos.torneo("Clausura", pd.Timestamp("2025-02-01")) == "Clausura"
    assert partidos.torneo("Quarter-finals", pd.Timestamp("2024-05-10")) == "Clausura"
    assert partidos.torneo("Regular Season", pd.Timestamp("2026-08-10")) == "Apertura"


def _tabla_partidos(filas: list[tuple]) -> pd.DataFrame:
    """filas: (match_id, fecha, local, visita, dt_local, dt_visita)."""
    return pd.DataFrame([{
        "match_id": m, "fecha": pd.Timestamp(f), "local_id": l, "local": f"E{l}", "visitante_id": v,
        "visitante": f"E{v}", "dt_local_id": dl, "dt_local": f"DT{dl}", "dt_visitante_id": dv,
        "dt_visitante": f"DT{dv}", "goles_local": 1, "goles_visitante": 0, "cancha_neutral": False,
        "etapa": "Apertura", "collection_status": "Complete", "match_status": "available",
        "match_status_360": "available" if m % 2 else "scheduled",
    } for m, f, l, v, dl, dv in filas])


def test_validos_y_del_equipo() -> None:
    tabla = _tabla_partidos([(1, "2024-08-01", 9, 5, 90, 50), (2, "2024-08-08", 5, 9, 50, 90)])
    assert len(partidos.validos(tabla)) == 2
    assert list(partidos.validos(tabla, con_360=True)["match_id"]) == [1]
    nueve = partidos.del_equipo(tabla, 9)
    assert list(nueve["lado"]) == ["local", "visitante"]
    assert list(nueve["entrenador_id"]) == [90, 90]
    assert list(nueve["goles_favor"]) == [1, 0]
    assert list(partidos.con_torneo(tabla)["torneo_corto"]) == ["AP24", "AP24"]


def test_relevos_ignora_interinatos_cortos() -> None:
    # Equipo 9: DT 90 (4 partidos) → interino 91 (1 partido) → DT 92 (3 partidos). Rival fijo.
    filas = [(i, f"2024-0{1 + i // 4}-{10 + i % 4:02d}", 9, 5, dt, 50)
             for i, dt in enumerate([90, 90, 90, 90, 91, 92, 92, 92])]
    r = partidos.relevos(_tabla_partidos(filas), min_partidos=3)
    del_9 = r[r["equipo_id"] == 9]
    assert len(del_9) == 1
    assert (del_9.iloc[0]["entrenador_saliente_id"], del_9.iloc[0]["entrenador_entrante_id"]) == (90, 92)
    assert r[r["equipo_id"] == 5].empty


def test_juego_abierto_y_recuperaciones() -> None:
    ev = pd.DataFrame({
        "patron": ["Regular Play", "From Corner", "From Counter"],
        "tipo": ["Ball Recovery", "Interception", "Interception"],
        "recuperacion_fallida": [False, False, False],
        "intercepcion_resultado": [None, "Won", "Lost In Play"],
    })
    assert list(juego.es_juego_abierto(ev)) == [True, False, True]
    assert list(juego.es_recuperacion(ev)) == [True, True, False]
