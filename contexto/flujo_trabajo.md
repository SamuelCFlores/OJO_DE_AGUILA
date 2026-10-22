# Flujo de trabajo

Cómo trabajamos en Ojo de Águila. Aplica a las personas del equipo y a Claude Code por igual.

| Alias | Nombre | Rol |
| --- | --- | --- |
| chamuel | Samuel de María Cabrera Flores | Responsable del proyecto; corre la descarga con sus credenciales |
| Tilin | Héctor | Colaborador |

Claude Code apoya a los dos: escribe y revisa código, y sigue este mismo flujo.

## 1. Tamaño de la tarea

Antes de empezar, decide qué tan grande es la tarea. No conviertas una tarea simple en un proceso largo.

| Tamaño | Ejemplos | Qué se hace |
| --- | --- | --- |
| Simple | Corregir un typo, cambiar un umbral en `params.yaml`, responder una duda | Directo: qué pasa, qué hacer, cómo verificar |
| Mediana | Una métrica nueva, un ajuste a una lente, una figura del reporte | Objetivo, plan corto y riesgos; luego ejecutar y verificar |
| Compleja | Una lente completa (Voronoi), la descarga completa, la validación del CL26, el reporte | Las 5 fases completas (sección 2) |

## 2. Las 5 fases (tareas medianas y complejas)

### Fase 1 · Entender

- Qué se quiere conseguir y qué resultado se espera ver.
- Quién lo va a usar: el jurado, el cuerpo técnico o el equipo.
- Restricciones: reglas no negociables de `CLAUDE.md`, tiempo, datos disponibles, compatibilidad con Windows.
- Qué falta. Si falta algo sin lo cual el resultado puede salir mal, se pregunta antes de seguir. Si es menor, se supone y se marca: `[Supuesto: ...]`.

### Fase 2 · Planear

- Qué archivos se tocan y por qué.
- Orden de construcción y dependencias (las capas van en un solo sentido: `ingesta → datos → framework → lentes → salidas`).
- Decisiones importantes, riesgos previsibles y casos límite (partidos sin 360, Phases of Play vacío, tiempo añadido, expulsiones).
- El plan se anota en la sección **Planeado** del archivo del día en `CAMBIOS/`.

### Fase 3 · Criterios de calidad

- Qué debe funcionar sí o sí y qué prueba lo demuestra (`tests/`, con fixtures sintéticas).
- Qué errores hay que evitar: números mágicos, campos inventados, datos crudos en salidas, fuga de información hacia el Clausura 2026.
- Qué haría que el resultado se considere incompleto.

### Fase 4 · Ejecutar

- Se sigue el plan; no se agregan funciones que nadie pidió ni se cambia el objetivo.
- La solución más simple que cumpla. Sin sobreingeniería y sin dejar funciones críticas a medias.
- Cada métrica sale de `contexto/framework.md` y cada umbral de `config/params.yaml`.
- Los comentarios usan la simbología de la sección 7.
- Commits pequeños y descriptivos (sección 6).

### Fase 5 · Revisar

- **Contra lo pedido:** ¿cumple todo?, ¿falta algo?, ¿se agregó algo innecesario?, ¿quedó un caso límite sin cubrir?
- **De calidad:** ¿es claro?, ¿es robusto?, ¿se puede reutilizar para otro equipo cambiando solo `params.yaml`?
- `python -m pytest` pasa completo.
- `git status` no muestra nada de `data/`, `.env`, `logs/` ni salidas con datos.
- Se actualiza el archivo del día en `CAMBIOS/`: **Hecho**, **Por hacer** y **Propuestas**.

## 3. El día a día

**Al empezar**

```powershell
git switch tests
git pull
.venv\Scripts\Activate.ps1
```

Lee el último archivo de `CAMBIOS/` para saber qué hizo el otro y qué quedó pendiente. Si el archivo del día no existe, créalo desde `CAMBIOS/PLANTILLA.md` y anota en **Planeado** en qué vas a trabajar.

**Al terminar**

```powershell
python -m pytest
git status                          # nada de data/, .env ni logs/
git add <archivos>
git commit -m "área: qué cambió"
git pull                            # trae lo del otro antes de subir
git push
```

## 4. Trabajar en paralelo sin pisarse

- En **Planeado** cada quien anota los archivos que va a tocar. Si los dos necesitan el mismo archivo, se ponen de acuerdo antes.
- En el archivo del día, cada quien escribe en sus propias viñetas, marcadas con su alias (`[chamuel]`, `[Tilin]`). Así hay menos conflictos al hacer `git pull`.
- Cambios pequeños van directo a `tests`. Los grandes (una lente nueva, un cambio de estructura) van en una rama de trabajo, `chamuel/<tema>` o `tilin/<tema>`, y entran a `tests` por PR para que el otro lo revise.
- Si `git pull` marca conflicto, se resuelve a mano conservando el trabajo de los dos; si hay duda, se pregunta antes de borrar algo.
- Cada quien usa su propio `.env`. Las credenciales nunca se comparten por chat ni se suben a git.

