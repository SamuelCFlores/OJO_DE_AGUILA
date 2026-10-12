# Barra lateral del explorador: elementos para el diseño

Inventario de lo que lleva la barra lateral (y el panel que controla), con el campo de `resumenes.json` que alimenta cada elemento (`contexto/resumenes.md`). Sirve para diseñarla en Figma sin inventar datos que no existen. Identidad: `branding/README.md`.

La barra **filtra resultados ya calculados**: no llama a la API ni a ningún servidor.

## Flujo

```text
API StatsBomb → caché (02) → parquet (03) → framework + lentes (04…) → resumenes.json (05) → barra lateral → panel
```

## Elementos de la barra

| # | Elemento | Qué muestra | Sale de | Estados |
| --- | --- | --- | --- | --- |
| 1 | Placa del rival elegido | "RIVAL", nombre y chip "N PARTIDOS" | `catalogos.rivales[].nombre`, `combinaciones[clave].n_partidos` | Con rival · "Todos los rivales" |
| 2 | Lista de rivales | Nombre y partidos contra el América, de más a menos | `catalogos.rivales` (ya viene ordenada) | Normal · hover · seleccionado |
| 3 | Selector de torneo | Chips AP23 … CL26 y "Todos" | `catalogos.torneos` | Normal · seleccionado · sin partidos con ese rival (deshabilitado) · **prueba** (CL26, estilo distinto: el modelo no lo vio) |
| 4 | Selector de situación | Chips agrupados: Fase (salida, presión alta, transiciones), Marcador (ganando, empatando, perdiendo), Balón parado (a favor, en contra) y "Todo el partido" | `catalogos.situaciones` (`grupo` agrupa) | Normal · seleccionado · sin partidos (deshabilitado). Una situación a la vez |
| 5 | Indicador de muestra | "12 partidos · 1,840 acciones" o "Muestra insuficiente: 2 partidos" | `n_partidos`, `n_acciones`, `muestra_suficiente`; umbral en `meta.min_partidos` | Suficiente · insuficiente (aviso visible, sin números) |
| 6 | Resumen rápido | Control del América frente al rival y partidos G-E-P | `metricas.america.control`, `metricas.rival.control`, `resultados` | Con datos · vacío |
| 7 | Ficha de 10 segundos | Botón o pestaña que abre la ficha del rival | `fichas[rival]` | Visible solo con un rival elegido |
| 8 | Volver al caso principal | Regresa a los filtros del caso por defecto | `caso_por_defecto` | Visible cuando los filtros cambiaron |
| 9 | Leyenda | Dorado = América · blanco = rival · línea blanca = frontera | Fija | — |

## Panel principal (lo que cambia con la barra)

| Elemento | Sale de |
| --- | --- |
| Título "AMÉRICA VS RIVAL" y migas (Pilar · torneos) | Filtros elegidos y `catalogos` |
| Mapa de control sobre la cancha (rejilla 12 × 8; atenuado donde hubo poca cobertura) | `mapa_control`, `mapa_cobertura`, `meta.rejilla` |
| Frase en lenguaje de cancha | `frase` |
| Métricas a dos bandas (América · rival · liga) | `metricas` |
| Ficha de 10 segundos (si se abre): carriles de progresión, zonas donde concede, posición que participa poco, balón parado, respuesta de Jardine | `fichas[rival]` |

## Comportamiento

- **Sin combinación:** si la clave `rival|torneo|situacion` no existe, el panel dice "Sin partidos con estos filtros" y sugiere quitar un filtro.
- **Muestra insuficiente:** se muestra el aviso y el número de partidos; nunca un porcentaje.
- **CL26:** al elegirlo, el panel avisa que es el torneo de prueba (validación).
- **Teléfono:** la barra se vuelve un panel desplegable arriba del contenido; los chips hacen scroll horizontal.
- **Accesibilidad:** todo se opera con teclado; los chips usan `aria-pressed`; el contraste del texto sobre dorado y sobre azul cumple AA.

## Lo que no lleva

- Nombres de jugadores en mapas ni posiciones de un momento concreto (solo agregados; regla 1).
- Filtros que no existen en `resumenes.json` (localía, tramo): si se quieren, primero se agregan al contrato.
