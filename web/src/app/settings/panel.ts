/**
 * Settings sheet (stage W3): a modal bottom sheet on phones (the reading text stays visible above it) and a side
 * panel on wide screens. A quick row (text size, theme, reading mode) sits above five tabs: Giao diện, Chữ, Bố cục,
 * Giọng đọc and Nguồn dữ liệu. Every change is written straight through `core/settings`, so the page behind the
 * sheet is the live preview.
 *
 * Exports `settingsPanel: SettingsPanelApi` (core/contracts.ts).
 */
import type { SettingsPanelApi, SettingsTab } from '../core/contracts';
import { fonts, type FontInfo } from '../core/fonts';
import { html, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { activePreset, isDark, onChange, presets, RANGE, S, patch, reset, set, type Preset } from '../core/settings';
import { confirmDialog, openDialog, toast, type DialogHandle } from '../core/ui';
import { bindControls, checkRow, rangeRow, segRow, syncControls } from './controls';
import { matchPreset, presetValues, TYPO_PRESETS } from './presets';
import { mountSource } from './source';
import { mountVoice } from './voice';

interface TabDef {
  id: SettingsTab;
  label: string;
}
export const TABS: TabDef[] = [
  { id: 'theme', label: 'Giao diện' },
  { id: 'font', label: 'Chữ' },
  { id: 'layout', label: 'Bố cục' },
  { id: 'voice', label: 'Giọng đọc' },
  { id: 'source', label: 'Nguồn dữ liệu' },
];

const THEME_OPTIONS: ['light' | 'sepia' | 'dark' | 'auto', string][] = [
  ['light', 'Sáng'],
  ['sepia', 'Giấy'],
  ['dark', 'Tối'],
  ['auto', 'Tự động'],
];

const PREVIEW = 'Nguyễn Thị Ẩn ngồi bên hiên, ỡ ự ặ — trời về chiều. Gió lùa qua khe cửa, mang theo mùi khói bếp.';

let dlg: DialogHandle | null = null;
let lastTab: SettingsTab = 'theme';

const preview = (): SafeHtml => html`<p class="ss-preview" lang="vi" aria-label="Xem trước chữ khi đọc">${PREVIEW}</p>`;

// ---------------------------------------------------------------- tab bodies

function swatches(kind: 'day' | 'night'): SafeHtml {
  const list = presets[kind];
  const key = kind === 'day' ? 'dayPreset' : 'nightPreset';
  const label = kind === 'day' ? 'Màu nền ban ngày' : 'Màu nền ban đêm';
  return html`<div class="ss-row">
    <div class="ss-label" id="ss-sw-${kind}">${label}</div>
    <div class="ss-swatches" role="radiogroup" aria-labelledby="ss-sw-${kind}" data-swatches="${key}">
      ${list.map(
        (p: Preset) =>
          html`<button type="button" class="ss-sw ${p.bg ? '' : 'is-default'}" role="radio" aria-checked="${S[key] === p.id ? 'true' : 'false'}" data-preset="${p.id}" title="${p.label}">
            <span class="ss-sw-chip" data-bg="${p.bg || ''}" data-fg="${p.fg || ''}" aria-hidden="true">Aa</span>
            <span class="ss-sw-name">${p.label}</span>
          </button>`,
      )}
    </div>
  </div>`;
}

function paintSwatches(root: ParentNode): void {
  for (const box of root.querySelectorAll<HTMLElement>('[data-swatches]')) {
    const key = box.dataset.swatches as 'dayPreset' | 'nightPreset';
    for (const b of box.querySelectorAll<HTMLButtonElement>('[data-preset]')) b.setAttribute('aria-checked', String(S[key] === b.dataset.preset));
  }
}

function themeTab(): SafeHtml {
  return html`${segRow('theme', 'Chế độ', THEME_OPTIONS)} ${preview()} ${swatches('day')} ${swatches('night')}
    <p class="hint ss-active-note" id="ss-active-note"></p>
    ${rangeRow('brightness')}`;
}

function typoPresets(): SafeHtml {
  return html`<div class="ss-row">
    <div class="ss-label" id="ss-typo-l">Kiểu chữ có sẵn</div>
    <div class="ss-presets" role="radiogroup" aria-labelledby="ss-typo-l" data-typo>
      ${TYPO_PRESETS.map(
        (p) => html`<button type="button" class="ss-preset" role="radio" aria-checked="false" data-typo-id="${p.id}"><strong>${p.label}</strong><small>${p.hint}</small></button>`,
      )}
    </div>
  </div>`;
}

function fontTab(): SafeHtml {
  return html`${preview()} ${typoPresets()}
    <div class="ss-row">
      <div class="ss-label" id="ss-fonts-l">Phông chữ</div>
      <div id="ss-fonts" class="ss-fonts" role="radiogroup" aria-labelledby="ss-fonts-l"></div>
      <div id="ss-local" class="ss-local" hidden>
        <button type="button" class="btn btn-sm" data-local-pick>Font của máy…</button>
        <label class="ss-local-sel" hidden><span class="sr-only">Chọn font của máy</span><select class="select" data-local-select></select></label>
      </div>
    </div>
    ${rangeRow('weight')} ${rangeRow('size')} ${rangeRow('line')} ${rangeRow('letter')} ${rangeRow('word')}`;
}

function layoutTab(): SafeHtml {
  return html`${preview()}
    ${segRow('align', 'Căn lề', [
      ['left', 'Trái'],
      ['justify', 'Đều hai bên'],
    ])}
    ${rangeRow('indent')} ${rangeRow('paraGap')} ${rangeRow('margin')} ${rangeRow('width')}
    ${segRow('readMode', 'Kiểu đọc', [
      ['scroll', 'Cuộn dọc'],
      ['page', 'Lật trang'],
    ])}
    ${checkRow('tapZones', 'Chạm hai bên màn hình để lật trang')}`;
}

function voiceTab(): SafeHtml {
  return html`<div class="ss-row" id="ss-engine-row">
      <div class="ss-label" id="ss-engine-l">Bộ đọc</div>
      <div class="ss-seg" role="radiogroup" aria-labelledby="ss-engine-l" id="ss-engine"></div>
      <p class="hint" id="ss-engine-note" role="status"></p>
    </div>
    <div class="ss-row">
      <label class="ss-label" for="ss-voice">Giọng</label>
      <div class="ss-voice-line">
        <select id="ss-voice" class="select ss-voice" aria-describedby="ss-voice-note"></select>
        <button type="button" class="btn" id="ss-voice-test">${icon('play')}<span>Nghe thử</span></button>
      </div>
      <p class="hint" id="ss-voice-note" role="status"></p>
    </div>
    ${rangeRow('rate')} ${rangeRow('pitch')}
    <div class="ss-checks">
      ${checkRow('autoNext', 'Tự chuyển chương khi nghe hết')} ${checkRow('follow', 'Tự cuộn theo đoạn đang đọc')} ${checkRow('readTitle', 'Đọc tiêu đề chương')}
      ${checkRow('ttsChapterCue', 'Báo “Hết chương” trước khi qua chương mới')} ${checkRow('ttsClean', 'Lọc ký tự lạ trước khi đọc')} ${checkRow('keepAwake', 'Giữ màn hình sáng khi nghe')}
    </div>
    <p class="hint">Mẹo: nhấp đúp vào một đoạn để nghe từ đó. Phím tắt: Space phát/dừng, ←/→ chương trước/sau, J/K đoạn sau/trước.</p>`;
}

// ---------------------------------------------------------------- font picker

const GROUPS: [FontInfo['group'], string][] = [
  ['serif', 'Có chân'],
  ['sans', 'Không chân'],
  ['system', 'Font máy'],
];

function fontButton(f: FontInfo): SafeHtml {
  return html`<button type="button" class="ss-font" role="radio" aria-checked="${S.font === f.id ? 'true' : 'false'}" data-font="${f.id}"><span class="ss-font-name">${f.label}</span><span class="ss-font-sample" lang="vi">${f.sample}</span></button>`;
}

async function paintFonts(root: HTMLElement): Promise<void> {
  const box = root.querySelector<HTMLElement>('#ss-fonts');
  if (!box) return;
  const list = await fonts.available();
  if (!box.isConnected) return;
  const known = list.some((f) => f.id === S.font) ? list : list.concat(fonts.find(S.font) || []);
  render(
    box,
    html`${GROUPS.map(([g, label]) => {
      const items = known.filter((f) => f.group === g);
      return items.length ? html`<div class="ss-font-group"><div class="ss-font-head">${label}</div><div class="ss-font-grid">${items.map(fontButton)}</div></div>` : '';
    })}`,
  );
  for (const b of box.querySelectorAll<HTMLButtonElement>('[data-font]')) b.style.setProperty('--ff', fonts.cssStack(b.dataset.font as string));
  const local = root.querySelector<HTMLElement>('#ss-local');
  if (local) local.hidden = !fonts.canQueryLocal();
}

function markFonts(root: ParentNode): void {
  for (const b of root.querySelectorAll<HTMLButtonElement>('[data-font]')) b.setAttribute('aria-checked', String(b.dataset.font === S.font));
}

function markTypo(root: ParentNode): void {
  const id = matchPreset(S);
  for (const b of root.querySelectorAll<HTMLButtonElement>('[data-typo-id]')) b.setAttribute('aria-checked', String(b.dataset.typoId === id));
}

function paintSwatchColours(root: ParentNode): void {
  for (const c of root.querySelectorAll<HTMLElement>('.ss-sw-chip')) {
    if (c.dataset.bg) c.style.setProperty('--sw-bg', c.dataset.bg);
    if (c.dataset.fg) c.style.setProperty('--sw-fg', c.dataset.fg);
  }
}

function noteActive(root: ParentNode): void {
  const el = root.querySelector<HTMLElement>('#ss-active-note');
  if (!el) return;
  const p = activePreset();
  el.textContent = isDark() ? `Đang ở chế độ tối: màu nền ban đêm “${p.label}” được dùng khi đọc.` : `Màu nền ban ngày “${p.label}” được dùng khi đọc (chế độ Sáng và Giấy).`;
}

// ---------------------------------------------------------------- the sheet

function open(tab?: SettingsTab): void {
  if (dlg && !dlg.closed) {
    if (tab) select(dlg.el, tab, true);
    return;
  }
  const first: SettingsTab = tab && TABS.some((t) => t.id === tab) ? tab : lastTab;
  const d = openDialog({
    title: 'Cài đặt',
    variant: 'drawer',
    className: 'ss-panel',
    onClose: () => {
      unbind();
      offChange();
      unmountVoice();
      unmountSource();
      dlg = null;
    },
    body: html`<div class="ss-top">
        <div class="ss-quick" role="group" aria-label="Chỉnh nhanh">
          <div class="ss-size" role="group" aria-label="Cỡ chữ khi đọc">
            <button type="button" class="btn btn-icon-only ss-step" data-step="-1" aria-label="Giảm cỡ chữ">−</button>
            <output class="ss-size-out" data-out="size" aria-live="polite">${S.size} px</output>
            <button type="button" class="btn btn-icon-only ss-step" data-step="1" aria-label="Tăng cỡ chữ">+</button>
          </div>
          ${segRow('theme', 'Giao diện', THEME_OPTIONS, { compact: true, hideLabel: true })}
          ${segRow(
            'readMode',
            'Kiểu đọc',
            [
              ['scroll', 'Cuộn'],
              ['page', 'Lật trang'],
            ],
            { compact: true, hideLabel: true },
          )}
        </div>
        <div class="ss-tabs" role="tablist" aria-label="Nhóm cài đặt">
          ${TABS.map((t) => html`<button type="button" class="ss-tab" role="tab" id="ss-tab-${t.id}" aria-controls="ss-pane-${t.id}" aria-selected="false" tabindex="-1" data-tab="${t.id}">${t.label}</button>`)}
        </div>
      </div>
      <div class="ss-panes">
        <section class="ss-pane" role="tabpanel" id="ss-pane-theme" aria-labelledby="ss-tab-theme" tabindex="0" hidden>${themeTab()}</section>
        <section class="ss-pane" role="tabpanel" id="ss-pane-font" aria-labelledby="ss-tab-font" tabindex="0" hidden>${fontTab()}</section>
        <section class="ss-pane" role="tabpanel" id="ss-pane-layout" aria-labelledby="ss-tab-layout" tabindex="0" hidden>${layoutTab()}</section>
        <section class="ss-pane" role="tabpanel" id="ss-pane-voice" aria-labelledby="ss-tab-voice" tabindex="0" hidden>${voiceTab()}</section>
        <section class="ss-pane" role="tabpanel" id="ss-pane-source" aria-labelledby="ss-tab-source" tabindex="0" hidden></section>
      </div>`,
    footer: html`<button type="button" class="btn" data-reset>Đặt lại mặc định</button><button type="button" class="btn btn-primary" data-close>Xong</button>`,
    initialFocus: `#ss-tab-${first}`,
  });
  dlg = d;
  const root = d.el;
  lastTab = first;
  const unbind = bindControls(root);
  const offChange = onChange(() => {
    markFonts(root);
    markTypo(root);
    paintSwatches(root);
    noteActive(root);
  });
  paintSwatchColours(root);
  void paintFonts(root).then(() => markFonts(root));
  markTypo(root);
  noteActive(root);
  syncControls(root);

  let unmountVoice = (): void => {};
  let unmountSource = (): void => {};
  let voiceMounted = false;
  let sourceMounted = false;
  root.addEventListener('settings-tab', (e) => {
    const id = (e as CustomEvent<SettingsTab>).detail;
    lastTab = id;
    if (id === 'voice' && !voiceMounted) {
      voiceMounted = true;
      unmountVoice = mountVoice(root);
    }
    if (id === 'source' && !sourceMounted) {
      sourceMounted = true;
      unmountSource = mountSource(root.querySelector<HTMLElement>('#ss-pane-source') as HTMLElement);
    }
  });

  root.addEventListener('click', (e) => {
    const t = e.target as Element;
    const tabBtn = t.closest<HTMLElement>('[data-tab]');
    if (tabBtn) return select(root, tabBtn.dataset.tab as SettingsTab, false);
    const step = t.closest<HTMLElement>('[data-step]');
    if (step) {
      const [min, max] = RANGE.size;
      const v = Math.min(max, Math.max(min, S.size + Number(step.dataset.step)));
      set('size', v);
      return;
    }
    const sw = t.closest<HTMLElement>('.ss-sw[data-preset]');
    if (sw) {
      const key = (sw.closest('[data-swatches]') as HTMLElement).dataset.swatches as 'dayPreset' | 'nightPreset';
      set(key, sw.dataset.preset);
      return;
    }
    const ff = t.closest<HTMLElement>('[data-font]');
    if (ff) {
      set('font', ff.dataset.font);
      return;
    }
    const ty = t.closest<HTMLElement>('[data-typo-id]');
    if (ty) {
      const p = TYPO_PRESETS.find((x) => x.id === ty.dataset.typoId);
      if (p) patch(presetValues(p));
      return;
    }
    if (t.closest('[data-local-pick]')) void pickLocal(root);
    if (t.closest('[data-reset]')) void resetAll();
  });
  root.addEventListener('keydown', (e) => {
    const tab = (e.target as Element).closest<HTMLElement>('[role="tab"]');
    if (tab) tabKeys(root, e, tab);
    else radioKeys(e);
  });
  root.querySelector<HTMLSelectElement>('[data-local-select]')?.addEventListener('change', (e) => {
    const fam = (e.target as HTMLSelectElement).value;
    if (fam) set('font', fonts.addLocal(fam));
    void paintFonts(root).then(() => markFonts(root));
  });
  select(root, first, false, false);
}

/** Shows a tab. Moves focus to its button only when the user asked for it. */
function select(root: HTMLElement, id: SettingsTab, focus: boolean, announce = true): void {
  for (const b of root.querySelectorAll<HTMLElement>('[data-tab]')) {
    const on = b.dataset.tab === id;
    b.setAttribute('aria-selected', String(on));
    b.tabIndex = on ? 0 : -1;
    if (on && (focus || announce)) b.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }
  for (const p of root.querySelectorAll<HTMLElement>('.ss-pane')) p.hidden = p.id !== `ss-pane-${id}`;
  if (focus) root.querySelector<HTMLElement>(`#ss-tab-${id}`)?.focus();
  root.querySelector('.dialog-body')?.scrollTo?.({ top: 0 });
  root.dispatchEvent(new CustomEvent<SettingsTab>('settings-tab', { detail: id }));
}

/** Arrow / Home / End move between tabs (automatic activation). */
function tabKeys(root: HTMLElement, e: KeyboardEvent, tab: HTMLElement): void {
  const ids = TABS.map((t) => t.id);
  const i = ids.indexOf(tab.dataset.tab as SettingsTab);
  let n = i;
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = (i + 1) % ids.length;
  else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = (i - 1 + ids.length) % ids.length;
  else if (e.key === 'Home') n = 0;
  else if (e.key === 'End') n = ids.length - 1;
  else return;
  e.preventDefault();
  select(root, ids[n] as SettingsTab, true);
}

/** Arrow keys inside a role="radio" button group (fonts, swatches, presets) move the selection. */
function radioKeys(e: KeyboardEvent): void {
  const b = (e.target as Element).closest<HTMLElement>('button[role="radio"]');
  if (!b || !['ArrowRight', 'ArrowLeft', 'ArrowDown', 'ArrowUp'].includes(e.key)) return;
  const group = b.closest<HTMLElement>('[role="radiogroup"]');
  const items = [...(group?.querySelectorAll<HTMLElement>('button[role="radio"]') ?? [])];
  const i = items.indexOf(b);
  const n = items[(i + (e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length];
  if (n) {
    e.preventDefault();
    n.focus();
  }
}

async function pickLocal(root: HTMLElement): Promise<void> {
  const sel = root.querySelector<HTMLSelectElement>('[data-local-select]');
  const wrap = root.querySelector<HTMLElement>('.ss-local-sel');
  if (!sel || !wrap) return;
  try {
    const list = await fonts.queryLocal();
    if (!list.length) return void toast('Không đọc được danh sách font của máy.');
    render(sel, html`<option value="">— Chọn font của máy (${list.length}) —</option>${list.map((f) => html`<option value="${f.family}">${f.family}</option>`)}`);
    wrap.hidden = false;
    sel.focus();
  } catch {
    toast({ message: 'Trình duyệt không cho đọc danh sách font của máy.', kind: 'error' });
  }
}

async function resetAll(): Promise<void> {
  const ok = await confirmDialog({ title: 'Đặt lại mặc định?', message: 'Đưa toàn bộ cài đặt đọc và nghe về mặc định. Lịch sử đọc, đánh dấu và nguồn truyện được giữ nguyên.', confirmLabel: 'Đặt lại', cancelLabel: 'Giữ nguyên' });
  if (!ok) return;
  reset();
  if (dlg && !dlg.closed) {
    syncControls(dlg.el);
    markFonts(dlg.el);
    markTypo(dlg.el);
    paintSwatches(dlg.el);
  }
  toast({ message: 'Đã đặt lại cài đặt mặc định.', kind: 'ok' });
}

export const settingsPanel: SettingsPanelApi = {
  open,
  close(): void {
    dlg?.close();
    dlg = null;
  },
  isOpen: () => !!dlg && !dlg.closed,
};
