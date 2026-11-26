/**
 * Piper: free Vietnamese neural voices that run ON THE USER'S DEVICE (WebAssembly in a Web Worker), so the server
 * never synthesises anything. Nothing here runs at startup: the runtime (public/tts/, copied from npm by
 * scripts/copy-tts.mjs) and the model are only loaded after the user chose Piper and downloaded a voice.
 *
 *   model files   downloaded once from the Piper voice repository (or the GitHub release), kept in the Cache API (never localStorage)
 *   worker        public/tts/piper-worker.js: espeak-ng phonemizer + onnxruntime-web, one chunk at a time
 *   result        a 16-bit WAV blob URL that the player's <audio> element plays like any audio clip
 */
import { piperSupported, S } from '../core/settings';
import { fetchVerified, type Artifact } from './piper-fetch';

export { piperSupported };

export interface PiperVoice {
  id: string;
  /** Shown in the picker. */
  name: string;
  /** Path below the voice repository, with the trailing slash. */
  path: string;
  /** Exact size of the .onnx file (also the integrity check). */
  bytes: number;
  /** SHA-256 of the .onnx file (hex); checked after the download when the browser has crypto.subtle. */
  sha256: string;
  /** Size and SHA-256 of the small .onnx.json config next to the model. */
  configBytes: number;
  configSha256: string;
  sampleRate: number;
  /** One line about quality / licence. */
  note: string;
}

/** Pinned to a commit of the voice repository, so the files cannot change under the size / hash below. */
const REPO = 'https://huggingface.co/rhasspy/piper-voices/resolve/5ec43b186ef915a195d3ddbcfd9916e76c503c3f/vi/vi_VN/';

/** Second source: assets of the "piper-models" GitHub release of this repository (same files as the pinned commit). */
export const RELEASE_URL = 'https://github.com/quangminh1212/MythLab/releases/download/piper-models/';

/** The Vietnamese voices. The first one is the default: its data (VAIS-1000) is CC BY 4.0, free for any use. */
export const PIPER_VOICES: readonly PiperVoice[] = [
  { id: 'vi_VN-vais1000-medium', name: 'Vais1000 — chất lượng cao', path: 'vais1000/medium/', bytes: 63_221_984, sha256: '0567643f67b8329a46b3f0b549befc58e1e7e21ef558677768068d23a41d8471', configBytes: 6197, configSha256: '19240ab1eb13e5eb9c7dd00f9d1de5db08ff88d591c5008cbd24f1a25f51e13a', sampleRate: 22050, note: 'CC BY 4.0' },
  { id: 'vi_VN-25hours_single-low', name: '25 giờ — một giọng', path: '25hours_single/low/', bytes: 63_104_526, sha256: '266945c4a80cb3301450c8ba6fcf6ba3542c56cf952a08a8ff3d2d4ff0ab5609', configBytes: 4176, configSha256: '344b5849f5bc585031a63b9cc75f96e2c469f3d98879d8d3acbc2fce6d470064', sampleRate: 16000, note: 'chất lượng vừa' },
  { id: 'vi_VN-vivos-x_low', name: 'Vivos — nhẹ', path: 'vivos/x_low/', bytes: 27_789_413, sha256: '6ab13374eb0862021a545befe7727aef59e16117f1c075aa9e0362237ecc98ae', configBytes: 5592, configSha256: '9dc373d69b0e4f39d864cb8ac9fe42cee49817a0f02d831e57a9ce6e944e234a', sampleRate: 16000, note: 'gọn nhất, chỉ dùng phi thương mại (CC BY-NC-SA)' },
];

export const DEFAULT_PIPER_VOICE = (PIPER_VOICES[0] as PiperVoice).id;

/** The voice for a saved id; an unknown id (older / newer app) gives the default. */
export const piperVoice = (id: string | undefined): PiperVoice => PIPER_VOICES.find((v) => v.id === id) ?? (PIPER_VOICES[0] as PiperVoice);

export const piperModelUrl = (v: PiperVoice): string => `${REPO}${v.path}${v.id}.onnx`;
export const piperConfigUrl = (v: PiperVoice): string => `${piperModelUrl(v)}.json`;

/** File names of a voice: "vi_VN-vais1000-medium.onnx" and its ".json". */
const modelFile = (v: PiperVoice): string => `${v.id}.onnx`;

/** Ordered download sources of a file of a voice (`suffix` is '' for the model, '.json' for the config). */
export function piperSources(v: PiperVoice, suffix = ''): string[] {
  const file = modelFile(v) + suffix;
  return [`${REPO}${v.path}${file}`, RELEASE_URL + file];
}

const modelArtifact = (v: PiperVoice): Artifact => ({ name: 'giọng ' + v.name, bytes: v.bytes, sha256: v.sha256, sources: piperSources(v) });
const configArtifact = (v: PiperVoice): Artifact => ({ name: 'cấu hình giọng', bytes: v.configBytes, sha256: v.configSha256, sources: piperSources(v, '.json') });

