# Terminología de la página: qué significa cada término y cómo traducirlo

> Lista del 18 oct, sacada del texto que de verdad aparece en `app/maqueta.html` y en `outputs/app/datos.js`. El jurado no es técnico: cada término debe entenderse sin el glosario, o llevar al lado lo que significa.
>
> Columna **Decisión**: la llena chamuel. Lo que se decida se aplica en `app/maqueta.html`, `app/app.js`, `scripts/08_maqueta.py` (textos de los datos) y `ojo.salidas.decision` (la matriz), y el guion del video se ajusta igual.

## 1. Nombres de las vistas

| Hoy | Qué es | Propuesta | Decisión |
| --- | --- | --- | --- |
| Portada | El resumen: tesis, índice por torneo y los seis principios | **Resumen** (o "Jardine en 90 s") | |
| Explorar | Un principio visto en un partido real: el caso, el reproductor con Voronoi y la simulación | **El partido** (o "Un partido a fondo") | |
| Decidir | Herramientas para el cuerpo técnico: matriz de situaciones, ficha por rival, balón parado, cambios y los casos del CL26 | **Para decidir** | |
| Método | El reporte: datos, criterio, evidencia, validación, límites y glosario | **Cómo lo medimos** | |

En el teléfono la barra de vistas mide 375 px: los nombres largos se recortan a una palabra ("Resumen · Partido · Decidir · Método").

## 2. Goles esperados y resultados

| Término | Dónde | Qué significa | Propuesta | Decisión |
| --- | --- | --- | --- | --- |
| xG | Principios, matriz, balón parado, ficha | Goles esperados: la probabilidad de que un tiro sea gol por dónde y cómo se tiró. Sumado, cuántos goles "merecía" un equipo | "goles esperados (xG)" la primera vez en cada vista; después, xG | |
| xG neto | Matriz, ficha | xG a favor menos xG en contra. "+0.66 por 90" = en un partido completo genera 0.66 goles esperados más de los que concede | **Balance de ocasiones** (xG a favor − en contra) | |
| xG por envío | Balón parado | Peligro medio de cada balón parado | **Peligro por envío** | |
| por 90 / por 10 min | Matriz, principios, validación | La cifra llevada a un partido completo o a cada 10 minutos, para comparar tramos de distinto largo | "por partido (90 min)" / "cada 10 minutos" | |
| OBV | Glosario | On-Ball Value de StatsBomb: cuánto sube o baja la probabilidad de gol con cada acción con balón | **Valor de cada acción (OBV)** | |
| ¿Qué tan merecido? (Monte Carlo explicativo) | Explorar, sección 4 | Se juega el partido 10 000 veces con los tiros que hubo y se cuenta quién gana | "¿Qué tan merecido? (simulación con los tiros del partido)"; quitar "Monte Carlo" del título | |
| 4G 2E 1P · puntos por partido | Ficha | Ganados, empatados y perdidos | "4 ganados, 2 empates, 1 perdido" | |

## 3. Presión, posesión y fases

| Término | Dónde | Qué significa | Propuesta | Decisión |
| --- | --- | --- | --- | --- |
| PPDA | Matriz, ficha, Método | Pases que el rival da en su salida por cada acción defensiva propia (entrada, intercepción, falta) en esa zona. **Menos = presiona más** | **Presión (PPDA; menos = más intensa)** | |
| Field tilt | Línea del índice | De los pases completos en el último tercio, qué parte es del equipo | **Dominio del último tercio** | |
| Posesión | Línea del índice | Tiempo con el balón entre el de ambos | Igual | |
| Asentado / Juego asentado / Elabora | Línea del índice, ficha | Posesión en control, fuera de transición (Phases of Play de StatsBomb) | **Ataque elaborado** | |
| Juego directo / Pase largo | Línea del índice, ficha | Qué tan rápido va hacia la portería rival / largo medio del pase | "Va directo" / "pase largo" (igual) | |
| Transición | Método, datos | Los segundos después de recuperar o perder el balón | **Contragolpe / repliegue** según el lado | |
| Presión alta | Línea del índice | Presiones en campo rival por minuto | Igual | |
| Contrapresión ("el rival no lo aprieta") | Principio | Presionar en los segundos siguientes a perder el balón | **Presión tras pérdida** | |
| Bloque alto / Altura del bloque | Línea del índice, principio | Qué tan adelante están, en promedio, los jugadores de campo sin balón | **Altura del equipo sin balón** (en metros) | |

## 4. Índice y espacio

| Término | Dónde | Qué significa | Propuesta | Decisión |
| --- | --- | --- | --- | --- |
| Índice Proactivo–Reactivo | Portada, Explorar, matriz | 0 a 100 por minuto, de 8 señales con el mismo peso: posesión, ataque elaborado, dominio del último tercio, espacio en campo rival, altura, presión alta (suman) y juego directo y pase largo (restan). 50 = neutro | **Índice de iniciativa** (0 = espera, 100 = propone) | |
| Voronoi | Explorar, Método | Divide la cancha: cada punto es del jugador que llega primero (el más cercano). Así se mide quién controla cada metro | **Mapa de control del espacio** (Voronoi entre paréntesis) | |
| Espacio arriba / Espacio en campo rival | Línea del índice | Parte del campo rival que controla el equipo según el Voronoi | **Espacio en campo rival** (uno solo de los dos nombres) | |
| Foto 360 / "Sin foto 360 en este minuto" | Reproductor | StatsBomb 360: dónde estaban los jugadores visibles en cada evento | **Foto de posiciones (360)** | |
| Foto real / estimado | Reproductor | Entre dos fotos, el movimiento se estima; la página marca cuál es cuál | Igual, con la leyenda al lado | |
| Huella de pases y redes | Método | Qué tipos de pase usa (60 grupos de StatsBomb) y quién se pasa con quién, por posición | **Forma de pasar** | |

