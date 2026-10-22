"""Documentación del proyecto en PDF: convierte DOCUMENTACION.md en una página con la identidad azulcrema y la imprime con Chrome.

El Markdown de la raíz es la única fuente: el PDF siempre dice lo mismo que el repositorio. El conversor cubre solo lo
que usa el documento (títulos, párrafos, citas, cursivas, listas con un nivel de anidación y párrafos sangrados dentro de un
elemento, tablas, negritas, código y enlaces).
NOTA1: el documento no lleva datos de StatsBomb, solo resultados agregados, como la página; aun así va a outputs/entrega/
(lo generado no se versiona).
NOTA2: Chrome imprime sin servidor (--print-to-pdf); la tipografía Poppins llega de Google Fonts, así que hace falta
internet para que salga con la letra de la marca.

Cómo correrlo, desde la raíz del repo y con el entorno activado:
    python scripts/10_guia.py
y abrir outputs/entrega/Ojo_de_Aguila_documentacion.pdf. Con --sin-pdf solo escribe el HTML (para revisarlo en el navegador).
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

from ojo.config import DIR_SALIDAS, RAIZ

FUENTE = RAIZ / "DOCUMENTACION.md"
DESTINO = DIR_SALIDAS / "entrega"
NOMBRE = "Ojo_de_Aguila_documentacion"
CHROMES = [Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
           Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
           Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")]
# El ojo de la marca en azulcrema, igual que en la página (app/app.js, OJO_LEYENDA)
OJO = ('<svg viewBox="0 14 102 70" width="58" height="40" aria-hidden="true">'
       '<polygon points="12,19.6 86,30.8 99,46.7 95.4,50.6 24.1,29.2" fill="#F0EB9A" stroke="#F0EB9A" stroke-width="2"/>'
       '<clipPath id="almendra"><path d="M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z"/></clipPath>'
       '<path d="M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z" fill="#0F1D41" stroke="#F0EB9A" stroke-width="6"/>'
       '<g clip-path="url(#almendra)"><circle cx="54" cy="54" r="24" fill="#F0EB9A"/>'
       '<path d="M49.3 47.5L58.7 47.5L61.6 56.5L54 62L46.4 56.5Z" fill="#0F1D41" stroke="#0F1D41" stroke-width="3"/></g></svg>')
CSS = """
@page { size: Letter; margin: 16mm 16mm 18mm; }
* { box-sizing: border-box; }
body { margin: 0; font: 400 10.2pt/1.5 Poppins, "Segoe UI", Arial, sans-serif; color: #0F1D41; }
header.portada { background: #0F1D41; color: #fff; border-radius: 10px; padding: 16px 20px 14px; display: grid;
  grid-template-columns: auto 1fr; gap: 6px 16px; align-items: center; border-bottom: 5px solid #F6303E; }
header.portada svg { grid-row: span 2; }
header.portada h1 { margin: 0; font-size: 21pt; font-weight: 900; text-transform: uppercase; letter-spacing: .01em; line-height: 1.1; }
header.portada h1 span { color: #F0EB9A; }
header.portada .sub { font-size: 9.6pt; color: rgba(255,255,255,.85); }
header.portada .sub p { margin: 0; }
header.portada strong { color: #F0EB9A; font-weight: 700; }
h2 { font-size: 13.5pt; font-weight: 900; text-transform: uppercase; margin: 20px 0 8px; padding-bottom: 4px;
  border-bottom: 3px solid #F0EB9A; break-after: avoid; }
h3 { font-size: 11pt; margin: 14px 0 6px; break-after: avoid; }
p { margin: 6px 0; }
blockquote { margin: 12px 0; background: #F0EB9A; border-radius: 8px; padding: 9px 14px; font-weight: 500; }
blockquote p { margin: 0; }
ul, ol { margin: 6px 0; padding-left: 20px; }
li { margin: 3px 0; }
li > ul { margin: 3px 0; }
li > p { margin: 4px 0 2px; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 10px; font-size: 9.2pt; break-inside: avoid; }
th { background: #0F1D41; color: #fff; text-align: left; font-weight: 700; padding: 6px 8px; }
td { padding: 5px 8px; border-bottom: 1px solid rgba(15,29,65,.15); vertical-align: top; }
tr:nth-child(even) td { background: rgba(240,235,154,.25); }
code { font-family: Consolas, monospace; font-size: 8.8pt; background: rgba(15,29,65,.07); padding: 0 3px; border-radius: 3px; }
a { color: #0F1D41; font-weight: 600; }
strong { font-weight: 700; }
footer { margin-top: 18px; padding-top: 8px; border-top: 1px solid rgba(15,29,65,.2); font-size: 8.4pt; color: rgba(15,29,65,.7); }
"""


def en_linea(texto: str) -> str:
    """Negritas, código y enlaces dentro de una línea (el resto, escapado)."""
    partes = re.split(r"(`[^`]+`)", texto)
    salida = []
    for p in partes:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            salida.append(f"<code>{html.escape(p[1:-1])}</code>")
            continue
        s = html.escape(p, quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![*\w])\*([^*\s][^*]*?)\*(?![*\w])", r"<em>\1</em>", s)  # cursiva con un asterisco
        s = re.sub(r"(https?://[^\s<)]+[^\s<).,;])", r'<a href="\1">\1</a>', s)
        salida.append(s)
    return "".join(salida)


def celdas(linea: str) -> list[str]:
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def convertir(md: str) -> tuple[str, str, list[str]]:
    """Markdown de la guía → (título, cuerpo HTML, líneas del subtítulo que van en la portada)."""
    lineas = md.splitlines()
    titulo, sub, cuerpo = "", [], []
    k, n = 0, len(lineas)
    while k < n:
        l = lineas[k]
        if not l.strip():
            k += 1
            continue
        if l.startswith("# "):
            titulo = l[2:].strip()
            k += 1
            while k < n and not lineas[k].strip():
                k += 1
            while k < n and lineas[k].strip() and not lineas[k].startswith(("#", ">")):  # subtítulo de la portada
                sub.append(en_linea(lineas[k].strip().rstrip("\\").strip()))  # "\" al final: salto de línea de Markdown
                k += 1
            continue
        if l.startswith("## "):
            cuerpo.append(f"<h2>{en_linea(l[3:].strip())}</h2>")
        elif l.startswith("### "):
            cuerpo.append(f"<h3>{en_linea(l[4:].strip())}</h3>")
        elif l.startswith(">"):
            bloque = []
            while k < n and lineas[k].startswith(">"):
                bloque.append(lineas[k].lstrip("> ").strip())
                k += 1
            cuerpo.append(f"<blockquote><p>{en_linea(' '.join(bloque))}</p></blockquote>")
            continue
        elif l.startswith("|"):
            filas = []
            while k < n and lineas[k].startswith("|"):
                filas.append(lineas[k])
                k += 1
            cab, datos = celdas(filas[0]), [celdas(f) for f in filas[2:]]
            cuerpo.append("<table><thead><tr>" + "".join(f"<th>{en_linea(c)}</th>" for c in cab) + "</tr></thead><tbody>"
                          + "".join("<tr>" + "".join(f"<td>{en_linea(c)}</td>" for c in f) + "</tr>" for f in datos)
                          + "</tbody></table>")
            continue
        elif re.match(r"^(- |\d+\. )", l):
            ordenada = bool(re.match(r"^\d+\. ", l))
            items: list[dict] = []  # {"texto", "sub": viñetas anidadas, "extra": párrafos sangrados después de ellas}
            while k < n:
                m = lineas[k]
                if not m.strip():  # una línea en blanco sigue la lista si lo siguiente está sangrado
                    sigue = next((x for x in lineas[k + 1:] if x.strip()), "")
                    if re.match(r"^\s{2,}\S", sigue):
                        k += 1
                        continue
                    break
                if re.match(r"^\s{2,}- ", m):
                    items[-1]["sub"].append(en_linea(m.strip()[2:]))
                elif re.match(r"^\s{2,}\S", m):
                    items[-1]["extra"].append(en_linea(m.strip()))
                elif re.match(r"^(- |\d+\. )", m):
                    items.append({"texto": en_linea(re.sub(r"^(- |\d+\. )", "", m).strip()), "sub": [], "extra": []})
                else:
                    break
                k += 1
            etiqueta = "ol" if ordenada else "ul"
            cuerpo.append(f"<{etiqueta}>" + "".join(
                "<li>" + i["texto"] + ("<ul>" + "".join(f"<li>{x}</li>" for x in i["sub"]) + "</ul>" if i["sub"] else "")
                + "".join(f"<p>{x}</p>" for x in i["extra"]) + "</li>" for i in items) + f"</{etiqueta}>")
            continue
        else:
            parrafo = []
            while k < n and lineas[k].strip() and not re.match(r"^(#|>|\||- |\d+\. )", lineas[k]):
                parrafo.append(lineas[k].strip())
                k += 1
            cuerpo.append(f"<p>{en_linea(' '.join(parrafo))}</p>")
            continue
        k += 1
    return titulo, "\n".join(cuerpo), sub


def pagina(titulo: str, cuerpo: str, sub: list[str]) -> str:
    nombre, _, resto = titulo.partition(" · ")
    titulo_html = html.escape(nombre) + (f" · <span>{html.escape(resto)}</span>" if resto else "")
    return (f'<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><title>{html.escape(titulo)}</title>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;900&display=swap">'
            f"<style>{CSS}</style></head><body>"
            f'<header class="portada">{OJO}<h1>{titulo_html}</h1>'
            f'<div class="sub">{"".join(f"<p>{s}</p>" for s in sub)}</div></header>\n{cuerpo}\n'
            "<footer>Generado desde DOCUMENTACION.md (scripts/10_guia.py). Datos de Hudl StatsBomb, solo para la competencia.</footer>"
            "</body></html>")


def imprimir(html_ruta: Path, pdf_ruta: Path) -> bool:
    """Imprime el HTML a PDF con Chrome (o Edge) sin ventana. Devuelve False si no encuentra el navegador."""
    navegador = next((c for c in CHROMES if c.exists()), None) or (Path(p) if (p := shutil.which("chrome")) else None)
    if navegador is None:
        return False
    subprocess.run([str(navegador), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    f"--print-to-pdf={pdf_ruta}", html_ruta.resolve().as_uri()], check=True, capture_output=True, timeout=120)
    return pdf_ruta.exists()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sin-pdf", action="store_true", help="solo escribe el HTML")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    DESTINO.mkdir(parents=True, exist_ok=True)
    titulo, cuerpo, sub = convertir(FUENTE.read_text(encoding="utf-8"))
    ruta_html = DESTINO / f"{NOMBRE}.html"
    ruta_html.write_text(pagina(titulo, cuerpo, sub), encoding="utf-8")
    print(f"HTML: {ruta_html.relative_to(RAIZ)}")
    if args.sin_pdf:
        return 0
    ruta_pdf = DESTINO / f"{NOMBRE}.pdf"
    if not imprimir(ruta_html, ruta_pdf):
        print("✗ No encontré Chrome ni Edge: abre el HTML y guárdalo como PDF desde el navegador (Ctrl+P).")
        return 1
    print(f"PDF: {ruta_pdf.relative_to(RAIZ)} ({ruta_pdf.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
