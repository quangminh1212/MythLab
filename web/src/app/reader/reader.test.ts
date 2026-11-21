import { beforeEach, describe, expect, it } from 'vitest';
import { progress } from '../core/progress';
import type { StoryDetail } from '../core/contracts';
import { chapterSwipe, clampPage, firstPara, pageCount, pageOfOffset, pageSwipe, stride, tapZone, turn, wheelTurn } from './pager';
import { anchorAt, excerpt, firstBelow, readMinutes, scrollFor, scrollFraction, startPosition, storyPercent, type Box } from './position';

describe('pager maths', () => {
  const g = { width: 700, gap: 48, scrollWidth: 0 };
  it('counts pages from the laid-out width', () => {
    expect(stride(g)).toBe(748);
    expect(pageCount({ ...g, scrollWidth: 700 })).toBe(1);
    expect(pageCount({ ...g, scrollWidth: 700 + 748 })).toBe(2);
    expect(pageCount({ ...g, scrollWidth: 700 + 748 * 11 })).toBe(12);
    // sub-pixel rounding of the browser must not add or lose a page
    expect(pageCount({ ...g, scrollWidth: 700 + 748 * 11 - 0.6 })).toBe(12);
    expect(pageCount({ ...g, scrollWidth: 0 })).toBe(1);
    expect(pageCount({ width: 0, gap: 0, scrollWidth: 100 })).toBe(1);
  });
  it('maps an offset to its page', () => {
    const geo = { ...g, scrollWidth: 700 + 748 * 3 };
    expect(pageOfOffset(0, geo)).toBe(0);
    expect(pageOfOffset(699, geo)).toBe(0);
    expect(pageOfOffset(748, geo)).toBe(1);
    expect(pageOfOffset(747.6, geo)).toBe(1);
    expect(pageOfOffset(748 * 3 + 10, geo)).toBe(3);
    expect(pageOfOffset(99999, geo)).toBe(3);
    expect(pageOfOffset(-5, geo)).toBe(0);
  });
  it('clamps pages', () => {
    expect(clampPage(-1, 5)).toBe(0);
    expect(clampPage(7, 5)).toBe(4);
    expect(clampPage(2.9, 5)).toBe(2);
    expect(clampPage(NaN, 5)).toBe(0);
    expect(clampPage(3, 0)).toBe(0);
  });
  it('finds the first paragraph of a page', () => {
    // paragraph 0: page 0; 1: pages 0-2 (spills over); 2: page 2; 3: page 3
    const starts = [0, 0, 2, 3];
    const ends = [0, 2, 2, 3];
    expect(firstPara(starts, ends, 0)).toBe(0);
    expect(firstPara(starts, ends, 1)).toBe(1); // nothing starts here: the paragraph that runs through
    expect(firstPara(starts, ends, 2)).toBe(2);
    expect(firstPara(starts, ends, 3)).toBe(3);
    expect(firstPara(starts, ends, 4)).toBe(3); // the end page after the text
    expect(firstPara([], [], 0)).toBe(0);
    expect(firstPara([1, 1], [1, 1], 0)).toBe(0); // title page before the text
  });
  it('turns pages and crosses chapters only at the ends', () => {
    expect(turn(0, 1, 3, 5, 10)).toEqual({ kind: 'page', page: 1 });
    expect(turn(2, 1, 3, 5, 10)).toEqual({ kind: 'next' });
    expect(turn(0, -1, 3, 5, 10)).toEqual({ kind: 'prev' });
    expect(turn(0, -1, 3, 0, 10)).toEqual({ kind: 'start' });
    expect(turn(2, 1, 3, 9, 10)).toEqual({ kind: 'end' });
    expect(turn(1, -1, 3, 0, 10)).toEqual({ kind: 'page', page: 0 });
  });
  it('tap zones are 28 / 44 / 28 percent', () => {
    expect(tapZone(10, 400)).toBe('prev');
    expect(tapZone(111, 400)).toBe('prev');
    expect(tapZone(113, 400)).toBe('menu');
    expect(tapZone(200, 400)).toBe('menu');
    expect(tapZone(288, 400)).toBe('menu');
    expect(tapZone(289, 400)).toBe('next');
    expect(tapZone(5, 0)).toBe('menu');
  });
  it('recognises swipes', () => {
    expect(pageSwipe(-60, 10)).toBe(1);
    expect(pageSwipe(60, 10)).toBe(-1);
    expect(pageSwipe(-40, 0)).toBe(0);
    expect(pageSwipe(-60, 50)).toBe(0);
    // chapter swipe in scroll mode: long, flat and away from the screen edges
    expect(chapterSwipe(-130, 10, 200, 390)).toBe(1);
    expect(chapterSwipe(130, 10, 200, 390)).toBe(-1);
    expect(chapterSwipe(-80, 0, 200, 390)).toBe(0);
    expect(chapterSwipe(-130, 70, 200, 390)).toBe(0);
    expect(chapterSwipe(130, 0, 10, 390)).toBe(0);
    expect(chapterSwipe(-130, 0, 380, 390)).toBe(0);
    expect(chapterSwipe(-200, 0, 700, 1440)).toBe(0);
    expect(chapterSwipe(-230, 0, 700, 1440)).toBe(1);
  });
  it('throttles the wheel', () => {
    expect(wheelTurn(100, 1000, 0)).toBe(1);
    expect(wheelTurn(-100, 1000, 0)).toBe(-1);
    expect(wheelTurn(2, 1000, 0)).toBe(0);
    expect(wheelTurn(100, 1000, 700)).toBe(0);
  });
});

