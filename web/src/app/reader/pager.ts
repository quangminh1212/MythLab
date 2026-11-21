/**
 * Maths of the paged reading mode and of the reader's gestures. Pure functions (no DOM) so they are unit-tested.
 *
 * The chapter is laid out in CSS columns, each exactly one page wide; page `i` is shown by shifting the column
 * box left by `i × stride`. Nothing scrolls, so there is no scroll snapping to fight with.
 */

export interface PageGeom {
  /** Width of one page (= the visible box) in px. */
  width: number;
  /** Gap between two columns in px. */
  gap: number;
  /** Full width of the laid-out columns in px. */
  scrollWidth: number;
}

/** Distance between the left edges of two pages. */
export const stride = (g: PageGeom): number => g.width + g.gap;

/** Number of pages of the laid-out chapter (at least 1). */
export function pageCount(g: PageGeom): number {
  const st = stride(g);
  if (!(st > 0) || !(g.scrollWidth > 0)) return 1;
  return Math.max(1, Math.round((g.scrollWidth + g.gap) / st));
}

export const clampPage = (page: number, count: number): number => Math.max(0, Math.min(Math.max(1, count) - 1, Math.trunc(page) || 0));

/** Page that holds a horizontal offset inside the column box. */
export function pageOfOffset(left: number, g: PageGeom, count = pageCount(g)): number {
  const st = stride(g);
  if (!(st > 0)) return 0;
  // half a gap of tolerance: sub-pixel layout must not push an edge onto the page before
  return clampPage(Math.floor((left + g.gap / 2 + 0.5) / st), count);
}

/**
 * First paragraph of a page: the first paragraph that starts on it, otherwise the paragraph that spills over
 * from an earlier page. `starts[i]` / `ends[i]` are the pages where paragraph i starts and ends.
 */
export function firstPara(starts: ArrayLike<number>, ends: ArrayLike<number>, page: number): number {
  const n = starts.length;
  if (!n) return 0;
  let spill = -1;
  for (let i = 0; i < n; i++) {
    const s = starts[i] as number;
    if (s === page) return i;
    if (s > page) break;
    if ((ends[i] as number) >= page) spill = i;
  }
  if (spill >= 0) return spill;
  // a page without any paragraph (title page, end page): the closest paragraph before it, else the first
  let before = 0;
  for (let i = 0; i < n; i++) if ((starts[i] as number) < page) before = i;
  return before;
}

export type Turn =
  /** Stay in the chapter and show this page. */
  | { kind: 'page'; page: number }
  /** Open the next chapter at its first page. */
  | { kind: 'next' }
  /** Open the previous chapter at its last page. */
  | { kind: 'prev' }
  /** Nothing before the first page of the first chapter. */
  | { kind: 'start' }
  /** Nothing after the last page of the last chapter. */
  | { kind: 'end' };

/** What turning `d` pages from `page` means in chapter `idx` of `total`. */
export function turn(page: number, d: number, count: number, idx: number, total: number): Turn {
  const to = page + d;
  if (to < 0) return idx > 0 ? { kind: 'prev' } : { kind: 'start' };
  if (to >= count) return idx < total - 1 ? { kind: 'next' } : { kind: 'end' };
  return { kind: 'page', page: to };
}

export type Zone = 'prev' | 'menu' | 'next';

/** Tap zones of a page: the left 28 % turns back, the right 28 % turns forward, the middle shows the controls. */
export function tapZone(x: number, width: number): Zone {
  if (!(width > 0)) return 'menu';
  const f = x / width;
  return f < 0.28 ? 'prev' : f > 0.72 ? 'next' : 'menu';
}

/** A page-turning swipe: longer than 50 px and clearly horizontal. Returns +1 (next), -1 (previous) or 0. */
export function pageSwipe(dx: number, dy: number): -1 | 0 | 1 {
  if (Math.abs(dx) <= 50 || Math.abs(dx) <= Math.abs(dy) * 1.5) return 0;
  return dx < 0 ? 1 : -1;
}

/** Zone at both screen edges where a swipe belongs to the system (back gesture), in px. */
export const EDGE_GUARD = 24;

/**
 * A chapter-changing swipe in scroll mode. It has to be deliberate, because the page also scrolls vertically:
 * at least 90 px and 30 % of the screen wide, much more horizontal than vertical, and not started at a screen
 * edge. Returns +1 (next chapter), -1 (previous) or 0.
 */
export function chapterSwipe(dx: number, dy: number, startX: number, width: number): -1 | 0 | 1 {
  if (!(width > 0) || startX < EDGE_GUARD || startX > width - EDGE_GUARD) return 0;
  const need = Math.max(90, Math.min(width * 0.3, 220));
  if (Math.abs(dx) < need || Math.abs(dx) < Math.abs(dy) * 2.5) return 0;
  return dx < 0 ? 1 : -1;
}

/** Wheel turns one page per gesture: at most one turn per `gap` ms and tiny deltas are ignored. */
export function wheelTurn(delta: number, now: number, last: number, gap = 450): -1 | 0 | 1 {
  if (Math.abs(delta) < 4 || now - last < gap) return 0;
  return delta > 0 ? 1 : -1;
}
