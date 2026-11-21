/**
 * The player's dock in `#player-dock`: one row on every screen. Wide screens show every control in the row;
 * under 720 px the row holds the title, play / pause, "expand" and close, and the rest lives in a bottom sheet.
 * The dock is built once per listening session and then updated in place. It keeps `--player-h` on <html>
 * equal to its real height (0px when hidden) and owns the player's global keys.
 */
import { html, join, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { href } from '../core/router';
import { S, settings } from '../core/settings';
import { openDialog, type DialogHandle } from '../core/ui';
import { xicon } from '../reader/icons';
import { createHighlighter, type Highlighter } from '../reader/highlight';
import { keyOf, typingTarget } from '../reader/keys';
import { openSettings } from '../shell';
import { ENGINE_LABEL } from './engines';
import type { Player } from './index';
import { onMark } from './mark';
import { isPipSupported, togglePip } from './pip';
import { RATES, SLEEP_MINUTES, sleepLabel } from './text';

let player: Player;
let host: HTMLElement | null = null;
let built = false;
let sheet: DialogHandle | null = null;
let tick: ReturnType<typeof setInterval> | undefined;
let observer: ResizeObserver | null = null;
/** "Now reading" panel of the open sheet: the paragraphs around the voice and the sentence highlighter. */
let now: { key: string; hl: Highlighter | null; off: () => void; at: string } | null = null;

const rateLabel = (r: number): string => `${String(Math.round(r * 100) / 100).replace('.', ',')}×`;

function rateOptions(): SafeHtml {
  const list = RATES.includes(S.rate) ? [...RATES] : [...RATES, S.rate].sort((a, b) => a - b);
  return join(list.map((r) => html`<option value="${r}">${rateLabel(r)}</option>`));
}

function sleepOptions(): SafeHtml {
  return html`<option value="0">Không hẹn giờ</option>${SLEEP_MINUTES.map((m) => html`<option value="${m}">${m} phút</option>`)}
    <option value="-1">Hết chương</option>`;
}

function transport(big: boolean): SafeHtml {
  const b = big ? 'icon-btn pl-big' : 'icon-btn pl-wide';
  return html`<button type="button" class="${b}" data-pl="prevch" aria-label="Nghe chương trước" title="Chương trước (Shift + ←)">${xicon('chapterPrev')}</button>
    <button type="button" class="${b}" data-pl="back" aria-label="Lùi một đoạn" title="Lùi một đoạn (K)">${xicon('stepBack')}</button>
    <button type="button" class="pl-play" data-pl="toggle" aria-label="Tạm dừng">
      <span class="pl-play-pause">${icon('pause')}</span><span class="pl-play-play">${icon('play')}</span>
    </button>
    <button type="button" class="${b}" data-pl="fwd" aria-label="Tới một đoạn" title="Tới một đoạn (J)">${xicon('stepNext')}</button>
    <button type="button" class="${b}" data-pl="nextch" aria-label="Nghe chương sau" title="Chương sau (Shift + →)">${xicon('chapterNext')}</button>`;
}

function dockMarkup(): SafeHtml {
  return html`<div class="pl-dock" role="region" aria-label="Trình nghe truyện">
    <div class="pl-line" aria-hidden="true"><span class="pl-line-fill" data-pl-fill></span></div>
    <div class="pl-row">
      <a class="pl-info" data-pl-link href="#/" title="Mở chương đang nghe">
        <span class="pl-title" data-pl-title></span>
        <span class="pl-sub" data-pl-sub></span>
      </a>
      <div class="pl-ctl">${transport(false)}</div>
      <div class="pl-opts pl-wide">
        <label class="pl-opt" title="Tốc độ đọc"><span class="sr-only">Tốc độ đọc</span><select class="select pl-select" data-pl="rate">${rateOptions()}</select></label>
        <label class="pl-opt" title="Hẹn giờ tắt"
          >${xicon('timer')}<span class="sr-only">Hẹn giờ tắt</span><select class="select pl-select" data-pl="sleep">${sleepOptions()}</select></label
        >
        <span class="pl-left" data-pl-left></span>
      </div>
      <button type="button" class="icon-btn pl-narrow" data-pl="expand" aria-label="Mở bảng điều khiển nghe" aria-haspopup="dialog">${xicon('expand')}</button>
      <button type="button" class="icon-btn" data-pl="close" aria-label="Dừng nghe và đóng" title="Dừng nghe và đóng">${icon('close')}</button>
    </div>
  </div>`;
}

function sheetMarkup(): SafeHtml {
  return html`<div class="pl-sheet">
    <p class="pl-sheet-title" data-pl-title></p>
    <p class="pl-sheet-sub" data-pl-sub></p>
    <div class="pl-line pl-sheet-line" aria-hidden="true"><span class="pl-line-fill" data-pl-fill></span></div>
    <div class="pl-sheet-ctl">${transport(true)}</div>
    <div class="pl-now" data-pl-now aria-live="off"></div>
    <div class="pl-field">
      <label for="pl-sheet-rate">Tốc độ đọc</label>
      <select id="pl-sheet-rate" class="select" data-pl="rate">${rateOptions()}</select>
    </div>
    <div class="pl-field">
      <label for="pl-sheet-sleep">Hẹn giờ tắt <span class="pl-left" data-pl-left></span></label>
      <select id="pl-sheet-sleep" class="select" data-pl="sleep">${sleepOptions()}</select>
    </div>
    <div class="pl-sheet-links">
      <a class="btn" data-pl-link href="#/">${icon('book')}<span>Mở chương đang nghe</span></a>
      <button type="button" class="btn" data-pl="voice">${icon('settings')}<span>Giọng đọc</span></button>
      ${isPipSupported() ? html`<button type="button" class="btn" data-pl="pip">${icon('book')}<span>Cửa sổ nhỏ</span></button>` : ''}
    </div>
  </div>`;
}

/** Writes the player's state into a dock or sheet tree. */
function sync(root: ParentNode): void {
  const st = player.getState();
  const inf = player.info();
  const playing = st.status === 'playing' || st.status === 'loading';
  const title = st.chapterTitle || (st.status === 'loading' ? 'Đang tải…' : '');
  let sub = st.storyName || '';
  if (st.status === 'error') sub = st.error || 'Không đọc được';
  else if (st.status === 'loading' && !inf.chunks) sub = [sub, 'đang tải'].filter(Boolean).join(' · ');
  else if (inf.chunks) sub = [sub, `đoạn ${inf.chunk + 1}/${inf.chunks}`, inf.fallback && st.engine ? ENGINE_LABEL[st.engine].toLowerCase() : ''].filter(Boolean).join(' · ');
  const text = (sel: string, v: string): void => {
    for (const el of root.querySelectorAll<HTMLElement>(sel)) if (el.textContent !== v) el.textContent = v;
  };
  text('[data-pl-title]', title);
  text('[data-pl-sub]', sub);
  const link = st.source && st.key ? href.read(st.source, st.key, st.idx ?? 0) : '#/';
  for (const a of root.querySelectorAll<HTMLAnchorElement>('[data-pl-link]')) if (a.getAttribute('href') !== link) a.setAttribute('href', link);
  for (const b of root.querySelectorAll<HTMLElement>('[data-pl="toggle"]')) {
    b.classList.toggle('is-playing', playing);
    b.classList.toggle('is-loading', st.status === 'loading');
    b.classList.toggle('is-error', st.status === 'error');
    const label = st.status === 'loading' ? 'Đang tải — nhấn để tạm dừng' : playing ? 'Tạm dừng' : st.status === 'error' ? 'Thử lại' : 'Nghe tiếp';
    if (b.getAttribute('aria-label') !== label) b.setAttribute('aria-label', label);
    b.title = `${label} (Phím cách)`;
  }
  const frac = inf.chunks ? Math.min(1, (inf.chunk + (st.status === 'idle' ? 0 : 1)) / inf.chunks) : 0;
  for (const f of root.querySelectorAll<HTMLElement>('[data-pl-fill]')) f.style.transform = `scaleX(${frac.toFixed(4)})`;
  const idx = st.idx ?? 0;
  for (const b of root.querySelectorAll<HTMLButtonElement>('[data-pl="prevch"]')) b.disabled = idx <= 0;
  for (const b of root.querySelectorAll<HTMLButtonElement>('[data-pl="nextch"]')) b.disabled = inf.total > 0 && idx >= inf.total - 1;
  for (const b of root.querySelectorAll<HTMLButtonElement>('[data-pl="back"], [data-pl="fwd"]')) b.disabled = !inf.chunks;
  for (const sel of root.querySelectorAll<HTMLSelectElement>('select[data-pl="rate"]')) {
    if (!Array.from(sel.options).some((o) => Number(o.value) === S.rate)) render(sel, rateOptions());
    if (document.activeElement !== sel) sel.value = String(S.rate);
  }
  // the selector always mirrors the timer: back to "off" when it fired, was cleared or the player closed
  for (const sel of root.querySelectorAll<HTMLSelectElement>('select[data-pl="sleep"]')) sel.value = String(inf.sleep);
  const left = inf.sleep > 0 ? `còn ${sleepLabel(inf.sleepAt - Date.now())}` : inf.sleep === -1 ? 'khi hết chương' : '';
  text('[data-pl-left]', left);
}

/** Shows the paragraphs around the voice in the sheet and marks the sentence being spoken. */
function syncNow(): void {
  const box = sheet && !sheet.closed ? sheet.body.querySelector<HTMLElement>('[data-pl-now]') : null;
  if (!box || !now) return;
  const n = player.getNowReading();
  if (!n) {
    now.hl?.clear();
    now.hl = null;
    now.key = '';
    box.replaceChildren();
    return;
  }
  const lo = Math.max(0, n.para - 1);
  const hi = Math.min(n.paragraphs.length - 1, Math.max(0, n.para) + 2);
  const key = `${n.source}|${n.key}|${n.idx}|${lo}`;
  if (now.key !== key || !now.hl) {
    const els = new Map<number, HTMLElement>();
    for (let i = lo; i <= hi; i++) {
      const p = document.createElement('p');
      p.className = 'pl-now-p';
      p.textContent = n.paragraphs[i] ?? '';
      els.set(i, p);
    }
    box.replaceChildren(...els.values());
    now.hl = createHighlighter({ paraEl: (i) => els.get(i) ?? null, paraText: (i) => n.paragraphs[i] ?? '', titleEl: null });
    now.key = key;
    now.at = '';
  }
  const target = n.para >= 0 ? now.hl.set(n.para, n.s, n.e) : null;
  // scroll only the panel itself (never the page behind the sheet), and only when the sentence changed,
  // so the 1 s sleep-timer tick does not fight a finger scrolling the panel
  const at = `${key}|${n.para}|${n.s}`;
  if (target && now.at !== at) {
    now.at = at;
    try {
      const b = box.getBoundingClientRect();
      const t = target.getBoundingClientRect();
      box.scrollTo?.({ top: Math.max(0, box.scrollTop + t.top - b.top - (b.height - t.height) / 2), behavior: 'smooth' });
    } catch {
      // scrolling is only a nicety
    }
  }
}

function syncAll(): void {
  const st = player.getState();
  const dock = host;
  if (!dock) return;
  if (st.status === 'idle') {
    if (built) {
      built = false;
      dock.replaceChildren();
    }
    sheet?.close();
    document.documentElement.style.setProperty('--player-h', '0px');
    document.body.classList.remove('has-player');
    if (tick !== undefined) clearInterval(tick);
    tick = undefined;
    return;
  }
  if (!built) {
    built = true;
    render(dock, dockMarkup());
    document.body.classList.add('has-player');
    measure();
  }
  sync(dock);
  if (sheet && !sheet.closed) {
    sync(sheet.body);
    syncNow();
  }
  const timed = player.info().sleep > 0;
  if (timed && tick === undefined) tick = setInterval(syncAll, 1000);
  else if (!timed && tick !== undefined) {
    clearInterval(tick);
    tick = undefined;
  }
}

function measure(): void {
  if (!host) return;
  const h = built ? Math.ceil(host.getBoundingClientRect().height) : 0;
  document.documentElement.style.setProperty('--player-h', `${h}px`);
}

function openSheet(): void {
  if (sheet && !sheet.closed) return;
  sheet = openDialog({
    title: 'Đang nghe',
    variant: 'sheet',
    className: 'pl-sheet-dialog',
    body: sheetMarkup(),
    initialFocus: '[data-pl="toggle"]',
    onClose: () => {
      sheet = null;
      now?.off();
      now = null;
    },
  });
  sheet.body.addEventListener('click', onClick);
  sheet.body.addEventListener('change', onInput);
  sync(sheet.body);
  now = { key: '', hl: null, off: onMark(syncNow), at: '' };
  syncNow();
}

function onClick(e: Event): void {
  const t = (e.target as Element | null)?.closest<HTMLElement>('[data-pl]');
  if (!t || t instanceof HTMLSelectElement) return;
  const st = player.getState();
  switch (t.dataset.pl) {
    case 'toggle':
      player.toggle();
      break;
    case 'back':
      player.step(-1);
      break;
    case 'fwd':
      player.step(1);
      break;
    case 'prevch':
      player.gotoChapter((st.idx ?? 0) - 1);
      break;
    case 'nextch':
      player.gotoChapter((st.idx ?? 0) + 1);
      break;
    case 'expand':
      openSheet();
      break;
    case 'pip':
      togglePip();
      break;
    case 'voice':
      sheet?.close();
      openSettings('voice');
      break;
    case 'close':
      player.stop();
      break;
    default:
  }
}

function onInput(e: Event): void {
  const t = e.target as HTMLSelectElement | null;
  if (!(t instanceof HTMLSelectElement)) return;
  if (t.dataset.pl === 'rate') settings.set('rate', Number(t.value));
  else if (t.dataset.pl === 'sleep') player.setSleep(Number(t.value));
}

export { typingTarget };

/**
 * The player's keys, wherever the user is: Space = play / pause, Shift + ← → = previous / next chapter of
 * what is playing, J / K = one chunk forward / back.
 */
function onKey(e: KeyboardEvent): void {
  if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey || e.isComposing) return;
  const st = player.getState();
  if (st.status === 'idle') return;
  if (typingTarget(e)) return;
  // a dialog owns the keyboard, except the player's own sheet
  if (document.documentElement.classList.contains('has-overlay') && !(sheet && !sheet.closed)) return;
  const k = keyOf(e);
  if (k === ' ' && !e.shiftKey) {
    if (!e.repeat) player.toggle();
  } else if (e.shiftKey && k === 'ArrowLeft') player.gotoChapter((st.idx ?? 0) - 1);
  else if (e.shiftKey && k === 'ArrowRight') player.gotoChapter((st.idx ?? 0) + 1);
  else if (!e.shiftKey && k === 'j') player.step(1);
  else if (!e.shiftKey && k === 'k') player.step(-1);
  else return;
  e.preventDefault();
}

/** Called once by the player. */
export function initDock(p: Player): void {
  if (host || typeof document === 'undefined') return;
  player = p;
  host = document.getElementById('player-dock');
  if (!host) return;
  host.addEventListener('click', onClick);
  host.addEventListener('change', onInput);
  document.addEventListener('keydown', onKey);
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(measure);
    observer.observe(host);
  }
  window.addEventListener('resize', measure);
  player.onChange(syncAll);
  syncAll();
}
