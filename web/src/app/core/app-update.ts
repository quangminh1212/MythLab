/**
 * Android app only: finds a newer APK on the server, downloads it and hands it to the system installer.
 *
 * The APK is not on Google Play, so the server publishes `/android/latest.json` next to the APK:
 *   { versionCode, versionName, url, sha256, size?, notes? }
 * The native `AppUpdate` plugin (apps/android …/AppUpdatePlugin.java) does the network and install work (static files
 * carry no CORS headers, so the page cannot fetch them itself). Android only installs an APK signed with the
 * same key as the installed app, and the plugin checks the SHA-256 from the manifest before offering it.
 *
 * The plugin is read from `Capacitor.Plugins` like the other native plugins; in a browser nothing here does anything.
 */
import { NATIVE_SERVER_URL } from './backend/index';
import { isNative } from './settings';

export interface UpdateManifest {
  versionCode: number;
  versionName: string;
  url: string;
  sha256: string;
  size: number;
  notes: string;
}

export interface Installed {
  versionCode: number;
  versionName: string;
  canInstall: boolean;
}

export type UpdateState =
  | { kind: 'idle' }
  | { kind: 'checking' }
  | { kind: 'uptodate'; current: Installed }
  | { kind: 'available'; current: Installed; latest: UpdateManifest }
  | { kind: 'downloading'; latest: UpdateManifest; loaded: number; total: number }
  /** downloaded; `needPermission` when Android still has to be told to allow installs from MythLab */
  | { kind: 'ready'; latest: UpdateManifest; needPermission: boolean }
  | { kind: 'error'; message: string; current?: Installed };

interface Handle {
  remove(): void | Promise<void>;
}
interface AppUpdatePlugin {
  getInfo(): Promise<Installed>;
  fetchManifest(o: { url: string }): Promise<{ text?: string }>;
  download(o: { url: string; sha256: string }): Promise<{ size?: number }>;
  install(): Promise<unknown>;
  addListener(ev: 'progress', fn: (e: { loaded?: number; total?: number }) => void): Promise<Handle> | Handle;
}

export const MANIFEST_PATH = '/android/latest.json';
const SEEN_KEY = 'mythlab.updateSeen';

function plugin(): AppUpdatePlugin | null {
  try {
    if (!isNative()) return null;
    const p = (globalThis as { Capacitor?: { Plugins?: Record<string, unknown> } }).Capacitor?.Plugins?.AppUpdate as AppUpdatePlugin | undefined;
    return p && typeof p.getInfo === 'function' && typeof p.download === 'function' ? p : null;
  } catch {
    return null;
  }
}

/**
 * Validates the manifest. The APK must come from the same https host as the manifest, with a SHA-256 and a
 * positive integer version; anything else is ignored, so a broken or tampered file never reaches the installer.
 */
export function parseManifest(raw: unknown, base: string): UpdateManifest | null {
  if (!raw || typeof raw !== 'object') return null;
  const m = raw as Record<string, unknown>;
  const code = m.versionCode;
  if (typeof code !== 'number' || !Number.isInteger(code) || code <= 0) return null;
  if (typeof m.sha256 !== 'string' || !/^[0-9a-f]{64}$/i.test(m.sha256)) return null;
  if (typeof m.url !== 'string' || !m.url) return null;
  let url: URL;
  let from: URL;
  try {
    from = new URL(base);
    url = new URL(m.url, from);
  } catch {
    return null;
  }
  if (url.protocol !== 'https:' || url.host !== from.host) return null;
  const size = typeof m.size === 'number' && Number.isFinite(m.size) && m.size > 0 ? Math.floor(m.size) : 0;
  return {
    versionCode: code,
    versionName: typeof m.versionName === 'string' ? m.versionName.slice(0, 32) : String(code),
    url: url.href,
    sha256: m.sha256.toLowerCase(),
    size,
    notes: typeof m.notes === 'string' ? m.notes.slice(0, 600) : '',
  };
}

export const isNewer = (latest: { versionCode: number }, current: { versionCode: number }): boolean => latest.versionCode > current.versionCode;

let state: UpdateState = { kind: 'idle' };
const listeners = new Set<(s: UpdateState) => void>();
const set = (s: UpdateState): void => {
  state = s;
  for (const fn of [...listeners]) {
    try {
      fn(s);
    } catch {
      /* a broken listener must not stop the others */
    }
  }
};

