"""Partidos válidos, torneo, partidos de un equipo y relevos de entrenador.

REF1: contexto/framework.md, secciones "Partidos válidos", "Contexto del partido" y
"Validación, causalidad y decisión" (definición de relevo).
"""

from __future__ import annotations

import pandas as pd

ESTADO_COMPLETO = "Complete"
DISPONIBLE = "available"
APERTURA, CLAUSURA = "Apertura", "Clausura"
MES_INICIO_APERTURA = 7  # el Apertura se juega de julio a diciembre


def validos(partidos: pd.DataFrame, con_360: bool = False) -> pd.DataFrame:
    """Partidos con eventos completos y descargables; con_360 exige además el 360 disponible."""
    filtro = (partidos["collection_status"] == ESTADO_COMPLETO) & (partidos["match_status"] == DISPONIBLE)
    if con_360:
        filtro &= partidos["match_status_360"] == DISPONIBLE
    return partidos[filtro]


def torneo(etapa: str | None, fecha: pd.Timestamp) -> str:
    """Apertura o Clausura: del prefijo de competition_stage.name o, si no lo trae, de la fecha."""
    texto = (etapa or "").strip()
    for nombre in (APERTURA, CLAUSURA):
        if texto.startswith(nombre):
            return nombre
    # HACK1: fases como "Quarter-finals" o "Regular Season" no traen prefijo; se usa la fecha.
    return APERTURA if pd.Timestamp(fecha).month >= MES_INICIO_APERTURA else CLAUSURA


def con_torneo(partidos: pd.DataFrame) -> pd.DataFrame:
    """Agrega la columna torneo (Apertura/Clausura) y una etiqueta corta, p. ej. AP23 o CL26."""
    tabla = partidos.copy()
    tabla["torneo"] = [torneo(e, f) for e, f in zip(tabla["etapa"], tabla["fecha"])]
    # Cada torneo se juega dentro de un año natural (AP: jul–dic, CL: ene–may), así que la fecha da el año.
    anio = (tabla["fecha"].dt.year % 100).map("{:02d}".format)
    tabla["torneo_corto"] = tabla["torneo"].map({APERTURA: "AP", CLAUSURA: "CL"}) + anio
    return tabla


def del_equipo(partidos: pd.DataFrame, team_id: int) -> pd.DataFrame:
    """Partidos de un equipo vistos desde su lado: localía, rival, entrenador y marcador."""
    local = partidos["local_id"] == team_id
    visita = partidos["visitante_id"] == team_id
    tabla = partidos[local | visita].copy()
    es_local = tabla["local_id"] == team_id
    tabla["lado"] = es_local.map({True: "local", False: "visitante"})
    tabla["localia"] = tabla["lado"].where(~tabla["cancha_neutral"], "neutral")
    tabla["rival_id"] = tabla["visitante_id"].where(es_local, tabla["local_id"])
    tabla["rival"] = tabla["visitante"].where(es_local, tabla["local"])
    tabla["entrenador_id"] = tabla["dt_local_id"].where(es_local, tabla["dt_visitante_id"])
    tabla["entrenador"] = tabla["dt_local"].where(es_local, tabla["dt_visitante"])
    tabla["goles_favor"] = tabla["goles_local"].where(es_local, tabla["goles_visitante"])
    tabla["goles_contra"] = tabla["goles_visitante"].where(es_local, tabla["goles_local"])
    return tabla.sort_values("fecha")


def entrenador_por_partido(partidos: pd.DataFrame) -> pd.DataFrame:
    """Una fila por equipo y partido con su entrenador (las dos caras de cada partido)."""
    columnas = ["match_id", "fecha", "equipo_id", "entrenador_id", "entrenador"]
    local = partidos.rename(columns={"local_id": "equipo_id", "dt_local_id": "entrenador_id", "dt_local": "entrenador"})
    visita = partidos.rename(
        columns={"visitante_id": "equipo_id", "dt_visitante_id": "entrenador_id", "dt_visitante": "entrenador"}
    )
    return pd.concat([local[columnas], visita[columnas]], ignore_index=True).sort_values(["equipo_id", "fecha"])


def relevos(partidos: pd.DataFrame, min_partidos: int) -> pd.DataFrame:
    """Relevos de entrenador por equipo: cambio de entrenador entre etapas de min_partidos o más.

    Un interinato de menos de min_partidos partidos no cuenta como relevo: sus partidos se
    descartan y el relevo se registra entre el entrenador anterior y el siguiente.
    """
    filas = []
    for equipo_id, grupo in entrenador_por_partido(partidos).groupby("equipo_id"):
        grupo = grupo.dropna(subset=["entrenador_id"]).sort_values("fecha")
        bloque = (grupo["entrenador_id"] != grupo["entrenador_id"].shift()).cumsum()
        etapas = grupo.groupby(bloque).agg(
            entrenador_id=("entrenador_id", "first"), entrenador=("entrenador", "first"),
            desde=("fecha", "min"), hasta=("fecha", "max"), partidos=("match_id", "size"),
        )
        etapas = etapas[etapas["partidos"] >= min_partidos].reset_index(drop=True)
        # Dos etapas seguidas del mismo entrenador (separadas por un interinato) son una sola.
        etapas = etapas[etapas["entrenador_id"] != etapas["entrenador_id"].shift()].reset_index(drop=True)
        for i in range(1, len(etapas)):
            antes, despues = etapas.iloc[i - 1], etapas.iloc[i]
            filas.append({
                "equipo_id": equipo_id,
                "entrenador_saliente_id": antes["entrenador_id"], "entrenador_saliente": antes["entrenador"],
                "entrenador_entrante_id": despues["entrenador_id"], "entrenador_entrante": despues["entrenador"],
                "ultimo_partido_saliente": antes["hasta"], "primer_partido_entrante": despues["desde"],
            })
    return pd.DataFrame(filas)
