/**
 * UI primitives shared by every stage: toast, modal dialog / sheet (focus trap, Escape, focus restore), confirm,
 * virtual list, error / empty state, skeletons. Markup classes are styled in src/styles/components.css.
 */
import { on } from './events';
import { ApiError } from './backend/types';
import type { ToastOptions } from './contracts';
import { errMsg } from './format';
import { append, html, raw, render, type SafeHtml } from './html';
import { icon, type IconName } from './icons';

// ---------------------------------------------------------------- toast

let toastTimer: ReturnType<typeof setTimeout> | undefined;

/** Shows a message in the polite live region `#toasts` (one at a time; a new one replaces the old). */
export function toast(o: ToastOptions | string): void {
  const opt: ToastOptions = typeof o === 'string' ? { message: o } : o;
  const host = document.getElementById('toasts');
  if (!host) return;
  clearTimeout(toastTimer);
  const kind = opt.kind || 'info';
  render(
    host,
    html`<div class="toast toast-${kind}">
      <span class="toast-msg">${opt.message}</span>
      ${opt.action ? html`<button type="button" class="toast-act">${opt.action.label}</button>` : ''}
    </div>`,
  );
  const hide = (): void => host.replaceChildren();
  if (opt.action) {
    const act = opt.action;
    host.querySelector('.toast-act')?.addEventListener('click', () => {
      hide();
      act.run();
    });
  }
  toastTimer = setTimeout(hide, opt.duration ?? (opt.action ? 6000 : 3200));
}

let toastBound = false;
/** Routes the app event "toast" to the toast region. Called once by main.ts. */
export function bindToasts(): void {
  if (toastBound) return;
  toastBound = true;
  on('toast', toast);
}

// ---------------------------------------------------------------- dialog / sheet

const FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]):not([type="hidden"]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';

export function focusables(root: Element): HTMLElement[] {
  return Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter((el) => !el.hidden && el.getClientRects().length > 0);
}

/**
 * Keeps Tab inside `el`, handles Escape, makes the rest of the page inert and restores focus on release.
 * Use for anything modal that is not built with `openDialog` (e.g. the mobile side nav).
 */
export function trapFocus(el: HTMLElement, onEscape?: () => void): () => void {
  const prev = document.activeElement as HTMLElement | null;
  const onKey = (e: KeyboardEvent): void => {
    if (e.key === 'Escape' && onEscape) {
      e.stopPropagation();
      e.preventDefault();
      onEscape();
      return;
    }
    if (e.key !== 'Tab') return;
    const f = focusables(el);
    if (!f.length) {
      e.preventDefault();
      el.focus();
      return;
    }
    const first = f[0] as HTMLElement;
    const last = f[f.length - 1] as HTMLElement;
    const a = document.activeElement;
    if (e.shiftKey && (a === first || !el.contains(a))) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && (a === last || !el.contains(a))) {
      e.preventDefault();
      first.focus();
    }
  };
  document.addEventListener('keydown', onKey, true);
  return () => {
    document.removeEventListener('keydown', onKey, true);
    if (prev && prev.isConnected) prev.focus({ preventScroll: true });
  };
}

export interface DialogOptions {
  title: string;
  /** Body markup. */
  body: SafeHtml;
  /** Footer markup (buttons). */
  footer?: SafeHtml;
  /**
   * 'dialog' = centred card; 'sheet' = bottom sheet on phones and centred card on wide screens;
   * 'drawer' = right-hand panel on wide screens and bottom sheet on phones.
   */
  variant?: 'dialog' | 'sheet' | 'drawer';
  /** Extra class on the panel. */
  className?: string;
  /** Hide the title visually (still announced). */
  hideTitle?: boolean;
  /** Called after the dialog closed, whatever the reason. */
  onClose?(): void;
  /** Close when the backdrop is clicked (default true). */
  dismissable?: boolean;
  /** Selector of the element to focus first (default: first focusable in the body, else the close button). */
  initialFocus?: string;
}

