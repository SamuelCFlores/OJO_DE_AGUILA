# Player Match Stats v8.0.0

- Endpoint: `GET https://data.statsbombservices.com/api/v8/matches/{match_id}/player-stats`
- Una fila por jugador por partido.
- Nota: Las métricas 360 (espacio, line-breaking passes) valen 0 o faltan en partidos sin 360; usar player_match_360_minutes.
- Campos: 177. Los nombres abajo omiten el prefijo `player_match_` cuando lo tienen (el nombre real es `player_match_<campo>`).
- Tipos: int, float, pct (porcentaje), str, bool, date. Descripciones tal como el PDF de StatsBomb; (sic) marca correcciones.
- Errata: el PDF escribe `layer_match_fhalf_lbp_received`; aquí aparece como `fhalf_lbp_received` (verificar el nombre real en la prueba de humo).

## Identificadores y contexto (7)
- `player_id` (int): The id of the player
- `player_name` (str): The full name of the player
- `team_id` (int): The id of the team
- `team_name` (str): The full name of the playerʼs team
- `match_id` (int): The id of the match
- `minutes` (int): The number of minutes played this match
- `360_minutes` (float): The number of minutes played for this match, or 0 for matches which do not have 360 data

## Fases de juego y transición (Phases of Play) (6)
- `transition_possession_rate` (float): Proportion of the player's possessions that remain in the In Possession Transition state. Ratio in [0, 1]. Absent or null when model output is unavailable.
- `transition_xg` (float): Expected goals the player generates within the In Possession Transition state.
- `transition_obv` (float): On-ball value the player generates within the In Possession Transition state.
- `avg_player_possession_directness` (float): Average player_possession_directness over the player's on-ball events (count-weighted). Unbounded and can be negative, unlike the team's [0, 1] possession_directness.
- `avg_player_possession_directness_in_control` (float): Average player possession directness on events where the possession has reached control_degree = 1 (settled play).
- `avg_player_possession_directness_in_transition` (float): Average player possession directness on events where is_transition = true (unsettled play).

## Balón parado (4)
Nombres autoexplicativos; se listan sin descripción. Jugadas: `corners`, `free_kicks` (tiros libres indirectos), `indirect_free_kicks`, `direct_free_kicks`, `throw_ins`, `sp` (todo balón parado), `penalties`. Patrones: `<jugada>` = cantidad, `<jugada>_xg` = xG generado, `xg_per_<jugada>` = xG por jugada, `shots_from_<jugada>` / `goals_from_<jugada>`, `<jugada>_shot_ratio` / `<jugada>_goal_ratio` = tiros o goles por jugada, `_conceded` = versión en contra, `_pg` / `_90` = por partido / por 90.

`penalties_faced`, `penalties_conceded`, `penalties_won`, `sp_xa`

## Tiros, xG y goles (23)
- `goals` (float): All goals scored by the player, including penalties.
- `goals_conceded` (int): How many goals a goalkeeper conceded (doesnʼt include penalties or own goals)
- `np_goals` (float): All goals scored by the player, excluding penalties.
- `obv_shot` (float): On Ball Value Added (net) from Shots
- `np_psxg` (float): Post Shot xG earned from on-target shots
- `npot_psxg_faced` (float): How much non-penalty on-target post-shot xG a goalkeeper faced
- `shot_touch_ratio` (pct): The amount of shots a player takes as a proportion of their touches of the ball.
- `np_shots` (float): Number of shots not from penalties
- `op_shots` (float): Number of shots from open play
- `shots_blocked` (float): Number of shots blocked
- `np_shots_on_target` (float): Number of non-penalty shots on target
- `npot_shots_faced` (float): How many non-penalty on-target shots a goalkeeper faced
- `touches_inside_box` (float): Successful footed touches inside the box (including shots)
- `np_xg` (float): Non-penalty xG of the player's shots (sic: el PDF dice 'xG assisted').
- `np_xg_per_shot` (float): Non-penalty xG per shot (sic: el PDF dice 'xG assisted per shot').
- `xgbuildup` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession. The buildup version omits xG and xG Assisted to focus on possession work prior to the end of the chain
- `op_xgbuildup` (float): xG buildup in open play
- `xgbuildup_per_possession` (float): xG buildup per possession
- `op_xgbuildup_per_possession` (float): xG buildup per possession (open play)
- `xgchain` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession.
- `op_xgchain` (float): xG chain in open play
- `xgchain_per_possession` (float): xG chain per possession
- `op_xgchain_per_possession` (float): xG chain per possession (open play)

