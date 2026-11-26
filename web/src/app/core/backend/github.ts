/**
 * GitHub-direct backend: reads the `Done_*` repositories through api.github.com with a read-only token and answers
 * the same routes as the server (`/sources`, `/stories`, `/story`, `/chapter`).
 * Cache (IndexedDB `mythlab` v1, schema unchanged): trees by tree sha, chapter lists `<sha>/<story>`, blobs by blob
 * sha, cover images `img:<sha>`, ETags and repo lists in `meta`. At most 4 requests run at once.
 */
import { emit } from '../events';
import { idb } from '../store';
import { chapterJson, chapterList, infoSummary, parseChapterName, pickCover } from '../textutil';
import { ApiError, type BackendImpl, type Chapter, type ChapterRef, type CoverRef, type RepoInfo, type Source, type StoryDetail, type StorySummary, type TokenTest } from './types';

const API = 'https://api.github.com';
const TTL = 600e3;
const REASON: Record<number, string> = { 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 409: 'Conflict', 422: 'Unprocessable Entity', 429: 'Too Many Requests' };
const TREE_V = 3; // bump when the tree summary shape or the chapter-list rules change (3: shared textutil fixture rules)

let active = 0;
const waiting: (() => void)[] = [];
const acquire = (): Promise<void> => (active < 4 ? (active++, Promise.resolve()) : new Promise((r) => waiting.push(r)));
const release = (): void => {
  const n = waiting.shift();
  if (n) n();
  else active--;
};

let lastRate: number | null = null;
let rateToastAt = 0;
function noteRate(r: Response): void {
  const rem = r.headers.get('X-RateLimit-Remaining');
  if (rem == null) return;
  lastRate = +rem;
  if (lastRate < 100 && Date.now() - rateToastAt > 60e3) {
    rateToastAt = Date.now();
    const reset = new Date(+(r.headers.get('X-RateLimit-Reset') || NaN) * 1000);
    const hm = Number.isNaN(reset.getTime()) ? '' : ` (đặt lại lúc ${reset.toTimeString().slice(0, 5)})`;
    emit('toast', { message: `GitHub: chỉ còn ${lastRate} lượt gọi API${hm}` });
  }
}

const isNetErr = (e: unknown): boolean => {
  const x = e as { ghStatus?: number; name?: string } | null;
  return !!x && !x.ghStatus && (x.name === 'TypeError' || x.name === 'AbortError');
};
const segs = (s: string): string => String(s).split('/').map(encodeURIComponent).join('/');
const cmp = (a: string, b: string): number => (a < b ? -1 : a > b ? 1 : 0);
// cover inside the story folder: cover.* > poster.* > folder.* > thumb.* > any image (pick_cover of the server)
const own = <T>(o: Record<string, T>, k: string): T | undefined => (Object.prototype.hasOwnProperty.call(o, k) ? o[k] : undefined);
const split = (key: string): [string, string] => {
  const i = key.indexOf('/');
  return i < 0 ? [key, ''] : [key.slice(0, i), key.slice(i + 1)];
};

/** API chapter of a stored row; `sub`/`vol` (non-zero only) are re-derived from the file name. */
function chapterRef(x: ChapterRow): ChapterRef {
  const c: ChapterRef = { n: x[0], title: x[1], file: x[2] };
  const p = parseChapterName(x[2]);
  if (p?.sub) c.sub = p.sub;
  if (p?.vol) c.vol = p.vol;
  return c;
}

/** [n, title, file, blobSha] */
type ChapterRow = [number, string, string, string];
interface TreeSummary {
  v: number;
  sha: string;
  stories: Record<string, { info: string | null; n: number; c: string | null }>;
}
interface TreeMeta {
  etag: string | null;
  sha: string;
  url: string;
  at: number;
}
interface GhResult<T = unknown> {
  status: number;
  etag: string | null;
  link: string;
  body: T;
}
interface TreeEntry {
  path: string;
  type: string;
  sha: string;
}

