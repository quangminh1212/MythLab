/**
 * Bookmarks: paragraphs the reader marked, newest first. A bookmark opens the reader at its chapter with the
 * paragraph in the query (`#/r/<source>/<key>/<idx>?p=<para>`).
 */
import type { Bookmark, Route, ViewContext } from '../core/contracts';
import { on } from '../core/events';
import { fmtNum, timeAgo } from '../core/format';
import { html, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { library } from '../core/library';
import { href, setQuery } from '../core/router';
import { confirmDialog, stateView, toast } from '../core/ui';
import { setCrumbs } from '../shell';
import { pageHead } from './cards';

const PAGE = 30;
let root: HTMLElement | null = null;
let route: Route | null = null;
let off: (() => void)[] = [];

function row(b: Bookmark): SafeHtml {
  const chapter = b.title || `Chương ${fmtNum(b.n)}`;
  return html`<li class="row">
    <a class="row-main" href="${href.read(b.source, b.key, b.idx, { p: b.para })}" title="Mở đoạn đã đánh dấu">
      <span class="row-ic" aria-hidden="true">${icon('bookmark')}</span>
      <span class="row-body">
        <span class="row-title">${b.name || b.key}</span>
        <span class="row-meta">${chapter}</span>
        ${b.excerpt ? html`<span class="row-excerpt">${b.excerpt}</span>` : ''}
        <span class="row-meta row-sub">${timeAgo(b.ts)}</span>
      </span>
    </a>
    <span class="row-actions">
      <a class="icon-btn" href="${href.story(b.source, b.key)}" aria-label="Trang truyện ${b.name || b.key}" title="Trang truyện">${icon('list')}</a>
      <button type="button" class="icon-btn" data-remove="${b.id}" aria-label="Bỏ đánh dấu ${chapter} của ${b.name || b.key}" title="Bỏ đánh dấu">${icon('trash')}</button>
    </span>
  </li>`;
}

function draw(): void {
  const el = root;
  if (!el || !route) return;
  const list = library.bookmarks();
  const pages = Math.min(50, Math.max(1, parseInt(route.query.n || '1', 10) || 1));
  const shown = list.slice(0, pages * PAGE);
  const more = list.length - shown.length;
  render(
    el,
    html`<div class="page page-narrow">
      ${pageHead(
        'Đánh dấu',
        list.length ? `${fmtNum(list.length)} đoạn đã đánh dấu` : undefined,
        list.length ? html`<button type="button" class="btn btn-danger-ghost" data-clear>${icon('trash')}<span>Xoá tất cả</span></button>` : undefined,
      )}
      ${list.length
        ? html`<ul class="rows">
              ${shown.map(row)}
            </ul>
            ${more > 0
              ? html`<div class="more-row"><button type="button" class="btn" data-more>Xem thêm ${fmtNum(Math.min(PAGE, more))} đánh dấu</button><span class="muted">Đang hiện ${fmtNum(shown.length)} / ${fmtNum(list.length)}</span></div>`
              : ''}`
        : stateView({
            icon: 'bookmark',
            title: 'Chưa có đánh dấu nào',
            message: 'Khi đang đọc, hãy đánh dấu đoạn bạn muốn quay lại. Các đánh dấu sẽ được lưu ở đây.',
            home: true,
          })}
    </div>`,
  );
}

async function onClick(e: Event): Promise<void> {
  const t = e.target as Element;
  const rm = t.closest<HTMLElement>('[data-remove]');
  if (rm) {
    const id = rm.dataset.remove as string;
    const old = library.bookmarks().find((b) => b.id === id);
    library.removeBookmark(id);
    toast({ message: 'Đã bỏ đánh dấu.', action: old ? { label: 'Hoàn tác', run: () => void library.addBookmark(old) } : undefined });
    return;
  }
  if (t.closest('[data-more]')) {
    setQuery({ n: Math.max(1, parseInt(route?.query.n || '1', 10) || 1) + 1 });
    return;
  }
  if (t.closest('[data-clear]')) {
    const ok = await confirmDialog({
      title: 'Xoá tất cả đánh dấu?',
      message: 'Mọi đoạn đã đánh dấu sẽ bị xoá khỏi thiết bị này. Thao tác này không hoàn tác được.',
      confirmLabel: 'Xoá tất cả',
      cancelLabel: 'Giữ lại',
      danger: true,
    });
    if (ok) {
      library.clearBookmarks();
      toast('Đã xoá tất cả đánh dấu.');
    }
  }
}
const click = (e: Event): void => void onClick(e);

export function mount(el: HTMLElement, r: Route, ctx: ViewContext): void {
  root = el;
  route = r;
  ctx.setTitle('Đánh dấu');
  setCrumbs([{ label: 'Đánh dấu' }]);
  draw();
  el.addEventListener('click', click);
  off = [on('bookmarks', draw)];
}

export function update(r: Route): void {
  route = r;
  draw();
}

export function unmount(): void {
  root?.removeEventListener('click', click);
  for (const f of off) f();
  off = [];
  root = null;
  route = null;
}
