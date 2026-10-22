# Ojo de Águila

Motor analítico reutilizable sobre las APIs de StatsBomb (Liga MX, Apertura 2021 – Clausura 2026). Primer caso: el América de André Jardine (Apertura 2023 – Clausura 2026), para el Hackathon ISAC 2026 con el Club América.

**¿Eres del jurado?** Empieza por la [documentación del proyecto](DOCUMENTACION.md): materiales entregados, recorrido sugerido, metodología, resultados, limitaciones, reproducibilidad y registro de cambios.

Repositorio privado. Los datos de StatsBomb son solo para la competencia: aquí se versiona código y resultados, **nunca datos ni credenciales**. Contexto completo en [`CLAUDE.md`](CLAUDE.md) y [`contexto/`](contexto/).

## Instalación (Windows, PowerShell, Python 3.13)

Desde la raíz del repo:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1          # si falla: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python -m pip install -r requirements.txt
nbstripout --install                # una vez por clon: guarda los notebooks sin salidas
Copy-Item .env.example .env         # y llena tus credenciales de StatsBomb en .env
```

`requirements.txt` instala también el paquete `ojo` en modo editable, así que scripts y notebooks hacen `from ojo...` sin tocar `sys.path`.

Verificación: `python -m pytest` debe pasar completo.

## Del dato a la figura

Los scripts se corren en orden; todos son incrementales (lo ya hecho se salta) y los que tocan la API usan el cliente con caché.

| Paso | Comando | Red | Qué hace |
| --- | --- | --- | --- |
| 0 | `python scripts/00_prueba_humo.py` | Sí | Credenciales, ids reales y estructura de las APIs |
| 1 | `python scripts/01_inspector.py` | Sí (muestra) | Cobertura por torneo (Phases of Play, 360, OBV…) → `reports/inspeccion_api.md` |
| 2 | `python scripts/02_descarga.py --plan` y luego sin `--plan` | Sí | Descarga completa: liga (Team Match Stats) y partidos del equipo (Events, 360, Lineups) |
| 3 | `python scripts/03_procesar.py` | No | Caché cruda → parquet en `data/processed/` |
| 4 | `python scripts/04_voronoi.py --procesos 4` | No | Control territorial y grafo de vecindad por evento → `outputs/voronoi/` |
| 5 | `python scripts/05_panel.py --procesos 4` | No | Panel por minuto a dos bandas, red de pases por posición y forma del bloque → `outputs/panel/` |
| 6 | `python scripts/06_paso_a_paso.py --listar --quiebre sustitucion_tactica_propia` y luego el comando que imprime | No | El Voronoi de una jugada real paso a paso → `outputs/reportes/voronoi_paso_a_paso.html` (también `--partido MATCH_ID`) |
| 7 | `python scripts/07_caso.py --partido 3886547 --tipo expulsion_contra` | No | **Histórica** (maqueta 2, no se edita): caso puntual leído hasta un quiebre → `outputs/reportes/maqueta_2.html` |
| 8 | `python scripts/08_maqueta.py --partido 3918375 --tipo expulsion_favor` | No | Datos de la **maqueta definitiva** → `outputs/app/datos.js`; la página es `app/maqueta.html` (diseño editable a mano, ver `app/README.md`) |
| 9 | `python scripts/09_entrega.py` | No | **Entrega**: un solo HTML autocontenido con la maqueta, sus estilos, scripts, marca y datos → `outputs/entrega/ojo_de_aguila.html` (abre con doble clic; lleva datos reales, no se sube) |
| 10 | `python scripts/10_guia.py` | No | Documentación del proyecto: `DOCUMENTACION.md` → `outputs/entrega/Ojo_de_Aguila_documentacion.pdf` (con Chrome, sin instalar nada) |

Pasos 0–2 los corre quien tenga credenciales (Samuel). Del 3 en adelante cualquiera con la caché. Después de agregar una columna a `ojo.datos.tablas`: `python scripts/03_procesar.py --rehacer eventos`.

Los modelos y las pruebas de hipótesis viven en notebooks:

| Notebook | Qué hace |
| --- | --- |
| `01_voronoi_exploracion` | Corte del Voronoi |
| `02_puntos_de_quiebre` | Antes/después de cada quiebre, con controles, criterio v2 y placebo |
| `03_barrido_estilo` | Estilo frente a la liga y tabla final de hallazgos |
| `04_balon_parado_y_jugadores` | Componentes obligatorios: balón parado y uso de jugadores |
| `05_matriz_de_situaciones` | Qué hace Jardine en cada situación y qué le funciona |
| `06_validacion_cl26` | Única apertura del torneo de prueba |
| `07_casos_cl26` | Tres casos de decisión elegidos por regla |

Se corren en orden; el 07 necesita antes `08_maqueta.py` (las fichas).

## Créditos, terceros y uso de IA

- **Datos:** Hudl StatsBomb, Liga MX (Apertura 2021 – Clausura 2026), entregados para el Hackathon ISAC 2026. Solo para la competencia: no se versionan ni se publican. Del proveedor se usan tal cual xG, OBV, Phases of Play y los 60 `pass_cluster`; el índice de iniciativa, el Voronoi recortado, los quiebres, el criterio de hallazgo (los 4 parámetros), la matriz y la lectura del motor son nuestros (`contexto/framework.md`).
- **IA generativa** (detalle en [`contexto/uso_ia.md`](contexto/uso_ia.md)): usamos Claude Code (Anthropic) como asistente de programación. Escribió y revisó buena parte del código (`src/ojo`, `scripts`, `app/`), ayudó a redactar documentación y textos de la página, y armó la animación del video, la alineación de las voces y su exportación. Las preguntas, definiciones, umbrales (`config/params.yaml`), reglas de decisión e interpretación las fijó el equipo; cada número sale del código con pruebas (`python -m pytest`). Las voces del video son del equipo, no sintéticas. Las instrucciones que le dimos están en `CLAUDE.md` y el trabajo de cada día, en la bitácora `CAMBIOS/` (rama `tests`).
- **Software libre:** las librerías de `requirements.txt` (pandas, NumPy, SciPy, Shapely, NetworkX, mplsoccer, Matplotlib, scikit-learn, statsmodels, DuckDB, PyArrow, requests, python-dotenv, PyYAML, tqdm, pytest, nbstripout); React en la animación de la marca (`branding/dist/vendor`); tipografía Poppins (Google Fonts, SIL Open Font License).
- **Métodos de la literatura:** diagramas de Voronoi, bootstrap por partidos, Benjamini–Hochberg (1995) para FDR, diferencia en diferencias y PCA.
- **Fotos del video:** fotos de prensa usadas solo como ilustración; sus derechos son de sus autores.

## Entrega

| Qué | Dónde |
| --- | --- |
| Reporte y app (un solo HTML) | `python scripts/09_entrega.py` → `outputs/entrega/ojo_de_aguila.html` (doble clic) y `outputs/publicar/index.html` (lo que se aloja en Netlify) |
| Video (máximo 5 minutos) | Guion en `contexto/guion_video.md`; el MP4 se arma fuera del repo |
| Términos para el jurado | `contexto/terminologia.md` |
| Documentación del proyecto | [`DOCUMENTACION.md`](DOCUMENTACION.md) y su PDF (`python scripts/10_guia.py`) |

## Equipo y forma de trabajo

Samuel de María Cabrera Flores (**chamuel**) y Héctor Cortés Pérez (**Tilin**), con apoyo de Claude Code. Todos seguimos [`contexto/flujo_trabajo.md`](contexto/flujo_trabajo.md): tamaño de la tarea, 5 fases, día a día, ramas, commits y simbología de comentarios (`NOTAn`, `OBSn`, `REFn`, `IMPORn`, `TODOn`, `FIXn`, `HACKn`, `PERFn`, `DEPRECn`).

Lo que hace cada quien se documenta en la bitácora `CAMBIOS/` (solo en la rama `tests`), un archivo por día: `C##_ddmm.md`.

