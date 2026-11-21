/**
 * Global search results: `#/search?q=…`. The query comes from the search box in the top bar (shell.ts keeps the
 * two in sync). Uses the server index when there is one, otherwise searches the story lists the browser knows
 * and offers to load the rest.
 */
import type { Route, ViewContext } from '../core/contracts';
import { hydrateCovers } from '../core/covers';
import { data, isAbort, type SearchResult } from '../core/data';
import { fmtNum } from '../core/format';
import { html, render } from '../core/html';
import { icon } from '../core/icons';
import { href, navigate, setQuery } from '../core/router';
import { announce, showError, skeleton, stateView } from '../core/ui';
import { setCrumbs } from '../shell';
import { pageHead, storyCard } from './cards';

const PAGE = 24;

let ctx: ViewContext | null = null;
let root: HTMLElement | null = null;
let seq = 0;
let indexing: AbortController | null = null;

function focusSearchBox(): void {
  const toggle = document.getElementById('search-toggle');
  if (toggle && getComputedStyle(toggle).display !== 'none') toggle.click();
  else document.getElementById('q')?.focus();
}

function partialNote(res: SearchResult): ReturnType<typeof html> {
  const ix = res.indexed;
  if (!res.partial || !ix) return html``;
  return html`<div class="notice notice-row" id="search-partial">
    <span>Mới tìm trong ${fmtNum(ix.repos)} / ${fmtNum(ix.reposTotal)} kho truyện đã mở.</span>
    <button type="button" class="btn btn-sm" data-index-all>Tìm trong tất cả kho</button>
  </div>`;
}

async function run(r: Route): Promise<void> {
  const el = root;
  const c = ctx;
  if (!el || !c) return;
  const my = ++seq;
  indexing?.abort();
  indexing = null;
  const q = (r.query.q || '').trim();
  const pages = Math.min(20, Math.max(1, parseInt(r.query.n || '1', 10) || 1));
  c.setTitle(q ? `Tìm “${q}”` : 'Tìm truyện');
  setCrumbs([{ label: 'Tìm truyện' }]);
  if (!q) {
    render(
      el,
      html`<div class="page">
        ${pageHead('Tìm truyện')}
        ${stateView({
          icon: 'search',
          title: 'Bạn muốn đọc gì hôm nay?',
          message: 'Gõ tên truyện, tác giả hoặc thể loại vào ô tìm kiếm. Không cần gõ dấu.',
          actions: html`<button type="button" class="btn btn-primary" data-focus-search>${icon('search')}<span>Tìm truyện</span></button>`,
        })}
      </div>`,
    );
    el.querySelector('[data-focus-search]')?.addEventListener('click', focusSearchBox);
    return;
  }
  if (!el.querySelector('#search-body')) {
    render(el, html`<div class="page">${pageHead(`Kết quả cho “${q}”`, 'Đang tìm…')}<div id="search-body">${skeleton.view(skeleton.cards(12))}</div></div>`);
  } else {
    (el.querySelector('.page-title') as HTMLElement).textContent = `Kết quả cho “${q}”`;
  }
  const body = el.querySelector<HTMLElement>('#search-body') as HTMLElement;
  const sub = el.querySelector<HTMLElement>('.page-sub');
  try {
    const res = await data.search(q, { limit: pages * PAGE, offset: 0, signal: c.signal });
    if (my !== seq || c.signal.aborted) return;
    if (sub) sub.textContent = res.total ? `${fmtNum(res.total)} truyện` : 'Không có kết quả';
    announce(res.total ? `Tìm thấy ${fmtNum(res.total)} truyện` : `Không tìm thấy truyện nào cho ${q}`);
    if (!res.items.length) {
      render(
        body,
        html`${stateView({
          icon: 'search',
          title: `Không tìm thấy truyện nào cho “${q}”`,
          message: 'Kiểm tra lại chính tả hoặc thử từ khoá ngắn hơn. Không cần gõ dấu.',
          actions: html`<button type="button" class="btn" data-clear-search>${icon('close')}<span>Xoá từ khoá</span></button>`,
          home: true,
        })}
        ${partialNote(res)}`,
      );
    } else {
      const more = res.total - res.items.length;
      render(
        body,
        html`${partialNote(res)}
          <div class="grid">${res.items.map((s) => storyCard(s, s.source || '', { showRepo: true }))}</div>
          ${more > 0
            ? html`<div class="more-row"><button type="button" class="btn" data-more>Xem thêm ${fmtNum(Math.min(PAGE, more))} truyện</button><span class="muted">Đang hiện ${fmtNum(res.items.length)} / ${fmtNum(res.total)}</span></div>`
            : ''}`,
      );
      hydrateCovers(body);
    }
    body.querySelector('[data-more]')?.addEventListener('click', () => setQuery({ n: pages + 1 }));
    body.querySelector('[data-clear-search]')?.addEventListener('click', () => {
      const input = document.getElementById('q') as HTMLInputElement | null;
      if (input) input.value = '';
      navigate(href.search(''), { replace: true });
      focusSearchBox();
    });
    body.querySelector('[data-index-all]')?.addEventListener('click', () => {
      const note = body.querySelector<HTMLElement>('#search-partial');
      if (!note) return;
      const ctl = (indexing = new AbortController());
      c.signal.addEventListener('abort', () => ctl.abort(), { once: true });
      render(note, html`<span data-progress role="status">Đang mở các kho truyện…</span><button type="button" class="btn btn-sm" data-stop>Dừng</button>`);
      const label = note.querySelector('[data-progress]') as HTMLElement;
      note.querySelector('[data-stop]')?.addEventListener('click', () => {
        ctl.abort();
        void run(r);
      });
      data
        .indexAll({
          signal: ctl.signal,
          onProgress: (done, total) => {
            label.textContent = `Đang mở các kho truyện… ${fmtNum(done)} / ${fmtNum(total)}`;
          },
        })
        .then(
          () => my === seq && void run(r),
          () => {},
        );
    });
  } catch (e) {
    if (isAbort(e) || my !== seq || c.signal.aborted) return;
    if (sub) sub.textContent = '';
    showError(body, e, () => {
      data.invalidate('search:');
      render(body, skeleton.view(skeleton.cards(12)));
      void run(r);
    });
  }
}

export function mount(el: HTMLElement, r: Route, c: ViewContext): Promise<void> {
  ctx = c;
  root = el;
  return run(r);
}

export function update(r: Route): void {
  // an empty query replaces the result page with the prompt, and the other way round
  if (root && !(r.query.q || '').trim()) root.replaceChildren();
  else if (root && !root.querySelector('#search-body')) root.replaceChildren();
  void run(r);
}

export function unmount(): void {
  seq++;
  indexing?.abort();
  indexing = null;
  ctx = null;
  root = null;
}
