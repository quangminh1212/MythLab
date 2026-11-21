/**
 * The theme table: one entry per selectable colour theme. The colours themselves live in styles/tokens.css, one
 * `:root[data-scheme="<id>"]` block per entry (contrast.test.ts checks that every entry has a block and that every
 * text pair is >= 4.5:1). Adding a theme = one entry here + one block there + the id in public/boot.js (a test
 * keeps boot.js in sync). `bg`/`surface`/`text`/`accent` only paint the small preview swatch in Settings.
 */
export interface ThemeDef {
  id: string;
  label: string;
  /** Dark family: night reading presets, dark status-bar icons are light, `color-scheme: dark`. */
  dark: boolean;
  bg: string;
  surface: string;
  text: string;
  accent: string;
}

export const THEMES = [
  { id: 'light', label: 'Sáng', dark: false, bg: '#f3f4f6', surface: '#ffffff', text: '#111827', accent: '#0f766e' },
  { id: 'sepia', label: 'Giấy ngà', dark: false, bg: '#f4efe4', surface: '#fffdf7', text: '#2b2520', accent: '#0f766e' },
  { id: 'forest', label: 'Xanh lá', dark: false, bg: '#e8f0e4', surface: '#f5faf2', text: '#1c2a1b', accent: '#166534' },
  { id: 'dark', label: 'Tối', dark: true, bg: '#0b1120', surface: '#1e293b', text: '#f7f9fb', accent: '#2dd4bf' },
  { id: 'navy', label: 'Xanh đêm', dark: true, bg: '#0a1424', surface: '#14233a', text: '#eef3fa', accent: '#60a5fa' },
  { id: 'amoled', label: 'AMOLED', dark: true, bg: '#000000', surface: '#0d0d0d', text: '#f2f2f2', accent: '#2dd4bf' },
] as const satisfies readonly ThemeDef[];

export type Scheme = (typeof THEMES)[number]['id'];
export type Theme = Scheme | 'auto';

export const SCHEME_IDS: readonly string[] = THEMES.map((t) => t.id);
export const THEME_IDS: readonly string[] = [...SCHEME_IDS, 'auto'];
export const themeDef = (id: string): ThemeDef => (THEMES.find((t) => t.id === id) as ThemeDef | undefined) ?? (THEMES[0] as ThemeDef);
export const isDarkScheme = (id: string): boolean => themeDef(id).dark;

/** Accent colour choices ("default" keeps the theme's own accent). The values live in tokens.css (`data-accent`). */
export interface AccentDef {
  id: string;
  label: string;
  /** Swatch colour (the light-family accent). */
  color: string;
}
export const ACCENTS: readonly AccentDef[] = [
  { id: 'default', label: 'Theo giao diện', color: '#0f766e' },
  { id: 'blue', label: 'Xanh dương', color: '#1d4ed8' },
  { id: 'violet', label: 'Tím', color: '#6d28d9' },
  { id: 'rose', label: 'Hồng đỏ', color: '#be123c' },
  { id: 'orange', label: 'Cam', color: '#b45309' },
];
export const ACCENT_IDS: readonly string[] = ACCENTS.map((a) => a.id);
