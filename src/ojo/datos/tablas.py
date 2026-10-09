"""Conversión del JSON de StatsBomb a tablas planas (pandas).

Funciones puras: reciben el JSON ya leído y devuelven un DataFrame, así se prueban con
fixtures sintéticas. Los nombres de columna están en español y son la interfaz del resto
del paquete; los campos de origen se documentan en contexto/api/.

OBS1: Matches trae los ids anidados con prefijo (home_team_id, season_id, ...) y no {id, name}
como dice la documentación; _id/_nombre aceptan ambas formas (contexto/api/matches.md).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _id(obj: dict | None, prefijo: str) -> Any:
    """Id de un objeto anidado de StatsBomb, con o sin prefijo (home_team_id o id)."""
    if not obj:
        return None
    return obj.get(f"{prefijo}_id", obj.get("id"))


def _nombre(obj: dict | None, prefijo: str) -> Any:
    """Nombre de un objeto anidado de StatsBomb, con o sin prefijo."""
    if not obj:
        return None
    return obj.get(f"{prefijo}_name", obj.get("name"))


def _entrenador(partido: dict, lado: str) -> dict:
    """Primer entrenador de un lado: home_team.managers (real) o home_team_manager (documentado)."""
    valor = (partido.get(f"{lado}_team") or {}).get("managers")
    if valor is None:
        valor = partido.get(f"{lado}_team_manager")
    if isinstance(valor, list):
        valor = valor[0] if valor else None
    return valor or {}


def _xy(valor: Any) -> tuple[float, float]:
    """Separa una ubicación [x, y] (o [x, y, z]) en dos números; NaN si falta."""
    if isinstance(valor, list) and len(valor) >= 2:
        return float(valor[0]), float(valor[1])
    return np.nan, np.nan


def _nombre_de(obj: Any) -> Any:
    """Nombre de un objeto {id, name} o None."""
    return obj.get("name") if isinstance(obj, dict) else None


def partidos(crudo: list[dict]) -> pd.DataFrame:
    """Tabla de partidos de una respuesta de Matches: equipos, entrenadores, marcador y estado."""
    filas = []
    for p in crudo:
        local, visita = p.get("home_team") or {}, p.get("away_team") or {}
        dt_local, dt_visita = _entrenador(p, "home"), _entrenador(p, "away")
        filas.append({
            "match_id": p["match_id"],
            "fecha": p.get("match_date"),
            "hora": p.get("kick_off"),
            "competition_id": _id(p.get("competition"), "competition"),
            "season_id": _id(p.get("season"), "season"),
            "temporada": _nombre(p.get("season"), "season"),
            "etapa": _nombre_de(p.get("competition_stage")),
            "jornada": p.get("match_week"),
            "local_id": _id(local, "home_team"),
            "local": _nombre(local, "home_team"),
            "visitante_id": _id(visita, "away_team"),
            "visitante": _nombre(visita, "away_team"),
            "dt_local_id": dt_local.get("id"),
            "dt_local": dt_local.get("name"),
            "dt_visitante_id": dt_visita.get("id"),
            "dt_visitante": dt_visita.get("name"),
            "goles_local": p.get("home_score"),
            "goles_visitante": p.get("away_score"),
            "cancha_neutral": bool(p.get("neutral_ground")),
            "collection_status": p.get("collection_status"),
            "match_status": p.get("match_status"),
            "match_status_360": p.get("match_status_360"),
            "last_updated": p.get("last_updated"),
            "last_updated_360": p.get("last_updated_360"),
        })
    tabla = pd.DataFrame(filas)
    if not tabla.empty:
        tabla["fecha"] = pd.to_datetime(tabla["fecha"])
    return tabla


def eventos(crudo: list[dict], match_id: int) -> pd.DataFrame:
    """Tabla de eventos de un partido con los campos que usan el framework y las lentes."""
    filas = []
    for e in crudo:
        tipo = _nombre_de(e.get("type"))
        x, y = _xy(e.get("location"))
        detalle = e.get({"Pass": "pass", "Carry": "carry", "Shot": "shot"}.get(tipo, "")) or {}
        fin_x, fin_y = _xy(detalle.get("end_location"))
        pase = e.get("pass") or {}
        tiro = e.get("shot") or {}
        duelo = e.get("duel") or {}
        sustitucion = e.get("substitution") or {}
        filas.append({
            "match_id": match_id,
            "id": e.get("id"),
            "indice": e.get("index"),
            "periodo": e.get("period"),
            "timestamp": e.get("timestamp"),
            "minuto": e.get("minute"),
            "segundo": e.get("second"),
            "tipo": tipo,
            "equipo_id": _id(e.get("team"), "team"),
            "equipo": _nombre_de(e.get("team")),
            "posesion": e.get("possession"),
            "posesion_equipo_id": _id(e.get("possession_team"), "team"),
            "patron": _nombre_de(e.get("play_pattern")),
            "jugador_id": _id(e.get("player"), "player"),
            "posicion_id": _id(e.get("position"), "position"),
            "x": x, "y": y, "fin_x": fin_x, "fin_y": fin_y,
            "duracion": e.get("duration"),
            "bajo_presion": bool(e.get("under_pressure")),
            "contrapresion": bool(e.get("counterpress")),
            "pase_receptor_id": _id(pase.get("recipient"), "player"),
            "pase_resultado": _nombre_de(pase.get("outcome")),
            "pase_tipo": _nombre_de(pase.get("type")),
            "pase_altura": _nombre_de(pase.get("height")),
            "pase_cluster_id": pase.get("pass_cluster_id"),
            "pase_prob_exito": pase.get("pass_success_probability"),
            "tiro_xg": tiro.get("statsbomb_xg"),
            "tiro_resultado": _nombre_de(tiro.get("outcome")),
            "recuperacion_fallida": bool((e.get("ball_recovery") or {}).get("recovery_failure")),
            "intercepcion_resultado": _nombre_de((e.get("interception") or {}).get("outcome")),
            "duelo_tipo": _nombre_de(duelo.get("type")),
            "duelo_resultado": _nombre_de(duelo.get("outcome")),
            "sustitucion_resultado": _nombre_de(sustitucion.get("outcome")),
            "sustitucion_entra_id": _id(sustitucion.get("replacement"), "player"),
            "formacion": (e.get("tactics") or {}).get("formation"),
            "control_degree": e.get("control_degree"),
            "es_transicion": e.get("is_transition"),
            "posesion_controlada": e.get("is_controlled_possession"),
            "directness": e.get("possession_directness"),
            "tercio": e.get("location_bucket"),
            "obv_total_net": e.get("obv_total_net"),
            "obv_for_net": e.get("obv_for_net"),
            "obv_against_net": e.get("obv_against_net"),
        })
    return pd.DataFrame(filas)


def frames_360(crudo: list[dict], match_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Dos tablas del 360: frames (área visible) y jugadores visibles de cada frame."""
    frames, jugadores = [], []
    for f in crudo:
        uuid = f.get("event_uuid")
        visibles = f.get("freeze_frame") or []
        frames.append({
            "match_id": match_id,
            "event_uuid": uuid,
            "area_visible": [float(v) for v in (f.get("visible_area") or [])],
            "n_visibles": len(visibles),
        })
        for j in visibles:
            x, y = _xy(j.get("location"))
            jugadores.append({
                "match_id": match_id, "event_uuid": uuid, "x": x, "y": y,
                "companero": bool(j.get("teammate")), "actor": bool(j.get("actor")),
                "portero": bool(j.get("keeper")),
            })
    return pd.DataFrame(frames), pd.DataFrame(jugadores)


def formaciones(crudo: list[dict], match_id: int) -> pd.DataFrame:
    """Cronología de formaciones de cada equipo (Lineups): inicial y cambios tácticos."""
    filas = [
        {
            "match_id": match_id,
            "equipo_id": equipo.get("team_id"),
            "periodo": f.get("period"),
            "timestamp": f.get("timestamp"),
            "motivo": f.get("reason"),
            "formacion": f.get("formation"),
        }
        for equipo in crudo
        for f in equipo.get("formations") or []
    ]
    return pd.DataFrame(filas)


def estadisticas_equipo(crudo: list[dict]) -> pd.DataFrame:
    """Team Match Stats: una fila por equipo con los ~200 campos de StatsBomb tal como vienen."""
    return pd.json_normalize(crudo)
