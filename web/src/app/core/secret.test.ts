import { beforeEach, describe, expect, it, vi } from 'vitest';

const KEY = 'mythlab.ghToken';
const TOKEN = 'github_pat_SUPER_SECRET_123';

/** Fresh copies of store.ts and secret.ts, like a page reload (IndexedDB and localStorage content survive). */
async function reload() {
  vi.resetModules();
  const store = await import('./store');
  store.idb._reset();
  const secret = await import('./secret');
  return { ...secret, idb: store.idb };
}

beforeEach(async () => {
  vi.unstubAllGlobals();
  localStorage.clear();
  await new Promise<void>((res) => {
    const r = indexedDB.deleteDatabase('mythlab');
    r.onsuccess = r.onerror = r.onblocked = () => res();
  });
});

describe('secret: encryption at rest', () => {
  it('round-trips a token and stores only {v,iv,ct}', async () => {
    const s = await reload();
    await s.initSecret();
    expect(s.peekToken()).toBe('');
    await s.setToken(TOKEN);
    expect(s.peekToken()).toBe(TOKEN);
    expect(await s.getToken()).toBe(TOKEN);
    expect(s.isProtected()).toBe(true);
    const raw = localStorage.getItem(KEY) as string;
    expect(raw).not.toContain('SECRET');
    const o = JSON.parse(raw) as { v: number; iv: string; ct: string };
    expect(o.v).toBe(1);
    expect(o.iv).toMatch(/^[A-Za-z0-9+/]+=*$/);
    expect(o.ct).toMatch(/^[A-Za-z0-9+/]+=*$/);
  });

  it('uses a fresh IV for every write', async () => {
    const s = await reload();
    await s.setToken(TOKEN);
    const a = JSON.parse(localStorage.getItem(KEY) as string).iv;
    await s.setToken(TOKEN);
    expect(JSON.parse(localStorage.getItem(KEY) as string).iv).not.toBe(a);
  });

  it('keeps the key across a reload and decrypts with it', async () => {
    const a = await reload();
    await a.setToken(TOKEN);
    const b = await reload();
    expect(b.peekToken()).toBe('');
    await b.initSecret();
    expect(b.peekToken()).toBe(TOKEN);
    expect(b.isProtected()).toBe(true);
  });

  it('creates a non-extractable key and keeps the other IndexedDB stores', async () => {
    const s = await reload();
    await s.idb.put('meta', 'x', { a: 1 });
    await s.setToken(TOKEN);
    const k = await s.idb.secretGet<CryptoKey>('token-key-v1');
    expect(k?.extractable).toBe(false);
    await expect(crypto.subtle.exportKey('raw', k as CryptoKey)).rejects.toThrow();
    // "Xoá bộ nhớ đệm" must not destroy the key
    await s.idb.clear();
    expect(await s.idb.secretGet('token-key-v1')).toBeTruthy();
    const t = await reload();
    await t.initSecret();
    expect(t.peekToken()).toBe(TOKEN);
  });

  it('migrates a legacy plaintext token and never leaves plaintext', async () => {
    localStorage.setItem(KEY, JSON.stringify(TOKEN));
    const s = await reload();
    await s.initSecret();
    expect(s.peekToken()).toBe(TOKEN);
    expect(localStorage.getItem(KEY)).not.toContain('SECRET');
    expect(JSON.parse(localStorage.getItem(KEY) as string).v).toBe(1);
    const t = await reload();
    await t.initSecret();
    expect(t.peekToken()).toBe(TOKEN);
  });

  it('upgrades a version 1 database without losing data', async () => {
    await new Promise<void>((res) => {
      const r = indexedDB.open('mythlab', 1);
      r.onupgradeneeded = () => {
        for (const n of ['trees', 'blobs', 'meta']) r.result.createObjectStore(n);
      };
      r.onsuccess = () => {
        const t = r.result.transaction('meta', 'readwrite');
        t.objectStore('meta').put('kept', 'k');
        t.oncomplete = () => {
          r.result.close();
          res();
        };
      };
    });
    const s = await reload();
    await s.setToken(TOKEN);
    expect(await s.idb.get('meta', 'k')).toBe('kept');
    const t = await reload();
    await t.initSecret();
    expect(t.peekToken()).toBe(TOKEN);
  });

  it('drops corrupted or tampered ciphertext instead of throwing', async () => {
    const a = await reload();
    await a.setToken(TOKEN);
    const o = JSON.parse(localStorage.getItem(KEY) as string);
    const bytes = atob(o.ct).split('');
    bytes[0] = String.fromCharCode(bytes[0]!.charCodeAt(0) ^ 1);
    localStorage.setItem(KEY, JSON.stringify({ ...o, ct: btoa(bytes.join('')) }));
    const b = await reload();
    await b.initSecret();
    expect(b.peekToken()).toBe('');
    expect(localStorage.getItem(KEY)).not.toBeNull(); // kept: a transient IndexedDB failure must not destroy the token

    localStorage.setItem(KEY, JSON.stringify({ v: 1, iv: '!!!', ct: '???' }));
    const c = await reload();
    await c.initSecret();
    expect(c.peekToken()).toBe('');
  });

  it('drops a sealed token whose key is gone', async () => {
    const a = await reload();
    await a.setToken(TOKEN);
    await a.idb.secretDel('token-key-v1');
    const b = await reload();
    await b.initSecret();
    expect(b.peekToken()).toBe('');
  });

  it('forgets the token', async () => {
    const s = await reload();
    await s.setToken(TOKEN);
    await s.clearToken();
    expect(s.peekToken()).toBe('');
    expect(localStorage.getItem(KEY)).toBeNull();
  });

  it('keeps writes in order', async () => {
    const s = await reload();
    void s.setToken('one');
    void s.setToken('two');
    await s.setToken('three');
    const t = await reload();
    await t.initSecret();
    expect(t.peekToken()).toBe('three');
  });

  it('falls back to plaintext without crypto.subtle (insecure origin)', async () => {
    vi.stubGlobal('crypto', { getRandomValues: crypto.getRandomValues.bind(crypto) });
    const s = await reload();
    await s.initSecret();
    expect(s.isProtected()).toBe(false);
    expect(s.protectionHint()).toMatch(/không hỗ trợ mã hóa/);
    await s.setToken(TOKEN);
    expect(JSON.parse(localStorage.getItem(KEY) as string)).toBe(TOKEN);
    expect(s.isProtected()).toBe(false);
    // legacy plaintext stays readable
    const t = await reload();
    await t.initSecret();
    expect(t.peekToken()).toBe(TOKEN);
  });

  it('falls back to plaintext without IndexedDB', async () => {
    vi.stubGlobal('indexedDB', undefined);
    const s = await reload();
    await s.setToken(TOKEN);
    expect(s.isProtected()).toBe(false);
    expect(JSON.parse(localStorage.getItem(KEY) as string)).toBe(TOKEN);
  });

  it('reports protection and the Vietnamese hint when encryption works', async () => {
    const s = await reload();
    await s.setToken(TOKEN);
    expect(s.protectionHint()).toMatch(/được mã hóa/);
  });
});
