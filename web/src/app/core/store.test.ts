import { beforeEach, describe, expect, it } from 'vitest';
import { idb, migrateLegacy, store } from './store';

beforeEach(() => {
  localStorage.clear();
});

describe('store (localStorage)', () => {
  it('round-trips JSON values under the frozen key names', () => {
    expect(store.set('mythlab.sort', { gh0: 'chapters' })).toBe(true);
    expect(localStorage.getItem('mythlab.sort')).toBe('{"gh0":"chapters"}');
    expect(store.get('mythlab.sort', {})).toEqual({ gh0: 'chapters' });
    store.set('mythlab.ghToken', 'abc');
    expect(localStorage.getItem('mythlab.ghToken')).toBe('"abc"');
    store.del('mythlab.ghToken');
    expect(store.get('mythlab.ghToken', null)).toBeNull();
  });

  it('returns the default for missing or corrupt values', () => {
    expect(store.get('mythlab.none', 7)).toBe(7);
    localStorage.setItem('mythlab.bad', '{not json');
    expect(store.get('mythlab.bad', 'd')).toBe('d');
  });

  it('migrates xlab.* keys once and never overwrites newer mythlab.* data', () => {
    localStorage.setItem('xlab.settings', '{"size":22}');
    localStorage.setItem('xlab.progress', '{"a|b":{"source":"a","key":"b"}}');
    localStorage.setItem('xlab.sort', '{"old":1}');
    localStorage.setItem('mythlab.sort', '{"new":1}');
    migrateLegacy();
    expect(store.get('mythlab.settings', null)).toEqual({ size: 22 });
    expect(store.get('mythlab.progress', null)).toEqual({ 'a|b': { source: 'a', key: 'b' } });
    expect(store.get('mythlab.sort', null)).toEqual({ new: 1 });
    expect(localStorage.getItem('xlab.settings')).toBeNull();
    expect(localStorage.getItem('xlab.progress')).toBeNull();
    expect(localStorage.getItem('xlab.sort')).toBeNull();
    migrateLegacy();
    expect(store.get('mythlab.settings', null)).toEqual({ size: 22 });
  });
});

describe('idb (IndexedDB "mythlab" v1)', () => {
  it('stores and reads values in the three object stores', async () => {
    await idb.put('trees', 'k1', { tree: [1, 2] });
    await idb.put('meta', 'k1', 'm');
    expect(await idb.get('trees', 'k1')).toEqual({ tree: [1, 2] });
    expect(await idb.get('meta', 'k1')).toBe('m');
    expect(await idb.get('blobs', 'k1')).toBeUndefined();
  });

  it('opens the database with the frozen name, version and stores', async () => {
    await idb.put('blobs', 'x', 1);
    const db = await new Promise<IDBDatabase>((resolve, reject) => {
      const r = indexedDB.open('mythlab');
      r.onsuccess = () => resolve(r.result);
      r.onerror = () => reject(r.error);
    });
    expect(db.version).toBe(1);
    expect([...db.objectStoreNames].sort()).toEqual(['blobs', 'meta', 'trees']);
    db.close();
  });

  it('clear() empties every store', async () => {
    await idb.put('trees', 'a', 1);
    await idb.put('blobs', 'b', 2);
    await idb.clear();
    expect(await idb.get('trees', 'a')).toBeUndefined();
    expect(await idb.get('blobs', 'b')).toBeUndefined();
  });
});
