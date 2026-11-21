/**
 * Text-to-speech player. Exports `player: PlayerApi` (core/contracts.ts) plus the extras the reader, the dock
 * and the settings panel use (`start`, `step`, `gotoChapter`, `setSleep`, `info`, `onChange`).
 *
 * A chapter is cut into chunks (text.ts); one engine (engines.ts) speaks a chunk at a time and reports the
 * sentence it is on, which becomes the speech mark (mark.ts) the reader highlights. Every asynchronous step
 * carries the generation number `gen`: anything that comes back after a newer command is dropped, so a late
 * error or a retry timer can never restart something the user stopped.
 *
 * The player stores only the listening position (`progress.listen`) and the furthest chapter; the reading
 * position belongs to the reader.
 */
import type { Chapter, ChapterRef, PlayerApi, PlayerState, PlayRequest, StoryDetail } from '../core/contracts';
import { backend } from '../core/backend/index';
import { genCover } from '../core/covers';
import { data, isAbort } from '../core/data';
import { initDock } from './dock';
import { Emitter, emit } from '../core/events';
import { chapterLabel, errMsg } from '../core/format';
import { progress } from '../core/progress';
import { currentRoute, href, navigate } from '../core/router';
import { S, settings, type TtsEngine } from '../core/settings';
import { toast } from '../core/ui';
import { edgeAvailable, edgeForget, edgeHolding, edgePrefetch, edgeRate, effectiveEngine, Interrupted, localEngine, pauseHeld, refreshEdge, resumeHeld, speak, stopAll, Stopped } from './engines';
import { keepAwake } from './keepawake';
import { setMark } from './mark';
import { buildChunks, CHAPTER_CUE, clean, EDGE_MAX, LOCAL_MAX, startChunk, type Chunk } from './text';

export { engines, effectiveEngine, voices, installVoices, ENGINE_LABEL } from './engines';
export type { VoiceOption } from './engines';
export { RATES, SLEEP_MINUTES } from './text';

/** Sleep timer: 0 = off, -1 = stop at the end of the chapter, otherwise minutes. */
export type SleepMode = number;

export interface PlayerInfo {
  /** Index of the chunk being read and the number of chunks of the chapter. */
  chunk: number;
  chunks: number;
  /** Chapter count of the story (0 when idle). */
  total: number;
  sleep: SleepMode;
  /** Epoch ms when a timed sleep fires (0 otherwise). */
  sleepAt: number;
  /** True while the device voice stands in for the server voice. */
  fallback: boolean;
}

interface Session {
  story: StoryDetail;
  idx: number;
  ref: ChapterRef;
  ch: Chapter | null;
  chunks: Chunk[];
  /** Engine limit the chunks were built for. */
  max: number;
  /** Chunk and sentence being spoken (ci === chunks.length = the chapter is finished). */
  ci: number;
  si: number;
  /** Paragraph wanted while the chapter is still loading. */
  wantPara: number;
}

let state: PlayerState = { status: 'idle' };
const stateChanges = new Emitter<PlayerState>();
/** Fires on anything the dock shows: state, chunk position, sleep timer. */
const changes = new Emitter<void>();

let ses: Session | null = null;
let gen = 0;
/** The engine holds a paused clip that `resumeHeld()` can continue. */
let held = false;
let retryTimer: ReturnType<typeof setTimeout> | undefined;
let pitchTimer: ReturnType<typeof setTimeout> | undefined;

/** Server voice health: consecutive failed chunks, and "use the device voice for now". */
let edgeFails = 0;
let edgeDown = false;
let localFails = 0;

let sleep: SleepMode = 0;
let sleepAt = 0;
let sleepTimer: ReturnType<typeof setTimeout> | undefined;

// ---------------------------------------------------------------- state

function setState(patch: Partial<PlayerState>): void {
  const next: PlayerState = { ...state, ...patch };
  if (patch.status && patch.status !== 'error') delete next.error;
  state = next;
  const active = state.status === 'playing' || state.status === 'loading';
  keepAwake(active);
  syncMediaState();
  stateChanges.emit(state);
  emit('player', state);
  changes.emit();
}

function currentEngine(): TtsEngine | null {
  return effectiveEngine(edgeDown);
}

function chunkMax(): number {
  return currentEngine() === 'edge' ? EDGE_MAX : LOCAL_MAX;
}

