"""Pruebas del contrato de resumenes.json con el ejemplo inventado de tests/fixtures."""

import copy
import json
from pathlib import Path

import pytest

from ojo.config import params
from ojo.salidas.resumenes import IDS_SITUACION, validar

EJEMPLO = Path(__file__).parent / "fixtures" / "resumenes_ejemplo.json"


@pytest.fixture
def resumen() -> dict:
    return json.loads(EJEMPLO.read_text(encoding="utf-8"))


def test_el_ejemplo_cumple_el_contrato(resumen) -> None:
    assert validar(resumen) == []


def test_la_rejilla_coincide_con_params(resumen) -> None:
    rejilla = params()["resumenes"]["rejilla"]
    assert (resumen["meta"]["rejilla"]["filas"], resumen["meta"]["rejilla"]["columnas"]) == (rejilla["filas"], rejilla["columnas"])


def test_las_situaciones_del_framework_estan_en_el_contrato() -> None:
    texto = (Path(__file__).parents[1] / "contexto" / "framework.md").read_text(encoding="utf-8")
    for situacion in IDS_SITUACION - {"todas"}:
        assert f"`{situacion}`" in texto, f"{situacion} no está definida en framework.md"


@pytest.mark.parametrize("romper, mensaje", [
    (lambda r: r["combinaciones"].update({"9001|salida": r["combinaciones"]["9001|todos|salida"]}), "rival|torneo|situacion"),
    (lambda r: r["combinaciones"].update({"9999|todos|salida": r["combinaciones"]["9001|todos|salida"]}), "fuera de los catálogos"),
    (lambda r: r["combinaciones"]["9001|CL26|salida"]["metricas"]["america"].update(control=0.5), "debe ser null"),
    (lambda r: r["combinaciones"]["9001|todos|salida"].update(muestra_suficiente=False), "muestra_suficiente"),
    (lambda r: r["combinaciones"]["9001|todos|salida"]["mapa_control"].pop(), "matriz"),
    (lambda r: r["combinaciones"]["9001|todos|salida"]["metricas"]["america"].update(control=1.4), "fuera de [0, 1]"),
    (lambda r: r["fichas"]["9001"]["progresa_por"].update(centro=0.9), "sumar 1"),
    (lambda r: r.update(caso_por_defecto={"rival": "9002", "torneo": "todos", "situacion": "salida"}), "caso_por_defecto"),
    (lambda r: r["catalogos"]["rivales"].reverse(), "más a menos"),
])
def test_el_validador_detecta_incumplimientos(resumen, romper, mensaje) -> None:
    roto = copy.deepcopy(resumen)
    romper(roto)
    assert any(mensaje in e for e in validar(roto)), validar(roto)
