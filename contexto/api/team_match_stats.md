# Team Match Stats v4.0.0

- Endpoint: `GET https://data.statsbomb.com/api/v4/matches/{match_id}/team-stats`
- Una fila por equipo por partido (≈150 métricas, como en StatsBomb IQ). Incluye las dos filas del partido (equipo y rival).
- Nota: v4 agrega métricas de Phases of Play (tiempo en transición/control, xG y OBV en transición y sus versiones concedidas, tasa de posesiones en transición, directness promedio).
- Campos: 207. Los nombres abajo omiten el prefijo `team_match_` cuando lo tienen (el nombre real es `team_match_<campo>`).
- Tipos: int, float, pct (porcentaje), str, bool, date. Descripciones tal como el PDF de StatsBomb; (sic) marca correcciones.

## Identificadores y contexto (11)
- `account_id` (int)
- `match_id` (int): The id of the match
- `team_id` (int): The id of the team
- `team_name` (str): The full name of the team
- `opposition_id` (int): The id of the opposition
- `opposition_name` (str): The full name of the opposition
- `competition_id` (int): The id of the competition
- `competition_name` (str): The full name of the competition
- `season_id` (int): The id of the season
- `season_name` (str): A description of the season (e.g. “2020/2021ˮ)
- `team_female` (bool): Female team?

## Fases de juego y transición (Phases of Play) (10)
- `time_in_transition` (float): Total duration (milliseconds) of the team's on-ball events (passes, shots, carries) that occurred in the transition state (control_degree below 1).
- `time_in_control` (float): Total duration (milliseconds) of the team's on-ball events (passes, shots, carries) that occurred in the control state (control_degree = 1). Together with team_match_time_in_transition this sums to the team's total on-ball event duration.
- `transition_xg` (float): Expected goals generated within the In Possession Transition state (before control_degree reaches 1).
- `transition_xg_conceded` (float): Defensive mirror: xG allowed during the team's own Out of Possession Transition state.
- `transition_obv` (float): On-ball value generated within the In Possession Transition state.
- `transition_obv_conceded` (float): Defensive mirror: OBV allowed during the team's own Out of Possession Transition state.
- `avg_team_possession_directness` (float): Average possession_directness across all the team's possessions.
- `avg_team_possession_directness_in_control` (float): Average team possession directness filtered to settled possessions (control_degree = 1).
- `avg_team_possession_directness_in_transition` (float): Average team possession directness filtered to transitional possessions (is_transition = true).
- `transition_possession_rate` (float): Proportion of the team's possessions that remain in the In Possession Transition state (never reach control_degree = 1). Ratio in [0, 1]. Absent or null when model output is unavailable.

## Balón parado (90)
Nombres autoexplicativos; se listan sin descripción. Jugadas: `corners`, `free_kicks` (tiros libres indirectos), `indirect_free_kicks`, `direct_free_kicks`, `throw_ins`, `sp` (todo balón parado), `penalties`. Patrones: `<jugada>` = cantidad, `<jugada>_xg` = xG generado, `xg_per_<jugada>` = xG por jugada, `shots_from_<jugada>` / `goals_from_<jugada>`, `<jugada>_shot_ratio` / `<jugada>_goal_ratio` = tiros o goles por jugada, `_conceded` = versión en contra, `_pg` / `_90` = por partido / por 90.

`sp_shots`, `sp_xg`, `sp_shot_distance`, `sp_shots_conceded`, `sp_xg_conceded`, `sp_shot_distance_conceded`, `corners`, `corner_xg`, `xg_per_corner`, `free_kicks`, `free_kick_xg`, `xg_per_free_kick`, `direct_free_kicks`, `direct_free_kick_xg`, `xg_per_direct_free_kick`, `throw_ins`, `throw_in_xg`, `xg_per_throw_in`, `penalty_goals`, `penalty_goals_conceded`, `shots_from_corners`, `goals_from_corners`, `shots_from_free_kicks`, `goals_from_free_kicks`, `direct_free_kick_goals`, `shots_from_direct_free_kicks`, `shots_from_throw_ins`, `goals_from_throw_ins`, `direct_free_kick_goals_conceded`, `shots_from_direct_free_kicks_conceded`, `corners_conceded`, `corner_xg_conceded`, `shots_from_corners_conceded`, `goals_from_corners_conceded`, `free_kicks_conceded`, `free_kick_xg_conceded`, `shots_from_free_kicks_conceded`, `goals_from_free_kicks_conceded`, `direct_free_kicks_conceded`, `direct_free_kick_xg_conceded`, `throw_ins_conceded`, `throw_in_xg_conceded`, `shots_from_throw_ins_conceded`, `goals_from_throw_ins_conceded`, `corner_shot_ratio`, `corner_goal_ratio`, `free_kick_shot_ratio`, `free_kick_goal_ratio`, `direct_free_kick_goal_ratio`, `throw_in_shot_ratio`, `throw_in_goal_ratio`, `xg_per_corner_conceded`, `corner_shot_ratio_conceded`, `corner_goal_ratio_conceded`, `xg_per_free_kick_conceded`, `free_kick_shot_ratio_conceded`, `free_kick_goal_ratio_conceded`, `xg_per_direct_free_kick_conceded`, `direct_free_kick_goal_ratio_conceded`, `xg_per_throw_in_conceded`, `throw_in_shot_ratio_conceded`, `throw_in_goal_ratio_conceded`, `direct_free_kick_shot_ratio`, `direct_free_kick_shot_ratio_conceded`, `sp`, `xg_per_sp`, `sp_shot_ratio`, `sp_goals`, `sp_goal_ratio`, `sp_conceded`, `xg_per_sp_conceded`, `sp_shot_ratio_conceded`, `sp_goals_conceded`, `sp_goal_ratio_conceded`, `penalties_won`, `penalties_conceded`, `indirect_free_kicks`, `indirect_free_kicks_conceded`, `indirect_free_kick_xg`, `indirect_free_kick_xg_conceded`, `xg_per_indirect_free_kick`, `xg_per_indirect_free_kick_conceded`, `shots_from_indirect_free_kicks`, `shots_from_indirect_free_kicks_conceded`, `goals_from_indirect_free_kicks`, `goals_from_indirect_free_kicks_conceded`, `indirect_free_kick_shot_ratio`, `indirect_free_kick_shot_ratio_conceded`, `indirect_free_kick_goal_ratio`, `indirect_free_kick_goal_ratio_conceded`

