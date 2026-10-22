"""Construye la marca animada de Ojo de Águila a partir del proyecto de Claude Design.

Entradas (branding/):
    fuente/                       proyecto de Claude Design descomprimido (animations-v3.jsx,
                                  mirada-rapaz.jsx, ojo-loop.jsx, marca-2a/...)
    exportados/intro_mirada_rapaz.html
                                  exportación del video; de aquí salen React, ReactDOM, Babel
                                  y la tipografía Poppins (no se descarga nada)

Salidas (branding/dist/, se versionan):
    marca.js                      animación de entrada y loop del ícono, ya compilados
    marca.css                     Poppins 500/700 incrustada y tokens de color
    vendor/react*.js              React 18.3.1 (licencia MIT)

Requiere Node.js (compila el JSX con el Babel incluido en la exportación).

Cómo correrlo, desde la raíz del repo:
    python branding/construir_marca.py
"""

from __future__ import annotations

import base64
import gzip
import json
import re
import subprocess
import tempfile
from pathlib import Path

DIR = Path(__file__).resolve().parent
FUENTE = DIR / "fuente"
EXPORTADO = DIR / "exportados" / "intro_mirada_rapaz.html"
DIST = DIR / "dist"

# NOTA1: solo el subconjunto latino de Poppins; la entrada y la marca no usan otros alfabetos.
POPPINS_RANGOS = ("U+0000-00FF", "U+0100-02BA")

COMPILAR_JS = r"""
const fs = require('fs');
const [babelRuta, entrada, salida] = process.argv.slice(2);
const Babel = require(babelRuta);
const codigo = fs.readFileSync(entrada, 'utf8');
const r = Babel.transform(codigo, { presets: ['react'], sourceType: 'script', comments: false });
fs.writeFileSync(salida, r.code);
"""


def desempacar(html: Path) -> tuple[dict[str, tuple[str, bytes]], str]:
    """Devuelve {id o uuid: (mime, bytes)} y la plantilla de una exportación de Claude Design."""
    texto = html.read_text(encoding="utf-8")

    def bloque(tipo: str) -> str:
        m = re.search(r'<script type="__bundler/' + tipo + r'">(.*?)</script>', texto, re.S)
        if not m:
            raise SystemExit(f"{html.name}: no encuentro el bloque __bundler/{tipo}")
        return m.group(1)

    manifest = json.loads(bloque("manifest"))
    plantilla = json.loads(bloque("template"))
    nombres = {e["uuid"]: e["id"] for e in json.loads(bloque("ext_resources"))}
    recursos = {}
    for uuid, entrada in manifest.items():
        datos = base64.b64decode(entrada["data"])
        if entrada.get("compressed"):
            datos = gzip.decompress(datos)
        recursos[nombres.get(uuid, uuid)] = (entrada["mime"], datos)
    return recursos, plantilla


def recurso(recursos: dict, contiene: str) -> bytes:
    """Busca un recurso por fragmento de su nombre (las librerías vienen con su URL de unpkg)."""
    for nombre, (_, datos) in recursos.items():
        if contiene in nombre:
            return datos
    raise SystemExit(f"La exportación no trae {contiene}")


def compilar_jsx(babel: Path, origen: Path, tmp: Path) -> str:
    """Compila un archivo JSX a JavaScript con el Babel de la exportación (Node.js)."""
    script, salida = tmp / "compilar.js", tmp / (origen.stem + ".js")
    script.write_text(COMPILAR_JS, encoding="utf-8")
    subprocess.run(["node", str(script), str(babel), str(origen), str(salida)], check=True)
    return salida.read_text(encoding="utf-8")


def css_poppins(recursos: dict, plantilla: str) -> str:
    """Reescribe los @font-face latinos de Poppins con las fuentes incrustadas como data URI."""
    reglas = []
    for regla in re.findall(r"@font-face\s*{[^}]*}", plantilla):
        if not any(r in regla for r in POPPINS_RANGOS):
            continue
        uuid = re.search(r'url\("([0-9a-f-]{36})"\)', regla).group(1)
        mime, datos = recursos[uuid]
        uri = f"data:{mime};base64,{base64.b64encode(datos).decode()}"
        reglas.append(regla.replace(f'url("{uuid}")', f'url("{uri}")'))
    return "\n".join(reglas)


def envolver_escena(codigo: str, nombre_global: str) -> str:
    """Aísla una escena en su propio ámbito (las dos declaran NAVY, Piece, MOTION...)."""
    return f";(function () {{\n{codigo}\nwindow.{nombre_global} = Piece;\n}})();\n"


def main() -> None:
    recursos, plantilla = desempacar(EXPORTADO)
    DIST.mkdir(exist_ok=True)
    (DIST / "vendor").mkdir(exist_ok=True)
    (DIST / "vendor" / "react.production.min.js").write_bytes(recurso(recursos, "react@18.3.1/umd/react.production"))
    (DIST / "vendor" / "react-dom.production.min.js").write_bytes(recurso(recursos, "react-dom@18.3.1/umd/react-dom.production"))

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        babel = tmp / "babel.min.js"
        babel.write_bytes(recurso(recursos, "@babel/standalone"))
        runtime = compilar_jsx(babel, FUENTE / "animations-v3.jsx", tmp)
        intro = compilar_jsx(babel, FUENTE / "mirada-rapaz.jsx", tmp)
        loop = compilar_jsx(babel, FUENTE / "ojo-loop.jsx", tmp)

    anfitrion = (DIR / "anfitrion.js").read_text(encoding="utf-8")
    cabecera = "/* Ojo de Águila · marca animada. Generado por branding/construir_marca.py: no editar a mano. */\n"
    (DIST / "marca.js").write_text(
        cabecera + runtime + "\n" + envolver_escena(intro, "__OjoIntroPieza")
        + envolver_escena(loop, "__OjoLoopPieza") + anfitrion,
        encoding="utf-8",
    )
    tokens = (DIR / "tokens.css").read_text(encoding="utf-8")
    (DIST / "marca.css").write_text(cabecera + css_poppins(recursos, plantilla) + "\n" + tokens, encoding="utf-8")

    for archivo in sorted(DIST.rglob("*.*")):
        print(f"{archivo.stat().st_size:>9,}  {archivo.relative_to(DIR)}")


if __name__ == "__main__":
    main()
