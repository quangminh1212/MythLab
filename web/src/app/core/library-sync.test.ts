import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const be = vi.hoisted(() => ({
  kind: 'server' as string,
  features: ['progress', 'auth', 'library'] as string[],
  serverBase: 'http://srv',
  get: vi.fn(),
  send: vi.fn(),
  init: vi.fn(async () => 'server'),
}));
vi.mock('./backend', () => ({ backend: be }));

import { setSession, _resetAuth } from './auth-token';
import { library, _resetLibrary } from './library';
import * as sync from './library-sync';

const signIn = (id = 'u1'): void => setSession({ token: 'T-' + id, user: { id, name: id, email: id + '@x', picture: '' }, base: 'http://srv', expires: 0 });
const st = (key: string) => ({ source: 's', key, name: 'Truyện ' + key, author: null, poster: null, cover: null, cover_sha: null });
const wFollow = (key: string, ts: number): Record<string, unknown> => ({
  kind: 'follow',
  id: `s|${key}`,
  ts,
  data: { source: 's', key, name: 'R ' + key, author: null, poster: null, cover: null, cover_sha: null, group: null, ts },
});
const wMark = (id: string, ts: number): Record<string, unknown> => ({
  kind: 'bookmark',
  id,
  ts,
  data: { id, source: 's', key: 'k', name: 'K', idx: 1, n: 2, file: 'f', title: 'T', para: 3, excerpt: 'x', ts },
});
const bm = { source: 's', key: 'k', name: 'K', idx: 0, n: 1, file: 'f', title: 'T', para: 1, excerpt: 'e' };

let server: { entries: Record<string, unknown>[]; offset: number };

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(1_000_000);
  localStorage.clear();
  _resetAuth();
  _resetLibrary();
  sync._reset();
  be.kind = 'server';
  be.features = ['progress', 'auth', 'library'];
  be.get.mockReset();
  be.send.mockReset();
  server = { entries: [], offset: 0 };
  be.get.mockImplementation(async () => ({ entries: server.entries, now: Date.now() + server.offset }));
  be.send.mockImplementation(async (_m: string, _p: string, body: { entries: unknown[] }) => ({ entries: body.entries, now: Date.now() + server.offset }));
});
afterEach(() => {
  sync._reset();
  vi.useRealTimers();
});

describe('library applyRemote (last writer wins)', () => {
  it('adds, keeps the newer side and ignores ties and junk', () => {
    library.setFollow(st('a'), true);
    expect(library.applyRemote('follow', [wFollow('a', 999_000)])).toBe(0);
    expect(library.applyRemote('follow', [wFollow('a', 1_000_000)])).toBe(0);
    expect(library.applyRemote('follow', [wFollow('a', 1_005_000)])).toBe(1);
    expect(library.follows()[0]).toMatchObject({ name: 'R a', ts: 1_005_000 });
    expect(library.applyRemote('follow', [wFollow('b', 5), { kind: 'follow', id: 'x', ts: 5, data: {} }, null, wMark('m', 5)])).toBe(1);
    expect(library.follows().map((f) => f.key)).toEqual(['a', 'b']);
  });

  it('moves incoming timestamps into the local clock', () => {
    library.applyRemote('bookmark', [wMark('m1', 10_000)], 4000);
    expect(library.bookmarks()[0]?.ts).toBe(6000);
  });

  it('a newer deletion removes the item and leaves a tombstone; a tie keeps the live item', () => {
    library.setFollow(st('a'), true);
    expect(library.applyRemote('follow', [{ kind: 'follow', id: 's|a', ts: 1_000_000, deleted: true }])).toBe(0);
    expect(library.follows()).toHaveLength(1);
    expect(library.applyRemote('follow', [{ kind: 'follow', id: 's|a', ts: 1_000_001, deleted: true }])).toBe(1);
    expect(library.follows()).toHaveLength(0);
    expect(library.tombstone('follow', 's|a')).toBe(1_000_001);
    expect(library.applyRemote('follow', [wFollow('a', 1_000_000)])).toBe(0);
    expect(library.applyRemote('follow', [wFollow('a', 1_000_002)])).toBe(1);
    expect(library.tombstone('follow', 's|a')).toBeUndefined();
  });

  it('a local deletion stays deleted against an older remote copy', () => {
    library.setFollow(st('a'), true);
    vi.setSystemTime(1_050_000);
    library.setFollow(st('a'), false);
    expect(library.tombstone('follow', 's|a')).toBe(1_050_000);
    expect(library.applyRemote('follow', [wFollow('a', 1_040_000)])).toBe(0);
    expect(library.follows()).toHaveLength(0);
  });

  it('removing and clearing bookmarks leaves tombstones, re-adding clears them; changes are announced', () => {
    const seen: string[] = [];
    library.onLocalChange((k, id, d) => seen.push(`${k}:${id}:${d}`));
    const made = library.addBookmark(bm);
    library.removeBookmark(made.id);
    expect(library.tombstone('bookmark', made.id)).toBeDefined();
    library.addBookmark(bm);
    expect(library.tombstone('bookmark', made.id)).toBeUndefined();
    library.clearBookmarks();
    expect(library.tombstone('bookmark', made.id)).toBeDefined();
    expect(seen).toEqual([`bookmark:${made.id}:false`, `bookmark:${made.id}:true`, `bookmark:${made.id}:false`, `bookmark:${made.id}:true`]);
  });

  it('forgets tombstones older than 60 days', () => {
    localStorage.setItem('mythlab.library.tomb', JSON.stringify({ 'follow|s|old': 1_000_000 - 61 * 24 * 3600 * 1000, 'follow|s|new': 999_000 }));
    expect(library.tombstone('follow', 's|old')).toBeUndefined();
    expect(library.tombstone('follow', 's|new')).toBe(999_000);
  });

  it('does not report remote changes as local ones', () => {
    const cb = vi.fn();
    library.onLocalChange(cb);
    library.applyRemote('follow', [wFollow('z', 5)]);
    expect(cb).not.toHaveBeenCalled();
  });
});

