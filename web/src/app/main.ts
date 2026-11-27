/**
 * App entry: applies the settings, wires the shell, chooses the data source and starts the router.
 * Views, the player, the settings panel, the offline module and the PWA glue are loaded on demand so this
 * entry stays small.
 */
import { backend } from './core/backend/index';
import { data } from './core/data';
import { initSecret } from './core/secret';
import type { Route, ViewModule, ViewName } from './core/contracts';
import { emit, on } from './core/events';
import { html, render } from './core/html';
import { library } from './core/library';
import { progress } from './core/progress';
import { progressSync } from './core/progress-sync';
import { auth } from './core/auth';
import { librarySync } from './core/library-sync';
import { init as initBackNav } from './core/backnav';
import { router } from './core/router';
import { settings } from './core/settings';
import { bindToasts, showError, skeleton, toast } from './core/ui';
import { shell } from './shell';
import { appUpdate } from './core/app-update';

declare global {
  interface Window {
    __mlBooted?: boolean;
    __mlBootTimer?: ReturnType<typeof setTimeout>;
    __mlBootFail?: () => void;
  }
}

type Loader = () => Promise<ViewModule>;

const views: Record<ViewName, Loader> = {
  home: () => import('./views/home'),
  lib: () => import('./views/library'),
  story: () => import('./views/story'),
  read: () => import('./views/reader'),
  search: () => import('./views/search'),
  history: () => import('./views/history'),
  bookmarks: () => import('./views/bookmarks'),
};
const onboarding: Loader = () => import('./views/onboarding');
/** Views that need a story source; history and bookmarks work from what is stored on the device. */
const NEEDS_SOURCE: ReadonlySet<ViewName> = new Set<ViewName>(['home', 'lib', 'story', 'read', 'search']);

function loadingView(el: HTMLElement, route: Route): void {
  const inner =
    route.view === 'story'
      ? html`${skeleton.story()}${skeleton.rows(8)}`
      : route.view === 'history' || route.view === 'bookmarks'
        ? skeleton.rows(8)
        : route.view === 'read'
          ? skeleton.lines(12)
          : skeleton.cards(12);
  render(el, html`<div class="page">${skeleton.view(inner)}</div>`);
}

/** Android app: a check at launch, again when the app returns to the foreground (spaced out); a dialog offers each new version once. */
async function announceUpdate(): Promise<void> {
  if (!appUpdate.available()) return;
  const s = await appUpdate.check();
  if (s.kind !== 'available' || !appUpdate.firstSight(s.latest.versionCode)) return;
  void import('./settings/update-dialog').then((m) => m.openUpdateDialog());
}

function watchUpdates(): void {
  if (!appUpdate.available()) return;
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState !== 'visible') return;
    appUpdate.resumeInstall();
    void appUpdate.checkIfDue().then((s) => {
      if (s.kind === 'available' && appUpdate.firstSight(s.latest.versionCode)) void import('./settings/update-dialog').then((m) => m.openUpdateDialog());
    });
  });
}

async function boot(): Promise<void> {
  settings.init();
  bindToasts();
  progress.init();
  void progressSync.init(); // waits for the backend; syncs only with a server that offers "progress"
  void librarySync.init(); // account only: follows and bookmarks, when the server lists "library"
  void auth.init(); // checks a stored Google session once the backend is known
  library.init();
  shell.init();

  const outlet = document.getElementById('view');
  if (!outlet) throw new Error('missing #view');

  window.addEventListener('online', () => {
    emit('online', true);
    toast({ message: 'Đã có mạng trở lại.', kind: 'ok' });
  });
  window.addEventListener('offline', () => {
    emit('online', false);
    toast({ message: 'Bạn đang ngoại tuyến. Các chương đã tải về vẫn đọc được.', duration: 5000 });
  });
  document.documentElement.classList.toggle('is-offline', navigator.onLine === false);
  on('online', (v) => document.documentElement.classList.toggle('is-offline', !v));

  // the data source is chosen before the first view mounts so the views never see "none" by accident
  await initSecret();
  await backend.init();

  router.start({
    outlet,
    views,
    resolve: (route) => (backend.kind === 'none' && NEEDS_SOURCE.has(route.view) ? onboarding : null),
    onError: (el, e) => showError(el, e, () => router.reload()),
    onLoading: loadingView,
  });
  initBackNav();
  on('backend', () => router.reload());
  void shell.refreshSources();
  void data.preload(); // the library list, so the first search needs no round trip

  window.__mlBooted = true;
  clearTimeout(window.__mlBootTimer);
  const bootError = document.getElementById('boot-error');
  if (bootError) bootError.hidden = true;

  // not needed for the first paint
  const idle = (fn: () => void): void => {
    if ('requestIdleCallback' in window) requestIdleCallback(fn, { timeout: 4000 });
    else setTimeout(fn, 1500);
  };
  idle(() => {
    void announceUpdate();
    watchUpdates();
    // the selected on-device voice downloads by itself (one voice, skipped when the connection saves data)
    void import('./player/autovoice').then(
      async (m) => {
        // Android app: with no Vietnamese voice on the phone, Piper is the reader and downloads like on the web
        const hasNative = await import('./player/engines').then((e) => e.probeNativeVoices(), () => true);
        await m.autoInstallVoice(!hasNative);
      },
      () => {},
    );
    void import('./pwa').then(
      (m) => m.pwa.init(),
      () => {},
    );
  });
}

boot().catch((e) => {
  console.error(e);
  window.__mlBootFail?.();
});