function rebuild(s: Session, para: number): void {
  s.max = chunkMax();
  s.chunks = s.ch ? buildChunks({ title: chapterLabel(s.ref) || s.ch.title, paragraphs: s.ch.paragraphs }, { max: s.max, readTitle: S.readTitle, clean: S.ttsClean }) : [];
  s.ci = startChunk(s.chunks, para);
  s.si = 0;
}

/** Paragraph of the current position (-1 = title). */
function paraNow(s: Session): number {
  const c = s.chunks[Math.min(s.ci, s.chunks.length - 1)];
  return c ? c.p : s.wantPara;
}

function publishMark(s: Session): void {
  const c = s.chunks[s.ci];
  const sent = c?.sents[s.si];
  if (!c || !sent || state.status === 'idle') {
    setMark(null);
    return;
  }
  setMark({ source: s.story.source, key: s.story.key, idx: s.idx, para: c.p, s: sent.s, e: sent.e });
}

function saveListen(s: Session): void {
  const para = Math.max(0, paraNow(s));
  if (!progress.get(s.story.source, s.story.key)) progress.saveReading(s.story, s.idx, para, 0);
  progress.update({ source: s.story.source, key: s.story.key, listen: { idx: s.idx, para, file: s.ref.file }, maxIdx: s.idx });
}

function clearTimers(): void {
  if (retryTimer !== undefined) clearTimeout(retryTimer);
  retryTimer = undefined;
  if (pitchTimer !== undefined) clearTimeout(pitchTimer);
  pitchTimer = undefined;
}

/** Cancellable wait tied to a generation. */
function wait(ms: number, my: number): Promise<boolean> {
  return new Promise((res) => {
    retryTimer = setTimeout(() => {
      retryTimer = undefined;
      res(my === gen);
    }, ms);
  });
}

// ---------------------------------------------------------------- speaking

function speakChunk(engine: TtsEngine, s: Session, c: Chunk, from: number, my: number): Promise<void> {
  return speak(engine, c, {
    from,
    rate: S.rate,
    pitch: S.pitch,
    onSent(k) {
      if (my !== gen) return;
      s.si = k;
      publishMark(s);
    },
    onPaused() {
      if (my !== gen || state.status !== 'playing') return;
      held = true;
      setState({ status: 'paused' });
    },
    onResumed() {
      if (my !== gen || state.status !== 'paused') return;
      held = false;
      setState({ status: 'playing' });
    },
  });
}

/** The user has to press play (autoplay policy): wait in the paused state at the same place. */
function needGesture(): void {
  stopAll();
  held = false;
  setState({ status: 'paused' });
  toast('Nhấn ▶ để bắt đầu phát');
}

/** Speaks from chunk `ci`, sentence `si`, then the following chunks, then moves to the next chapter. */
async function run(ci: number, si = 0): Promise<void> {
  const s = ses;
  if (!s) return;
  const my = ++gen;
  clearTimers();
  held = false;
  for (;;) {
    if (my !== gen || ses !== s) return;
    s.ci = Math.max(0, Math.min(ci, s.chunks.length));
    s.si = si;
    const c = s.chunks[s.ci];
    if (!c) {
      setMark(null);
      return chapterEnd(s, my, false);
    }
    const engine = currentEngine();
    if (!engine) {
      stopAll();
      setMark(null);
      setState({ status: 'error', error: 'Thiết bị không hỗ trợ đọc thành tiếng' });
      toast({ message: 'Thiết bị không hỗ trợ đọc thành tiếng', kind: 'error' });
      return;
    }
    setState({ status: 'playing', para: c.p, engine });
    publishMark(s);
    saveListen(s);
    if (engine === 'edge') edgePrefetch(s.chunks[s.ci + 1]);
    try {
      await speakWithFallback(engine, s, c, si, my);
    } catch (e) {
      if (my !== gen) return;
      if (e instanceof Stopped) return;
      if (e instanceof Interrupted) {
        // the system silenced the voice: stay at this sentence until the user resumes
        held = false;
        setState({ status: 'paused' });
        return;
      }
      if ((e as { name?: string } | null)?.name === 'NotAllowedError') return needGesture();
      localFails++;
      if (localFails >= 3) {
        stopAll();
        setMark(null);
        setState({ status: 'error', error: `Không đọc được: ${errMsg(e)}` });
        toast({ message: `Không đọc được: ${errMsg(e)}`, kind: 'error' });
        return;
      }
      toast('Không tạo được giọng đọc cho đoạn này — bỏ qua');
    }
    if (my !== gen) return;
    ci = s.ci + 1;
    si = 0;
  }
}

