"""Pruebas del perfil de estilo y los rivales parecidos (ojo.lentes.rivales)."""

import numpy as np
import pandas as pd

from ojo.lentes import rivales


def _tms(team: int, posesion: float, directo: float, n: int = 3) -> list[dict]:
    base = {c: 1.0 for c in rivales.COLUMNAS}
    base.update({"team_match_possession": posesion, "team_match_avg_team_possession_directness": directo})
    return [{"match_id": team * 100 + i, "team_id": team, **base} for i in range(n)]


def test_perfil_z_y_rasgos_destacados() -> None:
    tms = pd.DataFrame(_tms(1, .65, .2) + _tms(2, .50, .4) + _tms(3, .45, .45) + _tms(4, .40, .5))
    medias, z = rivales.perfiles(tms)
    assert medias.loc[1, "posesion"] == .65
    assert z.loc[1, "posesion"] > 1 and z.loc[1, "directness"] < -1
    etiquetas = rivales.destacados(z.loc[1], "progresa", umbral=.5)
    assert etiquetas == ["Tiene el balón", "Elabora"] or etiquetas == ["Elabora", "Tiene el balón"]


def test_similares_por_estilo() -> None:
    z = pd.DataFrame(0.0, index=[1, 2, 3, 4], columns=rivales.ESTILO)
    z.loc[1, "posesion"], z.loc[2, "posesion"], z.loc[3, "posesion"], z.loc[4, "posesion"] = 2.0, 1.8, -1.0, 0.0
    assert rivales.similares(z, 1, k=2) == [2, 4]
    assert rivales.similares(z, 1, k=1, excluir=(2,)) == [4]
    assert rivales.similares(z, 99, k=1) == []
    assert not np.isnan(z.values).any()
