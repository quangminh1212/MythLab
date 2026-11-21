/**
 * Offline storage: chapters downloaded on purpose ("Tải về để đọc offline"), what the caches hold and how to
 * empty them.
 *
 * Layers (names in src/sw/shared.ts):
 *  - `mythlab-offline`   chapters the user downloaded (never evicted) + one small record per story;
 *  - `mythlab-chapters`  chapters read recently (LRU, kept by the service worker);
 *  - `mythlab-api`, `mythlab-covers`, `mythlab-tts`, `mythlab-assets`, `mythlab-shell-*` (service worker);
 *  - IndexedDB `mythlab` (GitHub-direct trees and files) and the in-memory caches of core/data.
 *
 * A chapter is stored once under a synthetic same-origin URL (`chapterKey`). On the server backend the service
 * worker answers `/api/chapter` from these entries, so the reader works offline without knowing about them; on
 * GitHub-direct the files are also in IndexedDB, which that backend reads when the network is gone.
 */
import { backend } from '../core/backend/index';
import type { Chapter } from '../core/backend/types';
import type { ChapterRef, DownloadOptions, DownloadProgress, OfflineApi } from '../core/contracts';
import { data, isAbort } from '../core/data';
import { Emitter } from '../core/events';
import { sKey } from '../core/format';
import { idb } from '../core/store';
import { CACHE, chapterKey, HDR_AT, HDR_SIZE, parseChapterKey, parseStoryMetaKey, scopeOf, storyMetaKey, storyPrefix, type SwRequest } from '../../sw/shared';

export const CHAPTER_CACHE = CACHE.chapters;
export const PINNED_CACHE = CACHE.pinned;

const scope = (): string => scopeOf(location.href);
const available = (): boolean => typeof caches !== 'undefined' && typeof location !== 'undefined' && /^https?:$/.test(location.protocol);

/** Sends a message to the controlling service worker, if there is one. */
function tellWorker(msg: SwRequest): void {
  try {
    navigator.serviceWorker?.controller?.postMessage(msg);
  } catch {
    /* no worker */
  }
}

/** A JSON entry with the time and size headers the service worker also writes. */
export function jsonEntry(value: unknown, now = Date.now()): Response {
  const text = JSON.stringify(value);
  const size = new Blob([text]).size;
  return new Response(text, { headers: { 'Content-Type': 'application/json; charset=utf-8', [HDR_AT]: String(now), [HDR_SIZE]: String(size) } });
}

/** Size of a stored entry in bytes: the recorded size, the Content-Length, else the body itself. */
export async function entrySize(res: Response): Promise<number> {
  const n = Number(res.headers.get(HDR_SIZE) || res.headers.get('content-length'));
  if (Number.isFinite(n) && n > 0) return n;
  try {
    return (await res.blob()).size;
  } catch {
    return 0;
  }
}

// ---------------------------------------------------------------- downloaded stories

/** The record kept next to the chapters of a downloaded story. */
export interface StoryRecord {
  source: string;
  key: string;
  name: string;
  /** Chapters the story had when it was last downloaded. */
  total: number;
  ts: number;
}

export interface DownloadedStory extends StoryRecord {
  /** Chapters stored on this device. */
  chapters: number;
  bytes: number;
}

async function writeRecord(rec: StoryRecord): Promise<void> {
  const cache = await caches.open(CACHE.pinned);
  await cache.put(storyMetaKey(scope(), rec.source, rec.key), jsonEntry(rec));
}

async function readRecord(cache: Cache, source: string, key: string): Promise<StoryRecord | null> {
  try {
    const m = await cache.match(storyMetaKey(scope(), source, key));
    const r = m ? ((await m.json()) as Partial<StoryRecord>) : null;
    if (!r || typeof r.name !== 'string') return null;
    return { source, key, name: r.name, total: Number(r.total) || 0, ts: Number(r.ts) || 0 };
  } catch {
    return null;
  }
}

