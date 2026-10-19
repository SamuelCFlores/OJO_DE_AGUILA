# Auditoría de Ojo de Águila · 19/10/2026

Segunda revisión, de solo lectura, de la rama `tests` (último commit `80c9b1a`, 18/10/2026). No se modificó código, no se tocaron `data/` ni `.env` y no se corrió ningún script de descarga ni ningún notebook: los números de los resultados se toman de las lecturas escritas en los notebooks y en `CAMBIOS/C07_1810.md`, porque los datos no están en el repo. Faltan **3 días** para la entrega (22/10).

## Veredicto en una línea

El salto desde el 14/10 es enorme y el avance **se puede entregar**: casi todo lo de la auditoría anterior quedó resuelto y la entrega existe completa (un HTML con reporte, matriz, fichas, validación y casos). Lo que falta para que sea "casi impecable" no es código nuevo, sino **cuidar cuatro afirmaciones** que hoy dicen más de lo que la evidencia sostiene, y cerrar lo pendiente de chamuel (video, prueba de 90 s, correo).

## 1. Qué pasó con la auditoría del 14/10

| # | Hallazgo del 14/10 | Estado hoy | Comentario |
| --- | --- | --- | --- |
| A1 | El caso estrella (Fidalgo) era de Ortiz | **Resuelto** | El caso ahora es la final del AP23 (roja a Fulgencio), partido de Jardine. Fidalgo queda solo en la maqueta 2 histórica. |
| A2 | Criterio permisivo, sin FDR | **Resuelto** | Criterio v2 en `ojo.lentes.hallazgo`: escala de las ventanas de control, Benjamini-Hochberg y placebo. La tabla final baja de 69 a 30 de 636. Ver N3 sobre el placebo. |
| A3 | Regla del Voronoi casi infalsable | **Resuelto con honestidad** | El notebook 02 dice qué pasó: el control en campo rival solo pasa tras expulsiones (mecánico) y el principio se apoya en la forma del bloque. Ver N2 y N6. |
| A4 | El control depende de los jugadores visibles | **No resuelto, declarado** | Se declaró como límite en Método. Pesa más de lo que parece en el principio estrella (N2). |
| M1 | Faltaban reporte, ficha y PPDA | **Resuelto** | HTML único (`scripts/09_entrega.py`, sin Quarto), fichas de 17 rivales, PPDA y altura de recuperación (r = 0.95 con `team_match_ppda`). |
| M2 | Rúbrica sin confirmar | **Resuelto** | Oficial confirmada el 18/10 (4 × 25 %); la simulación quedó solo explicativa. |
| M3 | Procesado incremental puede dejar salidas viejas | **Riesgo bajo** | Desde el 12/10 no cambió nada en `datos`, `framework`, `minuto`, `voronoi`, `forma` ni `redes` (solo se agregó una constante en `juego.py`). La corrida en limpio sigue siendo buena práctica, no urgencia. |
| M4 | Sin CI | Fuera de alcance | Decisión del 18/10. Aceptable a 3 días. |
| M5 | Resultados solo en notebooks | **Parcial** | Existe `ojo.lentes.efectos`, pero el notebook 02 conserva su copia y `efectos.py` tiene **0 % de cobertura** (N8). |
| B1 | `filtrar_jugadores` puede perder al actor | Abierto | `src/ojo/lentes/voronoi.py:145`: si otro jugador comparte coordenadas y llega antes, el actor se descarta. Raro. |
| B2 | Roja a un suplente cuenta como expulsión | Abierto, declarado | Nota en `situaciones.py`. Importa para N2: hay pocas expulsiones y conviene revisarlas a mano. |
| B3 | Controles sin igualar número de jugadores | Abierto | `quiebres.segmentos_libres` solo empareja por marcador. |
| B4 | Sesgo de Nickell en agresividad | Abierto, sin efecto | La hipótesis no pasa y no se presenta como causal. |
| B5 | `CLAUDE.md` de `main` desactualizado | Pendiente | Se corrige con la promoción a `main`. |

## 2. Lo que está bien

