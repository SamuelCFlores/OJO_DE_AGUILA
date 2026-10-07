# Player Season Stats v7.0.0

- Endpoint: `GET https://data.statsbombservices.com/api/v7/competitions/{competition_id}/seasons/{season_id}/player-stats`
- Una fila por jugador por equipo y torneo; casi todo por 90 minutos (sufijo _90).
- Nota: Para métricas 360 convertir de per-90 a totales con player_season_360_minutes, no con player_season_minutes.
- Campos: 232. Los nombres abajo omiten el prefijo `player_season_` cuando lo tienen (el nombre real es `player_season_<campo>`).
- Tipos: int, float, pct (porcentaje), str, bool, date. Descripciones tal como el PDF de StatsBomb; (sic) marca correcciones.

## Identificadores y contexto (22)
- `player_id` (int): The id of the player
- `player_name` (str): The full name of the player
- `team_id` (int): The id of the team
- `team_name` (str): The full name of the playerʼs team
- `competition_id` (int): The id of the competition
- `competition_name` (str): The title of the competition
- `season_id` (int): The id of the season
- `season_name` (str): A description of the season (e.g. “2020/2021ˮ)
- `country_id` (int): The id of the country the competition season was in
- `birth_date` (date): The date of birth of the player
- `player_female` (bool): Whether the player plays in a female team
- `player_weight` (float): The weight of the player in kg
- `player_height` (int): The height of the player in cm
- `minutes` (int): The number of minutes played this season. This value is used to calculate all other stat values as per-90.
- `90s_played` (int): Number of 90s played
- `appearances` (float): The number of matches the player has participated in on-pitch this season (starts and substitute appearances).
- `average_minutes` (float): The average minutes played per match for the season
- `most_recent_match` (int): The id of the most recent match
- `primary_position` (int): The primary position
- `secondary_position` (int): The secondary position
- `starting_appearances` (float): The number of starts the player has made this season
- `360_minutes` (?)

## Fases de juego y transición (Phases of Play) (6)
- `transition_possession_rate` (?)
- `transition_xg_90` (float): Transition xG per 90 minutes.
- `transition_obv_90` (float): Transition OBV per 90 minutes.
- `avg_player_possession_directness` (float): Season average player_possession_directness over the player's on-ball events (count-weighted, accumulated not per 90). Unbounded and can be negative, unlike the team's [0, 1] possession_directness.
- `avg_player_possession_directness_in_control` (float): Season average player possession directness, events at control_degree = 1 (settled play).
- `avg_player_possession_directness_in_transition` (float): Season average player possession directness, events where is_transition = true.

## Balón parado (8)
Nombres autoexplicativos; se listan sin descripción. Jugadas: `corners`, `free_kicks` (tiros libres indirectos), `indirect_free_kicks`, `direct_free_kicks`, `throw_ins`, `sp` (todo balón parado), `penalties`. Patrones: `<jugada>` = cantidad, `<jugada>_xg` = xG generado, `xg_per_<jugada>` = xG por jugada, `shots_from_<jugada>` / `goals_from_<jugada>`, `<jugada>_shot_ratio` / `<jugada>_goal_ratio` = tiros o goles por jugada, `_conceded` = versión en contra, `_pg` / `_90` = por partido / por 90.

`penalty_conversion_ratio`, `penalties_conceded_90`, `penalties_faced_90`, `penalty_wins_90`, `sp_assists_90`, `sp_key_passes_90`, `sp_passes_into_box_90`, `sp_xa_90`

