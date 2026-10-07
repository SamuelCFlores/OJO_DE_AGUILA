# Plan de trabajo técnico

Cómo se construye Ojo de Águila. El qué y el porqué están en `docs/propuesta_base.md`; las definiciones, en `docs/framework.md`.

## Ecosistema

| Capa | Herramienta | Por qué |
| --- | --- | --- |
| Sistema | Windows (laptop de Samuel), PowerShell | Donde corre todo |
| Lenguaje | Python 3.12 | Todas las librerías tienen versión para Windows |
| Entorno | `venv` + `requirements.txt` con versiones fijas | Mismo entorno para todo el equipo sin herramientas extra |
| Editor | VS Code + Jupyter | Notebooks para explorar; el código reutilizable vive en `src/` |
| Ingesta | `requests` + `python-dotenv` | Cliente propio (statsbombpy probablemente no cubre Events v11 ni 360 v2) |
| Almacenamiento | JSON crudo (gzip) → parquet con `pandas` + `pyarrow` | Se descarga una vez y se consulta rápido |
| Consultas | DuckDB | SQL directo sobre parquet |
| Geometría y grafos | `scipy`, `shapely`, `networkx` | Voronoi, recortes, redes |
| Visualización | `mplsoccer` + `matplotlib` | Canchas y redes |
| Modelos | `scikit-learn`, `statsmodels` | Perfiles, clustering, contexto |
| Reporte | Quarto (HTML autocontenido) | Se instala la segunda semana |
| Versiones | GitHub privado + `nbstripout` | Código sí, datos nunca |

Comandos base (PowerShell):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1          # si falla: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python -m pip install -r requirements.txt
nbstripout --install
```

## Estructura del repositorio (propuesta, pendiente de confirmar)

```
ojo-de-aguila/
├── CLAUDE.md
├── README.md
├── .gitignore            # data/, .env, *.parquet, .venv/
├── .env.example          # STATSBOMB_USER=, STATSBOMB_PASSWORD= (sin valores)
├── requirements.txt
├── config/params.yaml    # todos los umbrales del framework
├── docs/                 # propuesta, framework, plan, referencias de API
├── data/                 # nunca en git
│   ├── raw/{api}/...     # JSON tal como llega (gzip)
│   └── processed/        # parquet limpios
├── src/ojo/
│   ├── ingest/           # client.py + un módulo por API
│   ├── framework.py      # posesiones, fases, transiciones, tramos, contexto
│   ├── metrics/          # proveedor, grafos, voronoi, huella, dos_bandas, balon_parado
│   ├── models/           # contexto, sustituciones, validacion
│   ├── simulation.py
│   └── viz/
├── scripts/              # 00_prueba_humo.py, 01_inspector.py, 02_descarga.py, ...
├── notebooks/            # exploración numerada
├── reports/              # informe.qmd y salidas sin datos crudos
└── tests/
```

## Cliente de la API (`src/ojo/ingest/client.py`)

- Credenciales desde `.env` (`STATSBOMB_USER`, `STATSBOMB_PASSWORD`); nunca en código, logs ni salidas.
- Autenticación: HTTP Basic (supuesto; confirmar en la prueba de humo).
- Caché en disco: la ruta depende de la API y sus parámetros; si el archivo existe, no se hace la solicitud. Opción `force` para volver a bajar un partido actualizado (`last_updated` en Matches).
- Pausa configurable entre solicitudes (1 s por defecto) y reintentos con espera creciente ante 429 y 5xx; no reintentar 401/403.
- Prueba ambos dominios (`data.statsbombservices.com` y `data.statsbomb.com`) y recuerda cuál respondió para cada endpoint.
- Versiones de API en un solo lugar (diccionario o `params.yaml`).
- Registro de cada solicitud: endpoint, estado, bytes, si vino de caché (sin credenciales).

## Prueba de humo (`scripts/00_prueba_humo.py`, la corre Samuel)

1. Competitions → filas de Liga MX con `competition_id`, `season_id`, `season_name` y fechas de 360.
2. Matches de un torneo de Jardine → partidos del América con fecha, rival, localía, entrenador de ambos, `collection_status`, `match_status_360`.
3. Para un partido de Jardine con 360: Events v11, 360 v2, Lineups v5, Team Match Stats v4 y Player Match Stats v8.
4. Imprime solo conteos y nombres de campos, nunca filas de datos.

## Inspector (`scripts/01_inspector.py`)

Genera `reports/inspeccion_api.md` con resúmenes, sin filas de datos:

- por API: campos, tipos, % de presencia y valores posibles de cada categoría;
- si Phases of Play viene poblado (porcentaje de eventos de juego abierto con `control_degree`);
- porcentaje de eventos con frame 360 y con `visible_area`; jugadores visibles promedio;
- presencia de OBV, xG, `pass_cluster_id` y `pass_success_probability`;
- formaciones y motivos de cambio en Lineups;
- tamaño por partido, para estimar el total de la descarga;
- verificación de la orientación de coordenadas (supuesto del framework).

## Descarga completa (`scripts/02_descarga.py`, la corre Samuel)

1. Competitions y Matches de los 8 torneos de Liga MX.
2. Team Season Stats de los 8 torneos y Team Match Stats de toda la liga en los torneos necesarios (línea base y efecto América).
3. Detalle de los ~160 partidos del América (Jardine y predecesores): Events, 360, Lineups, Player Match Stats.
4. Player Season Stats de esos torneos. Player Mapping solo si hace falta.

## Criterios de calidad de la fase de datos

- La prueba de humo baja las 5 APIs de un partido sin errores.
- Una segunda ejecución no hace ninguna solicitud: todo sale de la caché.
- `git status` nunca muestra `data/` ni `.env`.
- Lista confirmada de partidos de Jardine y sus predecesores, con estado 360.
- Cualquiera del equipo reproduce el entorno con 3 comandos.

## Orden de construcción después de la ingesta

1. `framework.py` y `params.yaml` con valores confirmados.
2. Perfil por partido (Team Match Stats) y percentiles contra la liga.
3. Lentes: redes por posición, huella de pases, Voronoi (regla de corte el 14 de octubre).
4. Lectura a dos bandas por tramo y efecto América.
5. Contexto, comparaciones (predecesores, liga, cambio de entrenador) y validación temporal.
6. Balón parado y simulación Monte Carlo de xG (posesiones agrupadas, 10,000 repeticiones).
7. Ficha de 10 segundos y reporte en Quarto.

## Riesgos técnicos

| Riesgo | Mitigación |
| --- | --- |
| Credenciales en el repo | `.env` en `.gitignore`; el código nunca las imprime |
| Exceder límites de consumo | Caché, pausa entre solicitudes, reintentos con espera creciente |
| Phases of Play vacío en partidos históricos | Plan B de transición en `params.yaml` |
| Partidos sin 360 o recolección incompleta | Se registran y se excluyen solo de las métricas 360 |
| Windows: activación del venv, rutas con acentos u OneDrive | `Set-ExecutionPolicy`; proyecto fuera de OneDrive o `data/` excluida de la sincronización |
| Nombres de campos distintos a la documentación | El inspector compara contra `docs/api/` y reporta diferencias |
