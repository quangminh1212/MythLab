/**
 * Reading fonts: bundled OFL/Apache faces (public/fonts/fonts.css) + system fonts referenced by name + local
 * fonts picked through queryLocalFonts(). fonts.css only declares the 72 faces (with unicode-range); the browser
 * downloads a file only when text is rendered in that family, so only the selected reading font is fetched.
 */
import { store } from './store';

export const SERIF_FB = '"Noto Serif", Georgia, "Times New Roman", serif';
export const SANS_FB = 'system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif';
export const FONT_SAMPLE = 'Nguyễn Thị Ẩn ỡ ự ặ';

export interface FontInfo {
  id: string;
  label: string;
  family: string;
  group: 'serif' | 'sans' | 'system';
  license: 'OFL-1.1' | 'Apache-2.0' | 'system' | 'local';
  sample: string;
  serif?: boolean;
  local?: boolean;
}

const f = (id: string, label: string, group: FontInfo['group'], license: FontInfo['license']): FontInfo => ({ id, label, family: label, group, license, sample: FONT_SAMPLE });

const bundled: FontInfo[] = [
  f('literata', 'Literata', 'serif', 'OFL-1.1'),
  f('merriweather', 'Merriweather', 'serif', 'OFL-1.1'),
  f('lora', 'Lora', 'serif', 'OFL-1.1'),
  f('noto-serif', 'Noto Serif', 'serif', 'OFL-1.1'),
  f('source-serif-4', 'Source Serif 4', 'serif', 'OFL-1.1'),
  f('spectral', 'Spectral', 'serif', 'OFL-1.1'),
  f('crimson-pro', 'Crimson Pro', 'serif', 'OFL-1.1'),
  f('eb-garamond', 'EB Garamond', 'serif', 'OFL-1.1'),
  f('alegreya', 'Alegreya', 'serif', 'OFL-1.1'),
  f('tinos', 'Tinos', 'serif', 'OFL-1.1'),
  f('roboto-slab', 'Roboto Slab', 'serif', 'Apache-2.0'),
  f('inter', 'Inter', 'sans', 'OFL-1.1'),
  f('be-vietnam-pro', 'Be Vietnam Pro', 'sans', 'OFL-1.1'),
  f('noto-sans', 'Noto Sans', 'sans', 'OFL-1.1'),
  f('roboto', 'Roboto', 'sans', 'OFL-1.1'),
  f('open-sans', 'Open Sans', 'sans', 'OFL-1.1'),
  f('nunito-sans', 'Nunito Sans', 'sans', 'OFL-1.1'),
  f('mulish', 'Mulish', 'sans', 'OFL-1.1'),
  f('arimo', 'Arimo', 'sans', 'OFL-1.1'),
  f('montserrat', 'Montserrat', 'sans', 'OFL-1.1'),
];

// never bundled, offered only when installed
const system: FontInfo[] = (
  [
    ['segoe-ui', 'Segoe UI', 0],
    ['times-new-roman', 'Times New Roman', 1],
    ['georgia', 'Georgia', 1],
    ['cambria', 'Cambria', 1],
    ['calibri', 'Calibri', 0],
    ['tahoma', 'Tahoma', 0],
    ['arial', 'Arial', 0],
    ['verdana', 'Verdana', 0],
    ['palatino-linotype', 'Palatino Linotype', 1],
    ['constantia', 'Constantia', 1],
  ] as [string, string, number][]
).map(([id, fam, serif]) => ({ ...f(id, fam, 'system', 'system'), serif: !!serif }));

const LOCAL_KEY = 'mythlab.localFonts';
const kebab = (s: string): string =>
  String(s)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
const toLocal = (fam: string): FontInfo => ({ ...f('local-' + kebab(fam), fam, 'system', 'local'), local: true });
const loadLocal = (): FontInfo[] => {
  const v = store.get<unknown>(LOCAL_KEY, []);
  return (Array.isArray(v) ? v : []).filter((s): s is string => typeof s === 'string').map(toLocal);
};
let local = loadLocal();

