# Ojo de Águila · Guía para el jurado

**Hackathon ISAC 2026 · Club América · "La historia de un entrenador a través de los datos"**\
Equipo: Samuel de María Cabrera Flores y Héctor Cortés Pérez

> Esta guía explica qué entregamos, cómo recorrerlo en cinco minutos y de dónde sale cada número. No hace falta instalar nada: todo se ve en el navegador.

## 1. Qué es, en 30 segundos

Ojo de Águila es un motor analítico reutilizable sobre los datos de StatsBomb de la Liga MX. Convierte la idea de juego de un entrenador en evidencia y en decisiones. Su primer caso es **André Jardine en el América** (Apertura 2023 – Clausura 2026), comparado con sus antecesores, Solari y Ortiz, y con cada rival en el mismo minuto.

La tesis: **propone más que sus rivales, sale jugando corto y, cuando el partido se rompe, se instala arriba.**

## 2. Qué entregamos

| Entregable | Dónde | Para qué |
| --- | --- | --- |
| **Página** (reporte y app en uno) | https://ojodeaguila.netlify.app/ · también el archivo `ojo_de_aguila.html`, que abre con doble clic | El reporte completo, en cuatro vistas |
| **Video** (3:55) | Enlace de YouTube en el formulario | La historia en menos de 5 minutos |
| **Código** | https://github.com/SamuelCFlores/OJO_DE_AGUILA (rama `main`) | Revisión de integridad |
| **Esta guía** | PDF y `DOCUMENTACION.md` en el repositorio | Cómo recorrer lo anterior |

## 3. Cómo recorrer la página en cinco minutos

Al abrirla corre una animación de entrada de 5 segundos («Saltar» la omite). Arriba están las cuatro vistas.

