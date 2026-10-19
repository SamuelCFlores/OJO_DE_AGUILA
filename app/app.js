/* Ojo de Águila · lógica de la app (app/maqueta.html). Se edita directo: Python no genera este archivo.
   Lee window.OJO_DATOS (../outputs/app/datos.js, escrito por scripts/08_maqueta.py) y dibuja las cuatro vistas:
   Resumen (portada), El partido (explorar, con la barra lateral y el reproductor), Plan de juego (decidir) y Método.
   Los nombres para el jurado siguen contexto/terminologia.md; los ids internos (portada, explorar, decidir) no cambian.
   NOTA1: maqueta. Los controles de la barra cambian de estado pero todavía no recalculan la vista. */
(function () {
  'use strict';
  var D = window.OJO_DATOS;
  var NS = 'http://www.w3.org/2000/svg';
  var BANDAS = (D && D.reproductor && D.reproductor.bandas) || [40, 60];  // indice.bandas de config/params.yaml (vía datos.js): bajo 40 reactivo, sobre 60 proactivo
  var cuerpo = document.body;
  var MOV = window.OjoMov || null;  // biblioteca de movimiento (movimiento.js); sin ella todo funciona sin animar
  function reducido() { return MOV ? MOV.reducido() : window.matchMedia('(prefers-reduced-motion: reduce)').matches; }
  function movil() { return window.matchMedia('(max-width: 900px)').matches; }

  // ---------- utilidades ----------
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function slots(nombre) { return document.querySelectorAll('[data-slot="' + nombre + '"]'); }
  function html(nombre, valor) { slots(nombre).forEach(function (n) { n.innerHTML = valor; }); }
  function texto(nombre, valor) { slots(nombre).forEach(function (n) { n.textContent = valor; }); }
  function el(tag, attrs, padre) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (padre) padre.appendChild(e);
    return e;
  }
  function pares(plano) { var s = []; for (var k = 0; k < plano.length; k += 2) s.push(plano[k] + ',' + plano[k + 1]); return s.join(' '); }
  function pct(v) { return Math.round(v * 100) + ' %'; }
  // Texto de las gráficas SVG: al menos 12 unidades del viewBox (≥ 11 px en pantalla a 1280 px) y la fuente de la marca
  function fuente(peso, px) { return 'font:' + peso + ' ' + px + 'px var(--oda-fuente)'; }
  function corto(nombre) { return String(nombre).split(' ')[0].toUpperCase().slice(0, 8); }

  // ---------- canchas con Voronoi ----------
  var OJO_LEYENDA = '<svg viewBox="0 14 102 70" width="34" height="24" aria-hidden="true">' +
    '<polygon points="12,19.6 86,30.8 99,46.7 95.4,50.6 24.1,29.2" style="fill:var(--c-acento);stroke:var(--c-acento);stroke-width:2"/>' +
    '<path d="M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z" style="fill:var(--c-azul);stroke:var(--c-acento);stroke-width:6"/>' +
    '<g clip-path="url(#clip-almendra)"><circle cx="54" cy="54" r="24" style="fill:var(--c-acento)"/>' +
    '<path d="M49.3 47.5L58.7 47.5L61.6 56.5L54 62L46.4 56.5Z" style="fill:var(--c-azul);stroke:var(--c-azul);stroke-width:3"/></g></svg>';
  var CANCHA = '<svg class="cancha-svg" viewBox="-3 -3 126 86" role="img" aria-label="Foto de posiciones (360) con el mapa de control del espacio">' +
    '<rect x="0" y="0" width="120" height="80" style="fill:url(#fuera)"/><g class="capa"></g>' +
    '<g class="lineas"><rect x="0" y="0" width="120" height="80"/><line x1="60" y1="0" x2="60" y2="80"/><circle cx="60" cy="40" r="10"/>' +
    '<rect x="0" y="18" width="18" height="44"/><rect x="102" y="18" width="18" height="44"/><rect x="0" y="30" width="6" height="20"/><rect x="114" y="30" width="6" height="20"/></g>' +
    '<rect class="borde-foto" x="-2" y="-2" width="124" height="84" rx="2"/>' +
    '<text class="sin-foto" x="60" y="42" text-anchor="middle">Sin foto de posiciones en este minuto</text></svg>';

  function crearCancha(contenedor) { contenedor.innerHTML = CANCHA; return contenedor.querySelector('svg'); }
  function ojo(x, y, padre) {
    var s = 4.6 / 102, g = el('g', { transform: 'translate(' + (x - 54 * s) + ',' + (y - 54 * s) + ') scale(' + s + ')' }, padre);
    el('polygon', { points: '12,19.6 86,30.8 99,46.7 95.4,50.6 24.1,29.2', style: 'fill:var(--c-acento);stroke:var(--c-acento);stroke-width:2' }, g);
    el('path', { d: 'M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z', style: 'fill:var(--c-azul);stroke:var(--c-acento);stroke-width:6' }, g);
    var iris = el('g', { 'clip-path': 'url(#clip-almendra)' }, g);
    el('circle', { cx: 54, cy: 54, r: 24, style: 'fill:var(--c-acento)' }, iris);
    el('path', { d: 'M49.3 47.5L58.7 47.5L61.6 56.5L54 62L46.4 56.5Z', style: 'fill:var(--c-azul);stroke:var(--c-azul);stroke-width:3' }, iris);
  }
  // ---------- Voronoi en el navegador (mismas reglas que ojo.lentes.voronoi: cancha ∩ área visible ∩ alcance) ----------
  function recortarSemiplano(poli, a, b, c) {  // conserva los puntos con a·x + b·y ≤ c (Sutherland–Hodgman)
    var fuera = [], n = poli.length;
    for (var k = 0; k < n; k++) {
      var P = poli[k], Q = poli[(k + 1) % n], dp = a * P[0] + b * P[1] - c, dq = a * Q[0] + b * Q[1] - c;
      if (dp <= 0) fuera.push(P);
      if ((dp < 0 && dq > 0) || (dp > 0 && dq < 0)) { var s = dp / (dp - dq); fuera.push([P[0] + s * (Q[0] - P[0]), P[1] + s * (Q[1] - P[1])]); }
    }
    return fuera;
  }
  function areaFirmada(p) { var s = 0; for (var k = 0; k < p.length; k++) { var q = p[(k + 1) % p.length]; s += p[k][0] * q[1] - q[0] * p[k][1]; } return s / 2; }
  function recortarConvexo(poli, clip) {
    var signo = areaFirmada(clip) >= 0 ? 1 : -1;
    for (var k = 0; k < clip.length && poli.length; k++) {
      var A = clip[k], B = clip[(k + 1) % clip.length], dx = B[0] - A[0], dy = B[1] - A[1];
      poli = recortarSemiplano(poli, dy * signo, -dx * signo, (dy * A[0] - dx * A[1]) * signo);
    }
    return poli;
  }
  function casco(puntos) {  // envolvente convexa (cadena monótona)
    var p = puntos.slice().sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
    function cruz(o, a, b) { return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); }
    var inf = [], sup = [];
    p.forEach(function (q) { while (inf.length >= 2 && cruz(inf[inf.length - 2], inf[inf.length - 1], q) <= 0) inf.pop(); inf.push(q); });
    p.slice().reverse().forEach(function (q) { while (sup.length >= 2 && cruz(sup[sup.length - 2], sup[sup.length - 1], q) <= 0) sup.pop(); sup.push(q); });
    return inf.slice(0, -1).concat(sup.slice(0, -1));
  }
  function aPuntos(plano) { var p = []; for (var k = 0; k < plano.length; k += 2) p.push([plano[k], plano[k + 1]]); return p; }
  function mayorVisible(visibles) {  // el polígono visible más grande, como envolvente convexa
    var mejor = null, area = -1;
    visibles.forEach(function (v) { var p = aPuntos(v), a = Math.abs(areaFirmada(p)); if (a > area) { mejor = p; area = a; } });
    return mejor ? casco(mejor) : null;
  }
  function voronoiJS(jug, visible, alcance, segmentos) {
    var cancha = [[0, 0], [120, 0], [120, 80], [0, 80]];
    var celdas = jug.map(function (p, i) {
      var poli = cancha;
      jug.forEach(function (q, j) {
        var a = q.x - p.x, b = q.y - p.y;
        if (j === i || (a === 0 && b === 0)) return;
        poli = recortarSemiplano(poli, a, b, (q.x * q.x + q.y * q.y - p.x * p.x - p.y * p.y) / 2);
      });
      if (visible) poli = recortarConvexo(poli, visible);
      var circulo = [];
      for (var k = 0; k < segmentos; k++) circulo.push([p.x + alcance * Math.cos(2 * Math.PI * k / segmentos), p.y + alcance * Math.sin(2 * Math.PI * k / segmentos)]);
      return recortarConvexo(poli, circulo);
    });
    // Frontera: aristas de una celda propia que caen sobre la mediatriz con un rival (equidistantes de los dos)
    var frontera = [], propia = 0, total = 0;
    celdas.forEach(function (c, i) {
      var a = Math.abs(areaFirmada(c)); total += a; if (jug[i].propio) propia += a;
      if (!jug[i].propio) return;
      for (var k = 0; k < c.length; k++) {
        var P = c[k], Q = c[(k + 1) % c.length], m = [(P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2];
        var di = Math.hypot(m[0] - jug[i].x, m[1] - jug[i].y);
        for (var j = 0; j < jug.length; j++) {
          if (jug[j].propio || Math.abs(Math.hypot(m[0] - jug[j].x, m[1] - jug[j].y) - di) > 1e-4) continue;
          if (Math.hypot(Q[0] - P[0], Q[1] - P[1]) > 0.05) frontera.push([P[0], P[1], Q[0], Q[1]]);
          break;
        }
      }
    });
    return { celdas: celdas, frontera: frontera, control: total ? propia / total : null };
  }

  // ---------- dibujo de un estado (una foto exacta o un instante interpolado) ----------
  function fotoAEstado(f) {  // foto exacta de Python: celdas recortadas por shapely
    return { celdas: f.celdas.map(function (c, k) { return { poli: aPuntos(c), propio: !!f.propias[k] }; }),
             frontera: f.frontera.map(function (l) { return l; }), visibles: f.visible.map(aPuntos),
             jugadores: f.jugadores.map(function (j) { return { x: j[0], y: j[1], propio: !!j[2], actor: !!j[3], op: 1 }; }),
             flecha: f.flecha, eq: f.eq, nombre: f.nombre || '', control: f.control };
  }
  function dibujarEstado(svg, e) {
    var capa = svg.querySelector('.capa');
    while (capa.firstChild) capa.removeChild(capa.firstChild);
    svg.classList.toggle('vacia', !e);
    if (!e) return;
    function puntos(p) { return p.map(function (q) { return q[0] + ',' + q[1]; }).join(' '); }
    e.visibles.forEach(function (v) { el('polygon', { points: puntos(v), style: 'fill:var(--c-azul)' }, capa); });
    e.celdas.forEach(function (c) {
      if (c.poli.length < 3) return;
      el('polygon', { points: puntos(c.poli), style: c.propio ? 'fill:var(--c-acento);fill-opacity:.82;stroke:var(--c-azul);stroke-width:.35'
                                                            : 'fill:#fff;fill-opacity:.08;stroke:var(--c-azul);stroke-width:.35' }, capa);
    });
    e.frontera.forEach(function (l) {
      var pts = l.length === 4 ? l[0] + ',' + l[1] + ' ' + l[2] + ',' + l[3] : pares(l);
      el('polyline', { points: pts, style: 'fill:none;stroke:#fff;stroke-width:.8;stroke-linecap:round' }, capa);
    });
    e.visibles.forEach(function (v) { el('polygon', { points: puntos(v), style: 'fill:none;stroke:rgba(255,255,255,.5);stroke-width:.3;stroke-dasharray:1.2 .9' }, capa); });
    if (e.flecha) {
      el('line', { x1: e.flecha[0], y1: e.flecha[1], x2: e.flecha[2], y2: e.flecha[3], 'marker-end': 'url(#' + (e.eq ? 'punta-eq' : 'punta-riv') + ')',
                   style: 'stroke:' + (e.eq ? 'var(--c-acento)' : '#fff') + ';stroke-width:.6;opacity:' + (e.opFlecha == null ? 1 : e.opFlecha) }, capa);
    }
    e.jugadores.forEach(function (j) {
      var g = el('g', { style: 'opacity:' + j.op }, capa);
      if (j.actor) {
        el('circle', { cx: j.x, cy: j.y, r: 2.8, style: 'fill:none;stroke-width:.5;stroke:' + (e.eq ? 'var(--c-acento)' : '#fff') }, g);
        if (e.nombre) el('text', { x: j.x, y: j.y - 3.6, 'text-anchor': 'middle', class: 'nombre-actor' }, g).textContent = e.nombre;
      }
      if (j.propio) ojo(j.x, j.y, g);
      else el('circle', { cx: j.x, cy: j.y, r: .95, style: 'fill:#fff;stroke:var(--c-azul);stroke-width:.35' }, g);
    });
  }
  function dibujarFoto(svg, f) { dibujarEstado(svg, f ? fotoAEstado(f) : null); }

  // ---------- piezas de contenido ----------
  function tarjeta(p, grande) {
    var caso = p.caso ? '<button type="button" class="insignia ir-caso" title="Ir al partido que lo ilustra">' + esc(p.caso) + ' <span aria-hidden="true">→</span></button>' : '';
    var cifras = '<dl class="cifras"><div><dt>' + esc(D.nuevo) + '</dt><dd>' + esc(p.jardine) + '</dd></div>' +
      '<div><dt>Solari y Ortiz</dt><dd>' + esc(p.previos) + '</dd></div>' +
      '<div><dt>Diferencia</dt><dd>' + esc(p.diferencia) + '<small>' + esc(p.intervalo) + '</small></dd></div>' +
      '<div><dt>Torneos en la misma dirección</dt><dd>' + esc(p.torneos) + '</dd></div></dl>';
    var extra = grande ? '<p><strong>Qué significa.</strong> ' + esc(p.significa) + '</p><p><strong>Para el cuerpo técnico (hipótesis).</strong> ' + esc(p.uso) + '</p>' : '';
    return '<article class="tarjeta' + (grande ? ' grande' : '') + '"><header><h3>' + esc(p.titulo) + '</h3>' + caso + '</header>' +
      '<p class="frase">' + esc(p.frase) + '</p>' + cifras + extra + '<span class="estado">' + esc(p.estado) + '</span></article>';
  }
  function montecarlo(m) {
    var marcadores = m.marcadores.slice(0, 3).map(function (x) { return esc(x[0]) + ' (' + pct(x[1]) + ')'; }).join(' · ');
    var partes = [['g', m.gana, 'Gana ' + D.equipo], ['e', m.empata, 'Empate'], ['p', m.pierde, 'Gana ' + D.rival]];
    return '<article class="mc"><h3>' + esc(m.titulo) + '</h3><p>' + esc(m.texto) + '</p>' +
      '<div class="mc-barra" role="img" aria-label="Gana ' + esc(D.equipo) + ' ' + pct(m.gana) + ', empate ' + pct(m.empata) + ', gana ' + esc(D.rival) + ' ' + pct(m.pierde) + '">' +
      partes.map(function (s) { return '<span class="' + s[0] + '" style="width:' + (s[1] * 100).toFixed(1) + '%"></span>'; }).join('') + '</div>' +
      '<div class="mc-cifras" aria-hidden="true" style="grid-template-columns:' + partes.map(function (s) { return 'minmax(64px,' + Math.max(1, s[1] * 100).toFixed(1) + 'fr)'; }).join(' ') + '">' +
      partes.map(function (s) { return '<span><i class="c' + s[0] + '"></i><strong>' + pct(s[1]) + '</strong><small>' + esc(s[2]) + '</small></span>'; }).join('') + '</div>' +
      '<p class="nota">Goles esperados: ' + m.goles_favor.toFixed(2) + ' – ' + m.goles_contra.toFixed(2) + '. Marcadores más frecuentes: ' + marcadores + '.</p></article>';
  }
  function graficaTorneos(contenedor, filas) {
    var antes = filas.filter(function (f) { return !f.nuevo; }).map(function (f) { return f.entrenador; })
      .filter(function (n, k, a) { return a.indexOf(n) === k; }).join(' y ');
    var etiqueta = 'Índice de iniciativa medio por torneo (0 espera, 100 propone). ' + filas.map(function (f) {
      return f.torneo + ' con ' + f.entrenador + ': ' + D.equipo + ' ' + Math.round(f.propio) + ', rivales ' + Math.round(f.rival); }).join('; ') + '.';
    var W = 560, H = 286, M = { i: 36, d: 10, a: 44, b: 46 }, svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': etiqueta });
    contenedor.innerHTML = ''; contenedor.appendChild(svg);
    el('rect', { x: 0, y: 0, width: W, height: H, rx: 8, style: 'fill:var(--c-azul)' }, svg);
    var ancho = (W - M.i - M.d) / filas.length;
    function y(v) { return M.a + (H - M.a - M.b) * (1 - v / 100); }
    el('rect', { x: M.i, y: y(BANDAS[1]), width: W - M.i - M.d, height: y(BANDAS[0]) - y(BANDAS[1]), style: 'fill:rgba(255,255,255,.07)' }, svg);  // banda "equilibrado"
    [0, BANDAS[0], BANDAS[1], 100].forEach(function (v) {
      var banda = v === BANDAS[0] || v === BANDAS[1];
      el('line', { x1: M.i, x2: W - M.d, y1: y(v), y2: y(v), style: 'stroke:rgba(255,255,255,' + (banda ? .3 : .12) + ');stroke-dasharray:' + (banda ? '3 3' : 'none') }, svg);
      el('text', { x: M.i - 6, y: y(v) + 4, 'text-anchor': 'end', style: 'fill:rgba(255,255,255,.7);' + fuente(600, 12) }, svg).textContent = v;
    });
    // Leyenda: quién es cada barra y qué es el punto (V-A6)
    var lx = M.i;
    [['rect', 'fill:var(--c-acento)', D.nuevo], ['rect', 'fill:rgba(255,255,255,.45)', 'Antes de ' + D.nuevo + ' (' + antes + ')'], ['circle', 'fill:#fff;stroke:var(--c-azul);stroke-width:2', 'Rivales']].forEach(function (c) {
      if (c[0] === 'rect') el('rect', { x: lx, y: 12, width: 12, height: 12, rx: 2, style: c[1] }, svg);
      else el('circle', { cx: lx + 6, cy: 18, r: 5, style: c[1] }, svg);
      var t = el('text', { x: lx + 18, y: 23, style: 'fill:#fff;' + fuente(600, 12) }, svg); t.textContent = c[2];
      lx += 18 + (t.getComputedTextLength() || c[2].length * 7) + 18;
    });
    filas.forEach(function (f, k) {
      var x = M.i + ancho * k + ancho * .2, w = ancho * .6;
      el('rect', { x: x, y: y(f.propio), width: w, height: y(0) - y(f.propio), rx: 2, style: f.nuevo ? 'fill:var(--c-acento)' : 'fill:rgba(255,255,255,.45)' }, svg);
      el('text', { x: x + w / 2, y: y(f.propio) - 5, 'text-anchor': 'middle', style: 'fill:#fff;' + fuente(800, 12) }, svg).textContent = Math.round(f.propio);
      el('circle', { cx: x + w / 2, cy: y(f.rival), r: 5, style: 'fill:#fff;stroke:var(--c-azul);stroke-width:2' }, svg);
      el('text', { x: x + w + 2, y: y(f.rival) + 4, style: 'fill:rgba(255,255,255,.85);' + fuente(600, 12) }, svg).textContent = Math.round(f.rival);
      el('text', { x: x + w / 2, y: H - 26, 'text-anchor': 'middle', style: 'fill:rgba(255,255,255,.85);' + fuente(700, 12) }, svg).textContent = f.torneo;
      el('text', { x: x + w / 2, y: H - 10, 'text-anchor': 'middle', style: 'fill:rgba(255,255,255,.7);' + fuente(600, 12) }, svg).textContent = f.entrenador;
    });
  }

  // ---------- barra lateral v5: elegir rival y abrir su ficha de 10 segundos; plegable y ocultable ----------
  // Los rivales y sus partidos salen de las fichas (D.decidir.fichas: partidos con Jardine, AP23–AP25), igual que en Plan de juego.
  function seccion(id, titulo, contenido, abierta, clase) {
    return '<details class="seccion ' + (clase || '') + '" data-seccion="' + id + '"' + (abierta ? ' open' : '') + '><summary>' + esc(titulo) +
      '<span class="resumen-sec"></span></summary><div class="cuerpo-sec">' + contenido + '</div></details>';
  }
  function tamanoNombre(nombre) { return Math.min(30, Math.floor(228 / (0.8 * nombre.length))); }  // igual que app.tamano_nombre
  function conJardine(n) { return n + (n === 1 ? ' partido' : ' partidos') + ' con ' + D.nuevo; }
  function renderBarra(fichas, inicial) {
    var sel = fichas.filter(function (f) { return f.rival === inicial; })[0] || fichas[0];
    var otros = fichas.filter(function (f) { return f !== sel; });
    var rivales = otros.map(function (f) {
      return '<li><button type="button" class="rival-btn" data-rival="' + esc(f.rival) + '" data-n="' + f.partidos + '"><span>' + esc(f.rival) + '</span><span class="n">' + f.partidos + '</span></button></li>';
    }).join('');
    var rival = '<div class="placa-rival"><span class="sel">Seleccionado</span><strong id="rival-nombre" style="font-size:' + tamanoNombre(sel.rival) + 'px">' + esc(sel.rival) + '</strong>' +
      '<span class="cinta-n" id="rival-n" data-n="' + sel.partidos + '">' + conJardine(sel.partidos) + '</span></div><ul class="lista-rivales">' + rivales + '</ul>' +
      (otros.length > 4 ? '<button type="button" class="ver-todos">Ver todos (' + otros.length + ')</button>' : '');
    html('barra',
      '<div class="barra-cab"><span class="titulo-barra">Rivales</span><div class="acciones-cab"><button type="button" class="enlace" data-volver>Restablecer</button>' +
      '<button type="button" class="btn-ocultar" data-ocultar aria-label="Ocultar la barra de rivales" aria-expanded="true">‹</button></div></div>' +
      seccion('rival', 'Rival', rival, true) +
      '<div class="pie-barra"><p class="muestra">Su ficha de 10 segundos: cómo progresa, cómo defiende, dónde concede, su balón parado y cómo le fue a ' + esc(D.nuevo) +
      ' (AP23–AP25). El número es de partidos con ' + esc(D.nuevo) + '.</p>' +
      '<button type="button" class="btn-borde" data-ir-ficha>Ver su ficha de 10 segundos →</button></div>');
  }
  function montarBarra() {  // también "Restablecer": vuelve al rival del caso sin recargar
    renderBarra((D.decidir && D.decidir.fichas) || [], D.rival);
    if (MOV) document.querySelectorAll('details.seccion').forEach(MOV.plegable);
    actualizarResumenes();
  }
  function actualizarResumenes() {
    var nombre = document.getElementById('rival-nombre').textContent;
    document.querySelectorAll('details.seccion .resumen-sec').forEach(function (s) { s.textContent = nombre; });
    // Variante chips (3c): con la barra oculta, el rival elegido queda arriba del contenido
    document.querySelector('.tira-filtros .chips-tira').innerHTML = '<span class="chip-tira">' + esc(nombre) + '</span>';
  }
  function conectarBarra() {
    var aside = document.querySelector('aside.barra');
    aside.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.classList.contains('rival-btn')) cambiarRival(b);
      else if (b.classList.contains('ver-todos')) { var l = aside.querySelector('.lista-rivales'); l.classList.toggle('todos'); b.textContent = l.classList.contains('todos') ? 'Ver menos' : 'Ver todos (' + l.children.length + ')'; }
      else if (b.hasAttribute('data-ocultar')) ocultarBarra(!cuerpo.classList.contains('barra-oculta'), true);
      else if (b.hasAttribute('data-volver')) { montarBarra(); var v = aside.querySelector('[data-volver]'); if (v) v.focus(); return; }
      else if (b.hasAttribute('data-ir-ficha')) { irAFicha(document.getElementById('rival-nombre').textContent); return; }
      actualizarResumenes();
    });
  }
  function cambiarRival(b) {
    var nombre = document.getElementById('rival-nombre'), conteo = document.getElementById('rival-n');
    var antes = [nombre.textContent, conteo.dataset.n];
    nombre.textContent = b.dataset.rival; conteo.dataset.n = b.dataset.n; conteo.textContent = conJardine(+b.dataset.n);
    nombre.style.fontSize = tamanoNombre(b.dataset.rival) + 'px';
    b.dataset.rival = antes[0]; b.dataset.n = antes[1];
    b.firstElementChild.textContent = antes[0]; b.lastElementChild.textContent = antes[1];
    // el cajón del teléfono sigue abierto: el siguiente paso es "Ver su ficha", dentro de la barra
  }
  // Mostrar u ocultar la barra en escritorio (variantes en movimiento.js). Lo oculto queda inerte y el foco pasa al botón visible.
  function ocultarBarra(oculta, porUsuario) {
    var variante = cuerpo.getAttribute('data-barra-variante') || 'riel';
    if (MOV && porUsuario) MOV.barra(oculta, variante); else cuerpo.classList.toggle('barra-oculta', oculta);  // al cargar, sin animar
    var contenido = document.querySelector('aside.barra .barra-contenido'), riel = document.querySelector('aside.barra .riel');
    contenido.inert = oculta && !movil();
    riel.inert = !oculta || variante === 'chips';
    document.querySelectorAll('[data-ocultar]').forEach(function (b) { b.setAttribute('aria-expanded', String(!oculta)); });
    try { localStorage.setItem('ojo.barraOculta', oculta ? '1' : '0'); } catch (e) { /* sin almacenamiento: solo en esta visita */ }
    if (!porUsuario) return;
    var destino = !oculta ? contenido.querySelector('[data-ocultar]')
      : (variante === 'chips' ? document.querySelector('.tira-filtros [data-ocultar]') : riel.querySelector('[data-ocultar]'));
    // en la variante riel el botón del riel aparece cuando termina de apagarse el contenido
    var espera = oculta && variante === 'riel' && MOV ? MOV.dur('rapida') + 20 : 0;
    if (destino) setTimeout(function () { destino.focus({ preventScroll: true }); }, espera);
  }

  // ---------- render general ----------
  function render() {
    texto('equipo', D.equipo); texto('rival', D.rival);
    html('kpis', D.portada.kpis.map(function (k) { return '<div class="kpi"><span>' + esc(k.etq) + '</span><strong>' + esc(k.valor) + '</strong><small>' + esc(k.detalle) + '</small></div>'; }).join(''));
    slots('torneos').forEach(function (c) { graficaTorneos(c, D.portada.torneos); });
    html('principios', D.portada.principios.map(function (p) { return tarjeta(p, false); }).join(''));
    texto('ejemplo-texto', 'Ejemplo: ' + D.portada.ejemplo.texto);
    slots('ejemplo-foto').forEach(function (c) { dibujarFoto(crearCancha(c), D.portada.ejemplo.foto); });
    html('leyenda', '<li><span class="pastilla">' + OJO_LEYENDA + '</span>' + esc(D.equipo) + '</li><li><span class="pastilla"><span class="punto"></span></span>' + esc(D.rival) +
      '</li><li><span class="pastilla"><span class="raya"></span></span>Frontera entre equipos</li>');
    texto('que-muestra', D.explorar.que_muestra);
    var X = D.explorar;
    texto('antetitulo', X.antetitulo);
    texto('titulo-explorar', D.equipo.toUpperCase() + ' VS ' + D.rival.toUpperCase());
    html('filtros', X.filtros.map(function (f) { return '<span class="filtro">' + esc(f) + '</span>'; }).join(''));
    html('principio', tarjeta(X.principio, true));
    texto('caso-titulo', X.caso.titulo);
    html('caso-chips', X.caso.chips.map(function (c) { return '<div class="dato"><span>' + esc(c[0]) + '</span><strong>' + esc(c[1]) + '</strong></div>'; }).join(''));
    html('caso-quiebres', X.caso.quiebres.map(function (q) { return '<li class="' + (q[2] ? 'caso' : '') + '"><span class="min">' + esc(q[0]) + '</span>' + esc(q[1]) + '</li>'; }).join(''));
    html('montecarlo', X.montecarlo.map(montecarlo).join(''));
    if (X.simulaciones) texto('simulaciones', X.simulaciones.toLocaleString('es-MX'));
    if (MOV) document.querySelectorAll('.mc-barra').forEach(function (b) { MOV.alVer(b, function () { MOV.crecer(b.children, { escalon: 80 }); }); });  // A6, una vez
    texto('lectura', X.lectura); texto('metodo', X.metodo);
    html('siguiente', (X.siguiente || []).map(function (s) {  // bloque 6: del caso a la matriz, a la ficha del rival y a la evidencia
      return '<article class="paso-sig"><h3>' + esc(s.titulo) + '</h3><p>' + esc(s.texto) + '</p><button type="button" class="btn-ir" data-ir="' + esc(s.vista + '#' + s.ancla) + '"' +
        (s.rival ? ' data-rival="' + esc(s.rival) + '"' : '') + (s.situacion ? ' data-situacion="' + esc(s.situacion) + '"' : '') + '>' + esc(s.boton) + ' →</button></article>';
    }).join(''));
    html('notas', X.notas.map(function (n) { return '<p class="nota">' + esc(n) + '</p>'; }).join(''));
    if (D.decidir) renderDecidir(D.decidir);
    if (D.metodo) renderMetodo(D.metodo);
  }

  // ---------- Decidir: matriz de situaciones, ficha de 10 segundos, balón parado y uso de jugadores ----------
  var NIVELES = { domina: ['▲', 'Le funciona'], parejo: ['●', 'Parejo'], sufre: ['▼', 'Sufre'] };
  function num(v, dec) { return v == null ? '—' : Number(v).toFixed(dec == null ? 2 : dec); }
  function riesgo(q) { return q < .01 ? 'menos de 1 %' : Math.round(q * 100) + ' %'; }  // igual que decision.texto_riesgo
  function tablaComp(filas, primera) {
    return '<thead><tr><th>' + esc(primera) + '</th><th>' + esc(D.nuevo) + '</th><th>Solari y Ortiz</th><th>¿Distinto? (4 filtros)</th></tr></thead><tbody>' +
      filas.map(function (f) {
        return '<tr><th>' + esc(f.etq) + '</th><td>' + num(f.jardine) + '</td><td>' + num(f.previos) + '</td><td class="' + (f.pasa ? 'si' : '') + '">' +
          (f.pasa ? 'Sí (riesgo de falso hallazgo: ' + riesgo(f.q) + ')' : 'No') + '</td></tr>';
      }).join('') + '</tbody>';
  }
  function renderFicha(f) {
    function chips(lista) { return '<div class="chips-f">' + lista.map(function (c) { return '<i>' + esc(c) + '</i>'; }).join('') + '</div>'; }
    html('ficha', '<h3>' + esc(f.rival) + '</h3>' +
      '<div class="campo"><span>Cómo progresa</span>' + chips(f.progresa) + '</div>' +
      '<div class="campo"><span>Cómo defiende</span>' + chips(f.defiende) + '</div>' +
      '<div class="campo"><span>Dónde concede</span>' + chips(f.concede) + '</div>' +
      '<div class="campo"><span>Balón parado</span>' + (f.balon_parado_rasgos.length ? chips(f.balon_parado_rasgos) : '') + '<p>' + esc(f.balon_parado) + '</p></div>' +
      '<div class="campo"><span>' + esc(D.nuevo) + ' contra él</span><p>' + esc(f.jardine) + '</p></div>' +
      '<div class="campo"><span>Contra rivales parecidos</span><p>' + esc(f.parecidos.join(', ')) + '</p><p>' + esc(f.jardine_parecidos) + '</p></div>');
  }
  // De la barra a la ficha de 10 segundos del rival elegido (vista Decidir)
  function irAFicha(nombre) {
    var fichas = (D.decidir && D.decidir.fichas) || [], k = fichas.map(function (f) { return f.rival; }).indexOf(nombre);
    cerrarCajon();
    cambiarVista('decidir', function () {
      var sel = document.getElementById('rival-ficha');
      if (k >= 0) { sel.value = String(k); sel.dispatchEvent(new Event('change')); }
      var destino = document.getElementById('ficha');
      if (MOV) MOV.irA(destino); else destino.scrollIntoView();
    });
  }
  function renderDecidir(X) {
    if (X.base) texto('base-decidir', 'Su partido normal (AP23–AP25, sin el torneo reservado): índice de iniciativa ' + X.base.indice + ', PPDA ' + num(X.base.ppda, 1) +
      ' y balance de ocasiones ' + (X.base.xg_dif_90 >= 0 ? '+' : '') + num(X.base.xg_dif_90) + ' xG cada 90 minutos.');
    html('matriz', X.matriz.map(function (m) {
      var n = NIVELES[m.nivel] || NIVELES.parejo;
      return '<article class="situacion"><header><h3>' + esc(m.situacion) + '</h3><span class="nivel ' + m.nivel + '">' + n[0] + ' ' + n[1] + '</span></header>' +
        '<p><strong>Qué hace.</strong> ' + esc(m.hace) + '</p><p><strong>Resultado.</strong> ' + esc(m.funciona) + '</p>' +
        '<p class="rec"><b>Recomendación (hipótesis)</b>' + esc(m.recomendacion) + '</p><p class="evid">' + esc(m.evidencia) + '</p></article>';
    }).join(''));
    var sel = document.getElementById('rival-ficha');
    sel.innerHTML = X.fichas.map(function (f, k) { return '<option value="' + k + '">' + esc(f.rival) + ' (' + f.partidos + ' partidos)</option>'; }).join('');
    var inicial = X.fichas.map(function (f) { return f.rival; }).indexOf(D.rival);
    sel.value = String(inicial >= 0 ? inicial : 0);
    if (X.fichas.length) renderFicha(X.fichas[+sel.value]);
    sel.addEventListener('change', function () { renderFicha(X.fichas[+sel.value]); });
    if (X.balon_parado) {
      html('bp-resumen', tablaComp(X.balon_parado.resumen, 'Por partido'));
      var maximo = Math.max.apply(null, X.balon_parado.zonas.map(function (z) { return Math.max(z.jardine || 0, z.previos || 0); })) || 1;
      html('bp-zonas', '<p class="ley"><span><i style="background:var(--c-acento)"></i>' + esc(D.nuevo) + '</span><span><i style="background:var(--c-azul)"></i>Solari y Ortiz</span></p>' +
        ['favor', 'contra'].map(function (lado) {
          return '<h4>' + (lado === 'favor' ? 'Remata el América' : 'Le rematan') + '</h4>' + X.balon_parado.zonas.filter(function (z) { return z.lado === lado; }).map(function (z) {
            return '<div class="zona-fila"><span>' + esc(z.zona) + '</span><div class="barras" role="img" aria-label="' + esc(z.zona) + ': ' + esc(D.nuevo) + ' ' + num(z.jardine) + ', Solari y Ortiz ' + num(z.previos) + ' xG por partido">' +
              '<span class="b j" style="width:' + (100 * (z.jardine || 0) / maximo).toFixed(1) + '%"></span><span class="b p" style="width:' + (100 * (z.previos || 0) / maximo).toFixed(1) + '%"></span></div></div>';
          }).join('');
        }).join(''));
    }
    if (X.jugadores) html('uso-resumen', tablaComp(X.jugadores.resumen, 'Por partido'));
    html('casos', (X.casos || []).map(function (c, k) {
      return '<article class="caso-dec"><span class="n">' + (k + 1) + '</span><h3>' + esc(c.titulo) + '</h3>' +
        '<p class="regla">Regla: ' + esc(c.regla) + '</p>' +
        '<div class="dos-col"><div><span class="etq-c">Qué marcaba la herramienta</span><p>' + esc(c.marcaba) + '</p></div>' +
        '<div><span class="etq-c">Qué pasó</span><ul>' + c.paso.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ul></div></div>' +
        '<p class="lect"><b>Lectura.</b> ' + esc(c.lectura) + '</p></article>';
    }).join('') || '<p class="pie">Sin casos disponibles.</p>');
  }

  // ---------- Método: el reporte (datos, criterio, principios con evidencia y validación) ----------
  var SIMBOLOS = { se_sostiene: '✓', misma_direccion: '≈', no_se_sostiene: '✗', sin_muestra: '—' };
  function veredicto(v) { return (SIMBOLOS[v.veredicto] ? SIMBOLOS[v.veredicto] + ' ' : '') + v.texto; }
  function renderMetodo(M) {
    var d = M.datos;
    html('met-datos', '<li><strong>StatsBomb, Liga MX:</strong> ' + d.liga.toLocaleString('es-MX') + ' partidos de AP21 a CL26, con eventos, fotos de posiciones (360), estadísticas de equipo y alineaciones.</li>' +
      '<li><strong>' + esc(D.nuevo) + ':</strong> ' + d.nuevo + ' partidos (' + esc(d.torneos_nuevo) + ').</li>' +
      '<li><strong>Solari y Ortiz:</strong> ' + d.previos + ' partidos (' + esc(d.torneos_previos) + ').</li>' +
      '<li><strong>Torneo reservado:</strong> ' + d.prueba + ' partidos (' + esc(d.torneos_prueba) + '), apartados hasta la evaluación final.</li>');
    var p = M.pca;
    texto('met-pca', 'Ocho señales por minuto (ataque elaborado, posesión, dominio del último tercio, espacio en campo rival, altura sin balón y presión alta suman; juego directo y pase largo restan), con el mismo peso, de 0 (espera) a 100 (propone). Comprobación de los pesos con los datos (PCA): ' +
      (p.mismo_signo ? 'las 8 empujan en la dirección esperada' : 'no todas empujan en la dirección esperada') + ', resumen el ' + Math.round(p.varianza * 100) + ' % de la variación y el promedio con pesos iguales coincide en ' + num(p.correlacion) + ' (correlación) con la combinación que sale de los datos.');
    if (M.criterio) {
      var c = M.criterio;
      texto('met-criterio', 'Prueba en falso (placebo): en ' + c.placebo_pruebas + ' momentos clave inventados (tramos donde no pasó nada), la primera versión de los filtros, sin el filtro 4, aprobaba ' + c.placebo_v1 +
        '; con los 4 filtros, ' + c.placebo_v2 + '. De las ' + c.pruebas + ' pruebas del análisis pasan ' + c.pasan_v2 + ' (con la primera versión pasaban ' + c.pasan_v1 + ').' +
        (c.reales_1a3 == null ? '' : ' Sin el filtro 4, los filtros 1 a 3 aprueban ' + c.placebo_1a3 + ' de ' + c.placebo_pruebas + ' momentos inventados frente a ' + c.reales_1a3 + ' de ' + c.reales_pruebas + ' reales: esa diferencia es la que muestra que el método no inventa.') +
        ' La prueba en falso se hizo con los momentos clave de ' + D.nuevo + '; la comparación con Solari y Ortiz no tiene una propia.');
    }
    var val = {};
    ((D.decidir && D.decidir.validacion) || []).forEach(function (v) { val[v.principio] = v; });
    html('met-principios', '<thead><tr><th>Principio</th><th>' + esc(D.nuevo) + '</th><th>Solari y Ortiz</th><th>Diferencia</th><th>Torneos</th><th>4 filtros</th><th>En el CL26</th></tr></thead><tbody>' +
      D.portada.principios.map(function (pr) {
        var v = val[pr.titulo];
        return '<tr><th>' + esc(pr.titulo) + '</th><td>' + esc(pr.jardine) + '</td><td>' + esc(pr.previos) + '</td><td>' + esc(pr.diferencia) + '<br><small>' + esc(pr.intervalo) + '</small></td><td>' +
          esc(pr.torneos) + '</td><td>' + esc(pr.estado) + '</td><td class="ver-' + (v ? v.veredicto : '') + '">' + esc(v ? veredicto(v) : '—') + '</td></tr>';
      }).join('') + '</tbody>');
    html('met-validacion', '<thead><tr><th>Principio</th><th>Diferencia en los torneos analizados (AP23–AP25)</th><th>Diferencia en el torneo reservado (CL26)</th><th>Partidos</th><th>Veredicto</th></tr></thead><tbody>' +
      ((D.decidir && D.decidir.validacion) || []).map(function (v) {
        return '<tr><th>' + esc(v.principio) + '</th><td>' + esc(v.entrenamiento || '—') + '</td><td>' + (v.prueba == null ? '—' : esc(v.prueba) + '<br><small>rango probable: ' + esc(v.bajo) + ' a ' + esc(v.alto) + '</small>') +
          '</td><td>' + v.partidos + '</td><td class="ver-' + v.veredicto + '">' + esc(veredicto(v)) + '</td></tr>';
      }).join('') + '</tbody>');
  }

  // ---------- reproductor: minuto a minuto (fundido) y jugadas animadas (Voronoi en movimiento) ----------
  function reproductor() {
    var R = D.reproductor, svg = crearCancha(document.querySelector('[data-slot="cancha-repro"]'));
    var repro = document.getElementById('repro'), tiempo = document.getElementById('tiempo');
    var reloj = document.getElementById('reloj'), accion = document.getElementById('accion'), play = document.getElementById('play');
    var A = R.animacion || { escala: 1.5, duracion: [0.35, 2.5], alcance: 20, cuartos_circulo: 8 };
    var modo = 'partido', jugada = null, i = 0, p = 0, timer = null, raf = null, previo = null, pausa = 0, fotoMostrada = -1;
    var PASO_MINUTO = 650;  // ms por minuto en el modo partido (solo presentación)
    var PAUSA_FOTO = 1000 * (A.pausa_foto == null ? .6 : A.pausa_foto);  // en cada foto real de una jugada (A1)
    var insignia = document.getElementById('insignia-foto');
    // A1 · cada cuadro dice si es dato (foto 360) o relleno (posición estimada entre fotos): insignia y borde
    function marcarFoto(estado) {
      svg.classList.toggle('foto-real', estado === 'real'); svg.classList.toggle('foto-estimada', estado === 'estimado');
      insignia.hidden = !estado;
      if (!estado || insignia.dataset.estado === estado) return;
      insignia.dataset.estado = estado;
      insignia.textContent = estado === 'real' ? '● Foto real' : '◌ Estimado';
    }
    function pulsoActor(f) {  // anillo en quien ejecuta la acción al llegar a una foto real
      var a = f.jugadores.filter(function (j) { return j[3]; })[0];
      if (a && MOV) MOV.pulso(svg, a[0], a[1], { r0: 2.6, r1: 9, grosor: .6 });
    }

    // Botones de modo: partido completo y una por jugada animada
    var modos = document.querySelector('.modos');
    modos.innerHTML = '<button type="button" data-modo="partido" aria-pressed="true">Partido completo</button>' +
      (R.jugadas || []).map(function (j, k) { return '<button type="button" data-modo="jugada" data-j="' + k + '" aria-pressed="false">▶ ' + esc(j.titulo) + '</button>'; }).join('');

    function etiquetaIndice(v) { return v >= BANDAS[1] ? 'propone' : (v <= BANDAS[0] ? 'espera' : 'equilibrado'); }  // igual que decision.banda_indice
    function formato(c, v) { if (v == null) return '—'; if (c.formato === 'pct') return pct(v); if (c.formato === 'm') return v.toFixed(1) + ' m'; return v.toFixed(2); }
    // A3 · radar: la parte fija se dibuja una vez y los dos polígonos se transforman de un minuto al siguiente
    var cx = 160, cy = 114, Rr = 72, nR = R.componentes.length, polyA = null, polyR = null;
    function punto(k, z) { var a = -Math.PI / 2 + 2 * Math.PI * k / nR, r = Rr * (Math.max(-2.5, Math.min(2.5, z == null ? 0 : z)) + 2.5) / 5; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
    function radar(m) {
      if (!polyA) construirRadar();
      var pa = [], pr = [];
      for (var k = 0; k < nR; k++) { pa.push(punto(k, m.za[k])); pr.push(punto(k, m.zr[k])); }
      if (MOV) { MOV.poligono(polyR, pr); MOV.poligono(polyA, pa); }
      else { polyR.setAttribute('points', pr.join(' ')); polyA.setAttribute('points', pa.join(' ')); }
    }
    function construirRadar() {
      var s = document.getElementById('radar'), n = nR;
      el('rect', { x: 0, y: 0, width: 320, height: 230, rx: 8, style: 'fill:var(--c-azul)' }, s);
      [-2.5, 0, 2.5].forEach(function (z) {
        var ps = []; for (var k = 0; k < n; k++) ps.push(punto(k, z).join(','));
        el('polygon', { points: ps.join(' '), style: 'fill:none;stroke:rgba(255,255,255,' + (z === 0 ? .45 : .15) + ');stroke-width:' + (z === 0 ? 1.2 : .8) }, s);
      });
      R.componentes.forEach(function (c, k) {
        var q = punto(k, 2.5), a = -Math.PI / 2 + 2 * Math.PI * k / n;
        el('line', { x1: cx, y1: cy, x2: q[0], y2: q[1], style: 'stroke:rgba(255,255,255,.15)' }, s);
        el('text', { x: cx + (Rr + 10) * Math.cos(a), y: cy + (Rr + 10) * Math.sin(a) + 4, 'text-anchor': Math.abs(Math.cos(a)) < .2 ? 'middle' : (Math.cos(a) > 0 ? 'start' : 'end'),
                     style: 'fill:rgba(255,255,255,.9);' + fuente(600, 12) }, s).textContent = c.radar;
      });
      // El rival solo con contorno discontinuo: se distingue del América sin depender del color (V-A1)
      polyR = el('polygon', { style: 'fill:none;stroke:#fff;stroke-width:1.6;stroke-dasharray:5 4' }, s);
      polyA = el('polygon', { style: 'fill:var(--c-acento);fill-opacity:.35;stroke:var(--c-acento);stroke-width:2.4' }, s);
    }
    function panelMinuto(m) {
      document.getElementById('m-a').style.left = (m.ia == null ? 50 : m.ia) + '%';
      document.getElementById('m-r').style.left = (m.ir == null ? 50 : m.ir) + '%';
      var fa = m.ia == null ? '—' : Math.round(m.ia), fr = m.ir == null ? '—' : Math.round(m.ir);
      document.getElementById('frase-momento').innerHTML = '<strong>' + esc(D.equipo) + ' ' + fa + '</strong> (' + (m.ia == null ? 'sin dato' : etiquetaIndice(m.ia)) +
        ') · ' + esc(D.rival) + ' ' + fr + ' (' + (m.ir == null ? 'sin dato' : etiquetaIndice(m.ir)) + '). Marcador ' + esc(m.marcador) + '.';
      radar(m);
      var filas = '<thead><tr><th></th><th>' + esc(D.equipo) + '</th><th>' + esc(D.rival) + '</th></tr></thead><tbody>';
      R.componentes.forEach(function (c, k) { filas += '<tr><th>' + esc(c.nombre) + '</th><td>' + formato(c, m.va[k]) + '</td><td>' + formato(c, m.vr[k]) + '</td></tr>'; });
      document.getElementById('tabla-momento').innerHTML = filas + '</tbody>';
    }

    // Instante interpolado entre la foto k y la k+1 de una jugada (p de 0 a 1)
    function instante(fotos, k, prog) {
      var a = fotos[k], b = fotos[Math.min(k + 1, fotos.length - 1)];
      if (a === b) prog = 0;
      var enB = {}; b.ids.forEach(function (id, j) { enB[id] = j; });
      var enA = {}; a.ids.forEach(function (id) { enA[id] = true; });
      var base = prog < .5 ? a : b, jug = [];
      a.jugadores.forEach(function (ja, k2) {
        var id = a.ids[k2];
        if (id in enB) {
          var jb = b.jugadores[enB[id]];
          jug.push({ x: ja[0] + (jb[0] - ja[0]) * prog, y: ja[1] + (jb[1] - ja[1]) * prog, propio: !!ja[2], actor: prog < .5 ? !!ja[3] : !!jb[3], op: 1 });
        } else if (prog < .5) jug.push({ x: ja[0], y: ja[1], propio: !!ja[2], actor: !!ja[3], op: 1 - 2 * prog });  // sale de cámara
      });
      b.jugadores.forEach(function (jb, j) {
        if (!enA[b.ids[j]] && prog >= .5) jug.push({ x: jb[0], y: jb[1], propio: !!jb[2], actor: !!jb[3], op: 2 * prog - 1 });  // entra a cámara
      });
      var v = voronoiJS(jug, mayorVisible(base.visible), A.alcance, 4 * A.cuartos_circulo);
      return { celdas: v.celdas.map(function (c, k2) { return { poli: c, propio: jug[k2].propio }; }), frontera: v.frontera,
               visibles: base.visible.map(aPuntos), jugadores: jug, flecha: a.flecha, opFlecha: 1 - prog, eq: base.eq,
               nombre: base.nombre, control: v.control, texto: base.texto, reloj: base.reloj };
    }
    function duracion(fotos, k) {
      if (k >= fotos.length - 1) return 1;
      return Math.max(A.duracion[0], Math.min(A.duracion[1], (fotos[k + 1].t - fotos[k].t) * A.escala));
    }
    function mostrarJugada() {
      var prog = reducido() ? 0 : p;  // con movimiento reducido, solo fotos reales: nada se interpola
      var e = instante(jugada.fotos, i, prog);
      dibujarEstado(svg, e);
      marcarFoto(prog === 0 ? 'real' : 'estimado');
      reloj.textContent = e.reloj;
      tiempo.setAttribute('aria-valuetext', 'Foto ' + (i + 1) + ' de ' + jugada.fotos.length + ', ' + e.reloj);
      accion.textContent = e.reloj + ' · ' + e.texto + ' · control del ' + D.equipo + ': ' + (e.control == null ? '—' : pct(e.control)) +
        (prog === 0 ? ' · foto de posiciones (360)' : ' · posiciones estimadas entre fotos');
    }
    function mostrarMinuto() {
      var m = R.minutos[i], f = m.foto == null ? null : R.fotos[m.foto], capa = svg.querySelector('.capa');
      // A4 · fundido real entre minutos (la foto vieja se apaga mientras la nueva aparece): las fotos están a 60 s, no se inventa movimiento
      if (m.foto !== fotoMostrada) {
        if (MOV && fotoMostrada !== -1) MOV.cruce(capa, function () { dibujarFoto(svg, f); }); else dibujarFoto(svg, f);
        fotoMostrada = m.foto;
      }
      marcarFoto(f ? 'real' : null);
      accion.textContent = f ? f.reloj + ' · ' + f.texto + ' · control del ' + D.equipo + ': ' + pct(f.control) : '';
      reloj.textContent = m.etq + ' · ' + m.marcador;
      tiempo.setAttribute('aria-valuetext', 'Minuto ' + m.etq + ', marcador ' + m.marcador);
      panelMinuto(m); marcarLinea();
    }
    function lista() { return modo === 'partido' ? R.minutos : jugada.fotos; }
    function actualizar() {
      var L = lista(); i = Math.max(0, Math.min(i, L.length - 1)); tiempo.max = L.length - 1; tiempo.value = i;
      if (modo === 'partido') mostrarMinuto();
      else { mostrarJugada(); var mm = R.minutos[jugada.minuto]; if (mm) panelMinuto(mm); }
    }
    function detener() {
      if (timer) clearInterval(timer); if (raf) cancelAnimationFrame(raf);
      timer = raf = previo = null; play.textContent = '▶'; play.setAttribute('aria-label', 'Reproducir'); repro.classList.remove('reproduciendo');
    }
    // Animación continua de la jugada: lineal entre fotos (sin easing) y una pausa en cada foto real
    function cuadro(ahora) {
      if (previo != null) {
        var dt = ahora - previo;
        if (pausa > 0) pausa -= dt;
        else {
          p += dt / 1000 / duracion(jugada.fotos, i);
          if (p >= 1) { i++; p = 0; pausa = PAUSA_FOTO; pulsoActor(jugada.fotos[i]); }
          if (i >= jugada.fotos.length - 1) { p = 0; mostrarJugada(); tiempo.value = i; detener(); return; }
          tiempo.value = i; mostrarJugada();
        }
      }
      previo = ahora; raf = requestAnimationFrame(cuadro);
    }
    function reproducir() {
      if (i >= lista().length - 1) { i = 0; p = 0; }
      play.textContent = '❚❚'; play.setAttribute('aria-label', 'Pausar'); repro.classList.add('reproduciendo');
      if (modo === 'partido') timer = setInterval(function () { if (i >= lista().length - 1) { detener(); return; } i++; actualizar(); }, PASO_MINUTO);
      else { if (p === 0) { pausa = PAUSA_FOTO; pulsoActor(jugada.fotos[i]); } raf = requestAnimationFrame(cuadro); }
    }
    play.addEventListener('click', function () { if (timer || raf) detener(); else reproducir(); });
    tiempo.addEventListener('input', function () { detener(); i = +tiempo.value; p = 0; actualizar(); });
    function irAQuiebre(dir) {  // minuto del quiebre anterior (-1) o siguiente (+1) en el modo partido
      var ks = R.quiebres.map(function (q) { return q.k; }).filter(function (k) { return dir > 0 ? k > i : k < i; });
      if (!ks.length) return;
      detener(); i = dir > 0 ? Math.min.apply(null, ks) : Math.max.apply(null, ks); p = 0; actualizar();
    }
    repro.addEventListener('keydown', function (e) {
      if (e.key === 'PageDown' || e.key === 'PageUp') {
        if (modo !== 'partido') return;
        e.preventDefault(); irAQuiebre(e.key === 'PageDown' ? 1 : -1); return;
      }
      if (e.target.tagName === 'INPUT') return;  // el deslizador ya maneja flechas, Inicio y Fin
      if (e.key === ' ') { e.preventDefault(); if (timer || raf) detener(); else reproducir(); }
      if (e.key === 'ArrowRight') { detener(); i++; p = 0; actualizar(); }
      if (e.key === 'ArrowLeft') { detener(); i--; p = 0; actualizar(); }
      if (e.key === 'Home' || e.key === 'End') { e.preventDefault(); detener(); i = e.key === 'Home' ? 0 : lista().length - 1; p = 0; actualizar(); }
    });
    modos.addEventListener('click', function (ev) {
      var b = ev.target.closest('button'); if (!b) return;
      detener(); modo = b.dataset.modo; jugada = modo === 'jugada' ? R.jugadas[+b.dataset.j] : null; i = 0; p = 0; fotoMostrada = -1;
      modos.querySelectorAll('button').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      document.querySelector('.linea-js').hidden = modo !== 'partido'; actualizar();
      if (modo === 'jugada' && !reducido()) reproducir();  // al elegir una jugada arranca la animación; con movimiento reducido espera al ▶ (V-M8)
    });
    // Línea del índice (modo partido): clic para saltar
    var linea = document.getElementById('linea'), W = 560, H = 214, M = { i: 34, d: 70, a: 58, b: 26 }, cursor;
    var FS = 12.5;  // la línea se ve a ~0.9 de su viewBox a 1280 px: 12.5 unidades ≈ 11.4 px
    linea.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    function xDe(k) { return M.i + (W - M.i - M.d) * k / Math.max(R.minutos.length - 1, 1); }
    function yDe(v) { return M.a + (H - M.a - M.b) * (1 - v / 100); }
    el('rect', { x: 0, y: 0, width: W, height: H, rx: 8, style: 'fill:var(--c-azul)' }, linea);
    el('rect', { x: M.i, y: yDe(BANDAS[1]), width: W - M.i - M.d, height: yDe(BANDAS[0]) - yDe(BANDAS[1]), style: 'fill:rgba(255,255,255,.05)' }, linea);  // banda "equilibrado"
    [BANDAS[0], 50, BANDAS[1]].forEach(function (v) {
      el('line', { x1: M.i, x2: W - M.d, y1: yDe(v), y2: yDe(v), style: 'stroke:rgba(255,255,255,' + (v === 50 ? .3 : .12) + ');stroke-dasharray:3 3' }, linea);
      if (v !== 50) el('text', { x: M.i - 6, y: yDe(v) + 4, 'text-anchor': 'end', style: 'fill:rgba(255,255,255,.7);' + fuente(600, FS) }, linea).textContent = v;
    });
    R.etiquetasX.forEach(function (e) { if (e.periodo && e.k > 0) el('line', { x1: xDe(e.k) - .5, x2: xDe(e.k) - .5, y1: M.a, y2: H - M.b, style: 'stroke:rgba(255,255,255,.35)' }, linea); });
    // Quiebres: línea en su minuto; goles y expulsiones con etiqueta en el primer nivel libre (3 niveles), dentro del área
    var niveles = [[], [], []], marcasQ = [];
    R.quiebres.forEach(function (q) {
      var ln = el('line', { x1: xDe(q.k), x2: xDe(q.k), y1: M.a, y2: H - M.b, style: 'stroke:' + (q.favor ? 'var(--c-acento)' : '#fff') + ';stroke-width:' + (q.fuerte ? 1.6 : .8) + ';opacity:' + (q.fuerte ? .9 : .45) }, linea);
      var marca = { q: q, linea: ln, texto: null }; marcasQ.push(marca);
      if (!q.fuerte) return;
      var t = el('text', { y: 0, style: 'fill:' + (q.favor ? 'var(--c-acento)' : '#fff') + ';' + fuente(700, FS + .5) }, linea);
      t.textContent = q.corto;
      var w = t.getComputedTextLength() || q.corto.length * 8,  // en una vista oculta no se puede medir: estimación
          x0 = Math.max(M.i, Math.min(W - M.d - w, xDe(q.k) - w / 2));
      var choque = niveles.map(function (nv) { return nv.reduce(function (s, r) { return s + Math.max(0, Math.min(r[1], x0 + w + 4) - Math.max(r[0], x0 - 4)); }, 0); });
      var lv = choque.indexOf(Math.min.apply(null, choque));
      niveles[lv].push([x0, x0 + w]);
      t.setAttribute('x', x0); t.setAttribute('y', 16 + 15 * lv);
      marca.texto = t;
    });
    // Rival discontinuo y etiquetas directas al final de cada serie: se distinguen en gris y con daltonismo (V-A1)
    // A2 · lo ya jugado se ve opaco (recortado hasta el cursor) y lo que falta al 25 %
    var SERIES = [['ir', '#fff', 1.6, '5 4', D.rival], ['ia', 'var(--c-acento)', 2.4, 'none', D.equipo]];
    var finales = [], recorte = el('rect', { x: 0, y: 0, width: 0, height: H }, el('clipPath', { id: 'linea-jugado' }, el('defs', {}, linea)));
    SERIES.forEach(function (s) {
      var ps = [], ultimo = null; R.minutos.forEach(function (m, k) { if (m[s[0]] != null) { ps.push(xDe(k) + ',' + yDe(m[s[0]])); ultimo = yDe(m[s[0]]); } });
      var estilo = 'fill:none;stroke:' + s[1] + ';stroke-width:' + s[2] + ';stroke-dasharray:' + s[3];
      el('polyline', { points: ps.join(' '), style: estilo + ';opacity:.25' }, linea);
      el('polyline', { points: ps.join(' '), style: estilo, 'clip-path': 'url(#linea-jugado)' }, linea);
      if (ultimo != null) finales.push({ y: ultimo, color: s[1], txt: corto(s[4]) });
    });
    if (finales.length === 2 && Math.abs(finales[0].y - finales[1].y) < 14) {  // separa las etiquetas si las series terminan juntas
      var medio = (finales[0].y + finales[1].y) / 2, arriba = finales[0].y <= finales[1].y ? 0 : 1;
      finales[arriba].y = medio - 7; finales[1 - arriba].y = medio + 7;
    }
    finales.forEach(function (f) {
      el('text', { x: W - 6, y: Math.max(M.a + 6, Math.min(H - M.b - 2, f.y + 4)), 'text-anchor': 'end', style: 'fill:' + f.color + ';' + fuente(800, FS) }, linea).textContent = f.txt;
    });
    R.etiquetasX.forEach(function (e) {
      el('text', { x: xDe(e.k), y: H - 8, 'text-anchor': e.periodo ? 'start' : 'middle', style: 'fill:rgba(255,255,255,' + (e.periodo ? .9 : .7) + ');' + fuente(e.periodo ? 700 : 600, FS) }, linea).textContent = e.etq;
    });
    cursor = el('line', { y1: M.a - 4, y2: H - M.b + 4, style: 'stroke:var(--c-rojo);stroke-width:2;stroke-dasharray:.1 3.6;stroke-linecap:round' }, linea);
    linea.addEventListener('click', function (ev) {
      var r = linea.getBoundingClientRect(), x = (ev.clientX - r.left) * W / r.width;
      detener(); i = Math.round((x - M.i) / (W - M.i - M.d) * (R.minutos.length - 1)); actualizar();
    });
    // A2 · cursor, recorte de lo jugado y quiebres: al cruzar uno (avanzando de a poco) crece un anillo y la frase lo nombra
    var fraseLinea = document.getElementById('frase-linea'), iLinea = null, VENTANA_FRASE = 8;  // minutos que la frase sigue nombrando el quiebre
    function marcarLinea() {
      if (!cursor) return;
      var x = xDe(i), reciente = null;
      cursor.setAttribute('x1', x); cursor.setAttribute('x2', x); recorte.setAttribute('width', x);
      marcasQ.forEach(function (mq) {
        var q = mq.q, hecho = q.k <= i;
        if (mq.texto) mq.texto.style.opacity = hecho ? 1 : .35;
        if (q.fuerte && hecho && i - q.k < VENTANA_FRASE) reciente = q;
        if (q.fuerte && MOV && iLinea != null && i > iLinea && i - iLinea <= 3 && q.k > iLinea && q.k <= i) {
          var m = R.minutos[q.k]; MOV.pulso(linea, xDe(q.k), yDe(m.ia == null ? 50 : m.ia));
        }
      });
      fraseLinea.textContent = reciente ? R.minutos[reciente.k].etq + ' · ' + reciente.corto : 'Lo ya jugado, en firme; lo que falta, tenue. 1T y 2T: tiempos; PR: prórroga.';
      iLinea = i;
    }
    i = R.inicio || 0;
    actualizar();
  }

  // ---------- vistas, cajón (teléfono), entrada y ícono ----------
  function mostrar(vista) {
    cuerpo.dataset.vista = vista;
    document.querySelectorAll('nav.vistas [data-vista]').forEach(function (b) {
      if (b.dataset.vista === vista) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current');
    });
    if (location.hash !== '#' + vista) history.replaceState(null, '', '#' + vista);
    cerrarCajon(); window.scrollTo(0, 0);
  }
  var abridorCajon = null;
  function cajonInerte() {  // en el teléfono, la barra cerrada no recibe foco y, abierta, el contenido de atrás tampoco (el botón Filtros la cierra)
    if (!D) return;
    var abierto = cuerpo.classList.contains('cajon'), tel = movil();
    document.querySelector('aside.barra').inert = tel && !abierto;
    document.querySelector('.contenido').inert = tel && abierto;
    document.querySelectorAll('nav [data-cajon]').forEach(function (b) { b.setAttribute('aria-expanded', String(abierto)); });
  }
  function abrirCajon(boton) {
    abridorCajon = boton || null;
    cuerpo.classList.add('cajon'); cajonInerte();
    var primero = document.querySelector('aside.barra .barra-contenido button:not([disabled])');
    if (primero) primero.focus();
  }
  function cerrarCajon() {
    var estaba = cuerpo.classList.contains('cajon');
    cuerpo.classList.remove('cajon'); cajonInerte();
    if (estaba && abridorCajon) { abridorCajon.focus(); abridorCajon = null; }
  }
  // A8 · Portada → Explorar: la vista que se va se apaga y la nueva aparece (OjoMov.vista)
  function cambiarVista(vista, despues) {
    var hacer = function () { mostrar(vista); if (despues) despues(); };
    if (cuerpo.dataset.vista === vista) { if (despues) despues(); return; }
    if (MOV) MOV.vista(hacer); else hacer();
  }
  document.querySelectorAll('button[data-vista]').forEach(function (b) { b.addEventListener('click', function () { cambiarVista(b.dataset.vista); }); });
  // Enlaces entre vistas: data-ir="vista#ancla"; con data-rival abre esa ficha y con data-situacion resalta esa tarjeta de la matriz
  function irAVista(vista, ancla, op) {
    if (op.rival) { irAFicha(op.rival); return; }
    cambiarVista(vista, function () {
      var destino = ancla ? document.getElementById(ancla) : null;
      if (op.situacion) {
        var t = Array.prototype.filter.call(document.querySelectorAll('.situacion'), function (a) { return a.querySelector('h3').textContent === op.situacion; })[0];
        if (t) destino = t;
      }
      if (!destino) return;
      if (MOV) MOV.irA(destino, { bloque: op.situacion ? 'center' : 'start' }); else destino.scrollIntoView();
    });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-ir]'); if (!b) return;
    var partes = b.getAttribute('data-ir').split('#');
    irAVista(partes[0], partes[1], { rival: b.getAttribute('data-rival'), situacion: b.getAttribute('data-situacion') });
  });
  // A5 · de la tarjeta del principio al partido que lo ilustra: desplazamiento y resaltado
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.ir-caso')) return;
    var destino = document.getElementById('caso');
    cambiarVista('explorar', function () {
      if (MOV) MOV.irA(destino, { foco: true }); else { destino.scrollIntoView(); destino.focus({ preventScroll: true }); }
    });
  });
  // A7 · conteo de los KPI, una sola vez y solo si la portada está a la vista
  var contados = false;
  function contarKPIs() {
    if (contados || !MOV || cuerpo.dataset.vista !== 'portada') return;
    contados = true;
    document.querySelectorAll('.kpi strong').forEach(MOV.contar);
  }
  document.querySelectorAll('[data-cajon]').forEach(function (b) {
    b.addEventListener('click', function () { if (cuerpo.classList.contains('cajon')) cerrarCajon(); else abrirCajon(b.tagName === 'BUTTON' ? b : null); });
  });
  window.matchMedia('(max-width: 900px)').addEventListener('change', function () {  // al cambiar de tamaño, el estado correcto de cada lado
    if (!movil()) cuerpo.classList.remove('cajon');
    cajonInerte();
    if (D) ocultarBarra(cuerpo.classList.contains('barra-oculta'));
  });
  window.addEventListener('keydown', function (e) { if (e.key === 'Escape') cerrarCajon(); });
  // El encabezado crece en el teléfono: al desplazarse a una sección se usa su alto real (--alto-enc-real)
  var enc = document.querySelector('header.enc');
  function altoEnc() { if (enc) document.documentElement.style.setProperty('--alto-enc-real', enc.offsetHeight + 'px'); }
  altoEnc();
  window.addEventListener('resize', altoEnc);
  if (enc && window.ResizeObserver) new ResizeObserver(altoEnc).observe(enc);

  if (!D) {
    document.getElementById('sin-datos').hidden = false;
    document.querySelectorAll('.vista').forEach(function (v) { v.remove(); });
  } else {
    var variante = (/[?&]barra=(sobre|riel|chips)(&|$)/.exec(location.search) || [])[1];  // para probar las variantes 3a–3c
    if (variante) cuerpo.setAttribute('data-barra-variante', variante);
    render(); montarBarra(); conectarBarra(); reproductor();
    document.querySelector('[data-slot="tira"]').addEventListener('click', function (e) { if (e.target.closest('[data-ocultar]')) ocultarBarra(false, true); });
    var oculta = false;
    try { oculta = localStorage.getItem('ojo.barraOculta') === '1'; } catch (e) { /* sin almacenamiento */ }
    ocultarBarra(oculta);
    mostrar(['#explorar', '#decidir', '#metodo'].indexOf(location.hash) >= 0 ? location.hash.slice(1) : 'portada');
  }

  if (window.OjoMarca) OjoMarca.loop(document.getElementById('loop-icono'), { estatico: reducido() });
  var intro = document.getElementById('intro');
  if (!window.__ojoMostrarIntro || !window.OjoMarca) { intro.remove(); document.documentElement.classList.remove('con-intro'); if (D) contarKPIs(); return; }
  var control = null, cerrada = false;
  function cerrar() {
    if (cerrada) return; cerrada = true;
    intro.classList.add('saliendo'); document.documentElement.classList.remove('con-intro');
    setTimeout(function () { if (control) control.detener(); intro.remove(); if (D) contarKPIs(); }, 650);
  }
  control = OjoMarca.intro(document.getElementById('intro-lienzo'), { segundos: 5, alTerminar: cerrar });
  setTimeout(cerrar, 6500);  // respaldo: si el navegador no dibuja cuadros (pestaña en segundo plano), la entrada no se queda puesta
  intro.addEventListener('click', cerrar);
  window.addEventListener('keydown', function (e) { if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') cerrar(); });
})();
