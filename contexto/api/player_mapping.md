# Player Mapping v1.0.0 (StatsBomb)

- Endpoint: `GET https://data.statsbomb.com/api/v1/player-mapping?<parámetros>` (sin parámetros no devuelve nada).
- Uso en el proyecto: opcional, para seguir jugadores entre temporadas y equipos (altas y bajas de la plantilla).

## Parámetros

| Parámetro | Notas |
| --- | --- |
| `competition-id`, `season-id` | Filtran el bloque competición-temporada |
| `offline-player-id` o `live-player-id` | Solo uno de los dos. `offline` = ids del sistema estándar (los de Events) |
| `match-date-from`, `match-date-to` | `yyyy-mm-dd`; bloques con partidos en ese rango |
| `all-account-data` | `true` para devolver todo lo licenciado |
| `add-matches-played` | `true` para incluir los partidos de cada jugador |

Ejemplo: `…/api/v1/player-mapping?season-id=90&competition-id=37&offline-player-id=10172&add-matches-played=true`

Si la consulta supera 5,000 registros, la respuesta se envía como archivo JSON en lugar del cuerpo de la respuesta.

## Respuesta (una fila por jugador × competición × temporada × equipo)

`competition_id`, `competition_name`, `season_id`, `season_name`, `offline_team_id`, `live_team_id`, `team_name`, `team_gender`, `earliest_match_date`, `most_recent_match_date`, `offline_player_id`, `live_player_id`, `player_name`, `player_nickname`, `player_height`, `player_weight`, `player_birth_date`, `player_preferred_foot`, país de nacimiento (`offline_country_of_birth_id`, `live_country_of_birth_id`, `country_of_birth_name`) y `matches_played[]` = {offline_match_id, live_match_id, match_date} (siempre el bloque completo, aunque se filtre por fecha).

Nota: la existencia de ids "live" indica que StatsBomb tiene un sistema en vivo; nuestro acceso es al sistema offline.