/** "63 MB" */
export const megabytes = (bytes: number): string => `${Math.round(bytes / 1e6)} MB`;

/** Picker label: "Vais1000 — chất lượng cao · 63 MB · đã tải". */
export const piperVoiceLabel = (v: PiperVoice, installed: boolean): string => `${v.name} · ${megabytes(v.bytes)}${installed ? ' · đã tải' : ''}`;

/** Float PCM (-1..1) as a 16-bit mono WAV file. */
export function wavFromPcm(pcm: Float32Array, sampleRate: number): ArrayBuffer {
  const buf = new ArrayBuffer(44 + pcm.length * 2);
  const v = new DataView(buf);
  const tag = (at: number, s: string): void => {
    for (let i = 0; i < s.length; i++) v.setUint8(at + i, s.charCodeAt(i));
  };
  tag(0, 'RIFF');
  v.setUint32(4, 36 + pcm.length * 2, true);
  tag(8, 'WAVE');
  tag(12, 'fmt ');
  v.setUint32(16, 16, true);
  v.setUint16(20, 1, true); // PCM
  v.setUint16(22, 1, true); // mono
  v.setUint32(24, sampleRate, true);
  v.setUint32(28, sampleRate * 2, true);
  v.setUint16(32, 2, true);
  v.setUint16(34, 16, true);
  tag(36, 'data');
  v.setUint32(40, pcm.length * 2, true);
  for (let i = 0; i < pcm.length; i++) {
    const x = Math.max(-1, Math.min(1, pcm[i] as number));
    v.setInt16(44 + i * 2, x < 0 ? x * 0x8000 : x * 0x7fff, true);
  }
  return buf;
}

// ---------------------------------------------------------------- installed models (Cache API)

const CACHE = 'mythlab-piper-v1';
const installed = new Set<string>();

/** True when the voice's files are stored on this device (known after refreshPiper()). */
export const piperInstalled = (id: string): boolean => installed.has(id);

/** True when the saved Piper voice can speak right now (supported here and downloaded). */
export const piperReady = (): boolean => piperSupported() && installed.has(piperVoice(S.piperVoice).id);

/** Looks into the cache for downloaded voices. Cheap, never throws, never loads the runtime. */
export async function refreshPiper(): Promise<void> {
  if (!piperSupported()) return;
  try {
    const c = await caches.open(CACHE);
    for (const v of PIPER_VOICES) {
      const [m, j] = await Promise.all([c.match(piperModelUrl(v)), c.match(piperConfigUrl(v))]);
      if (m && j) installed.add(v.id);
      else installed.delete(v.id);
    }
  } catch {
    // private window / blocked storage: nothing is installed
  }
}

/**
 * Downloads a voice into the cache (once) from the first working source (Hugging Face, then the GitHub
 * release). `onProgress` gets 0..1 of the current source and restarts at 0 when the next source starts, which
 * `onSource` announces. Rejects when every source fails; a bad or half download is never kept.
 */
export async function installPiper(
  id: string,
  onProgress?: (done: number) => void,
  signal?: AbortSignal,
  onSource?: (index: number, total: number) => void,
): Promise<void> {
  const v = piperVoice(id);
  if (!piperSupported()) throw new Error('Thiết bị này không chạy được giọng Piper');
  const cache = await caches.open(CACHE);
  const cfg = await fetchVerified(configArtifact(v), { signal, onSource: (i, n) => onSource?.(i, n) });
  const cfgBody = await cfg.blob.arrayBuffer();
  const model = await fetchVerified(modelArtifact(v), { onProgress, signal, onSource: (i, n) => onSource?.(i, n) });
  const blob = model.blob;
  try {
    await cache.put(piperModelUrl(v), new Response(blob, { headers: { 'content-type': 'application/octet-stream' } }));
    await cache.put(piperConfigUrl(v), new Response(cfgBody, { headers: { 'content-type': 'application/json' } }));
  } catch (e) {
    await removePiper(id);
    throw new Error(`Không đủ chỗ lưu giọng trên máy (${(e as Error).message || e})`);
  }
  installed.add(v.id);
  try {
    // keep the voice when the device is short of space
    await navigator.storage?.persist?.();
  } catch {
    // best effort
  }
}

/** Deletes a downloaded voice (and frees the worker when it was the loaded one). */
export async function removePiper(id: string): Promise<void> {
  const v = piperVoice(id);
  installed.delete(v.id);
  if (loaded === v.id) piperShutdown();
  try {
    const c = await caches.open(CACHE);
    await Promise.all([c.delete(piperModelUrl(v)), c.delete(piperConfigUrl(v))]);
  } catch {
    // nothing stored
  }
}

// ---------------------------------------------------------------- worker

interface Pending {
  resolve(v: unknown): void;
  reject(e: Error): void;
}

