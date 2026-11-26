/**
 * The voices of the player and what is known about them (Vietnamese voices only, nothing runs on the server):
 *   piper    free Vietnamese neural voices synthesised on the device (piper.ts), played as clips through one <audio>
 *            element (true pause / resume, seekable)
 *   browser  the browser's speech synthesis
 *   native   the Android app's text-to-speech (Capacitor TextToSpeech plugin)
 * Each engine speaks one chunk and reports the sentence it is on. The player (index.ts) decides which engine
 * speaks, what happens on errors and what comes next.
 */
import type { TtsEngine } from '../core/settings';
import { S, set } from '../core/settings';
import { confirmDialog, toast } from '../core/ui';
import { BROWSER_PIECE, NATIVE_PIECE, offsetAtTime, pieces, sentAt, type Chunk, type ChunkSent } from './text';
import { isVi } from '../settings/voices';
import { forget as piperForgetClips, installPiper, megabytes, piperPrefetch, piperReady, piperSource, piperSupported, piperChoice, PIPER_SIZE_NOTE, PIPER_CHOICES, piperInstalled, piperChoiceLabel } from './piper';

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
const synth = (): SpeechSynthesis | null =>
  typeof speechSynthesis !== 'undefined' && typeof SpeechSynthesisUtterance !== 'undefined' ? speechSynthesis : null;

/** The engines that exist here, in display order. */
export function engines(): TtsEngine[] {
  const out: TtsEngine[] = [];
  if (synth()) out.push('browser');
  if (nativeTts()) out.push('native');
  if (piperSupported()) out.push('piper');
  return out;
}

/** The voice of the device: the app's own engine when it was chosen, otherwise the browser's. */
export function localEngine(): 'browser' | 'native' | null {
  if ((S.engine === 'native' || S.engine === 'piper') && nativeTts()) return 'native';
  if (synth()) return 'browser';
  if (nativeTts()) return 'native';
  return null;
}

/**
 * The engine that will actually speak. The saved choice ("engine" setting) is never rewritten: Piper is only used
 * once its voice is downloaded, the device voice speaks meanwhile.
 */
export function effectiveEngine(): TtsEngine | null {
  if (S.engine === 'piper' && piperReady()) return 'piper';
  return localEngine();
}

export const ENGINE_LABEL: Record<TtsEngine, string> = {
  browser: 'Giọng của trình duyệt',
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

async function nativeVoices(): Promise<NativeVoice[]> {
  const p = nativeTts();
  if (!p) return [];
  if (!nativeList) {
    const r = await p.getSupportedVoices().catch(() => ({ voices: [] as NativeVoice[] }));
    nativeList = r?.voices || [];
  }
  return nativeList;
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
      message: `${PIPER_SIZE_NOTE} Giọng “${c.name}” nặng ${megabytes(v.bytes)}${v.speakers ? `, dùng chung cho mọi giọng “${v.name}”` : ''}.`,
      confirmLabel: 'Tải về',
    });
    if (!ok) return false;
    let last = -1;
    let from = '';
    const say = (pct: number): void => toast({ message: `Đang tải giọng Piper${from}… ${pct}%`, duration: 120_000 });
    say(0);
    try {
      await installPiper(
        v.id,
        (f) => {
          const pct = Math.floor(f * 10) * 10;
          if (pct !== last) {
            last = pct;
            say(pct);
          }
        },
        undefined,
        (i, n) => {
          // the next source starts from 0 again
          from = i ? ` (nguồn dự phòng ${i + 1}/${n})` : '';
          last = -1;
        },
      );
    } catch (e) {
      toast({ message: `Không tải được giọng Piper: ${(e as Error).message || e}`, kind: 'error' });
      return false;
    }
    toast('Đã tải xong giọng Piper');
  }
  set('piperVoice', c.id);
  set('engine', 'piper');
  return true;
}

