"""Prueba de humo de las APIs de StatsBomb.

Comprueba credenciales y estructura de las respuestas, y encuentra los ids que
necesita config/params.yaml. Imprime solo conteos, nombres de campos y
catálogos (temporadas, equipos, entrenadores); nunca filas de datos.

Cómo correrlo (PowerShell, desde la raíz del repo y con el entorno activado):
    python scripts/00_prueba_humo.py
Opcional, para fijar el partido de prueba:
    python scripts/00_prueba_humo.py --match-id 123456

Hace unas 15 solicitudes la primera vez (~20 s). Una segunda ejecución sale
completa de la caché (data/raw/) y no toca la API. Registro en logs/prueba_humo.log.
"""

from __future__ import annotations

import argparse
import logging
import sys
import unicodedata
from collections import Counter
from typing import Any

from ojo.config import DIR_LOGS
from ojo.ingesta.cliente import ClienteStatsBomb, ErrorAPI, ErrorAutenticacion

# Texto para encontrar el caso en los catálogos; los ids salen de aquí hacia params.yaml
BUSCAR_LIGA = "liga mx"
BUSCAR_EQUIPO = "america"
BUSCAR_ENTRENADOR = "jardine"

avisos: list[str] = []


def normalizar(texto: Any) -> str:
    """Minúsculas y sin acentos, para comparar nombres."""
    sin_acentos = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode()
    return sin_acentos.lower()


def avisar(mensaje: str) -> None:
    """Registra una diferencia con la documentación para el resumen final (una vez)."""
    if mensaje in avisos:
        return
    avisos.append(mensaje)
    print(f"  ⚠ {mensaje}")


def titulo(texto: str) -> None:
    print(f"\n=== {texto} ===")


def equipo_de(partido: dict, lado: str) -> tuple[Any, str]:
    """Id y nombre del equipo local/visitante según Matches v6 (con respaldo si difiere)."""
    equipo = partido.get(f"{lado}_team") or {}
    if "id" in equipo:
        return equipo["id"], equipo.get("name", "")
    if f"{lado}_team_id" in equipo:
        avisar(f"Matches: {lado}_team usa {lado}_team_id/{lado}_team_name, no id/name")
        return equipo[f"{lado}_team_id"], equipo.get(f"{lado}_team_name", "")
    raise ErrorAPI(f"Matches: no encuentro el id de {lado}_team; campos: {sorted(equipo)}")


def entrenadores_de(partido: dict, lado: str) -> list[dict]:
    """Entrenador(es) de un lado; la documentación dice objeto o lista en {lado}_team_manager."""
    valor = partido.get(f"{lado}_team_manager")
    if valor is None:
        valor = (partido.get(f"{lado}_team") or {}).get("managers")
        if valor is not None:
            avisar(f"Matches: entrenador en {lado}_team.managers, no en {lado}_team_manager")
    if valor is None:
        return []
    return valor if isinstance(valor, list) else [valor]


def paso_competiciones(cliente: ClienteStatsBomb) -> list[dict]:
    titulo("1. Competitions: torneos de Liga MX")
    competiciones = cliente.obtener("competitions")
    print(f"  Combinaciones competición-temporada con licencia: {len(competiciones)}")
    print(f"  Campos: {sorted(competiciones[0]) if competiciones else '—'}")
    liga = [c for c in competiciones if BUSCAR_LIGA in normalizar(c.get("competition_name"))]
    if not liga:
        nombres = sorted({c.get("competition_name") for c in competiciones})
        raise ErrorAPI(f"No encuentro '{BUSCAR_LIGA}'. Competiciones disponibles: {nombres}")
    print(f"  {'competition_id':>14} {'season_id':>9}  season_name")
    for c in sorted(liga, key=lambda c: str(c.get("season_name"))):
        print(f"  {c['competition_id']:>14} {c['season_id']:>9}  {c.get('season_name')}")
    return liga


