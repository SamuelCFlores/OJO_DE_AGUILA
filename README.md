# Ojo de Águila

Motor analítico reutilizable sobre las APIs de StatsBomb (Liga MX, Apertura 2021 – Clausura 2026). Primer caso: el América de André Jardine (Apertura 2023 – Clausura 2026), para el Hackathon ISAC 2026 con el Club América.

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
| 7 | `python scripts/07_caso.py --partido 3886547 --tipo expulsion_contra` | No | Caso puntual leído hasta un quiebre (línea de tiempo a dos bandas, jugada con Voronoi, protagonista) → `outputs/reportes/maqueta_2.html` |

Pasos 0–2 los corre quien tenga credenciales (Samuel). Del 3 en adelante cualquiera con la caché. Después de agregar una columna a `ojo.datos.tablas`: `python scripts/03_procesar.py --rehacer eventos`.

Los modelos y las pruebas de hipótesis viven en notebooks: `01_voronoi_exploracion` (corte del Voronoi), `02_puntos_de_quiebre` (antes/después de cada quiebre, con controles) y `03_barrido_estilo` (estilo frente a la liga y tabla final de hallazgos).

## Equipo y forma de trabajo

Samuel (**chamuel**) y Héctor (**Tilin**), con apoyo de Claude Code. Todos seguimos [`contexto/flujo_trabajo.md`](contexto/flujo_trabajo.md): tamaño de la tarea, 5 fases, día a día, ramas, commits y simbología de comentarios (`NOTAn`, `OBSn`, `REFn`, `IMPORn`, `TODOn`, `FIXn`, `HACKn`, `PERFn`, `DEPRECn`).

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
├── branding/                 # identidad: logos, animación de entrada, ícono en loop (ver branding/README.md)
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
│   └── api/                  # referencia condensada de las 10 APIs
├── src/ojo/                  # el motor: todo el código reutilizable
│   ├── ingesta/              # capa 1 · cliente con caché + un módulo por API
│   ├── datos/                # JSON crudo → parquet; único punto de lectura de data/
│   ├── framework/            # capa 2 · definiciones de contexto/framework.md
│   ├── lentes/               # capa 3 · proveedor, redes, huella, Voronoi, dos bandas, contexto, comparaciones
│   └── salidas/              # capa 4 · figuras, tablas del reporte, ficha de 10 segundos
├── scripts/                  # puntos de entrada numerados: 00_prueba_humo.py, 01_inspector.py, 02_descarga.py…
├── notebooks/                # exploración numerada (NN_tema.ipynb); solo llaman a src/ojo
├── reports/                  # fuentes Quarto (.qmd) y resúmenes revisados, sin datos crudos
├── tests/
│   └── fixtures/             # datos SINTÉTICOS hechos a mano, nunca datos reales
│
│   — solo en local, fuera de git —
├── data/
│   ├── raw/{api}/v{n}/       # JSON gzip tal como llega de la API (caché)
│   └── processed/            # parquet normalizados
└── outputs/                  # todo lo generado: figuras, HTML, tablas
```

## Reglas de la estructura

1. **Las capas van en un solo sentido:** `ingesta → datos → framework → lentes → salidas`. Una capa nunca importa a una posterior.
2. **Un solo acceso a la red y a los datos:** solo `ojo.ingesta` llama a la API y solo `ojo.datos` lee `data/`. Scripts y notebooks piden tablas a `ojo.datos`.
3. **Nada específico del caso en el código:** ids de equipo, entrenador y temporadas salen de `config/params.yaml`; cambiar el parámetro cambia el caso.
4. **Scripts y notebooks son delgados:** orquestan y exploran; la lógica que sirva dos veces se mueve a `src/ojo/`.
5. **Pruebas sin datos reales:** `tests/` usa fixtures sintéticas, así cualquiera las corre sin credenciales ni descarga.
6. **Lo generado no se versiona:** va a `outputs/`. Un resultado se comparte a propósito, nunca por accidente.
