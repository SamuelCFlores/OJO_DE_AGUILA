// Ojo de Águila — "Mirada de rapaz" logo reveal (direction 1, angry Voronoi eye).
const NAVY = '#0B2545', GOLD = '#E8B100', WHITE = '#FFFFFF';
const W = 1920, H = 1080;

const MOTION = {
  enter: Easing.easeOutCubic,
  draw: Easing.easeInOutCubic,
  pop: Easing.easeOutBack,
};
const prog = (t, a, b, ease = MOTION.enter) => animate({ from: 0, to: 1, start: a, end: b, ease })(t);
const lerp = (a, b, p) => a + (b - a) * p;

// ---------- geometry (100-unit mark space) ----------
const V = {
  vesica: 'M4 52A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z',
  seeds: [[54,54],[54,41],[66.4,50],[61.6,64.5],[46.4,64.5],[41.6,50],[61.3,31.7],[72.4,43.8],[77.9,51.9],[70.9,68.1],[61.3,73.1],[44.6,75],[37.7,68.7],[30,53.2],[36.2,42.9],[48.7,31.1]],
  scatter: [[22,48],[-34,8],[118,22],[96,92],[-12,96],[-48,52],[70,-6],[140,58],[150,4],[128,106],[48,112],[6,-10],[-60,86],[-20,30],[30,4],[86,40]],
  edges: [[49.3,47.5,58.7,47.5],[58.7,47.5,61.6,56.5],[61.6,56.5,54,62],[54,62,46.4,56.5],[46.4,56.5,49.3,47.5],[54.9,34.2,63.4,40.8],[63.4,40.8,63.4,41.1],[63.4,41.1,58.7,47.5],[49.3,47.5,45.1,41.7],[45.1,41.7,44.8,39.5],[44.8,39.5,54.9,34.2],[69.2,58.9,61.6,56.5],[63.4,41.1,72.3,49.8],[72.3,49.8,70.9,58.5],[70.9,58.5,69.2,58.9],[54,68.6,54,62],[69.2,58.9,65.2,69],[65.2,69,54,68.6],[38.4,59.1,46.4,56.5],[54,68.6,52.6,70.9],[52.6,70.9,43.4,69.4],[43.4,69.4,38.4,59.1],[38.4,59.1,37.8,59],[37.8,59,35.2,49.3],[35.2,49.3,45.1,41.7],[71.5,33.5,63.4,40.8],[54.9,34.2,55.2,27],[79.4,44.9,72.3,49.8],[79.7,62.3,70.9,58.5],[69.1,76.4,65.2,69],[53.8,81,52.6,70.9],[37.8,75.6,43.4,69.4],[28.7,63.5,37.8,59],[28.5,45.2,35.2,49.3],[38,32.3,44.8,39.5]],
  pupil: '49.3,47.5 58.7,47.5 61.6,56.5 54,62 46.4,56.5',
  // player positions on the pitch, in mark space at the opening frame
  field: [[-25,4],[-12,-28],[-12,36],[8,-36],[8,-10],[8,20],[8,44],[30,-22],[30,30],[72,-26],[72,32],[95,-36],[95,-8],[95,20],[95,44],[120,4]],
};
V.edgesSorted = V.edges
  .map(e => ({ e, d: Math.hypot((e[0] + e[2]) / 2 - 54, (e[1] + e[3]) / 2 - 54) }))
  .sort((a, b) => a.d - b.d).map(o => o.e);



