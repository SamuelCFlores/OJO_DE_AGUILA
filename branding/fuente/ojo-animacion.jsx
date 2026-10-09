// Ojo de Águila — logo reveal for the three directions.
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
};
V.edgesSorted = V.edges
  .map(e => ({ e, d: Math.hypot((e[0] + e[2]) / 2 - 54, (e[1] + e[3]) / 2 - 54) }))
  .sort((a, b) => a.d - b.d).map(o => o.e);

const C = {
  head: 'M15 96L13 58A30 30 0 0 1 36 14L72 24A32 32 0 0 1 94 56A8 8 0 0 0 86 47L58 46L82 52L66 60L70 96Z',
  eye: [50, 34],
};

const R = {
  eye: [[5,52],[20,36],[38,27],[58,26],[77,35],[95,51],[78,64],[60,72],[40,72],[21,64],[54,49]],
  form: [[-40,50],[0,10],[0,37],[40,20],[85,15],[85,50],[85,85],[40,80],[0,63],[0,90],[40,50]],
  r: [3.6,4.6,5.8,4.6,5.8,4.6,4.6,5.8,4.6,3.6],
  edges: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,0],[2,10],[10,5],[10,9],[10,7]],
};

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

function MarkFuria({ id, lidP = 1, discP = 1, edgeP = 1, pupilP = 1, browP = 1, lookX = 0, squint = 0, scanX = 0, scanOn = 0 }) {
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

function MarkCancha({ id, lineP = 1, circleP = 1, boxP = 1, spotP = 1, headP = 1, beakP = 1, outerP = 0 }) {
  const [ex, ey] = C.eye;
  return (
    <g>
      <defs>
        <clipPath id={id + 'head'}><path d={C.head} /></clipPath>
        <clipPath id={id + 'rev'}><circle cx={ex} cy={ey} r={headP * 120} /></clipPath>
      </defs>
      <g stroke={WHITE} strokeWidth="4" fill="none" opacity={outerP}>
        <line x1="50" y1="-120" x2="50" y2="220" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - lineP} />
        <line x1="72" y1="-120" x2="72" y2="220" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - boxP} />
        <circle cx={ex} cy={ey} r="9.5" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - circleP} transform={`rotate(-90 ${ex} ${ey})`} />
      </g>
      <g clipPath={`url(#${id}rev)`}>
        <g clipPath={`url(#${id}head)`}>
          <rect x="0" y="0" width="100" height="100" fill={WHITE} />
          <rect x="72" y="0" width={40 * beakP} height="100" fill={GOLD} />
          <g stroke={NAVY} strokeWidth="4" fill="none">
            <line x1="50" y1="0" x2="50" y2="100" />
            <line x1="72" y1="0" x2="72" y2="100" />
            <circle cx={ex} cy={ey} r="9.5" />
          </g>
        </g>
      </g>
      <circle cx={ex} cy={ey} r={4.5 * spotP} fill={GOLD} />
    </g>
  );
}

function MarkRed({ morphP = 1, edgeP = 1, nodeP = 1, irisP = 1 }) {
  const m = MOTION.draw(morphP);
  const pos = R.eye.map((e, i) => [lerp(R.form[i][0], e[0], m), lerp(R.form[i][1], e[1], m)]);
  const n = R.edges.length;
  return (
    <g>
      <g stroke={WHITE} strokeLinecap="round" fill="none">
        {R.edges.map(([a, b], i) => {
          const p = clamp(edgeP * (n + 4) / 5 - i / 5, 0, 1);
          const A = pos[a], B = pos[b];
          const L = Math.hypot(B[0] - A[0], B[1] - A[1]);
          return <line key={i} x1={A[0]} y1={A[1]} x2={lerp(A[0], B[0], p)} y2={lerp(A[1], B[1], p)}
            strokeWidth={i < 10 ? lerp(2.4, 3.4, m) : 2.2} opacity={L > 0.1 && p > 0 ? 1 : 0} />;
        })}
      </g>
      {pos.slice(0, 10).map((p, i) => {
        const s = MOTION.pop(clamp(nodeP * 1.6 - i * 0.06, 0, 1));
        return <circle key={i} cx={p[0]} cy={p[1]} r={Math.max(0, lerp(4.2, R.r[i], m) * s)} fill={WHITE} />;
      })}
      {(() => {
        const s = MOTION.pop(clamp(nodeP * 1.6 - 0.6, 0, 1));
        const p = pos[10];
        const ir = lerp(4.2, 15, irisP);
        return (
          <g>
            <circle cx={p[0]} cy={p[1]} r={Math.max(0, ir * s)} fill={irisP > 0.02 ? GOLD : WHITE} />
            <circle cx={p[0]} cy={p[1]} r={Math.max(0, 6 * irisP)} fill={NAVY} />
          </g>
        );
      })()}
    </g>
  );
}