- **Pruebas**: 126 pasan en 5.5 s con las versiones fijas (Python 3.13, entorno limpio en Linux). Cobertura de `src/ojo` del 84 %. `node --check` pasa en `app.js` y `movimiento.js`.
- **Higiene**: los 7 notebooks están sin salidas; en todo el historial no hay datos, `.env` ni salidas con datos. `09_entrega.py` deja la entrega en `outputs/` (fuera de git) y avisa que lleva posiciones y nombres reales.
- **Torneo reservado bien cuidado**: `INCLUIR_PRUEBA = False` en los notebooks 02–05, el índice se escala con minutos de entrenamiento y las fichas se arman sin el CL26. El notebook 06 informa también lo que no se sostiene.
- **Honestidad**: Método tiene una sección de límites clara, las recomendaciones se presentan como hipótesis y nunca se promete que una decisión "habría cambiado". El notebook 05 reporta que la matriz no se separa de Solari y Ortiz (q = 0.99).
- **Componentes de la página oficial**: balón parado y uso de jugadores ya están, con su prueba y su lectura.

## 3. Hallazgos nuevos

### Alta (cambian lo que se le dice al jurado; casi todo se arregla con texto)

**N1. La recomendación estrella de la matriz confunde un efecto de marcador universal con un rasgo de Jardine.**
"Ganando por 1 se repliega y el partido se empareja; no regalar la iniciativa" (`src/ojo/salidas/decision.py:57`, guion bloques 5 y 6, coach drill 1) tiene tres problemas:
- Que el equipo que gana se repliegue y el rival empuje es un patrón de cualquier liga ("score effects"). La matriz no lo compara contra la liga, y contra Solari y Ortiz no se separa (q = 0.99). Hoy no hay evidencia de que sea propio de Jardine ni de que replegarse *cause* el empate.
- La propia matriz lo contradice: **ganando por 2** el índice baja aún más (46) y el xG neto sigue claramente positivo (+0.88, IC 0.04 a 1.68). "Cuando se repliega, el partido se empareja" no se sostiene ni dentro de la tabla.
- En el caso 1 del CL26 (Querétaro) **no hubo repliegue** (índice 54 frente a 57, menos que el umbral de 5) y aun así el rival generó más. Eso no confirma el mecanismo de la matriz; el guion dice "el empate que advertía la matriz" y el partido terminó 2-1.

Arreglo (texto, 1 h): presentar la fila como "ganando por 1 el balance de ocasiones deja de ser claro (IC cruza 0); en el CL26 se repitió" y la hipótesis como "probar a sostener la iniciativa", sin el "cuando se repliega, se empareja". En el guion, cambiar "el empate que advertía la matriz" por "el partido se emparejó, como marcaba la matriz, aunque esta vez sin repliegue". Si hay tiempo, una frase en Límites sobre los efectos del marcador.

**N2. El principio estrella ("Con uno más, hunde al rival", 17.8 m) es el más expuesto a A4 y a la muestra chica.**
- `altura_sin_balon` es la x media de los jugadores **visibles** (`src/ojo/lentes/forma.py`, OBS1: la toma ve ≈ 27 % de la cancha). Si con Jardine el balón vive más cerca del área rival, la cámara apunta ahí y los defensores visibles "bajan" aunque el bloque real no cambie tanto. 17.8 m de diferencia en la altura de un bloque es mucho para un efecto real.
- Las expulsiones a favor son pocas por grupo (sobre todo con Solari y Ortiz). Con 3–6 partidos el intervalo por bootstrap de percentiles es poco confiable y sale demasiado estrecho.
- En el CL26 queda **sin muestra**, y es el principio de la portada, del caso y del bloque 3 del video.

Arreglo (2–3 h, lo corre chamuel): (a) contar cuántos partidos con expulsión a favor hay en cada grupo y mostrarlo en la tarjeta; (b) revisar a mano esas rojas (B2); (c) repetir el efecto controlando por jugadores visibles del rival en la ventana, o al menos reportar el field tilt en el mismo quiebre como apoyo. Si no da tiempo, en el video decir "el juego se instala cerca del área rival" en lugar de "el rival queda 17.8 m más atrás", y marcar el principio como "muestra chica, sin validar en el CL26".

