import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it, vi } from 'vitest';
import { S } from '../core/settings';
import { DEFAULT_PIPER_VOICE, megabytes, PIPER_VOICES, piperConfigUrl, piperModelUrl, piperReady, piperSources, piperVoice, piperVoiceLabel, wavFromPcm } from './piper';

describe('piper catalog', () => {
  it('lists three Vietnamese voices with sizes and the commercial-safe one first', () => {
    expect(PIPER_VOICES.map((v) => v.id)).toEqual(['vi_VN-vais1000-medium', 'vi_VN-25hours_single-low', 'vi_VN-vivos-x_low']);
    expect(DEFAULT_PIPER_VOICE).toBe('vi_VN-vais1000-medium');
    expect(megabytes(piperVoice('vi_VN-vivos-x_low').bytes)).toBe('28 MB');
  });

  it('maps a saved id to a voice and falls back to the default for an unknown one', () => {
    expect(piperVoice('vi_VN-25hours_single-low').sampleRate).toBe(16000);
    expect(piperVoice('gone').id).toBe(DEFAULT_PIPER_VOICE);
    expect(piperVoice(undefined).id).toBe(DEFAULT_PIPER_VOICE);
  });

  it('builds model urls next to their json and labels downloaded voices', () => {
    const v = piperVoice(DEFAULT_PIPER_VOICE);
    expect(piperModelUrl(v)).toBe('https://huggingface.co/rhasspy/piper-voices/resolve/5ec43b186ef915a195d3ddbcfd9916e76c503c3f/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx');
    expect(piperConfigUrl(v)).toBe(`${piperModelUrl(v)}.json`);
    expect(piperVoiceLabel(v, false)).toContain('63 MB');
    expect(piperVoiceLabel(v, true)).toContain('đã tải');
  });
});

describe('wavFromPcm', () => {
  it('writes a mono 16-bit RIFF header and clamps samples', () => {
    const wav = wavFromPcm(Float32Array.from([0, 1, -1, 2, -2]), 22050);
    const v = new DataView(wav);
    const tag = (at: number): string => String.fromCharCode(v.getUint8(at), v.getUint8(at + 1), v.getUint8(at + 2), v.getUint8(at + 3));
    expect(wav.byteLength).toBe(44 + 10);
    expect([tag(0), tag(8), tag(12), tag(36)]).toEqual(['RIFF', 'WAVE', 'fmt ', 'data']);
    expect(v.getUint32(4, true)).toBe(36 + 10);
    expect(v.getUint16(22, true)).toBe(1);
    expect(v.getUint32(24, true)).toBe(22050);
    expect(v.getUint32(28, true)).toBe(44100);
    expect(v.getUint32(40, true)).toBe(10);
    expect([0, 1, 2, 3, 4].map((i) => v.getInt16(44 + i * 2, true))).toEqual([0, 32767, -32768, 32767, -32768]);
  });
});

describe('piper readiness', () => {
  it('is not ready before a voice was found in the cache (nothing downloads by itself)', () => {
    S.piperVoice = DEFAULT_PIPER_VOICE;
    expect(piperReady()).toBe(false);
  });
});

describe('piper integrity', () => {
  it('pins a commit and gives every voice a sha-256', () => {
    for (const v of PIPER_VOICES) expect(v.sha256).toMatch(/^[0-9a-f]{64}$/);
    expect(piperModelUrl(PIPER_VOICES[0] as (typeof PIPER_VOICES)[number])).not.toContain('/main/');
  });
});

describe('piper sources and Vietnamese-only catalog', () => {
  const v = PIPER_VOICES[0] as (typeof PIPER_VOICES)[number];

  it('lists Hugging Face (pinned), our mirror, then the GitHub release, for the model and its config', () => {
    const [hf, mirror, gh] = piperSources(v, '', 'https://myth.example/app/');
    expect(hf).toBe(piperModelUrl(v));
    expect(mirror).toBe('https://myth.example/app/tts/models/vi_VN-vais1000-medium.onnx');
    expect(gh).toBe('https://github.com/quangminh1212/MythLab/releases/download/piper-models/vi_VN-vais1000-medium.onnx');
    expect(piperSources(v, '.json', 'https://myth.example/').map((u) => u.slice(-5))).toEqual(['.json', '.json', '.json']);
  });

  it('resolves the mirror against the app origin, and the native app against myth.xlabrnd.com', () => {
    expect(piperSources(v)[1]).toMatch(/[/]tts[/]models[/]vi_VN-vais1000-medium[.]onnx$/);
    vi.stubGlobal('Capacitor', { isNativePlatform: () => true });
    try {
      expect(piperSources(v)[1]).toBe('https://myth.xlabrnd.com/tts/models/vi_VN-vais1000-medium.onnx');
    } finally {
      vi.unstubAllGlobals();
    }
  });

  it('has only Vietnamese voices and every source is for Vietnamese', () => {
    for (const x of PIPER_VOICES) {
      expect(x.id.startsWith('vi_VN-')).toBe(true);
      expect(piperModelUrl(x)).toContain('/vi/vi_VN/');
      expect(x.configSha256).toMatch(/^[0-9a-f]{64}$/);
    }
  });

  it('matches scripts/piper-models.json, which fetch-models.mjs downloads from', () => {
    const cat = JSON.parse(readFileSync(join(process.cwd(), 'scripts', 'piper-models.json'), 'utf8')) as { repo: string; models: Record<string, unknown>[] };
    expect(cat.models.map((m) => m.id)).toEqual(PIPER_VOICES.map((x) => x.id));
    for (const m of cat.models) {
      const x = piperVoice(m.id as string);
      expect(m).toEqual({ id: x.id, path: x.path, bytes: x.bytes, sha256: x.sha256, configBytes: x.configBytes, configSha256: x.configSha256 });
      expect(`${cat.repo}${x.path}${x.id}.onnx`).toBe(piperModelUrl(x));
    }
  });
});
