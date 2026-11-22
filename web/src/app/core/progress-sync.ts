/**
 * Reading-progress sync with the MythLab server (`/api/progress`, advertised as feature "progress" by /api/ping).
 * Runs only against a server backend that lists the feature; GitHub-direct and the Python server never sync.
 *
 *   pull  GET ?since=<cursor>: on start, when the page becomes visible, when the network or the Android app comes
 *         back, and every 60 s while visible. Entries are applied without being sent back (progress.applyRemote).
 *   push  PUT the entries in the outbox (ids persisted in localStorage, so nothing is lost on reload): at once for
 *         a new chapter or a deletion, at most every 15 s for a moving position, and with `keepalive` on pagehide.
 *   clock the server answers with its clock; the difference is added to outgoing timestamps and removed from
 *         incoming ones, so a device with a wrong clock does not win or lose merges it should not.
 *   fail  401/403 stop syncing (wrong key), 404/405 switch it off (old server); other errors back off 5 s .. 5 min.
 *   user  signed in with Google: requests carry the session token (backend layer), the server then uses the
 *         per-account store, so no access key is needed. The outbox and the cursor are kept per account, so a
 *         device switching accounts never sends one account's pending changes to another; the first sync of an
 *         account (no cursor yet) sends everything this device has.
 * Entries whose source the server does not list (other servers have other source ids) are neither sent nor applied.
 */
import { accountId } from './auth-token';
import { backend } from './backend';
import type { Progress } from './contracts';
import { on } from './events';
import { sKey } from './format';
import { progress, TOMB_AGE } from './progress';
import { store } from './store';
import { syncStatus } from './sync-status';

export const OUTBOX_KEY = 'mythlab.progress.outbox';
export const CURSOR_KEY = 'mythlab.progress.cursor';

export const PULL_EVERY = 60_000;
export const PUSH_POSITION_EVERY = 15_000;
const PUSH_DELAY = 1_500;
const BACKOFF_MIN = 5_000;
const BACKOFF_MAX = 300_000;
const BATCH = 100;
const BEACON_MAX = 20;
const SOURCES_TTL = 10 * 60_000;

interface WireBody {
  entries: unknown[];
  now: number;
}
interface Item {
  id: string;
  ts: number;
  entry: Record<string, unknown>;
}

let running = false;
let disabled = false;
let bound = false;
let skew = 0;
let failures = 0;
let sources: { at: number; ids: Set<string> } | null = null;
let chain: Promise<void> = Promise.resolve();
let pushTimer: ReturnType<typeof setTimeout> | undefined;
let pullTimer: ReturnType<typeof setInterval> | undefined;
let retryTimer: ReturnType<typeof setTimeout> | undefined;
let offLocal: (() => void) | undefined;
let lastPushAt = 0;
const lastSentIdx = new Map<string, number>();

const visible = (): boolean => document.visibilityState !== 'hidden';
const online = (): boolean => navigator.onLine !== false;

function splitId(id: string): [string, string] {
  const i = id.indexOf('|');
  return [id.slice(0, i), id.slice(i + 1)];
}

/** Storage key of the signed-in account's state; the anonymous (access-key) state keeps the original name. */
const scoped = (key: string): string => {
  const id = accountId(backend.serverBase ?? '');
  return id ? `${key}.${id}` : key;
};

function readOutbox(): Set<string> {
  const v = store.get<unknown>(scoped(OUTBOX_KEY), []);
  return new Set(Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : []);
}
function writeOutbox(s: Set<string>): void {
  if (s.size) store.set(scoped(OUTBOX_KEY), [...s]);
  else store.del(scoped(OUTBOX_KEY));
}

function readCursor(): number | null {
  const c = store.get<{ base?: string; since?: number } | null>(scoped(CURSOR_KEY), null);
  return c && c.base === (backend.serverBase ?? '') && typeof c.since === 'number' ? c.since : null;
}
const writeCursor = (since: number): void => void store.set(scoped(CURSOR_KEY), { base: backend.serverBase ?? '', since });

/**
 * Is syncing possible with the active backend? A server that lists "progress" syncs for the access key (or an open
 * server) and, when signed in with Google, for the account: the token replaces the key.
 */
export function supported(): boolean {
  return backend.kind === 'server' && backend.features.includes('progress');
}

async function knownSources(): Promise<Set<string>> {
  if (sources && Date.now() - sources.at < SOURCES_TTL) return sources.ids;
  const r = await backend.get<{ sources?: { id: string }[] }>('/sources', { timeout: 20_000 });
  sources = { at: Date.now(), ids: new Set((r.sources ?? []).map((s) => s.id)) };
  return sources.ids;
}

const wire = (p: Progress): Record<string, unknown> => ({ ...p, ts: p.ts + skew });

/** The entries to send for outbox ids: live progress, or the pending deletion; unknown sources are dropped. */
function outgoing(ids: Iterable<string>, known: Set<string>): Item[] {
  const out: Item[] = [];
  const min = Date.now() - TOMB_AGE;
  for (const id of ids) {
    const [source, key] = splitId(id);
    if (!source || !key || !known.has(source)) continue;
    const p = progress.get(source, key);
    if (p) {
      out.push({ id, ts: p.ts, entry: wire(p) });
      continue;
    }
    const t = progress.tombstone(id);
    if (t !== undefined && t > min) out.push({ id, ts: t, entry: { source, key, ts: t + skew, deleted: true } });
  }
  return out;
}

