# Rúbrica de próximos pasos · 14 oct 2026

> **Actualización 18 oct.** Los organizadores confirmaron la rúbrica **oficial**: innovación, comunicación, accionabilidad, y metodología y visualización, 25 % cada una; la simulación explica, no predice. La entrega es **un solo HTML** (sin Quarto). Por eso:
> - salen los pasos 6 (modelo de riesgo), 13 (barra que filtra), 14 (costo de progresión), 15, 20 (CI) y 22 (presentación, después del 22);
> - el paso 5 pasa a "estabilidad fuera de muestra" y el 16 a "HTML único" (`scripts/09_entrega.py`).
>
> Lo hacen chamuel y Claude Code. El plan y el cómo se cubre cada criterio están en `contexto/propuesta_base.md`, "Rúbrica oficial".

Para revisarla entre **chamuel** y **Tilin** en unos 30 minutos y decidir qué hacer en los 8 días que quedan (entrega: 22 oct).

**Rúbrica del jurado.** Se trabaja con la tabla planeada (predictiva 30 %, causal 25 %, interpretabilidad 25 %, valor operativo 20 %) mientras los organizadores responden el correo del 14 oct. Al lado va la tabla de la página oficial (innovación, comunicación, accionabilidad, metodología y visualización, 25 % cada una) y sus "componentes esperados", para que nada de lo que hagamos quede fuera si la oficial es la que aplica.

## 1. Cómo usarla

1. **Dónde estamos (sección 2):** acuerden el nivel actual de cada criterio con la escala de la sección 3.
2. **Qué sigue (sección 4):** califiquen cada paso con la escala de la sección 5 y calculen su prioridad.
3. **Decidan:** con prioridad ≥ 6 se hace ya; entre 3 y 5 se planea; con 2 o menos se recorta si falta tiempo. Pongan responsable y fecha.
4. **Cierren (sección 6):** revisen la definición de "hecho" de cada entregable.

## 2. Dónde estamos frente al jurado

| Criterio (tabla planeada) | Peso | Equivale en la oficial | Nivel hoy (1–4) | Lo que ya tenemos | Lo que falta para subir |
| --- | --- | --- | --- | --- | --- |
| Capacidad predictiva | 30 % | Metodología (25 %) | 1 · Insuficiente | CL26 apartado sin tocar; índice Proactivo–Reactivo por minuto (propuesta) | Modelo de comportamiento con R² en el CL26 contra una línea base; modelo de riesgo con log-loss y calibración |
| Identificación causal | 25 % | Metodología (25 %) | 2 · Básico | Diferencia en diferencias por quiebres con controles emparejados, bootstrap por partido y criterio fijado antes de ver resultados | Criterio v2 (escala de las ventanas de control y FDR), prueba placebo, controlar cámara y número de jugadores, fuerza del rival, relevo Ortiz → Jardine frente a la liga |
| Interpretabilidad | 25 % | Comunicación (25 %) y visualización | 3 · Sólido | App con portada "Jardine en 90 segundos", tarjetas de principios, reproductor con Voronoi animado, radar y "Cómo leerla" | Reporte Quarto, video, prueba de 3 escenarios en menos de 90 s con alguien externo |
| Valor operativo | 20 % | Accionabilidad (25 %) | 1 · Insuficiente | Lecturas para el cuerpo técnico (hipótesis) en las tarjetas | Ficha de 10 segundos, matriz de situaciones, casos de decisión del CL26 |
| — | — | Innovación (25 %) | 3 · Sólido | Voronoi recortado al área visible, lectura por quiebres, índice Proactivo–Reactivo, Voronoi en movimiento con seguimiento estimado | Costo de progresión (grafo de pases dirigido) |

**Componentes esperados de la página oficial**

| Componente | Estado | Dónde está o qué falta |
| --- | --- | --- |
| Construcción de juego | Parcial | Largo de pase y huella (salida corta); falta leerlo por zonas de salida |
| Progresión entre fases | Parcial | Field tilt, red por posición; falta el costo de progresión |
| Generación de ocasiones | Parcial | xG, OBV, Monte Carlo explicativo; falta un mapa de origen de ocasiones |
| Presión | Parcial | Presión alta en el índice; falta PPDA por tramo (Tilin) |
| Organización defensiva | Parcial | Altura, largo y compactación del bloque (forma); falta altura de recuperación |
| Transiciones | Parcial | Tiros en transición y contragolpes en contra (principio "ganando, cierra la transición") |
| Consistencia y variabilidad | Parcial | Índice por torneo, dirección en 5 torneos, huella que evoluciona |
| Uso de jugadores | Falta | Roles por posición, cambios en alineaciones, impacto de sustituciones (quiebres) |
| Balón parado ofensivo y defensivo | **Falta** | Córners, tiros libres, laterales; zonas de remate y de vulnerabilidad |
| Evidencia cuantitativa | Cubierto | xG, OBV, field tilt, presión; métricas propias (Voronoi, índice) |
| Framework analítico | Cubierto | `contexto/framework.md` y `config/params.yaml` |

