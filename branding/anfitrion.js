/* Reproductor propio para las escenas de Claude Design (se concatena al final de dist/marca.js).
 *
 * NOTA1: se reemplaza CompositionStage porque trae barra de controles y guarda el segundo de
 * reproducción en localStorage; aquí el reloj arranca en 0, sin controles y sin estado.
 * NOTA2: "nat" es la duración con que se diseñó la escena y "dur" la duración reproducida;
 * ccDerive/ccWarp (animations-v3) aceleran la escena sin tocar el diseño.
 * REF1: CompositionStage, ccDerive, ccWarp y CompositionClock en branding/fuente/animations-v3.jsx.
 */
;(function () {
  'use strict';
  var h = React.createElement;
  var NAVY = '#0B2545';
  var INTRO_NAT_S = 10; // duración de diseño de "Mirada de rapaz"
  var ESCENAS_LOOP = [
    { name: 'Mirada', dur: 2.2 }, { name: 'Parpadeo', dur: 0.9 },
    { name: 'Escaneo', dur: 2.3 }, { name: 'Pausa', dur: 0.6 },
  ];

  // Escala un lienzo fijo para que quepa completo en su contenedor, centrado.
  function Ajuste(props) {
    var ref = React.useRef(null);
    var estado = React.useState(0);
    var escala = estado[0], setEscala = estado[1];
    React.useLayoutEffect(function () {
      var el = ref.current;
      function medir() {
        var r = el.getBoundingClientRect();
        setEscala(Math.min(r.width / props.ancho, r.height / props.alto));
      }
      medir();
      var ro = new ResizeObserver(medir);
      ro.observe(el);
      return function () { ro.disconnect(); };
    }, []);
    return h('div', { ref: ref, style: { position: 'absolute', inset: 0, overflow: 'hidden', background: props.fondo } },
      h('div', { style: {
        position: 'absolute', left: '50%', top: '50%', width: props.ancho, height: props.alto,
        transform: 'translate(-50%, -50%) scale(' + escala + ')', transformOrigin: 'center',
      } }, props.children));
  }

  // Reloj: una vez (alTerminar al final), en bucle, o congelado en tiempoFijo.
  function Reproductor(props) {
    var d = props.derivado;
    var estado = React.useState(props.tiempoFijo != null ? props.tiempoFijo : 0);
    var t = estado[0], setT = estado[1];
    React.useEffect(function () {
      if (props.tiempoFijo != null) return undefined;
      var id, t0 = null, avisado = false;
      function paso(ahora) {
        if (t0 === null) t0 = ahora;
        var s = (ahora - t0) / 1000;
        if (props.bucle) {
          setT(s % d.total);
        } else if (s >= d.total) {
          setT(d.total);
          if (!avisado && props.alTerminar) { avisado = true; props.alTerminar(); }
          return;
        } else {
          setT(s);
        }
        id = requestAnimationFrame(paso);
      }
      id = requestAnimationFrame(paso);
      return function () { cancelAnimationFrame(id); };
    }, [d]);
    return h(TimelineContext.Provider, { value: { time: t, duration: d.total, playing: true } },
      h(Ajuste, { ancho: props.ancho, alto: props.alto, fondo: props.fondo },
        h(CompositionClock, { derived: d, cues: d.table }, h(props.Pieza))));
  }

  function montar(contenedor, elemento) {
    var raiz = ReactDOM.createRoot(contenedor);
    raiz.render(elemento);
    return { detener: function () { raiz.unmount(); } };
  }

  window.OjoMarca = {
    // Animación de entrada "Mirada de rapaz". opciones: { segundos (por defecto 5), alTerminar }
    intro: function (contenedor, opciones) {
      opciones = opciones || {};
      var segundos = opciones.segundos || 5;
      // HACK1: la escena lee window.OM_SCENES y window.OM_INTRO directamente (HAS_CANCHA, modo campo).
      window.OM_SCENES = JSON.stringify([{ name: 'Mirada', dur: segundos }]);
      window.OM_INTRO = 'campo';
      var d = ccDerive([{ name: 'Mirada', dur: segundos, nat: INTRO_NAT_S }]);
      return montar(contenedor, h(Reproductor, {
        derivado: d, Pieza: window.__OjoIntroPieza, ancho: 1920, alto: 1080, fondo: NAVY,
        alTerminar: opciones.alTerminar,
      }));
    },
    // Ícono animado en bucle. opciones: { estatico: true } muestra el ojo quieto.
    loop: function (contenedor, opciones) {
      opciones = opciones || {};
      var d = ccDerive(ESCENAS_LOOP);
      return montar(contenedor, h(Reproductor, {
        derivado: d, Pieza: window.__OjoLoopPieza, ancho: 512, alto: 512,
        fondo: opciones.fondo || NAVY, bucle: true, tiempoFijo: opciones.estatico ? 0 : null,
      }));
    },
  };
})();
