import { describe, expect, it } from 'vitest';
import { href, parseHash } from './router';

describe('router hashes', () => {
  it('parses every route', () => {
    expect(parseHash('')).toMatchObject({ view: 'home' });
    expect(parseHash('#/')).toMatchObject({ view: 'home', query: {} });
    expect(parseHash('#/lib/gh0')).toMatchObject({ view: 'lib', source: 'gh0' });
    expect(parseHash('#/lib/gh0/Done_CoTich?q=ph%C6%B0%E1%BB%A3ng&sort=chapters')).toMatchObject({ view: 'lib', source: 'gh0', repo: 'Done_CoTich', query: { q: 'phượng', sort: 'chapters' } });
    expect(parseHash('#/lib/gh0/*')).toMatchObject({ view: 'lib', source: 'gh0', repo: '*' });
    expect(parseHash('#/search?q=a+b')).toMatchObject({ view: 'search', query: { q: 'a b' } });
    expect(parseHash('#/history')).toMatchObject({ view: 'history' });
    expect(parseHash('#/bookmarks')).toMatchObject({ view: 'bookmarks' });
    expect(parseHash('#/nothing/here')).toMatchObject({ view: 'home' });
  });

  it('round-trips keys with slashes, spaces and Vietnamese letters', () => {
    const key = 'Done_CoTich/Phượng Đế Cửu Khuynh';
    expect(parseHash(href.story('gh0', key))).toMatchObject({ view: 'story', source: 'gh0', key });
    expect(parseHash(href.read('gh0', key, 12, { p: 7 }))).toMatchObject({ view: 'read', source: 'gh0', key, idx: 12, query: { p: '7' } });
    expect(parseHash(href.lib('local0', 'A B', { q: 'x&y=z' }))).toMatchObject({ view: 'lib', source: 'local0', repo: 'A B', query: { q: 'x&y=z' } });
    expect(parseHash(href.search('100% tốt'))).toMatchObject({ view: 'search', query: { q: '100% tốt' } });
  });

  it('tolerates hand-written and broken hashes', () => {
    expect(parseHash('#/s/gh0/Repo/Truyện A')).toMatchObject({ view: 'story', key: 'Repo/Truyện A' });
    expect(parseHash('#/r/gh0/Repo/Truyện A/5')).toMatchObject({ view: 'read', key: 'Repo/Truyện A', idx: 5 });
    expect(parseHash('#/r/gh0/k')).toMatchObject({ view: 'read', key: 'k', idx: 0 });
    expect(parseHash('#/s/gh0/%E0%A4%A')).toMatchObject({ view: 'story', key: '%E0%A4%A' });
    expect(parseHash('#/s/gh0')).toMatchObject({ view: 'home' });
  });

  it('builds stable hashes: sorted query, empty values dropped, index clamped', () => {
    expect(href.lib('gh0', null, { sort: 'name', q: '', n: 60 })).toBe('#/lib/gh0?n=60&sort=name');
    expect(href.read('s', 'k', -3)).toBe('#/r/s/k/0');
    expect(href.search()).toBe('#/search');
    expect(href.home()).toBe('#/');
  });
});
