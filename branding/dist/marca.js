/* Ojo de Águila · marca animada. Generado por branding/construir_marca.py: no editar a mano. */
const Easing = {
  linear: t => t,
  easeInQuad: t => t * t,
  easeOutQuad: t => t * (2 - t),
  easeInOutQuad: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  easeInCubic: t => t * t * t,
  easeOutCubic: t => --t * t * t + 1,
  easeInOutCubic: t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
  easeInQuart: t => t * t * t * t,
  easeOutQuart: t => 1 - --t * t * t * t,
  easeInOutQuart: t => t < 0.5 ? 8 * t * t * t * t : 1 - 8 * --t * t * t * t,
  easeInExpo: t => t === 0 ? 0 : Math.pow(2, 10 * (t - 1)),
  easeOutExpo: t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
  easeInOutExpo: t => {
    if (t === 0) return 0;
    if (t === 1) return 1;
    if (t < 0.5) return 0.5 * Math.pow(2, 20 * t - 10);
    return 1 - 0.5 * Math.pow(2, -20 * t + 10);
  },
  easeInSine: t => 1 - Math.cos(t * Math.PI / 2),
  easeOutSine: t => Math.sin(t * Math.PI / 2),
  easeInOutSine: t => -(Math.cos(Math.PI * t) - 1) / 2,
  easeOutBack: t => {
    const c1 = 1.70158,
      c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  },
  easeInBack: t => {
    const c1 = 1.70158,
      c3 = c1 + 1;
    return c3 * t * t * t - c1 * t * t;
  },
  easeInOutBack: t => {
    const c1 = 1.70158,
      c2 = c1 * 1.525;
    return t < 0.5 ? Math.pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2) / 2 : (Math.pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2;
  },
  easeOutElastic: t => {
    const c4 = 2 * Math.PI / 3;
    if (t === 0) return 0;
    if (t === 1) return 1;
    return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  }
};
const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
function interpolate(input, output, ease = Easing.linear) {
  return t => {
    if (t <= input[0]) return output[0];
    if (t >= input[input.length - 1]) return output[output.length - 1];
    for (let i = 0; i < input.length - 1; i++) {
      if (t >= input[i] && t <= input[i + 1]) {
        const span = input[i + 1] - input[i];
        const local = span === 0 ? 0 : (t - input[i]) / span;
        const easeFn = Array.isArray(ease) ? ease[i] || Easing.linear : ease;
        const eased = easeFn(local);
        return output[i] + (output[i + 1] - output[i]) * eased;
      }
    }
    return output[output.length - 1];
  };
}
function animate({
  from = 0,
  to = 1,
  start = 0,
  end = 1,
  ease = Easing.easeInOutCubic
}) {
  return t => {
    if (t <= start) return from;
    if (t >= end) return to;
    const local = (t - start) / (end - start);
    return from + (to - from) * ease(local);
  };
}
const TimelineContext = React.createContext({
  time: 0,
  duration: 10,
  playing: false
});
const useTime = () => React.useContext(TimelineContext).time;
const useTimeline = () => React.useContext(TimelineContext);
var SS_EXT_PLAY_MS = 400;
function useInlineFontsInto(svgRef) {
  React.useEffect(() => {
    const svg = svgRef.current;
    const host = svg && svg.querySelector('foreignObject > div');
    if (!svg || !host) return;
    let cancelled = false;
    (async () => {
      const rules = [];
      for (const ss of document.styleSheets) {
        let cssRules;
        try {
          cssRules = ss.cssRules;
        } catch {
          if (ss.href) {
            try {
              const txt = await fetch(ss.href).then(r => {
                if (!r.ok) throw 0;
                return r.text();
              });
              for (const ff of txt.match(/@font-face\s*{[^}]*}/g) || []) rules.push({
                css: ff,
                base: ss.href
              });
            } catch {}
          }
          continue;
        }
        if (!cssRules) continue;
        for (const r of cssRules) {
          if (r.type === CSSRule.FONT_FACE_RULE) {
            rules.push({
              css: r.cssText,
              base: ss.href || location.href
            });
          }
        }
      }
      const toDataURL = url => fetch(url).then(r => {
        if (!r.ok) throw 0;
        return r.blob();
      }).then(b => new Promise(res => {
        const fr = new FileReader();
        fr.onload = () => res(fr.result);
        fr.onerror = () => res(url);
        fr.readAsDataURL(b);
      })).catch(() => url);
      const parts = await Promise.all(rules.map(async ({
        css,
        base
      }) => {
        const re = /url\((['"]?)([^'")]+)\1\)/g;
        let out = css,
          m;
        while (m = re.exec(css)) {
          const u = m[2];
          if (u.startsWith('data:')) continue;
          let abs;
          try {
            abs = new URL(u, base).href;
          } catch {
            continue;
          }
          out = out.split(m[0]).join(`url("${await toDataURL(abs)}")`);
        }
        return out;
      }));
      if (cancelled || !parts.length) {
        svg.setAttribute('data-om-fonts-inlined', 'true');
        return;
      }
      const style = document.createElement('style');
      style.textContent = parts.join('\n');
      host.insertBefore(style, host.firstChild);
      svg.setAttribute('data-om-fonts-inlined', 'true');
    })();
    return () => {
      cancelled = true;
    };
  }, []);
}
function Stage({
  width = 1280,
  height = 720,
  duration = 10,
  background = '#f6f4ef',
  fps = 60,
  loop = true,
  autoplay = true,
  playback = null,
  persistKey = 'animstage-v3',
  children
}) {
  width = +width || 1280;
  height = +height || 720;
  duration = +duration || 10;
  fps = +fps || 60;
  if (typeof loop === 'string') loop = loop !== 'false';
  if (typeof autoplay === 'string') autoplay = autoplay !== 'false';
  const playTimes = playback && playback.mode === 'times' ? playback.count : null;
  const loopEff = playback ? playback.mode === 'loop' : loop;
  const [time, setTime] = React.useState(() => {
    try {
      const v = parseFloat(localStorage.getItem(persistKey + ':t') || '0');
      return isFinite(v) ? clamp(v, 0, duration) : 0;
    } catch {
      return 0;
    }
  });
  const [playing, setPlaying] = React.useState(autoplay);
  const [extPlay, setExtPlay] = React.useState(false);
  const extPlayTimerRef = React.useRef(null);
  const [hoverTime, setHoverTime] = React.useState(null);
  const [scale, setScale] = React.useState(1);
  const stageRef = React.useRef(null);
  const canvasRef = React.useRef(null);
  const rafRef = React.useRef(null);
  const lastTsRef = React.useRef(null);
  React.useEffect(() => {
    try {
      localStorage.setItem(persistKey + ':t', String(time));
    } catch {}
  }, [time, persistKey]);
  React.useEffect(() => {
    if (!stageRef.current) return;
    const el = stageRef.current;
    const measure = () => {
      const barH = 44;
      const s = Math.min(el.clientWidth / width, (el.clientHeight - barH) / height);
      setScale(Math.max(0.05, s));
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    window.addEventListener('resize', measure);
    return () => {
      ro.disconnect();
      window.removeEventListener('resize', measure);
    };
  }, [width, height]);
  const passesRef = React.useRef(0);
  React.useEffect(() => {
    if (!playing) {
      lastTsRef.current = null;
      return;
    }
    passesRef.current = 0;
    const step = ts => {
      if (lastTsRef.current == null) lastTsRef.current = ts;
      const dt = (ts - lastTsRef.current) / 1000;
      lastTsRef.current = ts;
      setTime(t => {
        let next = t + dt;
        if (next >= duration) {
          if (playTimes !== null) {
            passesRef.current += 1;
            if (passesRef.current >= playTimes) {
              next = duration;
              setPlaying(false);
            } else {
              next = next % duration;
            }
          } else if (loopEff) {
            next = next % duration;
          } else {
            next = duration;
            setPlaying(false);
          }
        }
        return next;
      });
      rafRef.current = requestAnimationFrame(step);
    };
    rafRef.current = requestAnimationFrame(step);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      lastTsRef.current = null;
    };
  }, [playing, duration, loopEff, playTimes]);
  React.useEffect(() => {
    const onKey = e => {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
      if (e.code === 'Space') {
        e.preventDefault();
        setPlaying(p => !p);
      } else if (e.code === 'ArrowLeft') {
        setTime(t => clamp(t - (e.shiftKey ? 1 : 0.1), 0, duration));
      } else if (e.code === 'ArrowRight') {
        setTime(t => clamp(t + (e.shiftKey ? 1 : 0.1), 0, duration));
      } else if (e.key === '0' || e.code === 'Home') {
        setTime(0);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [duration]);
  React.useEffect(() => {
    const el = canvasRef.current;
    if (!el) return;
    const canSyncSeek = typeof ReactDOM !== 'undefined' && typeof ReactDOM.flushSync === 'function';
    const onSeek = e => {
      const apply = () => {
        setPlaying(false);
        const hostPlay = !!(e.detail && e.detail.playing === true);
        if (extPlayTimerRef.current) {
          clearTimeout(extPlayTimerRef.current);
          extPlayTimerRef.current = null;
        }
        if (hostPlay) {
          extPlayTimerRef.current = setTimeout(() => {
            extPlayTimerRef.current = null;
            setExtPlay(false);
          }, SS_EXT_PLAY_MS);
        }
        setExtPlay(hostPlay);
        setTime(clamp(e.detail.time, 0, duration));
      };
      if (canSyncSeek && e.detail && e.detail.sync === true) {
        ReactDOM.flushSync(apply);
      } else {
        apply();
      }
    };
    el.addEventListener('data-om-seek-to-time-frame', onSeek);
    if (canSyncSeek) el.setAttribute('data-om-sync-seek', 'true');
    return () => {
      el.removeEventListener('data-om-seek-to-time-frame', onSeek);
      el.removeAttribute('data-om-sync-seek');
      if (extPlayTimerRef.current) {
        clearTimeout(extPlayTimerRef.current);
        extPlayTimerRef.current = null;
      }
      setExtPlay(false);
    };
  }, [duration]);
  useInlineFontsInto(canvasRef);
  const displayTime = hoverTime != null ? hoverTime : time;
  const ctxValue = React.useMemo(() => ({
    time: displayTime,
    duration,
    playing,
    extPlaying: extPlay,
    setTime,
    setPlaying
  }), [displayTime, duration, playing, extPlay]);
  return (React.createElement("div", {
      ref: stageRef,
      "data-om-starter": "animations-v3",
      style: {
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        background: '#0a0a0a',
        fontFamily: 'Inter, system-ui, sans-serif'
      }
    }, React.createElement("div", {
      style: {
        flex: 1,
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        minHeight: 0
      }
    }, React.createElement("svg", {
      ref: canvasRef,
      width: width,
      height: height,
      "data-om-exportable-video-with-duration-secs": duration,
      style: {
        transform: `scale(${scale})`,
        transformOrigin: 'center',
        flexShrink: 0,
        boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
        display: 'block'
      }
    }, React.createElement("foreignObject", {
      x: "0",
      y: "0",
      width: "100%",
      height: "100%"
    }, React.createElement("div", {
      xmlns: "http://www.w3.org/1999/xhtml",
      style: {
        width,
        height,
        background,
        position: 'relative',
        overflow: 'hidden'
      }
    }, React.createElement(TimelineContext.Provider, {
      value: ctxValue
    }, children))))), React.createElement(PlaybackBar, {
      time: displayTime,
      actualTime: time,
      duration: duration,
      playing: playing,
      onPlayPause: () => setPlaying(p => !p),
      onReset: () => {
        setTime(0);
      },
      onSeek: t => setTime(t),
      onHover: t => setHoverTime(t)
    }))
  );
}
function PlaybackBar({
  time,
  duration,
  playing,
  onPlayPause,
  onReset,
  onSeek,
  onHover
}) {
  const trackRef = React.useRef(null);
  const [dragging, setDragging] = React.useState(false);
  const timeFromEvent = React.useCallback(e => {
    const rect = trackRef.current.getBoundingClientRect();
    const x = clamp((e.clientX - rect.left) / rect.width, 0, 1);
    return x * duration;
  }, [duration]);
  const onTrackMove = e => {
    if (!trackRef.current) return;
    const t = timeFromEvent(e);
    if (dragging) {
      onSeek(t);
    } else {
      onHover(t);
    }
  };
  const onTrackLeave = () => {
    if (!dragging) onHover(null);
  };
  const onTrackDown = e => {
    setDragging(true);
    const t = timeFromEvent(e);
    onSeek(t);
    onHover(null);
  };
  React.useEffect(() => {
    if (!dragging) return;
    const onUp = () => setDragging(false);
    const onMove = e => {
      if (!trackRef.current) return;
      const t = timeFromEvent(e);
      onSeek(t);
    };
    window.addEventListener('mouseup', onUp);
    window.addEventListener('mousemove', onMove);
    return () => {
      window.removeEventListener('mouseup', onUp);
      window.removeEventListener('mousemove', onMove);
    };
  }, [dragging, timeFromEvent, onSeek]);
  const pct = duration > 0 ? time / duration * 100 : 0;
  const fmt = t => {
    const total = Math.max(0, t);
    const m = Math.floor(total / 60);
    const s = Math.floor(total % 60);
    const cs = Math.floor(total * 100 % 100);
    return `${String(m).padStart(1, '0')}:${String(s).padStart(2, '0')}.${String(cs).padStart(2, '0')}`;
  };
  const mono = 'JetBrains Mono, ui-monospace, SFMono-Regular, monospace';
  return React.createElement("div", {
    "data-omelette-chrome": true,
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 10,
      padding: '6px 12px',
      background: 'rgba(20,20,20,0.92)',
      borderTop: '1px solid rgba(255,255,255,0.08)',
      width: '100%',
      maxWidth: 680,
      alignSelf: 'center',
      borderRadius: 6,
      color: '#f6f4ef',
      fontFamily: 'Inter, system-ui, sans-serif',
      userSelect: 'none',
      flexShrink: 0
    }
  }, React.createElement(IconButton, {
    onClick: onPlayPause,
    title: "Play/pause (space)"
  }, playing ? React.createElement("svg", {
    width: "14",
    height: "14",
    viewBox: "0 0 14 14",
    fill: "none"
  }, React.createElement("rect", {
    x: "3",
    y: "2",
    width: "3",
    height: "10",
    fill: "currentColor"
  }), React.createElement("rect", {
    x: "8",
    y: "2",
    width: "3",
    height: "10",
    fill: "currentColor"
  })) : React.createElement("svg", {
    width: "14",
    height: "14",
    viewBox: "0 0 14 14",
    fill: "none"
  }, React.createElement("path", {
    d: "M3 2l9 5-9 5V2z",
    fill: "currentColor"
  }))), React.createElement(IconButton, {
    onClick: onReset,
    title: "Return to start (0)"
  }, React.createElement("svg", {
    width: "14",
    height: "14",
    viewBox: "0 0 14 14",
    fill: "none"
  }, React.createElement("path", {
    d: "M3 2v10M12 2L5 7l7 5V2z",
    stroke: "currentColor",
    strokeWidth: "1.5",
    strokeLinejoin: "round",
    strokeLinecap: "round"
  }))), React.createElement("div", {
    style: {
      fontFamily: mono,
      fontSize: 12,
      fontVariantNumeric: 'tabular-nums',
      width: 64,
      textAlign: 'right',
      color: '#f6f4ef'
    }
  }, fmt(time)), React.createElement("div", {
    ref: trackRef,
    onMouseMove: onTrackMove,
    onMouseLeave: onTrackLeave,
    onMouseDown: onTrackDown,
    style: {
      flex: 1,
      height: 22,
      position: 'relative',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center'
    }
  }, React.createElement("div", {
    style: {
      position: 'absolute',
      left: 0,
      right: 0,
      height: 4,
      background: 'rgba(255,255,255,0.12)',
      borderRadius: 2
    }
  }), React.createElement("div", {
    style: {
      position: 'absolute',
      left: 0,
      width: `${pct}%`,
      height: 4,
      background: 'oklch(72% 0.12 250)',
      borderRadius: 2
    }
  }), React.createElement("div", {
    style: {
      position: 'absolute',
      left: `${pct}%`,
      top: '50%',
      width: 12,
      height: 12,
      marginLeft: -6,
      marginTop: -6,
      background: '#fff',
      borderRadius: 6,
      boxShadow: '0 2px 4px rgba(0,0,0,0.4)'
    }
  })), React.createElement("div", {
    style: {
      fontFamily: mono,
      fontSize: 12,
      fontVariantNumeric: 'tabular-nums',
      width: 64,
      textAlign: 'left',
      color: 'rgba(246,244,239,0.55)'
    }
  }, fmt(duration)), typeof VideoEncoder !== 'undefined' && React.createElement(IconButton, {
    title: "Export video",
    onClick: () => window.parent.postMessage({
      type: 'omelette:request-video-export'
    }, '*')
  }, React.createElement("svg", {
    width: "14",
    height: "14",
    viewBox: "0 0 14 14",
    fill: "none"
  }, React.createElement("path", {
    d: "M7 2v7m0 0L4 6m3 3l3-3M2 12h10",
    stroke: "currentColor",
    strokeWidth: "1.5",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }))));
}
function IconButton({
  children,
  onClick,
  title
}) {
  const [hover, setHover] = React.useState(false);
  return React.createElement("button", {
    onClick: onClick,
    title: title,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      width: 24,
      height: 24,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: hover ? 'rgba(255,255,255,0.12)' : 'rgba(255,255,255,0.04)',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: 5,
      color: '#f6f4ef',
      cursor: 'pointer',
      padding: 0,
      transition: 'background 120ms'
    }
  }, children);
}
function ssParse(raw) {
  if (typeof raw !== 'string' || !raw || raw.length > 16 * 1024) return null;
  var parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (e) {
    return null;
  }
  if (!Array.isArray(parsed) || parsed.length === 0 || parsed.length > 50) return null;
  for (var i = 0; i < parsed.length; i++) {
    var s = parsed[i];
    if (typeof s !== 'object' || s === null) return null;
    if (typeof s.name !== 'string' || typeof s.dur !== 'number') return null;
    if (!isFinite(s.dur) || s.dur <= 0 || s.dur > 300) return null;
  }
  return parsed;
}
function ppParse(raw) {
  if (typeof raw !== 'string' || !raw || raw.length > 256) return null;
  var parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (e) {
    return null;
  }
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) return null;
  var keys = Object.keys(parsed);
  if (parsed.mode === 'loop') return keys.length === 1 ? {
    mode: 'loop'
  } : null;
  if (parsed.mode === 'times') {
    if (keys.length !== 2) return null;
    var c = parsed.count;
    if (typeof c !== 'number' || c !== Math.floor(c) || c < 1 || c > 99) return null;
    return {
      mode: 'times',
      count: c
    };
  }
  return null;
}
function PlaybackSync(props) {
  var ref = React.useRef(null);
  var raw = props.raw;
  var onUpdate = props.onUpdate;
  React.useEffect(function () {
    var el = ref.current;
    if (!el) return;
    var root = el.closest('[data-om-exportable-video-with-duration-secs]');
    if (!root) return;
    root.setAttribute('data-om-timeline-playback', raw);
    var onEvent = function (e) {
      var next = e && e.detail;
      if (ppParse(next)) onUpdate(next);
    };
    root.addEventListener('data-om-timeline-playback-update', onEvent);
    return function () {
      root.removeEventListener('data-om-timeline-playback-update', onEvent);
      root.removeAttribute('data-om-timeline-playback');
    };
  }, [raw, onUpdate]);
  return React.createElement("div", {
    ref: ref,
    style: {
      display: 'none'
    }
  });
}
function SceneSync(props) {
  var ref = React.useRef(null);
  var raw = props.raw;
  var onUpdate = props.onUpdate;
  React.useEffect(function () {
    var el = ref.current;
    if (!el) return;
    var root = el.closest('[data-om-exportable-video-with-duration-secs]');
    if (!root) return;
    root.setAttribute('data-om-timeline-scenes', raw);
    var onEvent = function (e) {
      var next = e && e.detail;
      if (ssParse(next)) onUpdate(next);
    };
    root.addEventListener('data-om-timeline-scenes-update', onEvent);
    return function () {
      root.removeEventListener('data-om-timeline-scenes-update', onEvent);
      root.removeAttribute('data-om-timeline-scenes');
    };
  }, [raw, onUpdate]);
  return React.createElement("div", {
    ref: ref,
    style: {
      display: 'none'
    }
  });
}
var CompositionContext = React.createContext(null);
function useComposition() {
  var ctx = React.useContext(CompositionContext);
  if (!ctx) throw new Error('useComposition() must be called inside <CompositionStage>');
  return ctx;
}
function ccDerive(scenes) {
  var playStart = 0;
  var authStart = 0;
  var sections = [];
  var table = Object.create(null);
  for (var i = 0; i < scenes.length; i++) {
    var s = scenes[i];
    var nat = typeof s.nat === 'number' && isFinite(s.nat) && s.nat > 0 ? s.nat : s.dur;
    sections.push({
      name: s.name,
      playStart: playStart,
      dur: s.dur,
      authStart: authStart,
      nat: nat
    });
    if (!Object.prototype.hasOwnProperty.call(table, s.name)) {
      table[s.name] = Math.round(authStart * 1000) / 1000;
    }
    playStart += s.dur;
    authStart += nat;
  }
  return {
    sections: sections,
    table: table,
    total: Math.round(playStart * 1000) / 1000,
    authoredTotal: Math.round(authStart * 1000) / 1000
  };
}
function ccWarp(d, t) {
  var ss = d.sections;
  if (ss.length === 0) return 0;
  var idx = ss.length - 1;
  for (var i = 0; i < ss.length; i++) {
    if (t < ss[i].playStart + ss[i].dur) {
      idx = i;
      break;
    }
  }
  var s = ss[idx];
  var local = Math.min(Math.max(t - s.playStart, 0), s.dur);
  var T = s.authStart + (s.dur > 0 ? local * (s.nat / s.dur) : 0);
  return Math.min(T, d.authoredTotal);
}
var CC_META = Object.assign(Object.create(null), {
  toString: 1,
  toLocaleString: 1,
  valueOf: 1,
  toJSON: 1,
  then: 1,
  constructor: 1,
  hasOwnProperty: 1,
  isPrototypeOf: 1,
  propertyIsEnumerable: 1,
  default: 1
});
function ccCueProxy(table, unknownRef) {
  if (typeof Proxy !== 'function') return table;
  return new Proxy(table, {
    get: function (target, prop) {
      if (typeof prop !== 'string' || prop in target) return target[prop];
      if (CC_META[prop] || prop.indexOf('@@') === 0) return Object.prototype[prop];
      unknownRef.current[prop] = true;
      return NaN;
    }
  });
}
function CcUnknownWatch(props) {
  var tl = useTimeline();
  React.useEffect(function () {
    var next = Object.keys(props.unknownRef.current).sort().join(', ');
    if (next !== props.badge) props.setBadge(next);
  }, [tl.time]);
  return null;
}
function CompositionClock(props) {
  var tl = useTimeline();
  var d = props.derived;
  var T = ccWarp(d, tl.time);
  var value = React.useMemo(function () {
    return {
      T: T,
      CUES: props.cues,
      time: tl.time,
      duration: tl.duration,
      authoredTotal: d.authoredTotal,
      playing: tl.playing || tl.extPlaying === true
    };
  }, [T, props.cues, tl.time, tl.duration, d, tl.playing, tl.extPlaying]);
  return React.createElement(CompositionContext.Provider, {
    value: value
  }, props.children);
}
function Shot(props) {
  var c = useComposition();
  var from = +props.from;
  var to = props.to == null ? Infinity : +props.to;
  var on = isFinite(from) && c.T >= from && c.T < to;
  return React.createElement("div", {
    style: {
      position: 'absolute',
      inset: 0,
      visibility: on ? 'visible' : 'hidden'
    }
  }, props.children);
}
var CAPTION_FADE = 0.18;
function Captions(props) {
  var c = useComposition();
  var t = c.T;
  var items = (props.items || []).filter(function (it) {
    return it && isFinite(+it.at);
  }).sort(function (a, b) {
    return a.at - b.at;
  });
  var active = null;
  var end = Infinity;
  for (var i = 0; i < items.length; i++) {
    if (t < items[i].at) break;
    active = items[i];
    end = typeof active.until === 'number' && isFinite(active.until) ? active.until : i + 1 < items.length ? items[i + 1].at : Infinity;
  }
  if (!active || t >= end) return null;
  var o = Math.min(1, (t - active.at) / CAPTION_FADE);
  if (isFinite(end)) o = Math.min(o, (end - t) / CAPTION_FADE);
  o = Math.max(0, Math.min(1, o));
  return React.createElement("div", {
    "data-om-caption": true,
    style: Object.assign({
      position: 'absolute',
      left: '8%',
      right: '8%',
      bottom: '7%',
      textAlign: 'center',
      opacity: o,
      pointerEvents: 'none',
      font: '500 30px Inter, system-ui, sans-serif',
      color: '#f6f4ef',
      textShadow: '0 1px 14px rgba(0,0,0,0.45)'
    }, props.style)
  }, active.text);
}
function CompositionStage(props) {
  var width = +props.width || 1280;
  var height = +props.height || 720;
  var bg = props.bg || '#0b0b0e';
  var autoplay = props.autoplay == null ? true : String(props.autoplay) !== 'false';
  var loop = props.loop == null ? true : String(props.loop) !== 'false';
  var state = React.useState(props.scenes);
  var raw = state[0];
  var setRaw = state[1];
  var scenes = React.useMemo(function () {
    return ssParse(raw);
  }, [raw]);
  var pstate = React.useState(props.playback);
  var praw = pstate[0];
  var setPraw = pstate[1];
  var pb = React.useMemo(function () {
    return ppParse(praw);
  }, [praw]);
  var unknownRef = React.useRef({});
  var badgeState = React.useState('');
  var badge = badgeState[0];
  var setBadge = badgeState[1];
  var derived = React.useMemo(function () {
    unknownRef.current = {};
    return scenes ? ccDerive(scenes) : null;
  }, [scenes]);
  var cues = React.useMemo(function () {
    return derived ? ccCueProxy(derived.table, unknownRef) : null;
  }, [derived]);
  React.useEffect(function () {
    var next = Object.keys(unknownRef.current).sort().join(', ');
    if (next !== badge) setBadge(next);
  });
  if (!scenes) {
    return React.createElement("div", {
      style: {
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#0b0b0e',
        color: '#c96442',
        font: '500 16px Inter, system-ui, sans-serif',
        textAlign: 'center'
      }
    }, "animations-v3: the scenes prop isn't a valid JSON scene list", React.createElement("br", null), "(expected '[", '{', "\"name\":\"\u2026\",\"dur\":N", '}', ", \u2026]')");
  }
  return React.createElement(React.Fragment, null, React.createElement(Stage, {
    width: width,
    height: height,
    duration: derived.total,
    background: bg,
    autoplay: autoplay,
    loop: loop,
    playback: pb
  }, React.createElement(SceneSync, {
    raw: raw,
    onUpdate: setRaw
  }), typeof praw === 'string' && praw !== '' && React.createElement(PlaybackSync, {
    raw: praw,
    onUpdate: setPraw
  }), React.createElement(CompositionClock, {
    derived: derived,
    cues: cues
  }, props.children), React.createElement(CcUnknownWatch, {
    unknownRef: unknownRef,
    badge: badge,
    setBadge: setBadge
  })), badge !== '' && React.createElement("div", {
    "data-om-unknown-cues": true,
    style: {
      position: 'absolute',
      left: 12,
      bottom: 56,
      zIndex: 10,
      padding: '6px 10px',
      borderRadius: 6,
      background: 'rgba(0,0,0,0.72)',
      color: '#e8906a',
      font: '500 12px Inter, system-ui, sans-serif',
      pointerEvents: 'none'
    }
  }, "choreography references unknown section", badge.indexOf(',') >= 0 ? 's' : '', ": ", badge));
}
var WC_PIXEL_CAP = 11000000;
function wcLayerOpts(props) {
  var w = +props.width || 900,
    h = +props.height || 1200;
  var askScale = +props.scale || 1;
  return {
    width: w,
    height: h,
    scale: Math.min(askScale, Math.sqrt(WC_PIXEL_CAP / (w * h))),
    seed: props.seed == null ? undefined : +props.seed,
    quality: props.quality == null ? undefined : +props.quality
  };
}
var wcWarned = {};
function wcWarnOnce(key, message, err) {
  if (wcWarned[key]) return;
  wcWarned[key] = true;
  console.warn(message, err);
}
function useWatercolorLayers(painting, opts) {
  var kit = window.WatercolorKit;
  if (typeof painting !== 'function' || !kit || typeof kit.layers !== 'function') return null;
  try {
    return kit.layers(painting, wcLayerOpts(opts || {}));
  } catch (e) {
    wcWarnOnce('layers:' + e, 'watercolor painting failed to build; rendering the fallback sheet', e);
    return null;
  }
}
var WatercolorSheetContext = React.createContext(null);
function WatercolorSheet(props) {
  var L = props.layers || null;
  var style = Object.assign({
    position: 'relative',
    display: 'block',
    width: '100%',
    aspectRatio: L ? L.width + ' / ' + L.height : '3 / 4',
    isolation: 'isolate',
    overflow: 'hidden'
  }, props.style);
  if (!L) {
    return React.createElement("div", {
      style: Object.assign(style, {
        background: '#f4f1e8',
        color: '#8a8270',
        font: '12px system-ui, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      })
    }, "watercolor-kit.js not loaded (or the painting failed to build)");
  }
  return React.createElement(WatercolorSheetContext.Provider, {
    value: L
  }, React.createElement("div", {
    style: style,
    "data-om-watercolor-sheet": true
  }, React.createElement("img", {
    src: L.paper,
    alt: props.alt || '',
    style: {
      position: 'absolute',
      left: 0,
      top: 0,
      width: '100%',
      height: '100%',
      display: 'block'
    }
  }), props.children));
}
function WatercolorStroke(props) {
  var fromSheet = React.useContext(WatercolorSheetContext);
  var L = props.layers || fromSheet;
  if (!L) return null;
  var i = +props.index;
  if (!(i >= 0) || i >= L.count) return null;
  var at = props.at == null ? 1 : clamp(+props.at, 0, 1);
  if (!(at > 0)) return null;
  var box, src;
  try {
    box = L.box(i);
    src = box ? L.src(i, at) : null;
  } catch (e) {
    wcWarnOnce('stroke:' + i + ':' + e, 'watercolor stroke ' + i + ' failed to render; skipping it', e);
    return null;
  }
  if (!box || !src) return null;
  var style = Object.assign({
    position: 'absolute',
    display: 'block',
    left: box.x * 100 + '%',
    top: box.y * 100 + '%',
    width: box.w * 100 + '%',
    height: box.h * 100 + '%',
    mixBlendMode: L.kind(i) === 'reserve' ? 'normal' : 'multiply',
    pointerEvents: 'none'
  }, props.style);
  return React.createElement("img", {
    src: src,
    alt: "",
    "data-om-watercolor-stroke": i,
    "data-om-stroke-kind": L.kind(i),
    style: style
  });
}
function WatercolorPainting(props) {
  var c = useComposition();
  var from = +props.from || 0;
  var to = props.to == null ? from + 6 : +props.to;
  var u = clamp((c.T - from) / Math.max(to - from, 0.001), 0, 1);
  var eased = Easing.easeInOutQuad(u);
  var L = useWatercolorLayers(props.painting, props);
  var tick = React.useState(0)[1];
  var warmed = React.useRef(null);
  React.useEffect(function () {
    if (!L || typeof L.warm !== 'function') return;
    var p = L.warm();
    if (warmed.current === p) return;
    var live = true;
    p.then(function () {
      warmed.current = p;
      if (live) tick(function (x) {
        return x + 1;
      });
    });
    return function () {
      live = false;
    };
  }, [L && L.paper, props.painting]);
  var strokes = [];
  if (L) {
    for (var i = 0; i < L.count; i++) {
      var sp = L.span(i);
      var at = clamp((eased - sp.from) / Math.max(sp.to - sp.from, 1e-6), 0, 1);
      if (at <= 0) break;
      strokes.push(React.createElement(WatercolorStroke, {
        key: i,
        layers: L,
        index: i,
        at: at
      }));
    }
  }
  return React.createElement(WatercolorSheet, {
    layers: L,
    style: props.style,
    alt: props.alt
  }, strokes);
}
function WatercolorReveal(props) {
  var c = useComposition();
  var from = +props.from || 0;
  var to = props.to == null ? from + 6 : +props.to;
  var u = clamp((c.T - from) / Math.max(to - from, 0.001), 0, 1);
  var style = Object.assign({
    display: 'block',
    width: '100%',
    height: '100%',
    objectFit: 'contain'
  }, props.style);
  var frames = Array.isArray(props.frames) && props.frames.length ? props.frames : null;
  var steps = frames ? frames.length - 1 : Math.max(1, Math.round(+props.steps || 36));
  var i = Math.min(steps, Math.round(Easing.easeInOutQuad(u) * steps));
  var painting = typeof props.painting === 'function' ? props.painting : null;
  var kit = window.WatercolorKit;
  var w = +props.width || 900,
    h = +props.height || 1200;
  var askScale = +props.scale || Math.min(2, window.devicePixelRatio || 1);
  var opts = {
    width: w,
    height: h,
    scale: Math.min(askScale, Math.sqrt(11000000 / (w * h))),
    seed: props.seed == null ? undefined : +props.seed,
    steps: steps,
    type: props.format || 'image/jpeg',
    quality: props.quality == null ? 0.88 : +props.quality
  };
  var key = opts.width + 'x' + opts.height + '#' + opts.seed + '@' + opts.scale + '/' + steps + ':' + opts.type + '/' + opts.quality;
  var cache = React.useRef({
    fn: null,
    key: '',
    frames: {},
    baking: false
  }).current;
  var tick = React.useState(0)[1];
  if (cache.fn !== painting && String(cache.fn) !== String(painting) || cache.key !== key) {
    cache.key = key;
    cache.frames = {};
    cache.baking = false;
  }
  cache.fn = painting;
  React.useEffect(function () {
    if (frames || cache.baking || !painting || !kit || typeof kit.bake !== 'function') return;
    cache.baking = true;
    var target = cache.frames;
    try {
      kit.bake(painting, opts, function (n, _t, url) {
        target[n] = url;
      }).then(function (all) {
        if (cache.frames !== target) return;
        for (var n = 0; n < all.length; n++) target[n] = all[n];
        tick(function (x) {
          return x + 1;
        });
      }).catch(function () {});
    } catch (e) {}
  });
  if (frames) return React.createElement("img", {
    src: frames[i],
    alt: props.alt || '',
    style: style
  });
  if (!kit || !painting) {
    return React.createElement("div", {
      style: Object.assign({
        width: '100%',
        height: '100%',
        background: '#f4f1e8',
        color: '#8a8270',
        font: '12px system-ui, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }, props.style)
    }, "watercolor-kit.js not loaded (or no painting function)");
  }
  if (!cache.frames[i]) {
    try {
      cache.frames[i] = kit.frame(painting, Object.assign({}, opts, {
        at: i / steps
      }));
    } catch (e) {
      return React.createElement("div", {
        style: Object.assign({
          width: '100%',
          height: '100%',
          background: '#f4f1e8',
          color: '#8a8270',
          font: '12px system-ui, sans-serif',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }, props.style)
      }, "painting too large to render (", String(e && e.message).slice(0, 80), ")");
    }
  }
  return React.createElement("img", {
    src: cache.frames[i],
    alt: props.alt || '',
    style: style
  });
}
Object.assign(window, {
  Easing,
  interpolate,
  animate,
  clamp,
  TimelineContext,
  useTime,
  useTimeline,
  Stage,
  PlaybackBar,
  CompositionStage,
  useComposition,
  Shot,
  Captions,
  WatercolorReveal,
  WatercolorPainting,
  WatercolorSheet,
  WatercolorStroke,
  useWatercolorLayers
});
;(function () {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const NAVY = '#0B2545',
  GOLD = '#E8B100',
  WHITE = '#FFFFFF';
const W = 1920,
  H = 1080;
const MOTION = {
  enter: Easing.easeOutCubic,
  draw: Easing.easeInOutCubic,
  pop: Easing.easeOutBack
};
const prog = (t, a, b, ease = MOTION.enter) => animate({
  from: 0,
  to: 1,
  start: a,
  end: b,
  ease
})(t);
const lerp = (a, b, p) => a + (b - a) * p;
const V = {
  vesica: 'M4 52A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z',
  seeds: [[54, 54], [54, 41], [66.4, 50], [61.6, 64.5], [46.4, 64.5], [41.6, 50], [61.3, 31.7], [72.4, 43.8], [77.9, 51.9], [70.9, 68.1], [61.3, 73.1], [44.6, 75], [37.7, 68.7], [30, 53.2], [36.2, 42.9], [48.7, 31.1]],
  scatter: [[22, 48], [-34, 8], [118, 22], [96, 92], [-12, 96], [-48, 52], [70, -6], [140, 58], [150, 4], [128, 106], [48, 112], [6, -10], [-60, 86], [-20, 30], [30, 4], [86, 40]],
  edges: [[49.3, 47.5, 58.7, 47.5], [58.7, 47.5, 61.6, 56.5], [61.6, 56.5, 54, 62], [54, 62, 46.4, 56.5], [46.4, 56.5, 49.3, 47.5], [54.9, 34.2, 63.4, 40.8], [63.4, 40.8, 63.4, 41.1], [63.4, 41.1, 58.7, 47.5], [49.3, 47.5, 45.1, 41.7], [45.1, 41.7, 44.8, 39.5], [44.8, 39.5, 54.9, 34.2], [69.2, 58.9, 61.6, 56.5], [63.4, 41.1, 72.3, 49.8], [72.3, 49.8, 70.9, 58.5], [70.9, 58.5, 69.2, 58.9], [54, 68.6, 54, 62], [69.2, 58.9, 65.2, 69], [65.2, 69, 54, 68.6], [38.4, 59.1, 46.4, 56.5], [54, 68.6, 52.6, 70.9], [52.6, 70.9, 43.4, 69.4], [43.4, 69.4, 38.4, 59.1], [38.4, 59.1, 37.8, 59], [37.8, 59, 35.2, 49.3], [35.2, 49.3, 45.1, 41.7], [71.5, 33.5, 63.4, 40.8], [54.9, 34.2, 55.2, 27], [79.4, 44.9, 72.3, 49.8], [79.7, 62.3, 70.9, 58.5], [69.1, 76.4, 65.2, 69], [53.8, 81, 52.6, 70.9], [37.8, 75.6, 43.4, 69.4], [28.7, 63.5, 37.8, 59], [28.5, 45.2, 35.2, 49.3], [38, 32.3, 44.8, 39.5]],
  pupil: '49.3,47.5 58.7,47.5 61.6,56.5 54,62 46.4,56.5',
  field: [[-25, 4], [-12, -28], [-12, 36], [8, -36], [8, -10], [8, 20], [8, 44], [30, -22], [30, 30], [72, -26], [72, 32], [95, -36], [95, -8], [95, 20], [95, 44], [120, 4]]
};
V.edgesSorted = V.edges.map(e => ({
  e,
  d: Math.hypot((e[0] + e[2]) / 2 - 54, (e[1] + e[3]) / 2 - 54)
})).sort((a, b) => a.d - b.d).map(o => o.e);
function MarkVoronoi({
  id,
  seedP = 1,
  discP = 1,
  edgeP = 1,
  pupilP = 1,
  openP = 1,
  browP = 1
}) {
  const off = (1 - browP) * -34;
  const y = x => 26 + 0.18 * x + off;
  const n = V.edgesSorted.length;
  return React.createElement("g", null, React.createElement("defs", null, React.createElement("clipPath", {
    id: id + 'brow'
  }, React.createElement("polygon", {
    points: `-500,${y(-500)} 600,${y(600)} 600,600 -500,600`
  })), React.createElement("clipPath", {
    id: id + 'iris'
  }, React.createElement("circle", {
    cx: "54",
    cy: "54",
    r: "24"
  }))), React.createElement("g", {
    clipPath: `url(#${id}brow)`
  }, React.createElement("path", {
    d: V.vesica,
    fill: WHITE,
    opacity: openP > 0.02 ? 1 : 0,
    transform: `translate(0 52) scale(1 ${Math.max(openP, 0.0001)}) translate(0 -52)`
  }), React.createElement("circle", {
    cx: "54",
    cy: "54",
    r: 24 * discP,
    fill: GOLD
  }), React.createElement("g", {
    clipPath: `url(#${id}iris)`,
    stroke: NAVY,
    strokeWidth: "2.4",
    strokeLinecap: "round",
    fill: "none"
  }, V.edgesSorted.map((e, i) => {
    const p = clamp(edgeP * (n + 6) / 7 - i / 7, 0, 1);
    return React.createElement("line", {
      key: i,
      x1: e[0],
      y1: e[1],
      x2: e[2],
      y2: e[3],
      pathLength: "1",
      strokeDasharray: "1",
      strokeDashoffset: 1 - p
    });
  })), React.createElement("polygon", {
    points: V.pupil,
    fill: NAVY,
    stroke: NAVY,
    strokeWidth: "2.4",
    strokeLinejoin: "round",
    transform: `translate(54 54.6) scale(${pupilP}) translate(-54 -54.6)`
  })), seedP < 1.01 && V.seeds.map((s, i) => {
    const a = V.scatter[i];
    const p = clamp(seedP * 1.3 - i * 0.02, 0, 1);
    const ep = MOTION.draw(p);
    return React.createElement("circle", {
      key: i,
      cx: lerp(a[0], s[0], ep),
      cy: lerp(a[1], s[1], ep),
      r: "1.5",
      fill: i === 0 ? GOLD : WHITE,
      opacity: 1 - edgeP
    });
  }));
}
function Players({
  seedP,
  linkP,
  fade,
  tx,
  ty
}) {
  if (fade <= 0) return null;
  return React.createElement("g", {
    opacity: fade
  }, V.field.map((a, i) => {
    const p = MOTION.draw(clamp(seedP * 1.25 - i * 0.015, 0, 1));
    const s = V.seeds[i];
    const x = lerp(a[0], s[0], p),
      y = lerp(a[1], s[1], p);
    const lp = clamp(linkP * 1.3 - i * 0.02, 0, 1);
    return React.createElement("g", {
      key: i
    }, React.createElement("line", {
      x1: x,
      y1: y,
      x2: lerp(x, tx, lp),
      y2: lerp(y, ty, lp),
      stroke: WHITE,
      strokeWidth: "0.35",
      opacity: (1 - p) * 0.7
    }), React.createElement("circle", {
      cx: x,
      cy: y,
      r: lerp(2.2, 1.4, p),
      fill: i === 0 ? GOLD : WHITE
    }));
  }));
}
function MarkFuria({
  id,
  lidP = 1,
  discP = 1,
  edgeP = 1,
  pupilP = 1,
  browP = 1,
  lookX = 0,
  squint = 0,
  scanX = 0,
  scanOn = 0,
  campo = false,
  seedP = 1
}) {
  if (campo) return React.createElement(MarkCampo, {
    id,
    lidP,
    discP,
    edgeP,
    pupilP,
    browP,
    lookX,
    squint,
    scanX,
    scanOn,
    seedP
  });
  const off = (1 - lidP) * 70 + squint;
  const y = x => 22 + 0.3 * x + off;
  const n = V.edgesSorted.length;
  const bd = (1 - browP) * -60 + squint * 0.6;
  return React.createElement("g", null, React.createElement("defs", null, React.createElement("clipPath", {
    id: id + 'lid'
  }, React.createElement("polygon", {
    points: `-500,${y(-500)} 600,${y(600)} 600,600 -500,600`
  })), React.createElement("clipPath", {
    id: id + 'ves'
  }, React.createElement("path", {
    d: V.vesica
  })), React.createElement("clipPath", {
    id: id + 'iris'
  }, React.createElement("circle", {
    cx: "54",
    cy: "54",
    r: "24"
  }))), React.createElement("polygon", {
    points: "12,19.6 86,30.8 99,46.7",
    fill: GOLD,
    opacity: browP > 0.01 ? 1 : 0,
    transform: `translate(0 ${bd})`
  }), React.createElement("g", {
    clipPath: `url(#${id}lid)`
  }, React.createElement("g", {
    clipPath: `url(#${id}ves)`
  }, React.createElement("path", {
    d: V.vesica,
    fill: WHITE
  }), React.createElement("circle", {
    cx: 54 + lookX,
    cy: "54",
    r: 24 * discP,
    fill: GOLD
  }), React.createElement("g", {
    clipPath: `url(#${id}iris)`,
    transform: `translate(${lookX} 0)`,
    stroke: NAVY,
    strokeWidth: "2.4",
    strokeLinecap: "round",
    fill: "none"
  }, V.edgesSorted.map((e, i) => {
    const p = clamp(edgeP * (n + 6) / 7 - i / 7, 0, 1);
    return React.createElement("line", {
      key: i,
      x1: e[0],
      y1: e[1],
      x2: e[2],
      y2: e[3],
      pathLength: "1",
      strokeDasharray: "1",
      strokeDashoffset: 1 - p
    });
  })), React.createElement("polygon", {
    points: V.pupil,
    fill: NAVY,
    stroke: NAVY,
    strokeWidth: "2.4",
    strokeLinejoin: "round",
    transform: `translate(${lookX} 0) translate(54 54.6) scale(${pupilP}) translate(-54 -54.6)`
  }), React.createElement("line", {
    x1: scanX,
    y1: "0",
    x2: scanX,
    y2: "100",
    stroke: WHITE,
    strokeWidth: "2.4",
    opacity: scanOn
  }))));
}
function MarkCampo({
  id,
  lidP,
  discP,
  edgeP,
  pupilP,
  browP,
  lookX,
  squint,
  scanX,
  scanOn,
  seedP
}) {
  const yL = x => 22 + 0.3 * x + (1 - lidP) * 70 + squint;
  const yS = x => 22 + 0.3 * x + squint - (1 - lidP) * 30;
  const n = V.edgesSorted.length;
  const bd = (1 - browP) * -60 + squint * 0.6;
  const open = lidP > 0.999;
  return React.createElement("g", null, React.createElement("defs", null, React.createElement("clipPath", {
    id: id + 'lid'
  }, React.createElement("polygon", {
    points: `-500,${yL(-500)} 600,${yL(600)} 600,600 -500,600`
  })), React.createElement("clipPath", {
    id: id + 'top'
  }, React.createElement("polygon", {
    points: `-500,${yS(-500)} 600,${yS(600)} 600,600 -500,600`
  })), React.createElement("clipPath", {
    id: id + 'ves'
  }, React.createElement("path", {
    d: V.vesica
  })), React.createElement("clipPath", {
    id: id + 'iris'
  }, React.createElement("circle", {
    cx: "54",
    cy: "54",
    r: "24"
  }))), React.createElement("polygon", {
    points: "12,19.6 86,30.8 99,46.7",
    fill: GOLD,
    opacity: browP > 0.01 ? 1 : 0,
    transform: `translate(0 ${bd})`
  }), React.createElement("g", {
    clipPath: `url(#${id}lid)`
  }, React.createElement("path", {
    d: V.vesica,
    fill: WHITE,
    clipPath: `url(#${id}top)`
  })), React.createElement("g", {
    clipPath: `url(#${id}top)`
  }, React.createElement("g", {
    clipPath: open ? `url(#${id}ves)` : undefined
  }, React.createElement("circle", {
    cx: 54 + lookX,
    cy: "54",
    r: 24 * discP,
    fill: GOLD
  }), React.createElement("g", {
    clipPath: `url(#${id}iris)`,
    transform: `translate(${lookX} 0)`,
    stroke: NAVY,
    strokeWidth: "2.4",
    strokeLinecap: "round",
    fill: "none"
  }, V.edgesSorted.map((e, i) => {
    const p = clamp(edgeP * (n + 6) / 7 - i / 7, 0, 1);
    return React.createElement("line", {
      key: i,
      x1: e[0],
      y1: e[1],
      x2: e[2],
      y2: e[3],
      pathLength: "1",
      strokeDasharray: "1",
      strokeDashoffset: 1 - p
    });
  })), React.createElement("polygon", {
    points: V.pupil,
    fill: NAVY,
    stroke: NAVY,
    strokeWidth: "2.4",
    strokeLinejoin: "round",
    transform: `translate(${lookX} 0) translate(54 54.6) scale(${pupilP}) translate(-54 -54.6)`
  }), React.createElement("line", {
    x1: scanX,
    y1: "0",
    x2: scanX,
    y2: "100",
    stroke: WHITE,
    strokeWidth: "2.4",
    opacity: scanOn
  }))), edgeP < 1 && V.seeds.map((p0, i) => {
    const a = V.scatter[i];
    const ep = MOTION.draw(clamp(seedP * 1.3 - i * 0.02, 0, 1));
    return React.createElement("circle", {
      key: i,
      cx: lerp(a[0], p0[0], ep),
      cy: lerp(a[1], p0[1], ep),
      r: "1.5",
      fill: i === 0 ? GOLD : WHITE,
      opacity: 1 - edgeP
    });
  }));
}
function Pitch({
  opacity
}) {
  if (opacity <= 0.001) return null;
  const x0 = 210,
    y0 = 115,
    w = 1500,
    h = 850;
  return React.createElement("g", {
    stroke: WHITE,
    strokeWidth: "3",
    fill: "none",
    opacity: opacity * 0.14
  }, React.createElement("rect", {
    x: x0,
    y: y0,
    width: w,
    height: h
  }), React.createElement("line", {
    x1: x0 + w / 2,
    y1: y0,
    x2: x0 + w / 2,
    y2: y0 + h
  }), React.createElement("circle", {
    cx: x0 + w / 2,
    cy: y0 + h / 2,
    r: "120"
  }), React.createElement("rect", {
    x: x0,
    y: y0 + h / 2 - 200,
    width: "240",
    height: "400"
  }), React.createElement("rect", {
    x: x0 + w - 240,
    y: y0 + h / 2 - 200,
    width: "240",
    height: "400"
  }));
}
function Wordmark({
  x,
  y,
  F,
  p,
  accentP,
  align = 'left'
}) {
  const a = MOTION.pop(accentP);
  return React.createElement("div", {
    style: {
      position: 'absolute',
      left: x,
      top: y - F * 0.5 - F * 0.2,
      paddingTop: F * 0.2,
      fontFamily: 'Poppins, sans-serif',
      fontWeight: 700,
      fontSize: F,
      lineHeight: 1,
      letterSpacing: '0.02em',
      color: WHITE,
      whiteSpace: 'nowrap',
      transform: `translateX(${align === 'center' ? '-50%' : '0'}) translateX(${(1 - p) * -40}px)`,
      clipPath: `inset(0 ${100 - 100 * p}% 0 0)`
    }
  }, "OJO DE ", React.createElement("span", {
    style: {
      position: 'relative',
      display: 'inline-block'
    }
  }, "A", React.createElement("span", {
    style: {
      position: 'absolute',
      left: '0.3em',
      top: '-0.14em',
      width: '0.24em',
      height: '0.17em',
      background: GOLD,
      clipPath: 'polygon(52% 0,100% 0,40% 100%,0 100%)',
      transform: `translateY(${(1 - a) * -0.5}em) scale(${Math.max(a, 0)})`,
      opacity: accentP > 0 ? 1 : 0
    }
  })), "GUILA");
}
const WORD_W = 7.62;
const F = 104,
  GAP = 0.42 * F;
function lockup(Sf, minX, maxX, mcx) {
  const vw = (maxX - minX) * Sf / 100;
  const left = W / 2 - (vw + GAP + WORD_W * F) / 2;
  return {
    cx: left + (mcx - minX) * Sf / 100,
    wx: left + vw + GAP
  };
}
function sceneFade(t, dur) {
  return prog(t, 0, 0.35) * (1 - prog(t, dur - 0.45, dur, MOTION.draw));
}
function Frame({
  t,
  dur,
  opacity,
  children,
  words
}) {
  const z = 1 + 0.03 * clamp(t / dur, 0, 1);
  return React.createElement("div", {
    style: {
      position: 'absolute',
      inset: 0,
      opacity,
      transform: `scale(${z})`,
      transformOrigin: '50% 50%'
    }
  }, React.createElement("svg", {
    width: W,
    height: H,
    viewBox: `0 0 ${W} ${H}`,
    style: {
      position: 'absolute',
      inset: 0,
      overflow: 'visible'
    }
  }, children), words);
}
const HAS_CANCHA = () => String(window.OM_SCENES || '').includes('"Cancha"');
function PitchIntro() {
  const {
    T,
    CUES
  } = useComposition();
  if (!HAS_CANCHA()) return null;
  const t = T - CUES.Cancha,
    m = T - CUES.Mirada;
  const x0 = 210,
    y0 = 115,
    w = 1500,
    h = 850,
    cx = W / 2,
    cy = H / 2;
  const d = (a, b) => 1 - prog(t, a, b, MOTION.draw);
  const fade = 1 - prog(m, 0.9, 1.7, MOTION.draw);
  const grow = prog(m, 0.1, 1.0, MOTION.draw);
  const riseM = lerp(46, 0, prog(m, 0.2, 1.4, MOTION.draw));
  const ccx = lerp(cx, cx + 22, grow),
    ccy = lerp(cy, cy + (4 + riseM) * 8.8, grow),
    cr = lerp(120, 211, grow);
  const z = 1 + 0.03 * clamp(m / 9, 0, 1);
  const L = (x1, y1, x2, y2, a, b, k) => React.createElement("line", {
    key: k,
    x1: x1,
    y1: y1,
    x2: x2,
    y2: y2,
    pathLength: "1",
    strokeDasharray: "1",
    strokeDashoffset: d(a, b)
  });
  return React.createElement(Shot, {
    from: CUES.Cancha,
    to: CUES.Mirada + 2
  }, React.createElement("svg", {
    width: W,
    height: H,
    viewBox: `0 0 ${W} ${H}`,
    style: {
      position: 'absolute',
      inset: 0,
      opacity: prog(t, 0, 0.2) * fade,
      transform: `scale(${m > 0 ? z : 1})`
    }
  }, React.createElement("g", {
    stroke: WHITE,
    strokeWidth: "4",
    fill: "none",
    strokeLinecap: "round"
  }, L(cx, y0 + h, cx, y0, 0.1, 0.9, 'mid'), L(x0, y0 + h, x0 + w, y0 + h, 0.1, 0.7, 'b'), L(x0, y0 + h, x0, y0, 0.4, 1.1, 'l'), L(x0 + w, y0 + h, x0 + w, y0, 0.4, 1.1, 'r'), L(x0, y0, x0 + w, y0, 0.9, 1.5, 't'), L(x0, y0 + h / 2 + 200, x0 + 240, y0 + h / 2 + 200, 1.0, 1.3, 'b1'), L(x0 + 240, y0 + h / 2 + 200, x0 + 240, y0 + h / 2 - 200, 1.1, 1.5, 'b2'), L(x0 + 240, y0 + h / 2 - 200, x0, y0 + h / 2 - 200, 1.3, 1.6, 'b3'), L(x0 + w, y0 + h / 2 + 200, x0 + w - 240, y0 + h / 2 + 200, 1.0, 1.3, 'c1'), L(x0 + w - 240, y0 + h / 2 + 200, x0 + w - 240, y0 + h / 2 - 200, 1.1, 1.5, 'c2'), L(x0 + w - 240, y0 + h / 2 - 200, x0 + w, y0 + h / 2 - 200, 1.3, 1.6, 'c3'), React.createElement("circle", {
    cx: ccx,
    cy: ccy,
    r: cr,
    pathLength: "1",
    strokeDasharray: "1",
    strokeDashoffset: d(1.2, 2.1),
    transform: `rotate(90 ${ccx} ${ccy})`,
    strokeWidth: lerp(4, 6, grow)
  })), m <= 0 && V.field.map((a, i) => {
    const k = MOTION.pop(prog(t, 1.4 + i * 0.04, 1.75 + i * 0.04, x => x));
    return React.createElement("circle", {
      key: i,
      cx: cx + (a[0] - 51.5) * 8.8,
      cy: cy + (a[1] - 4) * 8.8,
      r: Math.max(0, 2.2 * 8.8 * k),
      fill: i === 0 ? GOLD : WHITE
    });
  }), React.createElement("circle", {
    cx: ccx,
    cy: ccy,
    r: 10 * MOTION.pop(prog(t, 1.9, 2.3, x => x)) * (1 - grow),
    fill: GOLD
  })));
}
function SceneVoronoi() {
  const {
    T,
    CUES,
    authoredTotal
  } = useComposition();
  const campo = window.OM_INTRO === 'campo';
  const t = T - CUES.Mirada,
    dur = authoredTotal - CUES.Mirada;
  const fadeIn = !HAS_CANCHA();
  const o = campo ? 0.9 : 0;
  const move = prog(t, 5.6 + o, 6.5 + o, MOTION.draw);
  const L = lockup(281, 4, 99, 51.5);
  const S = lerp(880, 281, move),
    cx = lerp(W / 2, L.cx, move);
  const rise = campo ? 0 : lerp(46, 0, prog(t, 0.2, 1.4, MOTION.draw));
  const lookX = t < 3.6 + o ? animate({
    from: 0,
    to: -9,
    start: 3.0 + o,
    end: 3.35 + o,
    ease: MOTION.draw
  })(t) : t < 4.3 + o ? animate({
    from: -9,
    to: 9,
    start: 3.6 + o,
    end: 4.05 + o,
    ease: MOTION.draw
  })(t) : animate({
    from: 9,
    to: 0,
    start: 4.3 + o,
    end: 4.6 + o,
    ease: MOTION.draw
  })(t);
  const sq = t < 5 + o ? animate({
    from: 0,
    to: 5,
    start: 4.6 + o,
    end: 4.85 + o,
    ease: MOTION.draw
  })(t) : animate({
    from: 5,
    to: 0,
    start: 5.5 + o,
    end: 5.75 + o,
    ease: MOTION.draw
  })(t);
  const scanX = animate({
    from: 8,
    to: 98,
    start: 4.7 + o,
    end: 5.5 + o,
    ease: MOTION.draw
  })(t);
  const scanOn = prog(t, 4.65 + o, 4.75 + o, x => x) * (1 - prog(t, 5.45 + o, 5.55 + o, x => x));
  const pupil = t < 5 + o ? lerp(1, 0.75, prog(t, 4.6 + o, 4.9 + o)) : lerp(0.75, 1, prog(t, 5.5 + o, 5.8 + o));
  const k = campo ? {
    seedP: prog(t, 0.2, 1.5, MOTION.draw),
    discP: MOTION.pop(prog(t, 1.2, 1.9, x => x)),
    edgeP: prog(t, 1.6, 2.7, MOTION.draw),
    pupilP: MOTION.pop(prog(t, 2.5, 2.9, x => x)) * pupil,
    lidP: prog(t, 2.8, 3.5, MOTION.draw),
    browP: MOTION.pop(prog(t, 3.4, 3.75, Easing.easeInQuad))
  } : {
    lidP: prog(t, 0.2, 1.4, MOTION.draw),
    discP: MOTION.pop(prog(t, 1.0, 1.6, x => x)),
    edgeP: prog(t, 1.4, 2.4, MOTION.draw),
    pupilP: MOTION.pop(prog(t, 2.2, 2.6, x => x)) * pupil,
    browP: MOTION.pop(prog(t, 2.5, 2.85, Easing.easeInQuad))
  };
  return React.createElement(Shot, {
    from: CUES.Mirada,
    to: authoredTotal + 1
  }, React.createElement(Frame, {
    t: t,
    dur: dur,
    opacity: fadeIn ? sceneFade(t, dur) : 1 - prog(t, dur - 0.45, dur, MOTION.draw),
    words: React.createElement(Wordmark, {
      x: L.wx,
      y: H / 2,
      F: F,
      p: prog(t, 6.0 + o, 6.8 + o, MOTION.draw),
      accentP: prog(t, 6.7 + o, 7.1 + o)
    })
  }, campo && React.createElement(Pitch, {
    opacity: 1 - prog(t, 1.0, 1.8)
  }), React.createElement("g", {
    transform: `translate(${cx} ${H / 2}) scale(${S / 100}) translate(-51.5 ${-50 + rise})`
  }, !fadeIn && React.createElement(Players, {
    seedP: prog(t, 0.45, 1.5, x => x),
    linkP: prog(t, 0.0, 0.5, MOTION.draw),
    fade: 1 - prog(t, 1.5, 2.2),
    tx: lerp(51.5, 54, prog(t, 0.1, 1.0, MOTION.draw)),
    ty: lerp(0, 4 + rise, prog(t, 0.1, 1.0, MOTION.draw)) + 50 - rise
  }), React.createElement(MarkFuria, _extends({
    id: "af",
    campo: campo
  }, k, {
    lookX: lookX,
    squint: sq,
    scanX: scanX,
    scanOn: scanOn
  })))));
}
function Piece() {
  const {
    time
  } = useComposition();
  return React.createElement("div", {
    "data-screen-label": `t=${Math.floor(time)}s`,
    style: {
      position: 'absolute',
      inset: 0,
      background: NAVY,
      overflow: 'hidden'
    }
  }, React.createElement(PitchIntro, null), React.createElement(SceneVoronoi, null));
}
function MiradaRapaz() {
  const [tw, setTweak] = useTweaks(window.TWEAK_DEFAULTS || {
    motionEditor: true
  });
  return React.createElement(React.Fragment, null, React.createElement(CompositionStage, {
    width: 1920,
    height: 1080,
    scenes: window.OM_SCENES,
    playback: window.OM_PLAYBACK,
    bg: NAVY
  }, React.createElement(Piece, null)), React.createElement(TweaksPanel, null, React.createElement(TweakSection, {
    label: "Video"
  }), React.createElement(TweakToggle, {
    label: "Motion editor",
    value: tw.motionEditor,
    onChange: v => setTweak('motionEditor', v)
  })));
}
window.MiradaRapaz = MiradaRapaz;
window.__OjoIntroPieza = Piece;
})();
;(function () {
const NAVY = '#0B2545',
  GOLD = '#E8B100',
  WHITE = '#FFFFFF';
const SIZE = 512;
const MOTION = {
  enter: Easing.easeOutCubic,
  move: Easing.easeInOutCubic,
  snap: Easing.easeInQuad
};
const tw = (t, a, b, from, to, ease = MOTION.move) => animate({
  from,
  to,
  start: a,
  end: b,
  ease
})(t);
const VESICA = 'M4 52A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z';
const EDGES = 'M69.9 32.2L59.8 46M48.2 46L38.1 32.2M79.7 62.3L63.4 57.1M54 81L54 63.9M28.3 62.3L44.6 57.1';
const PUPIL = 'M48.2 46L59.8 46L63.4 57.1L54 63.9L44.6 57.1Z';
function Eye({
  lookX,
  lid,
  pupil,
  scanX,
  scanOn,
  browDy
}) {
  const y = x => 22 + 0.3 * x + lid;
  return React.createElement("svg", {
    width: SIZE,
    height: SIZE,
    viewBox: "0 0 100 100",
    style: {
      position: 'absolute',
      inset: 0
    }
  }, React.createElement("defs", null, React.createElement("clipPath", {
    id: "lv"
  }, React.createElement("path", {
    d: VESICA
  })), React.createElement("clipPath", {
    id: "ll"
  }, React.createElement("polygon", {
    points: `-50,${y(-50)} 150,${y(150)} 150,150 -50,150`
  })), React.createElement("clipPath", {
    id: "li"
  }, React.createElement("circle", {
    cx: "54",
    cy: "54",
    r: "24"
  }))), React.createElement("g", {
    transform: "translate(50 50) scale(0.68) translate(-52 -49)"
  }, React.createElement("polygon", {
    points: "10,17 86,27 99,46",
    fill: GOLD,
    transform: `translate(0 ${browDy})`
  }), React.createElement("g", {
    clipPath: "url(#lv)"
  }, React.createElement("g", {
    clipPath: "url(#ll)"
  }, React.createElement("path", {
    d: VESICA,
    fill: WHITE
  }), React.createElement("g", {
    transform: `translate(${lookX} 0)`
  }, React.createElement("circle", {
    cx: "54",
    cy: "54",
    r: "24",
    fill: GOLD
  }), React.createElement("path", {
    clipPath: "url(#li)",
    d: EDGES,
    fill: "none",
    stroke: NAVY,
    strokeWidth: "4.5",
    strokeLinecap: "round"
  }), React.createElement("path", {
    d: PUPIL,
    fill: NAVY,
    stroke: NAVY,
    strokeWidth: "4",
    strokeLinejoin: "round",
    transform: `translate(54 55) scale(${pupil}) translate(-54 -55)`
  })), React.createElement("line", {
    x1: scanX,
    y1: "0",
    x2: scanX,
    y2: "100",
    stroke: NAVY,
    strokeWidth: "2.2",
    opacity: scanOn
  })))));
}
function Piece() {
  const {
    T,
    CUES,
    time
  } = useComposition();
  const m = CUES.Mirada,
    p = CUES.Parpadeo,
    e = CUES.Escaneo,
    z = CUES.Pausa;
  const lookX = T < m + 0.9 ? tw(T, m + 0.25, m + 0.6, 0, -9) : T < m + 1.7 ? tw(T, m + 0.95, m + 1.45, -9, 9) : tw(T, m + 1.8, m + 2.15, 9, 0);
  const blink = T < p + 0.5 ? tw(T, p + 0.05, p + 0.25, 0, 42, MOTION.snap) : tw(T, p + 0.35, p + 0.75, 42, 0, MOTION.enter);
  const squint = T < e + 1 ? tw(T, e + 0.0, e + 0.3, 0, 5) : tw(T, e + 2.0, e + 2.3, 5, 0);
  const lid = Math.max(blink, squint);
  const browDy = blink / 42 * 3 + squint / 5 * 2.5;
  const pupil = T < e + 1 ? tw(T, e + 0.0, e + 0.4, 1, 0.72, MOTION.enter) : tw(T, e + 2.0, e + 2.3, 0.72, 1, MOTION.enter);
  const scanX = T < e + 1.3 ? tw(T, e + 0.4, e + 1.2, 6, 98) : tw(T, e + 1.3, e + 2.0, 98, 6);
  const scanOn = T < e + 1 ? tw(T, e + 0.35, e + 0.45, 0, 1, x => x) : tw(T, e + 1.95, e + 2.1, 1, 0, x => x);
  return React.createElement("div", {
    "data-screen-label": `t=${Math.floor(time)}s`,
    style: {
      position: 'absolute',
      inset: 0,
      background: NAVY
    }
  }, React.createElement(Eye, {
    lookX: lookX,
    lid: lid,
    pupil: pupil,
    scanX: scanX,
    scanOn: scanOn,
    browDy: browDy
  }));
}
function OjoLoop() {
  const [t, setTweak] = useTweaks(window.TWEAK_DEFAULTS || {
    motionEditor: true
  });
  return React.createElement(React.Fragment, null, React.createElement(CompositionStage, {
    width: SIZE,
    height: SIZE,
    scenes: window.OM_SCENES,
    playback: window.OM_PLAYBACK,
    bg: NAVY
  }, React.createElement(Piece, null)), React.createElement(TweaksPanel, null, React.createElement(TweakSection, {
    label: "Video"
  }), React.createElement(TweakToggle, {
    label: "Motion editor",
    value: t.motionEditor,
    onChange: v => setTweak('motionEditor', v)
  })));
}
window.OjoLoop = OjoLoop;
window.__OjoLoopPieza = Piece;
})();
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
