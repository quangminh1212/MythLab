/**
 * The voices of the player and what is known about them (Vietnamese voices only, nothing runs on the server):
 *   piper    free Vietnamese neural voices synthesised on the device (piper.ts), played as clips through one <audio>
 *            element (true pause / resume, seekable). The only reader of the plain web.
 *   native   the Android app's text-to-speech (Capacitor TextToSpeech plugin), only where that plugin exists
 * (The browser's own speechSynthesis is not used: most devices have no Vietnamese voice in it.)
 * Each engine speaks one chunk and reports the sentence it is on. The player (index.ts) decides which engine
 * speaks, what happens on errors and what comes next.
 */
import type { TtsEngine } from '../core/settings';
import { S, set } from '../core/settings';
import { isNativeIOS } from '../core/native-platform';
import { confirmDialog, toast } from '../core/ui';
import { NATIVE_PIECE, offsetAtTime, pieces, sentAt, type Chunk, type ChunkSent } from './text';
import { isVi } from '../settings/voices';
import { installVoiceOnce } from './autovoice';
import { downloadBytes, forget as piperForgetClips, megabytes, piperPrefetch, piperSource, piperSupported, piperChoice, PIPER_SIZE_NOTE, lowMemoryNote, tooHeavyHere, PIPER_CHOICES, piperInstalled, piperChoiceLabel } from './piper';

/** Thrown into a pending speak() when the player itself stopped it; never shown to the user. */
export class Stopped extends Error {
  constructor() {
    super('stopped');
    this.name = 'Stopped';
  }
}

/** Thrown when the system cut the voice off (another app took the audio, the tab was frozen …). */
export class Interrupted extends Error {
  constructor() {
    super('interrupted');
    this.name = 'Interrupted';
  }
}

export interface SpeakOptions {
  /** Sentence of the chunk to start at. */
  from: number;
  rate: number;
  pitch: number;
  /** Called when a sentence starts. */
  onSent(k: number): void;
  /** Clip engines (Piper): the audio was paused / resumed from outside (media keys, headset, the system). */
  onPaused?(): void;
  onResumed?(): void;
}

const sentText = (c: Chunk, k: number): string => {
  const s = c.sents[k] as ChunkSent;
  return c.text.slice(s.at, s.at + s.len);
};

// ---------------------------------------------------------------- availability

interface NativeVoice {
  voiceURI: string;
  name?: string;
  lang: string;
}
interface NativeTts {
  speak(o: { text: string; lang: string; rate: number; pitch: number; volume: number; category: string; voice?: number; queueStrategy?: number }): Promise<void>;
  stop(): Promise<void>;
  getSupportedVoices(): Promise<{ voices?: NativeVoice[] }>;
  openInstall?(): Promise<void>;
}

const nativeTts = (): NativeTts | null =>
  (globalThis as { Capacitor?: { Plugins?: { TextToSpeech?: NativeTts } } }).Capacitor?.Plugins?.TextToSpeech ?? null;

/** The engines that exist here, in display order. */
export function engines(): TtsEngine[] {
  const out: TtsEngine[] = [];
  if (nativeTts()) out.push('native');
  if (piperSupported()) out.push('piper');
  return out;
}

/** The voice of the device (the Android app's own text-to-speech) as a fallback reader: null on the plain web and when the device has no Vietnamese voice (a foreign voice is never used). */
export function localEngine(): 'native' | null {
  return nativeTts() && nativeHasVi !== false ? 'native' : null;
}

/**
 * The engine that will speak. The saved choice ("engine" setting) is never rewritten. Piper is returned even while
 * its voice is still downloading: the player waits for it (index.ts) instead of speaking with something else.
 */
export function effectiveEngine(): TtsEngine | null {
  if (S.engine === 'piper' && piperSupported()) return 'piper';
  // the phone has no Vietnamese voice of its own: the on-device Piper voice reads instead of silence / a foreign voice
  if (nativeTts() && nativeHasVi === false && piperSupported()) return 'piper';
  if (nativeTts()) return 'native';
  return piperSupported() ? 'piper' : null;
}

export const ENGINE_LABEL: Record<TtsEngine, string> = {
  native: 'Giọng của máy',
  piper: 'Giọng Piper (offline, trên máy)',
};

// ---------------------------------------------------------------- voices