## 5. Ramas: TESTS y FINAL

| Rama | Papel | Qué contiene |
| --- | --- | --- |
| `tests` | **TESTS**: trabajo diario | Todo, incluida la bitácora `CAMBIOS/` |
| `main` | **FINAL**: solo lo confirmado | Todo **menos** `CAMBIOS/` |

Nunca se hacen commits directos a `main`. Para pasar a `main` lo que ya se confirmó en `tests` (pruebas pasan y se verificó en la laptop), se usa una rama de promoción que excluye `CAMBIOS/`:

```powershell
git fetch origin
git switch -c promocion/ddmm origin/main
git restore --source=origin/tests --staged --worktree -- . ":(exclude)CAMBIOS"
git commit -m "promoción: tests → main (dd/mm)"
git push -u origin promocion/ddmm
gh pr create --base main --head promocion/ddmm --title "Promoción dd/mm" --body "Qué se confirma y cómo se probó"
```

Por qué así: un PR directo `tests → main` llevaría `CAMBIOS/` a `main`. La rama de promoción parte de `main` y toma de `tests` todo lo demás, así que `main` nunca recibe la bitácora y `tests` nunca la pierde.

Como respaldo, la acción `.github/workflows/main_sin_cambios.yml` hace fallar cualquier PR hacia `main` que traiga `CAMBIOS/`.

## 6. Commits

- Formato: `área: qué cambió`, en español. Áreas: `ingesta`, `datos`, `framework`, `lentes`, `salidas`, `scripts`, `docs`, `tests`, `entorno`, `cambios`.
- Un cambio lógico por commit. Nunca datos, credenciales ni salidas con datos crudos.
- Ejemplo: `lentes: Voronoi recortado a visible_area con exclusión por borde`.

## 7. Simbología de comentarios

Para código y documentación. Cada etiqueta se numera dentro de su archivo (`NOTA1`, `NOTA2`…), va en mayúsculas y termina en dos puntos.

| Etiqueta | Cuándo se usa | Ejemplo en este proyecto |
| --- | --- | --- |
| `NOTAn` | Información general, contexto y condiciones de uso | `# NOTA1: Solo vale para partidos con match_status_360 = available.` |
| `OBSn` | Comportamientos extraños, dependencias invisibles o advertencias estructurales | `# OBS1: Matches trae el entrenador en home_team.managers, no en home_team_manager como dice la documentación.` |
| `REFn` | Enlaces a documentación externa, tickets o fuentes | `# REF1: Definición de PPDA en contexto/api/team_match_stats.md.` |
| `IMPORn` | Advertencias críticas, reglas estrictas o seguridad | `# IMPOR1: No imprimir filas crudas: regla no negociable 1 de CLAUDE.md.` |
| `TODOn` | Tareas pendientes, mejoras futuras o deuda técnica reconocida | `# TODO1: Recalcular la fuerza del rival solo con partidos anteriores.` |
| `FIXn` | Explicación de un parche aplicado para resolver un bug específico | `# FIX1: Se filtra competition_gender = male porque "liga mx" también encontraba la Femenil.` |
| `HACKn` | Soluciones temporales, poco elegantes o forzadas | `# HACK1: Se toma el torneo de la fecha porque algunas fases no traen prefijo Apertura/Clausura.` |
| `PERFn` | Código hecho así por rendimiento; no tocar por estética | `# PERF1: Se lee el parquet por columnas para no cargar los ~2,800 eventos completos de cada partido.` |
| `DEPRECn` | Código obsoleto que no debe usarse y se eliminará | `# DEPREC1: Usar ojo.lentes.voronoi.control_recortado; esta función se borra al cerrar el pilar 1.` |

**Cómo se escribe según el tipo de archivo**

- Python: `# NOTA1: ...` en la línea anterior al código que explica. Los docstrings siguen siendo docstrings; las etiquetas no los reemplazan.
- YAML (`params.yaml`): `# NOTA1: ...` junto a la clave.
- Markdown, visible para el lector: `> **NOTA1:** ...`
- Markdown, solo para el equipo: `<!-- NOTA1: ... -->`

**Reglas**

- Todo `TODOn` y todo `HACKn` se anota también en **Por hacer** del archivo del día, para que no se pierda.
- Un `DEPRECn` dice qué usar en su lugar.
- Un `IMPORn` cita la regla que protege (de `CLAUDE.md` o de `framework.md`).
- Para encontrar todas las etiquetas pendientes:

```powershell
git grep -nE "(TODO|HACK|FIX|DEPREC)[0-9]+:"
```

## 8. Bitácora `CAMBIOS/`

Vive solo en la rama `tests`. Un archivo por día con lo planeado, lo hecho, lo pendiente, las propuestas y quién lo hizo. Las reglas completas están en `CAMBIOS/README.md` (en la rama `tests`).
