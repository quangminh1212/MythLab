/**
 * Contracts between the stages of the web app. W1 (foundation) owns this file; W2 (reader + player) and W3
 * (settings + offline + PWA) implement the interfaces marked for them and must keep the exported names and
 * signatures of their modules stable, because the shell and the browse views import them.
 *
 *   src/app/views/reader.ts      default-free module exporting `mount`, `unmount`, optional `update`  (ViewModule)
 *   src/app/player/index.ts      export const player: PlayerApi
 *   src/app/settings/panel.ts    export const settingsPanel: SettingsPanelApi
 *   src/app/offline/index.ts     export const offline: OfflineApi
 *   src/app/pwa.ts               export const pwa: PwaApi
 */
import type { ChapterRef, StoryDetail } from './backend/types';

export type { BackendKind, Chapter, ChapterRef, CoverRef, RepoInfo, Source, SourcesResponse, StoryDetail, StorySummary, TtsOptions, Voice } from './backend/types';

// ---------------------------------------------------------------- routing

export type ViewName = 'home' | 'lib' | 'story' | 'read' | 'search' | 'history' | 'bookmarks';

/**
 * A parsed location hash. Path segments are percent-decoded.
 *   #/                         home
 *   #/lib/<source>[/<repo>|*]  lib      (repo "*" = every story of the source)
 *   #/s/<source>/<key>         story
 *   #/r/<source>/<key>/<idx>   read     (idx is 0-based)
 *   #/search?q=…               search
 *   #/history, #/bookmarks
 * Everything after "?" inside the hash is view state (`query`), e.g. #/lib/gh0/Done_X?sort=chapters&tag=Hài.
 */
export interface Route {
  view: ViewName;
  source?: string;
  repo?: string;
  key?: string;
  idx?: number;
  query: Record<string, string>;
  /** The path part of the hash without the query, e.g. "#/s/gh0/Done_X%2FTruyen". */
  path: string;
  /** The full hash as written in the address bar. */
  hash: string;
}

/** Passed to every view on mount. */
export interface ViewContext {
  /** Aborted when the view is unmounted: pass it to fetches and check it after every await. */
  signal: AbortSignal;
  /** Sets `document.title` ("<title> — MythLab"; empty = the app name). */
  setTitle(title: string): void;
}

/**
 * A view module. The router calls `mount` when the route's path changes and `update` (when present) when only
 * the query changed; without `update` the view is unmounted and mounted again.
 * `mount` renders into `el` (the `<main id="view">` content box) and may return before its data has loaded.
 */
export interface ViewModule {
  mount(el: HTMLElement, route: Route, ctx: ViewContext): void | Promise<void>;
  unmount?(): void;
  update?(route: Route): void;
}

// ---------------------------------------------------------------- stored data (localStorage)

/**
 * One entry of `mythlab.progress` (key "<source>|<key>"). The first block is the legacy shape and must keep its
 * meaning; the optional fields are additive (old clients ignore them).
 */
export interface Progress {
  source: string;
  key: string;
  name: string;
  poster: string | null;
  cover: string | null;
  cover_sha: string | null;
  author: string | null;
  /** At most 3. */
  genres: string[];
  group: string | null;
  /** 0-based chapter index. */
  idx: number;
  /** Chapter number as displayed. */
  n: number;
  /** Chapter count of the story when saved. */
  total: number;
  /** Paragraph index inside the chapter. */
  para: number;
  /** Epoch ms of the last update. */
  ts: number;
  // additive
  /** Chapter file name: survives re-ordering of the chapter list (preferred over `idx` when present). */
  file?: string;
  /** Fraction (0..1) of the paragraph `para` scrolled past, for sub-paragraph restore. */
  frac?: number;
  /** Highest chapter index ever opened (drives the read/unread state of chapter lists). */
  maxIdx?: number;
  /** Listening position {idx, para} when the player was last used on this story. */
  listen?: { idx: number; para: number; file?: string };
  /** Chapter title for shelves ("Chương 6: …"). */
  title?: string;
}

/** One entry of `mythlab.bookmarks` (array, newest first). */
export interface Bookmark {
  id: string;
  source: string;
  key: string;
  /** Story name. */
  name: string;
  idx: number;
  n: number;
  file: string;
  /** Chapter title as displayed. */
  title: string;
  para: number;
  /** First ~160 characters of the bookmarked paragraph. */
  excerpt: string;
  ts: number;
}

/** One entry of `mythlab.follows` (array, newest first). */
export interface Follow {
  source: string;
  key: string;
  name: string;
  author: string | null;
  poster: string | null;
  cover: string | null;
  cover_sha: string | null;
  group: string | null;
  ts: number;
}

// ---------------------------------------------------------------- player (W2)

