# Team Season Stats v4.0.0

- Endpoint: `GET https://data.statsbombservices.com/api/v4/competitions/{competition_id}/seasons/{season_id}/team-stats`
- Una fila por equipo por torneo; casi todo viene por partido (sufijo _pg).
- Nota: Base para percentiles contra la liga y para la línea base del 'efecto América'.
- Campos: 204. Los nombres abajo omiten el prefijo `team_season_` cuando lo tienen (el nombre real es `team_season_<campo>`).
- Tipos: int, float, pct (porcentaje), str, bool, date. Descripciones tal como el PDF de StatsBomb; (sic) marca correcciones.

## Identificadores y contexto (9)
- `team_id` (int): The id of the team
- `team_name` (str): The full name of the team
- `competition_id` (int): The id of the competition
- `competition` (str): The title of the competition
- `season_id` (int): The id of the season
- `season_name` (str): A description of the season (e.g. “2020/2021ˮ)
- `team_female` (bool): Female team?
- `matches` (int): Number of matches for the team for the season
- `minutes` (float): Total number of minutes for the team for the season

## Fases de juego y transición (Phases of Play) (10)
- `transition_possession_rate` (float): Season proportion of the team's possessions remaining in the In Possession Transition state. Ratio in [0, 1].
- `time_in_transition_pg` (float): Per-game average of the team's on-ball event duration (milliseconds) in the transition state (control_degree below 1).
- `time_in_control_pg` (float): Per-game average of the team's on-ball event duration (milliseconds) in the control state (control_degree = 1).
- `transition_xg_pg` (float): Per-game transition xG.
- `transition_xg_conceded_pg` (float): Per-game transition xG conceded.
- `transition_obv_pg` (float): Per-game transition OBV.
- `transition_obv_conceded_pg` (float): Per-game transition OBV conceded.
- `avg_team_possession_directness` (float): Season average possession_directness across all the team's possessions (accumulated, not per game).
- `avg_team_possession_directness_in_control` (float): Season average team possession directness, settled possessions (control_degree = 1).
- `avg_team_possession_directness_in_transition` (float): Season average team possession directness, transitional possessions (is_transition = true).

## Balón parado (90)
Nombres autoexplicativos; se listan sin descripción. Jugadas: `corners`, `free_kicks` (tiros libres indirectos), `indirect_free_kicks`, `direct_free_kicks`, `throw_ins`, `sp` (todo balón parado), `penalties`. Patrones: `<jugada>` = cantidad, `<jugada>_xg` = xG generado, `xg_per_<jugada>` = xG por jugada, `shots_from_<jugada>` / `goals_from_<jugada>`, `<jugada>_shot_ratio` / `<jugada>_goal_ratio` = tiros o goles por jugada, `_conceded` = versión en contra, `_pg` / `_90` = por partido / por 90.

`corner_goal_ratio`, `corner_goal_ratio_conceded`, `corner_shot_ratio`, `corner_shot_ratio_conceded`, `corner_xg_conceded_pg`, `corner_xg_pg`, `corners_conceded_pg`, `corners_pg`, `direct_free_kick_goal_ratio`, `direct_free_kick_goal_ratio_conceded`, `direct_free_kick_goals_conceded_pg`, `direct_free_kick_goals_pg`, `direct_free_kick_shot_ratio`, `direct_free_kick_shot_ratio_conceded`, `direct_free_kick_xg_conceded_pg`, `direct_free_kick_xg_pg`, `direct_free_kicks_conceded_pg`, `direct_free_kicks_pg`, `free_kick_goal_ratio`, `free_kick_goal_ratio_conceded`, `free_kick_shot_ratio`, `free_kick_shot_ratio_conceded`, `free_kick_xg_conceded_pg`, `free_kick_xg_pg`, `free_kicks_conceded_pg`, `free_kicks_pg`, `goals_from_corners_conceded_pg`, `goals_from_corners_pg`, `goals_from_free_kicks_conceded_pg`, `goals_from_free_kicks_pg`, `goals_from_throw_ins_conceded_pg`, `goals_from_throw_ins_pg`, `penalties_conceded_pg`, `penalties_won_pg`, `penalty_goals_conceded_pg`, `penalty_goals_pg`, `shots_from_corners_conceded_pg`, `shots_from_corners_pg`, `shots_from_direct_free_kicks_conceded_pg`, `shots_from_direct_free_kicks_pg`, `shots_from_free_kicks_conceded_pg`, `shots_from_free_kicks_pg`, `shots_from_throw_ins_conceded_pg`, `shots_from_throw_ins_pg`, `sp_goal_ratio`, `sp_goal_ratio_conceded`, `sp_goals_pg`, `sp_goals_pg_conceded`, `sp_pg`, `sp_pg_conceded`, `sp_shot_distance`, `sp_shot_distance_conceded`, `sp_shot_ratio`, `sp_shot_ratio_conceded`, `sp_shots_conceded_pg`, `sp_shots_pg`, `sp_xg_conceded_pg`, `sp_xg_pg`, `throw_in_goal_ratio`, `throw_in_goal_ratio_conceded`, `throw_in_shot_ratio`, `throw_in_shot_ratio_conceded`, `throw_in_xg_conceded_pg`, `throw_in_xg_pg`, `throw_ins_conceded_pg`, `throw_ins_pg`, `xg_per_corner`, `xg_per_corner_conceded`, `xg_per_direct_free_kick`, `xg_per_direct_free_kick_conceded`, `xg_per_free_kick`, `xg_per_free_kick_conceded`, `xg_per_sp`, `xg_per_sp_conceded`, `xg_per_throw_in`, `xg_per_throw_in_conceded`, `indirect_free_kicks_pg`, `indirect_free_kicks_conceded_pg`, `indirect_free_kick_xg_pg`, `indirect_free_kick_xg_conceded_pg`, `xg_per_indirect_free_kick`, `xg_per_indirect_free_kick_conceded`, `shots_from_indirect_free_kicks_pg`, `shots_from_indirect_free_kicks_conceded_pg`, `goals_from_indirect_free_kicks_pg`, `goals_from_indirect_free_kicks_conceded_pg`, `indirect_free_kick_shot_ratio`, `indirect_free_kick_shot_ratio_conceded`, `indirect_free_kick_goal_ratio`, `indirect_free_kick_goal_ratio_conceded`