## Tiros, xG y goles (33)
- `gd` (int): Team goals scored minus team goals conceded
- `xgd` (float): Team xG minus Team xG conceded
- `np_shots` (int): Number of non-penalty shots
- `op_shots` (int): Number of open play shots
- `op_shots_outside_box` (int): Number of shots from outside the box in open play
- `np_xg` (float): Total expected goal value of all non-penalty shots
- `op_xg` (float): Total expected goal value of shots from open play
- `np_xg_per_shot` (float): Non-penalty expected goals per shot.
- `np_shot_distance` (float): Average distance from goal of non-penalty shots.
- `op_shot_distance` (float): Average distance from goal (open play).
- `pace_towards_goal` (float): The average speed of buildup for possessions that end in shots, from the start of possession to shot (m/s)
- `np_shots_conceded` (int): Non-penalty shots conceded.
- `op_shots_conceded` (int): Number of shots conceded in open play.
- `op_shots_conceded_outside_box` (int): Shots conceded from outside the box in open play.
- `np_xg_conceded` (float): Cumulative xG value of non_penalty shots conceded.
- `op_xg_conceded` (float): Expected goal value of shots from open play conceded.
- `np_xg_per_shot_conceded` (float): Average expected goal value per shot conceded (no penalties)
- `np_shot_distance_conceded` (float): Average distance from goal of opponent non-penalty shots.
- `op_shot_distance_conceded` (float): Average distance from goal of opponent open play shots.
- `counter_attacking_shots` (int): Shots generated within 15 seconds of a possession that originates from their own half.
- `high_press_shots` (int): Shots generated from possessions that were won within 5 seconds of a defensive action (pressure/tackle/interception/blocked pass) in the oppositionʼs half.
- `shots_in_clear` (int): Shots generated when only the opponent's goalkeeper was in between shot-taker and goal. (Within a cone between the shot-taker and the goalposts.)
- `counter_attacking_shots_conceded` (int): Shots generated within 15 seconds of a possession that originates from opponent's own half.
- `shots_in_clear_conceded` (int): Shots generated when only a team's goalkeeper was in between shot-taker and goal.
- `goals` (int): Goals scored
- `own_goals` (int): Own goals
- `goals_conceded` (int): Goals conceded
- `opposition_own_goals` (int): Opposition own goals
- `high_press_shots_conceded` (int): Shots conceded from possessions that were lost within 5 seconds of a opposition defensive action (pressure/tackle/interception/blocked pass) in the team's half.
- `np_gd` (int): Goals scored minus goals conceded (not including penalties)
- `np_xgd` (float): xG minus xG conceded (not including penalties)
- `obv_shot` (float): On Ball Value Added (net) from Shots
- `obv_shot_nconceded` (float): Opposition On Ball Value Added (net) from Shots