let worker: Worker | null = null;
let loaded = '';
let loading: Promise<void> | null = null;
let seq = 0;
const pending = new Map<number, Pending>();

const runtimeBase = (): string => new URL('tts/', document.baseURI).href;

function spawn(): Worker {
  if (worker) return worker;
  const w = new Worker(new URL('piper-worker.js', runtimeBase()));
  w.onmessage = (e: MessageEvent<{ id: number; err?: string } & Record<string, unknown>>) => {
    const p = pending.get(e.data.id);
    if (!p) return;
    pending.delete(e.data.id);
    if (e.data.err) p.reject(new Error(e.data.err));
    else p.resolve(e.data);
  };
  w.onerror = (e) => fail(new Error(e.message || 'Bộ đọc Piper bị lỗi'));
  worker = w;
  return w;
}

function fail(e: Error): void {
  clearTimeout(idle);
  for (const p of pending.values()) p.reject(e);
  pending.clear();
  worker?.terminate();
  worker = null;
  loaded = '';
  loading = null;
}

/** The worker holds about 100 MB: it is stopped when nothing was synthesised for a while (clips already made stay). */
const IDLE_MS = 90_000;
let idle: ReturnType<typeof setTimeout> | undefined;

function touch(): void {
  clearTimeout(idle);
  idle = setTimeout(() => {
    if (pending.size) return touch();
    fail(new Error('idle'));
  }, IDLE_MS);
}

function call<T>(msg: Record<string, unknown>, transfer: Transferable[] = []): Promise<T> {
  touch();
  const id = ++seq;
  return new Promise<T>((resolve, reject) => {
    pending.set(id, { resolve: resolve as (v: unknown) => void, reject });
    spawn().postMessage({ ...msg, id }, transfer);
  });
}

/** Stops the worker and frees its memory (the model is about 60 MB in RAM). */
export function piperShutdown(): void {
  forget();
  fail(new Error('stopped'));
}

/** Makes the worker hold the model of a voice. Loads the runtime on first use. */
function load(v: PiperVoice): Promise<void> {
  if (loaded === v.id) return Promise.resolve();
  if (loading) return loading.then(() => load(v));
  loading = (async () => {
    const cache = await caches.open(CACHE);
    const [m, j] = await Promise.all([cache.match(piperModelUrl(v)), cache.match(piperConfigUrl(v))]);
    if (!m || !j) {
      installed.delete(v.id);
      throw new Error('Chưa tải giọng Piper');
    }
    const [model, config] = await Promise.all([m.arrayBuffer(), j.json()]);
    await call({ t: 'init', base: runtimeBase(), model, config }, [model]);
    loaded = v.id;
  })();
  const mine = loading;
  void mine.then(
    () => {
      if (loading === mine) loading = null;
    },
    () => {
      if (loading === mine) loading = null;
    },
  );
  return mine;
}

/** Synthesises text with a voice. Resolves with a WAV blob. */
export async function piperSynth(text: string, id: string): Promise<Blob> {
  const v = piperVoice(id);
  await load(v);
  const r = await call<{ pcm: Float32Array; rate: number }>({ t: 'synth', text });
  return new Blob([wavFromPcm(r.pcm, r.rate || v.sampleRate)], { type: 'audio/wav' });
}

// ---------------------------------------------------------------- prepared clips

/** Clips of the chunks about to be played: at most KEEP, object URLs are released on eviction. */
const KEEP = 3;
const clips = new Map<string, Promise<string>>();

const key = (text: string): string => `${piperVoice(S.piperVoice).id}|${text}`;

function drop(k: string): void {
  const p = clips.get(k);
  clips.delete(k);
  void p?.then((u) => URL.revokeObjectURL(u)).catch(() => {});
}

/** Blob URL of the audio of a chunk (synthesised once, shared by prefetch and playback). */
export function piperSource(text: string): Promise<string> {
  const k = key(text);
  const had = clips.get(k);
  if (had) {
    clips.delete(k);
    clips.set(k, had);
    return had;
  }
  const p = piperSynth(text, S.piperVoice).then((b) => URL.createObjectURL(b));
  clips.set(k, p);
  p.catch(() => {
    if (clips.get(k) === p) clips.delete(k);
  });
  while (clips.size > KEEP) drop(clips.keys().next().value as string);
  return p;
}

/** Synthesises a chunk that will be played soon, so chunks follow each other without a gap. */
export function piperPrefetch(text: string | undefined): void {
  if (text && piperReady()) void piperSource(text).catch(() => {});
}

/** Forgets every prepared clip (voice changed, player closed). */
export function forget(): void {
  for (const k of [...clips.keys()]) drop(k);
}

export const PIPER_SIZE_NOTE = 'Giọng Piper chạy ngay trên máy bạn, không dùng máy chủ. Lần đầu cần tải về một lần (cộng khoảng 12 MB bộ chạy).';
