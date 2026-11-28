/**
 * The reader's personal library: history (derived from progress), bookmarks (`mythlab.bookmarks`) and followed
 * stories (`mythlab.follows`). Lists are stored newest first; every write re-reads the stored list first so two
 * tabs do not overwrite each other.
 */
import type { Bookmark, Follow, Progress, StoryDetail } from './contracts';
import { emit } from './events';
import { sKey } from './format';
import { progress } from './progress';
import { store } from './store';

export const BOOKMARKS_KEY = 'mythlab.bookmarks';
export const FOLLOWS_KEY = 'mythlab.follows';
export const MAX_BOOKMARKS = 1000;
export const MAX_FOLLOWS = 500;
/** `mythlab.library.tomb` = { "<kind>|<id>": deletion ts }: removed follows/bookmarks that sync must propagate. */
export const LIB_TOMB_KEY = 'mythlab.library.tomb';
/** How long a deletion is remembered (the server keeps tombstones for the same time). */
export const LIB_TOMB_AGE = 60 * 24 * 3600 * 1000;

export type LibKind = 'follow' | 'bookmark';
type LocalChange = (kind: LibKind, id: string, deleted: boolean) => void;
const changeListeners = new Set<LocalChange>();
let tombs: Record<string, number> | null = null;

/** Writes a list; when storage refuses it, tells the user and returns false (callers then skip the success event). */
function persist(key: string, list: unknown): boolean {
  if (store.set(key, list)) return true;
  emit('toast', { message: 'Không lưu được: bộ nhớ trình duyệt đã đầy hoặc bị chặn.', kind: 'error' });
  return false;
}

function readTombs(): Record<string, number> {
  if (tombs) return tombs;
  const raw = store.get<unknown>(LIB_TOMB_KEY, {});
  const min = Date.now() - LIB_TOMB_AGE;
  const out: Record<string, number> = {};
  if (raw && typeof raw === 'object' && !Array.isArray(raw)) {
    for (const [k, v] of Object.entries(raw as Record<string, unknown>)) if (typeof v === 'number' && v > min) out[k] = v;
  }
  return (tombs = out);
}
function setTomb(kind: LibKind, id: string, ts: number | null): void {
  const t = readTombs();
  const k = `${kind}|${id}`;
  if (ts === null) {
    if (!(k in t)) return;
    delete t[k];
  } else t[k] = ts;
  store.set(LIB_TOMB_KEY, t);
}
function notify(kind: LibKind, id: string, deleted: boolean): void {
  for (const fn of [...changeListeners]) {
    try {
      fn(kind, id, deleted);
    } catch (e) {
      console.error(e);
    }
  }
}
/** Calls `fn` when this device adds, changes or removes a follow or bookmark; never for entries applied from a remote. */
export function onLocalChange(fn: LocalChange): () => void {
  changeListeners.add(fn);
  return () => void changeListeners.delete(fn);
}
/** Deletion time of a follow/bookmark removed on this device (still to be propagated), or undefined. */
export function tombstone(kind: LibKind, id: string): number | undefined {
  return readTombs()[`${kind}|${id}`];
}

/** Ids of the deletions still remembered for a kind. */
export function tombstoneIds(kind: LibKind): string[] {
  const p = kind + '|';
  return Object.keys(readTombs())
    .filter((k) => k.startsWith(p))
    .map((k) => k.slice(p.length));
}

function readList<T>(key: string, ok: (v: T) => boolean): T[] {
  const v = store.get<unknown>(key, []);
  return Array.isArray(v) ? (v as T[]).filter((x) => !!x && typeof x === 'object' && ok(x)) : [];
}

// ---------------------------------------------------------------- history

/** Stories opened in the reader, most recent first. */
export const history = (): Progress[] => progress.all();
export const removeHistory = (source: string, key: string): void => progress.remove(source, key);
export const clearHistory = (): void => progress.clear();

// ---------------------------------------------------------------- bookmarks

const okBookmark = (b: Bookmark): boolean => typeof b.id === 'string' && typeof b.source === 'string' && typeof b.key === 'string';

/** Every bookmark, newest first; optionally only those of one story. */
export function bookmarks(source?: string, key?: string): Bookmark[] {
  const list = readList<Bookmark>(BOOKMARKS_KEY, okBookmark);
  return source === undefined ? list : list.filter((b) => b.source === source && b.key === key);
}

const bookmarkId = (source: string, key: string, file: string, para: number): string => `${source}|${key}|${file}|${para}`;

/** The bookmark on a paragraph, if any. */
export function findBookmark(source: string, key: string, file: string, para: number): Bookmark | null {
  const id = bookmarkId(source, key, file, para);
  return bookmarks().find((b) => b.id === id) ?? null;
}

/** Adds a bookmark (replacing one on the same paragraph) and returns it. */
export function addBookmark(b: Omit<Bookmark, 'id' | 'ts'> & { ts?: number }): Bookmark {
  return tryAddBookmark(b).bm;
}