/**
 * One chunk with the server-voice safety net: a failed clip is tried once more after 1.5 s, then the device
 * voice reads that chunk; after three failed chunks in a row the device voice takes over until the engine
 * setting changes. The saved engine choice is never touched.
 */
async function speakWithFallback(engine: TtsEngine, s: Session, c: Chunk, from: number, my: number): Promise<void> {
  if (engine !== 'edge') {
    try {
      await speakChunk(engine, s, c, from, my);
    } catch (e) {
      // the device has no working voice (an emulator without a TTS engine, say): the server voice reads this chunk
      if (my !== gen || e instanceof Stopped || e instanceof Interrupted || (e as { name?: string } | null)?.name === 'NotAllowedError') throw e;
      if (!edgeAvailable() || edgeDown) throw e;
      toast('Giọng của máy không đọc được — dùng giọng Edge của máy chủ');
      setState({ engine: 'edge' });
      await speakChunk('edge', s, c, s.si, my);
    }
    localFails = 0;
    return;
  }
  for (let attempt = 0; ; attempt++) {
    try {
      await speakChunk('edge', s, c, attempt ? s.si : from, my);
      edgeFails = 0;
      localFails = 0;
      return;
    } catch (e) {
      if (my !== gen || e instanceof Stopped || e instanceof Interrupted || (e as { name?: string } | null)?.name === 'NotAllowedError') throw e;
      if (attempt === 0) {
        setState({ status: 'loading' });
        if (!(await wait(1500, my))) throw new Stopped();
        setState({ status: 'playing' });
        continue;
      }
      const local = localEngine();
      if (!local) throw e;
      edgeFails++;
      if (edgeFails >= 3 && !edgeDown) {
        edgeDown = true;
        toast('Dịch vụ giọng Edge đang lỗi — tạm đọc bằng giọng của máy');
      } else if (!edgeDown) toast('Đoạn này đọc bằng giọng của máy (Edge TTS lỗi)');
      setState({ engine: local });
      await speakChunk(local, s, c, s.si, my);
      localFails = 0;
      return;
    }
  }
}

async function chapterEnd(s: Session, my: number, force: boolean): Promise<void> {
  const last = s.idx >= s.story.chapters.length - 1;
  if (!force) {
    if (sleep === -1) {
      clearSleep();
      setState({ status: 'paused' });
      toast('Đã hết chương — dừng theo hẹn giờ');
      return;
    }
    if (last) {
      toast('Đã nghe hết truyện');
      stop();
      return;
    }
    if (!S.autoNext) {
      setState({ status: 'paused' });
      toast('Hết chương');
      return;
    }
    if (S.ttsChapterCue) {
      const engine = currentEngine();
      const text = clean(CHAPTER_CUE, true);
      if (engine && text) {
        try {
          await speak(engine, { p: -2, text, sents: [{ s: 0, e: 0, at: 0, len: text.length }] }, { from: 0, rate: S.rate, pitch: S.pitch, onSent() {} });
        } catch (e) {
          if (my !== gen || e instanceof Stopped) return;
          if (e instanceof Interrupted) {
            setState({ status: 'paused' });
            return;
          }
          // the cue is a nicety: go on without it
        }
        if (my !== gen) return;
      }
    }
  } else if (last) {
    toast('Đã hết truyện');
    setState({ status: 'paused' });
    return;
  }
  await load(s.story, s.idx + 1, -1, true);
}

