# Framework analítico — borrador v0

Toda métrica, visualización y modelo del proyecto se deriva de estas definiciones. Si algo no está aquí, se agrega aquí primero. Los umbrales viven en `config/params.yaml`; los valores de abajo son propuestas iniciales que se confirman después de la prueba de humo y del inspector.

**Regla de oro:** si StatsBomb define el objeto, lo adoptamos; si no, lo definimos aquí.

## Coordenadas y orientación

- Cancha de 120 × 80 yardas; centro (60, 40). Tercios: defensivo x < 40, medio 40 ≤ x < 80, final x ≥ 80.
- Verificado con la API real (9 oct): cada evento viene en la perspectiva del equipo que lo ejecuta (ataca hacia x = 120; los tiros de ambos equipos tienen x ≈ 106). Antes de mezclar acciones de ambos equipos en un mismo mapa, reorientar las del rival con (120 − x, 80 − y) (`ojo.framework.contexto.orientar`).
- Los freeze frames 360 están en la orientación del evento (el equipo del actor ataca de 0 a 120).

## Partidos válidos

- Eventos: `collection_status = Complete` y `match_status = available`.
- Métricas 360: además `match_status_360 = available`. Se reporta la cobertura (porcentaje de eventos con frame y con `visible_area`).
- Equipo y entrenador: se filtran por `team_id` y por el id del entrenador en `home_team.managers` / `away_team.managers` (API Matches; la documentación decía `home_team_manager`), no por fechas.

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
| PPDA | Por partido, `team_match_ppda`. Por tramo: pases del rival con x < `presion.ppda_zona_max_x` (en su orientación) entre las acciones defensivas propias en esa misma zona, con la definición de StatsBomb: entradas (Duel tipo Tackle), intercepciones (Interception) y faltas (Foul Committed); los bloqueos no cuentan. Se valida que, agregada al partido, se acerque a `team_match_ppda` | StatsBomb (tramo: propia) |
| Altura de recuperación | x promedio de las recuperaciones del equipo en juego abierto: Ball Recovery sin `recovery_failure` e Interception con `outcome` 4 Won, 15 Success o 16 Success In Play | Propia |
| Pase completo | Evento Pass sin `outcome` | StatsBomb |
| Pase progresivo | Pase completo en juego abierto que acerca el balón al centro de la portería (120, 40) al menos `pase_progresivo.avance_min_yd`, o que entra al área | Propia |
| Balón parado | `play_pattern` From Corner, From Free Kick, From Throw In; fase con `set_piece_phase` (1 o 2). Lateral en zona de peligro: x ≥ 80 | StatsBomb + propia |
| Espacio al recibir | Métricas 360: `ball_receipt_in_space`, `ball_receipt_exceeds_distance`, `distance_to_nearest_defender` | StatsBomb |
| Pase que rompe líneas | `line_breaking_pass` (360) | StatsBomb |
| Control territorial | Fracción del espacio alcanzado que controla el equipo del actor según Voronoi de los jugadores visibles; cada celda se recorta a cancha ∩ `visible_area` ∩ un círculo de radio `voronoi.alcance_max_yd` alrededor del jugador (las zonas vacías lejanas no cuentan). Se excluyen jugadores a menos de `voronoi.min_dist_borde` del borde visible, salvo el actor | Propia |
| Grafo de vecindad | Dos jugadores son vecinos si sus celdas comparten un borde de al menos `voronoi.min_borde_arista_yd` (dual de Delaunay dentro de lo visible). Métricas: apoyos (compañeros vecinos del actor), rivales cerca (rivales vecinos del actor), frontera (yardas de borde entre celdas de equipos distintos) y distancia media entre compañeros vecinos | Propia |
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

## Lectura del partido por puntos de quiebre

Idea central (12 oct): el partido se lee momento a momento y se corta en tramos entre **puntos de quiebre**. Cada quiebre se compara contra el mismo partido (antes y después) y contra ventanas de control sin quiebre. Comparar dentro del partido mantiene fijos la cámara, el rival y el día, que son los factores que confundieron la comparación de promedios entre entrenadores (notebook 01).