export interface DialogHandle {
  /** The panel element (role="dialog"). */
  el: HTMLElement;
  /** The body container. */
  body: HTMLElement;
  close(): void;
  readonly closed: boolean;
}

let dialogSeq = 0;
const stack: DialogHandle[] = [];

/** Opens a modal dialog in `#overlay-root`. Dialogs stack; Escape closes the top one. */
export function openDialog(o: DialogOptions): DialogHandle {
  const root = document.getElementById('overlay-root') || document.body;
  const id = `dlg${++dialogSeq}`;
  const variant = o.variant || 'dialog';
  const wrap = document.createElement('div');
  wrap.className = `overlay overlay-${variant}`;
  render(
    wrap,
    html`<div class="overlay-scrim" data-close></div>
      <div class="dialog ${o.className || ''}" role="dialog" aria-modal="true" aria-labelledby="${id}-t" tabindex="-1">
        <header class="dialog-head">
          <h2 id="${id}-t" class="${o.hideTitle ? 'sr-only' : 'dialog-title'}">${o.title}</h2>
          <button type="button" class="icon-btn dialog-close" data-close aria-label="Đóng">${icon('close')}</button>
        </header>
        <div class="dialog-body">${o.body}</div>
        ${o.footer ? html`<footer class="dialog-foot">${o.footer}</footer>` : ''}
      </div>`,
  );
  const panel = wrap.querySelector<HTMLElement>('.dialog') as HTMLElement;
  const body = wrap.querySelector<HTMLElement>('.dialog-body') as HTMLElement;
  let closed = false;
  let release: () => void = () => {};
  const handle: DialogHandle = {
    el: panel,
    body,
    get closed() {
      return closed;
    },
    close() {
      if (closed) return;
      closed = true;
      const i = stack.indexOf(handle);
      if (i >= 0) stack.splice(i, 1);
      wrap.remove();
      if (!stack.length) document.documentElement.classList.remove('has-overlay');
      release();
      o.onClose?.();
    },
  };
  wrap.addEventListener('click', (e) => {
    const t = (e.target as Element).closest('[data-close]');
    if (!t) return;
    if (t.classList.contains('overlay-scrim') && o.dismissable === false) return;
    handle.close();
  });
  root.appendChild(wrap);
  stack.push(handle);
  document.documentElement.classList.add('has-overlay');
  release = trapFocus(panel, () => {
    if (stack[stack.length - 1] === handle) handle.close();
  });
  const first = (o.initialFocus && panel.querySelector<HTMLElement>(o.initialFocus)) || focusables(body)[0] || focusables(panel)[0] || panel;
  first.focus({ preventScroll: true });
  return handle;
}

/** Closes every open dialog (route changes do this). */
export function closeAllDialogs(): void {
  for (const d of [...stack].reverse()) d.close();
}

/** Asks a yes/no question. Resolves true when confirmed. */
export function confirmDialog(o: { title: string; message: string; confirmLabel?: string; cancelLabel?: string; danger?: boolean }): Promise<boolean> {
  return new Promise((resolve) => {
    let ok = false;
    const d = openDialog({
      title: o.title,
      body: html`<p class="dialog-text">${o.message}</p>`,
      footer: html`<button type="button" class="btn" data-close>${o.cancelLabel || 'Huỷ'}</button>
        <button type="button" class="btn ${o.danger ? 'btn-danger' : 'btn-primary'}" data-ok>${o.confirmLabel || 'Đồng ý'}</button>`,
      className: 'dialog-sm',
      initialFocus: '[data-ok]',
      onClose: () => resolve(ok),
    });
    d.el.querySelector('[data-ok]')?.addEventListener('click', () => {
      ok = true;
      d.close();
    });
  });
}

// ---------------------------------------------------------------- virtual list

