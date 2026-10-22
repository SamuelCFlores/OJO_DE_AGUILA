"""Lectura de la caché cruda (data/raw), sin red y sin credenciales.

Es la única puerta de ojo.datos hacia data/raw/. Si un archivo no está en la caché,
falla con un mensaje que indica cómo descargarlo; nunca llama a la API.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

from ojo.config import DIR_RAW
from ojo.ingesta.cliente import ruta_cache


def ruta(api: str, dir_raw: Path = DIR_RAW, **params: Any) -> Path:
    """Ruta del archivo de caché de una API (misma convención que el cliente)."""
    return ruta_cache(api, dir_raw=dir_raw, **params)


def existe(api: str, dir_raw: Path = DIR_RAW, **params: Any) -> bool:
    """Indica si la respuesta de una API ya está en la caché."""
    return ruta(api, dir_raw=dir_raw, **params).exists()


def leer(api: str, dir_raw: Path = DIR_RAW, **params: Any) -> Any:
    """Devuelve el JSON guardado en la caché; falla si no se ha descargado."""
    archivo = ruta(api, dir_raw=dir_raw, **params)
    if not archivo.exists():
        raise FileNotFoundError(
            f"No está en la caché: {api} {params}. Descárgalo con scripts/02_descarga.py."
        )
    with gzip.open(archivo, "rt", encoding="utf-8") as f:
        return json.load(f)
