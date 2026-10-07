"""Pruebas de la estructura del repo: paquete instalable, params.yaml válido y .gitignore protector."""

import importlib
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]

SUBPAQUETES = ["ojo", "ojo.ingesta", "ojo.datos", "ojo.framework", "ojo.lentes", "ojo.salidas"]

# Secciones de la propuesta de params.yaml en contexto/framework.md
SECCIONES_PARAMS = [
    "equipo", "entrenador", "liga", "campo", "tercios", "presion", "transicion",
    "pase_progresivo", "balon_parado", "tramos_min", "red_pases", "voronoi", "simulacion",
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
]

# Rutas que sí deben poder versionarse
DEBEN_VERSIONARSE = [
    ".env.example",
    "config/params.yaml",
    "tests/fixtures/partido_sintetico.json",
    "notebooks/01_exploracion.ipynb",
    "reports/informe.qmd",
]


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
