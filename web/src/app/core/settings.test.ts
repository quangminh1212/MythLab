import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DEF, RANGE, S, activePreset, apply, chromeColor, defaults, get, load, normalise, onChange, patch, reset, scheme, set, solidHex, syncStatusBar, syncThemeColor } from './settings';

const KEY = 'mythlab.settings';
const stored = (): Record<string, unknown> => JSON.parse(localStorage.getItem(KEY) || '{}') as Record<string, unknown>;

beforeEach(() => {
  localStorage.clear();
  load();
});

describe('settings model', () => {
  it('starts from the defaults and persists them with the migration flags', () => {
    expect(S).toEqual(defaults());
    expect(stored()).toMatchObject({ theme: 'light', size: 20, ui2: 1, ui3: 1 });
  });

  it('clamps numbers and rejects unknown enum values', () => {
    expect(normalise('size', 999)).toBe(RANGE.size[1]);
    expect(normalise('size', '18')).toBe(18);
    expect(normalise('size', 'abc')).toBe(DEF.size);
    expect(normalise('theme', 'neon')).toBe(DEF.theme);
    expect(normalise('align', 'left')).toBe('left');
    expect(normalise('autoNext', false)).toBe(false);
    expect(normalise('autoNext', 'yes')).toBe(DEF.autoNext);
    expect(set('rate', 9)).toBe(RANGE.rate[1]);
    expect(get('rate')).toBe(RANGE.rate[1]);
    expect(stored().rate).toBe(RANGE.rate[1]);
  });

  it('migrates old stored values and keeps unknown keys for newer versions', () => {
    localStorage.setItem(KEY, JSON.stringify({ theme: 'sepia', font: 'serif', size: 24, engine: 'native', future: { a: 1 } }));
    expect(load()).toBe(true);
    expect(S.theme).toBe('light');
    expect(S.font).toBe('literata');
    expect(S.size).toBe(24);
    expect(S.engine).toBe('browser');
    expect(stored().future).toEqual({ a: 1 });
    expect(load()).toBe(false);
  });

  it('maps a saved server (Edge) engine to the device voice and drops server voice ids', () => {
    localStorage.setItem(KEY, JSON.stringify({ engine: 'edge', voice: 'vi-VN-HoaiMyNeural', browserVoice: 'vi-VN-NamMinhNeural', nativeVoice: 'vi-VN-Vais1000Piper' }));
    expect(load()).toBe(true);
    expect(S.engine).toBe('browser');
    expect(S.browserVoice).toBe('');
    expect(S.nativeVoice).toBe('');
    expect('voice' in stored()).toBe(false);
    expect(load()).toBe(false);
    localStorage.setItem(KEY, JSON.stringify({ engine: 'edge', browserVoice: 'Google Tiếng Việt' }));
    load();
    expect(S.browserVoice).toBe('Google Tiếng Việt');
    expect(normalise('engine', 'edge')).toBe(DEF.engine);
  });

  it('new users start with the voice of the device; Piper is only a choice', () => {
    expect(DEF.engine).toBe('browser');
    expect(DEF.piperVoice).toBe('vi_VN-vais1000-medium');
    expect(normalise('engine', 'piper')).toBe('piper');
    expect(normalise('engine', 'sherpa')).toBe(DEF.engine);
  });

  it('keeps a stored Piper choice and returns to the device voice when the host cannot run it', () => {
    vi.stubGlobal('caches', {});
    vi.stubGlobal('Worker', class {});
    localStorage.setItem(KEY, JSON.stringify({ engine: 'piper', piperVoice: 'vi_VN-vivos-x_low' }));
    load();
    expect(S.engine).toBe('piper');
    expect(S.piperVoice).toBe('vi_VN-vivos-x_low');
    vi.stubGlobal('Worker', undefined);
    load();
    expect(S.engine).toBe('browser');
    vi.unstubAllGlobals();
  });

  it('a sepia theme chosen after the migration is kept', () => {
    set('theme', 'sepia');
    load();
    expect(S.theme).toBe('sepia');
    expect(scheme()).toBe('sepia');
  });

  it('survives corrupt storage', () => {
    localStorage.setItem(KEY, '[1,2');
    load();
    expect(S).toEqual(defaults());
    localStorage.setItem(KEY, '"text"');
    load();
    expect(S.size).toBe(DEF.size);
  });

  it('applies the scheme and the reader variables to the document', () => {
    patch({ theme: 'dark', size: 22, line: 2, width: 800, nightPreset: 'than' });
    const root = document.documentElement;
    expect(root.dataset.theme).toBe('dark');
    expect(root.dataset.scheme).toBe('dark');
    expect(root.style.getPropertyValue('--read-size')).toBe('22px');
    expect(root.style.getPropertyValue('--read-line')).toBe('2');
    expect(root.style.getPropertyValue('--read-width')).toBe('800px');
    expect(activePreset().id).toBe('than');
    expect(root.style.getPropertyValue('--read-bg')).toBe('#1f2937');
    set('nightPreset', 'default');
    expect(root.style.getPropertyValue('--read-bg')).toBe('');
    set('theme', 'light');
    apply();
    expect(root.dataset.scheme).toBe('light');
    expect(activePreset().id).toBe('default');
  });

  it('notifies listeners and resets', () => {
    const seen: (string | null)[] = [];
    const off = onChange((k) => seen.push(k));
    set('size', 25);
    set('size', 25);
    patch({ line: 2.2, word: 1 });
    reset(['size']);
    off();
    set('size', 30);
    expect(seen).toEqual(['size', null, null]);
    expect(S.line).toBe(2.2);
    reset();
    expect(S).toEqual(defaults());
  });
});

