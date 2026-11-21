// WCAG AA for every text/background pair of the three schemes (parsed from styles/tokens.css, one per entry of core/themes.ts) and of the 11
// reading presets (core/settings.ts).
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { presets } from './settings';
import { ACCENTS, THEMES } from './themes';

const css = readFileSync(resolve(process.cwd(), 'src/styles/tokens.css'), 'utf8');

function lum(hex: string): number {
  const m = /^#([0-9a-f]{6})$/i.exec(hex);
  if (!m) throw new Error(`not a #rrggbb colour: ${hex}`);
  const n = parseInt(m[1] as string, 16);
  const ch = [n >> 16, (n >> 8) & 255, n & 255].map((v) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  }) as [number, number, number];
  return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
}

function ratio(a: string, b: string): number {
  const la = lum(a);
  const lb = lum(b);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

function block(scheme: string): Record<string, string> {
  const start = css.indexOf(`:root[data-scheme="${scheme}"] {`);
  if (start < 0) throw new Error(`no block for scheme ${scheme}`);
  const body = css.slice(start, css.indexOf('}', start));
  const out: Record<string, string> = {};
  for (const m of body.matchAll(/^\s*(--[\w-]+):\s*(#[0-9a-fA-F]{6});/gm)) out[m[1] as string] = m[2] as string;
  return out;
}

/** [foreground, background]: every pairing the stylesheets use for text. */
const TEXT_PAIRS: [string, string][] = [
  ['--text', '--bg'],
  ['--text', '--surface'],
  ['--text', '--surface-2'],
  ['--text', '--surface-3'],
  ['--text', '--hl'],
  ['--text-2', '--bg'],
  ['--text-2', '--surface'],
  ['--text-2', '--surface-2'],
  ['--text-2', '--surface-3'],
  ['--text-2', '--hl'],
  ['--muted', '--bg'],
  ['--muted', '--surface'],
  ['--muted', '--surface-2'],
  ['--muted', '--surface-3'],
  ['--muted', '--hl'],
  ['--accent-text', '--bg'],
  ['--accent-text', '--surface'],
  ['--accent-text', '--surface-2'],
  ['--accent-text', '--surface-3'],
  ['--accent-text', '--hl'],
  ['--accent-ink', '--accent'],
  ['--accent-ink', '--accent-hover'],
  ['--danger', '--bg'],
  ['--danger', '--surface'],
  ['--danger', '--danger-bg'],
  ['--ok', '--bg'],
  ['--ok', '--surface'],
  ['--read-fg', '--read-bg'],
  ['--read-accent', '--read-bg'],
  ['--toast-fg', '--toast-bg'],
];

/** Non-text UI (input borders, focus ring): 3:1 against the surfaces they sit on. */
const UI_PAIRS: [string, string][] = [
  ['--border-strong', '--surface'],
  ['--border-strong', '--bg'],
  ['--accent', '--surface'],
  ['--accent', '--bg'],
];

describe.each(THEMES.map((t) => t.id))('tokens.css, %s scheme', (scheme) => {
  const t = block(scheme);
  it('defines every colour token', () => {
    for (const name of new Set([...TEXT_PAIRS, ...UI_PAIRS].flat())) expect(t[name], name).toMatch(/^#[0-9a-f]{6}$/i);
  });
  it.each(TEXT_PAIRS)('%s on %s is at least 4.5:1', (fg, bg) => {
    expect(ratio(t[fg] as string, t[bg] as string)).toBeGreaterThanOrEqual(4.5);
  });
  it.each(UI_PAIRS)('%s on %s is at least 3:1', (fg, bg) => {
    expect(ratio(t[fg] as string, t[bg] as string)).toBeGreaterThanOrEqual(3);
  });
});

describe('reading presets', () => {
  const all = [...presets.day.map((p) => ({ ...p, mode: 'day' })), ...presets.night.map((p) => ({ ...p, mode: 'night' }))];
  it('are the 11 presets: 6 day, 5 night, each list starting with the theme default', () => {
    expect(presets.day.length).toBe(6);
    expect(presets.night.length).toBe(5);
    expect(presets.day[0]?.bg).toBeNull();
    expect(presets.night[0]?.bg).toBeNull();
    expect(new Set(presets.day.map((p) => p.id)).size).toBe(6);
    expect(new Set(presets.night.map((p) => p.id)).size).toBe(5);
  });
  it.each(all.filter((p) => p.bg))('$mode/$id: text and accent are at least 4.5:1 on the background', (p) => {
    expect(ratio(p.fg as string, p.bg as string)).toBeGreaterThanOrEqual(4.5);
    expect(ratio(p.accent as string, p.bg as string)).toBeGreaterThanOrEqual(4.5);
  });
  it('the default presets use the scheme reading colours, which pass in all three schemes', () => {
    for (const { id: scheme } of THEMES) {
      const t = block(scheme);
      expect(ratio(t['--read-fg'] as string, t['--read-bg'] as string)).toBeGreaterThanOrEqual(4.5);
      expect(ratio(t['--read-accent'] as string, t['--read-bg'] as string)).toBeGreaterThanOrEqual(4.5);
    }
  });
});

describe('theme table', () => {
  it('has unique ids, a swatch preview that matches tokens.css, and both a light and a dark family', () => {
    expect(new Set(THEMES.map((t) => t.id)).size).toBe(THEMES.length);
    expect(THEMES.length).toBeGreaterThanOrEqual(6);
    expect(THEMES.some((t) => t.dark)).toBe(true);
    expect(THEMES.some((t) => !t.dark)).toBe(true);
    for (const t of THEMES) {
      const tk = block(t.id);
      expect(tk['--bg'], t.id).toBe(t.bg);
      expect(tk['--surface'], t.id).toBe(t.surface);
      expect(tk['--text'], t.id).toBe(t.text);
      expect(new RegExp(String.raw`:root\[data-scheme="${t.id}"\] \{\s*color-scheme: ${t.dark ? 'dark' : 'light'};`).test(css), `${t.id} color-scheme`).toBe(true);
    }
  });
  it('public/boot.js knows every theme and which are dark', () => {
    const boot = readFileSync(resolve(process.cwd(), 'public/boot.js'), 'utf8');
    for (const t of THEMES) expect(boot, t.id).toContain(`'${t.id}'`);
    for (const a of ACCENTS) expect(boot, a.id).toContain(`'${a.id}'`);
    const dark = /var DARK = \{([^}]*)\}/.exec(boot)?.[1] ?? '';
    expect([...dark.matchAll(/(\w+):/g)].map((m) => m[1]).sort()).toEqual(THEMES.filter((t) => t.dark).map((t) => t.id).sort());
  });
});

describe('accent colours, on every theme', () => {
  const accentBlock = (id: string, mode: string): Record<string, string> => {
    const m = new RegExp(String.raw`:root\[data-accent="${id}"\]\[data-mode="${mode}"\] \{([^}]*)\}`).exec(css);
    if (!m) throw new Error(`no accent block ${id}/${mode}`);
    const out: Record<string, string> = {};
    for (const x of (m[1] as string).matchAll(/(--[\w-]+):\s*(#[0-9a-fA-F]{6});/g)) out[x[1] as string] = x[2] as string;
    return out;
  };
  const pairs: [string, string][] = [
    ['--accent-text', '--bg'],
    ['--accent-text', '--surface'],
    ['--accent-text', '--surface-2'],
    ['--accent-text', '--surface-3'],
    ['--accent-text', '--hl'],
    ['--accent-ink', '--accent'],
    ['--accent-ink', '--accent-hover'],
    ['--read-accent', '--read-bg'],
  ];
  const cases = ACCENTS.filter((a) => a.id !== 'default').flatMap((a) => THEMES.map((t) => [a.id, t.id, t.dark] as const));
  it.each(cases)('%s on %s', (a, theme, dark) => {
    const t = { ...block(theme), ...accentBlock(a, dark ? 'dark' : 'light') };
    for (const [fg, bg] of pairs) expect(ratio(t[fg] as string, t[bg] as string), `${fg} on ${bg}`).toBeGreaterThanOrEqual(4.5);
    expect(ratio(t['--accent'] as string, t['--surface'] as string), 'accent on surface').toBeGreaterThanOrEqual(3);
    expect(ratio(t['--accent'] as string, t['--bg'] as string), 'accent on bg').toBeGreaterThanOrEqual(3);
  });
});