## Ramas: TESTS y FINAL

| Rama | Papel | Cómo se actualiza |
| --- | --- | --- |
| `tests` | **TESTS**: trabajo diario, incluye la bitácora `CAMBIOS/` | Commits directos o PR desde ramas de trabajo (`chamuel/<tema>`, `tilin/<tema>`) |
| `main` | **FINAL**: solo cambios confirmados, sin `CAMBIOS/` | Únicamente por PR desde una rama `promocion/ddmm` (ver `contexto/flujo_trabajo.md`, sección 5) |

Si algo en `tests` deja de funcionar, `main` sigue intacto y se puede volver a él (`git switch main`). Se trabaja siempre en `tests`:

```powershell
git switch tests
git pull                            # antes de empezar, para traer lo último
```

## Estructura

```
OJO_DE_AGUILA/
├── CLAUDE.md                 # contexto y reglas para Claude Code
├── CAMBIOS/                  # bitácora del equipo, C##_ddmm.md (solo en la rama tests)
├── app/                      # la página (reporte + app): maqueta.html, app.css, app.js, movimiento.js; Python solo escribe sus datos (ver app/README.md)
├── branding/                 # identidad: logos, animación de entrada, ícono en loop (ver branding/README.md)
├── auditoria/                # auditorías del proyecto (14 y 19 oct) y lo que se corrigió
├── .github/workflows/        # guardia: un PR a main no puede traer CAMBIOS/
├── README.md
├── pyproject.toml            # metadatos del paquete `ojo` (sin dependencias)
├── requirements.txt          # dependencias con versión fija + `-e .`
├── .gitignore                # data/, outputs/, .env y formatos de datos en todo el repo
├── .gitattributes            # finales de línea y filtro nbstripout
├── .env.example              # plantilla vacía de credenciales
├── config/
│   └── params.yaml           # TODOS los umbrales del framework (nada de números mágicos)
├── contexto/                 # contexto del proyecto (lo lee Claude Code y el equipo)
│   ├── propuesta_base.md     # qué y por qué
│   ├── framework.md          # definiciones de cada objeto y métrica
│   ├── plan_trabajo.md       # cómo se construye
│   ├── flujo_trabajo.md      # cómo trabajamos: fases, ramas, commits, simbología
│   ├── plan_cierre.md        # plan del cierre (validación, casos, método, video)
│   ├── terminologia.md       # cada término de la página y cómo se le dice al jurado
│   ├── guion_video.md        # guion del video a dos voces
│   ├── resumenes.md          # contrato de datos del explorador
│   ├── uso_ia.md             # uso de IA generativa: qué hizo, qué decidió el equipo y cómo se verificó
│   └── api/                  # resumen de las 10 APIs de StatsBomb: fuera del repo por las reglas de la competencia (ver api/REMOVIDO.md)
├── src/ojo/                  # el motor: todo el código reutilizable
│   ├── ingesta/              # capa 1 · cliente con caché + un módulo por API
│   ├── datos/                # JSON crudo → parquet; único punto de lectura de data/
│   ├── framework/            # capa 2 · definiciones de contexto/framework.md
│   ├── lentes/               # capa 3 · proveedor, redes, huella, Voronoi, dos bandas, contexto, comparaciones
│   └── salidas/              # capa 4 · figuras, datos de la página, partido clave, matriz y lectura del motor (ficha)
├── scripts/                  # puntos de entrada numerados, del 00_prueba_humo.py al 09_entrega.py (tabla de arriba)
├── notebooks/                # exploración numerada (NN_tema.ipynb); solo llaman a src/ojo
├── reports/                  # resúmenes revisados, sin datos crudos (la entrega es un HTML único: scripts/09_entrega.py)
├── tests/
│   └── fixtures/             # datos SINTÉTICOS hechos a mano, nunca datos reales
│
│   — solo en local, fuera de git —
├── data/
│   ├── raw/{api}/v{n}/       # JSON gzip tal como llega de la API (caché)
│   └── processed/            # parquet normalizados
└── outputs/                  # todo lo generado: hallazgos, datos de la página (app/datos.js), entrega/ y publicar/
```

