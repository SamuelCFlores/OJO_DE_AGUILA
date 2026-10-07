# Events v11.0.0 (StatsBomb)

- Endpoint: `GET https://data.statsbombservices.com/api/v11/events/{match_id}` (la v10 sigue en `/api/v10/events/{match_id}`).
- Respuesta: arreglo JSON con todos los eventos del partido, de ambos equipos. Los detalles de cada tipo vienen anidados en un objeto con el nombre del tipo (`pass`, `shot`, `carry`…).
- Novedad v11: campos de **Phases of Play** (solo juego abierto, no balón parado): `control_degree`, `is_transition`, `is_controlled_possession`, `possession_directness`, `player_possession_directness`, `location_bucket`. Además `advantage` en Offside y la falta "8 Seconds" (id 25). Verificar que vengan poblados en partidos 2023–2025.

## Campos de nivel superior

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | uuid | Id único del evento |
| `index` | int | Orden dentro del partido (1…n) |
| `period` | int | 1 y 2 = tiempos, 3 y 4 = prórroga, 5 = penales |
| `timestamp` | str | `HH:MM:SS.mmm`; se reinicia en cada periodo |
| `minute`, `second` | int | Reloj de partido; el 2.º tiempo arranca en 45, la prórroga en 90 |
| `type` | {id, name} | Tipo de evento (lista abajo) |
| `possession` | int | Número de posesión. Inicia una nueva cuando un equipo establece control; puede ser nueva aunque el equipo sea el mismo (p. ej., pase bloqueado que sale a lateral propio) |
| `possession_team` | {id, name} | Equipo que inició la posesión; aparece también en eventos del rival dentro de esa posesión |
| `play_pattern` | {id, name} | Patrón de juego (lista abajo) |
| `team` | {id, name} | Equipo del evento |
| `attacking_direction` | str | `left_to_right` / `right_to_left`, relativo a la cámara |
| `player`, `position` | {id, name} | Jugador y posición al momento del evento (ids de posición abajo) |
| `location` | [x, y] | Coordenadas en cancha 120×80; centro = (60, 40) |
| `duration` | float | Segundos, si aplica |
| `under_pressure` | bool | Acción hecha bajo presión (solo aparece si es TRUE) |
| `off_camera` | bool | Evento con cámara apagada; datos inferidos (solo si TRUE) |
| `out` | bool | El balón salió como resultado del evento |
| `related_events` | [uuid] | Eventos relacionados (p. ej., tiro ↔ portero ↔ bloqueo) |
| `tactics` | {formation, lineup[]} | Solo en `Starting XI` y `Tactical Shift`; lineup = {jersey_number, player{id,name}, position{id,name}} |
| `obv_for_before/after/net` | float | Probabilidad de anotar en la posesión antes/después del evento y su cambio |
| `obv_against_before/after/net` | float | Probabilidad de recibir gol en la siguiente posesión, antes/después y cambio |
| `obv_total_net` | float | Cambio neto en diferencia de goles esperada en las 2 siguientes posesiones |
| `set_piece_phase` | int | 1 o 2; solo durante jugadas a balón parado |
| `counterpress` | bool | Acción de presión dentro de 5 s de una pérdida en juego abierto |
| `defensive_responsibility` | obj | `categories` (`pressure_like`, `interception_like`), `probability_sum`, `players[]` = {player_id, probability, pressure_like_probability, interception_like_probability}, ordenado de mayor a menor probabilidad |
| `control_degree` | float | Estabilidad de la posesión; sube hasta 1.0 = posesión establecida. Ausente si no hay salida del modelo |
| `is_transition` | bool | TRUE si `control_degree` < 1 (juego no asentado) |
| `is_controlled_possession` | bool | Constante en la posesión: TRUE si alcanzó `control_degree` = 1 en algún momento |
| `possession_directness` | float | [0, 1]; ~1 = progresión sostenida a portería, ~0 = circulación. Igual para todos los eventos de la posesión |
| `player_possession_directness` | float | Log-odds de progresión durante la conducción del jugador; positivo = avanza, negativo = retrocede |
| `location_bucket` | str | Tercio donde inicia el evento según la dirección del equipo en posesión: `defensive_third`, `midfield_third`, `final_third` |

OBV viene en: Carry, pases (raso, bajo, alto), Dribble, Shot, Block, Tackle, Interception, Clearance, Foul Committed y acciones de portero (Collection, Sweep, Save, Concede). Falta cuando un evento fuera del balón interrumpe la secuencia.

## Tipos de evento (`type.id` / `type.name`)

