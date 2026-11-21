// Pure helpers of the browse views: the in-memory story filter, the column-major chapter grid and the
// onboarding address parser.
import { describe, expect, it } from 'vitest';
import type { StorySummary } from '../core/backend/types';
import { filterStories, tagCounts } from '../core/data';
import { normaliseServerUrl } from './onboarding';
import { colsFor, posAt, rowCount, rowOf } from './story';

const st = (name: string, o: Partial<StorySummary> = {}): StorySummary => ({
  key: name,
  folder: name,
  name,
  author: null,
  synopsis: '',
  poster: null,
  genres: [],
  tags: [],
  status: null,
  declared_chapters: null,
  link: null,
  cover: null,
  ...o,
});

describe('filterStories', () => {
  const list = [
    st('Phượng Đế Cửu Khuynh', { chapter_files: 2888, genres: ['Cổ Đại'], tags: ['Nữ Cường'], status: 'Hoàn thành', author: 'Mộc' }),
    st('Ánh Trăng', { chapter_files: 12, genres: ['Hiện Đại'], status: 'Đang ra', updated: '2026-02-01' }),
    st('Bạch Xà', { declared_chapters: 300, genres: ['Cổ Đại'], status: 'Hoàn thành', updated: '2026-03-01' }),
    st('Đông Cung', { chapter_files: 50, genres: ['Cổ Đại', 'Cung Đấu'] }),
  ];

  it('sorts by Vietnamese name by default and reports totals, tags and statuses', () => {
    const p = filterStories(list, {});
    expect(p.items.map((s) => s.name)).toEqual(['Ánh Trăng', 'Bạch Xà', 'Đông Cung', 'Phượng Đế Cửu Khuynh']);
    expect(p.total).toBe(4);
    expect(p.all).toBe(4);
    expect(p.tags[0]).toEqual({ name: 'Cổ Đại', count: 3 });
    expect(p.statuses).toEqual(['Đang ra', 'Hoàn thành']);
  });

  it('matches without diacritics over name, author and tags', () => {
    expect(filterStories(list, { q: 'phuong de' }).items.map((s) => s.name)).toEqual(['Phượng Đế Cửu Khuynh']);
    expect(filterStories(list, { q: 'moc' }).total).toBe(1);
    expect(filterStories(list, { q: 'cung dau' }).items.map((s) => s.name)).toEqual(['Đông Cung']);
    expect(filterStories(list, { q: 'không có' }).total).toBe(0);
  });

  it('filters by tag and status, sorts by chapters, updated and recent, and pages', () => {
    expect(filterStories(list, { tag: 'cổ đại', status: 'hoàn thành' }).items.map((s) => s.name)).toEqual(['Bạch Xà', 'Phượng Đế Cửu Khuynh']);
    expect(filterStories(list, { sort: 'chapters' }).items.map((s) => s.name)).toEqual(['Phượng Đế Cửu Khuynh', 'Bạch Xà', 'Đông Cung', 'Ánh Trăng']);
    expect(filterStories(list, { sort: 'updated' }).items.map((s) => s.name).slice(0, 2)).toEqual(['Bạch Xà', 'Ánh Trăng']);
    const recent = filterStories(list, { sort: 'recent', recentOf: (k) => (k === 'Đông Cung' ? 9 : 0) });
    expect(recent.items[0]?.name).toBe('Đông Cung');
    const page = filterStories(list, { offset: 1, limit: 2 });
    expect(page.items.map((s) => s.name)).toEqual(['Bạch Xà', 'Đông Cung']);
    expect(page.total).toBe(4);
  });

  it('counts a name once per story even when it is both a genre and a tag', () => {
    expect(tagCounts([st('a', { genres: ['X'], tags: ['X', 'Y'] }), st('b', { tags: ['Y'] })])).toEqual([
      { name: 'Y', count: 2 },
      { name: 'X', count: 1 },
    ]);
  });
});

describe('chapter grid (column-major blocks of ten rows)', () => {
  it('chooses the column count from the list width', () => {
    expect(colsFor(390)).toBe(1);
    expect(colsFor(700)).toBe(2);
    expect(colsFor(1100)).toBe(3);
  });

  it('reads down each column inside a block', () => {
    // 30 chapters, 3 columns: one block of 10 rows; column 0 = 0..9, column 1 = 10..19, column 2 = 20..29
    expect(rowCount(30, 3)).toBe(10);
    expect([0, 1, 2].map((c) => posAt(0, c, 30, 3))).toEqual([0, 10, 20]);
    expect([0, 1, 2].map((c) => posAt(9, c, 30, 3))).toEqual([9, 19, 29]);
    // a second, partial block: 37 chapters -> 7 more in ceil(7/3) = 3 rows: 30,31,32 | 33,34,35 | 36
    expect(rowCount(37, 3)).toBe(13);
    expect([0, 1, 2].map((c) => posAt(10, c, 37, 3))).toEqual([30, 33, 36]);
    expect([0, 1, 2].map((c) => posAt(11, c, 37, 3))).toEqual([31, 34, -1]);
    expect([0, 1, 2].map((c) => posAt(12, c, 37, 3))).toEqual([32, 35, -1]);
    expect(posAt(13, 0, 37, 3)).toBe(-1);
  });

  it('shows every chapter exactly once and rowOf finds its row', () => {
    for (const cols of [1, 2, 3]) {
      for (const n of [0, 1, 2, 9, 10, 11, 29, 30, 31, 59, 61, 693, 1000, 2888]) {
        const rows = rowCount(n, cols);
        const seen: number[] = [];
        for (let r = 0; r < rows; r++) {
          for (let c = 0; c < cols; c++) {
            const p = posAt(r, c, n, cols);
            if (p < 0) continue;
            seen.push(p);
            expect(rowOf(p, n, cols), `n=${n} cols=${cols} pos=${p}`).toBe(r);
          }
        }
        expect(seen.sort((a, b) => a - b), `n=${n} cols=${cols}`).toEqual(Array.from({ length: n }, (_, i) => i));
      }
    }
  });

  it('one column is the plain list', () => {
    expect(rowCount(2888, 1)).toBe(2888);
    expect(posAt(1234, 0, 2888, 1)).toBe(1234);
    expect(rowOf(1234, 2888, 1)).toBe(1234);
  });
});

describe('normaliseServerUrl', () => {
  it('accepts what people type', () => {
    expect(normaliseServerUrl('192.168.1.5:8765')).toBe('http://192.168.1.5:8765');
    expect(normaliseServerUrl('  http://may-chu.local:8765/  ')).toBe('http://may-chu.local:8765');
    expect(normaliseServerUrl('https://doc.example.org/truyen/')).toBe('https://doc.example.org/truyen');
    expect(normaliseServerUrl('localhost:18801')).toBe('http://localhost:18801');
  });

  it('rejects empty input and other schemes', () => {
    expect(normaliseServerUrl('')).toBeNull();
    expect(normaliseServerUrl('   ')).toBeNull();
    expect(normaliseServerUrl('ftp://x')).toBeNull();
    expect(normaliseServerUrl('javascript://alert(1)')).toBeNull();
    expect(normaliseServerUrl('http://')).toBeNull();
  });
});