## Tiros, xG y goles (35)
- `counter_attacking_shots_conceded_pg` (float): Shots generated within 15 seconds of a possession that originates from opponent's own half.
- `counter_attacking_shots_pg` (float): Shots generated within 15 seconds of a possession that originates from a team's own half.
- `gd` (float): Goals scored minus goals conceded
- `gd_pg` (float): Goals scored minus goals conceded (including penalties)
- `goals_conceded_pg` (float): Goals conceded (including penalties) plus own goals.
- `goals_pg` (float): Goals scored (including penalties) plus opponent own goals.
- `high_press_shots_conceded_pg` (float): Shots conceded from possessions that were lost within 5 seconds of a opposition defensive action (pressure/tackle/interception/blocked pass) in the team's half.
- `high_press_shots_pg` (float): Shots generated from possessions that were won within 5 seconds of a defensive action (pressure/tackle/interception/blocked pass) in the oppositionʼs half.
- `np_gd_pg` (float): Goals scored minus goals conceded (not including penalties)
- `np_shot_distance` (float): Average distance from goal of non-penalty shots.
- `np_shot_distance_conceded` (float): Average distance from goal of opponent non-penalty shots.
- `np_shots_conceded_pg` (float): Non-penalty shots conceded.
- `np_shots_pg` (float): Number of shots.
- `np_xg_conceded_pg` (float): Cumulative expected goal value of all non-penalty shots conceded
- `np_xg_per_shot` (float): Non-penalty expected goals per shot.
- `np_xg_per_shot_conceded` (float): Average expected goal value per shot conceded (no penalties)
- `np_xg_pg` (float): Cumulative expected goal value of all non-penalty shots
- `np_xgd_pg` (float): xG minus xG conceded (not including penalties)
- `opposition_own_goals_pg` (float): Opposition own goals.
- `own_goals_pg` (float): Own goals.
- `pace_towards_goal` (float): The average speed of buildup for possessions that end in shots, from the start of possession to shot (m/s)
- `op_shot_distance` (float): Average distance from goal (open play).
- `op_shot_distance_conceded` (float): Average distance from goal of opponent (open play).
- `op_shots_conceded_outside_box_pg` (float): Shots conceded from outside the box in open play.
- `op_shots_conceded_pg` (float): Number of shots conceded in open play.
- `shots_in_clear_conceded_pg` (float): Shots generated when only a team's goalkeeper was in between shot-taker and goal.
- `shots_in_clear_pg` (float): Shots generated when only the opponent's goalkeeper was in between shot-taker and goal. (Within a cone between the shot-taker and the goalposts.)
- `op_shots_outside_box_pg` (float): Shots from outside the box in open play.
- `op_shots_pg` (float): Number of shots in open play.
- `op_xg_conceded_pg` (float): Expected goal value of shots from open play conceded.
- `op_xg_pg` (float): Expected goal value of shots from open play.
- `xgd` (float): xG minus xG conceded
- `xgd_pg` (float): xG minus xG conceded (including penalties)
- `obv_shot_pg` (float): On Ball Value Added (net) from shots average per game
- `obv_shot_conceded_pg` (float): Opposition On Ball Value Added (net) from shots average per game

