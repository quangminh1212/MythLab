/**
 * System Back button (Android / Capacitor). Without this the WebView's Back finishes the Activity, so Back from
 * any inner page (story, reader, the full-page error) used to leave the app.
 *
 *   inner page, a previous entry exists  -> history.back()
 *   inner page, opened directly          -> replace with home (never exits silently)
 *   home                                 -> toast, and exit only on a second press within EXIT_WINDOW_MS
 */
import { navigate, currentRoute } from './router';
import { toast } from './ui';

export const EXIT_WINDOW_MS = 2000;

export type BackAction = 'back' | 'home' | 'warn' | 'exit';

/** Pure decision: what a Back press does. */
export function decideBack(view: string, canGoBack: boolean, now: number, lastWarnAt: number): BackAction {
  if (view === 'home') return now - lastWarnAt <= EXIT_WINDOW_MS ? 'exit' : 'warn';
  return canGoBack ? 'back' : 'home';
}

interface BackEvent {
  canGoBack?: boolean;
}
interface AppPlugin {
  addListener(name: 'backButton', cb: (e: BackEvent) => void): unknown;
  exitApp(): unknown;
}

export const nativeApp = (): AppPlugin | null => (globalThis as { Capacitor?: { Plugins?: { App?: AppPlugin } } }).Capacitor?.Plugins?.App ?? null;

/** Handles one Back press; returns the action taken. `exit` is injected for tests. */
export function handleBack(e: BackEvent, exit: () => void, now: number = Date.now(), state = { lastWarnAt: -Infinity }): BackAction {
  const act = decideBack(currentRoute().view, e.canGoBack !== false && history.length > 1, now, state.lastWarnAt);
  if (act === 'back') history.back();
  else if (act === 'home') navigate('#/', { replace: true });
  else if (act === 'warn') {
    state.lastWarnAt = now;
    toast('Nhấn Back lần nữa để thoát');
  } else exit();
  return act;
}

/** Registers the Back handler when running inside the Capacitor shell. */
export function init(): boolean {
  const app = nativeApp();
  if (!app) return false;
  const state = { lastWarnAt: -Infinity };
  app.addListener('backButton', (e) => handleBack(e, () => void app.exitApp(), Date.now(), state));
  return true;
}
