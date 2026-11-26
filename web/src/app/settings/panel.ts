/**
 * Settings sheet (stage W3): a modal bottom sheet on phones (the reading text stays visible above it) and a side
 * panel on wide screens. A quick row (text size, theme) sits above a vertical menu of setting groups (Giao diện, Chữ,
 * Bố cục, Giọng đọc, Nguồn dữ liệu, ...). Each row shows a short summary and a chevron; clicking it expands the group's
 * controls right below it (accordion: one open at a time, click again to collapse). Every change is written straight through `core/settings`, so the page behind the
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
import { ACCENTS, THEMES } from '../core/themes';
import { bindControls, checkRow, rangeRow, segRow, syncControls } from './controls';
import { matchPreset, presetValues, TYPO_PRESETS } from './presets';
import { auth } from '../core/auth';
import { mountAccount } from './account';
import { mountApp } from './app';
import { appUpdate } from '../core/app-update';
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
  { id: 'account', label: 'Tài khoản' },
  { id: 'app', label: 'Ứng dụng' },
];

/** The tabs to show: "Tài khoản" only when the server offers Google sign-in (or a session exists); "Ứng dụng" only in the Android app. */
export const visibleTabs = (): TabDef[] =>
  TABS.filter((t) => (t.id !== 'account' || auth.available() || auth.signedIn()) && (t.id !== 'app' || appUpdate.available()));

/** Short current-value summary shown on a group's menu row (empty when there is nothing cheap to say). */
export function groupSummary(id: SettingsTab): string {
  switch (id) {
    case 'theme':
      return S.theme === 'auto' ? 'Tự động' : (THEMES.find((t) => t.id === S.theme)?.label ?? '');
    case 'font':
      return [fonts.find(S.font)?.label, `${S.size} px`].filter(Boolean).join(' · ');
    case 'layout':
      return S.readMode === 'page' ? 'Lật trang' : 'Cuộn dọc';
    case 'voice':
      return `Tốc độ ${Number(S.rate.toFixed(2))}×`;
    default:
      return '';
  }
}

/** Quick row: the three everyday choices; the Giao diện tab has every theme. */
const THEME_OPTIONS: ['light' | 'dark' | 'auto', string][] = [
  ['auto', 'Tự động'],
  ['light', 'Sáng'],
  ['dark', 'Tối'],
];

/** One radio tile per entry of the theme table (+ "Tự động" = follow the system), previewed with its own colours. */
function themeGrid(): SafeHtml {
  const tile = (v: string, label: string, style: string, extra = ''): SafeHtml =>
    html`<label class="ss-theme ${extra}"><input type="radio" name="ss-theme" value="${v}" ${S.theme === v ? html`checked` : ''} /><span class="ss-theme-chip" data-chip="${style}" aria-hidden="true"><i></i><b>Aa</b></span><span class="ss-theme-name">${label}</span></label>`;
  return html`<div class="ss-row">
    <div class="ss-label" id="ss-theme-l">Giao diện</div>
    <div class="ss-themes" role="radiogroup" aria-labelledby="ss-theme-l" data-seg="theme">
      ${tile('auto', 'Tự động', 'auto', 'is-auto')} ${THEMES.map((t) => tile(t.id, t.label, `${t.bg}|${t.surface}|${t.text}|${t.accent}`))}
    </div>
    <p class="hint">Tự động đổi giữa Sáng và Tối theo thiết bị.</p>
  </div>
  <div class="ss-row">
    <div class="ss-label" id="ss-accent-l">Màu nhấn</div>
    <div class="ss-accents" role="radiogroup" aria-labelledby="ss-accent-l" data-seg="accent">
      ${ACCENTS.map((a) => html`<label class="ss-accent" title="${a.label}"><input type="radio" name="ss-accent" value="${a.id}" ${S.accent === a.id ? html`checked` : ''} /><span class="ss-accent-dot" data-color="${a.color}" data-def="${a.id === 'default' ? '1' : ''}" aria-hidden="true"></span><span class="sr-only">${a.label}</span></label>`)}
    </div>
  </div>`;
}

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
  return html`${themeGrid()} ${preview()} ${swatches('day')} ${swatches('night')}
    <p class="hint ss-active-note" id="ss-active-note"></p>
    ${rangeRow('brightness')}`;
}

