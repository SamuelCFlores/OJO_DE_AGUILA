# Ojo de Águila

Motor analítico reutilizable sobre las APIs de StatsBomb (Liga MX, Apertura 2021 – Clausura 2025). Primer caso: el América de André Jardine (Apertura 2023 – Clausura 2025), para el Hackathon ISAC 2026 con el Club América.

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

## Estructura

```
OJO_DE_AGUILA/
├── CLAUDE.md                 # contexto y reglas para Claude Code
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