const LEGACY: Record<string, string> = { serif: 'literata', sans: 'inter' };
const all = (): FontInfo[] => bundled.concat(system, local);
const q = (fam: string): string => '"' + String(fam).replace(/["\\]/g, '') + '"';

/** Looks a font up by id (legacy ids "serif"/"sans" map to literata/inter). */
export function find(id: string): FontInfo | undefined {
  const real = LEGACY[id] || id;
  return all().find((x) => x.id === real);
}

/** CSS font-family value for a font id, with a Vietnamese-capable fallback chain. Unknown ids → Literata. */
export function cssStack(id: string): string {
  const x = find(id) || (bundled[0] as FontInfo);
  const fb = x.group === 'sans' || (x.group === 'system' && !x.serif && !x.local) ? SANS_FB : SERIF_FB;
  return q(x.family) + ', ' + fb;
}

// document.fonts.check() returns true for unknown families in Chromium, so confirm with a width probe.
let ctx: CanvasRenderingContext2D | null | undefined;
const PROBE = 'mmmmmmmmmmlliWWẨỡựặ 0123';
const width = (c: CanvasRenderingContext2D, font: string, text = PROBE): number => {
  c.font = font;
  return c.measureText(text).width;
};
// every Vietnamese probe glyph must come from the family itself (same width whatever fallback follows);
// e.g. Georgia lacks ồ/ẩ/ự and renders detached marks
const VI = [...'ồẩữặỡựễƯươĐđ'];

/** True when a system font family is installed and covers Vietnamese. */
export function installed(fam: string): boolean {
  try {
    if (document.fonts && !document.fonts.check('16px ' + q(fam))) return false;
  } catch {
    /* fall through to the probe */
  }
  try {
    if (ctx === undefined) ctx = document.createElement('canvas').getContext('2d');
    const c = ctx;
    if (!c) return true;
    if (!['monospace', 'serif', 'sans-serif'].some((b) => width(c, `72px ${q(fam)}, ${b}`) !== width(c, `72px ${b}`))) return false;
    return VI.every((ch) => width(c, `40px ${q(fam)}, monospace`, ch) === width(c, `40px ${q(fam)}, serif`, ch));
  } catch {
    return false;
  }
}

let availP: Promise<FontInfo[]> | undefined;
/** Bundled + installed system fonts + fonts previously picked through queryLocal(). */
export function available(): Promise<FontInfo[]> {
  if (!availP) {
    const ready: Promise<unknown> = document.fonts?.ready ?? Promise.resolve();
    availP = ready.catch(() => {}).then(() => bundled.concat(system.filter((s) => installed(s.family))));
  }
  return availP.then((l) => l.concat(local));
}

type LocalFontData = { family: string };
const queryFn = (): (() => Promise<LocalFontData[]>) | null => {
  const fn = (globalThis as { queryLocalFonts?: () => Promise<LocalFontData[]> }).queryLocalFonts;
  return typeof fn === 'function' ? fn.bind(globalThis) : null;
};
export const canQueryLocal = (): boolean => !!queryFn();

/** Chromium desktop only; must be called from a user gesture. One entry per installed family. */
export async function queryLocal(): Promise<FontInfo[]> {
  const fn = queryFn();
  if (!fn) return [];
  const faces = await fn();
  return [...new Set(faces.map((x) => x.family))].sort((a, b) => a.localeCompare(b)).map(toLocal);
}

/** Remembers a family picked from queryLocal() so cssStack/available know it; returns its id. */
export function addLocal(family: string): string {
  const x = toLocal(family);
  if (!local.some((l) => l.id === x.id)) {
    local.push(x);
    store.set(LOCAL_KEY, local.map((l) => l.family));
  }
  return x.id;
}

/**
 * Asks the browser to fetch a bundled font now (regular + bold) so the first paint in it does not swap.
 * Resolves when loaded or after `timeout` ms; never rejects.
 */
export function ensure(id: string, timeout = 3000): Promise<void> {
  const x = find(id);
  if (!x || x.group === 'system' || !document.fonts?.load) return Promise.resolve();
  const fam = q(x.family);
  const load = Promise.all([document.fonts.load(`400 1em ${fam}`, FONT_SAMPLE), document.fonts.load(`700 1em ${fam}`, FONT_SAMPLE)]).then(
    () => {},
    () => {},
  );
  return Promise.race([load, new Promise<void>((r) => setTimeout(r, timeout))]);
}

export const fonts = {
  /** Bundled and system fonts (installed or not). */
  list: bundled.concat(system),
  bundled,
  get local(): FontInfo[] {
    return local.slice();
  },
  available,
  cssStack,
  find,
  installed,
  canQueryLocal,
  queryLocal,
  addLocal,
  ensure,
  /** Test hook: re-reads the stored local fonts. */
  _reload(): void {
    local = loadLocal();
    availP = undefined;
  },
};
