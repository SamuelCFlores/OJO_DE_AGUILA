"""Validación en el torneo de prueba: ¿cada principio mantiene su dirección en partidos que el análisis no vio?

REF1: contexto/framework.md, "Validación, causalidad y decisión" y contexto/plan_cierre.md (fase A).
IMPOR1: el torneo de prueba se abre una sola vez, con los principios ya fijados por el criterio v2; se informa el
veredicto aunque un principio no se sostenga.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.config import params
from ojo.lentes import hallazgo

VEREDICTOS = {"se_sostiene": "Se sostiene", "misma_direccion": "Misma dirección, sin certeza",
              "no_se_sostiene": "No se sostiene", "sin_muestra": "Sin muestra suficiente"}


def veredicto(dif_entrenamiento: float, dif_prueba: float, bajo: float, alto: float, partidos_prueba: int,
              min_partidos: int | None = None) -> str:
    """Clave de VEREDICTOS: la diferencia del torneo de prueba frente a la de entrenamiento (misma métrica, mismos previos)."""
    min_partidos = min_partidos or params()["validacion"]["min_partidos_prueba"]
    if partidos_prueba < min_partidos or not np.isfinite(dif_prueba):
        return "sin_muestra"
    if np.sign(dif_prueba) != np.sign(dif_entrenamiento):
        return "no_se_sostiene"
    return "se_sostiene" if (bajo > 0 or alto < 0) else "misma_direccion"


def diferencia(prueba: pd.DataFrame, previos: pd.DataFrame, valor: str, rng: np.random.Generator) -> dict:
    """Diferencia de medias prueba − previos con IC por bootstrap de partidos (cada lado se remuestrea por separado)."""
    p, v = prueba.dropna(subset=[valor]), previos.dropna(subset=[valor])
    n = int(p["match_id"].nunique())
    if n == 0 or v.empty:
        return {"dif": np.nan, "bajo": np.nan, "alto": np.nan, "partidos": n, "eventos": len(p)}
    medias = hallazgo.medias_bootstrap(p, valor, rng) - hallazgo.medias_bootstrap(v, valor, rng)
    bajo, alto = hallazgo.intervalo(medias)
    dif = float(p.groupby("match_id")[valor].sum().sum() / len(p) - v.groupby("match_id")[valor].sum().sum() / len(v))
    return {"dif": dif, "bajo": bajo, "alto": alto, "partidos": n, "eventos": len(p)}
