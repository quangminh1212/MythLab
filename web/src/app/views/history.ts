/** Reading history: every story that was opened, newest first, with its chapter and percentage. */
import type { Progress, Route, ViewContext } from '../core/contracts';
import { cover, hydrateCovers } from '../core/covers';
import { on } from '../core/events';
import { fmtNum, repoLabel, timeAgo } from '../core/format';
import { html, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { library } from '../core/library';
import { progress } from '../core/progress';
import { href, setQuery } from '../core/router';
import { confirmDialog, stateView, toast } from '../core/ui';
import { setCrumbs } from '../shell';
import { pageHead } from './cards';

const PAGE = 30;
let root: HTMLElement | null = null;
let route: Route | null = null;
let off: (() => void)[] = [];

function row(p: Progress): SafeHtml {
  const pct = progress.percent(p);
  const where = p.total ? `Chương ${fmtNum(p.n)} / ${fmtNum(p.total)}` : `Chương ${fmtNum(p.n)}`;
  const name = p.name || p.key;
  return html`<li class="row">
    <a class="row-main" href="${href.read(p.source, p.key, p.idx)}" title="Đọc tiếp ${name}">
      ${cover({ key: p.key, name: p.name, author: p.author, genres: p.genres, group: p.group, cover: p.cover, poster: p.poster, cover_sha: p.cover_sha }, { w: 80, cls: 'row-cover' })}
      <span class="row-body">
        <span class="row-title">${name}</span>
        <span class="row-meta">${where}${p.title ? html` · ${p.title}` : ''}</span>
        <span class="row-meta row-sub">${timeAgo(p.ts)}${p.group ? html` · ${repoLabel(p.group)}` : ''}</span>
        <progress class="bar" max="100" value="${pct}" aria-label="Đã đọc ${pct}%"></progress>
      </span>
    </a>
    <span class="row-actions">
      <a class="icon-btn" href="${href.story(p.source, p.key)}" aria-label="Trang truyện ${name}" title="Trang truyện">${icon('list')}</a>
      <button type="button" class="icon-btn" data-remove="${p.source}|${p.key}" aria-label="Xoá ${name} khỏi lịch sử" title="Xoá khỏi lịch sử">${icon('trash')}</button>
    </span>
  </li>`;
}

function draw(): void {
  const el = root;
  if (!el || !route) return;
  const list = library.history();
  const pages = Math.min(50, Math.max(1, parseInt(route.query.n || '1', 10) || 1));
  const shown = list.slice(0, pages * PAGE);
  const more = list.length - shown.length;
  render(
    el,
    html`<div class="page page-narrow">
      ${pageHead(
        'Lịch sử đọc',
        list.length ? `${fmtNum(list.length)} truyện` : undefined,
        list.length ? html`<button type="button" class="btn btn-danger-ghost" data-clear>${icon('trash')}<span>Xoá tất cả</span></button>` : undefined,
      )}
      ${list.length
        ? html`<ul class="rows">
              ${shown.map(row)}
            </ul>
            ${more > 0
              ? html`<div class="more-row"><button type="button" class="btn" data-more>Xem thêm ${fmtNum(Math.min(PAGE, more))} truyện</button><span class="muted">Đang hiện ${fmtNum(shown.length)} / ${fmtNum(list.length)}</span></div>`
              : ''}`
        : stateView({ icon: 'history', title: 'Chưa có lịch sử đọc', message: 'Truyện bạn mở sẽ xuất hiện ở đây để đọc tiếp đúng chương đang dở.', home: true })}
    </div>`,
  );
  hydrateCovers(el);
}

async function onClick(e: Event): Promise<void> {
  const t = e.target as Element;
  const rm = t.closest<HTMLElement>('[data-remove]');
  if (rm) {
    const [source, ...rest] = (rm.dataset.remove as string).split('|');
    const key = rest.join('|');
    const old = progress.get(source as string, key);
    library.removeHistory(source as string, key);
    toast({
      message: `Đã xoá “${old?.name || key}” khỏi lịch sử.`,
      action: old ? { label: 'Hoàn tác', run: () => void progress.update(old, { now: true }) } : undefined,
    });
    return;
  }
  if (t.closest('[data-more]')) {
    setQuery({ n: Math.max(1, parseInt(route?.query.n || '1', 10) || 1) + 1 });
    return;
  }
  if (t.closest('[data-clear]')) {
    const ok = await confirmDialog({
      title: 'Xoá toàn bộ lịch sử đọc?',
      message: 'Vị trí đang đọc của mọi truyện sẽ bị xoá khỏi thiết bị này. Thao tác này không hoàn tác được.',
      confirmLabel: 'Xoá tất cả',
      cancelLabel: 'Giữ lại',
      danger: true,
    });
    if (ok) {
      library.clearHistory();
      toast('Đã xoá lịch sử đọc.');
    }
  }
}
const click = (e: Event): void => void onClick(e);

export function mount(el: HTMLElement, r: Route, ctx: ViewContext): void {
  root = el;
  route = r;
  ctx.setTitle('Lịch sử đọc');
  setCrumbs([{ label: 'Lịch sử đọc' }]);
  draw();
  el.addEventListener('click', click);
  off = [on('progress', draw)];
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
