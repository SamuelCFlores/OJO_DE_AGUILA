# app/: la página de Ojo de Águila (maqueta definitiva)

**Esta es la maqueta definitiva desde el 18 oct: todo cambio visual se hace aquí.** Las anteriores (maqueta 2 de `scripts/07_caso.py` y los `outputs/reportes/maqueta_*.html`) quedan como históricas y no se editan.

El **diseño** vive aquí y se edita directo; los **datos** los genera Python y nunca entran a git.

| Archivo | Qué es | ¿Se edita a mano? | ¿En git? |
| --- | --- | --- | --- |
| `maqueta.html` | Estructura y textos fijos (títulos, pilares, avisos). Los datos llegan a los elementos con `data-slot` | Sí | Sí |
| `app.css` | Estilos. Paleta azulcrema (definitiva, 14 oct) tomada de `branding/tokens.css` | Sí | Sí |
| `app.js` | Dibuja todo con los datos: portada, barra lateral, Voronoi, reproductor, radar, Monte Carlo | Sí | Sí |
| `movimiento.js` | Biblioteca de movimiento `window.OjoMov` (se carga antes de `app.js`); sus tokens `--dur-*` están al final de `app.css` | Sí | Sí |
| `../outputs/app/datos.js` | `window.OJO_DATOS = {...}`, escrito por `scripts/08_maqueta.py` | No | **No** (datos reales) |

## Cómo verla

```powershell
python scripts/08_maqueta.py --partido 3918375 --tipo expulsion_favor   # escribe outputs/app/datos.js
```

Después abre `app/maqueta.html` (doble clic) o, con el servidor `maqueta-marca` de `.claude/launch.json`, `http://localhost:8765/app/maqueta.html`. Sin `datos.js`, la página muestra cómo generarlo. La entrada animada y el ícono salen de `branding/dist`.

Para cambiar el diseño no hace falta Python: edita `maqueta.html`, `app.css` o `app.js` y recarga. Python solo se corre de nuevo si cambian los datos (otro partido, otro quiebre o el pipeline).

Opciones en la dirección (para revisar y grabar):

| Opción | Qué hace |
| --- | --- |
| `?sin-intro` | No muestra la entrada animada (sin la opción, se ve una vez por sesión del navegador) |
| `?barra=sobre`, `riel` o `chips` | Variante de la barra lateral (por defecto `sobre`; también `data-barra-variante` en el `<body>`) |
| `?movimiento=reducido` | Simula `prefers-reduced-motion`: nada se anima y todo queda en su estado final |

## Contrato de `datos.js`

Lo valida `ojo.salidas.datos_app.validar` (claves obligatorias y JSON válido). Primer nivel:

| Clave | Contenido |
| --- | --- |
| `meta` | Fecha de generación, partido, tipo de quiebre y aviso de datos |
| `titulo`, `equipo`, `rival`, `nuevo` | Textos generales (`nuevo` = entrenador del caso: Jardine) |
| `portada` | `kpis` [{etq, valor, detalle}], `torneos` [{torneo, entrenador, propio, rival, nuevo}], `principios` [tarjetas], `ejemplo` {texto, foto, que_muestra} |
| `explorar` | `antetitulo`, `filtros`, `principio` (tarjeta grande), `caso` {titulo, chips, quiebres}, `montecarlo` [...], `simulaciones` (repeticiones del Monte Carlo), `lectura`, `metodo`, `que_muestra`, `pendientes`, `notas` |
| `barra` | Barra compacta (ver `contexto/barra_lateral.md`, versión 3): `rival`, `rivales`, `torneos`, `momento`, `condicion`, `partidos`, `mas`, `muestra` |
| `reproductor` | `componentes`, `minutos` (índice, z, valores y marcador por minuto), `fotos` (Voronoi por minuto), `quiebres`, `etiquetasX`, `jugadas` [{titulo, fotos, minuto}], `animacion` {escala, duracion, pausa_foto, alcance, cuartos_circulo}, `bandas` (40/60 del índice), `inicio` |

Una **foto** (`ojo.salidas.reproductor.foto`) trae celdas y a quién pertenecen, frontera, área visible, jugadores `[x, y, propio, actor]`, la flecha del pase o la conducción y el control, siempre con el América atacando hacia la derecha. En las **jugadas** cada foto agrega `t` (segundos), `ids` (pista estimada de cada jugador, `ojo.lentes.seguimiento`) y `nombre` (quien ejecuta, de Events + Lineups).

**Voronoi en movimiento.** En las jugadas, `app.js` interpola las posiciones entre fotos y recalcula el Voronoi en cada cuadro con las mismas reglas que Python (cancha ∩ área visible ∩ alcance); en las fotos reales da el mismo control que `ojo.lentes.voronoi` (verificado: 6 de 6 fotos iguales). Los jugadores que entran o salen de cámara aparecen y desaparecen con un fundido. Las posiciones entre fotos son estimadas y la página lo dice. En el modo minuto a minuto (fotos a 60 s) no se inventa movimiento: hay un fundido entre fotos.

**Movimiento (auditoría visual del 16 oct).** Lo que se mueve ayuda a leer un dato o a seguir la historia; lo demás no se anima.

- Entre minutos hay un fundido real (`OjoMov.cruce`).
- En las jugadas, el movimiento entre fotos es lineal. Hay una pausa en cada foto real, con la insignia "Foto real" (o "Estimado" entre fotos) y un anillo en quien ejecuta.
- La línea del índice se dibuja hasta el cursor y marca cada quiebre al cruzarlo.
- El radar se transforma y sigue visible al reproducir.
- La insignia del caso lleva al partido y lo resalta.
- El Monte Carlo se reparte la primera vez que se ve, los KPI cuentan una vez y la portada pasa a Explorar con un fundido.
- Duraciones: `--dur-rapida` 150 ms, `--dur-media` 280 ms y `--dur-lenta` 600 ms; con movimiento reducido valen 0.
- Cada animación tiene un temporizador de respaldo: aunque la pestaña esté oculta, el estado final siempre llega.

## Reglas

- Nada de datos en `app/`: si un número o una posición sale del partido, va en `datos.js`.
- Las bandas del índice y las repeticiones del Monte Carlo llegan en `datos.js` desde `config/params.yaml`. `app.js` solo guarda un respaldo de 40/60 por si `datos.js` es anterior al 17 oct.
- La placa del logotipo conserva el azul y el dorado de la marca; todo lo demás usa la paleta azulcrema.