## Presión y defensa (26)
- `aggressive_actions` (float): Tackles, pressure events and fouls recorded within 2 seconds of an opposition ball receipt
- `ball_recoveries` (int): Number of ball recoveries
- `challenge_ratio` (pct): Percentage of time a player makes a tackle when going into a duel vs getting dribbled past.
- `clearances` (?): Number of clearances.
- `counterpressure_duration_avg` (float): Average duration of counterpressures
- `counterpressure_duration_total` (float): Total duration of counterpressures
- `counterpressured_action_fails` (float): Number of counterpressures attempted that failed.
- `counterpressures` (float): Number of counterpressures. Counterpressures are pressures exerted within 5 seconds of a turnover.
- `da_aggressive_distance` (float): An average value of how far forward from the goal a goalkeeper is coming to perform defensive actions
- `dribbled_past` (float): How often a player fails a challenge and is dribbled past.
- `fhalf_ball_recoveries` (int): How many ball recoveries the player made in the opposition (final) half of the pitch
- `interceptions` (float): Number of interceptions.
- `obv_defensive_action` (float): On Ball Value Added (net) from Defensive Actions
- `pressure_duration_avg` (float): Average duration of pressures.
- `pressure_duration_total` (float): Total duration of pressures.
- `pressure_regains` (float): Times a player won the ball back within 5 seconds of the player pressuring an opponent.
- `pressured_action_fails` (float): Times a player failed to win the ball back within 5 seconds of the player pressuring an opponent.
- `pressured_long_balls` (float): Number of clearances or long balls attempted while under pressure.
- `pressures` (float): The number of times a player pressures an opposition player.
- `tackles` (float): Successful challenges made.
- `unpressured_long_balls` (float): Times a player plays a long ball while not under pressure
- `defensive_actions` (int): Tackles, pressure events and fouls recorded
- `defensive_responsibility_actions` (float): The number of defensive actions a player made in response to attacking events.
- `expected_defensive_actions` (float): Responsibility-based expectation of how many defensive actions a player should be involved in, given the situations faced while on the pitch. Measures defensive opportunity / load.
- `defensive_actions_above_expectation` (float): Difference between actual defensive actions performed and expected defensive actions. Measures defensive aggressiveness or passivity relative to opportunity.
- `obv_conceded_responsibility_weighted` (float): The OBV conceded by a player weighted by their defensive responsibility probability to attacking events.

## 360: espacio y pases que rompen líneas (57)
Nombres autoexplicativos; se listan sin descripción. `lbp` = line-breaking pass (pase que cruza una línea defensiva), `fhalf_` = en campo rival, `f3_` = en el último tercio, `ball_receipts_in_space_N` = recepciones con al menos N m libres (2, 5, 10), `lbp_to_space_N` = pase que rompe líneas y llega con N m libres, `_received` = como receptor, `average_..._distance` = espacio promedio, `obv_lbp` = OBV de esos pases, `*_360` = conteos solo en partidos con 360.

`average_space_received_in`, `average_fhalf_space_received_in`, `average_f3_space_received_in`, `ball_receipts_in_space_10`, `ball_receipts_in_space_2`, `ball_receipts_in_space_5`, `fhalf_ball_receipts_in_space_10`, `fhalf_ball_receipts_in_space_2`, `fhalf_ball_receipts_in_space_5`, `f3_ball_receipts_in_space_10`, `f3_ball_receipts_in_space_2`, `f3_ball_receipts_in_space_5`, `lbp`, `lbp_completed`, `fhalf_lbp_completed`, `f3_lbp_completed`, `fhalf_lbp`, `f3_lbp`, `obv_lbp`, `fhalf_obv_lbp`, `f3_obv_lbp`, `lbp_received`, `fhalf_lbp_received`, `f3_lbp_received`, `average_lbp_to_space_distance`, `fhalf_average_lbp_to_space_distance`, `f3_average_lbp_to_space_distance`, `lbp_to_space_10_received`, `fhalf_lbp_to_space_10_received`, `f3_lbp_to_space_10_received`, `lbp_to_space_2_received`, `fhalf_lbp_to_space_2_received`, `f3_lbp_to_space_2_received`, `lbp_to_space_5_received`, `fhalf_lbp_to_space_5_received`, `f3_lbp_to_space_5_received`, `average_lbp_to_space_received_distance`, `fhalf_average_lbp_to_space_received_distance`, `f3_average_lbp_to_space_received_distance`, `lbp_to_space_10`, `fhalf_lbp_to_space_10`, `f3_lbp_to_space_10`, `lbp_to_space_2`, `fhalf_lbp_to_space_2`, `f3_lbp_to_space_2`, `lbp_to_space_5`, `fhalf_lbp_to_space_5`, `f3_lbp_to_space_5`, `passes_360`, `obv_passes_360`, `fhalf_passes_360`, `fhalf_obv_passes_360`, `f3_passes_360`, `f3_obv_passes_360`, `ball_receipts_360`, `fhalf_ball_receipts_360`, `f3_ball_receipts_360`

