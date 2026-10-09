# Ojo de Águila — Propuesta base

Versión del 5 de octubre de 2026, actualizada el 7 de octubre (ventana AP23–CL26, predicción, decisión) · Samuel de María Cabrera Flores. El documento editable vive en Claude Docs; este archivo es una copia para Claude Code.

## Resumen

Ojo de Águila es un motor analítico reutilizable que convierte los eventos y datos 360 de StatsBomb en una narrativa táctica trazable. Su primer caso es el América de André Jardine (Apertura 2023 – Clausura 2026), leído siempre frente a lo que hace el rival en el mismo partido. Entregamos un reporte HTML, un video de 5 minutos y una ficha de 10 segundos para el cuerpo técnico.

**En una línea:** Ojo de Águila usa datos 360, grafos y Voronoi para explicar los principios de Jardine y cómo los ajusta frente a cada rival.

**Lema:** “Ojo de Águila: la intuición del entrenador, convertida en evidencia.”

## El reto

El Hackathon ISAC 2026 con el Club América pide explicar, con eventos StatsBomb 360, cómo juega un entrenador a lo largo de varios partidos. El registro cierra el 12 de octubre de 2026 y la entrega es el 22 de octubre de 2026. La convocatoria habla de 8 torneos de Liga MX (Apertura 2021 – Clausura 2025); la API entrega de 2021/22 a 2026/27, y usamos Apertura 2021 – Clausura 2026 para cubrir completa la etapa de Jardine.

**Pregunta central:** ¿cuáles son los principios que definen al equipo en fase ofensiva y defensiva, cómo se manifiestan a lo largo del tiempo y cómo ajusta el entrenador su comportamiento según el contexto (rival, marcador, localía o momento del juego)?

