# Ojo de Águila — Propuesta base

Versión del 5 de octubre de 2026 · Samuel de María Cabrera Flores. El documento editable vive en Claude Docs; este archivo es una copia para Claude Code.

## Resumen

Ojo de Águila es un motor analítico reutilizable que convierte los eventos y datos 360 de StatsBomb en una narrativa táctica trazable. Su primer caso es el América de André Jardine (Apertura 2023 – Clausura 2025), leído siempre frente a lo que hace el rival en el mismo partido. Entregamos un reporte HTML, un video de 5 minutos y una ficha de 10 segundos para el cuerpo técnico.

**En una línea:** Ojo de Águila usa datos 360, grafos y Voronoi para explicar los principios de Jardine y cómo los ajusta frente a cada rival.

**Lema:** “Ojo de Águila: la intuición del entrenador, convertida en evidencia.”

## El reto

El Hackathon ISAC 2026 con el Club América pide explicar, con eventos StatsBomb 360, cómo juega un entrenador a lo largo de varios partidos. El registro cierra el 12 de octubre de 2026 y la entrega es el 22 de octubre de 2026. Los datos cubren 8 temporadas de Liga MX (Apertura 2021 – Clausura 2025) por API.

**Pregunta central:** ¿cuáles son los principios que definen al equipo en fase ofensiva y defensiva, cómo se manifiestan a lo largo del tiempo y cómo ajusta el entrenador su comportamiento según el contexto (rival, marcador, localía o momento del juego)?

**Principio rector:** alguien que no vio los partidos debe entender cómo juega el equipo y cuáles son las ideas del entrenador ([convocatoria](https://www.isac-app.com/competition-details/hackathon-club-america.html)).

## Objetivo

**Objetivo general.** Construir Ojo de Águila, un motor analítico reutilizable sobre las APIs de StatsBomb, y usarlo para explicar cuáles son los principios de juego del América de André Jardine, qué tan estables son, cómo interactúan con lo que hace el rival a lo largo del mismo partido, cómo los ajusta según marcador, localía, rival y momento, y en qué se distinguen de sus predecesores y del resto de la Liga MX, de forma que un cuerpo técnico lo entienda sin ver un solo video.

**Objetivos específicos**

1. **Principios:** identificar 4 a 6 principios ofensivos y defensivos, cada uno como hipótesis comprobable.
2. **Estabilidad:** medir qué tan constantes son a lo largo de los 4 torneos de Jardine.
3. **Interacción con el rival:** leer en paralelo a ambos equipos en cada partido, tramo a tramo: quién domina, cuándo cambia y cómo responde cada uno.
4. **Contexto:** cuantificar los ajustes por marcador, localía, fuerza del rival y momento del partido.
5. **Comparación:** contrastar a Jardine con sus predecesores en el club y con el resto de la Liga MX.
6. **Herramienta:** dejar el motor listo para cualquier equipo y generar la ficha de 10 segundos.

**Cómo cubre el alcance que pide la convocatoria**

| Alcance (convocatoria) | Objetivos | Cómo lo medimos | Salida |
| --- | --- | --- | --- |
| Patrones recurrentes | 1, 2 | Métricas estables entre partidos: perfil, huella de pases, redes | Los 4–6 principios |
| Tendencias del entrenador | 5 | Comparación con predecesores y liga; cambio de entrenador como experimento natural | Mapa de estilos y “huella Jardine” |
| Ajustes según contexto | 3, 4 | Lectura a dos bandas, comparaciones dentro del partido, cambios tácticos de ambos equipos | Tabla “si el rival hace X, Jardine hace Y” |
| Diferencias entre partidos o momentos | 2, 3 | Partidos atípicos, tramos de 15 minutos, evolución por torneo, simulación Monte Carlo | Línea de tiempo con partidos anómalos explicados |

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
| 4. Experimento natural | El cambio de entrenador entre CL23 y AP23, frente al cambio promedio de la liga | El efecto del cambio de entrenador | Estadísticas por equipo y partido |

Hasta donde sabemos, los predecesores en la ventana fueron Solari y Ortiz; la API de Matches lo confirma. Los fichajes del verano 2023 confunden el nivel 4, y lo declaramos como límite.

## Datos y framework

Usamos las 10 APIs de StatsBomb y adoptamos sus definiciones donde existen; lo propio se documenta y todos los umbrales viven en un solo archivo. Detalle en `docs/framework.md` y `docs/api/`.

## Entregables

| Entregable | Contenido | Fecha |
| --- | --- | --- |
| Reporte HTML (Quarto) | Metodología, framework, los 4–6 principios, lectura a dos bandas, comparaciones y fichas | 22 oct 2026 |
| Video de máximo 5 minutos | La historia de Jardine en sus principios y una demostración de la ficha de unos 15 segundos | 22 oct 2026 |
| Ficha de 10 segundos | Una tarjeta por rival: cómo progresa, dónde concede, quién participa poco, su balón parado vulnerable y cómo respondió Jardine ante rivales parecidos | Dentro del reporte |
| Presentación final (solo finalistas) | Máximo 10 diapositivas, con la hoja de ruta como cierre | 11 nov 2026 |

La ficha responde al criterio de evaluación en que el jurado resuelve 3 escenarios de decisión en menos de 90 segundos.

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
| Phases of Play vacío en partidos históricos | Definición propia de transición en `params.yaml` (plan B) |
| Cobertura 360 incompleta | Métricas 360 solo con frames válidos; se reporta la cobertura |
| Narrativa obvia para un jurado que conoce al equipo | Lectura a dos bandas y comparación contra la liga |
| Falta de tiempo | Regla de corte del 14 de octubre; el modo repetición solo si sobra tiempo |
| Fuga de datos o credenciales | Repositorio privado; `data/` y `.env` fuera de git |
| Tabla de evaluación ambigua | Correo a los organizadores y un diseño que cubre ambas lecturas |

## Decisiones abiertas y siguientes pasos

- [ ] Registrar al equipo (antes del 12 de octubre)
- [ ] Enviar el correo a los organizadores: tabla de evaluación, elección del entrenador, límites de la API y reporte interactivo
- [ ] Crear el repositorio privado y la carpeta local (fuera de OneDrive, o con `data/` excluida de la sincronización)
- [ ] Correr la prueba de humo de la API
- [ ] Diseñar el logo en Claude Design
- [ ] Definir la estructura del repositorio en GitHub

**Preguntas sin resolver**

- ¿La tabla de evaluación publicada aplica a este reto?
- ¿La elección de Jardine es libre?
- ¿Phases of Play viene poblado en los partidos de 2023 a 2025?
- ¿El modo repetición entra en la entrega o queda como visión?
