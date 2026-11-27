/**
 * Voice picker logic of the settings sheet: which engines exist on this host, which one will really speak, and the
 * voice list of an engine. Only Vietnamese voices are ever listed. The saved `engine` setting is never rewritten
 * behind the user's back: when it cannot speak here the picker shows the other engine and says why.
 */
import { piperSupported, type Settings, type TtsEngine } from '../core/settings';
import { isNativeIOS } from '../core/native-platform';
import { DEFAULT_PIPER_VOICE, piperChoice, piperChoiceLabel, piperInstalled, piperSynth, PIPER_CHOICES } from '../player/piper';

export interface EngineEnv {
  /** Capacitor text-to-speech plugin exists. */
  native: boolean;
  /** The native engine is the iOS app's (labels only). */
  ios?: boolean;
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
  if (env.native) out.push({ id: 'native', label: env.ios ? 'Máy (iPhone/iPad)' : 'Máy (Android)', available: true });
  out.push({
    id: 'piper',
    label: 'Piper (offline)',
    available: !!env.piper,
    reason: env.piper ? undefined : 'Thiết bị này không chạy được giọng Piper (cần WebAssembly).',
  });
  return out;
}

/** The engine that will speak with the saved choice: the choice itself when usable, else the other one that is. */
export function effectiveEngine(saved: TtsEngine, env: EngineEnv): TtsEngine | null {
  const ok = (id: TtsEngine): boolean => engineChoices(env).some((c) => c.id === id && c.available);
  if (ok(saved)) return saved;
  if (ok('native')) return 'native';
  if (ok('piper')) return 'piper';
  return null;
}

/** The setting that stores the voice of an engine. */
export const voiceKey = (engine: TtsEngine): 'nativeVoice' | 'piperVoice' => (engine === 'piper' ? 'piperVoice' : 'nativeVoice');

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

/** Reads the environment. */
export function readEnv(): EngineEnv {
  return { native: !!nativeTts(), piper: piperSupported(), ios: isNativeIOS() };
}

/** The Piper voices (gender, download size, lightest first) and whether their model is already on this device. */
export const piperItems = (): VoiceItem[] => PIPER_CHOICES.map((c) => ({ id: c.id, label: piperChoiceLabel(c, piperInstalled(c.model.id)) }));

/** The Vietnamese voices of an engine, ready for the picker. Never throws. */
export async function listVoices(engine: TtsEngine): Promise<VoiceItem[]> {
  try {
    if (engine === 'piper') return piperItems();
    const r = await nativeTts()
      ?.getSupportedVoices()
      .catch(() => ({ voices: [] as NativeVoice[] }));
    return voiceItems((r?.voices || []).map((v) => ({ id: v.voiceURI, name: v.name || v.voiceURI, lang: v.lang })));
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
  } catch {
    /* nothing was playing */
  }
}

export const PREVIEW_TEXT = 'Xin chào, đây là giọng đọc truyện của MythLab.';

/** Speaks a short sample with the chosen engine and voice. Rejects when the engine cannot speak. */
export async function preview(engine: TtsEngine, s: Pick<Settings, 'piperVoice' | 'rate' | 'pitch'>): Promise<void> {
  stopPreview();
  if (engine !== 'piper') throw new Error('no preview');
  if (!piperInstalled(piperChoice(s.piperVoice).model.id)) throw new Error('Chưa tải giọng Piper');
  const url = URL.createObjectURL(await piperSynth(PREVIEW_TEXT, s.piperVoice));
  previewUrl = url;
  const a = new Audio(url);
  a.playbackRate = s.rate;
  previewAudio = a;
  await a.play();
}
