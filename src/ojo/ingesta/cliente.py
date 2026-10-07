"""Cliente HTTP de StatsBomb con caché en disco, pausa y reintentos.

Uso:
    cliente = ClienteStatsBomb.desde_entorno()
    eventos = cliente.obtener("events", match_id=123)

Cada respuesta se guarda tal como llega en data/raw/{api}/{version}/{clave}.json.gz.
Si el archivo existe, no se hace la solicitud (regla no negociable 3).
Las credenciales nunca se registran ni se incluyen en mensajes de error.
"""

from __future__ import annotations

import gzip
import json
import logging
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from ojo.config import ARCHIVO_ENV, DIR_RAW
from ojo.ingesta.endpoints import (
    DOMINIO_SERVICES,
    DOMINIO_STATSBOMB,
    ENDPOINTS,
    ESPERA_BASE_S,
    MAX_REINTENTOS,
    PAUSA_S,
    TIMEOUT_S,
    Endpoint,
)

logger = logging.getLogger(__name__)

DOMINIOS = (DOMINIO_SERVICES, DOMINIO_STATSBOMB)


class ErrorAutenticacion(RuntimeError):
    """La API rechazó las credenciales (401/403 o redirección al login)."""


class ErrorAPI(RuntimeError):
    """La API respondió algo que no se puede usar."""


