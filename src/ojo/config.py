"""Rutas del proyecto y parámetros del framework, resueltos con pathlib desde el paquete."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

# src/ojo/config.py → parents[2] es la raíz del repo (instalación editable)
RAIZ: Path = Path(__file__).resolve().parents[2]

DIR_DATOS: Path = RAIZ / "data"
DIR_RAW: Path = DIR_DATOS / "raw"
DIR_PROCESADO: Path = DIR_DATOS / "processed"
DIR_LOGS: Path = RAIZ / "logs"
DIR_REPORTES: Path = RAIZ / "reports"
DIR_SALIDAS: Path = RAIZ / "outputs"
ARCHIVO_ENV: Path = RAIZ / ".env"
ARCHIVO_PARAMS: Path = RAIZ / "config" / "params.yaml"


@lru_cache(maxsize=1)
def params() -> dict[str, Any]:
    """Umbrales y ids del framework (config/params.yaml), leídos una sola vez."""
    return yaml.safe_load(ARCHIVO_PARAMS.read_text(encoding="utf-8"))
