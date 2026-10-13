"""Criterio de hallazgo fijado antes de ver resultados: intervalo, tamaño y estabilidad por torneo.

REF1: contexto/framework.md, "Criterio de hallazgo" (12 oct).
NOTA1: la unidad de remuestreo es el partido: las acciones, minutos o quiebres de un mismo partido
no son independientes, así que se remuestrean partidos completos con reemplazo.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.config import params


def _sumas_por_partido(tabla: pd.DataFrame, valor: str) -> tuple[np.ndarray, np.ndarray]:
    g = tabla.dropna(subset=[valor]).groupby("match_id")[valor].agg(["sum", "size"])
    return g["sum"].to_numpy(float), g["size"].to_numpy(float)


def medias_bootstrap(tabla: pd.DataFrame, valor: str, rng: np.random.Generator,
                     repeticiones: int | None = None) -> np.ndarray:
    """Media de `valor` en cada remuestreo de partidos (cada fila pesa igual dentro de su partido)."""
    repeticiones = repeticiones or params()["estadistica"]["bootstrap_repeticiones"]
    sumas, conteos = _sumas_por_partido(tabla, valor)
    if len(sumas) == 0:
        return np.full(repeticiones, np.nan)
    idx = rng.integers(0, len(sumas), size=(repeticiones, len(sumas)))
    return sumas[idx].sum(axis=1) / conteos[idx].sum(axis=1)


def intervalo(muestras: np.ndarray, nivel: float | None = None) -> tuple[float, float]:
    """Intervalo de percentiles del bootstrap al nivel de confianza de params.yaml."""
    nivel = nivel or params()["estadistica"]["nivel_confianza"]
    alfa = (1 - nivel) / 2
    return float(np.nanquantile(muestras, alfa)), float(np.nanquantile(muestras, 1 - alfa))


def direcciones(por_torneo: pd.Series, efecto: float) -> int:
    """Torneos cuyo efecto va en la misma dirección que el efecto global (los vacíos no cuentan)."""
    return int((np.sign(por_torneo.dropna()) == np.sign(efecto)).sum()) if efecto else 0


def evaluar(efecto: float, bajo: float, alto: float, de_entre_partidos: float, torneos_misma_direccion: int,
            cfg: dict | None = None) -> dict:
    """Aplica las tres condiciones del criterio y dice cuáles se cumplen.

    1. El intervalo no cruza 0. 2. |efecto| ≥ tamano_min_de · DE entre partidos.
    3. Misma dirección en al menos min_torneos_misma_direccion torneos.
    """
    cfg = cfg or params()["hallazgo"]
    tamano = efecto / de_entre_partidos if de_entre_partidos and de_entre_partidos > 0 else np.nan
    c1 = bool(bajo > 0 or alto < 0)
    c2 = bool(abs(tamano) >= cfg["tamano_min_de"]) if np.isfinite(tamano) else False
    c3 = torneos_misma_direccion >= cfg["min_torneos_misma_direccion"]
    return {"tamano_de": tamano, "ic_sin_cero": c1, "tamano_suficiente": c2, "estable": c3, "pasa": c1 and c2 and c3}