export interface VoiceOption {
  id: string;
  name: string;
  lang?: string;
}

const byName = (a: VoiceOption, b: VoiceOption): number => a.name.localeCompare(b.name);

let nativeList: NativeVoice[] | null = null;
let warnedVi = false;
/** null until the device voices were listed; then whether the device has any Vietnamese voice. */
let nativeHasVi: boolean | null = null;

async function nativeVoices(): Promise<NativeVoice[]> {
  const p = nativeTts();
  if (!p) return [];
  if (!nativeList) {
    const r = await p.getSupportedVoices().catch(() => ({ voices: [] as NativeVoice[] }));
    nativeList = r?.voices || [];
    nativeHasVi = nativeList.some((v) => isVi(v.lang));
  }
  return nativeList;
}

/**
 * Android app: lists the device voices once. Resolves false when the device has none in Vietnamese (the player then
 * reads with Piper, see effectiveEngine), true otherwise and on the plain web.
 */
export async function probeNativeVoices(): Promise<boolean> {
  if (!nativeTts()) return true;
  await nativeVoices();
  return nativeHasVi !== false;
}

/** How long the player waits for the device to list its voices before it trusts the saved engine. */
const PROBE_WAIT_MS = 6000;

/**
 * Android app: resolves once the device voices are listed (or after PROBE_WAIT_MS), so the player never starts with
 * the device default voice before it knows whether the phone speaks Vietnamese (see effectiveEngine). Instant on the
 * plain web and once the list is known.
 */
export function settleEngine(): Promise<void> {
  if (!nativeTts() || nativeHasVi !== null) return Promise.resolve();
  return Promise.race([nativeVoices().then(() => undefined), new Promise<void>((r) => setTimeout(r, PROBE_WAIT_MS))]);
}

function warnNoVi(): void {
  if (warnedVi) return;
  warnedVi = true;
  if (!piperSupported()) {
    if (isNativeIOS()) {
      // iOS has no installer to open: voices are downloaded in the system settings
      toast({ message: 'Máy chưa có giọng tiếng Việt — vào Cài đặt > Trợ năng > Nội dung đã đọc > Giọng nói > Tiếng Việt để tải', duration: 10000 });
      return;
    }
    toast({
      message: 'Máy chưa có giọng tiếng Việt — cài “Speech Services by Google” rồi tải gói Tiếng Việt',
      duration: 8000,
      action: { label: 'Cài giọng', run: installVoices },
    });
    return;
  }
  toast({
    message: 'Máy chưa có giọng tiếng Việt. Dùng giọng Piper miễn phí, đọc ngay trên máy?',
    duration: 10000,
    action: { label: 'Dùng giọng Piper', run: () => void offerPiper() },
  });
}

/**
 * Asks before the one big download, then fetches the voice and switches to Piper. Never called without a tap.
 * Resolves true when Piper is ready and selected.
 */
export async function offerPiper(id: string = S.piperVoice): Promise<boolean> {
  const c = piperChoice(id);
  const v = c.model;
  if (!piperInstalled(v.id)) {
    // a phone with 2 GB of RAM or less: refuse by default (Huỷ has the focus); only an explicit "Vẫn tải" goes on
    const heavy = tooHeavyHere(downloadBytes(v));
    const ok = await confirmDialog({
      title: heavy ? 'Giọng này quá nặng cho máy' : 'Tải giọng Piper?',
      message: `${PIPER_SIZE_NOTE} Giọng “${c.name}” nặng ${megabytes(downloadBytes(v))}${v.speakers ? `, dùng chung cho mọi giọng “${v.name}”` : ''}.${lowMemoryNote(downloadBytes(v))}${heavy ? ' Nên giữ giọng nhẹ (Vivos).' : ''}`,
      confirmLabel: heavy ? 'Vẫn tải' : 'Tải về',
      ...(heavy ? { danger: true, cancelFirst: true } : {}),
    });
    if (!ok) return false;
    try {
      await installVoiceOnce(c.id);
    } catch (e) {
      toast({ message: `Không tải được giọng Piper: ${(e as Error).message || e}`, kind: 'error' });
      return false;
    }
  }
  set('piperVoice', c.id);
  set('engine', 'piper');
  return true;
}

