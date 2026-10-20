"""Arma la entrega: un solo archivo HTML autocontenido con la maqueta definitiva, sus estilos, scripts, marca y datos.

La página de app/maqueta.html carga archivos vecinos (app.css, app.js, movimiento.js, branding/dist y
outputs/app/datos.js). Este script los incrusta todos en un solo HTML que abre con doble clic, sin servidor y sin
otros archivos. Lo único externo es la hoja de Google Fonts para los pesos de Poppins que la marca no incrusta; sin
internet, esos pesos caen al respaldo del sistema.

IMPOR1: la entrega lleva datos reales de StatsBomb (posiciones del 360 y nombres en las jugadas): es para los
organizadores del hackathon; se guarda en outputs/entrega/ (fuera de git). Solo se aloja en la web con el enlace que va
en el formulario de entrega (la página lleva noindex), por decisión de chamuel.
NOTA1: además escribe outputs/publicar/index.html, el mismo archivo con el nombre que piden los servicios de alojamiento
de arrastrar y soltar (la carpeta publicar/ completa es lo que se sube).
NOTA2: y outputs/entrega/ojo_de_aguila_artifact.html, la misma página para publicarla como artifact de claude.ai (privado,
compartido por invitación): sin <!doctype>, <html>, <head> ni <body> propios, porque el artifact pone ese esqueleto.

Cómo correrlo, desde la raíz del repo y con el entorno activado (antes, scripts/08_maqueta.py):
    python scripts/09_entrega.py
y abrir outputs/entrega/ojo_de_aguila.html con doble clic. Para alojarla, se sube la carpeta outputs/publicar/.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path

from ojo.config import DIR_SALIDAS, RAIZ

APP = RAIZ / "app"
SALIDA = DIR_SALIDAS / "entrega" / "ojo_de_aguila.html"
PUBLICAR = DIR_SALIDAS / "publicar" / "index.html"  # copia para alojar (NOTA1)
ARTIFACT = DIR_SALIDAS / "entrega" / "ojo_de_aguila_artifact.html"  # versión para artifact (NOTA2)


def _seguro_en_script(texto: str) -> str:
    """Evita que un "</script" dentro del código cierre la etiqueta antes de tiempo."""
    return re.sub(r"</(script)", r"<\\/\1", texto, flags=re.IGNORECASE)


def incrustar(html: str, base: Path) -> tuple[str, list[str]]:
    """Reemplaza <link rel=stylesheet>, <script src> e ícono locales por su contenido; devuelve el HTML y los archivos usados."""
    usados: list[str] = []

    def leer(ref: str) -> str:
        ruta = (base / ref).resolve()
        usados.append(str(ruta.relative_to(RAIZ)))
        return ruta.read_text(encoding="utf-8")

    def hoja(m: re.Match) -> str:
        ref = m.group(1)
        if ref.startswith("http"):
            return m.group(0)
        return f"<style>/* {Path(ref).name} */\n{leer(ref)}\n</style>"

    def guion(m: re.Match) -> str:
        ref = m.group(1)
        if ref.startswith("http"):
            return m.group(0)
        return f"<script>/* {Path(ref).name} */\n{_seguro_en_script(leer(ref))}\n</script>"

    def icono(m: re.Match) -> str:
        ref = m.group(1)
        ruta = (base / ref).resolve()
        usados.append(str(ruta.relative_to(RAIZ)))
        datos = base64.b64encode(ruta.read_bytes()).decode()
        return f'<link rel="icon" href="data:image/svg+xml;base64,{datos}" type="image/svg+xml">'

    html = re.sub(r'<link rel="icon" href="([^"]+)" type="image/svg\+xml">', icono, html)
    html = re.sub(r'<link rel="stylesheet" href="([^"]+)">', hoja, html)
    html = re.sub(r'<script src="([^"]+)"></script>', guion, html)
    return html, usados


def para_artifact(html: str, titulo: str = "Ojo de Águila") -> str:
    """La página sin su esqueleto (doctype, html, head y body), que el artifact pone por su cuenta. Los atributos de
    <html> y <body> (idioma, vista inicial y variante de la barra) se fijan con un script al principio del contenido."""
    def atributos(etiqueta: str) -> list[tuple[str, str]]:
        m = re.search(rf"<{etiqueta}(\s[^>]*)?>", html, flags=re.I)
        return re.findall(r'([\w-]+)="([^"]*)"', (m.group(1) or "") if m else "")
    poner = "".join(f"document.documentElement.setAttribute({json.dumps(k)},{json.dumps(v)});" for k, v in atributos("html"))
    poner += "".join(f"document.body.setAttribute({json.dumps(k)},{json.dumps(v)});" for k, v in atributos("body"))
    cuerpo = html
    for patron in (r"<!doctype html>\s*", r"<html(\s[^>]*)?>\s*", r"<head>\s*", r"<meta charset=\"utf-8\">\s*",
                   r"<meta name=\"viewport\"[^>]*>\s*", r"</head>\s*"):
        cuerpo = re.sub(patron, "", cuerpo, count=1, flags=re.I)  # la primera aparición es la etiqueta real
    cuerpo = re.sub(r"<body(\s[^>]*)?>", lambda _: f"<script>{poner}</script>", cuerpo, count=1, flags=re.I)
    for cierre in ("</html>", "</body>"):  # la última aparición es la etiqueta real
        k = cuerpo.lower().rfind(cierre)
        if k >= 0:
            cuerpo = cuerpo[:k] + cuerpo[k + len(cierre):]
    return re.sub(r"<title>[^<]*</title>", f"<title>{titulo}</title>", cuerpo, count=1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--salida", type=Path, default=SALIDA, help="archivo HTML a escribir")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if not (DIR_SALIDAS / "app" / "datos.js").exists():
        print("✗ Falta outputs/app/datos.js: corre antes python scripts/08_maqueta.py --partido 3918375 --tipo expulsion_favor")
        return 1
    html, usados = incrustar((APP / "maqueta.html").read_text(encoding="utf-8"), APP)
    restantes = re.findall(r'(?:src|href)="(?!https?:|data:|#)([^"]+)"', html)
    if restantes:
        print(f"✗ Quedan referencias locales sin incrustar: {restantes}")
        return 1
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(html, encoding="utf-8")
    PUBLICAR.parent.mkdir(parents=True, exist_ok=True)
    PUBLICAR.write_text(html, encoding="utf-8")
    print(f"Entrega: {args.salida.relative_to(RAIZ)} ({args.salida.stat().st_size / 1e6:.1f} MB; datos reales: no se sube a git)")
    print(f"Para alojar: {PUBLICAR.parent.relative_to(RAIZ)}/ (index.html; solo con el enlace del formulario)")
    ARTIFACT.write_text(para_artifact(html), encoding="utf-8")
    print(f"Para artifact: {ARTIFACT.relative_to(RAIZ)} (privado, compartido por invitación)")
    print("Incrustados: " + ", ".join(usados))
    return 0


if __name__ == "__main__":
    sys.exit(main())
