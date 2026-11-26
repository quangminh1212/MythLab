/**
 * Story page: cover, metadata, synopsis, the primary actions (Đọc tiếp / Đọc từ đầu / Nghe / Theo dõi / Tải về)
 * and the chapter list: virtualised, column-major inside blocks of ten rows, with search, numeric jump, sort
 * toggle and read / current state.
 */
import { copyText } from '../core/export-file';
import type { ChapterRef, Progress, Route, StoryDetail, ViewContext } from '../core/contracts';
import { cover, hydrateCovers } from '../core/covers';
import { data, isAbort } from '../core/data';
import { debounce, on } from '../core/events';
import { chapterLabel, fmtDate, fmtNum, matchTokens, normKey, repoLabel, sKey, tokens } from '../core/format';
import { html, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { library } from '../core/library';
import { progress } from '../core/progress';
import { href, setQuery } from '../core/router';
import { announce, showError, skeleton, toast, virtualList, type VirtualListHandle } from '../core/ui';
import { setCrumbs } from '../shell';

const ROW_H = 48;
/** Rows per block: inside a block the chapters run down the first column, then the next. */
const BLOCK_ROWS = 10;

interface State {
  el: HTMLElement;
  ctx: ViewContext;
  route: Route;
  st: StoryDetail;
  /** Positions → chapter indices after search and sorting. */
  order: number[];
  cols: number;
  list: VirtualListHandle | null;
  labels: string[];
  keys: string[] | null;
  download: AbortController | null;
  /** The offline change listener is attached (once per mounted story). */
  watching?: boolean;
}
let state: State | null = null;
let off: (() => void)[] = [];

// ---------------------------------------------------------------- chapter grid layout

export const colsFor = (width: number): number => (width >= 980 ? 3 : width >= 620 ? 2 : 1);

export function rowCount(n: number, cols: number): number {
  const block = cols * BLOCK_ROWS;
  const full = Math.floor(n / block);
  return full * BLOCK_ROWS + Math.ceil((n - full * block) / cols);
}
/** Position in `order` shown at (row, col), or -1 for an empty cell. */
export function posAt(row: number, col: number, n: number, cols: number): number {
  const block = cols * BLOCK_ROWS;
  const b = Math.floor(row / BLOCK_ROWS);
  const base = b * block;
  const m = Math.min(block, n - base);
  if (m <= 0) return -1;
  const rows = Math.ceil(m / cols);
  const p = base + col * rows + (row % BLOCK_ROWS);
  return row % BLOCK_ROWS < rows && p < base + m ? p : -1;
}
export function rowOf(pos: number, n: number, cols: number): number {
  const block = cols * BLOCK_ROWS;
  const b = Math.floor(pos / block);
  const base = b * block;
  const rows = Math.ceil(Math.min(block, n - base) / cols);
  return b * BLOCK_ROWS + ((pos - base) % rows);
}

// ---------------------------------------------------------------- rendering

function readState(s: State): { p: Progress | null; cur: number; max: number } {
  const p = progress.get(s.st.source, s.st.key);
  if (!p) return { p: null, cur: -1, max: -1 };
  const cur = progress.resolveIdx(p, s.st.chapters);
  return { p, cur, max: Math.max(cur, Math.min(s.st.chapters.length - 1, p.maxIdx ?? p.idx)) };
}

function chapterRow(s: State, row: number): SafeHtml {
  const { cur, max } = readState(s);
  const n = s.order.length;
  const cells: SafeHtml[] = [];
  for (let c = 0; c < s.cols; c++) {
    const pos = posAt(row, c, n, s.cols);
    if (pos < 0) {
      cells.push(html`<span class="ch ch-empty"></span>`);
      continue;
    }
    const idx = s.order[pos] as number;
    const isCur = idx === cur;
    const cls = isCur ? 'ch is-current' : idx <= max ? 'ch is-read' : 'ch';
    cells.push(
      html`<a class="${cls}" href="${href.read(s.st.source, s.st.key, idx)}" data-idx="${idx}" ${isCur ? html`aria-current="true"` : ''}>
        <span class="ch-label">${s.labels[idx] as string}</span>${isCur ? html`<span class="badge badge-accent">Đang đọc</span>` : ''}
      </a>`,
    );
  }
  return html`<div class="ch-row${row % BLOCK_ROWS === 0 && row > 0 ? ' ch-row-first' : ''}" data-cols="${s.cols}">${cells}</div>`;
}

function actions(s: State): SafeHtml {
  const { st } = s;
  const { p, cur } = readState(s);
  const has = st.chapters.length > 0;
  const curCh = cur >= 0 ? (st.chapters[cur] as ChapterRef) : null;
  const followed = library.isFollowed(st.source, st.key);
  return html`${has
      ? p && curCh
        ? html`<a class="btn btn-primary btn-lg" href="${href.read(st.source, st.key, cur)}" data-act="continue">${icon('book')}<span>Đọc tiếp · Chương ${fmtNum(curCh.n)}</span></a>
            <a class="btn btn-lg" href="${href.read(st.source, st.key, 0)}" data-act="start">Đọc từ đầu</a>`
        : html`<a class="btn btn-primary btn-lg" href="${href.read(st.source, st.key, 0)}" data-act="start">${icon('book')}<span>Bắt đầu đọc</span></a>`
      : ''}
    ${has ? html`<button type="button" class="btn btn-lg" data-act="listen">${icon('headphones')}<span>Nghe</span></button>` : ''}
    <button type="button" class="btn btn-lg" data-act="follow" aria-pressed="${followed ? 'true' : 'false'}">${icon('heart')}<span>${followed ? 'Đang theo dõi' : 'Theo dõi'}</span></button>
    ${has ? html`<button type="button" class="btn btn-lg" data-act="download">${icon('download')}<span data-dl-label>Tải về</span></button>` : ''}
    <button type="button" class="btn btn-lg btn-icon-only" data-act="copy" aria-label="Sao chép liên kết truyện" title="Sao chép liên kết">${icon('link')}</button>`;
}

function meta(st: StoryDetail): SafeHtml {
  const group = st.key.includes('/') ? (st.key.split('/')[0] as string) : null;
  const tags = [...new Set([...(st.genres || []), ...(st.tags || [])].filter(Boolean))].slice(0, 16);
  const last = st.chapters[st.chapters.length - 1];
  const rows: SafeHtml[] = [];
  if (st.author) rows.push(html`<div class="meta-row"><dt>Tác giả</dt><dd>${st.author}</dd></div>`);
  if (st.status) rows.push(html`<div class="meta-row"><dt>Trạng thái</dt><dd>${st.status}</dd></div>`);
  rows.push(html`<div class="meta-row"><dt>Số chương</dt><dd>${fmtNum(st.chapters.length)}</dd></div>`);
  if (group) rows.push(html`<div class="meta-row"><dt>Kho</dt><dd><a class="link" href="${href.lib(st.source, group)}">${repoLabel(group)}</a></dd></div>`);
  if (st.updated && fmtDate(st.updated)) rows.push(html`<div class="meta-row"><dt>Cập nhật</dt><dd>${fmtDate(st.updated)}</dd></div>`);
  if (last) {
    rows.push(html`<div class="meta-row"><dt>Mới nhất</dt><dd><a class="link" href="${href.read(st.source, st.key, st.chapters.length - 1)}">${chapterLabel(last)}</a></dd></div>`);
  }
  if (st.link && /^https?:\/\//i.test(st.link)) {
    rows.push(html`<div class="meta-row"><dt>Nguồn</dt><dd><a class="link" href="${st.link}" target="_blank" rel="noopener noreferrer">Trang gốc ${icon('external', 'ic-sm')}</a></dd></div>`);
  }
  return html`<dl class="meta">${rows}</dl>
    ${tags.length
      ? html`<ul class="chips chips-static" aria-label="Thể loại">
          ${tags.map((t) => html`<li><a class="chip" href="${href.lib(st.source, group, { tag: t })}">${t}</a></li>`)}
        </ul>`
      : ''}`;
}

function synopsis(st: StoryDetail): SafeHtml {
  const paras = String(st.synopsis || '')
    .split(/\n+/)
    .map((x) => x.trim())
    .filter(Boolean);
  if (!paras.length) return html``;
  return html`<section class="section" aria-labelledby="st-syn">
    <h2 id="st-syn" class="section-title">Giới thiệu</h2>
    <div id="st-syn-text" class="synopsis is-clamped">${paras.map((p) => html`<p>${p}</p>`)}</div>
    <button type="button" class="link-btn" data-act="more" aria-expanded="false" aria-controls="st-syn-text" hidden>Xem thêm</button>
  </section>`;
}

function chapterSection(s: State): SafeHtml {
  const n = s.st.chapters.length;
  if (!n) {
    return html`<section class="section" aria-labelledby="st-ch">
      <h2 id="st-ch" class="section-title">Danh sách chương</h2>
      <p class="muted">Truyện này chưa có chương nào.</p>
    </section>`;
  }
  const desc = s.route.query.order === 'desc';
  const max = s.st.chapters.reduce((m, c) => Math.max(m, c.n), 0);
  return html`<section class="section" aria-labelledby="st-ch">
    <div class="section-head">
      <h2 id="st-ch" class="section-title">Danh sách chương <span class="section-count">${fmtNum(n)}</span></h2>
    </div>
    <div class="toolbar ch-toolbar">
      <div class="field field-grow">
        <label class="sr-only" for="ch-q">Tìm chương theo tên</label>
        <span class="field-ic">${icon('search')}</span>
        <input id="ch-q" class="input input-ic" type="search" placeholder="Tìm chương theo tên…" autocomplete="off" spellcheck="false" />
      </div>
      <form class="field ch-jump" id="ch-jump-form">
        <label class="sr-only" for="ch-jump">Tới chương số</label>
        <input id="ch-jump" class="input" type="number" inputmode="numeric" min="1" max="${max}" placeholder="Chương số…" />
        <button type="submit" class="btn">Tới</button>
      </form>
      <button type="button" class="btn" data-act="order" aria-pressed="${desc ? 'true' : 'false'}" title="Đổi thứ tự chương">${icon('sort')}<span>${desc ? 'Mới nhất trước' : 'Cũ nhất trước'}</span></button>
      <button type="button" class="btn" data-act="goto-current" hidden>${icon('book')}<span>Chương đang đọc</span></button>
    </div>
    <p id="ch-empty" class="muted" hidden>Không có chương nào khớp.</p>
    <div id="ch-list" class="ch-list"></div>
  </section>`;
}

// ---------------------------------------------------------------- behaviour

function applyOrder(s: State, q = ''): void {
  const n = s.st.chapters.length;
  let order = Array.from({ length: n }, (_, i) => i);
  const toks = tokens(q);
  if (toks.length) {
    s.keys ??= s.labels.map((l) => normKey(l));
    const keys = s.keys;
    order = order.filter((i) => matchTokens(keys[i] as string, toks));
  }
  if (s.route.query.order === 'desc') order.reverse();
  s.order = order;
  const empty = s.el.querySelector<HTMLElement>('#ch-empty');
  if (empty) empty.hidden = order.length > 0;
  if (toks.length) announce(order.length ? `${fmtNum(order.length)} chương khớp` : 'Không có chương nào khớp');
}

function buildList(s: State): void {
  const box = s.el.querySelector<HTMLElement>('#ch-list');
  if (!box) return;
  s.cols = colsFor(box.clientWidth || s.el.clientWidth);
  const count = rowCount(s.order.length, s.cols);
  if (s.list) s.list.refresh({ count });
  else s.list = virtualList({ container: box, count, itemHeight: ROW_H, overscan: 8, render: (row) => (state ? chapterRow(state, row) : html``) });
}

/** Scrolls the list to a chapter index and focuses its link. */
function reveal(s: State, idx: number, focus: boolean): void {
  const pos = s.order.indexOf(idx);
  if (pos < 0 || !s.list) return;
  s.list.scrollTo(rowOf(pos, s.order.length, s.cols), 'center');
  requestAnimationFrame(() =>
    requestAnimationFrame(() => {
      const a = s.el.querySelector<HTMLElement>(`#ch-list a[data-idx="${idx}"]`);
      if (!a) return;
      a.classList.add('is-flash');
      setTimeout(() => a.classList.remove('is-flash'), 1600);
      if (focus) a.focus({ preventScroll: true });
    }),
  );
}

function renderActions(s: State): void {
  const box = s.el.querySelector<HTMLElement>('#st-actions');
  if (!box || s.download) return;
  render(box, actions(s));
  const { cur } = readState(s);
  const go = s.el.querySelector<HTMLElement>('[data-act="goto-current"]');
  if (go) go.hidden = cur < 0;
  void refreshOffline(s);
}

async function refreshOffline(s: State): Promise<void> {
  try {
    const { offline } = await import('../offline/index');
    const btn = s.el.querySelector<HTMLButtonElement>('[data-act="download"]');
    if (!btn || state !== s) return;
    if (!s.watching && offline.isAvailable()) {
      s.watching = true;
      off.push(offline.onChange(() => void refreshOffline(s)));
    }
    if (s.download) return;
    if (!offline.isAvailable()) {
      btn.hidden = true;
      return;
    }
    const got = (await offline.storyStatus(s.st.source, s.st.key)).chapters;
    const label = btn.querySelector('[data-dl-label]');
    if (label && state === s && !s.download) label.textContent = got >= s.st.chapters.length ? 'Đã tải về' : got > 0 ? `Tải về (đã có ${fmtNum(got)})` : 'Tải về';
  } catch {
    /* the offline module is optional */
  }
}

async function startDownload(s: State, btn: HTMLButtonElement): Promise<void> {
  void btn;
  try {
    const { openDownloadDialog } = await import('../offline/dialog');
    openDownloadDialog({ source: s.st.source, key: s.st.key, name: s.st.name, chapters: s.st.chapters });
  } catch (e) {
    if (!isAbort(e)) toast({ message: 'Không mở được hộp thoại tải về. Vui lòng thử lại.', kind: 'error' });
  }
}

async function listen(s: State): Promise<void> {
  const { p, cur } = readState(s);
  try {
    const { player } = await import('../player/index');
    if (player.matches(s.st.source, s.st.key)) {
      player.toggle();
      return;
    }
    await player.play({ source: s.st.source, key: s.st.key, idx: Math.max(0, cur), para: p && cur >= 0 ? p.para : 0, story: s.st });
  } catch {
    toast({ message: 'Không mở được trình đọc truyện. Vui lòng thử lại.', kind: 'error' });
  }
}

async function copyLink(): Promise<void> {
  const url = location.href;
  if (await copyText(url)) toast({ message: 'Đã sao chép liên kết.', kind: 'ok' });
  else toast({ message: 'Không sao chép được liên kết.', kind: 'error' });
}

function onClick(e: Event): void {
  const s = state;
  if (!s) return;
  const t = (e.target as Element).closest<HTMLElement>('[data-act]');
  if (!t) return;
  switch (t.dataset.act) {
    case 'listen':
      void listen(s);
      break;
    case 'follow': {
      const now = library.toggleFollow(s.st);
      toast(now ? 'Đã thêm vào danh sách theo dõi.' : 'Đã bỏ theo dõi.');
      break;
    }
    case 'download':
      void startDownload(s, t as HTMLButtonElement);
      break;
    case 'copy':
      void copyLink();
      break;
    case 'more': {
      const box = s.el.querySelector<HTMLElement>('#st-syn-text');
      if (!box) break;
      const open = box.classList.toggle('is-clamped') === false;
      t.setAttribute('aria-expanded', String(open));
      t.textContent = open ? 'Thu gọn' : 'Xem thêm';
      break;
    }
    case 'order':
      setQuery({ order: s.route.query.order === 'desc' ? null : 'desc' });
      break;
    case 'goto-current': {
      const { cur } = readState(s);
      const input = s.el.querySelector<HTMLInputElement>('#ch-q');
      if (input && input.value) {
        input.value = '';
        applyOrder(s);
        buildList(s);
      }
      if (cur >= 0) reveal(s, cur, true);
      break;
    }
    default:
  }
}

function bind(s: State): void {
  const { el } = s;
  el.addEventListener('click', onClick);
  const q = el.querySelector<HTMLInputElement>('#ch-q');
  q?.addEventListener(
    'input',
    debounce(() => {
      if (state !== s) return;
      applyOrder(s, q.value);
      buildList(s);
    }, 120),
  );
  el.querySelector<HTMLFormElement>('#ch-jump-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = el.querySelector<HTMLInputElement>('#ch-jump') as HTMLInputElement;
    const n = parseInt(input.value, 10);
    if (!Number.isFinite(n)) return;
    const chapters = s.st.chapters;
    let idx = chapters.findIndex((c) => c.n === n);
    if (idx < 0) {
      // no chapter carries that number: go to the nearest one
      let best = Infinity;
      chapters.forEach((c, i) => {
        const d = Math.abs(c.n - n);
        if (d < best) {
          best = d;
          idx = i;
        }
      });
      if (idx >= 0) toast(`Không có chương ${fmtNum(n)}. Đã tới ${chapterLabel(chapters[idx])}.`);
    }
    if (idx < 0) return;
    if (q && q.value) {
      q.value = '';
      applyOrder(s);
      buildList(s);
    }
    reveal(s, idx, true);
  });
  const more = el.querySelector<HTMLElement>('[data-act="more"]');
  const syn = el.querySelector<HTMLElement>('#st-syn-text');
  if (more && syn) more.hidden = syn.scrollHeight <= syn.clientHeight + 4;
  if (more?.hidden) syn?.classList.remove('is-clamped');

  let lastCols = s.cols;
  const onResize = debounce(() => {
    if (state !== s) return;
    const box = el.querySelector<HTMLElement>('#ch-list');
    const cols = colsFor(box?.clientWidth || el.clientWidth);
    if (cols !== lastCols) {
      lastCols = cols;
      buildList(s);
    }
  }, 150);
  window.addEventListener('resize', onResize);
  const k = sKey(s.st.source, s.st.key);
  off = [
    () => window.removeEventListener('resize', onResize),
    on('follows', () => state === s && renderActions(s)),
    on('progress', (ev) => {
      if (state !== s || (ev.key !== null && ev.key !== k)) return;
      renderActions(s);
      s.list?.refresh();
    }),
  ];
}

