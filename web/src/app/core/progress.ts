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
/** localStorage `mythlab.progress.tomb` = { "<source>|<key>": deletion ts }: deletions that sync must propagate. */
export const TOMB_KEY = 'mythlab.progress.tomb';
/** How long a deletion is remembered (the server keeps tombstones for the same time). */
export const TOMB_AGE = 60 * 24 * 3600 * 1000;
/** Entries kept at most; the oldest are dropped on write. */
export const MAX_ENTRIES = 500;

type ProgressMap = Record<string, Progress>;

let map: ProgressMap = {};
/** Keys changed in this tab since the last flush (value false = deleted). */
const dirty = new Map<string, boolean>();
let loaded = false;
let bound = false;
let tombs: Record<string, number> = {};
type LocalChange = (id: string, deleted: boolean) => void;
const changeListeners = new Set<LocalChange>();
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
  tombs = readTombs();
}

function readTombs(): Record<string, number> {
  const raw = store.get<unknown>(TOMB_KEY, {});
  const out: Record<string, number> = {};
  const min = Date.now() - TOMB_AGE;
  if (raw && typeof raw === 'object' && !Array.isArray(raw)) {
    for (const [k, v] of Object.entries(raw as Record<string, unknown>)) if (typeof v === 'number' && v > min) out[k] = v;
  }
  return out;
}

function setTomb(id: string, ts: number | null): void {
  if (ts === null) delete tombs[id];
  else tombs[id] = ts;
  store.set(TOMB_KEY, tombs);
}

function notify(id: string, deleted: boolean): void {
  for (const fn of [...changeListeners]) {
    try {
      fn(id, deleted);
    } catch (e) {
      console.error(e);
    }
  }
}

/** Calls `fn` when this device changes progress (update / remove / clear), never for entries applied from a remote. */
export function onLocalChange(fn: LocalChange): () => void {
  changeListeners.add(fn);
  return () => void changeListeners.delete(fn);
}

/** Deletion time of a story removed on this device (still to be propagated), or undefined. */
export function tombstone(id: string): number | undefined {
  ensure();
  return tombs[id];
}

const num = (v: unknown, d = 0): number => (typeof v === 'number' && Number.isFinite(v) ? Math.max(0, Math.trunc(v)) : d);
const str = (v: unknown): string | null => (typeof v === 'string' ? v : null);

/**
 * Combines two versions of one story (same rule as the server): newer `ts` wins, a tie goes to the larger
 * maxIdx then idx; `maxIdx` is the maximum of both; the listening position follows the winner.
 */
export function merge(a: Progress, b: Progress): Progress {
  const bWins = (b.ts || 0) > (a.ts || 0) || ((b.ts || 0) === (a.ts || 0) && ((b.maxIdx ?? 0) > (a.maxIdx ?? 0) || ((b.maxIdx ?? 0) === (a.maxIdx ?? 0) && b.idx > a.idx)));
  const [win, lose] = bWins ? [b, a] : [a, b];
  const out: Progress = { ...win };
  out.maxIdx = Math.max(win.maxIdx ?? 0, lose.maxIdx ?? 0, win.idx || 0);
  if (!out.listen && lose.listen) out.listen = lose.listen;
  return out;
}

/** One wire entry from the server as a Progress (ts moved into the local clock by `skew`), or null when unusable. */
function fromWire(raw: unknown, skew: number): { id: string; ts: number; deleted: boolean; p: Progress } | null {
  const r = raw as Record<string, unknown> | null;
  if (!r || typeof r !== 'object' || typeof r.source !== 'string' || typeof r.key !== 'string' || !r.source || !r.key) return null;
  if (typeof r.ts !== 'number' || !Number.isFinite(r.ts) || r.ts <= 0) return null;
  const ts = Math.round(r.ts - skew);
  const id = sKey(r.source, r.key);
  const idx = num(r.idx);
  const l = r.listen as Record<string, unknown> | null | undefined;
  const p: Progress = {
    source: r.source,
    key: r.key,
    name: str(r.name) ?? '',
    poster: str(r.poster),
    cover: str(r.cover),
    cover_sha: str(r.cover_sha),
    author: str(r.author),
    genres: Array.isArray(r.genres) ? r.genres.filter((g): g is string => typeof g === 'string').slice(0, 3) : [],
    group: str(r.group),
    idx,
    n: num(r.n, idx + 1),
    total: num(r.total),
    para: num(r.para),
    ts,
    maxIdx: Math.max(num(r.maxIdx), idx),
  };
  if (typeof r.file === 'string' && r.file) p.file = r.file;
  if (typeof r.title === 'string' && r.title) p.title = r.title;
  if (typeof r.frac === 'number' && r.frac >= 0 && r.frac <= 1) p.frac = r.frac;
  if (l && typeof l === 'object') {
    p.listen = { idx: num(l.idx), para: num(l.para), ...(typeof l.file === 'string' && l.file ? { file: l.file } : {}) };
  }
  return { id, ts, deleted: r.deleted === true, p };
}

