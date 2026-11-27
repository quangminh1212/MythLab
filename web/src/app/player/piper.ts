/**
 * Piper: free Vietnamese neural voices that run ON THE USER'S DEVICE (WebAssembly in a Web Worker), so the server
 * never synthesises anything. The runtime (public/tts/, copied from npm by
 * scripts/copy-tts.mjs) is only loaded when a voice speaks; the selected voice's files are fetched by autovoice.ts after load.
 *
 *   model files   downloaded once from the Piper voice repository (or the GitHub release), kept in the Cache API (never localStorage)
 *   worker        public/tts/piper-worker.js: espeak-ng phonemizer + onnxruntime-web, one chunk at a time
 *   result        a 16-bit WAV blob URL that the player's <audio> element plays like any audio clip
 */
import { isIOS } from '../core/platform';
import { piperSupported, S } from '../core/settings';
import { fetchVerified, type Artifact } from './piper-fetch';

export { piperSupported };

/** A speaker of a multi-speaker model, with a gender that is documented (model card) or measured, never guessed. */
export interface PiperSpeaker {
  sid: number;
  name: string;
  /** Null when neither the model card nor a measurement says (the picker then shows "Chưa rõ giới tính"). */
  gender: 'nam' | 'nu' | null;
}

export interface PiperVoice {
  id: string;
  /** Shown in the picker. */
  name: string;
  /** Pinned directory of the model files (commit of the repository), with the trailing slash: `${repo}${id}.onnx`. */
  repo: string;
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
  /** Who made the voice and under which licence (attribution shown in Settings). */
  credit: string;
  /** Speakers offered in the picker. Missing = one speaker of unknown gender. */
  speakers?: readonly PiperSpeaker[];
  /** Kokoro (not a Piper model): its own files and worker; `bytes` / `sha256` describe `model`. */
  kokoro?: KokoroFiles;
}

/** A downloadable file with an exact size and hash and every place that serves exactly these bytes. */
export interface PiperFile {
  /** Asset name in the "piper-models" GitHub release (the last fallback source). */
  name: string;
  /** Pinned primary URL. */
  url: string;
  /** Other pinned URLs with the same bytes (tried after `url`, before the release). */
  mirrors?: readonly string[];
  bytes: number;
  sha256: string;
}

/** Model + config + SEA-G2P pronunciation dictionary of the Kokoro voice. */
export interface KokoroFiles {
  model: PiperFile;
  config: PiperFile;
  dict: PiperFile;
  /** The 14-voice model only: one style pack (510x256 float32) per speaker, in `sid` order. Its worker is kokoro-web-worker.js. */
  voices?: readonly PiperFile[];
}

/** Pinned to a commit of the voice repository, so the files cannot change under the size / hash below. */
const REPO = 'https://huggingface.co/rhasspy/piper-voices/resolve/5ec43b186ef915a195d3ddbcfd9916e76c503c3f/vi/vi_VN/';

/** Second source: assets of the "piper-models" GitHub release of this repository (same files as the pinned commit). */
export const RELEASE_URL = 'https://github.com/quangminh1212/MythLab/releases/download/piper-models/';

/** Kokoro-Vietnamese-Lite: pinned Hugging Face revisions (the author's repo, and a byte-identical copy as a mirror). */
const KOKORO_HF = 'https://huggingface.co/loanhviet/Kokoro-Vietnamese-Lite/resolve/a4c4cfefa8caf35aaaeb5ec628be996858df2121/';
const KOKORO_HF_MIRROR = 'https://huggingface.co/chungvh/kokoro-vietnamese-lite/resolve/7a7271e4058f4d34fd9f5b4f05a765a4a81ebb73/';
/** The SEA-G2P dictionary is only published in the SEA-G2P git repository (pinned commit). */
const SEA_G2P_BIN = 'https://raw.githubusercontent.com/pnnbao97/sea-g2p/e825173f235d08ea19315b2b279fb11153b44cea/python/sea_g2p/sea_g2p.bin';

