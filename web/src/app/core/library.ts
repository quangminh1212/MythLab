/**
 * The reader's personal library: history (derived from progress), bookmarks (`mythlab.bookmarks`) and followed
 * stories (`mythlab.follows`). Lists are stored newest first; every write re-reads the stored list first so two
 * tabs do not overwrite each other.
 */
import type { Bookmark, Follow, Progress, StoryDetail } from './contracts';
import { emit } from './events';
import { progress } from './progress';
import { store } from './store';

export const BOOKMARKS_KEY = 'mythlab.bookmarks';
export const FOLLOWS_KEY = 'mythlab.follows';
export const MAX_BOOKMARKS = 1000;
export const MAX_FOLLOWS = 500;

/** Writes a list; when storage refuses it, tells the user and returns false (callers then skip the success event). */
function persist(key: string, list: unknown): boolean {
  if (store.set(key, list)) return true;
  emit('toast', { message: 'Không lưu được: bộ nhớ trình duyệt đã đầy hoặc bị chặn.', kind: 'error' });
  return false;
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
  if (ok) emit('bookmarks', { id });
  return { bm, ok };
}

/** Returns false when the bookmark could not be removed because storage failed. */
export function removeBookmark(id: string): boolean {
  const list = bookmarks();
  const next = list.filter((b) => b.id !== id);
  if (next.length === list.length) return true;
  if (!persist(BOOKMARKS_KEY, next)) return false;
  emit('bookmarks', { id });
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
  if (!persist(BOOKMARKS_KEY, [])) return false;
  emit('bookmarks', { id: null });
  return true;
}

// ---------------------------------------------------------------- follows

const okFollow = (f: Follow): boolean => typeof f.source === 'string' && typeof f.key === 'string';

export const follows = (): Follow[] => readList<Follow>(FOLLOWS_KEY, okFollow);
export const isFollowed = (source: string, key: string): boolean => follows().some((f) => f.source === source && f.key === key);

export function setFollow(st: Pick<StoryDetail, 'source' | 'key' | 'name' | 'author' | 'poster' | 'cover' | 'cover_sha'>, on: boolean): boolean {
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
  emit('follows', { key: `${st.source}|${st.key}` });
  return true;
}

/** Flips the followed state; returns the new state (the old one when storage failed). */
export function toggleFollow(st: Pick<StoryDetail, 'source' | 'key' | 'name' | 'author' | 'poster' | 'cover' | 'cover_sha'>): boolean {
  const on = !isFollowed(st.source, st.key);
  return setFollow(st, on) ? on : !on;
}

/** Relays changes made in other tabs as app events. Called once by main.ts. */
let bound = false;
export function init(): void {
  if (bound) return;
  bound = true;
  window.addEventListener('storage', (e) => {
    if (e.key === BOOKMARKS_KEY) emit('bookmarks', { id: null });
    else if (e.key === FOLLOWS_KEY) emit('follows', { key: null });
  });
}

export const library = { init, history, removeHistory, clearHistory, bookmarks, findBookmark, addBookmark, removeBookmark, toggleBookmark, clearBookmarks, follows, isFollowed, setFollow, toggleFollow };
