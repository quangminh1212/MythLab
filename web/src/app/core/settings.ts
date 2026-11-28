/**
 * Reader settings: stored in localStorage `mythlab.settings` (same keys and defaults as the old app, plus the
 * migration markers `ui2`/`ui3`), validated on load, applied to <html> as data attributes and CSS variables.
 * Unknown stored keys are preserved so other versions of the app do not lose their data.
 */
import { emit } from './events';
import { cssStack, ensure } from './fonts';
import { store } from './store';

import { ACCENT_IDS, isDarkScheme, THEME_IDS, type Scheme, type Theme } from './themes';
export type { Scheme, Theme };
export type TtsEngine = 'native' | 'piper';

/** True when the on-device Piper engine can run here (WebAssembly + Web Worker + Cache API). */
export const piperSupported = (): boolean => typeof WebAssembly === 'object' && typeof Worker === 'function' && typeof caches === 'object';

export interface Settings {
  theme: Theme;
  /** Accent colour id (themes.ts ACCENTS). */
  accent: string;
  font: string;
  weight: number;
  size: number;
  line: number;
  letter: number;
  word: number;
  align: 'left' | 'justify';
  indent: number;
  paraGap: number;
  margin: number;
  width: number;
  dayPreset: string;
  nightPreset: string;
  readMode: 'scroll' | 'page';
  tapZones: boolean;
  brightness: number;
  /** Follow the device's own screen brightness: the in-page dim layer is off and the slider is disabled. */
  brightnessAuto: boolean;
  /** Extra vertical padding of the reading page (px), on top of the standard one. */
  padY: number;
  /** "auto" theme follows the clock (nightFrom..nightTo is dark) instead of the system. */
  nightSchedule: boolean;
  /** "HH:MM" 24 h. */
  nightFrom: string;
  nightTo: string;
  /** Colours of the "Tuỳ chỉnh" reading preset (#rrggbb). */
  customBg: string;
  customFg: string;
  engine: TtsEngine;
  nativeVoice: string;
  /** Piper voice id (player/piper.ts catalog). */
  piperVoice: string;
  rate: number;
  pitch: number;
  autoNext: boolean;
  follow: boolean;
  /** Starting to listen elsewhere opens the reader at the chapter being read. */
  autoOpenReader: boolean;
  readTitle: boolean;
  ttsClean: boolean;
  ttsChapterCue: boolean;
  keepAwake: boolean;
  /** Single-key reader shortcuts (M, B, A, Space, ...); off satisfies WCAG 2.1.4. */
  shortcuts: boolean;
}
export type SettingKey = keyof Settings;

const KEY = 'mythlab.settings';

export const isNative = (): boolean => {
  const c = (globalThis as { Capacitor?: { isNativePlatform?: () => boolean } }).Capacitor;
  return !!c && typeof c.isNativePlatform === 'function' && c.isNativePlatform();
};

/** The default Piper voice (VAIS-1000, 63 MB); the old default id is kept for the migration below. */
const DEFAULT_VOICE = 'vi_VN-vais1000-medium#0';

export function defaults(): Settings {
  return {
    theme: 'light',
    accent: 'default',
    font: 'literata',
    weight: 400,
    size: 20,
    line: 1.8,
    letter: 0,
    word: 0,
    align: 'justify',
    indent: 0,
    paraGap: 1,
    margin: 0,
    width: 720,
    dayPreset: 'default',
    nightPreset: 'default',
    readMode: 'scroll',
    tapZones: true,
    brightness: 1,
    brightnessAuto: true,
    padY: 0,
    nightSchedule: false,
    nightFrom: '19:00',
    nightTo: '06:00',
    customBg: '#f4ecd8',
    customFg: '#2b2118',
    // Piper (on the device) is the reader of the web; the Android app starts with the phone's own voice
    engine: isNative() ? 'native' : 'piper',
    nativeVoice: '',
    // 63 MB, best quality: downloaded by itself in the background after the first load
    piperVoice: DEFAULT_VOICE,
    rate: 1,
    pitch: 1,
    autoNext: true,
    follow: true,
    autoOpenReader: true,
    readTitle: true,
    ttsClean: true,
    ttsChapterCue: true,
    keepAwake: true,
    shortcuts: true,
  };
}
export const DEF: Readonly<Settings> = Object.freeze(defaults());

export const RANGE = {
  weight: [300, 700],
  size: [14, 34],
  line: [1.3, 2.6],
  letter: [-0.5, 2],
  word: [0, 8],
  indent: [0, 2],
  paraGap: [0, 2],
  margin: [0, 64],
  padY: [0, 64],
  width: [480, 1100],
  brightness: [0.3, 1],
  rate: [0.5, 3],
  pitch: [0.5, 2],
} as const satisfies Partial<Record<SettingKey, readonly [number, number]>>;

