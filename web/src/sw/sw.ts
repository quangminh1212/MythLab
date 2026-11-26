/**
 * MythLab service worker. Built by src/sw/integration.mjs into dist/sw.js after `astro build`, with the list of
 * shell files and a build id injected as __SW_MANIFEST__.
 *
 *  - Shell: every file of the build (except the font files) is precached under `mythlab-shell-<build>`. The
 *    install fails as a whole when one file cannot be fetched, so a half-cached shell is never activated.
 *  - Navigation: network first, falling back to the precached shell. Navigation responses are never written to
 *    a cache, so opening a stylesheet or a directory listing in a tab cannot replace the shell (bugs.md W1).
 *  - /api/chapter: stale-while-revalidate from the pinned bucket (downloads) and an LRU bucket (recent reads).
 *  - /api/sources|stories|story|voices: network first, last good answer when the network is gone.
 *  - /api/cover: cache first, revalidated in the background when older than a day (W2). /api/tts (removed from the server, kept for old clients): cache first.
 *    Both keep their old bucket names; the LRU order lives in a small index, bodies are not rewritten (W3).
 *  - Update: a new worker waits until the page asks it to take over (SKIP_WAITING), so one tab never mixes two
 *    builds. Old `mythlab-shell-*` buckets and the unversioned `mythlab-static` of worker v3 are deleted on
 *    activation.
 */
import { Lru } from './lru';
import { apiRoute, CACHE, chapterKey, chapterParams, fingerprint, HDR_AT, identUrl, KEY_HEADER, HDR_SIZE, LIMIT, parseRange, type SwActivated, type SwRequest, type SwVersion } from './shared';

declare const __SW_MANIFEST__: { v: string; files: string[] };

// Minimal worker types: the project compiles against the DOM library, which has no ServiceWorkerGlobalScope.
interface ExtendableEventLike extends Event {
  waitUntil(p: Promise<unknown>): void;
}
interface FetchEventLike extends ExtendableEventLike {
  readonly request: Request;
  respondWith(r: Promise<Response> | Response): void;
}
interface MessageEventLike extends ExtendableEventLike {
  readonly data: unknown;
  readonly ports: readonly MessagePort[];
}
interface ClientLike {
  postMessage(message: unknown): void;
}
interface WorkerScope {
  readonly registration: { readonly scope: string };
  readonly location: { readonly origin: string };
  skipWaiting(): Promise<void>;
  readonly clients: {
    claim(): Promise<void>;
    matchAll(o?: { type?: 'window'; includeUncontrolled?: boolean }): Promise<ClientLike[]>;
  };
  addEventListener(type: 'install' | 'activate', fn: (e: ExtendableEventLike) => void): void;
  addEventListener(type: 'fetch', fn: (e: FetchEventLike) => void): void;
  addEventListener(type: 'message', fn: (e: MessageEventLike) => void): void;
}

const sw = self as unknown as WorkerScope;
const MANIFEST = __SW_MANIFEST__;
const SCOPE = sw.registration.scope;
const SHELL = CACHE.shellPrefix + MANIFEST.v;
const SHELL_URL = SCOPE + 'index.html';
const PRECACHED = new Set(MANIFEST.files.map((f) => SCOPE + f));

const DAY = 86_400_000;
const CHAPTER_FRESH = 6 * 3_600_000;
const COVER_FRESH = DAY;
const FONT_FRESH = 30 * DAY;
// the precached shell is always valid, so a stalled network must not hold the first paint for long
const NAV_TIMEOUT = 1500;
const PING_TIMEOUT = 2500;

// ---------------------------------------------------------------- helpers

const isHtml = (res: Response): boolean => /^text\/html\b/i.test(res.headers.get('content-type') || '');

function timeout<T>(p: Promise<T>, ms: number): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('timeout')), ms);
    p.then(
      (v) => {
        clearTimeout(t);
        resolve(v);
      },
      (e) => {
        clearTimeout(t);
        reject(e);
      },
    );
  });
}

