# `resumenes.json`: contrato del explorador

Es el único archivo de datos que viaja dentro del reporte HTML. Lo genera Python a partir de la caché y lo lee la barra lateral (rival · torneo · situación) en el navegador, sin red y sin llamar a la API.

Versión del esquema: **1**. Validador: `ojo.salidas.resumenes.validar`. Ejemplo con datos inventados: `tests/fixtures/resumenes_ejemplo.json`.

## Reglas

1. **Solo agregados.** Ningún evento, frame ni posición de un jugador en un momento concreto: promedios, conteos y mapas por zona (regla no negociable 1).
2. **Siempre con su muestra.** Toda combinación lleva `n_partidos`; si es menor que `resumenes.min_partidos` (params.yaml), sus métricas van en `null` y `muestra_suficiente` es `false`. La barra muestra "muestra insuficiente" en lugar de un número.
3. **Perspectiva del América.** Coordenadas y mapas con el América atacando hacia la derecha (x = 120). Las métricas del rival son las del rival en esos mismos partidos.
4. **Redondeo.** Proporciones con 3 decimales (0.583), yardas y conteos con 1 decimal. `null` cuando no aplica o no hay dato; nunca 0 en su lugar.
5. **El torneo de prueba se marca.** El Clausura 2026 lleva `"prueba": true`: el modelo no lo vio y la barra lo distingue (ver `contexto/framework.md`, "Validación, causalidad y decisión").
6. **Ids como texto en las claves.** Los objetos indexados por id usan el id como texto ("1229"); "todos" es la opción sin filtro.

## Estructura

```text
{
  "meta":            {...}   quién, cuándo, con qué umbrales
  "catalogos":       {...}   opciones de cada filtro
  "combinaciones":   {...}   métricas por rival|torneo|situación
  "fichas":          {...}   ficha de 10 segundos por rival
  "entrenadores":    {...}   Solari, Ortiz y Jardine por situación (sección Relevo)
  "caso_por_defecto":{...}   lo que la página muestra al abrir
}
```

### `meta`

| Campo | Tipo | Ejemplo | Para qué |
| --- | --- | --- | --- |
| `version_esquema` | entero | `1` | La página rechaza versiones que no conoce |
| `generado` | texto ISO | `"2026-10-12T21:30:00"` | Pie del reporte |
| `equipo` | `{id, nombre}` | `{"id": 1229, "nombre": "América"}` | Títulos |
| `entrenador` | `{id, nombre}` | `{"id": 1000116, "nombre": "André Jardine"}` | Títulos |
| `min_partidos` | entero | `3` | Umbral de muestra usado |
| `rejilla` | `{columnas, filas, largo, ancho}` | `{"columnas": 12, "filas": 8, "largo": 120, "ancho": 80}` | Cómo leer los mapas |
| `aviso` | texto | `"Resultados agregados; datos StatsBomb solo para la competencia."` | Pie del reporte |

### `catalogos`

```json
"catalogos": {
  "rivales":   [{"id": "1301", "nombre": "Cruz Azul", "n_partidos": 12}],
  "torneos":   [{"id": "AP23", "nombre": "Apertura 2023", "prueba": false},
                {"id": "CL26", "nombre": "Clausura 2026", "prueba": true}],
  "situaciones": [{"id": "salida", "etiqueta": "Salida de balón", "grupo": "fase",
                   "definicion": "El América tiene el balón en juego abierto en su tercio defensivo"}]
}
```

`rivales` va ordenado por `n_partidos` (de mayor a menor), como en la maqueta. `grupo` agrupa las situaciones en la barra: `fase`, `marcador`, `balon_parado`.

**Situaciones (versión 1)**; cada una se define en `contexto/framework.md`, sección "Situaciones del explorador":

| id | Etiqueta | Grupo |
| --- | --- | --- |
| `todas` | Todo el partido | — |
| `salida` | Salida de balón | fase |
| `presion_alta` | Presión alta | fase |
| `transicion_defensiva` | Transición defensiva | fase |
| `transicion_ofensiva` | Transición ofensiva | fase |
| `gana` / `empata` / `pierde` | Ganando / Empatando / Perdiendo | marcador |
| `balon_parado_favor` / `balon_parado_contra` | Balón parado a favor / en contra | balon_parado |

### `combinaciones`