## Presión y defensa (16)
- `defensive_distance` (float): The average distance from a teamʼs own goal from which it makes defensive actions.
- `ppda` (float): How many passes does a team allow the opponent before making a defensive action (tackle, interception, foul). An indicator of pressing intensity this metric is defined in attacking areas ie 40% of the length of the pitch away from a team's own goal and forwards.
- `defensive_distance_ppda` (float): The average distance from a teamʼs own goal from which it makes defensive actions (passes per defensive action).
- `aggressive_actions` (int): Tackles, pressure events and fouls a team makes within 2 seconds of an opposition ball receipt.
- `aggression` (float): The proportion of an opponent's pass receipts that are tackled, fouled or pressured within 2 seconds.
- `pressures` (int): The number of times a team pressures the opponent
- `counterpressures` (int): Pressures exerted within 5 seconds of a turnover.
- `pressure_regains` (int): Ball is regained within 5 seconds of a player pressuring an opponent.
- `counterpressure_regains` (int): Times a team won the ball back within 5 seconds of a player counterpressuring an opponent.
- `defensive_action_regains` (int): Times a team won the ball back within 5 seconds of a defensive action by one of their players.
- `fhalf_pressures` (int): How many pressures are exerted in the opposition (final) half of the pitch.
- `fhalf_counterpressures` (int): How many counterpressures are exerted in the opposition (final) half of the pitch.
- `fhalf_pressures_ratio` (float): How many pressures are exerted in the opposition (final) half of the pitch, as a percentage of their total pressures.
- `fhalf_counterpressures_ratio` (float): How many counterpressures are exerted in the opposition (final) half of the pitch, as a percentage of their total counterpressures.
- `obv_defensive_action` (float): On Ball Value Added (net) from Defensive Actions
- `obv_defensive_action_conceded` (float): Opposition On Ball Value Added (net) from Defensive Actions

## Pases, progresión y posesión (28)
- `possessions` (int): Number of possessions.
- `possession` (float): Possession average
- `directness` (float): A ratio of the distance towards goal from the start of a possession that ended in a shot, divided by the total distance travelled in buildup to the shot.
- `gk_pass_distance` (float): Average length of pass from a goalkeeper when playing out from the back.
- `gk_long_pass_ratio` (float): Percentage of goalkeeper long passes that are completed.
- `box_cross_ratio` (float): What percentage of a team's passes into the box are crosses.
- `passes_inside_box` (int): Passes completed inside the box.
- `opp_passing_ratio` (float): Passing completion rate.
- `opp_final_third_pass_ratio` (float): Opposition's final third completion rate.
- `deep_completions_conceded` (int): Successful conceded passes within 20 metres of the opposition goal.
- `passes_inside_box_conceded` (int): Opponent passes completed inside the box.
- `deep_completions` (int): Successful passes within 20 meters of the opposition goal.
- `passing_ratio` (float): Passing completion rate.
- `crosses_into_box` (int): Number of crosses into the box
- `successful_crosses_into_box` (int): Number of successful crosses into the box
- `successful_box_cross_ratio` (float): What percentage of a team's completed passes into the box are crosses.
- `deep_progressions` (int): Passes, dribbles and carries into the opposition final third.
- `deep_progressions_conceded` (int): Passes, dribbles and carries conceded into the opposition final third.
- `obv_pass` (float): On Ball Value Added (net) from Passes
- `obv_dribble_carry` (float): On Ball Value Added (net) from Dribbles and Carries
- `obv_pass_conceded` (float): Opposition On Ball Value Added (net) from Passes
- `obv_dribble_carry_conceded` (float): Opposition On Ball Value Added (net) from Dribbles and Carries
- `passes` (int): Number of attempted passes
- `successful_passes` (int): Number of successful passes
- `passes_conceded` (int): Number of attempted passes by the opposition
- `successful_passes_conceded` (int): Number of successful passes by the opposition
- `op_passes` (int): Number of attempted passes in open play
- `op_passes_conceded` (int): Number of attempted passes in open play against the selected team

## OBV (On Ball Value) (4)
- `obv` (float): On Ball Value Added (net) total (all event types)
- `obv_gk` (float): On Ball Value Added (net) Goalkeeper
- `obv_conceded` (float): Opposition On Ball Value Added (net) total (all event types)
- `obv_gk_conceded` (float): Opposition On Ball Value Added (net) Goalkeeper

## Regate y duelos (11)
- `completed_dribbles` (int): Number of dribbles completed by a team.
- `failed_dribbles` (int): Dribbles attempted that were unsuccessful.
- `total_dribbles` (int): Total attempts to beat the opponent with the ball at their feet
- `dribble_ratio` (float): Percentage of dribbles that were completed
- `completed_dribbles_conceded` (int): Number of dribbles completed by the opposition.
- `failed_dribbles_conceded` (int): Number of dribbles attempted by the opposition that were unsuccessful.
- `total_dribbles_conceded` (int): Total opponent attempts to beat a team with the ball at their feet
- `opposition_dribble_ratio` (float): Percentage of opponent dribbles that were completed
- `aerial_duel_difficulty` (float): Average win % of aerial duels contested, as estimated by the HOPS player scores
- `aerial_unit_rating` (float): Time-weighted average normalised HOPS rating (0 - 1) of the team's top 5 aerial players on pitch
- `aerial_team_rating` (float): Time-weighted average normalised HOPS rating (0 - 1) of all 11 players on pitch

## Disciplina (3)
- `yellow_cards` (int): Yellow cards (sic: el PDF dice 'second yellow card').
- `second_yellow_cards` (int): How many times a team obtains a second yellow card
- `red_cards` (int): How many red cards the team obtains

## Otros (1)
- `ball_in_play_time` (float): Actual clock time the ball spends in play