// ---------- marks (dark-background colourway) ----------
function MarkVoronoi({ id, seedP = 1, discP = 1, edgeP = 1, pupilP = 1, openP = 1, browP = 1 }) {
  const off = (1 - browP) * -34;
  const y = x => 26 + 0.18 * x + off;
  const n = V.edgesSorted.length;
  return (
    <g>
      <defs>
        <clipPath id={id + 'brow'}><polygon points={`-500,${y(-500)} 600,${y(600)} 600,600 -500,600`} /></clipPath>
        <clipPath id={id + 'iris'}><circle cx="54" cy="54" r="24" /></clipPath>
      </defs>
      <g clipPath={`url(#${id}brow)`}>
        <path d={V.vesica} fill={WHITE} opacity={openP > 0.02 ? 1 : 0} transform={`translate(0 52) scale(1 ${Math.max(openP, 0.0001)}) translate(0 -52)`} />
        <circle cx="54" cy="54" r={24 * discP} fill={GOLD} />
        <g clipPath={`url(#${id}iris)`} stroke={NAVY} strokeWidth="2.4" strokeLinecap="round" fill="none">
          {V.edgesSorted.map((e, i) => {
            const p = clamp(edgeP * (n + 6) / 7 - i / 7, 0, 1);
            return <line key={i} x1={e[0]} y1={e[1]} x2={e[2]} y2={e[3]} pathLength="1" strokeDasharray="1" strokeDashoffset={1 - p} />;
          })}
        </g>
        <polygon points={V.pupil} fill={NAVY} stroke={NAVY} strokeWidth="2.4" strokeLinejoin="round"
          transform={`translate(54 54.6) scale(${pupilP}) translate(-54 -54.6)`} />
      </g>
      {seedP < 1.01 && V.seeds.map((s, i) => {
        const a = V.scatter[i];
        const p = clamp(seedP * 1.3 - i * 0.02, 0, 1);
        const ep = MOTION.draw(p);
        return <circle key={i} cx={lerp(a[0], s[0], ep)} cy={lerp(a[1], s[1], ep)} r="1.5"
          fill={i === 0 ? GOLD : WHITE} opacity={1 - edgeP} />;
      })}
    </g>
  );
}

function Players({ seedP, linkP, fade, tx, ty }) {
  if (fade <= 0) return null;
  return (
    <g opacity={fade}>
      {V.field.map((a, i) => {
        const p = MOTION.draw(clamp(seedP * 1.25 - i * 0.015, 0, 1));
        const s = V.seeds[i];
        const x = lerp(a[0], s[0], p), y = lerp(a[1], s[1], p);
        const lp = clamp(linkP * 1.3 - i * 0.02, 0, 1);
        return (
          <g key={i}>
            <line x1={x} y1={y} x2={lerp(x, tx, lp)} y2={lerp(y, ty, lp)} stroke={WHITE} strokeWidth="0.35" opacity={(1 - p) * 0.7} />
            <circle cx={x} cy={y} r={lerp(2.2, 1.4, p)} fill={i === 0 ? GOLD : WHITE} />
          </g>
        );
      })}
    </g>
  );
}

function MarkFuria({ id, lidP = 1, discP = 1, edgeP = 1, pupilP = 1, browP = 1, lookX = 0, squint = 0, scanX = 0, scanOn = 0, campo = false, seedP = 1 }) {
  if (campo) return <MarkCampo {...{ id, lidP, discP, edgeP, pupilP, browP, lookX, squint, scanX, scanOn, seedP }} />;
  const off = (1 - lidP) * 70 + squint;
  const y = x => 22 + 0.3 * x + off;
  const n = V.edgesSorted.length;
  const bd = (1 - browP) * -60 + squint * 0.6;
  return (
    <g>
      <defs>
        <clipPath id={id + 'lid'}><polygon points={`-500,${y(-500)} 600,${y(600)} 600,600 -500,600`} /></clipPath>
        <clipPath id={id + 'ves'}><path d={V.vesica} /></clipPath>
        <clipPath id={id + 'iris'}><circle cx="54" cy="54" r="24" /></clipPath>
      </defs>
      <polygon points="12,19.6 86,30.8 99,46.7" fill={GOLD} opacity={browP > 0.01 ? 1 : 0} transform={`translate(0 ${bd})`} />
      <g clipPath={`url(#${id}lid)`}><g clipPath={`url(#${id}ves)`}>
        <path d={V.vesica} fill={WHITE} />
        <circle cx={54 + lookX} cy="54" r={24 * discP} fill={GOLD} />
        <g clipPath={`url(#${id}iris)`} transform={`translate(${lookX} 0)`} stroke={NAVY} strokeWidth="2.4" strokeLinecap="round" fill="none">
          {V.edgesSorted.map((e, i) => {
            const p = clamp(edgeP * (n + 6) / 7 - i / 7, 0, 1);
            return <line key={i} x1={e[0]} y1={e[1]} x2={e[2]} y2={e[3]} pathLength="1" strokeDasharray="1" strokeDashoffset={1 - p} />;
          })}
        </g>
        <polygon points={V.pupil} fill={NAVY} stroke={NAVY} strokeWidth="2.4" strokeLinejoin="round"
          transform={`translate(${lookX} 0) translate(54 54.6) scale(${pupilP}) translate(-54 -54.6)`} />
        <line x1={scanX} y1="0" x2={scanX} y2="100" stroke={WHITE} strokeWidth="2.4" opacity={scanOn} />
      </g></g>
    </g>
  );
}

