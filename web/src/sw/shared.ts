/**
 * Names and URL helpers shared by the service worker (src/sw/sw.ts) and the page (offline module, PWA glue).
 * No DOM and no worker globals here: both sides import this file.
 */

/** Cache Storage buckets. `tts` and `covers` keep the names of the old app so existing entries survive. */
export const CACHE = {
  /** `mythlab-shell-<build>`: the precached app shell of one build. */
  shellPrefix: 'mythlab-shell-',
  /** Audio of /api/tts (LRU). */
  tts: 'mythlab-tts-v2',
  /** Images of /api/cover (LRU, revalidated when old). */
  covers: 'mythlab-covers-v2',
  /** Chapters read recently (LRU, stale-while-revalidate). */
  chapters: 'mythlab-chapters',
  /** Chapters the user downloaded on purpose ("Tải về để đọc offline"): never evicted. */
  pinned: 'mythlab-offline',
  /** Last good answers of /api/sources, /api/stories, /api/story, /api/voices and the same-origin ping (LRU). */
  api: 'mythlab-api-v2',
  /** Font files and hashed assets that are not part of the precache (LRU). */
  assets: 'mythlab-assets',
  /** Bookkeeping of the LRU buckets. */
  meta: 'mythlab-meta',
  /** Runtime cache of the old service worker (v3): never versioned, deleted on activation. */
  legacyStatic: 'mythlab-static',
  /** Buckets of worker versions whose keys carried no server/key identity: deleted on activation. */
  legacyIdentity: ['mythlab-tts', 'mythlab-covers', 'mythlab-api'],
} as const;

/** Entries kept per LRU bucket (api: lists, searches and details share it, so it is generous). */
export const LIMIT = { tts: 200, covers: 300, chapters: 300, api: 300, assets: 160 } as const;

/** Epoch ms when the service worker (or the page) stored the entry. */
export const HDR_AT = 'X-ML-At';
/** Body size in bytes, so sizes can be shown without reading bodies. */
export const HDR_SIZE = 'X-ML-Size';

const enc = encodeURIComponent;

/** Scope URL of the app (ends with "/") for a document or worker location. */
export const scopeOf = (href: string): string => new URL('./', href).href;

/** Prefix of every stored chapter of one story. */
export const storyPrefix = (scope: string, source: string, key: string): string => `${scope}__offline/chapter/${enc(source)}/${enc(key)}/`;

/** Request header that carries the LAN access key (see core/backend/server.ts). */
export const KEY_HEADER = 'X-MythLab-Key';

/**
 * Short identity of a server + access key, for cache keys. Only a SHA-256 prefix is kept, never the raw key, so a
 * rotated key or another server never reads (or is served) the answers stored for the previous one.
 */
export async function fingerprint(origin: string, key: string): Promise<string> {
  const data = new TextEncoder().encode(`${origin}\0${key}`);
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', data));
  return Array.from(digest.slice(0, 8), (b) => b.toString(16).padStart(2, '0')).join('');
}

/** Cache key of a private API answer: the request URL plus the identity it was fetched with. */
export const identUrl = (url: string, id: string): string => url + (url.includes('?') ? '&' : '?') + '__ml=' + id;

/** Cache key of one chapter: independent of the server address, so a chapter is stored once. */
export const chapterKey = (scope: string, source: string, key: string, file: string): string => storyPrefix(scope, source, key) + enc(file);

/** Cache key of the small JSON record describing a downloaded story. */
export const storyMetaKey = (scope: string, source: string, key: string): string => `${scope}__offline/story/${enc(source)}/${enc(key)}`;

export interface ChapterId {
  source: string;
  key: string;
  file: string;
}

function dec(s: string): string | null {
  try {
    return decodeURIComponent(s);
  } catch {
    return null;
  }
}

/** The chapter a cache key points at, or null for other keys. */
export function parseChapterKey(scope: string, url: string): ChapterId | null {
  const head = `${scope}__offline/chapter/`;
  if (!url.startsWith(head)) return null;
  const parts = url.slice(head.length).split('/');
  if (parts.length !== 3) return null;
  const [source, key, file] = parts.map(dec);
  if (source == null || key == null || file == null || !file) return null;
  return { source, key, file };
}

/** The story a meta key points at, or null. */
export function parseStoryMetaKey(scope: string, url: string): { source: string; key: string } | null {
  const head = `${scope}__offline/story/`;
  if (!url.startsWith(head)) return null;
  const parts = url.slice(head.length).split('/');
  if (parts.length !== 2) return null;
  const [source, key] = parts.map(dec);
  if (source == null || key == null) return null;
  return { source, key };
}

/** The chapter an `/api/chapter?source=&key=&file=` request asks for, or null when a parameter is missing. */
export function chapterParams(url: URL): ChapterId | null {
  const source = url.searchParams.get('source');
  const key = url.searchParams.get('key');
  const file = url.searchParams.get('file');
  return source && key && file ? { source, key, file } : null;
}

/** Which API route a URL is, by the end of its path (the server may live under any origin or prefix). */
export type ApiRoute = 'tts' | 'cover' | 'chapter' | 'ping' | 'data' | 'other' | null;
export function apiRoute(pathname: string): ApiRoute {
  const i = pathname.lastIndexOf('/api/');
  if (i < 0) return null;
  const rest = pathname.slice(i + 5);
  if (rest === 'tts' || rest === 'cover' || rest === 'chapter' || rest === 'ping') return rest;
  if (rest === 'sources' || rest === 'stories' || rest === 'story' || rest === 'voices') return 'data';
  return 'other';
}

/** Parses a `Range: bytes=a-b` header against a body of `size` bytes; null = not satisfiable / not a byte range. */
export function parseRange(header: string | null, size: number): { start: number; end: number } | null {
  const m = /^bytes=(\d*)-(\d*)$/.exec((header || '').trim());
  if (!m || (m[1] === '' && m[2] === '')) return null;
  let start: number;
  let end: number;
  if (m[1] === '') {
    const n = Number(m[2]);
    if (!n) return null;
    start = Math.max(0, size - n);
    end = size - 1;
  } else {
    start = Number(m[1]);
    end = m[2] === '' ? size - 1 : Math.min(size - 1, Number(m[2]));
  }
  if (!Number.isFinite(start) || !Number.isFinite(end) || start > end || start >= size) return null;
  return { start, end };
}

// ---------------------------------------------------------------- messages page <-> worker

export type SwRequest =
  /** Activate a waiting worker now (the user tapped "Tải lại", or the page already runs that build). */
  | { type: 'SKIP_WAITING' }
  /** Answered on the message port with SwVersion. */
  | { type: 'GET_VERSION' }
  /** The page deleted caches: forget the in-memory LRU bookkeeping. */
  | { type: 'CACHES_CLEARED' }
  /** Chapters under these key prefixes are being downloaded: store them in the pinned bucket. */
  | { type: 'PIN'; prefixes: string[] };

export interface SwVersion {
  version: string;
  /** Precached files, relative to the scope. */
  files: string[];
}

/** Broadcast to every window after a new worker took control. */
export interface SwActivated {
  type: 'ACTIVATED';
  version: string;
  files: string[];
}