## Reglas de la estructura

1. **Las capas van en un solo sentido:** `ingesta → datos → framework → lentes → salidas`. Una capa nunca importa a una posterior.
2. **Un solo acceso a la red y a los datos:** solo `ojo.ingesta` llama a la API y solo `ojo.datos` lee `data/`. Scripts y notebooks piden tablas a `ojo.datos`.
3. **Nada específico del caso en el código:** ids de equipo, entrenador y temporadas salen de `config/params.yaml`; cambiar el parámetro cambia el caso.
4. **Scripts y notebooks son delgados:** orquestan y exploran; la lógica que sirva dos veces se mueve a `src/ojo/`.
5. **Pruebas sin datos reales:** `tests/` usa fixtures sintéticas, así cualquiera las corre sin credenciales ni descarga.
6. **Lo generado no se versiona:** va a `outputs/`. Un resultado se comparte a propósito, nunca por accidente.
7. **La página se diseña a mano y se alimenta de datos:** `app/` es HTML, CSS y JS editables; `scripts/08_maqueta.py` solo escribe `outputs/app/datos.js` y `scripts/09_entrega.py` los junta en un solo HTML.
8. **Cada métrica tiene una definición y un umbral:** la definición en `contexto/framework.md`, el umbral en `config/params.yaml` y la prueba en `tests/`.
