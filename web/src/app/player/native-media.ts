/**
 * Android app only: bridges the player to the native MediaPlayback plugin (foreground service, wake lock,
 * MediaSession and notification) so speech keeps going with the screen off or the app in the background.
 * The plugin is looked up lazily on globalThis.Capacitor, so the browser/PWA build never touches it.
 */
import type { Player } from './index';
import { isNative } from '../core/settings';
import { isNativeIOS } from '../core/native-platform';
import { toast } from '../core/ui';

interface MediaPlaybackPlugin {
  start(o: { title: string; artist: string }): Promise<unknown>;
  update(o: { title: string; artist: string; playing: boolean }): Promise<unknown>;
  stop(): Promise<unknown>;
  batteryStatus?(): Promise<{ unrestricted?: boolean }>;
  openBatterySettings?(): Promise<unknown>;
  addListener(ev: 'action', fn: (e: { action?: string }) => void): Promise<unknown> | { remove(): void };
}

let plugin: MediaPlaybackPlugin | null | undefined;

function get(): MediaPlaybackPlugin | null {
  if (plugin !== undefined) return plugin;
  plugin = null;
  try {
    // no MediaPlayback plugin on iOS: the lock screen comes from the page's Media Session (mediasession.ts)
    if (!isNative() || isNativeIOS()) return null;
    const c = (
      globalThis as {
        Capacitor?: { Plugins?: Record<string, MediaPlaybackPlugin | undefined>; registerPlugin?: (n: string) => MediaPlaybackPlugin };
      }
    ).Capacitor;
    // the native bridge global exposes registered plugins on Capacitor.Plugins (registerPlugin only exists in the bundled core)
    plugin = c?.Plugins?.MediaPlayback ?? (c?.registerPlugin ? c.registerPlugin('MediaPlayback') : null);
  } catch {
    plugin = null;
  }
  return plugin;
}

/** Test hook: forget the cached plugin lookup. */
export function resetNativeMedia(): void {
  plugin = undefined;
}

const quiet = (r: unknown): void => {
  try {
    void Promise.resolve(r).catch(() => {});
  } catch {
    // ignore
  }
};

const BATTERY_KEY = 'mythlab.batteryHint';

/**
 * Once per install, when listening starts: if the system restricts the app's battery use, say how to let it play with the
 * screen off (some makers' task killers stop even a foreground service). Silent when unrestricted or unsupported.
 */
export function batteryHint(pl: MediaPlaybackPlugin): void {
  try {
    if (!pl.batteryStatus || localStorage.getItem(BATTERY_KEY)) return;
  } catch {
    return;
  }
  void Promise.resolve(pl.batteryStatus())
    .then((r) => {
      if (r?.unrestricted !== false) return;
      try {
        localStorage.setItem(BATTERY_KEY, '1');
      } catch {
        // asked again next time
      }
      toast({
        message: 'Để nghe liên tục khi tắt màn hình, hãy cho MythLab chạy nền không hạn chế pin.',
        duration: 12000,
        action: { label: 'Mở cài đặt', run: () => quiet(pl.openBatterySettings?.()) },
      });
    })
    .catch(() => {});
}

export function initNativeMedia(player: Player): void {
  const pl = get();
  if (!pl) return;
  let started = false;
  let last = '';
  const sync = (): void => {
    const st = player.getState();
    const playing = st.status === 'playing' || st.status === 'loading';
    if (st.status === 'idle' || st.status === 'error') {
      if (started) {
        started = false;
        last = '';
        quiet(pl.stop());
      }
      return;
    }
    const title = st.chapterTitle || 'MythLab Truyện';
    const artist = st.storyName || '';
    if (!started) {
      if (!playing) return;
      started = true;
      last = `${title}|${artist}|1`;
      quiet(pl.start({ title, artist }));
      batteryHint(pl);
      return;
    }
    const key = `${title}|${artist}|${playing ? 1 : 0}`;
    if (key === last) return;
    last = key;
    quiet(pl.update({ title, artist, playing }));
  };
  try {
    quiet(
      pl.addListener('action', (e) => {
        switch (e?.action) {
          case 'play':
            player.resume();
            break;
          case 'pause':
            player.pause();
            break;
          case 'next':
            player.gotoChapter((player.getState().idx ?? 0) + 1);
            break;
          case 'previous':
            player.gotoChapter((player.getState().idx ?? 0) - 1);
            break;
        }
      }),
    );
  } catch {
    // no events
  }
  player.onState(sync);
}