/** Every story with at least one downloaded chapter, newest download first. */
async function list(): Promise<DownloadedStory[]> {
  if (!available()) return [];
  try {
    const cache = await caches.open(CACHE.pinned);
    const sc = scope();
    const by = new Map<string, DownloadedStory>();
    const reqs = await cache.keys();
    for (const req of reqs) {
      const id = parseChapterKey(sc, req.url);
      if (!id) continue;
      const k = sKey(id.source, id.key);
      let st = by.get(k);
      if (!st) by.set(k, (st = { source: id.source, key: id.key, name: id.key.split('/').pop() || id.key, total: 0, ts: 0, chapters: 0, bytes: 0 }));
      st.chapters++;
      const res = await cache.match(req);
      if (res) st.bytes += await entrySize(res);
    }
    for (const req of reqs) {
      const id = parseStoryMetaKey(sc, req.url);
      const st = id && by.get(sKey(id.source, id.key));
      if (!id) continue;
      // a record without chapters is left over from a removal that was interrupted
      if (!st) {
        await cache.delete(req);
        continue;
      }
      const rec = await readRecord(cache, id.source, id.key);
      if (rec) Object.assign(st, { name: rec.name, total: rec.total, ts: rec.ts });
    }
    return [...by.values()].sort((a, b) => b.ts - a.ts || a.name.localeCompare(b.name));
  } catch {
    return [];
  }
}

/** Deletes the downloaded chapters of one story. Returns how many were removed. */
async function removeStory(source: string, key: string): Promise<number> {
  if (!available()) return 0;
  const cache = await caches.open(CACHE.pinned);
  const prefix = storyPrefix(scope(), source, key);
  let n = 0;
  for (const req of await cache.keys()) {
    if (req.url.startsWith(prefix) && (await cache.delete(req))) n++;
  }
  await cache.delete(storyMetaKey(scope(), source, key));
  changes.emit();
  return n;
}

/** The stored copy of a chapter (downloaded, else recently read), or null. */
async function read(source: string, key: string, file: string): Promise<Chapter | null> {
  if (!available()) return null;
  const url = chapterKey(scope(), source, key, file);
  try {
    for (const name of [CACHE.pinned, CACHE.chapters]) {
      const hit = await (await caches.open(name)).match(url);
      if (hit) return (await hit.json()) as Chapter;
    }
  } catch {
    /* unreadable entry: treat as missing */
  }
  return null;
}

/** The files of a story that are downloaded, as a set of chapter file names. */
async function storedFiles(source: string, key: string): Promise<Set<string>> {
  const out = new Set<string>();
  if (!available()) return out;
  try {
    const sc = scope();
    const prefix = storyPrefix(sc, source, key);
    for (const req of await (await caches.open(CACHE.pinned)).keys()) {
      if (!req.url.startsWith(prefix)) continue;
      const id = parseChapterKey(sc, req.url);
      if (id) out.add(id.file);
    }
  } catch {
    /* empty */
  }
  return out;
}

// ---------------------------------------------------------------- download jobs

export type JobState = 'running' | 'paused' | 'done' | 'cancelled';

export interface DownloadJob {
  readonly source: string;
  readonly key: string;
  readonly state: JobState;
  /** `done` counts every chapter handled (stored, already stored or failed); `failed` those that could not be fetched. */
  readonly progress: DownloadProgress;
  pause(): void;
  resume(): void;
  cancel(): void;
  /** Called after every chapter and every state change. Returns the unsubscribe function. */
  onChange(fn: (job: DownloadJob) => void): () => void;
  /** Resolves when the job ended (finished or cancelled); never rejects. */
  readonly finished: Promise<DownloadProgress>;
}

export interface JobOptions {
  /** Chapter list of the story (saves a request when the caller has it). */
  chapters?: ChapterRef[];
  /** First and last chapter index, inclusive (default: the whole story). */
  from?: number;
  to?: number;
  /** Story title for the list of downloads. */
  name?: string;
  /** Total number of chapters of the story (default: `chapters.length`). */
  total?: number;
}

const jobs = new Map<string, DownloadJob>();
const changes = new Emitter<void>();

