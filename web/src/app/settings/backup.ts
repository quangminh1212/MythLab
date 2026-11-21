/**
 * Export / import of the reader's own data as one JSON file: settings, reading progress, bookmarks, followed
 * stories and the picked system fonts. The server key and the GitHub token are left out unless the user asks for
 * them, in both directions.
 */
import { GH_SOURCE_KEY, SERVER_KEY } from '../core/backend/index';
import { peekToken, setToken } from '../core/secret';
import type { Bookmark, Follow, Progress } from '../core/contracts';
import { sKey } from '../core/format';
import { BOOKMARKS_KEY, FOLLOWS_KEY, MAX_BOOKMARKS, MAX_FOLLOWS } from '../core/library';
import { MAX_ENTRIES, PROGRESS_KEY, progress } from '../core/progress';
import { defaults, normalise, type SettingKey } from '../core/settings';
import { store } from '../core/store';

export const BACKUP_FORMAT = 'mythlab-backup';
export const BACKUP_VERSION = 1;
const SETTINGS_KEY = 'mythlab.settings';
const LOCAL_FONTS_KEY = 'mythlab.localFonts';
/** Larger files are refused before parsing (a full backup is a few hundred kB). */
export const MAX_BACKUP_BYTES = 8 * 1024 * 1024;

export interface BackupSecrets {
  server?: { url: string; key: string };
  ghToken?: string;
  ghSource?: Record<string, string>;
}

export interface Backup {
  format: typeof BACKUP_FORMAT;
  version: number;
  /** ISO time of the export. */
  exported: string;
  settings: Record<string, unknown>;
  progress: Record<string, Progress>;
  bookmarks: Bookmark[];
  follows: Follow[];
  localFonts: string[];
  /** Present only when the user ticked "Kèm khoá máy chủ và GitHub token". */
  secrets?: BackupSecrets;
}

/** A problem with a backup file, with a message that can be shown to the user. */
export class BackupError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'BackupError';
  }
}

const isObj = (v: unknown): v is Record<string, unknown> => !!v && typeof v === 'object' && !Array.isArray(v);
const str = (v: unknown): v is string => typeof v === 'string';
const num = (v: unknown, d = 0): number => (typeof v === 'number' && Number.isFinite(v) ? v : d);
const strOrNull = (v: unknown): string | null => (str(v) ? v : null);

// ---------------------------------------------------------------- validation

/** Known settings validated one by one; migration markers and unknown primitive keys are kept as they are. */
export function cleanSettings(raw: unknown): Record<string, unknown> {
  const out: Record<string, unknown> = Object.create(null) as Record<string, unknown>;
  if (!isObj(raw)) return out;
  const def = defaults();
  for (const [k, v] of Object.entries(raw)) {
    if (Object.hasOwn(def, k)) out[k] = normalise(k as SettingKey, v);
    else if (/^[a-zA-Z][\w-]{0,40}$/.test(k) && (typeof v === 'number' || typeof v === 'boolean' || (str(v) && v.length <= 200))) out[k] = v;
  }
  return out;
}

function cleanProgress(v: unknown): Progress | null {
  if (!isObj(v) || !str(v.source) || !str(v.key) || !v.source || !v.key) return null;
  const p: Progress = {
    source: v.source,
    key: v.key,
    name: str(v.name) ? v.name : v.key,
    poster: strOrNull(v.poster),
    cover: strOrNull(v.cover),
    cover_sha: strOrNull(v.cover_sha),
    author: strOrNull(v.author),
    genres: Array.isArray(v.genres) ? v.genres.filter(str).slice(0, 3) : [],
    group: strOrNull(v.group),
    idx: Math.max(0, Math.floor(num(v.idx))),
    n: num(v.n),
    total: Math.max(0, Math.floor(num(v.total))),
    para: Math.max(0, Math.floor(num(v.para))),
    ts: num(v.ts),
  };
  if (str(v.file)) p.file = v.file;
  if (typeof v.frac === 'number' && Number.isFinite(v.frac)) p.frac = Math.min(1, Math.max(0, v.frac));
  if (typeof v.maxIdx === 'number' && Number.isFinite(v.maxIdx)) p.maxIdx = Math.max(0, Math.floor(v.maxIdx));
  if (str(v.title)) p.title = v.title;
  if (isObj(v.listen)) {
    p.listen = { idx: Math.max(0, Math.floor(num(v.listen.idx))), para: Math.max(0, Math.floor(num(v.listen.para))) };
    if (str(v.listen.file)) p.listen.file = v.listen.file;
  }
  return p;
}

function cleanBookmark(v: unknown): Bookmark | null {
  if (!isObj(v) || !str(v.id) || !str(v.source) || !str(v.key) || !v.id) return null;
  return {
    id: v.id,
    source: v.source,
    key: v.key,
    name: str(v.name) ? v.name : v.key,
    idx: Math.max(0, Math.floor(num(v.idx))),
    n: num(v.n),
    file: str(v.file) ? v.file : '',
    title: str(v.title) ? v.title : '',
    para: Math.max(0, Math.floor(num(v.para))),
    excerpt: str(v.excerpt) ? v.excerpt.slice(0, 400) : '',
    ts: num(v.ts),
  };
}

