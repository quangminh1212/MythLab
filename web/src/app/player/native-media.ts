/**
 * Android app only: bridges the player to the native MediaPlayback plugin (foreground service, wake lock,
 * MediaSession and notification) so speech keeps going with the screen off or the app in the background.
 * The plugin is looked up lazily on globalThis.Capacitor, so the browser/PWA build never touches it.
 */
import type { Player } from './index';
import { isNative } from '../core/settings';

interface MediaPlaybackPlugin {
  start(o: { title: string; artist: string }): Promise<unknown>;
  update(o: { title: string; artist: string; playing: boolean }): Promise<unknown>;
  stop(): Promise<unknown>;
  addListener(ev: 'action', fn: (e: { action?: string }) => void): Promise<unknown> | { remove(): void };
}

let plugin: MediaPlaybackPlugin | null | undefined;

function get(): MediaPlaybackPlugin | null {
  if (plugin !== undefined) return plugin;
  plugin = null;
  try {
    if (!isNative()) return null;
    const c = (globalThis as { Capacitor?: { registerPlugin?: (n: string) => MediaPlaybackPlugin } }).Capacitor;
    plugin = c?.registerPlugin ? c.registerPlugin('MediaPlayback') : null;
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