/** Chapters fetched at the same time: GitHub's API is rate limited, a LAN server is not. */
const parallel = (): number => (backend.kind === 'github' ? 3 : 4);

/** The inclusive index range a job covers, clamped to the chapter list. */
export function clampRange(count: number, from?: number, to?: number): { from: number; to: number } {
  const last = Math.max(0, count - 1);
  const a = Math.min(last, Math.max(0, Math.floor(Number.isFinite(from as number) ? (from as number) : 0)));
  const b = Math.min(last, Math.max(0, Math.floor(Number.isFinite(to as number) ? (to as number) : last)));
  return a <= b ? { from: a, to: b } : { from: b, to: a };
}

/**
 * Starts downloading chapters of a story (one job per story; a running job is returned as is). The job keeps
 * running when the dialog that started it closes.
 */
function startJob(source: string, key: string, o: JobOptions = {}): DownloadJob {
  const id = sKey(source, key);
  const running = jobs.get(id);
  if (running && (running.state === 'running' || running.state === 'paused')) return running;

  let state: JobState = 'running';
  const progress: DownloadProgress = { done: 0, total: 0, failed: 0 };
  const listeners = new Emitter<DownloadJob>();
  const ctl = new AbortController();
  let wake: (() => void) | null = null;
  const notify = (): void => listeners.emit(job);
  /** Resolves at once while running; waits while paused. False when the job was cancelled. */
  const gate = async (): Promise<boolean> => {
    while (state === 'paused') await new Promise<void>((r) => (wake = r));
    return state === 'running';
  };

  const run = async (): Promise<DownloadProgress> => {
    try {
      if (!available()) return progress;
      const sc = scope();
      let chapters = o.chapters;
      let name = o.name;
      let total = o.total;
      if (!chapters || !name) {
        const st = await data.story(source, key, { signal: ctl.signal });
        chapters = chapters || st.chapters;
        name = name || st.name;
        total = total ?? st.chapters.length;
      }
      const r = clampRange(chapters.length, o.from, o.to);
      const todo = chapters.length ? chapters.slice(r.from, r.to + 1) : [];
      progress.total = todo.length;
      notify();
      if (!todo.length) return progress;

      void navigator.storage?.persist?.().catch(() => false);
      // the worker stores what it sees under this prefix as a download, not as a recent read
      tellWorker({ type: 'PIN', prefixes: [storyPrefix(sc, source, key)] });
      const pinned = await caches.open(CACHE.pinned);
      const recent = await caches.open(CACHE.chapters);
      await writeRecord({ source, key, name: name || key, total: total ?? chapters.length, ts: Date.now() });
      // keep the story page and the source list readable offline as well (answers land in the worker's cache)
      if (navigator.serviceWorker?.controller && backend.kind === 'server') {
        void backend.get(`/story?source=${encodeURIComponent(source)}&key=${encodeURIComponent(key)}`, { signal: ctl.signal }).catch(() => {});
      }

      let next = 0;
      const one = async (ch: ChapterRef): Promise<void> => {
        const url = chapterKey(sc, source, key, ch.file);
        if (await pinned.match(url)) return;
        const seen = await recent.match(url);
        if (seen) {
          await pinned.put(url, seen);
          return;
        }
        let body: Chapter;
        try {
          body = await data.chapter(source, key, ch.file, { signal: ctl.signal });
        } catch (e) {
          if (isAbort(e)) throw e;
          // one more try: a busy server or a dropped connection usually recovers
          await new Promise((r2) => setTimeout(r2, 600));
          body = await data.chapter(source, key, ch.file, { signal: ctl.signal });
        }
        await pinned.put(url, jsonEntry(body));
      };
      const worker = async (): Promise<void> => {
        while (next < todo.length) {
          if (!(await gate())) return;
          const ch = todo[next++] as ChapterRef;
          try {
            await one(ch);
          } catch (e) {
            if (isAbort(e) || ctl.signal.aborted) return;
            progress.failed++;
          }
          progress.done++;
          notify();
        }
      };
      await Promise.all(Array.from({ length: Math.min(parallel(), todo.length) }, worker));
      // the memory cache of core/data holds every chapter just fetched: free it
      data.invalidate('chapter:');
    } catch (e) {
      if (!isAbort(e)) progress.failed = Math.max(progress.failed, progress.total - progress.done);
    } finally {
      if (state !== 'cancelled') state = 'done';
      notify();
      changes.emit();
      if (jobs.get(id) === job) jobs.delete(id);
    }
    return { ...progress };
  };

  const job: DownloadJob = {
    source,
    key,
    get state() {
      return state;
    },
    get progress() {
      return { ...progress };
    },
    pause() {
      if (state !== 'running') return;
      state = 'paused';
      notify();
    },
    resume() {
      if (state !== 'paused') return;
      state = 'running';
      wake?.();
      wake = null;
      notify();
    },
    cancel() {
      if (state === 'done' || state === 'cancelled') return;
      state = 'cancelled';
      ctl.abort();
      wake?.();
      wake = null;
      notify();
    },
    onChange: (fn) => listeners.on(fn),
    get finished() {
      return finished;
    },
  };
  jobs.set(id, job);
  const finished = run();
  return job;
}