## Presión y defensa (16)
- `aggression` (float): The proportion of an opponent's pass receipts that are tackled, fouled or pressured within 2 seconds.
- `aggressive_actions_pg` (float): Tackles, pressure events and fouls a team makes within 2 seconds of an opposition ball receipt.
- `counterpressure_regains_pg` (float): Times a team won the ball back within 5 seconds of a player counterpressuring an opponent.
- `counterpressures_pg` (float): Pressures exerted within 5 seconds of a turnover.
- `defensive_action_regains_pg` (float): Times a team won the ball back within 5 seconds of a defensive action by one of their players.
- `defensive_distance` (float): The average distance from a teams own goal from which it makes defensive actions.
- `defensive_distance_ppda` (float): The average distance from a teams own goal from which it makes defensive actions (passes per defensive action).
- `fhalf_counterpressures_pg` (float): How many counterpressures are exerted in the opposition (final) half of the pitch.
- `fhalf_counterpressures_ratio` (pct): How many counterpressures are exerted in the opposition (final) half of the pitch, as a percentage of their total counterpressures.
- `fhalf_pressures_pg` (float): How many pressures are exerted in the opposition (final) half of the pitch.
- `fhalf_pressures_ratio` (pct): How many pressures are exerted in the opposition (final) half of the pitch, as a percentage of their total pressures.
- `ppda` (float): How many passes does a team allow the opponent before making a defensive action (tackle, interception, foul). An indicator of pressing intensity this metric is defined in attacking areas ie 40% of the length of the pitch away from a team's own goal and forwards.
- `pressure_regains_pg` (float): Ball is regained within 5 seconds of a player pressuring an opponent.
- `pressures_pg` (float): The number of times a team pressures the opponent
- `obv_defensive_action_pg` (float): On Ball Value Added (net) from defensive actions average per game
- `obv_defensive_action_conceded_pg` (float): Opposition On Ball Value Added (net) from defensive actions average per game

## Pases, progresión y posesión (28)
- `box_cross_ratio` (pct): What percentage of a player's passes into the box are crosses.
- `crosses_into_box_pg` (float): Number of crosses into the box
- `deep_completions_conceded_pg` (float): Successful conceded passes within 20 metres of the opposition goal.
- `deep_completions_pg` (float): Successful passes within 20 meters of the opposition goal.
- `deep_progressions_conceded_pg` (float): Passes, dribbles and carries conceded into the opposition final third.
- `deep_progressions_pg` (float): Passes, dribbles and carries into the opposition final third.
- `directness` (float): A ratio of the distance towards goal from the start of a possession that ended in a shot, divided by the total distance travelled in buildup to the shot.
- `gk_long_pass_ratio` (pct): Percentage of goalkeeper long passes that are completed.
- `gk_pass_distance` (float): Average length of pass from a goalkeeper when playing out from the back.
- `opp_final_third_pass_ratio` (pct): Opposition's final third completion rate.
- `opp_passing_ratio` (pct): Opposition's passing completion rate.
- `passes_inside_box_conceded_pg` (float): Opponent passes completed inside the box.
- `passes_inside_box_pg` (float): Passes completed inside the box.
- `passing_ratio` (pct): Passing completion rate.
- `possession` (pct): Standard metric for how much possession a team averages per match.
- `possessions` (float): Number of possessions.
- `successful_box_cross_ratio` (pct): What percentage of a player's completed passes into the box are crosses.
- `successful_crosses_into_box_pg` (float): Number of successful crosses into the box
- `obv_pass_pg` (float): On Ball Value Added (net) from passes average per game
- `obv_dribble_carry_pg` (float): On Ball Value Added (net) from dribbles and carries average per game
- `obv_pass_conceded_pg` (float): Opposition On Ball Value Added (net) from passes average per game
- `obv_dribble_carry_conceded_pg` (float): Opposition On Ball Value Added (net) from dribbles and carries average per game
- `passes_pg` (float): Number of attempted passes per game
- `successful_passes_pg` (float): Number of successful passes per game
- `passes_conceded_pg` (float): Number of attempted passes by the opposition per game
- `successful_passes_conceded_pg` (float): Number of successful passes by the opposition per game
- `op_passes_pg` (float): Number of attempted passes in open play per game
- `op_passes_conceded_pg` (float): Number of attempted passes in open play against the selected team per game

## OBV (On Ball Value) (4)
- `obv_pg` (float): On Ball Value Added (net) average per game
- `obv_gk_pg` (float): On Ball Value Added (net) goalkeeper average per game
- `obv_conceded_pg` (float): Opposition On Ball Value Added (net) average per game
- `obv_gk_conceded_pg` (float): Opposition On Ball Value Added (net) goalkeeper average per game

## Regate y duelos (8)
- `completed_dribbles_conceded_pg` (float): Number of dribbles completed by the opposition.
- `completed_dribbles_pg` (float): Number of dribbles completed by a team.
- `dribble_ratio` (pct): Percentage of dribbles that were completed
- `failed_dribbles_conceded_pg` (float): Number of dribbles attempted by the opposition that were unsuccessful.
- `failed_dribbles_pg` (float): Dribbles attempted that were unsuccessful.
- `opposition_dribble_ratio` (pct): Percentage of opponent dribbles that were completed
- `total_dribbles_conceded_pg` (float): Total opponent attempts to beat a team with the ball at their feet
- `total_dribbles_pg` (float): Total attempts to beat the opponent with the ball at their feet

## Disciplina (3)
- `red_cards_pg` (float): How many red cards the team obtains
- `second_yellow_cards_pg` (float): How many times a team obtains a second yellow card
- `yellow_cards_pg` (float): How many yellow cards the team obtains

## Otros (1)
- `ball_in_play_time` (float): Average actual clock time the ball spends in play
