// Reading fonts: bundled OFL/Apache faces (fonts/fonts.css) + system fonts referenced by name.
window.ML = window.ML || {};
(function () {
  const SERIF_FB = '"Noto Serif", Georgia, "Times New Roman", serif';
  const SANS_FB = 'system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif';
  const SAMPLE = 'Nguyễn Thị Ẩn ỡ ự ặ';
  const OFL = 'OFL-1.1', APACHE = 'Apache-2.0';
  const f = (id, label, group, license, family) => ({ id, label, family: family || label, group, license, sample: SAMPLE });

  const bundled = [
    f('literata', 'Literata', 'serif', OFL),
    f('merriweather', 'Merriweather', 'serif', OFL),
    f('lora', 'Lora', 'serif', OFL),
    f('noto-serif', 'Noto Serif', 'serif', OFL),
    f('source-serif-4', 'Source Serif 4', 'serif', OFL),
    f('spectral', 'Spectral', 'serif', OFL),
    f('crimson-pro', 'Crimson Pro', 'serif', OFL),
    f('eb-garamond', 'EB Garamond', 'serif', OFL),
    f('alegreya', 'Alegreya', 'serif', OFL),
    f('tinos', 'Tinos', 'serif', OFL),
    f('roboto-slab', 'Roboto Slab', 'serif', APACHE),
    f('inter', 'Inter', 'sans', OFL),
    f('be-vietnam-pro', 'Be Vietnam Pro', 'sans', OFL),
    f('noto-sans', 'Noto Sans', 'sans', OFL),
    f('roboto', 'Roboto', 'sans', OFL),
    f('open-sans', 'Open Sans', 'sans', OFL),
    f('nunito-sans', 'Nunito Sans', 'sans', OFL),
    f('mulish', 'Mulish', 'sans', OFL),
    f('arimo', 'Arimo', 'sans', OFL),
    f('montserrat', 'Montserrat', 'sans', OFL),
  ];
  // [id, family, serif?] — never bundled, shown only when installed
  const system = [
    ['segoe-ui', 'Segoe UI', 0], ['times-new-roman', 'Times New Roman', 1], ['georgia', 'Georgia', 1],
    ['cambria', 'Cambria', 1], ['calibri', 'Calibri', 0], ['tahoma', 'Tahoma', 0], ['arial', 'Arial', 0],
    ['verdana', 'Verdana', 0], ['palatino-linotype', 'Palatino Linotype', 1], ['constantia', 'Constantia', 1],
  ].map(([id, fam, serif]) => Object.assign(f(id, fam, 'system', 'system'), { serif: !!serif }));

  const LOCAL_KEY = 'mythlab.localFonts';
  const loadLocal = () => {
    try { return (ML.store ? ML.store.get(LOCAL_KEY, []) : JSON.parse(localStorage.getItem(LOCAL_KEY) || '[]')) || []; }
    catch { return []; }
  };
  const saveLocal = (arr) => {
    try { ML.store ? ML.store.set(LOCAL_KEY, arr) : localStorage.setItem(LOCAL_KEY, JSON.stringify(arr)); } catch {}
  };
  const kebab = (s) => String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  const toLocal = (fam) => Object.assign(f('local-' + kebab(fam), fam, 'system', 'local'), { local: true });
  let local = loadLocal().filter((s) => typeof s === 'string').map(toLocal);

  const LEGACY = { serif: 'literata', sans: 'inter' };
  const all = () => bundled.concat(system, local);
  const find = (id) => { id = LEGACY[id] || id; return all().find((x) => x.id === id); };
  const q = (fam) => '"' + String(fam).replace(/["\\]/g, '') + '"';

  // document.fonts.check() returns true for unknown families in Chromium, so confirm with a width probe.
  let ctx;
  const PROBE = 'mmmmmmmmmmlliWWẨỡựặ 0123';
  const width = (font) => { ctx.font = font; return ctx.measureText(PROBE).width; };
  function installed(fam) {
    try { if (document.fonts && !document.fonts.check('16px ' + q(fam))) return false; } catch {}
    try {
      ctx = ctx || document.createElement('canvas').getContext('2d');
      if (!ctx) return true;
      if (!['monospace', 'serif', 'sans-serif'].some((b) => width('72px ' + q(fam) + ', ' + b) !== width('72px ' + b))) return false;
      return viOk(fam);
    } catch { return false; }
  }
  // every Vietnamese probe glyph must come from the family itself (same width whatever fallback follows);
  // e.g. Georgia lacks ồ/ẩ/ự and renders detached marks
  const VI = [...'ồẩữặỡựễƯươĐđ'];
  const viOk = (fam) => VI.every((ch) => {
    ctx.font = '40px ' + q(fam) + ', monospace'; const a = ctx.measureText(ch).width;
    ctx.font = '40px ' + q(fam) + ', serif'; return a === ctx.measureText(ch).width;
  });

  let availP;
  ML.fonts = {
    list: bundled.concat(system),
    get local() { return local.slice(); },
    // bundled + installed system fonts + fonts previously picked via queryLocalFonts
    available() {
      if (!availP) availP = (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve())
        .catch(() => {}).then(() => bundled.concat(system.filter((s) => installed(s.family))));
      return availP.then((l) => l.concat(local));
    },
    cssStack(id) {
      const x = find(id) || find('literata');
      const fb = x.group === 'sans' || (x.group === 'system' && !x.serif && !x.local) ? SANS_FB : SERIF_FB;
      return q(x.family) + ', ' + fb;
    },
    find,
    installed,
    canQueryLocal: () => typeof window.queryLocalFonts === 'function',
    // Chromium desktop only; must be called from a user gesture. Returns [{id,label,family,...}] (one per family).
    async queryLocal() {
      if (!ML.fonts.canQueryLocal()) return [];
      const faces = await window.queryLocalFonts();
      const fams = [...new Set(faces.map((x) => x.family))].sort((a, b) => a.localeCompare(b));
      return fams.map(toLocal);
    },
    // remember a family picked from queryLocal() so cssStack/available know it; returns its id
    addLocal(family) {
      const x = toLocal(family);
      if (!local.some((l) => l.id === x.id)) { local.push(x); saveLocal(local.map((l) => l.family)); }
      return x.id;
    },
  };
})();
