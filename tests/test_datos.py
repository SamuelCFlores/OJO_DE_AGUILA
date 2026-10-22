"""Pruebas de ojo.datos con JSON sintético (hecho a mano, sin datos reales)."""

import gzip
import json

import pandas as pd
import pytest

from ojo.datos import almacen, crudo, tablas

PARTIDO_REAL = {  # forma real de Matches v6: ids con prefijo y entrenador en managers (lista)
    "match_id": 10, "match_date": "2025-01-12", "kick_off": "19:00:00.000",
    "competition": {"competition_id": 73, "competition_name": "Liga X"},
    "season": {"season_id": 318, "season_name": "2025/2026"},
    "competition_stage": {"id": 1, "name": "Clausura"}, "match_week": 1,
    "home_team": {"home_team_id": 1, "home_team_name": "Local", "managers": [{"id": 100, "name": "DT Local"}]},
    "away_team": {"away_team_id": 2, "away_team_name": "Visita", "managers": [{"id": 200, "name": "DT Visita"}]},
    "home_score": 2, "away_score": 1, "neutral_ground": False,
    "collection_status": "Complete", "match_status": "available", "match_status_360": "available",
}
PARTIDO_DOC = {  # forma documentada: {id, name} y home_team_manager como objeto
    "match_id": 11, "match_date": "2025-08-01",
    "competition": {"id": 73}, "season": {"id": 318},
    "home_team": {"id": 3, "name": "Otro"}, "away_team": {"id": 1, "name": "Local"},
    "home_team_manager": {"id": 300, "name": "DT Otro"}, "away_team_manager": {"id": 100, "name": "DT Local"},
}
EVENTOS = [
    {"id": "a", "index": 1, "period": 1, "minute": 0, "second": 1, "type": {"name": "Pass"},
     "team": {"id": 1, "name": "Local"}, "play_pattern": {"name": "Regular Play"}, "location": [60, 40],
     "pass": {"end_location": [70, 30], "pass_cluster_id": 5, "pass_cluster_label": "Etiqueta 5",
              "pass_success_probability": 0.9},
     "control_degree": 1.0, "is_transition": False},
    {"id": "b", "index": 2, "period": 1, "minute": 10, "second": 0, "type": {"name": "Shot"},
     "team": {"id": 1}, "play_pattern": {"name": "From Corner"}, "location": [110, 40],
     "shot": {"statsbomb_xg": 0.3, "outcome": {"name": "Goal"}, "end_location": [120, 40, 1]}},
    {"id": "c", "index": 3, "period": 1, "minute": 12, "second": 0, "type": {"name": "Ball Recovery"},
     "team": {"id": 2}, "location": [30, 20], "ball_recovery": {"recovery_failure": True}},
    {"id": "d", "index": 4, "period": 2, "minute": 60, "second": 0, "type": {"name": "Foul Committed"},
     "team": {"id": 2}, "foul_committed": {"card": {"id": 5, "name": "Red Card"}}},
    {"id": "e", "index": 5, "period": 2, "minute": 70, "second": 0, "type": {"name": "Bad Behaviour"},
     "team": {"id": 1}, "bad_behaviour": {"card": {"id": 6, "name": "Second Yellow"}}},
]
FRAMES = [{"event_uuid": "a", "visible_area": [0, 0, 120, 0, 120, 80, 0, 80, 0, 0],
           "freeze_frame": [{"location": [60, 40], "teammate": True, "actor": True, "keeper": False},
                            {"location": [80, 40], "teammate": False, "actor": False, "keeper": False}]}]


def test_partidos_lee_la_forma_real_y_la_documentada() -> None:
    tabla = tablas.partidos([PARTIDO_REAL, PARTIDO_DOC])
    assert list(tabla["local_id"]) == [1, 3]
    assert list(tabla["dt_visitante_id"]) == [200, 100]
    assert list(tabla["season_id"]) == [318, 318]
    assert tabla.loc[0, "etapa"] == "Clausura"
    assert pd.api.types.is_datetime64_any_dtype(tabla["fecha"])


def test_eventos_aplana_los_campos_del_framework() -> None:
    ev = tablas.eventos(EVENTOS, match_id=10)
    pase, tiro, recuperacion = ev.iloc[0], ev.iloc[1], ev.iloc[2]
    assert (pase["x"], pase["fin_x"], pase["pase_cluster_id"], pase["pase_cluster"]) == (60, 70, 5, "Etiqueta 5")
    assert pd.isna(pase["pase_resultado"])  # pase completo: sin outcome
    assert (tiro["tiro_xg"], tiro["tiro_resultado"], tiro["fin_x"]) == (0.3, "Goal", 120)
    assert bool(recuperacion["recuperacion_fallida"]) is True
    assert set(ev["match_id"]) == {10}
    assert pd.isna(ev.loc[2, "tarjeta"])
    assert list(ev["tarjeta"].iloc[3:]) == ["Red Card", "Second Yellow"]  # de Foul Committed y de Bad Behaviour


def test_frames_360_separa_area_y_jugadores() -> None:
    frames, jugadores = tablas.frames_360(FRAMES, match_id=10)
    assert frames.loc[0, "n_visibles"] == 2 and len(frames.loc[0, "area_visible"]) == 10
    assert list(jugadores["companero"]) == [True, False]
    assert jugadores["actor"].sum() == 1


def _guardar(dir_raw, api, version, clave, contenido) -> None:
    ruta = dir_raw / api / version / f"{clave}.json.gz"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(ruta, "wt", encoding="utf-8") as f:
        json.dump(contenido, f)


def test_crudo_falla_con_pista_si_no_esta_en_cache(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="02_descarga"):
        crudo.leer("events", dir_raw=tmp_path, match_id=1)


def test_almacen_procesa_y_carga_un_partido(tmp_path) -> None:
    raw, procesado = tmp_path / "raw", tmp_path / "processed"
    _guardar(raw, "events", "v11", 10, EVENTOS)
    _guardar(raw, "frames_360", "v2", 10, FRAMES)
    escritas = almacen.procesar_partido(10, dir_raw=raw, dir_procesado=procesado)
    assert escritas == ["eventos", "frames", "frames_jugadores"]
    assert almacen.procesar_partido(10, dir_raw=raw, dir_procesado=procesado) == []  # incremental
    ev = almacen.cargar("eventos", match_ids=[10], columnas=["id", "tipo"], dir_procesado=procesado)
    assert list(ev["id"]) == ["a", "b", "c", "d", "e"]
    n = almacen.consultar("SELECT count(*) AS n FROM frames_jugadores", dir_procesado=procesado)["n"][0]
    assert n == 2


def test_almacen_rehace_solo_las_tablas_pedidas(tmp_path) -> None:
    raw, procesado = tmp_path / "raw", tmp_path / "processed"
    _guardar(raw, "events", "v11", 10, EVENTOS)
    _guardar(raw, "frames_360", "v2", 10, FRAMES)
    almacen.procesar_partido(10, dir_raw=raw, dir_procesado=procesado)
    assert almacen.procesar_partido(10, forzar=["eventos"], dir_raw=raw, dir_procesado=procesado) == ["eventos"]
    assert almacen.procesar_partido(10, forzar=True, dir_raw=raw, dir_procesado=procesado) == [
        "eventos", "frames", "frames_jugadores"]
