# Auditoría de Ojo de Águila · 14/10/2026

Revisión de solo lectura de la rama `tests` (último commit `d73abd4`, 13/10/2026, Samuel). No se modificó nada del repo, no se tocaron `data/` ni `.env` y no se corrió ningún script de descarga. Faltan **8 días** para la entrega (22/10).

## Veredicto en una línea

El motor está bien hecho y es confiable como código; el riesgo ya no es técnico sino de **cierre**: no hay reporte Quarto, ni ficha, ni principios escritos, y la estadística de los quiebres necesita dos ajustes antes de contar hallazgos al jurado.

## 1. Lo que está bien

- **Pruebas**: 91 pasan en 3 s con las versiones fijas de `requirements.txt` (Python 3.13, entorno limpio en Linux). Cobertura de `src/ojo` del 88 %; `quiebres.py`, `redes.py`, `juego.py` y `config.py` al 100 %.
- **Higiene de datos y credenciales**: en todo el historial de git no hay JSON, parquet, CSV ni `.env` (solo `.env.example` y un fixture sintético). `.gitignore` bloquea formatos de datos en cualquier carpeta, los tres notebooks están sin salidas y `nbstripout` está configurado. Ninguna credencial en el historial.
- **Cliente de la API** (`src/ojo/ingesta/cliente.py`): caché en disco, escritura atómica, pausa mínima, reintentos con espera creciente y `Retry-After`, detección de login por redirección, y nunca registra credenciales. Cumple la regla 3.
- **Capas limpias**: un solo punto de lectura de `data/` (`ojo.datos`), funciones puras en `tablas.py`, umbrales en `params.yaml` sin números mágicos relevantes en el código.
- **Diseño analítico serio**: diferencia en diferencias con ventanas de control emparejadas por periodo, marcador y minuto; bootstrap por partido (la unidad correcta); criterio de hallazgo fijado antes de ver resultados; CL26 apartado como prueba (`INCLUIR_PRUEBA = False` en el notebook 02). Que el notebook reporte "cuántas pasarían por azar" es buena práctica.
- **Bitácora** (`CAMBIOS/`) al día y honesta: registra también lo que no salió (el Voronoi promedio no distingue entrenadores).

## 2. Hallazgos

### Alta (afectan lo que se le contará al jurado)

**A1. El caso estrella no es de Jardine.** El caso Fidalgo (`scripts/07_caso.py --partido 3886547`) es la semifinal de vuelta del CL23 contra Chivas. Según `params.yaml`, Ortiz dirigió hasta el 22/05/2023 y Jardine llegó el 01/07/2023, así que ese partido es de **Ortiz**. Hoy es el ejemplo de la portada (`src/ojo/salidas/app.py:48`) y el centro del guion de video propuesto. Sirve como demostración del método o como contraste "antes de Jardine", pero la pieza central del video y de la portada debería ser un partido de Jardine.

**A2. El criterio de hallazgo filtra menos de lo que parece.**
- La condición 2 divide el efecto de una ventana de 10 minutos entre la DE de la métrica **por partido completo** (`src/ojo/lentes/hallazgo.py:52`, notebook 02 celda 11). Las ventanas cortas varían mucho más que los promedios de partido, así que casi todo supera 0.5 DE. El propio `framework.md` lo admite (OBS1, línea 118). En la práctica el criterio tiene dos condiciones, no tres.
- Sugerencia: usar como escala la DE del cambio antes→después **en las ventanas de control** (ya están calculadas en `cambio[cambio["es_control"]]`). Es la misma idea, con la escala correcta.
- Multiplicidad: 279 pruebas en "quiebres con Jardine", 279 frente a predecesores y 636 en la tabla final. Con las tres condiciones, el azar puro dejaría pasar del orden de 5 a 10 de cada 279 (estimación, no calculada). Pasan 32, muchas mecánicas (expulsiones). Recomiendo agregar una columna con Benjamini-Hochberg (FDR) sobre los p del bootstrap y presentar solo lo que sobreviva, o al menos ordenar por eso.

**A3. La regla de corte del Voronoi es casi imposible de reprobar.** "Sigue como lente estructural si alguna de sus métricas cumple el criterio después de algún quiebre" (`framework.md:118`) se evalúa sobre unas 200 combinaciones (5 métricas × 10 tipos × 2 lados × 2 análisis). Con tantas oportunidades, algo pasa casi seguro. La decisión de hoy (14/10) debería decir qué métrica concreta pasó, tras qué quiebre, y si sobrevive al ajuste de A2. Si solo sobreviven efectos de expulsiones, el Voronoi está midiendo "hay un jugador menos", no un principio de Jardine.

**A4. El control del Voronoi depende de cuántos jugadores ve la cámara.** El notebook 01 lo midió: cada jugador visible de más baja el control ~0.2 puntos, y con Jardine se ven 0.5–0.8 jugadores más por frame. En los quiebres esto pesa: una expulsión o una sustitución que cambia el ritmo cambia también la cobertura. El panel (`src/ojo/lentes/minuto.py`) no guarda cuántos jugadores visibles hubo por minuto. Recomiendo sumar `n_jugadores` al panel y controlar por él (o reportar el control por jugador visible) antes de afirmar "sus cambios ganan espacio arriba".

### Media