2 Ball Recovery · 3 Dispossessed · 4 Duel · 5 Camera On (obsoleto) · 6 Block · 8 Offside (solo de tiros o despejes; los de pase van en el outcome del pase) · 9 Clearance · 10 Interception · 14 Dribble · 16 Shot · 17 Pressure · 18 Half Start · 19 Substitution · 20 Own Goal Against · 21 Foul Won · 22 Foul Committed · 23 Goal Keeper · 24 Bad Behaviour · 25 Own Goal For · 26 Player On · 27 Player Off · 28 Shield · 30 Pass · 33 50/50 · 34 Half End · 35 Starting XI · 36 Tactical Shift · 37 Error · 38 Miscontrol · 39 Dribbled Past · 40 Injury Stoppage · 41 Referee Ball-Drop · 42 Ball Receipt · 43 Carry

## Patrones de juego (`play_pattern`)

1 Regular Play · 2 From Corner · 3 From Free Kick · 4 From Throw In · 5 Other · 6 From Counter · 7 From Goal Kick · 8 From Keeper · 9 From Kick Off

**From Counter** (derivado, no recolectado): la posesión inicia con una pérdida en juego abierto fuera del último tercio del equipo que contraataca, es al menos 75 % directa hacia portería y avanza al menos 18 yardas.

## Objetos por tipo de evento

- **50/50** `outcome`: 108 Won, 109 Lost, 147 Success To Team, 148 Success To Opposition.
- **Bad Behaviour** `card`: 7 Yellow, 6 Second Yellow, 5 Red.
- **Ball Receipt** `outcome`: 9 Incomplete (sin outcome = recepción completa).
- **Ball Recovery**: `offensive`, `recovery_failure` (bool).
- **Block**: `deflection`, `offensive`, `save_block` (bloqueo de un tiro que iba a puerta).
- **Carry**: `end_location` [x, y].
- **Clearance**: `aerial_won`, `duel_win_probability` (modelo HOPS), `body_part` (37 Head, 38 Left Foot, 40 Right Foot, 70 Other) y booleanos `head`, `left_foot`, `right_foot`, `other`.
- **Dribble**: `overrun`, `nutmeg`, `no_touch`, `outcome` (8 Complete, 9 Incomplete).
- **Duel**: `type` (10 Aerial Lost, 11 Tackle), `outcome` (4 Won, 13 Lost In Play, 14 Lost Out, 15 Success, 16 Success In Play, 17 Success Out), `duel_win_probability`, `hops_rating`, `hops_raw_rating`, `hops_opponent_rating`, `hops_opponent_raw_rating`.
- **Foul Committed**: `offensive`, `advantage`, `penalty`, `card` (7/6/5), `type` (19 6 Seconds, 20 Backpass Pick, 21 Dangerous Play, 22 Dive, 23 Foul Out, 24 Handball, 25 8 Seconds).
- **Foul Won**: `defensive`, `advantage`, `penalty`.
- **Goal Keeper**: `position` (42 Moving, 43 Prone, 44 Set), `technique` (45 Diving, 46 Standing), `body_part` (35 Both Hands, 36 Chest, 37 Head, 38 Left Foot, 39 Left Hand, 40 Right Foot, 41 Right Hand), `type` (25 Collected, 26 Goal Conceded, 27 Keeper Sweeper, 28 Penalty Conceded, 29 Penalty Saved, 30 Punch, 31 Save, 32 Shot Faced, 33 Shot Saved, 34 Smother, 113 Shot Saved Off T, 114 Shot Saved To Post, 110 Saved To Post, 109 Penalty Saved To Post), `outcome` (47 Claim, 48 Clear, 49 Collected Twice, 50 Fail, 51 In Play, 52 In Play Danger, 53 In Play Safe, 55 No Touch, 56 Saved Twice, 15 Success, 58 Touched In, 59 Touched Out, 4 Won, 16 Success In Play, 17 Success Out, 13 Lost In Play, 14 Lost Out, 117 Punched Out). Todo tiro tiene un evento de portero relacionado.
- **Half End**: `early_video_end`, `match_suspended`. **Half Start**: `late_video_start`.
- **Injury Stoppage**: `in_chain` (el balón era del equipo del lesionado).
- **Interception** `outcome`: 1 Lost, 13 Lost In Play, 14 Lost Out, 15 Success, 16 Success In Play, 17 Success Out, 4 Won.
- **Miscontrol**: `aerial_won`, `duel_win_probability`.
- **Offside**: `advantage`.
- **Player Off**: `permanent`.
- **Substitution**: `replacement` {id, name} (entra; `player` es quien sale), `outcome` (102 Injury, 103 Tactical).

### Pass