**Reloj.** Minuto de StatsBomb dentro de cada periodo. Ninguna ventana cruza el descanso.

**Tipos de quiebre** (siempre desde el América; "a favor" = beneficia al América):

| Tipo | Definición | Corta ventanas |
| --- | --- | --- |
| `gol_favor` / `gol_contra` | Tiro con resultado Goal u Own Goal For del equipo (sin tanda de penales) | Sí |
| `expulsion_favor` / `expulsion_contra` | Tarjeta Red Card o Second Yellow (en Foul Committed o Bad Behaviour) al rival / al América | Sí |
| `cambio_sistema_propio` / `cambio_sistema_rival` | Tactical Shift con una formación distinta de la vigente | No |
| `sustitucion_tactica_propia` / `_rival` | Substitution con motivo Tactical | No |
| `sustitucion_lesion_propia` / `_rival` | Substitution con motivo Injury: cambio forzado, comparación natural frente al táctico | No |

Los quiebres que **no** cortan suelen ser la respuesta del entrenador al quiebre; por eso se miden pero no truncan las ventanas de otros quiebres.

**Ventanas** (en minutos enteros; m = minuto del quiebre). Antes: [m − `quiebres.ventana_min`, m − `quiebres.exclusion_min`); después: (m + `exclusion_min`, m + `ventana_min`]; el minuto del quiebre nunca cuenta. Se truncan al inicio o fin del periodo y en el siguiente quiebre que corta; si una queda más corta que `quiebres.min_ventana_min`, el quiebre se descarta. Las tasas se expresan por minuto para que ventanas truncadas sean comparables.

**Efecto de un tipo de quiebre** (diferencia en diferencias): promedio de (después − antes) en los quiebres de ese tipo, menos el promedio de (después − antes) en **ventanas de control**: partidos del América con el mismo estado del marcador antes, minuto ± `quiebres.tolerancia_control_min`, mismo periodo y sin quiebre que corte dentro de la ventana (hasta `quiebres.max_controles` por quiebre). Así se descuenta lo que cambia solo con el paso del tiempo. Intervalo por bootstrap de partidos.

**Métricas por bloque** (dos bandas: América y rival en la misma ventana; coordenadas en la perspectiva de cada equipo):

| Bloque | Métrica | Definición |
| --- | --- | --- |
| Estructura | Control en campo rival | Control medio (Voronoi) de las acciones del equipo con x ≥ `presion.campo_rival_min_x` |
| | Altura del bloque | x medio de los jugadores visibles del equipo sin el portero |
| | Ancho / largo del bloque | Rango de y / rango de x de esos jugadores. El largo del bloque sin balón aproxima el espacio entre líneas (sin identidad no hay líneas por posición) |
| | Compactación | Área de la envolvente convexa de esos jugadores entre su número |
| Circulación | Centralización de la red | Red de pases completos por posición (nodo = posición; posición del receptor = su posición más frecuente en el partido); centralización = Σ (s_max − s_i) / (n − 1), donde s_i es la fracción de los pases (dados y recibidos) que toca la posición i y n las posiciones que tocan el balón; 0 = circulación repartida, cerca de 1 = todo pasa por una posición. Solo ventanas con al menos `red_pases.min_pases_ventana` pases |
| Intensidad | Presiones, faltas, contrapresiones | Eventos Pressure, Foul Committed y acciones con `counterpress`, por minuto |
| Valor | xG, OBV, field tilt | xG de los tiros y OBV total por minuto; field tilt: pases completos del equipo en el último tercio entre los de ambos equipos |
| Riesgo | Tiros en transición y contragolpes en contra | Tiros del rival con `is_transition`; posesiones del rival que empiezan con `play_pattern` From Counter (en el minuto en que empiezan); por minuto |

Las métricas de forma solo usan frames con al menos `forma.min_jugadores_equipo` jugadores visibles de ese equipo.