function typoPresets(): SafeHtml {
  return html`<div class="ss-row">
    <div class="ss-label" id="ss-typo-l">Kiểu chữ có sẵn</div>
    <select id="ss-typo" class="select ss-dd" aria-labelledby="ss-typo-l" data-typo-select>
      <option value="">Tuỳ chỉnh</option>
      ${TYPO_PRESETS.map((p) => html`<option value="${p.id}">${p.label} — ${p.hint}</option>`)}
    </select>
  </div>`;
}

function fontTab(): SafeHtml {
  return html`${preview()} ${typoPresets()}
    <div class="ss-row">
      <div class="ss-label" id="ss-fonts-l">Phông chữ</div>
      <select id="ss-fonts" class="select ss-dd" aria-labelledby="ss-fonts-l" data-font-select></select>
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
    ${checkRow('tapZones', 'Chạm hai bên màn hình để lật trang')}
    ${checkRow('shortcuts', 'Phím tắt một phím (M, B, A, Space, ?)', 'Tắt nếu dùng giọng nói hoặc hay bấm nhầm. Phím mũi tên vẫn dùng được.')}`;
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
    <div class="ss-row" id="ss-piper-row" hidden>
      <div class="ss-label">Giọng Piper trên máy</div>
      <div class="ss-voice-line">
        <button type="button" class="btn" id="ss-piper-dl">Tải giọng này</button>
        <button type="button" class="btn" id="ss-piper-rm" hidden>Xoá khỏi máy</button>
      </div>
      <p class="hint" id="ss-piper-note" role="status"></p>
    </div>
    ${rangeRow('rate')} ${rangeRow('pitch')}
    <div class="ss-checks">
      ${checkRow('autoNext', 'Tự chuyển chương khi nghe hết')} ${checkRow('follow', 'Tự cuộn theo đoạn đang đọc')} ${checkRow('autoOpenReader', 'Mở trang đọc khi bắt đầu nghe')} ${checkRow('readTitle', 'Đọc tiêu đề chương')}
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

function fontOption(f: FontInfo): SafeHtml {
  return html`<option value="${f.id}" data-font="${f.id}" ${S.font === f.id ? html`selected` : ''}>${f.label}</option>`;
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
      return items.length ? html`<optgroup label="${label}">${items.map(fontOption)}</optgroup>` : '';
    })}`,
  );
  for (const o of box.querySelectorAll<HTMLOptionElement>('option[data-font]')) o.style.fontFamily = fonts.cssStack(o.dataset.font as string);
  const local = root.querySelector<HTMLElement>('#ss-local');
  if (local) local.hidden = !fonts.canQueryLocal();
}

function markFonts(root: ParentNode): void {
  const sel = root.querySelector<HTMLSelectElement>('#ss-fonts');
  if (sel) sel.value = S.font;
}

function markTypo(root: ParentNode): void {
  const sel = root.querySelector<HTMLSelectElement>('#ss-typo');
  if (sel) sel.value = matchPreset(S) ?? '';
}

function paintSwatchColours(root: ParentNode): void {
  for (const c of root.querySelectorAll<HTMLElement>('.ss-sw-chip')) {
    if (c.dataset.bg) c.style.setProperty('--sw-bg', c.dataset.bg);
    if (c.dataset.fg) c.style.setProperty('--sw-fg', c.dataset.fg);
  }
}

function paintThemeChips(root: ParentNode): void {
  for (const c of root.querySelectorAll<HTMLElement>('.ss-theme-chip')) {
    const d = c.dataset.chip || '';
    if (d === 'auto') continue;
    const [bg, surface, text, accent] = d.split('|');
    c.style.setProperty('--c-bg', bg || '');
    c.style.setProperty('--c-surface', surface || '');
    c.style.setProperty('--c-text', text || '');
    c.style.setProperty('--c-accent', accent || '');
  }
  for (const d of root.querySelectorAll<HTMLElement>('.ss-accent-dot')) if (d.dataset.color && !d.dataset.def) d.style.setProperty('--dot', d.dataset.color);
}

function noteActive(root: ParentNode): void {
  const el = root.querySelector<HTMLElement>('#ss-active-note');
  if (!el) return;
  const p = activePreset();
  el.textContent = isDark() ? `Đang ở chế độ tối: màu nền ban đêm “${p.label}” được dùng khi đọc.` : `Màu nền ban ngày “${p.label}” được dùng khi đọc (các giao diện sáng).`;
}

// ---------------------------------------------------------------- the sheet

function open(tab?: SettingsTab): void {
  if (dlg && !dlg.closed) {
    if (tab) select(dlg.el, tab, true);
    return;
  }
  const shown = visibleTabs();
  const first: SettingsTab = tab && shown.some((t) => t.id === tab) ? tab : shown.some((t) => t.id === lastTab) ? lastTab : 'theme';
  const d = openDialog({
    title: 'Cài đặt',
    variant: 'drawer',
    className: 'ss-panel',
    onClose: () => {
      unbind();
      offChange();
      unmountVoice();
      unmountSource();
      unmountAccount();
      unmountApp();
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
        </div>
      </div>
      <div class="ss-menu" role="group" aria-label="Nhóm cài đặt">
        ${shown.map(
          (t) => html`<div class="ss-group" data-group="${t.id}">
            <h3 class="ss-group-h"><button type="button" class="ss-group-btn" id="ss-tab-${t.id}" aria-expanded="false" aria-controls="ss-pane-${t.id}" data-tab="${t.id}"><span class="ss-g-name">${t.label}</span><span class="ss-g-sum" data-sum="${t.id}">${groupSummary(t.id)}</span><span class="ss-g-chev" aria-hidden="true">${icon('down')}</span></button></h3>
            <section class="ss-pane" role="region" id="ss-pane-${t.id}" aria-labelledby="ss-tab-${t.id}" hidden>${t.id === 'theme' ? themeTab() : t.id === 'font' ? fontTab() : t.id === 'layout' ? layoutTab() : t.id === 'voice' ? voiceTab() : ''}</section>
          </div>`,
        )}
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
    paintSummaries(root);
  });
  paintSwatchColours(root);
  paintThemeChips(root);
  void paintFonts(root).then(() => markFonts(root));
  markTypo(root);
  noteActive(root);
  syncControls(root);

  let unmountVoice = (): void => {};
  let unmountSource = (): void => {};
  let voiceMounted = false;
  let sourceMounted = false;
  let unmountAccount = (): void => {};
  let accountMounted = false;
  let unmountApp = (): void => {};
  let appMounted = false;
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
    const accountPane = root.querySelector<HTMLElement>('#ss-pane-account');
    if (id === 'account' && accountPane && !accountMounted) {
      accountMounted = true;
      unmountAccount = mountAccount(accountPane);
    }
    const appPane = root.querySelector<HTMLElement>('#ss-pane-app');
    if (id === 'app' && appPane && !appMounted) {
      appMounted = true;
      unmountApp = mountApp(appPane);
    }
  });

  root.addEventListener('click', (e) => {
    const t = e.target as Element;
    const tabBtn = t.closest<HTMLElement>('[data-tab]');
    if (tabBtn) return toggle(root, tabBtn.dataset.tab as SettingsTab);
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
    if (t.closest('[data-local-pick]')) void pickLocal(root);
    if (t.closest('[data-reset]')) void resetAll();
  });
  root.addEventListener('keydown', (e) => {
    const tab = (e.target as Element).closest<HTMLElement>('.ss-group-btn');
    if (tab) tabKeys(root, e, tab);
    else radioKeys(e);
  });
  root.addEventListener('change', (e) => {
    const t = e.target as HTMLElement;
    if (t.matches('[data-font-select]')) set('font', (t as HTMLSelectElement).value);
    else if (t.matches('[data-typo-select]')) {
      const p = TYPO_PRESETS.find((x) => x.id === (t as HTMLSelectElement).value);
      if (p) patch(presetValues(p));
    }
  });
  root.querySelector<HTMLSelectElement>('[data-local-select]')?.addEventListener('change', (e) => {
    const fam = (e.target as HTMLSelectElement).value;
    if (fam) set('font', fonts.addLocal(fam));
    void paintFonts(root).then(() => markFonts(root));
  });
  select(root, first, false, false);
  if (tab || first !== 'theme') requestAnimationFrame(() => root.querySelector<HTMLElement>(`#ss-tab-${first}`) && reveal(root.querySelector<HTMLElement>(`#ss-tab-${first}`) as HTMLElement, root.querySelector<HTMLElement>(`#ss-pane-${first}`)));
}