## 3. Escala para calificar el proyecto (1–4)

| Criterio | 1 · Insuficiente | 2 · Básico | 3 · Sólido | 4 · Sobresaliente |
| --- | --- | --- | --- | --- |
| Predictiva | No hay modelo evaluado fuera de muestra | Un modelo evaluado en el CL26, sin línea base o sin calibración | Comportamiento (R²) y riesgo (log-loss) superan la línea base; curva de calibración | Además, estables por rival y explicados en lenguaje de cancha |
| Causal | Solo correlaciones | Comparación emparejada sin controles de confusión | Diferencia en diferencias con placebo, FDR y controles (cámara, número de jugadores, rival) | Además, relevo frente a la liga con placebo y supuestos discutidos |
| Interpretabilidad | Gráficas sin explicación | Cada gráfica con texto, pero no se entiende sin el equipo | Alguien externo resuelve 3 escenarios en menos de 90 s | Lo resuelve con la ficha sola; el video cuenta la historia completa |
| Valor operativo | Curiosidades estadísticas | Recomendaciones genéricas | Ficha y matriz con recomendaciones por situación | Casos reales del CL26: qué marcaba la herramienta frente a lo que decidió Jardine |
| Innovación (oficial) | Métricas estándar | Una métrica propia | Varias lentes propias coherentes | Una forma nueva de ver el partido que el jurado no ha visto |

## 4. Próximos pasos a evaluar

La columna **Sugerencia** es la de Claude Code (Alta / Media / Baja); las columnas de calificación son para llenarlas juntos con la escala de la sección 5.

| # | Paso | Criterio que mueve | Hecho cuando | Responsable sugerido | Depende de | Sugerencia | Impacto | Urgencia | Esfuerzo | Riesgo | Prioridad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Confirmar el índice Proactivo–Reactivo (PCA, pesos) y fijarlo en el framework | Predictiva, interpretabilidad | Definición confirmada en `framework.md`; TODO1 cerrado | chamuel | — | Alta | | | | | |
| 2 | Criterio v2, prueba placebo y FDR (auditoría A2, A3) | Causal | Tabla de hallazgos v2 con cuántos pasan por azar | chamuel | — | Alta | | | | | |
| 3 | Jugadores visibles y en cancha en el panel y los controles; arreglos B1–B3 (auditoría A4) | Causal | Rerun del notebook 02 con estos controles | chamuel | 2 | Alta | | | | | |
| 4 | PPDA y altura de recuperación por tramo | Predictiva, componentes | Métricas en el panel con pruebas | Tilin | — | Alta | | | | | |
| 5 | Modelo de comportamiento: predecir el índice por tramo según el contexto | Predictiva | R² en el CL26 frente a dos líneas base | chamuel | 1, 4 | Alta | | | | | |
| 6 | Modelo de riesgo: peligro en contra en los próximos 10 minutos | Predictiva, accionabilidad | Log-loss y curva de calibración en el CL26 | chamuel | 1, 5 | Alta | | | | | |
| 7 | Balón parado ofensivo y defensivo (Voronoi en el envío, zonas de remate) | Componente obligatorio | Sección en la app y en el reporte | Tilin | — | Alta | | | | | |
| 8 | Uso de jugadores: roles por posición, alineaciones, impacto de sustituciones | Componente obligatorio | Sección con 2–3 hallazgos | Tilin | 2 | Media | | | | | |
| 9 | Relevo Ortiz → Jardine frente a la liga, placebo Solari → Ortiz | Causal | Efecto con intervalo y placebo | chamuel | 2 | Media | | | | | |
| 10 | Ficha de 10 segundos por rival | Valor operativo | Una ficha por rival frecuente en la app | Tilin | 4, 7 | Alta | | | | | |
| 11 | Matriz de situaciones (situación → qué hace Jardine → qué le funciona → recomendación) | Valor operativo | Tabla en la app y en el reporte | chamuel | 2, 6 | Alta | | | | | |
| 12 | Casos de decisión del CL26 | Valor operativo | 3–5 casos "la herramienta marcaba X; Jardine hizo Y" | chamuel | 6, 11 | Media | | | | | |
| 13 | `resumenes.json` v2 y barra que filtra de verdad | Interpretabilidad | La barra recalcula la vista | Tilin | 4 | Media | | | | | |
| 14 | Costo de progresión (grafo de pases dirigido) | Innovación | Métrica y figura | chamuel | — | Baja | | | | | |
| 15 | Monte Carlo explicativo desde el estado de cada quiebre | Interpretación (simulación opcional) | En el reproductor del caso | chamuel | — | Baja | | | | | |
| 16 | Reporte Quarto: esqueleto con la narrativa | Entregable principal | Render en HTML con todas las secciones | ambos | — | **Alta** | | | | | |
| 17 | Video de 5 minutos con el caso de Jardine | Comunicación | Guion, grabación y edición | ambos | 16 | Alta | | | | | |
| 18 | Prueba de 3 escenarios en menos de 90 s con alguien externo | Interpretabilidad | Tiempo medido y ajustes | ambos | 10, 11 | Media | | | | | |
| 19 | Corrida en limpio 03 → 05 con `--forzar` y congelar código (auditoría M3) | Calidad | Números finales reproducibles | chamuel | todo lo anterior | Alta (al final) | | | | | |
| 20 | CI con pytest en cada push a `tests` (auditoría M4) | Calidad | Workflow en verde | Tilin | — | Media | | | | | |
| 21 | Promoción a `main` (`promocion/ddmm`, sin `CAMBIOS/`) | Orden | PR revisado y fusionado | ambos | 19 | Media | | | | | |
| 22 | Presentación de 10 diapositivas (solo finalistas, 11 nov) | Comunicación | Después del 2 nov | ambos | — | Baja | | | | | |

