/**
 * The three voices of the player and what is known about them:
 *   edge     the server's neural voices, played through one <audio> element (true pause / resume, seekable)
 *   browser  the browser's speech synthesis
 *   native   the Android app's text-to-speech (Capacitor TextToSpeech plugin)
 * Each engine speaks one chunk and reports the sentence it is on. The player (index.ts) decides which engine
 * speaks, what happens on errors and what comes next.
 */
import type { TtsEngine } from '../core/settings';
import type { Voice } from '../core/contracts';
import { backend } from '../core/backend/index';
import { data } from '../core/data';
import { S } from '../core/settings';
import { toast } from '../core/ui';
import { BROWSER_PIECE, edgePitch, NATIVE_PIECE, offsetAtTime, pieces, sentAt, type Chunk, type ChunkSent } from './text';

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
  /** Edge only: the audio was paused / resumed from outside (media keys, headset, the system). */
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

/** What `/api/sources` said about the server voices (null = not asked yet). */
let edgeFlag: boolean | null = null;

/** Asks the server whether its voices work (cached by core/data). Never throws. */
export async function refreshEdge(): Promise<void> {
  if (backend.kind !== 'server') return;
  try {
    const r = await data.sources();
    edgeFlag = r.tts ? r.tts.edge !== false : true;
  } catch {
    // unknown: keep the last answer
  }
}

/** True when the server voices can be used with the current data source. */
export const edgeAvailable = (): boolean => backend.kind === 'server' && edgeFlag !== false;

/** The engines that exist here, in display order. */
export function engines(): TtsEngine[] {
  const out: TtsEngine[] = [];
  if (edgeAvailable()) out.push('edge');
  if (synth()) out.push('browser');
  if (nativeTts()) out.push('native');
  return out;
}

/** The voice of the device: the app's own engine when it was chosen, otherwise the browser's. */
export function localEngine(): Exclude<TtsEngine, 'edge'> | null {
  if (S.engine === 'native' && nativeTts()) return 'native';
  if (synth()) return 'browser';
  if (nativeTts()) return 'native';
  return null;
}

/**
 * The engine that will actually speak. The saved choice ("engine" setting) is never rewritten: when the server
 * voices are chosen but missing (GitHub-direct mode, service down) the device voice is used meanwhile.
 */
export function effectiveEngine(edgeDown = false): TtsEngine | null {
  const edge = edgeAvailable() && !edgeDown;
  if (S.engine === 'edge' && edge) return 'edge';
  return localEngine() ?? (edge ? 'edge' : null);
}

export const ENGINE_LABEL: Record<TtsEngine, string> = {
  edge: 'Giọng Edge (máy chủ)',
  browser: 'Giọng của trình duyệt',
  native: 'Giọng của máy',
};

// ---------------------------------------------------------------- voices

export interface VoiceOption {
  id: string;
  name: string;
  lang?: string;
}

const isVi = (lang: string | undefined): boolean => /^vi\b/i.test(String(lang || '').replace('_', '-'));
const sortVi = (a: VoiceOption, b: VoiceOption): number => Number(isVi(b.lang)) - Number(isVi(a.lang)) || a.name.localeCompare(b.name);

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
  toast({
    message: 'Máy chưa có giọng tiếng Việt — cài “Speech Services by Google” rồi tải gói Tiếng Việt',
    duration: 8000,
    action: { label: 'Cài giọng', run: installVoices },
  });
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

