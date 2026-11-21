/**
 * PWA glue: service worker registration and the update flow, the install prompt, the offline indicator and the
 * `color-scheme` / `theme-color` metas.
 *
 * Update flow: a new worker installs in the background and waits. When the page already runs the build that
 * worker serves (first visit after a deploy, or the upgrade from the old app's worker v3, which let the new page
 * through from the network) it is activated at once and nothing reloads. Otherwise the toast
 * "Có bản mới" offers "Tải lại": only then does the new worker take over, and the page reloads once.
 *
 * No service worker inside Capacitor (the files are local), outside http(s), or under `astro dev`.
 */
import type { PwaApi } from './core/contracts';
import { Emitter, on } from './core/events';
import { append, html } from './core/html';
import { icon } from './core/icons';
import { isNative, scheme, syncThemeColor } from './core/settings';
import { store } from './core/store';
import { toast } from './core/ui';
import type { SwActivated, SwRequest, SwVersion } from '../sw/shared';

interface InstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

const HINT_KEY = 'mythlab.installHint';

let deferred: InstallPromptEvent | null = null;
let started = false;
const installChanges = new Emitter<boolean>();
const updateChanges = new Emitter<boolean>();

let registration: ServiceWorkerRegistration | null = null;
/** A waiting worker that serves another build than the one on screen. */
let pending: ServiceWorker | null = null;
/** Another tab activated a new build: a plain reload brings this tab up to date. */
let stale = false;
let reloading = false;
let lastCheck = 0;

/** True when a service worker can be used on this host. */
export function swSupported(): boolean {
  try {
    return !isNative() && /^https?:$/.test(location.protocol) && 'serviceWorker' in navigator && !import.meta.env.DEV;
  } catch {
    return false;
  }
}

/** The hashed files (`_astro/…`) the current document loaded, relative to the app root. */
export function pageAssets(doc: Document = document): string[] {
  const root = new URL('./', doc.baseURI).href;
  const urls = [
    ...[...doc.querySelectorAll<HTMLScriptElement>('script[src]')].map((s) => s.src),
    ...[...doc.querySelectorAll<HTMLLinkElement>('link[rel~="stylesheet"][href]')].map((l) => l.href),
  ];
  const out = new Set<string>();
  for (const u of urls) {
    if (!u.startsWith(root)) continue;
    const rel = u.slice(root.length).split(/[?#]/)[0] as string;
    if (rel.startsWith('_astro/')) out.add(rel);
  }
  return [...out];
}

/** True when a build (its precache list) contains everything the current document loaded. */
export function sameBuild(files: readonly string[], assets: readonly string[] = pageAssets()): boolean {
  if (!assets.length) return false;
  const have = new Set(files);
  return assets.every((a) => have.has(a));
}

/** Asks a worker which build it serves; null when it does not answer (the old worker v3 never does). */
function askVersion(worker: ServiceWorker, wait = 2000): Promise<SwVersion | null> {
  return new Promise((resolve) => {
    let done = false;
    const finish = (v: SwVersion | null): void => {
      if (done) return;
      done = true;
      resolve(v);
    };
    try {
      const ch = new MessageChannel();
      ch.port1.onmessage = (e: MessageEvent) => {
        const d = e.data as SwVersion | null;
        finish(d && typeof d.version === 'string' && Array.isArray(d.files) ? d : null);
      };
      const msg: SwRequest = { type: 'GET_VERSION' };
      worker.postMessage(msg, [ch.port2]);
    } catch {
      finish(null);
    }
    setTimeout(() => finish(null), wait);
  });
}

const skipWaiting = (worker: ServiceWorker): void => {
  const msg: SwRequest = { type: 'SKIP_WAITING' };
  worker.postMessage(msg);
};

function offerUpdate(): void {
  updateChanges.emit(true);
  toast({
    message: 'Có bản mới của MythLab.',
    duration: 20000,
    action: { label: 'Tải lại', run: applyUpdate },
  });
}

/** Activates the waiting build (if any) and reloads the page once. */
function applyUpdate(): void {
  if (reloading) return;
  const w = pending;
  if (!w) {
    reloading = true;
    location.reload();
    return;
  }
  reloading = true;
  // reload when the new worker took control; the timer covers a worker that never answers
  navigator.serviceWorker.addEventListener('controllerchange', () => location.reload(), { once: true });
  setTimeout(() => location.reload(), 3000);
  skipWaiting(w);
}

/** A worker finished installing while another one controls the page. */
async function onWaiting(worker: ServiceWorker): Promise<void> {
  if (worker === pending) return;
  const v = await askVersion(worker);
  if (worker.state !== 'installed') return;
  if (v && sameBuild(v.files)) {
    // this page is already the new build: let its worker take over quietly
    skipWaiting(worker);
    return;
  }
  pending = worker;
  offerUpdate();
}

function watch(reg: ServiceWorkerRegistration): void {
  const track = (worker: ServiceWorker | null): void => {
    if (!worker) return;
    const check = (): void => {
      // "installed" with a controller = waiting behind the active worker; without one it activates by itself
      // (a hard reload leaves the page uncontrolled although a worker is active)
      if (worker.state === 'installed' && (navigator.serviceWorker.controller || reg.active)) void onWaiting(worker);
    };
    worker.addEventListener('statechange', check);
    check();
  };
  track(reg.waiting);
  track(reg.installing);
  reg.addEventListener('updatefound', () => track(reg.installing));
}

async function register(): Promise<void> {
  try {
    navigator.serviceWorker.addEventListener('message', (e: MessageEvent) => {
      const d = e.data as SwActivated | null;
      if (!d || d.type !== 'ACTIVATED' || !Array.isArray(d.files)) return;
      pending = null;
      if (reloading || sameBuild(d.files)) {
        stale = false;
        updateChanges.emit(false);
        return;
      }
      // a newer build was activated from another tab
      stale = true;
      offerUpdate();
    });
    const reg = await navigator.serviceWorker.register('./sw.js', { scope: './', updateViaCache: 'none' });
    registration = reg;
    watch(reg);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') void checkForUpdate();
    });
  } catch (e) {
    console.warn('service worker:', e);
  }
}

