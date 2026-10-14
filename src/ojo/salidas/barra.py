"""Barra lateral de la app: textos de partidos y etapas, y el estado de la barra para un partido.

La usan las maquetas (scripts/07_caso.py y 08_maqueta.py); el contrato v2 de resumenes.json la
llenará después para cualquier combinación (contexto/barra_lateral.md, versión 2).
"""

from __future__ import annotations

import pandas as pd

from ojo.config import params
from ojo.framework import partidos as fp
from ojo.salidas.app import Barra
from ojo.salidas.resumenes import SITUACIONES

ETAPAS = {"Semi-finals": "Semifinal", "Quarter-finals": "Cuartos de final", "Final": "Final", "Finals": "Final",
          "Play-offs": "Repechaje"}
GRUPOS_SITUACION = {"todas": "General", "fase": "Fase", "marcador": "Marcador", "balon_parado": "Balón parado"}
ESTADO_SITUACION = {"gana": "Ganando", "empata": "Empatando", "pierde": "Perdiendo"}
# Situaciones "tras un quiebre" (propuesta para el contrato de resumenes.json): una por tipo, sin separar propio/rival
# salvo en goles y expulsiones, donde importa quién lo sufre.
ETIQUETA_SITUACION = {
    "gol_favor": "Tras gol a favor", "gol_contra": "Tras gol en contra", "expulsion_favor": "Expulsión a favor",
    "expulsion_contra": "Expulsión en contra", "cambio_sistema_propio": "Cambio de sistema",
    "cambio_sistema_rival": "Cambio de sistema", "sustitucion_tactica_propia": "Cambio táctico",
    "sustitucion_tactica_rival": "Cambio táctico", "sustitucion_lesion_propia": "Cambio por lesión",
    "sustitucion_lesion_rival": "Cambio por lesión",
}
MAX_RIVALES_LISTA = 6  # rivales en la lista de la barra, además del seleccionado (presentación)


def corto(nombre: str) -> str:
    """"Fernando Ortiz" → "Ortiz"; "André Soares Jardine" → "Jardine"."""
    return str(nombre).split(" ")[-1]


def nombres_entrenadores() -> dict[int, str]:
    """Nombre corto de cada entrenador del análisis según params.yaml (StatsBomb trae el nombre completo)."""
    p = params()
    return {d["manager_id"]: corto(d["nombre"]) for d in [*p["predecesores"], p["entrenador"]]}


def condicion(localia: str) -> str:
    return {"local": "Local", "visitante": "Visita"}.get(str(localia), "Todos")


def minuscula(texto: str) -> str:
    """Primera letra en minúscula, sin tocar nombres propios."""
    return texto[:1].lower() + texto[1:]


def plural(n: int, singular: str, varios: str) -> str:
    return f"{n} {singular if n == 1 else varios}"


def etapa_legible(etapa: str | None, vuelta: bool) -> str:
    """"Clausura - Semi-finals" → "Clausura · Semifinal de vuelta"."""
    partes = [p.strip() for p in (etapa or "").split(" - ")]
    texto = " · ".join(ETAPAS.get(p, p) for p in partes if p)
    return texto + (" de vuelta" if vuelta else "")


def ida_de(partidos: pd.DataFrame, info: pd.Series) -> pd.Series | None:
    """Partido de ida de una eliminatoria: mismo rival, torneo y etapa, jugado antes."""
    if not any(k in (info["etapa"] or "") for k in ETAPAS):
        return None
    previos = partidos[(partidos["rival_id"] == info["rival_id"]) & (partidos["torneo_corto"] == info["torneo_corto"])
                       & (partidos["etapa"] == info["etapa"]) & (partidos["fecha"] < info["fecha"])]
    return previos.iloc[-1] if not previos.empty else None


def etiqueta_partido(partidos: pd.DataFrame, fila: pd.Series) -> str:
    """"Semifinal · vuelta", "Final · ida" o "Fase regular" para la lista de partidos de la barra."""
    partes = [ETAPAS.get(x.strip(), x.strip()) for x in str(fila["etapa"] or "").split(" - ")]
    fase = next((x for x in partes if x in ETAPAS.values()), None)
    if fase is None:
        return "Fase regular"
    misma = partidos[(partidos["rival_id"] == fila["rival_id"]) & (partidos["torneo_corto"] == fila["torneo_corto"])
                     & (partidos["etapa"] == fila["etapa"])]
    if len(misma) < 2:
        return fase
    return f"{fase} · {'vuelta' if fila['fecha'] == misma['fecha'].max() else 'ida'}"


