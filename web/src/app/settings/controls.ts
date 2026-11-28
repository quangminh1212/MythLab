/**
 * Form controls of the settings sheet. Every control carries a `data-*` attribute naming the setting it edits;
 * one delegated listener per sheet writes the value through `core/settings` (which validates, stores and
 * applies it) and one subscription keeps every control in step with the stored value (presets, reset, other
 * tabs, the quick row and the full tabs showing the same setting).
 */
import { html, type SafeHtml } from '../core/html';
import { onChange, RANGE, S, set, type SettingKey, type Settings } from '../core/settings';

export type RangeKey = keyof typeof RANGE;

export interface RangeDef {
  key: RangeKey;
  label: string;
  step: number;
  /** Text shown next to the label for a value. */
  fmt(v: number): string;
}

const fix = (v: number, d: number): string => v.toFixed(d).replace('.', ',');

export const RANGES: Record<RangeKey, RangeDef> = {
  brightness: { key: 'brightness', label: 'Độ sáng', step: 0.05, fmt: (v) => `${Math.round(v * 100)}%` },
  weight: { key: 'weight', label: 'Độ đậm', step: 100, fmt: (v) => String(Math.round(v)) },
  size: { key: 'size', label: 'Cỡ chữ', step: 1, fmt: (v) => `${Math.round(v)} px` },
  line: { key: 'line', label: 'Giãn dòng', step: 0.1, fmt: (v) => fix(v, 1) },
  letter: { key: 'letter', label: 'Giãn chữ', step: 0.1, fmt: (v) => `${fix(v, 1)} px` },
  word: { key: 'word', label: 'Giãn từ', step: 0.5, fmt: (v) => `${fix(v, 1)} px` },
  indent: { key: 'indent', label: 'Thụt đầu dòng', step: 0.25, fmt: (v) => `${fix(v, 2)} em` },
  paraGap: { key: 'paraGap', label: 'Cách đoạn', step: 0.1, fmt: (v) => `${fix(v, 1)} em` },
  margin: { key: 'margin', label: 'Lề hai bên', step: 2, fmt: (v) => (v === 0 ? 'Tự động' : `${Math.round(v)} px`) },
  padY: { key: 'padY', label: 'Lề trên/dưới', step: 2, fmt: (v) => (v === 0 ? 'Mặc định' : `+${Math.round(v)} px`) },
  width: { key: 'width', label: 'Độ rộng cột', step: 20, fmt: (v) => `${Math.round(v)} px` },
  rate: { key: 'rate', label: 'Tốc độ đọc', step: 0.1, fmt: (v) => `${fix(v, 1)}×` },
  pitch: { key: 'pitch', label: 'Cao độ giọng', step: 0.05, fmt: (v) => fix(v, 2) },
};

let seq = 0;

/** A labelled slider bound to a numeric setting. */
export function rangeRow(key: RangeKey): SafeHtml {
  const d = RANGES[key];
  const [min, max] = RANGE[key];
  const id = `ss-r-${key}-${++seq}`;
  return html`<div class="ss-row">
    <label class="ss-label" for="${id}"><span>${d.label}</span><output class="ss-out" for="${id}" data-out="${key}">${d.fmt(S[key])}</output></label>
    <input id="${id}" class="ss-range" type="range" min="${min}" max="${max}" step="${d.step}" value="${S[key]}" data-range="${key}" ${key === 'brightness' && S.brightnessAuto ? html`disabled` : ''} />
  </div>`;
}

/** A group of radio buttons drawn as a segmented control. */
export function segRow<K extends 'theme' | 'align' | 'readMode' | 'engine'>(key: K, label: string, options: [Settings[K], string][], o: { compact?: boolean; hideLabel?: boolean } = {}): SafeHtml {
  const group = `ss-g-${key}-${++seq}`;
  return html`<div class="ss-row">
    <div class="${o.hideLabel ? 'sr-only' : 'ss-label'}" id="${group}-l">${label}</div>
    <div class="ss-seg ${o.compact ? 'is-compact' : ''}" role="radiogroup" aria-labelledby="${group}-l" data-seg="${key}">
      ${options.map(([v, text]) => html`<label class="ss-opt"><input type="radio" name="${group}" value="${String(v)}" ${String(S[key]) === String(v) ? html`checked` : ''} /><span>${text}</span></label>`)}
    </div>
  </div>`;
}