// Original "campo" build: iris assembles from players first, then the eye opens bottom-up.
function MarkCampo({ id, lidP, discP, edgeP, pupilP, browP, lookX, squint, scanX, scanOn, seedP }) {
  const yL = x => 22 + 0.3 * x + (1 - lidP) * 70 + squint;
  const yS = x => 22 + 0.3 * x + squint - (1 - lidP) * 30;
  const n = V.edgesSorted.length;
  const bd = (1 - browP) * -60 + squint * 0.6;
  const open = lidP > 0.999;
  return (
    <g>
      <defs>
        <clipPath id={id + 'lid'}><polygon points={`-500,${yL(-500)} 600,${yL(600)} 600,600 -500,600`} /></clipPath>
        <clipPath id={id + 'top'}><polygon points={`-500,${yS(-500)} 600,${yS(600)} 600,600 -500,600`} /></clipPath>
        <clipPath id={id + 'ves'}><path d={V.vesica} /></clipPath>
        <clipPath id={id + 'iris'}><circle cx="54" cy="54" r="24" /></clipPath>
      </defs>
      <polygon points="12,19.6 86,30.8 99,46.7" fill={GOLD} opacity={browP > 0.01 ? 1 : 0} transform={`translate(0 ${bd})`} />
      <g clipPath={`url(#${id}lid)`}><path d={V.vesica} fill={WHITE} clipPath={`url(#${id}top)`} /></g>
      <g clipPath={`url(#${id}top)`}><g clipPath={open ? `url(#${id}ves)` : undefined}>
        <circle cx={54 + lookX} cy="54" r={24 * discP} fill={GOLD} />
        <g clipPath={`url(#${id}iris)`} transform={`translate(${lookX} 0)`} stroke={NAVY} strokeWidth="2.4" strokeLinecap="round" fill="none">
          {V.edgesSorted.map((e, i) => {
            const p = clamp(edgeP * (n + 6) / 7 - i / 7, 0, 1);
            return <line key={i} x1={e[0]} y1={e[1]} x2={e[2]} y2={e[3]} pathLength="1" strokeDasharray="1" strokeDashoffset={1 - p} />;
          })}
        </g>
        <polygon points={V.pupil} fill={NAVY} stroke={NAVY} strokeWidth="2.4" strokeLinejoin="round"
          transform={`translate(${lookX} 0) translate(54 54.6) scale(${pupilP}) translate(-54 -54.6)`} />
        <line x1={scanX} y1="0" x2={scanX} y2="100" stroke={WHITE} strokeWidth="2.4" opacity={scanOn} />
      </g></g>
      {edgeP < 1 && V.seeds.map((p0, i) => {
        const a = V.scatter[i];
        const ep = MOTION.draw(clamp(seedP * 1.3 - i * 0.02, 0, 1));
        return <circle key={i} cx={lerp(a[0], p0[0], ep)} cy={lerp(a[1], p0[1], ep)} r="1.5" fill={i === 0 ? GOLD : WHITE} opacity={1 - edgeP} />;
      })}
    </g>
  );
}

