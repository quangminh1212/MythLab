/**
 * Reading-position maths: which paragraph is at the reading line, how far into it, and where to scroll to get
 * back there. Pure functions so save / restore is unit-tested without a layout engine.
 *
 * A position is { para, frac }: the paragraph crossing the reading line (just under the top bar) and the
 * fraction of that paragraph above the line. It survives font changes, resizes and re-flows.
 */
import type { ChapterRef, Progress } from '../core/contracts';

export interface Anchor {
  para: number;
  /** 0..1: share of the paragraph above the reading line. */
  frac: number;
}

export interface Box {
  top: number;
  height: number;
}

const clamp01 = (v: number): number => (v > 0 ? (v < 1 ? v : 1) : 0);

/**
 * Index of the first of `count` boxes whose bottom is below `line` (the boxes are stacked top to bottom).
 * Binary search, so only a handful of boxes are measured. Returns the last box when all are above the line.
 */
export function firstBelow(count: number, bottomOf: (i: number) => number, line: number): number {
  if (count <= 0) return 0;
  let lo = 0;
  let hi = count - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (bottomOf(mid) > line) hi = mid;
    else lo = mid + 1;
  }
  return lo;
}

/** The position for a reading line, given a way to measure paragraph `i` in the same coordinates as `line`. */
export function anchorAt(count: number, boxOf: (i: number) => Box, line: number): Anchor {
  if (count <= 0) return { para: 0, frac: 0 };
  const para = firstBelow(count, (i) => {
    const b = boxOf(i);
    return b.top + b.height;
  }, line);
  const b = boxOf(para);
  // 4 decimals are plenty (a 2,000 px paragraph resolves to 0.2 px) and keep the stored JSON small
  return { para, frac: b.height > 0 ? Math.round(clamp01((line - b.top) / b.height) * 10000) / 10000 : 0 };
}

/**
 * Scroll offset that puts the position back on the reading line. `box` is the paragraph in document
 * coordinates; `line` is the distance of the reading line from the top of the viewport.
 */
export function scrollFor(box: Box, frac: number, line: number, maxScroll = Infinity): number {
  const y = box.top + clamp01(frac) * box.height - line;
  return Math.max(0, Math.min(maxScroll, Math.round(y)));
}

export interface StartInput {
  /** `?p=` of the route (a bookmark or a link to a paragraph). */
  queryPara?: string | undefined;
  /** `?end=1`: arrived by turning back from the next chapter. */
  atEnd?: boolean;
  saved: Pick<Progress, 'idx' | 'para' | 'file' | 'frac'> | null;
  /** Chapter being opened. */
  idx: number;
  chapters: Pick<ChapterRef, 'file'>[];
  /** Paragraph count of the chapter. */
  count: number;
}

export interface Start extends Anchor {
  /** Open at the very end of the chapter (last page / bottom). */
  end: boolean;
  /** The position came from the route, not from the saved progress. */
  explicit: boolean;
}

/**
 * Where a chapter opens: an explicit paragraph wins, then "at the end", then the saved position when it is in
 * this chapter (matched by file name first, so a re-ordered chapter list does not misplace it), else the top.
 */
export function startPosition(o: StartInput): Start {
  const last = Math.max(0, o.count - 1);
  const q = o.queryPara != null && o.queryPara !== '' ? Number(o.queryPara) : NaN;
  if (Number.isFinite(q)) return { para: Math.max(0, Math.min(last, Math.trunc(q))), frac: 0, end: false, explicit: true };
  if (o.atEnd) return { para: last, frac: 0, end: true, explicit: true };
  const s = o.saved;
  if (s) {
    const here = s.file ? o.chapters[o.idx]?.file === s.file : s.idx === o.idx;
    if (here && s.para >= 0 && s.para <= last) return { para: Math.trunc(s.para), frac: clamp01(s.frac ?? 0), end: false, explicit: false };
  }
  return { para: 0, frac: 0, end: false, explicit: false };
}

/** Progress through the chapter (0..1) of a scroll position. */
export function scrollFraction(scrollY: number, docHeight: number, viewHeight: number): number {
  const max = docHeight - viewHeight;
  return max > 1 ? clamp01(scrollY / max) : 1;
}

/** Progress through the whole story in percent (0..100), from the chapter and the progress inside it. */
export function storyPercent(idx: number, total: number, chapterFrac: number): number {
  if (!(total > 0)) return 0;
  return Math.round(clamp01((idx + clamp01(chapterFrac)) / total) * 1000) / 10;
}

/** The first ~160 characters of a paragraph, cut at a word, for a bookmark. */
export function excerpt(text: string, max = 160): string {
  const t = String(text || '').replace(/\s+/g, ' ').trim();
  if (t.length <= max) return t;
  const cut = t.lastIndexOf(' ', max);
  return t.slice(0, cut > max * 0.6 ? cut : max).replace(/[\s,;:–—-]+$/, '') + '…';
}

/** Reading time in minutes for a word count (230 words a minute, at least 1). */
export const readMinutes = (words: number): number => Math.max(1, Math.round((words || 0) / 230));
