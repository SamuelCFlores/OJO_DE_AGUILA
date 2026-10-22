"""Panel por minuto a dos bandas y métricas de cualquier ventana o tramo.

El panel guarda, por partido, periodo, minuto y equipo, solo sumas y conteos (son aditivos):
cualquier ventana (antes/después de un quiebre, control, tramo, partido completo) se arma
sumando minutos, sin volver a leer eventos ni frames.

REF1: contexto/framework.md, "Lectura del partido por puntos de quiebre" (métricas por bloque).
NOTA1: "propio" y "rival" se refieren al equipo de referencia; el riesgo de un lado es lo que
genera el otro (tiros en transición y contragolpes en contra).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ojo.config import DIR_SALIDAS, params
from ojo.framework import contexto, juego
from ojo.lentes import forma as lente_forma
from ojo.lentes import redes

PROPIO, RIVAL = "propio", "rival"
CONTRAGOLPE = "From Counter"
FASES = {"con": True, "sin": False}  # forma con y sin balón

SUMAS_EVENTOS = ("eventos", "presiones", "presiones_campo_rival", "faltas", "contrapresiones", "xg", "obv",
                 "pases_completos", "pases_ultimo_tercio", "tiros_transicion")
SUMAS_FORMA = tuple(f"{m}_{f}_suma" for f in FASES for m in lente_forma.METRICAS) + tuple(f"forma_{f}_n" for f in FASES)
SUMAS = SUMAS_EVENTOS + ("contragolpes", "control_campo_rival_suma", "control_campo_rival_n") + SUMAS_FORMA

# Métricas pre-registradas por bloque (framework.md); el orden es el de las tablas de resultados.
METRICAS = {
    "estructura": ["control_campo_rival", "altura_sin_balon", "largo_sin_balon", "ancho_con_balon",
                   "compactacion_sin_balon"],
    "circulacion": ["centralizacion"],
    "intensidad": ["presiones", "faltas", "contrapresiones"],
    "valor": ["xg", "obv", "field_tilt"],
    "riesgo": ["tiros_transicion_contra", "contragolpes_contra"],
}
BLOQUE_DE = {m: b for b, lista in METRICAS.items() for m in lista}
CLAVES_MINUTO = ["match_id", "periodo", "minuto"]
DIR_PANEL = DIR_SALIDAS / "panel"  # lo escribe scripts/05_panel.py (fuera de git)
SALIDAS = ("minuto", "aristas", "forma")


def _banderas(ev: pd.DataFrame) -> pd.DataFrame:
    """Columnas 0/1 o valores por evento que luego se suman por minuto."""
    cfg = params()
    tiro = ev["tipo"] == "Shot"
    presion = ev["tipo"] == "Pressure"
    completo = juego.es_pase_completo(ev)
    return pd.DataFrame({
        "eventos": 1,
        "presiones": presion,
        "presiones_campo_rival": presion & (ev["x"] >= cfg["presion"]["campo_rival_min_x"]),
        "faltas": ev["tipo"] == "Foul Committed",
        "contrapresiones": ev["contrapresion"].fillna(False).astype(bool),
        "xg": ev["tiro_xg"].where(tiro, 0.0).fillna(0.0),
        "obv": ev["obv_total_net"].fillna(0.0),
        "pases_completos": completo,
        "pases_ultimo_tercio": completo & (ev["x"] >= cfg["tercios"]["final_min_x"]),
        "tiros_transicion": tiro & (ev["es_transicion"].fillna(False).astype(bool)),
    }, index=ev.index).astype(float)


def panel_partido(eventos: pd.DataFrame, equipo_id: int, voronoi: pd.DataFrame | None = None,
                  forma: pd.DataFrame | None = None) -> pd.DataFrame:
    """Panel por minuto de UN partido: una fila por (periodo, minuto, equipo) con las SUMAS.

    voronoi: métricas por evento de ojo.lentes.voronoi.por_evento (columna control).
    forma: salida de ojo.lentes.forma.por_frame. Ambas son opcionales (sin 360 quedan en 0).
    Agrega lado (propio/rival) y estado del equipo de referencia al empezar el minuto.
    """
    ev = eventos[eventos["periodo"] != contexto.PERIODO_PENALES].sort_values("indice")
    claves = ["match_id", "periodo", "minuto", "equipo_id"]
    base = pd.concat([ev[claves], _banderas(ev)], axis=1).groupby(claves).sum()

    inicios = ev.drop_duplicates("posesion")
    contra = inicios[inicios["patron"] == CONTRAGOLPE]
    base["contragolpes"] = (contra.groupby(["match_id", "periodo", "minuto", "posesion_equipo_id"]).size()
                            .rename_axis(claves).reindex(base.index, fill_value=0))

    if voronoi is not None and not voronoi.empty:
        lim = params()["presion"]["campo_rival_min_x"]
        v = ev[["id", *claves, "x"]].merge(voronoi[["id", "control"]], on="id")
        v = v[(v["x"] >= lim) & v["control"].notna()]
        g = v.groupby(claves)["control"].agg(["sum", "size"])
        base["control_campo_rival_suma"] = g["sum"].reindex(base.index, fill_value=0.0)
        base["control_campo_rival_n"] = g["size"].reindex(base.index, fill_value=0)
    if forma is not None and not forma.empty:
        f = forma.merge(ev[["id", "periodo", "minuto"]], on="id")
        for fase, con_balon in FASES.items():
            sub = f[f["con_balon"] == con_balon]
            g = sub.groupby(claves)
            base[f"forma_{fase}_n"] = g.size().reindex(base.index, fill_value=0)
            for m in lente_forma.METRICAS:
                base[f"{m}_{fase}_suma"] = g[m].sum().reindex(base.index, fill_value=0.0)
    for col in SUMAS:
        if col not in base:
            base[col] = 0.0

    tabla = base[list(SUMAS)].reset_index()
    tabla["lado"] = np.where(tabla["equipo_id"] == equipo_id, PROPIO, RIVAL)
    estado = contexto.marcador(ev, equipo_id)["estado"]
    por_minuto = ev.assign(estado=estado).drop_duplicates(["periodo", "minuto"])[["periodo", "minuto", "estado"]]
    return tabla.merge(por_minuto, on=["periodo", "minuto"], how="left")


def expandir(ventanas: pd.DataFrame, clave: str = "ventana_id") -> pd.DataFrame:
    """Una fila por minuto de cada ventana (columnas clave, match_id, periodo, desde, hasta)."""
    ventanas = ventanas.reset_index(drop=True)
    n = (ventanas["hasta"] - ventanas["desde"] + 1).clip(lower=0).astype(int)
    filas = ventanas.loc[ventanas.index.repeat(n), [clave, "match_id", "periodo", "desde"]]
    filas["minuto"] = filas["desde"] + filas.groupby(level=0).cumcount()
    return filas.drop(columns="desde").reset_index(drop=True)


def sumar(panel: pd.DataFrame, minutos: pd.DataFrame, clave: str) -> pd.DataFrame:
    """Suma el panel en los minutos de cada clave; agrega n_min (minutos de la ventana)."""
    n_min = minutos.groupby(clave).size().rename("n_min")
    unidos = minutos.merge(panel, on=CLAVES_MINUTO)
    sumas = unidos.groupby([clave, "lado"])[list(SUMAS)].sum()
    completo = pd.MultiIndex.from_product([n_min.index, [PROPIO, RIVAL]], names=[clave, "lado"])
    return sumas.reindex(completo, fill_value=0.0).join(n_min, on=clave).reset_index()


def _cociente(numerador: pd.Series, denominador: pd.Series) -> pd.Series:
    return numerador / denominador.where(denominador > 0)


def metricas(sumas: pd.DataFrame, clave: str, centralidad: pd.DataFrame | None = None) -> pd.DataFrame:
    """Métricas por bloque de cada (clave, lado) a partir de las sumas; tasas por minuto.

    centralidad: salida de ventanas_red (clave, lado, centralizacion); sin ella queda NaN.
    """
    s = sumas.set_index([clave, "lado"])
    otro = s.rename(index={PROPIO: RIVAL, RIVAL: PROPIO}, level="lado").reindex(s.index)
    n = s["n_min"]
    tabla = pd.DataFrame(index=s.index)
    tabla["control_campo_rival"] = _cociente(s["control_campo_rival_suma"], s["control_campo_rival_n"])
    tabla["altura_sin_balon"] = _cociente(s["altura_sin_suma"], s["forma_sin_n"])
    tabla["largo_sin_balon"] = _cociente(s["largo_sin_suma"], s["forma_sin_n"])
    tabla["ancho_con_balon"] = _cociente(s["ancho_con_suma"], s["forma_con_n"])
    tabla["compactacion_sin_balon"] = _cociente(s["compactacion_sin_suma"], s["forma_sin_n"])
    tabla["centralizacion"] = np.nan
    for col in ("presiones", "faltas", "contrapresiones", "xg", "obv", "presiones_campo_rival"):
        tabla[col] = _cociente(s[col], n)
    tabla["field_tilt"] = _cociente(s["pases_ultimo_tercio"], s["pases_ultimo_tercio"] + otro["pases_ultimo_tercio"])
    tabla["tiros_transicion_contra"] = _cociente(otro["tiros_transicion"], n)
    tabla["contragolpes_contra"] = _cociente(otro["contragolpes"], n)
    tabla["n_min"] = n
    tabla = tabla.reset_index()
    if centralidad is not None and not centralidad.empty:
        tabla = tabla.drop(columns="centralizacion").merge(
            centralidad[[clave, "lado", "centralizacion"]], on=[clave, "lado"], how="left")
    return tabla


def ventanas_red(aristas: pd.DataFrame, minutos: pd.DataFrame, clave: str, min_pases: int | None = None) -> pd.DataFrame:
    """Centralización de la red de cada (clave, lado); NaN si hay menos de min_pases pases.

    aristas: salida de redes.aristas_por_minuto con la columna lado agregada.
    """
    min_pases = min_pases or params()["red_pases"]["min_pases_ventana"]
    unidos = minutos.merge(aristas, on=CLAVES_MINUTO)
    if unidos.empty:
        return pd.DataFrame(columns=[clave, "lado", "centralizacion", "pases"])
    agregadas = unidos.groupby([clave, "lado", "origen", "destino"])["pases"].sum().reset_index()
    tabla = redes.centralizacion(agregadas, por=[clave, "lado"])
    tabla.loc[tabla["pases"] < min_pases, "centralizacion"] = np.nan
    return tabla


def medir(panel: pd.DataFrame, aristas: pd.DataFrame, ventanas: pd.DataFrame, clave: str = "ventana_id",
          lote: int = 5000) -> pd.DataFrame:
    """Atajo: métricas de cada ventana (clave, match_id, periodo, desde, hasta) a dos bandas.

    PERF1: la red se arma por lotes de ventanas; unir todas las aristas con todos los minutos de
    decenas de miles de ventanas a la vez no cabe cómodo en memoria.
    """
    minutos = expandir(ventanas, clave)
    ids = ventanas[clave].unique()
    redes_lote = [ventanas_red(aristas, minutos[minutos[clave].isin(ids[i:i + lote])], clave)
                  for i in range(0, len(ids), lote)]
    return metricas(sumar(panel, minutos, clave), clave, pd.concat(redes_lote, ignore_index=True))


def cargar_panel(nombre: str = "minuto") -> pd.DataFrame:
    """Une las tablas por partido de una salida de scripts/05_panel.py (minuto, aristas o forma)."""
    if nombre not in SALIDAS:
        raise ValueError(f"Salida desconocida: {nombre}. Opciones: {', '.join(SALIDAS)}")
    archivos = sorted((DIR_PANEL / nombre).glob("*.parquet"))
    if not archivos:
        raise FileNotFoundError(f"No hay {nombre} en {DIR_PANEL}. Corre scripts/05_panel.py.")
    return pd.concat([pd.read_parquet(a) for a in archivos], ignore_index=True)
