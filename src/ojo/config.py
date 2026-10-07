"""Rutas del proyecto, resueltas con pathlib desde la ubicación del paquete."""

from pathlib import Path

# src/ojo/config.py → parents[2] es la raíz del repo (instalación editable)
RAIZ: Path = Path(__file__).resolve().parents[2]

DIR_DATOS: Path = RAIZ / "data"
DIR_RAW: Path = DIR_DATOS / "raw"
DIR_LOGS: Path = RAIZ / "logs"
ARCHIVO_ENV: Path = RAIZ / ".env"
