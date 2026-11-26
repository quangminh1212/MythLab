// Trims the espeak-ng data bundled in @diffusionstudio/piper-wasm (piper_phonemize.data + the loadPackage metadata
// in piper_phonemize.js) to Vietnamese only, and phonemizes text in Node to prove the trimmed copy gives the very
// same phoneme ids as the original. Pure functions: no file system access, same input -> same output bytes.

const DATA = '/espeak-ng-data/';

/**
 * What a Vietnamese voice needs: the phoneme tables, the intonations, the "vi" dictionary and its voice files.
 * en_dict stays: measured, without it Latin words inside Vietnamese text (iPhone, Facebook, hello) get different phonemes.
 */
export const KEEP = [
  'phondata', 'phondata-manifest', 'phonindex', 'phontab', 'intonations', 'vi_dict', 'en_dict',
  'lang/aav/vi', 'lang/aav/vi-VN-x-central', 'lang/aav/vi-VN-x-south',
].map((f) => DATA + f);

const START = 'loadPackage(';

/** Locates the metadata object literal passed to loadPackage in the emscripten loader. */
function metaRange(js) {
  const at = js.indexOf(START + '{"files"');
  if (at < 0) throw new Error('piper_phonemize.js: loadPackage metadata not found');
  const from = at + START.length;
  const end = js.indexOf('})', from);
  if (end < 0) throw new Error('piper_phonemize.js: loadPackage metadata not closed');
  return { from, to: end + 1 };
}

export const readMeta = (js) => {
  const r = metaRange(js);
  return JSON.parse(js.slice(r.from, r.to));
};

/**
 * Returns the loader script and data file reduced to `keep`. Files are laid out back to back in the order of
 * `keep`, offsets and remote_package_size are rewritten, and the FS_createPath calls of unused folders are removed.
 */
export function trimEspeak(js, data, keep = KEEP) {
  const meta = readMeta(js);
  const byName = new Map(meta.files.map((f) => [f.filename, f]));
  const parts = [];
  const files = [];
  let at = 0;
  for (const name of keep) {
    const f = byName.get(name);
    if (!f) throw new Error(`espeak data has no ${name}`);
    parts.push(data.subarray(f.start, f.end));
    files.push({ filename: name, start: at, end: at + (f.end - f.start) });
    at += f.end - f.start;
  }
  const out = new Uint8Array(at);
  let o = 0;
  for (const p of parts) {
    out.set(p, o);
    o += p.length;
  }
  const dirs = new Set(['/espeak-ng-data']);
  for (const name of keep) {
    const segs = name.split('/').slice(0, -1);
    for (let i = 2; i <= segs.length; i++) dirs.add(segs.slice(0, i).join('/'));
  }
  const r = metaRange(js);
  let head = js.slice(0, r.from);
  head = head.replace(/Module\["FS_createPath"\]\("([^"]*)","([^"]*)",true,true\);/g, (all, parent, name) => {
    const full = (parent === '/' ? '' : parent) + '/' + name;
    return dirs.has(full) ? all : '';
  });
  const tail = js.slice(r.to);
  const next = JSON.stringify({ files, remote_package_size: at });
  return { js: head + next + tail, data: out };
}

/** Minimal browser-worker-like host for the emscripten module (no `process`, so it takes the web code path). */
function loadFactory(js) {
  const m = { exports: {} };
  new Function('module', 'exports', 'process', 'importScripts', 'location', 'self', js)(m, m.exports, undefined, () => {}, { href: 'http://x/a.js', pathname: '/a.js' }, { location: { href: 'http://x/a.js' } });
  return m.exports;
}

/** Phoneme ids of `text` for espeak voice `voice`, exactly as public/tts/piper-worker.js asks for them. */
export async function phonemizeIds(js, wasm, data, text, voice = 'vi') {
  const create = loadFactory(js);
  const ab = data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength);
  let ids = null;
  const mod = await create({
    print: (line) => {
      if (ids) return;
      try {
        ids = JSON.parse(line).phoneme_ids;
      } catch {
        // not a result line
      }
    },
    printErr: () => {},
    wasmBinary: wasm,
    getPreloadedPackage: () => ab,
    locateFile: (f) => f,
  });
  try {
    mod.callMain(['-l', voice, '--input', JSON.stringify([{ text }]), '--espeak_data', '/espeak-ng-data']);
  } catch {
    // callMain may throw ExitStatus
  }
  return ids;
}

/** Vietnamese test sentences: tones, numbers, Latin words, punctuation, a name in English, symbols. */
export const SAMPLES = [
  'Xin chào các bạn, hôm nay trời đẹp quá.',
  'Nguyễn Văn An đã đi từ Hà Nội vào Sài Gòn vào năm 1975 với 2.500 đồng.',
  'Chương 12: Kiếm khách giữa đêm mưa. "Ngươi là ai?" hắn hỏi.',
  'Anh ấy dùng iPhone, Facebook và Wi-Fi của Microsoft; hello world!',
  'Một, hai, ba, bốn, năm, sáu, bảy, tám, chín, mười... 50% và 3,14 km.',
];

/** Throws unless the trimmed data gives the same phoneme ids as the original for every sample. */
export async function verifyTrim(js, wasm, data, trimmed) {
  for (const text of SAMPLES) {
    const a = await phonemizeIds(js, wasm, data, text);
    const b = await phonemizeIds(trimmed.js, wasm, trimmed.data, text);
    if (!a || !a.length) throw new Error(`espeak: the original gave no phonemes for "${text}"`);
    if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`espeak: trimmed data differs from the original for "${text}"`);
  }
}