export const KOKORO_FILES: KokoroFiles = {
  model: { name: 'kokoro_vi_lite.onnx', url: `${KOKORO_HF}kokoro_vi_lite.onnx`, mirrors: [`${KOKORO_HF_MIRROR}kokoro_vi_lite.onnx`], bytes: 9_210_026, sha256: '64d423426f09e1b9eac74d8f0c64781a24f4d37c784c05db847086324166c791' },
  config: { name: 'kokoro_vi_lite.config.json', url: `${KOKORO_HF}config.json`, mirrors: [`${KOKORO_HF_MIRROR}config.json`], bytes: 2351, sha256: '5abb01e2403b072bf03d04fde160443e209d7a0dad49a423be15196b9b43c17f' },
  dict: { name: 'sea_g2p.bin', url: SEA_G2P_BIN, bytes: 62_829_820, sha256: '4346e690d0711ebc5231e7a42c5c88aaf6e40377e894b4617c018fd81c6f4096' },
};

/** Kokoro 14 giọng (relingo/kokoro-vi-web, Apache-2.0): pinned revision; text frontend (config + SEA-G2P dictionary) is shared with Kokoro Lite. */
const KOKORO_WEB_HF = 'https://huggingface.co/relingo/kokoro-vi-web/resolve/8d088e9470451e2d88a707be82f58eb7f72d1c36/';

export const KOKORO_WEB_FILES: KokoroFiles = {
  model: { name: 'kokoro_vi_web.onnx', url: `${KOKORO_WEB_HF}kokoro_vi.web.onnx`, bytes: 82_653_554, sha256: '11f1a9a1f675575a027547206f11c6cd318119d92540d456391cc376621ba04c' },
  config: KOKORO_FILES.config,
  dict: KOKORO_FILES.dict,
  voices: [
    { name: 'kokoro_vi_web.voice.diem_trinh.bin', url: `${KOKORO_WEB_HF}voices/diem_trinh.bin`, bytes: 522240, sha256: 'ebd57307c0913fc06bca0acf8170b7f5d65dc1cb103ae42f91d36b3cef34495a' },
    { name: 'kokoro_vi_web.voice.duc_an.bin', url: `${KOKORO_WEB_HF}voices/duc_an.bin`, bytes: 522240, sha256: '9729a7a6888660ac8147a9bce7d1c9bb6d12ec15221764a6e6ba0c87833eab82' },
    { name: 'kokoro_vi_web.voice.duc_duy.bin', url: `${KOKORO_WEB_HF}voices/duc_duy.bin`, bytes: 522240, sha256: '0defaafea4d30679e7fc71d5284359f71812d0708dbc7e8920fdf73b980b54d6' },
    { name: 'kokoro_vi_web.voice.hung_thinh.bin', url: `${KOKORO_WEB_HF}voices/hung_thinh.bin`, bytes: 522240, sha256: 'b67fb932eefeb7e4fdb7c998fdf8676a78467d8b3c11c4fa7c1f5be4697a3b5a' },
    { name: 'kokoro_vi_web.voice.mai_linh.bin', url: `${KOKORO_WEB_HF}voices/mai_linh.bin`, bytes: 522240, sha256: 'd917a7048b12efdabb636e6e1eaaa63ae70851b58cf30a09ee948b55b6d0ca5b' },
    { name: 'kokoro_vi_web.voice.mai_loan.bin', url: `${KOKORO_WEB_HF}voices/mai_loan.bin`, bytes: 522240, sha256: '443f5c5a3147f2a2345fd15cfc82bcb8120ff809a2bdfd188efce95f73656b36' },
    { name: 'kokoro_vi_web.voice.manh_dung.bin', url: `${KOKORO_WEB_HF}voices/manh_dung.bin`, bytes: 522240, sha256: 'e4dade38606f12545cf73e0a5600fbefc5534cf3afbd31055ba1763726ecfa63' },
    { name: 'kokoro_vi_web.voice.my_yen.bin', url: `${KOKORO_WEB_HF}voices/my_yen.bin`, bytes: 522240, sha256: '935224b602b9ab917375f36107a661fe1ce01ca4d5ecb426685a8552ed9a37d4' },
    { name: 'kokoro_vi_web.voice.ngoc_huyen.bin', url: `${KOKORO_WEB_HF}voices/ngoc_huyen.bin`, bytes: 522240, sha256: '7f2554fd3f8e56748cb8c1f755335dc9b421783341c27574ee52affd367887ad' },
    { name: 'kokoro_vi_web.voice.phat_tai.bin', url: `${KOKORO_WEB_HF}voices/phat_tai.bin`, bytes: 522240, sha256: '31a1259b74ff5191e1320d692e51790c5e25ed411701465ef8599689b1c9a317' },
    { name: 'kokoro_vi_web.voice.storyvert.bin', url: `${KOKORO_WEB_HF}voices/storyvert.bin`, bytes: 522240, sha256: '1b2929c66e258f563b75d286a586a783fb3c962a9da3e0ad5a7c587643ab0545' },
    { name: 'kokoro_vi_web.voice.thanh_dat.bin', url: `${KOKORO_WEB_HF}voices/thanh_dat.bin`, bytes: 522240, sha256: '5ac281a299b49ff715fb31cd387d71746beefb2dab8cce69b02ac80ce9dea495' },
    { name: 'kokoro_vi_web.voice.thuc_trinh.bin', url: `${KOKORO_WEB_HF}voices/thuc_trinh.bin`, bytes: 522240, sha256: '5be77562f0fd5ccefe83e0bc18c6271df5e67b23fcafcd6210009d85ec115f31' },
    { name: 'kokoro_vi_web.voice.tuan_ngoc.bin', url: `${KOKORO_WEB_HF}voices/tuan_ngoc.bin`, bytes: 522240, sha256: 'bc0c98f5819b1d7598b229ea55da1dae3187048326423664dd7222095a38924f' },
  ],
};

