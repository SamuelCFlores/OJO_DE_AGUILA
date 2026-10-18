/* Ojo de Águila · biblioteca de movimiento (window.OjoMov). Se carga antes de app.js.
   Referencia: auditoría visual del 16 oct (plan de animaciones A1–A8) y "Propuestas visuales" (tarjetas 1g y 4a).
   Reglas:
   - Solo se mueve lo que cambia un dato o lleva al siguiente paso de la historia.
   - Las duraciones salen de los tokens --dur-rapida, --dur-media y --dur-lenta de app.css; con movimiento reducido valen 0
     y cada función deja el elemento en su estado final sin animar.
   - Nada queda oculto en reposo: las animaciones parten del estado final o vuelven a él (fill sin "forwards" salvo al salir).
   - Entre fotos 360 el movimiento es lineal: no se inventan aceleraciones (eso lo decide app.js).
   NOTA1: ?movimiento=reducido en la dirección simula prefers-reduced-motion (para revisar y grabar sin animaciones). */
(function () {
  'use strict';
  var raiz = document.documentElement;
  var consulta = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (/[?&]movimiento=reducido(&|$)/.test(location.search)) raiz.setAttribute('data-movimiento', 'reducido');
  var EASE_SALIDA = 'cubic-bezier(.2,.7,.2,1)', EASE_MOV = 'cubic-bezier(.45,0,.2,1)';

  function reducido() { return consulta.matches || raiz.getAttribute('data-movimiento') === 'reducido'; }
  // Duración en ms de un token (rapida, media, lenta); 0 con movimiento reducido o sin Web Animations
  function dur(nombre) {
    if (reducido() || !Element.prototype.animate) return 0;
    var v = getComputedStyle(raiz).getPropertyValue('--dur-' + nombre).trim();
    var n = parseFloat(v);
    return isNaN(n) ? 0 : (/ms$/.test(v) ? n : n * 1000);
  }
  function suave(x) { return 1 - Math.pow(1 - Math.max(0, Math.min(1, x)), 3); }  // salida cúbica
  // Llama a fn una vez al terminar la animación o, si el evento no llega (pestaña en segundo plano), al cumplirse su duración
  function alTerminar(anim, ms, fn) {
    var hecho = false, una = function () { if (!hecho) { hecho = true; fn(); } };
    anim.onfinish = anim.oncancel = una;
    setTimeout(una, ms + 60);
  }

  // A4 · fundido real entre dos estados de una capa SVG: la vieja se apaga mientras la nueva aparece
  function cruce(capa, dibujar) {
    var padre = capa.parentNode;
    padre.querySelectorAll('.capa-saliente').forEach(function (n) { n.remove(); });
    var d = dur('media');
    if (!d) { dibujar(); return; }
    var vieja = capa.cloneNode(true);
    vieja.classList.remove('capa'); vieja.classList.add('capa-saliente'); vieja.setAttribute('aria-hidden', 'true');
    padre.insertBefore(vieja, capa.nextSibling);
    dibujar();
    var a = vieja.animate([{ opacity: 1 }, { opacity: 0 }], { duration: d, easing: 'linear', fill: 'forwards' });
    alTerminar(a, d, function () { vieja.remove(); });
    capa.animate([{ opacity: 0 }, { opacity: 1 }], { duration: d, easing: 'linear' });
  }

  // Secciones <details> que se abren y cierran con altura animada (barra lateral)
  function plegable(det) {
    if (det.__plegable) return;
    det.__plegable = true;
    var sum = det.querySelector('summary'), cuerpo = sum && sum.nextElementSibling;
    if (!cuerpo) return;
    sum.addEventListener('click', function (e) {
      var d = dur('media');
      if (!d) return;  // sin movimiento: el comportamiento nativo
      e.preventDefault();
      if (det.__anim) { var previa = det.__anim; det.__anim = null; previa.cancel(); }
      cuerpo.style.overflow = 'hidden';
      var cerrar = det.open, anim;
      if (cerrar) {
        det.classList.add('cerrando');
        anim = cuerpo.animate([{ height: cuerpo.offsetHeight + 'px', opacity: 1 }, { height: '0px', opacity: 0 }], { duration: d, easing: EASE_MOV, fill: 'forwards' });
      } else {
        det.open = true;
        anim = cuerpo.animate([{ height: '0px', opacity: 0 }, { height: cuerpo.offsetHeight + 'px', opacity: 1 }], { duration: d, easing: EASE_MOV });
      }
      det.__anim = anim;
      alTerminar(anim, d, function () {
        if (det.__anim !== anim) return;  // otra apertura o cierre ya tomó el control
        if (cerrar) det.open = false;
        anim.cancel(); cuerpo.style.overflow = ''; det.classList.remove('cerrando'); det.__anim = null;
      });
    });
  }

  // A5 · resaltado breve de un elemento (anillo crema que crece y se va)
  function resaltar(el) {
    var d = dur('lenta');
    if (!d) return;
    var base = getComputedStyle(el).boxShadow, b = base === 'none' ? '' : base + ', ';
    var crema = getComputedStyle(raiz).getPropertyValue('--c-acento').trim() || 'currentColor';
    el.animate([{ boxShadow: b + '0 0 0 0 ' + crema }, { boxShadow: b + '0 0 0 6px ' + crema, offset: .25 },
                { boxShadow: b + '0 0 0 0 ' + crema }], { duration: d * 2, easing: EASE_SALIDA });
  }
  // A5 · lleva la vista a un elemento y lo resalta al llegar
  function irA(el, opciones) {
    var d = dur('lenta');
    el.scrollIntoView({ behavior: d ? 'smooth' : 'auto', block: (opciones && opciones.bloque) || 'start' });
    if (opciones && opciones.foco) el.focus({ preventScroll: true });
    var hecho = false, listo = function () { if (hecho) return; hecho = true; window.removeEventListener('scrollend', listo); resaltar(el); };
    if (!d) return;
    window.addEventListener('scrollend', listo);
    setTimeout(listo, d * 1.5);  // navegadores sin scrollend
  }

  // A1 y A2 · anillo que crece y se apaga en (x, y) de un SVG: marca una foto real o un quiebre
  function pulso(svg, x, y, opciones) {
    var d = dur('media');
    if (!d) return;
    var o = opciones || {}, ns = 'http://www.w3.org/2000/svg', c = document.createElementNS(ns, 'circle');
    c.setAttribute('cx', x); c.setAttribute('cy', y); c.setAttribute('r', o.r0 || 4);
    c.setAttribute('style', 'fill:none;pointer-events:none;stroke:' + (o.color || 'var(--c-rojo)') + ';stroke-width:' + (o.grosor || 2));
    (o.padre || svg).appendChild(c);
    var t0 = null, total = d * 3, r0 = o.r0 || 4, r1 = o.r1 || 18;
    function paso(t) {
      if (t0 == null) t0 = t;
      var p = (t - t0) / total;
      if (p >= 1 || !c.isConnected) { c.remove(); return; }
      c.setAttribute('r', r0 + (r1 - r0) * suave(p * 2));
      c.setAttribute('opacity', 1 - p);
      requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
  }

  // A7 · conteo de un número exacto ("57", "-1.5 yd", "+32 pts"); un intervalo o un texto se queda tal cual
  function contar(el) {
    var final = el.textContent, m = /^([+\-−]?)(\d+(?:[.,]\d+)?)(\s*\D*)$/.exec(final.trim()), d = dur('lenta');
    if (!m || !d) return;
    var valor = parseFloat(m[2].replace(',', '.')), dec = (m[2].split(/[.,]/)[1] || '').length, sep = m[2].indexOf(',') >= 0 ? ',' : '.';
    var t0 = null;
    function paso(t) {
      if (t0 == null) t0 = t;
      var p = Math.min(1, (t - t0) / d);
      el.textContent = p >= 1 ? final : m[1] + (valor * suave(p)).toFixed(dec).replace('.', sep) + m[3];
      if (p < 1) requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
  }

  // A6 · elementos que crecen desde 0 hasta su ancho, en orden (escalón en ms entre cada uno)
  function crecer(els, opciones) {
    var d = dur('lenta'), escalon = (opciones && opciones.escalon) || 80;
    if (!d) return;
    Array.prototype.forEach.call(els, function (el, k) {
      var ancho = el.style.width || getComputedStyle(el).width;
      el.animate([{ width: '0%' }, { width: ancho }], { duration: d, delay: k * escalon, easing: EASE_SALIDA, fill: 'backwards' });
    });
  }

  // A3 · transforma los vértices de un polígono SVG hacia otros puntos (misma cantidad de vértices)
  function poligono(poly, puntos) {
    var destino = puntos.map(function (p) { return [+p[0], +p[1]]; });
    var texto = function (ps) { return ps.map(function (p) { return p[0].toFixed(2) + ',' + p[1].toFixed(2); }).join(' '); };
    if (poly.__raf) cancelAnimationFrame(poly.__raf);
    var origen = poly.__actual, d = dur('media');  // parte de lo que se ve ahora, aunque otra transición siga a medias
    if (!d || !origen || origen.length !== destino.length) { poly.__actual = destino; poly.setAttribute('points', texto(destino)); return; }
    var t0 = null;
    function paso(t) {
      if (t0 == null) t0 = t;
      var p = suave((t - t0) / d);
      poly.__actual = origen.map(function (o, k) { return [o[0] + (destino[k][0] - o[0]) * p, o[1] + (destino[k][1] - o[1]) * p]; });
      poly.setAttribute('points', texto(poly.__actual));
      poly.__raf = p < 1 ? requestAnimationFrame(paso) : null;
    }
    poly.__raf = requestAnimationFrame(paso);
  }

  // Barra lateral: tres variantes (Propuestas visuales 3a, 3b y 3c). Solo cambia clases; app.js cuida foco, inert y aria.
  //   riel  (3a): el contenido de la barra se apaga y después la columna encoge; al abrir, al revés.
  //   sobre (3b, recomendada): la barra se desliza encima del contenido; solo anima transform y la cancha no se redibuja.
  //   chips (3c): la barra se va por completo y los filtros activos bajan como chips arriba del contenido.
  function barra(oculta, variante) {
    var c = document.body;
    if (variante) c.setAttribute('data-barra-variante', variante);
    variante = c.getAttribute('data-barra-variante') || 'sobre';
    clearTimeout(c.__barraT);
    var rapida = dur('rapida'), media = dur('media');
    if (variante === 'riel' && rapida) {
      if (oculta) {
        c.classList.add('barra-apagando');
        c.__barraT = setTimeout(function () { c.classList.add('barra-oculta'); }, rapida);
      } else {
        c.classList.add('barra-apagando'); c.classList.remove('barra-oculta');
        c.__barraT = setTimeout(function () { c.classList.remove('barra-apagando'); }, media);
      }
      return;
    }
    c.classList.remove('barra-apagando');
    c.classList.toggle('barra-oculta', oculta);
  }

  // Llama a fn una sola vez, cuando el elemento entra en pantalla (A6)
  function alVer(el, fn) {
    if (!('IntersectionObserver' in window)) { fn(el); return; }
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) { if (e.isIntersecting) { io.disconnect(); fn(el); } });
    }, { threshold: .4 });
    io.observe(el);
  }

  // A8 · cambio de vista: la que se va se apaga rápido; la que llega aparece y sube 8 px
  function vista(fn) {
    var r = dur('rapida'), m = dur('media');
    function visible() { return Array.prototype.filter.call(document.querySelectorAll('.vista'), function (v) { return v.offsetParent !== null; })[0]; }
    var antes = visible();
    if (!r || !antes) { fn(); return; }
    var salida = antes.animate([{ opacity: 1 }, { opacity: 0 }], { duration: r, easing: 'linear', fill: 'forwards' });
    alTerminar(salida, r, function () {
      fn(); salida.cancel();
      var nueva = visible();
      if (nueva) nueva.animate([{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }], { duration: m, easing: EASE_SALIDA });
    });
  }

  window.OjoMov = { reducido: reducido, dur: dur, cruce: cruce, plegable: plegable, resaltar: resaltar, irA: irA, pulso: pulso,
                    contar: contar, crecer: crecer, poligono: poligono, barra: barra, alVer: alVer, vista: vista };
})();
