import { describe, expect, it } from 'vitest';
import type { Follow } from './contracts';
import { sKey } from './format';
import { isFollowSort, sortFollows } from './library';

const f = (key: string, name: string, ts: number): Follow => ({ source: 's', key, name, author: null, poster: null, cover: null, cover_sha: null, group: null, ts });
const list = [f('a', 'Đông', 1), f('b', 'An', 3), f('c', 'Bình', 2)];
const names = (l: Follow[]): string[] => l.map((x) => x.name);

describe('sortFollows', () => {
  it('sorts by name, vietnamese aware', () => expect(names(sortFollows(list, 'name'))).toEqual(['An', 'Bình', 'Đông']));
  it('sorts by follow time, newest first', () => expect(names(sortFollows(list, 'added'))).toEqual(['An', 'Bình', 'Đông']));
  it('sorts by last read, unread last', () => {
    const lastRead = new Map([[sKey('s', 'a'), 50], [sKey('s', 'c'), 10]]);
    expect(names(sortFollows(list, 'recent', { lastRead }))).toEqual(['Đông', 'Bình', 'An']);
  });
  it('sorts by updated date, unknown last', () => {
    const updated = new Map([[sKey('s', 'c'), '2024-02-01'], [sKey('s', 'a'), '2024-01-01']]);
    expect(names(sortFollows(list, 'updated', { updated }))).toEqual(['Bình', 'Đông', 'An']);
  });
  it('does not mutate and validates ids', () => {
    sortFollows(list, 'name');
    expect(list[0]?.key).toBe('a');
    expect(isFollowSort('added')).toBe(true);
    expect(isFollowSort('x')).toBe(false);
  });
});