const nu = (sid: number, name: string): PiperSpeaker => ({ sid, name, gender: 'nu' });
const nam = (sid: number, name: string): PiperSpeaker => ({ sid, name, gender: 'nam' });
const unk = (sid: number, name: string): PiperSpeaker => ({ sid, name, gender: null });

/** The Vietnamese voices. The default is VAIS-1000 (CC BY 4.0, the best quality); Piper v3 and Kokoro Lite add more male and female voices. */
export const PIPER_VOICES: readonly PiperVoice[] = [
  { id: 'vi_VN-vais1000-medium', name: 'Vais1000', repo: `${REPO}vais1000/medium/`, bytes: 63_221_984, sha256: '0567643f67b8329a46b3f0b549befc58e1e7e21ef558677768068d23a41d8471', configBytes: 6197, configSha256: '19240ab1eb13e5eb9c7dd00f9d1de5db08ff88d591c5008cbd24f1a25f51e13a', sampleRate: 22050, note: 'CC BY 4.0', credit: 'Vais1000: dữ liệu VAIS-1000 (VAIS), giấy phép CC BY 4.0; mô hình Piper (Rhasspy).', speakers: [nu(0, 'Mai')] },
  { id: 'vi_VN-25hours_single-low', name: '25 giờ', repo: `${REPO}25hours_single/low/`, bytes: 63_104_526, sha256: '266945c4a80cb3301450c8ba6fcf6ba3542c56cf952a08a8ff3d2d4ff0ab5609', configBytes: 4176, configSha256: '344b5849f5bc585031a63b9cc75f96e2c469f3d98879d8d3acbc2fce6d470064', sampleRate: 16000, note: 'chất lượng vừa', credit: '25 giờ: dữ liệu InfoRe (giấy phép chưa rõ); mô hình Piper (Rhasspy).', speakers: [nu(0, 'Hương')] },
  {
    id: 'vi_VN-csa-voice-piper-v3-medium',
    name: 'Piper v3',
    repo: 'https://huggingface.co/CakeByVPBank/piper-pgl-v4-vi_VN-version39_epoch39/resolve/8ea50134bea762f6a1faac671e1a33c41871289c/',
    bytes: 77_100_991,
    sha256: '99424831c88afec929eba3aef83a1b3d92f261b0bdc771bc2458f7f1ba63b6d2',
    configBytes: 4917,
    configSha256: '919c6f45f16e6549e5f72ae4961bf191abbb661830574e7786ab13da496a408e',
    sampleRate: 22050,
    note: 'MIT, 5 giọng',
    credit: 'Piper v3: CakeByVPBank, giấy phép MIT; huấn luyện trên dữ liệu giọng tổng hợp.',
    speakers: [nu(0, 'Ngọc Lan (miền Bắc)'), nu(1, 'Minh Anh (miền Bắc)'), nam(2, 'Quang Huy (miền Bắc)'), nu(3, 'Thu Hà (miền Bắc)'), nu(4, 'Yến Nhi (miền Nam)')],
  },
  {
    // Not a Piper model: Kokoro-Vietnamese-Lite, a 9 MB int8 model with two built-in voices (0 = female, 1 = male, per its
    // model card) that needs the 63 MB SEA-G2P dictionary to turn text into phonemes.
    id: 'kokoro-vi-lite',
    name: 'Kokoro Lite',
    repo: KOKORO_HF,
    bytes: KOKORO_FILES.model.bytes,
    sha256: KOKORO_FILES.model.sha256,
    configBytes: KOKORO_FILES.config.bytes,
    configSha256: KOKORO_FILES.config.sha256,
    sampleRate: 24000,
    note: 'Apache-2.0, mô hình 9 MB, đọc nhanh',
    credit: 'Kokoro Lite: loanhviet (Kokoro-Vietnamese-Lite), giấy phép Apache-2.0, chưng cất từ contextboxai/Kokoro-Vietnamese và hexgrad/Kokoro-82M (Apache-2.0); từ điển phát âm SEA-G2P (pnnbao97, Apache-2.0).',
    speakers: [nu(0, 'Diễm Trinh'), nam(1, 'Đức Duy')],
    kokoro: KOKORO_FILES,
  },
  {
    // Not a Piper model: kokoro-vi-web, 14 voices (7 female, 6 male, 1 of unknown gender) of the Kokoro-Vietnamese model.
    // 83 MB model + 0.5 MB per voice + the same 63 MB SEA-G2P dictionary as Kokoro Lite (stored once). Needs onnxruntime-web 1.30.
    id: 'kokoro-vi-web',
    name: 'Kokoro 14 giọng',
    repo: KOKORO_WEB_HF,
    bytes: KOKORO_WEB_FILES.model.bytes,
    sha256: KOKORO_WEB_FILES.model.sha256,
    configBytes: KOKORO_WEB_FILES.config.bytes,
    configSha256: KOKORO_WEB_FILES.config.sha256,
    sampleRate: 24000,
    note: 'Apache-2.0, 14 giọng, nặng 153 MB; đọc chậm hơn tốc độ nói trên máy thường (đã đo khoảng 2,6 lần thời gian thật), hợp để nghe thử hoặc đoạn ngắn',
    credit: 'Kokoro 14 giọng: relingo (kokoro-vi-web), giấy phép Apache-2.0, chuyển đổi từ contextboxai/Kokoro-Vietnamese và hexgrad/Kokoro-82M (Apache-2.0); từ điển phát âm SEA-G2P (pnnbao97, Apache-2.0). Giấy phép dữ liệu huấn luyện không được nêu.',
    speakers: [nu(0, 'Diễm Trinh'), nam(1, 'Đức An'), nam(2, 'Đức Duy'), nam(3, 'Hưng Thịnh'), nu(4, 'Mai Linh'), nu(5, 'Mai Loan'), nam(6, 'Mạnh Dũng'), nu(7, 'Mỹ Yến'), nu(8, 'Ngọc Huyền'), nam(9, 'Phát Tài'), nu(10, 'Storyvert'), nam(11, 'Thành Đạt'), nu(12, 'Thục Trinh'), unk(13, 'Tuấn Ngọc')],
    kokoro: KOKORO_WEB_FILES,
  },
];