/** Refreshes the value summaries on the menu rows. */
function paintSummaries(root: ParentNode): void {
  for (const el of root.querySelectorAll<HTMLElement>('[data-sum]')) el.textContent = groupSummary(el.dataset.sum as SettingsTab);
}

/** A click on a row: expands it (closing the others) or collapses it when it is already open. */
function toggle(root: HTMLElement, id: SettingsTab): void {
  const btn = root.querySelector<HTMLElement>(`#ss-tab-${id}`);
  if (btn?.getAttribute('aria-expanded') === 'true') collapse(root);
  else select(root, id, false, true);
}

function collapse(root: HTMLElement): void {
  for (const b of root.querySelectorAll<HTMLElement>('[data-tab]')) b.setAttribute('aria-expanded', 'false');
  for (const p of root.querySelectorAll<HTMLElement>('.ss-pane')) p.hidden = true;
  root.querySelectorAll('.ss-group').forEach((g) => g.classList.remove('is-open'));
}

/** Expands a group (accordion) and scrolls its row into view. Moves focus to its row only when asked to. */
function select(root: HTMLElement, id: SettingsTab, focus: boolean, scroll = true): void {
  collapse(root);
  const btn = root.querySelector<HTMLElement>(`#ss-tab-${id}`);
  btn?.setAttribute('aria-expanded', 'true');
  const pane = root.querySelector<HTMLElement>(`#ss-pane-${id}`);
  if (pane) pane.hidden = false;
  btn?.closest('.ss-group')?.classList.add('is-open');
  if (focus) btn?.focus();
  root.dispatchEvent(new CustomEvent<SettingsTab>('settings-tab', { detail: id }));
  if (scroll && btn) reveal(btn, pane);
}