function show(el: HTMLElement, route: Route, ctx: ViewContext, st: StoryDetail): void {
  const s: State = { el, ctx, route, st, order: [], cols: 1, list: null, labels: st.chapters.map((c) => chapterLabel(c)), keys: null, download: null };
  state = s;
  ctx.setTitle(st.name);
  const group = st.key.includes('/') ? (st.key.split('/')[0] as string) : null;
  const crumbs = (sourceName: string): void =>
    setCrumbs([{ label: sourceName, href: href.lib(st.source) }, ...(group ? [{ label: repoLabel(group), href: href.lib(st.source, group) }] : []), { label: st.name }]);
  crumbs('Kho truyện');
  data.sources({ signal: ctx.signal }).then(
    (j) => {
      const src = j.sources.find((x) => x.id === st.source);
      if (src && state === s) crumbs(src.name);
    },
    () => {},
  );
  render(
    el,
    html`<article class="page page-story">
      <header class="story-head">
        ${cover({ ...st, group }, { w: 240, cls: 'story-cover', eager: true })}
        <div class="story-info">
          <h1 class="page-title story-title">${st.name}</h1>
          ${meta(st)}
          <div id="st-actions" class="story-actions"></div>
        </div>
      </header>
      ${synopsis(st)} ${chapterSection(s)}
    </article>`,
  );
  hydrateCovers(el);
  renderActions(s);
  applyOrder(s);
  buildList(s);
  bind(s);
}