/** The ts this device holds for an id now (live entry or deletion), to tell whether it changed after sending. */
const currentTs = (id: string): number | undefined => {
  const [s, k] = splitId(id);
  return progress.get(s, k)?.ts ?? progress.tombstone(id);
};

function fail(e: unknown): void {
  const status = (e as { status?: number } | null)?.status ?? 0;
  syncStatus.fail('progress');
  if (status === 401 || status === 403) {
    stop(); // wrong or revoked key: stay quiet until the backend is chosen again
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

async function pullOnce(): Promise<void> {
  const known = await knownSources();
  let cursor = readCursor();
  if (cursor === null) {
    // first sync with this server: send everything this device has
    const box = readOutbox();
    for (const p of progress.all()) box.add(sKey(p.source, p.key));
    writeOutbox(box);
    cursor = 0;
  }
  const t0 = Date.now();
  const r = await backend.get<WireBody>('/progress?since=' + cursor, { timeout: 20_000 });
  measureSkew(t0, Date.now(), r.now);
  const list = Array.isArray(r.entries) ? r.entries : [];
  progress.applyRemote(
    list.filter((e) => known.has((e as { source?: string } | null)?.source ?? '')),
    skew,
  );
  if (typeof r.now === 'number') writeCursor(Math.max(0, r.now - 1000));
}

async function pushOnce(): Promise<void> {
  const box = readOutbox();
  if (!box.size) return;
  const known = await knownSources();
  const items = outgoing(box, known);
  // ids with nothing to send (another server's story, entry gone without a deletion) must not pile up
  const sendable = new Set(items.map((x) => x.id));
  const rest = new Set([...box].filter((id) => sendable.has(id)));
  writeOutbox(rest);
  for (let i = 0; i < items.length; i += BATCH) {
    const part = items.slice(i, i + BATCH);
    const t0 = Date.now();
    const r = await backend.send<WireBody>('PUT', '/progress', { entries: part.map((x) => x.entry) }, { timeout: 20_000 });
    measureSkew(t0, Date.now(), r.now);
    lastPushAt = Date.now();
    const cur = readOutbox();
    for (const x of part) {
      if (currentTs(x.id) === x.ts) cur.delete(x.id); // else it changed in flight: stays queued
      const p = progress.get(...splitId(x.id));
      if (p) lastSentIdx.set(x.id, p.idx);
    }
    writeOutbox(cur);
    progress.applyRemote(Array.isArray(r.entries) ? r.entries : [], skew);
  }
}

/** Runs `job` after the previous one, only while syncing is possible. Never rejects. */
function enqueue(job: () => Promise<void>): Promise<void> {
  chain = chain.then(async () => {
    if (!running || disabled || !supported() || !online()) return;
    syncStatus.start('progress');
    try {
      await job();
      failures = 0;
      syncStatus.ok('progress');
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

function schedulePush(urgent: boolean): void {
  if (pushTimer !== undefined) {
    if (!urgent) return; // a push is already due
    clearTimeout(pushTimer);
  }
  const wait = urgent ? PUSH_DELAY : Math.max(PUSH_DELAY, PUSH_POSITION_EVERY - (Date.now() - lastPushAt));
  pushTimer = setTimeout(() => {
    pushTimer = undefined;
    void push();
  }, wait);
}

function onLocal(id: string, deleted: boolean): void {
  if (!running) return;
  const box = readOutbox();
  box.add(id);
  writeOutbox(box);
  const p = deleted ? null : progress.get(...splitId(id));
  schedulePush(deleted || !p || lastSentIdx.get(id) !== p.idx);
}

/** Last-chance send while the page goes away: a few recent entries with `keepalive`. */
function beacon(): void {
  if (!running || disabled || !supported() || !sources) return;
  const box = readOutbox();
  if (!box.size) return;
  const items = outgoing(box, sources.ids).slice(0, BEACON_MAX);
  const body = { entries: items.map((x) => x.entry) };
  if (!items.length || JSON.stringify(body).length > 60_000) return;
  backend.send('PUT', '/progress', body, { keepalive: true, timeout: 0 }).then(
    () => {
      const cur = readOutbox();
      for (const x of items) if (currentTs(x.id) === x.ts) cur.delete(x.id);
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
  on('auth', () => void init()); // another account (or none) has its own outbox and cursor
}

/** Starts or stops syncing for the backend that is active now. Called by main.ts; runs again when the backend changes. */
export async function init(): Promise<void> {
  bindOnce();
  await backend.init();
  stop();
  disabled = false;
  failures = 0;
  sources = null;
  if (!supported()) {
    syncStatus.reset('progress');
    return;
  }
  running = true;
  progress.init();
  offLocal = progress.onLocalChange(onLocal);
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
  sources = null;
  chain = Promise.resolve();
  lastPushAt = 0;
  lastSentIdx.clear();
}

export const progressSync = { init, stop, sync, supported, _reset };