## Pases, progresión y posesión (37)
- `assists` (float): Number of assists.
- `op_assists` (float): Number of open play assists
- `backward_passes` (float): Number of backward passes
- `box_cross_ratio` (pct): What percentage of a player's completed passes into the box are crosses. See Event Specification for details of cross location definition.
- `crosses` (float): Completed crosses.
- `crosses_into_box` (float): Number of crosses into the box
- `crossing_ratio` (pct): Percentage of attempted crosses that are successful and received by a teammate
- `deep_completions` (int): Number of deep completions
- `deep_progressions` (float): Passes and dribbles/carries into the opposition final third.
- `dispossessions` (float): Number of times a player loses the ball by getting tackled.
- `op_f3_backward_passes` (float): Number of open play, final third backward passes
- `op_f3_forward_passes` (float): Number of open play, final third forward passes
- `op_f3_passes` (float): Number of open play, final third passes
- `op_f3_sideways_passes` (float): Number of open play, final third sideways passes
- `forward_passes` (float): How many forward passes a player makes
- `key_passes` (float): Passes that create shots for teammates. Can also be seen to be referred to as "shot assists" or "chances created"
- `op_key_passes` (float): Open play passes that create shots for teammates. Can also be seen to be referred to as "shot assists" or "chances created"
- `long_ball_ratio` (pct): Percentage of attempted long balls that are actually completed.
- `long_balls` (float): Number of completed long balls
- `obv_pass` (float): On Ball Value Added (net) from Passes
- `obv_dribble_carry` (float): On Ball Value Added (net) from Dribbles and Carries
- `passes` (float): Number of attempted passes
- `op_passes` (float): Number of attempted passes in open play.
- `passes_inside_box` (float): Passes completed starting and ending inside the box.
- `passes_into_box` (float): Successful passes into the box from outside the box.
- `op_passes_into_box` (float): Successful passes into the box from outside the box (open play).
- `passing_ratio` (pct): Percentage of all passes attempted that were completed.
- `positive_outcome_score` (pct): How frequently is the player involved in sequences that resolve with a positive outcome (shot, free kick in the attacking half or a corner) while on the pitch
- `possession` (pct): How much possession a player has per match.
- `sideways_passes` (float): Number of sideways passes
- `successful_crosses` (float): Number of successful crosses
- `successful_long_balls` (float): Number of successful long balls
- `successful_passes` (float): Number of successful passes
- `through_balls` (float): A completed pass splitting the defence for a teammate to run onto.
- `touches` (float): Number of successful footed touches
- `xa` (float): xG assisted.
- `op_xa` (float): xG assisted from open play.

## OBV (On Ball Value) (2)
- `obv` (float): On Ball Value Added (net) total (all event types)
- `obv_gk` (float): On Ball Value Added (net) Goalkeeper

## Regate y duelos (9)
- `aerial_ratio` (pct): Percentage of aerial duels a player enters that they win
- `aerials` (float): Number of aerial duels
- `dribbles` (float): How often a player successfully dribbles past an opponent
- `dribbles_faced` (float): How often a player faces a dribble
- `fouls` (float): How many fouls a player commits
- `fouls_won` (float): How many times a player is fouled.
- `successful_aerials` (float): Number of successful aerials
- `turnovers` (float): How often a player loses the ball via a miscontrol or a failed dribble.
- `predicted_headers` (float): Predicted headers won in a match, based on the difficulty of each duel.

## Portero (6)
- `ccaa` (pct): Claims or CCAA% (Claimable Collection Attempts over Average), is a measure of how likely the goalkeeper is to attempt to claim a "claimable" pass, versus the average goalkeeper attempted claim rate
- `claim_success` (pct): How many of a goalkeeperʼs claim attempts are successful
- `gk_positioning_error` (float): How far on average a goalkeeper is from the optimal position for facing a shot
- `gsaa` (float): How many goals did the keeper save/concede versus expectation (post-shot xG faced)
- `gsaa_ratio` (pct): The measure of goals saved above average, as a percentage of shots faced by the goalkeeper
- `save_ratio` (pct): Percentage of on-target shots that were saved by the goalkeeper