class ClienteStatsBomb:
    """Descarga de las APIs de StatsBomb con caché, pausa y espera creciente."""

    def __init__(
        self,
        usuario: str,
        contrasena: str,
        dir_raw: Path = DIR_RAW,
        pausa_s: float = PAUSA_S,
        max_reintentos: int = MAX_REINTENTOS,
        espera_base_s: float = ESPERA_BASE_S,
        sesion: requests.Session | None = None,
        dormir: Callable[[float], None] = time.sleep,
    ) -> None:
        self._auth = (usuario, contrasena)
        self.dir_raw = dir_raw
        self.pausa_s = pausa_s
        self.max_reintentos = max_reintentos
        self.espera_base_s = espera_base_s
        self._sesion = sesion or requests.Session()
        self._dormir = dormir
        self._ultima_solicitud = float("-inf")
        self._dominio_que_respondio: dict[str, str] = {}

    @classmethod
    def desde_entorno(cls, **kwargs: Any) -> ClienteStatsBomb:
        """Crea el cliente con STATSBOMB_USER y STATSBOMB_PASSWORD del archivo .env."""
        load_dotenv(ARCHIVO_ENV)
        usuario = os.environ.get("STATSBOMB_USER", "").strip()
        contrasena = os.environ.get("STATSBOMB_PASSWORD", "").strip()
        if not usuario or not contrasena:
            raise ErrorAutenticacion(
                f"Faltan credenciales: copia .env.example como .env en {ARCHIVO_ENV.parent} "
                "y llena STATSBOMB_USER y STATSBOMB_PASSWORD."
            )
        return cls(usuario, contrasena, **kwargs)

    def ruta_cache(self, api: str, **params: Any) -> Path:
        """Ruta del archivo de caché de una solicitud: data/raw/{api}/{version}/{clave}.json.gz."""
        endpoint = _endpoint(api)
        _validar_parametros(api, endpoint, params)
        clave = "_".join(str(params[p]) for p in endpoint.parametros) or "todas"
        return self.dir_raw / api / endpoint.version / f"{clave}.json.gz"

    def obtener(self, api: str, forzar: bool = False, **params: Any) -> Any:
        """Devuelve la respuesta JSON de una API; usa la caché salvo que `forzar` sea True."""
        ruta = self.ruta_cache(api, **params)
        if ruta.exists() and not forzar:
            logger.info("%s %s: desde caché", api, ruta.name)
            with gzip.open(ruta, "rb") as f:
                return json.load(f)
        contenido = self._descargar(api, **params)
        _guardar_gzip(ruta, contenido)
        return json.loads(contenido)

    def _descargar(self, api: str, **params: Any) -> bytes:
        """Descarga una API probando el dominio documentado y, si da 404, el otro."""
        endpoint = _endpoint(api)
        ruta_url = endpoint.ruta.format(**params)
        preferido = self._dominio_que_respondio.get(api, endpoint.dominio)
        dominios = [preferido] + [d for d in DOMINIOS if d != preferido]
        for dominio in dominios:
            respuesta = self._solicitar(api, dominio + ruta_url)
            if respuesta.status_code == 404:
                logger.warning("%s: 404 en %s, pruebo el otro dominio", api, dominio)
                continue
            if dominio != endpoint.dominio:
                logger.warning("%s respondió en %s, no en el dominio documentado", api, dominio)
            self._dominio_que_respondio[api] = dominio
            return respuesta.content
        raise ErrorAPI(f"{api}: 404 en ambos dominios para {ruta_url}")

    def _solicitar(self, api: str, url: str) -> requests.Response:
        """Hace un GET con pausa previa y reintentos con espera creciente ante 429, 5xx o red."""
        for intento in range(self.max_reintentos + 1):
            self._respetar_pausa()
            try:
                respuesta = self._sesion.get(
                    url, auth=self._auth, timeout=TIMEOUT_S, allow_redirects=False
                )
            except (requests.ConnectionError, requests.Timeout) as error:
                motivo = type(error).__name__
                respuesta = None
            else:
                motivo = str(respuesta.status_code)
                logger.info("%s %s -> %s (%d bytes)", api, url, motivo, len(respuesta.content))
                estado = respuesta.status_code
                if estado in (401, 403) or 300 <= estado < 400:
                    # Sin credenciales válidas la API redirige al login (302)
                    raise ErrorAutenticacion(
                        f"{api}: la API rechazó las credenciales (estado {estado}). "
                        "Revisa STATSBOMB_USER y STATSBOMB_PASSWORD en .env."
                    )
                if estado == 200:
                    _validar_json(api, respuesta)
                    return respuesta
                if estado == 404:
                    return respuesta
                if estado != 429 and estado < 500:
                    raise ErrorAPI(f"{api}: estado {estado} inesperado en {url}")
            if intento == self.max_reintentos:
                break
            espera = self._espera(intento, respuesta)
            logger.warning("%s: %s, reintento %d en %.0f s", api, motivo, intento + 1, espera)
            self._dormir(espera)
        raise ErrorAPI(f"{api}: sin respuesta válida tras {self.max_reintentos} reintentos ({motivo})")

    def _espera(self, intento: int, respuesta: requests.Response | None) -> float:
        """Segundos antes del siguiente intento: Retry-After si viene, si no espera creciente."""
        if respuesta is not None:
            retry_after = respuesta.headers.get("Retry-After", "")
            if retry_after.isdigit():
                return float(retry_after)
        return self.espera_base_s * 2**intento

    def _respetar_pausa(self) -> None:
        """Duerme lo necesario para dejar `pausa_s` segundos desde la solicitud anterior."""
        restante = self.pausa_s - (time.monotonic() - self._ultima_solicitud)
        if restante > 0:
            self._dormir(restante)
        self._ultima_solicitud = time.monotonic()


def _endpoint(api: str) -> Endpoint:
    """Busca la API en el catálogo y falla con la lista de opciones si no existe."""
    if api not in ENDPOINTS:
        raise ValueError(f"API desconocida: {api}. Opciones: {', '.join(ENDPOINTS)}")
    return ENDPOINTS[api]


def _validar_parametros(api: str, endpoint: Endpoint, params: dict[str, Any]) -> None:
    """Exige exactamente los parámetros que pide la ruta del endpoint."""
    esperados = set(endpoint.parametros)
    if set(params) != esperados:
        raise ValueError(f"{api} requiere {sorted(esperados)}, recibió {sorted(params)}")


def _validar_json(api: str, respuesta: requests.Response) -> None:
    """Confirma que la respuesta sea JSON (una página HTML de login no lo es)."""
    try:
        respuesta.json()
    except ValueError as error:
        raise ErrorAPI(f"{api}: la respuesta no es JSON") from error


def _guardar_gzip(ruta: Path, contenido: bytes) -> None:
    """Escribe el contenido comprimido de forma atómica (archivo temporal y renombrado)."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(ruta.name + ".tmp")
    with gzip.open(temporal, "wb") as f:
        f.write(contenido)
    temporal.replace(ruta)
