# CAMBIOS: bitácora del equipo

Aquí documentamos lo que hace cada quien en el código y la documentación. Esta carpeta vive **solo en la rama `tests`**: nunca pasa a `main` (ver `contexto/flujo_trabajo.md`, sección 5).

## Nombre de los archivos

`C##_ddmm.md`

| Parte | Significado | Ejemplo |
| --- | --- | --- |
| `C##` | Número de cambio, consecutivo y con dos dígitos | `C01`, `C02`… `C10` |
| `ddmm` | Día y mes en que se hizo | `0810` = 8 de octubre |

Ejemplo: `C01_0810.md` = cambio 1, del 8 de octubre de 2026.

- Todo lo que se hizo en un día se escribe en el mismo archivo.
- Un día nuevo abre el número siguiente.
- Solo si en un mismo día hay un cambio grande y separado del resto (por ejemplo, una lente completa), se abre otro archivo con el número siguiente y la misma fecha. Por defecto, un archivo por día.
- La fecha va completa dentro del archivo, en el título.

## Secciones de cada archivo

Se copia `PLANTILLA.md`. Todo puede cambiar.

1. **Planeado:** qué se iba a hacer ese día y qué archivos se iban a tocar.
2. **Hecho:** qué se hizo de verdad, con el commit cuando aplica.
3. **Por hacer:** lo que quedó pendiente, como casillas `- [ ]`. Incluye cada `TODOn` y `HACKn` que se haya dejado en el código.
4. **Propuestas:** ideas para discutir; no son decisiones.
5. **Quién hizo el cambio:** alias de cada persona y qué hizo.

Cada viñeta lleva el alias de quien la escribe, para que los dos puedan escribir en el mismo archivo sin pisarse.

## Alias

| Alias | Nombre |
| --- | --- |
| chamuel | Samuel |
| Tilin | Héctor |

Si Claude Code hizo o ayudó en el cambio, se agrega `(con Claude Code)` junto al alias de quien lo pidió.
