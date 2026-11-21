import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { StoryDetail } from './backend/types';
import { on } from './events';
import * as library from './library';
import * as progress from './progress';

const story = (key = 'Repo/Truyện A', n = 5): StoryDetail => ({
  source: 'gh0',
  key,
  name: key.split('/').pop() as string,
  author: 'Tác Giả',
  synopsis: '',
  poster: null,
  genres: ['a', 'b', 'c', 'd'],
  tags: [],
  status: null,
  declared_chapters: n,
  link: null,
  cover: null,
  chapters: Array.from({ length: n }, (_, i) => ({ n: i + 1, title: `Tên ${i + 1}`, file: `Chương ${i + 1}.txt` })),
});

beforeEach(() => {
  localStorage.clear();
  progress._reset();
});

describe('progress', () => {
  it('saves the reading position under mythlab.progress with the frozen shape', () => {
    const p = progress.saveReading(story(), 2, 7, 0.5, { now: true });
    expect(p).toMatchObject({ source: 'gh0', key: 'Repo/Truyện A', name: 'Truyện A', idx: 2, n: 3, total: 5, para: 7, file: 'Chương 3.txt', title: 'Chương 3: Tên 3', group: 'Repo', maxIdx: 2 });
    expect(p.genres.length).toBeLessThanOrEqual(3);
    const raw = JSON.parse(localStorage.getItem('mythlab.progress') as string) as Record<string, unknown>;
    expect(Object.keys(raw)).toEqual(['gh0|Repo/Truyện A']);
    expect(progress.get('gh0', 'Repo/Truyện A')?.idx).toBe(2);
    expect(progress.percent(p)).toBe(60);
  });

  it('maxIdx only grows and writes are debounced', () => {
    vi.useFakeTimers();
    try {
      progress.saveReading(story(), 4);
      expect(localStorage.getItem('mythlab.progress')).toBeNull();
      const p = progress.saveReading(story(), 1);
      expect(p.idx).toBe(1);
      expect(p.maxIdx).toBe(4);
      vi.advanceTimersByTime(700);
      expect(localStorage.getItem('mythlab.progress')).toContain('"maxIdx":4');
    } finally {
      vi.useRealTimers();
    }
  });

  it('reads legacy entries without the additive fields', () => {
    localStorage.setItem('mythlab.progress', JSON.stringify({ 'local0|X': { source: 'local0', key: 'X', name: 'X', idx: 3, n: 4, total: 10, para: 0, ts: 5 }, bad: 1, 'also|bad': null }));
    progress._reset();
    expect(progress.all().map((p) => p.key)).toEqual(['X']);
    expect(progress.resolveIdx(progress.get('local0', 'X'), story('X', 10).chapters)).toBe(3);
  });

  it('merges with entries written by another tab instead of overwriting them', () => {
    progress.saveReading(story('A'), 1, 0, 0, { now: true });
    const other = JSON.parse(localStorage.getItem('mythlab.progress') as string) as Record<string, unknown>;
    other['gh0|B'] = { source: 'gh0', key: 'B', name: 'B', idx: 0, n: 1, total: 3, para: 0, ts: 1 };
    localStorage.setItem('mythlab.progress', JSON.stringify(other));
    progress.saveReading(story('A'), 2, 0, 0, { now: true });
    const raw = JSON.parse(localStorage.getItem('mythlab.progress') as string) as Record<string, { idx: number }>;
    expect(Object.keys(raw).sort()).toEqual(['gh0|A', 'gh0|B']);
    expect(raw['gh0|A']?.idx).toBe(2);
  });

  it('resolves the chapter by file name when the list changed', () => {
    const chapters = story('A', 6).chapters;
    expect(progress.resolveIdx({ idx: 1, file: 'Chương 4.txt' }, chapters)).toBe(3);
    expect(progress.resolveIdx({ idx: 99 }, chapters)).toBe(5);
    expect(progress.resolveIdx({ idx: 2, file: 'gone.txt' }, chapters)).toBe(2);
    expect(progress.resolveIdx(null, chapters)).toBe(0);
    expect(progress.resolveIdx({ idx: 3 }, [])).toBe(0);
  });

  it('removes and clears, emitting the progress event', () => {
    const keys: (string | null)[] = [];
    const off = on('progress', (e) => keys.push(e.key));
    progress.saveReading(story('A'), 0, 0, 0, { now: true });
    progress.saveReading(story('B'), 0, 0, 0, { now: true });
    progress.remove('gh0', 'A');
    expect(progress.all().map((p) => p.key)).toEqual(['B']);
    progress.clear();
    off();
    expect(progress.all()).toEqual([]);
    expect(localStorage.getItem('mythlab.progress')).toBe('{}');
    expect(keys).toEqual(['gh0|A', 'gh0|B', 'gh0|A', null]);
  });
});