/** Looks for a new build (at most every 10 minutes unless forced). Never throws. */
async function checkForUpdate(force = false): Promise<void> {
  const reg = registration;
  if (!reg) return;
  const now = Date.now();
  if (!force && now - lastCheck < 600_000) return;
  lastCheck = now;
  try {
    await reg.update();
  } catch {
    /* offline */
  }
}

// ---------------------------------------------------------------- page chrome

function mountOfflineBadge(): void {
  if (document.getElementById('st-offline')) return;
  append(document.body, html`<div id="st-offline" class="st-offline" aria-hidden="true">${icon('wifiOff')}<span>Ngoại tuyến</span></div>`);
}

/** `color-scheme` follows the theme so form controls and scrollbars match; `theme-color` follows the page. */
function syncMeta(): void {
  const meta = document.querySelector<HTMLMetaElement>('meta[name="color-scheme"]');
  const want = scheme() === 'dark' ? 'dark' : 'light';
  if (meta && meta.content !== want) meta.content = want;
  syncThemeColor();
}

function bindInstall(): void {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferred = e as InstallPromptEvent;
    installChanges.emit(true);
    if (!store.get<number>(HINT_KEY, 0)) {
      store.set(HINT_KEY, Date.now());
      toast({ message: 'Cài MythLab như một ứng dụng để mở nhanh và đọc khi không có mạng.', duration: 9000, action: { label: 'Cài đặt', run: () => void pwa.install() } });
    }
  });
  window.addEventListener('appinstalled', () => {
    deferred = null;
    installChanges.emit(false);
    toast({ message: 'Đã cài MythLab.', kind: 'ok' });
  });
}

export const pwa: PwaApi & {
  /** True when a newer build waits for a reload. */
  updateAvailable(): boolean;
  /** Switches to the newer build (reloads the page). */
  applyUpdate(): void;
  /** Asks the server for a new build now. */
  checkForUpdate(): Promise<void>;
  onUpdateChange(fn: (available: boolean) => void): () => void;
  /** True when a service worker controls this page (offline start and server-mode offline reading work). */
  controlled(): boolean;
  /** Build id and precache size of the active worker, or null. */
  version(): Promise<SwVersion | null>;
} = {
  init(): void {
    if (started) return;
    started = true;
    try {
      bindInstall();
      mountOfflineBadge();
      syncMeta();
      on('settings', syncMeta);
      on('route', () => queueMicrotask(syncMeta));
      if (swSupported()) void register();
    } catch (e) {
      console.warn('pwa:', e);
    }
  },
  installAvailable: () => !!deferred,
  async install(): Promise<boolean> {
    const ev = deferred;
    if (!ev) return false;
    deferred = null;
    installChanges.emit(false);
    try {
      await ev.prompt();
      return (await ev.userChoice).outcome === 'accepted';
    } catch {
      return false;
    }
  },
  onInstallChange: (fn) => installChanges.on(fn),
  standalone(): boolean {
    if (isNative()) return true;
    try {
      return matchMedia('(display-mode: standalone)').matches || (navigator as { standalone?: boolean }).standalone === true;
    } catch {
      return false;
    }
  },
  updateAvailable: () => !!pending || stale,
  applyUpdate,
  checkForUpdate: () => checkForUpdate(true),
  onUpdateChange: (fn) => updateChanges.on(fn),
  controlled(): boolean {
    try {
      return !!navigator.serviceWorker?.controller;
    } catch {
      return false;
    }
  },
  async version(): Promise<SwVersion | null> {
    try {
      const w = navigator.serviceWorker?.controller;
      return w ? await askVersion(w, 1500) : null;
    } catch {
      return null;
    }
  },
};
