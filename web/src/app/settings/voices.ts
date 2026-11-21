/**
 * Voice picker logic of the settings sheet: which engines exist on this host with the current data source, which
 * one will really speak, and the voice list of an engine. The saved `engine` setting is never rewritten behind
 * the user's back: on GitHub-direct (no server voices) the picker shows the device voices and says why.
 */
import { backend } from '../core/backend/index';
import type { Voice, VoicesResponse } from '../core/backend/types';
import { data } from '../core/data';
import type { Settings, TtsEngine } from '../core/settings';

export interface EngineEnv {
  /** Active data source. */
  kind: 'server' | 'github' | 'none';
  /** `/api/sources` → tts.edge (false = the server says its voices are down). */
  edge: boolean;
  /** `speechSynthesis` exists. */
  browser: boolean;
  /** Capacitor text-to-speech plugin exists. */
  native: boolean;
}

export interface EngineChoice {
  id: TtsEngine;
  label: string;
  available: boolean;
  /** Why it cannot be used here (shown under the picker). */
  reason?: string;
}

/** The engines to show, in display order. Edge is always listed so the user sees why it is unavailable. */
export function engineChoices(env: EngineEnv): EngineChoice[] {
  const out: EngineChoice[] = [];
  const edgeOk = env.kind === 'server' && env.edge;
  out.push({
    id: 'edge',
    label: 'Edge (tự nhiên)',
    available: edgeOk,
    reason: edgeOk ? undefined : env.kind === 'server' ? 'Máy chủ báo dịch vụ giọng Edge đang không dùng được.' : 'Giọng Edge cần máy chủ MythLab. Khi đọc trực tiếp từ GitHub, ứng dụng dùng giọng của thiết bị.',
  });
  if (env.browser || !env.native) out.push({ id: 'browser', label: 'Trình duyệt', available: env.browser, reason: env.browser ? undefined : 'Trình duyệt này không hỗ trợ đọc thành tiếng.' });
  if (env.native) out.push({ id: 'native', label: 'Máy (Android)', available: true });
  return out;
}

/** The engine that will speak with the saved choice: the choice itself when usable, else the device voice. */
export function effectiveEngine(saved: TtsEngine, env: EngineEnv): TtsEngine | null {
  const ok = (id: TtsEngine): boolean => engineChoices(env).some((c) => c.id === id && c.available);
  if (ok(saved)) return saved;
  if (saved !== 'native' && ok('browser')) return 'browser';
  if (ok('native')) return 'native';
  if (ok('browser')) return 'browser';
  return ok('edge') ? 'edge' : null;
}

/** The setting that stores the voice of an engine. */
export const voiceKey = (engine: TtsEngine): 'voice' | 'browserVoice' | 'nativeVoice' => (engine === 'edge' ? 'voice' : engine === 'browser' ? 'browserVoice' : 'nativeVoice');

export interface VoiceItem {
  id: string;
  label: string;
  vi: boolean;
}

const isVi = (lang: string | undefined): boolean => /^vi\b/i.test(String(lang || '').replace('_', '-'));

/** "Microsoft HoaiMy Online (Natural) - Vietnamese (Vietnam)" → "HoaiMy - Vietnamese (Vietnam)". */
export const cleanVoiceName = (name: string): string =>
  String(name || '')
    .replace(/^Microsoft\s+/i, '')
    .replace(/\s+Online\s*\(Natural\)/i, '')
    .trim();

/** Edge voices as "{name} — {id}"; device voices as "{name} ({lang})", Vietnamese first. */
export function voiceItems(engine: TtsEngine, raw: { id: string; name?: string; lang?: string }[]): VoiceItem[] {
  if (engine === 'edge') {
    return raw.map((v) => {
      const name = cleanVoiceName(v.name || '');
      return { id: v.id, label: name && name !== v.id ? `${name} — ${v.id}` : v.id, vi: isVi(v.lang || v.id) };
    });
  }
  return raw
    .map((v) => ({ id: v.id, label: `${cleanVoiceName(v.name || v.id)}${v.lang ? ` (${v.lang})` : ''}`, vi: isVi(v.lang) }))
    .sort((a, b) => Number(b.vi) - Number(a.vi) || a.label.localeCompare(b.label));
}

export interface VoiceSelection {
  /** Value the `<select>` shows. '' = "automatic" (device engines only). */
  value: string;
  /** Voice id to store because the saved one does not exist (Edge only), else null. */
  store: string | null;
}