export interface PlayRequest {
  source: string;
  key: string;
  /** 0-based chapter index. */
  idx: number;
  /** Paragraph to start from (default 0; -1 = the chapter title). */
  para?: number;
  /** Story detail when the caller already has it (saves a request). */
  story?: StoryDetail;
}

export interface PlayerState {
  status: 'idle' | 'loading' | 'playing' | 'paused' | 'error';
  source?: string;
  key?: string;
  idx?: number;
  /** Paragraph being read (-1 = title). */
  para?: number;
  storyName?: string;
  chapterTitle?: string;
  engine?: 'native' | 'piper';
  error?: string;
}

/**
 * The text-to-speech player. It owns `#player-dock` (rendered empty by the shell) and sets the CSS variable
 * `--player-h` on `<html>` to the dock's real height (0px when hidden) so the page pads itself.
 * It also emits the app event "player" with every state change.
 */
export interface PlayerApi {
  /** Starts reading a chapter aloud (replaces whatever is playing). Rejects only on programming errors. */
  play(req: PlayRequest): Promise<void>;
  /** Play/pause the current item; no-op when idle. */
  toggle(): void;
  pause(): void;
  resume(): void;
  /** Stops and hides the dock. */
  stop(): void;
  getState(): PlayerState;
  onState(fn: (s: PlayerState) => void): () => void;
  /** True when the player is on this story (and chapter, when `idx` is given) and not idle. */
  matches(source: string, key: string, idx?: number): boolean;
}

// ---------------------------------------------------------------- settings panel (W3)

export type SettingsTab = 'theme' | 'font' | 'layout' | 'voice' | 'source' | 'account' | 'app';

export interface SettingsPanelApi {
  /** Opens the panel (modal sheet), optionally on a tab. */
  open(tab?: SettingsTab): void;
  close(): void;
  isOpen(): boolean;
}

// ---------------------------------------------------------------- offline (W3)

export interface DownloadProgress {
  done: number;
  total: number;
  /** Chapters that failed so far. */
  failed: number;
  /** Reason of the most recent failure (for diagnosis). */
  lastError?: string;
}

export interface DownloadOptions {
  /** 0-based inclusive chapter range; default the whole story. */
  from?: number;
  to?: number;
  signal?: AbortSignal;
  onProgress?(p: DownloadProgress): void;
  /** Chapter list when the caller already has it. */
  chapters?: ChapterRef[];
}

export interface OfflineApi {
  /** True when chapters can be stored for offline reading on this host. */
  isAvailable(): boolean;
  /** Stores the chapters of a story for offline reading; resolves with the final counts. */
  downloadStory(source: string, key: string, opts?: DownloadOptions): Promise<DownloadProgress>;
  /** How many chapters of a story are stored. */
  storyStatus(source: string, key: string): Promise<{ chapters: number }>;
  /** Bytes used / available (0 when the browser does not say). */
  usage(): Promise<{ used: number; quota: number }>;
  /** Clears every cache layer (chapters, covers, audio, GitHub cache). Settings and progress are kept. */
  clear(): Promise<void>;
}

// ---------------------------------------------------------------- PWA (W3)

export interface PwaApi {
  /** Registers the service worker when the host supports it. Never throws. */
  init(): void;
  /** True when an install prompt can be shown now. */
  installAvailable(): boolean;
  /** Shows the install prompt; resolves true when the app was installed. */
  install(): Promise<boolean>;
  onInstallChange(fn: (available: boolean) => void): () => void;
  /** True when running as an installed app (standalone display mode, Capacitor or desktop shell). */
  standalone(): boolean;
}

// ---------------------------------------------------------------- app events (core/events.ts)

export interface ToastOptions {
  message: string;
  kind?: 'info' | 'ok' | 'error';
  /** ms; default 3200 (6000 with an action). */
  duration?: number;
  action?: { label: string; run(): void };
}

export interface AppEvents {
  /** Show a toast (any module may emit; core/ui.ts renders). */
  toast: ToastOptions;
  /** After the router mounted or updated a view. */
  route: Route;
  /** A setting changed (`key` null = several / reset). Emitted after CSS variables were applied. */
  settings: { key: string | null };
  /** Reading progress changed (`key` = "<source>|<key>", null = several). */
  progress: { key: string | null };
  bookmarks: { id: string | null };
  follows: { key: string | null };
  /** The data source was (re)selected; views should reload. */
  backend: { kind: 'none' | 'server' | 'github' };
  /** Mirror of PlayerApi.onState. */
  player: PlayerState;
  /** navigator.onLine changed. */
  online: boolean;
  /** The Google session changed (signed in, signed out, token rejected, profile refreshed). */
  auth: { signedIn: boolean };
}