def paso_partidos(cliente: ClienteStatsBomb, liga: list[dict]) -> list[dict]:
    titulo("2. Matches: partidos por temporada (¿season_id = torneo o año?)")
    todos: list[dict] = []
    print(f"  {'season':<12} {'partidos':>8} {'Complete':>8} {'360 disp.':>9}  fechas")
    for c in sorted(liga, key=lambda c: str(c.get("season_name"))):
        partidos = cliente.obtener("matches", competition_id=c["competition_id"], season_id=c["season_id"])
        fechas = sorted(p.get("match_date", "") for p in partidos)
        completos = sum(p.get("collection_status") == "Complete" for p in partidos)
        con_360 = sum(p.get("match_status_360") == "available" for p in partidos)
        rango = f"{fechas[0]} → {fechas[-1]}" if fechas else "—"
        print(f"  {str(c.get('season_name')):<12} {len(partidos):>8} {completos:>8} {con_360:>9}  {rango}")
        todos.extend(partidos)
    if todos:
        print(f"  Campos de Matches: {sorted(todos[0])}")
        etapas = Counter((p.get("competition_stage") or {}).get("name") for p in todos)
        print(f"  Fases del torneo (competition_stage): {dict(etapas)}")
    print("  Pista: un torneo de Liga MX tiene ~153 partidos de fase regular más liguilla;")
    print("  si una temporada trae ~300 o más, junta Apertura y Clausura.")
    return todos


def paso_equipo_y_entrenadores(partidos: list[dict]) -> tuple[Any, list[dict]]:
    titulo("3. Equipo y entrenadores")
    equipos: dict[Any, str] = {}
    for p in partidos:
        for lado in ("home", "away"):
            id_equipo, nombre = equipo_de(p, lado)
            equipos[id_equipo] = nombre
    candidatos = {i: n for i, n in equipos.items() if BUSCAR_EQUIPO in normalizar(n)}
    print(f"  Equipos que coinciden con '{BUSCAR_EQUIPO}': {candidatos}")
    if len(candidatos) != 1:
        raise ErrorAPI("Necesito exactamente un equipo; ajusta BUSCAR_EQUIPO en el script")
    team_id = next(iter(candidatos))

    propios = []
    resumen: dict[Any, dict] = {}
    for p in partidos:
        lado = next((l for l in ("home", "away") if equipo_de(p, l)[0] == team_id), None)
        if lado is None:
            continue
        propios.append(p)
        for e in entrenadores_de(p, lado):
            r = resumen.setdefault(e.get("id"), {"nombre": e.get("name"), "partidos": 0, "fechas": []})
            r["partidos"] += 1
            r["fechas"].append(p.get("match_date", ""))
    print(f"  Partidos del equipo en la ventana: {len(propios)}")
    print(f"  {'manager_id':>10} {'partidos':>8}  {'desde':<10}  {'hasta':<10}  nombre")
    for id_entrenador, r in sorted(resumen.items(), key=lambda x: min(x[1]["fechas"])):
        print(f"  {str(id_entrenador):>10} {r['partidos']:>8}  {min(r['fechas']):<10}  "
              f"{max(r['fechas']):<10}  {r['nombre']}")
    return team_id, propios


def elegir_partido(partidos_equipo: list[dict], team_id: Any) -> dict:
    """El partido más reciente de Jardine con eventos completos y 360 disponible."""
    def es_de_jardine(p: dict) -> bool:
        lado = "home" if equipo_de(p, "home")[0] == team_id else "away"
        return any(BUSCAR_ENTRENADOR in normalizar(e.get("name")) for e in entrenadores_de(p, lado))

    validos = [
        p for p in partidos_equipo
        if es_de_jardine(p)
        and p.get("collection_status") == "Complete"
        and p.get("match_status") == "available"
        and p.get("match_status_360") == "available"
    ]
    if not validos:
        raise ErrorAPI("No hay partidos de Jardine con eventos completos y 360; usa --match-id")
    return max(validos, key=lambda p: p.get("match_date", ""))


def porcentaje(parte: int, total: int) -> str:
    return f"{100 * parte / total:.1f} %" if total else "—"