describe('library: history, bookmarks, follows', () => {
  it('history is the progress list, most recent first', () => {
    vi.useFakeTimers();
    try {
      vi.setSystemTime(1000);
      progress.saveReading(story('A'), 0, 0, 0, { now: true });
      vi.setSystemTime(2000);
      progress.saveReading(story('B'), 0, 0, 0, { now: true });
    } finally {
      vi.useRealTimers();
    }
    expect(library.history().map((p) => p.key)).toEqual(['B', 'A']);
    library.removeHistory('gh0', 'B');
    expect(library.history().map((p) => p.key)).toEqual(['A']);
    library.clearHistory();
    expect(library.history()).toEqual([]);
  });

  it('adds, finds, toggles and removes bookmarks', () => {
    const base = { source: 'gh0', key: 'A', name: 'A', idx: 2, n: 3, file: 'Chương 3.txt', title: 'Chương 3: Tên', para: 4, excerpt: '  Một   đoạn\nvăn ' + 'x'.repeat(300) };
    const b = library.addBookmark(base);
    expect(b.id).toBe('gh0|A|Chương 3.txt|4');
    expect(b.excerpt.length).toBe(160);
    expect(b.excerpt.startsWith('Một đoạn văn')).toBe(true);
    library.addBookmark({ ...base, excerpt: 'lần hai' });
    expect(library.bookmarks().length).toBe(1);
    expect(library.findBookmark('gh0', 'A', 'Chương 3.txt', 4)?.excerpt).toBe('lần hai');
    library.addBookmark({ ...base, key: 'B', name: 'B' });
    expect(library.bookmarks('gh0', 'A').length).toBe(1);
    expect(library.bookmarks().length).toBe(2);
    expect(library.toggleBookmark(base)).toBe(false);
    expect(library.toggleBookmark(base)).toBe(true);
    library.removeBookmark('gh0|B|Chương 3.txt|4');
    expect(library.bookmarks().map((x) => x.key)).toEqual(['A']);
    library.clearBookmarks();
    expect(library.bookmarks()).toEqual([]);
  });

  it('ignores corrupt stored lists', () => {
    localStorage.setItem(library.BOOKMARKS_KEY, '{"a":1}');
    expect(library.bookmarks()).toEqual([]);
    localStorage.setItem(library.FOLLOWS_KEY, JSON.stringify([null, 3, { source: 'a' }, { source: 'a', key: 'b', name: 'n' }]));
    expect(library.follows().map((f) => f.key)).toEqual(['b']);
  });

  it('follows and unfollows a story', () => {
    const st = story('Repo/T');
    expect(library.toggleFollow(st)).toBe(true);
    expect(library.isFollowed('gh0', 'Repo/T')).toBe(true);
    expect(library.follows()[0]).toMatchObject({ source: 'gh0', key: 'Repo/T', name: 'T', group: 'Repo' });
    expect(library.toggleFollow(st)).toBe(false);
    expect(library.follows()).toEqual([]);
  });
});