const ENUM = {
  theme: THEME_IDS as readonly string[],
  accent: ACCENT_IDS as readonly string[],
  align: ['left', 'justify'],
  readMode: ['scroll', 'page'],
  engine: ['native', 'piper'],
} as const satisfies Partial<Record<SettingKey, readonly string[]>>;

export interface Preset {
  id: string;
  label: string;
  /** Reading background / text / accent; null for "default" (the theme's own colours). */
  bg: string | null;
  fg: string | null;
  accent: string | null;
}
const P = (id: string, label: string, bg: string | null = null, fg: string | null = null, accent: string | null = null): Preset => ({ id, label, bg, fg, accent });

/**
 * Reading colour presets. Day presets apply in the light and sepia schemes, night presets in the dark scheme.
 * Every preset's text and accent are >= 4.5:1 on its background (asserted in contrast.test.ts); the day accents
 * are darker than the old ones for that reason.
 */
export const presets: { day: Preset[]; night: Preset[] } = {
  day: [
    P('default', 'Mặc định'),
    P('trang', 'Trắng', '#ffffff', '#1f2328', '#0f766e'),
    P('giay', 'Giấy', '#f4ecd8', '#3b2f22', '#0b5f58'),
    P('xam', 'Xám', '#e9e9e9', '#222222', '#0b5f58'),
    P('xanh', 'Xanh dịu', '#dfeedd', '#22311f', '#1b5e20'),
    P('hong', 'Hồng nhạt', '#f6e7e7', '#3a2626', '#9b2c40'),
  ],
  night: [
    P('default', 'Mặc định'),
    P('den', 'Đen', '#000000', '#c8c8c8', '#2dd4bf'),
    P('than', 'Than', '#1f2937', '#e5e7eb', '#5eead4'),
    P('nau', 'Nâu tối', '#2b2118', '#e6d6bd', '#e0a96d'),
    P('xanhdem', 'Xanh đêm', '#0f1b2a', '#cfdcec', '#7cc4ff'),
  ],
};

/** Id of the user-defined reading preset (offered in both the day and the night list by the settings UI). */
export const CUSTOM_PRESET_ID = 'custom';
export const CUSTOM_PRESET_LABEL = 'Tuỳ chỉnh';

const TIME_RE = /^([01]\d|2[0-3]):([0-5]\d)$/;
const HEX_RE = /^#[0-9a-f]{6}$/i;

/** Minutes after midnight for "HH:MM", or null when malformed. */
export function parseTime(t: string): number | null {
  const m = TIME_RE.exec(t);
  return m ? Number(m[1]) * 60 + Number(m[2]) : null;
}

/**
 * True when `minutes` (after midnight) falls in the night window [from, to). The window may wrap midnight
 * (19:00 to 06:00). Equal bounds mean an empty window; malformed bounds are never night.
 */
export function inNightWindow(minutes: number, from: string, to: string): boolean {
  const a = parseTime(from);
  const b = parseTime(to);
  if (a === null || b === null || a === b) return false;
  return a < b ? minutes >= a && minutes < b : minutes >= a || minutes < b;
}

const nowMinutes = (d = new Date()): number => d.getHours() * 60 + d.getMinutes();

const clamp = (v: unknown, [lo, hi]: readonly [number, number], d: number): number => {
  const n = typeof v === 'number' ? v : typeof v === 'string' && v.trim() !== '' ? Number(v) : NaN;
  return Number.isFinite(n) ? Math.min(hi, Math.max(lo, n)) : d;
};

/** Returns a valid value for `key` (clamped / defaulted). */
export function normalise<K extends SettingKey>(key: K, v: unknown): Settings[K] {
  const d = DEF[key];
  if (key in RANGE) return clamp(v, RANGE[key as keyof typeof RANGE], d as number) as Settings[K];
  if (key in ENUM) return ((ENUM[key as keyof typeof ENUM] as readonly string[]).includes(v as string) ? v : d) as Settings[K];
  if (key === 'dayPreset') return (v === CUSTOM_PRESET_ID || presets.day.some((p) => p.id === v) ? v : d) as Settings[K];
  if (key === 'nightPreset') return (v === CUSTOM_PRESET_ID || presets.night.some((p) => p.id === v) ? v : d) as Settings[K];
  if (key === 'nightFrom' || key === 'nightTo') return (typeof v === 'string' && TIME_RE.test(v) ? v : d) as Settings[K];
  if (key === 'customBg' || key === 'customFg') return (typeof v === 'string' && HEX_RE.test(v) ? v.toLowerCase() : d) as Settings[K];
  if (typeof d === 'boolean') return (typeof v === 'boolean' ? v : d) as Settings[K];
  return (typeof v === 'string' ? v : d) as Settings[K];
}

