/**
 * Data access for the views: thin, cached wrappers around `backend.get`. Views never build API paths themselves.
 * Caches are in memory (the service worker and the GitHub backend persist what is worth persisting) and are
 * dropped when the data source changes.
 */
import { backend } from './backend/index';
import type { Chapter, GetOptions, SearchResponse, SourcesResponse, StoriesResponse, StoryDetail, StorySummary } from './backend/types';
import { on } from './events';
import { matchTokens, normKey, tokens, viCompare } from './format';

const enc = encodeURIComponent;

interface Entry<T> {
  t: number;
  p: Promise<T>;
}
const cache = new Map<string, Entry<unknown>>();
const MAX_ENTRIES = 120;

function cached<T>(key: string, ttl: number, load: () => Promise<T>): Promise<T> {
  const hit = cache.get(key) as Entry<T> | undefined;
  if (hit && Date.now() - hit.t < ttl) {
    cache.delete(key);
    cache.set(key, hit);
    return hit.p;
  }
  const p = load();
  const e: Entry<T> = { t: Date.now(), p };
  cache.set(key, e);
  p.catch(() => {
    if (cache.get(key) === e) cache.delete(key);
  });
  while (cache.size > MAX_ENTRIES) cache.delete(cache.keys().next().value as string);
  return p;
}

/** Rejects with AbortError when `signal` aborts, without cancelling the shared (cached) request. */
function withSignal<T>(p: Promise<T>, signal?: AbortSignal): Promise<T> {
  if (!signal) return p;
  if (signal.aborted) return Promise.reject(new DOMException('Aborted', 'AbortError'));
  return new Promise<T>((resolve, reject) => {
    const onAbort = (): void => reject(new DOMException('Aborted', 'AbortError'));
    signal.addEventListener('abort', onAbort, { once: true });
    p.then(
      (v) => {
        signal.removeEventListener('abort', onAbort);
        resolve(v);
      },
      (e) => {
        signal.removeEventListener('abort', onAbort);
        reject(e);
      },
    );
  });
}

/** Drops every cached response (the data source changed, or the user asked to refresh). */
export function invalidate(prefix = ''): void {
  if (!prefix) cache.clear();
  else for (const k of [...cache.keys()]) if (k.startsWith(prefix)) cache.delete(k);
}
on('backend', () => invalidate());

/** True for an aborted request: views ignore these. */
export const isAbort = (e: unknown): boolean => (e as { name?: string } | null)?.name === 'AbortError';

export function sources(o: GetOptions = {}): Promise<SourcesResponse> {
  return withSignal(
    cached('sources', 60_000, () => backend.get<SourcesResponse>('/sources', { timeout: 30_000 })),
    o.signal,
  );
}

/** Every story of a source (local) or of one repository (GitHub). Unpaged: the legacy response. */
export function stories(source: string, repo?: string | null, o: GetOptions = {}): Promise<StorySummary[]> {
  const path = `/stories?source=${enc(source)}${repo ? `&repo=${enc(repo)}` : ''}`;
  return withSignal(
    cached('stories:' + path, 5 * 60_000, () => backend.get<StoriesResponse>(path, { timeout: 90_000 }).then((j) => j.stories || [])),
    o.signal,
  );
}

export function story(source: string, key: string, o: GetOptions = {}): Promise<StoryDetail> {
  const path = `/story?source=${enc(source)}&key=${enc(key)}`;
  return withSignal(
    cached('story:' + path, 5 * 60_000, () => backend.get<StoryDetail>(path, { timeout: 60_000 })),
    o.signal,
  );
}

/** A chapter is small text: an unreachable server should show the error screen within ~20 s, not a minute. */
const CHAPTER_TIMEOUT_MS = 20_000;

export function chapter(source: string, key: string, file: string, o: GetOptions = {}): Promise<Chapter> {
  const path = `/chapter?source=${enc(source)}&key=${enc(key)}&file=${enc(file)}`;
  return withSignal(
    cached('chapter:' + path, 10 * 60_000, () => backend.get<Chapter>(path, { timeout: CHAPTER_TIMEOUT_MS })),
    o.signal,
  );
}

// ---------------------------------------------------------------- story lists (filter / sort / page)