/** A storable copy of a response: 200, the few headers worth keeping, the time and the size. */
async function stamped(res: Response): Promise<Response> {
  const buf = await res.arrayBuffer();
  const h = new Headers();
  for (const k of ['content-type', 'etag', 'last-modified']) {
    const v = res.headers.get(k);
    if (v) h.set(k, v);
  }
  h.set(HDR_AT, String(Date.now()));
  h.set(HDR_SIZE, String(buf.byteLength));
  return new Response(buf, { status: 200, headers: h });
}

/** Age of a stored entry in ms; entries without a stamp (written by worker v3) count as old. */
function age(res: Response): number {
  const at = Number(res.headers.get(HDR_AT));
  return Number.isFinite(at) && at > 0 ? Date.now() - at : Infinity;
}

/** True for a response whose body may be stored: a complete, readable 200. */
const storable = (res: Response): boolean => res.status === 200 && res.type !== 'opaque' && res.type !== 'opaqueredirect';

// ---------------------------------------------------------------- LRU buckets

class Bucket {
  readonly name: string;
  readonly max: number;
  private idx: Promise<Lru> | null = null;
  private timer: Promise<void> | null = null;

  constructor(name: string, max: number) {
    this.name = name;
    this.max = max;
  }

  private open(): Promise<Cache> {
    return caches.open(this.name);
  }

  private metaUrl(): string {
    return `${SCOPE}__meta/lru/${this.name}`;
  }

  /** The index, loaded once per worker life and aligned with what the cache really holds. */
  private index(): Promise<Lru> {
    if (!this.idx) {
      this.idx = (async () => {
        let saved: unknown = null;
        try {
          const m = await (await caches.open(CACHE.meta)).match(this.metaUrl());
          if (m) saved = await m.json();
        } catch {
          /* no index yet */
        }
        const lru = new Lru(this.max, saved);
        try {
          const c = await this.open();
          const gone = lru.sync((await c.keys()).map((r) => r.url));
          await Promise.all(gone.map((k) => c.delete(k)));
        } catch {
          /* storage unavailable: the bucket simply stays empty */
        }
        return lru;
      })();
    }
    return this.idx;
  }

  /** Forget the index (the page deleted caches). */
  reset(): void {
    this.idx = null;
  }

  async match(url: string): Promise<Response | undefined> {
    const hit = await (await this.open()).match(url);
    if (hit) (await this.index()).touch(url);
    return hit;
  }

  async put(url: string, res: Response): Promise<void> {
    const c = await this.open();
    await c.put(url, res);
    const gone = (await this.index()).add(url);
    await Promise.all(gone.map((k) => c.delete(k)));
  }

  /** Writes the index a little later, once for a burst of uses. Hand the promise to `waitUntil`. */
  settle(): Promise<void> {
    if (!this.timer) {
      this.timer = new Promise<void>((r) => setTimeout(r, 3000)).then(async () => {
        this.timer = null;
        try {
          const lru = this.idx ? await this.idx : null;
          if (!lru || !lru.dirty) return;
          await (await caches.open(CACHE.meta)).put(this.metaUrl(), new Response(JSON.stringify(lru), { headers: { 'Content-Type': 'application/json' } }));
        } catch {
          /* the next burst writes it */
        }
      });
    }
    return this.timer;
  }
}

const tts = new Bucket(CACHE.tts, LIMIT.tts);
const covers = new Bucket(CACHE.covers, LIMIT.covers);
const chapters = new Bucket(CACHE.chapters, LIMIT.chapters);
const api = new Bucket(CACHE.api, LIMIT.api);
const assets = new Bucket(CACHE.assets, LIMIT.assets);
const BUCKETS = [tts, covers, chapters, api, assets];

/** Key prefixes of stories being downloaded right now → expiry time. */
const pinning = new Map<string, number>();
function isPinning(key: string): boolean {
  const now = Date.now();
  for (const [prefix, until] of pinning) {
    if (until < now) pinning.delete(prefix);
    else if (key.startsWith(prefix)) return true;
  }
  return false;
}

// ---------------------------------------------------------------- server / key identity

const IDENT_URL = `${SCOPE}__meta/ident`;
/** origin -> fingerprint of the key last used with it (loaded from the meta cache on first use). */
let seen: Promise<Map<string, string>> | null = null;
let identChain: Promise<unknown> = Promise.resolve();