// ---------- shared pieces ----------
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

// ---------- scenes ----------
function SceneVoronoi() {
  const { T, CUES, authoredTotal } = useComposition();
  const endT = CUES.Cancha;
  const t = T - CUES.Voronoi, dur = endT - CUES.Voronoi;
  const move = prog(t, 5.6, 6.5, MOTION.draw);
  const L = lockup(281, 4, 99, 51.5);
  const S = lerp(880, 281, move), cx = lerp(W / 2, L.cx, move);
  const rise = lerp(46, 0, prog(t, 0.2, 1.4, MOTION.draw));
  const lookX = t < 3.6 ? animate({ from: 0, to: -9, start: 3.0, end: 3.35, ease: MOTION.draw })(t)
    : t < 4.3 ? animate({ from: -9, to: 9, start: 3.6, end: 4.05, ease: MOTION.draw })(t)
    : animate({ from: 9, to: 0, start: 4.3, end: 4.6, ease: MOTION.draw })(t);
  const sq = t < 5 ? animate({ from: 0, to: 5, start: 4.6, end: 4.85, ease: MOTION.draw })(t) : animate({ from: 5, to: 0, start: 5.5, end: 5.75, ease: MOTION.draw })(t);
  const scanX = animate({ from: 8, to: 98, start: 4.7, end: 5.5, ease: MOTION.draw })(t);
  const scanOn = prog(t, 4.65, 4.75, x => x) * (1 - prog(t, 5.45, 5.55, x => x));
  const pupil = t < 5 ? lerp(1, 0.75, prog(t, 4.6, 4.9)) : lerp(0.75, 1, prog(t, 5.5, 5.8));
  return (
    <Shot from={CUES.Voronoi} to={CUES.Cancha}>
      <Frame t={t} dur={dur} opacity={sceneFade(t, dur)}
        words={<Wordmark x={L.wx} y={H / 2} F={F} p={prog(t, 6.0, 6.8, MOTION.draw)} accentP={prog(t, 6.7, 7.1)} />}>
        <g transform={`translate(${cx} ${H / 2}) scale(${S / 100}) translate(-51.5 ${-50 + rise})`}>
          <MarkFuria id="af" lidP={prog(t, 0.2, 1.4, MOTION.draw)} discP={MOTION.pop(prog(t, 1.0, 1.6, x => x))}
            edgeP={prog(t, 1.4, 2.4, MOTION.draw)} pupilP={MOTION.pop(prog(t, 2.2, 2.6, x => x)) * pupil}
            browP={MOTION.pop(prog(t, 2.5, 2.85, Easing.easeInQuad))} lookX={lookX} squint={sq} scanX={scanX} scanOn={scanOn} />
        </g>
      </Frame>
    </Shot>
  );
}

function SceneCancha() {
  const { T, CUES } = useComposition();
  const t = T - CUES.Cancha, dur = CUES.Red - CUES.Cancha;
  const move = prog(t, 3.5, 4.4, MOTION.draw);
  const L = lockup(198, 13, 94, 53.5);
  const S = lerp(760, 198, move), cx = lerp(W / 2, L.cx, move);
  return (
    <Shot from={CUES.Cancha} to={CUES.Red}>
      <Frame t={t} dur={dur} opacity={sceneFade(t, dur)}
        words={<Wordmark x={L.wx} y={H / 2} F={F} p={prog(t, 3.9, 4.7, MOTION.draw)} accentP={prog(t, 4.6, 5.0)} />}>
        <g transform={`translate(${cx} ${H / 2}) scale(${S / 100}) translate(-53.5 -55)`}>
          <MarkCancha id="ac" lineP={prog(t, 0.2, 1.1, MOTION.draw)} boxP={prog(t, 0.6, 1.4, MOTION.draw)}
            circleP={prog(t, 0.8, 1.6, MOTION.draw)} spotP={MOTION.pop(prog(t, 1.5, 1.9, x => x))}
            headP={prog(t, 1.9, 2.9, MOTION.draw)} beakP={prog(t, 2.6, 3.2, MOTION.draw)}
            outerP={1 - prog(t, 2.7, 3.3)} />
        </g>
      </Frame>
    </Shot>
  );
}

