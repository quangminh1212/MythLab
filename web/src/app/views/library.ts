/**
 * Library: `#/lib/<source>` lists the repositories of a GitHub source (filterable) or the stories of a local
 * source; `#/lib/<source>/<repo>` and `#/lib/<source>/*` list stories with search, status / tag filters, sorting
 * and incremental paging. Every piece of view state lives in the hash query (q, status, tag, sort, n), so
 * back/forward and shared links restore it.
 */
import { backend } from '../core/backend/index';
import type { Route, Source, ViewContext } from '../core/contracts';
import { hydrateCovers } from '../core/covers';
import { data, isAbort, type StoryPage, type StorySort } from '../core/data';
import { debounce } from '../core/events';
import { fmtNum, matchTokens, normKey, repoLabel, sKey, tokens, viCompare } from '../core/format';
import { html, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { progress } from '../core/progress';
import { href, setQuery } from '../core/router';
import { announce, showError, skeleton, stateView } from '../core/ui';
import { setCrumbs } from '../shell';
import { pageHead, repoTile, storyCard } from './cards';

const PAGE = 48;
const TAG_CHIPS = 14;

let ctx: ViewContext | null = null;
let root: HTMLElement | null = null;
let route: Route | null = null;
let source: Source | null = null;
let seq = 0;

const SORTS: [StorySort, string][] = [
  ['name', 'Tên A-Z'],
  ['chapters', 'Nhiều chương nhất'],
  ['updated', 'Mới cập nhật'],
  ['recent', 'Đọc gần đây'],
];

const isSort = (v: string | undefined): v is StorySort => SORTS.some(([k]) => k === v);

// ---------------------------------------------------------------- repository list

function repoGrid(s: Source, r: Route): SafeHtml {
  const q = r.query.q || '';
  const toks = tokens(q);
  const byDate = r.query.sort === 'updated';
  let list = (s.repos || []).filter((x) => !toks.length || matchTokens(normKey(repoLabel(x.repo) + ' ' + x.repo), toks));
  list = [...list].sort((a, b) => (byDate ? String(b.pushed_at || '').localeCompare(String(a.pushed_at || '')) : 0) || viCompare(repoLabel(a.repo), repoLabel(b.repo)));
  if (!list.length) {
    return stateView({
      title: q ? `Không có kho nào khớp “${q}”` : 'Nguồn này chưa có kho truyện nào',
      message: q ? 'Thử từ khoá khác hoặc xoá bộ lọc.' : undefined,
      actions: q ? html`<button type="button" class="btn" data-clear>Xoá bộ lọc</button>` : undefined,
    });
  }
  return html`<div class="tiles tiles-all">${list.map((x) => repoTile(s.id, x))}</div>`;
}

function mountRepos(el: HTMLElement, s: Source, r: Route): void {
  const total = s.repos?.length || 0;
  render(
    el,
    html`<div class="page">
      ${pageHead(s.name, `${fmtNum(total)} kho truyện`)}
      ${s.stale ? html`<p class="notice">Danh sách kho có thể chưa mới nhất do nguồn đang giới hạn truy cập.</p>` : ''}
      <div class="toolbar">
        <div class="field field-grow">
          <label class="sr-only" for="lib-q">Lọc kho truyện</label>
          <span class="field-ic">${icon('filter')}</span>
          <input id="lib-q" class="input input-ic" type="search" placeholder="Lọc kho truyện…" autocomplete="off" spellcheck="false" value="${r.query.q || ''}" />
        </div>
        <div class="field">
          <label class="sr-only" for="lib-sort">Sắp xếp</label>
          <select id="lib-sort" class="select">
            <option value="name" ${r.query.sort !== 'updated' ? html`selected` : ''}>Tên A-Z</option>
            <option value="updated" ${r.query.sort === 'updated' ? html`selected` : ''}>Mới cập nhật</option>
          </select>
        </div>
      </div>
      <div id="lib-body">${repoGrid(s, r)}</div>
    </div>`,
  );
  const input = el.querySelector<HTMLInputElement>('#lib-q') as HTMLInputElement;
  input.addEventListener(
    'input',
    debounce(() => setQuery({ q: input.value.trim() || null }), 150),
  );
  (el.querySelector('#lib-sort') as HTMLSelectElement).addEventListener('change', (e) => setQuery({ sort: (e.target as HTMLSelectElement).value === 'updated' ? 'updated' : null }));
  el.addEventListener('click', onClear);
}

function onClear(e: Event): void {
  if (!(e.target as Element).closest('[data-clear]')) return;
  setQuery({ q: null, status: null, tag: null });
}

// ---------------------------------------------------------------- story list

function recentOf(sourceId: string): (key: string) => number {
  const m = new Map<string, number>();
  for (const p of progress.all()) if (p.source === sourceId) m.set(sKey(p.source, p.key), p.ts || 0);
  return (key) => m.get(sKey(sourceId, key)) || 0;
}

function filtersBar(r: Route, page: StoryPage | null): SafeHtml {
  const sort = isSort(r.query.sort) ? r.query.sort : 'name';
  const status = r.query.status || '';
  const tag = r.query.tag || '';
  const statuses = page ? [...new Set([...page.statuses, ...(status ? [status] : [])])] : status ? [status] : [];
  const tags = page ? page.tags.slice(0, TAG_CHIPS) : [];
  if (tag && !tags.some((t) => normKey(t.name) === normKey(tag))) tags.unshift({ name: tag, count: 0 });
  return html`<div class="toolbar">
      <div class="field field-grow">
        <label class="sr-only" for="lib-q">Tìm trong danh sách</label>
        <span class="field-ic">${icon('search')}</span>
        <input id="lib-q" class="input input-ic" type="search" placeholder="Tìm trong danh sách…" autocomplete="off" spellcheck="false" value="${r.query.q || ''}" />
      </div>
      ${statuses.length
        ? html`<div class="field">
            <label class="sr-only" for="lib-status">Trạng thái</label>
            <select id="lib-status" class="select">
              <option value="">Mọi trạng thái</option>
              ${statuses.map((s) => html`<option value="${s}" ${normKey(s) === normKey(status) ? html`selected` : ''}>${s}</option>`)}
            </select>
          </div>`
        : ''}
      <div class="field">
        <label class="sr-only" for="lib-sort">Sắp xếp</label>
        <select id="lib-sort" class="select">
          ${SORTS.map(([k, label]) => html`<option value="${k}" ${k === sort ? html`selected` : ''}>${label}</option>`)}
        </select>
      </div>
    </div>
    ${tags.length
      ? html`<div class="chips" role="group" aria-label="Lọc theo thể loại">
          ${tags.map((t) => {
            const on = normKey(t.name) === normKey(tag);
            return html`<button type="button" class="chip" data-tag="${t.name}" aria-pressed="${on ? 'true' : 'false'}">${t.name}${t.count ? html` <span class="chip-n">${fmtNum(t.count)}</span>` : ''}</button>`;
          })}
        </div>`
      : ''}`;
}

async function loadStories(): Promise<void> {
  const el = root;
  const r = route;
  const c = ctx;
  const s = source;
  if (!el || !r || !c || !s) return;
  const my = ++seq;
  const body = el.querySelector<HTMLElement>('#lib-body');
  const bar = el.querySelector<HTMLElement>('#lib-filters');
  if (!body || !bar) return;
  const repo = r.repo && r.repo !== '*' ? r.repo : null;
  const pages = Math.min(40, Math.max(1, parseInt(r.query.n || '1', 10) || 1));
  const sort = isSort(r.query.sort) ? r.query.sort : 'name';
  try {
    const page = await data.queryStories({
      source: s.id,
      repo,
      q: r.query.q,
      status: r.query.status,
      tag: r.query.tag,
      sort,
      offset: 0,
      limit: pages * PAGE,
      recentOf: recentOf(s.id),
      signal: c.signal,
    });
    if (my !== seq || c.signal.aborted) return;
    // keep the search box (and its caret) while the user is typing in it
    const typing = document.activeElement?.id === 'lib-q';
    if (!typing) {
      render(bar, filtersBar(r, page));
      bindFilters(el);
    } else {
      const chips = bar.querySelector('.chips');
      const fresh = document.createElement('div');
      render(fresh, filtersBar(r, page));
      const next = fresh.querySelector('.chips');
      if (chips && next) chips.replaceWith(next);
    }
    const sub = el.querySelector('.page-sub');
    if (sub) sub.textContent = page.total === page.all ? `${fmtNum(page.all)} truyện` : `${fmtNum(page.total)} / ${fmtNum(page.all)} truyện`;
    announce(`${fmtNum(page.total)} truyện`);
    if (!page.items.length) {
      const filtered = !!(r.query.q || r.query.status || r.query.tag);
      render(
        body,
        stateView({
          title: filtered ? 'Không có truyện nào khớp bộ lọc' : 'Chưa có truyện nào ở đây',
          message: filtered ? 'Thử từ khoá khác hoặc xoá bộ lọc.' : undefined,
          actions: filtered ? html`<button type="button" class="btn" data-clear>Xoá bộ lọc</button>` : undefined,
          home: !filtered,
        }),
      );
      return;
    }
    const more = page.total - page.items.length;
    render(
      body,
      html`${page.stale ? html`<p class="notice">Danh sách có thể chưa đầy đủ vì nguồn đang giới hạn truy cập; sẽ tự đầy đủ khi tải lại sau ít phút.</p>` : ''}<div class="grid">${page.items.map((x) => storyCard(x, s.id, { showRepo: !repo && s.kind === 'github' }))}</div>
        ${more > 0
          ? html`<div class="more-row"><button type="button" class="btn" data-more>Xem thêm ${fmtNum(Math.min(PAGE, more))} truyện</button><span class="muted">Đang hiện ${fmtNum(page.items.length)} / ${fmtNum(page.total)}</span></div>`
          : ''}`,
    );
    hydrateCovers(body);
    body.querySelector('[data-more]')?.addEventListener('click', () => setQuery({ n: pages + 1 }));
  } catch (e) {
    if (isAbort(e) || my !== seq || c.signal.aborted) return;
    showError(body, e, () => {
      data.invalidate('stories:');
      data.invalidate('page:');
      render(body, skeleton.view(skeleton.cards(12)));
      void loadStories();
    });
  }
}

function bindFilters(el: HTMLElement): void {
  const input = el.querySelector<HTMLInputElement>('#lib-q');
  if (input && !input.dataset.bound) {
    input.dataset.bound = '1';
    input.addEventListener(
      'input',
      debounce(() => setQuery({ q: input.value.trim() || null, n: null }), 200),
    );
  }
  el.querySelector<HTMLSelectElement>('#lib-sort')?.addEventListener('change', (e) => {
    const v = (e.target as HTMLSelectElement).value;
    setQuery({ sort: v === 'name' ? null : v, n: null });
  });
  el.querySelector<HTMLSelectElement>('#lib-status')?.addEventListener('change', (e) => setQuery({ status: (e.target as HTMLSelectElement).value || null, n: null }));
}

function onChip(e: Event): void {
  const chip = (e.target as Element).closest<HTMLElement>('[data-tag]');
  if (!chip || !route) return;
  const t = chip.dataset.tag || '';
  setQuery({ tag: normKey(route.query.tag || '') === normKey(t) ? null : t, n: null });
}

function mountStories(el: HTMLElement, s: Source, r: Route): void {
  const repo = r.repo && r.repo !== '*' ? r.repo : null;
  const title = repo ? repoLabel(repo) : s.kind === 'github' ? `Tất cả truyện: ${s.name}` : s.name;
  render(
    el,
    html`<div class="page">
      ${pageHead(title, 'Đang tải…')}
      <div id="lib-filters">${filtersBar(r, null)}</div>
      <div id="lib-body">${skeleton.view(skeleton.cards(12))}</div>
    </div>`,
  );
  bindFilters(el);
  el.addEventListener('click', onChip);
  el.addEventListener('click', onClear);
  void loadStories();
}

// ---------------------------------------------------------------- view

/** A GitHub source without a repository shows its repositories, unless the server can page the whole source. */
const showsRepos = (s: Source, r: Route): boolean => s.kind === 'github' && (!r.repo || (r.repo === '*' && backend.api < 2));

export async function mount(el: HTMLElement, r: Route, c: ViewContext): Promise<void> {
  ctx = c;
  root = el;
  route = r;
  source = null;
  const sid = r.source as string;
  const repo = r.repo && r.repo !== '*' ? r.repo : null;
  c.setTitle(repo ? repoLabel(repo) : 'Kho truyện');
  setCrumbs([{ label: repo ? repoLabel(repo) : 'Kho truyện' }]);
  render(el, html`<div class="page">${skeleton.view(html`<div class="sk sk-title"></div>${skeleton.cards(12)}`)}</div>`);
  let list: Source[];
  try {
    list = (await data.sources({ signal: c.signal })).sources;
  } catch (e) {
    if (isAbort(e) || c.signal.aborted) return;
    showError(el, e, () => {
      data.invalidate();
      void mount(el, r, c);
    });
    return;
  }
  if (c.signal.aborted) return;
  const s = list.find((x) => x.id === sid);
  if (!s || !s.available) {
    render(
      el,
      stateView({
        h1: true,
        kind: 'error',
        icon: 'inbox',
        title: s ? 'Nguồn truyện này hiện không dùng được' : 'Không tìm thấy nguồn truyện',
        message: s ? s.error || 'Thư mục hoặc kho của nguồn này chưa sẵn sàng.' : 'Đường dẫn không đúng hoặc nguồn đã bị gỡ.',
        home: true,
      }),
    );
    c.setTitle('Không tìm thấy');
    setCrumbs([{ label: 'Không tìm thấy' }]);
    return;
  }
  source = s;
  if (showsRepos(s, r)) {
    c.setTitle(s.name);
    setCrumbs([{ label: s.name }]);
    mountRepos(el, s, r);
    return;
  }
  if (repo) {
    c.setTitle(repoLabel(repo));
    setCrumbs([{ label: s.name, href: href.lib(s.id) }, { label: repoLabel(repo) }]);
  } else {
    c.setTitle(s.name);
    setCrumbs(s.kind === 'github' ? [{ label: s.name, href: href.lib(s.id) }, { label: 'Tất cả truyện' }] : [{ label: s.name }]);
  }
  mountStories(el, s, r);
}

/** Query-only change (filter, sort, paging): re-render the list, keep the page and the focused control. */
export function update(r: Route): void {
  route = r;
  const el = root;
  const s = source;
  if (!el || !s) return;
  if (showsRepos(s, r)) {
    const body = el.querySelector<HTMLElement>('#lib-body');
    if (body) render(body, repoGrid(s, r));
    const input = el.querySelector<HTMLInputElement>('#lib-q');
    if (input && document.activeElement !== input) input.value = r.query.q || '';
    return;
  }
  const input = el.querySelector<HTMLInputElement>('#lib-q');
  if (input && document.activeElement !== input) input.value = r.query.q || '';
  void loadStories();
}

export function unmount(): void {
  root?.removeEventListener('click', onChip);
  root?.removeEventListener('click', onClear);
  seq++;
  ctx = null;
  root = null;
  route = null;
  source = null;
}
