/**
 * Voice picker logic of the settings sheet: which engines exist on this host, which one will really speak, and the
 * voice list of an engine. Only Vietnamese voices are ever listed. The saved `engine` setting is never rewritten
 * behind the user's back: when it cannot speak here the picker shows the device voices and says why.
 */
import { piperSupported, type Settings, type TtsEngine } from '../core/settings';
import { DEFAULT_PIPER_VOICE, piperChoice, piperChoiceLabel, piperInstalled, piperSynth, PIPER_CHOICES } from '../player/piper';

export interface EngineEnv {
  /** `speechSynthesis` exists. */
  browser: boolean;
  /** Capacitor text-to-speech plugin exists. */
  native: boolean;
  /** Piper can run here (WebAssembly + Worker + Cache API). Missing = no. */
  piper?: boolean;
}

export interface EngineChoice {
  id: TtsEngine;
  label: string;
  available: boolean;
  /** Why it cannot be used here (shown under the picker). */
  reason?: string;
}

/** The engines to show, in display order. */
export function engineChoices(env: EngineEnv): EngineChoice[] {
  const out: EngineChoice[] = [];
  if (env.browser || !env.native) out.push({ id: 'browser', label: 'Trình duyệt', available: env.browser, reason: env.browser ? undefined : 'Trình duyệt này không hỗ trợ đọc thành tiếng.' });
  if (env.native) out.push({ id: 'native', label: 'Máy (Android)', available: true });
  out.push({
    id: 'piper',
    label: 'Piper (offline)',
    available: !!env.piper,
    reason: env.piper ? undefined : 'Thiết bị này không chạy được giọng Piper (cần WebAssembly).',
  });
  return out;
}

/** The engine that will speak with the saved choice: the choice itself when usable, else the device voice. */
export function effectiveEngine(saved: TtsEngine, env: EngineEnv): TtsEngine | null {
  const ok = (id: TtsEngine): boolean => engineChoices(env).some((c) => c.id === id && c.available);
  if (ok(saved)) return saved;
  if (saved !== 'native' && ok('browser')) return 'browser';
  if (ok('native')) return 'native';
  if (ok('browser')) return 'browser';
  return null;
}

/** The setting that stores the voice of an engine. */
export const voiceKey = (engine: TtsEngine): 'browserVoice' | 'nativeVoice' | 'piperVoice' => (engine === 'browser' ? 'browserVoice' : engine === 'piper' ? 'piperVoice' : 'nativeVoice');

export interface VoiceItem {
  id: string;
  label: string;
}

/** True for a Vietnamese language tag: vi, vi-VN, vi_VN. */
export const isVi = (lang: string | undefined): boolean => /^vi\b/i.test(String(lang || '').replace('_', '-'));

/** "Microsoft HoaiMy Online (Natural) - Vietnamese (Vietnam)" → "HoaiMy - Vietnamese (Vietnam)". */
export const cleanVoiceName = (name: string): string =>
  String(name || '')
    .replace(/^Microsoft\s+/i, '')
    .replace(/\s+Online\s*\(Natural\)/i, '')
    .trim();

/** Device voices as "{name} ({lang})": the Vietnamese ones only, sorted by name. */
export function voiceItems(raw: { id: string; name?: string; lang?: string }[]): VoiceItem[] {
  return raw
    .filter((v) => isVi(v.lang))
    .map((v) => ({ id: v.id, label: `${cleanVoiceName(v.name || v.id)}${v.lang ? ` (${v.lang})` : ''}` }))
    .sort((a, b) => a.label.localeCompare(b.label));
}

export interface VoiceSelection {
  /** Value the `<select>` shows. '' = "automatic" (device engines only). */
  value: string;
  /** Voice id to store because the saved one does not exist (Piper only), else null. */
  store: string | null;
}

/**
 * What to select for the saved voice. Piper needs a real voice id: a missing one is replaced by the default voice.
 * Device engines keep '' = "let the device choose a Vietnamese voice" when the saved voice is not in the list.
 */
export function selectVoice(engine: TtsEngine, items: VoiceItem[], saved: string): VoiceSelection {
  if (items.some((v) => v.id === saved)) return { value: saved, store: null };
  if (engine !== 'piper') return { value: '', store: null };
  const first = items.find((v) => v.id === DEFAULT_PIPER_VOICE) ?? items[0];
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

/** Reads the environment. */
export function readEnv(): EngineEnv {
  return { browser: !!synth(), native: !!nativeTts(), piper: piperSupported() };
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

/** The Piper voices (gender, download size, lightest first) and whether their model is already on this device. */
export const piperItems = (): VoiceItem[] => PIPER_CHOICES.map((c) => ({ id: c.id, label: piperChoiceLabel(c, piperInstalled(c.model.id)) }));

/** The Vietnamese voices of an engine, ready for the picker. Never throws. */
export async function listVoices(engine: TtsEngine): Promise<VoiceItem[]> {
  try {
    if (engine === 'piper') return piperItems();
    if (engine === 'native') {
      const r = await nativeTts()
        ?.getSupportedVoices()
        .catch(() => ({ voices: [] as NativeVoice[] }));
      return voiceItems((r?.voices || []).map((v) => ({ id: v.voiceURI, name: v.name || v.voiceURI, lang: v.lang })));
    }
    return voiceItems((await browserVoices()).map((v) => ({ id: v.voiceURI, name: v.name, lang: v.lang })));
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
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = '';
    synth()?.cancel();
  } catch {
    /* nothing was playing */
  }
}

export const PREVIEW_TEXT = 'Xin chào, đây là giọng đọc truyện của MythLab.';

/** Speaks a short sample with the chosen engine and voice. Rejects when the engine cannot speak. */
export async function preview(engine: TtsEngine, s: Pick<Settings, 'browserVoice' | 'piperVoice' | 'rate' | 'pitch'>): Promise<void> {
  stopPreview();
  if (engine === 'piper') {
    if (!piperInstalled(piperChoice(s.piperVoice).model.id)) throw new Error('Chưa tải giọng Piper');
    const url = URL.createObjectURL(await piperSynth(PREVIEW_TEXT, s.piperVoice));
    previewUrl = url;
    const a = new Audio(url);
    a.playbackRate = s.rate;
    previewAudio = a;
    await a.play();
    return;
  }
  const sy = synth();
  if (engine !== 'browser' || !sy) throw new Error('no preview');
  const u = new SpeechSynthesisUtterance(PREVIEW_TEXT);
  const all = sy.getVoices().filter((x) => isVi(x.lang));
  const v = all.find((x) => x.voiceURI === s.browserVoice) || all[0];
  if (v) u.voice = v;
  u.lang = v?.lang || 'vi-VN';
  u.rate = Math.min(2, s.rate);
  u.pitch = s.pitch;
  sy.speak(u);
}