/** The Vietnamese voices of an engine. Never throws (an empty list when the engine is missing). */
export async function voices(engine: TtsEngine): Promise<VoiceOption[]> {
  try {
    if (engine === 'piper') return PIPER_CHOICES.map((c) => ({ id: c.id, name: piperChoiceLabel(c, false), lang: 'vi-VN' }));
    if (engine === 'native') {
      const vs = await nativeVoices();
      if (nativeTts() && !vs.some((v) => isVi(v.lang))) warnNoVi();
      return vs.filter((v) => isVi(v.lang)).map((v) => ({ id: v.voiceURI, name: v.name || v.voiceURI, lang: v.lang })).sort(byName);
    }
    return [];
  } catch {
    return [];
  }
}

/** Android: opens the system screen that installs voice data. */
export function installVoices(): void {
  void nativeTts()
    ?.openInstall?.()
    .catch(() => {});
}

// ---------------------------------------------------------------- clips (Piper)

interface ClipJob {
  chunk: Chunk;
  o: SpeakOptions;
  /** We want the audio to be running (false after pause()). */
  want: boolean;
  sent: number;
  settle(err?: unknown): void;
}

let audio: HTMLAudioElement | null = null;
let job: ClipJob | null = null;
let clipToken = 0;
/** Silent clip the element loops while it waits for the next clip (keeps the page "playing", unlocked for autoplay). */
let hold = '';
/** True from a src change until the element plays again: a pause in between is ours, not the system's. */
let swapping = false;

function atEnd(a: HTMLAudioElement): boolean {
  return a.ended || (Number.isFinite(a.duration) && a.duration > 0 && a.currentTime >= a.duration - 0.08);
}

function element(): HTMLAudioElement {
  if (audio) return audio;
  const a = new Audio();
  a.preload = 'auto';
  a.addEventListener('ended', () => job?.settle());
  a.addEventListener('error', () => {
    if (a.getAttribute('src')) job?.settle(new Error('Không phát được âm thanh'));
  });
  a.addEventListener('timeupdate', () => {
    const j = job;
    if (!j) return;
    const k = Math.max(j.o.from, sentAt(j.chunk, offsetAtTime(j.chunk, a.currentTime, a.duration)));
    if (k !== j.sent) {
      j.sent = k;
      j.o.onSent(k);
    }
  });
  // a pause we did not ask for: headset button, another app took the audio focus, the system media controls
  a.addEventListener('pause', () => {
    const j = job;
    if (swapping || !j || !j.want || atEnd(a)) return;
    j.want = false;
    j.o.onPaused?.();
  });
  a.addEventListener('playing', () => {
    swapping = false;
    const j = job;
    if (!j || j.want) return;
    j.want = true;
    j.o.onResumed?.();
  });
  audio = a;
  return a;
}

/**
 * Call inside the user's gesture: the shared element starts a silent loop, which unlocks it for later play() calls
 * (iOS Safari only allows them on an element started by a gesture) and keeps the page audible while the next clip
 * is still being synthesised with the screen off. `src` is a silent WAV.
 */
export function unlockClips(src: string): void {
  try {
    hold = src;
    const a = element();
    if (job || a.getAttribute('src')) return;
    holdSilence(a);
  } catch {
    // no unlock here
  }
}

function holdSilence(a: HTMLAudioElement): void {
  if (!hold || a.getAttribute('src')) return;
  swapping = true;
  a.loop = true;
  a.src = hold;
  void a.play()?.catch(() => {
    swapping = false;
  });
}

/** Forgets every prepared clip (voice changed, player closed). */
export function forgetClips(): void {
  piperForgetClips();
}

/** Prepares the audio of the next chunk (Piper clips are synthesised ahead so chunks follow without a gap). */
export function prefetch(engine: TtsEngine | null, chunk: Chunk | undefined): void {
  hint = engine === 'native' ? chunk : undefined;
  if (engine === 'piper') piperPrefetch(chunk?.text);
}

/** How many chunks ahead are synthesised (about 15 s of speech each): covers a screen-off stretch of CPU throttling. */
export const LOOKAHEAD = 3;

/** Chunks to prepare after index `ci`, nearest first. */
export function lookaheadChunks<T>(chunks: readonly T[], ci: number, n = LOOKAHEAD): T[] {
  return chunks.slice(ci + 1, ci + 1 + Math.max(0, n));
}