export interface VirtualListOptions {
  /** Element that receives the rows; it gets `position: relative` and the total height. */
  container: HTMLElement;
  /** Number of items. */
  count: number;
  /** Height of every item in px, or a function for variable heights (called once per item, cached). */
  itemHeight: number | ((index: number) => number);
  /** Markup of one item. The list wraps it in an absolutely positioned `.vrow` box. */
  render(index: number): SafeHtml;
  /** Items rendered beyond the viewport on each side (default 6). */
  overscan?: number;
  /** Scrolling element; default the window. */
  scroller?: HTMLElement | null;
  /** Called after the rendered window changed. */
  onRender?(first: number, last: number): void;
}

export interface VirtualListHandle {
  /** Re-renders (after the data behind `render` changed); `count`/`itemHeight` replace the old values. */
  refresh(o?: { count?: number; itemHeight?: number | ((index: number) => number) }): void;
  /** Scrolls so the item is visible ('start' | 'center'). */
  scrollTo(index: number, align?: 'start' | 'center', smooth?: boolean): void;
  /** Offset of an item from the top of the container, in px. */
  offsetOf(index: number): number;
  /** The element of a rendered item, or null when it is outside the window. */
  elementOf(index: number): HTMLElement | null;
  destroy(): void;
}

/**
 * Windowed list: only the items near the viewport exist in the DOM. Works inside a scrolling element or with the
 * page as the scroller, with fixed or per-item heights (prefix sums + binary search).
 */
export function virtualList(o: VirtualListOptions): VirtualListHandle {
  const { container } = o;
  const scroller = o.scroller ?? null;
  const overscan = o.overscan ?? 6;
  let count = o.count;
  let ih = o.itemHeight;
  let offsets: Float64Array | null = null;
  let total = 0;
  const rows = new Map<number, HTMLElement>();
  let raf = 0;
  let dead = false;

  function measure(): void {
    if (typeof ih === 'number') {
      offsets = null;
      total = ih * count;
    } else {
      offsets = new Float64Array(count + 1);
      for (let i = 0; i < count; i++) offsets[i + 1] = (offsets[i] as number) + ih(i);
      total = offsets[count] as number;
    }
    container.style.position = 'relative';
    container.style.height = total + 'px';
  }
  const top = (i: number): number => (offsets ? (offsets[Math.min(count, Math.max(0, i))] as number) : (ih as number) * i);
  const heightOf = (i: number): number => (offsets ? (offsets[i + 1] as number) - (offsets[i] as number) : (ih as number));
  function indexAt(y: number): number {
    if (count <= 0) return 0;
    if (!offsets) return Math.min(count - 1, Math.max(0, Math.floor(y / ((ih as number) || 1))));
    let lo = 0;
    let hi = count - 1;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      if ((offsets[mid] as number) <= y) lo = mid;
      else hi = mid - 1;
    }
    return lo;
  }
  /** Visible range of the container in its own coordinates. */
  function viewport(): [number, number] {
    const r = container.getBoundingClientRect();
    if (scroller) {
      const s = scroller.getBoundingClientRect();
      return [s.top - r.top, s.bottom - r.top];
    }
    return [-r.top, window.innerHeight - r.top];
  }

  function paint(): void {
    raf = 0;
    if (dead) return;
    const [a, b] = viewport();
    let first = 0;
    let last = -1;
    if (count > 0 && b > 0 && a < total) {
      first = Math.max(0, indexAt(Math.max(0, a)) - overscan);
      last = Math.min(count - 1, indexAt(Math.min(total, b)) + overscan);
    }
    for (const [i, el] of rows) {
      if (i < first || i > last) {
        el.remove();
        rows.delete(i);
      }
    }
    for (let i = first; i <= last; i++) {
      if (rows.has(i)) continue;
      const el = document.createElement('div');
      el.className = 'vrow';
      el.style.cssText = `position:absolute;left:0;right:0;top:${top(i)}px;height:${heightOf(i)}px`;
      el.dataset.index = String(i);
      render(el, o.render(i));
      container.appendChild(el);
      rows.set(i, el);
    }
    o.onRender?.(first, last);
  }
  const schedule = (): void => {
    if (!raf && !dead) raf = requestAnimationFrame(paint);
  };

  const target: HTMLElement | Window = scroller || window;
  target.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  measure();
  paint();

  return {
    refresh(n) {
      if (n?.count !== undefined) count = n.count;
      if (n?.itemHeight !== undefined) ih = n.itemHeight;
      for (const el of rows.values()) el.remove();
      rows.clear();
      measure();
      paint();
    },
    scrollTo(index, align = 'start', smooth = false) {
      if (count <= 0) return;
      const i = Math.min(count - 1, Math.max(0, index));
      const r = container.getBoundingClientRect();
      const behavior: ScrollBehavior = smooth && !matchMedia('(prefers-reduced-motion: reduce)').matches ? 'smooth' : 'auto';
      if (scroller) {
        const s = scroller.getBoundingClientRect();
        const base = scroller.scrollTop + (r.top - s.top) + top(i);
        const y = align === 'center' ? base - (scroller.clientHeight - heightOf(i)) / 2 : base;
        scroller.scrollTo({ top: Math.max(0, y), behavior });
      } else {
        const pad = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--topbar-h')) || 56;
        const base = window.scrollY + r.top + top(i);
        const y = align === 'center' ? base - (window.innerHeight - heightOf(i)) / 2 : base - pad - 8;
        window.scrollTo({ top: Math.max(0, y), behavior });
      }
      schedule();
    },
    offsetOf: (i) => top(i),
    elementOf: (i) => rows.get(i) ?? null,
    destroy() {
      dead = true;
      if (raf) cancelAnimationFrame(raf);
      target.removeEventListener('scroll', schedule);
      window.removeEventListener('resize', schedule);
      for (const el of rows.values()) el.remove();
      rows.clear();
    },
  };
}