## Tiros, xG y goles (36)
- `blocks_per_shot` (float): Blocks made per shot faced.
- `conversion_ratio` (pct): Percentage of non-penalty shots a player takes that are converted into goals.
- `goals_90` (float): All goals scored by the player, including penalties.
- `goals_faced_90` (float): Count of all goals conceded by the goalkeeper.
- `np_psxg_faced_90` (float): The post shot expected goals faced
- `np_shots_90` (float): Number of non-penalty shots a player takes.
- `np_xg_90` (float): Non-penalty expected goals produced by the player.
- `np_xg_faced_90` (float): Total xG from all non-penalty shots faced (including off target shots)
- `np_xg_per_shot` (float): A measure of shot quality, this looks at the average non-penalty expected goal value per shot a player takes.
- `npg_90` (float): Goals scored (not including penalties).
- `npga_90` (float): Non-penalty goals and assists. A combined measure of the direct goal contribution of a player via goalscoring or goal assisting
- `npot_psxg_faced_90` (float): Total post-shot xG of on-target shots faced by the goalkeeper, as predicted from a trained and calibrated model of only shots on target. Penalties not included.
- `npxgxa_90` (float): Non-penalty xG and xG Assisted. A combined measure of a player's contribution to shots via shots themselves or the key pass prior to the shot, measured in terms of expected goal values
- `np_psxg_90` (float): Post Shot xG earned from on-target shots
- `obv_shot_90` (float): On Ball Value Added (net) from Shots
- `ot_shots_faced_90` (float): Count of on-target shots faced by the goalkeeper.
- `ot_shots_faced_ratio` (pct): Percentage of shots faced by the goalkeeper that were on-target.
- `over_under_performance_90` (float): Goals and assists above expectation. The difference between scoring contribution (actual contribution to goals) and xG & xG Assisted (expected contribution to goals)
- `op_passes_into_and_touches_inside_box_90` (float): Successful passes into the box from outside the box (open play) and touches inside the box combined
- `shot_on_target_ratio` (pct): The percentage of total shots by a player that are on target (includes goals, saved, and cleared off line).
- `shot_touch_ratio` (pct): The amount of shots a player takes as a proportion of their touches of the ball.
- `shots_faced_90` (float): Count of all shots faced by the goalkeeper (including off-target shots.)
- `shots_key_passes_90` (float): Non-penalty shots and key passes. A combined measure of a player's contribution to shots via shots themselves or the key pass prior to the shot
- `touches_inside_box_90` (float): Successful footed touches inside the box (including shots)
- `op_xgbuildup` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession. The buildup version omits xG and xG Assisted to focus on possession work prior to the end of the chain
- `op_xgbuildup_90` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession. The buildup version omits xG and xG Assisted to focus on possession work prior to the end of the chain
- `xgbuildup` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession. The buildup version omits xG and xG Assisted to focus on possession work prior to the end of the chain
- `xgbuildup_90` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession. The buildup version omits xG and xG Assisted to focus on possession work prior to the end of the chain
- `op_xgbuildup_per_possession` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession. The buildup version omits xG and xG Assisted to focus on possession work prior to the end of the chain
- `xgbuildup_per_possession` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession. The buildup version omits xG and xG Assisted to focus on possession work prior to the end of the chain
- `op_xgchain` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession.
- `op_xgchain_90` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession.
- `xgchain` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession.
- `xgchain_90` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession.
- `op_xgchain_per_possession` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession.
- `xgchain_per_possession` (float): A model that attributes the xG value of the final shot to all players involved in the entire possession.