function loadSeen(): Promise<Map<string, string>> {
  if (!seen) {
    seen = (async () => {
      const m = new Map<string, string>();
      try {
        const r = await (await caches.open(CACHE.meta)).match(IDENT_URL);
        if (r) for (const [o, f] of Object.entries((await r.json()) as Record<string, string>)) if (typeof f === 'string') m.set(o, f);
      } catch {
        /* nothing remembered */
      }
      return m;
    })();
  }
  return seen;
}

/** Deletes every answer stored under a (possibly stale) identity: API data, covers and audio. Downloads stay. */
async function purgePrivate(): Promise<void> {
  for (const b of [tts, covers, api]) {
    await caches.delete(b.name).catch(() => false);
    b.reset();
  }
}

/**
 * Identity of a request's server + key. When the key used with an origin differs from the one seen before, the
 * private buckets are purged first, so nothing fetched with the old key can be served.
 */
function identity(req: Request): Promise<string> {
  const run = async (): Promise<string> => {
    const origin = new URL(req.url).origin;
    const id = await fingerprint(origin, req.headers.get(KEY_HEADER) || '');
    const known = await loadSeen();
    const before = known.get(origin);
    if (before !== id) {
      known.set(origin, id);
      if (before !== undefined) await purgePrivate();
      try {
        await (await caches.open(CACHE.meta)).put(IDENT_URL, new Response(JSON.stringify(Object.fromEntries(known)), { headers: { 'Content-Type': 'application/json' } }));
      } catch {
        /* remembered in memory only */
      }
    }
    return id;
  };
  const next = identChain.then(run, run);
  identChain = next.catch(() => {});
  return next;
}

// ---------------------------------------------------------------- install / activate

async function precache(): Promise<void> {
  const cache = await caches.open(SHELL);
  const files = MANIFEST.files.slice();
  let failed: Error | null = null;
  const worker = async (): Promise<void> => {
    while (files.length && !failed) {
      const file = files.shift() as string;
      const shell = file === 'index.html';
      try {
        // the shell is requested as "./" so servers that redirect /index.html still answer with the document
        let res = await fetch(new Request(shell ? SCOPE : SCOPE + file, { cache: 'reload', credentials: 'same-origin' }));
        if (!res.ok) throw new Error(`${file}: HTTP ${res.status}`);
        if (shell && !isHtml(res)) throw new Error('index.html: not an HTML document');
        // a redirected response cannot answer a navigation: store a clean copy
        if (res.redirected) res = new Response(await res.blob(), { status: 200, headers: res.headers });
        await cache.put(SCOPE + file, res);
      } catch (e) {
        failed = e instanceof Error ? e : new Error(String(e));
      }
    }
  };
  await Promise.all(Array.from({ length: 6 }, worker));
  if (failed) {
    await caches.delete(SHELL).catch(() => false);
    throw failed;
  }
}

sw.addEventListener('install', (e) => {
  // no skipWaiting here: the page decides when the new build takes over (see pwa.ts)
  e.waitUntil(precache());
});

sw.addEventListener('activate', (e) => {
  e.waitUntil(
    (async () => {
      for (const name of await caches.keys()) {
        if ((name.startsWith(CACHE.shellPrefix) && name !== SHELL) || name === CACHE.legacyStatic || (CACHE.legacyIdentity as readonly string[]).includes(name)) await caches.delete(name);
      }
      await sw.clients.claim();
      const msg: SwActivated = { type: 'ACTIVATED', version: MANIFEST.v, files: MANIFEST.files };
      for (const c of await sw.clients.matchAll({ type: 'window', includeUncontrolled: true })) c.postMessage(msg);
    })(),
  );
});

sw.addEventListener('message', (e) => {
  const d = e.data as SwRequest | 'skipWaiting' | null;
  // 'skipWaiting' (a bare string) is what the old app sent
  if (d === 'skipWaiting' || (d && typeof d === 'object' && d.type === 'SKIP_WAITING')) {
    e.waitUntil(sw.skipWaiting());
    return;
  }
  if (!d || typeof d !== 'object') return;
  if (d.type === 'GET_VERSION') {
    const reply: SwVersion = { version: MANIFEST.v, files: MANIFEST.files };
    e.ports[0]?.postMessage(reply);
  } else if (d.type === 'CACHES_CLEARED') {
    for (const b of BUCKETS) b.reset();
    pinning.clear();
  } else if (d.type === 'PIN' && Array.isArray(d.prefixes)) {
    const until = Date.now() + 10 * 60_000;
    for (const p of d.prefixes) if (typeof p === 'string' && p.startsWith(SCOPE)) pinning.set(p, until);
  }
});

