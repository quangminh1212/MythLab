import { describe, expect, it } from 'vitest';
import type { StorySummary } from '../core/contracts';
import { reportUrl } from './report';
import { pickSuggestions } from './suggest';

const s = (key: string, o: Partial<StorySummary> = {}): StorySummary => ({ key, name: key, author: null, synopsis: '', poster: null, genres: [], tags: [], status: null, declared_chapters: null, link: null, cover: null, ...o });

describe('pickSuggestions', () => {
  it('excludes the current story and duplicates, limits to 6', () => {
    const list = ['cur', 'a', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].map((k) => s(k));
    const r = pickSuggestions(list, { key: 'cur' });
    expect(r).toHaveLength(6);
    expect(r.map((x) => x.key)).not.toContain('cur');
    expect(new Set(r.map((x) => x.key)).size).toBe(6);
  });
  it('prefers the same author, then shared genres, then unread', () => {
    const list = [s('x', { genres: ['Hài'] }), s('y', { author: 'Nam Cao' }), s('z'), s('w', { genres: ['Hài'] })];
    const r = pickSuggestions(list, { key: 'cur', author: 'nam cao', genres: ['Hài'] }, { seen: (k) => k === 'x' });
    expect(r.map((x) => x.key)).toEqual(['y', 'w', 'x', 'z']);
  });
  it('falls back to the most recently updated', () => {
    const list = [s('old', { updated: '2020-01-01' }), s('new', { updated: '2024-01-01' })];
    expect(pickSuggestions(list, { key: 'cur' }).map((x) => x.key)).toEqual(['new', 'old']);
  });
});

describe('reportUrl', () => {
  it('prefills title and body', () => {
    const u = new URL(reportUrl({ story: 'Tên', source: 'local', key: 'k', chapter: 'Chương 3', idx: 2 }));
    expect(u.pathname).toBe('/quangminh1212/MythLab/issues/new');
    expect(u.searchParams.get('title')).toContain('Chương 3');
    expect(u.searchParams.get('body')).toContain('Khóa: k');
  });
});