/** The live settings object. Read freely; write through `set()`. */
export const S: Settings = defaults();
let extra: Record<string, unknown> = {};

const isObj = (v: unknown): v is Record<string, unknown> => !!v && typeof v === 'object' && !Array.isArray(v);

/** Loads and migrates the stored settings into `S`. Returns true when something had to be rewritten. */
export function load(): boolean {
  const raw = store.get<unknown>(KEY, null);
  const st = isObj(raw) ? raw : {};
  const next: Record<string, unknown> = { ...st };
  // ui2 (old migration, kept): a stored "sepia" theme from before the day presets becomes light
  if (!next.ui2) {
    if (next.theme === 'sepia') next.theme = 'light';
    next.ui2 = 1;
  }
  if (next.font === 'serif') next.font = 'literata';
  if (next.font === 'sans') next.font = 'inter';
  // The browser's speechSynthesis reader is gone (most devices have no Vietnamese voice in it), the server (Edge)
  // voices are gone too: those choices, and the Android voice on a host without the app, become Piper (on the device).
  if (next.engine === 'browser' || next.engine === 'edge' || (next.engine === 'native' && !isNative())) next.engine = isNative() ? 'native' : 'piper';
  delete next.browserVoice;
  // the Vivos voices were removed: a saved Vivos choice goes back to the default voice
  if (typeof next.piperVoice === 'string' && next.piperVoice.startsWith('vi_VN-vivos')) delete next.piperVoice;
  // the stored server voice id and device voice ids that are server voices (Edge "...Neural", server Piper "...Piper") are dropped
  delete next.voice;
  if (typeof next.nativeVoice === 'string' && /(Neural|Piper)$/.test(next.nativeVoice)) next.nativeVoice = '';
  // a stored Piper choice in the Android app on a WebView that cannot run it goes back to the phone's own voice
  if (next.engine === 'piper' && !piperSupported() && isNative()) next.engine = 'native';
  // ui3: justified text makes rivers on phones, so a phone that never chose an alignment starts left-aligned
  if (!next.ui3) {
    const narrow = typeof matchMedia === 'function' && matchMedia('(max-width: 599px)').matches;
    if (narrow && (next.align === undefined || next.align === 'justify')) next.align = 'left';
    next.ui3 = 1;
  }
  const def = defaults();
  extra = {};
  for (const k of Object.keys(next)) if (!(k in def)) extra[k] = next[k];
  for (const k of Object.keys(def) as SettingKey[]) (S as unknown as Record<string, unknown>)[k] = normalise(k, k in next ? next[k] : def[k]);
  const changed = JSON.stringify(sorted({ ...extra, ...S })) !== JSON.stringify(sorted(st));
  if (changed) save();
  return changed;
}

function sorted(o: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const k of Object.keys(o).sort()) out[k] = o[k];
  return out;
}

export function save(): boolean {
  return store.set(KEY, { ...extra, ...S });
}

const mqDark = (): MediaQueryList | null => (typeof matchMedia === 'function' ? matchMedia('(prefers-color-scheme: dark)') : null);

/** The scheme actually shown: "auto" follows the system. */
export function scheme(): Scheme {
  if (S.theme === 'auto') {
    if (S.nightSchedule) return inNightWindow(nowMinutes(), S.nightFrom, S.nightTo) ? 'dark' : 'light';
    return mqDark()?.matches ? 'dark' : 'light';
  }
  return S.theme;
}
export const isDark = (): boolean => isDarkScheme(scheme());

/** The active reading preset (never null; the default preset has null colours). */
export function activePreset(): Preset {
  const list = isDark() ? presets.night : presets.day;
  const id = isDark() ? S.nightPreset : S.dayPreset;
  if (id === CUSTOM_PRESET_ID) return { id, label: CUSTOM_PRESET_LABEL, bg: S.customBg, fg: S.customFg, accent: null };
  return list.find((p) => p.id === id) || (list[0] as Preset);
}

export const fontStack = (): string => cssStack(S.font);

