# Ojo de Águila

**Documentación del proyecto · Hackathon ISAC 2026 · Club América**\
Equipo: Samuel de María Cabrera Flores y Héctor Cortés Pérez

> Este documento describe el proyecto, los materiales entregados, la metodología, los resultados y la forma de verificarlos. Está dirigido a quienes lo evalúan sin conocerlo previamente. No es necesario instalar ningún programa: todos los materiales se consultan en el navegador.

## 1. Resumen

Ojo de Águila es un motor analítico reutilizable, construido sobre los datos de Hudl StatsBomb de la Liga MX, que convierte la idea de juego de un entrenador en evidencia medible y en recomendaciones para un cuerpo técnico. Su primer caso de aplicación es **André Jardine en el Club América** (Apertura 2023 – Clausura 2026). Su juego se compara con el de sus antecesores, Fernando Ortiz y Santiago Solari, y con el de cada rival en el mismo minuto de cada partido.

La conclusión principal es que el América de Jardine **propone más que sus rivales, sale jugando corto desde atrás y, cuando el partido se rompe, se instala en campo rival.**

## 2. Objetivo y alcance

**Pregunta central.** ¿Qué principios definen al América de Jardine en ataque y en defensa, qué tan estables son y cómo los ajusta según el marcador, el rival y el momento del partido?

**Objetivo general.** Construir un motor analítico reutilizable sobre las APIs de StatsBomb y usarlo para:
- identificar los principios de juego de Jardine, cada uno con su evidencia;
- comprobar que se sostienen en un torneo que el análisis no vio;
- traducirlos en decisiones que un cuerpo técnico pueda usar sin ver video.

**Alcance.**
- El proyecto **describe y compara**: no afirma relaciones causales.
- La simulación de partidos **explica** resultados con los tiros que ocurrieron; no predice partidos futuros.
- El procesamiento de video y el análisis en tiempo real se plantean como trabajo futuro y no forman parte de lo construido.

## 3. Materiales entregados

| Material | Ubicación | Propósito |
| --- | --- | --- |
| **Página web** (reporte y aplicación en un solo archivo) | https://ojodeaguila.netlify.app/ · también el archivo `ojo_de_aguila.html`, que se abre con doble clic | Reporte completo, en cuatro vistas |
| **Video** (3:55) | Enlace de YouTube incluido en el formulario | Presentación del proyecto en menos de cinco minutos |
| **Código fuente** | https://github.com/SamuelCFlores/OJO_DE_AGUILA (rama `main`; bitácora en la rama `tests`) | Revisión de integridad y reproducibilidad |
| **Esta documentación** | PDF y `DOCUMENTACION.md` en el repositorio | Guía de lectura y referencia técnica |

## 4. Recorrido sugerido de la página (cinco minutos)

Al abrir la página se reproduce una animación de entrada de cinco segundos, que puede omitirse con «Saltar». En la parte superior se encuentran las cuatro vistas.

1. **Resumen** (un minuto). Presenta la tesis, el índice de iniciativa por torneo y los seis principios. Incluye además una foto real del caso: el mapa de control del espacio con la lectura del juego hasta ese momento.
2. **El partido** (dos minutos). Reproduce la final del Apertura 2023 contra Tigres UANL minuto a minuto.
   - El botón ▶ muestra la cancha, el índice de iniciativa de ambos equipos y los eventos de cada minuto: goles, cambios, faltas, tiros de esquina y saques.
   - Conviene detenerse en la expulsión del minuto 79 y revisar las jugadas animadas.
   - La sección «¿Qué tan merecido?» simula el resultado con los tiros del partido.
   - En la barra lateral puede elegirse cualquiera de otros 16 rivales para ver su partido clave con Jardine.
3. **Plan de juego** (un minuto).
   - Matriz de situaciones: 14 tarjetas por marcador, número de jugadores, localía, fase del torneo y cierre del partido.
   - «Qué dice nuestro motor»: la lectura de cada rival.
   - Balón parado, uso de jugadores y tres casos de decisión del Clausura 2026.
4. **Método** (un minuto). Expone los datos, la lectura de un partido, el criterio de hallazgo y la prueba en falso. Siguen los principios con su evidencia, la validación, los límites, un glosario de 42 términos, el trabajo futuro y los créditos.

