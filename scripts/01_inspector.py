"""Inspector de contenido: revisa una muestra de partidos antes de la descarga completa.

Responde, con conteos y porcentajes (nunca filas de datos):
    - ¿Phases of Play (control_degree) viene poblado en cada temporada?
    - ¿Cuánta cobertura tiene el 360 (eventos con frame, área visible, jugadores visibles)?
    - ¿Vienen OBV, xG, pass_cluster_id y pass_success_probability?
    - ¿Qué formaciones y motivos de cambio trae Lineups?
    - ¿Las coordenadas vienen en la perspectiva de quien ejecuta (supuesto del framework)?
    - ¿Cuánto pesa un partido, para estimar el total de la descarga?
Escribe reports/inspeccion_api.md (sin datos crudos: se puede versionar).

Muestra: --por-temporada partidos del equipo de params.yaml en cada temporada (por defecto 2,
repartidos en el tiempo), con 360 disponible. Descarga sus 5 APIs por el cliente con caché
(unas 5 solicitudes por partido; quedan en caché para la descarga completa).

Cómo correrlo (PowerShell, desde la raíz del repo y con el entorno activado):
    python scripts/01_inspector.py
    python scripts/01_inspector.py --por-temporada 4
"""

from __future__ import annotations

import argparse
import logging
import statistics
import sys
from collections import Counter
from datetime import date

import pandas as pd

from ojo.config import DIR_LOGS, DIR_REPORTES, params
from ojo.datos import crudo, tablas
from ojo.framework import juego
from ojo.framework import partidos as fp
from ojo.ingesta.cliente import ClienteStatsBomb, ErrorAPI, ErrorAutenticacion

APIS_PARTIDO = ("events", "frames_360", "lineups", "team_match_stats", "player_match_stats")
UMBRAL_ORIENTACION_X = 60  # un tiro en perspectiva del actor está en la mitad rival (x > 60)


def pct(parte: float, total: float) -> str:
    return f"{100 * parte / total:.1f} %" if total else "—"


def elegir_muestra(liga: pd.DataFrame, team_id: int, por_temporada: int) -> pd.DataFrame:
    """Partidos del equipo con 360, repartidos a lo largo de cada temporada."""
    del_equipo = fp.validos(fp.del_equipo(liga, team_id), con_360=True)
    elegidos = []
    for _, grupo in del_equipo.groupby("season_id"):
        grupo = grupo.sort_values("fecha").reset_index(drop=True)
        posiciones = sorted({round(i * (len(grupo) - 1) / max(por_temporada - 1, 1)) for i in range(por_temporada)})
        elegidos.append(grupo.iloc[posiciones])
    return fp.con_torneo(pd.concat(elegidos, ignore_index=True))


def tabla_md(filas: list[dict]) -> str:
    """Convierte una lista de diccionarios en una tabla Markdown."""
    if not filas:
        return "_(sin filas)_\n"
    columnas = list(filas[0])
    lineas = ["| " + " | ".join(columnas) + " |", "| " + " | ".join("---" for _ in columnas) + " |"]
    lineas += ["| " + " | ".join(str(f[c]) for c in columnas) + " |" for f in filas]
    return "\n".join(lineas) + "\n"


