/**
 * Home: continue reading first, then followed stories, then one section per source (at most 12 items each with
 * a "Xem tất cả" link). Never more than a few hundred DOM nodes, whatever the size of the library.
 */
import { backend } from '../core/backend/index';
import type { Route, Source, ViewContext } from '../core/contracts';
import { hydrateCovers } from '../core/covers';
import { data, isAbort } from '../core/data';
import { on } from '../core/events';
import { fmtNum, repoLabel } from '../core/format';
import { html, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { library } from '../core/library';
import { href } from '../core/router';
import { showError, skeleton } from '../core/ui';
import { openSettings, setCrumbs } from '../shell';
import { continueCard, repoTile, sectionHead, storyCard } from './cards';

const SHELF = 12;
let off: (() => void)[] = [];

function personalShelves(): SafeHtml {
  const hist = library.history();
  const fol = library.follows();
  const parts: SafeHtml[] = [];
  if (hist.length) {
    parts.push(html`<section class="section" aria-labelledby="h-continue">
      ${sectionHead({ id: 'h-continue', title: 'Đọc tiếp', more: hist.length > SHELF ? { href: href.history(), aria: 'Xem tất cả lịch sử đọc' } : undefined })}
      <div class="shelf">${hist.slice(0, SHELF).map(continueCard)}</div>
    </section>`);
  }
  if (fol.length) {
    parts.push(html`<section class="section" aria-labelledby="h-follow">
      ${sectionHead({ id: 'h-follow', title: 'Đang theo dõi', count: fol.length })}
      <div class="shelf">
        ${fol.slice(0, SHELF).map((f) => storyCard({ ...f, synopsis: '', genres: [], tags: [], status: null, declared_chapters: null, link: null }, f.source))}
      </div>
    </section>`);
  }
  return html`${parts}`;
}

function hero(first: boolean): SafeHtml {
  if (!first) return html`<h1 class="sr-only">MythLab: đọc và nghe truyện</h1>`;
  return html`<section class="hero" aria-labelledby="h-hero">
    <h1 id="h-hero" class="hero-title">Đọc và nghe truyện theo cách của bạn</h1>
    <p class="hero-text">Chọn một truyện bên dưới để bắt đầu. MythLab nhớ chương bạn đang đọc, đổi được phông chữ, màu nền và có thể đọc thành tiếng.</p>
  </section>`;
}

function sourceSection(s: Source, i: number): SafeHtml {
  const id = `h-src-${i}`;
  if (s.kind === 'github' && s.repos) {
    const repos = [...s.repos].sort((a, b) => String(b.pushed_at || '').localeCompare(String(a.pushed_at || '')));
    const newest = repos[0];
    return html`${newest
        ? html`<section class="section" aria-labelledby="${id}-new">
            ${sectionHead({
              id: `${id}-new`,
              title: `Mới cập nhật: ${repoLabel(newest.repo)}`,
              more: { href: href.lib(s.id, newest.repo), aria: `Xem tất cả truyện trong ${repoLabel(newest.repo)}` },
            })}
            <div class="shelf" data-shelf="${s.id}" data-repo="${newest.repo}">${skeleton.cards(6, 'shelf-sk')}</div>
          </section>`
        : ''}
      <section class="section" aria-labelledby="${id}">
        ${sectionHead({
          id,
          title: s.name,
          count: repos.length,
          more: { href: href.lib(s.id), label: repos.length > SHELF ? `Xem tất cả ${fmtNum(repos.length)} kho` : 'Xem tất cả', aria: `Xem tất cả kho truyện của ${s.name}` },
        })}
        ${repos.length
          ? html`<div class="tiles">${repos.slice(0, SHELF).map((r) => repoTile(s.id, r))}</div>`
          : html`<p class="muted">Nguồn này chưa có kho truyện nào.</p>`}
      </section>`;
  }
  return html`<section class="section" aria-labelledby="${id}">
    ${sectionHead({ id, title: s.name, more: { href: href.lib(s.id), aria: `Xem tất cả truyện của ${s.name}` } })}
    <div class="shelf" data-shelf="${s.id}">${skeleton.cards(6, 'shelf-sk')}</div>
  </section>`;
}

async function fillShelf(box: HTMLElement, signal: AbortSignal): Promise<void> {
  const source = box.dataset.shelf as string;
  const repo = box.dataset.repo || null;
  try {
    const list = await data.stories(source, repo, { signal });
    if (signal.aborted) return;
    if (!list.length) {
      render(box, html`<p class="muted shelf-note">Chưa có truyện nào.</p>`);
      return;
    }
    render(box, html`${list.slice(0, SHELF).map((s) => storyCard(s, source))}`);
    hydrateCovers(box);
  } catch (e) {
    if (isAbort(e) || signal.aborted) return;
    render(box, html`<p class="muted shelf-note">Không tải được danh sách truyện. <button type="button" class="link-btn" data-retry>Thử lại</button></p>`);
    box.querySelector('[data-retry]')?.addEventListener('click', () => {
      data.invalidate('stories:');
      render(box, skeleton.cards(6, 'shelf-sk'));
      void fillShelf(box, signal);
    });
  }
}

export async function mount(el: HTMLElement, _route: Route, ctx: ViewContext): Promise<void> {
  ctx.setTitle('');
  setCrumbs([]);
  const first = library.history().length === 0;
  render(
    el,
    html`<div class="page page-home">
      ${first ? '' : hero(false)}
      <div id="home-personal">${personalShelves()}</div>
      ${first ? hero(true) : ''}
      <div id="home-sources">${skeleton.view(html`<div class="section"><div class="sk sk-title"></div>${skeleton.cards(6, 'shelf')}</div>`)}</div>
    </div>`,
  );
  hydrateCovers(el);
  const personal = el.querySelector<HTMLElement>('#home-personal') as HTMLElement;
  const refreshPersonal = (): void => {
    render(personal, personalShelves());
    hydrateCovers(personal);
  };
  off = [on('follows', refreshPersonal), on('progress', (e) => e.key === null && refreshPersonal())];

  const box = el.querySelector<HTMLElement>('#home-sources') as HTMLElement;
  const load = async (): Promise<void> => {
    try {
      const j = await data.sources({ signal: ctx.signal });
      if (ctx.signal.aborted) return;
      const ok = j.sources.filter((s) => s.available);
      const offl = j.sources.filter((s) => !s.available);
      if (!ok.length) {
        render(
          box,
          html`<section class="state">
            <div class="state-ic">${icon('inbox')}</div>
            <h2 class="state-title">Chưa có nguồn truyện nào sẵn sàng</h2>
            <p class="state-msg">
              ${backend.kind === 'github' ? 'Tài khoản GitHub này chưa có kho truyện phù hợp.' : 'Máy chủ chưa tìm thấy thư mục truyện nào.'} Bạn có thể đổi nguồn truyện
              trong phần Cài đặt.
            </p>
            <div class="state-actions"><button type="button" class="btn btn-primary" data-settings>${icon('settings')}<span>Mở Cài đặt</span></button></div>
          </section>`,
        );
        box.querySelector('[data-settings]')?.addEventListener('click', () => openSettings('source'));
        return;
      }
      render(
        box,
        html`${ok.map(sourceSection)}
        ${offl.length
          ? html`<p class="muted home-off">Nguồn chưa sẵn sàng: ${offl.map((s) => s.name).join(', ')}.</p>`
          : ''}`,
      );
      for (const shelf of Array.from(box.querySelectorAll<HTMLElement>('[data-shelf]'))) void fillShelf(shelf, ctx.signal);
    } catch (e) {
      if (isAbort(e) || ctx.signal.aborted) return;
      showError(box, e, () => {
        data.invalidate();
        render(box, skeleton.view(skeleton.cards(6, 'shelf')));
        void load();
      });
    }
  };
  await load();
}

export function unmount(): void {
  for (const f of off) f();
  off = [];
}
