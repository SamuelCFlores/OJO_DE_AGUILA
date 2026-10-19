# Ojo de Águila — contexto para Claude Code

Proyecto de Samuel de María Cabrera Flores (Ingeniería en Ciencia de Datos, BUAP) para el Hackathon ISAC 2026 con el Club América: "La Historia de un Entrenador a través de los Datos". Responde siempre en español.

## Qué construimos

Un **motor analítico reutilizable** sobre las APIs de StatsBomb (Liga MX, Apertura 2021 – Clausura 2026) y su primer caso: **el América de André Jardine** (Apertura 2023 – Clausura 2026).

Objetivo: contar la historia de Jardine en el América: sus principios de juego, con el control del espacio como lente central; qué tan estables fueron; cómo interactúan con lo que hace el rival en cada partido y cómo los ajustó según marcador, localía, rival y momento. Medir qué cambió con su llegada frente a Solari y Ortiz (relevo como experimento natural) y validar en un torneo que el modelo no vio (Clausura 2026) que esos principios anticipan su comportamiento y sus resultados, de forma que un cuerpo técnico lo entienda sin ver un solo video y lo use para tomar decisiones. Texto completo en `contexto/propuesta_base.md`.

Eje central, tres pilares: (1) **Espacio**: Voronoi sobre el 360, recortado a `visible_area`; (2) **Evidencia con rigor**: cada principio con número, intervalo, prueba placebo y corrección por pruebas múltiples, y su estabilidad en un torneo que el análisis no vio; (3) **Del dato a la decisión**: matriz de situaciones, ficha de 10 segundos y casos de decisión. Nunca prometer que la herramienta "habría cambiado" una decisión: se muestra qué recomendaba frente a lo que se decidió.

Entregables (formulario, una persona por equipo, jueves 22 de octubre de 2026, 23:59 CDMX):
- **Obligatorios:** video de máximo 5 minutos y reporte del proyecto (HTML o PDF).
- **Adicionales:** archivo HTML, enlace a la app alojada, repositorio y presentación en PDF (esta última obligatoria si pasamos a la final, con el contenido del reporte; 10 diapositivas, 11 de noviembre).
- **El jurado no ejecuta código ni instala nada:** ve páginas web, videos, tableros y reportes; no clona repositorios ni descarga ejecutables.
- **Decisión (19 oct):** el reporte es **un solo archivo HTML autocontenido** (la app y el reporte juntos, con las fichas de 10 segundos; sin Quarto). Debe abrirse con doble clic, y se entrega además como **enlace web**: la carpeta `outputs/publicar/` se aloja, con `noindex` y el enlace solo en el formulario. A eso se suma el video.

## Decisiones tomadas

