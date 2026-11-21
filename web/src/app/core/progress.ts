/**
 * Reading progress: localStorage `mythlab.progress` = { "<source>|<key>": Progress } (legacy shape + additive
 * fields, see contracts.ts).
 *
 * Cross-tab safe: writes are collected in memory and flushed (debounced, and on pagehide / when the page is
 * hidden) by re-reading the stored map and merging only the entries this tab changed, newest `ts` wins per
 * story. A `storage` event from another tab refreshes the in-memory copy.
 */
import type { ChapterRef, Progress, StoryDetail } from './contracts';
import { debounce, emit } from './events';
import { chapterLabel, sKey } from './format';
import { store } from './store';

export const PROGRESS_KEY = 'mythlab.progress';
/** Entries kept at most; the oldest are dropped on write. */
export const MAX_ENTRIES = 500;

type ProgressMap = Record<string, Progress>;

let map: ProgressMap = {};
/** Keys changed in this tab since the last flush (value false = deleted). */
const dirty = new Map<string, boolean>();
let loaded = false;
let bound = false;
/** True after the "storage full" toast was shown, until a write succeeds again. */
let warned = false;

function valid(p: unknown): p is Progress {
  const x = p as Progress | null;
  return !!x && typeof x === 'object' && typeof x.source === 'string' && typeof x.key === 'string';
}

function readStored(): ProgressMap {
  const raw = store.get<unknown>(PROGRESS_KEY, {});
  const out: ProgressMap = Object.create(null) as ProgressMap;
  if (raw && typeof raw === 'object' && !Array.isArray(raw)) {
    for (const [k, v] of Object.entries(raw as Record<string, unknown>)) if (valid(v)) out[k] = v;
  }
  return out;
}

function ensure(): void {
  if (loaded) return;
  loaded = true;
  map = readStored();
}

/** Writes the entries changed in this tab, merged into whatever is stored now. Returns false when storage failed. */
export function flush(): boolean {
  save.cancel();
  if (!dirty.size) return true;
  const stored = readStored();
  for (const [k, alive] of dirty) {
    const mine = map[k];
    if (!alive || !mine) {
      delete stored[k];
      continue;
    }
    const theirs = stored[k];
    stored[k] = theirs && (theirs.ts || 0) > (mine.ts || 0) ? theirs : mine;
  }
  const keys = Object.keys(stored);
  if (keys.length > MAX_ENTRIES) {
    keys.sort((a, b) => ((stored[b] as Progress).ts || 0) - ((stored[a] as Progress).ts || 0));
    for (const k of keys.slice(MAX_ENTRIES)) delete stored[k];
  }
  map = stored;
  if (store.set(PROGRESS_KEY, stored)) {
    dirty.clear();
    warned = false;
    return true;
  }
  // storage refused the write: keep the entries dirty so the next flush retries, and tell the user once
  if (!warned) {
    warned = true;
    emit('toast', { message: 'Không lưu được tiến độ đọc: bộ nhớ trình duyệt đã đầy hoặc bị chặn.', kind: 'error' });
  }
  save();
  return false;
}

const save = debounce(() => void flush(), 600);

/** Starts the cross-tab and page-lifecycle listeners. Called once by main.ts (safe to call again). */
export function init(): void {
  ensure();
  if (bound) return;
  bound = true;
  window.addEventListener('storage', (e) => {
    if (e.key !== null && e.key !== PROGRESS_KEY) return;
    const fresh = readStored();
    for (const [k, alive] of dirty) {
      const mine = map[k];
      if (!alive) delete fresh[k];
      else if (mine && (!fresh[k] || ((fresh[k] as Progress).ts || 0) <= (mine.ts || 0))) fresh[k] = mine;
    }
    map = fresh;
    emit('progress', { key: null });
  });
  window.addEventListener('pagehide', () => void flush());
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') flush();
  });
}

/** The saved progress of a story, or null. */
export function get(source: string, key: string): Progress | null {
  ensure();
  return map[sKey(source, key)] ?? null;
}

