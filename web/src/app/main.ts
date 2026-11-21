/**
 * App entry: applies the settings, wires the shell, chooses the data source and starts the router.
 * Views, the player, the settings panel, the offline module and the PWA glue are loaded on demand so this
 * entry stays small.
 */
import { backend } from './core/backend/index';
import type { Route, ViewModule, ViewName } from './core/contracts';
import { emit, on } from './core/events';
import { html, render } from './core/html';
import { library } from './core/library';
import { progress } from './core/progress';
import { router } from './core/router';
import { settings } from './core/settings';
import { bindToasts, showError, skeleton, toast } from './core/ui';
import { shell } from './shell';

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

async function boot(): Promise<void> {
  settings.init();
  bindToasts();
  progress.init();
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
  await backend.init();

  router.start({
    outlet,
    views,
    resolve: (route) => (backend.kind === 'none' && NEEDS_SOURCE.has(route.view) ? onboarding : null),
    onError: (el, e) => showError(el, e, () => router.reload()),
    onLoading: loadingView,
  });
  on('backend', () => router.reload());
  void shell.refreshSources();

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