export async function mount(el: HTMLElement, route: Route, ctx: ViewContext): Promise<void> {
  const source = route.source as string;
  const key = route.key as string;
  ctx.setTitle('Truyện');
  setCrumbs([{ label: 'Truyện' }]);
  render(el, html`<div class="page page-story">${skeleton.view(html`${skeleton.story()}${skeleton.rows(8)}`)}</div>`);
  try {
    const st = await data.story(source, key, { signal: ctx.signal });
    if (ctx.signal.aborted) return;
    show(el, route, ctx, { ...st, source: st.source || source, key: st.key || key, chapters: st.chapters || [] });
  } catch (e) {
    if (isAbort(e) || ctx.signal.aborted) return;
    ctx.setTitle('Không tải được truyện');
    showError(el, e, () => {
      data.invalidate('story:');
      void mount(el, route, ctx);
    });
  }
}

/** Query-only change: the sort order. */
export function update(route: Route): void {
  const s = state;
  if (!s) return;
  s.route = route;
  const btn = s.el.querySelector<HTMLElement>('[data-act="order"]');
  const desc = route.query.order === 'desc';
  if (btn) {
    btn.setAttribute('aria-pressed', String(desc));
    const label = btn.querySelector('span');
    if (label) label.textContent = desc ? 'Mới nhất trước' : 'Cũ nhất trước';
  }
  applyOrder(s, s.el.querySelector<HTMLInputElement>('#ch-q')?.value || '');
  buildList(s);
}

export function unmount(): void {
  const s = state;
  state = null;
  for (const f of off) f();
  off = [];
  if (!s) return;
  s.el.removeEventListener('click', onClick);
  s.list?.destroy();
  s.download?.abort();
}