**Hipótesis de agresividad.** Panel por tramos de `agresividad.tramo_min` minutos dentro de cada periodo: la presión del América en un tramo (presiones en campo rival por minuto) se relaciona con, en el tramo siguiente del mismo periodo, su xG a favor, sus faltas y los contragolpes y tiros en transición en contra. Modelo con efectos fijos por partido y por estado del marcador, la misma respuesta en el tramo actual como control, errores agrupados por partido e interacción con los tramos que empiezan en el minuto `agresividad.tardio_min` o después. Es una relación temporal, no causalidad.

**Barrido de estilo** (notebook 03). Métricas de Team Match Stats de toda la liga, ajustadas por la liga: valor del América menos el promedio de la liga en el mismo torneo. Jardine frente a Solari y Ortiz, intervalo por bootstrap de partidos.

**Criterio de hallazgo** (fijado el 12 oct, antes de ver resultados). Un efecto es hallazgo si cumple las tres:
1. Su intervalo de confianza (`estadistica.nivel_confianza`) no cruza 0.
2. Su tamaño es al menos `hallazgo.tamano_min_de` desviaciones estándar de la variación entre partidos de esa métrica (DE del valor por partido en los partidos del América usados).
3. Va en la misma dirección en al menos `hallazgo.min_torneos_misma_direccion` de los torneos de Jardine.

IMPOR1: el Clausura 2026 es el torneo de prueba (sección "Validación, causalidad y decisión"). Los hallazgos alimentan los principios que luego se validan ahí, así que el criterio se evalúa en los 5 torneos de entrenamiento (AP23–AP25: al menos 4 de 5) y el CL26 se usa al final solo para confirmar la dirección.

Se reporta cuántas pruebas se hicieron, porque con muchas pruebas algunas pasan por azar. Agregado al ver los primeros resultados, sin cambiar qué pasa: los efectos con menos de `hallazgo.partidos_aviso` partidos se marcan como muestra chica (con tan pocos partidos el bootstrap subestima la incertidumbre). OBS1: en los quiebres, la condición 2 filtra poco, porque una ventana de 10 minutos cambia mucho más que el promedio de un partido completo; los filtros que pesan son la 1 y la 3. **Voronoi** sigue como lente estructural si alguna de sus métricas (control en campo rival, forma) cumple el criterio después de algún quiebre; si no, queda como apoyo visual. El resultado final es una tabla de qué pasa y qué no.

## Índice Proactivo–Reactivo (propuesta del 14 oct, pendiente de confirmar)

Escala de 0 a 100 que resume cómo juega un equipo en cada minuto: **0 = reactivo** (juego directo y transiciones), **100 = proactivo** (iniciativa y posesión asentada). Se calcula para los dos equipos (dos bandas). Código: `ojo.lentes.indice`.

| Componente | Definición (ventana hacia atrás de `indice.ventana_min` minutos) | Signo |
| --- | --- | --- |
| Juego asentado | Duración de pases, conducciones y tiros en estado de control (Phases of Play: `is_transition` falso) entre la duración de los que tienen fase | + |
| Posesión | Duración de las acciones con balón del equipo entre las de ambos | + |
| Field tilt | Pases completos en el último tercio entre los de ambos equipos | + |
| Espacio en campo rival | Control medio (Voronoi) de las acciones del equipo en campo rival | + |
| Altura del bloque | x media de los jugadores visibles del equipo sin balón (sin porteros) | + |
| Presión alta | Presiones en campo rival por minuto | + |
| Juego directo | `possession_directness` medio de las acciones con balón | − |
| Pase largo | Largo medio de los pases (yd) | − |

**Cálculo.** Cada componente se estandariza (z) con media y DE de los minutos de entrenamiento (ambos equipos, partidos del América sin el torneo de prueba); se multiplica por su signo; el compuesto es el promedio de los z disponibles (mismo peso); el índice es el percentil del compuesto frente a los minutos de entrenamiento. Por minuto y no por foto: las fotos 360 solo existen en eventos y dependen de la cámara.

**Lectura.** Bajo `indice.bandas[0]` el minuto se lee como reactivo, sobre `indice.bandas[1]` como proactivo y en medio como equilibrado.