def armar(partidos: pd.DataFrame, info: pd.Series, tipo_quiebre: str | None, estado: str | None,
          resumen: list[tuple[str, str]], muestra: str) -> Barra:
    """Barra con el estado de un partido: rival, entrenador, torneo, partido, situación y condición."""
    ids = nombres_entrenadores()
    conteo = partidos.groupby("rival").size().sort_values(ascending=False)
    rivales = [(r, int(n)) for r, n in conteo.items() if r != info["rival"]][:MAX_RIVALES_LISTA]
    torneos = partidos.sort_values("fecha").drop_duplicates("torneo_corto")
    lista_torneos = [(t, t == info["torneo_corto"], bool(pr)) for t, pr in zip(torneos["torneo_corto"], fp.es_prueba(torneos))]
    del_rival = partidos[(partidos["rival_id"] == info["rival_id"]) & (partidos["torneo_corto"] == info["torneo_corto"])]
    lista_partidos = [(pd.Timestamp(r.fecha).strftime("%d/%m"), etiqueta_partido(partidos, pd.Series(r._asdict())),
                       f"{int(r.goles_favor)}-{int(r.goles_contra)}", r.match_id == info["match_id"])
                      for r in del_rival.sort_values("fecha").itertuples()]
    activa, estado_txt = ETIQUETA_SITUACION.get(tipo_quiebre or ""), ESTADO_SITUACION.get(estado or "")
    grupos: dict[str, list[tuple[str, bool]]] = {}
    for s in SITUACIONES:
        grupos.setdefault(GRUPOS_SITUACION.get(s["grupo"], s["grupo"]), []).append((s["etiqueta"], s["etiqueta"] == estado_txt))
    grupos["Tras un quiebre"] = [(x, x == activa) for x in dict.fromkeys(ETIQUETA_SITUACION.values())]
    return Barra(rival=info["rival"], partidos_rival=int(conteo.get(info["rival"], 0)), rivales=rivales,
                 entrenadores=[(n, i == info["entrenador_id"]) for i, n in ids.items()], torneos=lista_torneos,
                 partidos=lista_partidos, situaciones=list(grupos.items()), condicion=condicion(info["localia"]),
                 muestra=muestra, resumen=resumen)


# Barra compacta (14 oct): lo esencial a la vista y lo secundario en "Más filtros" (contexto/barra_lateral.md, versión 3).
MOMENTOS = {  # tipo de quiebre → opción de "Tras un quiebre" (propio y rival se juntan salvo en goles y expulsiones)
    "gol_favor": "Gol a favor", "gol_contra": "Gol en contra", "expulsion_favor": "Uno más", "expulsion_contra": "Uno menos",
    "cambio_sistema_propio": "Cambio propio", "sustitucion_tactica_propia": "Cambio propio",
    "cambio_sistema_rival": "Cambio rival", "sustitucion_tactica_rival": "Cambio rival",
}


def compacta(partidos: pd.DataFrame, info: pd.Series, tipo_quiebre: str | None, estado: str | None, muestra: str) -> dict:
    """Barra compacta lista para JSON: rival, torneo, momento, condición y partidos; entrenador, fase y balón parado en "más"."""
    b = armar(partidos, info, tipo_quiebre, estado, [], muestra)
    activo = MOMENTOS.get(tipo_quiebre or "")
    estado_txt = ESTADO_SITUACION.get(estado or "")
    opciones = lambda pares: [{"etq": e, "activo": bool(a)} for e, a in pares]  # noqa: E731
    por_grupo = {s["grupo"]: [] for s in SITUACIONES}
    for s in SITUACIONES:
        por_grupo[s["grupo"]].append((s["etiqueta"], False))
    return {
        "rival": {"nombre": b.rival, "partidos": b.partidos_rival},
        "rivales": [[n, k] for n, k in b.rivales],
        "torneos": [{"id": t, "activo": bool(a), "prueba": bool(p)} for t, a, p in b.torneos],
        "momento": [
            {"grupo": "Marcador", "opciones": opciones((e, e == estado_txt) for e in ESTADO_SITUACION.values())},
            {"grupo": "Tras un quiebre", "opciones": opciones((e, e == activo) for e in dict.fromkeys(MOMENTOS.values()))},
        ],
        "condicion": b.condicion,
        "partidos": [{"fecha": f, "etapa": e, "marcador": m, "activo": bool(a)} for f, e, m, a in b.partidos],
        "mas": [
            {"grupo": "Entrenador", "opciones": opciones(b.entrenadores)},
            {"grupo": "Fase", "opciones": opciones(por_grupo.get("fase", []))},
            {"grupo": "Balón parado", "opciones": opciones(por_grupo.get("balon_parado", []))},
        ],
        "muestra": muestra,
    }
