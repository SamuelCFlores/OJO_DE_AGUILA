# `contexto/api/` · retirado temporalmente del repositorio

> Retirado el 21 de octubre de 2026 por las reglas de seguridad de la competencia: los datos de StatsBomb y su documentación son solo para el Hackathon ISAC 2026. Esta carpeta era un resumen, escrito por el equipo, de la documentación de las APIs de StatsBomb. Como deriva de material del proveedor, sale del repositorio mientras se confirma con los organizadores qué se puede compartir. El equipo la conserva en sus copias locales (fuera de git) y la puede mostrar a los organizadores si la piden.

## Qué contenía

Once archivos de Markdown, uno por API más un índice. Cada uno resumía campos, tipos y catálogos de ids, con las diferencias que encontramos entre la documentación y la API real.

| Archivo | Qué resumía |
| --- | --- |
| `README.md` | Índice de las 10 APIs: acceso (versiones y dominios de los endpoints) y qué archivo leer para cada tarea |
| `competitions.md` | Competitions: competiciones y temporadas disponibles |
| `matches.md` | Matches: partidos, equipos, entrenadores, etapas y estado de la recolección de datos |
| `events.md` | Events: campos de cada evento y catálogos de tipos (pases, tiros, faltas, sustituciones, patrones de juego…) |
| `frames_360.md` | 360 Frames: área que ve la cámara y posiciones de los jugadores en cada foto |
| `lineups.md` | Lineups: jugadores, posiciones por tramo del partido y tarjetas |
| `player_mapping.md` | Player Mapping: identificadores de jugadores por competición, temporada y equipo |
| `player_match_stats.md`, `player_season_stats.md` | Estadísticas de jugador por partido y por temporada |
| `team_match_stats.md`, `team_season_stats.md` | Estadísticas de equipo por partido y por temporada |

## Para qué se usaba

- **Regla de trabajo:** antes de usar un campo de la API se revisaba aquí (`CLAUDE.md`, regla 5: "No inventes campos").
- **Referencias del código:** varios módulos la citan en sus comentarios (por ejemplo, `src/ojo/framework/juego.py` → `events.md`). Esas referencias se quedan como están: apuntan a esta nota mientras la carpeta esté fuera.
- **Diferencias con la API real:** lo que encontraron `scripts/00_prueba_humo.py` y `scripts/01_inspector.py` se anotaba aquí, junto al campo.

## Cómo vuelve

Si los organizadores confirman que se puede compartir, se restaura desde las copias locales del equipo y se quita la regla de `.gitignore`.