describe('reading position', () => {
  // five paragraphs of 200 px with 20 px between them, in document coordinates
  const doc: Box[] = [0, 1, 2, 3, 4].map((i) => ({ top: 300 + i * 220, height: 200 }));
  const view = (scrollY: number) => (i: number): Box => ({ top: (doc[i] as Box).top - scrollY, height: 200 });
  const LINE = 60;

  it('finds the paragraph on the reading line', () => {
    expect(firstBelow(5, (i) => (view(0)(i).top + 200), LINE)).toBe(0);
    expect(anchorAt(5, view(0), LINE)).toEqual({ para: 0, frac: 0 });
    expect(anchorAt(5, view(340), LINE)).toEqual({ para: 0, frac: 0.5 });
    // in the gap between two paragraphs: the next one, not yet started
    expect(anchorAt(5, view(450), LINE)).toEqual({ para: 1, frac: 0 });
    expect(anchorAt(5, view(99999), LINE)).toEqual({ para: 4, frac: 1 });
    expect(anchorAt(0, view(0), LINE)).toEqual({ para: 0, frac: 0 });
  });

  it('save then restore lands on the same pixel, also after a re-flow', () => {
    for (const y of [0, 240, 340, 517, 733, 1111]) {
      const a = anchorAt(5, view(y), LINE);
      const back = scrollFor(doc[a.para] as Box, a.frac, LINE);
      // positions above the first paragraph or inside a gap snap to the paragraph start
      const inside = y + LINE >= (doc[a.para] as Box).top;
      if (inside) expect(Math.abs(back - y)).toBeLessThanOrEqual(1);
      else expect(back).toBe((doc[a.para] as Box).top - LINE);
    }
    // the font got bigger: every paragraph is now 300 px tall; the same sentence is on the line again
    const a = anchorAt(5, view(630), LINE); // paragraph 1, 85 % read
    expect(a).toEqual({ para: 1, frac: 0.85 });
    const big: Box = { top: 300 + 320, height: 300 };
    expect(scrollFor(big, a.frac, LINE)).toBe(620 + 255 - 60);
    expect(scrollFor(big, a.frac, LINE, 500)).toBe(500);
    expect(scrollFor({ top: 10, height: 100 }, 0, LINE)).toBe(0);
  });

  it('chooses where a chapter opens', () => {
    const chapters = [{ file: 'a.txt' }, { file: 'b.txt' }, { file: 'c.txt' }];
    const base = { idx: 1, chapters, count: 40 };
    expect(startPosition({ ...base, saved: null })).toEqual({ para: 0, frac: 0, end: false, explicit: false });
    expect(startPosition({ ...base, saved: { idx: 1, para: 12, frac: 0.4 } })).toEqual({ para: 12, frac: 0.4, end: false, explicit: false });
    // saved in another chapter
    expect(startPosition({ ...base, saved: { idx: 2, para: 12 } }).para).toBe(0);
    // the chapter list was re-ordered: the file name decides, not the index
    expect(startPosition({ ...base, saved: { idx: 0, file: 'b.txt', para: 7 } }).para).toBe(7);
    expect(startPosition({ ...base, saved: { idx: 1, file: 'a.txt', para: 7 } }).para).toBe(0);
    // a paragraph that no longer exists
    expect(startPosition({ ...base, saved: { idx: 1, para: 99 } }).para).toBe(0);
    // an explicit paragraph (bookmark) wins and is clamped
    expect(startPosition({ ...base, queryPara: '5', saved: { idx: 1, para: 12 } })).toEqual({ para: 5, frac: 0, end: false, explicit: true });
    expect(startPosition({ ...base, queryPara: '500', saved: null }).para).toBe(39);
    expect(startPosition({ ...base, queryPara: 'x', saved: { idx: 1, para: 12 } }).para).toBe(12);
    expect(startPosition({ ...base, atEnd: true, saved: { idx: 1, para: 12 } })).toEqual({ para: 39, frac: 0, end: true, explicit: true });
  });

  it('progress numbers', () => {
    expect(scrollFraction(0, 3000, 800)).toBe(0);
    expect(scrollFraction(1100, 3000, 800)).toBe(0.5);
    expect(scrollFraction(5000, 3000, 800)).toBe(1);
    expect(scrollFraction(0, 700, 800)).toBe(1);
    expect(storyPercent(0, 100, 0)).toBe(0);
    expect(storyPercent(49, 100, 0.5)).toBe(49.5);
    expect(storyPercent(99, 100, 1)).toBe(100);
    expect(storyPercent(3, 0, 1)).toBe(0);
    expect(readMinutes(2300)).toBe(10);
    expect(readMinutes(10)).toBe(1);
  });

  it('cuts a bookmark excerpt at a word', () => {
    expect(excerpt('  ngắn   thôi ')).toBe('ngắn thôi');
    const long = 'từ '.repeat(100);
    const e = excerpt(long);
    expect(e.length).toBeLessThanOrEqual(161);
    expect(e.endsWith('…')).toBe(true);
    expect(e).not.toMatch(/\s…$/);
  });
});