export type StorySort = 'name' | 'chapters' | 'updated' | 'recent';

export interface StoryQuery {
  source: string;
  /** Repository; null/undefined = the whole source. */
  repo?: string | null;
  q?: string;
  status?: string;
  tag?: string;
  sort?: StorySort;
  offset?: number;
  limit?: number;
  /** For sort "recent": last-read time by story key (0 = never). */
  recentOf?(key: string): number;
  signal?: AbortSignal;
}

export interface StoryPage {
  items: StorySummary[];
  /** Number of stories matching the filters (before paging). */
  total: number;
  /** Tags of the unfiltered list with their counts, most frequent first. */
  tags: { name: string; count: number }[];
  /** Distinct status values of the unfiltered list. */
  statuses: string[];
  /** Size of the unfiltered list (when known). */
  all: number;
  /** The server answered from cache (rate limit / offline): the list may be incomplete. */
  stale?: boolean;
}

const chapterCount = (s: StorySummary): number => s.chapter_files ?? s.declared_chapters ?? 0;

/** Search key of a story (name, author, folder, tags, genres), normalised like the server index. */
export const storyHay = (s: StorySummary): string => normKey([s.name, s.author || '', s.folder || '', (s.genres || []).join(' '), (s.tags || []).join(' ')].join(' '));

export function tagCounts(list: StorySummary[]): { name: string; count: number }[] {
  const m = new Map<string, number>();
  for (const s of list) for (const t of new Set([...(s.genres || []), ...(s.tags || [])])) if (t) m.set(t, (m.get(t) || 0) + 1);
  return [...m].map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count || viCompare(a.name, b.name));
}

/** Filters, sorts and pages a story list in memory (the fallback for servers without paging, and for "recent"). */
export function filterStories(list: StorySummary[], q: Omit<StoryQuery, 'source' | 'repo' | 'signal'>): StoryPage {
  const toks = tokens(q.q || '');
  const tag = q.tag ? normKey(q.tag) : '';
  const status = q.status ? normKey(q.status) : '';
  let items = list.filter((s) => {
    if (status && normKey(s.status || '') !== status) return false;
    if (tag && ![...(s.genres || []), ...(s.tags || [])].some((t) => normKey(t) === tag)) return false;
    return !toks.length || matchTokens(storyHay(s), toks);
  });
  const sort = q.sort || 'name';
  if (sort === 'chapters') items = [...items].sort((a, b) => chapterCount(b) - chapterCount(a) || viCompare(a.name, b.name));
  else if (sort === 'updated') items = [...items].sort((a, b) => String(b.updated || '').localeCompare(String(a.updated || '')) || viCompare(a.name, b.name));
  else if (sort === 'recent' && q.recentOf) {
    const r = q.recentOf;
    items = [...items].sort((a, b) => r(b.key) - r(a.key) || viCompare(a.name, b.name));
  } else items = [...items].sort((a, b) => viCompare(a.name, b.name));
  const total = items.length;
  const offset = Math.max(0, q.offset || 0);
  const statuses = [...new Set(list.map((s) => (s.status || '').trim()).filter(Boolean))].sort(viCompare);
  return { items: q.limit ? items.slice(offset, offset + q.limit) : items.slice(offset), total, tags: tagCounts(list), statuses, all: list.length };
}

/** True when the story list of this query should be paged by the server (Go server, whole GitHub source). */
function serverPaged(q: StoryQuery): boolean {
  return backend.api >= 2 && !!q.limit && q.sort !== 'recent';
}

/**
 * One page of a story list. Uses the server's `q/status/tag/sort/offset/limit` parameters when the API level
 * allows it, otherwise loads the legacy list once (cached) and filters in memory.
 */
