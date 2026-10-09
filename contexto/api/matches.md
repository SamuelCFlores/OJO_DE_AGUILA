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

## Verificado con la API real (prueba de humo, 2026-10-07)

- `home_team` / `away_team` **no** traen `{id, name}`: traen `home_team_id`, `home_team_name` (y `away_team_id`, `away_team_name`) dentro del objeto.
- `season` trae `season_id` y `season_name` (no `id`/`name`); `ojo.datos.tablas` acepta ambas formas (verificado el 9 oct).
- Campos de nivel superior observados: `attendance`, `away_score`, `away_team`, `behind_closed_doors`, `collection_status`, `competition`, `competition_stage`, `home_score`, `home_team`, `kick_off`, `last_updated`, `last_updated_360`, `match_date`, `match_id`, `match_status`, `match_status_360`, `match_week`, `metadata`, `neutral_ground`, `play_status`, `referee`, `season`, `stadium`. No aparecen arriba `home_team_manager`/`away_team_manager`, `country_name`, `referee_name` ni `stadium_country`.
- El entrenador viene en `home_team.managers` / `away_team.managers` (objeto o lista con `id`, `name`), no en `home_team_manager`.
- `season_id` es el **año** (p. ej. 2023/2024), no el torneo: junta Apertura y Clausura (~340 partidos). El torneo se distingue con `competition_stage.name`, que en Liga MX usa nombres como `Apertura`, `Clausura`, `Apertura - Quarter-finals`, `Clausura - Final`, `Apertura - Reclasificación` (la grafía varía: `Clausura - Reclasificacion`, `Final`/`Finals`).
- `"liga mx"` en `competition_name` coincide con dos competiciones: 73 `Liga MX` (`male`, con 360) y 1438 `Liga MX Femenil` (`female`, sin 360). Filtrar por `competition_gender`.