function tryAddBookmark(b: Omit<Bookmark, 'id' | 'ts'> & { ts?: number }): { bm: Bookmark; ok: boolean } {
  const id = bookmarkId(b.source, b.key, b.file, b.para);
  const bm: Bookmark = { ...b, excerpt: String(b.excerpt || '').replace(/\s+/g, ' ').trim().slice(0, 160), id, ts: b.ts ?? Date.now() };
  const list = [bm, ...bookmarks().filter((x) => x.id !== id)].slice(0, MAX_BOOKMARKS);
  const ok = persist(BOOKMARKS_KEY, list);
  if (ok) {
    setTomb('bookmark', id, null);
    emit('bookmarks', { id });
    notify('bookmark', id, false);
  }
  return { bm, ok };
}

/** Returns false when the bookmark could not be removed because storage failed. */
export function removeBookmark(id: string): boolean {
  const list = bookmarks();
  const next = list.filter((b) => b.id !== id);
  if (next.length === list.length) return true;
  if (!persist(BOOKMARKS_KEY, next)) return false;
  setTomb('bookmark', id, Date.now());
  emit('bookmarks', { id });
  notify('bookmark', id, true);
  return true;
}

/** Adds the bookmark when the paragraph has none, removes it otherwise. Returns true when it is now set (the old state when storage failed). */
export function toggleBookmark(b: Omit<Bookmark, 'id' | 'ts'>): boolean {
  const cur = findBookmark(b.source, b.key, b.file, b.para);
  if (cur) {
    return !removeBookmark(cur.id);
  }
  return tryAddBookmark(b).ok;
}

export function clearBookmarks(): boolean {
  const old = bookmarks();
  if (!persist(BOOKMARKS_KEY, [])) return false;
  const now = Date.now();
  for (const b of old) setTomb('bookmark', b.id, now);
  emit('bookmarks', { id: null });
  for (const b of old) notify('bookmark', b.id, true);
  return true;
}

// ---------------------------------------------------------------- follows

const okFollow = (f: Follow): boolean => typeof f.source === 'string' && typeof f.key === 'string';

export const follows = (): Follow[] => readList<Follow>(FOLLOWS_KEY, okFollow);
export const isFollowed = (source: string, key: string): boolean => follows().some((f) => f.source === source && f.key === key);

export function setFollow(st: Pick<StoryDetail, 'source' | 'key' | 'name' | 'author' | 'poster' | 'cover' | 'cover_sha'>, on: boolean): boolean {
  const had = isFollowed(st.source, st.key);
  const rest = follows().filter((f) => !(f.source === st.source && f.key === st.key));
  if (on) {
    rest.unshift({
      source: st.source,
      key: st.key,
      name: st.name,
      author: st.author ?? null,
      poster: st.poster ?? null,
      cover: st.cover ?? null,
      cover_sha: st.cover_sha ?? null,
      group: st.key.includes('/') ? (st.key.split('/')[0] as string) : null,
      ts: Date.now(),
    });
  }
  if (!persist(FOLLOWS_KEY, rest.slice(0, MAX_FOLLOWS))) return false;
  const id = sKey(st.source, st.key);
  if (on) setTomb('follow', id, null);
  else if (had) setTomb('follow', id, Date.now());
  emit('follows', { key: id });
  if (on || had) notify('follow', id, !on);
  return true;
}

/** Flips the followed state; returns the new state (the old one when storage failed). */
export function toggleFollow(st: Pick<StoryDetail, 'source' | 'key' | 'name' | 'author' | 'poster' | 'cover' | 'cover_sha'>): boolean {
  const on = !isFollowed(st.source, st.key);
  return setFollow(st, on) ? on : !on;
}

export type FollowSort = 'updated' | 'recent' | 'name' | 'added';
export const FOLLOW_SORTS: [FollowSort, string][] = [
  ['updated', 'Chương mới'],
  ['recent', 'Mới đọc'],
  ['name', 'Tên A-Z'],
  ['added', 'Mới thêm'],
];
export const isFollowSort = (v: unknown): v is FollowSort => FOLLOW_SORTS.some(([k]) => k === v);

/** Sorts follows (a copy). `updated`/`lastRead` map "source|key" ids to an ISO date / timestamp; missing = oldest. */
export function sortFollows(list: Follow[], sort: FollowSort, o: { updated?: Map<string, string>; lastRead?: Map<string, number> } = {}): Follow[] {
  const id = (f: Follow): string => sKey(f.source, f.key);
  const name = (a: Follow, b: Follow): number => a.name.localeCompare(b.name, 'vi', { numeric: true, sensitivity: 'base' });
  const out = [...list];
  if (sort === 'name') return out.sort(name);
  if (sort === 'added') return out.sort((a, b) => (b.ts || 0) - (a.ts || 0) || name(a, b));
  if (sort === 'recent') return out.sort((a, b) => (o.lastRead?.get(id(b)) ?? 0) - (o.lastRead?.get(id(a)) ?? 0) || (b.ts || 0) - (a.ts || 0));
  return out.sort((a, b) => (o.updated?.get(id(b)) ?? '').localeCompare(o.updated?.get(id(a)) ?? '') || (b.ts || 0) - (a.ts || 0));
}

