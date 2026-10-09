# Identidad de Ojo de Águila

Ojo de Águila se presenta como un producto: tiene logo, colores, tipografía, una animación de entrada y un ícono animado. El logo es un iris hecho con un Voronoi de jugadores, el mismo lenguaje con que se muestran los datos.

El diseño se hizo en Claude Design; aquí está su fuente y la versión lista para usar en el reporte.

## Identidad

| Token | Valor | Uso |
| --- | --- | --- |
| `--oda-azul` | `#0B2545` | Fondo de marca, encabezado, cancha en las figuras |
| `--oda-dorado` | `#E8B100` | Acento; el América en las figuras |
| `--oda-blanco` | `#FFFFFF` | Texto sobre azul; el rival en las figuras |
| `--oda-gris-fondo` | `#EEF0F3` | Fondo de páginas claras |
| `--oda-gris-texto` | `#4A5B70` | Texto secundario |
| `--oda-fuente` | Poppins (500 y 700 incrustadas; 400 y 600 desde Google Fonts) | Todo el texto |

Los tokens viven en `tokens.css` y se copian a `dist/marca.css` al construir.

## Archivos

| Ruta | Qué es | ¿Se versiona? |
| --- | --- | --- |
| `fuente/` | Proyecto de Claude Design descomprimido: animaciones (`*.jsx`), logos (`marca-2a/`), keyframes | Sí, menos `uploads/` y `scraps/` |
| `fuente/marca-2a/` | Logos listos: isotipo (color, fondo oscuro, monocromo), favicon, horizontal, apilado, con lema | Sí |
| `exportados/` | Exportaciones HTML de Claude Design del video y del loop; de aquí salen React, Babel y Poppins al construir | No (solo local) |
| `anfitrion.js` | Reproductor propio: reloj sin controles, una vez o en bucle | Sí |
| `tokens.css` | Colores y tipografía | Sí |
| `construir_marca.py` | Compila las animaciones y genera `dist/` | Sí |
| `dist/` | `marca.js`, `marca.css` y React 18.3.1: lo que usan el reporte y la maqueta | Sí |
| `maqueta.html` | Maqueta de la experiencia: entrada, encabezado con loop y una figura con la identidad | Sí |

## Cómo se comporta la entrada

1. La primera vez que se abre el reporte, la animación "Mirada de rapaz" ocupa la pantalla: los jugadores forman el iris Voronoi, el ojo se abre, mira, escanea y forma el logotipo.
2. Dura 5 s (diseñada en 10 s y acelerada sin tocar el diseño). Al terminar se desvanece y queda el contenido.
3. No se vuelve a mostrar en ese navegador (`localStorage`, clave `ojo-de-aguila:intro-vista`). Con `#intro` al final de la dirección se fuerza para demostrarla.
4. Un clic, Esc, Enter o Espacio la saltan. Si el sistema tiene activado "reducir movimiento", no se muestra y el ícono queda quieto.
5. El ícono del encabezado (mirar, parpadear, escanear) se repite cada 6 s.

Uso en cualquier página:

```html
<link rel="stylesheet" href="dist/marca.css">
<script src="dist/vendor/react.production.min.js"></script>
<script src="dist/vendor/react-dom.production.min.js"></script>
<script src="dist/marca.js"></script>
<script>
  OjoMarca.intro(contenedor, { segundos: 5, alTerminar: function () { /* desvanecer */ } });
  OjoMarca.loop(contenedorIcono);                 // { estatico: true } para el ojo quieto
</script>
```

## Cómo verla

Desde la raíz del repo:

```powershell
python -m http.server 8765
```

y abre `http://localhost:8765/branding/maqueta.html#intro`. La figura de la maqueta usa datos reales y se genera en local (`outputs/poc/voronoi_marca.png`); sin ella aparece un aviso.

## Cómo reconstruir si cambia el diseño

1. En Claude Design, exporta de nuevo el proyecto (zip) y descomprímelo en `fuente/`; exporta el video como HTML a `exportados/intro_mirada_rapaz.html`.
2. Desde la raíz del repo, con Node.js instalado:

```powershell
python branding/construir_marca.py
```

3. Abre la maqueta y revisa la entrada y el loop.
