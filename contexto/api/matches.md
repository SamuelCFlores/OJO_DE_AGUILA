# Matches v6.0.0 (StatsBomb)

- Endpoint: `GET https://data.statsbombservices.com/api/v6/competitions/{competition_id}/seasons/{season_id}/matches` (ids desde Competitions).
- Respuesta: arreglo JSON, un objeto por partido. Es la fuente de **entrenador, localía, fase del torneo y disponibilidad del 360**.

## Campos

| Campo | Tipo | Notas |
| --- | --- | --- |
| `match_id` | int | Necesario para Events, 360, Lineups y stats por partido |
| `competition`, `season` | {id, name} | |
| `country_name` | str | |
| `match_date`, `kick_off` | date, time | `"2018-03-09"`, `"16:00:00.000"` |
| `stadium`, `stadium_country` | {id, name}, str | |
| `referee_name`, `referee_country` | {id, name} | |
| `home_team`, `away_team` | {id, name} | |
| `home_team_manager`, `away_team_manager` | objeto (o lista) | {id, name, nickname, dob, country {id, name}} → **filtrar partidos por entrenador** |
| `home_team_gender`, `home_team_youth`, `home_team_group`, `home_team_country` | | Igual para `away_` |
| `home_score`, `away_score` | int | Marcador final |
| `attendance`, `behind_closed_doors`, `neutral_ground` | int, bool, bool | |
| `collection_status` | str | Estado de recolección (abajo); usar solo `Complete` |
| `play_status` | str | Normal, Postponed, Cancelled, Abandoned, Forfeited |
| `match_status` | str | `available` = eventos descargables; también deleted, scheduled |
| `match_status_360` | str | `available` = 360 descargable; `scheduled` = pendiente; `unscheduled` = no tendrá 360 |
| `match_week` | int | Jornada |
| `competition_stage` | {id, name} | Fase del torneo (abajo) |
| `last_updated`, `last_updated_360` | datetime | Si cambian después de descargar, StatsBomb corrigió datos: volver a descargar |
| `metadata` | obj | `data_version` (p. ej. "1.1.0"), `shot_fidelity_version` (1 o 2) |

## `collection_status`

Unassigned (sin iniciar) · InProgress · WithoutLocation (ubicando eventos) · WithoutFreezeFrame (falta freeze frame de tiros) · PendingValidation / Validating / Invalid / WithoutDirection (validación) · **Complete** (terminado) · Postponed · NoVidError (sin video) · IncVidError (video incompleto) · PoorVidError (video malo) · ErrorAbandoned · ErrorCancelled · ErrorForfeit

## `competition_stage` relevantes para Liga MX

1 Regular Season · 2 Play-In Round · 11 Quarter-finals · 15 Semi-finals · 26 Final · 28 Play-offs. (El catálogo completo incluye fases de otras ligas; verificar cuáles usa Liga MX en los datos.)