def paso_detalle_partido(cliente: ClienteStatsBomb, match_id: int) -> None:
    titulo(f"4. Detalle de un partido (match_id {match_id})")

    eventos = cliente.obtener("events", match_id=match_id)
    print(f"  Events v11: {len(eventos)} eventos")
    tipos = Counter((e.get("type") or {}).get("name") for e in eventos)
    print(f"    Tipos más frecuentes: {dict(tipos.most_common(6))}")
    campos = Counter(k for e in eventos for k in e)
    print(f"    Campos de nivel superior: {sorted(campos)}")
    con_control = sum("control_degree" in e for e in eventos)
    print(f"    Phases of Play (control_degree presente): {porcentaje(con_control, len(eventos))} de eventos")
    for campo in ("is_transition", "possession_directness", "location_bucket", "obv_total_net"):
        if campo not in campos:
            avisar(f"Events: no aparece {campo}")
    pases = [e.get("pass") or {} for e in eventos if (e.get("type") or {}).get("name") == "Pass"]
    tiros = [e.get("shot") or {} for e in eventos if (e.get("type") or {}).get("name") == "Shot"]
    print(f"    Pases con pass_cluster_id: {porcentaje(sum('pass_cluster_id' in p for p in pases), len(pases))}")
    print(f"    Pases con pass_success_probability: "
          f"{porcentaje(sum('pass_success_probability' in p for p in pases), len(pases))}")
    print(f"    Tiros con statsbomb_xg: {porcentaje(sum('statsbomb_xg' in t for t in tiros), len(tiros))}")

    frames = cliente.obtener("frames_360", match_id=match_id)
    ids_eventos = {e.get("id") for e in eventos}
    unidos = sum(f.get("event_uuid") in ids_eventos for f in frames)
    con_area = sum(bool(f.get("visible_area")) for f in frames)
    print(f"  360 Frames v2: {len(frames)} frames")
    print(f"    Campos: {sorted({k for f in frames for k in f})}")
    print(f"    Eventos con frame: {porcentaje(unidos, len(eventos))}; frames con visible_area: "
          f"{porcentaje(con_area, len(frames))}")
    if frames:
        jugadores = sum(len(f.get("freeze_frame") or []) for f in frames) / len(frames)
        print(f"    Jugadores visibles por frame (promedio): {jugadores:.1f}")

    alineaciones = cliente.obtener("lineups", match_id=match_id)
    print(f"  Lineups v5: {len(alineaciones)} equipos")
    for equipo in alineaciones:
        formaciones = [f.get("formation") for f in equipo.get("formations") or []]
        print(f"    {len(equipo.get('lineup') or [])} jugadores en la hoja, formaciones: {formaciones}")
    if alineaciones:
        print(f"    Campos: {sorted(alineaciones[0])}")

    for api, prefijo, esperados in (
        ("team_match_stats", "team_match_", ["team_match_ppda", "team_match_time_in_transition"]),
        ("player_match_stats", "player_match_", ["player_match_360_minutes", "player_match_fhalf_lbp_received"]),
    ):
        filas = cliente.obtener(api, match_id=match_id)
        columnas = {k for f in filas for k in f}
        print(f"  {api}: {len(filas)} filas, {len(columnas)} campos "
              f"({sum(c.startswith(prefijo) for c in columnas)} con prefijo {prefijo})")
        for campo in esperados:
            if campo not in columnas:
                avisar(f"{api}: no aparece {campo}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--match-id", type=int, help="partido para el paso 4 (por defecto, uno de Jardine)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # consola de Windows: acentos y símbolos

    DIR_LOGS.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(DIR_LOGS / "prueba_humo.log", encoding="utf-8")],
    )

    try:
        cliente = ClienteStatsBomb.desde_entorno()
        liga = paso_competiciones(cliente)
        partidos = paso_partidos(cliente, liga)
        team_id, propios = paso_equipo_y_entrenadores(partidos)
        match_id = args.match_id or elegir_partido(propios, team_id)["match_id"]
        paso_detalle_partido(cliente, match_id)
    except (ErrorAutenticacion, ErrorAPI) as error:
        print(f"\n✗ {error}")
        print("  Detalle en logs/prueba_humo.log")
        return 1

    titulo("Resumen")
    print("  ✓ Las 5 APIs del partido respondieron.")
    print(f"  Diferencias con la documentación: {len(avisos)}")
    for aviso in avisos:
        print(f"    - {aviso}")
    print("  Copia esta salida completa y pégasela a Claude (no contiene filas de datos).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
