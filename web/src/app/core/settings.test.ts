import { beforeEach, describe, expect, it } from 'vitest';
import { DEF, RANGE, S, activePreset, apply, defaults, get, load, normalise, onChange, patch, reset, scheme, set } from './settings';

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
    expect(S.engine).toBe('edge');
    expect(stored().future).toEqual({ a: 1 });
    expect(load()).toBe(false);
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
