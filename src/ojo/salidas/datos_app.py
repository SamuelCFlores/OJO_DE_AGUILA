"""Datos de la app (app/maqueta.html): un solo archivo outputs/app/datos.js que la plantilla dibuja.

El diseño vive en app/ (HTML, CSS y JS, versionados y editables a mano); Python solo produce datos.
datos.js define `window.OJO_DATOS = {...}` para que la página funcione abierta desde el disco (sin
servidor: un <script> sí carga archivos locales; fetch de un JSON no).

REF1: app/README.md (contrato de datos y cómo correr); contexto/barra_lateral.md, versión 3.
IMPOR1: lleva posiciones y nombres reales: vive en outputs/ (fuera de git).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from ojo.config import DIR_SALIDAS
from ojo.lentes.simulacion import Simulacion

ARCHIVO = DIR_SALIDAS / "app" / "datos.js"
VARIABLE = "window.OJO_DATOS"
CLAVES = ("meta", "titulo", "equipo", "rival", "portada", "explorar", "barra", "reproductor")


@dataclass
class Principio:
    """Tarjeta de un principio (criterio v2), con números ya formateados para leer."""

    titulo: str
    frase: str
    significa: str
    uso: str
    jardine: str
    previos: str
    diferencia: str
    intervalo: str
    torneos: str
    estado: str
    caso: str = ""


def principio(p: Principio) -> dict:
    return asdict(p)


def montecarlo(titulo: str, texto: str, s: Simulacion) -> dict:
    """Una simulación explicada, en números redondeados para la página."""
    return {"titulo": titulo, "texto": texto, "gana": round(s.gana, 4), "empata": round(s.empata, 4),
            "pierde": round(s.pierde, 4), "goles_favor": round(s.goles_favor, 2), "goles_contra": round(s.goles_contra, 2),
            "marcadores": [[m, round(v, 4)] for m, v in s.marcadores]}


def validar(datos: dict) -> list[str]:
    """Problemas del contrato (vacío si está completo)."""
    faltan = [f"falta {c}" for c in CLAVES if c not in datos]
    try:
        json.dumps(datos, allow_nan=False)
    except (TypeError, ValueError) as error:
        faltan.append(f"no es JSON válido: {error}")
    return faltan


def escribir(datos: dict, ruta: Path = ARCHIVO) -> Path:
    """Escribe datos.js (falla si el contrato está incompleto)."""
    problemas = validar(datos)
    if problemas:
        raise ValueError("; ".join(problemas))
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("// Generado por scripts/08_maqueta.py: datos reales, no se sube a git ni se publica.\n"
                    f"{VARIABLE} = {texto};\n", encoding="utf-8")
    return ruta


def leer(ruta: Path = ARCHIVO) -> dict:
    """Lee un datos.js (para pruebas y revisiones)."""
    texto = ruta.read_text(encoding="utf-8")
    return json.loads(texto[texto.index("=") + 1:].strip().rstrip(";"))