// ---------------------------------------------------------------- strategies

async function cachedShell(): Promise<Response | undefined> {
  return (await caches.open(SHELL)).match(SHELL_URL);
}

/** Network first; the precached shell when the network fails or answers with something that is not the app. */
async function navigation(req: Request): Promise<Response> {
  try {
    const res = await timeout(fetch(req), NAV_TIMEOUT);
    if (res.ok && isHtml(res)) return res;
    return (await cachedShell()) || res;
  } catch (e) {
    const shell = await cachedShell();
    if (shell) return shell;
    throw e;
  }
}

/** A file of this build: from the precache, else from the network. */
async function shellFile(req: Request, key: string): Promise<Response> {
  return (await (await caches.open(SHELL)).match(key)) || fetch(req);
}

/** Cache first for static files outside the precache (fonts, hashed files of a newer build). */
async function staticAsset(e: FetchEventLike, key: string, freshFor: number): Promise<Response> {
  const hit = await assets.match(key);
  if (hit) {
    e.waitUntil(assets.settle());
    if (age(hit) > freshFor) e.waitUntil(refresh(assets, key, e.request.clone()));
    return hit;
  }
  const res = await fetch(e.request);
  if (storable(res)) {
    const copy = res.clone();
    e.waitUntil(
      stamped(copy)
        .then((r) => assets.put(key, r))
        .then(() => assets.settle())
        .catch(() => {}),
    );
  }
  return res;
}

/** Re-fetches an entry and replaces it when the server answers with a complete response. */
async function refresh(bucket: Bucket, key: string, req: Request): Promise<void> {
  try {
    const res = await fetch(req);
    if (!storable(res)) return;
    await bucket.put(key, await stamped(res));
    await bucket.settle();
  } catch {
    /* offline: keep the stored copy */
  }
}

async function cover(e: FetchEventLike): Promise<Response> {
  const req = e.request;
  const ck = identUrl(req.url, await identity(req));
  const hit = await covers.match(ck);
  if (hit) {
    e.waitUntil(covers.settle());
    if (age(hit) > COVER_FRESH) e.waitUntil(refresh(covers, ck, req.clone()));
    return hit;
  }
  const res = await fetch(req);
  if (storable(res)) {
    const copy = res.clone();
    e.waitUntil(
      stamped(copy)
        .then((r) => covers.put(ck, r))
        .then(() => covers.settle())
        .catch(() => {}),
    );
  }
  return res;
}

/** The same request without its Range header (the whole body is fetched and cached once). */
function withoutRange(req: Request): Request {
  if (!req.headers.has('range')) return req;
  const headers = new Headers();
  if (req.mode !== 'no-cors') {
    req.headers.forEach((v, k) => {
      if (k.toLowerCase() !== 'range') headers.set(k, v);
    });
  }
  return new Request(req.url, { headers, mode: req.mode === 'navigate' ? 'cors' : req.mode, credentials: req.credentials, referrerPolicy: 'no-referrer' });
}