/** Applies the settings to the document: data attributes, CSS variables, theme-color, brightness layer. */
export function apply(): void {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  const sc = scheme();
  lastScheme = sc;
  root.dataset.theme = S.theme;
  root.dataset.scheme = sc;
  root.dataset.mode = isDarkScheme(sc) ? 'dark' : 'light';
  root.dataset.accent = S.accent;
  root.dataset.readmode = S.readMode;
  root.dataset.tapzones = S.tapZones ? 'on' : 'off';
  root.style.colorScheme = isDarkScheme(sc) ? 'dark' : 'light';
  const st = root.style;
  st.setProperty('--read-size', S.size + 'px');
  st.setProperty('--read-line', String(S.line));
  st.setProperty('--read-width', S.width + 'px');
  st.setProperty('--font-read', fontStack());
  st.setProperty('--read-weight', String(S.weight));
  st.setProperty('--read-letter', S.letter + 'px');
  st.setProperty('--read-word', S.word + 'px');
  st.setProperty('--read-align', S.align);
  st.setProperty('--read-indent', S.indent + 'em');
  st.setProperty('--read-gap', S.paraGap + 'em');
  if (S.margin > 0) {
    st.setProperty('--read-margin', S.margin + 'px');
    root.dataset.margin = '1';
  } else {
    st.removeProperty('--read-margin');
    delete root.dataset.margin;
  }
  const p = activePreset();
  const setOr = (name: string, v: string | null): void => (v ? st.setProperty(name, v) : void st.removeProperty(name));
  setOr('--read-bg', p.bg);
  setOr('--read-fg', p.fg);
  setOr('--read-accent', p.accent);
  root.dataset.preset = p.id;
  const bright = S.brightnessAuto ? 1 : S.brightness;
  st.setProperty('--brightness', String(bright));
  st.setProperty('--read-pad-y', S.padY + 'px');
  let dim = document.getElementById('dim');
  if (!dim && document.body) {
    dim = document.createElement('div');
    dim.id = 'dim';
    dim.setAttribute('aria-hidden', 'true');
    document.body.appendChild(dim);
  }
  if (dim) dim.style.opacity = String(Math.round((1 - bright) * 100) / 100);
  syncThemeColor();
  void ensure(S.font);
}

interface RGB {
  r: number;
  g: number;
  b: number;
  a: number;
}

function parseColor(s: string): RGB | null {
  const t = s.trim();
  const hex = /^#([0-9a-f]{3,8})$/i.exec(t);
  if (hex) {
    let h = hex[1] as string;
    if (h.length === 3 || h.length === 4) h = [...h].map((c) => c + c).join('');
    if (h.length !== 6 && h.length !== 8) return null;
    const n = Number.parseInt(h.slice(0, 6), 16);
    return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255, a: h.length === 8 ? Number.parseInt(h.slice(6), 16) / 255 : 1 };
  }
  const rgb = /^rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)\s*(?:[,/]\s*([\d.]+)\s*)?\)$/i.exec(t);
  if (!rgb) return null;
  return { r: Number(rgb[1]), g: Number(rgb[2]), b: Number(rgb[3]), a: rgb[4] === undefined ? 1 : Number(rgb[4]) };
}

function toHex(r: number, g: number, b: number): string {
  const h = (n: number): string => Math.max(0, Math.min(255, Math.round(n))).toString(16).padStart(2, '0');
  return `#${h(r)}${h(g)}${h(b)}`;
}

/** Opaque `#rrggbb`. A translucent `fg` is composited over `bg` (status-bar APIs reject rgba). */
export function solidHex(fg: string, bg = '#000000'): string {
  const f = parseColor(fg);
  const under = parseColor(bg);
  if (!f) return under ? toHex(under.r, under.g, under.b) : '#0d9488';
  if (f.a >= 0.999 || !under) return toHex(f.r, f.g, f.b);
  const a = Math.max(0, Math.min(1, f.a));
  return toHex(f.r * a + under.r * (1 - a), f.g * a + under.g * (1 - a), f.b * a + under.b * (1 - a));
}

/** Solid chrome colour: the reading page, or the frosted header composited over the page. */
export function chromeColor(): string {
  if (typeof getComputedStyle !== 'function') return '#0d9488';
  const cs = getComputedStyle(document.documentElement);
  const reading = !!document.body?.classList.contains('view-read');
  const page = cs.getPropertyValue('--bg').trim() || '#000000';
  const raw = (reading ? cs.getPropertyValue('--read-bg') : cs.getPropertyValue('--header-bg')).trim();
  return solidHex(raw || page, reading ? raw || page : page);
}

/** `<meta name="theme-color">` follows the page (a solid colour; reader routes use the reading background). */
export function syncThemeColor(): void {
  const meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
  const c = chromeColor();
  if (meta && c) meta.content = c;
  syncStatusBar(c);
}

