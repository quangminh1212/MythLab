/**
 * Hash router. Route shapes are frozen (see contracts.ts `Route`); view state lives in a query string inside the
 * hash so back/forward restores filters, sorting and search text.
 */
import type { Route, ViewContext, ViewModule, ViewName } from './contracts';
import { emit } from './events';

export const APP_NAME = 'MythLab';

const enc = encodeURIComponent;
const dec = (s: string): string => {
  try {
    return decodeURIComponent(s);
  } catch {
    return s;
  }
};

function queryString(q: Record<string, string | number | null | undefined> | undefined): string {
  if (!q) return '';
  const parts: string[] = [];
  for (const k of Object.keys(q).sort()) {
    const v = q[k];
    if (v == null || v === '') continue;
    parts.push(`${enc(k)}=${enc(String(v))}`);
  }
  return parts.length ? '?' + parts.join('&') : '';
}

type Q = Record<string, string | number | null | undefined>;

/** Hash builders: the only place that knows how routes are written. */
export const href = {
  home: (): string => '#/',
  lib: (source: string, repo?: string | null, q?: Q): string => `#/lib/${enc(source)}${repo ? '/' + (repo === '*' ? '*' : enc(repo)) : ''}${queryString(q)}`,
  story: (source: string, key: string): string => `#/s/${enc(source)}/${enc(key)}`,
  read: (source: string, key: string, idx: number, q?: Q): string => `#/r/${enc(source)}/${enc(key)}/${Math.max(0, Math.trunc(idx) || 0)}${queryString(q)}`,
  search: (q?: string): string => `#/search${queryString({ q })}`,
  history: (): string => '#/history',
  bookmarks: (): string => '#/bookmarks',
  follows: (): string => '#/follows',
};

