import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { apiRoute } from '../../sw/shared';
import type { Progress } from './contracts';

const be = vi.hoisted(() => ({
  kind: 'server' as string,
  features: ['progress'] as string[],
  serverBase: 'http://srv',
  get: vi.fn(),
  send: vi.fn(),
  init: vi.fn(async () => 'server'),
}));
vi.mock('./backend', () => ({ backend: be }));

import { setSession, _resetAuth } from './auth-token';
import { progress } from './progress';
import * as sync from './progress-sync';

const wireEntry = (o: Record<string, unknown>): Record<string, unknown> => ({ source: 'local0', key: 'a', name: 'A', idx: 0, n: 1, total: 5, para: 0, ts: 1000, maxIdx: 0, genres: [], ...o });

let server: { entries: Record<string, unknown>[]; offset: number };

function routes(): void {
  be.get.mockImplementation(async (path: string) => {
    if (path.startsWith('/sources')) return { sources: [{ id: 'local0' }] };
    if (path.startsWith('/progress')) return { entries: server.entries, now: Date.now() + server.offset };
    throw new Error('unexpected ' + path);
  });
  be.send.mockImplementation(async (_m: string, _p: string, body: { entries: unknown[] }) => ({ entries: body.entries, now: Date.now() + server.offset }));
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(1_000_000);
  localStorage.clear();
  _resetAuth();
  progress._reset();
  sync._reset();
  be.kind = 'server';
  be.features = ['progress'];
  be.get.mockReset();
  be.send.mockReset();
  server = { entries: [], offset: 0 };
  routes();
});
afterEach(() => {
  sync._reset();
  vi.useRealTimers();
});

const story = (key = 'a', idx = 1): Parameters<typeof progress.update>[0] => ({ source: 'local0', key, name: key, idx, n: idx + 1, total: 5, para: 0 });

describe('applyRemote', () => {
  it('adds, merges and does not report local changes (no echo)', () => {
    const changed = vi.fn();
    progress.onLocalChange(changed);
    expect(progress.applyRemote([wireEntry({ idx: 2, maxIdx: 3, ts: 5000 })])).toBe(1);
    expect(progress.get('local0', 'a')).toMatchObject({ idx: 2, maxIdx: 3, ts: 5000 });
    // an older remote entry changes nothing but may raise maxIdx
    expect(progress.applyRemote([wireEntry({ idx: 0, maxIdx: 9, ts: 4000 })])).toBe(1);
    expect(progress.get('local0', 'a')).toMatchObject({ idx: 2, maxIdx: 9, ts: 5000 });
    expect(progress.applyRemote([wireEntry({ idx: 2, maxIdx: 9, ts: 5000 })])).toBe(0);
    expect(changed).not.toHaveBeenCalled();
  });

  it('moves remote timestamps into the local clock and ignores junk', () => {
    progress.applyRemote([wireEntry({ ts: 10_000 }), { source: 1 }, null, wireEntry({ key: '', ts: 5 }), wireEntry({ key: 'b', ts: -1 })], 4000);
    expect(progress.get('local0', 'a')?.ts).toBe(6000);
    expect(progress.all()).toHaveLength(1);
  });

  it('applies a newer deletion, keeps a newer local entry, and remembers the tombstone', () => {
    progress.update(story('a'));
    const ts = (progress.get('local0', 'a') as Progress).ts;
    progress.applyRemote([{ source: 'local0', key: 'a', ts: ts - 10, deleted: true }]);
    expect(progress.get('local0', 'a')).not.toBeNull();
    progress.applyRemote([{ source: 'local0', key: 'a', ts: ts + 10, deleted: true }]);
    expect(progress.get('local0', 'a')).toBeNull();
    expect(progress.tombstone('local0|a')).toBe(ts + 10);
    // a write older than the deletion stays dead, a newer one revives
    progress.applyRemote([wireEntry({ ts: ts + 5 })]);
    expect(progress.get('local0', 'a')).toBeNull();
    progress.applyRemote([wireEntry({ ts: ts + 20 })]);
    expect(progress.get('local0', 'a')).not.toBeNull();
    expect(progress.tombstone('local0|a')).toBeUndefined();
  });

  it('remove() leaves a tombstone and notifies; update() clears it', () => {
    const seen: [string, boolean][] = [];
    progress.onLocalChange((id, d) => seen.push([id, d]));
    progress.update(story('a'));
    progress.remove('local0', 'a');
    expect(progress.tombstone('local0|a')).toBeDefined();
    progress.update(story('a'));
    expect(progress.tombstone('local0|a')).toBeUndefined();
    expect(seen).toEqual([['local0|a', false], ['local0|a', true], ['local0|a', false]]);
  });
});

