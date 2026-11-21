/** Server backend: the `/api/*` routes of the MythLab server, same origin (base "") or remote (URL + LAN key). */
import { isNative } from '../settings';
import { apiRoute, CACHE, chapterKey, chapterParams, fingerprint, identUrl, scopeOf } from '../../../sw/shared';
import { ApiError, type BackendImpl, type CoverRef, type GetOptions, type PingResponse, type TtsOptions } from './types';

const norm = (p: string): string => '/' + String(p || '').replace(/^\/+/, '').replace(/^api\//, '');

export const COVER_WIDTHS = [160, 240, 320, 480] as const;

export interface ServerBackend extends BackendImpl {
  readonly kind: 'server';
  readonly base: string;
  /** Resolves the ping body (null when the server is unreachable or refuses the key) and records `api`. */
  ping(timeout?: number): Promise<PingResponse | null>;
}

/** Combines a caller signal with a timeout; returns the signal and a disposer. */
function withTimeout(timeout: number, signal?: AbortSignal): { signal: AbortSignal | undefined; done: () => void; timedOut: () => boolean } {
  if (!timeout && !signal) return { signal: undefined, done: () => {}, timedOut: () => false };
  const ctl = new AbortController();
  const onAbort = (): void => ctl.abort();
  if (signal) {
    if (signal.aborted) ctl.abort();
    else signal.addEventListener('abort', onAbort, { once: true });
  }
  let fired = false;
  const t = timeout
    ? setTimeout(() => {
        fired = true;
        ctl.abort();
      }, timeout)
    : undefined;
  return {
    signal: ctl.signal,
    timedOut: () => fired && !signal?.aborted,
    done: () => {
      if (t !== undefined) clearTimeout(t);
      signal?.removeEventListener('abort', onAbort);
    },
  };
}

/** Native app: how long a data request may take before the saved copy (if any) is used instead. */
const NATIVE_FALLBACK_MS = 8_000;

/**
 * The key travels only in the `X-MythLab-Key` header, never in a URL (URLs end up in caches, history and logs).
 * With a key, images and audio therefore cannot be loaded by `<img>`/`<audio>` directly: `mediaNeedsFetch` is true
 * and callers go through `fetchMedia` + object URLs (the backend facade does this for covers and TTS).
 */
export function createServerBackend(baseIn = '', key = ''): ServerBackend {
  const base = String(baseIn || '').replace(/\/+$/, '');
  const headers: Record<string, string> = key ? { 'X-MythLab-Key': key } : {};

  // The native app has no service worker (its https://localhost origin cannot fetch a plain-http server from one),
  // so the page itself keeps the last good data answers and serves downloaded chapters when the network is gone.
  const ident = isNative() && typeof caches !== 'undefined' ? fingerprint(base, key).catch(() => '') : null;

  async function offlineGet<T>(url: string): Promise<T | undefined> {
    if (!ident) return undefined;
    try {
      const u = new URL(url, 'http://x');
      const route = apiRoute(u.pathname);
      if (route === 'chapter') {
        const c = chapterParams(u);
        if (!c) return undefined;
        const k = chapterKey(scopeOf(location.href), c.source, c.key, c.file);
        for (const name of [CACHE.pinned, CACHE.chapters]) {
          const hit = await (await caches.open(name)).match(k);
          if (hit) return (await hit.json()) as T;
        }
        return undefined;
      }
      if (route === 'data') {
        const hit = await (await caches.open(CACHE.api)).match(identUrl(scopeOf(location.href) + '__native' + u.pathname + u.search, await ident));
        if (hit) return (await hit.json()) as T;
      }
    } catch {
      /* unreadable entry: treat as missing */
    }
    return undefined;
  }

  /** The chapter the user downloaded on purpose (never the LRU bucket: that one may be stale), or undefined. */
  async function offlinePinned<T>(url: string): Promise<T | undefined> {
    try {
      const u = new URL(url, 'http://x');
      if (apiRoute(u.pathname) !== 'chapter') return undefined;
      const c = chapterParams(u);
      if (!c) return undefined;
      const hit = await (await caches.open(CACHE.pinned)).match(chapterKey(scopeOf(location.href), c.source, c.key, c.file));
      return hit ? ((await hit.json()) as T) : undefined;
    } catch {
      return undefined;
    }
  }

  async function remember(url: string, body: string): Promise<void> {
    if (!ident) return;
    try {
      const u = new URL(url, 'http://x');
      if (apiRoute(u.pathname) !== 'data') return;
      const k = identUrl(scopeOf(location.href) + '__native' + u.pathname + u.search, await ident);
      await (await caches.open(CACHE.api)).put(k, new Response(body, { headers: { 'Content-Type': 'application/json' } }));
    } catch {
      /* storage full or blocked: skip */
    }
  }

  async function get<T = unknown>(path: string, opts: GetOptions = {}): Promise<T> {
    const url = '/api' + norm(path);
    if (ident) {
      // A downloaded chapter never changes: read it from the device first, with no network round trip. (A host that
      // is switched off or asleep drops packets silently, so asking the network first would hang until the OS gives up.)
      const pinned = await offlinePinned<T>(url);
      if (pinned !== undefined) return pinned;
    }
    // Native with a saved copy: a dead server must not stall the page for the caller's long timeout (30-90 s) before
    // the copy is used. Without a copy the caller's own timeout stands, so a slow but working server still answers.
    const saved = ident ? await offlineGet<T>(url) : undefined;
    if (saved !== undefined) opts = { ...opts, timeout: Math.min(opts.timeout || NATIVE_FALLBACK_MS, NATIVE_FALLBACK_MS) };
    try {
      return await getLive<T>(path, opts);
    } catch (e) {
      if (e instanceof ApiError || opts.signal?.aborted) throw e;
      if (saved !== undefined) return saved;
      throw e;
    }
  }

  async function getLive<T = unknown>(path: string, { timeout = 0, signal }: GetOptions = {}): Promise<T> {
    const t = withTimeout(timeout, signal);
    try {
      let r: Response;
      try {
        r = await fetch(base + '/api' + norm(path), { headers, signal: t.signal });
      } catch (e) {
        // Our own timeout is a network failure (the caller shows an error), not a user abort, which views ignore silently.
        if (t.timedOut()) throw new Error('Máy chủ không phản hồi', { cause: e });
        throw e;
      }
      const j = (await r.json().catch(() => ({ error: `HTTP ${r.status}` }))) as { error?: unknown; code?: unknown };
      if (!r.ok || j.error) {
        // `error` is a string today; tolerate the structured {code, message} form as well
        const e = j.error as string | { message?: string; code?: string } | undefined;
        const msg = typeof e === 'string' ? e : e?.message || `HTTP ${r.status}`;
        const code = typeof j.code === 'string' ? j.code : typeof e === 'object' && e ? e.code : undefined;
        throw new ApiError(msg, r.status, { code, json: j });
      }
      void remember('/api' + norm(path), JSON.stringify(j));
      return j as T;
    } finally {
      t.done();
    }
  }

  function ttsUrl({ text, voice, rate, pitch }: TtsOptions): string {
    // parameter order (voice, text) is part of the HTTP/service-worker cache key: do not reorder
    let u = `${base}/api/tts?voice=${encodeURIComponent(voice || 'vi-VN-HoaiMyNeural')}&text=${encodeURIComponent(text || '')}`;
    const edgeInt = (v: unknown): v is number => typeof v === 'number' && Number.isInteger(v) && Math.abs(v) > 4;
    if (edgeInt(rate)) u += `&rate=${rate}`;
    if (edgeInt(pitch)) u += `&pitch=${pitch}`;
    return u;
  }

  async function ping(timeout = 5000): Promise<PingResponse | null> {
    const t = withTimeout(timeout);
    try {
      const r = await fetch(base + '/api/ping', { headers, signal: t.signal, cache: 'no-store' });
      if (r.status === 401 || r.status === 403 || !/json/i.test(r.headers.get('Content-Type') || '')) return null;
      const j = (await r.json()) as PingResponse | null;
      if (!j) return null;
      self.api = typeof j.api === 'number' && j.api >= 2 ? j.api : 1;
      return j;
    } catch {
      return null;
    } finally {
      t.done();
    }
  }

  async function fetchMedia(url: string, signal?: AbortSignal): Promise<Blob> {
    const r = await fetch(url, { headers, signal });
    if (!r.ok) throw new ApiError(`HTTP ${r.status}`, r.status);
    return r.blob();
  }

  const coverBlobs = new Map<string, Promise<string>>();
  function blobUrl(url: string): Promise<string> {
    let p = coverBlobs.get(url);
    if (!p) {
      p = fetchMedia(url).then((b) => URL.createObjectURL(b));
      coverBlobs.set(url, p);
      p.catch(() => coverBlobs.delete(url));
      if (coverBlobs.size > 400) {
        const first = coverBlobs.keys().next().value as string;
        const old = coverBlobs.get(first);
        coverBlobs.delete(first);
        old?.then((u) => URL.revokeObjectURL(u)).catch(() => {});
      }
    }
    return p;
  }

  function coverUrl(st: CoverRef, w?: number): string | Promise<string> | null {
    const c = st && st.cover;
    if (typeof c === 'string' && c.startsWith('/api/')) {
      let u = base + c;
      if (w && self.api >= 2 && !/[?&]w=/.test(u)) {
        const dpr = Math.min(2, globalThis.devicePixelRatio || 1);
        const want = w * dpr;
        const pick = COVER_WIDTHS.find((x) => x >= want) ?? 480;
        u += (u.includes('?') ? '&' : '?') + 'w=' + pick;
      }
      return key ? blobUrl(u) : u;
    }
    const u = (st && (c || st.poster)) || '';
    return /^https?:\/\//i.test(u) ? u : null;
  }

  const self: ServerBackend = { kind: 'server', base, api: 1, get, ttsUrl, coverUrl, ping, mediaNeedsFetch: !!key, fetchMedia };
  return self;
}
