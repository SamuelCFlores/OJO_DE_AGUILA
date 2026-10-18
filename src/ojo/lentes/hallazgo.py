"""Criterio de hallazgo: intervalo, tamaño, estabilidad por torneo y, desde la versión 2, pruebas múltiples.

REF1: contexto/framework.md, "Criterio de hallazgo" (v1 del 12 oct; v2 del 18 oct tras la auditoría A2).
NOTA1: la unidad de remuestreo es el partido: las acciones, minutos o quiebres de un mismo partido
no son independientes, así que se remuestrean partidos completos con reemplazo.
NOTA2: versión 2. (a) En los quiebres, la escala de la condición 2 es la DE del cambio antes→después en las
ventanas de control (la misma escala que el efecto), no la DE por partido completo. (b) Condición 4: el
efecto sobrevive a Benjamini-Hochberg (FDR) dentro de su familia de pruebas. (c) Placebo: el mismo criterio
aplicado a ventanas de control tratadas como si fueran quiebres dice cuántas pruebas pasan por azar.
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


def evaluar(efecto: float, bajo: float, alto: float, escala: float, torneos_misma_direccion: int,
            cfg: dict | None = None) -> dict:
    """Aplica las condiciones 1–3 del criterio y dice cuáles se cumplen (la 4, FDR, la agrega `con_fdr`).

    1. El intervalo no cruza 0. 2. |efecto| ≥ tamano_min_de · escala (v1: DE entre partidos; v2 en los
    quiebres: DE del cambio en las ventanas de control). 3. Misma dirección en al menos
    min_torneos_misma_direccion torneos.
    """
    cfg = cfg or params()["hallazgo"]
    tamano = efecto / escala if escala and escala > 0 else np.nan
    c1 = bool(bajo > 0 or alto < 0)
    c2 = bool(abs(tamano) >= cfg["tamano_min_de"]) if np.isfinite(tamano) else False
    c3 = torneos_misma_direccion >= cfg["min_torneos_misma_direccion"]
    return {"tamano_de": tamano, "ic_sin_cero": c1, "tamano_suficiente": c2, "estable": c3, "pasa": c1 and c2 and c3}


def p_bootstrap(muestras: np.ndarray) -> float:
    """p de dos colas a partir de las medias del bootstrap: qué tan seguido el remuestreo cae del otro lado de 0.

    Con la corrección +1 (nunca da 0): p = 2 · min(#{m ≤ 0} + 1, #{m ≥ 0} + 1) / (n + 1), recortado a 1.
    """
    m = np.asarray(muestras, dtype=float)
    m = m[np.isfinite(m)]
    if len(m) == 0:
        return np.nan
    abajo, arriba = (m <= 0).sum() + 1, (m >= 0).sum() + 1
    return float(min(1.0, 2 * min(abajo, arriba) / (len(m) + 1)))


def fdr_bh(p: np.ndarray | pd.Series) -> np.ndarray:
    """Valores q de Benjamini-Hochberg (monótonos, ≤ 1). Los p vacíos dan q vacío y no cuentan en el total."""
    p = np.asarray(p, dtype=float)
    q = np.full(p.shape, np.nan)
    validos = np.flatnonzero(np.isfinite(p))
    if len(validos) == 0:
        return q
    orden = validos[np.argsort(p[validos])]
    m = len(orden)
    ajustados = p[orden] * m / np.arange(1, m + 1)
    ajustados = np.minimum.accumulate(ajustados[::-1])[::-1]  # monótonos de arriba hacia abajo
    q[orden] = np.minimum(ajustados, 1.0)
    return q


def con_fdr(tabla: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Condición 4 (v2): agrega q (BH sobre la columna p de la familia), `fdr` (q ≤ hallazgo.fdr_q) y `pasa_1a3`
    (condiciones 1–3); `pasa` queda como el criterio v2 completo (condiciones 1–4)."""
    cfg = cfg or params()["hallazgo"]
    t = tabla.copy()
    t["q"] = fdr_bh(t["p"])
    t["fdr"] = t["q"] <= cfg["fdr_q"]
    t["pasa_1a3"] = t["pasa"].astype(bool)
    t["pasa"] = t["pasa_1a3"] & t["fdr"]
    return t


def efectos_placebo(cambio_controles: pd.DataFrame) -> pd.DataFrame:
    """Placebo: para cada quiebre con 2+ controles, el primer control hace de quiebre falso y los demás de controles.

    Recibe el cambio antes→después de las ventanas de control (quiebre_id, id, lado, metrica, cambio) y devuelve
    quiebre_id, id (el control que hace de quiebre falso), lado, metrica y efecto = su cambio − la media del cambio
    de los demás controles. Si el criterio es bueno, casi nada de esto debería pasar.
    """
    c = cambio_controles.dropna(subset=["cambio"]).sort_values("id")
    grupos = c.groupby(["quiebre_id", "lado", "metrica"])
    primero, elegido = grupos["cambio"].first(), grupos["id"].first()
    total, n = grupos["cambio"].sum(), grupos["cambio"].size()
    resto = (total - primero) / (n - 1).where(n >= 2)
    salida = pd.DataFrame({"id": elegido, "efecto": primero - resto})[n >= 2]
    return salida.reset_index()
