# APIs de StatsBomb: índice

Referencias condensadas de los 10 PDFs oficiales (versión indicada en cada archivo). Lee solo el archivo que necesites.

| API | Versión | Endpoint | Archivo |
| --- | --- | --- | --- |
| Competitions | v4 | `data.statsbombservices.com/api/v4/competitions` | `competitions.md` |
| Matches | v6 | `data.statsbombservices.com/api/v6/competitions/{c}/seasons/{s}/matches` | `matches.md` |
| Events | v11 | `data.statsbombservices.com/api/v11/events/{match_id}` | `events.md` |
| 360 Frames | v2 | `data.statsbombservices.com/api/v2/360-frames/{match_id}` | `frames_360.md` |
| Lineups | v5 | `data.statsbomb.com/api/v5/lineups/{match_id}` | `lineups.md` |
| Team Match Stats | v4 | `data.statsbomb.com/api/v4/matches/{match_id}/team-stats` | `team_match_stats.md` |
| Team Season Stats | v4 | `data.statsbombservices.com/api/v4/competitions/{c}/seasons/{s}/team-stats` | `team_season_stats.md` |
| Player Match Stats | v8 | `data.statsbombservices.com/api/v8/matches/{match_id}/player-stats` | `player_match_stats.md` |
| Player Season Stats | v7 | `data.statsbombservices.com/api/v7/competitions/{c}/seasons/{s}/player-stats` | `player_season_stats.md` |
| Player Mapping | v1 | `data.statsbomb.com/api/v1/player-mapping?…` | `player_mapping.md` |

Todas las URLs usan `https://`. Las respuestas son JSON.

## Acceso

- Credenciales: las "general API notes" de StatsBomb no venían en los PDFs. Supuesto a confirmar en la prueba de humo: usuario y contraseña por HTTP Basic, como hace el paquete oficial `statsbombpy`.
- Sin credenciales, `data.statsbombservices.com` responde 302 hacia `/login` (probado el 4 de octubre de 2026).
- Los PDFs usan dos dominios (`data.statsbombservices.com` y `data.statsbomb.com`). El cliente debe probar el indicado y, si falla, el otro.
- Las versiones anteriores siguen disponibles cambiando el número en la URL; usar siempre las de esta tabla.
- Paquetes oficiales: StatsBombR y statsbombpy. Probablemente no cubren Events v11 ni 360 v2; por eso usamos un cliente propio.

## Qué archivo leer para qué

- Encontrar Liga MX, torneos y partidos de un entrenador → `competitions.md`, `matches.md`.
- Posesiones, fases de juego (Phases of Play), xG, OBV, presión, clusters de pase → `events.md`.
- Voronoi, espacio, pases que rompen líneas → `frames_360.md`.
- Formaciones, cambios tácticos, sustituciones → `lineups.md`.
- Perfil por partido y línea base de la liga → `team_match_stats.md`, `team_season_stats.md`.
- Roles y rendimiento por jugador → `player_match_stats.md`, `player_season_stats.md`.