**N3. El placebo no cubre de dónde salen los principios y, con FDR, el "0 de 280" casi está garantizado.**
- El placebo solo se corre para "quiebres con Jardine" (notebook 02, celda 19). Cuatro de los seis principios salen de **Jardine frente a predecesores**, que no tiene placebo.
- Con efectos nulos, Benjamini-Hochberg casi nunca deja pasar nada, así que "0 de 280 con v2" demuestra poco. Lo informativo es comparar **condiciones 1–3 en el placebo contra condiciones 1–3 en lo real** (la columna `pasa_1a3` ya existe).
- Las notas de la app afirman sin condición que "cada principio pasa los 4 filtros" y que en el placebo "ninguno de los momentos clave inventados los pasa" (`scripts/08_maqueta.py:342-344`), y el glosario dice que si el rango no incluye el 0, "no es casualidad" (`app/maqueta.html:80` y `:291`).

Arreglo: en Método, mostrar "placebo: X de 280 pasan las condiciones 1–3 frente a Y en las pruebas reales" y decir que el placebo se hizo con los quiebres de Jardine. Cambiar "no es casualidad" por "es poco probable que sea casualidad". Si da tiempo (1 h de chamuel), correr el mismo placebo en la comparación con predecesores.

**N4. La validación en el CL26 es más débil de lo que suena "ningún principio se invierte".**
- Cada principio se valida como "Jardine en el CL26 frente a Solari y Ortiz" (notebook 06). La referencia de los predecesores es la misma con la que se eligió el principio: si fue extrema por azar, cualquier dato nuevo de Jardine seguirá "en la misma dirección". Solo se re-muestrea un lado.
- Con 6 principios, 1 sin muestra y 3 "sin certeza", lo validado son dos: la salida corta y la alerta del cambio de sistema (esta con solo 4 partidos).

Arreglo (texto): en Método y en el video, decir exactamente eso: "se sostienen dos; tres mantienen la dirección sin certeza; uno sin muestra". Agregar al notebook 06, si hay tiempo, el efecto de Jardine en el CL26 frente al de Jardine en entrenamiento (¿se repite su propio efecto?), que no depende de los predecesores.

**N5. El titular de la portada contradice las bandas del propio índice.**
"Propone, sale jugando corto…" (`app/maqueta.html:68`), pero el índice de Jardine es 57 y las bandas dicen que de 40 a 60 es "equilibrado" (`params.yaml`, `indice.bandas`). El 57 frente a 53 de los predecesores tampoco pasó por el criterio. Arreglo: "Propone más que sus rivales…" (57 frente a 48 de los rivales es lo que sí se ve) o mover las bandas antes de la entrega, no después.

### Media

**N6. La historia vende el Voronoi como lente central y la evidencia no lo sostiene.** `CLAUDE.md` y la propuesta dicen "con el control del espacio como lente central", pero el control solo pasa tras expulsiones (mecánico) y el principio se apoya en la forma. La app ya lo trata bien ("mapa de control del espacio" como imagen y medición). Conviene que el video y la portada digan "lo vemos con el mapa de control" y no "lo descubrimos con el mapa de control", para que el jurado de metodología no lo note primero.

**N7. Comparaciones con predecesores sin descontar la tendencia de la liga.** Salvo el estilo (notebook 03 descuenta la liga con Team Match Stats), los quiebres comparan Jardine contra Solari y Ortiz sin mirar si toda la liga cambió entre 2021 y 2025. El paso 9 (relevo frente a la liga) no se hizo, pero `propuesta_base.md:63` y `CLAUDE.md` siguen listando el "relevo como experimento natural" como parte de la metodología. Arreglo: quitarlo de lo que se dice que se hizo o pasarlo a "trabajo futuro".

**N8. `ojo.lentes.efectos` no tiene pruebas** (0 % de cobertura) y es la tubería que alimenta la validación del CL26. El notebook 02 usa su propia copia. Hoy parecen idénticos, pero nada lo garantiza. Una prueba de humo con quiebres sintéticos (como `tests/test_quiebres.py`) cuesta poco.

**N9. Textos fijos que no dependen de los números.** La lectura del caso cierra siempre con "Es lo que dice el principio: con uno más, se instala arriba" (`scripts/08_maqueta.py:296`), aunque el índice no subiera, y la constancia se escribe como "de 5" fijo (línea 106). Hacerlos condicionales evita contradicciones si se cambia el partido del caso.