describe('shortcuts setting', () => {
  it('defaults on and normalises non-booleans', () => {
    expect(DEF.shortcuts).toBe(true);
    expect(normalise('shortcuts', 'no')).toBe(true);
    expect(normalise('shortcuts', false)).toBe(false);
  });
});

describe('theme and accent persistence', () => {
  it.each(['light', 'sepia', 'forest', 'dark', 'navy', 'amoled', 'auto'])('theme %s is stored, reloaded and applied', (theme) => {
    set('theme', theme);
    expect(stored().theme).toBe(theme);
    S.theme = 'light';
    load();
    expect(S.theme).toBe(theme);
    apply();
    const root = document.documentElement;
    expect(root.dataset.theme).toBe(theme);
    expect(root.dataset.scheme).toBe(scheme());
    const dark = ['dark', 'navy', 'amoled'].includes(scheme());
    expect(root.dataset.mode).toBe(dark ? 'dark' : 'light');
    expect(root.style.colorScheme).toBe(dark ? 'dark' : 'light');
  });

  it('dark themes use the night reading presets', () => {
    set('theme', 'amoled');
    patch({ nightPreset: 'than' });
    expect(activePreset().id).toBe('than');
    set('theme', 'forest');
    expect(activePreset().id).toBe(S.dayPreset);
  });

  it('accent is validated, stored and applied; unknown ids fall back', () => {
    set('accent', 'violet');
    expect(stored().accent).toBe('violet');
    expect(document.documentElement.dataset.accent).toBe('violet');
    expect(normalise('accent', 'nope')).toBe('default');
    expect(normalise('theme', 'neon')).toBe('light');
  });
});

describe('system bar colour', () => {
  it('composites a frosted header into an opaque hex', () => {
    expect(solidHex('#0b1120')).toBe('#0b1120');
    expect(solidHex('rgba(255, 255, 255, 0.94)', '#f3f4f6')).toBe('#fefefe');
    expect(solidHex('rgba(0, 0, 0, 0.92)', '#000000')).toBe('#000000');
    expect(solidHex('not-a-color', '#111827')).toBe('#111827');
    expect(solidHex('nope', 'also-nope')).toBe('#0d9488');
  });

  it('theme-color is the header over the page, or the reading background', () => {
    const root = document.documentElement;
    root.style.setProperty('--bg', '#f3f4f6');
    root.style.setProperty('--header-bg', 'rgba(255, 255, 255, 0.94)');
    root.style.setProperty('--read-bg', '#1f2937');
    document.body.classList.remove('view-read');
    const meta = document.createElement('meta');
    meta.name = 'theme-color';
    document.head.appendChild(meta);
    syncThemeColor();
    expect(chromeColor()).toBe('#fefefe');
    expect(meta.content).toBe('#fefefe');
    document.body.classList.add('view-read');
    syncThemeColor();
    expect(meta.content).toBe('#1f2937');
    meta.remove();
    root.style.removeProperty('--bg');
    root.style.removeProperty('--header-bg');
    root.style.removeProperty('--read-bg');
    document.body.classList.remove('view-read');
  });

  it('asks ThemeBars on the native bridge, and SystemBars when that plugin is absent', () => {
    const applyBars = vi.fn(async () => ({}));
    const setStyle = vi.fn(async () => ({}));
    const g = globalThis as { Capacitor?: unknown };
    g.Capacitor = { isNativePlatform: () => true, Plugins: { ThemeBars: { apply: applyBars }, SystemBars: { setStyle } } };
    document.documentElement.style.setProperty('--bg', '#0b1120');
    document.documentElement.style.setProperty('--header-bg', '#0b1120');
    set('theme', 'dark');
    syncStatusBar('#0b1120');
    expect(applyBars).toHaveBeenCalledWith({ color: '#0b1120', dark: true });
    expect(setStyle).not.toHaveBeenCalled();
    g.Capacitor = { isNativePlatform: () => true, Plugins: { SystemBars: { setStyle } } };
    syncStatusBar('#0b1120');
    expect(setStyle).toHaveBeenCalledWith({ style: 'DARK' });
    g.Capacitor = { isNativePlatform: () => false, Plugins: { ThemeBars: { apply: applyBars } } };
    applyBars.mockClear();
    syncStatusBar('#ffffff');
    expect(applyBars).not.toHaveBeenCalled();
    delete g.Capacitor;
  });
});
