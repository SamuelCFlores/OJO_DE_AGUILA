"""Contrato de resumenes.json (el archivo de datos del explorador del reporte) y su validador.

REF1: contexto/resumenes.md (estructura campo por campo y reglas).
IMPOR1: el archivo solo lleva agregados; ningún evento ni frame (regla no negociable 1).
"""

from __future__ import annotations

from typing import Any

VERSION_ESQUEMA = 1
TODOS = "todos"
TODAS = "todas"

# Situaciones del explorador, versión 1 (definiciones en contexto/framework.md)
SITUACIONES: tuple[dict[str, str], ...] = (
    {"id": "todas", "etiqueta": "Todo el partido", "grupo": "todas"},
    {"id": "salida", "etiqueta": "Salida de balón", "grupo": "fase"},
    {"id": "presion_alta", "etiqueta": "Presión alta", "grupo": "fase"},
    {"id": "transicion_defensiva", "etiqueta": "Transición defensiva", "grupo": "fase"},
    {"id": "transicion_ofensiva", "etiqueta": "Transición ofensiva", "grupo": "fase"},
    {"id": "gana", "etiqueta": "Ganando", "grupo": "marcador"},
    {"id": "empata", "etiqueta": "Empatando", "grupo": "marcador"},
    {"id": "pierde", "etiqueta": "Perdiendo", "grupo": "marcador"},
    {"id": "balon_parado_favor", "etiqueta": "Balón parado a favor", "grupo": "balon_parado"},
    {"id": "balon_parado_contra", "etiqueta": "Balón parado en contra", "grupo": "balon_parado"},
)
IDS_SITUACION = frozenset(s["id"] for s in SITUACIONES)

METRICAS = ("control", "frontera", "apoyos", "rivales_cerca", "distancia_companeros", "ppda",
            "field_tilt", "altura_recuperacion", "xg_favor_90", "xg_contra_90")
PROPORCIONES = frozenset({"control", "field_tilt"})
BANDAS = ("america", "rival", "liga")
SECCIONES = ("meta", "catalogos", "combinaciones", "fichas", "entrenadores", "caso_por_defecto")
TOLERANCIA_SUMA = 0.02  # progresa_por debe sumar 1 salvo redondeo


def _es_proporcion(v: Any) -> bool:
    return v is None or (isinstance(v, (int, float)) and 0 <= v <= 1)


def _validar_mapa(nombre: str, mapa: Any, filas: int, columnas: int, proporcion: bool) -> list[str]:
    if mapa is None:
        return []
    if not (isinstance(mapa, list) and len(mapa) == filas and all(isinstance(f, list) and len(f) == columnas for f in mapa)):
        return [f"{nombre}: debe ser una matriz de {filas} × {columnas}"]
    if proporcion and not all(_es_proporcion(v) for f in mapa for v in f):
        return [f"{nombre}: valores fuera de [0, 1]"]
    return []


def validar(resumen: dict) -> list[str]:
    """Lista de incumplimientos del contrato; vacía si el archivo es válido."""
    errores = [f"falta la sección {s}" for s in SECCIONES if s not in resumen]
    if errores:
        return errores
    meta, catalogos = resumen["meta"], resumen["catalogos"]
    if meta.get("version_esquema") != VERSION_ESQUEMA:
        errores.append(f"meta.version_esquema debe ser {VERSION_ESQUEMA}")
    rejilla = meta.get("rejilla") or {}
    filas, columnas = rejilla.get("filas"), rejilla.get("columnas")
    if not (isinstance(filas, int) and isinstance(columnas, int)):
        return errores + ["meta.rejilla debe traer filas y columnas enteras"]
    min_partidos = meta.get("min_partidos")

    rivales = {r["id"] for r in catalogos.get("rivales", [])}
    torneos = {t["id"] for t in catalogos.get("torneos", [])}
    situaciones = {s["id"] for s in catalogos.get("situaciones", [])}
    if any(not isinstance(r, str) for r in rivales):
        errores.append("catalogos.rivales: los ids van como texto")
    if desconocidas := situaciones - IDS_SITUACION:
        errores.append(f"catalogos.situaciones desconocidas: {sorted(desconocidas)}")
    n_rivales = [r.get("n_partidos", 0) for r in catalogos.get("rivales", [])]
    if n_rivales != sorted(n_rivales, reverse=True):
        errores.append("catalogos.rivales debe ir de más a menos partidos")

    for clave, c in resumen["combinaciones"].items():
        partes = clave.split("|")
        if len(partes) != 3:
            errores.append(f"{clave}: la clave debe ser rival|torneo|situacion")
            continue
        rival, torneo, situacion = partes
        if rival not in rivales | {TODOS} or torneo not in torneos | {TODOS} or situacion not in situaciones | {TODAS}:
            errores.append(f"{clave}: rival, torneo o situación fuera de los catálogos")
        n = c.get("n_partidos")
        if not isinstance(n, int) or n < 1:
            errores.append(f"{clave}: n_partidos debe ser un entero ≥ 1")
            continue
        suficiente = n >= min_partidos
        if c.get("muestra_suficiente") is not suficiente:
            errores.append(f"{clave}: muestra_suficiente no coincide con n_partidos y min_partidos")
        for banda in BANDAS:
            valores = (c.get("metricas") or {}).get(banda) or {}
            for m, v in valores.items():
                if m not in METRICAS:
                    errores.append(f"{clave}: métrica desconocida {banda}.{m}")
                elif not suficiente and banda != "liga" and v is not None:
                    errores.append(f"{clave}: con muestra insuficiente {banda}.{m} debe ser null")
                elif m in PROPORCIONES and not _es_proporcion(v):
                    errores.append(f"{clave}: {banda}.{m} fuera de [0, 1]")
        errores += _validar_mapa(f"{clave}.mapa_control", c.get("mapa_control"), filas, columnas, proporcion=True)
        errores += _validar_mapa(f"{clave}.mapa_cobertura", c.get("mapa_cobertura"), filas, columnas, proporcion=False)
        if not isinstance(c.get("frase"), str) or not c["frase"]:
            errores.append(f"{clave}: falta la frase")

    for rival, ficha in resumen["fichas"].items():
        if rival not in rivales:
            errores.append(f"fichas.{rival}: rival fuera del catálogo")
        reparto = ficha.get("progresa_por")
        if reparto and abs(sum(reparto.values()) - 1) > TOLERANCIA_SUMA:
            errores.append(f"fichas.{rival}.progresa_por debe sumar 1")
        errores += _validar_mapa(f"fichas.{rival}.concede_en", ficha.get("concede_en"), 3, 6, proporcion=False)

    defecto = resumen["caso_por_defecto"]
    clave_defecto = f"{defecto.get('rival')}|{defecto.get('torneo')}|{defecto.get('situacion')}"
    if clave_defecto not in resumen["combinaciones"]:
        errores.append(f"caso_por_defecto apunta a una combinación que no existe: {clave_defecto}")
    return errores