1. **Resumen** (1 min). La tesis, el índice de iniciativa por torneo, los seis principios y una foto real del caso: el mapa de control del espacio con la lectura del juego hasta ese momento.
2. **El partido** (2 min). La final del Apertura 2023 contra Tigres, minuto a minuto.
   - Con ▶ se reproduce: la cancha, el índice de los dos equipos y los eventos (goles, cambios, faltas, tiros de esquina, saques).
   - Pausa en la expulsión (79') y prueba las jugadas animadas.
   - Al final está «¿Qué tan merecido?», una simulación con los tiros del partido.
   - En la barra de la izquierda, elige otro rival: aparece su partido clave con Jardine (16 rivales).
3. **Plan de juego** (1 min).
   - La matriz de situaciones (14 tarjetas: marcador, jugadores de más o de menos, local o visitante, liguilla, cierre del partido).
   - Qué dice nuestro motor de cada rival.
   - Balón parado, uso de jugadores y tres casos del Clausura 2026.
4. **Método** (1 min). Datos, cómo se lee un partido, los 4 parámetros y la prueba en falso, los principios con su evidencia, la validación, los límites, el glosario (42 términos), lo que sigue y los créditos.

## 4. Tres decisiones en 90 segundos

| Si el cuerpo técnico pregunta… | Dónde está la respuesta | Qué dice |
| --- | --- | --- |
| «Vamos 1-0 al minuto 60» | Plan de juego → matriz → **Ganando por 1** | Parejo: el balance de ocasiones deja de ser claro. Hipótesis a probar: sostener la iniciativa |
| «Mañana jugamos contra Pumas» | Barra de rivales → **Pumas UNAM** → «Ver la lectura del motor» | Cómo progresa, cómo defiende, dónde concede, su balón parado y cómo le fue a Jardine contra rivales parecidos |
| «Nos expulsaron a uno» | Plan de juego → matriz → **Con uno menos** | Replegarse es lo esperado y el partido se sostiene parejo (muestra chica) |

Las recomendaciones salen de reglas fijas sobre los números y son hipótesis, no órdenes.

## 5. El método en una página

**Datos.** Hudl StatsBomb, Liga MX del Apertura 2021 al Clausura 2026: estadísticas de equipo de 1,701 partidos de la liga, y eventos y fotos de posiciones (360) de los partidos del América.

| Grupo | Partidos | Torneos |
| --- | --- | --- |
| Jardine | 110 | AP23 a AP25 |
| Solari y Ortiz | 82 | AP21 a CL23 |
| Torneo reservado | 19 | CL26, abierto una sola vez al final |

**Mediciones propias.**
- **Índice de iniciativa:** ocho señales por minuto con el mismo peso, de 0 (espera) a 100 (propone). La comprobación con PCA coincide en 0.94 con los pesos iguales.
- **Mapa de control del espacio:** Voronoi sobre cada foto 360, recortado a lo que ve la cámara y a 18 m por jugador.
- **Momentos clave:** goles, expulsiones, cambios de sistema y sustituciones. Cada uno se compara con tramos de otros partidos donde no pasó nada (cambio neto, o diferencia en diferencias).

**Cuándo algo es un hallazgo: los 4 parámetros.**
1. **Claro:** el rango probable (95 %, por remuestreo de partidos) no cruza el cero.
2. **Grande:** al menos media variación típica.
3. **Constante:** misma dirección en al menos 4 de los 5 torneos de Jardine.
4. **A prueba de suerte:** riesgo de falso hallazgo de 10 % o menos (Benjamini–Hochberg).

En la prueba en falso, sobre 280 momentos inventados, los 4 parámetros no aprueban ninguno. De 636 pruebas sobreviven 30.

**Los seis principios** (Jardine frente a Solari y Ortiz).

| Principio | Jardine | Solari y Ortiz | En el CL26 |
| --- | --- | --- | --- |
| Sale jugando corto (largo de pase) | 18.7 m | 20.1 m | ✓ se sostiene |
| Con uno más, hunde al rival (cambio de altura del rival) | −15.1 m | +2.7 m | — sin muestra suficiente |
| Una lesión no lo frena (presiones) | +5.6 cada 10 min | −4.2 cada 10 min | ≈ misma dirección |
| Tras recibir gol, el rival no lo aprieta | −1.3 cada 10 min | +1.3 cada 10 min | ≈ misma dirección |
| Alerta: cambiar el sistema le cuesta (xG) | −0.03 cada 10 min | +0.17 cada 10 min | ✓ se sostiene |
| Refresca las bandas (cambios tácticos de defensas) | 1.15 por partido | 0.43 por partido | ≈ misma dirección |

En el torneo reservado, ningún principio salió al revés.

**Lo que no decimos.** Comparamos, no probamos causas. Expulsiones, lesiones y cambios de sistema son pocos por torneo. La cámara de las fotos 360 solo ve una parte de la cancha.

## 6. Datos, terceros y uso de IA

- **Datos:** Hudl StatsBomb, solo para la competencia. No se publican ni están en el repositorio. El resumen que hicimos de su documentación también se retiró (`contexto/api/REMOVIDO.md`).
- **Del proveedor, tal cual:** goles esperados (xG), valor de cada acción (OBV), fases de juego y tipos de pase. Lo demás es cálculo nuestro.
- **IA generativa:** usamos Claude Code (Anthropic) como asistente de programación. Escribió y revisó buena parte del código, ayudó a redactar textos y armó la animación y la exportación del video. Las preguntas, definiciones, umbrales, reglas e interpretación las fijó el equipo, y cada número lo calcula el código, con pruebas. Las voces del video son nuestras. Detalle en `contexto/uso_ia.md` y en la página (Método, sección 10).
- **Software libre:** Python (pandas, NumPy, SciPy, Shapely, NetworkX, mplsoccer, scikit-learn, statsmodels, DuckDB y otras), React y la tipografía Poppins.
- **Fotos del video:** fotos de prensa usadas solo como ilustración; sus derechos son de sus autores.

## 7. Cómo revisar el código

| Qué | Dónde |
| --- | --- |
| El motor, por capas (ingesta → datos → framework → lentes → salidas) | `src/ojo/` |
| Los pasos, del dato a la página | `scripts/00_prueba_humo.py` … `scripts/09_entrega.py` |
| Pruebas de hipótesis (quiebres, estilo, balón parado, matriz, validación, casos) | `notebooks/02` … `notebooks/07`, sin salidas |
| Todos los umbrales (nada fijo en el código) | `config/params.yaml` |
| La definición de cada métrica | `contexto/framework.md` |
| La página (HTML, CSS y JS) | `app/` |
| Pruebas automáticas, sin datos reales | `tests/` (`python -m pytest`: 146 pruebas) |
| Historial de cambios y bitácora diaria | commits de `main` y `tests` · `CAMBIOS/` en la rama `tests` |

Para reproducir las cifras se necesitan credenciales de StatsBomb; las reglas de la competencia no permiten compartir los datos. Las pruebas automáticas corren sin datos. Instalación y orden de los pasos en el `README.md`.