// ---------------------------------------------------------------- cache layers

export type LayerId = 'downloads' | 'chapters' | 'covers' | 'tts' | 'api' | 'assets' | 'shell' | 'idb';

export interface CacheLayer {
  id: LayerId;
  label: string;
  /** Stored entries (0 for IndexedDB, whose rows cannot be counted cheaply). */
  entries: number;
  bytes: number;
}

const LAYERS: { id: Exclude<LayerId, 'idb'>; label: string; match: (name: string) => boolean }[] = [
  { id: 'downloads', label: 'Truyện đã tải về', match: (n) => n === CACHE.pinned },
  { id: 'chapters', label: 'Chương đọc gần đây', match: (n) => n === CACHE.chapters },
  { id: 'covers', label: 'Ảnh bìa', match: (n) => n === CACHE.covers },
  { id: 'tts', label: 'Âm thanh giọng đọc', match: (n) => n === CACHE.tts },
  { id: 'api', label: 'Danh sách truyện', match: (n) => n === CACHE.api },
  { id: 'assets', label: 'Phông chữ', match: (n) => n === CACHE.assets || n === CACHE.legacyStatic },
  { id: 'shell', label: 'Ứng dụng (dùng khi mất mạng)', match: (n) => n.startsWith(CACHE.shellPrefix) },
];

async function cacheStats(name: string): Promise<{ entries: number; bytes: number }> {
  const cache = await caches.open(name);
  const reqs = await cache.keys();
  let bytes = 0;
  for (const req of reqs) {
    const res = await cache.match(req);
    if (res) bytes += await entrySize(res);
  }
  return { entries: reqs.length, bytes };
}

/** What every cache layer holds right now. */
async function layers(): Promise<CacheLayer[]> {
  const out: CacheLayer[] = [];
  if (available()) {
    let names: string[] = [];
    try {
      names = await caches.keys();
    } catch {
      /* storage blocked */
    }
    for (const l of LAYERS) {
      let entries = 0;
      let bytes = 0;
      for (const n of names.filter(l.match)) {
        try {
          const s = await cacheStats(n);
          entries += s.entries;
          bytes += s.bytes;
        } catch {
          /* skip an unreadable bucket */
        }
      }
      out.push({ id: l.id, label: l.label, entries, bytes });
    }
  }
  try {
    const e = (await navigator.storage.estimate()) as StorageEstimate & { usageDetails?: { indexedDB?: number } };
    const n = e.usageDetails?.indexedDB;
    if (typeof n === 'number') out.push({ id: 'idb', label: 'Dữ liệu kho GitHub', entries: 0, bytes: n });
  } catch {
    /* not supported */
  }
  return out;
}

export interface ClearOptions {
  /** Keep the chapters the user downloaded on purpose (default false: everything goes). */
  keepDownloads?: boolean;
}