/** The voice a new install uses and downloads by itself: VAIS-1000 (63 MB, same as core/settings.ts). */
export const DEFAULT_PIPER_VOICE = 'vi_VN-vais1000-medium#0';

/** The model for a saved id ("model" or "model#speaker"); an unknown id (older / newer app) gives the default. */
export const piperVoice = (id: string | undefined): PiperVoice =>
  PIPER_VOICES.find((v) => v.id === (id ?? '').split('#')[0]) ?? (PIPER_VOICES.find((v) => v.id === DEFAULT_PIPER_VOICE.split('#')[0]) as PiperVoice);

/** One entry of the picker: a model and the speaker it uses. */
export interface PiperChoice {
  /** Saved in the settings: the model id, plus "#sid" for a speaker of a multi-speaker model. */
  id: string;
  model: PiperVoice;
  sid: number;
  name: string;
  /** Null when the gender is not documented. */
  gender: 'nam' | 'nu' | null;
}

const GENDER = { nam: 'Nam', nu: 'Nữ' } as const;

/** Every voice the picker offers, the lightest download first (then Nữ before Nam, then catalog order). */
export const PIPER_CHOICES: readonly PiperChoice[] = PIPER_VOICES.flatMap((m): PiperChoice[] =>
  m.speakers ? m.speakers.map((s) => ({ id: `${m.id}#${s.sid}`, model: m, sid: s.sid, name: s.name, gender: s.gender })) : [{ id: m.id, model: m, sid: 0, name: m.name, gender: null }],
)
  .map((c, i) => ({ c, i }))
  .sort((a, b) => downloadBytes(a.c.model) - downloadBytes(b.c.model) || (a.c.gender === 'nu' ? 0 : 1) - (b.c.gender === 'nu' ? 0 : 1) || a.i - b.i)
  .map((x) => x.c);