// ---------------------------------------------------------------- states

export interface StateOptions {
  icon?: IconName;
  title: string;
  /** Human explanation. */
  message?: string;
  /** Technical detail, shown collapsed. */
  detail?: string;
  /** Shows "Thử lại" (a `<button data-retry>`). */
  retry?: boolean;
  /** Shows "Về trang chủ" (default true for errors). */
  home?: boolean;
  /** Extra action markup. */
  actions?: SafeHtml;
  kind?: 'empty' | 'error';
  /** The title is the page's only heading (a whole-view state): render it as the `<h1>`. */
  h1?: boolean;
}

/** The single empty / error state component. */
export function stateView(o: StateOptions): SafeHtml {
  const kind = o.kind || 'empty';
  return html`<section class="state state-${kind}" ${kind === 'error' ? raw('role="alert"') : ''}>
    <div class="state-ic">${icon(o.icon || (kind === 'error' ? 'alert' : 'inbox'))}</div>
    ${o.h1 ? html`<h1 class="state-title">${o.title}</h1>` : html`<h2 class="state-title">${o.title}</h2>`}
    ${o.message ? html`<p class="state-msg">${o.message}</p>` : ''}
    ${o.retry || o.home || o.actions
      ? html`<div class="state-actions">
          ${o.retry ? html`<button type="button" class="btn btn-primary" data-retry>${icon('refresh')}<span>Thử lại</span></button>` : ''}
          ${o.actions || ''} ${o.home ? html`<a class="btn" href="#/">${icon('home')}<span>Về trang chủ</span></a>` : ''}
        </div>`
      : ''}
    ${o.detail ? html`<details class="state-detail"><summary>Chi tiết kỹ thuật</summary><pre>${o.detail}</pre></details>` : ''}
  </section>`;
}