- Entrenador: André Jardine. Comparaciones: el rival en el mismo partido ("lectura a dos bandas"), sus predecesores en el América (Solari y Ortiz, confirmados en Matches), la Liga MX y el cambio de entrenador CL23 → AP23 como experimento natural, con placebo Solari → Ortiz y, si alcanza, todos los relevos de la liga.
- Entrenadores del análisis: solo Solari, Ortiz y Jardine (ids en `config/params.yaml`); quedan fuera Diego Cervantes (interino, 2 partidos en enero de 2025) y Jorge Almada (sucesor, 2026/27). De Solari solo hay datos desde el Apertura 2021.
- Lentes propias: control territorial con Voronoi (360), redes de pases por posición (no por jugador), huella de pases (60 clusters de StatsBomb). Además, métricas del proveedor: xG, OBV, PPDA, Phases of Play.
- Regla del framework: si StatsBomb define un objeto, se adopta; si no, se define en `contexto/framework.md`. Todos los umbrales viven en `config/params.yaml`.
- Tiempo real: solo visión a futuro. Nada en vivo, sin video ni tracking durante el hackathon.
- Regla de corte: si el 14 de octubre Voronoi no da hallazgos claros, pasa a lente de apoyo.
- Rúbrica (confirmada el 18 oct): la **oficial**, cuatro criterios de 25 %: innovación, comunicación, accionabilidad, y metodología y visualización. Además, los "componentes esperados" de la página oficial, entre ellos balón parado y uso de jugadores. La simulación es **para explicar, no para predecir**. La tabla 30/25/25/20 queda sustituida; cómo se cubre cada criterio está en `contexto/propuesta_base.md`, "Rúbrica oficial".
- Validación: entrenamiento AP23–AP25, prueba en el Clausura 2026 (intocable hasta la evaluación final, sin fuga de información). Plan B si los organizadores no permiten datos posteriores al CL25: AP23–AP24 y prueba en el CL25. Detalle en `contexto/framework.md`, "Validación, causalidad y decisión".
- Idea central (12 oct): leer el partido por **puntos de quiebre** (goles, expulsiones, cambios de sistema, sustituciones tácticas y por lesión, de ambos equipos): antes/después en ambos equipos, contra ventanas de control emparejadas (diferencia en diferencias). Criterio de hallazgo fijado antes de ver resultados y evaluado sin el CL26 (`contexto/framework.md`, "Lectura del partido por puntos de quiebre"). Cómo se conecta cada herramienta: `contexto/propuesta_base.md`, "Idea central".
- Monte Carlo: solo explicativo ("qué tan merecido fue", con el xG de los tiros del propio partido). El Monte Carlo predictivo antes del partido y el modelo de riesgo de 10 minutos salieron del alcance el 18 oct.

## Reglas no negociables

1. **Datos**: solo para la competencia; se publican resultados, nunca datos. `data/` y `.env` jamás entran a git. No imprimas filas de datos crudos en salidas que se vayan a compartir.
2. **Credenciales**: solo en `.env` (`STATSBOMB_USER`, `STATSBOMB_PASSWORD`). Nunca en código, logs, notebooks ni mensajes. Si las ves, no las repitas.
3. **Consumo de la API**: todo pasa por el cliente con caché; nunca descargar dos veces lo mismo; pausa entre solicitudes y reintentos con espera creciente (429/5xx).
4. **Coherencia**: cada métrica sale de una definición de `contexto/framework.md` y de un umbral de `config/params.yaml`. Sin números mágicos en el código.
5. **No inventes campos**: antes de usar un campo de la API, revísalo en `contexto/api/`. Si un campo real difiere de la documentación, avísalo y anótalo.
6. **Honestidad analítica**: separa correlación de causalidad; marca supuestos; no presentes la visión a futuro como algo construido.

## Entorno