/** The choice for a saved id: a bare model id means its first speaker; an unknown id gives the default voice. */
export function piperChoice(id: string | undefined): PiperChoice {
  const hit = PIPER_CHOICES.find((c) => c.id === id);
  if (hit) return hit;
  const m = piperVoice(id);
  return (m.id === DEFAULT_PIPER_VOICE.split('#')[0] ? PIPER_CHOICES.find((c) => c.id === DEFAULT_PIPER_VOICE) : undefined) ?? (PIPER_CHOICES.find((c) => c.model === m) as PiperChoice);
}

export const piperModelUrl = (v: PiperVoice): string => v.kokoro?.model.url ?? `${v.repo}${v.id}.onnx`;
export const piperConfigUrl = (v: PiperVoice): string => v.kokoro?.config.url ?? `${piperModelUrl(v)}.json`;
/** Cache key of the Kokoro pronunciation dictionary (null for Piper voices). */
export const kokoroDictUrl = (v: PiperVoice): string | null => v.kokoro?.dict.url ?? null;

/** Everything the user downloads for a voice: the model and, for Kokoro, its dictionary (and voice packs) too. */
export function downloadBytes(v: PiperVoice): number {
  return v.bytes + (v.kokoro?.dict.bytes ?? 0) + (v.kokoro?.voices ?? []).reduce((n, f) => n + f.bytes, 0);
}

/** Sources of a downloadable file: its pinned URL, pinned mirrors, then the GitHub release. */
const fileSources = (f: PiperFile): string[] => [f.url, ...(f.mirrors ?? []), RELEASE_URL + f.name];

/** File names of a voice: "vi_VN-vais1000-medium.onnx" and its ".json". */
const modelFile = (v: PiperVoice): string => `${v.id}.onnx`;

/** Ordered download sources of a file of a voice (`suffix` is '' for the model, '.json' for the config). */
export function piperSources(v: PiperVoice, suffix = ''): string[] {
  if (v.kokoro) return fileSources(suffix ? v.kokoro.config : v.kokoro.model);
  const file = modelFile(v) + suffix;
  return [`${v.repo}${file}`, RELEASE_URL + file];
}

const modelArtifact = (v: PiperVoice): Artifact => ({ name: 'giọng ' + v.name, bytes: v.bytes, sha256: v.sha256, sources: piperSources(v) });
const dictArtifact = (k: KokoroFiles): Artifact => ({ name: 'từ điển phát âm', bytes: k.dict.bytes, sha256: k.dict.sha256, sources: fileSources(k.dict) });
const voiceArtifact = (f: PiperFile, i: number): Artifact => ({ name: `gói giọng ${i + 1}`, bytes: f.bytes, sha256: f.sha256, sources: fileSources(f) });
const configArtifact = (v: PiperVoice): Artifact => ({ name: 'cấu hình giọng', bytes: v.configBytes, sha256: v.configSha256, sources: piperSources(v, '.json') });