**Supuestos.** Pesos iguales hasta verificar con PCA que el primer componente coincide con el eje (TODO1 en `ojo.lentes.indice`). La escala es relativa a los partidos del América y sus rivales, no a toda la liga (solo hay eventos de esos partidos).

## Animación del Voronoi (seguimiento estimado)

El 360 no identifica a los jugadores entre fotos: solo marca al que ejecuta (`actor`). Los **nombres** de la página salen de Events (`player` del evento, `pass.recipient` del pase) y de Lineups (`player_nickname`); ningún otro punto de la foto lleva nombre.

Para animar una jugada (`ojo.lentes.seguimiento`) se **estima** la correspondencia entre fotos consecutivas: en cada equipo, asignación de costo mínimo (distancia total) y solo parejas con distancia ≤ `animacion.velocidad_max_yd_s` × Δt + `animacion.tolerancia_yd`; los demás entran o salen de cámara. Entre dos fotos, las posiciones se interpolan y el Voronoi se recalcula en el navegador con las mismas reglas (cancha ∩ área visible ∩ alcance). Fotos a menos de `animacion.min_dt_s` se tratan como la misma. Es una estimación para dibujar, no un dato: ninguna métrica la usa. En el modo minuto a minuto (fotos a 60 s) no se interpola movimiento: se funde una foto con la siguiente.

## Situaciones del explorador

Filtros de la barra lateral del reporte (`contexto/resumenes.md`). Cada evento con 360 cae en las situaciones que cumple; "todas" no filtra. Coordenadas en la perspectiva de quien ejecuta el evento.

| id | Definición |
| --- | --- |
| `salida` | Posesión del América en juego abierto con el balón en su tercio defensivo (x < `tercios.defensivo_max_x`) |
| `presion_alta` | Posesión del rival en juego abierto con el balón en el tercio defensivo del rival (x < `tercios.defensivo_max_x` en su perspectiva): el América presiona arriba |
| `transicion_defensiva` | Posesión del rival con `is_transition` (plan B: los primeros `transicion.plan_b_segundos` tras una recuperación del rival) |
| `transicion_ofensiva` | Posesión del América con `is_transition` (mismo plan B) |
| `gana` / `empata` / `pierde` | Estado del marcador del América antes del evento (`ojo.framework.contexto.marcador`) |
| `balon_parado_favor` / `balon_parado_contra` | `play_pattern` de balón parado con posesión del América / del rival |

Una combinación rival · torneo · situación con menos de `resumenes.min_partidos` partidos se marca como muestra insuficiente y no muestra métricas.

## Validación, causalidad y decisión

**Partición temporal**

- Entrenamiento: los torneos de Jardine del Apertura 2023 al Apertura 2025. Prueba: el Clausura 2026 (`validacion` en `params.yaml`), que no se usa para definir principios, umbrales ni modelos hasta la evaluación final.
- Plan B, si los organizadores no permiten datos posteriores al Clausura 2025: entrenamiento AP23–AP24 y prueba en el Clausura 2025 (`validacion.plan_b`).
- Sin fuga: todo lo que alimenta una predicción o una ficha del torneo de prueba se calcula con partidos anteriores a ese día. La fuerza del rival se recalcula con partidos previos en vez de usar la estadística de la temporada completa.

**Predicción del comportamiento (R²)**

- Variables objetivo, por partido y por tramo: PPDA, field tilt, control territorial y altura de recuperación del América.
- Variables explicativas: marcador, localía, fuerza del rival, momento y los principios estimados en entrenamiento.
- Líneas base: el promedio de la liga en la misma situación y el América de Ortiz en la misma situación. Se reporta R² y error absoluto medio en el torneo de prueba; si los principios no mejoran a la línea base, se dice.

**Predicción de resultados (Monte Carlo antes del partido)**

