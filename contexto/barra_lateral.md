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

## Versión 2 (13 oct): propuesta visual + caso Fidalgo

**Histórica:** desde el 18 oct la maqueta definitiva es `app/maqueta.html` (versión 3 de la barra). La maqueta 2 (`scripts/07_caso.py` → `outputs/reportes/maqueta_2.html`, plantilla en `ojo.salidas.app`) toma la estructura del handoff de diseño (`branding/exportados/app_maximalismo`, local) con la paleta de la marca. La barra lleva la mayoría de los elementos:

| # | Elemento | Qué muestra | Cambio frente a la versión 1 |
| --- | --- | --- | --- |
| 1 | Rival | Placa con "SELECCIONADO", nombre (el tamaño se ajusta al largo) y cinta "N PARTIDOS"; lista con conteos | Igual, con el diseño del handoff |
| 2 | Entrenador | Solari · Ortiz · Jardine | **Nuevo** (`entrenadores` del contrato) |
| 3 | Torneo | AP21 … CL26; CL26 con línea punteada (prueba) | Selección **múltiple** |
| 4 | Partido | Los partidos con ese rival en el torneo (fecha, fase, marcador) | **Nuevo** |
| 5 | Situación | General, Fase, Marcador, Balón parado y **Tras un quiebre** (gol a favor / en contra, expulsión a favor / en contra, cambio de sistema, cambio táctico, cambio por lesión) | Selección **múltiple**; grupo nuevo |
| 6 | Condición | Todos · Local · Visita | **Nuevo** (localía) |
| 7 | Muestra | Partidos y jugadas con foto 360 | Igual |
| 8 | Resumen rápido | Control en la foto, xG hasta el momento, global | Igual, con datos del caso |
| 9 | Ficha de 10 segundos y Volver al caso | Botones | Igual (ficha: pronto) |
| — | Leyenda | Pasa al panel "Cómo leerla" (ojo dorado = América, punto blanco = rival, frontera) | Movida |

**Lo que necesita el contrato** (`contexto/resumenes.md`, pendiente): (a) sumas aditivas (numerador y denominador por métrica y por celda del mapa) para combinar varios torneos y situaciones en el navegador; (b) las dimensiones nuevas: entrenador, localía, partido y situaciones "tras un quiebre"; (c) los textos del panel (`lectura`, `metodo`) por combinación. Mientras tanto, la maqueta muestra un solo caso y los controles no recalculan.

## Versión 3 (14 oct): compacta, plegable y ocultable

Decisión del 14 oct: la barra queda **compacta** (lo esencial a la vista) y **plegable** (cada sección se abre o se cierra con su resumen a la derecha), y se **oculta** con un botón: queda un riel con el número de filtros activos, y la elección se recuerda en el navegador. La implementa `app/app.js` con los datos de `barra` en `outputs/app/datos.js` (`ojo.salidas.barra.compacta`).

| Sección | Abierta al inicio | Contenido | Por qué se queda |
| --- | --- | --- | --- |
| Rival | Sí | Placa con cinta de partidos y lista (4 visibles, "Ver todos") | La pregunta es "frente a cada rival"; alimenta la ficha |
| Torneo | Sí | Chips de selección múltiple; CL26 con línea punteada (prueba) | Estabilidad entre torneos y validación |
| Momento | Sí | Marcador (gana, empata, pierde) y Tras un quiebre (gol a favor, gol en contra, uno más, uno menos, cambio propio, cambio rival) | Es la idea central: el partido leído por quiebres y el contexto que pide la convocatoria |
| Condición | Sí | Todos · Local · Visita | La localía está en la pregunta del reto |
| Partidos | No | Los partidos con ese rival en el torneo | Entrada al reproductor de un partido |
| Más filtros | No | Entrenador, Fase (salida, presión alta, transiciones) y Balón parado | Útiles pero secundarios: la fase ya la resume el índice y el balón parado tendrá su sección |

**Sale de la barra:** el resumen rápido (ya está en el contenido), "Volver al caso" (duplicaba "Restablecer") y la leyenda (vive en "Cómo leerla"). Al pie quedan la muestra y el botón de la ficha de 10 segundos.