describe('library sync', () => {
  it('does nothing signed out or without the feature', async () => {
    await sync.init();
    expect(be.get).not.toHaveBeenCalled();
    signIn();
    be.features = ['progress'];
    await sync.init();
    expect(be.get).not.toHaveBeenCalled();
  });

  it('first sign-in sends everything local, merges the account down, stores a per-account cursor', async () => {
    library.setFollow(st('mine'), true);
    library.addBookmark(bm);
    server.entries = [wFollow('theirs', 900_000)];
    signIn('u1');
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    expect(be.get).toHaveBeenCalledWith('/library?since=0', expect.anything());
    expect(library.follows().map((f) => f.key).sort()).toEqual(['mine', 'theirs']);
    const sent = (be.send.mock.calls[0] as [string, string, { entries: { kind: string }[] }])[2].entries;
    expect(sent.map((e) => e.kind).sort()).toEqual(['bookmark', 'follow']);
    expect(JSON.parse(localStorage.getItem('mythlab.library.cursor.u1') as string)).toEqual({ base: 'http://srv', since: 999_000 });
    expect(localStorage.getItem('mythlab.library.outbox.u1')).toBeNull();
  });

  it('queues local changes per account and pushes them; deletions go out as tombstones', async () => {
    signIn('u1');
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    be.send.mockClear();
    library.setFollow(st('a'), true);
    expect(JSON.parse(localStorage.getItem('mythlab.library.outbox.u1') as string)).toEqual(['follow|s|a']);
    await vi.advanceTimersByTimeAsync(2000);
    expect(be.send).toHaveBeenCalledTimes(1);
    expect((be.send.mock.calls[0] as unknown[])[1]).toBe('/library');
    library.setFollow(st('a'), false);
    await vi.advanceTimersByTimeAsync(2000);
    const body = (be.send.mock.calls[1] as [string, string, { entries: Record<string, unknown>[] }])[2];
    expect(body.entries[0]).toEqual({ kind: 'follow', id: 's|a', ts: expect.any(Number), deleted: true });
    expect(localStorage.getItem('mythlab.library.outbox.u1')).toBeNull();
  });

  it('switching accounts never sends one account pending changes to the other', async () => {
    signIn('u1');
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    be.send.mockRejectedValue(Object.assign(new Error('down'), { status: 500 }));
    library.setFollow(st('pending'), true);
    await vi.advanceTimersByTimeAsync(2000);
    expect(localStorage.getItem('mythlab.library.outbox.u1')).toContain('follow|s|pending');
    be.send.mockReset();
    be.send.mockImplementation(async (_m: string, _p: string, body: { entries: unknown[] }) => ({ entries: body.entries, now: Date.now() }));
    be.get.mockClear();
    signIn('u2');
    await vi.advanceTimersByTimeAsync(0);
    expect(be.get).toHaveBeenCalledWith('/library?since=0', expect.anything());
    expect(localStorage.getItem('mythlab.library.outbox.u1')).toContain('follow|s|pending');
  });

  it('removes the clock skew from the server time', async () => {
    server.offset = 5000;
    server.entries = [wFollow('theirs', 1_004_000)];
    signIn();
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    expect(library.follows()[0]?.ts).toBe(999_000);
  });

  it('wire data carries the shifted ts', async () => {
    server.offset = 1000;
    signIn();
    library.setFollow(st('a'), true);
    await sync.init();
    await vi.advanceTimersByTimeAsync(0);
    const e = (be.send.mock.calls[0] as [string, string, { entries: { ts: number; data: Record<string, unknown> }[] }])[2].entries[0];
    expect(e?.ts).toBe(1_001_000);
    expect(e?.data).toMatchObject({ source: 's', key: 'a', ts: 1_001_000 });
  });
});