## 5. Tres decisiones en noventa segundos

| Pregunta del cuerpo técnico | Dónde se responde | Respuesta del motor |
| --- | --- | --- |
| «Vamos 1-0 al minuto 60» | Plan de juego → matriz → **Ganando por 1** | Parejo: el balance de ocasiones deja de ser claro. Hipótesis a probar: sostener la iniciativa |
| «Mañana jugamos contra Pumas» | Barra de rivales → **Pumas UNAM** → «Ver la lectura del motor» | Cómo progresa, cómo defiende, dónde concede, su balón parado y cómo le fue a Jardine contra rivales parecidos |
| «Nos expulsaron a un jugador» | Plan de juego → matriz → **Con uno menos** | Replegarse es lo esperado y el partido se sostiene parejo (muestra chica) |

Las recomendaciones se obtienen con reglas fijas sobre los números y se presentan como hipótesis, no como órdenes.

## 6. Datos

**Fuente.** Hudl StatsBomb, Liga MX, del Apertura 2021 al Clausura 2026, proporcionados para el hackathon. Se usaron las APIs Competitions, Matches, Events, 360 Frames, Lineups y Team Match Stats.

**Volumen.**
- Estadísticas de equipo de 1,701 partidos de la liga.
- 707,900 eventos de 213 partidos del América.
- 627,130 fotos de posiciones (360) de 212 de esos partidos.

**Grupos de comparación.**

| Grupo | Partidos | Torneos | Uso |
| --- | --- | --- | --- |
| Jardine | 110 | AP23 a AP25 | Elegir los principios |
| Solari y Ortiz | 82 | AP21 a CL23 | Comparación |
| Torneo reservado | 19 | CL26 | Validación, abierto una sola vez al final |

**Gestión de los datos.**
- La descarga se hizo con un cliente con caché: 2,557 solicitudes, ninguna fallida.
- Los datos no están en el repositorio ni se publican.
- La página muestra únicamente resultados y las posiciones necesarias para dibujar los partidos.

## 7. Metodología

### 7.1 Mediciones propias

- **Índice de iniciativa.** Combina ocho señales por minuto con el mismo peso, en una escala de 0 (espera y sale al contragolpe) a 100 (tiene el balón y presiona arriba):
  - suman: ataque elaborado, posesión, dominio del último tercio, espacio en campo rival, altura sin balón y presión alta;
  - restan: juego directo y pase largo.

  Un análisis de componentes principales confirma los pesos: coincide en 0.94 con el promedio de pesos iguales.
- **Mapa de control del espacio.** Diagrama de Voronoi sobre cada foto de posiciones (360): cada punto de la cancha pertenece al jugador que llega primero. Se recorta a la zona que ve la cámara y a 18 m por jugador.
- **Lectura frente a frente.** Cada medida del América se lee junto a la del rival en el mismo tramo del partido.
- **Momentos clave.** Goles, expulsiones, cambios de sistema y sustituciones de ambos equipos. Lo que ocurre en los diez minutos posteriores se compara con tramos de otros partidos del mismo entrenador, con igual marcador y minuto similar, en los que no ocurrió nada. La diferencia es el cambio neto, o diferencia en diferencias.

### 7.2 Criterio de hallazgo: los cuatro parámetros

Una diferencia se considera principio solo si cumple los cuatro parámetros, fijados antes de ver los resultados:

1. **Claro:** el rango probable (intervalo de confianza del 95 %, por remuestreo de partidos completos) no incluye el cero.
2. **Grande:** la diferencia mide al menos media variación típica (desviación estándar).
3. **Constante:** va en la misma dirección en al menos cuatro de los cinco torneos de Jardine.
4. **A prueba de suerte:** el riesgo de falso hallazgo es de 10 % o menos, con la corrección de Benjamini y Hochberg.

**Prueba en falso (placebo).** El criterio se aplicó a 280 momentos clave inventados, en tramos donde no ocurrió nada. La primera versión del criterio, sin el cuarto parámetro, aprobaba 11; la versión final no aprueba ninguno. De 636 pruebas del análisis sobreviven 30.

### 7.3 Validación fuera de muestra

El Clausura 2026 se reservó desde el inicio y se abrió una sola vez, con los principios ya fijados. Para cada principio se comprobó si la diferencia mantiene su dirección y si su rango probable excluye el cero.

