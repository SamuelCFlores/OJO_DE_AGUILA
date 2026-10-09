// Ojo de Águila — 1a "furia" icon loop: look side to side, blink, scan.
const NAVY = '#0B2545', GOLD = '#E8B100', WHITE = '#FFFFFF';
const SIZE = 512;
const MOTION = { enter: Easing.easeOutCubic, move: Easing.easeInOutCubic, snap: Easing.easeInQuad };
const tw = (t, a, b, from, to, ease = MOTION.move) => animate({ from, to, start: a, end: b, ease })(t);

const VESICA = 'M4 52A50.3 50.3 0 0 1 96 52A51.8 51.8 0 0 1 4 52Z';
const EDGES = 'M69.9 32.2L59.8 46M48.2 46L38.1 32.2M79.7 62.3L63.4 57.1M54 81L54 63.9M28.3 62.3L44.6 57.1';
const PUPIL = 'M48.2 46L59.8 46L63.4 57.1L54 63.9L44.6 57.1Z';

function Eye({ lookX, lid, pupil, scanX, scanOn, browDy }) {
  const y = x => 22 + 0.3 * x + lid;
  return (
    <svg width={SIZE} height={SIZE} viewBox="0 0 100 100" style={{ position: 'absolute', inset: 0 }}>
      <defs>
        <clipPath id="lv"><path d={VESICA} /></clipPath>
        <clipPath id="ll"><polygon points={`-50,${y(-50)} 150,${y(150)} 150,150 -50,150`} /></clipPath>
        <clipPath id="li"><circle cx="54" cy="54" r="24" /></clipPath>
      </defs>
      <g transform="translate(50 50) scale(0.68) translate(-52 -49)">
        <polygon points="10,17 86,27 99,46" fill={GOLD} transform={`translate(0 ${browDy})`} />
        <g clipPath="url(#lv)">
          <g clipPath="url(#ll)">
            <path d={VESICA} fill={WHITE} />
            <g transform={`translate(${lookX} 0)`}>
              <circle cx="54" cy="54" r="24" fill={GOLD} />
              <path clipPath="url(#li)" d={EDGES} fill="none" stroke={NAVY} strokeWidth="4.5" strokeLinecap="round" />
              <path d={PUPIL} fill={NAVY} stroke={NAVY} strokeWidth="4" strokeLinejoin="round"
                transform={`translate(54 55) scale(${pupil}) translate(-54 -55)`} />
            </g>
            <line x1={scanX} y1="0" x2={scanX} y2="100" stroke={NAVY} strokeWidth="2.2" opacity={scanOn} />
          </g>
        </g>
      </g>
    </svg>
  );
}

function Piece() {
  const { T, CUES, time } = useComposition();
  const m = CUES.Mirada, p = CUES.Parpadeo, e = CUES.Escaneo, z = CUES.Pausa;
  // look: left, right, centre
  const lookX = T < m + 0.9 ? tw(T, m + 0.25, m + 0.6, 0, -9)
    : T < m + 1.7 ? tw(T, m + 0.95, m + 1.45, -9, 9)
    : tw(T, m + 1.8, m + 2.15, 9, 0);
  // blink + squint
  const blink = T < p + 0.5 ? tw(T, p + 0.05, p + 0.25, 0, 42, MOTION.snap) : tw(T, p + 0.35, p + 0.75, 42, 0, MOTION.enter);
  const squint = T < e + 1 ? tw(T, e + 0.0, e + 0.3, 0, 5) : tw(T, e + 2.0, e + 2.3, 5, 0);
  const lid = Math.max(blink, squint);
  const browDy = blink / 42 * 3 + squint / 5 * 2.5;
  const pupil = T < e + 1 ? tw(T, e + 0.0, e + 0.4, 1, 0.72, MOTION.enter) : tw(T, e + 2.0, e + 2.3, 0.72, 1, MOTION.enter);
  const scanX = T < e + 1.3 ? tw(T, e + 0.4, e + 1.2, 6, 98) : tw(T, e + 1.3, e + 2.0, 98, 6);
  const scanOn = T < e + 1 ? tw(T, e + 0.35, e + 0.45, 0, 1, x => x) : tw(T, e + 1.95, e + 2.1, 1, 0, x => x);
  return (
    <div data-screen-label={`t=${Math.floor(time)}s`} style={{ position: 'absolute', inset: 0, background: NAVY }}>
      <Eye lookX={lookX} lid={lid} pupil={pupil} scanX={scanX} scanOn={scanOn} browDy={browDy} />
    </div>
  );
}

function OjoLoop() {
  const [t, setTweak] = useTweaks(window.TWEAK_DEFAULTS || { motionEditor: true });
  return (
    <>
      <CompositionStage width={SIZE} height={SIZE} scenes={window.OM_SCENES} playback={window.OM_PLAYBACK} bg={NAVY}>
        <Piece />
      </CompositionStage>
      <TweaksPanel>
        <TweakSection label="Video" />
        <TweakToggle label="Motion editor" value={t.motionEditor} onChange={v => setTweak('motionEditor', v)} />
      </TweaksPanel>
    </>
  );
}
window.OjoLoop = OjoLoop;
