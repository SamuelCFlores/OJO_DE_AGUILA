"""Efecto de cada punto de quiebre frente a sus ventanas de control (diferencia en diferencias), a dos bandas.

Es la tubería de las secciones 2–4 del notebook 02, empaquetada para correrla sobre cualquier conjunto de partidos
(por ejemplo, el torneo de prueba en el notebook 06).
REF1: contexto/framework.md, "Lectura del partido por puntos de quiebre".
NOTA1: los controles se buscan dentro del mismo valor de `por` (por defecto, el mismo grupo de entrenador).
"""

from __future__ import annotations

import pandas as pd

from ojo.framework import quiebres
from ojo.lentes import minuto

METRICAS = [m for lista in minuto.METRICAS.values() for m in lista]
COLUMNAS_EVENTOS = ["match_id", "indice", "periodo", "minuto", "tipo", "equipo_id", "tiro_resultado", "tarjeta",
                    "formacion", "sustitucion_resultado"]


def _a_ventanas(tabla: pd.DataFrame) -> pd.DataFrame:
    """Ventanas antes y después de cada fila (id, match_id, periodo y límites) en formato largo."""
    return pd.concat([pd.DataFrame({"ventana_id": tabla["id"] + "|" + fase, "match_id": tabla["match_id"],
                                    "periodo": tabla["periodo"], "desde": tabla[f"{fase}_desde"],
                                    "hasta": tabla[f"{fase}_hasta"]})
                      for fase in ("antes", "despues")], ignore_index=True)


def efectos(eventos: pd.DataFrame, panel: pd.DataFrame, aristas: pd.DataFrame, partidos: pd.DataFrame, equipo_id: int,
            por: tuple[str, ...] = ("grupo",)) -> pd.DataFrame:
    """Una fila por quiebre válido, lado y métrica: efecto = cambio tras el quiebre − cambio medio de sus controles.

    partidos: match_id, grupo y torneo_corto. Devuelve también tipo, grupo, torneo_corto, minuto y estado_antes.
    """
    info = partidos[["match_id", "grupo", "torneo_corto"]]
    limites = quiebres.limites_periodo(eventos)
    q = quiebres.ventanas(quiebres.detectar(eventos, equipo_id).merge(info, on="match_id"), limites)
    segmentos = quiebres.segmentos_libres(q, limites).merge(info[["match_id", *por]], on="match_id")
    controles = quiebres.controles(q, segmentos, por=por)
    controles["id"] = controles["quiebre_id"] + "|c" + controles.groupby("quiebre_id").cumcount().astype(str)
    validos = q[q["valida"]]
    ventanas = pd.concat([_a_ventanas(validos.assign(id=validos["quiebre_id"])), _a_ventanas(controles)], ignore_index=True)
    medidas = minuto.medir(panel, aristas, ventanas)
    medidas[["id", "fase"]] = medidas["ventana_id"].str.rsplit("|", n=1, expand=True)
    largo = medidas.melt(id_vars=["id", "fase", "lado"], value_vars=METRICAS, var_name="metrica")
    cambio = largo.pivot_table(index=["id", "lado", "metrica"], columns="fase", values="value").reset_index()
    cambio["cambio"] = cambio["despues"] - cambio["antes"]
    cambio["quiebre_id"] = cambio["id"].str.split("|c", regex=False).str[0]
    cambio["es_control"] = cambio["id"].str.contains("|c", regex=False)
    base = (cambio[cambio["es_control"]].groupby(["quiebre_id", "lado", "metrica"])["cambio"]
            .agg(cambio_control="mean", n_controles="size"))
    salida = (cambio[~cambio["es_control"]].join(base, on=["quiebre_id", "lado", "metrica"])
              .merge(q[["quiebre_id", "match_id", "tipo", "grupo", "torneo_corto", "minuto", "estado_antes"]], on="quiebre_id"))
    salida["efecto"] = salida["cambio"] - salida["cambio_control"]
    return salida