/** The voices of an engine, Vietnamese first. Never throws (an empty list when the engine is missing). */
export async function voices(engine: TtsEngine): Promise<VoiceOption[]> {
  try {
    if (engine === 'edge') {
      if (!edgeAvailable()) return [];
      const r = await backend.get<{ voices?: Voice[] }>('/voices');
      return (r.voices || []).map((v) => ({ id: v.id, name: v.name || v.id, lang: v.id.slice(0, 5) }));
    }
    if (engine === 'native') {
      const vs = await nativeVoices();
      if (nativeTts() && !vs.some((v) => isVi(v.lang))) warnNoVi();
      return vs.map((v) => ({ id: v.voiceURI, name: v.name || v.voiceURI, lang: v.lang })).sort(sortVi);
    }
    const vs = await browserVoices();
    return vs.map((v) => ({ id: v.voiceURI, name: v.name, lang: v.lang })).sort(sortVi);
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

// ---------------------------------------------------------------- edge (server voices)

interface EdgeJob {
  chunk: Chunk;
  o: SpeakOptions;
  /** We want the audio to be running (false after pause()). */
  want: boolean;
  sent: number;
  settle(err?: unknown): void;
}

let audio: HTMLAudioElement | null = null;
let job: EdgeJob | null = null;
let edgeToken = 0;

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

/** Sources of the chunks about to be played: at most KEEP entries, object URLs are released on eviction. */
const KEEP = 4;
const srcCache = new Map<string, { src: Promise<string>; ctl: AbortController; warm?: HTMLAudioElement }>();

function srcKey(text: string): string {
  return `${S.voice}|${edgePitch(S.pitch) ?? 0}|${text}`;
}

function evict(key: string): void {
  const e = srcCache.get(key);
  if (!e) return;
  srcCache.delete(key);
  e.ctl.abort();
  if (e.warm) {
    e.warm.removeAttribute('src');
    e.warm.load();
  }
  void e.src.then((u) => backend.releaseUrl(u)).catch(() => {});
}

function source(text: string): Promise<string> {
  const key = srcKey(text);
  let e = srcCache.get(key);
  if (e) {
    // most recently used last
    srcCache.delete(key);
    srcCache.set(key, e);
    return e.src;
  }
  const ctl = new AbortController();
  const pitch = edgePitch(S.pitch);
  const src = backend.ttsSrc({ text, ...(S.voice ? { voice: S.voice } : {}), ...(pitch !== undefined ? { pitch } : {}) }, { signal: ctl.signal });
  e = { src, ctl };
  srcCache.set(key, e);
  src.catch(() => {
    if (srcCache.get(key) === e) srcCache.delete(key);
  });
  while (srcCache.size > KEEP) evict(srcCache.keys().next().value as string);
  return src;
}

/** Starts fetching the audio of a chunk that will be played soon (so chunks follow each other without a gap). */
export function edgePrefetch(chunk: Chunk | undefined): void {
  if (!chunk || !edgeAvailable()) return;
  const key = srcKey(chunk.text);
  const had = srcCache.has(key);
  void source(chunk.text)
    .then((u) => {
      const e = srcCache.get(key);
      // a plain URL is only a name: let a silent element download it so the server has it synthesised
      if (had || !e || e.warm || u.startsWith('blob:') || typeof Audio === 'undefined') return;
      const w = new Audio();
      w.preload = 'auto';
      w.muted = true;
      w.src = u;
      e.warm = w;
    })
    .catch(() => {});
}

/** Forgets every prepared source (voice or pitch changed, player closed). */
export function edgeForget(): void {
  for (const k of [...srcCache.keys()]) evict(k);
}

function edgeSpeak(chunk: Chunk, o: SpeakOptions): Promise<void> {
  edgeStop();
  const my = ++edgeToken;
  const a = element();
  return source(chunk.text).then(
    (src) =>
      new Promise<void>((resolve, reject) => {
        if (my !== edgeToken) return reject(new Stopped());
        let done = false;
        const j: EdgeJob = {
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
function edgePause(): boolean {
  const j = job;
  if (!j || !audio) return false;
  j.want = false;
  audio.pause();
  return true;
}

/** Continues after edgePause(); false when nothing was held (the caller starts the chunk again). */
function edgeResume(): boolean {
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

function edgeStop(): void {
  edgeToken++;
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
export function edgeRate(rate: number): void {
  if (!audio) return;
  audio.defaultPlaybackRate = rate;
  audio.playbackRate = rate;
}

/** True while the server voice holds a clip (playing or paused). */
export const edgeHolding = (): boolean => !!job;

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
  const voice =
    vs.find((v) => v.voiceURI === S.browserVoice) || vs.find((v) => isVi(v.lang) && /natural|online/i.test(v.name)) || vs.find((v) => isVi(v.lang)) || null;
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
  let voice: number | undefined = vs.findIndex((v) => v.voiceURI === S.nativeVoice);
  if (voice < 0) {
    if (vs.length && !vs.some((v) => isVi(v.lang))) warnNoVi();
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
  if (engine === 'edge') {
    browserStop();
    nativeStop();
    return edgeSpeak(chunk, o);
  }
  edgeStop();
  if (engine === 'native') {
    browserStop();
    return nativeSpeak(chunk, o);
  }
  nativeStop();
  return browserSpeak(chunk, o);
}

/** Silences every engine. */
export function stopAll(): void {
  edgeStop();
  browserStop();
  nativeStop();
}

/**
 * Pauses. True when the engine holds its place and `resumeHeld()` continues exactly there (server voice);
 * false when the voice was cancelled and the player must speak the current sentence again (device voices have
 * no reliable pause).
 */
export function pauseHeld(engine: TtsEngine | undefined): boolean {
  if (engine === 'edge' && edgePause()) return true;
  stopAll();
  return false;
}

export const resumeHeld = (): boolean => edgeResume();