- Para cada partido del torneo de prueba se estima el xG esperado a favor y en contra de cada equipo solo con información previa: forma reciente (últimos `simulacion.forma_partidos` partidos), perfil del rival, localía y, para el América, los principios de Jardine.
- Se simulan `simulacion.repeticiones` marcadores y se obtienen las probabilidades de ganar, empatar o perder.
- Se evalúa con log-loss y calibración sobre todos los partidos de la Liga MX del torneo de prueba, y aparte sobre los del América. Líneas base: las frecuencias históricas de resultados por localía y el xG reciente de cada equipo sin principios.

**Monte Carlo después del partido (opcional, interpretativo)**

- Con el xG de los tiros del propio partido se simula el marcador para medir qué tan merecido fue el resultado. No es predicción y no cuenta para la parte predictiva.

**Efecto del relevo (causal)**

- Relevo: cambio de `manager_id` de un equipo entre partidos consecutivos. Los interinatos de menos de `relevos.min_partidos` partidos no cuentan como relevo (por ejemplo, Diego Cervantes en enero de 2025).
- Efecto de un relevo: cambio en las métricas del equipo entre los `relevos.ventana_partidos` partidos antes y después, menos el cambio promedio de la liga en las mismas fechas.
- Ortiz → Jardine frente a: el placebo Solari → Ortiz (débil: 27 partidos de Solari y salida a mitad de torneo) y, si alcanza el tiempo, la distribución de todos los relevos de la Liga MX en la ventana. Si el efecto de Jardine queda dentro del rango típico, no se atribuye a su estilo.

**Decisión real**

- Decisiones observables del torneo de prueba (sustituciones tácticas, cambios de formación, con minuto y marcador) frente a lo que recomendaba la herramienta con datos previos. Se reporta cuántas veces coincidieron; lo que pasó después se reporta como correlación.

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
validacion:
  season_id_prueba: 318          # 2025/26
  torneo_prueba: "Clausura"
  plan_b: {season_id_prueba: 317, torneo_prueba: "Clausura"}
relevos: {min_partidos: 5, ventana_partidos: 10}

campo: {largo: 120, ancho: 80, porteria: [120, 40]}
tercios: {defensivo_max_x: 40, final_min_x: 80}
presion: {campo_rival_min_x: 60, ultimo_tercio_min_x: 80, ppda_zona_max_x: 72}   # 72 = 60 % de la cancha desde la portería del rival
transicion: {fuente: "is_transition", plan_b_segundos: 10}
pase_progresivo: {avance_min_yd: 10, cuenta_entrada_area: true}
balon_parado: {lateral_peligro_min_x: 80}
tramos_min: 15            # 5 para lectura fina del flujo
red_pases: {min_pases_arista: 3, min_pases_ventana: 15}
voronoi: {min_dist_borde: 2.0, alcance_max_yd: 20, min_borde_arista_yd: 0.5, momentos: [pase_progresivo, progresion_rival, envio_balon_parado]}
simulacion: {repeticiones: 10000, semilla: 42, forma_partidos: 5}
resumenes: {min_partidos: 3, rejilla: {columnas: 12, filas: 8}}
estadistica: {bootstrap_repeticiones: 2000, nivel_confianza: 0.95, min_eventos_zona: 30}
quiebres: {ventana_min: 10, exclusion_min: 1, min_ventana_min: 4, tolerancia_control_min: 5, max_controles: 20}
forma: {min_jugadores_equipo: 4}
agresividad: {tramo_min: 5, tardio_min: 65}
casos: {tramo_min: 5, max_jugadas: 12, simplificar_yd: 0.25}
indice: {ventana_min: 5, bandas: [40, 60], componentes: {control: 1, posesion: 1, field_tilt: 1, control_campo_rival: 1, altura_sin_balon: 1, presion_alta: 1, directness: -1, largo_pase: -1}}
animacion: {velocidad_max_yd_s: 10, tolerancia_yd: 3, min_dt_s: 0.3, escala_tiempo: 1.5, duracion_s: [0.35, 2.5], max_fotos: 30}
hallazgo: {tamano_min_de: 0.5, min_torneos_misma_direccion: 4, partidos_aviso: 10}
```
