# Lineups v5.0.0 (StatsBomb)

- Endpoint: `GET https://data.statsbomb.com/api/v5/lineups/{match_id}` (ojo: dominio `data.statsbomb.com`).
- Respuesta: arreglo JSON con un objeto por equipo: `team_id`, `team_name`, `lineup[]`, `formations[]`, `events[]`.
- Novedad v5: rating HOPS (habilidad aérea) por jugador.

## `lineup[]` (jugadores en la hoja)

`player_id`, `player_name`, `player_nickname`, `player_gender`, `player_weight` (kg), `player_height` (cm), `birth_date`, `jersey_number`, `country` {id, name}, `positions[]`, `stats` {goals, assists, own_goals, penalties_missed, penalties_saved, penalties_scored}, `skills` {HOPS: {rating 0–1, raw_rating}}.

## `positions[]` (cada tramo del jugador en una posición)

| Campo | Notas |
| --- | --- |
| `position_id`, `position` | Ids 1–25 (ver `events.md`) |
| `from`, `to` | `HH:MM:SS.mmm`, se reinicia por periodo |
| `from_period`, `to_period` | 1–5 |
| `start_reason` | Starting XI, Tactical Shift, Substitution - On, Substitution - On (Tactical), Substitution - On (Injury), Substitution - On (Off Camera), Player On, Player On (Off Camera) |
| `end_reason` | Final Whistle, Tactical Shift, Substitution Off, Substitution - Off (Tactical), Substitution - Off (Injury), Substitution - Off (Off Camera), Player Off, Player Off (Off Camera), Player Off (Permanent), Red Card, Second Yellow Card, Starting XI |
| `counterpart_id`, `counterpart_name` | El otro jugador del cambio |

Uso clave: separar **sustituciones tácticas** (decisión del entrenador) de las de **lesión** (comparación natural).

## `formations[]`

`period`, `timestamp`, `reason` (`Starting XI` o `Tactical Shift`), `formation` (entero, p. ej. 433). Cronología de cambios de sistema con su minuto.

## `events[]` (eventos simplificados)

`player_id`, `player_name`, `period`, `timestamp`, `type` (Foul Committed, Bad Behaviour, Half Start, Half End, Shot, Penalty, Goal Keeper), `outcome` (Yellow Card, Second Yellow, Red Card, Goal, Off T, Penalty Saved, Saved To Post).