/** Turns an error into a friendly Vietnamese title + message (the raw text goes into the collapsed detail). */
export function describeError(e: unknown): { title: string; message: string; detail: string; icon: IconName } {
  const detail = errMsg(e);
  const st = e instanceof ApiError ? e.status : -1;
  const code = e instanceof ApiError ? e.code : undefined;
  if (code === 'no_backend') return { title: 'Chưa có nguồn truyện', message: 'Hãy kết nối tới máy chủ MythLab hoặc nhập GitHub token trong phần Cài đặt.', detail, icon: 'cloud' };
  if (st === 0 || code === 'network') {
    return navigator.onLine === false
      ? { title: 'Bạn đang ngoại tuyến', message: 'Kiểm tra kết nối mạng rồi thử lại. Các chương đã tải về vẫn đọc được.', detail, icon: 'wifiOff' }
      : { title: 'Không kết nối được', message: 'Máy chủ truyện không phản hồi. Kiểm tra máy chủ đang chạy rồi thử lại.', detail, icon: 'wifiOff' };
  }
  if (st === 401 || st === 403) return { title: 'Không có quyền truy cập', message: 'Mã truy cập không đúng hoặc đã hết hạn. Kiểm tra lại trong phần Cài đặt.', detail, icon: 'alert' };
  if (st === 404) return { title: 'Không tìm thấy', message: 'Nội dung này không còn tồn tại hoặc đường dẫn không đúng.', detail, icon: 'inbox' };
  if (st === 502 || st === 504) return { title: 'Nguồn truyện đang gặp sự cố', message: 'Không lấy được dữ liệu từ kho truyện. Vui lòng thử lại sau ít phút.', detail, icon: 'cloud' };
  if (st === 503) return { title: 'Dịch vụ tạm thời không sẵn sàng', message: 'Vui lòng thử lại sau ít phút.', detail, icon: 'cloud' };
  return { title: 'Đã xảy ra lỗi', message: 'Không tải được nội dung. Vui lòng thử lại.', detail, icon: 'alert' };
}

/** Renders the error state into `el`; "Thử lại" calls `retry`. */
export function showError(el: HTMLElement, e: unknown, retry?: () => void): void {
  const d = describeError(e);
  // when the error replaces the whole view there is no page title left: the state title becomes the <h1>
  const scope = el.closest('main') ?? document.body;
  const h1 = ![...scope.querySelectorAll('h1')].some((h) => !el.contains(h));
  render(el, stateView({ h1, kind: 'error', icon: d.icon, title: d.title, message: d.message, detail: d.detail, retry: !!retry, home: true }));
  if (retry) el.querySelector('[data-retry]')?.addEventListener('click', () => retry());
}

// ---------------------------------------------------------------- skeletons

const times = (n: number, fn: (i: number) => SafeHtml): SafeHtml[] => Array.from({ length: n }, (_, i) => fn(i));

export const skeleton = {
  /** A row/grid of story cards. */
  cards: (n = 6, cls = 'grid'): SafeHtml =>
    html`<div class="${cls}" aria-hidden="true">${times(n, () => html`<div class="card sk-card"><div class="cover sk"></div><div class="sk sk-line"></div><div class="sk sk-line sk-short"></div></div>`)}</div>`,
  /** Text lines. */
  lines: (n = 4): SafeHtml => html`<div class="sk-lines" aria-hidden="true">${times(n, (i) => html`<div class="sk sk-line ${i % 3 === 2 ? 'sk-short' : ''}"></div>`)}</div>`,
  /** List rows (history, chapters). */
  rows: (n = 8): SafeHtml => html`<div class="sk-rows" aria-hidden="true">${times(n, () => html`<div class="sk sk-row"></div>`)}</div>`,
  /** Story page header. */
  story: (): SafeHtml =>
    html`<div class="story-head" aria-hidden="true">
      <div class="cover sk story-cover"></div>
      <div class="story-info"><div class="sk sk-title"></div>${skeleton.lines(5)}</div>
    </div>`,
  /** Whole-view placeholder announced to assistive tech. */
  view: (inner: SafeHtml): SafeHtml => html`<div class="loading" role="status" aria-live="polite"><span class="sr-only">Đang tải…</span>${inner}</div>`,
};

/** Appends an sr-only status message (e.g. result counts) to the polite live region. */
export function announce(message: string): void {
  const el = document.getElementById('sr-status');
  if (el) el.textContent = message;
}

export { append };
