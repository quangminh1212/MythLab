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
import { confirmDialog, toast } from '../core/ui';
import { NATIVE_PIECE, offsetAtTime, pieces, sentAt, type Chunk, type ChunkSent } from './text';
import { isVi } from '../settings/voices';
import { installVoiceOnce } from './autovoice';
import { downloadBytes, forget as piperForgetClips, megabytes, piperPrefetch, piperSource, piperSupported, piperChoice, PIPER_SIZE_NOTE, lowMemoryNote, PIPER_CHOICES, piperInstalled, piperChoiceLabel } from './piper';

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
  speak(o: { text: string; lang: string; rate: number; pitch: number; volume: number; category: string; voice?: number }): Promise<void>;
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

/** The voice of the device (the Android app's own text-to-speech), null on the plain web. */
export function localEngine(): 'native' | null {
  return nativeTts() ? 'native' : null;
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

function warnNoVi(): void {
  if (warnedVi) return;
  warnedVi = true;
  if (!piperSupported()) {
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
    const ok = await confirmDialog({
      title: 'Tải giọng Piper?',
      message: `${PIPER_SIZE_NOTE} Giọng “${c.name}” nặng ${megabytes(downloadBytes(v))}${v.speakers ? `, dùng chung cho mọi giọng “${v.name}”` : ''}.${lowMemoryNote(downloadBytes(v))}`,
      confirmLabel: 'Tải về',
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
    if (!j || !j.want || atEnd(a)) return;
    j.want = false;
    j.o.onPaused?.();
  });
  a.addEventListener('playing', () => {
    const j = job;
    if (!j || j.want) return;
    j.want = true;
    j.o.onResumed?.();
  });
  audio = a;
  return a;
}

/** Forgets every prepared clip (voice changed, player closed). */
export function forgetClips(): void {
  piperForgetClips();
}

/** Prepares the audio of the next chunk (Piper clips are synthesised ahead so chunks follow without a gap). */
export function prefetch(engine: TtsEngine | null, chunk: Chunk | undefined): void {
  if (engine === 'piper') piperPrefetch(chunk?.text);
}

/** True for the engines that play clips through the audio element (true pause / resume, speed by playbackRate). */
export const playsClips = (engine: TtsEngine | undefined): boolean => engine === 'piper';

/** Plays the audio of a chunk (a Piper clip) through the shared element. */
function clipSpeak(chunk: Chunk, o: SpeakOptions, src: () => Promise<string>): Promise<void> {
  clipStop();
  const my = ++clipToken;
  const a = element();
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

function nativeStop(): void {
  nativeToken++;
  if (!nativeBusy) return;
  nativeBusy = false;
  void nativeTts()
    ?.stop()
    .catch(() => {});
}

async function nativeSpeak(chunk: Chunk, o: SpeakOptions): Promise<void> {
  const p = nativeTts();
  if (!p) throw new Error('Không có bộ đọc của máy');
  nativeStop();
  const my = nativeToken;
  const vs = await nativeVoices();
  if (my !== nativeToken) throw new Stopped();
  // only Vietnamese voices: the saved one, else the first the device has
  let voice: number | undefined = vs.findIndex((v) => v.voiceURI === S.nativeVoice && isVi(v.lang));
  if (voice < 0) voice = vs.findIndex((v) => isVi(v.lang));
  if (voice < 0) {
    if (vs.length) warnNoVi();
    voice = undefined;
  }
  for (let k = o.from; k < chunk.sents.length; k++) {
    if (my !== nativeToken) throw new Stopped();
    o.onSent(k);
    for (const piece of pieces(sentText(chunk, k), NATIVE_PIECE)) {
      if (my !== nativeToken) throw new Stopped();
      nativeBusy = true;
      try {
        await p.speak({ text: piece.text, lang: 'vi-VN', rate: o.rate, pitch: o.pitch, volume: 1, category: 'playback', ...(voice !== undefined ? { voice } : {}) });
      } catch (e) {
        if (my !== nativeToken) throw new Stopped();
        throw e;
      } finally {
        if (my === nativeToken) nativeBusy = false;
      }
    }
  }
  if (my !== nativeToken) throw new Stopped();
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
