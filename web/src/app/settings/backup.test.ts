import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SERVER_KEY, TOKEN_KEY } from '../core/backend/index';
import { setSession, _resetAuth } from '../core/auth-token';
import { initSecret, flushToken, peekToken, _resetSecret } from '../core/secret';
import { library } from '../core/library';
import { progress } from '../core/progress';
import { S, init, load, set } from '../core/settings';
import { applyBackup, BackupError, backupFileName, buildBackup, cleanSettings, mergeBackup, parseBackup } from './backup';

const story = { source: 's', key: 'k1', name: 'Truyện 1', idx: 4, n: 5, total: 10, para: 2, ts: 1000 };

beforeEach(() => {
  localStorage.clear();
  load();
  init();
  progress.init();
  library.init();
});

describe('backup', () => {
  it('round-trips settings and progress', () => {
    set('size', 26);
    set('theme', 'dark');
    progress.update(story);
    const text = JSON.stringify(buildBackup({ now: 0 }));
    localStorage.clear();
    load();
    expect(S.size).not.toBe(26);
    applyBackup(parseBackup(text), { mode: 'replace' });
    expect(S.size).toBe(26);
    expect(S.theme).toBe('dark');
    expect(progress.get('s', 'k1')?.idx).toBe(4);
  });

  it('never exports the Google session token or the sync state', () => {
    _resetAuth();
    setSession({ token: 'BEARER-SECRET', user: { id: 'u1', name: 'An', email: 'an@x.vn', picture: '' }, base: 'http://x:1', expires: 0 });
    localStorage.setItem('mythlab.library.outbox.u1', JSON.stringify(['follow|s|a']));
    expect(JSON.stringify(buildBackup())).not.toMatch(/BEARER-SECRET|mythlab\.auth|an@x\.vn/);
    expect(JSON.stringify(buildBackup({ includeSecrets: true }))).not.toMatch(/BEARER-SECRET|an@x\.vn/);
    _resetAuth();
  });

  it('leaves secrets out unless asked and restores them only when asked', async () => {
    _resetSecret();
    localStorage.setItem(TOKEN_KEY, JSON.stringify('github_pat_SECRET'));
    await initSecret();
    localStorage.setItem(SERVER_KEY, JSON.stringify({ url: 'http://x:1', key: 'LANKEY' }));
    expect(JSON.stringify(buildBackup())).not.toMatch(/SECRET|LANKEY/);
    const withS = buildBackup({ includeSecrets: true });
    expect(JSON.stringify(withS)).toMatch(/SECRET/);
    localStorage.clear();
    _resetSecret();
    applyBackup(parseBackup(JSON.stringify(withS)), { mode: 'merge', includeSecrets: false });
    await flushToken();
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
    applyBackup(parseBackup(JSON.stringify(withS)), { mode: 'merge', includeSecrets: true });
    await flushToken();
    // the imported plaintext token goes through setToken: encrypted at rest, readable in memory
    expect(peekToken()).toBe('github_pat_SECRET');
    expect(localStorage.getItem(TOKEN_KEY)).not.toMatch(/SECRET/);
    expect(JSON.parse(localStorage.getItem(TOKEN_KEY) as string).v).toBe(1);
  });

  it('rejects files that are not backups', () => {
    expect(() => parseBackup('not json')).toThrow(BackupError);
    expect(() => parseBackup('[]')).toThrow(BackupError);
    expect(() => parseBackup(JSON.stringify({ format: 'other', version: 1 }))).toThrow(BackupError);
  });

  it('validates settings: clamps, drops bad values and unsafe keys', () => {
    const c = cleanSettings({ size: 9999, theme: 'neon', autoNext: 'yes', 'bad key!': 1, extra: 'ok' });
    expect(c.size).toBeLessThan(9999);
    expect(c.theme).not.toBe('neon');
    expect(typeof c.autoNext).toBe('boolean');
    expect(c).not.toHaveProperty('bad key!');
    expect(c.extra).toBe('ok');
  });

  it('merge keeps the newer progress, replace takes the file', () => {
    progress.update({ ...story, idx: 8, ts: 5000 }, { now: false });
    const cur = buildBackup();
    const id = Object.keys(cur.progress)[0];
    const file = { ...cur, progress: { [id]: { ...cur.progress[id], idx: 1, ts: 1 } } };
    expect(Object.values(mergeBackup(cur, file, 'merge').progress)[0].idx).toBe(8);
    expect(Object.values(mergeBackup(cur, file, 'replace').progress)[0].idx).toBe(1);
  });

  it('names the file by date', () => {
    expect(backupFileName(Date.UTC(2026, 0, 5))).toBe('mythlab-sao-luu-2026-01-05.json');
  });
});

describe('backup hardening', () => {
  it('ignores prototype-named settings keys instead of throwing', () => {
    const text = '{"format":"mythlab-backup","version":1,"settings":{"constructor":5,"toString":1,"__proto__":{"x":1},"size":24}}';
    const b = parseBackup(text);
    expect(b.settings.size).toBe(24);
  });

  it('caps progress to MAX_ENTRIES in replace mode', () => {
    const prog: Record<string, unknown> = {};
    for (let i = 0; i < 520; i++) prog['s|k' + i] = { source: 's', key: 'k' + i, ts: i };
    const b = parseBackup(JSON.stringify({ format: 'mythlab-backup', version: 1, progress: prog }));
    const out = mergeBackup(buildBackup(), b, 'replace');
    expect(Object.keys(out.progress)).toHaveLength(500);
    expect(out.progress['s|k519']).toBeDefined();
    expect(out.progress['s|k0']).toBeUndefined();
  });

  it('rolls back every key when a write fails midway', () => {
    library.addBookmark({ source: 's', key: 'old', name: 'old', idx: 0, n: 1, file: 'f', title: 't', para: 0, excerpt: '' });
    const before = localStorage.getItem('mythlab.bookmarks');
    const b = parseBackup(JSON.stringify({ format: 'mythlab-backup', version: 1, settings: { size: 30 }, progress: { 's|k': { source: 's', key: 'k', ts: 1 } }, bookmarks: [], follows: [] }));
    const real = localStorage.setItem.bind(localStorage);
    let fails = 0;
    const spy = vi.spyOn(localStorage, 'setItem').mockImplementation((k: string, v: string) => {
      if (k === 'mythlab.follows' && fails++ === 0) throw new DOMException('full', 'QuotaExceededError');
      real(k, v);
    });
    expect(() => applyBackup(b, { mode: 'replace' })).toThrow(BackupError);
    spy.mockRestore();
    expect(localStorage.getItem('mythlab.bookmarks')).toBe(before);
    expect(localStorage.getItem('mythlab.progress')).toBeNull();
  });
});