### 7.4 Simulación explicativa

Cada tiro del partido se repite 10,000 veces como un intento que entra con probabilidad igual a sus goles esperados (xG). La simulación indica qué tan merecido fue un resultado; no se usa para predecir.

### 7.5 Del dato a la decisión

- **Matriz de situaciones:**
  - ocho situaciones excluyentes por marcador y número de jugadores;
  - seis contextos que se cruzan con ellas: local, visitante, cierre del partido, desde el minuto 75, liguilla y fase regular.
- **Lectura del motor por rival:** cómo progresa, cómo defiende, dónde concede, su balón parado y el resultado de Jardine contra rivales parecidos.
- **Partido clave de cada rival:** elegido con una regla fija. Es la eliminatoria más avanzada o, si no hubo, el partido con el momento clave de mayor peso.
- **Casos de decisión del Clausura 2026:** tres partidos elegidos con una regla escrita antes de verlos. En cada uno se muestra qué marcaba la herramienta frente a lo que ocurrió.

## 8. Resultados

| Principio | Jardine | Solari y Ortiz | Clausura 2026 |
| --- | --- | --- | --- |
| Sale jugando corto (largo medio de pase) | 18.7 m | 20.1 m | ✓ Se sostiene |
| Con uno más, hunde al rival (cambio en la altura del rival) | −15.1 m | +2.7 m | — Sin muestra suficiente |
| Una lesión no lo frena (presiones) | +5.6 cada 10 min | −4.2 cada 10 min | ≈ Misma dirección |
| Tras recibir gol, el rival no lo aprieta (presión rival tras perder el balón) | −1.3 cada 10 min | +1.3 cada 10 min | ≈ Misma dirección |
| Alerta: cambiar el sistema le cuesta (goles esperados) | −0.03 cada 10 min | +0.17 cada 10 min | ✓ Se sostiene |
| Refresca las bandas (cambios tácticos de defensas) | 1.15 por partido | 0.43 por partido | ≈ Misma dirección |

**Validación.** En el torneo reservado se confirman dos principios, tres mantienen la dirección sin certeza estadística y uno no tuvo casos suficientes. **Ninguno se invirtió.**

**Índice de iniciativa por entrenador.** Jardine promedia 57; Ortiz, 54, y Solari, 50.

**Lectura por contexto.**
- En liguilla, el América propone menos que en fase regular (índice de 51 frente a 59) y presiona menos.
- Al cerrar un 1-0 desde el minuto 75 pasa a esperar (índice de 37) y el balance de ocasiones deja de ser claro.

## 9. Limitaciones

- **Comparación, no causalidad.** El cambio neto descuenta el paso del tiempo, pero sustituir o cambiar de sistema son decisiones que responden a lo que ya ocurría en el partido.
- **Muestras pequeñas.** Expulsiones, lesiones y cambios de sistema son poco frecuentes; los resultados marcados como «muestra chica» o «sin certeza» se leen con cautela.
- **Cobertura de la cámara.** Las fotos de posiciones solo muestran a los jugadores que ve la cámara. El mapa de control se limita a esa zona, y las posiciones entre dos fotos son estimadas y no se usan en ninguna medida.
- **Escala relativa.** El índice se compara con los partidos del América y sus rivales, porque solo se cuenta con eventos de esos partidos.
- **Recomendaciones como hipótesis.** Nunca se afirma que otra decisión habría cambiado un resultado.

## 10. Arquitectura y reproducibilidad

**El motor, por capas.** Cada capa solo usa las anteriores.

| Capa | Ubicación | Función |
| --- | --- | --- |
| Ingesta | `src/ojo/ingesta/` | Cliente de las APIs con caché, pausas y reintentos |
| Datos | `src/ojo/datos/` | Conversión de JSON a tablas (parquet); único punto de lectura de los datos |
| Framework | `src/ojo/framework/` | Definiciones: tramos, marcador, orientación, momentos clave |
| Lentes | `src/ojo/lentes/` | Mediciones: Voronoi, índice, hallazgo, matriz, balón parado, rivales, simulación |
| Salidas | `src/ojo/salidas/` | Datos de la página, partido clave, decisiones y reproductor |

