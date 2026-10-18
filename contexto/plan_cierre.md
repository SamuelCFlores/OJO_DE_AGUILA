# Plan de cierre · 18 oct 2026

Lo trabajan chamuel y Claude Code. Rúbrica oficial (4 × 25 %): innovación, comunicación, accionabilidad, y metodología y visualización. La entrega es **un solo HTML** (`scripts/09_entrega.py`) y un video de máximo 5 minutos, el 22 de octubre.

## 1. Entendimiento

**Objetivo:** cerrar lo que falta para que el HTML único cuente la historia de Jardine con evidencia, la valide en el torneo que el análisis no vio y la lleve a decisiones.

**Ya está, al 18 oct:**
- Criterio v2 (placebo, FDR), con 6 principios.
- Índice confirmado con PCA.
- PPDA y altura de recuperación.
- Balón parado y uso de jugadores.
- Matriz de situaciones y fichas de 17 rivales.
- Vista Decidir.
- HTML único.

**Supuestos:**
- [Supuesto: los organizadores aceptan el Clausura 2026; si no, la validación se repite en el CL25 (plan B del framework).]
- [Supuesto: el CL26 se abre una sola vez, hoy, con los principios ya fijados por el criterio v2; nada se cambia después de verlo.]

## 2. Plan (en orden, con dependencias)

| # | Pieza | Depende de | Salida |
| --- | --- | --- | --- |
| A | **Validación en el CL26** (notebook 06) | criterio v2 | `outputs/hallazgos/validacion_cl26.parquet`; lectura en el notebook |
| B | **Casos de decisión** (3, elegidos por regla) | A, matriz, fichas | `decidir.casos` en `datos.js`; sección 5 de Decidir |
| C | **Vista Método** en el HTML: pregunta y datos, framework, lentes, criterio v2, principios con evidencia, validación, límites y glosario | A | `metodo` en `datos.js` y la vista en `app/` |
| D | **Guion del video** (5 min) | B, C | `contexto/guion_video.md` |
| E | **Documentación y verificación**: `CLAUDE.md`, `app/README.md`, bitácora, pruebas, `datos.js`, entrega, revisión en el navegador | todo | commits en `tests` |

**Validación (A).** Cada principio se mide en los partidos del CL26 con la misma métrica y se compara con Solari y Ortiz en entrenamiento:
- se informa si **mantiene la dirección** y con qué intervalo;
- si hay pocos eventos, dice "sin muestra suficiente".

Además, la matriz por situación en el CL26 frente a AP23–AP25, y el índice medio.

**Reglas de los casos (B), fijadas antes de ver los resultados de cada partido:**
1. **"Ganando por 1, no regalar la iniciativa"** (matriz): el partido del CL26 con más minutos ganando por 1. Qué marcaba la matriz, qué hizo el América (índice y PPDA en esos minutos) y qué pasó después.
2. **"Alerta: cambiar el sistema le cuesta"** (principio): el primer cambio de sistema propio del CL26. xG antes y después, frente a lo que anticipaba el principio.
3. **La eliminatoria** (ficha): los cuartos de final del CL26. La ficha del rival armada solo con datos previos y lo que pasó en los dos partidos.

En los tres se dice qué recomendaba la herramienta frente a lo que pasó. Nunca se dice que la herramienta habría cambiado algo.

**Queda fuera de este plan (lo decide o lo hace chamuel):**
- V-M14: descargar Poppins.
- Promoción a `main` con PR.
- Grabar el video.
- Correo de entrega.
- Variante de la barra.

## 3. Riesgos y casos límite

- **Muestra chica en el CL26:** 19 partidos y pocas expulsiones o lesiones. Se informa "sin muestra suficiente"; no se fuerza un veredicto.
- **Fuga de información:** las fichas de los casos se arman solo con partidos anteriores al caso.
- **Números escritos a mano en el método:** todo número sale de `datos.js` (V-M11). El texto fijo solo explica.
- **El HTML crece:** se vigila el tamaño de la entrega, hoy 0.8 MB.

## 4. Criterios de calidad

- **El CL26 se usa una sola vez,** y se informa aunque un principio no se sostenga.
- **Los casos salen de reglas escritas antes,** sin lenguaje de "habría cambiado".
- **El HTML único funciona sin conexión:**
  - abre sin errores de consola;
  - no tiene scroll horizontal a 375 y 1280 px;
  - con movimiento reducido no anima;
  - recorre sus 4 vistas con teclado.
- **Las pruebas pasan,** y la lógica nueva tiene las suyas.
- **Nada de datos en git:** `outputs/` queda fuera.