## 5. Cómo se lee el partido

| Término | Dónde | Qué significa | Propuesta | Decisión |
| --- | --- | --- | --- | --- |
| Dos bandas | Método | El América y el rival en el mismo minuto, uno frente al otro | **Frente a frente** (América vs rival, minuto a minuto) | |
| Punto de quiebre / quiebre | Explorar, principios, Método | Momento que cambia el partido: gol, expulsión, cambio de sistema, sustitución | **Momento clave** | |
| Ventanas de control | Método | Tramos parecidos sin quiebre, para saber cuánto cambia el partido "solo" | **Tramos de comparación** | |
| Diferencia en diferencias | Método | Lo que cambió tras el quiebre menos lo que cambia en los tramos de comparación | **Cambio neto** | |
| Tramo | Método | Ventana de 15 minutos | Igual | |
| Predecesores / "Solari y Ortiz" / "Antes" | Portada, principios | Los dos entrenadores anteriores del América (AP21–CL23) | **"Antes de Jardine (Solari y Ortiz)"** siempre igual | |

## 6. Estadística

| Término | Dónde | Qué significa | Propuesta | Decisión |
| --- | --- | --- | --- | --- |
| IC 95 % | Principios, matriz, validación | Intervalo de confianza: el rango donde está el valor real con 95 % de confianza. Si no cruza el 0, la diferencia no es ruido | **Rango probable** ("entre −2.0 y −1.0 m") | |
| Bootstrap | Método | Se re-muestrean partidos miles de veces para sacar ese rango | **Remuestreo de partidos** | |
| q / FDR / Benjamini-Hochberg | Principios, Método | Con 636 pruebas, unas salen por suerte; q es el riesgo de que el hallazgo sea falso, ya corregido. Se acepta q ≤ 0.10 | **Riesgo de falso hallazgo** ("menos de 1 %" en lugar de "q < 0,01") | |
| Criterio v2 | Portada, Método, balón parado | Las 4 condiciones para llamar hallazgo a algo (rango sin 0, tamaño mínimo, 4 de 5 torneos, riesgo de falso hallazgo) | **Los 4 filtros** (quitar "v2": al jurado no le dice nada) | |
| Placebo | Método | Se corre el método donde no pasó nada; si encuentra algo, el método está mal. Encontró 0 de 280 | **Prueba en falso** (placebo) | |
| DE / media desviación estándar | Ficha, Método | Variación típica entre partidos; 0.5 DE = diferencia de tamaño medio | **Variación típica** | |
| PCA / cargas / varianza / r | Método | Comprobación de que dar el mismo peso a las 8 señales del índice coincide con lo que dicen los datos (r = 0.94) | **Comprobación de los pesos** | |
| Torneos en la misma dirección | Principios | En cuántos de los 5 torneos de Jardine la diferencia tuvo el mismo signo | Igual | |
| Entrenamiento / torneo de prueba | Validación | AP23–AP25 se analizó; el CL26 se guardó sin ver para comprobar al final | **Torneos analizados / torneo reservado** ("entrenamiento" es jerga de modelos) | |
| Veredicto: se sostiene / misma dirección, sin certeza / sin muestra | Validación | Qué pasó con cada principio en el CL26 | Igual, con ✓ / ≈ / — | |
| Recomendación (hipótesis) | Matriz | Sugerencia que sale de los datos, no algo probado | Igual | |

## 7. Unidades y abreviaturas

| Término | Dónde | Qué significa | Propuesta | Decisión |
| --- | --- | --- | --- | --- |
| yd | Principios, validación | Yardas: StatsBomb mide la cancha en yardas (120 × 80). 1 yd = 0.91 m | **Metros**: −1.5 yd ≈ −1.4 m; −19.5 yd ≈ −17.8 m | |
| AP23, CL26… | Gráfica por torneo, barra | Apertura 2023, Clausura 2026 | Igual, con la leyenda "AP = Apertura, CL = Clausura" una vez | |
| 1T, 2T, PR1, PR2 | Línea del reproductor | Primer y segundo tiempo; prórroga 1 y 2 (la final AP23 se fue a tiempo extra) | Igual, con "PR = prórroga" en la leyenda | |
| ▲ Le funciona · ● Parejo · ▼ Sufre | Matriz | Si en esa situación genera más, lo mismo o menos de lo que concede | Igual | |
| Filtros · 2 | Barra oculta | Cuántos filtros están activos | Igual | |

## Lo que recomiendo cambiar primero

Si no da tiempo para todo, estos cinco son los que más confunden a alguien que no es analista:

1. Los nombres de las vistas.
2. **yd → metros**.
3. **"xG neto" → "balance de ocasiones"**.
4. **"IC 95 %" → "rango probable"**.
5. **"criterio v2" → "los 4 filtros"**.

Las siglas de StatsBomb (xG, PPDA, OBV, 360) se quedan, pero siempre con su traducción al lado.