**Flujo de trabajo.**
- Los scripts `scripts/00_prueba_humo.py` a `scripts/10_guia.py` van de la prueba de conexión con la API a esta documentación en PDF.
- Las pruebas de hipótesis están en `notebooks/02` a `notebooks/07`, que se guardan sin salidas.
- La página se diseña en `app/` (HTML, CSS y JavaScript), y `scripts/09_entrega.py` la reúne en un solo archivo.

**Coherencia.**
- Cada métrica se define en `contexto/framework.md`.
- Todos los umbrales están en `config/params.yaml`; el código no contiene valores fijos.

**Pruebas.** `python -m pytest` ejecuta 146 pruebas automáticas con datos sintéticos, sin credenciales.

**Reproducción.** Para obtener las cifras se requieren credenciales de StatsBomb, porque las reglas de la competencia no permiten compartir los datos. La instalación y el orden de los pasos se describen en el `README.md`.

## 11. Trazabilidad y registro de cambios

- **Bitácora diaria:** la carpeta `CAMBIOS/` de la rama `tests` (https://github.com/SamuelCFlores/OJO_DE_AGUILA/tree/tests/CAMBIOS).
  - Diez registros, uno por jornada de trabajo, del `C01_0810.md` (8 de octubre) al `C10_2110.md` (21 de octubre).
  - Cada registro anota lo planeado, lo hecho, lo pendiente, las propuestas y quién hizo cada cambio, incluidos los que se hicieron con apoyo de IA.
  - Las reglas de la bitácora están en `CAMBIOS/README.md`.
- **Historial de versiones:**
  - la rama `tests` concentra el trabajo diario, con más de 80 commits desde el 5 de octubre;
  - la rama `main` solo recibe lo confirmado, mediante solicitudes de integración (*pull requests*) desde ramas `promocion/ddmm`;
  - una revisión automática impide que la bitácora llegue a `main`.
- **Auditorías:** la carpeta `auditoria/` contiene dos revisiones de solo lectura del proyecto, del 14 y del 19 de octubre, con sus hallazgos y lo que se corrigió.
- **Decisiones del proyecto:** en `contexto/`:
  - propuesta y objetivos (`propuesta_base.md`);
  - definiciones (`framework.md`);
  - plan de cierre (`plan_cierre.md`);
  - términos para el jurado (`terminologia.md`);
  - guion del video (`guion_video.md`);
  - uso de IA (`uso_ia.md`).

## 12. Datos de terceros, software y uso de inteligencia artificial

- **Datos.** Hudl StatsBomb, de uso exclusivo para la competencia. El resumen que el equipo elaboró de su documentación también se retiró del repositorio (`contexto/api/REMOVIDO.md`).
- **Métricas del proveedor.** Se usan sin cambios los goles esperados (xG), el valor de cada acción (OBV), las fases de juego y los 60 tipos de pase. El resto de las mediciones son propias.
- **Inteligencia artificial generativa.** Se usó Claude Code (Anthropic) como asistente de programación:
  - escribió y revisó buena parte del código;
  - apoyó la redacción de textos;
  - armó la animación del video y su exportación.

  El equipo fijó las preguntas, las definiciones, los umbrales, las reglas de decisión y la interpretación, y cada cifra la calcula el código, con pruebas. Las voces del video son de los integrantes del equipo. El detalle está en `contexto/uso_ia.md` y en la página (Método, sección 10).
- **Software libre.** Python (pandas, NumPy, SciPy, Shapely, NetworkX, mplsoccer, Matplotlib, scikit-learn, statsmodels, DuckDB, PyArrow, entre otras), React y la tipografía Poppins (licencia SIL Open Font).
- **Métodos de la literatura.** Diagramas de Voronoi, remuestreo (bootstrap), corrección de Benjamini y Hochberg (1995), diferencia en diferencias y análisis de componentes principales.
- **Fotografías del video.** Imágenes de prensa usadas únicamente como ilustración; sus derechos pertenecen a sus autores.

## 13. Trabajo futuro

La base construida permite incorporar, sin cambiar el motor:
- **video y datos de seguimiento (tracking),** para tener a los 22 jugadores en todo momento y no solo a los que ve la cámara;
- **diagramas en tiempo real** del mapa de control del espacio y del índice de iniciativa, en partidos oficiales o en interescuadras de entrenamiento.

Esta sección es una propuesta: no forma parte de lo construido.
