/* MythLab — ML.store (localStorage JSON) + ML.idb (IndexedDB: trees, blobs, meta; RAM khi không có IndexedDB) */
(function () {
  "use strict";
  const ML = (window.ML = window.ML || {});

  const mem = new Map();
  let ls = null;
  try { ls = window.localStorage; ls.getItem("__ml"); } catch { ls = null; }
  ML.store = {
    get(key, def) {
      try {
        const v = ls ? ls.getItem(key) : mem.has(key) ? mem.get(key) : null;
        return v == null ? def : JSON.parse(v);
      } catch { return def; }
    },
    set(key, val) {
      try { const s = JSON.stringify(val); if (ls) ls.setItem(key, s); else mem.set(key, s); } catch { /* đầy/bị chặn */ }
    },
    del(key) {
      try { if (ls) ls.removeItem(key); else mem.delete(key); } catch { /* ignore */ }
    },
  };

  const STORES = ["trees", "blobs", "meta"];
  // không có IndexedDB (node, chặn lưu trữ): cache RAM có giới hạn (LRU)
  const ram = Object.fromEntries(STORES.map((s) => [s, new Map()]));
  const CAP = { trees: 400, blobs: 300, meta: 5000 };
  let dbp = null;
  function db() {
    if (dbp) return dbp;
    dbp = new Promise((resolve) => {
      try {
        if (typeof indexedDB === "undefined") return resolve(null);
        const req = indexedDB.open("mythlab", 1);
        req.onupgradeneeded = () => { for (const s of STORES) if (!req.result.objectStoreNames.contains(s)) req.result.createObjectStore(s); };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => resolve(null);
        req.onblocked = () => resolve(null);
      } catch { resolve(null); }
    });
    return dbp;
  }
  function tx(store, mode, fn) {
    return db().then((d) => new Promise((resolve) => {
      try {
        const t = d.transaction(store, mode);
        const r = fn(t.objectStore(store));
        t.oncomplete = () => resolve(r ? r.result : undefined);
        t.onerror = t.onabort = () => resolve(undefined);
      } catch { resolve(undefined); }
    }));
  }
  ML.idb = {
    async get(store, key) {
      const m = ram[store];
      if (m.has(key)) { const v = m.get(key); m.delete(key); m.set(key, v); return v; }
      if (!(await db())) return undefined;
      return tx(store, "readonly", (s) => s.get(key));
    },
    async put(store, key, val) {
      if (!(await db())) {
        const m = ram[store];
        m.delete(key); m.set(key, val);
        if (m.size > CAP[store]) m.delete(m.keys().next().value);
        return;
      }
      await tx(store, "readwrite", (s) => s.put(val, key));
    },
    async clear() {
      for (const s of STORES) ram[s].clear();
      if (!(await db())) return;
      for (const s of STORES) await tx(s, "readwrite", (o) => o.clear());
    },
  };
})();