/** Loads a chapter and starts speaking at `para` (-1 = from the title). */
async function load(story: StoryDetail, idxIn: number, para: number, follow = false): Promise<void> {
  const idx = Math.max(0, Math.min(story.chapters.length - 1, idxIn));
  const ref = story.chapters[idx];
  const my = ++gen;
  clearTimers();
  stopAll();
  held = false;
  setMark(null);
  if (!ref) {
    ses = null;
    setState({ status: 'error', source: story.source, key: story.key, idx: 0, storyName: story.name, chapterTitle: '', error: 'Truyện này chưa có chương nào' });
    toast({ message: 'Truyện này chưa có chương nào', kind: 'error' });
    return;
  }
  const from = ses && ses.story.source === story.source && ses.story.key === story.key ? ses.idx : -1;
  const s: Session = { story, idx, ref, ch: null, chunks: [], max: chunkMax(), ci: 0, si: 0, wantPara: para };
  ses = s;
  const engine = currentEngine();
  setState({ status: 'loading', source: story.source, key: story.key, idx, para, storyName: story.name, chapterTitle: chapterLabel(ref), ...(engine ? { engine } : {}) });
  syncMediaMeta(s);
  // the reader follows the voice into the next chapter when it is showing the chapter that just ended
  if (follow && from >= 0 && from !== idx) {
    const r = currentRoute();
    if (r.view === 'read' && r.source === story.source && r.key === story.key && r.idx === from) navigate(href.read(story.source, story.key, idx), { replace: true });
  }
  try {
    const [ch] = await Promise.all([data.chapter(story.source, story.key, ref.file), refreshEdge()]);
    if (my !== gen) return;
    s.ch = ch;
  } catch (e) {
    if (my !== gen || isAbort(e)) return;
    setState({ status: 'error', error: `Lỗi tải chương: ${errMsg(e)}` });
    toast({ message: `Lỗi tải chương: ${errMsg(e)}`, kind: 'error' });
    return;
  }
  rebuild(s, para);
  if (!s.chunks.length) {
    // nothing to read in this chapter (only scene breaks): treat it as finished
    s.ci = 0;
    return chapterEnd(s, my, false);
  }
  // warm the following chapter so the change-over has no gap
  const nextRef = story.chapters[idx + 1];
  if (nextRef && S.autoNext) void data.chapter(story.source, story.key, nextRef.file).catch(() => {});
  await run(s.ci, 0);
}

// ---------------------------------------------------------------- commands

/**
 * Starts reading a chapter aloud. `para`: -1 = from the title, n = from that paragraph. Unless `exact`, a
 * request for the saved reading position continues at the saved listening position when that is further on,
 * and a request without a paragraph starts with the title.
 */
async function start(req: PlayRequest & { exact?: boolean }): Promise<void> {
  const my = ++gen;
  clearTimers();
  stopAll();
  held = false;
  setMark(null);
  let story = req.story;
  if (!story) {
    setState({ status: 'loading', source: req.source, key: req.key, idx: req.idx, storyName: state.source === req.source && state.key === req.key ? state.storyName || '' : '', chapterTitle: '' });
    try {
      story = await data.story(req.source, req.key);
    } catch (e) {
      if (my !== gen || isAbort(e)) return;
      ses = null;
      setState({ status: 'error', error: `Lỗi tải truyện: ${errMsg(e)}` });
      toast({ message: `Lỗi tải truyện: ${errMsg(e)}`, kind: 'error' });
      return;
    }
    if (my !== gen) return;
  }
  story = { ...story, source: story.source || req.source, key: story.key || req.key };
  let idx = req.idx;
  let para = req.para ?? 0;
  if (!req.exact) {
    const p = progress.get(story.source, story.key);
    if (p?.listen && progress.resolveIdx(p, story.chapters) === idx && (req.para == null || req.para === p.para)) {
      const li = progress.resolveIdx({ idx: p.listen.idx, ...(p.listen.file ? { file: p.listen.file } : {}) }, story.chapters);
      if (li > idx || (li === idx && p.listen.para > para)) {
        idx = li;
        para = p.listen.para;
      }
    }
    if (para <= 0) para = -1;
  }
  edgeFails = 0;
  localFails = 0;
  await load(story, idx, para);
}

function pause(): void {
  const s = ses;
  if (!s || (state.status !== 'playing' && state.status !== 'loading')) return;
  if (state.status === 'loading' && !s.ch) {
    // the chapter is still on its way: remember to wait instead of starting when it arrives
    gen++;
    clearTimers();
    stopAll();
    held = false;
    setState({ status: 'paused' });
    return;
  }
  clearTimers();
  held = pauseHeld(state.engine);
  // a cancelled device voice or a pending retry must not continue on its own
  if (!held || !edgeHolding()) {
    held = false;
    gen++;
  }
  setState({ status: 'paused' });
}