/** A text-like input (time, colour) bound to a string setting. */
export function fieldRow(key: 'nightFrom' | 'nightTo' | 'customBg' | 'customFg', type: 'time' | 'color', label: string): SafeHtml {
  const id = `ss-f-${key}-${++seq}`;
  return html`<div class="ss-row ss-field">
    <label class="ss-label" for="${id}"><span>${label}</span></label>
    <input id="${id}" class="ss-input ss-input-${type}" type="${type}" value="${S[key]}" data-field="${key}" />
  </div>`;
}

/** A checkbox bound to a boolean setting. */
export function checkRow(key: { [K in SettingKey]: Settings[K] extends boolean ? K : never }[SettingKey], label: string, hint?: string): SafeHtml {
  const id = `ss-c-${key}-${++seq}`;
  return html`<div class="ss-row ss-check">
    <input id="${id}" type="checkbox" data-bool="${key}" ${S[key] ? html`checked` : ''} />
    <label for="${id}"><span>${label}</span>${hint ? html`<small class="hint">${hint}</small>` : ''}</label>
  </div>`;
}

/** Brings every bound control inside `root` in line with the stored settings. */
export function syncControls(root: ParentNode): void {
  for (const el of root.querySelectorAll<HTMLInputElement>('input[data-range]')) {
    const key = el.dataset.range as RangeKey;
    const v = S[key];
    if (Number(el.value) !== v) el.value = String(v);
    for (const out of root.querySelectorAll<HTMLElement>(`[data-out="${key}"]`)) out.textContent = RANGES[key].fmt(v);
  }
  for (const el of root.querySelectorAll<HTMLInputElement>('input[data-range="brightness"]')) el.disabled = S.brightnessAuto;
  for (const el of root.querySelectorAll<HTMLInputElement>('input[data-field]')) {
    const v = String(S[el.dataset.field as keyof Settings]);
    if (el.value !== v) el.value = v;
  }
  for (const el of root.querySelectorAll<HTMLElement>('[data-show-if]')) el.hidden = !(el.dataset.showIf === 'nightSchedule' ? S.theme === 'auto' && S.nightSchedule : S.dayPreset === 'custom' || S.nightPreset === 'custom');
  for (const el of root.querySelectorAll<HTMLInputElement>('input[data-bool]')) el.checked = !!S[el.dataset.bool as keyof Settings];
  for (const box of root.querySelectorAll<HTMLElement>('[data-seg]')) {
    const cur = String(S[box.dataset.seg as keyof Settings]);
    for (const r of box.querySelectorAll<HTMLInputElement>('input[type="radio"]')) r.checked = r.value === cur;
  }
}

/**
 * Writes control changes to the settings and keeps the controls current. Returns the function that removes
 * both again. Sliders write on `input` (live preview), checkboxes and radios on `change`.
 */
export function bindControls(root: HTMLElement): () => void {
  const onInput = (e: Event): void => {
    const t = e.target as HTMLInputElement;
    if (t.dataset?.range) set(t.dataset.range as RangeKey, t.value);
    else if (t.dataset?.field && t.value) set(t.dataset.field as 'nightFrom', t.value);
  };
  const onChange2 = (e: Event): void => {
    const t = e.target as HTMLInputElement;
    if (t.dataset?.bool) set(t.dataset.bool as 'tapZones', t.checked);
    else if (t.type === 'radio' && t.checked) {
      const key = (t.closest('[data-seg]') as HTMLElement | null)?.dataset.seg;
      if (key) set(key as 'theme', t.value);
    }
  };
  root.addEventListener('input', onInput);
  root.addEventListener('change', onChange2);
  const off = onChange(() => syncControls(root));
  return () => {
    root.removeEventListener('input', onInput);
    root.removeEventListener('change', onChange2);
    off();
  };
}
