# 360 Frames v2.0.0 (StatsBomb)

- Endpoint: `GET https://data.statsbombservices.com/api/v2/360-frames/{match_id}`
- Respuesta: arreglo JSON, un frame por evento con 360. Se une a Events por `event_uuid` = `id` del evento.

## Campos del frame

| Campo | Tipo | Notas |
| --- | --- | --- |
| `event_uuid` | uuid | Evento al que corresponde |
| `visible_area` | [x1, y1, x2, y2, …, x1, y1] | Polígono cerrado visible para la cámara. Puede venir vacío (cámara fuera de la cancha). Puede haber jugadores fuera del polígono si se colocaron a mano |
| `freeze_frame` | [obj] | Jugadores visibles (abajo) |
| `line_breaking_pass` | bool | Fue pase, cruzó una línea defensiva (defensores juntos) y progresó lo suficiente hacia el centro de la portería |
| `num_defenders_on_goal_side_of_actor` | int | Rivales visibles más cerca de su portería (en x) que el actor |
| `distance_to_nearest_defender` | float | Distancia del actor al rival visible más cercano (coordenadas de cancha) |
| `ball_receipt_in_space` | bool | La recepción fue en un área libre de defensores de radio ≥ 2 yd |
| `ball_receipt_exceeds_distance` | int | 2, 5 o 10: radio libre alcanzado en la recepción |
| `visible_player_counts` | [{team_id, count}] | Jugadores visibles por equipo |
| `distances_from_edge_of_visible_area` | [{point_id, distance}] | Distancia de cada jugador al borde del área visible (filtro de calidad para Voronoi) |

## `freeze_frame[]`

`location` [x, y] (orientado como el evento: el equipo del actor ataca de 0 a 120 en x), `teammate` (mismo equipo que el actor), `actor` (quien ejecuta el evento), `keeper`.

**Sin identidad de jugadores**: solo se sabe equipo, actor y portero.

## Advertencias (del PDF)

- Se recolecta sobre todo de la transmisión de TV: no siempre se ven los 22 jugadores.
- No todos los frames traen `visible_area` y no todos los eventos tienen frame.
- Algunos eventos no tienen jugador marcado como `actor`.
- En casos raros, `keeper` marca al portero del equipo del actor sin marcarlo como `teammate`.

## Ejemplo

```json
[{"event_uuid": "97a8f158-…", "visible_area": [37, 80, 25, 0, 60, 0, 42, 80, 37, 80],
  "freeze_frame": [{"location": [104.2, 54.0], "teammate": true, "actor": true, "keeper": false},
                   {"location": [104.2, 54.0], "teammate": false, "actor": false, "keeper": true}]}]
```