function resume(): void {
  const s = ses;
  if (!s) {
    if (state.status === 'error' && state.source && state.key) void start({ source: state.source, key: state.key, idx: state.idx ?? 0 });
    return;
  }
  if (state.status !== 'paused' && state.status !== 'error') return;
  if (!s.ch) {
    void load(s.story, s.idx, s.wantPara);
    return;
  }
  if (s.ci >= s.chunks.length) {
    // paused at the end of the chapter (sleep timer, auto-next off): the button means "next chapter"
    void chapterEnd(s, ++gen, true);
    return;
  }
  if (held && state.status === 'paused' && resumeHeld()) {
    held = false;
    setState({ status: 'playing' });
    return;
  }
  // continue with the sentence that was interrupted, never from the start of the chunk
  void run(s.ci, s.si);
}

function toggle(): void {
  if (state.status === 'idle') return;
  if (state.status === 'playing' || state.status === 'loading') pause();
  else resume();
}

function stop(): void {
  gen++;
  clearTimers();
  stopAll();
  edgeForget();
  held = false;
  ses = null;
  clearSleep();
  setMark(null);
  edgeFails = 0;
  localFails = 0;
  state = { status: 'idle' };
  setState({});
  if ('mediaSession' in navigator) {
    try {
      navigator.mediaSession.metadata = null;
    } catch {
      // not supported
    }
  }
}

/** Moves by `d` chunks (negative = back). At the first chunk it starts that chunk again. */
function step(d: number): void {
  const s = ses;
  if (!s || !s.ch || !s.chunks.length) return;
  const to = Math.max(0, Math.min(s.chunks.length - 1, (s.ci >= s.chunks.length ? s.chunks.length - 1 : s.ci) + d));
  if (state.status === 'paused' || state.status === 'error') {
    // stay paused, only move the position
    gen++;
    clearTimers();
    stopAll();
    held = false;
    s.ci = to;
    s.si = 0;
    setState({ status: 'paused', para: (s.chunks[to] as Chunk).p });
    publishMark(s);
    saveListen(s);
    return;
  }
  void run(to, 0);
}

/** Goes to another chapter of the story being played (bounds are the player's own chapter, not the page's). */
function gotoChapter(idx: number): void {
  const s = ses;
  if (!s) return;
  if (idx < 0) return;
  if (idx >= s.story.chapters.length) {
    toast('Đã hết truyện');
    return;
  }
  void load(s.story, idx, -1, true);
}

/** Starts listening to a paragraph of the chapter that is playing (used by the reader). */
function seekPara(para: number): void {
  const s = ses;
  if (!s || !s.ch) return;
  void run(startChunk(s.chunks, para), 0);
}

// ---------------------------------------------------------------- sleep timer

function clearSleep(): void {
  if (sleepTimer !== undefined) clearTimeout(sleepTimer);
  sleepTimer = undefined;
  sleep = 0;
  sleepAt = 0;
}

function setSleep(mode: SleepMode): void {
  clearSleep();
  if (mode === -1) {
    sleep = -1;
    toast('Sẽ dừng khi hết chương');
  } else if (mode > 0) {
    sleep = mode;
    sleepAt = Date.now() + mode * 60_000;
    sleepTimer = setTimeout(() => {
      clearSleep();
      pause();
      toast('Đã dừng theo hẹn giờ');
      changes.emit();
    }, mode * 60_000);
    toast(`Sẽ dừng sau ${mode} phút`);
  }
  changes.emit();
}

// ---------------------------------------------------------------- media session

function syncMediaState(): void {
  if (typeof navigator === 'undefined' || !('mediaSession' in navigator)) return;
  try {
    navigator.mediaSession.playbackState = state.status === 'idle' ? 'none' : state.status === 'playing' || state.status === 'loading' ? 'playing' : 'paused';
  } catch {
    // not supported
  }
}

