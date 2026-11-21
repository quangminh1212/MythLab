import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { on } from './events';
import { library } from './library';
import { progress } from './progress';

const bm = { source: 's', key: 'k', name: 'K', idx: 0, n: 1, file: 'c1.txt', title: 'C1', para: 1, excerpt: 'x' };
const st = { source: 's', key: 'g/k', name: 'K', author: null, poster: null, cover: null, cover_sha: null };

beforeEach(() => {
  localStorage.clear();
  progress._reset();
});
afterEach(() => vi.restoreAllMocks());

function failWrites(): { mockRestore(): void } {
  return vi.spyOn(localStorage, 'setItem').mockImplementation(() => {
    throw new DOMException('full', 'QuotaExceededError');
  });
}

describe('library storage failures', () => {
  it('toggleBookmark does not report success or emit when the write fails', () => {
    const toasts: string[] = [];
    const bookmarkEvents: unknown[] = [];
    const offs = [on('toast', (t) => toasts.push(t.kind ?? '')), on('bookmarks', (e) => bookmarkEvents.push(e))];
    const spy = failWrites();
    expect(library.toggleBookmark(bm)).toBe(false);
    spy.mockRestore();
    expect(bookmarkEvents).toEqual([]);
    expect(toasts).toEqual(['error']);
    offs.forEach((o) => o());
  });

  it('removeBookmark / clearBookmarks report false on failure and keep the data', () => {
    const b = library.addBookmark(bm);
    expect(library.bookmarks()).toHaveLength(1);
    const spy = failWrites();
    expect(library.removeBookmark(b.id)).toBe(false);
    expect(library.clearBookmarks()).toBe(false);
    expect(library.toggleBookmark(bm)).toBe(true);
    spy.mockRestore();
    expect(library.bookmarks()).toHaveLength(1);
  });

  it('toggleFollow returns the old state on failure', () => {
    const spy = failWrites();
    expect(library.toggleFollow(st)).toBe(false);
    expect(library.setFollow(st, true)).toBe(false);
    spy.mockRestore();
    expect(library.toggleFollow(st)).toBe(true);
    const spy2 = failWrites();
    expect(library.toggleFollow(st)).toBe(true);
    spy2.mockRestore();
  });
});

describe('library follows', () => {
  it('orders follows newest first and unfollows', () => {
    library.setFollow(st, true);
    library.setFollow({ ...st, key: 'g/j' }, true);
    expect(library.follows().map((f) => f.key)).toEqual(['g/j', 'g/k']);
    expect(library.setFollow(st, false)).toBe(true);
    expect(library.follows().map((f) => f.key)).toEqual(['g/j']);
  });
});