function Pitch({ opacity }) {
  if (opacity <= 0.001) return null;
  const x0 = 210, y0 = 115, w = 1500, h = 850;
  return (
    <g stroke={WHITE} strokeWidth="3" fill="none" opacity={opacity * 0.14}>
      <rect x={x0} y={y0} width={w} height={h} />
      <line x1={x0 + w / 2} y1={y0} x2={x0 + w / 2} y2={y0 + h} />
      <circle cx={x0 + w / 2} cy={y0 + h / 2} r="120" />
      <rect x={x0} y={y0 + h / 2 - 200} width="240" height="400" />
      <rect x={x0 + w - 240} y={y0 + h / 2 - 200} width="240" height="400" />
    </g>
  );
}

// ---------- shared pieces ----------

function Wordmark({ x, y, F, p, accentP, align = 'left' }) {
  const a = MOTION.pop(accentP);
  return (
    <div style={{
      position: 'absolute', left: x, top: y - F * 0.5 - F * 0.2, paddingTop: F * 0.2,
      fontFamily: 'Poppins, sans-serif', fontWeight: 700, fontSize: F, lineHeight: 1,
      letterSpacing: '0.02em', color: WHITE, whiteSpace: 'nowrap',
      transform: `translateX(${align === 'center' ? '-50%' : '0'}) translateX(${(1 - p) * -40}px)`,
      clipPath: `inset(0 ${100 - 100 * p}% 0 0)`,
    }}>
      OJO DE <span style={{ position: 'relative', display: 'inline-block' }}>A<span style={{
        position: 'absolute', left: '0.3em', top: '-0.14em', width: '0.24em', height: '0.17em', background: GOLD,
        clipPath: 'polygon(52% 0,100% 0,40% 100%,0 100%)',
        transform: `translateY(${(1 - a) * -0.5}em) scale(${Math.max(a, 0)})`, opacity: accentP > 0 ? 1 : 0,
      }} /></span>GUILA
    </div>
  );
}

const WORD_W = 7.62; // wordmark width in em
const F = 104, GAP = 0.42 * F;
function lockup(Sf, minX, maxX, mcx) {
  const vw = (maxX - minX) * Sf / 100;
  const left = W / 2 - (vw + GAP + WORD_W * F) / 2;
  return { cx: left + (mcx - minX) * Sf / 100, wx: left + vw + GAP };
}

function sceneFade(t, dur) {
  return prog(t, 0, 0.35) * (1 - prog(t, dur - 0.45, dur, MOTION.draw));
}

