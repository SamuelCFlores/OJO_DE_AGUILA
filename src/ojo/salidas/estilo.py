"""Identidad visual para las figuras: colores tomados de branding/tokens.css (fuente única).

Convención de datos: cancha azul marino, el equipo del caso en el acento (dorado o crema), el rival en blanco.
Hay dos paletas: "marca" (azul y dorado, la de siempre) y "azulcrema" (la del club, propuesta visual del
13 oct). Las funciones de figuras piden colores por papel ("azul", "dorado", "blanco"...) y la paleta activa
decide el valor; se cambia solo dentro de un bloque `with paleta("azulcrema"):`.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from ojo.config import RAIZ

ARCHIVO_TOKENS = RAIZ / "branding" / "tokens.css"
# Papel en las figuras → token de cada paleta (los que no aparecen se toman tal cual de --oda-*).
PALETAS: dict[str, dict[str, str]] = {
    "marca": {"rojo": "dorado", "azul-hover": "club-azul-hover", "lectura": "azul"},
    "azulcrema": {"azul": "club-azul", "dorado": "club-amarillo", "rojo": "club-rojo", "azul-hover": "club-azul-hover",
                  "lectura": "club-rojo"},
}
_activa = ["marca"]  # NOTA1: pila de una sola casilla; solo la cambia el administrador de contexto paleta()


@lru_cache(maxsize=1)
def tokens() -> dict[str, str]:
    """Colores de tokens.css como {nombre: '#RRGGBB'}: 'azul', 'dorado'... (--oda-*) y 'club-azul'... (--club-*)."""
    texto = ARCHIVO_TOKENS.read_text(encoding="utf-8")
    pares = re.findall(r"--(oda|club)-([a-z-]+):\s*(#[0-9A-Fa-f]{6})", texto)
    return {(nombre if prefijo == "oda" else f"club-{nombre}"): valor.upper() for prefijo, nombre, valor in pares}


@contextmanager
def paleta(nombre: str) -> Iterator[None]:
    """Usa otra paleta dentro del bloque (p. ej. "azulcrema") y vuelve a la anterior al salir."""
    if nombre not in PALETAS:
        raise ValueError(f"Paleta desconocida: {nombre}. Opciones: {', '.join(PALETAS)}")
    anterior, _activa[0] = _activa[0], nombre
    try:
        yield
    finally:
        _activa[0] = anterior


def paleta_activa() -> str:
    return _activa[0]


def color(nombre: str) -> str:
    """Color por papel o token ("azul", "dorado", "blanco", "club-rojo"...), según la paleta activa."""
    return tokens()[PALETAS[_activa[0]].get(nombre, nombre)]


def rgba(nombre: str, alfa: float) -> tuple[float, float, float, float]:
    """Color como tupla RGBA de matplotlib, según la paleta activa."""
    h = color(nombre).lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (alfa,)
