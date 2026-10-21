# Terminología de la página: qué significa cada término y cómo se muestra

> **Aplicada el 18 oct**, por decisión de chamuel ("aplica todas las propuestas").
>
> La lista sale del texto que de verdad aparece en `app/maqueta.html` y en `outputs/app/datos.js`. El jurado no es técnico: cada término debe entenderse sin el glosario o llevar al lado lo que significa.
>
> **Dónde vive cada texto:**
> - `app/maqueta.html` y `app/app.js`: textos fijos de la página.
> - `scripts/08_maqueta.py`: principios, lectura del caso y bloque 6.
> - `ojo.salidas.decision`: matriz y ficha.
> - `ojo.lentes.indice`: nombres de las ocho señales.
> - `ojo.lentes.rivales`: rasgos de la ficha.
> - `notebooks/07_casos_cl26.ipynb`: casos del CL26.
>
> El análisis interno (código, `framework.md`, notebooks) conserva los nombres técnicos; el glosario de Método los pone entre paréntesis.

## 1. Nombres de las vistas

Cada pestaña lleva debajo una descripción corta (en pantallas de 1180 px o más).

| Antes | Ahora | Descripción | Por qué |
| --- | --- | --- | --- |
| Portada | **Resumen** | en 90 segundos | Es la tesis, el índice por torneo y los seis principios: un resumen. |
| Explorar | **El partido** | minuto a minuto | La vista es un partido concreto (su título es "América vs Tigres UANL"). El artículo "el" lo hace específico. |
| Decidir | **Plan de juego** | para el cuerpo técnico | Ver la nota sobre "Lectura". |
| Método | **Método** | cómo lo medimos | Ver la nota sobre "Métricas". |

**¿"Lectura" en lugar de Decidir? No.**

- "Lectura" ya se usa dentro de la página con otro sentido: la lectura del partido, la lectura de cada caso y "Lectura frente a Tigres".
- Esta vista es donde el jurado busca qué hacer: los tres escenarios del coach drill ("vamos 1-0 al 60'", "mañana jugamos contra Pumas"). Un nombre de acción la encuentra más rápido.
- Su contenido es lo que trae un plan de juego: qué conviene por situación, la ficha del rival, el balón parado y los cambios.

**¿"Métricas" en lugar de Método? No.**

- La vista no es una lista de métricas. Su centro es cómo se decidió que algo es un hallazgo (los 4 parámetros y la prueba en falso), la validación en el CL26 y los límites.
- "Método" es la palabra del criterio de la rúbrica ("metodología y visualización"): quien califica ese criterio va directo ahí.

En el teléfono las pestañas van sin descripción; "Plan de juego" ocupa dos líneas.

### "Ficha de 10 segundos" → "Qué dice nuestro motor" (21 oct, chamuel)

La página ya no usa "ficha de 10 segundos". Se adapta según el lugar:

| Dónde | Ahora |
| --- | --- |
| Título del bloque 2 de Plan de juego | **Qué dice nuestro motor** |
| Botones (barra de rivales, bloque 6 de El partido) | **Ver la lectura del motor →** |
| Botón del cierre del Resumen | **Qué dice nuestro motor →** |
| Pilar 3 del Resumen | "qué dice nuestro motor de cada rival" |
| Casos del CL26 (notebook 07) | "Lectura del motor sobre {rival}", "lo que marcaba el motor" |
| Límites (Método §7) | "La lectura del motor describe al rival promedio" |

En el código y en los datos el objeto sigue llamándose `ficha` (`decidir.fichas`, `#ficha`, `ojo.salidas.decision.ficha`). El guion del video y el animatic todavía dicen "una ficha que se lee en diez segundos".

### Glosario de Método (21 oct, chamuel)

El glosario pasa de 15 a 42 términos: además de los que ya tenía, entra cada término "traducido" de esta tabla que aparece en la página (los 4 parámetros, principio, tramos de comparación, cambio neto, variación típica, remuestreo, comprobación de los pesos, propone · equilibrado · espera, ataque elaborado, contragolpe, juego directo y pase largo, presión alta, presión tras perder el balón, altura sin balón, altura de recuperación, espacio en campo rival, forma de pasar, peligro por envío, foto real y estimado, matriz de situaciones, ▲ ● ▼, recomendación, muestra chica, lectura del motor, partido clave, torneos analizados y los veredictos). Cada uno lleva entre paréntesis el nombre técnico.

Los ids internos (`portada`, `explorar`, `decidir`, `metodo`) y las direcciones (`#explorar`…) no cambian.

## 2. Goles esperados y resultados