export async function queryStories(q: StoryQuery): Promise<StoryPage> {
  await backend.init();
  if (serverPaged(q)) {
    const p = new URLSearchParams();
    p.set('source', q.source);
    if (q.repo) p.set('repo', q.repo);
    if (q.q) p.set('q', q.q);
    if (q.status) p.set('status', q.status);
    if (q.tag) p.set('tag', q.tag);
    if (q.sort) p.set('sort', q.sort);
    p.set('offset', String(Math.max(0, q.offset || 0)));
    p.set('limit', String(q.limit));
    const path = '/stories?' + p.toString();
    const j = await withSignal(
      cached('page:' + path, 2 * 60_000, () => backend.get<StoriesResponse>(path, { timeout: 90_000 })),
      q.signal,
    );
    if (typeof j.total === 'number') {
      const items = j.stories || [];
      const statuses = j.statuses || [...new Set(items.map((s) => (s.status || '').trim()).filter(Boolean))].sort(viCompare);
      return { items, total: j.total, tags: j.tags || [], statuses, all: j.all ?? j.total, stale: j.stale };
    }
    // the server ignored the paging parameters: it sent the whole list
    return filterStories(j.stories || [], q);
  }
  return filterStories(await stories(q.source, q.repo, { signal: q.signal }), q);
}

// ---------------------------------------------------------------- global search

export interface SearchResult extends SearchResponse {
  /** True when the result came from the in-browser index and some repositories could not be searched yet. */
  partial: boolean;
}

/** Stories known to the browser so far (every cached list), for the client-side search fallback. */
async function knownStories(signal?: AbortSignal): Promise<{ items: StorySummary[]; repos: number; reposTotal: number }> {
  const src = (await sources({ signal })).sources.filter((s) => s.available);
  const jobs: Promise<StorySummary[]>[] = [];
  let repos = 0;
  let reposTotal = 0;
  for (const s of src) {
    if (s.kind === 'github' && s.repos) {
      reposTotal += s.repos.length;
      for (const r of s.repos) {
        const path = `stories:/stories?source=${enc(s.id)}&repo=${enc(r.repo)}`;
        if (!cache.has(path)) continue;
        repos++;
        jobs.push(
          stories(s.id, r.repo, { signal }).then(
            (l) => l.map((x) => ({ ...x, source: s.id, repo: r.repo })),
            () => [],
          ),
        );
      }
    } else {
      reposTotal++;
      repos++;
      jobs.push(
        stories(s.id, null, { signal }).then(
          (l) => l.map((x) => ({ ...x, source: s.id, repo: null })),
          () => [],
        ),
      );
    }
  }
  return { items: (await Promise.all(jobs)).flat(), repos, reposTotal };
}

/** Repositories whose name matches the query are loaded on demand so a search for a genre finds its stories. */
async function warmMatchingRepos(q: string, signal?: AbortSignal): Promise<void> {
  const toks = tokens(q);
  if (!toks.length) return;
  const src = (await sources({ signal })).sources.filter((s) => s.available && s.kind === 'github' && s.repos);
  const jobs: Promise<unknown>[] = [];
  for (const s of src) {
    for (const r of s.repos || []) {
      if (jobs.length >= 3) break;
      if (matchTokens(normKey(r.repo.replace(/([a-z0-9])([A-Z])/g, '$1 $2')), toks)) jobs.push(stories(s.id, r.repo, { signal }).catch(() => []));
    }
  }
  await Promise.all(jobs);
}

/**
 * Global search. Go server: `/api/search`. Otherwise an in-browser search over every story list loaded so far
 * (plus the repositories whose name matches); `partial` says that not every repository was searched.
 */
export async function search(q: string, o: { limit?: number; offset?: number; source?: string; signal?: AbortSignal } = {}): Promise<SearchResult> {
  const limit = o.limit ?? 24;
  const offset = Math.max(0, o.offset ?? 0);
  const query = q.trim();
  if (!query) return { q: '', total: 0, items: [], partial: false };
  await backend.init();
  if (local) {
    if (Date.now() - local.at > LOCAL_FRESH) void preload(); // refresh behind the scenes, answer from memory now
    return rank(local.items, query, o, { stories: local.items.length, repos: 1, reposTotal: 1 });
  }
  if (backend.api >= 2) {
    const p = new URLSearchParams({ q: query, limit: String(limit), offset: String(offset) });
    if (o.source) p.set('source', o.source);
    const path = '/search?' + p.toString();
    try {
      const j = await withSignal(
        cached('search:' + path, 60_000, () => backend.get<SearchResponse>(path, { timeout: 30_000 })),
        o.signal,
      );
      const ix = j.indexed;
      return { ...j, items: j.items || [], total: j.total ?? (j.items || []).length, partial: !!ix && ix.repos < ix.reposTotal };
    } catch (e) {
      if (isAbort(e)) throw e;
      // fall through to the in-browser index (e.g. the route is missing on an older server)
    }
  }
  await warmMatchingRepos(query, o.signal);
  const known = await knownStories(o.signal);
  return rank(known.items, query, o, { stories: known.items.length, repos: known.repos, reposTotal: known.reposTotal });
}