/** FNV-1a fingerprint of the token: separates caches per account without storing the token. */
export function tokenFingerprint(token: string): string {
  let fp = 0x811c9dc5;
  for (const ch of String(token || '')) fp = Math.imul(fp ^ (ch.codePointAt(0) as number), 0x01000193) >>> 0;
  return fp.toString(16);
}

export interface GitHubOptions {
  owner?: string;
  prefix?: string;
  sid?: string;
}

export interface GitHubBackend extends BackendImpl {
  readonly kind: 'github';
  readonly sid: string;
  readonly prefix: string;
  owner: string;
  name: string;
  repos(): Promise<RepoInfo[]>;
  describe(): Promise<Source>;
  testToken(): Promise<TokenTest>;
}

export function createGitHubBackend(token: string, { owner = '', prefix = 'Done_', sid = 'gh0' }: GitHubOptions = {}): GitHubBackend {
  const fp = tokenFingerprint(token);
  const st = { owner, name: `GitHub ${owner || '(tôi)'}/${prefix}*` };

  async function gh<T = unknown>(url: string, { raw = false, bin = false, etag = null as string | null } = {}): Promise<GhResult<T>> {
    await acquire();
    try {
      const headers: Record<string, string> = { Accept: raw ? 'application/vnd.github.raw' : 'application/vnd.github+json' };
      const full = url.startsWith('http') ? url : API + url;
      if (!full.startsWith(API + '/')) throw new ApiError('URL GitHub không hợp lệ', 400);
      if (token) headers.Authorization = `Bearer ${token}`;
      if (etag) headers['If-None-Match'] = etag;
      const r = await fetch(full, { headers, cache: 'no-store' });
      noteRate(r);
      const res: GhResult<T> = { status: r.status, etag: r.headers.get('ETag'), link: r.headers.get('Link') || '', body: undefined as T };
      if (r.status === 304) return res;
      if (!r.ok) {
        const reason = r.statusText || REASON[r.status] || 'Error';
        throw new ApiError(`GitHub ${r.status}: ${reason}`, r.status === 404 ? 404 : 502, { ghStatus: r.status });
      }
      // text(): UTF-8, BOM dropped, invalid bytes → U+FFFD (same as utf-8-sig/replace on the server)
      res.body = (bin ? await r.blob() : raw ? await r.text() : await r.json()) as T;
      return res;
    } finally {
      release();
    }
  }

  // small JSON with an ETag (a 304 does not count against the rate limit); offline → the stored copy
  async function ghCached<T = unknown>(url: string): Promise<GhResult<T>> {
    const mk = 'etag:' + fp + ':' + url;
    const c = await idb.get<{ etag: string; body: T; link: string }>('meta', mk);
    let r: GhResult<T>;
    try {
      r = await gh<T>(url, { etag: c?.etag ?? null });
    } catch (e) {
      if (c && isNetErr(e)) return { status: 200, etag: c.etag, link: c.link, body: c.body };
      throw e;
    }
    if (r.status === 304) {
      if (c) return { status: 200, etag: c.etag, link: c.link, body: c.body };
      r = await gh<T>(url);
    }
    if (r.etag) await idb.put('meta', mk, { etag: r.etag, body: r.body, link: r.link });
    return r;
  }

  async function ownerName(): Promise<string> {
    if (!st.owner) {
      const mk = 'login:' + fp;
      let login = await idb.get<string>('meta', mk);
      if (!login) {
        login = (await ghCached<{ login: string }>('/user')).body.login;
        await idb.put('meta', mk, login);
      }
      st.owner = login;
      st.name = `GitHub ${st.owner}/${prefix}*`;
    }
    return st.owner;
  }

  interface GhRepo {
    name: string;
    owner: { login: string };
    default_branch?: string;
    pushed_at?: string | null;
    private?: boolean | null;
  }
  const REPOS_URL = '/user/repos?per_page=100&affiliation=owner,collaborator,organization_member&sort=full_name';
  let reposP: Promise<RepoInfo[]> | null = null;
  let reposAt = 0;
  function repos(): Promise<RepoInfo[]> {
    if (reposP && Date.now() - reposAt < TTL) return reposP;
    reposAt = Date.now();
    const p = (async () => {
      const ownr = await ownerName();
      const mk = `repos:${fp}:${ownr}:${prefix}`;
      const c = await idb.get<{ at: number; list: RepoInfo[] }>('meta', mk);
      if (c && Date.now() - c.at < TTL) return c.list;
      let pages: GhResult<GhRepo[]>[];
      try {
        const first = await ghCached<GhRepo[]>(REPOS_URL);
        pages = [first];
        // rel="last" present → fetch the remaining pages in parallel; otherwise follow rel="next"
        const next = /<([^>]+)>;\s*rel="next"/.exec(first.link || '');
        const last = /<([^>]+)>;\s*rel="last"/.exec(first.link || '');
        const lastN = last ? +((/[?&]page=(\d+)/.exec(last[1] as string) || [])[1] || 0) : 0;
        if (next && lastN) {
          const urls: string[] = [];
          for (let i = 2; i <= lastN; i++) urls.push((next[1] as string).replace(/([?&]page=)\d+/, `$1${i}`));
          pages.push(...(await Promise.all(urls.map((u) => ghCached<GhRepo[]>(u)))));
        } else {
          for (let m = next; m; ) {
            const pg = await ghCached<GhRepo[]>(m[1] as string);
            pages.push(pg);
            m = /<([^>]+)>;\s*rel="next"/.exec(pg.link || '');
          }
        }
      } catch (e) {
        if (c && isNetErr(e)) return c.list;
        throw e;
      }
      const out: RepoInfo[] = [];
      for (const { body } of pages)
        for (const r of body) {
          if (r.owner.login.toLowerCase() === ownr.toLowerCase() && r.name.startsWith(prefix))
            out.push({ repo: r.name, branch: r.default_branch || 'main', pushed_at: r.pushed_at ?? null, private: r.private ?? null });
        }
      out.sort((a, b) => cmp(a.repo.toLowerCase(), b.repo.toLowerCase()));
      await idb.put('meta', mk, { at: Date.now(), list: out });
      return out;
    })();
    reposP = p;
    p.catch(() => {
      if (reposP === p) reposP = null;
    });
    return p;
  }

  // repo tree → summary {sha, stories: {story: {info, n, c}}} kept in memory, chapter lists stored per story under
  // "<sha>/<story>" so a tree with tens of thousands of chapters never sits in memory at once
  function buildStories(entries: TreeEntry[]): Map<string, { info: string | null; chapters: ChapterRow[]; cover: string | null }> {
    const raw = new Map<string, { info: string | null; files: Map<string, string> }>();
    for (const e of entries) {
      if (e.type !== 'blob') continue;
      const parts = e.path.split('/');
      if (parts.length !== 2) continue;
      const [story, fname] = parts as [string, string];
      let s = raw.get(story);
      if (!s) raw.set(story, (s = { info: null, files: new Map() }));
      if (fname === 'info.json') s.info = e.sha;
      else s.files.set(fname, e.sha);
    }
    const stories = new Map<string, { info: string | null; chapters: ChapterRow[]; cover: string | null }>();
    for (const [k, s] of raw) {
      const names = [...s.files.keys()];
      const chapters = chapterList(names).map((c): ChapterRow => [c.n, c.title, c.file, s.files.get(c.file) as string]);
      if (!chapters.length && !s.info) continue;
      const cover = pickCover(names);
      stories.set(k, { info: s.info, chapters, cover: cover ? (s.files.get(cover) as string) : null });
    }
    return stories;
  }

  interface GhTree {
    sha: string;
    truncated?: boolean;
    tree: TreeEntry[];
  }
  async function treeSlow(ownr: string, repo: string, sha: string): Promise<TreeEntry[]> {
    const top = (await gh<GhTree>(`/repos/${ownr}/${segs(repo)}/git/trees/${sha}`)).body;
    const subs = await Promise.all(
      top.tree
        .filter((t) => t.type === 'tree')
        .map(async (t) => {
          const sub = (await gh<GhTree>(`/repos/${ownr}/${segs(repo)}/git/trees/${t.sha}`)).body;
          return sub.tree.map((e) => ({ ...e, path: `${t.path}/${e.path}` }));
        }),
    );
    return subs.flat();
  }

  /**
   * Tree bookkeeping per repo. The legacy key `tree:<repo>` was shared by every account (bugs C3): a second token
   * with a same-named repo would read the first account's tree. New entries are written under
   * `tree:<fingerprint>:<repo>`; a legacy entry is honoured only when its URL belongs to the current owner.
   */
  const treeKey = (repo: string): string => `tree:${fp}:${repo}`;
  async function treeMeta(repo: string): Promise<TreeMeta | undefined> {
    const c = await idb.get<TreeMeta>('meta', treeKey(repo));
    if (c) return c;
    const old = await idb.get<TreeMeta>('meta', 'tree:' + repo);
    if (!old || typeof old.url !== 'string') return undefined;
    const ownr = st.owner || (await idb.get<string>('meta', 'login:' + fp)) || '';
    return ownr && old.url.toLowerCase().startsWith(`/repos/${ownr}/${segs(repo)}/`.toLowerCase()) ? old : undefined;
  }

  async function loadTree(repo: string, force = false): Promise<TreeSummary> {
    const mk = treeKey(repo);
    const c = force ? undefined : await treeMeta(repo);
    if (c && Date.now() - c.at < TTL) {
      const s = await idb.get<TreeSummary>('trees', c.sha);
      if (s?.v === TREE_V) return s;
    }
    const offline = async (e: unknown): Promise<TreeSummary> => {
      const s = c && isNetErr(e) ? await idb.get<TreeSummary>('trees', c.sha) : undefined;
      if (s) return s;
      throw e;
    };
    let ownr: string;
    let url: string;
    let r: GhResult<GhTree>;
    try {
      ownr = await ownerName();
      const known = (await repos()).find((x) => x.repo === repo);
      if (!known) throw new ApiError(`không tìm thấy kho truyện: ${repo}`, 404);
      url = `/repos/${ownr}/${segs(repo)}/git/trees/${segs(known.branch || 'main')}?recursive=1`;
      r = await gh<GhTree>(url, { etag: c && c.url === url ? c.etag : null });
    } catch (e) {
      return offline(e);
    }
    if (r.status === 304 && c) {
      const s = await idb.get<TreeSummary>('trees', c.sha);
      if (s?.v === TREE_V) {
        await idb.put('meta', mk, { ...c, at: Date.now() });
        return s;
      }
      r = await gh<GhTree>(url);
    }
    const sha = r.body.sha;
    const etag = r.etag;
    let sum = force ? undefined : await idb.get<TreeSummary>('trees', sha);
    if (sum?.v !== TREE_V) {
      const stories = buildStories(r.body.truncated ? await treeSlow(ownr, repo, sha) : r.body.tree || []);
      const fresh: TreeSummary = { v: TREE_V, sha, stories: Object.create(null) as TreeSummary['stories'] };
      await Promise.all(
        [...stories].map(([k, s]) => {
          fresh.stories[k] = { info: s.info, n: s.chapters.length, c: s.cover };
          return idb.put('trees', `${sha}/${k}`, s.chapters);
        }),
      );
      await idb.put('trees', sha, fresh);
      sum = fresh;
    }
    await idb.put('meta', mk, { etag, sha, url, at: Date.now() } satisfies TreeMeta);
    return sum;
  }

  const trees = new Map<string, { at: number; p: Promise<TreeSummary> }>();
  function tree(repo: string, force = false): Promise<TreeSummary> {
    const hit = trees.get(repo);
    if (!force && hit && Date.now() - hit.at < TTL) return hit.p;
    const p = loadTree(repo, force);
    trees.set(repo, { at: Date.now(), p });
    p.catch(() => {
      if (trees.get(repo)?.p === p) trees.delete(repo);
    });
    return p;
  }

  // chapter rows of one story; a missing stored list (cache cleared) reloads the tree
  async function chaptersOf(repo: string, story: string): Promise<ChapterRow[]> {
    let sum = await tree(repo);
    if (!own(sum.stories, story)) return [];
    let ch = await idb.get<ChapterRow[]>('trees', `${sum.sha}/${story}`);
    if (!ch) {
      sum = await tree(repo, true);
      ch = own(sum.stories, story) ? await idb.get<ChapterRow[]>('trees', `${sum.sha}/${story}`) : [];
    }
    return ch || [];
  }
  // reading a chapter: use the stored tree when it has the file (no network needed), else load the tree
  async function chaptersForRead(repo: string, story: string, file: string): Promise<ChapterRow[]> {
    const c = await treeMeta(repo);
    const ch = c ? await idb.get<ChapterRow[]>('trees', `${c.sha}/${story}`) : undefined;
    if (ch && ch.some((x) => x[2] === file)) return ch;
    return chaptersOf(repo, story);
  }

  const blobsP = new Map<string, Promise<string>>();
  async function blob(repo: string, sha: string): Promise<string> {
    const hit = await idb.get<unknown>('blobs', sha);
    if (typeof hit === 'string') return hit;
    let p = blobsP.get(sha);
    if (!p) {
      p = (async () => {
        const ownr = await ownerName();
        const text = (await gh<string>(`/repos/${ownr}/${segs(repo)}/git/blobs/${sha}`, { raw: true })).body;
        await idb.put('blobs', sha, text);
        return text;
      })();
      blobsP.set(sha, p);
      p.finally(() => blobsP.delete(sha)).catch(() => {});
    }
    return p;
  }

  // cover inside the repo: blob fetched on demand (IndexedDB "blobs", key "img:<sha>") → object URL
  const coverUrls = new Map<string, Promise<string>>();
  function coverBlobUrl(repo: string, sha: string): Promise<string> {
    let p = coverUrls.get(sha);
    if (!p) {
      p = (async () => {
        let b = await idb.get<unknown>('blobs', 'img:' + sha);
        if (!(b instanceof Blob)) {
          b = (await gh<Blob>(`/repos/${await ownerName()}/${segs(repo)}/git/blobs/${sha}`, { raw: true, bin: true })).body;
          await idb.put('blobs', 'img:' + sha, b);
        }
        return URL.createObjectURL(b as Blob);
      })();
      coverUrls.set(sha, p);
      p.catch(() => coverUrls.delete(sha));
    }
    return p;
  }
  // `cover`: the poster when the folder has no image; with an image, `cover_sha` → coverUrl() fetches the blob lazily
  const withCover = <T extends { poster: string | null }>(s: T, c: string | null | undefined): T & { cover: string | null; cover_sha: string | null } =>
    Object.assign(s, { cover: c ? null : s.poster, cover_sha: c || null });
  function coverUrl(s: CoverRef): string | Promise<string> | null {
    if (s?.cover_sha && s.key) return coverBlobUrl(split(s.key)[0], s.cover_sha);
    return [s?.cover, s?.poster].find((u): u is string => typeof u === 'string' && /^https?:\/\//i.test(u)) || null;
  }

  async function infoFor(repo: string, story: string): Promise<unknown> {
    const s = own((await tree(repo)).stories, story);
    if (!s || !s.info) return null;
    try {
      return JSON.parse(await blob(repo, s.info));
    } catch {
      return null; // one bad info.json never fails a listing
    }
  }

  async function listStories(repo: string | null): Promise<StorySummary[]> {
    const list = repo ? [repo] : (await repos()).map((r) => r.repo);
    const parts = await Promise.all(
      list.map(async (rp) => {
        const t = (await tree(rp)).stories;
        return Promise.all(
          Object.keys(t)
            .sort(cmp)
            .map(async (story) =>
              withCover(
                { key: `${rp}/${story}`, folder: story, group: rp, chapter_files: (t[story] as { n: number }).n, ...infoSummary(await infoFor(rp, story), story) },
                (t[story] as { c: string | null }).c,
              ),
            ),
        );
      }),
    );
    return parts.flat();
  }

  async function describe(): Promise<Source> {
    const d: Source = { id: sid, name: st.name, kind: 'github', detail: `${st.owner}/${prefix}*`, available: true };
    try {
      d.repos = await repos();
      d.name = st.name;
      d.detail = `${st.owner}/${prefix}*`;
    } catch (e) {
      d.available = false;
      d.error = e instanceof Error ? e.message : String(e);
    }
    return d;
  }

  async function route(path: string): Promise<unknown> {
    const u = new URL('/' + String(path || '').replace(/^\/+/, '').replace(/^api\//, ''), 'http://x');
    const q: Record<string, string> = {};
    for (const [k, v] of u.searchParams) if (v !== '') q[k] = v; // parse_qs drops empty values
    const need = (k: string): string => {
      const v = q[k];
      if (v === undefined) throw new ApiError(`thiếu/không đúng tham số: '${k}'`, 400);
      return v;
    };
    const src = (): void => {
      const s = need('source');
      if (s !== sid) throw new ApiError(`thiếu/không đúng tham số: '${s}'`, 400);
    };
    switch (u.pathname.slice(1)) {
      case 'ping':
        return { ok: true, app: 'mythlab', api: 1, server: 'github-direct' };
      case 'sources':
        return { sources: [await describe()], tts: { edge: false, default_voice: 'vi-VN-HoaiMyNeural' } };
      case 'stories':
        src();
        return { stories: await listStories(q.repo || null) };
      case 'story': {
        src();
        const key = need('key');
        const [repo, story] = split(key);
        const sum = (await tree(repo)).stories;
        if (!own(sum, story)) throw new ApiError(`không tìm thấy truyện: ${story || key}`, 404);
        const info = await infoFor(repo, story);
        const chs = await chaptersOf(repo, story);
        const c = own(sum, story)?.c;
        const detail: StoryDetail = {
          ...withCover({ key, source: q.source as string, ...infoSummary(info, key.split('/').pop() as string) }, c),
          chapters: chs.map(chapterRef),
        };
        return detail;
      }
      case 'chapter': {
        src();
        const key = need('key');
        const file = need('file');
        const [repo, story] = split(key);
        const c = (await chaptersForRead(repo, story, file)).find((ch) => ch[2] === file);
        if (!c) throw new ApiError(`không tìm thấy: ${file}`, 404);
        const out: Chapter = chapterJson(await blob(repo, c[3]), file);
        return out;
      }
      case 'voices':
        return { voices: [], edge: false };
      case 'tts':
        throw new ApiError('Không có máy chủ đọc truyện (đang đọc trực tiếp từ GitHub)', 503);
      default:
        throw new ApiError('không có API này', 404);
    }
  }

  async function get<T = unknown>(path: string): Promise<T> {
    try {
      return (await route(path)) as T;
    } catch (e) {
      if (e instanceof ApiError) throw e;
      const x = e as Error;
      throw new ApiError(`${x?.name || 'Error'}: ${x?.message}`, 500, { cause: e });
    }
  }

  async function testToken(): Promise<TokenTest> {
    try {
      const me = await gh<{ login: string }>('/user');
      if (!st.owner) {
        st.owner = me.body.login;
        st.name = `GitHub ${st.owner}/${prefix}*`;
      }
      const rs = await repos();
      return { ok: true, login: me.body.login, repos: rs.length, rateRemaining: lastRate, error: null };
    } catch (e) {
      const x = e as ApiError;
      return { ok: false, login: null, repos: 0, rateRemaining: lastRate, error: x.ghStatus === 401 ? 'Token không hợp lệ hoặc đã hết hạn' : x.message };
    }
  }

  return {
    kind: 'github',
    api: 1,
    sid,
    prefix,
    get owner() {
      return st.owner;
    },
    set owner(v: string) {
      st.owner = v;
    },
    get name() {
      return st.name;
    },
    set name(v: string) {
      st.name = v;
    },
    get,
    coverUrl,
    mediaNeedsFetch: false,
    fetchMedia: async (url: string, signal?: AbortSignal) => {
      const r = await fetch(url, { signal, referrerPolicy: 'no-referrer' });
      if (!r.ok) throw new ApiError(`HTTP ${r.status}`, r.status);
      return r.blob();
    },
    repos,
    describe,
    testToken,
  };
}
