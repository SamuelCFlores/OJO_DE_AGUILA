"""Índice Proactivo–Reactivo por minuto, a dos bandas (PROPUESTA del 14 oct, pendiente de confirmar).

Ordena el juego en una escala: 0 = reactivo (juego directo y transiciones), 100 = proactivo (iniciativa
y posesión asentada). Cada componente es una métrica con sentido de cancha; se estandariza (z) con
los minutos de entrenamiento, se le pone signo (+ proactivo, − reactivo), se promedia con el mismo
peso y el promedio se lleva a percentil (0–100) frente a los minutos de entrenamiento.

REF1: contexto/framework.md, "Índice Proactivo–Reactivo (propuesta)"; pesos y ventana en params.yaml.
NOTA1: se calcula por minuto con una ventana hacia atrás de indice.ventana_min minutos (lo que el
equipo llevaba hasta ese minuto), no por foto: las fotos 360 solo existen en los eventos y dependen
de la cámara (auditoría A4).
NOTA2: el eje "control" usa Phases of Play de StatsBomb (is_transition sobre pases, conducciones y
tiros, ponderado por su duración), igual que time_in_control de Team Match Stats.
TODO1: verificar con PCA que el primer componente coincide con el eje antes de fijar los pesos.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ojo.config import params
from ojo.framework import contexto
from ojo.lentes import minuto

EN_BALON = frozenset({"Pass", "Carry", "Shot"})  # acciones con balón de Phases of Play
NOMBRES = {
    "control": "Juego asentado", "posesion": "Posesión", "field_tilt": "Field tilt",
    "control_campo_rival": "Espacio en campo rival", "altura_sin_balon": "Altura del bloque",
    "presion_alta": "Presión alta", "directness": "Juego directo", "largo_pase": "Pase largo",
}
# Para el radar: todos los ejes se leen "hacia afuera = más proactivo" (los reactivos ya llevan signo −).
NOMBRES_RADAR = {
    "control": "Asentado", "posesion": "Posesión", "field_tilt": "Field tilt", "control_campo_rival": "Espacio arriba",
    "altura_sin_balon": "Bloque alto", "presion_alta": "Presión alta", "directness": "Elabora", "largo_pase": "Pase corto",
}
CLAVES = ["match_id", "periodo", "minuto", "equipo_id"]


def piezas_por_minuto(eventos: pd.DataFrame) -> pd.DataFrame:
    """Sumas por minuto y equipo que el panel no guarda: duración con balón, en control, directness y pases."""
    ev = eventos[eventos["periodo"] != contexto.PERIODO_PENALES]
    en_balon = ev["tipo"].isin(EN_BALON) & ev["duracion"].notna()
    fase = en_balon & ev["es_transicion"].notna()
    pase = ev["tipo"] == "Pass"
    largo = np.hypot(ev["fin_x"] - ev["x"], ev["fin_y"] - ev["y"])
    piezas = pd.DataFrame({
        "dur_balon": ev["duracion"].where(en_balon, 0.0),
        "dur_fase": ev["duracion"].where(fase, 0.0),
        "dur_control": ev["duracion"].where(fase & ~ev["es_transicion"].fillna(True).astype(bool), 0.0),
        "directness_suma": ev["directness"].where(en_balon & ev["directness"].notna(), 0.0),
        "directness_n": (en_balon & ev["directness"].notna()).astype(float),
        "largo_suma": largo.where(pase & largo.notna(), 0.0),
        "pases_n": (pase & largo.notna()).astype(float),
    }, index=ev.index).fillna(0.0)
    return pd.concat([ev[CLAVES], piezas], axis=1).groupby(CLAVES).sum().reset_index()


def _ventana(tabla: pd.DataFrame, columnas: list[str], ventana: int) -> pd.DataFrame:
    """Suma hacia atrás de `ventana` minutos dentro de cada partido, periodo y equipo (minutos sin eventos = 0)."""
    partes = []
    for clave, g in tabla.groupby(["match_id", "periodo", "equipo_id"], sort=False):
        g = g.set_index("minuto").sort_index()
        completo = g[columnas].reindex(range(int(g.index.min()), int(g.index.max()) + 1), fill_value=0.0)
        sumas = completo.rolling(ventana, min_periods=1).sum()
        sumas["n_min"] = completo.index.to_series().rolling(ventana, min_periods=1).count().to_numpy()
        sumas = sumas.loc[g.index].reset_index()
        sumas[["match_id", "periodo", "equipo_id"]] = clave
        partes.append(sumas)
    return pd.concat(partes, ignore_index=True)


def componentes(panel: pd.DataFrame, piezas: pd.DataFrame, ventana_min: int | None = None) -> pd.DataFrame:
    """Componentes del índice por minuto y equipo (ventana hacia atrás), con lado y estado del panel."""
    ventana_min = ventana_min or params()["indice"]["ventana_min"]
    base = panel.merge(piezas, on=CLAVES, how="left").fillna({c: 0.0 for c in piezas.columns if c not in CLAVES})
    sumas_cols = ["pases_ultimo_tercio", "control_campo_rival_suma", "control_campo_rival_n", "altura_sin_suma",
                  "forma_sin_n", "presiones_campo_rival", "dur_balon", "dur_fase", "dur_control",
                  "directness_suma", "directness_n", "largo_suma", "pases_n"]
    s = _ventana(base[CLAVES + sumas_cols], sumas_cols, ventana_min)
    s = s.merge(base[CLAVES + ["lado", "estado"]], on=CLAVES)
    otro = s[["match_id", "periodo", "minuto", "lado", "dur_balon", "pases_ultimo_tercio"]].copy()
    otro["lado"] = otro["lado"].map({minuto.PROPIO: minuto.RIVAL, minuto.RIVAL: minuto.PROPIO})
    s = s.merge(otro, on=["match_id", "periodo", "minuto", "lado"], how="left", suffixes=("", "_otro"))
    div = lambda a, b: a / b.where(b > 0)  # noqa: E731
    s["control"] = div(s["dur_control"], s["dur_fase"])
    s["posesion"] = div(s["dur_balon"], s["dur_balon"] + s["dur_balon_otro"])
    s["field_tilt"] = div(s["pases_ultimo_tercio"], s["pases_ultimo_tercio"] + s["pases_ultimo_tercio_otro"])
    s["control_campo_rival"] = div(s["control_campo_rival_suma"], s["control_campo_rival_n"])
    s["altura_sin_balon"] = div(s["altura_sin_suma"], s["forma_sin_n"])
    s["presion_alta"] = div(s["presiones_campo_rival"], s["n_min"])
    s["directness"] = div(s["directness_suma"], s["directness_n"])
    s["largo_pase"] = div(s["largo_suma"], s["pases_n"])
    return s[[*CLAVES, "lado", "estado", *NOMBRES]]


@dataclass
class Escala:
    """Medias, desviaciones y distribución del compuesto en los minutos de entrenamiento."""

    medias: pd.Series
    desviaciones: pd.Series
    compuestos: np.ndarray  # ordenados, para llevar a percentil


def ajustar(comp: pd.DataFrame, signos: dict[str, int] | None = None) -> Escala:
    """Escala con los minutos de entrenamiento (ambos equipos, sin el torneo de prueba)."""
    signos = signos or params()["indice"]["componentes"]
    cols = list(signos)
    medias, desv = comp[cols].mean(), comp[cols].std()
    compuesto = _compuesto(comp, medias, desv, signos)
    return Escala(medias, desv, np.sort(compuesto.dropna().to_numpy()))


def _z(comp: pd.DataFrame, medias: pd.Series, desv: pd.Series, signos: dict[str, int]) -> pd.DataFrame:
    return pd.DataFrame({c: signo * (comp[c] - medias[c]) / desv[c] for c, signo in signos.items()}, index=comp.index)


def _compuesto(comp: pd.DataFrame, medias: pd.Series, desv: pd.Series, signos: dict[str, int]) -> pd.Series:
    return _z(comp, medias, desv, signos).mean(axis=1, skipna=True)


def calcular(comp: pd.DataFrame, escala: Escala, signos: dict[str, int] | None = None) -> pd.DataFrame:
    """Agrega z_<componente> (con signo: + proactivo), compuesto e indice (percentil 0–100)."""
    signos = signos or params()["indice"]["componentes"]
    z = _z(comp, escala.medias, escala.desviaciones, signos).add_prefix("z_")
    tabla = pd.concat([comp, z], axis=1)
    tabla["compuesto"] = z.mean(axis=1, skipna=True)
    rango = np.searchsorted(escala.compuestos, tabla["compuesto"].to_numpy(), side="right")
    tabla["indice"] = np.where(tabla["compuesto"].notna(), 100 * rango / max(len(escala.compuestos), 1), np.nan)
    return tabla
