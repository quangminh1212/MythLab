/** Wire types of the MythLab API (server-spec / frontend-spec 4.2). Fields marked "api 2" exist only on the Go server. */

export type BackendKind = 'none' | 'server' | 'github';

export interface RepoInfo {
  repo: string;
  branch: string;
  pushed_at: string | null;
  private: boolean | null;
}

export interface Source {
  id: string;
  name: string;
  kind: 'local' | 'github';
  detail: string;
  available: boolean;
  repos?: RepoInfo[];
  error?: string;
  /** api 2: the repo list came from a stale cache (rate limit / offline). */
  stale?: boolean;
}

export interface SourcesResponse {
  sources: Source[];
  tts: { edge: boolean; default_voice?: string };
}

export interface StorySummary {
  key: string;
  folder?: string;
  group?: string | null;
  chapter_files?: number;
  name: string;
  author: string | null;
  synopsis: string;
  poster: string | null;
  genres: string[];
  tags: string[];
  status: string | null;
  declared_chapters: number | null;
  link: string | null;
  /** Server: "/api/cover?source=…&key=…" or an absolute poster URL. GitHub-direct: poster URL or null. */
  cover: string | null;
  /** GitHub-direct only: blob sha of the cover image inside the repo. */
  cover_sha?: string | null;
  /** api 2 (optional): ISO date of the last update, used by sort=updated. */
  updated?: string | null;
  /** `/api/search` items carry their source and repo. */
  source?: string;
  repo?: string | null;
}

export interface ChapterRef {
  n: number;
  title: string;
  file: string;
  /** Sub-number ("Chương 12.5"), present only when non-zero. */
  sub?: number;
  /** Volume ("Quyển 2 Chương 1"), present only when non-zero. */
  vol?: number;
}

export interface StoryDetail extends Omit<StorySummary, 'folder' | 'group' | 'chapter_files'> {
  source: string;
  chapters: ChapterRef[];
}

export interface Chapter {
  title: string | null;
  paragraphs: string[];
  words: number;
}

export interface StoriesResponse {
  stories: StorySummary[];
  /** api 2, only when `limit` was sent. */
  total?: number;
  tags?: { name: string; count: number }[];
  /** api 2, with `limit`: status values and size of the whole listing (before filters). */
  statuses?: string[];
  all?: number;
  /** api 2: the listing came partly from cache because the source was rate-limited or unreachable. */
  stale?: boolean;
}

export interface SearchResponse {
  q: string;
  total: number;
  items: StorySummary[];
  indexed?: { stories: number; repos: number; reposTotal: number };
}

export interface Voice {
  id: string;
  name: string;
  gender?: string;
}

export interface VoicesResponse {
  voices: Voice[];
  edge?: boolean;
}

export interface PingResponse {
  ok?: boolean;
  app?: string;
  /** 2 on the Go server; absent on the Python server. */
  api?: number;
  server?: string;
}

export interface TtsOptions {
  text: string;
  voice?: string;
  /** Edge integer percent / Hz. Values with |v| <= 4 are playback factors and are not sent. */
  rate?: number;
  pitch?: number;
}

export interface TokenTest {
  ok: boolean;
  login: string | null;
  repos: number;
  rateRemaining: number | null;
  error: string | null;
}

/** Error thrown by every backend call: `status` is the HTTP status, `code` the server's additive error code. */
export class ApiError extends Error {
  status: number;
  code?: string;
  json?: unknown;
  /** GitHub status behind a 502 from the GitHub-direct backend. */
  ghStatus?: number;
  constructor(message: string, status: number, extra?: { code?: string; json?: unknown; ghStatus?: number; cause?: unknown }) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    if (extra?.code) this.code = extra.code;
    if (extra?.json !== undefined) this.json = extra.json;
    if (extra?.ghStatus) this.ghStatus = extra.ghStatus;
    if (extra?.cause !== undefined) (this as { cause?: unknown }).cause = extra.cause;
  }
}

export interface GetOptions {
  /** Abort after this many ms (0 = no timeout). */
  timeout?: number;
  signal?: AbortSignal;
}

/** What a concrete backend implements. The facade in `./index.ts` adds selection and media helpers. */
export interface BackendImpl {
  readonly kind: 'server' | 'github';
  /** API level: 2 for the Go server, 1 otherwise. */
  api: number;
  get<T = unknown>(path: string, opts?: GetOptions): Promise<T>;
  /** Direct audio URL (never contains the key); null when the backend has no TTS. */
  ttsUrl(opts: TtsOptions): string | null;
  /**
   * Cover URL for a story: a string usable as `<img src>`, a Promise of an object URL when the image needs an
   * authenticated fetch (GitHub blob, keyed server), or null when the story has no cover.
   * `w` asks for a resized variant (160|240|320|480) when the server supports it.
   */
  coverUrl(st: CoverRef, w?: number): string | Promise<string> | null;
  /** True when media URLs need the key header (so `<img>`/`<audio>` cannot load them directly). */
  readonly mediaNeedsFetch: boolean;
  /** Fetches a media URL of this backend with its credentials. */
  fetchMedia(url: string, signal?: AbortSignal): Promise<Blob>;
}

/** The fields `coverUrl` reads; StorySummary, StoryDetail and stored Progress all satisfy it. */
export interface CoverRef {
  key?: string;
  cover?: string | null;
  poster?: string | null;
  cover_sha?: string | null;
}
