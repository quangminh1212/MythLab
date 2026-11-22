/**
 * Sync of followed stories ("truyện yêu thích") and bookmarks with the signed-in account (`/api/library`,
 * advertised as feature "library" by /api/ping). It mirrors `progress-sync.ts` and runs only while a Google session
 * is active; there is no anonymous mode.
 *
 *   entry {kind: 'follow' | 'bookmark', id, ts, deleted?, data?}; follow id = "<source>|<key>", bookmark id = the
 *         bookmark id; `data` is the object stored in localStorage (`ts` inside it = the entry ts).
 *   pull  GET ?since=<cursor> on start, when the page becomes visible, when the network comes back, every 60 s.
 *   push  PUT the outbox (ids "<kind>|<id>" persisted per account) soon after a change, with `keepalive` on pagehide.
 *   merge last writer wins by `ts`; a tie keeps the live entry; deletions are tombstones kept 60 days (library.ts).
 *   clock the server's `now` gives a skew that is added to outgoing and removed from incoming timestamps.
 *   fail  401/403 stop (the backend layer already signed out on 401), 404/405 switch off; others back off 5 s .. 5 min.
 * The first sync of an account (no cursor) sends every follow, bookmark and tombstone of this device: nothing local is
 * deleted by signing in, and what the account holds is merged down.
 */
import { accountId } from './auth-token';
import { backend } from './backend';
import { on } from './events';
import { LIB_TOMB_AGE, library, type LibKind } from './library';
import { store } from './store';
import { syncStatus } from './sync-status';

export const LIB_OUTBOX_KEY = 'mythlab.library.outbox';
export const LIB_CURSOR_KEY = 'mythlab.library.cursor';

export const PULL_EVERY = 60_000;
const PUSH_DELAY = 1_500;
const BACKOFF_MIN = 5_000;
const BACKOFF_MAX = 300_000;
const BATCH = 100;
const BEACON_MAX = 20;
/** The server refuses bigger `data`; such an entry is not sent. */
const MAX_DATA_BYTES = 4096;

interface WireBody {
  entries: unknown[];
  now: number;
}
interface Item {
  ref: string;
  ts: number;
  entry: Record<string, unknown>;
}

let running = false;
let disabled = false;
let bound = false;
let skew = 0;
let failures = 0;
let chain: Promise<void> = Promise.resolve();
let pushTimer: ReturnType<typeof setTimeout> | undefined;
let pullTimer: ReturnType<typeof setInterval> | undefined;
let retryTimer: ReturnType<typeof setTimeout> | undefined;
let offLocal: (() => void) | undefined;

const visible = (): boolean => document.visibilityState !== 'hidden';
const online = (): boolean => navigator.onLine !== false;
const base = (): string => backend.serverBase ?? '';
const account = (): string => accountId(base());

const ref = (kind: LibKind, id: string): string => `${kind}|${id}`;
function splitRef(r: string): [LibKind, string] {
  const i = r.indexOf('|');
  return [r.slice(0, i) as LibKind, r.slice(i + 1)];
}
const scoped = (key: string): string => `${key}.${account()}`;