## Presión y defensa (40)
- `aggressive_actions_90` (float): Tackles, pressure events and fouls recorded within 2 seconds of an opposition ball receipt
- `average_x_defensive_action` (float): The average distance from the goal line that the player successfully makes a defensive action. The scale is the x-axis of the pitch, measured from 0-100.
- `average_x_pressure` (float): The average distance from the goal line that the player presses opponents with the ball. The scale here is the x-axis of the pitch, measured from 0-100.
- `ball_recoveries_90` (float): Number of ball recoveries
- `challenge_ratio` (pct): Percentage of time a player makes a tackle when going into a duel vs getting dribbled past.
- `clearance_90` (float): Number of clearances made by a player.
- `counterpressure_regains_90` (float): Times a playerʼs team won the ball back within 5 seconds of the player counterpressuring an opponent.
- `counterpressures_90` (float): Number of counterpressures. Counterpressures are pressures exerted within 5 seconds of a turnover.
- `da_aggressive_distance` (float): An average value of how far from the goal the goalkeeper is coming forward to perform defensive actions.
- `defensive_action_regains_90` (float): Times a playerʼs team won the ball back within 5 seconds of the player making a defensive action against an opponent.
- `dribble_faced_ratio` (pct): Of the dribbles faced by this player, what % of them were unsuccessful (stopped).
- `dribbled_past_90` (float): How often a player fails a challenge and is dribbled past.
- `fhalf_ball_recoveries_90` (float): How many ball recoveries the player made in the opposition (final) half of the pitch
- `fhalf_counterpressures_90` (float): How many counterpressures the player is exerting in the opposition (final) half of the pitch.
- `fhalf_counterpressures_ratio` (pct): How many counterpressures the player is exerting in the opposition (final) half of the pitch, as a percentage of their total counterpressures.
- `fhalf_pressures_90` (float): How many pressures the player is exerting in the opposition (final) half of the pitch.
- `fhalf_pressures_ratio` (pct): How many pressures the player is exerting in the opposition (final) half of the pitch, as a percentage of their total pressures.
- `interceptions_90` (float): Number of interceptions.
- `obv_defensive_action_90` (float): On Ball Value Added (net) from Defensive Actions
- `padj_clearances_90` (float): Number of clearances adjusted proportionally to the possession volume of a team
- `padj_interceptions_90` (float): Number of interceptions adjusted proportionally to the possession volume of a team
- `padj_pressures_90` (float): Possession adjusted pressures.
- `padj_tackles_90` (float): Number of tackles adjusted proportionally to the possession volume of a team
- `padj_tackles_and_interceptions_90` (float): Number of tackles and interceptions adjusted proportionally to the possession volume of a team
- `pass_into_pressure_ratio` (pct): Percentage of passes made where the recipient was under pressure
- `pressure_regains_90` (float): Times a playerʼs team won the ball back within 5 seconds of the player pressuring an opponent.
- `pressured_change_in_pass_length` (float): Difference in the pass length when under pressure. This is calculated as the pressured pass length minus pass length.
- `pressured_long_balls_90` (float): Number of clearances or long balls attempted while under pressure.
- `pressured_pass_length_ratio` (pct): Ratio between the completed pass length and pass length of passes made under pressure
- `pressured_passing_ratio` (pct): Proportion of pressured passes that were completed
- `pressures_90` (float): The number of times a player pressures an opposition player.
- `tackles_90` (float): Successful challenges made.
- `tackles_and_interceptions_90` (float): Combination of tackles and interceptions
- `unpressured_long_balls_90` (float): Times a player plays a long ball while not under pressure
- `defensive_responsibility_actions_90` (?)
- `expected_defensive_actions_90` (?)
- `defensive_actions_above_expectation` (?)
- `defensive_actions_above_expectation_90` (?)
- `expected_defensive_actions` (?)
- `obv_conceded_responsibility_weighted_90` (?)

## 360: espacio y pases que rompen líneas (54)
Nombres autoexplicativos; se listan sin descripción. `lbp` = line-breaking pass (pase que cruza una línea defensiva), `fhalf_` = en campo rival, `f3_` = en el último tercio, `ball_receipts_in_space_N` = recepciones con al menos N m libres (2, 5, 10), `lbp_to_space_N` = pase que rompe líneas y llega con N m libres, `_received` = como receptor, `average_..._distance` = espacio promedio, `obv_lbp` = OBV de esos pases, `*_360` = conteos solo en partidos con 360.

