import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { S } from '../core/settings';
import { DEFAULT_PIPER_VOICE, downloadBytes, KOKORO_FILES, megabytes, PIPER_CHOICES, PIPER_VOICES, piperChoice, piperChoiceLabel, piperConfigUrl, piperModelUrl, piperReady, piperSources, RELEASE_URL, piperVoice, piperVoiceLabel, wavFromPcm } from './piper';

describe('piper catalog', () => {
  it('lists the Vietnamese models with sizes and the commercial-safe one first', () => {
    expect(PIPER_VOICES.map((v) => v.id)).toEqual(['vi_VN-vais1000-medium', 'vi_VN-25hours_single-low', 'vi_VN-vivos-x_low', 'vi_VN-csa-voice-piper-v3-medium', 'kokoro-vi-lite']);
    expect(DEFAULT_PIPER_VOICE).toBe('vi_VN-vais1000-medium');
    expect(megabytes(piperVoice('vi_VN-vivos-x_low').bytes)).toBe('28 MB');
    expect(megabytes(piperVoice('vi_VN-csa-voice-piper-v3-medium').bytes)).toBe('77 MB');
  });

  it('maps a saved id to a voice and falls back to the default for an unknown one', () => {
    expect(piperVoice('vi_VN-25hours_single-low').sampleRate).toBe(16000);
    expect(piperVoice('gone').id).toBe(DEFAULT_PIPER_VOICE);
    expect(piperVoice(undefined).id).toBe(DEFAULT_PIPER_VOICE);
    expect(piperVoice('vi_VN-vivos-x_low#7').id).toBe('vi_VN-vivos-x_low');
  });

  it('builds model urls next to their json and labels downloaded voices', () => {
    const v = piperVoice(DEFAULT_PIPER_VOICE);
    expect(piperModelUrl(v)).toBe('https://huggingface.co/rhasspy/piper-voices/resolve/5ec43b186ef915a195d3ddbcfd9916e76c503c3f/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx');
    expect(piperConfigUrl(v)).toBe(`${piperModelUrl(v)}.json`);
    expect(piperVoiceLabel(v, false)).toContain('63 MB');
    expect(piperVoiceLabel(v, true)).toContain('đã tải');
  });
});