| Término técnico | En la página | Nota |
| --- | --- | --- |
| xG | "goles esperados (xG)" la primera vez; después, xG | |
| xG neto | **balance de ocasiones** (xG a favor − en contra) | |
| xG por envío | **peligro por envío (xG)**, a favor y en contra | |
| por 90 / por 10 min | **cada 90 min / cada 10 min** | |
| OBV | **valor de cada acción (OBV)** | Solo en el glosario. |
| Monte Carlo explicativo | **¿Qué tan merecido? (simulación con los tiros del partido)** | |
| 4G 2E 1P | **4 ganados, 2 empates, 1 perdido** | Con singular y plural. |

## 3. Presión, posesión y fases

| Término técnico | En la página | Nota |
| --- | --- | --- |
| PPDA | PPDA, explicado una vez por vista: "pases que el rival da antes de que le recuperen el balón; menos = más presión" | |
| Field tilt | **dominio del último tercio** | En el radar, "Último tercio". |
| Juego asentado / Asentado | **ataque elaborado** | En el radar, "Elaborado". |
| Elabora (radar, inverso de juego directo) | **Circula** | Para no repetir "Elaborado". |
| Elabora (ficha) | **Elabora sus ataques** | |
| Juego directo / Pase largo | Igual | |
| Transición | **contragolpe** | "Concede menos contragolpes", "vigilar el contragolpe rival", "Vive del contragolpe". |
| Contrapresión | **presión tras perder el balón** | |
| Altura del bloque / Bloque alto | **altura sin balón**, en metros | En el radar, "Altura". |

## 4. Índice y espacio

| Término técnico | En la página | Nota |
| --- | --- | --- |
| Índice Proactivo–Reactivo | **índice de iniciativa** (0 = espera, 100 = propone) | Las bandas se leen "propone · equilibrado · espera". |
| Voronoi | **mapa de control del espacio** (Voronoi entre paréntesis) | |
| Espacio arriba / Espacio en campo rival | **espacio en campo rival** | En el radar, "Campo rival". |
| Foto 360 | **foto de posiciones (360)** | |
| Foto real / estimado | Igual | |
| Huella de pases y redes | **forma de pasar** | |
| Lentes propias | **Nuestras mediciones** | |

## 5. Cómo se lee el partido

| Término técnico | En la página |
| --- | --- |
| Dos bandas | **frente a frente** |
| Punto de quiebre | **momento clave** |
| Ventanas de control | **tramos de comparación** |
| Diferencia en diferencias | **cambio neto** (el término técnico, entre comillas en Método) |
| Predecesores | **"Solari y Ortiz"** o "antes de Jardine (Solari y Ortiz)" |

## 6. Estadística

| Término técnico | En la página | Nota |
| --- | --- | --- |
| IC 95 % | **rango probable** | |
| Bootstrap | **remuestreo de partidos** | Solo en Método. |
| q / FDR / Benjamini-Hochberg | **riesgo de falso hallazgo**, en % | Por ejemplo, "menos de 1 %" o "6 %". |
| Criterio v2 | **los 4 parámetros** (antes "4 filtros"; cambio de chamuel del 21 oct, también en el video), con nombre: **Claro** (rango probable sin cero) · **Grande** (al menos media variación típica) · **Constante** (4 de 5 torneos) · **A prueba de suerte** (riesgo de falso hallazgo ≤ 10 %) | Nombres del 19 oct, en el Resumen y en Método |
| Placebo | **prueba en falso (placebo)** | |
| DE / desviación estándar | **variación típica** | |
| PCA / cargas / varianza | **comprobación de los pesos** | El término técnico va entre paréntesis en Método. |
| Entrenamiento / torneo de prueba | **torneos analizados / torneo reservado** | |
| Veredictos | ✓ Se sostiene · ≈ Misma dirección, sin certeza · — Sin muestra suficiente | |
| Recomendación (hipótesis) | Igual | |

Con esto también se quitó la coma decimal de "q = 0,06": toda la página usa punto decimal.

## 7. Unidades y abreviaturas

| Término técnico | En la página | Nota |
| --- | --- | --- |
| yd | **metros** (`campo.yarda_m` en `params.yaml`) | −1.5 yd → −1.4 m; −19.5 yd → −17.8 m. |
| AP / CL | Igual | Con "AP = Apertura, CL = Clausura" al pie de la gráfica por torneo. |
| 1T, 2T, PR1, PR2 | Igual | Con "PR: prórroga" en la línea del índice. |
| ▲ ● ▼ | Igual | |
| Filtros · 2 | Igual | |

Los números no cambian, solo su unidad o su nombre.