function cleanFollow(v: unknown): Follow | null {
  if (!isObj(v) || !str(v.source) || !str(v.key) || !v.source || !v.key) return null;
  return { source: v.source, key: v.key, name: str(v.name) ? v.name : v.key, author: strOrNull(v.author), poster: strOrNull(v.poster), cover: strOrNull(v.cover), cover_sha: strOrNull(v.cover_sha), group: strOrNull(v.group), ts: num(v.ts) };
}

function cleanSecrets(v: unknown): BackupSecrets | undefined {
  if (!isObj(v)) return undefined;
  const out: BackupSecrets = {};
  if (isObj(v.server) && str(v.server.url) && /^https?:\/\//i.test(v.server.url)) out.server = { url: v.server.url, key: str(v.server.key) ? v.server.key : '' };
  if (str(v.ghToken) && v.ghToken) out.ghToken = v.ghToken;
  if (isObj(v.ghSource)) {
    const g: Record<string, string> = {};
    for (const k of ['owner', 'prefix', 'sid']) if (str(v.ghSource[k])) g[k] = v.ghSource[k] as string;
    if (Object.keys(g).length) out.ghSource = g;
  }
  return Object.keys(out).length ? out : undefined;
}

function progressMap(raw: unknown): Record<string, Progress> {
  const out: Record<string, Progress> = Object.create(null) as Record<string, Progress>;
  if (!isObj(raw)) return out;
  for (const v of Object.values(raw)) {
    const p = cleanProgress(v);
    if (p) out[sKey(p.source, p.key)] = p;
  }
  return out;
}
const list = <T>(raw: unknown, clean: (v: unknown) => T | null): T[] => (Array.isArray(raw) ? raw.map(clean).filter((x): x is T => x !== null) : []);

// ---------------------------------------------------------------- export

/** Collects the stored data. Secrets are read only when asked for. */
export function buildBackup(o: { includeSecrets?: boolean; now?: number } = {}): Backup {
  progress.flush();
  const b: Backup = {
    format: BACKUP_FORMAT,
    version: BACKUP_VERSION,
    exported: new Date(o.now ?? Date.now()).toISOString(),
    settings: cleanSettings(store.get<unknown>(SETTINGS_KEY, {})),
    progress: progressMap(store.get<unknown>(PROGRESS_KEY, {})),
    bookmarks: list(store.get<unknown>(BOOKMARKS_KEY, []), cleanBookmark),
    follows: list(store.get<unknown>(FOLLOWS_KEY, []), cleanFollow),
    localFonts: list(store.get<unknown>(LOCAL_FONTS_KEY, []), (v) => (str(v) && v ? v : null)),
  };
  if (o.includeSecrets) {
    const s = cleanSecrets({ server: store.get<unknown>(SERVER_KEY, null), ghToken: peekToken(), ghSource: store.get<unknown>(GH_SOURCE_KEY, null) });
    if (s) b.secrets = s;
  }
  return b;
}

export const backupFileName = (now = Date.now()): string => `mythlab-sao-luu-${new Date(now).toISOString().slice(0, 10)}.json`;

// ---------------------------------------------------------------- import

/** Parses and validates the text of a backup file. Throws BackupError with a Vietnamese message. */
export function parseBackup(text: string): Backup {
  if (text.length > MAX_BACKUP_BYTES) throw new BackupError('Tệp quá lớn, không phải tệp sao lưu của MythLab.');
  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    throw new BackupError('Tệp không đọc được (không phải JSON hợp lệ).');
  }
  if (!isObj(raw) || raw.format !== BACKUP_FORMAT) throw new BackupError('Đây không phải tệp sao lưu của MythLab.');
  const version = num(raw.version);
  if (version < 1 || version > BACKUP_VERSION) throw new BackupError('Tệp sao lưu thuộc phiên bản mới hơn ứng dụng này. Hãy cập nhật MythLab rồi thử lại.');
  const b: Backup = {
    format: BACKUP_FORMAT,
    version,
    exported: str(raw.exported) ? raw.exported : '',
    settings: cleanSettings(raw.settings),
    progress: progressMap(raw.progress),
    bookmarks: list(raw.bookmarks, cleanBookmark),
    follows: list(raw.follows, cleanFollow),
    localFonts: list(raw.localFonts, (v) => (str(v) && v && v.length <= 120 ? v : null)),
  };
  const s = cleanSecrets(raw.secrets);
  if (s) b.secrets = s;
  return b;
}

export interface ImportResult {
  settings: number;
  progress: number;
  bookmarks: number;
  follows: number;
  /** True when a server address / key or a token was restored. */
  secrets: boolean;
}

export interface ImportOptions {
  /** 'merge' (default) keeps what is on this device and adds the file; 'replace' takes the file as it is. */
  mode?: 'merge' | 'replace';
  /** Restore the server key and the GitHub token found in the file (default false). */
  includeSecrets?: boolean;
}