describe('progress save / restore through core/progress', () => {
  const story: StoryDetail = {
    source: 'local0',
    key: 'Truyen',
    name: 'Truyện thử',
    author: null,
    synopsis: '',
    poster: null,
    genres: [],
    tags: [],
    status: null,
    declared_chapters: null,
    link: null,
    cover: null,
    chapters: [
      { n: 1, title: 'Một', file: '001.txt' },
      { n: 2, title: 'Hai', file: '002.txt' },
      { n: 3, title: 'Ba', file: '003.txt' },
    ],
  };
  beforeEach(() => {
    localStorage.clear();
    progress._reset();
  });

  it('stores the chapter file and the sub-paragraph fraction and restores them', () => {
    progress.saveReading(story, 1, 14, 0.37, { now: true });
    const saved = progress.get('local0', 'Truyen');
    expect(saved).toMatchObject({ idx: 1, n: 2, total: 3, para: 14, frac: 0.37, file: '002.txt', title: 'Chương 2: Hai' });
    expect(startPosition({ saved, idx: 1, chapters: story.chapters, count: 30 })).toEqual({ para: 14, frac: 0.37, end: false, explicit: false });
    expect(startPosition({ saved, idx: 2, chapters: story.chapters, count: 30 }).para).toBe(0);
    // survives a reload of the module state (what a page reload does)
    progress._reset();
    expect(progress.get('local0', 'Truyen')).toMatchObject({ idx: 1, para: 14, frac: 0.37 });
  });

  it('looking back at an early chapter keeps the furthest chapter, and listening keeps the reading position', () => {
    progress.saveReading(story, 2, 3, 0, { now: true });
    progress.saveReading(story, 0, 0, 0, { now: true });
    expect(progress.get('local0', 'Truyen')).toMatchObject({ idx: 0, maxIdx: 2 });
    // what the player writes: only the listening slot
    progress.update({ source: 'local0', key: 'Truyen', listen: { idx: 2, para: 9, file: '003.txt' }, maxIdx: 2 }, { now: true });
    expect(progress.get('local0', 'Truyen')).toMatchObject({ idx: 0, para: 0, file: '001.txt', listen: { idx: 2, para: 9 }, maxIdx: 2 });
  });
});
