"""Identidad visual para las figuras: colores tomados de branding/tokens.css (fuente única).

Convención de datos: cancha azul marino, el equipo del caso en dorado, el rival en blanco.
"""

from __future__ import annotations

import re
from functools import lru_cache

from ojo.config import RAIZ

ARCHIVO_TOKENS = RAIZ / "branding" / "tokens.css"


@lru_cache(maxsize=1)
def tokens() -> dict[str, str]:
    """Colores de la marca como {nombre: '#RRGGBB'} (p. ej. 'azul', 'dorado', 'blanco')."""
    texto = ARCHIVO_TOKENS.read_text(encoding="utf-8")
    return {nombre: valor.upper() for nombre, valor in re.findall(r"--oda-([a-z-]+):\s*(#[0-9A-Fa-f]{6})", texto)}


def color(nombre: str) -> str:
    """Color de la marca por nombre de token (sin el prefijo --oda-)."""
    return tokens()[nombre]


def rgba(nombre: str, alfa: float) -> tuple[float, float, float, float]:
    """Color de la marca como tupla RGBA de matplotlib."""
    h = color(nombre).lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (alfa,)