/** Every saved progress, most recent first. */
export function all(): Progress[] {
  ensure();
  return Object.values(map).sort((a, b) => (b.ts || 0) - (a.ts || 0));
}

/** The story fields stored with the progress so shelves can draw a card without loading the story. */
export function storyMeta(st: Pick<StoryDetail, 'name' | 'poster' | 'cover' | 'cover_sha' | 'author' | 'genres' | 'key'>): Pick<Progress, 'name' | 'poster' | 'cover' | 'cover_sha' | 'author' | 'genres' | 'group'> {
  return {
    name: st.name,
    poster: st.poster ?? null,
    cover: st.cover ?? null,
    cover_sha: st.cover_sha ?? null,
    author: st.author ?? null,
    genres: (st.genres || []).slice(0, 3),
    group: st.key.includes('/') ? (st.key.split('/')[0] as string) : null,
  };
}

/**
 * Merges `patch` into the progress of a story and stamps `ts`. `maxIdx` only ever grows.
 * The write reaches localStorage after 600 ms, or at once with `{ now: true }` and on pagehide.
 */
export function update(patch: Partial<Progress> & { source: string; key: string }, o: { now?: boolean } = {}): Progress {
  ensure();
  const k = sKey(patch.source, patch.key);
  const prev = map[k];
  const blank = { name: '', poster: null, cover: null, cover_sha: null, author: null, genres: [], group: null, idx: 0, n: 1, total: 0, para: 0 };
  const next = Object.assign(blank, prev, patch, { ts: Date.now() }) as Progress;
  next.maxIdx = Math.max(prev?.maxIdx ?? prev?.idx ?? 0, patch.maxIdx ?? 0, next.idx || 0);
  map[k] = next;
  dirty.set(k, true);
  if (o.now) flush();
  else save();
  emit('progress', { key: k });
  return next;
}

/** Records the reading position in a chapter (the usual call of the reader). */
export function saveReading(st: StoryDetail, idx: number, para = 0, frac = 0, o: { now?: boolean } = {}): Progress {
  const ch = st.chapters[idx] as ChapterRef | undefined;
  return update(
    {
      source: st.source,
      key: st.key,
      ...storyMeta(st),
      idx,
      n: ch ? ch.n : idx + 1,
      total: st.chapters.length,
      para,
      frac,
      ...(ch ? { file: ch.file, title: chapterLabel(ch) } : {}),
    },
    o,
  );
}

export function remove(source: string, key: string): void {
  ensure();
  const k = sKey(source, key);
  if (!map[k]) return;
  delete map[k];
  dirty.set(k, false);
  flush();
  emit('progress', { key: k });
}

export function clear(): void {
  ensure();
  for (const k of Object.keys(map)) dirty.set(k, false);
  map = {};
  flush();
  emit('progress', { key: null });
}

/**
 * The chapter index a saved progress points at in the current chapter list: by file name when it was stored
 * (survives re-ordering and inserted chapters), else the stored index clamped to the list.
 */
export function resolveIdx(p: Pick<Progress, 'idx' | 'file'> | null | undefined, chapters: ChapterRef[]): number {
  if (!p || !chapters.length) return 0;
  if (p.file) {
    const at = chapters[p.idx];
    if (at && at.file === p.file) return p.idx;
    const i = chapters.findIndex((c) => c.file === p.file);
    if (i >= 0) return i;
  }
  return Math.min(chapters.length - 1, Math.max(0, Math.trunc(p.idx) || 0));
}

/** 0..100: how far through the story the saved position is. */
export function percent(p: Pick<Progress, 'idx' | 'total'>): number {
  if (!p.total || p.total <= 0) return 0;
  return Math.min(100, Math.max(0, Math.round(((p.idx + 1) / p.total) * 100)));
}

/** Test hook: forget the in-memory copy. */
export function _reset(): void {
  save.cancel();
  dirty.clear();
  map = {};
  loaded = false;
  warned = false;
}

export const progress = { init, get, all, update, saveReading, remove, clear, flush, resolveIdx, percent, storyMeta, _reset };