- Windows + PowerShell, Python 3.13, `venv`, `requirements.txt` con versiones fijas, VS Code + Jupyter.
- Librerías: requests, python-dotenv, pandas, pyarrow, duckdb, numpy, scipy, shapely, networkx, mplsoccer, matplotlib, scikit-learn, statsmodels, pyyaml, tqdm, nbstripout. Sin Quarto: la entrega es un HTML autocontenido que arma un script.
- Rutas con `pathlib`; nada de rutas absolutas ni separadores fijos. Cuidado con OneDrive y rutas con acentos.
- Clon local de Samuel: `C:\Users\samue\OneDrive\Documentos\PROYECTOS\C_AMERICA`. Está bajo la carpeta de OneDrive pero la sincronización no está activa (todo queda en local); si se activa, excluir `data/` y `.venv/`.
- Activar el entorno: `.venv\Scripts\Activate.ps1` (si falla: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`).

## Cómo trabajar

- El código reutilizable va en `src/ojo/`; los notebooks son solo exploración y llaman a `src/`.
- **Maqueta definitiva (18 oct): `app/maqueta.html`** con `app.css`, `app.js` y `movimiento.js`. Todo cambio visual se hace ahí; sus datos los escribe `scripts/08_maqueta.py` en `outputs/app/datos.js`. La maqueta 2 (`scripts/07_caso.py`, `ojo.salidas.app`), los `outputs/reportes/maqueta_*.html` y `branding/maqueta.html` (solo la demostración de la marca) quedan como históricas y no se editan.
- Las páginas (maquetas, explorador) se diseñan en `app/` (HTML, CSS y JS editables a mano y versionados); Python solo escribe sus datos en `outputs/app/` (fuera de git). Contrato en `app/README.md`.
- Los modelos (comportamiento con R², Monte Carlo, efecto del relevo) se trabajan en notebooks `notebooks/NN_tema.ipynb`. La primera celda dice qué hace, qué necesita (pasos 02–04 corridos) y cómo probarlo; al terminar, se le dice a Samuel qué se hizo y qué celdas correr. Lo que sirva dos veces se mueve a `src/ojo/`.
- Funciones pequeñas con docstring en español, tipadas, sin efectos ocultos. Identificadores en español o inglés sin acentos, de forma consistente dentro de cada módulo.
- Cada script nuevo trae instrucciones para probarlo; agrega pruebas en `tests/` para la lógica del framework (tramos, game state, orientación, Voronoi recortado).
- Antes de cambios grandes, propone el plan y los archivos que tocarás.
- Samuel corre la descarga en su laptop con sus credenciales; tú escribes y revisas el código.
- Commits pequeños y descriptivos; nunca subir datos ni salidas con datos crudos.
- Equipo: Samuel (alias **chamuel**) y Héctor (alias **Tilin**). Todos siguen `contexto/flujo_trabajo.md`: tamaño de la tarea, 5 fases (entender, planear, criterios de calidad, ejecutar, revisar), día a día y trabajo en paralelo.
- Comentarios en código y documentación con la simbología de `contexto/flujo_trabajo.md`, sección 7: `NOTAn`, `OBSn`, `REFn`, `IMPORn`, `TODOn`, `FIXn`, `HACKn`, `PERFn`, `DEPRECn`, numerados por archivo. Todo `TODOn` y `HACKn` se anota también en **Por hacer** de la bitácora.
- Bitácora `CAMBIOS/` (solo en la rama `tests`): un archivo por día, `C##_ddmm.md` (reglas en `CAMBIOS/README.md`), con Planeado, Hecho, Por hacer, Propuestas y quién hizo el cambio. Al terminar un trabajo, actualiza el archivo del día con el alias de quien lo pidió y "(con Claude Code)".
- Ramas: `tests` = TESTS (trabajo diario, incluye `CAMBIOS/`); `main` = FINAL (solo lo confirmado, sin `CAMBIOS/`). A `main` se llega solo por PR desde una rama `promocion/ddmm` que excluye `CAMBIOS/` (`contexto/flujo_trabajo.md`, sección 5); nunca commits directos ni PR directo `tests → main`.
- Dos sesiones de Claude Code: la local (en la laptop) corre scripts y notebooks; la de la nube mantiene y revisa el repo. `git pull` antes de empezar en cualquiera.

## Estado actual (actualizar al avanzar)

- [x] Convocatoria analizada, propuesta base y framework v0 escritos.
- [x] Repo privado creado y estructura definida (ver `README.md`).
- [x] Entorno instalado en la laptop de Samuel (`python -m pytest` pasa).
- [x] Prueba de humo de la API (`scripts/00_prueba_humo.py`): ids en `config/params.yaml`, diferencias en `contexto/api/matches.md`.
- [x] Inspector de contenido (`scripts/01_inspector.py`, 9 oct): Phases of Play poblado en todos los torneos (82–88 % del juego abierto), 360 en 79–94 % de los eventos con área visible siempre, 11.6–16.2 jugadores visibles, orientación OK. Reporte en `reports/inspeccion_api.md`.
- [x] Descarga completa con caché (`scripts/02_descarga.py`, 12 oct): 2,557 solicitudes, 0 fallidas, 253 MB. Procesado (`03_procesar.py`): 707,900 eventos de 213 partidos del América, 627,130 frames 360 (212 partidos) y estadísticas de equipo de los 1,701 partidos de la liga.
- [x] Capa de datos (`ojo.datos`: crudo → tablas → parquet + DuckDB; `scripts/03_procesar.py`).
- [x] Framework base en código (`ojo.framework`: partidos válidos, torneo, del equipo, relevos, tramos, marcador, orientación, juego abierto, recuperaciones).
- [x] Lente Voronoi + grafo de vecindad (`ojo.lentes.voronoi`, `scripts/04_voronoi.py`) y figuras con la identidad (`ojo.salidas`).
- [x] Lectura por puntos de quiebre (12 oct): `ojo.framework.quiebres` (quiebres, ventanas, controles), panel por minuto a dos bandas con forma del bloque y red por posición (`ojo.lentes.minuto`, `forma`, `redes`; `scripts/05_panel.py`), criterio de hallazgo (`ojo.lentes.hallazgo`), notebooks 02 (quiebres) y 03 (estilo y tabla final) y el Voronoi paso a paso (`ojo.salidas.paso_a_paso`, `scripts/06_paso_a_paso.py`). Voronoi sigue como lente estructural por la regla fijada.
- [x] Maqueta 3 (14 oct): narrativa principio → caso confirmador (final AP23, roja a Fulgencio), índice Proactivo–Reactivo por minuto (`ojo.lentes.indice`, confirmado con PCA el 18 oct), reproductor minuto a minuto con Voronoi (`ojo.salidas.reproductor`) y Monte Carlo explicativo (`ojo.lentes.simulacion`). La página es la plantilla `app/maqueta.html` (+ `app.css`, `app.js`); `scripts/08_maqueta.py` solo escribe `outputs/app/datos.js`. Barra lateral v3: compacta, plegable y ocultable. Voronoi en movimiento en las jugadas (seguimiento estimado, `ojo.lentes.seguimiento`; Voronoi recalculado en el navegador). Auditoría del 14 oct en `auditoria/`. Auditoría visual del 16 oct implementada el 17 oct: `app/movimiento.js` (`OjoMov`), barra en tres variantes (por defecto `riel` desde el 18 oct: el contenido se ajusta; la barra v5 deja solo el rival, con los 17 de las fichas, y lleva a su ficha de 10 segundos) y opciones `?sin-intro`, `?barra=` y `?movimiento=reducido` (`app/README.md`).
- [x] Cierre (18 oct, con la rúbrica oficial; plan en `contexto/plan_cierre.md`):
  - **Criterio v2** (`ojo.lentes.hallazgo`): escala de los controles, FDR y placebo. El placebo pasa de 11 a 0 de 280 y la tabla final de 69 a 30 de 636.
  - **Índice confirmado con PCA** (r = 0.94 con los pesos iguales).
  - **PPDA y altura de recuperación** (`ojo.lentes.defensa`).
  - **Balón parado y uso de jugadores** (notebook 04).
  - **Matriz de situaciones** (notebook 05).
  - **Fichas de 10 segundos** (`ojo.lentes.rivales`, `ojo.salidas.decision`).
  - **Validación en el CL26** (notebook 06): ningún principio se invierte.
  - **3 casos de decisión** (notebook 07).
  - **Vistas Plan de juego y Método** en la app (desde el 18 oct las vistas se llaman Resumen, El partido, Plan de juego y Método; términos para el jurado en `contexto/terminologia.md`).
  - **HTML único** (`scripts/09_entrega.py`) y guion del video (`contexto/guion_video.md`).
  - Principios v2: sale jugando corto · con uno más, hunde al rival · una lesión no lo frena · tras recibir gol, el rival no lo aprieta · alerta: cambiar el sistema le cuesta · refresca las bandas.
- [ ] Pendiente de chamuel:
  - grabar el video;
  - prueba de 90 segundos con alguien externo;
  - V-M14 (descargar Poppins);
  - promoción a `main`;
  - correo de entrega.

Preguntas abiertas (la rúbrica oficial y el HTML único ya están confirmados): ¿cómo se plantean los coach drills?, ¿la elección de Jardine es libre?, ¿límites de consumo de la API?, ¿los organizadores aceptan datos de AP25–CL26? (la convocatoria habla de AP21–CL25, al parecer heredado de ediciones anteriores; se usan, con plan B listo), ¿cómo evalúan "la herramienta cambia una decisión real"?, ¿qué implica la nota de que no se necesita programación avanzada? Samuel envía el correo a los organizadores el 8 de octubre.

## Documentos (léelos solo cuando la tarea lo pida)

- `contexto/flujo_trabajo.md`: cómo trabajamos en equipo: fases, día a día, ramas y promoción a `main`, commits y simbología de comentarios.
- `branding/README.md`: identidad (colores, Poppins, logos), animación de entrada (5 s, cada vez que se abre el archivo) e ícono en loop; cómo usarlos y reconstruirlos. Toda salida visual (reporte, figuras, video, presentación) usa la **paleta azulcrema, definitiva desde el 14 oct**: cancha y fondos azul `#0F1D41`, América crema `#F0EB9A`, rival blanco y rojo `#F6303E` solo en acentos puntuales. Desde el 18 oct la placa del logotipo en la app también es azulcrema (crema con letras azul club); solo el ojo conserva el azul y el dorado de la marca.
- `CAMBIOS/` (rama `tests`): bitácora diaria; lee el último archivo para saber qué se hizo y qué quedó pendiente.
- `contexto/plan_cierre.md`: plan del cierre (18 oct): validación en el CL26, casos de decisión, vista Método, guion y verificación, con riesgos y criterios de calidad.
- `contexto/guion_video.md`: guion del video de 5 minutos y la prueba de 90 segundos.
- `contexto/terminologia.md`: cada término de la página, qué significa y cómo traducirlo para el jurado (decisiones de chamuel).
- `contexto/resumenes.md`: contrato de `resumenes.json`, el único archivo de datos del explorador (barra lateral rival · torneo · situación). Solo agregados; validador en `ojo.salidas.resumenes`.

- `contexto/propuesta_base.md`: objetivo, objetivos específicos, lectura a dos bandas, comparaciones, entregables, calendario y riesgos.
- `contexto/framework.md`: definiciones de objetos, contexto, supuestos, límites y propuesta de `params.yaml`.
- `README.md`: estructura del repo, instalación y reglas de la estructura (capas, acceso único a datos).
- `contexto/plan_trabajo.md`: ecosistema, decisiones de estructura, cliente de la API, prueba de humo, inspector, descarga, orden de construcción.
- `contexto/api/README.md`: índice de las 10 APIs con endpoints y qué archivo leer para cada tarea.
- `contexto/api/*.md`: referencia condensada de cada API (campos, tipos, catálogos de ids).

## Glosario rápido

- **Dos bandas**: leer cada métrica del América junto a la del rival en el mismo tramo del partido (diferencial América − rival).
- **Tramo**: ventana de minutos dentro de un periodo (15 por defecto).
- **Efecto América**: cómo cambia un rival al enfrentar al América frente a su promedio del torneo.
- **Huella de pases**: vector de frecuencias de los 60 `pass_cluster_id` por partido.
- **Ficha de 10 segundos**: tarjeta por rival con cómo progresa, dónde concede, quién participa poco, su balón parado vulnerable y cómo respondió Jardine ante rivales parecidos.
- **Coach drill**: prueba del jurado; resuelve 3 escenarios de decisión en menos de 90 s usando nuestro reporte.
- **Matriz de situaciones**: tabla situación de juego → qué hace Jardine, qué le funciona, recomendación, enlace a evidencia.
