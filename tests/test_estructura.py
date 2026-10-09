"""Pruebas de la estructura del repo: paquete instalable, params.yaml válido, .gitignore protector y bitácora CAMBIOS."""

import importlib
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]

SUBPAQUETES = ["ojo", "ojo.ingesta", "ojo.datos", "ojo.framework", "ojo.lentes", "ojo.salidas"]

# Secciones de la propuesta de params.yaml en contexto/framework.md
SECCIONES_PARAMS = [
    "equipo", "entrenador", "predecesores", "liga", "validacion", "relevos", "campo", "tercios", "presion", "transicion",
    "pase_progresivo", "balon_parado", "tramos_min", "red_pases", "voronoi", "simulacion", "resumenes",
]

# Rutas que nunca deben entrar a git (reglas no negociables 1 y 2)
DEBEN_IGNORARSE = [
    ".env",
    ".env.local",
    "data/raw/events/v11/123.json.gz",
    "data/processed/eventos.parquet",
    "data/cualquier_archivo.txt",  # la carpeta completa, no solo por extensión
    "outputs/figuras/red.png",
    "logs/solicitudes.log",
    "notebooks/eventos.csv",
    "notebooks/respuesta.json",
    "scripts/partido.parquet",
    "reports/informe.html",
    "branding/exportados/intro_mirada_rapaz.html",
    "branding/fuente/uploads/video.mp4",
]

# Rutas que sí deben poder versionarse
DEBEN_VERSIONARSE = [
    ".env.example",
    "config/params.yaml",
    "tests/fixtures/partido_sintetico.json",
    "notebooks/01_exploracion.ipynb",
    "reports/informe.qmd",
    "CAMBIOS/C01_0810.md",
    ".github/workflows/main_sin_cambios.yml",
    "branding/dist/marca.js",
    "branding/fuente/marca-2a/isotipo-color.svg",
]

# Bitácora: C##_ddmm.md (CAMBIOS/README.md); README y PLANTILLA no siguen el patrón
PATRON_CAMBIOS = re.compile(r"C(?P<numero>\d{2,})_(?P<ddmm>\d{4})\.md")
CAMBIOS_FIJOS = {"README.md", "PLANTILLA.md"}
ANIO_PROYECTO = 2026


def _esta_ignorada(ruta: str) -> bool:
    """Indica si git ignoraría la ruta según .gitignore, exista o no el archivo."""
    resultado = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", ruta],
        cwd=RAIZ,
        capture_output=True,
    )
    return resultado.returncode == 0


requiere_git = pytest.mark.skipif(
    shutil.which("git") is None or not (RAIZ / ".git").exists(),
    reason="requiere git y un clon del repo",
)


@pytest.mark.parametrize("nombre", SUBPAQUETES)
def test_subpaquete_importa(nombre: str) -> None:
    importlib.import_module(nombre)


def test_params_yaml_tiene_las_secciones_del_framework() -> None:
    params = yaml.safe_load((RAIZ / "config" / "params.yaml").read_text(encoding="utf-8"))
    assert isinstance(params, dict)
    faltantes = [s for s in SECCIONES_PARAMS if s not in params]
    assert not faltantes, f"faltan secciones en params.yaml: {faltantes}"


@requiere_git
@pytest.mark.parametrize("ruta", DEBEN_IGNORARSE)
def test_gitignore_protege_datos_y_secretos(ruta: str) -> None:
    assert _esta_ignorada(ruta), f"{ruta} podría subirse a git"


@requiere_git
@pytest.mark.parametrize("ruta", DEBEN_VERSIONARSE)
def test_gitignore_no_bloquea_archivos_del_proyecto(ruta: str) -> None:
    assert not _esta_ignorada(ruta), f"{ruta} quedó ignorado por error"


def test_bitacora_cambios_sigue_el_formato() -> None:
    carpeta = RAIZ / "CAMBIOS"
    if not carpeta.is_dir():
        pytest.skip("CAMBIOS/ solo existe en la rama tests")
    numeros = []
    for archivo in sorted(carpeta.iterdir()):
        if archivo.name in CAMBIOS_FIJOS:
            continue
        coincide = PATRON_CAMBIOS.fullmatch(archivo.name)
        assert coincide, f"{archivo.name} no sigue el formato C##_ddmm.md"
        ddmm = coincide["ddmm"]
        try:
            datetime.strptime(f"{ddmm}{ANIO_PROYECTO}", "%d%m%Y")
        except ValueError:
            pytest.fail(f"{archivo.name}: {ddmm} no es una fecha ddmm válida")
        numeros.append(int(coincide["numero"]))
    assert len(numeros) == len(set(numeros)), f"números de cambio repetidos: {sorted(numeros)}"