describe('piper picker choices', () => {
  it('offers male and female voices, lightest download first', () => {
    const sizes = PIPER_CHOICES.map((c) => downloadBytes(c.model));
    expect(sizes).toEqual([...sizes].sort((a, b) => a - b));
    expect(PIPER_CHOICES[0]?.model.id).toBe('vi_VN-vivos-x_low');
    expect(PIPER_CHOICES.filter((c) => c.gender === 'nam').length).toBeGreaterThanOrEqual(5);
    expect(PIPER_CHOICES.filter((c) => c.gender === 'nu').length).toBeGreaterThanOrEqual(5);
    expect(new Set(PIPER_CHOICES.map((c) => c.id)).size).toBe(PIPER_CHOICES.length);
  });

  it('only labels a gender for documented speakers, the others say it is unknown', () => {
    expect(piperChoiceLabel(piperChoice('vi_VN-vais1000-medium'), false)).toBe('Chưa rõ giới tính · Vais1000 — chất lượng cao · 63 MB');
    expect(piperChoiceLabel(piperChoice('vi_VN-csa-voice-piper-v3-medium#2'), true)).toBe('Nam · Quang Huy (miền Bắc) · 77 MB · đã tải');
    expect(piperChoiceLabel(piperChoice('vi_VN-vivos-x_low#0'), false)).toBe('Nữ · Vivos 1 · 28 MB');
    expect(PIPER_CHOICES.filter((c) => c.model.id === 'vi_VN-25hours_single-low').every((c) => c.gender === null)).toBe(true);
  });

  it('maps a saved id to its speaker; a bare or unknown id means the first speaker / the default', () => {
    expect(piperChoice('vi_VN-csa-voice-piper-v3-medium#4').sid).toBe(4);
    expect(piperChoice('vi_VN-vivos-x_low#9').sid).toBe(9);
    expect(piperChoice('vi_VN-vivos-x_low').model.id).toBe('vi_VN-vivos-x_low');
    expect(piperChoice('vi_VN-vivos-x_low#64').model.id).toBe('vi_VN-vivos-x_low');
    expect(piperChoice('gone').model.id).toBe(DEFAULT_PIPER_VOICE);
  });

  it('keeps every offered speaker inside the model (sid < 65 for vivos, < 5 for Piper v3) and gives every model a credit', () => {
    const max: Record<string, number> = { 'vi_VN-vivos-x_low': 65, 'vi_VN-csa-voice-piper-v3-medium': 5, 'kokoro-vi-lite': 2 };
    for (const v of PIPER_VOICES) {
      expect(v.credit.length).toBeGreaterThan(10);
      for (const s of v.speakers ?? []) expect(s.sid).toBeLessThan(max[v.id] as number);
    }
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
    for (const v of PIPER_VOICES) {
      expect(piperModelUrl(v)).not.toContain('/main/');
      expect(piperModelUrl(v)).toMatch(/\/resolve\/[0-9a-f]{40}\//);
    }
  });
});

describe('piper sources and Vietnamese-only catalog', () => {
  const v = PIPER_VOICES[0] as (typeof PIPER_VOICES)[number];

  it('lists Hugging Face (pinned), then the GitHub release, for the model and its config', () => {
    const [hf, gh, ...rest] = piperSources(v);
    expect(hf).toBe(piperModelUrl(v));
    expect(gh).toBe('https://github.com/quangminh1212/MythLab/releases/download/piper-models/vi_VN-vais1000-medium.onnx');
    expect(rest).toEqual([]);
    expect(piperSources(v, '.json').map((u) => u.slice(-5))).toEqual(['.json', '.json']);
  });

  it('has no source on our own server (the model mirror is gone)', () => {
    expect(piperSources(v).some((u) => u.includes('/tts/models/'))).toBe(false);
  });

  it('has only Vietnamese voices and every source is for Vietnamese', () => {
    for (const x of PIPER_VOICES.filter((y) => !y.kokoro)) {
      expect(x.id.startsWith('vi_VN-')).toBe(true);
      expect(piperModelUrl(x)).toMatch(/vi_VN/);
      expect(piperSources(x).every((u) => u.includes(x.id))).toBe(true);
      expect(x.configSha256).toMatch(/^[0-9a-f]{64}$/);
    }
  });

  it('matches scripts/piper-models.json, which fetch-models.mjs downloads from', () => {
    const cat = JSON.parse(readFileSync(join(process.cwd(), 'scripts', 'piper-models.json'), 'utf8')) as { models: Record<string, unknown>[] };
    expect(cat.models.map((m) => m.id)).toEqual(PIPER_VOICES.map((x) => x.id));
    for (const m of cat.models.filter((y) => !y.files)) {
      const x = piperVoice(m.id as string);
      expect(m).toEqual({ id: x.id, repo: x.repo, bytes: x.bytes, sha256: x.sha256, configBytes: x.configBytes, configSha256: x.configSha256 });
      expect(`${m.repo as string}${x.id}.onnx`).toBe(piperModelUrl(x));
    }
  });
});

describe('kokoro lite voice', () => {
  const k = piperVoice('kokoro-vi-lite');
  const sha = /^[0-9a-f]{64}$/;

  it('is one 9 MB model with a female and a male voice, labelled with the total download', () => {
    expect(megabytes(k.bytes)).toBe('9 MB');
    expect(megabytes(downloadBytes(k))).toBe('72 MB');
    expect(k.sampleRate).toBe(24000);
    expect(PIPER_CHOICES.filter((c) => c.model === k).map((c) => [c.id, c.gender, c.sid])).toEqual([
      ['kokoro-vi-lite#0', 'nu', 0],
      ['kokoro-vi-lite#1', 'nam', 1],
    ]);
    expect(piperChoiceLabel(piperChoice('kokoro-vi-lite#1'), true)).toBe('Nam · Đức Duy · 72 MB · đã tải');
    expect(piperChoiceLabel(piperChoice('kokoro-vi-lite#0'), false)).toBe('Nữ · Diễm Trinh · 72 MB');
    expect(piperChoice('kokoro-vi-lite#1').sid).toBe(1);
  });

  it('credits the licences of the model, its teacher and the dictionary', () => {
    expect(k.credit).toContain('Apache-2.0');
    expect(k.credit).toContain('SEA-G2P');
  });

  it('pins every file by revision, size and sha-256', () => {
    for (const f of Object.values(KOKORO_FILES)) {
      expect(f.sha256).toMatch(sha);
      expect(f.bytes).toBeGreaterThan(0);
      for (const u of [f.url, ...(f.mirrors ?? [])]) {
        expect(u).not.toMatch(/\/(main|master)\//);
        expect(u).toMatch(/\/[0-9a-f]{40}\//);
      }
    }
    expect(piperModelUrl(k)).toBe(KOKORO_FILES.model.url);
    expect(piperConfigUrl(k)).toBe(KOKORO_FILES.config.url);
  });

  it('tries the pinned repo, the mirror, then the GitHub release, for model and config; the dictionary has no mirror', () => {
    expect(piperSources(k).map((u) => new URL(u).host)).toEqual(['huggingface.co', 'huggingface.co', 'github.com']);
    expect(piperSources(k)[2]).toBe(RELEASE_URL + 'kokoro_vi_lite.onnx');
    expect(piperSources(k, '.json')[2]).toBe(RELEASE_URL + 'kokoro_vi_lite.config.json');
    expect(piperSources(k).some((u) => u.includes('/tts/models/'))).toBe(false);
  });

  it('is described in scripts/piper-models.json (what has to be uploaded to the GitHub release)', () => {
    const cat = JSON.parse(readFileSync(join(process.cwd(), 'scripts', 'piper-models.json'), 'utf8')) as { models: { id: string; files?: Record<string, unknown>[] }[] };
    const m = cat.models.find((x) => x.id === k.id);
    expect(m?.files).toEqual([KOKORO_FILES.model, KOKORO_FILES.config, KOKORO_FILES.dict].map((f) => ({ name: f.name, url: f.url, bytes: f.bytes, sha256: f.sha256 })));
  });
});