/** Ranks `all` against the query (name match first, then author/genre/tag) and pages the result. */
function rank(all: StorySummary[], query: string, o: { limit?: number; offset?: number; source?: string }, indexed: { stories: number; repos: number; reposTotal: number }): SearchResult {
  const limit = o.limit ?? 24;
  const offset = Math.max(0, o.offset ?? 0);
  const toks = tokens(query);
  const pool = o.source ? all.filter((s) => s.source === o.source) : all;
  const nq = normKey(query);
  const scored: { s: StorySummary; score: number }[] = [];
  for (const s of pool) {
    const name = normKey(s.name);
    const inName = matchTokens(name, toks);
    if (!inName && !matchTokens(storyHay(s) + ' ' + normKey((s.repo || '').replace(/([a-z0-9])([A-Z])/g, '$1 $2')), toks)) continue;
    scored.push({ s, score: name === nq ? 0 : name.startsWith(nq) ? 1 : inName ? 2 : 3 });
  }
  scored.sort((a, b) => a.score - b.score || viCompare(a.s.name, b.s.name));
  return { q: query, total: scored.length, items: scored.slice(offset, offset + limit).map((x) => x.s), indexed, partial: indexed.repos < indexed.reposTotal };
}

// ---------------------------------------------------------------- preloaded library

/** The whole library when every source is served by this device/server (no GitHub repositories): searched in memory. */
let local: { items: StorySummary[]; at: number } | null = null;
let localLoading: Promise<void> | null = null;
const LOCAL_FRESH = 5 * 60_000;

async function loadLocal(): Promise<void> {
  await backend.init();
  if (backend.api < 2) return;
  const src = (await sources()).sources.filter((s) => s.available);
  if (!src.length || src.some((s) => s.kind === 'github')) {
    local = null;
    return;
  }
  const lists = await Promise.all(
    src.map((s) => backend.get<StoriesResponse>(`/stories?source=${enc(s.id)}`, { timeout: 90_000 }).then((j) => (j.stories || []).map((x) => ({ ...x, source: s.id, repo: null })))),
  );
  local = { items: lists.flat(), at: Date.now() };
}

/** Loads the story list ahead of time so the first search is instant. Safe to call repeatedly. */
export function preload(): Promise<void> {
  localLoading ??= loadLocal()
    .catch(() => {})
    .finally(() => {
      localLoading = null;
    });
  return localLoading;
}

/**
 * Loads the story list of every repository that is not in memory yet, so the in-browser search covers the whole
 * library. Reports progress after each repository; failures are skipped. Only needed when `search()` says
 * `partial`.
 */
export async function indexAll(o: { signal?: AbortSignal; onProgress?(done: number, total: number): void } = {}): Promise<void> {
  const src = (await sources({ signal: o.signal })).sources.filter((s) => s.available && s.kind === 'github' && s.repos);
  const todo: [string, string][] = [];
  for (const s of src) for (const r of s.repos || []) if (!cache.has(`stories:/stories?source=${enc(s.id)}&repo=${enc(r.repo)}`)) todo.push([s.id, r.repo]);
  let done = 0;
  let next = 0;
  o.onProgress?.(0, todo.length);
  const worker = async (): Promise<void> => {
    while (next < todo.length && !o.signal?.aborted) {
      const [sid, repo] = todo[next++] as [string, string];
      await stories(sid, repo, { signal: o.signal }).catch(() => []);
      done++;
      if (!o.signal?.aborted) o.onProgress?.(done, todo.length);
    }
  };
  await Promise.all([worker(), worker(), worker()]);
  if (o.signal?.aborted) throw new DOMException('Aborted', 'AbortError');
}

export const data = { preload, sources, stories, story, chapter, queryStories, filterStories, search, indexAll, invalidate, isAbort, tagCounts };
