# Framework analítico — borrador v0

Toda métrica, visualización y modelo del proyecto se deriva de estas definiciones. Si algo no está aquí, se agrega aquí primero. Los umbrales viven en `config/params.yaml`; los valores de abajo son propuestas iniciales que se confirman después de la prueba de humo y del inspector.

**Regla de oro:** si StatsBomb define el objeto, lo adoptamos; si no, lo definimos aquí.

## Coordenadas y orientación

- Cancha de 120 × 80 yardas; centro (60, 40). Tercios: defensivo x < 40, medio 40 ≤ x < 80, final x ≥ 80.
- Supuesto a verificar: cada evento viene en la perspectiva del equipo que lo ejecuta (ataca hacia x = 120). Antes de mezclar acciones de ambos equipos en un mismo mapa, reorientar las del rival con (120 − x, 80 − y).
- Los freeze frames 360 están en la orientación del evento (el equipo del actor ataca de 0 a 120).

## Partidos válidos

- Eventos: `collection_status = Complete` y `match_status = available`.
- Métricas 360: además `match_status_360 = available`. Se reporta la cobertura (porcentaje de eventos con frame y con `visible_area`).
- Equipo y entrenador: se filtran por `team_id` y por el id del entrenador en `home_team_manager` / `away_team_manager` (API Matches), no por fechas.

## Objetos

| Objeto | Definición | Fuente |
| --- | --- | --- |
| Posesión | Campo `possession` | StatsBomb |
| Juego abierto | `play_pattern` en Regular Play, From Counter, From Keeper, From Goal Kick, From Kick Off, Other (no corner, tiro libre ni lateral) | Propia |
| Secuencia ofensiva | Posesión propia en juego abierto con al menos un pase completado o una conducción | Propia |
| Fase / tercio | `location_bucket` (defensive, midfield, final third) | StatsBomb |
| Transición | `is_transition` (control_degree < 1). Plan B si no viene poblado: los primeros `transicion.plan_b_segundos` tras una recuperación en juego abierto | StatsBomb (B: propia) |
| Posesión controlada | `is_controlled_possession` | StatsBomb |
| Directness | `possession_directness` (equipo) y `player_possession_directness` (jugador) | StatsBomb |
| Contraataque | `play_pattern = From Counter` | StatsBomb |
| Contrapresión | `counterpress = TRUE` (acción de presión dentro de 5 s tras pérdida) | StatsBomb |
| Presión | PPDA y distancia defensiva de Team Match Stats; presiones en campo rival (x ≥ 60); presión en último tercio (x ≥ 80) | StatsBomb + propia |
| Pase completo | Evento Pass sin `outcome` | StatsBomb |
| Pase progresivo | Pase completo en juego abierto que acerca el balón al centro de la portería (120, 40) al menos `pase_progresivo.avance_min_yd`, o que entra al área | Propia |
| Balón parado | `play_pattern` From Corner, From Free Kick, From Throw In; fase con `set_piece_phase` (1 o 2). Lateral en zona de peligro: x ≥ 80 | StatsBomb + propia |
| Espacio al recibir | Métricas 360: `ball_receipt_in_space`, `ball_receipt_exceeds_distance`, `distance_to_nearest_defender` | StatsBomb |
| Pase que rompe líneas | `line_breaking_pass` (360) | StatsBomb |
| Control territorial | Fracción de una zona controlada por cada equipo según Voronoi de los jugadores visibles, recortado a cancha ∩ `visible_area`; se excluyen jugadores a menos de `voronoi.min_dist_borde` del borde visible | Propia |
| Estructura de juego | Red de pases dirigida: nodos = posiciones del sistema (ids 1–25), aristas = pases completos entre posiciones; separada por fase y por marcador | Propia |
| Huella de pases | Vector de 60 frecuencias de `pass_cluster_id` por partido (y por equipo) | Propia |
| Riesgo de pase | Pases completos menos la suma de `pass_success_probability` | Propia |
| Valor de las acciones | xG (`statsbomb_xg`) y OBV (`obv_*`) | StatsBomb |

## Lectura a dos bandas

| Objeto | Definición |
| --- | --- |
| Tramo | Ventana de `tramos_min` minutos de reloj dentro de un periodo; el tiempo añadido de cada mitad es un tramo propio |
| Diferencial | Métrica del América en el tramo menos la misma métrica del rival en el mismo tramo |
| Field tilt | Pases completos de un equipo en el último tercio rival entre los de ambos equipos en el tramo |
| Acción y reacción | Relación entre la presión de un equipo en el tramo t y la salida del otro en t y t+1 |
| Ajuste cruzado | Cambio de formación (`Tactical Shift`) o sustitución táctica de cualquiera de los dos equipos, con su minuto, y las métricas antes y después |
| Efecto América | Métrica del rival en el partido contra el América menos su promedio del torneo sin ese partido |

