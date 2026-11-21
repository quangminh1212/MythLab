/**
 * Keeps the screen on while the player is speaking: the Capacitor KeepAwake plugin in the Android app, the
 * Screen Wake Lock API elsewhere. Gated by the "keepAwake" setting; a setting change applies at once.
 */
import { S, settings } from '../core/settings';

interface KeepAwakePlugin {
  keepAwake(): Promise<void>;
  allowSleep(): Promise<void>;
}
interface Sentinel {
  release(): Promise<void>;
  addEventListener(type: 'release', fn: () => void): void;
}

const plugin = (): KeepAwakePlugin | null =>
  (globalThis as { Capacitor?: { Plugins?: { KeepAwake?: KeepAwakePlugin } } }).Capacitor?.Plugins?.KeepAwake ?? null;

/** What the player asked for (true while speaking). */
let wanted = false;
let lock: Sentinel | null = null;
let bound = false;

const active = (): boolean => wanted && S.keepAwake !== false;

async function grab(): Promise<void> {
  if (!active() || lock || typeof document === 'undefined' || document.visibilityState !== 'visible') return;
  const wl = (navigator as { wakeLock?: { request(type: 'screen'): Promise<Sentinel> } }).wakeLock;
  if (!wl) return;
  try {
    const l = await wl.request('screen');
    if (!active()) {
      void l.release().catch(() => {});
      return;
    }
    lock = l;
    l.addEventListener('release', () => {
      if (lock === l) lock = null;
    });
  } catch {
    // refused (battery saver, hidden tab): nothing to do
  }
}

async function apply(): Promise<void> {
  const on = active();
  const ka = plugin();
  if (ka) {
    try {
      await (on ? ka.keepAwake() : ka.allowSleep());
      return;
    } catch {
      // fall through to the web API
    }
  }
  if (on) return grab();
  const l = lock;
  lock = null;
  if (l) await l.release().catch(() => {});
}

/** Asks for (or gives up) the awake screen. Safe to call often. */
export function keepAwake(on: boolean): void {
  if (!bound && typeof document !== 'undefined') {
    bound = true;
    // the browser drops the lock when the tab is hidden: take it again when it comes back
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') void grab();
    });
    settings.onChange((key) => {
      if (key === 'keepAwake' || key === null) void apply();
    });
  }
  if (on === wanted) return;
  wanted = on;
  void apply();
}
