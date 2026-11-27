/**
 * System media controls (lock screen, media keys, Chrome / Brave "media hub" popup).
 * Handlers are bound once; position and metadata follow the player. Device voices make no sound
 * through an <audio> element, so Chrome would not show a popup at all: a silent looping clip started
 * inside the user's gesture stands in for them (a separate element, so engines.ts never sees it).
 */
import type { Player } from './index';
import { effectiveEngine, unlockClips } from './engines';
import { initNativeMedia } from './native-media';

let p: Player | null = null;
let bound = false;
let silent: HTMLAudioElement | null = null;
let wantSilent = false;

/** One second of 8 kHz 8-bit mono silence as a data URI. */
export function silentWav(): string {
  const n = 8000;
  const b = new Uint8Array(44 + n);
  const dv = new DataView(b.buffer);
  const str = (o: number, s: string): void => {
    for (let i = 0; i < s.length; i++) b[o + i] = s.charCodeAt(i);
  };
  str(0, 'RIFF');
  dv.setUint32(4, 36 + n, true);
  str(8, 'WAVEfmt ');
  dv.setUint32(16, 16, true);
  dv.setUint16(20, 1, true);
  dv.setUint16(22, 1, true);
  dv.setUint32(24, n, true);
  dv.setUint32(28, n, true);
  dv.setUint16(32, 1, true);
  dv.setUint16(34, 8, true);
  str(36, 'data');
  dv.setUint32(40, n, true);
  b.fill(128, 44);
  let s = '';
  for (let i = 0; i < b.length; i += 0x2000) s += String.fromCharCode(...b.subarray(i, i + 0x2000));
  return 'data:audio/wav;base64,' + btoa(s);
}

let silentUri = '';
function silentSrc(): string {
  return (silentUri ||= silentWav());
}

function silentOn(): void {
  try {
    if (typeof Audio === 'undefined') return;
    if (!silent) {
      silent = new Audio(silentWav());
      silent.loop = true;
      silent.volume = 0.01;
    }
    void silent.play()?.catch(() => {});
  } catch {
    // no popup keep-alive here
  }
}

function silentOff(): void {
  try {
    silent?.pause();
  } catch {
    // ignore
  }
}

/** Call synchronously from the user's gesture (play button / "listen"), before any await. */
export function primeMediaSession(): void {
  try {
    const e = effectiveEngine();
    if (e === 'piper') {
      // clips play through the shared element: unlock it in this gesture (iOS) and keep it busy between clips
      unlockClips(silentSrc());
      return;
    }
  } catch {
    return;
  }
  wantSilent = true;
  silentOn();
}

/**
 * True when a Piper clip is playing (or about to) in a tab the system has hidden (screen off, other app). A silent loop then
 * keeps the page a media page between two clips, while the next one is synthesised, so Chrome does not freeze it.
 */
export function needsHiddenKeepAlive(status: string | undefined, engine: string | undefined, visibility: string | undefined): boolean {
  return (status === 'playing' || status === 'loading') && engine === 'piper' && visibility === 'hidden';
}

function sync(): void {
  if (!p) return;
  const st = p.getState();
  const ms = typeof navigator !== 'undefined' && 'mediaSession' in navigator ? navigator.mediaSession : null;
  const playing = st.status === 'playing' || st.status === 'loading';
  const hiddenKeep = !wantSilent && needsHiddenKeepAlive(st.status, st.engine, typeof document === 'undefined' ? undefined : document.visibilityState);
  if (st.status === 'idle') {
    wantSilent = false;
    silentOff();
  } else if (wantSilent) {
    if (playing) {
      if (silent?.paused) silentOn();
    } else silentOff();
  } else if (hiddenKeep) {
    if (!silent || silent.paused) silentOn();
  } else if (silent && !silent.paused) silentOff();
  if (!ms || !ms.setPositionState) return;
  try {
    const inf = p.info();
    if (st.status !== 'idle' && inf.chunks > 0) {
      // only valid values reach setPositionState (chunks stand in for seconds)
      const duration = inf.chunks;
      const position = Math.min(Math.max(inf.chunk, 0), duration);
      if (Number.isFinite(position)) ms.setPositionState({ duration, position, playbackRate: 1 });
    } else if (st.status === 'idle') {
      (ms.setPositionState as () => void)();
    }
  } catch {
    // not supported
  }
}

export function initMediaSession(player: Player): void {
  if (p || typeof navigator === 'undefined') return;
  p = player;
  if (!bound && 'mediaSession' in navigator) {
    bound = true;
    const bind = (action: string, fn: (d?: { seekTime?: number | null }) => void): void => {
      try {
        navigator.mediaSession.setActionHandler(action as MediaSessionAction, fn as MediaSessionActionHandler);
      } catch {
        // this action is not supported here
      }
    };
    bind('play', () => {
      primeMediaSession();
      player.resume();
    });
    bind('pause', () => player.pause());
    bind('previoustrack', () => player.gotoChapter((player.getState().idx ?? 0) - 1));
    bind('nexttrack', () => player.gotoChapter((player.getState().idx ?? 0) + 1));
    bind('seekto', (d) => {
      const t = d?.seekTime;
      const inf = player.info();
      if (typeof t === 'number' && Number.isFinite(t) && inf.chunks > 0) player.step(Math.round(t) - inf.chunk);
    });
  }
  player.onChange(sync);
  player.onState(sync);
  if (typeof document !== 'undefined') document.addEventListener('visibilitychange', sync);
  initNativeMedia(player);
}