/** Newest-first merge of two lists by identity; `a` wins a tie. */
function mergeBy<T extends { ts: number }>(a: T[], b: T[], id: (x: T) => string, max: number): T[] {
  const by = new Map<string, T>();
  for (const x of [...a, ...b]) {
    const k = id(x);
    const cur = by.get(k);
    if (!cur || x.ts > cur.ts) by.set(k, x);
  }
  return [...by.values()].sort((x, y) => y.ts - x.ts).slice(0, max);
}

/** Keeps the MAX_ENTRIES most recent progress entries (mutates and returns `prog`). */
function capProgress(prog: Record<string, Progress>): Record<string, Progress> {
  const keys = Object.keys(prog);
  if (keys.length > MAX_ENTRIES) {
    keys.sort((x, y) => (prog[y] as Progress).ts - (prog[x] as Progress).ts);
    for (const k of keys.slice(MAX_ENTRIES)) delete prog[k];
  }
  return prog;
}

/** What the stored data becomes after importing `b` (pure: nothing is written). */
export function mergeBackup(current: Backup, b: Backup, mode: 'merge' | 'replace' = 'merge'): Pick<Backup, 'settings' | 'progress' | 'bookmarks' | 'follows' | 'localFonts'> {
  if (mode === 'replace') return { settings: b.settings, progress: capProgress({ ...b.progress }), bookmarks: b.bookmarks.slice(0, MAX_BOOKMARKS), follows: b.follows.slice(0, MAX_FOLLOWS), localFonts: b.localFonts };
  // progress: per story, the more recent position wins
  const prog: Record<string, Progress> = { ...current.progress };
  for (const [k, p] of Object.entries(b.progress)) {
    const mine = prog[k];
    if (!mine || p.ts > mine.ts) prog[k] = p;
  }
  capProgress(prog);
  return {
    // settings of the file replace the same keys here; keys the file does not have stay
    settings: { ...current.settings, ...b.settings },
    progress: prog,
    bookmarks: mergeBy(current.bookmarks, b.bookmarks, (x) => x.id, MAX_BOOKMARKS),
    follows: mergeBy(current.follows, b.follows, (x) => sKey(x.source, x.key), MAX_FOLLOWS),
    localFonts: [...new Set([...current.localFonts, ...b.localFonts])],
  };
}

/** Tells the modules that keep a copy in memory (settings, progress, library) that a key was rewritten. */
function announce(key: string): void {
  try {
    window.dispatchEvent(new StorageEvent('storage', { key }));
  } catch {
    /* very old engines: the next reload picks the data up */
  }
}

/** The stored value of a key, or undefined when absent (so a rollback can delete what it created). */
const rawGet = (key: string): unknown => store.get<unknown>(key, undefined);
function rawRestore(key: string, v: unknown): void {
  if (v === undefined) store.del(key);
  else store.set(key, v);
}

/** Writes a parsed backup to storage and refreshes the running app. */
export function applyBackup(b: Backup, o: ImportOptions = {}): ImportResult {
  const next = mergeBackup(buildBackup(), b, o.mode || 'merge');
  const stored = isObj(store.get<unknown>(SETTINGS_KEY, {})) ? store.get<Record<string, unknown>>(SETTINGS_KEY, {}) : {};
  // migration markers of this device stay: imported values were already migrated by the device that wrote them
  const settingsOut = o.mode === 'replace' ? { ...next.settings, ui2: stored.ui2 ?? 1, ui3: stored.ui3 ?? 1 } : { ...stored, ...next.settings };
  const writes: [string, unknown][] = [
    [SETTINGS_KEY, settingsOut],
    [PROGRESS_KEY, next.progress],
    [BOOKMARKS_KEY, next.bookmarks],
    [FOLLOWS_KEY, next.follows],
    [LOCAL_FONTS_KEY, next.localFonts],
  ];
  // snapshot the raw previous values so a failed write can be rolled back (all or nothing)
  const before = writes.map(([k]) => [k, rawGet(k)] as const);
  if (!writes.every(([k, v]) => store.set(k, v))) {
    for (const [k, raw] of before) rawRestore(k, raw);
    for (const [k] of before) announce(k);
    throw new BackupError('Không ghi được dữ liệu (bộ nhớ trình duyệt đầy hoặc bị chặn). Dữ liệu cũ được giữ nguyên.');
  }
  let secrets = false;
  if (o.includeSecrets && b.secrets) {
    if (b.secrets.server) secrets = store.set(SERVER_KEY, b.secrets.server) || secrets;
    if (b.secrets.ghToken) {
      // encrypted and written in the background; the in-memory copy is updated at once
      void setToken(b.secrets.ghToken);
      secrets = true;
    }
    if (b.secrets.ghSource) store.set(GH_SOURCE_KEY, b.secrets.ghSource);
  }
  for (const k of [SETTINGS_KEY, PROGRESS_KEY, BOOKMARKS_KEY, FOLLOWS_KEY]) announce(k);
  return { settings: Object.keys(b.settings).filter((k) => Object.hasOwn(defaults(), k)).length, progress: Object.keys(b.progress).length, bookmarks: b.bookmarks.length, follows: b.follows.length, secrets };
}