/** True for the engines that play clips through the audio element (true pause / resume, speed by playbackRate). */
export const playsClips = (engine: TtsEngine | undefined): boolean => engine === 'piper';

/** Plays the audio of a chunk (a Piper clip) through the shared element. */
function clipSpeak(chunk: Chunk, o: SpeakOptions, src: () => Promise<string>): Promise<void> {
  clipStop();
  const my = ++clipToken;
  const a = element();
  holdSilence(a);
  return src().then(
    (src) =>
      new Promise<void>((resolve, reject) => {
        if (my !== clipToken) return reject(new Stopped());
        let done = false;
        const j: ClipJob = {
          chunk,
          o,
          want: true,
          sent: -1,
          settle(err) {
            if (done) return;
            done = true;
            if (job === j) job = null;
            if (err === undefined) resolve();
            else reject(err);
          },
        };
        job = j;
        swapping = true;
        a.loop = false;
        a.src = src;
        a.defaultPlaybackRate = o.rate;
        a.playbackRate = o.rate;
        (a as { preservesPitch?: boolean }).preservesPitch = true;
        const first = chunk.sents[o.from];
        if (o.from > 0 && first) {
          // start inside the clip: the position of a sentence is estimated from its share of the text
          const seek = (): void => {
            if (job === j && Number.isFinite(a.duration) && a.duration > 0) a.currentTime = (first.at / chunk.text.length) * a.duration;
          };
          a.addEventListener('loadedmetadata', seek, { once: true });
        }
        j.sent = o.from;
        o.onSent(o.from);
        a.play().catch((e: unknown) => {
          // pause() while the clip was still loading rejects the play() promise: that is not a failure
          swapping = false;
          if ((e as { name?: string } | null)?.name === 'AbortError' && (job !== j || !j.want)) return;
          j.settle(e);
        });
      }),
  );
}

/** Pauses the audio in place; true when there is something to resume. */
function clipPause(): boolean {
  const j = job;
  if (!j || !audio) return false;
  j.want = false;
  audio.pause();
  return true;
}

/** Continues after clipPause(); false when nothing was held (the caller starts the chunk again). */
function clipResume(): boolean {
  const j = job;
  const a = audio;
  if (!j || !a || !a.getAttribute('src')) return false;
  j.want = true;
  a.play().catch((e: unknown) => {
    if ((e as { name?: string } | null)?.name === 'AbortError') return;
    j.settle(e);
  });
  return true;
}

function clipStop(): void {
  clipToken++;
  const j = job;
  job = null;
  j?.settle(new Stopped());
  const a = audio;
  if (a && a.getAttribute('src')) {
    a.pause();
    a.removeAttribute('src');
    a.load();
  }
}

/** Applies a new speed to the clip that is playing. */
export function clipRate(rate: number): void {
  if (!audio) return;
  audio.defaultPlaybackRate = rate;
  audio.playbackRate = rate;
}

/** True while a clip is held (playing or paused). */
export const clipHolding = (): boolean => !!job;

// ---------------------------------------------------------------- native (Capacitor TextToSpeech)

let nativeToken = 0;
let nativeBusy = false;

/** Utterances already handed to the phone's speech queue (one entry per piece of a sentence). */
interface NativeQueue {
  chunk: Chunk;
  from: number;
  rate: number;
  pitch: number;
  token: number;
  voice: number;
  items: { k: number; p: Promise<void> }[];
}
/** The chunk after the one being spoken, already queued natively so it follows without a JS round trip. */
let ahead: NativeQueue | null = null;
/** The chunk that comes next, as announced by prefetch(). */
let hint: Chunk | undefined;

/** Rejecters of the chunks waiting on the speech service: the service never answers the utterances a stop() dropped. */
const nativeWaiters = new Set<(e: Error) => void>();

function nativeStop(): void {
  nativeToken++;
  ahead = null;
  for (const w of [...nativeWaiters]) w(new Stopped());
  nativeWaiters.clear();
  if (!nativeBusy) return;
  nativeBusy = false;
  void nativeTts()
    ?.stop()
    .catch(() => {});
}