let mediaBound = false;
function syncMediaMeta(s: Session): void {
  if (typeof navigator === 'undefined' || !('mediaSession' in navigator) || typeof MediaMetadata === 'undefined') return;
  const ms = navigator.mediaSession;
  const meta = (artwork: MediaImage[]): void => {
    try {
      ms.metadata = new MediaMetadata({ title: chapterLabel(s.ref), artist: s.story.name, album: 'MythLab Truyện', artwork });
    } catch {
      // not supported
    }
  };
  const svg = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(String(genCover(s.story)));
  meta([{ src: svg, sizes: '512x512', type: 'image/svg+xml' }]);
  try {
    void Promise.resolve(backend.coverUrl(s.story, 512))
      .then((u) => {
        if (u && ses === s) meta([{ src: new URL(u, location.href).href, sizes: '512x512' }]);
      })
      .catch(() => {});
  } catch {
    // keep the generated cover
  }
  if (mediaBound) return;
  mediaBound = true;
  const bind = (action: MediaSessionAction, fn: () => void): void => {
    try {
      ms.setActionHandler(action, fn);
    } catch {
      // this action is not supported here
    }
  };
  bind('play', resume);
  bind('pause', pause);
  bind('stop', stop);
  bind('nexttrack', () => ses && gotoChapter(ses.idx + 1));
  bind('previoustrack', () => ses && gotoChapter(ses.idx - 1));
  bind('seekforward', () => step(1));
  bind('seekbackward', () => step(-1));
}

// ---------------------------------------------------------------- settings

/** Speaks the current sentence again with the new settings (when something is being spoken). */
function respeak(rebuildChunks: boolean): void {
  const s = ses;
  if (!s || !s.ch) return;
  const para = paraNow(s);
  const keep = !rebuildChunks && s.max === chunkMax();
  const si = keep ? s.si : 0;
  if (!keep) {
    const done = s.ci >= s.chunks.length;
    rebuild(s, para);
    if (done) s.ci = s.chunks.length;
  }
  if (state.status === 'playing') void run(s.ci, si);
  else if (state.status === 'paused') {
    // paused: drop the held clip so the next play uses the new settings
    gen++;
    stopAll();
    held = false;
    s.si = si;
    changes.emit();
  }
}

settings.onChange((key) => {
  if (state.status === 'idle') return;
  if (key === 'rate') {
    edgeRate(S.rate);
    // device voices take the speed when an utterance starts
    if (state.engine !== 'edge' && state.status === 'playing') respeak(false);
    changes.emit();
    return;
  }
  if (key === 'pitch') {
    // whichever engine is speaking right now (also the device voice standing in for the server voice)
    if (pitchTimer !== undefined) clearTimeout(pitchTimer);
    pitchTimer = setTimeout(() => {
      pitchTimer = undefined;
      edgeForget();
      respeak(false);
    }, 350);
    return;
  }
  if (key === 'engine' || key === null) {
    edgeDown = false;
    edgeFails = 0;
  }
  if (key === 'engine' || key === 'voice' || key === 'browserVoice' || key === 'nativeVoice' || key === null) {
    edgeForget();
    respeak(true);
  } else if (key === 'ttsClean' || key === 'readTitle') respeak(true);
});

// ---------------------------------------------------------------- public face

function info(): PlayerInfo {
  const s = ses;
  return {
    chunk: s ? Math.min(s.ci, Math.max(0, s.chunks.length - 1)) : 0,
    chunks: s ? s.chunks.length : 0,
    total: s ? s.story.chapters.length : 0,
    sleep,
    sleepAt,
    fallback: !!s && S.engine === 'edge' && state.engine !== undefined && state.engine !== 'edge',
  };
}

function matches(source: string, key: string, idx?: number): boolean {
  return state.status !== 'idle' && state.source === source && state.key === key && (idx == null || state.idx === idx);
}

export interface Player extends PlayerApi {
  /** Like `play`, with `exact: true` to start at exactly the requested paragraph (no "continue listening"). */
  start(req: PlayRequest & { exact?: boolean }): Promise<void>;
  /** Moves by `d` chunks. */
  step(d: number): void;
  /** Another chapter of the story being played. */
  gotoChapter(idx: number): void;
  /** Jumps to a paragraph of the chapter being played. */
  seekPara(para: number): void;
  /** 0 = off, -1 = at the end of the chapter, n = minutes. */
  setSleep(mode: SleepMode): void;
  info(): PlayerInfo;
  /** Fires on every change the dock shows (state, position, sleep timer). */
  onChange(fn: () => void): () => void;
}

export const player: Player = {
  play: (req) => start(req),
  start,
  toggle,
  pause,
  resume,
  stop,
  step,
  gotoChapter,
  seekPara,
  setSleep,
  info,
  getState: () => state,
  onState: (fn) => stateChanges.on(fn),
  onChange: (fn) => changes.on(fn),
  matches,
};

// the dock draws itself from the player
initDock(player);
