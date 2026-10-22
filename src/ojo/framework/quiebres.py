"""Puntos de quiebre del partido, sus ventanas antes/después y las ventanas de control.

REF1: contexto/framework.md, "Lectura del partido por puntos de quiebre".
NOTA1: todo se mide desde un equipo de referencia (el América): "favor" y "propio" son suyos.
NOTA2: el reloj es el minuto entero de StatsBomb dentro de cada periodo; ninguna ventana cruza
el descanso, porque el añadido del primer tiempo y el arranque del segundo comparten minutos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.config import params
from ojo.framework import contexto

TARJETAS_EXPULSION = frozenset({"Red Card", "Second Yellow"})
SUSTITUCION_TACTICA, SUSTITUCION_LESION = "Tactical", "Injury"
INICIO_PARTIDO, CAMBIO_TACTICO = "Starting XI", "Tactical Shift"

# Los que cambian el marcador o el número de jugadores cortan las ventanas de los demás.
TIPOS_QUE_CORTAN = ("gol_favor", "gol_contra", "expulsion_favor", "expulsion_contra")
TIPOS_QUE_NO_CORTAN = (
    "cambio_sistema_propio", "cambio_sistema_rival",
    "sustitucion_tactica_propia", "sustitucion_tactica_rival",
    "sustitucion_lesion_propia", "sustitucion_lesion_rival",
)
TIPOS = TIPOS_QUE_CORTAN + TIPOS_QUE_NO_CORTAN
COLUMNAS = ["match_id", "indice", "periodo", "minuto", "tipo", "corta", "estado_antes", "detalle"]


def _cambios_de_sistema(ev: pd.DataFrame) -> pd.DataFrame:
    """Tactical Shift cuya formación difiere de la vigente de ese equipo (Starting XI o cambio previo)."""
    tacticos = ev[ev["tipo"].isin([INICIO_PARTIDO, CAMBIO_TACTICO])].sort_values("indice")
    previa = tacticos.groupby("equipo_id")["formacion"].shift()
    cambio = (tacticos["tipo"] == CAMBIO_TACTICO) & previa.notna() & (tacticos["formacion"] != previa)
    resultado = tacticos[cambio].copy()
    resultado["detalle"] = previa[cambio].astype(int).astype(str) + "→" + resultado["formacion"].astype(int).astype(str)
    return resultado


def detectar_partido(eventos: pd.DataFrame, equipo_id: int) -> pd.DataFrame:
    """Quiebres de UN partido desde equipo_id, en orden; sin la tanda de penales."""
    ev = eventos[eventos["periodo"] != contexto.PERIODO_PENALES]
    estado = contexto.marcador(ev, equipo_id)["estado"]
    propio = ev["equipo_id"] == equipo_id
    partes = []

    def agregar(filtro: pd.Series, tipo_propio: str, tipo_rival: str, detalle: pd.Series | str) -> None:
        sub = ev[filtro].assign(detalle=detalle if isinstance(detalle, str) else detalle[filtro])
        sub["tipo"] = np.where(propio[filtro], tipo_propio, tipo_rival)
        partes.append(sub)

    anotador = contexto.goles_por_evento(ev)
    gol = anotador.notna()
    partes.append(ev[gol].assign(tipo=np.where(anotador[gol] == equipo_id, "gol_favor", "gol_contra"), detalle=""))
    # Una expulsión al rival favorece al equipo de referencia.
    agregar(ev["tarjeta"].isin(TARJETAS_EXPULSION), "expulsion_contra", "expulsion_favor", ev["tarjeta"].astype(str))
    sistema = _cambios_de_sistema(ev)
    if not sistema.empty:
        partes.append(sistema.assign(
            tipo=np.where(sistema["equipo_id"] == equipo_id, "cambio_sistema_propio", "cambio_sistema_rival")))
    sustitucion = ev["tipo"] == "Substitution"
    agregar(sustitucion & (ev["sustitucion_resultado"] == SUSTITUCION_TACTICA),
            "sustitucion_tactica_propia", "sustitucion_tactica_rival", "")
    agregar(sustitucion & (ev["sustitucion_resultado"] == SUSTITUCION_LESION),
            "sustitucion_lesion_propia", "sustitucion_lesion_rival", "")

    partes = [p for p in partes if not p.empty]
    if not partes:
        return pd.DataFrame(columns=COLUMNAS)
    tabla = pd.concat(partes)
    tabla["estado_antes"] = estado.reindex(tabla.index)
    tabla["corta"] = tabla["tipo"].isin(TIPOS_QUE_CORTAN)
    return tabla[COLUMNAS].sort_values("indice").reset_index(drop=True)


def detectar(eventos: pd.DataFrame, equipo_id: int) -> pd.DataFrame:
    """Quiebres de varios partidos; agrega quiebre_id (match_id-indice) como clave única."""
    tablas = [detectar_partido(grupo, equipo_id) for _, grupo in eventos.groupby("match_id")]
    tabla = pd.concat([t for t in tablas if not t.empty], ignore_index=True) if tablas else pd.DataFrame(columns=COLUMNAS)
    tabla["quiebre_id"] = tabla["match_id"].astype(str) + "-" + tabla["indice"].astype(str)
    return tabla


def limites_periodo(eventos: pd.DataFrame) -> pd.DataFrame:
    """Primer y último minuto con eventos de cada periodo de cada partido (sin penales)."""
    ev = eventos[eventos["periodo"] != contexto.PERIODO_PENALES]
    return (ev.groupby(["match_id", "periodo"])["minuto"].agg(inicio="min", fin="max").reset_index())


def ventanas(quiebres: pd.DataFrame, limites: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Ventanas antes/después de cada quiebre en minutos enteros (límites inclusivos).

    Antes = [m − ventana, m − exclusión − 1]; después = [m + exclusión + 1, m + ventana].
    Se truncan en el inicio y fin del periodo y en el quiebre que corta anterior o siguiente
    (dejando también su exclusión). valida = ambas ventanas miden al menos min_ventana_min.
    """
    cfg = cfg or params()["quiebres"]
    v, e = cfg["ventana_min"], cfg["exclusion_min"]
    tabla = quiebres.merge(limites, on=["match_id", "periodo"], how="left")
    cortes = quiebres[quiebres["corta"]][["match_id", "periodo", "indice", "minuto"]]
    previo, siguiente = [], []
    for q in tabla.itertuples():
        mismos = cortes[(cortes["match_id"] == q.match_id) & (cortes["periodo"] == q.periodo)]
        antes = mismos[mismos["indice"] < q.indice]["minuto"]
        despues = mismos[mismos["indice"] > q.indice]["minuto"]
        previo.append(antes.max() + e + 1 if not antes.empty else -np.inf)
        siguiente.append(despues.min() - e - 1 if not despues.empty else np.inf)
    m = tabla["minuto"]
    tabla["antes_desde"] = np.maximum.reduce([m - v, tabla["inicio"], np.array(previo)]).astype(int)
    tabla["antes_hasta"] = m - e - 1
    tabla["despues_desde"] = m + e + 1
    tabla["despues_hasta"] = np.minimum.reduce([m + v, tabla["fin"], np.array(siguiente)]).astype(int)
    tabla["min_antes"] = (tabla["antes_hasta"] - tabla["antes_desde"] + 1).clip(lower=0)
    tabla["min_despues"] = (tabla["despues_hasta"] - tabla["despues_desde"] + 1).clip(lower=0)
    tabla["valida"] = (tabla["min_antes"] >= cfg["min_ventana_min"]) & (tabla["min_despues"] >= cfg["min_ventana_min"])
    return tabla.drop(columns=["inicio", "fin"])