function Frame({ t, dur, opacity, children, words }) {
  const z = 1 + 0.03 * clamp(t / dur, 0, 1);
  return (
    <div style={{ position: 'absolute', inset: 0, opacity, transform: `scale(${z})`, transformOrigin: '50% 50%' }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>{children}</svg>
      {words}
    </div>
  );
}

const HAS_CANCHA = () => String(window.OM_SCENES || '').includes('"Cancha"');

// ---------- pitch intro (only when a "Cancha" cue exists) ----------
function PitchIntro() {
  const { T, CUES } = useComposition();
  if (!HAS_CANCHA()) return null;
  const t = T - CUES.Cancha, m = T - CUES.Mirada;
  const x0 = 210, y0 = 115, w = 1500, h = 850, cx = W / 2, cy = H / 2;
  const d = (a, b) => 1 - prog(t, a, b, MOTION.draw);
  const fade = 1 - prog(m, 0.9, 1.7, MOTION.draw);
  const grow = prog(m, 0.1, 1.0, MOTION.draw);
  const riseM = lerp(46, 0, prog(m, 0.2, 1.4, MOTION.draw));
  const ccx = lerp(cx, cx + 22, grow), ccy = lerp(cy, cy + (4 + riseM) * 8.8, grow), cr = lerp(120, 211, grow);
  const z = 1 + 0.03 * clamp(m / 9, 0, 1);
  const L = (x1, y1, x2, y2, a, b, k) => <line key={k} x1={x1} y1={y1} x2={x2} y2={y2} pathLength="1" strokeDasharray="1" strokeDashoffset={d(a, b)} />;
  return (
    <Shot from={CUES.Cancha} to={CUES.Mirada + 2}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: 'absolute', inset: 0, opacity: prog(t, 0, 0.2) * fade, transform: `scale(${m > 0 ? z : 1})` }}>
        <g stroke={WHITE} strokeWidth="4" fill="none" strokeLinecap="round">
          {L(cx, y0 + h, cx, y0, 0.1, 0.9, 'mid')}
          {L(x0, y0 + h, x0 + w, y0 + h, 0.1, 0.7, 'b')}
          {L(x0, y0 + h, x0, y0, 0.4, 1.1, 'l')}
          {L(x0 + w, y0 + h, x0 + w, y0, 0.4, 1.1, 'r')}
          {L(x0, y0, x0 + w, y0, 0.9, 1.5, 't')}
          {L(x0, y0 + h / 2 + 200, x0 + 240, y0 + h / 2 + 200, 1.0, 1.3, 'b1')}
          {L(x0 + 240, y0 + h / 2 + 200, x0 + 240, y0 + h / 2 - 200, 1.1, 1.5, 'b2')}
          {L(x0 + 240, y0 + h / 2 - 200, x0, y0 + h / 2 - 200, 1.3, 1.6, 'b3')}
          {L(x0 + w, y0 + h / 2 + 200, x0 + w - 240, y0 + h / 2 + 200, 1.0, 1.3, 'c1')}
          {L(x0 + w - 240, y0 + h / 2 + 200, x0 + w - 240, y0 + h / 2 - 200, 1.1, 1.5, 'c2')}
          {L(x0 + w - 240, y0 + h / 2 - 200, x0 + w, y0 + h / 2 - 200, 1.3, 1.6, 'c3')}
          <circle cx={ccx} cy={ccy} r={cr} pathLength="1" strokeDasharray="1" strokeDashoffset={d(1.2, 2.1)} transform={`rotate(90 ${ccx} ${ccy})`} strokeWidth={lerp(4, 6, grow)} />
        </g>
        {m <= 0 && V.field.map((a, i) => {
          const k = MOTION.pop(prog(t, 1.4 + i * 0.04, 1.75 + i * 0.04, x => x));
          return <circle key={i} cx={cx + (a[0] - 51.5) * 8.8} cy={cy + (a[1] - 4) * 8.8} r={Math.max(0, 2.2 * 8.8 * k)} fill={i === 0 ? GOLD : WHITE} />;
        })}
        <circle cx={ccx} cy={ccy} r={10 * MOTION.pop(prog(t, 1.9, 2.3, x => x)) * (1 - grow)} fill={GOLD} />
      </svg>
    </Shot>
  );
}

