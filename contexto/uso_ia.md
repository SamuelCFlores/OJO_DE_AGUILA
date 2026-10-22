# Uso de IA generativa en Ojo de Águila

> Las reglas del Hackathon ISAC 2026 permiten la IA generativa siempre que se documente con transparencia. Aquí está qué usamos, para qué, qué decidió el equipo y cómo se verificó. Versión corta en la página (Método, sección 10) y en el `README.md`.

## Herramienta

- **Claude Code** (Anthropic), asistente de programación, con dos sesiones:
  - una local, en la laptop de Samuel, que corre scripts y notebooks;
  - una en la nube, que mantiene y revisa el repositorio.
- Las instrucciones permanentes que le dimos están en [`CLAUDE.md`](../CLAUDE.md): reglas de datos y credenciales, coherencia con `framework.md` y `params.yaml`, no inventar campos y honestidad analítica.

## Qué hizo la IA

- **Código:** escribió y revisó buena parte del motor (`src/ojo`), los scripts del 00 al 09, las pruebas (`tests/`) y la página (`app/`).
- **Corridas:** ejecutó los scripts y notebooks en la laptop del equipo y reportó los resultados. Las cifras de la página salen del código, no las escribió la IA.
- **Documentación y textos:** redactó y ordenó documentos de `contexto/`, el `README.md`, la bitácora y los textos de la página, a partir de lo que pidió el equipo y con los nombres de [`terminologia.md`](terminologia.md).
- **Video:**
  - armó la animación (animatic en HTML) a partir del guion del equipo;
  - recortó el fondo de las fotos;
  - alineó las voces grabadas con los subtítulos;
  - exportó el MP4 con Chrome y herramientas de Windows, sin instalar programas.

## Qué decidió el equipo

- La pregunta, el entrenador y las comparaciones (Solari y Ortiz, el rival en el mismo minuto, la liga).
- El criterio de hallazgo y sus umbrales (`config/params.yaml`), fijados antes de ver los resultados.
- Qué principios entran, las reglas de las recomendaciones y la regla del partido clave de cada rival.
- Los nombres que ve el jurado, el guion del video y el diseño final de la página.
- Todo lo que se publica o se entrega.
- Las voces del video son de Samuel de María Cabrera Flores y Héctor Cortés Pérez; ninguna es sintética.
- La descarga de datos se hizo con las credenciales de Samuel en su laptop; la IA no ve ni guarda credenciales (`.env` está fuera de git).

## Cómo se verificó

- **Pruebas automáticas:** `python -m pytest`, con datos sintéticos (`tests/fixtures`).
- **Método a prueba de sesgos:** criterio fijado antes de ver resultados, prueba en falso (placebo) y un torneo reservado, el Clausura 2026, abierto una sola vez.
- **Rastro de cada cambio:** cada tarea queda en la bitácora `CAMBIOS/` (rama `tests`) con "(con Claude Code)", y los commits hechos con la IA llevan la línea `Co-Authored-By`.
- **Revisión visual:** la página y el video se revisaron en el navegador antes de cada entrega.

## Límites

La IA puede equivocarse. Por eso los números salen de código con pruebas, las definiciones viven en `contexto/framework.md` y las recomendaciones se presentan como hipótesis, no como órdenes.