/** "63 MB" */
/** Extra line for the download dialogs: a big voice can run out of memory on a phone with 2 GB of RAM or less. */
export function lowMemoryNote(bytes: number): string {
  if (!tooHeavyHere(bytes)) return '';
  if (isIOS()) return ' Safari trên iPhone/iPad giới hạn bộ nhớ mỗi trang: giọng nặng có thể làm trang tự tải lại, nên chọn giọng nhẹ hơn.';
  return ' Máy có ít bộ nhớ (≤ 2 GB): giọng nặng có thể bị treo hoặc tự thoát, nên chọn giọng nhẹ hơn.';
}

/** Voices bigger than this can run out of memory on a phone with 2 GB of RAM or less. */
export const HEAVY_VOICE_BYTES = 70_000_000;

/**
 * The device reports 2 GB of RAM or less (`navigator.deviceMemory`, Chromium only; unknown counts as enough).
 * iOS has no deviceMemory and WebKit kills a page that grows past a per-tab limit, so iOS counts as low memory here.
 */
export function lowMemory(): boolean {
  if (isIOS()) return true;
  const mem = (globalThis.navigator as (Navigator & { deviceMemory?: number }) | undefined)?.deviceMemory;
  return mem !== undefined && mem <= 2;
}

/** A download of `bytes` is too heavy for this device: low memory and a big model. */
export const tooHeavyHere = (bytes: number): boolean => lowMemory() && bytes > HEAVY_VOICE_BYTES;

/** The lightest voice (the default), what low-memory devices use. */
export const lightChoice = (): PiperChoice => piperChoice(DEFAULT_PIPER_VOICE);

export const megabytes = (bytes: number): string => `${Math.round(bytes / 1e6)} MB`;

/** Label of a model: "Vais1000 — chất lượng cao · 63 MB · đã tải". */
export const piperVoiceLabel = (v: PiperVoice, installed: boolean): string => `${v.name} · ${megabytes(downloadBytes(v))}${installed ? ' · đã tải' : ''}`;