`average_space_received_in`, `average_fhalf_space_received_in`, `average_f3_space_received_in`, `ball_receipts_in_space_10_ratio`, `ball_receipts_in_space_2_ratio`, `ball_receipts_in_space_5_ratio`, `fhalf_ball_receipts_in_space_10_ratio`, `fhalf_ball_receipts_in_space_2_ratio`, `fhalf_ball_receipts_in_space_5_ratio`, `f3_ball_receipts_in_space_10_ratio`, `f3_ball_receipts_in_space_2_ratio`, `f3_ball_receipts_in_space_5_ratio`, `lbp_90`, `lbp_completed_90`, `lbp_ratio`, `fhalf_lbp_completed_90`, `fhalf_lbp_ratio`, `f3_lbp_completed_90`, `f3_lbp_ratio`, `fhalf_lbp_90`, `f3_lbp_90`, `obv_lbp_90`, `fhalf_obv_lbp_90`, `f3_obv_lbp_90`, `lbp_pass_ratio`, `fhalf_lbp_pass_ratio`, `f3_lbp_pass_ratio`, `lbp_received_90`, `fhalf_lbp_received_90`, `f3_lbp_received_90`, `average_lbp_to_space_distance`, `fhalf_average_lbp_to_space_distance`, `f3_average_lbp_to_space_distance`, `lbp_to_space_10_received_90`, `fhalf_lbp_to_space_10_received_90`, `f3_lbp_to_space_10_received_90`, `lbp_to_space_2_received_90`, `fhalf_lbp_to_space_2_received_90`, `f3_lbp_to_space_2_received_90`, `lbp_to_space_5_received_90`, `fhalf_lbp_to_space_5_received_90`, `f3_lbp_to_space_5_received_90`, `average_lbp_to_space_received_distance`, `fhalf_average_lbp_to_space_received_distance`, `f3_average_lbp_to_space_received_distance`, `lbp_to_space_10_90`, `fhalf_lbp_to_space_10_90`, `f3_lbp_to_space_10_90`, `lbp_to_space_2_90`, `fhalf_lbp_to_space_2_90`, `f3_lbp_to_space_2_90`, `lbp_to_space_5_90`, `fhalf_lbp_to_space_5_90`, `f3_lbp_to_space_5_90`

## Pases, progresión y posesión (43)
- `assists_90` (float): Number of assists.
- `op_assists_90` (float): Number of assists from open play.
- `average_x_pass` (float): The average distance from the goal line that the player successfully makes a pass. The scale is the x-axis of the pitch, measured from 0-100.
- `backward_pass_proportion` (pct): Proportion of a player's passes that are angled backwards. Backwards is defined as the arc of the circle from 5π/6 to 7π/6, of the circle 0:2π; angle-0 means a 0 change in y-coordinate (i.e. towards the opponent's goal line)
- `box_cross_ratio` (pct): What percentage of a player's completed passes into the box are crosses. See Event Specification for details of cross location definition.
- `carries_90` (float): A player controls the ball at their feet while moving or standing still.
- `carry_length` (float): Average carry length.
- `carry_ratio` (pct): Percentage of a player's carries that were successful.
- `change_in_passing_ratio` (pct): How does passing % change when under pressure? This is calculated as Pressured Pass % minus Pass %.
- `crosses_90` (float): Completed crosses.
- `crossing_ratio` (pct): Percentage of attempted crosses that are successful and received by a teammate
- `deep_completions_90` (float): Number of deep completions
- `deep_progressions_90` (float): Passes and dribbles/carries into the opposition final third.
- `dispossessions_90` (float): Number of times a player loses the ball by getting tackled.
- `op_f3_backward_pass_proportion` (pct): Proportion of a player's passes in the final third that are angled backwards. Backwards is defined as the arc of the circle from 5π/6 to 7π/6, of the circle 0:2π; angle-0 means a 0 change in y-coordinate (i.e. towards the opponent's goal line)
- `op_f3_forward_pass_proportion` (pct): Proportion of a player's passes in the final third that are angled forwards. Forwards is defined as the arc of the circle from 11π/6 to π/6, of the circle 0:2π; angle-0 means a 0 change in y-coordinate (i.e. towards the opponent's goal line)
- `op_f3_passes_90` (float): Successful open play final third passes.
- `op_f3_sideways_pass_proportion` (pct): Proportion of a player's passes in the final third that are angled sideways. Sideways is defined as the arc of the circle from π/6 to 5π/6, and from 7π/6 to 11π/6, of the circle 0:2π,; angle-0 means a 0 change in y-coordinate (i.e. towards the opponent's goal line)
- `forward_pass_proportion` (pct): Proportion of a player's passes that are angled forwards. Forwards is defined as the arc of the circle from 11π/6 to π/6, of the circle 0:2π; angle-0 means a 0 change in y-coordinate (i.e. towards the opponent's goal line)
- `key_passes_90` (float): Passes that create shots for teammates. Can also be seen to be referred to as "shot assists" or "chances created"
- `op_key_passes_90` (float): Passes that create shots for teammates, just from open play
- `long_ball_ratio` (pct): Percentage of attempted long balls that are actually completed.
- `long_balls_90` (float): Number of completed long balls
- `obv_pass_90` (float): On Ball Value Added (net) from Passes
- `obv_dribble_carry_90` (float): On Ball Value Added (net) from Dribbles and Carries
- `p_pass_length` (float): Average pass length of passes made under pressure.
- `pass_into_danger_ratio` (pct): Percentage of passes made where the recipient was deemed to be under pressure or was next engaged with a defensive action
- `pass_length` (float): Average pass length.
- `pass_length_ratio` (float): Ratio between the completed pass length and pass length.
- `op_passes_90` (float): Number of attempted passes in open play.
- `passes_inside_box_90` (float): Passes completed inside the box.
- `op_passes_into_box_90` (float): Successful passes into the box from outside the box (open play).
- `passes_into_box_90` (float): Successful passes into box from outside the box
- `passes_pressed_ratio` (pct): Proportion of passes that were made while under opponent pressure
- `passing_ratio` (pct): Percentage of all passes attempted that were completed.
- `positive_outcome_90` (float): A possession that connected through the player and resulted in either a shot, free kick in the attacking half or a corner
- `positive_outcome_score` (pct): How frequently is the player involved in sequences that resolve with a positive outcome while on the pitch
- `ps_pass_length` (float): Pass length of successful passes made under pressure.
- `s_pass_length` (float): Average pass length of completed passes.
- `sideways_pass_proportion` (pct): Proportion of a player's passes that are angled sideways. Sideways is defined as the arc of the circle from π/6 to 5π/6, and from 7π/6 to 11π/6, of the circle 0:2π,; angle-0 means a 0 change in y-coordinate (i.e. towards the opponent's goal line)
- `through_balls_90` (float): A completed pass splitting the defence for a teammate to run onto.
- `op_xa_90` (float): xG assisted from open play.
- `xa_90` (float): xG assisted. This is calculated from the expected goal value of the assisted shot