/** Parses a location hash into a Route. Unknown or malformed hashes resolve to home. */
export function parseHash(hashIn: string): Route {
  const hash = hashIn || '#/';
  const body = hash.replace(/^#\/?/, '');
  const qi = body.indexOf('?');
  const pathPart = qi < 0 ? body : body.slice(0, qi);
  const query: Record<string, string> = {};
  if (qi >= 0) {
    for (const kv of body.slice(qi + 1).split('&')) {
      if (!kv) continue;
      const i = kv.indexOf('=');
      const k = dec(i < 0 ? kv : kv.slice(0, i));
      if (k) query[k] = dec((i < 0 ? '' : kv.slice(i + 1)).replace(/\+/g, '%20'));
    }
  }
  const seg = pathPart.split('/').filter((s) => s !== '');
  const base = { query, hash, path: '#/' + pathPart.replace(/\/+$/, '') };
  const home: Route = { view: 'home', ...base };
  const head = seg[0];
  if (head === 'lib' && seg[1]) return { view: 'lib', source: dec(seg[1]), ...(seg[2] ? { repo: dec(seg[2]) } : {}), ...base };
  if (head === 's' && seg[1] && seg[2]) return { view: 'story', source: dec(seg[1]), key: dec(seg.slice(2).join('/')), ...base };
  if (head === 'r' && seg[1] && seg[2]) {
    // the key is one encoded segment; tolerate hand-written hashes with raw slashes in the key
    const last = seg[seg.length - 1] as string;
    const hasIdx = seg.length > 3 && /^\d+$/.test(last);
    const idx = hasIdx ? parseInt(last, 10) : 0;
    const key = dec(seg.slice(2, hasIdx ? -1 : undefined).join('/'));
    return { view: 'read', source: dec(seg[1]), key, idx: Number.isSafeInteger(idx) ? idx : 0, ...base };
  }
  if (head === 'search') return { view: 'search', ...base };
  if (head === 'history') return { view: 'history', ...base };
  if (head === 'bookmarks') return { view: 'bookmarks', ...base };
  if (head === 'follows') return { view: 'follows', ...base };
  return home;
}

type Loader = () => Promise<ViewModule>;

interface RouterOptions {
  /** The element views render into. */
  outlet: HTMLElement;
  /** View loaders by name (dynamic imports keep the entry small). */
  views: Record<ViewName, Loader>;
  /** Replaces the route before mounting (e.g. home → onboarding when no data source is configured). */
  resolve?(route: Route): Loader | null;
  /** Rendered into the outlet when a view module fails to load or throws while mounting. */
  onError(el: HTMLElement, error: unknown, route: Route): void;
  /** Skeleton shown while a view module is loading. */
  onLoading?(el: HTMLElement, route: Route): void;
}

let opt: RouterOptions | null = null;
let current: { route: Route; mod: ViewModule | null; ctl: AbortController; loader: Loader } | null = null;
let seq = 0;
/** Scroll positions by hash, for back/forward. */
const scrollPos = new Map<string, number>();
/** True when the next hashchange comes from a link click or navigate() (a new navigation → scroll to top). */
let fresh = false;
let lastHash = '';

export function setTitle(title: string): void {
  document.title = title ? `${title} — ${APP_NAME}` : `${APP_NAME} — Đọc & nghe truyện`;
}

function unmount(): void {
  if (!current) return;
  const c = current;
  current = null;
  c.ctl.abort();
  try {
    c.mod?.unmount?.();
  } catch (e) {
    console.error(e);
  }
}

async function run(): Promise<void> {
  const o = opt;
  if (!o) return;
  const route = parseHash(location.hash);
  const isNew = fresh;
  fresh = false;
  if (lastHash) scrollPos.set(lastHash, window.scrollY);
  lastHash = route.hash;
  const loader = o.resolve?.(route) || o.views[route.view];

  // only the query changed: let the view update itself
  if (current && current.mod && current.loader === loader && current.route.path === route.path && current.mod.update) {
    current.route = route;
    try {
      current.mod.update(route);
    } catch (e) {
      console.error(e);
    }
    emit('route', route);
    return;
  }

  const my = ++seq;
  unmount();
  const ctl = new AbortController();
  current = { route, mod: null, ctl, loader };
  document.body.dataset.view = route.view;
  document.body.classList.toggle('view-read', route.view === 'read');
  setTitle('');
  const el = o.outlet;
  let mod: ViewModule;
  try {
    const pending = loader();
    // show a skeleton only when the chunk is not instant
    const t = setTimeout(() => {
      if (my === seq) o.onLoading?.(el, route);
    }, 120);
    mod = await pending;
    clearTimeout(t);
  } catch (e) {
    if (my === seq) o.onError(el, e, route);
    return;
  }
  if (my !== seq) return;
  current.mod = mod;
  el.replaceChildren();
  const ctx: ViewContext = { signal: ctl.signal, setTitle };
  const restore = isNew ? 0 : (scrollPos.get(route.hash) ?? 0);
  try {
    const p = mod.mount(el, route, ctx);
    if (route.view !== 'read') {
      window.scrollTo(0, restore);
      // content arrives asynchronously: try again once it had time to render
      if (restore > 0 && p instanceof Promise) void p.then(() => my === seq && requestAnimationFrame(() => window.scrollTo(0, restore)));
    }
    emit('route', route);
    await p;
  } catch (e) {
    if (my === seq && !ctl.signal.aborted) o.onError(el, e, route);
  }
}

/** Goes to a hash (a new history entry unless `replace`). */
export function navigate(hash: string, { replace = false }: { replace?: boolean } = {}): void {
  if (hash === location.hash) {
    void run();
    return;
  }
  fresh = true;
  if (replace) {
    history.replaceState(history.state, '', hash);
    void run();
  } else {
    location.hash = hash;
  }
}

/** Updates the query of the current route (null/'' removes a key). Replaces the history entry by default. */
export function setQuery(patch: Q, { replace = true }: { replace?: boolean } = {}): void {
  const r = currentRoute();
  const q: Q = { ...r.query, ...patch };
  const hash = r.path + queryString(q);
  if (hash === location.hash) return;
  if (replace) {
    history.replaceState(history.state, '', hash);
    void run();
  } else {
    fresh = false;
    location.hash = hash;
  }
}

export const currentRoute = (): Route => current?.route ?? parseHash(location.hash);

/** Re-mounts the current view (after the data source changed, or "Thử lại"). */
export function reload(): void {
  unmount();
  void run();
}

/** Starts the router. Call once. */
export function start(options: RouterOptions): void {
  opt = options;
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  window.addEventListener('hashchange', () => void run());
  // links inside the app are new navigations (scroll to top); back/forward restores the position
  document.addEventListener(
    'click',
    (e) => {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      const a = (e.target as Element | null)?.closest?.('a[href^="#/"]');
      if (a && a.getAttribute('href') !== location.hash) fresh = true;
    },
    true,
  );
  void run();
}

export const router = { start, navigate, setQuery, reload, currentRoute, parseHash, href, setTitle };