/**
 * What to select for the saved voice. Edge needs a real voice id: a missing one is replaced by the first
 * Vietnamese voice. Device engines keep '' = "let the device choose a Vietnamese voice".
 */
export function selectVoice(engine: TtsEngine, items: VoiceItem[], saved: string): VoiceSelection {
  if (items.some((v) => v.id === saved)) return { value: saved, store: null };
  if (engine !== 'edge') return { value: '', store: null };
  const first = items.find((v) => v.vi) || items[0];
  return first ? { value: first.id, store: first.id } : { value: '', store: null };
}

// ---------------------------------------------------------------- host access

interface NativeVoice {
  voiceURI: string;
  name?: string;
  lang: string;
}
interface NativeTts {
  getSupportedVoices(): Promise<{ voices?: NativeVoice[] }>;
}
const nativeTts = (): NativeTts | null => (globalThis as { Capacitor?: { Plugins?: { TextToSpeech?: NativeTts } } }).Capacitor?.Plugins?.TextToSpeech ?? null;
const synth = (): SpeechSynthesis | null => (typeof speechSynthesis !== 'undefined' && typeof SpeechSynthesisUtterance !== 'undefined' ? speechSynthesis : null);

/** Reads the environment; asks the server whether its voices work (cached by core/data). */
export async function readEnv(): Promise<EngineEnv> {
  const kind = backend.kind;
  let edge = false;
  if (kind === 'server') {
    try {
      const r = await data.sources();
      edge = r.tts ? r.tts.edge !== false : true;
    } catch {
      // the list of voices decides below; an unreachable server has none
      edge = false;
    }
  }
  return { kind, edge, browser: !!synth(), native: !!nativeTts() };
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

/** The voices of an engine, ready for the picker. Never throws. */
export async function listVoices(engine: TtsEngine): Promise<VoiceItem[]> {
  try {
    if (engine === 'edge') {
      if (backend.kind !== 'server') return [];
      const r = await backend.get<VoicesResponse>('/voices', { timeout: 20_000 });
      return voiceItems(
        'edge',
        (r.voices || []).map((v: Voice) => ({ id: v.id, name: v.name, lang: v.id.slice(0, 5) })),
      );
    }
    if (engine === 'native') {
      const r = await nativeTts()
        ?.getSupportedVoices()
        .catch(() => ({ voices: [] as NativeVoice[] }));
      return voiceItems(
        'native',
        (r?.voices || []).map((v) => ({ id: v.voiceURI, name: v.name || v.voiceURI, lang: v.lang })),
      );
    }
    return voiceItems(
      'browser',
      (await browserVoices()).map((v) => ({ id: v.voiceURI, name: v.name, lang: v.lang })),
    );
  } catch {
    return [];
  }
}

let previewAudio: HTMLAudioElement | null = null;
let previewUrl = '';

/** Stops a running voice preview. */
export function stopPreview(): void {
  try {
    previewAudio?.pause();
    previewAudio = null;
    if (previewUrl) backend.releaseUrl(previewUrl);
    previewUrl = '';
    synth()?.cancel();
  } catch {
    /* nothing was playing */
  }
}

export const PREVIEW_TEXT = 'Xin chào, đây là giọng đọc truyện của MythLab.';

/** Speaks a short sample with the chosen engine and voice. Rejects when the engine cannot speak. */
export async function preview(engine: TtsEngine, s: Pick<Settings, 'voice' | 'browserVoice' | 'rate' | 'pitch'>): Promise<void> {
  stopPreview();
  if (engine === 'edge') {
    const src = await backend.ttsSrc({ text: PREVIEW_TEXT, voice: s.voice });
    previewUrl = src;
    const a = new Audio(src);
    a.playbackRate = s.rate;
    previewAudio = a;
    await a.play();
    return;
  }
  const sy = synth();
  if (engine !== 'browser' || !sy) throw new Error('no preview');
  const u = new SpeechSynthesisUtterance(PREVIEW_TEXT);
  const all = sy.getVoices();
  const v = all.find((x) => x.voiceURI === s.browserVoice) || all.find((x) => isVi(x.lang));
  if (v) u.voice = v;
  u.lang = v?.lang || 'vi-VN';
  u.rate = Math.min(2, s.rate);
  u.pitch = s.pitch;
  sy.speak(u);
}