function SceneRed() {
  const { T, CUES } = useComposition();
  const t = T - CUES.Red, dur = CUES.Cierre - CUES.Red;
  const morph = prog(t, 2.0, 3.2, x => x);
  const move = prog(t, 3.9, 4.8, MOTION.draw);
  const L = lockup(260, 1.4, 98.6, 50);
  const S = lerp(660, 260, move), cx = lerp(W / 2, L.cx, move);
  const mx = lerp(22.5, 50, MOTION.draw(morph)), my = 48;
  return (
    <Shot from={CUES.Red} to={CUES.Cierre}>
      <Frame t={t} dur={dur} opacity={sceneFade(t, dur)}
        words={<Wordmark x={L.wx} y={H / 2} F={F} p={prog(t, 4.3, 5.1, MOTION.draw)} accentP={prog(t, 5.0, 5.4)} />}>
        <Pitch opacity={1 - prog(t, 2.0, 2.8)} />
        <g transform={`translate(${cx} ${H / 2}) scale(${S / 100}) translate(${-mx} ${-my})`}>
          <MarkRed nodeP={prog(t, 0.15, 1.0, x => x)} edgeP={prog(t, 0.8, 2.0, MOTION.draw)}
            morphP={morph} irisP={MOTION.pop(prog(t, 3.0, 3.6, x => x))} />
        </g>
      </Frame>
    </Shot>
  );
}

function SceneCierre() {
  const { T, CUES, authoredTotal } = useComposition();
  const t = T - CUES.Cierre, dur = authoredTotal - CUES.Cierre;
  const items = [
    { n: '1', label: 'Mirada de rapaz', mark: <g transform="translate(-1.5 0)"><MarkFuria id="fv" /></g> },
    { n: '2', label: 'Águila + cancha', mark: <g transform="translate(-3.5 0)"><MarkCancha id="fc" /></g> },
    { n: '3', label: 'Ojo + red de pases', mark: <g transform="translate(0 2)"><MarkRed /></g> },
  ];
  const tagP = prog(t, 1.6, 2.4);
  return (
    <Shot from={CUES.Cierre} to={authoredTotal + 1}>
      <div style={{ position: 'absolute', inset: 0, opacity: sceneFade(t, dur), transform: `scale(${1 + 0.025 * clamp(t / dur, 0, 1)})` }}>
        <Wordmark x={W / 2} y={230} F={64} p={prog(t, 0.1, 0.8, MOTION.draw)} accentP={prog(t, 0.7, 1.1)} align="center" />
        {items.map((it, i) => {
          const p = prog(t, 0.4 + i * 0.18, 1.1 + i * 0.18);
          const s = MOTION.pop(prog(t, 0.4 + i * 0.18, 1.0 + i * 0.18, x => x));
          return (
            <div key={i} style={{ position: 'absolute', left: 560 + i * 400 - 160, top: 360, width: 320, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22, opacity: p, transform: `translateY(${(1 - p) * 30}px)` }}>
              <svg width="300" height="300" viewBox="0 0 100 100" style={{ overflow: 'visible', transform: `scale(${s})` }}>{it.mark}</svg>
              <div style={{ display: 'flex', gap: 14, alignItems: 'baseline', fontFamily: 'Poppins, sans-serif', whiteSpace: 'nowrap' }}>
                <span style={{ fontWeight: 700, fontSize: 28, color: GOLD }}>{it.n}</span>
                <span style={{ fontWeight: 500, fontSize: 30, color: WHITE }}>{it.label}</span>
              </div>
            </div>
          );
        })}
        <div style={{ position: 'absolute', left: 0, right: 0, top: 850, textAlign: 'center', fontFamily: 'Poppins, sans-serif', fontWeight: 500, fontSize: 40, color: WHITE, opacity: tagP, transform: `translateY(${(1 - tagP) * 20}px)` }}>
          La intuición del entrenador, convertida en evidencia.
        </div>
      </div>
    </Shot>
  );
}

function Piece() {
  const { time } = useComposition();
  return (
    <div data-screen-label={`t=${Math.floor(time)}s`} style={{ position: 'absolute', inset: 0, background: NAVY, overflow: 'hidden' }}>
      <SceneVoronoi />
      <SceneCancha />
      <SceneRed />
      <SceneCierre />
    </div>
  );
}

function OjoAnimacion() {
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

window.OjoAnimacion = OjoAnimacion;