## 5. Escala para calificar cada paso

| Eje | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- |
| **Impacto** | Cosmético | Mejora menor de un criterio | Mejora clara de un criterio | Sube de nivel un criterio de 25–30 % o es un componente obligatorio |
| **Urgencia** | Puede esperar a finalistas | Antes del 21 oct | Antes del 19 oct | Bloquea otros pasos o vence antes del 17 oct |
| **Esfuerzo** | Menos de 2 h | Medio día | Un día | Más de un día |
| **Riesgo** | Bajo | Algo incierto | Puede no salir a tiempo | Puede no salir o romper algo que ya funciona |

**Prioridad = 2 × Impacto + Urgencia − Esfuerzo − Riesgo** (de −6 a 10). Con 6 o más se hace ya; de 3 a 5 se planea; con 2 o menos se recorta si falta tiempo.

## 6. Definición de "hecho" por entregable

| Entregable | Está hecho cuando |
| --- | --- |
| Reporte HTML (Quarto) | Tiene metodología, framework, principios con número e intervalo, ajustes por contexto, casos confirmadores de Jardine, validación en el CL26 y límites; se entiende sin el equipo; no lleva datos crudos |
| Video (máx. 5 min) | Cuenta la historia de Jardine con un caso suyo (final AP23), muestra la app y una decisión; dura menos de 5 min |
| Ficha de 10 segundos | Por rival: cómo progresa, dónde concede, quién participa poco, balón parado vulnerable y cómo respondió Jardine ante rivales parecidos |
| App (`app/maqueta.html`) | Portada, barra que filtra, reproductor y "Cómo leerla" con datos de cualquier rival; abre sin servidor |
| Repo | Pruebas en verde, corrida en limpio reproducible, `main` promovido sin `CAMBIOS/` |
| Correo de entrega | A itamsportsanalytics@gmail.com con los correos de los integrantes, antes del 22 oct |

## 7. Calendario propuesto

| Fecha | Qué |
| --- | --- |
| 15 oct | Pasos 1, 2 y 4; esqueleto del reporte (16) |
| 16 oct | Pasos 3, 5 y 7 |
| 17 oct | Pasos 6, 8 y 10 |
| 18 oct | Pasos 9, 11 y 13 |
| 19 oct | Pasos 12 y 18; guion del video (17) |
| 20 oct | Reporte completo; grabación del video; paso 19 |
| 21 oct | Edición, revisión final, pasos 20 y 21 |
| 22 oct | Entrega |

**Si falta tiempo, se recorta en este orden:** 22, 15, 14, 9 (dejar solo el placebo dentro de 2), 13 (la barra puede quedar como maqueta), 12.

## 8. Decisiones abiertas

- ¿Qué tabla de evaluación aplica? (correo enviado el 14 oct; mientras, la planeada).
- ¿Se aceptan datos posteriores al CL25? Si no, plan B: prueba en el CL25.
- ¿El índice Proactivo–Reactivo es el eje de la narrativa?
- ¿Quién graba y edita el video?
