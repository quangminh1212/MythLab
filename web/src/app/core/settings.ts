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
export type TtsEngine = 'edge' | 'browser' | 'native';

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
  engine: TtsEngine;
  voice: string;
  nativeVoice: string;
  browserVoice: string;
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
    engine: isNative() ? 'native' : 'edge',
    voice: 'vi-VN-HoaiMyNeural',
    nativeVoice: '',
    browserVoice: '',
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
  engine: ['edge', 'browser', 'native'],
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

const clamp = (v: unknown, [lo, hi]: readonly [number, number], d: number): number => {
  const n = typeof v === 'number' ? v : typeof v === 'string' && v.trim() !== '' ? Number(v) : NaN;
  return Number.isFinite(n) ? Math.min(hi, Math.max(lo, n)) : d;
};

/** Returns a valid value for `key` (clamped / defaulted). */
export function normalise<K extends SettingKey>(key: K, v: unknown): Settings[K] {
  const d = DEF[key];
  if (key in RANGE) return clamp(v, RANGE[key as keyof typeof RANGE], d as number) as Settings[K];
  if (key in ENUM) return ((ENUM[key as keyof typeof ENUM] as readonly string[]).includes(v as string) ? v : d) as Settings[K];
  if (key === 'dayPreset') return (presets.day.some((p) => p.id === v) ? v : d) as Settings[K];
  if (key === 'nightPreset') return (presets.night.some((p) => p.id === v) ? v : d) as Settings[K];
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
  if (next.engine === 'native' && !isNative()) next.engine = 'edge';
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
  if (S.theme === 'auto') return mqDark()?.matches ? 'dark' : 'light';
  return S.theme;
}
export const isDark = (): boolean => isDarkScheme(scheme());

/** The active reading preset (never null; the default preset has null colours). */
export function activePreset(): Preset {
  const list = isDark() ? presets.night : presets.day;
  const id = isDark() ? S.nightPreset : S.dayPreset;
  return list.find((p) => p.id === id) || (list[0] as Preset);
}

export const fontStack = (): string => cssStack(S.font);

/** Applies the settings to the document: data attributes, CSS variables, theme-color, brightness layer. */
export function apply(): void {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  const sc = scheme();
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
  st.setProperty('--brightness', String(S.brightness));
  let dim = document.getElementById('dim');
  if (!dim && document.body) {
    dim = document.createElement('div');
    dim.id = 'dim';
    dim.setAttribute('aria-hidden', 'true');
    document.body.appendChild(dim);
  }
  if (dim) dim.style.opacity = String(Math.round((1 - S.brightness) * 100) / 100);
  syncThemeColor();
  void ensure(S.font);
}

/** `<meta name="theme-color">` follows the page background (or the reading preset on reader routes). */
export function syncThemeColor(): void {
  const meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
  if (!meta || typeof getComputedStyle !== 'function') return;
  const cs = getComputedStyle(document.documentElement);
  const reading = document.body?.classList.contains('view-read');
  const c = ((reading && cs.getPropertyValue('--read-bg')) || cs.getPropertyValue('--header-bg') || cs.getPropertyValue('--bg')).trim();
  if (c) meta.content = c;
  syncStatusBar();
}

/** Android (Capacitor SystemBars): light icons on dark themes, dark icons on light ones. A no-op elsewhere. */
export function syncStatusBar(): void {
  try {
    if (!isNative()) return;
    const c = (globalThis as { Capacitor?: { registerPlugin?: (n: string) => { setStyle?: (o: { style: string }) => unknown } } }).Capacitor;
    const bars = c?.registerPlugin?.('SystemBars');
    const r = bars?.setStyle?.({ style: isDark() ? 'DARK' : 'LIGHT' });
    void Promise.resolve(r).catch(() => {});
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
/** Loads, applies and starts following the system scheme and changes made in other tabs. Idempotent. */
export function init(): void {
  load();
  apply();
  if (started || typeof window === 'undefined') return;
  started = true;
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
}

export const settings = { DEF, S, RANGE, presets, defaults, normalise, load, save, apply, get, set, patch, reset, onChange, init, isDark, scheme, activePreset, fontStack, syncThemeColor, syncStatusBar, isNative };
