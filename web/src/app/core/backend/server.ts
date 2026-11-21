/** Server backend: the `/api/*` routes of the MythLab server, same origin (base "") or remote (URL + LAN key). */
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
function withTimeout(timeout: number, signal?: AbortSignal): { signal: AbortSignal | undefined; done: () => void } {
  if (!timeout && !signal) return { signal: undefined, done: () => {} };
  const ctl = new AbortController();
  const onAbort = (): void => ctl.abort();
  if (signal) {
    if (signal.aborted) ctl.abort();
    else signal.addEventListener('abort', onAbort, { once: true });
  }
  const t = timeout ? setTimeout(() => ctl.abort(), timeout) : undefined;
  return {
    signal: ctl.signal,
    done: () => {
      if (t !== undefined) clearTimeout(t);
      signal?.removeEventListener('abort', onAbort);
    },
  };
}

/**
 * The key travels only in the `X-MythLab-Key` header, never in a URL (URLs end up in caches, history and logs).
 * With a key, images and audio therefore cannot be loaded by `<img>`/`<audio>` directly: `mediaNeedsFetch` is true
 * and callers go through `fetchMedia` + object URLs (the backend facade does this for covers and TTS).
 */
export function createServerBackend(baseIn = '', key = ''): ServerBackend {
  const base = String(baseIn || '').replace(/\/+$/, '');
  const headers: Record<string, string> = key ? { 'X-MythLab-Key': key } : {};

  async function get<T = unknown>(path: string, { timeout = 0, signal }: GetOptions = {}): Promise<T> {
    const t = withTimeout(timeout, signal);
    try {
      const r = await fetch(base + '/api' + norm(path), { headers, signal: t.signal });
      const j = (await r.json().catch(() => ({ error: `HTTP ${r.status}` }))) as { error?: unknown; code?: unknown };
      if (!r.ok || j.error) {
        // `error` is a string today; tolerate the structured {code, message} form as well
        const e = j.error as string | { message?: string; code?: string } | undefined;
        const msg = typeof e === 'string' ? e : e?.message || `HTTP ${r.status}`;
        const code = typeof j.code === 'string' ? j.code : typeof e === 'object' && e ? e.code : undefined;
        throw new ApiError(msg, r.status, { code, json: j });
      }
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