const sameProgress = (a: Progress, b: Progress): boolean =>
  a.ts === b.ts && a.idx === b.idx && a.para === b.para && a.maxIdx === b.maxIdx && a.n === b.n && a.total === b.total && a.file === b.file && a.frac === b.frac && a.name === b.name && a.title === b.title && JSON.stringify(a.listen) === JSON.stringify(b.listen);

/**
 * Applies entries received from the sync server (`skew` = server clock minus this clock, ms). Nothing here counts
 * as a local change, so it is not sent back. A deletion newer than the local entry removes it; a story deleted
 * here after the remote copy was written stays deleted. Returns how many entries changed.
 */
export function applyRemote(entries: unknown[], skew = 0): number {
  ensure();
  let changed = 0;
  for (const raw of entries) {
    const e = fromWire(raw, skew);
    if (!e) continue;
    const mine = map[e.id];
    const tomb = tombs[e.id];
    if (e.deleted) {
      if (mine && mine.ts > e.ts) continue; // the local copy is newer: it wins and sync sends it
      if (tomb !== undefined && tomb >= e.ts) continue;
      if (mine) {
        delete map[e.id];
        dirty.set(e.id, false);
        changed++;
      }
      setTomb(e.id, e.ts);
      continue;
    }
    if (tomb !== undefined) {
      if (tomb >= e.ts) continue; // deleted here later than this write: the pending deletion wins
      setTomb(e.id, null);
    }
    const next = mine ? merge(mine, e.p) : e.p;
    if (mine && sameProgress(next, mine)) continue;
    map[e.id] = next;
    dirty.set(e.id, true);
    changed++;
  }
  if (changed) {
    save();
    emit('progress', { key: null });
  }
  return changed;
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
  if (tombs[k] !== undefined) setTomb(k, null); // alive again, newer than the deletion
  if (o.now) flush();
  else save();
  emit('progress', { key: k });
  notify(k, false);
  return next;
}

/** Records the reading position in a chapter (the usual call of the reader). */
export function saveReading(st: StoryDetail, idx: number, para = 0, frac = 0, o: { now?: boolean; skipSame?: boolean } = {}): Progress {
  const ch = st.chapters[idx] as ChapterRef | undefined;
  if (o.skipSame) {
    // A lifecycle flush (app backgrounded) of a position that did not move must not re-stamp `ts`: it would beat
    // a newer position another device pushed meanwhile.
    const prev = map[sKey(st.source, st.key)];
    if (prev && prev.idx === idx && prev.para === para && (prev.frac ?? 0) === frac) return prev;
  }
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
  setTomb(k, Date.now());
  flush();
  emit('progress', { key: k });
  notify(k, true);
}

export function clear(): void {
  ensure();
  const gone = Object.keys(map);
  const now = Date.now();
  for (const k of gone) {
    dirty.set(k, false);
    tombs[k] = now;
  }
  if (gone.length) store.set(TOMB_KEY, tombs);
  map = {};
  flush();
  emit('progress', { key: null });
  for (const k of gone) notify(k, true);
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
  tombs = {};
  changeListeners.clear();
  loaded = false;
  warned = false;
}

export const progress = { init, get, all, update, saveReading, remove, clear, flush, resolveIdx, percent, storyMeta, applyRemote, onLocalChange, tombstone, merge, _reset };
