/* Ojo de Águila · Pregúntale al motor (maqueta: app/maquetachatbot.html, bloque 6 de El partido).
   Responde con lo que ya trae la página: el partido que muestra El partido (window.OjoApp.partido()), lo que dice el
   motor de cada rival (D.decidir.fichas), la matriz de situaciones y el glosario de Método. No usa internet ni
   inteligencia artificial: entiende la pregunta por palabras clave y arma la respuesta con los números; si la pregunta
   no tiene datos, lo dice. NOTA1: maqueta para decidir si entra a la entrega. */
(function () {
  'use strict';
  var D = window.OJO_DATOS, API = window.OjoApp;
  var raiz = document.querySelector('[data-slot="motor"]');
  if (!D || !API || !raiz) return;
  var BANDAS = (D.reproductor && D.reproductor.bandas) || [40, 60];
  var reducido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- utilidades ----------
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[¿?¡!.,;:()"]/g, ' ').replace(/\s+/g, ' ').trim(); }
  function media(l) { var v = l.filter(function (x) { return x != null && !isNaN(x); }); return v.length ? v.reduce(function (a, b) { return a + b; }, 0) / v.length : null; }
  function r0(v) { return v == null ? '—' : Math.round(v); }
  function pct(v) { return v == null ? '—' : Math.round(v * 100) + ' %'; }
  function banda(v) { return v == null ? 'sin dato' : v >= BANDAS[1] ? 'propone' : (v <= BANDAS[0] ? 'espera' : 'equilibrado'); }  // igual que decision.banda_indice
  function minus(t) { return t ? t.charAt(0).toLowerCase() + t.slice(1) : t; }
  function lista(l) { return l.length > 1 ? l.slice(0, -1).join(', ') + ' y ' + l[l.length - 1] : (l[0] || ''); }
  function ficha(rival) { return (D.decidir && D.decidir.fichas || []).filter(function (f) { return f.rival === rival; })[0] || null; }
  function chip(caso, etq) { var c = (caso.chips || []).filter(function (x) { return x[0] === etq; })[0]; return c ? c[1] : null; }

  // Apodos para reconocer al rival en la pregunta
  var APODOS = { 'chivas': 'Guadalajara', 'guadalajara': 'Guadalajara', 'pumas': 'Pumas UNAM', 'unam': 'Pumas UNAM', 'tigres': 'Tigres UANL',
    'rayados': 'Monterrey', 'monterrey': 'Monterrey', 'cruz azul': 'Cruz Azul', 'maquina': 'Cruz Azul', 'tuzos': 'Pachuca', 'pachuca': 'Pachuca',
    'toluca': 'Toluca', 'diablos': 'Toluca', 'xolos': 'Tijuana', 'tijuana': 'Tijuana', 'necaxa': 'Necaxa', 'rayos': 'Necaxa', 'queretaro': 'Querétaro',
    'gallos': 'Querétaro', 'puebla': 'Puebla', 'camoteros': 'Puebla', 'juarez': 'Juárez', 'bravos': 'Juárez', 'atlas': 'Atlas', 'zorros': 'Atlas',
    'leon': 'León', 'esmeraldas': 'León', 'santos': 'Santos Laguna', 'guerreros': 'Santos Laguna', 'san luis': 'Atlético San Luis',
    'potosinos': 'Atlético San Luis', 'mazatlan': 'Mazatlán', 'canoneros': 'Mazatlán' };
  function rivalEn(q) {
    var mejor = null;
    Object.keys(APODOS).forEach(function (a) { if ((' ' + q + ' ').indexOf(' ' + a + ' ') >= 0 && (!mejor || a.length > mejor.length)) mejor = a; });
    return mejor ? APODOS[mejor] : null;
  }
  // Situaciones de la matriz
  var SITUACIONES = [['uno_mas', ['uno mas', 'expulsion del rival', 'superioridad', 'con 11 contra 10', 'les expulsan']],
    ['uno_menos', ['uno menos', 'nos expulsan', 'inferioridad', 'con 10']], ['gana_2', ['ganando por 2', 'ganando por dos', 'ganando 2', 'arriba por 2', 'goleando']],
    ['gana_1', ['ganando por 1', 'ganando por uno', '1 0', 'arriba por 1', 'ganando']], ['empata_1t', ['empatando primer tiempo', 'empate primer tiempo', 'empatados en el primer']],
    ['empata_2t', ['empatando segundo tiempo', 'empate segundo tiempo', 'empatados en el segundo', 'empatando', 'empate']],
    ['pierde_2', ['perdiendo por 2', 'perdiendo por dos', 'abajo por 2']], ['pierde_1', ['perdiendo por 1', 'perdiendo por uno', 'abajo por 1', 'perdiendo']]];
  function situacionEn(q) {
    for (var k = 0; k < SITUACIONES.length; k++) {
      if (SITUACIONES[k][1].some(function (c) { return q.indexOf(c) >= 0; })) return (D.decidir.matriz || []).filter(function (m) { return m.clave === SITUACIONES[k][0]; })[0] || null;
    }
    return null;
  }

  // ---------- lecturas del partido que se está viendo ----------
  function contexto() {
    var P = API.partido(), R = P.reproductor, X = P.explorar;
    var ids = R.componentes.map(function (c) { return c.id; });
    var mom = (X.caso.quiebres || []).filter(function (q) { return q[2]; })[0];
    return { P: P, R: R, X: X, rival: P.rival, ids: ids, momento: mom ? mom[0] + ' · ' + mom[1] : X.caso.titulo,
             final: chip(X.caso, 'Final del partido'), fuente: 'Datos de StatsBomb de ' + D.equipo + ' vs ' + P.rival + ' (' + X.antetitulo.split(' · ').slice(1).join(' · ') + ').' };
  }
  function promedios(R, desde, hasta, ids) {  // promedio del índice y de las señales entre dos posiciones de R.minutos
    var tramo = R.minutos.slice(Math.max(0, desde), Math.max(0, hasta));
    var s = {}; ids.forEach(function (id, k) { s[id] = [media(tramo.map(function (m) { return m.va[k]; })), media(tramo.map(function (m) { return m.vr[k]; }))]; });
    return { ia: media(tramo.map(function (m) { return m.ia; })), ir: media(tramo.map(function (m) { return m.ir; })), s: s, n: tramo.length };
  }
  function irAlMinuto(k, etq) { return { texto: 'Ver el ' + etq + ' en el reproductor', hacer: function () { API.irAMinuto(k); var r = document.getElementById('repro'); if (r) r.scrollIntoView({ behavior: reducido ? 'auto' : 'smooth', block: 'start' }); } }; }

  var INTENCIONES = [
    { id: 'momento', pregunta: '¿Qué pasó en el momento clave?', claves: ['momento clave', 'que paso', 'que sucedio', 'clave', 'expulsion', 'gol', 'roja', 'quiebre'],
      responder: function (c) {
        return { texto: [c.X.caso.titulo + '.', c.X.lectura], fuente: c.fuente + ' Momento: ' + c.momento + '.', acciones: [irAlMinuto(c.R.inicio || 0, c.R.minutos[c.R.inicio || 0].etq)] };
      } },
    { id: 'iniciativa', pregunta: '¿Quién tuvo la iniciativa?', claves: ['iniciativa', 'quien propuso', 'propuso', 'domino', 'dominio', 'quien jugo mejor', 'mejor', 'controlo', 'el balon'],
      responder: function (c) {
        var t = promedios(c.R, 0, c.R.minutos.length, c.ids);
        var porTiempo = [1, 2].map(function (p) {
          var idx = c.R.minutos.map(function (m, k) { return m.p === p ? k : -1; }).filter(function (k) { return k >= 0; });
          if (!idx.length) return null;
          var x = promedios(c.R, idx[0], idx[idx.length - 1] + 1, c.ids);
          return (p === 1 ? 'primer tiempo' : 'segundo tiempo') + ' ' + r0(x.ia) + ' contra ' + r0(x.ir);
        }).filter(Boolean);
        var quien = t.ia == null || t.ir == null ? '' : (Math.abs(t.ia - t.ir) < 3 ? ' La iniciativa estuvo repartida.' : (t.ia > t.ir ? ' El ' + D.equipo + ' tuvo más la iniciativa.' : ' ' + c.rival + ' tuvo más la iniciativa.'));
        return { texto: ['En todo el partido, el índice de iniciativa del ' + D.equipo + ' promedió ' + r0(t.ia) + ' (' + banda(t.ia) + ') y el de ' + c.rival + ', ' + r0(t.ir) + ' (' + banda(t.ir) + ').' + quien,
                         'Por tiempos: ' + lista(porTiempo) + '. La posesión del ' + D.equipo + ' fue de ' + pct(t.s.posesion && t.s.posesion[0]) + ' y su dominio del último tercio, de ' + pct(t.s.field_tilt && t.s.field_tilt[0]) + '.'],
                 fuente: c.fuente + ' Índice de iniciativa: 0 espera, 100 propone; de ' + BANDAS[0] + ' a ' + BANDAS[1] + ', equilibrado.' };
      } },
    { id: 'cambio', pregunta: '¿Cómo cambió el partido después del momento clave?', claves: ['cambio', 'como cambio', 'despues', 'despues del', 'antes', 'antes y despues', 'reaccion', 'respondio', 'que hizo', 'tras'],
      responder: function (c) {
        var k = c.R.inicio || 0, p = c.R.minutos[k].p;
        var mismo = function (j) { return c.R.minutos[j] && c.R.minutos[j].p === p; };
        var a0 = k, a1 = k; while (a0 > 0 && mismo(a0 - 1) && k - a0 < 10) a0--;
        var d1 = k + 1; while (mismo(d1) && d1 - k <= 10) d1++;
        var antes = promedios(c.R, a0, k, c.ids), desp = promedios(c.R, k + 1, d1, c.ids);
        if (!antes.n || !desp.n) return { texto: ['El momento clave cae muy pegado al inicio o al final del tiempo: no hay minutos suficientes antes y después para compararlos.'], fuente: c.fuente };
        var s = function (id, nombre) { var x = antes.s[id], y = desp.s[id]; return x && y && x[0] != null && y[0] != null ? nombre + ' del ' + D.equipo + ' pasó de ' + pct(x[0]) + ' a ' + pct(y[0]) : null; };
        var senales = [s('field_tilt', 'el dominio del último tercio'), s('control_campo_rival', 'el espacio en campo rival'), s('posesion', 'la posesión')].filter(Boolean);
        var alt = antes.s.altura_sin_balon, alt2 = desp.s.altura_sin_balon;
        var altura = alt && alt2 && alt[1] != null && alt2[1] != null ? ' La altura sin balón de ' + c.rival + ' pasó de ' + alt[1].toFixed(1) + ' m a ' + alt2[1].toFixed(1) + ' m' +
          (alt2[1] < alt[1] - 2 ? ': se metió atrás.' : (alt2[1] > alt[1] + 2 ? ': adelantó su bloque.' : ': casi no se movió.')) : '';
        return { texto: [c.momento + '.', 'En los ' + antes.n + ' minutos anteriores, el índice de iniciativa iba ' + r0(antes.ia) + ' contra ' + r0(antes.ir) + '; en los ' + desp.n + ' siguientes, ' + r0(desp.ia) + ' contra ' + r0(desp.ir) + '.',
                         (senales.length ? 'Además, ' + lista(senales) + '.' : '') + altura],
                 fuente: c.fuente + ' Promedios minuto a minuto antes y después del momento, en el mismo tiempo del partido.', acciones: [irAlMinuto(k, c.R.minutos[k].etq)] };
      } },
    { id: 'merecido', pregunta: '¿Fue merecido el resultado?', claves: ['merecido', 'merecio', 'justo', 'xg', 'goles esperados', 'suerte', 'resultado', 'simulacion'],
      responder: function (c) {
        var mc = c.X.montecarlo || [], tot = mc[mc.length - 1], ant = mc.length > 1 ? mc[0] : null;
        if (!tot) return { texto: ['No hay simulación de tiros para este partido.'], fuente: c.fuente };
        var lect = tot.gana > .5 ? 'Con esas ocasiones, ganar era lo más probable.' : (tot.pierde > .5 ? 'Con esas ocasiones, lo más probable era perder.' : 'Con esas ocasiones, el partido estaba abierto.');
        return { texto: ['Resultado real: ' + (c.final || '—') + '. Con los tiros de todo el partido, los goles esperados fueron ' + tot.goles_favor.toFixed(2) + ' del ' + D.equipo + ' contra ' + tot.goles_contra.toFixed(2) + ' de ' + c.rival + '.',
                         'En ' + (c.X.simulaciones || 10000).toLocaleString('es-MX') + ' simulaciones, el ' + D.equipo + ' ganó el ' + pct(tot.gana) + ', empató el ' + pct(tot.empata) + ' y perdió el ' + pct(tot.pierde) + '. ' + lect,
                         ant ? ant.titulo + ': el ' + D.equipo + ' ganaba el ' + pct(ant.gana) + ' de las simulaciones.' : ''],
                 fuente: c.fuente + ' Cada tiro entra con probabilidad igual a su xG (goles esperados). Explica el resultado; no predice.' };
      } },
    { id: 'mejor', pregunta: '¿Cuándo propuso más el América?', claves: ['cuando', 'mejor momento', 'peor', 'sufrio', 'propuso mas', 'minuto', 'tramo'],
      responder: function (c) {
        var mejor = null, peor = null, periodo = null, enPeriodo = 0, VENTANA = 5;  // cada minuto resume los 5 anteriores: los primeros de cada tiempo no cuentan
        c.R.minutos.forEach(function (m, k) {
          enPeriodo = m.p === periodo ? enPeriodo + 1 : 0; periodo = m.p;
          if (m.ia == null || m.ir == null || enPeriodo < VENTANA) return;
          var d = m.ia - m.ir; if (!mejor || d > mejor.d) mejor = { k: k, d: d, m: m }; if (!peor || d < peor.d) peor = { k: k, d: d, m: m };
        });
        if (!mejor) return { texto: ['No hay índice minuto a minuto para este partido.'], fuente: c.fuente };
        return { texto: ['El ' + D.equipo + ' propuso más al ' + mejor.m.etq + ': índice ' + r0(mejor.m.ia) + ' contra ' + r0(mejor.m.ir) + ', con ' + mejor.m.marcador + ' en el marcador.',
                         'Su tramo más difícil fue al ' + peor.m.etq + ': ' + r0(peor.m.ia) + ' contra ' + r0(peor.m.ir) + ' de ' + c.rival + ' (marcador ' + peor.m.marcador + ').'],
                 fuente: c.fuente + ' Diferencia del índice de iniciativa minuto a minuto (cada minuto resume los 5 anteriores).',
                 acciones: [irAlMinuto(mejor.k, mejor.m.etq), irAlMinuto(peor.k, peor.m.etq)] };
      } },
    { id: 'momentos', pregunta: '¿Cuáles fueron los momentos clave?', claves: ['momentos', 'momentos clave', 'cuales fueron', 'goles', 'expulsiones', 'cambios de sistema', 'cronologia', 'resumen'],
      responder: function (c) {
        var l = (c.X.caso.quiebres || []).map(function (q) { return q[0] + ' ' + q[1] + (q[2] ? ' (el que se analiza)' : ''); });
        return { texto: l.length ? ['Goles, expulsiones y cambios de sistema del partido:'].concat(l) : ['No hubo goles, expulsiones ni cambios de sistema registrados.'], fuente: c.fuente };
      } },
    { id: 'principio', pregunta: '¿Qué principio de Jardine se ve aquí?', claves: ['principio', 'principios', 'idea', 'estilo', 'jardine'],
      responder: function (c) {
        var pr = c.X.principio;
        if (!pr) return { texto: ['El momento clave de este partido no corresponde a ninguno de los seis principios. Aquí el motor lee el partido tal como fue.'], fuente: c.fuente };
        return { texto: [pr.titulo + '. ' + pr.frase, 'Qué tan sólido es: ' + minus(pr.estado) + '.' + (pr.muestra ? ' Muestra: ' + pr.muestra + '.' : '')],
                 fuente: 'Principios del Resumen: Jardine frente a Solari y Ortiz, con los 4 parámetros (detalle en Método).' };
      } },
    { id: 'rival', pregunta: null, claves: ['como juega', 'motor', 'lectura', 'rival', 'progresa', 'defiende', 'concede', 'balon parado', 'debilidad', 'fuerte'],
      responder: function (c, q, otro) {
        var nombre = otro || c.rival, f = ficha(nombre);
        if (!f) return { texto: ['No tengo la lectura del motor de ' + nombre + ': solo están los rivales de Jardine en AP23–AP25.'], fuente: 'Lectura del motor (AP23–AP25).' };
        var acciones = [{ texto: 'Ver su lectura completa', ir: 'decidir#ficha', rival: f.rival }];
        if (nombre !== c.rival && API.partido && D.partidos && (D.partidos[nombre] || nombre === D.rival)) acciones.push({ texto: 'Ver su partido clave', hacer: function () { API.elegirRival(nombre); } });
        var rasgos = function (l) { return lista(l.map(minus)); };
        return { texto: ['Lo que dice nuestro motor de ' + f.rival + ': progresa — ' + rasgos(f.progresa) + '; defiende — ' + rasgos(f.defiende) + '; concede — ' + rasgos(f.concede) + '.',
                         'Balón parado: ' + (f.balon_parado_rasgos.length ? rasgos(f.balon_parado_rasgos) + '. ' + f.balon_parado : f.balon_parado) + '.',
                         D.nuevo + ' contra ' + f.rival + ': ' + f.jardine + '.'],
                 fuente: 'Estilo de ' + f.rival + ' frente a la liga en los torneos de ' + D.nuevo + ' (AP23–AP25), con las estadísticas de equipo de StatsBomb. Describe al rival promedio.', acciones: acciones };
      } },
    { id: 'situacion', pregunta: '¿Qué conviene con uno más?', claves: ['conviene', 'que hacemos', 'que hago', 'recomendacion', 'si vamos', 'situacion', 'plan'],
      responder: function (c, q) {
        var m = situacionEn(q) || (D.decidir.matriz || [])[0];
        if (!m) return { texto: ['No está la matriz de situaciones en esta página.'], fuente: '' };
        return { texto: [m.situacion + ': ' + m.hace, 'Resultado: ' + m.funciona, (/^hip[oó]tesis/i.test(m.recomendacion) ? 'Recomendación: ' : 'Recomendación (hipótesis): ') + m.recomendacion],
                 fuente: 'Matriz de situaciones de Plan de juego (AP23–AP25). ' + m.evidencia,
                 acciones: [{ texto: 'Verla en la matriz', ir: 'decidir#sec-matriz', situacion: m.situacion }] };
      } },
    { id: 'jugadas', pregunta: '¿Qué jugadas puedo ver animadas?', claves: ['jugada', 'jugadas', 'animada', 'animacion', 'video', 'ver el gol'],
      responder: function (c) {
        var js = c.R.jugadas || [];
        if (!js.length) return { texto: ['Este partido no tiene jugadas animadas: en El partido se ve minuto a minuto.'], fuente: c.fuente };
        return { texto: ['Jugadas con el mapa de control del espacio en movimiento: ' + lista(js.map(function (j) { return j.titulo; })) + '. Las posiciones entre dos fotos son estimadas.'], fuente: c.fuente,
                 acciones: js.map(function (j, k) { return { texto: '▶ ' + j.titulo, hacer: function () { var b = document.querySelector('#repro .modos [data-j="' + k + '"]'); if (b) { b.click(); document.getElementById('repro').scrollIntoView({ behavior: reducido ? 'auto' : 'smooth', block: 'start' }); } } }; }) };
      } },
    { id: 'por_que', pregunta: '¿Por qué este partido?', claves: ['por que este', 'por que ese', 'elegido', 'regla', 'como se eligio'],
      responder: function (c) {
        return { texto: [c.X.caso.regla || ('Es el partido que ilustra el principio del Resumen: ' + minus(c.X.caso.titulo) + '.')], fuente: 'Regla escrita antes de mirar los partidos (bitácora del 21 oct).' };
      } },
    { id: 'glosario', pregunta: null, claves: ['que es', 'que significa', 'que mide', 'como se calcula', 'definicion'],
      responder: function (c, q) {
        var dl = Array.prototype.slice.call(document.querySelectorAll('.glosario > div'));
        var hit = dl.filter(function (d) { var t = norm(d.querySelector('dt').textContent); return t.split(' ').filter(function (w) { return w.length > 3; }).some(function (w) { return q.indexOf(w) >= 0; }); })[0];
        if (!hit) return { texto: ['Ese término no está en el glosario. Están: ' + lista(dl.map(function (d) { return d.querySelector('dt').textContent; })) + '.'], fuente: 'Glosario de Método.' };
        return { texto: [hit.querySelector('dt').textContent + ': ' + hit.querySelector('dd').textContent], fuente: 'Glosario de Método.' };
      } }
  ];

  // ---------- entender la pregunta ----------
  function responder(texto) {
    var q = norm(texto), c = contexto(), otro = rivalEn(q);
    if (otro === c.rival) otro = null;
    var puntos = INTENCIONES.map(function (it) { return it.claves.reduce(function (s, k) { return s + (q.indexOf(k) >= 0 ? k.split(' ').length : 0); }, 0); });
    if (/\bque es\b|\bque significa\b|\bque mide\b/.test(q)) puntos[INTENCIONES.map(function (i) { return i.id; }).indexOf('glosario')] += 3;
    if (situacionEn(q)) puntos[INTENCIONES.map(function (i) { return i.id; }).indexOf('situacion')] += 2;
    var mejor = puntos.indexOf(Math.max.apply(null, puntos));
    // Si nombra a otro rival: con preguntas del rival, su lectura; con preguntas del partido, se ofrece cambiar de partido
    if (otro && (puntos[mejor] === 0 || INTENCIONES[mejor].id === 'rival')) return INTENCIONES.filter(function (i) { return i.id === 'rival'; })[0].responder(c, q, otro);
    if (puntos[mejor] === 0) {
      return { texto: ['No sé responder eso con los datos de esta página, y no invento. Puedo leer el partido que estás viendo (' + D.equipo + ' vs ' + c.rival + '), decir qué dice el motor de cada rival o qué conviene en cada situación.'],
               fuente: '', sugerir: true };
    }
    var r = INTENCIONES[mejor].responder(c, q, otro);
    if (otro && INTENCIONES[mejor].id !== 'situacion' && INTENCIONES[mejor].id !== 'glosario') {
      r.texto.unshift('Esto es del partido que estás viendo (' + D.equipo + ' vs ' + c.rival + '). Para leer el de ' + otro + ', cámbialo con el botón de abajo.');
      if ((D.partidos && D.partidos[otro]) || otro === D.rival) (r.acciones = r.acciones || []).unshift({ texto: 'Ver el partido clave contra ' + otro, hacer: function () { API.elegirRival(otro); } });
    }
    return r;
  }

  // ---------- interfaz ----------
  raiz.innerHTML = '<div class="motor-log" role="log" aria-live="polite" aria-label="Conversación con el motor"></div>' +
    '<div class="motor-sugerencias" aria-label="Preguntas sugeridas"></div>' +
    '<form class="motor-form"><label class="solo-lector" for="motor-pregunta">Tu pregunta</label>' +
    '<input id="motor-pregunta" type="text" autocomplete="off" placeholder="Ej.: ¿cómo cambió el partido después de la expulsión?">' +
    '<button type="submit">Preguntar</button></form>';
  var log = raiz.querySelector('.motor-log'), sug = raiz.querySelector('.motor-sugerencias'), form = raiz.querySelector('form'), entrada = raiz.querySelector('input');

  function burbuja(clase, html) {
    var d = document.createElement('div'); d.className = 'msg ' + clase; d.innerHTML = html; log.appendChild(d);
    log.scrollTop = log.scrollHeight;
    return d;
  }
  function mostrarRespuesta(r) {
    var html = '<span class="quien">Motor</span>' + r.texto.filter(Boolean).map(function (t) { return '<p>' + esc(t) + '</p>'; }).join('') +
      (r.fuente ? '<p class="fuente">' + esc(r.fuente) + '</p>' : '');
    var d = burbuja('motor', html);
    if (r.acciones && r.acciones.length) {
      var fila = document.createElement('div'); fila.className = 'acciones-msg';
      r.acciones.forEach(function (a) {
        var b = document.createElement('button'); b.type = 'button'; b.textContent = a.texto + ' →';
        if (a.ir) { b.setAttribute('data-ir', a.ir); if (a.rival) b.setAttribute('data-rival', a.rival); if (a.situacion) b.setAttribute('data-situacion', a.situacion); }  // los enlaces de app.js
        else b.addEventListener('click', a.hacer);
        fila.appendChild(b);
      });
      d.appendChild(fila);
    }
    if (r.sugerir) pintarSugerencias(true);
  }
  function preguntar(texto) {
    texto = String(texto || '').trim(); if (!texto) return;
    burbuja('yo', '<span class="quien">Tú</span><p>' + esc(texto) + '</p>');
    var espera = burbuja('motor pensando', '<span class="quien">Motor</span><p>Leyendo los datos…</p>');
    setTimeout(function () { espera.remove(); mostrarRespuesta(responder(texto)); }, reducido ? 0 : 350);
  }
  function pintarSugerencias() {
    var c = contexto();
    var preguntas = INTENCIONES.filter(function (i) { return i.pregunta; }).map(function (i) { return i.pregunta; });
    preguntas.splice(5, 0, '¿Qué dice el motor de ' + c.rival + '?');
    sug.innerHTML = preguntas.map(function (p) { return '<button type="button" class="chip-pregunta">' + esc(p) + '</button>'; }).join('');
  }
  sug.addEventListener('click', function (e) { var b = e.target.closest('.chip-pregunta'); if (b) preguntar(b.textContent); });
  form.addEventListener('submit', function (e) { e.preventDefault(); preguntar(entrada.value); entrada.value = ''; entrada.focus(); });
  function saludo() {
    var c = contexto();
    burbuja('motor', '<span class="quien">Motor</span><p>Estás viendo ' + esc(D.equipo + ' vs ' + c.rival) + ' (' + esc(c.X.antetitulo) + '). Pregúntame por este partido, por lo que dice el motor de cualquier rival o por qué conviene en cada situación. Respondo solo con los datos de esta página.</p>');
    pintarSugerencias();
  }
  document.addEventListener('ojo:partido', function () {
    var c = contexto();
    burbuja('aviso', '<p>Cambiaste a ' + esc(D.equipo + ' vs ' + c.rival) + ': ahora respondo sobre este partido.</p>');
    pintarSugerencias();
  });
  saludo();
})();