Clave: `"<rival>|<torneo>|<situacion>"`, con `todos` como comodín. Ejemplos: `"1301|AP24|salida"`, `"todos|todos|todas"`, `"1301|todos|pierde"`. Solo se incluyen las combinaciones con al menos un partido.

```json
"1301|todos|salida": {
  "n_partidos": 12,
  "n_acciones": 1840,
  "muestra_suficiente": true,
  "metricas": {
    "america": {"control": 0.583, "frontera": 158.2, "apoyos": 1.6, "rivales_cerca": 1.9,
                "distancia_companeros": 12.1, "ppda": 9.4, "field_tilt": 0.612,
                "altura_recuperacion": 48.3, "xg_favor_90": 1.71, "xg_contra_90": 0.93},
    "rival":   {"control": 0.417, "...": "mismas claves"},
    "liga":    {"control": null, "ppda": 10.8, "...": "promedio de la liga en la misma situación"}
  },
  "resultados": {"ganados": 7, "empatados": 3, "perdidos": 2},
  "mapa_control": [[0.41, 0.52, "... 12 columnas"], "... 8 filas"],
  "mapa_cobertura": [[34, 51, "..."], "..."],
  "frase": "Contra Cruz Azul, en la salida de balón el América controló el 58 % del espacio que se ve (12 partidos)."
}
```

| Campo | Qué es |
| --- | --- |
| `n_partidos`, `n_acciones` | Muestra: partidos y eventos con 360 analizables en esa situación |
| `metricas.america` / `.rival` | Promedios por partido de cada equipo en esa situación. `control` y demás métricas de Voronoi vienen de `ojo.lentes.voronoi`; `ppda`, `field_tilt` y `altura_recuperacion`, del paso 6 |
| `metricas.liga` | Referencia: promedio de la liga en la misma situación. Las métricas de Voronoi quedan en `null` mientras no se descargue el 360 de toda la liga |
| `resultados` | Partidos ganados, empatados y perdidos de esa combinación |
| `mapa_control` | Matriz `filas × columnas` (y de arriba abajo, x de izquierda a derecha): fracción del tiempo visible en que el América controla cada zona. `null` en zonas sin cobertura suficiente |
| `mapa_cobertura` | Matriz del mismo tamaño: número de frames que vieron cada zona (para atenuar zonas poco vistas) |
| `frase` | Una oración generada desde los números, en lenguaje de cancha. Con muestra insuficiente: "Muestra insuficiente: 2 partidos." |

### `fichas` (ficha de 10 segundos)

Una por rival, con todos sus partidos contra el América en la ventana.

```json
"fichas": {
  "1301": {
    "progresa_por":   {"izquierda": 0.42, "centro": 0.21, "derecha": 0.37},
    "concede_en":     [[0.01, 0.02, 0.05, "... 6 columnas"], "... 3 filas"],
    "participa_poco": {"posicion": "Extremo derecho", "acciones_90": 18.4},
    "balon_parado":   {"xg_concedido_por_corner": 0.071, "zona": "segundo palo"},
    "respuesta_jardine": "Ante rivales parecidos, salida en tres y lateral izquierdo alto; ganó 4 de 6."
  }
}
```

`concede_en` es una rejilla 6 × 3 (tercios de ancho por sextos de largo) con el xG concedido por el rival en cada zona, en perspectiva del América atacando.

### `entrenadores` (sección Relevo)

Clave: id del entrenador. Dentro, una entrada por situación con las métricas del América bajo ese entrenador y su muestra.

```json
"entrenadores": {
  "1000116": {"nombre": "André Jardine", "n_partidos": 129,
              "situaciones": {"todas": {"control": 0.534, "ppda": 9.1, "...": "..."}}}
}
```

### `caso_por_defecto`

Lo que la página abre sin tocar la barra. El texto redactado a mano del caso vive en el reporte (el HTML de la entrega), no en este archivo.

```json
"caso_por_defecto": {"rival": "1301", "torneo": "todos", "situacion": "salida"}
```

## Cómo lo usa la página

1. Lee `catalogos` para pintar la barra.
2. Al cambiar un filtro, arma la clave `rival|torneo|situacion` y busca en `combinaciones`; si no existe, muestra "sin partidos".
3. Dibuja `mapa_control` como rejilla sobre la cancha (dorado = América, blanco = rival), atenuando con `mapa_cobertura`.
4. Si el rival no es `todos`, muestra su ficha de `fichas`.
