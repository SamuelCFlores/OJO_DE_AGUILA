"""Perfil de estilo de cada equipo de la liga y rivales parecidos: la base de la ficha de 10 segundos.

REF1: contexto/framework.md, "Ficha de 10 segundos" (18 oct). Campos de Team Match Stats en contexto/api/team_match_stats.md.
NOTA1: el perfil es la media por partido de cada rasgo en la ventana elegida, estandarizada (z) frente a los equipos
de la liga en esa misma ventana. Un rasgo "distingue" a un equipo si |z| ≥ ficha.umbral_z.
NOTA2: los rivales parecidos se buscan solo con cómo juega (progresar y defender), no con lo que concede: así
"cómo le fue a Jardine contra rivales parecidos" no mezcla estilo con calidad.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.config import params

# clave: (columna de Team Match Stats, etiqueta si es alto, etiqueta si es bajo, grupo de la ficha)
RASGOS = {
    "posesion": ("team_match_possession", "Tiene el balón", "Cede el balón", "progresa"),
    "directness": ("team_match_avg_team_possession_directness", "Va directo al arco", "Elabora sus ataques", "progresa"),
    "transicion": ("team_match_transition_possession_rate", "Vive del contragolpe", "Ataca en posicional", "progresa"),
    "centros": ("team_match_box_cross_ratio", "Llega con centros", "Llega por dentro", "progresa"),
    "ppda": ("team_match_ppda", "Presiona poco", "Presiona alto", "defiende"),
    "distancia_def": ("team_match_defensive_distance", "Defiende arriba", "Defiende cerca de su área", "defiende"),
    "contragolpes_contra": ("team_match_counter_attacking_shots_conceded", "Concede contragolpes", "Cierra los contragolpes", "concede"),
    "presion_contra": ("team_match_high_press_shots_conceded", "Pierde balones si lo presionan", "Sale bien de la presión", "concede"),
    "xg_contra": ("team_match_np_xg_conceded", "Concede mucho peligro", "Concede poco peligro", "concede"),
    "bp_contra": ("team_match_sp_xg_conceded", "Vulnerable a balón parado", "Sólido a balón parado", "balon_parado"),
    "bp_favor": ("team_match_sp_xg", "Peligroso a balón parado", "Poco peligro a balón parado", "balon_parado"),
}
COLUMNAS = [c for c, *_ in RASGOS.values()]
ESTILO = [k for k, (_, _, _, g) in RASGOS.items() if g in ("progresa", "defiende")]


def perfiles(tms: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Media por partido de cada rasgo por equipo (team_id) y su z frente a los equipos de la liga."""
    medias = tms.groupby("team_id")[COLUMNAS].mean().rename(columns={c: k for k, (c, *_) in RASGOS.items()})
    z = (medias - medias.mean()) / medias.std()
    return medias, z


def destacados(z: pd.Series, grupo: str, umbral: float | None = None, n: int = 2) -> list[str]:
    """Etiquetas de los rasgos de un grupo que distinguen al equipo (|z| ≥ umbral), del más marcado al menos."""
    umbral = umbral or params()["ficha"]["umbral_z"]
    claves = [k for k, (*_, g) in RASGOS.items() if g == grupo and k in z and pd.notna(z[k]) and abs(z[k]) >= umbral]
    claves.sort(key=lambda k: -abs(z[k]))
    return [RASGOS[k][1] if z[k] > 0 else RASGOS[k][2] for k in claves[:n]]


def similares(z: pd.DataFrame, team_id: int, k: int | None = None, excluir: tuple[int, ...] = ()) -> list[int]:
    """Los k equipos más parecidos en estilo (distancia euclidiana sobre los z de ESTILO)."""
    k = k or params()["ficha"]["similares"]
    estilo = z[ESTILO].dropna()
    if team_id not in estilo.index:
        return []
    distancia = np.sqrt(((estilo - estilo.loc[team_id]) ** 2).sum(axis=1)).drop([team_id, *excluir], errors="ignore")
    return distancia.nsmallest(k).index.tolist()