/** Answers a Range request from a stored complete body. */
async function ranged(req: Request, full: Response): Promise<Response> {
  const header = req.headers.get('range');
  if (!header) return full;
  const buf = await full.arrayBuffer();
  const r = parseRange(header, buf.byteLength);
  const type = full.headers.get('content-type') || 'audio/mpeg';
  if (!r) return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${buf.byteLength}` } });
  return new Response(buf.slice(r.start, r.end + 1), {
    status: 206,
    headers: { 'Content-Type': type, 'Content-Range': `bytes ${r.start}-${r.end}/${buf.byteLength}`, 'Content-Length': String(r.end - r.start + 1), 'Accept-Ranges': 'bytes' },
  });
}

async function speech(e: FetchEventLike): Promise<Response> {
  const req = e.request;
  const ck = identUrl(req.url, await identity(req));
  const hit = await tts.match(ck);
  if (hit) {
    e.waitUntil(tts.settle());
    return ranged(req, hit);
  }
  const res = await fetch(withoutRange(req));
  if (!storable(res)) return res;
  const copy = await stamped(res.clone());
  e.waitUntil(
    tts
      .put(ck, copy.clone())
      .then(() => tts.settle())
      .catch(() => {}),
  );
  return req.headers.has('range') ? ranged(req, copy) : res;
}

/** Stale-while-revalidate for a chapter: pinned downloads first, then the recent-reads bucket, then the network. */
async function chapter(e: FetchEventLike, key: string): Promise<Response> {
  const req = e.request;
  const pinnedCache = await caches.open(CACHE.pinned);
  const pinned = await pinnedCache.match(key);
  const hit = pinned || (await chapters.match(key));
  if (hit) {
    if (!pinned) e.waitUntil(chapters.settle());
    if (age(hit) > CHAPTER_FRESH) {
      const again = req.clone();
      e.waitUntil(
        (async () => {
          try {
            const res = await fetch(again);
            if (!storable(res)) return;
            const copy = await stamped(res);
            // a pinned chapter stays pinned; it may have been removed by the user meanwhile
            if (pinned) {
              if (await pinnedCache.match(key)) await pinnedCache.put(key, copy);
            } else {
              await chapters.put(key, copy);
              await chapters.settle();
            }
          } catch {
            /* offline */
          }
        })(),
      );
    }
    return hit;
  }
  const res = await fetch(req);
  if (storable(res)) {
    const copy = res.clone();
    e.waitUntil(
      (async () => {
        try {
          const st = await stamped(copy);
          if (isPinning(key)) await pinnedCache.put(key, st);
          else {
            await chapters.put(key, st);
            await chapters.settle();
          }
        } catch {
          /* quota: reading still works */
        }
      })(),
    );
  }
  return res;
}

/** Network first for JSON the views need to start; the last good answer when the network is gone. */
async function apiData(e: FetchEventLike, wait = 0): Promise<Response> {
  const req = e.request;
  const ck = identUrl(req.url, await identity(req));
  try {
    const res = await (wait ? timeout(fetch(req), wait) : fetch(req));
    if (storable(res)) {
      const copy = res.clone();
      e.waitUntil(
        stamped(copy)
          .then((r) => api.put(ck, r))
          .then(() => api.settle())
          .catch(() => {}),
      );
    }
    return res;
  } catch (err) {
    const hit = await api.match(ck);
    if (hit) return hit;
    throw err;
  }
}

// ---------------------------------------------------------------- routing

sw.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  let url: URL;
  try {
    url = new URL(req.url);
  } catch {
    return;
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;
  // GitHub-direct keeps its own cache in IndexedDB and sends a token: never touched here
  if (url.hostname === 'api.github.com') return;

  const route = apiRoute(url.pathname);
  if (route) {
    if (route === 'tts') return e.respondWith(speech(e));
    if (route === 'cover') return e.respondWith(cover(e));
    if (route === 'chapter') {
      const id = chapterParams(url);
      if (id) return e.respondWith(chapter(e, chapterKey(SCOPE, id.source, id.key, id.file)));
      return;
    }
    if (route === 'data') return e.respondWith(apiData(e));
    // the app is served by this origin: when it does not answer, the last ping keeps the server selected
    if (route === 'ping' && url.origin === sw.location.origin) return e.respondWith(apiData(e, PING_TIMEOUT));
    return;
  }

  if (url.origin !== sw.location.origin) return;
  const key = url.origin + url.pathname;
  if (!key.startsWith(SCOPE)) return;
  if (req.mode === 'navigate') {
    if (key === SCOPE || key === SHELL_URL) e.respondWith(navigation(req));
    return;
  }
  if (PRECACHED.has(key)) return e.respondWith(shellFile(req, key));
  const rel = key.slice(SCOPE.length);
  if (rel.startsWith('_astro/')) return e.respondWith(staticAsset(e, key, Infinity));
  if (/^fonts\/.+\.(woff2?|ttf|otf)$/i.test(rel)) return e.respondWith(staticAsset(e, key, FONT_FRESH));
});