def _estado(goles_favor: int, goles_contra: int) -> str:
    if goles_favor > goles_contra:
        return contexto.GANA
    return contexto.PIERDE if goles_favor < goles_contra else contexto.EMPATA


def segmentos_libres(quiebres: pd.DataFrame, limites: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Tramos de cada periodo sin quiebres que corten (con su exclusión), y el estado del marcador en ellos.

    Dentro de un segmento el marcador no cambia (los goles son quiebres que cortan), así que
    cualquier ventana dentro de él sirve de control para un quiebre con ese estado previo.
    """
    e = (cfg or params()["quiebres"])["exclusion_min"]
    filas = []
    for match_id, lim in limites.groupby("match_id"):
        cortes = quiebres[(quiebres["match_id"] == match_id) & quiebres["corta"]].sort_values(["periodo", "indice"])
        favor = contra = 0
        for lp in lim.sort_values("periodo").itertuples():
            desde = lp.inicio
            for c in cortes[cortes["periodo"] == lp.periodo].itertuples():
                filas.append((match_id, lp.periodo, desde, c.minuto - e - 1, _estado(favor, contra)))
                favor += c.tipo == "gol_favor"
                contra += c.tipo == "gol_contra"
                desde = c.minuto + e + 1
            filas.append((match_id, lp.periodo, desde, lp.fin, _estado(favor, contra)))
    tabla = pd.DataFrame(filas, columns=["match_id", "periodo", "desde", "hasta", "estado"])
    return tabla[tabla["hasta"] >= tabla["desde"]].reset_index(drop=True)


def controles(quiebres_v: pd.DataFrame, segmentos: pd.DataFrame, por: tuple[str, ...] = (),
              cfg: dict | None = None, semilla: int | None = None) -> pd.DataFrame:
    """Ventanas de control de cada quiebre válido: otro partido, mismo periodo y estado, minuto ± tolerancia.

    Cada control copia las ventanas del quiebre (mismos desfases respecto a su minuto) en un minuto
    m' cuya ventana completa cae en un segmento libre. Se eligen los más cercanos en minuto y los
    empates se rompen al azar con semilla fija, hasta max_controles por quiebre. `por` agrega
    columnas que deben coincidir (p. ej. el entrenador) y que deben estar en ambas tablas.
    """
    cfg = cfg or params()["quiebres"]
    semilla = params()["simulacion"]["semilla"] if semilla is None else semilla
    q = quiebres_v[quiebres_v["valida"]].copy()
    q["a0"] = q["minuto"] - q["antes_desde"]
    q["d1"] = q["despues_hasta"] - q["minuto"]
    claves = ["periodo", *por]
    cruce = q[["quiebre_id", "match_id", "minuto", "estado_antes", "a0", "d1", *claves]].merge(
        segmentos.rename(columns={"match_id": "match_control", "estado": "estado_antes"}),
        on=[*claves, "estado_antes"])
    cruce = cruce[cruce["match_control"] != cruce["match_id"]]
    bajo, alto = cruce["desde"] + cruce["a0"], cruce["hasta"] - cruce["d1"]
    cruce["minuto_control"] = cruce["minuto"].clip(lower=bajo, upper=alto)
    cruce["distancia"] = (cruce["minuto_control"] - cruce["minuto"]).abs()
    cruce = cruce[(bajo <= alto) & (cruce["distancia"] <= cfg["tolerancia_control_min"])].copy()
    cruce["azar"] = np.random.default_rng(semilla).random(len(cruce))
    cruce = (cruce.sort_values(["quiebre_id", "distancia", "azar"])
             .groupby("quiebre_id").head(cfg["max_controles"]))
    desfases = q.set_index("quiebre_id")[["antes_desde", "antes_hasta", "despues_desde", "despues_hasta", "minuto"]]
    rel = desfases.sub(desfases["minuto"], axis=0).drop(columns="minuto")
    tabla = cruce[["quiebre_id", "match_control", "periodo", "minuto_control"]].join(rel, on="quiebre_id")
    for col in rel.columns:
        tabla[col] = tabla[col] + tabla["minuto_control"]
    return tabla.rename(columns={"match_control": "match_id", "minuto_control": "minuto"}).reset_index(drop=True)
