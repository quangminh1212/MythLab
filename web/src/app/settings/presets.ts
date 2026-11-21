/** One-tap typography presets of the settings sheet: a named set of values for the text settings. */
import { DEF, normalise, type SettingKey, type Settings } from '../core/settings';

/** The settings a typography preset may touch (the font only when the preset names one). */
export const TYPO_KEYS = ['font', 'weight', 'size', 'line', 'letter', 'word', 'align', 'indent', 'paraGap', 'margin', 'width'] as const satisfies readonly SettingKey[];
export type TypoKey = (typeof TYPO_KEYS)[number];
export type TypoValues = Partial<Pick<Settings, TypoKey>>;

export interface TypoPreset {
  id: string;
  label: string;
  /** Short description shown under the label. */
  hint: string;
  values: TypoValues;
}

const base: TypoValues = { weight: DEF.weight, size: DEF.size, line: DEF.line, letter: DEF.letter, word: DEF.word, align: DEF.align, indent: DEF.indent, paraGap: DEF.paraGap, margin: DEF.margin, width: DEF.width };

export const TYPO_PRESETS: TypoPreset[] = [
  { id: 'default', label: 'Mặc định', hint: 'Cỡ 20, dòng thoáng vừa', values: { ...base, font: DEF.font } },
  { id: 'compact', label: 'Gọn', hint: 'Nhiều chữ trên màn hình', values: { ...base, size: 17, line: 1.5, paraGap: 0.6, width: 640, align: 'left' } },
  { id: 'airy', label: 'Thoáng', hint: 'Dòng và đoạn cách rộng', values: { ...base, size: 21, line: 2.1, paraGap: 1.4, letter: 0.2, width: 760, align: 'left' } },
  { id: 'large', label: 'Chữ lớn', hint: 'Dễ đọc, đỡ mỏi mắt', values: { ...base, size: 26, line: 1.9, weight: 500, paraGap: 1.1, width: 860, align: 'left' } },
  { id: 'book', label: 'Sách in', hint: 'Canh đều, thụt đầu dòng', values: { ...base, font: 'source-serif-4', size: 19, line: 1.65, paraGap: 0.2, indent: 1.5, width: 660, align: 'justify' } },
];

/** The values a preset really sets, validated like any other setting. */
export function presetValues(p: TypoPreset): TypoValues {
  const out: Record<string, unknown> = {};
  for (const k of Object.keys(p.values) as TypoKey[]) out[k] = normalise(k, p.values[k]);
  return out as TypoValues;
}

const same = (a: unknown, b: unknown): boolean => (typeof a === 'number' && typeof b === 'number' ? Math.abs(a - b) < 1e-6 : a === b);

/** The id of the preset whose values all match `s`, or null when the text was tuned by hand. */
export function matchPreset(s: Pick<Settings, TypoKey>): string | null {
  for (const p of TYPO_PRESETS) {
    const v = presetValues(p);
    if ((Object.keys(v) as TypoKey[]).every((k) => same(s[k], v[k]))) return p.id;
  }
  return null;
}