// ---------------------------------------------------------------- sync (see library-sync.ts)

const isRec = (v: unknown): v is Record<string, unknown> => !!v && typeof v === 'object' && !Array.isArray(v);

/** Every stored follow or bookmark of a kind with its sync id and timestamp. */
export function libraryItems(kind: LibKind): { id: string; ts: number; obj: Follow | Bookmark }[] {
  return kind === 'follow'
    ? follows().map((f) => ({ id: sKey(f.source, f.key), ts: f.ts || 0, obj: f }))
    : bookmarks().map((b) => ({ id: b.id, ts: b.ts || 0, obj: b }));
}

/** A wire entry's data as a Follow/Bookmark whose id matches the entry id, or null. */
function fromData(kind: LibKind, id: string, data: unknown, ts: number): Follow | Bookmark | null {
  if (!isRec(data) || typeof data.source !== 'string' || typeof data.key !== 'string' || !data.source || !data.key) return null;
  const s = (v: unknown): string | null => (typeof v === 'string' ? v : null);
  if (kind === 'follow') {
    if (sKey(data.source, data.key) !== id) return null;
    return { source: data.source, key: data.key, name: s(data.name) ?? data.key, author: s(data.author), poster: s(data.poster), cover: s(data.cover), cover_sha: s(data.cover_sha), group: s(data.group), ts };
  }
  if (data.id !== id) return null;
  const n = (v: unknown): number => (typeof v === 'number' && Number.isFinite(v) ? Math.max(0, Math.trunc(v)) : 0);
  return { id, source: data.source, key: data.key, name: s(data.name) ?? data.key, idx: n(data.idx), n: n(data.n), file: s(data.file) ?? '', title: s(data.title) ?? '', para: n(data.para), excerpt: (s(data.excerpt) ?? '').slice(0, 160), ts };
}

/**
 * Applies wire entries ({kind, id, ts, deleted, data}) received from the server, `skew` = server clock minus this
 * clock. Last writer wins by `ts`; on a tie a live entry beats a deletion. Nothing here is reported to
 * `onLocalChange`, so it is not sent back. Returns how many entries changed.
 */
export function applyRemote(kind: LibKind, entries: unknown[], skew = 0): number {
  const key = kind === 'follow' ? FOLLOWS_KEY : BOOKMARKS_KEY;
  const items = new Map<string, Follow | Bookmark>(libraryItems(kind).map((x) => [x.id, x.obj]));
  let changed = 0;
  for (const raw of entries) {
    if (!isRec(raw) || raw.kind !== kind || typeof raw.id !== 'string' || !raw.id) continue;
    if (typeof raw.ts !== 'number' || !Number.isFinite(raw.ts) || raw.ts <= 0) continue;
    const id = raw.id;
    const ts = Math.round(raw.ts - skew);
    const mine = items.get(id);
    const tomb = tombstone(kind, id);
    if (raw.deleted === true) {
      if (mine && mine.ts >= ts) continue; // local copy is newer (or a tie): the live entry wins
      if (tomb !== undefined && tomb >= ts) continue;
      if (mine) {
        items.delete(id);
        changed++;
      }
      setTomb(kind, id, ts);
      continue;
    }
    const obj = fromData(kind, id, raw.data, ts);
    if (!obj) continue;
    if (tomb !== undefined && tomb > ts) continue; // deleted here after this write: the pending deletion wins
    if (mine && mine.ts >= ts) continue;
    if (tomb !== undefined) setTomb(kind, id, null);
    items.set(id, obj);
    changed++;
  }
  if (!changed) return 0;
  const max = kind === 'follow' ? MAX_FOLLOWS : MAX_BOOKMARKS;
  const list = [...items.values()].sort((a, b) => (b.ts || 0) - (a.ts || 0)).slice(0, max);
  if (!persist(key, list)) return 0;
  if (kind === 'follow') emit('follows', { key: null });
  else emit('bookmarks', { id: null });
  return changed;
}

/** Test hook. */
export function _resetLibrary(): void {
  tombs = null;
  changeListeners.clear();
}

/** Relays changes made in other tabs as app events. Called once by main.ts. */
let bound = false;
export function init(): void {
  if (bound) return;
  bound = true;
  window.addEventListener('storage', (e) => {
    if (e.key === LIB_TOMB_KEY) tombs = null;
    if (e.key === BOOKMARKS_KEY) emit('bookmarks', { id: null });
    else if (e.key === FOLLOWS_KEY) emit('follows', { key: null });
  });
}

export const library = { init, onLocalChange, tombstone, tombstoneIds, libraryItems, applyRemote, history, removeHistory, clearHistory, bookmarks, findBookmark, addBookmark, removeBookmark, toggleBookmark, clearBookmarks, follows, sortFollows, isFollowed, setFollow, toggleFollow };
