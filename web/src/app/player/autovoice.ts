/**
 * The on-device voice installs itself. Shortly after the app is idle on load, the SELECTED Piper voice (the saved
 * choice, or the light default) is downloaded in the background, without a dialog: only that one voice, never the
 * catalog. The model goes into the Cache API (piper.ts), so later loads find it there and download nothing.
 *
 * Not done when the connection asks to save data (`navigator.connection.saveData`): the user starts it from the
 * settings or by pressing play. When the download fails or the device is offline, it is retried on the next load and
 * as soon as the browser reports it is online again.
 *
 * `installVoiceOnce` is the one place that downloads a voice: the automatic start, the settings button and the
 * player (play pressed before the voice is ready) all share the running download instead of starting another.
 */
import { S, set } from '../core/settings';
import { confirmDialog, toast } from '../core/ui';
import type { PiperChoice } from './piper';
import { downloadBytes, installPiper, lightChoice, lowMemoryNote, megabytes, piperChoice, piperInstalled, piperSupported, PIPER_SIZE_NOTE, refreshPiper, tooHeavyHere } from './piper';

/** Voices bigger than this ask before they download when the user did not pick them (play, saveData). */
export const CONFIRM_ABOVE = 70_000_000;

/** The connection asks to save data (Data Saver / metered): nothing is downloaded without the user. */
export function saveData(): boolean {
  return !!(globalThis.navigator as (Navigator & { connection?: { saveData?: boolean } }) | undefined)?.connection?.saveData;
}

interface Running {
  /** Model id (all speakers of a model share one download). */
  model: string;
  promise: Promise<void>;
}
let running: Running | null = null;
let percent = -1;
const watchers = new Set<(pct: number) => void>();

/** Percent (0..100) of the download in progress, or -1 when none runs. */
export const voiceProgress = (): number => percent;

/** Calls `fn` with the percent of the running download; returns the function that stops listening. */
export function onVoiceProgress(fn: (pct: number) => void): () => void {
  watchers.add(fn);
  return () => watchers.delete(fn);
}

function setPercent(p: number): void {
  percent = p;
  for (const fn of watchers) fn(p);
}

/** One download per model across tabs and windows (Web Locks): the others wait, then find the voice in the cache. */
function withVoiceLock<T>(model: string, fn: () => Promise<T>): Promise<T> {
  const locks = (globalThis.navigator as (Navigator & { locks?: LockManager }) | undefined)?.locks;
  return locks ? locks.request(`mythlab-voice:${model}`, fn) : fn();
}

/**
 * Downloads the voice `id` (a saved voice id) once. Joins the download that is already running for the same model.
 * Shows a progress toast every `step` percent. Rejects with the reason when every source failed.
 */
export function installVoiceOnce(id: string, step = 10): Promise<void> {
  const c = piperChoice(id);
  if (running && running.model === c.model.id) return running.promise;
  let last = -1;
  let from = '';
  const say = (pct: number): void => toast({ message: `Đang tải giọng đọc${from}… ${pct}%`, duration: 120_000 });
  const promise = withVoiceLock(c.model.id, async () => {
    say(0);
    setPercent(0);
    try {
      // another tab may have finished this voice while we waited for the lock
      await refreshPiper();
      if (!piperInstalled(c.model.id)) await installPiper(
        c.model.id,
        (f) => {
          const pct = Math.floor((f * 100) / step) * step;
          if (pct !== last) {
            last = pct;
            say(pct);
          }
          setPercent(Math.round(f * 100));
        },
        undefined,
        (i, n) => {
          // the next source starts from 0 again
          from = i ? ` (nguồn dự phòng ${i + 1}/${n})` : '';
          last = -1;
        },
      );
    } finally {
      setPercent(-1);
    }
    toast('Đã tải xong giọng đọc');
  });
  const mine: Running = { model: c.model.id, promise };
  running = mine;
  const done = (): void => {
    if (running === mine) running = null;
  };
  promise.then(done, done);
  return promise;
}

/**
 * A phone with 2 GB of RAM or less is not given a heavy voice it does not have yet: the saved choice becomes the
 * lightest voice (a voice that is already downloaded is never replaced).
 */
export function lightForLowMemory(c: PiperChoice): PiperChoice {
  if (!tooHeavyHere(downloadBytes(c.model)) || piperInstalled(c.model.id)) return c;
  const light = lightChoice();
  set('piperVoice', light.id);
  toast(`Máy có ít bộ nhớ (≤ 2 GB): dùng giọng nhẹ “${light.name}” thay cho giọng “${c.name}”`);
  return light;
}

/** Thrown by `ensureVoice` when the user declined the download. */
export class Declined extends Error {
  constructor() {
    super('declined');
    this.name = 'Declined';
  }
}

/**
 * Makes sure the voice of the saved choice is on the device, for the player. A voice that is already there or is
 * downloading costs nothing. A big voice (or any voice while data saving is on) is only downloaded after a
 * confirmation; the light default is downloaded straight away.
 */
export async function ensureVoice(id: string = S.piperVoice): Promise<void> {
  let c = piperChoice(id);
  await refreshPiper();
  if (piperInstalled(c.model.id)) return;
  c = lightForLowMemory(c);
  if (!running || running.model !== c.model.id) {
    if (saveData() || downloadBytes(c.model) > CONFIRM_ABOVE) {
      const ok = await confirmDialog({
        title: 'Tải giọng đọc?',
        message: `${PIPER_SIZE_NOTE} Giọng “${c.name}” nặng ${megabytes(downloadBytes(c.model))}.${lowMemoryNote(downloadBytes(c.model))}`,
        confirmLabel: 'Tải về',
        persistent: true, // the reader view may still be mounting (route change) when this comes up
      });
      if (!ok) throw new Declined();
    }
  }
  await installVoiceOnce(c.id);
}

let waitingOnline = false;

/** Retries the automatic download once when the browser reports it is online again. */
function retryWhenOnline(): void {
  if (waitingOnline || typeof window === 'undefined') return;
  waitingOnline = true;
  window.addEventListener(
    'online',
    () => {
      waitingOnline = false;
      void autoInstallVoice();
    },
    { once: true },
  );
}

/** The automatic download of the selected voice (main.ts calls it once the page is idle; `force`: the device has no Vietnamese voice, so Piper is the reader although the saved engine is the device). Never throws. Returns true when the voice is on the device. */
export async function autoInstallVoice(force = false): Promise<boolean> {
  try {
    if ((S.engine !== 'piper' && !force) || !piperSupported()) return false;
    await refreshPiper();
    let c = piperChoice(S.piperVoice);
    if (piperInstalled(c.model.id)) return true;
    c = lightForLowMemory(c);
    if (piperInstalled(c.model.id)) return true;
    if (saveData()) return false;
    if (typeof navigator !== 'undefined' && navigator.onLine === false) {
      retryWhenOnline();
      return false;
    }
    try {
      void Promise.resolve(navigator.storage?.persist?.()).catch(() => {});
      await installVoiceOnce(c.id, 25);
      return true;
    } catch (e) {
      toast({ message: `Chưa tải được giọng đọc (${(e as Error).message || e}). Sẽ thử lại khi có mạng.`, kind: 'error' });
      retryWhenOnline();
      return false;
    }
  } catch {
    return false;
  }
}