// ---------- scenes ----------
function SceneVoronoi() {
  const { T, CUES, authoredTotal } = useComposition();
  const campo = window.OM_INTRO === 'campo';
  const t = T - CUES.Mirada, dur = authoredTotal - CUES.Mirada;
  const fadeIn = !HAS_CANCHA();
  const o = campo ? 0.9 : 0;
  const move = prog(t, 5.6 + o, 6.5 + o, MOTION.draw);
  const L = lockup(281, 4, 99, 51.5);
  const S = lerp(880, 281, move), cx = lerp(W / 2, L.cx, move);
  const rise = campo ? 0 : lerp(46, 0, prog(t, 0.2, 1.4, MOTION.draw));
  const lookX = t < 3.6 + o ? animate({ from: 0, to: -9, start: 3.0 + o, end: 3.35 + o, ease: MOTION.draw })(t)
    : t < 4.3 + o ? animate({ from: -9, to: 9, start: 3.6 + o, end: 4.05 + o, ease: MOTION.draw })(t)
    : animate({ from: 9, to: 0, start: 4.3 + o, end: 4.6 + o, ease: MOTION.draw })(t);
  const sq = t < 5 + o ? animate({ from: 0, to: 5, start: 4.6 + o, end: 4.85 + o, ease: MOTION.draw })(t) : animate({ from: 5, to: 0, start: 5.5 + o, end: 5.75 + o, ease: MOTION.draw })(t);
  const scanX = animate({ from: 8, to: 98, start: 4.7 + o, end: 5.5 + o, ease: MOTION.draw })(t);
  const scanOn = prog(t, 4.65 + o, 4.75 + o, x => x) * (1 - prog(t, 5.45 + o, 5.55 + o, x => x));
  const pupil = t < 5 + o ? lerp(1, 0.75, prog(t, 4.6 + o, 4.9 + o)) : lerp(0.75, 1, prog(t, 5.5 + o, 5.8 + o));
  const k = campo
    ? { seedP: prog(t, 0.2, 1.5, MOTION.draw), discP: MOTION.pop(prog(t, 1.2, 1.9, x => x)), edgeP: prog(t, 1.6, 2.7, MOTION.draw),
        pupilP: MOTION.pop(prog(t, 2.5, 2.9, x => x)) * pupil, lidP: prog(t, 2.8, 3.5, MOTION.draw), browP: MOTION.pop(prog(t, 3.4, 3.75, Easing.easeInQuad)) }
    : { lidP: prog(t, 0.2, 1.4, MOTION.draw), discP: MOTION.pop(prog(t, 1.0, 1.6, x => x)), edgeP: prog(t, 1.4, 2.4, MOTION.draw),
        pupilP: MOTION.pop(prog(t, 2.2, 2.6, x => x)) * pupil, browP: MOTION.pop(prog(t, 2.5, 2.85, Easing.easeInQuad)) };
  return (
    <Shot from={CUES.Mirada} to={authoredTotal + 1}>
      <Frame t={t} dur={dur} opacity={fadeIn ? sceneFade(t, dur) : 1 - prog(t, dur - 0.45, dur, MOTION.draw)}
        words={<Wordmark x={L.wx} y={H / 2} F={F} p={prog(t, 6.0 + o, 6.8 + o, MOTION.draw)} accentP={prog(t, 6.7 + o, 7.1 + o)} />}>
        {campo && <Pitch opacity={1 - prog(t, 1.0, 1.8)} />}
        <g transform={`translate(${cx} ${H / 2}) scale(${S / 100}) translate(-51.5 ${-50 + rise})`}>
          {!fadeIn && <Players seedP={prog(t, 0.45, 1.5, x => x)} linkP={prog(t, 0.0, 0.5, MOTION.draw)} fade={1 - prog(t, 1.5, 2.2)}
            tx={lerp(51.5, 54, prog(t, 0.1, 1.0, MOTION.draw))} ty={lerp(0, 4 + rise, prog(t, 0.1, 1.0, MOTION.draw)) + 50 - rise} />}
          <MarkFuria id="af" campo={campo} {...k} lookX={lookX} squint={sq} scanX={scanX} scanOn={scanOn} />
        </g>
      </Frame>
    </Shot>
  );
}

function Piece() {
  const { time } = useComposition();
  return (
    <div data-screen-label={`t=${Math.floor(time)}s`} style={{ position: 'absolute', inset: 0, background: NAVY, overflow: 'hidden' }}>
      <PitchIntro />
      <SceneVoronoi />
    </div>
  );
}

function MiradaRapaz() {
  const [tw, setTweak] = useTweaks(window.TWEAK_DEFAULTS || { motionEditor: true });
  return (
    <>
      <CompositionStage width={1920} height={1080} scenes={window.OM_SCENES} playback={window.OM_PLAYBACK} bg={NAVY}>
        <Piece />
      </CompositionStage>
      <TweaksPanel>
        <TweakSection label="Video" />
        <TweakToggle label="Motion editor" value={tw.motionEditor} onChange={v => setTweak('motionEditor', v)} />
      </TweaksPanel>
    </>
  );
}
window.MiradaRapaz = MiradaRapaz;
