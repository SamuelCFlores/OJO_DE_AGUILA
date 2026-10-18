"""Del dato a la decisión: textos de la matriz de situaciones y de la ficha de 10 segundos.

REF1: contexto/framework.md, "Matriz de situaciones" y "Ficha de 10 segundos" (18 oct).
IMPOR1: las recomendaciones son hipótesis para el cuerpo técnico que salen de reglas fijas sobre los números
(params.yaml: matriz y ficha); nunca dicen qué "habría cambiado" una decisión.
"""

from __future__ import annotations

import pandas as pd

from ojo.config import params
from ojo.lentes import rivales

DOMINA, PAREJO, SUFRE = "domina", "parejo", "sufre"


def banda_indice(v: float) -> str:
    bajo, alto = params()["indice"]["bandas"]
    return "proactivo" if v >= alto else ("reactivo" if v <= bajo else "equilibrado")


def fila_matriz(r: pd.Series, base: pd.Series, equipo: str = "América", cfg: dict | None = None) -> dict:
    """Una fila de la matriz: situación, qué hace, qué le funciona, recomendación (hipótesis) y evidencia."""
    cfg = cfg or params()["matriz"]
    hace = [f"Índice {r['indice']:.0f} ({banda_indice(r['indice'])}); el rival, {r['indice_rival']:.0f}"]
    if r["indice"] - base["indice"] >= cfg["dif_indice"]:
        hace.append("más proactivo que su partido normal")
    elif base["indice"] - r["indice"] >= cfg["dif_indice"]:
        hace.append("se repliega frente a su partido normal")
    if pd.notna(r["ppda"]) and base["ppda"] - r["ppda"] >= cfg["dif_ppda"]:
        hace.append(f"presiona más (PPDA {r['ppda']:.1f})")
    elif pd.notna(r["ppda"]) and r["ppda"] - base["ppda"] >= cfg["dif_ppda"]:
        hace.append(f"presiona menos (PPDA {r['ppda']:.1f})")
    nivel = DOMINA if r["xg_dif_bajo"] > 0 else (SUFRE if r["xg_dif_alto"] < 0 else PAREJO)
    funciona = {DOMINA: f"Le funciona: genera más de lo que concede (xG neto {r['xg_dif_90']:+.2f} por 90)",
                SUFRE: f"Sufre: concede más de lo que genera (xG neto {r['xg_dif_90']:+.2f} por 90)",
                PAREJO: f"Parejo: el xG neto ({r['xg_dif_90']:+.2f} por 90) no se separa de cero"}[nivel]
    replegado = base["indice"] - r["indice"] >= cfg["dif_indice"]
    if nivel == DOMINA:
        rec = ("Sostener, sabiendo que cede el balón: vigilar la transición en contra." if replegado
               else "Sostener el plan: en esta situación le funciona.")
    elif nivel == SUFRE:
        rec = "Corregir: en esta situación concede más de lo que genera; proteger la pérdida."
    elif r.get("situacion") == "uno_menos" and replegado:
        rec = "Con uno menos, replegarse es lo esperado: el partido se sostiene parejo."
    else:
        rec = ("No regalar la iniciativa: cuando se repliega, el partido se empareja." if replegado
               else "Buscar la ventaja: tiene el balón, pero no saca diferencia en ocasiones.")
    chica = r["minutos"] < cfg["minutos_min"]
    evidencia = (f"{r['minutos']:.0f} minutos en {r['partidos']:.0f} partidos · xG neto {r['xg_dif_90']:+.2f} "
                 f"(IC {r['xg_dif_bajo']:+.2f} a {r['xg_dif_alto']:+.2f})")
    if pd.notna(r.get("previos_xg_dif_90")):
        evidencia += f" · con Solari y Ortiz, {r['previos_xg_dif_90']:+.2f}"
    return {"situacion": r["nombre"], "hace": "; ".join(hace) + ".", "funciona": funciona + ".",
            "recomendacion": rec + (" Muestra chica: leer con cautela." if chica else ""), "evidencia": evidencia,
            "nivel": nivel, "muestra_chica": bool(chica)}


def registro(tabla: pd.DataFrame) -> dict:
    """Ganados, empatados, perdidos, puntos por partido y xG neto medio de una tabla de partidos del América."""
    g = int((tabla["goles_favor"] > tabla["goles_contra"]).sum())
    e = int((tabla["goles_favor"] == tabla["goles_contra"]).sum())
    p = int((tabla["goles_favor"] < tabla["goles_contra"]).sum())
    n = len(tabla)
    return {"partidos": n, "g": g, "e": e, "p": p, "puntos": (3 * g + e) / n if n else float("nan"),
            "xg_neto": float(tabla["xg_neto"].mean()) if n else float("nan")}


def texto_registro(r: dict) -> str:
    if not r["partidos"]:
        return "Sin partidos en la ventana."
    return (f"{r['partidos']} partidos: {r['g']}G {r['e']}E {r['p']}P · {r['puntos']:.2f} puntos por partido · "
            f"xG neto {r['xg_neto']:+.2f}")


def ficha(team_id: int, nombre: str, z: pd.DataFrame, medias: pd.DataFrame, contra: dict, parecidos: list[str],
          contra_parecidos: dict) -> dict:
    """Ficha de 10 segundos de un rival: cómo progresa, cómo defiende, dónde concede, balón parado y cómo le fue a Jardine."""
    fila, liga = z.loc[team_id], medias.mean()
    bp = medias.loc[team_id]
    return {
        "rival": nombre,
        "progresa": rivales.destacados(fila, "progresa") or ["Sin un rasgo que lo distinga de la liga"],
        "defiende": rivales.destacados(fila, "defiende") or ["Defiende como el promedio de la liga"],
        "concede": rivales.destacados(fila, "concede") or ["Concede como el promedio de la liga"],
        "balon_parado": (f"Concede {bp['bp_contra']:.2f} xG de balón parado por partido (liga {liga['bp_contra']:.2f}); "
                         f"genera {bp['bp_favor']:.2f} (liga {liga['bp_favor']:.2f})."),
        "balon_parado_rasgos": rivales.destacados(fila, "balon_parado"),
        "jardine": texto_registro(contra),
        "parecidos": parecidos,
        "jardine_parecidos": texto_registro(contra_parecidos),
    }
