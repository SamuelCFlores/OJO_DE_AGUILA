# Inspección de las APIs

Generado por `scripts/01_inspector.py` el 2026-10-09. Muestra: 10 partidos del equipo 1229 con 360, 2 por temporada. Solo conteos y porcentajes; sin datos crudos.

## Cobertura por torneo

Phases of Play e `is_transition` se miden sobre eventos de juego abierto; las demás, sobre todos los eventos, pases o tiros.

| Torneo | Partidos | Phases of Play (control_degree) | is_transition | OBV | pass_cluster_id | pass_success_probability | xG en tiros | Eventos con frame 360 | Frames con área visible | Jugadores visibles (prom.) | Orientación del actor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AP21 | 1 | 86.6 % | 86.6 % | 56.4 % | 91.6 % | 99.2 % | 100.0 % | 79.0 % | 100.0 % | 13.0 | OK |
| CL22 | 1 | 81.7 % | 81.7 % | 56.2 % | 86.3 % | 98.7 % | 100.0 % | 88.0 % | 100.0 % | 11.6 | OK |
| AP22 | 1 | 84.9 % | 84.9 % | 56.9 % | 91.9 % | 99.6 % | 100.0 % | 90.7 % | 100.0 % | 12.5 | OK |
| CL23 | 1 | 82.7 % | 82.7 % | 54.2 % | 91.4 % | 99.5 % | 100.0 % | 86.2 % | 100.0 % | 12.5 | OK |
| AP23 | 1 | 85.0 % | 85.0 % | 56.2 % | 92.5 % | 99.8 % | 100.0 % | 93.7 % | 100.0 % | 13.1 | OK |
| CL24 | 1 | 87.4 % | 87.4 % | 57.9 % | 93.3 % | 99.5 % | 100.0 % | 88.6 % | 100.0 % | 12.5 | OK |
| AP24 | 1 | 88.2 % | 88.2 % | 57.9 % | 93.3 % | 99.7 % | 100.0 % | 90.1 % | 100.0 % | 15.1 | OK |
| CL25 | 1 | 83.1 % | 83.1 % | 57.6 % | 90.5 % | 99.9 % | 100.0 % | 89.8 % | 100.0 % | 11.9 | OK |
| AP25 | 1 | 84.8 % | 84.8 % | 58.5 % | 91.6 % | 99.3 % | 100.0 % | 91.9 % | 100.0 % | 14.5 | OK |
| CL26 | 1 | 84.3 % | 84.3 % | 58.9 % | 90.4 % | 98.4 % | 100.0 % | 80.5 % | 100.0 % | 16.2 | OK |

## Campos de nivel superior en Events

Presencia sobre 32,287 eventos. Un campo ausente o muy bajo que el framework use debe revisarse (regla 5).

| Campo | Presencia |
| --- | --- |
| id | 100.0 % |
| index | 100.0 % |
| period | 100.0 % |
| timestamp | 100.0 % |
| minute | 100.0 % |
| second | 100.0 % |
| type | 100.0 % |
| possession | 100.0 % |
| possession_team | 100.0 % |
| play_pattern | 100.0 % |
| obv_for_after | 100.0 % |
| obv_for_before | 100.0 % |
| obv_for_net | 100.0 % |
| obv_against_after | 100.0 % |
| obv_against_before | 100.0 % |
| obv_against_net | 100.0 % |
| obv_total_net | 100.0 % |
| team | 100.0 % |
| attacking_direction | 99.8 % |
| player | 99.5 % |
| position | 99.5 % |
| location_bucket | 99.0 % |
| location | 99.0 % |
| related_events | 97.4 % |
| possession_directness | 92.8 % |
| control_degree | 84.8 % |
| is_transition | 84.8 % |
| is_controlled_possession | 84.8 % |
| player_possession_directness | 79.5 % |
| duration | 74.4 % |
| defensive_responsibility | 51.5 % |
| pass | 28.2 % |
| carry | 22.6 % |
| under_pressure | 19.6 % |
| set_piece_phase | 8.4 % |
| ball_receipt | 2.9 % |
| counterpress | 2.8 % |
| duel | 2.1 % |
| out | 1.5 % |
| off_camera | 1.3 % |
| clearance | 1.2 % |
| goalkeeper | 0.9 % |
| dribble | 0.8 % |
| shot | 0.7 % |
| interception | 0.5 % |
| foul_won | 0.3 % |
| substitution | 0.2 % |
| foul_committed | 0.2 % |
| ball_recovery | 0.2 % |
| 50_50 | 0.2 % |
| tactics | 0.2 % |
| block | 0.1 % |
| injury_stoppage | 0.0 % |
| bad_behaviour | 0.0 % |
| miscontrol | 0.0 % |

## Lineups

- Motivos de cambio de formación: {'Starting XI': 20, 'Tactical Shift': 16}
- Formaciones más frecuentes: {4231: 8, 352: 7, 4141: 5, 442: 4, 41212: 2, 4411: 2, 3412: 2, 3421: 2}

## Team Match Stats

Campos por fila: 205.

## Tamaño y estimación de la descarga

| API | KB por partido (gzip) |
| --- | --- |
| events | 674 |
| frames_360 | 469 |
| lineups | 4 |
| team_match_stats | 3 |
| player_match_stats | 17 |

- Partidos válidos de la liga: 1,701; del equipo: 213.
- Descarga de `scripts/02_descarga.py` (niveles 1-4): ~252 MB.
- Con `--liga-completa` (nivel 5): ~1951 MB más.
