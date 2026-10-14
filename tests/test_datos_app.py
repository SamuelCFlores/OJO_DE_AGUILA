"""Pruebas del contrato de datos de la app (outputs/app/datos.js) y de la barra compacta."""

import pytest

from ojo.framework import quiebres
from ojo.salidas import barra, datos_app


def _datos() -> dict:
    return {c: {} for c in datos_app.CLAVES} | {"titulo": "Caso </script> con etiqueta", "equipo": "América", "rival": "Rival"}


def test_escribe_y_lee_datos_js(tmp_path) -> None:
    ruta = datos_app.escribir(_datos(), tmp_path / "datos.js")
    texto = ruta.read_text(encoding="utf-8")
    assert texto.splitlines()[1].startswith(datos_app.VARIABLE + " = ")
    assert "</script>" not in texto  # no puede cerrar la etiqueta <script> que lo carga
    assert datos_app.leer(ruta)["titulo"] == "Caso </script> con etiqueta"


def test_rechaza_datos_incompletos_o_no_json(tmp_path) -> None:
    incompletos = _datos()
    del incompletos["barra"]
    with pytest.raises(ValueError, match="falta barra"):
        datos_app.escribir(incompletos, tmp_path / "datos.js")
    con_nan = _datos() | {"meta": {"x": float("nan")}}
    assert any("JSON" in p for p in datos_app.validar(con_nan))


def test_cada_quiebre_del_caso_tiene_su_momento_en_la_barra() -> None:
    sin_momento = {"sustitucion_lesion_propia", "sustitucion_lesion_rival"}  # los cambios forzados no son un filtro
    assert set(quiebres.TIPOS) - sin_momento == set(barra.MOMENTOS)
    assert len(set(barra.MOMENTOS.values())) == 6
