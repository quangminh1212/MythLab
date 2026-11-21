/**
 * Persistence primitives. Names and shapes are frozen (users keep their data across the rewrite):
 *  - localStorage keys `mythlab.*`, values JSON-encoded (a token is stored with quotes);
 *  - IndexedDB database `mythlab`, version 2, object stores `trees`, `blobs`, `meta` (out-of-line keys) and, since
 *    version 2, `secrets` (the non-extractable encryption key of core/secret.ts; never emptied by `idb.clear()`).
 * Both fall back to memory when the browser blocks storage, so the app still works for the session.
 */

const mem = new Map<string, string>();
let ls: Storage | null = null;
try {
  ls = globalThis.localStorage;
  ls.getItem('__ml');
} catch {
  ls = null;
}

/** Copies legacy `xlab.settings|progress|sort` to `mythlab.*` when the new key is absent, then removes the old key. */
export function migrateLegacy(): void {
  if (!ls) return;
  try {
    for (const k of ['settings', 'progress', 'sort']) {
      const old = ls.getItem('xlab.' + k);
      if (old == null) continue;
      if (ls.getItem('mythlab.' + k) == null) ls.setItem('mythlab.' + k, old);
      ls.removeItem('xlab.' + k);
    }
  } catch {
    /* storage blocked or full: keep the legacy keys */
  }
}
migrateLegacy();

export const store = {
  /** Parsed value, or `def` when the key is missing or unreadable. */
  get<T>(key: string, def: T): T {
    try {
      const v = ls ? ls.getItem(key) : mem.has(key) ? (mem.get(key) as string) : null;
      return v == null ? def : (JSON.parse(v) as T);
    } catch {
      return def;
    }
  },
  /** Returns false when the write failed (quota, blocked storage) so callers can tell the user. */
  set(key: string, val: unknown): boolean {
    try {
      const s = JSON.stringify(val);
      if (ls) ls.setItem(key, s);
      else mem.set(key, s);
      return true;
    } catch {
      return false;
    }
  },
  del(key: string): void {
    try {
      if (ls) ls.removeItem(key);
      else mem.delete(key);
    } catch {
      /* ignore */
    }
  },
  /** True when values survive a reload (real localStorage). */
  persistent(): boolean {
    return !!ls;
  },
};

export type IdbStore = 'trees' | 'blobs' | 'meta';
const STORES: IdbStore[] = ['trees', 'blobs', 'meta'];
/** Object stores that exist in the database; `secrets` is deliberately not part of the cache stores above. */
const ALL_STORES = [...STORES, 'secrets'] as const;
const DB_VERSION = 2;
const CAP: Record<IdbStore, number> = { trees: 400, blobs: 300, meta: 5000 };
const ram: Record<IdbStore, Map<string, unknown>> = { trees: new Map(), blobs: new Map(), meta: new Map() };

let dbp: Promise<IDBDatabase | null> | null = null;
function db(): Promise<IDBDatabase | null> {
  if (dbp) return dbp;
  dbp = new Promise((resolve) => {
    try {
      if (typeof indexedDB === 'undefined') return resolve(null);
      const req = indexedDB.open('mythlab', DB_VERSION);
      req.onupgradeneeded = () => {
        // v1 -> v2 only adds `secrets`; existing stores and their data are kept
        for (const s of ALL_STORES) if (!req.result.objectStoreNames.contains(s)) req.result.createObjectStore(s);
      };
      req.onsuccess = () => {
        const d = req.result;
        // another tab upgrading or deleting the database must not be blocked by this connection
        d.onversionchange = () => {
          d.close();
          dbp = null;
        };
        resolve(d);
      };
      req.onerror = () => resolve(null);
      req.onblocked = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
  return dbp;
}

function tx<T>(name: IdbStore | 'secrets', mode: IDBTransactionMode, fn: (s: IDBObjectStore) => IDBRequest<T> | void): Promise<T | undefined> {
  return db().then(
    (d) =>
      new Promise<T | undefined>((resolve) => {
        if (!d) return resolve(undefined);
        try {
          const t = d.transaction(name, mode);
          const r = fn(t.objectStore(name));
          t.oncomplete = () => resolve(r ? r.result : undefined);
          t.onerror = t.onabort = () => resolve(undefined);
        } catch {
          resolve(undefined);
        }
      }),
  );
}

export const idb = {
  async get<T = unknown>(name: IdbStore, key: string): Promise<T | undefined> {
    const m = ram[name];
    if (m.has(key)) {
      const v = m.get(key);
      m.delete(key);
      m.set(key, v);
      return v as T;
    }
    if (!(await db())) return undefined;
    return tx<T>(name, 'readonly', (s) => s.get(key) as IDBRequest<T>);
  },
  async put(name: IdbStore, key: string, val: unknown): Promise<void> {
    if (!(await db())) {
      const m = ram[name];
      m.delete(key);
      m.set(key, val);
      if (m.size > CAP[name]) m.delete(m.keys().next().value as string);
      return;
    }
    await tx(name, 'readwrite', (s) => s.put(val, key));
  },
  async del(name: IdbStore, key: string): Promise<void> {
    ram[name].delete(key);
    if (!(await db())) return;
    await tx(name, 'readwrite', (s) => s.delete(key));
  },
  /** Empties all three stores (the "Xoá bộ nhớ đệm" action). */
  async clear(): Promise<void> {
    for (const s of STORES) ram[s].clear();
    if (!(await db())) return;
    for (const s of STORES) await tx(s, 'readwrite', (o) => o.clear());
  },
  /** Persistent-only access to the `secrets` store (no memory fallback: a key that cannot survive a reload is useless). */
  async secretGet<T = unknown>(key: string): Promise<T | undefined> {
    return tx<T>('secrets', 'readonly', (s) => s.get(key) as IDBRequest<T>);
  },
  /** Stores `val` only when `key` is free; true when it was written (false: already there, or no database). */
  async secretAdd(key: string, val: unknown): Promise<boolean> {
    return (await tx('secrets', 'readwrite', (s) => s.add(val, key))) !== undefined;
  },
  async secretDel(key: string): Promise<void> {
    await tx('secrets', 'readwrite', (s) => s.delete(key));
  },
  /** Test hook: forget the cached connection and the memory fallback. */
  _reset(): void {
    dbp = null;
    for (const s of STORES) ram[s].clear();
  },
};
