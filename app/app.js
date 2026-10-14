/* Ojo de Águila · lógica de la app (app/maqueta.html). Se edita directo: Python no genera este archivo.
   Lee window.OJO_DATOS (../outputs/app/datos.js, escrito por scripts/08_maqueta.py) y dibuja la portada,
   la barra lateral (compacta, plegable y ocultable), el contenido de Explorar y el reproductor.
   NOTA1: maqueta. Los controles de la barra cambian de estado pero todavía no recalculan la vista. */
(function () {
  'use strict';
  var D = window.OJO_DATOS;
  var NS = 'http://www.w3.org/2000/svg';
  var BANDAS = [40, 60];  // igual que indice.bandas en config/params.yaml: bajo 40 reactivo, sobre 60 proactivo
  var cuerpo = document.body;

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

  // ---------- canchas con Voronoi ----------
  var OJO_LEYENDA = '<svg viewBox="0 14 102 70" width="34" height="24" aria-hidden="true">' +
    '<polygon points="12,19.6 86,30.8 99,46.7 95.4,50.6 24.1,29.2" style="fill:var(--c-acento);stroke:var(--c-acento);stroke-width:2"/>' +
    '<path d="M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z" style="fill:var(--c-azul);stroke:var(--c-acento);stroke-width:6"/>' +
    '<g clip-path="url(#clip-almendra)"><circle cx="54" cy="54" r="24" style="fill:var(--c-acento)"/>' +
    '<path d="M49.3 47.5L58.7 47.5L61.6 56.5L54 62L46.4 56.5Z" style="fill:var(--c-azul);stroke:var(--c-azul);stroke-width:3"/></g></svg>';
  var CANCHA = '<svg class="cancha-svg" viewBox="-3 -3 126 86" role="img" aria-label="Foto 360 con el Voronoi del momento">' +
    '<rect x="0" y="0" width="120" height="80" style="fill:url(#fuera)"/><g class="capa"></g>' +
    '<g class="lineas"><rect x="0" y="0" width="120" height="80"/><line x1="60" y1="0" x2="60" y2="80"/><circle cx="60" cy="40" r="10"/>' +
    '<rect x="0" y="18" width="18" height="44"/><rect x="102" y="18" width="18" height="44"/><rect x="0" y="30" width="6" height="20"/><rect x="114" y="30" width="6" height="20"/></g>' +
    '<text class="sin-foto" x="60" y="42" text-anchor="middle">Sin foto 360 en este minuto</text></svg>';

  function crearCancha(contenedor) { contenedor.innerHTML = CANCHA; return contenedor.querySelector('svg'); }
  function ojo(x, y, padre) {
    var s = 4.6 / 102, g = el('g', { transform: 'translate(' + (x - 54 * s) + ',' + (y - 54 * s) + ') scale(' + s + ')' }, padre);
    el('polygon', { points: '12,19.6 86,30.8 99,46.7 95.4,50.6 24.1,29.2', style: 'fill:var(--c-acento);stroke:var(--c-acento);stroke-width:2' }, g);
    el('path', { d: 'M4 52A50.3 50.3 0 0 1 24.1 29.2L95.4 50.6A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z', style: 'fill:var(--c-azul);stroke:var(--c-acento);stroke-width:6' }, g);
    var iris = el('g', { 'clip-path': 'url(#clip-almendra)' }, g);
    el('circle', { cx: 54, cy: 54, r: 24, style: 'fill:var(--c-acento)' }, iris);
    el('path', { d: 'M49.3 47.5L58.7 47.5L61.6 56.5L54 62L46.4 56.5Z', style: 'fill:var(--c-azul);stroke:var(--c-azul);stroke-width:3' }, iris);
  }
  function dibujarFoto(svg, f) {
    var capa = svg.querySelector('.capa');
    while (capa.firstChild) capa.removeChild(capa.firstChild);
    svg.classList.toggle('vacia', !f);
    if (!f) return;
    f.visible.forEach(function (v) { el('polygon', { points: pares(v), style: 'fill:var(--c-azul)' }, capa); });
    f.celdas.forEach(function (c, k) {
      el('polygon', { points: pares(c), style: f.propias[k] ? 'fill:var(--c-acento);fill-opacity:.82;stroke:var(--c-azul);stroke-width:.35'
                                                         : 'fill:#fff;fill-opacity:.08;stroke:var(--c-azul);stroke-width:.35' }, capa);
    });
    f.frontera.forEach(function (l) { el('polyline', { points: pares(l), style: 'fill:none;stroke:#fff;stroke-width:.8;stroke-linecap:round' }, capa); });
    f.visible.forEach(function (v) { el('polygon', { points: pares(v), style: 'fill:none;stroke:rgba(255,255,255,.5);stroke-width:.3;stroke-dasharray:1.2 .9' }, capa); });
    if (f.flecha) {
      el('line', { x1: f.flecha[0], y1: f.flecha[1], x2: f.flecha[2], y2: f.flecha[3], 'marker-end': 'url(#' + (f.eq ? 'punta-eq' : 'punta-riv') + ')',
                   style: 'stroke:' + (f.eq ? 'var(--c-acento)' : '#fff') + ';stroke-width:.6' }, capa);
    }
    f.jugadores.forEach(function (j) {
      if (j[3]) el('circle', { cx: j[0], cy: j[1], r: 2.8, style: 'fill:none;stroke-width:.5;stroke:' + (f.eq ? 'var(--c-acento)' : '#fff') }, capa);
      if (j[2]) ojo(j[0], j[1], capa);
      else el('circle', { cx: j[0], cy: j[1], r: .95, style: 'fill:#fff;stroke:var(--c-azul);stroke-width:.35' }, capa);
    });
  }

  // ---------- piezas de contenido ----------
  function tarjeta(p, grande) {
    var caso = p.caso ? '<span class="insignia">' + esc(p.caso) + '</span>' : '';
    var cifras = '<dl class="cifras"><div><dt>' + esc(D.nuevo) + '</dt><dd>' + esc(p.jardine) + '</dd></div>' +
      '<div><dt>Solari y Ortiz</dt><dd>' + esc(p.previos) + '</dd></div>' +
      '<div><dt>Diferencia</dt><dd>' + esc(p.diferencia) + '<small>' + esc(p.intervalo) + '</small></dd></div>' +
      '<div><dt>Torneos en la misma dirección</dt><dd>' + esc(p.torneos) + '</dd></div></dl>';
    var extra = grande ? '<p><strong>Qué significa.</strong> ' + esc(p.significa) + '</p><p><strong>Lectura para el cuerpo técnico (hipótesis).</strong> ' + esc(p.uso) + '</p>' : '';
    return '<article class="tarjeta' + (grande ? ' grande' : '') + '"><header><h3>' + esc(p.titulo) + '</h3>' + caso + '</header>' +
      '<p class="frase">' + esc(p.frase) + '</p>' + cifras + extra + '<span class="estado">' + esc(p.estado) + '</span></article>';
  }
  function montecarlo(m) {
    var marcadores = m.marcadores.slice(0, 3).map(function (x) { return esc(x[0]) + ' (' + pct(x[1]) + ')'; }).join(' · ');
    return '<article class="mc"><h3>' + esc(m.titulo) + '</h3><p>' + esc(m.texto) + '</p>' +
      '<div class="mc-barra" role="img" aria-label="Gana ' + pct(m.gana) + ', empate ' + pct(m.empata) + ', pierde ' + pct(m.pierde) + '">' +
      '<span class="g" style="width:' + (m.gana * 100).toFixed(1) + '%">' + pct(m.gana) + '</span>' +
      '<span class="e" style="width:' + (m.empata * 100).toFixed(1) + '%">' + pct(m.empata) + '</span>' +
      '<span class="p" style="width:' + (m.pierde * 100).toFixed(1) + '%">' + pct(m.pierde) + '</span></div>' +
      '<p class="mc-ley"><span class="cg"></span>Gana ' + esc(D.equipo) + ' <span class="ce"></span>Empate <span class="cp"></span>Gana ' + esc(D.rival) + '</p>' +
      '<p class="nota">Goles esperados: ' + m.goles_favor.toFixed(2) + ' – ' + m.goles_contra.toFixed(2) + '. Marcadores más frecuentes: ' + marcadores + '.</p></article>';
  }
  function graficaTorneos(contenedor, filas) {
    var W = 640, H = 270, M = { i: 36, d: 10, a: 22, b: 44 }, svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': 'Índice medio por torneo' });
    contenedor.innerHTML = ''; contenedor.appendChild(svg);
    el('rect', { x: 0, y: 0, width: W, height: H, rx: 8, style: 'fill:var(--c-azul)' }, svg);
    var ancho = (W - M.i - M.d) / filas.length;
    function y(v) { return M.a + (H - M.a - M.b) * (1 - v / 100); }
    [0, 50, 100].forEach(function (v) {
      el('line', { x1: M.i, x2: W - M.d, y1: y(v), y2: y(v), style: 'stroke:rgba(255,255,255,' + (v === 50 ? .35 : .12) + ');stroke-dasharray:' + (v === 50 ? '3 3' : 'none') }, svg);
      el('text', { x: M.i - 6, y: y(v) + 3, 'text-anchor': 'end', style: 'fill:rgba(255,255,255,.6);font:600 10px Poppins, sans-serif' }, svg).textContent = v;
    });
    filas.forEach(function (f, k) {
      var x = M.i + ancho * k + ancho * .2, w = ancho * .6;
      el('rect', { x: x, y: y(f.propio), width: w, height: y(0) - y(f.propio), rx: 2, style: f.nuevo ? 'fill:var(--c-acento)' : 'fill:rgba(255,255,255,.45)' }, svg);
      el('text', { x: x + w / 2, y: y(f.propio) - 5, 'text-anchor': 'middle', style: 'fill:#fff;font:800 11px Poppins, sans-serif' }, svg).textContent = Math.round(f.propio);
      el('circle', { cx: x + w / 2, cy: y(f.rival), r: 5, style: 'fill:#fff;stroke:var(--c-azul);stroke-width:1.5' }, svg);
      el('text', { x: x + w / 2, y: H - 26, 'text-anchor': 'middle', style: 'fill:rgba(255,255,255,.85);font:700 10px Poppins, sans-serif' }, svg).textContent = f.torneo;
      el('text', { x: x + w / 2, y: H - 12, 'text-anchor': 'middle', style: 'fill:rgba(255,255,255,.6);font:600 9px Poppins, sans-serif' }, svg).textContent = f.entrenador;
    });
  }

  // ---------- barra lateral v3: compacta, plegable y ocultable ----------
  function chip(etq, activo, clase, titulo) {
    return '<button type="button" class="chip-t ' + (clase || '') + '" data-toggle aria-pressed="' + !!activo + '"' + (titulo ? ' title="' + esc(titulo) + '"' : '') + '>' + esc(etq) + '</button>';
  }
  function seccion(id, titulo, contenido, abierta, clase) {
    return '<details class="seccion ' + (clase || '') + '" data-seccion="' + id + '"' + (abierta ? ' open' : '') + '><summary>' + esc(titulo) +
      '<span class="resumen-sec"></span></summary><div class="cuerpo-sec">' + contenido + '</div></details>';
  }
  function grupos(lista) {
    return lista.map(function (g) {
      return '<p class="sub">' + esc(g.grupo) + '</p><div class="chips-s">' + g.opciones.map(function (o) { return chip(o.etq, o.activo, 'redondo'); }).join('') + '</div>';
    }).join('');
  }
  function tamanoNombre(nombre) { return Math.min(30, Math.floor(228 / (0.8 * nombre.length))); }  // igual que app.tamano_nombre
  function renderBarra(b) {
    var rivales = b.rivales.map(function (r) {
      return '<li><button type="button" class="rival-btn" data-rival="' + esc(r[0]) + '" data-n="' + r[1] + '"><span>' + esc(r[0]) + '</span><span class="n">' + r[1] + '</span></button></li>';
    }).join('');
    var rival = '<div class="placa-rival"><span class="sel">Seleccionado</span><strong id="rival-nombre" style="font-size:' + tamanoNombre(b.rival.nombre) + 'px">' + esc(b.rival.nombre) + '</strong>' +
      '<span class="cinta-n" id="rival-n">' + b.rival.partidos + ' partidos</span></div><ul class="lista-rivales">' + rivales + '</ul>' +
      (b.rivales.length > 4 ? '<button type="button" class="ver-todos">Ver todos (' + b.rivales.length + ')</button>' : '');
    var torneos = '<div class="rejilla-3">' + b.torneos.map(function (t) { return chip(t.id, t.activo, t.prueba ? 'prueba' : '', t.prueba ? 'Torneo de prueba: el modelo no lo vio' : ''); }).join('') + '</div>' +
      '<p class="aviso-prueba">Línea punteada: torneo de prueba (CL26).</p>';
    var condicion = '<div class="segmentado" role="radiogroup" aria-label="Condición">' + ['Todos', 'Local', 'Visita'].map(function (c) {
      return '<button type="button" role="radio" aria-checked="' + (c === b.condicion) + '" class="seg">' + c + '</button>'; }).join('') + '</div>';
    var partidos = '<ul class="lista-partidos">' + b.partidos.map(function (p) {
      return '<li><button type="button" class="partido-btn" aria-pressed="' + p.activo + '"><span class="fecha">' + esc(p.fecha) + '</span><span>' + esc(p.etapa) +
        '</span><strong>' + esc(p.marcador) + '</strong></button></li>'; }).join('') + '</ul>';
    html('barra',
      '<div class="barra-cab"><span class="titulo-barra">Filtros</span><div class="acciones-cab"><button type="button" class="enlace" data-volver>Restablecer</button>' +
      '<button type="button" class="btn-ocultar" data-ocultar aria-label="Ocultar filtros" aria-expanded="true">‹</button></div></div>' +
      seccion('rival', 'Rival', rival, true) + seccion('torneo', 'Torneo', torneos, true) +
      seccion('momento', 'Momento', grupos(b.momento), true) + seccion('condicion', 'Condición', condicion, true) +
      seccion('partidos', 'Partidos', partidos, false) +
      seccion('mas', 'Más filtros', grupos(b.mas), false, 'secundaria') +
      '<div class="pie-barra"><p class="muestra">' + esc(b.muestra) + '</p>' +
      '<button type="button" class="btn-borde" disabled title="Llega con resumenes.json">Ficha de 10 segundos · pronto</button></div>');
  }
  function activos(sel, raiz) { return Array.prototype.map.call((raiz || document).querySelectorAll(sel), function (b) { return b.textContent; }); }
  function actualizarResumenes() {
    var total = 0;
    document.querySelectorAll('details.seccion').forEach(function (d) {
      var id = d.dataset.seccion, txt = '', n = 0;
      if (id === 'rival') txt = document.getElementById('rival-nombre').textContent;
      else if (id === 'condicion') { txt = activos('.seg[aria-checked="true"]', d)[0] || 'Todos'; n = txt === 'Todos' ? 0 : 1; }
      else if (id === 'partidos') { var p = d.querySelector('.partido-btn[aria-pressed="true"] span:nth-child(2)'); txt = p ? p.textContent : d.querySelectorAll('.partido-btn').length + ''; }
      else { var a = activos('[data-toggle][aria-pressed="true"]', d); n = a.length; txt = a.length ? a.join(', ') : (id === 'mas' ? 'entrenador, fase, balón parado' : 'Todos'); }
      total += n;
      d.querySelector('.resumen-sec').textContent = txt;
    });
    document.querySelectorAll('[data-cuenta-filtros]').forEach(function (c) { c.textContent = total; });
  }
  function conectarBarra() {
    var aside = document.querySelector('aside.barra');
    aside.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.hasAttribute('data-toggle')) b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      else if (b.classList.contains('seg')) document.querySelectorAll('.seg').forEach(function (o) { o.setAttribute('aria-checked', o === b ? 'true' : 'false'); });
      else if (b.classList.contains('partido-btn')) document.querySelectorAll('.partido-btn').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      else if (b.classList.contains('rival-btn')) cambiarRival(b);
      else if (b.classList.contains('ver-todos')) { var l = aside.querySelector('.lista-rivales'); l.classList.toggle('todos'); b.textContent = l.classList.contains('todos') ? 'Ver menos' : 'Ver todos (' + l.children.length + ')'; }
      else if (b.hasAttribute('data-ocultar')) ocultarBarra(!cuerpo.classList.contains('barra-oculta'));
      else if (b.hasAttribute('data-volver')) location.reload();
      actualizarResumenes();
    });
  }
  function cambiarRival(b) {
    var nombre = document.getElementById('rival-nombre'), conteo = document.getElementById('rival-n');
    var antes = [nombre.textContent, parseInt(conteo.textContent, 10)];
    nombre.textContent = b.dataset.rival; conteo.textContent = b.dataset.n + ' partidos';
    nombre.style.fontSize = tamanoNombre(b.dataset.rival) + 'px';
    b.dataset.rival = antes[0]; b.dataset.n = antes[1];
    b.firstElementChild.textContent = antes[0]; b.lastElementChild.textContent = antes[1];
    cerrarCajon();
  }
  function ocultarBarra(oculta) {
    cuerpo.classList.toggle('barra-oculta', oculta);
    document.querySelectorAll('[data-ocultar][aria-expanded]').forEach(function (b) { b.setAttribute('aria-expanded', String(!oculta)); });
    try { localStorage.setItem('ojo.barraOculta', oculta ? '1' : '0'); } catch (e) { /* sin almacenamiento: solo en esta visita */ }
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
    html('filtros', X.filtros.map(function (f) { return '<button type="button" class="filtro">' + esc(f) + '<span aria-hidden="true">×</span></button>'; }).join(''));
    html('principio', tarjeta(X.principio, true));
    texto('caso-titulo', X.caso.titulo);
    html('caso-chips', X.caso.chips.map(function (c) { return '<div class="dato"><span>' + esc(c[0]) + '</span><strong>' + esc(c[1]) + '</strong></div>'; }).join(''));
    html('caso-quiebres', X.caso.quiebres.map(function (q) { return '<li class="' + (q[2] ? 'caso' : '') + '"><span class="min">' + esc(q[0]) + '</span>' + esc(q[1]) + '</li>'; }).join(''));
    html('montecarlo', X.montecarlo.map(montecarlo).join(''));
    texto('lectura', X.lectura); texto('metodo', X.metodo);
    html('pendientes', X.pendientes.map(function (p) { return '<article class="pendiente"><span class="estado">En construcción · ' + esc(p.requisito) + '</span><h3>' + esc(p.titulo) + '</h3><p>' + esc(p.texto) + '</p></article>'; }).join(''));
    html('notas', X.notas.map(function (n) { return '<p class="nota">' + esc(n) + '</p>'; }).join(''));
    renderBarra(D.barra);
    document.querySelectorAll('.filtro').forEach(function (b) { b.addEventListener('click', function () { b.remove(); }); });
  }

  // ---------- reproductor ----------
  function reproductor() {
    var R = D.reproductor, svg = crearCancha(document.querySelector('[data-slot="cancha-repro"]'));
    var repro = document.getElementById('repro'), tiempo = document.getElementById('tiempo');
    var reloj = document.getElementById('reloj'), accion = document.getElementById('accion'), play = document.getElementById('play');
    var modo = 'partido', i = 0, timer = null, VEL = { partido: 650, jugada: 1100 };  // ms por paso (solo presentación)
    var btnJugada = document.getElementById('btn-jugada');
    if (!R.jugada || !R.jugada.fotos.length) btnJugada.hidden = true; else btnJugada.textContent = R.jugada.titulo;

    function etiquetaIndice(v) { return v >= BANDAS[1] ? 'proactivo' : (v <= BANDAS[0] ? 'reactivo' : 'equilibrado'); }
    function formato(c, v) { if (v == null) return '—'; if (c.formato === 'pct') return pct(v); if (c.formato === 'yd') return v.toFixed(1) + ' yd'; return v.toFixed(2); }
    function radar(m) {
      var s = document.getElementById('radar'); while (s.firstChild) s.removeChild(s.firstChild);
      var cx = 160, cy = 114, Rr = 76, n = R.componentes.length;
      function punto(k, z) { var a = -Math.PI / 2 + 2 * Math.PI * k / n, r = Rr * (Math.max(-2.5, Math.min(2.5, z == null ? 0 : z)) + 2.5) / 5; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
      el('rect', { x: 0, y: 0, width: 320, height: 230, rx: 8, style: 'fill:var(--c-azul)' }, s);
      [-2.5, 0, 2.5].forEach(function (z) {
        var ps = []; for (var k = 0; k < n; k++) ps.push(punto(k, z).join(','));
        el('polygon', { points: ps.join(' '), style: 'fill:none;stroke:rgba(255,255,255,' + (z === 0 ? .45 : .15) + ');stroke-width:' + (z === 0 ? 1.2 : .8) }, s);
      });
      R.componentes.forEach(function (c, k) {
        var p = punto(k, 2.5), a = -Math.PI / 2 + 2 * Math.PI * k / n;
        el('line', { x1: cx, y1: cy, x2: p[0], y2: p[1], style: 'stroke:rgba(255,255,255,.15)' }, s);
        el('text', { x: cx + (Rr + 12) * Math.cos(a), y: cy + (Rr + 12) * Math.sin(a) + 3, 'text-anchor': Math.abs(Math.cos(a)) < .2 ? 'middle' : (Math.cos(a) > 0 ? 'start' : 'end'),
                     style: 'fill:rgba(255,255,255,.85);font:600 9px Poppins, sans-serif' }, s).textContent = c.radar;
      });
      [['zr', 'fill:#fff;fill-opacity:.12;stroke:#fff;stroke-width:1.4'], ['za', 'fill:var(--c-acento);fill-opacity:.35;stroke:var(--c-acento);stroke-width:2']].forEach(function (par) {
        var ps = []; for (var k = 0; k < n; k++) ps.push(punto(k, m[par[0]][k]).join(','));
        el('polygon', { points: ps.join(' '), style: par[1] }, s);
      });
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
    function mostrarFoto(f) {
      dibujarFoto(svg, f);
      accion.textContent = f ? f.reloj + ' · ' + f.texto + ' · control del ' + D.equipo + ': ' + pct(f.control) : '';
    }
    function lista() { return modo === 'partido' ? R.minutos : R.jugada.fotos; }
    function actualizar() {
      var L = lista(); i = Math.max(0, Math.min(i, L.length - 1)); tiempo.max = L.length - 1; tiempo.value = i;
      if (modo === 'partido') {
        var m = R.minutos[i]; mostrarFoto(m.foto == null ? null : R.fotos[m.foto]); reloj.textContent = m.etq + ' · ' + m.marcador;
        panelMinuto(m); marcarLinea();
      } else {
        var f = R.jugada.fotos[i]; mostrarFoto(f); reloj.textContent = f.reloj;
        var mm = R.minutos[R.jugada.minuto]; if (mm) panelMinuto(mm);
      }
    }
    function detener() { if (timer) clearInterval(timer); timer = null; play.textContent = '▶'; play.setAttribute('aria-label', 'Reproducir'); repro.classList.remove('reproduciendo'); }
    function reproducir() {
      if (i >= lista().length - 1) i = 0;
      play.textContent = '❚❚'; play.setAttribute('aria-label', 'Pausar'); repro.classList.add('reproduciendo');
      timer = setInterval(function () { if (i >= lista().length - 1) { detener(); return; } i++; actualizar(); }, VEL[modo]);
    }
    play.addEventListener('click', function () { if (timer) detener(); else reproducir(); });
    tiempo.addEventListener('input', function () { detener(); i = +tiempo.value; actualizar(); });
    repro.addEventListener('keydown', function (e) {
      if (e.target.tagName === 'INPUT') return;
      if (e.key === ' ') { e.preventDefault(); if (timer) detener(); else reproducir(); }
      if (e.key === 'ArrowRight') { detener(); i++; actualizar(); }
      if (e.key === 'ArrowLeft') { detener(); i--; actualizar(); }
    });
    document.querySelectorAll('.modos button').forEach(function (b) {
      b.addEventListener('click', function () {
        detener(); modo = b.dataset.modo; i = 0;
        document.querySelectorAll('.modos button').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        document.querySelector('.linea-js').hidden = modo !== 'partido'; actualizar();
      });
    });
    // Línea del índice (modo partido): clic para saltar
    var linea = document.getElementById('linea'), W = 640, H = 210, M = { i: 34, d: 8, a: 40, b: 24 }, cursor;
    function xDe(k) { return M.i + (W - M.i - M.d) * k / Math.max(R.minutos.length - 1, 1); }
    function yDe(v) { return M.a + (H - M.a - M.b) * (1 - v / 100); }
    el('rect', { x: 0, y: 0, width: W, height: H, rx: 8, style: 'fill:var(--c-azul)' }, linea);
    [BANDAS[0], 50, BANDAS[1]].forEach(function (v) {
      el('line', { x1: M.i, x2: W - M.d, y1: yDe(v), y2: yDe(v), style: 'stroke:rgba(255,255,255,' + (v === 50 ? .3 : .12) + ');stroke-dasharray:3 3' }, linea);
      el('text', { x: M.i - 6, y: yDe(v) + 3, 'text-anchor': 'end', style: 'fill:rgba(255,255,255,.6);font:600 9px Poppins, sans-serif' }, linea).textContent = v;
    });
    R.etiquetasX.forEach(function (e) { if (e.periodo && e.k > 0) el('line', { x1: xDe(e.k) - .5, x2: xDe(e.k) - .5, y1: M.a, y2: H - M.b, style: 'stroke:rgba(255,255,255,.35)' }, linea); });
    var nivel = 0;
    R.quiebres.forEach(function (q) {
      el('line', { x1: xDe(q.k), x2: xDe(q.k), y1: M.a, y2: H - M.b, style: 'stroke:' + (q.favor ? 'var(--c-acento)' : '#fff') + ';stroke-width:' + (q.fuerte ? 1.6 : .8) + ';opacity:' + (q.fuerte ? .9 : .45) }, linea);
      if (!q.fuerte) return;  // solo goles y expulsiones llevan etiqueta; escalonadas para no encimarse
      el('text', { x: xDe(q.k), y: 12 + 11 * (nivel++ % 3), 'text-anchor': 'middle', style: 'fill:' + (q.favor ? 'var(--c-acento)' : '#fff') + ';font:700 9px Poppins, sans-serif' }, linea).textContent = q.corto;
    });
    [['ir', '#fff', 1.4], ['ia', 'var(--c-acento)', 2.2]].forEach(function (s) {
      var ps = []; R.minutos.forEach(function (m, k) { if (m[s[0]] != null) ps.push(xDe(k) + ',' + yDe(m[s[0]])); });
      el('polyline', { points: ps.join(' '), style: 'fill:none;stroke:' + s[1] + ';stroke-width:' + s[2] }, linea);
    });
    R.etiquetasX.forEach(function (e) {
      el('text', { x: xDe(e.k), y: H - 8, 'text-anchor': e.periodo ? 'start' : 'middle', style: 'fill:rgba(255,255,255,' + (e.periodo ? .9 : .6) + ');font:' + (e.periodo ? 700 : 600) + ' 9px Poppins, sans-serif' }, linea).textContent = e.etq;
    });
    cursor = el('line', { y1: M.a - 4, y2: H - M.b + 4, style: 'stroke:#fff;stroke-width:1.2' }, linea);
    linea.addEventListener('click', function (ev) {
      var r = linea.getBoundingClientRect(), x = (ev.clientX - r.left) * W / r.width;
      detener(); i = Math.round((x - M.i) / (W - M.i - M.d) * (R.minutos.length - 1)); actualizar();
    });
    function marcarLinea() { if (cursor) { cursor.setAttribute('x1', xDe(i)); cursor.setAttribute('x2', xDe(i)); } }
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
  function cerrarCajon() { cuerpo.classList.remove('cajon'); }
  document.querySelectorAll('button[data-vista]').forEach(function (b) { b.addEventListener('click', function () { mostrar(b.dataset.vista); }); });
  document.querySelectorAll('[data-cajon]').forEach(function (b) { b.addEventListener('click', function () { cuerpo.classList.toggle('cajon'); }); });
  window.addEventListener('keydown', function (e) { if (e.key === 'Escape') cerrarCajon(); });

  if (!D) {
    document.getElementById('sin-datos').hidden = false;
    document.querySelectorAll('.vista').forEach(function (v) { v.remove(); });
  } else {
    render(); conectarBarra(); actualizarResumenes(); reproductor();
    var oculta = false;
    try { oculta = localStorage.getItem('ojo.barraOculta') === '1'; } catch (e) { /* sin almacenamiento */ }
    ocultarBarra(oculta);
    mostrar(location.hash === '#explorar' ? 'explorar' : 'portada');
  }

  var reducir = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (window.OjoMarca) OjoMarca.loop(document.getElementById('loop-icono'), { estatico: reducir });
  var intro = document.getElementById('intro');
  if (!window.__ojoMostrarIntro || !window.OjoMarca) { intro.remove(); document.documentElement.classList.remove('con-intro'); return; }
  var control = null, cerrada = false;
  function cerrar() {
    if (cerrada) return; cerrada = true;
    intro.classList.add('saliendo'); document.documentElement.classList.remove('con-intro');
    setTimeout(function () { if (control) control.detener(); intro.remove(); }, 650);
  }
  control = OjoMarca.intro(document.getElementById('intro-lienzo'), { segundos: 5, alTerminar: cerrar });
  intro.addEventListener('click', cerrar);
  window.addEventListener('keydown', function (e) { if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') cerrar(); });
})();