**M1. Faltan las piezas que se entregan.** No existe ningún `.qmd` ni el reporte Quarto; no hay código de la ficha de 10 segundos, de Monte Carlo ni de `scripts/08_resumenes.py`. El contrato de `resumenes.json` pide `ppda`, `altura_recuperacion` y `field_tilt` por combinación (`src/ojo/salidas/resumenes.py:30`), pero nada los produce todavía (es la tarea pendiente de Tilin en C03). La barra lateral es maqueta: sus controles no recalculan.

**M2. La rúbrica sigue sin confirmar.** El repo construye el pilar 2 (log-loss, calibración, R²) sobre una tabla de 30/25/25/20. La página oficial muestra 4 criterios de 25 % y pide que la simulación explique y no prediga. Si manda la oficial, el pilar 2 resta tiempo sin sumar puntos. También sigue abierta la pregunta de si se aceptan datos AP25–CL26 (hay plan B en `params.yaml`).

**M3. El procesado incremental puede dejar salidas viejas.** `scripts/05_panel.py:73` y `almacen.procesar_partido` saltan un partido si su parquet ya existe, sin revisar si la entrada cambió. Si se rehace `eventos` (como pasó con `tarjeta` el 12/10) y no se corre `05_panel.py --forzar`, el panel queda con la versión anterior sin avisar. Antes de los números finales, conviene correr 03 → 04 → 05 con `--forzar` en limpio una vez.

**M4. No hay CI que corra las pruebas.** El único workflow (`.github/workflows/main_sin_cambios.yml`) solo revisa que `CAMBIOS/` no llegue a main. Un workflow con `pytest` en push a `tests` cuesta poco y evita que alguien rompa algo a 2 días de la entrega.

**M5. Los resultados viven solo en los notebooks.** Los criterios, tablas y figuras de hallazgos se calculan en celdas (notebooks 02 y 03), no en `src/`. Para el reporte conviene mover a `src/ojo/lentes/` la función que arma `efectos` y la que evalúa el criterio, para que Quarto llame lo mismo que el notebook y no una copia.

### Baja

- **B1.** En `filtrar_jugadores` (`src/ojo/lentes/voronoi.py:145`) se quitan jugadores duplicados por coordenadas; si el actor comparte coordenadas con otro jugador y llega segundo, se pierde el actor y `apoyos`/`rivales_cerca` quedan en NaN. Raro, pero conviene conservar siempre al actor.
- **B2.** Una tarjeta roja por `bad_behaviour` a un suplente o al banquillo (`src/ojo/datos/tablas.py:105`) cuenta como expulsión aunque el equipo siga con 11. Vale filtrar por jugadores en cancha o revisar a mano las pocas expulsiones.
- **B3.** Los segmentos de control solo emparejan por marcador; un segmento después de una expulsión (10 contra 11) puede servir de control a un gol. Se podría agregar "número de jugadores" a `segmentos_libres`.
- **B4.** El modelo de agresividad (notebook 02, celda 21) usa efectos fijos por partido junto con la variable rezagada; con ~18 tramos por partido eso sesga el coeficiente (sesgo de Nickell). No cambia la conclusión ("no pasa"), pero no conviene presentarlo como causal.
- **B5.** `CLAUDE.md` en `main` está desactualizado frente a `tests` (ventana AP23–CL25 frente a AP23–CL26, estado de avance). Se corrige solo con la próxima promoción.

## 3. Estado frente al calendario

| Pieza | Estado | Comentario |
| --- | --- | --- |
| Ingesta, descarga y procesado | Hecho | 2,557 solicitudes sin fallas, 213 partidos del América |
| Framework (tramos, marcador, orientación, quiebres) | Hecho y probado | Bien documentado |
| Voronoi, forma, redes, panel por minuto | Hecho | Ver A3 y A4 |
| Corte de Voronoi | **Vence hoy** | Falta escribir la decisión con la métrica concreta |
| Hallazgos y principios | En notebooks | Falta convertirlos en 3–4 principios con número e intervalo |
| PPDA, altura de recuperación por tramo | Pendiente (Tilin) | Bloquea `resumenes.json` |
| Ficha de 10 segundos | No empezada | |
| Reporte Quarto | No empezado | Es el entregable principal |
| Video | No empezado | Guion propuesto gira en torno a un partido de Ortiz (A1) |

## 4. Qué haría en los 8 días

1. **Hoy**: confirmar la rúbrica; escribir la decisión del Voronoi con la métrica y el quiebre concretos; elegir un caso de Jardine para la portada y el video.
2. **15–16 oct**: ajustar el criterio (A2: escala de control y FDR), agregar `n_jugadores` al panel (A4) y volver a correr el notebook 02. Lo que sobreviva son los principios.
3. **16–17 oct**: PPDA y altura de recuperación por tramo (Tilin) y `08_resumenes.py`; mover a `src/` lo que el reporte necesite (M5).
4. **17–19 oct**: esqueleto Quarto ya, aunque sea con texto provisional, y la ficha por rival.
5. **19–20 oct**: corrida en limpio 03 → 05 con `--forzar` (M3), congelar código, ensayo con cronómetro.

Si hay que recortar, lo primero que sale es el pilar predictivo (log-loss, R²) y el placebo Solari → Ortiz.
