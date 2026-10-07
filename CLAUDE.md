# Ojo de Águila — contexto para Claude Code

Proyecto de Samuel de María Cabrera Flores (Ingeniería en Ciencia de Datos, BUAP) para el Hackathon ISAC 2026 con el Club América: "La Historia de un Entrenador a través de los Datos". Responde siempre en español.

## Qué construimos

Un **motor analítico reutilizable** sobre las APIs de StatsBomb (Liga MX, Apertura 2021 – Clausura 2026) y su primer caso: **el América de André Jardine** (Apertura 2023 – Clausura 2026).

Objetivo: explicar los principios de juego de Jardine, qué tan estables son, cómo interactúan con lo que hace el rival a lo largo del mismo partido, cómo los ajusta según marcador, localía, rival y momento, y en qué se distinguen de sus predecesores y del resto de la Liga MX, de forma que un cuerpo técnico lo entienda sin ver un solo video.

Entregables (22 de octubre de 2026): reporte HTML en Quarto, video de máximo 5 minutos y una "ficha de 10 segundos" por rival. Finalistas: presentación de 10 diapositivas (11 de noviembre).

## Decisiones tomadas

- Entrenador: André Jardine. Comparaciones: el rival en el mismo partido ("lectura a dos bandas"), sus predecesores en el América (Solari y Ortiz, confirmados en Matches). Entrenadores del análisis: solo Solari, Ortiz y Jardine (ids en `config/params.yaml`); quedan fuera Diego Cervantes (interino, 2 partidos en enero de 2025) y Jorge Almada (sucesor, 2026/27), la Liga MX y el cambio de entrenador CL23 → AP23 como experimento natural.
- Lentes propias: control territorial con Voronoi (360), redes de pases por posición (no por jugador), huella de pases (60 clusters de StatsBomb). Además, métricas del proveedor: xG, OBV, PPDA, Phases of Play.
- Regla del framework: si StatsBomb define un objeto, se adopta; si no, se define en `contexto/framework.md`. Todos los umbrales viven en `config/params.yaml`.
- Tiempo real: solo visión a futuro. Nada en vivo, sin video ni tracking durante el hackathon.
- Regla de corte: si el 14 de octubre Voronoi no da hallazgos claros, pasa a lente de apoyo.
- Rúbrica: nos apegamos a la tabla de evaluación publicada (predictiva 30 %, causal 25 %, interpretabilidad 25 %, valor operativo 20 %) y el objetivo se adapta a ella (supuesto hasta que los organizadores confirmen). La interpretabilidad se cubre con la capa "Decide en 90 segundos" (`contexto/propuesta_base.md`).
- Predicción y decisión: entrenamiento AP23–AP25, prueba en el Clausura 2026 (intocable hasta la evaluación final, sin fuga de información). El valor operativo ("la herramienta cambia una decisión real") se demuestra con casos de decisión del CL26 frente a lo que recomendaba la herramienta con datos previos. Monte Carlo: resultado merecido (descriptivo) y rangos de incertidumbre (predictivo), nunca mezclados. Voronoi es eje central, recortado a `visible_area`.

## Reglas no negociables

1. **Datos**: solo para la competencia; se publican resultados, nunca datos. `data/` y `.env` jamás entran a git. No imprimas filas de datos crudos en salidas que se vayan a compartir.
2. **Credenciales**: solo en `.env` (`STATSBOMB_USER`, `STATSBOMB_PASSWORD`). Nunca en código, logs, notebooks ni mensajes. Si las ves, no las repitas.
3. **Consumo de la API**: todo pasa por el cliente con caché; nunca descargar dos veces lo mismo; pausa entre solicitudes y reintentos con espera creciente (429/5xx).
4. **Coherencia**: cada métrica sale de una definición de `contexto/framework.md` y de un umbral de `config/params.yaml`. Sin números mágicos en el código.
5. **No inventes campos**: antes de usar un campo de la API, revísalo en `contexto/api/`. Si un campo real difiere de la documentación, avísalo y anótalo.
6. **Honestidad analítica**: separa correlación de causalidad; marca supuestos; no presentes la visión a futuro como algo construido.

## Entorno

- Windows + PowerShell, Python 3.13, `venv`, `requirements.txt` con versiones fijas, VS Code + Jupyter.
- Librerías: requests, python-dotenv, pandas, pyarrow, duckdb, numpy, scipy, shapely, networkx, mplsoccer, matplotlib, scikit-learn, statsmodels, pyyaml, tqdm, nbstripout. Quarto después.
- Rutas con `pathlib`; nada de rutas absolutas ni separadores fijos. Cuidado con OneDrive y rutas con acentos.
- Clon local de Samuel: `C:\Users\samue\OneDrive\Documentos\PROYECTOS\C_AMERICA`. Está bajo la carpeta de OneDrive pero la sincronización no está activa (todo queda en local); si se activa, excluir `data/` y `.venv/`.
- Activar el entorno: `.venv\Scripts\Activate.ps1` (si falla: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`).

## Cómo trabajar

- El código reutilizable va en `src/ojo/`; los notebooks son solo exploración y llaman a `src/`.
- Funciones pequeñas con docstring en español, tipadas, sin efectos ocultos. Identificadores en español o inglés sin acentos, de forma consistente dentro de cada módulo.
- Cada script nuevo trae instrucciones para probarlo; agrega pruebas en `tests/` para la lógica del framework (tramos, game state, orientación, Voronoi recortado).
- Antes de cambios grandes, propone el plan y los archivos que tocarás.
- Samuel corre la descarga en su laptop con sus credenciales; tú escribes y revisas el código.
- Commits pequeños y descriptivos; nunca subir datos ni salidas con datos crudos.
- Ramas: `tests` = TESTS (trabajo diario, se actualiza constantemente); `main` = FINAL (solo cambios confirmados, únicamente por PR `tests → main`). Nunca commits directos a `main`.
- Dos sesiones de Claude Code: la local (en la laptop) corre scripts y notebooks; la de la nube mantiene y revisa el repo. `git pull` antes de empezar en cualquiera.

## Estado actual (actualizar al avanzar)

- [x] Convocatoria analizada, propuesta base y framework v0 escritos.
- [x] Repo privado creado y estructura definida (ver `README.md`).
- [x] Entorno instalado en la laptop de Samuel (`python -m pytest` pasa).
- [x] Prueba de humo de la API (`scripts/00_prueba_humo.py`): ids en `config/params.yaml`, diferencias en `contexto/api/matches.md`.
- [ ] Inspector de contenido (`scripts/01_inspector.py`) y ajustes al framework.
- [ ] Descarga completa con caché.
- [ ] Framework en código, métricas, lentes, dos bandas, contexto, simulación, ficha, reporte, video.

Preguntas abiertas: ¿los organizadores confirman que la tabla de evaluación aplica a este reto?, ¿cómo se plantean los coach drills?, ¿la elección de Jardine es libre?, ¿Phases of Play viene poblado en 2023–2025? (en un partido de 2026 `control_degree` aparece en el 83.8 % de eventos; falta revisar temporadas anteriores en el inspector), ¿límites de consumo de la API?, ¿los organizadores aceptan datos de AP25–CL26? (la convocatoria habla de AP21–CL25, pero la API los entrega)
## Documentos (léelos solo cuando la tarea lo pida)

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