/**
 * Empties every cache layer: memory, IndexedDB and Cache Storage. The shell of the running build stays, so the
 * app still opens without a network. Returns the number of bytes that were stored in the removed buckets.
 */
async function clear(o: ClearOptions = {}): Promise<number> {
  let freed = 0;
  if (!o.keepDownloads) for (const j of [...jobs.values()]) j.cancel();
  if (typeof caches !== 'undefined') {
    let current = '';
    try {
      // the shell bucket the page was loaded from is the newest one
      const shells = (await caches.keys()).filter((n) => n.startsWith(CACHE.shellPrefix));
      current = await currentShell(shells);
    } catch {
      /* none */
    }
    for (const name of await caches.keys().catch(() => [] as string[])) {
      const ours = name.startsWith('mythlab-');
      if (!ours || name === current) continue;
      if (o.keepDownloads && name === CACHE.pinned) continue;
      try {
        if (name !== CACHE.meta) freed += (await cacheStats(name)).bytes;
        await caches.delete(name);
      } catch {
        /* keep going */
      }
    }
  }
  await idb.clear();
  data.invalidate();
  tellWorker({ type: 'CACHES_CLEARED' });
  changes.emit();
  return freed;
}

/** The shell bucket that holds the scripts of the running page (the one to keep). */
async function currentShell(shells: string[]): Promise<string> {
  if (shells.length <= 1) return shells[0] || '';
  const mine = [...document.querySelectorAll<HTMLScriptElement>('script[src]')].map((s) => s.src).filter((s) => s.includes('/_astro/'));
  for (const name of shells) {
    const cache = await caches.open(name);
    const hits = await Promise.all(mine.map((u) => cache.match(u)));
    if (mine.length && hits.every(Boolean)) return name;
  }
  return shells[shells.length - 1] as string;
}

// ---------------------------------------------------------------- public API

export const offline: OfflineApi & {
  /** Starts (or returns the running) download job of a story. */
  startJob: typeof startJob;
  /** The running or paused job of a story, if any. */
  job(source: string, key: string): DownloadJob | null;
  read: typeof read;
  storedFiles: typeof storedFiles;
  list: typeof list;
  removeStory: typeof removeStory;
  layers: typeof layers;
  /** Empties the caches; the contract's `clear()` removes everything, `{ keepDownloads: true }` spares downloads. */
  clear(o?: ClearOptions): Promise<void>;
  clearAll: typeof clear;
  /** Fires when downloads were added or removed, or the caches were emptied. */
  onChange(fn: () => void): () => void;
} = {
  isAvailable: available,

  async downloadStory(source: string, key: string, opts: DownloadOptions = {}): Promise<DownloadProgress> {
    if (!available()) return { done: 0, total: 0, failed: 0 };
    const job = startJob(source, key, { chapters: opts.chapters, from: opts.from, to: opts.to });
    const off = opts.onProgress ? job.onChange((j) => opts.onProgress?.(j.progress)) : null;
    const onAbort = (): void => job.cancel();
    if (opts.signal?.aborted) job.cancel();
    else opts.signal?.addEventListener('abort', onAbort, { once: true });
    try {
      return await job.finished;
    } finally {
      off?.();
      opts.signal?.removeEventListener('abort', onAbort);
    }
  },

  async storyStatus(source: string, key: string): Promise<{ chapters: number }> {
    return { chapters: (await storedFiles(source, key)).size };
  },

  async usage(): Promise<{ used: number; quota: number }> {
    try {
      const e = await navigator.storage.estimate();
      return { used: e.usage || 0, quota: e.quota || 0 };
    } catch {
      return { used: 0, quota: 0 };
    }
  },

  async clear(o?: ClearOptions): Promise<void> {
    await clear(o);
  },
  clearAll: clear,

  startJob,
  job: (source, key) => jobs.get(sKey(source, key)) ?? null,
  read,
  storedFiles,
  list,
  removeStory,
  layers,
  onChange: (fn) => changes.on(fn),
};