interface ThemeBarsPlugin {
  apply(o: { color: string; dark: boolean }): unknown;
}
interface SystemBarsPlugin {
  setStyle(o: { style: string }): unknown;
}

const quiet = (r: unknown): void => {
  try {
    void Promise.resolve(r).catch(() => {});
  } catch {
    // ignore
  }
};

/**
 * Android: paint the system bars and pick light or dark icons.
 * The bridge global exposes plugins on `Capacitor.Plugins` (`registerPlugin` exists only in the bundled core,
 * the same gap as the media service). ThemeBars sets the colour; SystemBars is the icon-only fallback.
 */
export function syncStatusBar(color?: string): void {
  try {
    if (!isNative()) return;
    const cap = (
      globalThis as {
        Capacitor?: { Plugins?: Record<string, unknown>; registerPlugin?: (n: string) => unknown };
      }
    ).Capacitor;
    const hex = color || chromeColor();
    const dark = isDark();
    const plugins = cap?.Plugins;
    const theme = plugins?.ThemeBars as ThemeBarsPlugin | undefined;
    if (theme?.apply) {
      quiet(theme.apply({ color: hex, dark }));
      return;
    }
    const bars = (plugins?.SystemBars ?? (cap?.registerPlugin ? cap.registerPlugin('SystemBars') : null)) as SystemBarsPlugin | null;
    if (bars?.setStyle) quiet(bars.setStyle({ style: dark ? 'DARK' : 'LIGHT' }));
  } catch {
    // no native bars
  }
}

type Listener = (key: SettingKey | null, value: unknown) => void;
const listeners = new Set<Listener>();

/** Subscribes to changes (`key` null = reset or an external change). Returns the unsubscribe function. */
export function onChange(fn: Listener): () => void {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}
function notify(key: SettingKey | null, value: unknown): void {
  for (const fn of [...listeners]) {
    try {
      fn(key, value);
    } catch (e) {
      console.error(e);
    }
  }
  emit('settings', { key });
}

export const get = <K extends SettingKey>(key: K): Settings[K] => S[key];

/** Validates, stores and applies one setting. Returns the value actually stored. */
export function set<K extends SettingKey>(key: K, value: unknown): Settings[K] {
  const v = normalise(key, value);
  if (S[key] === v) return v;
  S[key] = v;
  save();
  apply();
  notify(key, v);
  return v;
}

/** Sets several settings with one save/apply/notification. */
export function patch(values: Partial<Settings>): void {
  let changed = false;
  for (const k of Object.keys(values) as SettingKey[]) {
    if (!(k in DEF)) continue;
    const v = normalise(k, values[k]);
    if (S[k] !== v) {
      (S as unknown as Record<string, unknown>)[k] = v;
      changed = true;
    }
  }
  if (!changed) return;
  save();
  apply();
  notify(null, null);
}

/** Back to the defaults; `keys` limits the reset to those settings. */
export function reset(keys?: SettingKey[]): void {
  const def = defaults();
  for (const k of keys || (Object.keys(def) as SettingKey[])) (S as unknown as Record<string, unknown>)[k] = def[k];
  save();
  apply();
  notify(null, null);
}

let started = false;
let barTimer = 0;
let lastScheme = '';
/** Re-applies when the clock-driven scheme flipped (scheduled night mode). */
function clockTick(): void {
  if (S.theme !== 'auto' || !S.nightSchedule) return;
  if (scheme() === lastScheme) return;
  apply();
  notify('theme', S.theme);
}
/** Loads, applies and starts following the system scheme and changes made in other tabs. Idempotent. */
export function init(): void {
  load();
  apply();
  if (started || typeof window === 'undefined') return;
  started = true;
  window.setInterval(clockTick, 60_000);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') clockTick();
  });
  mqDark()?.addEventListener?.('change', () => {
    if (S.theme === 'auto') {
      apply();
      notify('theme', S.theme);
    }
  });
  window.addEventListener('storage', (e) => {
    if (e.key !== KEY) return;
    load();
    apply();
    notify(null, null);
  });
  // rotation: Capacitor SystemBars repaints the decor view teal; re-apply after it
  if (isNative()) {
    window.addEventListener('resize', () => {
      window.clearTimeout(barTimer);
      barTimer = window.setTimeout(() => syncStatusBar(), 80);
    });
  }
}

export const settings = { inNightWindow, DEF, S, RANGE, presets, defaults, normalise, load, save, apply, get, set, patch, reset, onChange, init, isDark, scheme, activePreset, fontStack, solidHex, chromeColor, syncThemeColor, syncStatusBar, isNative };
