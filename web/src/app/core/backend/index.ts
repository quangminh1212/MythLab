/**
 * Backend facade: picks the data source at boot and exposes one API for both.
 *   1. the server on the same origin (browser at :8765, desktop app) — skipped inside Capacitor;
 *   2. a remote server from `mythlab.server` {url, key} — the native app is pinned to https://myth.xlabrnd.com;
 *   3. GitHub-direct with the token in `mythlab.ghToken` (encrypted at rest, see core/secret.ts) (+ `mythlab.ghSource` {owner?, prefix?, sid?});
 *   4. none → the onboarding view.
 * The LAN key and the token never appear in a URL: keyed media is fetched with the header and handed out as
 * object URLs (`cover()`, `ttsSrc()`).
 */
import { emit } from '../events';
import { isNative } from '../settings';
import { clearToken, initSecret, peekToken, setToken, TOKEN_KEY } from '../secret';
import { store } from '../store';
import { createGitHubBackend, type GitHubBackend, type GitHubOptions } from './github';
import { createServerBackend, type ServerBackend } from './server';
import { ApiError, type BackendKind, type CoverRef, type GetOptions, type SendOptions, type TokenTest, type TtsOptions } from './types';

export * from './types';
export { createServerBackend } from './server';
export { createGitHubBackend } from './github';

export const SERVER_KEY = 'mythlab.server';
/** Native builds always read from this host. A saved key is kept only when the stored URL is already this host. */
export const NATIVE_SERVER_URL = 'https://myth.xlabrnd.com';

export function pinnedNativeServer(current: ServerConfig | null, native: boolean): ServerConfig | null {
  if (!native) return current;
  if (current) {
    try {
      if (new URL(current.url).hostname.toLowerCase() === 'myth.xlabrnd.com') return current;
    } catch {
      /* replace an unparseable stored address */
    }
  }
  return { url: NATIVE_SERVER_URL, key: '' };
}
export { TOKEN_KEY };
export const GH_SOURCE_KEY = 'mythlab.ghSource';

export interface ServerConfig {
  url: string;
  key?: string;
}

let impl: ServerBackend | GitHubBackend | null = null;
let ready: Promise<BackendKind> | null = null;

const NONE = (): ApiError => new ApiError('Chưa cấu hình nguồn dữ liệu (máy chủ hoặc GitHub token)', 503, { code: 'no_backend' });