## Contexto del partido

| Variable | Definición |
| --- | --- |
| Marcador (game state) | Gana, empata o pierde, recalculado evento a evento con goles (tiros con outcome Goal y Own Goal For/Against) |
| Localía | Local o visitante según Matches; `neutral_ground` aparte |
| Fuerza del rival | Tercil del rival en el torneo según xG diferencial por partido (`team_season_np_xgd_pg`) |
| Momento | Bloques de 15 minutos: 1–15, 16–30, 31–45+, 46–60, 61–75, 76–90+ |
| Torneo | Apertura (jul–dic) o Clausura (ene–may) dentro de una temporada (`season_id` es el año). Se toma del prefijo de `competition_stage.name`; si no lo trae, de `match_date` |
| Fase del torneo | `competition_stage` (fase regular contra liguilla) |
| Entrenador | Id del entrenador en Matches (`home_team.managers` / `away_team.managers`) |

## Validación y decisión

- **Partición temporal.** Entrenamiento: los torneos de Jardine del Apertura 2023 al Apertura 2025. Prueba: el Clausura 2026, que no se usa para definir principios, umbrales ni modelos hasta la evaluación final.
- **Qué se predice.** El comportamiento de Jardine por situación (las filas de la matriz de situaciones): métricas por tramo según marcador, localía, fuerza del rival y momento.
- **Línea base.** El promedio de la liga en la misma situación y el promedio general de Jardine sin contexto. Si los principios no mejoran a la línea base, se reporta así.
- **Sin fuga.** Todo lo que alimenta una predicción o una ficha del Clausura 2026 se calcula con partidos anteriores a ese día; la fuerza del rival se recalcula con partidos previos en vez de usar la estadística de la temporada completa.
- **Monte Carlo.** Dos usos separados: resultado merecido con el xG de los tiros del propio partido (descriptivo, posterior) y rangos de incertidumbre de la predicción (solo con datos de entrenamiento).
- **Decisión real.** Decisiones observables del Clausura 2026 (sustituciones tácticas, cambios de formación, con minuto y marcador) frente a lo que recomendaba la herramienta con datos previos; lo que pasó después se reporta como correlación.

## Supuestos explícitos

- Aceptamos los modelos del proveedor (xG, OBV, Phases of Play, responsabilidad defensiva, probabilidad de pase) y heredamos sus supuestos.
- En el 360 solo usamos jugadores lejos del borde del área visible y celdas recortadas a cancha ∩ área visible.
- Las métricas propias con 360 se calculan solo en momentos clave: pases progresivos propios, progresiones del rival y envíos a balón parado.
- Cada hallazgo debe sostenerse ante variaciones razonables de los umbrales (análisis de sensibilidad).
- Comparaciones de contexto: dentro del mismo partido cuando sea posible (efectos fijos por partido) y emparejando por minuto y marcador. Lo que sea solo correlación se etiqueta como tal.

## Alcance y límites

- **Sí captura:** qué hace cada equipo con y sin balón, dónde, en qué contexto y frente a qué hace el rival; estructura de pases; control del espacio visible en momentos clave; formaciones y cambios.
- **No captura:** movimientos sin balón entre eventos, datos físicos, jugadores fuera de cámara, identidad de los jugadores en los frames 360 (salvo el actor), ni instrucciones del entrenador que no se reflejen en la conducta.
- Los datos vienen de la transmisión de TV: algunos eventos no tienen frame y algunos frames no tienen área visible.

## Propuesta inicial de `config/params.yaml`

```yaml
# Ids reales de la API (prueba de humo, 2026-10-07); valores vigentes en config/params.yaml
equipo: {nombre: "América", team_id: 1229}
entrenador: {nombre: "André Jardine", manager_id: 1000116}
predecesores: [{nombre: "Santiago Solari", manager_id: 25}, {nombre: "Fernando Ortiz", manager_id: 1001173}]
liga: {competition_name: "Liga MX", competition_id: 73, season_ids: [108, 235, 281, 317, 318]}
validacion: {season_id_prueba: 318, torneo_prueba: "Clausura"}

campo: {largo: 120, ancho: 80, porteria: [120, 40]}
tercios: {defensivo_max_x: 40, final_min_x: 80}
presion: {campo_rival_min_x: 60, ultimo_tercio_min_x: 80}
transicion: {fuente: "is_transition", plan_b_segundos: 10}
pase_progresivo: {avance_min_yd: 10, cuenta_entrada_area: true}
balon_parado: {lateral_peligro_min_x: 80}
tramos_min: 15            # 5 para lectura fina del flujo
red_pases: {min_pases_arista: 3}
voronoi: {min_dist_borde: 2.0, momentos: [pase_progresivo, progresion_rival, envio_balon_parado]}
simulacion: {repeticiones: 10000, semilla: 42}
```
