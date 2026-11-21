import { beforeEach, describe, expect, it } from 'vitest';
import { SERVER_KEY, TOKEN_KEY } from '../core/backend/index';
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

  it('leaves secrets out unless asked and restores them only when asked', () => {
    localStorage.setItem(TOKEN_KEY, JSON.stringify('github_pat_SECRET'));
    localStorage.setItem(SERVER_KEY, JSON.stringify({ url: 'http://x:1', key: 'LANKEY' }));
    expect(JSON.stringify(buildBackup())).not.toMatch(/SECRET|LANKEY/);
    const withS = buildBackup({ includeSecrets: true });
    expect(JSON.stringify(withS)).toMatch(/SECRET/);
    localStorage.clear();
    applyBackup(parseBackup(JSON.stringify(withS)), { mode: 'merge', includeSecrets: false });
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
    applyBackup(parseBackup(JSON.stringify(withS)), { mode: 'merge', includeSecrets: true });
    expect(localStorage.getItem(TOKEN_KEY)).toMatch(/SECRET/);
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
