"""Contexto de cada evento: tramo del partido, marcador (game state) y orientación.

REF1: contexto/framework.md, secciones "Coordenadas y orientación", "Lectura a dos bandas"
(tramo) y "Contexto del partido" (marcador).
OBS1: verificado con la API real (9 oct): cada evento viene en la perspectiva de quien lo
ejecuta (sus tiros tienen x cercana a 120 para ambos equipos).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.config import params

INICIO_PERIODO = {1: 0, 2: 45, 3: 90, 4: 105}  # minuto de reloj en que arranca cada periodo
FIN_PERIODO = {1: 45, 2: 90, 3: 105, 4: 120}
PERIODO_PENALES = 5
GANA, EMPATA, PIERDE = "gana", "empata", "pierde"


def tramo(periodo: pd.Series, minuto: pd.Series, tramos_min: int | None = None) -> pd.Series:
    """Etiqueta del tramo: ventanas de tramos_min minutos por periodo; el añadido es un tramo propio.

    Ejemplos con 15 min: "1T 0-15", "1T 30-45", "1T 45+", "2T 60-75", "2T 90+".
    """
    tramos_min = tramos_min or params()["tramos_min"]
    etiquetas = []
    for p, m in zip(periodo.astype(int), minuto.astype(int)):
        if p not in INICIO_PERIODO:
            etiquetas.append(None)
            continue
        inicio, fin = INICIO_PERIODO[p], FIN_PERIODO[p]
        nombre = f"{p}T" if p <= 2 else f"PR{p - 2}"
        if m >= fin:
            etiquetas.append(f"{nombre} {fin}+")
            continue
        desde = inicio + ((m - inicio) // tramos_min) * tramos_min
        hasta = min(desde + tramos_min, fin)
        etiquetas.append(f"{nombre} {desde}-{hasta}")
    return pd.Series(etiquetas, index=periodo.index, dtype="object")


def goles_por_evento(eventos: pd.DataFrame) -> pd.Series:
    """Equipo que anota con cada evento (id) o NaN: tiro con resultado Goal u Own Goal For.

    IMPOR1: no se cuentan los tiros de la tanda de penales (periodo 5).
    """
    gol_de_tiro = (eventos["tipo"] == "Shot") & (eventos["tiro_resultado"] == "Goal")
    autogol_a_favor = eventos["tipo"] == "Own Goal For"
    anota = (gol_de_tiro | autogol_a_favor) & (eventos["periodo"] != PERIODO_PENALES)
    return eventos["equipo_id"].where(anota)


def marcador(eventos: pd.DataFrame, equipo_id: int) -> pd.DataFrame:
    """Goles a favor, en contra y estado (gana/empata/pierde) de un equipo ANTES de cada evento."""
    ordenados = eventos.sort_values("indice")
    anotador = goles_por_evento(ordenados)
    favor = (anotador == equipo_id).astype(int)
    contra = (anotador.notna() & (anotador != equipo_id)).astype(int)
    # Antes del evento: el gol cuenta a partir del evento siguiente.
    goles_favor = favor.cumsum().shift(fill_value=0)
    goles_contra = contra.cumsum().shift(fill_value=0)
    diferencia = goles_favor - goles_contra
    estado = np.select([diferencia > 0, diferencia < 0], [GANA, PIERDE], default=EMPATA)
    resultado = pd.DataFrame(
        {"goles_favor": goles_favor, "goles_contra": goles_contra, "estado": estado}, index=ordenados.index
    )
    return resultado.loc[eventos.index]


def orientar(eventos: pd.DataFrame, equipo_id: int, columnas: tuple[tuple[str, str], ...] = (("x", "y"), ("fin_x", "fin_y"))) -> pd.DataFrame:
    """Lleva las coordenadas a la perspectiva de equipo_id (ataca hacia x = 120).

    Las acciones del rival vienen en su propia perspectiva; se reflejan con (120 - x, 80 - y).
    """
    campo = params()["campo"]
    tabla = eventos.copy()
    del_rival = tabla["equipo_id"] != equipo_id
    for cx, cy in columnas:
        if cx in tabla:
            tabla.loc[del_rival, cx] = campo["largo"] - tabla.loc[del_rival, cx]
        if cy in tabla:
            tabla.loc[del_rival, cy] = campo["ancho"] - tabla.loc[del_rival, cy]
    return tabla


def con_contexto(eventos: pd.DataFrame, equipo_id: int) -> pd.DataFrame:
    """Eventos con tramo, marcador del equipo y coordenadas en su perspectiva."""
    tabla = orientar(eventos, equipo_id)
    tabla["tramo"] = tramo(tabla["periodo"], tabla["minuto"])
    return tabla.join(marcador(eventos, equipo_id))