const msg = (e: unknown): string => {
  const x = e instanceof Error ? e.message : typeof e === 'object' && e && 'message' in e ? String((e as { message: unknown }).message) : String(e ?? '');
  if (/checksum/i.test(x)) return 'Tệp tải về không khớp mã kiểm tra. Hãy thử lại sau.';
  if (/HTTP 404/.test(x)) return 'Máy chủ chưa có bản cập nhật.';
  if (/busy/i.test(x)) return 'Đang tải rồi.';
  if (/already up to date/i.test(x)) return 'Ứng dụng đã là bản mới nhất.';
  return 'Không cập nhật được. Kiểm tra kết nối mạng rồi thử lại.';
};

let seq = 0;

export const appUpdate = {
  /** True inside the Android app, where the native plugin exists. */
  available: (): boolean => plugin() !== null,
  get: (): UpdateState => state,
  on(fn: (s: UpdateState) => void): () => void {
    listeners.add(fn);
    return () => listeners.delete(fn);
  },

  /** Asks the server for the newest version. Never throws; the result is in `get()`. */
  async check(): Promise<UpdateState> {
    const p = plugin();
    if (!p) return state;
    if (state.kind === 'checking' || state.kind === 'downloading') return state;
    const my = ++seq;
    set({ kind: 'checking' });
    let current: Installed | undefined;
    try {
      current = await p.getInfo();
      const r = await p.fetchManifest({ url: NATIVE_SERVER_URL + MANIFEST_PATH });
      if (my !== seq) return state;
      let json: unknown = null;
      try {
        json = JSON.parse(r?.text ?? '');
      } catch {
        /* handled below */
      }
      const latest = parseManifest(json, NATIVE_SERVER_URL + MANIFEST_PATH);
      if (!latest) {
        set({ kind: 'uptodate', current }); // no (valid) manifest published: nothing to offer
      } else if (isNewer(latest, current)) {
        lastLatest = latest;
        set({ kind: 'available', current, latest });
      } else {
        set({ kind: 'uptodate', current });
      }
    } catch (e) {
      if (my !== seq) return state;
      // "HTTP 404" = nothing published yet; treat as up to date instead of an error
      if (current && /HTTP 404/.test(msg(e) + String((e as { message?: unknown })?.message ?? ''))) set({ kind: 'uptodate', current });
      else set({ kind: 'error', message: msg(e), current });
    }
    return state;
  },

  /** Downloads the offered APK, then opens the system installer. */
  async start(): Promise<void> {
    const p = plugin();
    const s = state;
    if (!p || (s.kind !== 'available' && s.kind !== 'ready' && s.kind !== 'error')) return;
    const latest = s.kind === 'error' ? lastLatest : s.latest;
    if (!latest) return;
    lastLatest = latest;
    if (s.kind !== 'ready') {
      set({ kind: 'downloading', latest, loaded: 0, total: latest.size });
      let handle: Handle | null = null;
      try {
        const h = await p.addListener('progress', (e) => {
          if (state.kind !== 'downloading') return;
          const total = typeof e.total === 'number' && e.total > 0 ? e.total : latest.size;
          set({ kind: 'downloading', latest, loaded: Math.max(0, e.loaded ?? 0), total });
        });
        handle = h ?? null;
      } catch {
        /* progress is optional */
      }
      try {
        await p.download({ url: latest.url, sha256: latest.sha256 });
      } catch (e) {
        set({ kind: 'error', message: msg(e) });
        return;
      } finally {
        void Promise.resolve(handle?.remove()).catch(() => {});
      }
    }
    await appUpdate.install(latest);
  },

  /** Opens the installer for the downloaded file (also the retry after allowing installs from this app). */
  async install(latest?: UpdateManifest): Promise<void> {
    const p = plugin();
    const l = latest ?? (state.kind === 'ready' ? state.latest : lastLatest);
    if (!p || !l) return;
    try {
      await p.install();
      set({ kind: 'ready', latest: l, needPermission: false });
    } catch (e) {
      if (/permission/i.test(String((e as { message?: unknown })?.message ?? e))) set({ kind: 'ready', latest: l, needPermission: true });
      else set({ kind: 'error', message: msg(e) });
    }
  },

  /** True once for each offered version, so the launch toast does not nag on every start. */
  firstSight(versionCode: number): boolean {
    try {
      if (localStorage.getItem(SEEN_KEY) === String(versionCode)) return false;
      localStorage.setItem(SEEN_KEY, String(versionCode));
    } catch {
      /* private mode: show it every time */
    }
    return true;
  },

  /** Test hook. */
  _reset(): void {
    seq++;
    state = { kind: 'idle' };
    lastLatest = null;
    listeners.clear();
  },
};

let lastLatest: UpdateManifest | null = null;

/** "12,3 MB" for the progress line. */
export function fmtMB(bytes: number): string {
  return `${(bytes / 1048576).toFixed(1).replace('.', ',')} MB`;
}