**Principio rector:** alguien que no vio los partidos debe entender cómo juega el equipo y cuáles son las ideas del entrenador ([convocatoria](https://www.isac-app.com/competition-details/hackathon-club-america.html)).

## Objetivo

**Objetivo general.** Construir Ojo de Águila, un motor analítico reutilizable sobre las APIs de StatsBomb, y usarlo para contar la historia de André Jardine en el América (Apertura 2023 – Clausura 2026): sus principios de juego, con el control del espacio como lente central; qué tan estables fueron; cómo interactúan con lo que hace el rival en cada partido y cómo los ajustó según marcador, localía, rival y momento. Mediremos qué cambió con su llegada frente a Solari y Ortiz, usando el relevo como experimento natural, y validaremos en un torneo que el modelo no vio (Clausura 2026) que esos principios anticipan su comportamiento y sus resultados, de forma que un cuerpo técnico lo entienda sin ver un solo video y lo use para tomar decisiones.

**Objetivos específicos**

1. **Principios:** identificar 4 a 6 principios ofensivos y defensivos, cada uno como hipótesis comprobable.
2. **Estabilidad:** medir qué tan constantes son a lo largo de los 6 torneos de Jardine.
3. **Interacción con el rival:** leer en paralelo a ambos equipos en cada partido, tramo a tramo: quién domina, cuándo cambia y cómo responde cada uno.
4. **Contexto:** cuantificar los ajustes por marcador, localía, fuerza del rival y momento del partido.
5. **Efecto del relevo:** comparar el cambio Ortiz → Jardine con el cambio promedio de la liga en el mismo periodo, con el relevo Solari → Ortiz como placebo y, si alcanza el tiempo, con todos los relevos de entrenador de la Liga MX en la ventana.
6. **Predicción del comportamiento:** con lo aprendido en AP23–AP25, anticipar en el Clausura 2026 el PPDA, el field tilt, el control territorial y la altura de recuperación del América por partido y por tramo según el contexto, y medir con R² si supera a la línea base.
7. **Predicción de resultados:** con información previa a cada partido, simular 10,000 veces los partidos del Clausura 2026 (Monte Carlo) y evaluar las probabilidades de ganar, empatar o perder con log-loss y calibración frente a la línea base.
8. **Decisión:** mostrar con casos concretos del Clausura 2026 qué recomendaba la herramienta antes del partido o en el descanso frente a lo que decidió el cuerpo técnico.
9. **Herramienta:** dejar el motor listo para cualquier equipo y generar la ficha de 10 segundos.

## Eje central: tres pilares

| Pilar | Qué es | Criterio |
| --- | --- | --- |
| **1. Espacio** | Control territorial con Voronoi sobre el 360, de ambos equipos y en los momentos clave; siempre recortado a `visible_area` y leído como "control en la zona visible al momento de cada acción". Es la imagen central del reporte y del video, y también se predice (objetivo 6). Regla de corte el 14 de octubre | Interpretabilidad y predictiva |
| **2. Validación fuera de muestra** | (a) Comportamiento: PPDA, field tilt, control territorial y altura de recuperación, con R² contra la línea base. (b) Resultados: Monte Carlo antes del partido, con log-loss y calibración | Predictiva |
| **3. Del dato a la decisión** | Casos de decisión del Clausura 2026 y ficha de 10 segundos por rival, hechos solo con datos previos | Valor operativo |

La parte causal es el diseño de comparación del objetivo 5. El Monte Carlo después del partido ("qué tan merecido fue el resultado") queda como componente opcional e interpretativo, separado del predictivo.

**Cómo cubre el alcance que pide la convocatoria**

| Alcance (convocatoria) | Objetivos | Cómo lo medimos | Salida |
| --- | --- | --- | --- |
| Patrones recurrentes | 1, 2 | Métricas estables entre partidos: perfil, huella de pases, redes, control territorial | Los 4–6 principios |
| Tendencias del entrenador | 5 | Comparación con predecesores y liga; cambio de entrenador como experimento natural | Mapa de estilos y “huella Jardine” |
| Ajustes según contexto | 3, 4 | Lectura a dos bandas, comparaciones dentro del partido, cambios tácticos de ambos equipos | Tabla “si el rival hace X, Jardine hace Y” |
| Diferencias entre partidos o momentos | 2, 3 | Partidos atípicos, tramos de 15 minutos, evolución por torneo, resultado merecido (Monte Carlo posterior) | Línea de tiempo con partidos anómalos explicados |

**Cómo cubre la tabla de evaluación** (supuesto: aplica a este reto, hasta que los organizadores lo confirmen)

| Criterio | Peso | Objetivos | Cómo lo demostramos |
| --- | --- | --- | --- |
| Predictiva | 30 % | 6, 7 | Entrenamiento AP23–AP25 y prueba en el Clausura 2026, sin tocarlo antes. Comportamiento: R² frente al promedio de la liga en la misma situación y frente al América de Ortiz. Resultados: log-loss y calibración sobre todos los partidos de la Liga MX del Clausura 2026 (unos 150) y aparte el subconjunto del América, frente a las frecuencias históricas y al xG reciente de cada equipo |
| Causal | 25 % | 5, 4 | Relevo Ortiz → Jardine frente al cambio de la liga, placebo Solari → Ortiz y, si alcanza, todos los relevos de la liga; comparaciones dentro del mismo partido y emparejadas por minuto y marcador. Lo que sea correlación se etiqueta como tal |
| Interpretabilidad | 25 % | 1, 3 | Capa "Decide en 90 segundos", Voronoi como imagen de cancha y lenguaje de cancha |
| Valor operativo | 20 % | 8, 9 | Casos de decisión del Clausura 2026 y ficha de 10 segundos por rival |

**Plan B de fechas:** si los organizadores no permiten datos posteriores al Clausura 2025, se entrena con AP23–AP24 y se prueba con el Clausura 2025.

## Del dato a la decisión

La tabla de evaluación pide que la herramienta cambie una decisión real del entrenador. Con datos históricos no podemos demostrarlo en vivo, así que nos acercamos lo más posible de forma retrospectiva y sin trampa, sobre el Clausura 2026:

1. **Decisiones observables.** Del Clausura 2026 tomamos las decisiones que deja ver el dato: sustituciones tácticas (no por lesión), cambios de formación, su minuto y el marcador en que ocurrieron.
2. **Qué decía la herramienta antes.** Para cada caso armamos la ficha y la matriz de situaciones solo con partidos anteriores a ese día (sin información del propio partido).
3. **Comparación.** Mostramos si la herramienta coincidía con la decisión o recomendaba algo distinto o antes, junto con lo que pasó después en el partido (xG, OBV y control territorial por tramo).
4. **Resultado.** Una lista corta de casos del tipo "la ficha marcaba X; Jardine hizo Y en el minuto Z; después pasó W", y cuántas veces coincidieron herramienta y entrenador.

No afirmamos que la recomendación habría cambiado el resultado: lo que pasó después de una decisión es correlación, y así se presenta.

## Propuesta de valor

Ojo de Águila se distingue porque es un motor y no un análisis de una sola vez: cada hallazgo se traza a una definición y el mismo código analiza cualquier equipo.

- **Todas las APIs, un solo framework:** eventos, 360, alineaciones y estadísticas de equipo y jugador alimentan definiciones únicas y trazables.
- **Lectura a dos bandas:** cada métrica del América se lee junto a la del rival en el mismo tramo del partido, no de forma aislada.
- **Lentes propias:** control territorial con Voronoi, redes de pases por posición y huella de pases.
- **Comparación como prueba:** el mismo motor corre sobre los predecesores de Jardine y sobre la liga, así que la reutilización queda demostrada y no solo prometida.
- **Del dato a la decisión:** cada principio cierra con una recomendación, y la ficha de 10 segundos la lleva a la banca.

## Enfoque en tres capas

El motor es lo reutilizable, el caso Jardine es lo que evalúa el jurado y la visión queda marcada como futuro.

1. **Motor reutilizable (cualquier equipo o entrenador):** APIs StatsBomb (eventos y 360, alineaciones, stats por equipo) → Framework (definiciones únicas, `params.yaml`, todo trazable) → Lentes (Voronoi y grafos, huella de pases, dos bandas y contexto) → Salidas (reporte HTML, video de 5 min, ficha de 10 s).
2. **Caso evaluado: el América de Jardine**, frente al rival en cada partido, sus predecesores y la Liga MX; 4 a 6 principios, cada uno con evidencia y una decisión.
3. **Visión a futuro:** ficha en medio tiempo y en vivo con datos propios.

El mismo motor se apunta a otro equipo o entrenador cambiando un parámetro; la visión no se presenta como algo ya construido.

## Lectura a dos bandas: el América frente al rival

Cada partido se analiza como un duelo: lo que hace el América se lee junto a lo que hace el rival en el mismo tramo. Así separamos el estilo propio de Jardine de su respuesta a cada oponente.

| Qué medimos | Cómo | Pregunta que responde |
| --- | --- | --- |
| Flujo del partido | xG, OBV y field tilt de ambos equipos por tramos de 5 a 15 minutos | ¿Quién dominó cada fase y cuándo cambió? |
| Control territorial | Voronoi de ambos equipos en los mismos momentos clave | ¿Qué zonas controla cada uno y cuáles cede? |
| Acción y reacción | Presión del rival por tramo frente a la salida del América, y al revés | ¿Cómo responde Jardine cuando el rival presiona alto o se repliega? |
| Ajustes cruzados | Cambios de formación y sustituciones de ambos equipos, con su minuto | ¿Quién movió primero y qué cambió después? |
| Efecto América | Métricas del rival contra el América frente a su promedio del torneo | ¿Cómo cambian los rivales su plan al enfrentar a Jardine? |
| Fortaleza contra debilidad | Por dónde progresa el América frente a dónde concede ese rival | ¿Ataca Jardine las zonas débiles de cada rival? |

Todo se expresa como diferencial (América menos rival) por tramo, con las mismas definiciones del framework. El efecto América usa las estadísticas por partido de toda la liga, que ya trae la API.

## Comparaciones

Comparar en cuatro niveles aísla la huella de Jardine y prueba que el motor es reutilizable.

| Nivel | Contra qué | Qué aísla | Datos |
| --- | --- | --- | --- |
| 1. Dentro del partido | El rival en el mismo tramo | Estilo propio frente a respuesta al rival | Eventos y 360 de ambos equipos |
| 2. Mismo club | Sus predecesores en la ventana de datos | La huella del entrenador con el mismo club | Eventos y 360 de unos 160 partidos del América |
| 3. Liga MX | Todos los equipos de cada torneo | Dónde se ubica el estilo de Jardine | Estadísticas por equipo |
| 4. Experimento natural | El cambio de entrenador entre CL23 y AP23, frente al cambio promedio de la liga; placebo Solari → Ortiz y, si alcanza, todos los relevos de la Liga MX en la ventana | El efecto del cambio de entrenador | Estadísticas por equipo y partido; entrenadores de todos los equipos en Matches (ya en caché) |

Los predecesores en la ventana son Solari y Ortiz, confirmados en Matches; de Solari solo hay datos desde el Apertura 2021 (falta su Clausura 2021). Los fichajes del verano 2023 confunden el nivel 4, y lo declaramos como límite. El placebo Solari → Ortiz es débil: de Solari hay solo 27 partidos y su salida fue a mitad del Clausura 2022, no entre torneos.

## Datos y framework

Usamos las 10 APIs de StatsBomb y adoptamos sus definiciones donde existen; lo propio se documenta y todos los umbrales viven en un solo archivo. Detalle en `contexto/framework.md` y `contexto/api/`.

## Entregables

| Entregable | Contenido | Fecha |
| --- | --- | --- |
| Reporte HTML (Quarto) | Metodología, framework, los 4–6 principios, lectura a dos bandas, comparaciones y fichas | 22 oct 2026 |
| Video de máximo 5 minutos | La historia de Jardine en sus principios y una demostración de la ficha de unos 15 segundos | 22 oct 2026 |
| Ficha de 10 segundos | Una tarjeta por rival: cómo progresa, dónde concede, quién participa poco, su balón parado vulnerable y cómo respondió Jardine ante rivales parecidos | Dentro del reporte |
| Presentación final (solo finalistas) | Máximo 10 diapositivas, con la hoja de ruta como cierre | 11 nov 2026 |

La ficha responde al criterio de evaluación en que el jurado resuelve 3 escenarios de decisión en menos de 90 segundos.

## Capa de decisión: "Decide en 90 segundos"

El criterio de interpretabilidad menciona "coach drills": el jurado, actuando como cuerpo técnico, resuelve 3 escenarios de decisión en menos de 90 segundos (~30 s cada uno) usando nuestro material. Supuesto (por confirmar con los organizadores): el jurado define los escenarios sin datos y los resuelve consultando nuestro reporte HTML. No conocemos los escenarios, así que el reporte debe responder cualquier situación típica.

**Lector objetivo:** sabe de fútbol, no vio los partidos y no sabe de ciencia de datos. La capa principal usa lenguaje de cancha ("espacio que controla cada equipo", "qué tan probable era ganar"); el método va en una capa técnica aparte.

**Contenido, al inicio del reporte HTML:**

1. **Matriz de situaciones.** Filas = situaciones de decisión: rival presiona alto, rival en bloque bajo, vamos ganando después del 70', vamos perdiendo, empate en el segundo tiempo, balón parado a favor, balón parado en contra, transición en contra, rival con ventaja numérica o expulsión. Columnas, una línea cada una: qué hace Jardine y con qué frecuencia · qué le funciona (xG/OBV) · recomendación · enlace a la evidencia.
2. **Tres escenarios resueltos** como ejemplo: pregunta, respuesta en una frase, el dato que la sostiene y su gráfica.
3. **Fichas de 10 segundos por rival**, para escenarios que nombren a un equipo concreto.

**Reglas de diseño:**
- Cada respuesta se encuentra en 2 clics o desplazamientos como máximo y se lee en 30 segundos.
- Cada celda de la matriz enlaza a la sección de evidencia del principio correspondiente.
- Nada de jerga técnica en esta capa; los términos del framework se explican en lenguaje de cancha.

**Ensayo:** antes de entregar, 2 o 3 personas que sepan de fútbol y no hayan trabajado en el proyecto resuelven 3 escenarios con cronómetro. Si tardan más de 90 s en total, se simplifica. El tiempo medido puede reportarse en el HTML como evidencia de interpretabilidad (solo si se hizo de verdad).

**Dónde va cada pieza:**

| Pieza | Reporte HTML | Video (≤ 5 min) | Presentación (≤ 10 diapositivas, solo finalistas) |
| --- | --- | --- | --- |
| Decide en 90 segundos | Al inicio del reporte | Demostración en vivo resolviendo un escenario con el HTML (~60 s) | 1 diapositiva |
| Los 4–6 principios de Jardine | Completos, con evidencia | Núcleo de la historia | 1 diapositiva por principio clave |
| Lectura a dos bandas y comparaciones | Completas | Un partido como ejemplo | 1 diapositiva |
| Metodología y framework | Completos, capa técnica | 20–30 s | 1 diapositiva |
| Simulación Monte Carlo | Sección propia | 10–15 s o nada | Opcional |
| Hoja de ruta (tiempo real) | Breve, como visión | Cierre de 15 s | Diapositiva final |

La simulación Monte Carlo es el componente opcional de la convocatoria y no forma parte de los coach drills. Tiene dos usos, y no se mezclan: (a) **antes del partido**, con el xG esperado estimado solo con información previa, da las probabilidades de ganar, empatar o perder del Clausura 2026 y cuenta para la parte predictiva (objetivo 7); (b) **después del partido**, con el xG de los tiros del propio partido, mide qué tan merecido fue el resultado; es interpretación, no predicción, y va como componente opcional.

## Alcance y hoja de ruta

Durante el hackathon todo se hace con datos históricos; el tiempo real queda como hoja de ruta y se presenta como visión.

- **Dentro del alcance:** análisis de unos 160 partidos del América y de la liga, lectura a dos bandas y ficha de 10 segundos. El modo repetición entra solo si el 17 de octubre lo principal está terminado.
- **Fuera, por ahora:** datos en vivo (StatsBomb recolecta después del partido y no tenemos un feed en vivo), video y tracking (no se entregan, y extraer posiciones de la transmisión es un proyecto de meses) y cualquier uso fuera de la competencia (la licencia de estos datos no lo permite).

Hoja de ruta: **Fase 1 · Hackathon** (oct 2026, datos históricos: reporte, video y ficha; modo repetición opcional) → condición: datos en vivo con licencia → **Fase 2 · Medio tiempo** (futuro: ficha al descanso, qué cambió el rival) → condición: tracking o video → **Fase 3 · En vivo** (futuro: alertas durante el juego, movimientos sin balón, visión por computadora).

## Calendario y riesgos

La entrega es el 22 de octubre, y el 14 de octubre decidimos si Voronoi se queda como lente central o pasa a ser de apoyo.

| Bloque | Fechas |
| --- | --- |
| Ingesta y prueba de API | 5–6 oct |
| Framework y línea base | 7–9 oct |
| Grafos, Voronoi, huella | 10–14 oct |
| Cierre de registro | 12 oct |
| Corte de Voronoi | 14 oct |
| Contexto y comparaciones | 15–17 oct |
| Principios y reporte | 18–20 oct |
| Video final | 21–22 oct |
| **Entrega** | **22 oct** |

| Riesgo | Mitigación |
| --- | --- |
| Phases of Play vacío en partidos históricos | Definición propia de transición en `params.yaml` (plan B). Descartado: el inspector (9 oct) lo encontró en el 82–88 % del juego abierto en todos los torneos AP21–CL26 |
| Los organizadores no permiten datos posteriores al Clausura 2025 | Plan B: entrenamiento AP23–AP24 y prueba en el Clausura 2025 |
| Pocos partidos del América para evaluar resultados | El Monte Carlo se evalúa sobre toda la liga en el torneo de prueba; el América se reporta aparte |
| Fuga de información en la predicción | Todo lo que alimenta una predicción del Clausura 2026 (incluida la fuerza del rival) se calcula solo con partidos anteriores |
| Cobertura 360 incompleta | Métricas 360 solo con frames válidos; se reporta la cobertura |
| Narrativa obvia para un jurado que conoce al equipo | Lectura a dos bandas y comparación contra la liga |
| Falta de tiempo | Regla de corte del 14 de octubre; el modo repetición solo si sobra tiempo |
| Fuga de datos o credenciales | Repositorio privado; `data/` y `.env` fuera de git |
| Tabla de evaluación ambigua | Correo a los organizadores y un diseño que cubre ambas lecturas |

## Decisiones abiertas y siguientes pasos

- [ ] Registrar al equipo (antes del 12 de octubre)
- [ ] Enviar el correo a los organizadores (8 oct): tabla de evaluación (incluida la nota de que no se necesita programación avanzada), datos de 2025/26, cómo evalúan "cambia una decisión real", elección del entrenador, límites de la API y reporte interactivo
- [x] Crear el repositorio privado y la carpeta local (`PROYECTOS\C_AMERICA`, bajo OneDrive con la sincronización inactiva)
- [x] Correr la prueba de humo de la API (7 oct)
- [ ] Diseñar el logo en Claude Design
- [x] Definir la estructura del repositorio en GitHub

**Preguntas sin resolver**

- ¿La tabla de evaluación publicada aplica a este reto?
- ¿La elección de Jardine es libre?
- ~~¿Phases of Play viene poblado en los partidos de 2023 a 2025?~~ Sí: 82–88 % del juego abierto en todos los torneos (inspector, 9 oct).
- ¿El modo repetición entra en la entrega o queda como visión?
- ¿Aceptan datos del Apertura 2025 y el Clausura 2026? La API los entrega; el rango AP21–CL25 de la convocatoria parece heredado de ediciones anteriores. Se usan, con el plan B listo.
- ¿Cómo evalúan que "la herramienta cambia una decisión real del entrenador"?
- ¿Qué implica para la rúbrica la nota de que no se necesita programación avanzada?