function browserVoices(): Promise<SpeechSynthesisVoice[]> {
  const sy = synth();
  if (!sy) return Promise.resolve([]);
  const now = sy.getVoices();
  if (now.length) return Promise.resolve(now);
  return new Promise((res) => {
    let done = false;
    const finish = (): void => {
      if (done) return;
      done = true;
      sy.removeEventListener?.('voiceschanged', finish);
      res(sy.getVoices());
    };
    sy.addEventListener?.('voiceschanged', finish);
    setTimeout(finish, 1500);
  });
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
    const vs = await browserVoices();
    if (vs.length && !vs.some((v) => isVi(v.lang))) warnNoVi();
    return vs.filter((v) => isVi(v.lang)).map((v) => ({ id: v.voiceURI, name: v.name, lang: v.lang })).sort(byName);
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

// ---------------------------------------------------------------- browser speech synthesis

let browserToken = 0;
let keepAlive: ReturnType<typeof setInterval> | undefined;
/** Chrome drops the events of utterances that were garbage-collected: keep the running ones referenced. */
const live = new Set<SpeechSynthesisUtterance>();

function browserStop(): void {
  browserToken++;
  if (keepAlive !== undefined) clearInterval(keepAlive);
  keepAlive = undefined;
  live.clear();
  try {
    synth()?.cancel();
  } catch {
    // some WebViews throw when nothing is queued
  }
}

async function browserSpeak(chunk: Chunk, o: SpeakOptions): Promise<void> {
  const sy = synth();
  if (!sy) throw new Error('Trình duyệt không có giọng đọc');
  browserStop();
  const my = browserToken;
  const vs = await browserVoices();
  if (my !== browserToken) throw new Stopped();
  const vi = vs.filter((v) => isVi(v.lang));
  if (vs.length && !vi.length) warnNoVi();
  const voice = vi.find((v) => v.voiceURI === S.browserVoice) || vi.find((v) => /natural|online/i.test(v.name)) || vi[0] || null;
  // Chrome on desktop cuts online voices off after ~15 s: nudge it (on Android pause() means cancel, so not there)
  if (voice && !voice.localService && !/Android/i.test(navigator.userAgent)) {
    keepAlive = setInterval(() => {
      if (sy.speaking && !sy.paused) {
        sy.pause();
        sy.resume();
      }
    }, 10_000);
  }
  const say = (text: string): Promise<void> =>
    new Promise<void>((resolve, reject) => {
      const u = new SpeechSynthesisUtterance(text);
      if (voice) u.voice = voice;
      u.lang = voice?.lang || 'vi-VN';
      u.rate = Math.max(0.1, Math.min(10, o.rate));
      u.pitch = Math.max(0, Math.min(2, o.pitch));
      let started = false;
      const watchdog = setTimeout(() => {
        if (!started && !sy.speaking) fail(new Error('Giọng đọc của trình duyệt không phản hồi'));
      }, 8000);
      const end = (): void => {
        clearTimeout(watchdog);
        live.delete(u);
      };
      const fail = (e: Error): void => {
        end();
        reject(e);
      };
      u.onstart = () => {
        started = true;
      };
      u.onend = () => {
        end();
        resolve();
      };
      u.onerror = (ev) => {
        const code = String((ev as SpeechSynthesisErrorEvent).error || 'error');
        if (my !== browserToken) fail(new Stopped());
        else if (code === 'interrupted' || code === 'canceled') fail(new Interrupted());
        else if (code === 'not-allowed') fail(Object.assign(new Error(code), { name: 'NotAllowedError' }));
        else fail(new Error(code));
      };
      live.add(u);
      sy.speak(u);
    });
  try {
    for (let k = o.from; k < chunk.sents.length; k++) {
      if (my !== browserToken) throw new Stopped();
      o.onSent(k);
      for (const piece of pieces(sentText(chunk, k), BROWSER_PIECE)) {
        if (my !== browserToken) throw new Stopped();
        await say(piece.text);
      }
    }
    if (my !== browserToken) throw new Stopped();
  } finally {
    if (my === browserToken && keepAlive !== undefined) {
      clearInterval(keepAlive);
      keepAlive = undefined;
    }
  }
}

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
    browserStop();
    nativeStop();
    return clipSpeak(chunk, o, () => piperSource(chunk.text));
  }
  clipStop();
  if (engine === 'native') {
    browserStop();
    return nativeSpeak(chunk, o);
  }
  nativeStop();
  return browserSpeak(chunk, o);
}

/** Silences every engine. */
export function stopAll(): void {
  clipStop();
  browserStop();
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