/**
 * Hands a chunk to the phone's speech queue in one go (QUEUE_ADD after the first utterance), so the voice goes on
 * from sentence to sentence, and chunk to chunk, inside the speech service even when the WebView is throttled
 * with the screen off. `flush` starts a fresh queue (the first utterance drops whatever was queued).
 */
function nativeQueue(p: NativeTts, chunk: Chunk, from: number, rate: number, pitch: number, voice: number, token: number, flush: boolean): NativeQueue {
  const items: NativeQueue['items'] = [];
  let first = flush;
  for (let k = from; k < chunk.sents.length; k++) {
    for (const piece of pieces(sentText(chunk, k), NATIVE_PIECE)) {
      const r = Promise.resolve(p.speak({ text: piece.text, lang: 'vi-VN', rate, pitch, volume: 1, category: 'playback', queueStrategy: first ? 0 : 1, voice }));
      r.catch(() => {});
      first = false;
      items.push({ k, p: r });
    }
  }
  if (items.length) nativeBusy = true;
  return { chunk, from, rate, pitch, token, voice, items };
}

async function nativeSpeak(chunk: Chunk, o: SpeakOptions): Promise<void> {
  const p = nativeTts();
  if (!p) throw new Error('Không có bộ đọc của máy');
  let q: NativeQueue | null = null;
  const a = ahead;
  if (a && a.chunk === chunk && a.from === 0 && o.from === 0 && a.rate === o.rate && a.pitch === o.pitch && a.token === nativeToken) {
    // this chunk is already queued in the speech service and is probably speaking: just follow it
    q = a;
    ahead = null;
  } else {
    nativeStop();
  }
  const my = nativeToken;
  if (!q) {
    const vs = await nativeVoices();
    if (my !== nativeToken) throw new Stopped();
    // only Vietnamese voices: the saved one, else the first the device has
    let voice = vs.findIndex((v) => v.voiceURI === S.nativeVoice && isVi(v.lang));
    if (voice < 0) voice = vs.findIndex((v) => isVi(v.lang));
    if (voice < 0) {
      // never the device default voice: it is not Vietnamese
      warnNoVi();
      throw new Error('Máy chưa có giọng tiếng Việt');
    }
    q = nativeQueue(p, chunk, o.from, o.rate, o.pitch, voice, my, true);
  }
  // queue the next chunk behind this one
  const h = hint;
  if (h && h !== chunk && !ahead && my === nativeToken && h.sents.length) {
    const n = nativeQueue(p, h, 0, o.rate, o.pitch, q.voice, my, false);
    if (n.items.length) ahead = n;
  }
  let cancel: ((e: Error) => void) | undefined;
  const cancelled = new Promise<never>((_, rej) => {
    cancel = rej;
    nativeWaiters.add(rej);
  });
  cancelled.catch(() => {});
  try {
    let at = -1;
    for (const it of q.items) {
      if (my !== nativeToken) throw new Stopped();
      if (it.k !== at) {
        at = it.k;
        o.onSent(it.k);
      }
      try {
        await Promise.race([it.p, cancelled]);
      } catch (e) {
        if (my !== nativeToken) throw new Stopped();
        throw e;
      }
    }
    if (my !== nativeToken) throw new Stopped();
  } finally {
    if (cancel) nativeWaiters.delete(cancel);
    if (my === nativeToken) nativeBusy = ahead !== null;
  }
}

// ---------------------------------------------------------------- one face for the player

/** Speaks a chunk with an engine. Resolves when the chunk was spoken; rejects with Stopped / Interrupted / an error. */
export function speak(engine: TtsEngine, chunk: Chunk, o: SpeakOptions): Promise<void> {
  if (engine === 'piper') {
    nativeStop();
    return clipSpeak(chunk, o, () => piperSource(chunk.text));
  }
  clipStop();
  return nativeSpeak(chunk, o);
}

/** Silences every engine. */
export function stopAll(): void {
  hold = '';
  clipStop();
  nativeStop();
}

/**
 * Pauses. True when the engine holds its place and `resumeHeld()` continues exactly there (Piper clip);
 * false when the voice was cancelled and the player must speak the current sentence again (device voices have
 * no reliable pause).
 */
export function pauseHeld(engine: TtsEngine | undefined): boolean {
  if (playsClips(engine) && clipPause()) return true;
  stopAll();
  return false;
}

export const resumeHeld = (): boolean => clipResume();
