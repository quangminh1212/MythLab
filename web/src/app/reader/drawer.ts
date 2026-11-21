/**
 * The reader's drawer: the chapter list (virtualised, with a numeric jump) and the bookmarks of the story.
 * A right-hand panel on wide screens and a bottom sheet on phones (`openDialog` variant "drawer").
 */
import type { Bookmark, ChapterRef, StoryDetail } from '../core/contracts';
import { on } from '../core/events';
import { chapterLabel, fmtNum, timeAgo } from '../core/format';
import { html, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { library } from '../core/library';
import { progress } from '../core/progress';
import { href, navigate } from '../core/router';
import { openDialog, virtualList, type DialogHandle, type VirtualListHandle } from '../core/ui';

export type DrawerTab = 'toc' | 'marks';

const ROW = 48;

/**
 * Chapter a typed number means: the chapter carrying that number when there is one (numbers can have gaps or
 * repeat), else that position in the list. Returns -1 for something that is not a usable number.
 */
export function chapterOfNumber(chapters: Pick<ChapterRef, 'n'>[], typed: string | number): number {
  const v = typeof typed === 'number' ? typed : Number(String(typed).trim().replace(',', '.'));
  if (!Number.isFinite(v) || v < 0 || !chapters.length) return -1;
  const byNumber = chapters.findIndex((c) => c.n === v);
  if (byNumber >= 0) return byNumber;
  return Math.max(0, Math.min(chapters.length - 1, Math.trunc(v) - 1));
}

/** Bookmarks in reading order. */
export const sortMarks = (list: Bookmark[]): Bookmark[] => [...list].sort((a, b) => a.idx - b.idx || a.para - b.para);

function marksMarkup(st: StoryDetail, list: Bookmark[]): SafeHtml {
  if (!list.length) {
    return html`<div class="rd-dr-empty">
      <p><strong>Chưa có đánh dấu nào trong truyện này.</strong></p>
      <p>Nhấn nút đánh dấu trên thanh đọc (phím B) để lưu đoạn đang đọc.</p>
    </div>`;
  }
  return html`<ul class="rd-dr-marks">
    ${sortMarks(list).map(
      (b) =>
        html`<li class="rd-dr-mark">
          <a class="rd-dr-mark-link" href="${href.read(st.source, st.key, b.idx, { p: b.para })}" data-close>
            <span class="rd-dr-mark-ch">${b.title || `Chương ${b.n}`}</span>
            <span class="rd-dr-mark-text">${b.excerpt || 'Đoạn ' + (b.para + 1)}</span>
            <span class="rd-dr-mark-when">${timeAgo(b.ts)}</span>
          </a>
          <button type="button" class="icon-btn" data-unmark="${b.id}" aria-label="Xoá đánh dấu này" title="Xoá đánh dấu">${icon('trash')}</button>
        </li>`,
    )}
  </ul>`;
}

let open: DialogHandle | null = null;

export function closeChapterDrawer(): void {
  open?.close();
}

export function openChapterDrawer(o: { st: StoryDetail; idx: number; tab?: DrawerTab }): void {
  if (open && !open.closed) open.close();
  const { st, idx } = o;
  const total = st.chapters.length;
  const reached = Math.max(idx, progress.get(st.source, st.key)?.maxIdx ?? -1);
  let target = -1;
  let list: VirtualListHandle | null = null;

  const d = openDialog({
    title: st.name,
    variant: 'drawer',
    className: 'rd-drawer',
    initialFocus: '[role="tab"][aria-selected="true"]',
    body: html`<div class="rd-dr">
      <div class="rd-dr-tabs" role="tablist" aria-label="Mục lục và đánh dấu">
        <button type="button" role="tab" id="rd-tab-toc" aria-controls="rd-pane-toc" data-tab="toc" aria-selected="true">Chương (${fmtNum(total)})</button>
        <button type="button" role="tab" id="rd-tab-marks" aria-controls="rd-pane-marks" data-tab="marks" aria-selected="false" tabindex="-1">
          Đánh dấu <span data-mark-count></span>
        </button>
      </div>
      <div class="rd-dr-pane" id="rd-pane-toc" role="tabpanel" aria-labelledby="rd-tab-toc" data-pane="toc">
        <form class="rd-dr-jump" novalidate>
          <label class="sr-only" for="rd-jump">Tới chương số</label>
          <input id="rd-jump" class="input" type="text" inputmode="numeric" autocomplete="off" enterkeyhint="go" placeholder="Tới chương số… (1–${fmtNum(total)})" />
          <button type="submit" class="btn btn-primary">Tới</button>
        </form>
        <div class="rd-dr-scroll" data-scroll tabindex="-1"><div class="rd-dr-list" data-list></div></div>
      </div>
      <div class="rd-dr-pane" id="rd-pane-marks" role="tabpanel" aria-labelledby="rd-tab-marks" data-pane="marks" hidden>
        <div class="rd-dr-scroll" data-marks></div>
      </div>
    </div>`,
    onClose: () => {
      list?.destroy();
      list = null;
      offMarks();
      if (open === d) open = null;
    },
  });
  open = d;
  const body = d.body;
  const scroller = body.querySelector<HTMLElement>('[data-scroll]') as HTMLElement;
  const container = body.querySelector<HTMLElement>('[data-list]') as HTMLElement;
  const marksBox = body.querySelector<HTMLElement>('[data-marks]') as HTMLElement;
  const input = body.querySelector<HTMLInputElement>('#rd-jump') as HTMLInputElement;
  const tabs = Array.from(body.querySelectorAll<HTMLElement>('[role="tab"]'));

  const row = (i: number): SafeHtml => {
    const ref = st.chapters[i] as ChapterRef;
    const cls = ['rd-dr-row', i === idx ? 'is-current' : '', i !== idx && i <= reached ? 'is-read' : '', i === target ? 'is-target' : ''].filter(Boolean).join(' ');
    return html`<a class="${cls}" href="${href.read(st.source, st.key, i)}" data-close ${i === idx ? html`aria-current="page"` : ''}>
      <span class="rd-dr-num">${i + 1}</span>
      <span class="rd-dr-name">${chapterLabel(ref)}</span>
      ${i === idx ? html`<span class="rd-dr-tag">Đang đọc</span>` : ''}
    </a>`;
  };
  list = virtualList({ container, count: total, itemHeight: ROW, render: row, scroller, overscan: 8 });
  list.scrollTo(idx, 'center');

  function drawMarks(): void {
    const marks = library.bookmarks(st.source, st.key);
    render(marksBox, marksMarkup(st, marks));
    const count = body.querySelector('[data-mark-count]');
    if (count) count.textContent = marks.length ? `(${marks.length})` : '';
  }
  const offMarks = on('bookmarks', drawMarks);
  drawMarks();

  function select(tab: DrawerTab, focus = false): void {
    for (const t of tabs) {
      const onTab = t.dataset.tab === tab;
      t.setAttribute('aria-selected', String(onTab));
      t.tabIndex = onTab ? 0 : -1;
      if (onTab && focus) t.focus();
    }
    for (const p of body.querySelectorAll<HTMLElement>('[data-pane]')) p.hidden = p.dataset.pane !== tab;
    if (tab === 'toc') list?.refresh();
  }

  function aim(navigateNow: boolean): void {
    const i = input.value.trim() === '' ? -1 : chapterOfNumber(st.chapters, input.value);
    if (i < 0) {
      if (target >= 0) {
        target = -1;
        list?.refresh();
      }
      return;
    }
    if (navigateNow) {
      d.close();
      navigate(href.read(st.source, st.key, i));
      return;
    }
    target = i;
    list?.refresh();
    list?.scrollTo(i, 'center');
  }

  body.addEventListener('click', (e) => {
    const t = e.target as Element;
    const tab = t.closest<HTMLElement>('[role="tab"]');
    if (tab) {
      select(tab.dataset.tab as DrawerTab);
      return;
    }
    const un = t.closest<HTMLElement>('[data-unmark]');
    if (un) library.removeBookmark(un.dataset.unmark as string);
  });
  body.querySelector('[role="tablist"]')?.addEventListener('keydown', (e) => {
    const k = (e as KeyboardEvent).key;
    if (k !== 'ArrowLeft' && k !== 'ArrowRight') return;
    e.preventDefault();
    const cur = tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true');
    const next = tabs[(cur + (k === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length] as HTMLElement;
    select(next.dataset.tab as DrawerTab, true);
  });
  input.addEventListener('input', () => aim(false));
  body.querySelector('form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    aim(true);
  });

  if (o.tab === 'marks') select('marks', true);
}