/** Scrolls the sheet body just enough that the opened group's controls are visible (its row stays on screen). */
function reveal(btn: HTMLElement, pane: HTMLElement | null): void {
  const body = btn.closest<HTMLElement>('.dialog-body');
  if (!body) return void btn.scrollIntoView?.({ block: 'nearest' });
  const view = body.getBoundingClientRect();
  const head = btn.getBoundingClientRect();
  const end = (pane && !pane.hidden ? pane.getBoundingClientRect().bottom : head.bottom) - view.bottom;
  const toHead = head.top - view.top;
  const dy = end > 0 ? Math.min(end, Math.max(toHead, 0)) : Math.min(toHead, 0);
  if (dy) body.scrollBy({ top: dy });
}

/** Arrow Up/Down, Home and End move between the menu rows (no activation; Enter/Space toggles). */
function tabKeys(root: HTMLElement, e: KeyboardEvent, tab: HTMLElement): void {
  const btns = [...root.querySelectorAll<HTMLElement>('.ss-group-btn')];
  const i = btns.indexOf(tab);
  let n = i;
  if (e.key === 'ArrowDown') n = (i + 1) % btns.length;
  else if (e.key === 'ArrowUp') n = (i - 1 + btns.length) % btns.length;
  else if (e.key === 'Home') n = 0;
  else if (e.key === 'End') n = btns.length - 1;
  else return;
  e.preventDefault();
  btns[n]?.focus();
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
