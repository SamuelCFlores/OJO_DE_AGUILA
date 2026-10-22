"""Red de pases por posición: aristas por minuto y centralización de cualquier ventana.

REF1: contexto/framework.md, "Lectura del partido por puntos de quiebre" (bloque de circulación).
NOTA1: el nodo es la posición (posicion_id de StatsBomb), no el jugador: así la red se compara
entre partidos aunque cambien los nombres. La posición del receptor es la más frecuente de ese
jugador en el partido, porque el pase no trae la posición de quien recibe.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.framework import juego


def posicion_habitual(eventos: pd.DataFrame) -> pd.Series:
    """Posición más frecuente de cada jugador en cada partido: índice (match_id, jugador_id)."""
    con_posicion = eventos.dropna(subset=["jugador_id", "posicion_id"])
    conteo = con_posicion.groupby(["match_id", "jugador_id", "posicion_id"]).size().rename("n").reset_index()
    conteo = conteo.sort_values(["match_id", "jugador_id", "n", "posicion_id"], ascending=[True, True, False, True])
    return conteo.drop_duplicates(["match_id", "jugador_id"]).set_index(["match_id", "jugador_id"])["posicion_id"]


def aristas_por_minuto(eventos: pd.DataFrame) -> pd.DataFrame:
    """Pases completos entre posiciones por partido, periodo, minuto y equipo (aditivo por minuto).

    Columnas: match_id, periodo, minuto, equipo_id, origen, destino, pases. Se omiten los pases
    a la misma posición y los que no tienen receptor identificado.
    """
    pases = eventos[juego.es_pase_completo(eventos)].dropna(subset=["posicion_id", "pase_receptor_id"])
    habitual = posicion_habitual(eventos)
    claves = pd.MultiIndex.from_arrays([pases["match_id"], pases["pase_receptor_id"]])
    pases = pases.assign(origen=pases["posicion_id"].astype(int), destino=habitual.reindex(claves).to_numpy())
    pases = pases.dropna(subset=["destino"])
    pases = pases[pases["origen"] != pases["destino"]].astype({"destino": int})
    return (pases.groupby(["match_id", "periodo", "minuto", "equipo_id", "origen", "destino"])
            .size().rename("pases").reset_index())


def centralizacion(aristas: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    """Centralización de la red de cada grupo `por`, y los pases que la sostienen.

    centralizacion = Σ (s_max − s_i) / (n − 1), con s_i la fracción de los toques de red (pases dados
    y recibidos) de la posición i y n las posiciones con algún pase. 0 = circulación repartida;
    cerca de 1 = todo pasa por una posición.
    """
    origen = aristas[[*por, "origen", "pases"]].rename(columns={"origen": "posicion"})
    destino = aristas[[*por, "destino", "pases"]].rename(columns={"destino": "posicion"})
    grado = pd.concat([origen, destino]).groupby([*por, "posicion"])["pases"].sum().rename("grado").reset_index()
    total = grado.groupby(por)["grado"].transform("sum")
    grado["s"] = grado["grado"] / total
    resumen = grado.groupby(por).agg(s_max=("s", "max"), suma_s=("s", "sum"), n=("s", "size"))
    pases = aristas.groupby(por)["pases"].sum()
    # Σ (s_max − s_i) = n·s_max − Σ s_i = n·s_max − 1
    valor = (resumen["n"] * resumen["s_max"] - resumen["suma_s"]) / (resumen["n"] - 1).replace(0, np.nan)
    return pd.DataFrame({"centralizacion": valor, "pases": pases}).reset_index()