**N10. Pregunta abierta que puede tirar la validación**: ¿los organizadores aceptan datos del AP25 y el CL26? `CLAUDE.md` la sigue listando como abierta. Si la respuesta es no, el plan B cambia entrenamiento y prueba. Conviene preguntarlo hoy o declarar en Método que se usaron y por qué.

### Baja

- **N11.** `contexto/propuesta_base.md:62` cita `ojo.salidas.ficha`, que no existe (es `ojo.salidas.decision`).
- **N12.** La ficha no tiene "quién participa poco", que la definición de "hecho" pide; ya está declarado en Límites. Basta con quitarlo del glosario de `CLAUDE.md` o dejarlo como futuro.
- **N13.** La entrega carga Poppins de Google Fonts (V-M14 pendiente). Si el jurado abre el archivo sin internet, la tipografía cambia. No rompe nada.
- **N14.** El PPDA de la matriz (16.2) y el del notebook 03 (frente a la liga) usan definiciones distintas (eventos propios frente a Team Match Stats). Si ambos aparecen, una nota de una línea evita la pregunta.

## 4. Frente a la rúbrica oficial (4 × 25 %)

| Criterio | Nivel hoy (1–4) | Qué lo sostiene | Qué lo sube antes del 22 |
| --- | --- | --- | --- |
| Innovación | 3.5 | Lectura por momentos clave a dos bandas, índice de iniciativa, Voronoi recortado y en movimiento | N6: presentar el Voronoi como lenguaje visual y medición, no como fuente de hallazgos |
| Comunicación | 3 | Un solo HTML con cuatro vistas, glosario, lenguaje de cancha, guion listo | Grabar el video y hacer la prueba de 90 s; corregir N1, N2 y N5 en el guion |
| Accionabilidad | 3 | Matriz, 17 fichas, casos del CL26 sin prometer resultados | N1: que la recomendación principal no sea un efecto de marcador universal |
| Metodología y visualización | 3 | Criterio v2 con FDR, placebo, torneo reservado, límites escritos | N2, N3 y N4 en texto; el control por jugadores visibles si alcanza |

Un jurado técnico va a buscar justo N1–N4. Ninguno obliga a rehacer el análisis: con texto honesto, el proyecto gana puntos de metodología en lugar de perderlos.

## 5. Lista priorizada antes de entregar

| # | Qué | Quién | Esfuerzo | Por qué |
| --- | --- | --- | --- | --- |
| 1 | Reescribir la recomendación "ganando por 1" (N1) en `decision.py`, guion y coach drill | Tilin o chamuel | 1 h | Es lo primero que lee el cuerpo técnico y hoy no se sostiene |
| 2 | Ajustar el titular (N5), "no es casualidad" y las notas del placebo (N3) | Tilin | 30 min | Texto; evita contradicciones visibles |
| 3 | Contar partidos y revisar a mano las expulsiones del principio estrella (N2 a, b) | chamuel | 1 h | Si la muestra es de 3–4 partidos, cambia cómo se cuenta en el video |
| 4 | Validación con la frase exacta (N4) en Método y video | Tilin | 30 min | Evita sobrevender "ningún principio se invierte" |
| 5 | Grabar el video y prueba de 90 s | chamuel | medio día | Pendiente desde el 18/10 |
| 6 | Preguntar o declarar el uso de AP25–CL26 (N10) | chamuel | 15 min | Si no se acepta, cambia la validación |
| 7 | Placebo en "frente a predecesores" y condiciones 1–3 en Método (N3) | chamuel | 1–2 h | Sube metodología |
| 8 | Control por jugadores visibles en el principio estrella (N2 c) | chamuel | 2–3 h | Solo si 1–6 ya están |
| 9 | Prueba de humo de `efectos.py` (N8), B1 y referencias de docs (N7, N11) | Tilin | 1–2 h | Calidad; no lo ve el jurado |
| 10 | `08_maqueta` → `09_entrega` → promoción a `main` → correo | chamuel | 1 h | Cierre |

Si hay que recortar, lo último que sale es 8 y 9; 1–4 son texto y son lo que más protege la calificación.
