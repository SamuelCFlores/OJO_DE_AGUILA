"""Pruebas del cliente de StatsBomb con una sesión falsa: sin red ni credenciales reales."""

import gzip
import json
import logging
from pathlib import Path

import pytest

from ojo.ingesta.cliente import ClienteStatsBomb, ErrorAPI, ErrorAutenticacion
from ojo.ingesta.endpoints import DOMINIO_SERVICES, DOMINIO_STATSBOMB

USUARIO, CONTRASENA = "usuario_prueba", "secreto_prueba"


class RespuestaFalsa:
    """Imita lo mínimo de requests.Response que usa el cliente."""

    def __init__(self, estado: int, cuerpo: object = None, headers: dict | None = None) -> None:
        self.status_code = estado
        self.content = json.dumps(cuerpo).encode() if cuerpo is not None else b"<html>login</html>"
        self.headers = headers or {}

    def json(self) -> object:
        return json.loads(self.content)


class SesionFalsa:
    """Devuelve respuestas programadas en orden y registra las URLs pedidas."""

    def __init__(self, respuestas: list[RespuestaFalsa]) -> None:
        self.respuestas = list(respuestas)
        self.urls: list[str] = []

    def get(self, url: str, **kwargs: object) -> RespuestaFalsa:
        assert kwargs["allow_redirects"] is False
        self.urls.append(url)
        return self.respuestas.pop(0)


def _cliente(tmp_path: Path, respuestas: list[RespuestaFalsa]) -> tuple[ClienteStatsBomb, SesionFalsa, list[float]]:
    """Cliente sin pausa real: las esperas se registran en una lista."""
    sesion = SesionFalsa(respuestas)
    esperas: list[float] = []
    cliente = ClienteStatsBomb(
        USUARIO, CONTRASENA, dir_raw=tmp_path, pausa_s=0, max_reintentos=2,
        espera_base_s=2.0, sesion=sesion, dormir=esperas.append,
    )
    return cliente, sesion, esperas


def test_ruta_cache_sigue_la_convencion(tmp_path: Path) -> None:
    cliente, _, _ = _cliente(tmp_path, [])
    assert cliente.ruta_cache("events", match_id=7) == tmp_path / "events" / "v11" / "7.json.gz"
    assert cliente.ruta_cache("matches", competition_id=1, season_id=2).name == "1_2.json.gz"
    assert cliente.ruta_cache("competitions").name == "todas.json.gz"


def test_parametros_incorrectos_fallan_antes_de_pedir(tmp_path: Path) -> None:
    cliente, sesion, _ = _cliente(tmp_path, [])
    with pytest.raises(ValueError):
        cliente.obtener("events", partido=7)
    assert sesion.urls == []


def test_segunda_llamada_sale_de_la_cache(tmp_path: Path) -> None:
    cliente, sesion, _ = _cliente(tmp_path, [RespuestaFalsa(200, [{"id": 1}])])
    assert cliente.obtener("events", match_id=7) == [{"id": 1}]
    assert cliente.obtener("events", match_id=7) == [{"id": 1}]
    assert len(sesion.urls) == 1
    with gzip.open(tmp_path / "events" / "v11" / "7.json.gz", "rb") as f:
        assert json.load(f) == [{"id": 1}]


def test_redireccion_al_login_es_error_de_autenticacion_sin_reintentos(tmp_path: Path) -> None:
    cliente, sesion, _ = _cliente(tmp_path, [RespuestaFalsa(302)])
    with pytest.raises(ErrorAutenticacion) as error:
        cliente.obtener("competitions")
    assert len(sesion.urls) == 1
    assert CONTRASENA not in str(error.value)


def test_429_reintenta_con_espera_creciente(tmp_path: Path) -> None:
    respuestas = [RespuestaFalsa(429, {}), RespuestaFalsa(503, {}), RespuestaFalsa(200, [])]
    cliente, sesion, esperas = _cliente(tmp_path, respuestas)
    assert cliente.obtener("competitions") == []
    assert len(sesion.urls) == 3
    assert esperas == [2.0, 4.0]


def test_respeta_retry_after(tmp_path: Path) -> None:
    respuestas = [RespuestaFalsa(429, {}, {"Retry-After": "30"}), RespuestaFalsa(200, [])]
    cliente, _, esperas = _cliente(tmp_path, respuestas)
    cliente.obtener("competitions")
    assert esperas == [30.0]


def test_agota_reintentos_y_no_guarda_cache(tmp_path: Path) -> None:
    cliente, _, _ = _cliente(tmp_path, [RespuestaFalsa(500, {})] * 3)
    with pytest.raises(ErrorAPI):
        cliente.obtener("competitions")
    assert not cliente.ruta_cache("competitions").exists()


def test_404_prueba_el_otro_dominio_y_lo_recuerda(tmp_path: Path) -> None:
    respuestas = [RespuestaFalsa(404, {}), RespuestaFalsa(200, []), RespuestaFalsa(200, [])]
    cliente, sesion, _ = _cliente(tmp_path, respuestas)
    cliente.obtener("lineups", match_id=1)
    cliente.obtener("lineups", match_id=2)
    assert sesion.urls[0].startswith(DOMINIO_STATSBOMB)
    assert sesion.urls[1].startswith(DOMINIO_SERVICES)
    assert sesion.urls[2].startswith(DOMINIO_SERVICES)


def test_respuesta_que_no_es_json_falla(tmp_path: Path) -> None:
    respuesta = RespuestaFalsa(200)  # cuerpo HTML
    cliente, _, _ = _cliente(tmp_path, [respuesta])
    with pytest.raises(ErrorAPI):
        cliente.obtener("competitions")


def test_el_registro_no_contiene_credenciales(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    cliente, _, _ = _cliente(tmp_path, [RespuestaFalsa(200, [])])
    with caplog.at_level(logging.DEBUG):
        cliente.obtener("competitions")
    assert caplog.text
    assert USUARIO not in caplog.text and CONTRASENA not in caplog.text


def test_desde_entorno_sin_credenciales_explica_que_hacer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ojo.ingesta.cliente.load_dotenv", lambda *_: None)
    monkeypatch.delenv("STATSBOMB_USER", raising=False)
    monkeypatch.delenv("STATSBOMB_PASSWORD", raising=False)
    with pytest.raises(ErrorAutenticacion, match=".env"):
        ClienteStatsBomb.desde_entorno()