- `recipient` {id, name} (también el destinatario de pases incompletos), `length` (yardas), `angle` (radianes; 0 = hacia adelante, positivo = horario, ±π = hacia atrás), `end_location` [x, y].
- `height`: 1 Ground Pass, 2 Low Pass (bajo el hombro), 3 High Pass.
- `type`: 61 Corner, 62 Free Kick, 63 Goal Kick, 64 Interception, 65 Kick Off, 66 Recovery, 67 Throw-in.
- `outcome`: 9 Incomplete, 74 Injury Clearance, 75 Out, 76 Pass Offside, 77 Unknown. **Sin `outcome` = pase completo.**
- `technique`: 104 Inswinging, 105 Outswinging, 107 Straight (córners), 108 Through Ball. Booleanos equivalentes: `inswinging`, `outswinging`, `straight`, `through_ball`.
- `body_part`: 68 Drop Kick, 37 Head, 69 Keeper Arm, 38 Left Foot, 70 Other, 40 Right Foot, 106 No Touch.
- Booleanos: `cross`, `cut_back`, `switch` (recorre más del 50 % del ancho, ~40 yd), `shot_assist`, `goal_assist`, `backheel`, `deflected`, `miscommunication`, `aerial_won`, `no_touch`.
- `assisted_shot_id` (uuid del tiro que asistió), `duel_win_probability`, `xclaim` (probabilidad de que el portero atrape el balón).
- `pass_success_probability`: probabilidad estimada de completar el pase según ubicación, contexto y destino.
- `pass_cluster_id` (0–59), `pass_cluster_label`, `pass_cluster_probability`: 60 clusters descritos por tercio de inicio, lado, largo (largo = más de ~35 yd), dirección y altura modal. La etiqueta viene en el dato.

### Shot

- `statsbomb_xg`: probabilidad de gol de la situación (incluye posición del portero y bloqueadores, no la ejecución).
- `shot_execution_xg` y `shot_execution_xg_uplift` (ejecución: colocación y velocidad; el uplift puede ser negativo), `gk_save_difficulty_xg` (solo tiros a puerta no bloqueados), `gk_positioning_xg_suppression`, `gk_shot_stopping_xg_suppression`.
- `type`: 61 Corner, 62 Free Kick, 65 Kick Off, 87 Open Play, 88 Penalty.
- `outcome`: 96 Blocked, 97 Goal, 98 Off T, 99 Post, 100 Saved, 101 Wayward, 115 Saved Off T, 116 Saved To Post.
- `technique`: 89 Backheel, 90 Diving Header, 91 Half Volley, 92 Lob, 93 Normal, 94 Overhead Kick, 95 Volley. `body_part`: 37 Head, 38 Left Foot, 40 Right Foot, 70 Other.
- `key_pass_id`, `end_location` [x, y] o [x, y, z] (z = altura en yardas), `first_time`, `follows_dribble`, `open_goal`, `one_on_one`, `deflected`, `redirect`, `aerial_won`, `duel_win_probability`, `kick_off`, `saved_off_target`, `saved_to_post`, `shot_shot_assist`, `shot_goal_assist`.
- `freeze_frame`: jugadores relevantes al momento del tiro, **con identidad**: {location [x, y], player {id, name}, position {id, name}, teammate}.

## Posiciones (`position.id`)

1 GK · 2 RB · 3 RCB · 4 CB · 5 LCB · 6 LB · 7 RWB · 8 LWB · 9 RDM · 10 CDM · 11 LDM · 12 RM · 13 RCM · 14 CM · 15 LCM · 16 LM · 17 RW · 18 RAM · 19 CAM · 20 LAM · 21 LW · 22 RCF · 23 ST · 24 LCF · 25 SS (Secondary Striker, en desuso)

## Notas

- **Presión (`under_pressure`)**: un evento con balón está bajo presión si se traslapa con la duración de un evento Pressure; un pase que llega durante la presión se marca como recibido bajo presión. Desde v4 también aplica a duelos y regates aunque no haya evento Pressure.
- **Coordenadas**: cancha de 120×80 (el anexo del PDF es una imagen). Supuesto a verificar en la prueba de humo: cada evento viene en la perspectiva del equipo que lo ejecuta, atacando hacia x = 120; las acciones defensivas deben reorientarse antes de mezclarse con las del rival.
- **Cross** y **cutback** se definen por zonas de origen y destino (anexos en imagen); usar los booleanos del dato.
- `data_version` y `shot_fidelity_version` vienen en Matches (`metadata`). Fidelidad de tiro 2 = coordenadas de alta precisión en tiros y freeze frames.