describe('merge', () => {
  const p = (o: Partial<Progress>): Progress => ({ source: 's', key: 'k', name: '', poster: null, cover: null, cover_sha: null, author: null, genres: [], group: null, idx: 0, n: 1, total: 1, para: 0, ts: 0, ...o });
  it('newer wins, tie goes to larger maxIdx, listen falls back', () => {
    expect(progress.merge(p({ ts: 1, idx: 4, maxIdx: 4 }), p({ ts: 2, idx: 1, maxIdx: 1 }))).toMatchObject({ ts: 2, idx: 1, maxIdx: 4 });
    expect(progress.merge(p({ ts: 1, idx: 1, maxIdx: 1 }), p({ ts: 1, idx: 2, maxIdx: 2 })).idx).toBe(2);
    expect(progress.merge(p({ ts: 1, listen: { idx: 3, para: 1 } }), p({ ts: 2 })).listen).toEqual({ idx: 3, para: 1 });
  });
});

describe('sync', () => {
  it('does nothing without the feature or on a non-server backend', async () => {
    be.features = [];
    await sync.init();
    expect(be.get).not.toHaveBeenCalled();
    be.features = ['progress'];
    be.kind = 'github';
    await sync.init();
    await sync.sync();
    expect(be.get).not.toHaveBeenCalled();
    expect(be.send).not.toHaveBeenCalled();
  });

  it('first sync uploads local progress, pulls remote entries and stores a cursor', async () => {
    progress.update(story('mine'));
    server.entries = [wireEntry({ key: 'theirs', ts: 900_000, idx: 3, maxIdx: 3 }), wireEntry({ source: 'gh9', key: 'x', ts: 900_000 })];
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    expect(be.get).toHaveBeenCalledWith('/progress?since=0', expect.anything());
    expect(progress.get('local0', 'theirs')?.idx).toBe(3);
    expect(progress.get('gh9', 'x')).toBeNull(); // unknown source
    expect(be.send).toHaveBeenCalledTimes(1);
    const sent = (be.send.mock.calls[0] as [string, string, { entries: { key: string }[] }])[2].entries;
    expect(sent.map((e) => e.key)).toEqual(['mine']);
    expect(JSON.parse(localStorage.getItem('mythlab.progress.cursor') as string)).toEqual({ base: 'http://srv', since: 999_000 });
    expect(localStorage.getItem('mythlab.progress.outbox')).toBeNull();
  });

  it('corrects the clock skew on both directions', async () => {
    server.offset = 5000; // server is 5 s ahead
    server.entries = [wireEntry({ key: 'theirs', ts: 1_004_000 })];
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    expect(progress.get('local0', 'theirs')?.ts).toBe(999_000);
    progress.update(story('mine'));
    await vi.advanceTimersByTimeAsync(1600);
    const body = (be.send.mock.calls.at(-1) as [string, string, { entries: { ts: number }[] }])[2];
    expect(body.entries[0]?.ts).toBe((progress.get('local0', 'mine') as Progress).ts + 5000);
  });

  it('pushes a chapter change soon and a moving position at most every 15 s', async () => {
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    progress.update(story('a', 1));
    await vi.advanceTimersByTimeAsync(1600);
    expect(be.send).toHaveBeenCalledTimes(1);
    progress.update({ ...story('a', 1), para: 3 });
    await vi.advanceTimersByTimeAsync(2000);
    expect(be.send).toHaveBeenCalledTimes(1); // throttled
    await vi.advanceTimersByTimeAsync(14_000);
    expect(be.send).toHaveBeenCalledTimes(2);
    progress.update(story('a', 2)); // new chapter: not throttled
    await vi.advanceTimersByTimeAsync(1600);
    expect(be.send).toHaveBeenCalledTimes(3);
  });

  it('sends deletions as tombstones', async () => {
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    progress.update(story('a'));
    await vi.advanceTimersByTimeAsync(1600);
    progress.remove('local0', 'a');
    await vi.advanceTimersByTimeAsync(1600);
    const body = (be.send.mock.calls.at(-1) as [string, string, { entries: { deleted?: boolean; key: string }[] }])[2];
    expect(body.entries[0]).toMatchObject({ key: 'a', deleted: true });
  });

  it('backs off on errors, stops on 401 and disables on 404', async () => {
    be.get.mockImplementation(async (path: string) => {
      if (path.startsWith('/sources')) return { sources: [{ id: 'local0' }] };
      throw Object.assign(new Error('net'), { status: 0 });
    });
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    const calls = (): number => be.get.mock.calls.filter((c) => String(c[0]).startsWith('/progress')).length;
    expect(calls()).toBe(1);
    await vi.advanceTimersByTimeAsync(5000);
    expect(calls()).toBe(2);
    await vi.advanceTimersByTimeAsync(5000);
    expect(calls()).toBe(2); // second wait is 10 s
    await vi.advanceTimersByTimeAsync(5000);
    expect(calls()).toBe(3);

    for (const status of [401, 404]) {
      sync._reset();
      be.get.mockImplementation(async (path: string) => {
        if (path.startsWith('/sources')) return { sources: [{ id: 'local0' }] };
        throw Object.assign(new Error('x'), { status });
      });
      await sync.init();
      await vi.advanceTimersByTimeAsync(0);
      const n = calls();
      await vi.advanceTimersByTimeAsync(10 * 60_000);
      expect(calls()).toBe(n); // no more attempts, not even the 60 s poll
    }
  });

  it('pulls every 60 s only while visible', async () => {
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    const calls = (): number => be.get.mock.calls.filter((c) => String(c[0]).startsWith('/progress')).length;
    const n = calls();
    await vi.advanceTimersByTimeAsync(sync.PULL_EVERY);
    expect(calls()).toBe(n + 1);
    vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('hidden');
    await vi.advanceTimersByTimeAsync(sync.PULL_EVERY * 2);
    expect(calls()).toBe(n + 1);
    vi.restoreAllMocks();
  });
});

describe('signed in', () => {  it('uses a per-account cursor and outbox, leaving the anonymous ones alone', async () => {    localStorage.setItem('mythlab.progress.cursor', JSON.stringify({ base: 'http://srv', since: 5 }));    setSession({ token: 'T', user: { id: 'u1', name: 'A', email: 'a@x', picture: '' }, base: 'http://srv', expires: 0 });    progress.update(story('mine'));    await sync.init();    await vi.advanceTimersByTimeAsync(0);    expect(be.get).toHaveBeenCalledWith('/progress?since=0', expect.anything());    expect(JSON.parse(localStorage.getItem('mythlab.progress.cursor.u1') as string)).toEqual({ base: 'http://srv', since: 999_000 });    expect(JSON.parse(localStorage.getItem('mythlab.progress.cursor') as string)).toEqual({ base: 'http://srv', since: 5 });  });});
describe('service worker', () => {
  it('never treats /api/progress as cacheable data', () => {
    expect(apiRoute('/api/progress')).toBe('other');
    expect(apiRoute('/base/api/progress')).toBe('other');
  });
});
