/** "Tủ truyện": every followed story as a grid, with a sort that is remembered on this device. */
import type { Follow, Route, StorySummary, ViewContext } from '../core/contracts';
import { hydrateCovers } from '../core/covers';
import { data } from '../core/data';
import { on } from '../core/events';
import { fmtNum, sKey } from '../core/format';
import { html, render } from '../core/html';
import { FOLLOW_SORTS, isFollowSort, library, type FollowSort } from '../core/library';
import { progress } from '../core/progress';
import { store } from '../core/store';
import { stateView } from '../core/ui';
import { setCrumbs } from '../shell';
import { pageHead, storyCard } from './cards';

export const FOLLOW_SORT_KEY = 'mythlab.followSort';

let root: HTMLElement | null = null;
let off: (() => void)[] = [];
let updated = new Map<string, string>();
let ctlSignal: AbortSignal | null = null;

const currentSort = (): FollowSort => {
  const v = store.get<unknown>(FOLLOW_SORT_KEY, 'added');
  return isFollowSort(v) ? v : 'added';
};

const asSummary = (f: Follow): StorySummary => ({ ...f, synopsis: '', genres: [], tags: [], status: null, declared_chapters: null, link: null }) as unknown as StorySummary;

function draw(): void {
  const el = root;
  if (!el) return;
  const sort = currentSort();
  const list = library.follows();
  const lastRead = new Map(progress.all().map((p) => [sKey(p.source, p.key), p.ts]));
  const sorted = library.sortFollows(list, sort, { updated, lastRead });
  render(
    el,
    html`<div class="page">
      ${pageHead(
        'Tủ truyện',
        list.length ? `${fmtNum(list.length)} truyện đang theo dõi` : undefined,
        list.length
          ? html`<label class="sr-only" for="follow-sort">Sắp xếp</label>
              <select id="follow-sort" class="select">
                ${FOLLOW_SORTS.map(([k, label]) => html`<option value="${k}" ${k === sort ? html`selected` : ''}>${label}</option>`)}
              </select>`
          : undefined,
      )}
      ${list.length
        ? html`<div class="grid">${sorted.map((f) => storyCard(asSummary(f), f.source))}</div>`
        : stateView({ icon: 'heart', title: 'Tủ truyện còn trống', message: 'Bấm “Theo dõi” ở trang truyện để thêm truyện vào đây.', home: true })}
    </div>`,
  );
  hydrateCovers(el);
  el.querySelector<HTMLSelectElement>('#follow-sort')?.addEventListener('change', (e) => {
    const v = (e.target as HTMLSelectElement).value;
    if (isFollowSort(v)) store.set(FOLLOW_SORT_KEY, v);
    draw();
    el.querySelector<HTMLSelectElement>('#follow-sort')?.focus();
  });
}

/** Best effort: last-update dates come from the source lists (cached by data), so "Chương mới" can order by them. */
async function loadUpdated(signal: AbortSignal): Promise<void> {
  const sources = [...new Set(library.follows().map((f) => f.source))];
  let got = false;
  for (const s of sources) {
    try {
      for (const st of await data.stories(s, null, { signal })) {
        if (st.updated) {
          updated.set(sKey(s, st.key), st.updated);
          got = true;
        }
      }
    } catch {
      /* the sort falls back to the follow time */
    }
  }
  if (got && !signal.aborted && root && currentSort() === 'updated') draw();
}

export function mount(el: HTMLElement, _r: Route, ctx: ViewContext): void {
  root = el;
  updated = new Map();
  ctlSignal = ctx.signal;
  ctx.setTitle('Tủ truyện');
  setCrumbs([{ label: 'Tủ truyện' }]);
  draw();
  off = [on('follows', draw), on('progress', (e) => e.key === null && draw())];
  void loadUpdated(ctlSignal);
}

export function unmount(): void {
  for (const f of off) f();
  off = [];
  root = null;
  ctlSignal = null;
}