def inspeccionar_partido(match_id: int) -> dict:
    """Métricas de presencia de un partido (solo conteos)."""
    ev_crudo = crudo.leer("events", match_id=match_id)
    ev = tablas.eventos(ev_crudo, match_id)
    abierto = juego.es_juego_abierto(ev)
    pases = ev[ev["tipo"] == "Pass"]
    tiros = ev[ev["tipo"] == "Shot"]
    frames, jugadores = tablas.frames_360(crudo.leer("frames_360", match_id=match_id), match_id)
    con_frame = ev["id"].isin(set(frames["event_uuid"]))
    x_tiros = tiros.groupby("equipo_id")["x"].mean()
    tamanos = {api: crudo.ruta(api, match_id=match_id).stat().st_size for api in APIS_PARTIDO}
    return {
        "eventos": len(ev),
        "campos_evento": Counter(k for e in ev_crudo for k in e),
        "abiertos": int(abierto.sum()),
        "abiertos_con_control": int((abierto & ev["control_degree"].notna()).sum()),
        "abiertos_con_transicion": int((abierto & ev["es_transicion"].notna()).sum()),
        "con_obv": int(ev["obv_total_net"].notna().sum()),
        "pases": len(pases),
        "pases_cluster": int(pases["pase_cluster_id"].notna().sum()),
        "pases_prob": int(pases["pase_prob_exito"].notna().sum()),
        "tiros": len(tiros),
        "tiros_xg": int(tiros["tiro_xg"].notna().sum()),
        "con_frame": int(con_frame.sum()),
        "frames": len(frames),
        "frames_area": int((frames["area_visible"].str.len() >= 6).sum()) if len(frames) else 0,
        "visibles_prom": frames["n_visibles"].mean() if len(frames) else float("nan"),
        "orientacion_ok": bool(len(x_tiros) and (x_tiros > UMBRAL_ORIENTACION_X).all()),
        "formaciones": tablas.formaciones(crudo.leer("lineups", match_id=match_id), match_id),
        "tms_campos": len(tablas.estadisticas_equipo(crudo.leer("team_match_stats", match_id=match_id)).columns),
        "tamanos": tamanos,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--por-temporada", type=int, default=2, help="partidos por temporada (por defecto 2)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    DIR_LOGS.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                        handlers=[logging.FileHandler(DIR_LOGS / "inspector.log", encoding="utf-8")])

    p = params()
    competition_id, season_ids, team_id = p["liga"]["competition_id"], p["liga"]["season_ids"], p["equipo"]["team_id"]
    try:
        cliente = ClienteStatsBomb.desde_entorno()
        liga = fp.validos(pd.concat(
            [tablas.partidos(cliente.obtener("matches", competition_id=competition_id, season_id=s)) for s in season_ids],
            ignore_index=True,
        ))
        muestra = elegir_muestra(liga, team_id, args.por_temporada)
        print(f"Muestra: {len(muestra)} partidos del equipo {team_id}. Descargando lo que falte...")
        for match_id in muestra["match_id"]:
            for api in APIS_PARTIDO:
                cliente.obtener(api, match_id=int(match_id))
    except (ErrorAutenticacion, ErrorAPI) as error:
        print(f"✗ {error}\n  Detalle en logs/inspector.log")
        return 1

    resultados = {int(m): inspeccionar_partido(int(m)) for m in muestra["match_id"]}
    muestra = muestra.assign(r=muestra["match_id"].map(resultados))

    por_torneo = []
    for torneo_corto, grupo in muestra.groupby("torneo_corto", sort=False):
        r = list(grupo["r"])
        s = lambda k: sum(x[k] for x in r)  # noqa: E731
        por_torneo.append({
            "Torneo": torneo_corto, "Partidos": len(r),
            "Phases of Play (control_degree)": pct(s("abiertos_con_control"), s("abiertos")),
            "is_transition": pct(s("abiertos_con_transicion"), s("abiertos")),
            "OBV": pct(s("con_obv"), s("eventos")),
            "pass_cluster_id": pct(s("pases_cluster"), s("pases")),
            "pass_success_probability": pct(s("pases_prob"), s("pases")),
            "xG en tiros": pct(s("tiros_xg"), s("tiros")),
            "Eventos con frame 360": pct(s("con_frame"), s("eventos")),
            "Frames con área visible": pct(s("frames_area"), s("frames")),
            "Jugadores visibles (prom.)": f"{statistics.mean(x['visibles_prom'] for x in r):.1f}",
            "Orientación del actor": "OK" if all(x["orientacion_ok"] for x in r) else "revisar",
        })

    todos = list(resultados.values())
    total_eventos = sum(x["eventos"] for x in todos)
    campos = Counter()
    for x in todos:
        campos.update(x["campos_evento"])
    filas_campos = [{"Campo": c, "Presencia": pct(n, total_eventos)} for c, n in sorted(campos.items(), key=lambda kv: -kv[1])]
    formaciones = pd.concat([x["formaciones"] for x in todos], ignore_index=True)
    motivos = formaciones["motivo"].value_counts().to_dict()
    top_formaciones = formaciones["formacion"].value_counts().head(8).to_dict()
    tam = {api: statistics.mean(x["tamanos"][api] for x in todos) for api in APIS_PARTIDO}
    n_equipo = len(fp.del_equipo(liga, team_id))
    mb_equipo = n_equipo * sum(tam[a] for a in ("events", "frames_360", "lineups", "player_match_stats")) / 1e6
    mb_liga = len(liga) * tam["team_match_stats"] / 1e6
    mb_liga_completa = len(liga) * sum(tam[a] for a in ("events", "frames_360", "lineups")) / 1e6

    reporte = f"""# Inspección de las APIs

Generado por `scripts/01_inspector.py` el {date.today().isoformat()}. Muestra: {len(muestra)} partidos del equipo {team_id} con 360, {args.por_temporada} por temporada. Solo conteos y porcentajes; sin datos crudos.

## Cobertura por torneo

Phases of Play e `is_transition` se miden sobre eventos de juego abierto; las demás, sobre todos los eventos, pases o tiros.

{tabla_md(por_torneo)}
## Campos de nivel superior en Events

Presencia sobre {total_eventos:,} eventos. Un campo ausente o muy bajo que el framework use debe revisarse (regla 5).

{tabla_md(filas_campos)}
## Lineups

- Motivos de cambio de formación: {motivos}
- Formaciones más frecuentes: {top_formaciones}

## Team Match Stats

Campos por fila: {statistics.mean(x['tms_campos'] for x in todos):.0f}.

## Tamaño y estimación de la descarga

| API | KB por partido (gzip) |
| --- | --- |
""" + "".join(f"| {api} | {tam[api] / 1e3:.0f} |\n" for api in APIS_PARTIDO) + f"""
- Partidos válidos de la liga: {len(liga):,}; del equipo: {n_equipo}.
- Descarga de `scripts/02_descarga.py` (niveles 1-4): ~{mb_equipo + mb_liga:.0f} MB.
- Con `--liga-completa` (nivel 5): ~{mb_liga_completa:.0f} MB más.
"""
    DIR_REPORTES.mkdir(exist_ok=True)
    salida = DIR_REPORTES / "inspeccion_api.md"
    salida.write_text(reporte, encoding="utf-8")
    print(tabla_md(por_torneo))
    print(f"Reporte completo: {salida.relative_to(DIR_REPORTES.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