/** Picker label of a voice: "Nữ · Vivos 1 · 28 MB · đã tải" ("Chưa rõ giới tính" when the data has no gender). */
export const piperChoiceLabel = (c: PiperChoice, installed: boolean): string => `${c.gender ? GENDER[c.gender] : 'Chưa rõ giới tính'} · ${piperVoiceLabel({ ...c.model, name: c.name }, installed)}`;

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
      const dict = kokoroDictUrl(v);
      const [m, j, d, p] = await Promise.all([
        c.match(piperModelUrl(v)),
        c.match(piperConfigUrl(v)),
        dict ? c.match(dict) : Promise.resolve(true),
        Promise.all((v.kokoro?.voices ?? []).map((f) => c.match(f.url))),
      ]);
      if (m && j && d && p.every(Boolean)) installed.add(v.id);
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
  // progress of the whole voice: the model first, then (Kokoro) the dictionary, each weighted by its size
  const total = downloadBytes(v);
  const part = (from: number, size: number) => (f: number): void => onProgress?.(Math.min(1, (from + f * size) / total));
  const model = await fetchVerified(modelArtifact(v), { onProgress: v.kokoro ? part(0, v.bytes) : onProgress, signal, onSource: (i, n) => onSource?.(i, n) });
  const dict = v.kokoro ? await fetchVerified(dictArtifact(v.kokoro), { onProgress: part(v.bytes, v.kokoro.dict.bytes), signal, onSource: (i, n) => onSource?.(i, n) }) : null;
  const packs: Blob[] = [];
  let from = v.bytes + (v.kokoro?.dict.bytes ?? 0);
  for (const [i, f] of (v.kokoro?.voices ?? []).entries()) {
    packs.push((await fetchVerified(voiceArtifact(f, i), { onProgress: part(from, f.bytes), signal, onSource: (k, n) => onSource?.(k, n) })).blob);
    from += f.bytes;
  }
  try {
    await cache.put(piperModelUrl(v), new Response(model.blob, { headers: { 'content-type': 'application/octet-stream' } }));
    await cache.put(piperConfigUrl(v), new Response(cfgBody, { headers: { 'content-type': 'application/json' } }));
    if (v.kokoro && dict) await cache.put(v.kokoro.dict.url, new Response(dict.blob, { headers: { 'content-type': 'application/octet-stream' } }));
    for (const [i, f] of (v.kokoro?.voices ?? []).entries()) await cache.put(f.url, new Response(packs[i], { headers: { 'content-type': 'application/octet-stream' } }));
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
    // the config and dictionary are shared by both Kokoro voices: keep them while the other one is still installed
    const shared = (url: string): boolean => PIPER_VOICES.some((o) => o.id !== v.id && installed.has(o.id) && (kokoroDictUrl(o) === url || (o.kokoro && piperConfigUrl(o) === url)));
    const dict = kokoroDictUrl(v);
    const urls = [piperModelUrl(v), piperConfigUrl(v), ...(dict ? [dict] : []), ...(v.kokoro?.voices ?? []).map((f) => f.url)].filter((u) => !shared(u));
    await Promise.all(urls.map((u) => c.delete(u)));
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
/** Which worker script runs: Piper's or Kokoro's (different runtimes, so a switch restarts the worker). */
let workerKind: 'piper' | 'kokoro' | 'kokoro-web' = 'piper';
let loaded = '';
let loading: Promise<void> | null = null;
let seq = 0;
const pending = new Map<number, Pending>();

const runtimeBase = (): string => new URL('tts/', document.baseURI).href;

function spawn(): Worker {
  if (worker) return worker;
  const w = new Worker(new URL(workerKind === 'piper' ? 'piper-worker.js' : `${workerKind}-worker.js`, runtimeBase()));
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
    const kind = v.kokoro ? (v.kokoro.voices ? 'kokoro-web' : 'kokoro') : 'piper';
    if (worker && workerKind !== kind) {
      // the other engine's worker: stop it (fail() would also forget this load in progress)
      worker.terminate();
      worker = null;
      loaded = '';
    }
    workerKind = kind;
    const [model, config] = await Promise.all([m.arrayBuffer(), j.json()]);
    if (v.kokoro) {
      const d = await cache.match(v.kokoro.dict.url);
      if (!d) {
        installed.delete(v.id);
        throw new Error('Chưa tải từ điển phát âm');
      }
      const dict = await d.arrayBuffer();
      const voices: ArrayBuffer[] = [];
      for (const f of v.kokoro.voices ?? []) {
        const r = await cache.match(f.url);
        if (!r) {
          installed.delete(v.id);
          throw new Error('Chưa tải gói giọng Kokoro');
        }
        voices.push(await r.arrayBuffer());
      }
      await call({ t: 'init', base: runtimeBase(), model, config, dict, ...(voices.length ? { voices } : {}) }, [model, dict, ...voices]);
    } else {
      await call({ t: 'init', base: runtimeBase(), model, config }, [model]);
    }
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
  const c = piperChoice(id);
  const v = c.model;
  await load(v);
  const r = await call<{ pcm: Float32Array; rate: number }>({ t: 'synth', text, sid: c.sid });
  return new Blob([wavFromPcm(r.pcm, r.rate || v.sampleRate)], { type: 'audio/wav' });
}

// ---------------------------------------------------------------- prepared clips

/** Clips of the chunks about to be played: at most KEEP, object URLs are released on eviction. */
const KEEP = 6;
const clips = new Map<string, Promise<string>>();

const key = (text: string): string => `${piperChoice(S.piperVoice).id}|${text}`;

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
  if (!text || !piperReady()) return;
  // synthesising ahead counts as use: the worker must not be shut down in the middle of a long chapter
  if (worker) touch();
  void piperSource(text).catch(() => {});
}

/** Forgets every prepared clip (voice changed, player closed). */
export function forget(): void {
  for (const k of [...clips.keys()]) drop(k);
}

export const PIPER_SIZE_NOTE = 'Giọng Piper chạy ngay trên máy bạn, không dùng máy chủ. Lần đầu cần tải về một lần (cộng khoảng 12 MB bộ chạy).';
