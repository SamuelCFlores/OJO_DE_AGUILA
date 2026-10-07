"""Catálogo de endpoints de StatsBomb y parámetros técnicos del cliente.

Versiones y dominios tal como vienen en contexto/api/README.md. Es el único
lugar donde se fijan; para cambiar de versión se edita solo este archivo.
"""

from dataclasses import dataclass
from string import Formatter

DOMINIO_SERVICES = "https://data.statsbombservices.com"
DOMINIO_STATSBOMB = "https://data.statsbomb.com"

# Consumo responsable de la API (regla no negociable 3)
PAUSA_S = 1.0           # pausa mínima entre solicitudes
MAX_REINTENTOS = 4      # reintentos ante 429, 5xx o fallas de red
ESPERA_BASE_S = 2.0     # espera creciente: 2, 4, 8, 16 s
TIMEOUT_S = 60.0        # tiempo máximo por solicitud


@dataclass(frozen=True)
class Endpoint:
    """Una API de StatsBomb: versión, plantilla de ruta y dominio documentado."""

    version: str
    ruta: str
    dominio: str

    @property
    def parametros(self) -> list[str]:
        """Nombres de los parámetros de la ruta, en orden de aparición."""
        return [campo for _, campo, _, _ in Formatter().parse(self.ruta) if campo]


ENDPOINTS: dict[str, Endpoint] = {
    "competitions": Endpoint("v4", "/api/v4/competitions", DOMINIO_SERVICES),
    "matches": Endpoint(
        "v6", "/api/v6/competitions/{competition_id}/seasons/{season_id}/matches", DOMINIO_SERVICES
    ),
    "events": Endpoint("v11", "/api/v11/events/{match_id}", DOMINIO_SERVICES),
    "frames_360": Endpoint("v2", "/api/v2/360-frames/{match_id}", DOMINIO_SERVICES),
    "lineups": Endpoint("v5", "/api/v5/lineups/{match_id}", DOMINIO_STATSBOMB),
    "team_match_stats": Endpoint("v4", "/api/v4/matches/{match_id}/team-stats", DOMINIO_STATSBOMB),
    "team_season_stats": Endpoint(
        "v4", "/api/v4/competitions/{competition_id}/seasons/{season_id}/team-stats", DOMINIO_SERVICES
    ),
    "player_match_stats": Endpoint("v8", "/api/v8/matches/{match_id}/player-stats", DOMINIO_SERVICES),
    "player_season_stats": Endpoint(
        "v7", "/api/v7/competitions/{competition_id}/seasons/{season_id}/player-stats", DOMINIO_SERVICES
    ),
    # Player Mapping (v1) usa parámetros de consulta; se agrega solo si hace falta.
}