## OBV (On Ball Value) (2)
- `obv_90` (float): On Ball Value Added (net) total (all event types)
- `obv_gk_90` (float): On Ball Value Added (net) Goalkeeper

## Regate y duelos (10)
- `aerial_ratio` (pct): Percentage of aerial duels a player enters that they win
- `aerial_wins_90` (float): Number of aerial duels a player wins.
- `dribble_ratio` (pct): Percentage of dribbles that were successful
- `dribbles_90` (float): How often a player successfully dribbles past an opponent
- `failed_dribbles_90` (float): Number of dribbles attempted that were unsuccessful.
- `fouls_90` (float): How many fouls a player commits
- `fouls_won_90` (float): How many times a player is fouled.
- `total_dribbles_90` (float): An attempt by the player to beat the opponent with the ball at their feet
- `turnovers_90` (float): How often a player loses the ball via a miscontrol or a failed dribble.
- `predicted_headers_90` (?)

## Portero (6)
- `clcaa` (pct): Claims or CCAA% (Claimable Collection Attempts over Average), is a measure of how likely the goalkeeper is to attempt to claim a "claimable" pass, versus the average goalkeeper attempted claim rate.
- `gsaa_90` (float): How many goals did the keeper save/concede versus expectation (post-shot xG faced)? This is representative of how many goals the goalkeeper's saves prevented within a season.
- `gsaa_ratio` (pct): The measure of goals saved above average, as a percentage of shots faced by the goalkeeper.
- `np_optimal_gk_dlength` (float): How far from the optimal position for facing a shot the Goalkeeper is (on average). This metric is modelled from a starting point of the average location of goalkeepers from 20
- `save_ratio` (pct): Percentage of on-target shots that were saved by the goalkeeper.
- `xs_ratio` (pct): Given the post-shot xG (modelled from on frame location) of shots faced by the goalkeeper what % would we expect them to save?

## Disciplina (3)
- `red_cards_90` (float): How many red cards the player obtains
- `second_yellow_cards_90` (float): How many times a player obtains a second yellow card
- `yellow_cards_90` (float): How many yellow cards the player obtains

## Otros (2)
- `errors_90` (float): How many errors the player makes per 90. An error is an on the ball mistake that led to a shot.
- `left_foot_ratio` (pct): Proportion of footed passes made by this player with their left foot. Players can be considered left-footed when this value is over 60% (and right-footed at less than 40%).