function readOutbox(): Set<string> {
  const v = store.get<unknown>(scoped(LIB_OUTBOX_KEY), []);
  return new Set(Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string' && /^(follow|bookmark)\|./.test(x)) : []);
}
function writeOutbox(s: Set<string>): void {
  if (s.size) store.set(scoped(LIB_OUTBOX_KEY), [...s]);
  else store.del(scoped(LIB_OUTBOX_KEY));
}

function readCursor(): number | null {
  const c = store.get<{ base?: string; since?: number } | null>(scoped(LIB_CURSOR_KEY), null);
  return c && c.base === base() && typeof c.since === 'number' ? c.since : null;
}
const writeCursor = (since: number): void => void store.set(scoped(LIB_CURSOR_KEY), { base: base(), since });

/** Is syncing possible: a server that lists "library" and a Google session on it. */
export function supported(): boolean {
  return backend.kind === 'server' && backend.features.includes('library') && account() !== '';
}

/** The entry for an outbox ref: the live object, or the pending deletion; null when there is nothing to send. */
function build(r: string): Item | null {
  const [kind, id] = splitRef(r);
  const mine = library.libraryItems(kind).find((x) => x.id === id);
  if (mine) {
    const data = { ...mine.obj, ts: mine.ts + skew };
    if (JSON.stringify(data).length > MAX_DATA_BYTES) return null;
    return { ref: r, ts: mine.ts, entry: { kind, id, ts: mine.ts + skew, data } };
  }
  const t = library.tombstone(kind, id);
  if (t !== undefined && t > Date.now() - LIB_TOMB_AGE) return { ref: r, ts: t, entry: { kind, id, ts: t + skew, deleted: true } };
  return null;
}

/** The ts this device holds for a ref now (live entry or deletion), to tell whether it changed after sending. */
function currentTs(r: string): number | undefined {
  const [kind, id] = splitRef(r);
  return library.libraryItems(kind).find((x) => x.id === id)?.ts ?? library.tombstone(kind, id);
}

function fail(e: unknown): void {
  const status = (e as { status?: number } | null)?.status ?? 0;
  syncStatus.fail('library');
  if (status === 401 || status === 403) {
    stop();
    return;
  }
  if (status === 404 || status === 405 || status === 501) {
    disabled = true;
    stop();
    return;
  }
  failures++;
  clearTimeout(retryTimer);
  retryTimer = setTimeout(() => void sync(), Math.min(BACKOFF_MAX, BACKOFF_MIN * 2 ** (failures - 1)));
}

function measureSkew(t0: number, t1: number, now: unknown): void {
  if (typeof now === 'number' && Number.isFinite(now)) skew = Math.round(now - (t0 + t1) / 2);
}

function applyAll(entries: unknown): void {
  const list = Array.isArray(entries) ? entries : [];
  library.applyRemote('follow', list, skew);
  library.applyRemote('bookmark', list, skew);
}

async function pullOnce(): Promise<void> {
  let cursor = readCursor();
  if (cursor === null) {
    // first sync of this account on this device: send everything, then merge what the account holds
    const box = readOutbox();
    for (const kind of ['follow', 'bookmark'] as const) {
      for (const x of library.libraryItems(kind)) box.add(ref(kind, x.id));
      for (const id of library.tombstoneIds(kind)) box.add(ref(kind, id));
    }
    writeOutbox(box);
    cursor = 0;
  }
  const t0 = Date.now();
  const r = await backend.get<WireBody>('/library?since=' + cursor, { timeout: 20_000 });
  measureSkew(t0, Date.now(), r.now);
  applyAll(r.entries);
  if (typeof r.now === 'number') writeCursor(Math.max(0, r.now - 1000));
}

async function pushOnce(): Promise<void> {
  const box = readOutbox();
  if (!box.size) return;
  const items: Item[] = [];
  for (const r of box) {
    const it = build(r);
    if (it) items.push(it);
  }
  // refs with nothing to send (entry gone without a deletion, oversized) must not pile up
  const sendable = new Set(items.map((x) => x.ref));
  writeOutbox(new Set([...box].filter((r) => sendable.has(r))));
  for (let i = 0; i < items.length; i += BATCH) {
    const part = items.slice(i, i + BATCH);
    const t0 = Date.now();
    const r = await backend.send<WireBody>('PUT', '/library', { entries: part.map((x) => x.entry) }, { timeout: 20_000 });
    measureSkew(t0, Date.now(), r.now);
    const cur = readOutbox();
    for (const x of part) if (currentTs(x.ref) === x.ts) cur.delete(x.ref); // else it changed in flight: stays queued
    writeOutbox(cur);
    applyAll(r.entries);
  }
}

/** Runs `job` after the previous one, only while syncing is possible. Never rejects. */
function enqueue(job: () => Promise<void>): Promise<void> {
  chain = chain.then(async () => {
    if (!running || disabled || !supported() || !online()) return;
    syncStatus.start('library');
    try {
      await job();
      failures = 0;
      syncStatus.ok('library');
    } catch (e) {
      fail(e);
    }
  });
  return chain;
}

/** Pull, then push. */
export const sync = (): Promise<void> =>
  enqueue(async () => {
    await pullOnce();
    await pushOnce();
  });

const push = (): Promise<void> => enqueue(pushOnce);

function schedulePush(): void {
  if (pushTimer !== undefined) clearTimeout(pushTimer);
  pushTimer = setTimeout(() => {
    pushTimer = undefined;
    void push();
  }, PUSH_DELAY);
}

function onLocal(kind: LibKind, id: string): void {
  if (!running) return;
  const box = readOutbox();
  box.add(ref(kind, id));
  writeOutbox(box);
  schedulePush();
}

/** Last-chance send while the page goes away: a few recent entries with `keepalive`. */
function beacon(): void {
  if (!running || disabled || !supported()) return;
  const box = readOutbox();
  if (!box.size) return;
  const items = [...box].map(build).filter((x): x is Item => x !== null).slice(0, BEACON_MAX);
  const body = { entries: items.map((x) => x.entry) };
  if (!items.length || JSON.stringify(body).length > 60_000) return;
  backend.send('PUT', '/library', body, { keepalive: true, timeout: 0 }).then(
    () => {
      const cur = readOutbox();
      for (const x of items) if (currentTs(x.ref) === x.ts) cur.delete(x.ref);
      writeOutbox(cur);
    },
    () => {},
  );
}

interface AppPlugin {
  addListener(name: 'appStateChange', cb: (e: { isActive?: boolean }) => void): unknown;
}

function bindOnce(): void {
  if (bound) return;
  bound = true;
  document.addEventListener('visibilitychange', () => {
    if (visible()) void sync();
    else beacon();
  });
  window.addEventListener('online', () => {
    failures = 0;
    void sync();
  });
  window.addEventListener('pagehide', beacon);
  try {
    const app = (globalThis as { Capacitor?: { Plugins?: { App?: AppPlugin } } }).Capacitor?.Plugins?.App;
    app?.addListener('appStateChange', (e) => (e.isActive ? void sync() : beacon()));
  } catch {
    /* no native shell */
  }
  on('backend', () => void init());
  on('auth', () => void init());
}

/** Starts or stops syncing for the backend and account that are active now. Called by main.ts; runs again on change. */
export async function init(): Promise<void> {
  bindOnce();
  await backend.init();
  stop();
  disabled = false;
  failures = 0;
  library.init();
  if (!supported()) {
    syncStatus.reset('library');
    return;
  }
  running = true;
  offLocal = library.onLocalChange(onLocal);
  pullTimer = setInterval(() => {
    if (visible()) void sync();
  }, PULL_EVERY);
  void sync();
}

/** Stops timers and listeners (the outbox stays for the next start). */
export function stop(): void {
  running = false;
  clearTimeout(pushTimer);
  clearTimeout(retryTimer);
  clearInterval(pullTimer);
  pushTimer = retryTimer = undefined;
  pullTimer = undefined;
  offLocal?.();
  offLocal = undefined;
}

/** Test hook. */
export function _reset(): void {
  stop();
  disabled = false;
  skew = 0;
  failures = 0;
  chain = Promise.resolve();
}

export const librarySync = { init, stop, sync, supported, _reset };