function readServer(): ServerConfig | null {
  const v = store.get<unknown>(SERVER_KEY, null) as { url?: unknown; key?: unknown } | null;
  if (!v || typeof v.url !== 'string' || !/^https?:\/\//i.test(v.url)) return null;
  return { url: v.url, key: typeof v.key === 'string' ? v.key : '' };
}
function readGhSource(): GitHubOptions {
  const v = store.get<unknown>(GH_SOURCE_KEY, null) as Record<string, unknown> | null;
  const o: GitHubOptions = {};
  if (v && typeof v === 'object') {
    if (typeof v.owner === 'string') o.owner = v.owner;
    if (typeof v.prefix === 'string' && v.prefix) o.prefix = v.prefix;
    if (typeof v.sid === 'string' && v.sid) o.sid = v.sid;
  }
  return o;
}

async function select(): Promise<BackendKind> {
  impl = null;
  await initSecret(); // the token is decrypted into memory before it is read below
  if (isNative()) {
    const cur = readServer();
    const next = pinnedNativeServer(cur, true);
    if (next && (cur?.url !== next.url || (cur?.key || '') !== (next.key || ''))) store.set(SERVER_KEY, next);
  }
  if (!isNative() && /^https?:$/.test(location.protocol)) {
    const same = createServerBackend('', '');
    const p = await same.ping(5000);
    if (p && p.app === 'mythlab') {
      impl = same;
      return 'server';
    }
  }
  const cfg = readServer();
  if (cfg) {
    const remote = createServerBackend(cfg.url, cfg.key || '');
    const p = await remote.ping(6000);
    if (p && p.app === 'mythlab') {
      impl = remote;
      return 'server';
    }
  }
  const token = peekToken();
  if (token) {
    impl = createGitHubBackend(token, readGhSource());
    return 'github';
  }
  // a configured but unreachable server is still the user's choice: keep it so errors say "không kết nối được"
  if (cfg) {
    impl = createServerBackend(cfg.url, cfg.key || '');
    return 'server';
  }
  return 'none';
}

const objectUrls: string[] = [];
function track(url: string): string {
  objectUrls.push(url);
  while (objectUrls.length > 80) URL.revokeObjectURL(objectUrls.shift() as string);
  return url;
}

export const backend = {
  /** 'none' until `init()` resolved. */
  get kind(): BackendKind {
    return impl ? impl.kind : 'none';
  },
  /** API level of the active backend (2 = Go server with search/paging/cover variants; otherwise 1). */
  get api(): number {
    return impl ? impl.api : 0;
  },
  /** Base URL of the server backend ('' = same origin); null for other kinds. */
  get serverBase(): string | null {
    return impl && impl.kind === 'server' ? impl.base : null;
  },
  /** The stored remote-server configuration, if any. */
  serverConfig: readServer,
  /** Chooses the backend (idempotent; `reinit()` to choose again after the configuration changed). */
  init(): Promise<BackendKind> {
    if (!ready) ready = select();
    return ready;
  },
  async reinit(): Promise<BackendKind> {
    ready = select();
    const kind = await ready;
    emit('backend', { kind });
    return kind;
  },
  /** GET an API route ("/stories?source=…"); rejects with ApiError. */
  async get<T = unknown>(path: string, opts?: GetOptions): Promise<T> {
    await backend.init();
    if (!impl) throw NONE();
    try {
      return await impl.get<T>(path, opts);
    } catch (e) {
      if (e instanceof ApiError) throw e;
      const x = e as Error;
      if (x?.name === 'AbortError') throw e;
      throw new ApiError(navigator.onLine === false ? 'Không có kết nối mạng' : 'Không kết nối được tới máy chủ', 0, { code: 'network', cause: e });
    }
  },
  /** Optional server capabilities from the last ping ("progress"); empty for GitHub-direct and the Python server. */
  get features(): readonly string[] {
    return impl && impl.kind === 'server' ? impl.features : [];
  },
  /** Google sign-in offered by the active server (from its last ping), or null. */
  get auth(): { google: boolean; clientId: string } | null {
    return impl && impl.kind === 'server' ? impl.auth : null;
  },
  /** PUT/POST JSON to the server API. Only the server backend can write: GitHub-direct rejects with 501. */
  async send<T = unknown>(method: 'PUT' | 'POST', path: string, body: unknown, opts?: SendOptions): Promise<T> {
    await backend.init();
    if (!impl) throw NONE();
    if (impl.kind !== 'server') throw new ApiError('Nguồn dữ liệu này không hỗ trợ ghi', 501, { code: 'no_send' });
    try {
      return await impl.send<T>(method, path, body, opts);
    } catch (e) {
      if (e instanceof ApiError) throw e;
      if ((e as Error)?.name === 'AbortError') throw e;
      throw new ApiError(navigator.onLine === false ? 'Không có kết nối mạng' : 'Không kết nối được tới máy chủ', 0, { code: 'network', cause: e });
    }
  },
  /** Direct TTS URL without credentials; null when the backend has no TTS (GitHub-direct). Prefer `ttsSrc`. */
  ttsUrl(opts: TtsOptions): string | null {
    return impl ? impl.ttsUrl(opts) : null;
  },
  /**
   * Something an `<audio>` element can play: the plain URL when no key is needed, otherwise the audio fetched
   * with the key header as an object URL. The caller should `releaseUrl()` object URLs it no longer needs.
   */
  async ttsSrc(opts: TtsOptions, o: { signal?: AbortSignal } = {}): Promise<string> {
    await backend.init();
    const u = impl ? impl.ttsUrl(opts) : null;
    if (!impl || !u) throw new ApiError('Không có máy chủ đọc truyện (đang đọc trực tiếp từ GitHub)', 503, { code: 'no_tts' });
    if (!impl.mediaNeedsFetch) return u;
    return track(URL.createObjectURL(await impl.fetchMedia(u, o.signal)));
  },
  /** Revokes an object URL returned by `ttsSrc` (plain URLs are ignored). */
  releaseUrl(url: string): void {
    if (!url.startsWith('blob:')) return;
    const i = objectUrls.indexOf(url);
    if (i >= 0) objectUrls.splice(i, 1);
    URL.revokeObjectURL(url);
  },
  /**
   * Cover of a story: a URL string, a Promise of one (authenticated fetch), or null when there is none.
   * `w` is the CSS width the image is shown at; the Go server answers with a resized variant.
   */
  coverUrl(st: CoverRef, w?: number): string | Promise<string> | null {
    return impl ? impl.coverUrl(st, w) : null;
  },
  /** GitHub-direct only: checks a token without storing it. */
  testToken(token: string, opts?: GitHubOptions): Promise<TokenTest> {
    return createGitHubBackend(token, opts ?? readGhSource()).testToken();
  },
  /** Checks a server URL + key without storing them: 'ok', 'auth' (wrong key) or 'unreachable'. */
  async testServer(url: string, key = ''): Promise<'ok' | 'auth' | 'unreachable'> {
    const b = createServerBackend(url, key);
    const p = await b.ping(6000);
    if (p && p.app === 'mythlab') {
      // ping is public on some servers: confirm the key on a protected route
      try {
        await b.get('/sources', { timeout: 20000 });
        return 'ok';
      } catch (e) {
        return e instanceof ApiError && (e.status === 401 || e.status === 403) ? 'auth' : 'ok';
      }
    }
    try {
      const r = await fetch(url.replace(/\/+$/, '') + '/api/ping', { cache: 'no-store' });
      return r.status === 401 || r.status === 403 ? 'auth' : 'unreachable';
    } catch {
      return 'unreachable';
    }
  },
  /** Stores a remote server and switches to it. */
  async useServer(url: string, key = ''): Promise<BackendKind> {
    store.set(SERVER_KEY, { url: url.replace(/\/+$/, ''), key });
    return backend.reinit();
  },
  /** Stores a GitHub token (and optional owner/prefix) and switches to GitHub-direct when no server answers. */
  async useToken(token: string, opts?: GitHubOptions): Promise<BackendKind> {
    await setToken(token);
    if (opts && (opts.owner || opts.prefix)) store.set(GH_SOURCE_KEY, { ...readGhSource(), ...opts });
    return backend.reinit();
  },
  /** Forgets the stored server and token. */
  async forget(what: 'server' | 'token' | 'all' = 'all'): Promise<BackendKind> {
    if (what !== 'token') store.del(SERVER_KEY);
    if (what !== 'server') {
      await clearToken();
      store.del(GH_SOURCE_KEY);
    }
    return backend.reinit();
  },
};

export type Backend = typeof backend;
