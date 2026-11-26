import { describe, expect, it } from 'vitest';
import { effectiveEngine, engineChoices, isPiperVoice, piperItems, selectVoice, voiceDisplayName, voiceItems, voiceKey, type EngineEnv } from './voices';

describe('Piper voices in the server voice list', () => {
  const raw = [
    { id: 'vi-VN-HoaiMyNeural', name: 'Microsoft HoaiMy Online (Natural) - Vietnamese (Vietnam)', lang: 'vi-VN' },
    { id: 'vi-VN-Vais1000Piper', name: 'Vais1000 (Piper)', lang: 'vi-VN' },
    { id: 'en-US-AriaNeural', name: 'Aria', lang: 'en-US' },
  ];

  it('recognises the Piper suffix only', () => {
    expect(isPiperVoice('vi-VN-VivosXPiper')).toBe(true);
    expect(isPiperVoice('vi-VN-HoaiMyNeural')).toBe(false);
  });

  it('labels Piper voices as offline, once', () => {
    expect(voiceDisplayName('vi-VN-Vais1000Piper', 'Vais1000')).toBe('Vais1000 (offline)');
    expect(voiceDisplayName('vi-VN-Vais1000Piper', 'Vais1000 (Piper, offline)')).toBe('Vais1000 (Piper, offline)');
    expect(voiceDisplayName('vi-VN-HoaiMyNeural', 'HoaiMy')).toBe('HoaiMy');
  });

  it('lists Piper next to Edge voices and keeps them selectable', () => {
    const items = voiceItems('edge', raw);
    const p = items.find((v) => v.id === 'vi-VN-Vais1000Piper');
    expect(p?.vi).toBe(true);
    expect(p?.label).toContain('(offline)');
    expect(selectVoice('edge', items, 'vi-VN-Vais1000Piper')).toEqual({ value: 'vi-VN-Vais1000Piper', store: null });
  });
});

describe('on-device Piper in the picker', () => {
  const env: EngineEnv = { kind: 'github', edge: false, browser: true, native: false, piper: true };

  it('is listed and available when the host can run it', () => {
    expect(engineChoices(env).find((c) => c.id === 'piper')?.available).toBe(true);
    expect(engineChoices({ ...env, piper: false }).find((c) => c.id === 'piper')).toMatchObject({ available: false });
  });

  it('is kept as the saved choice, and falls back to the device voice when unsupported', () => {
    expect(effectiveEngine('piper', env)).toBe('piper');
    expect(effectiveEngine('piper', { ...env, piper: false })).toBe('browser');
  });

  it('stores its voice in piperVoice and lists the three voices with sizes', () => {
    expect(voiceKey('piper')).toBe('piperVoice');
    const items = piperItems();
    expect(items).toHaveLength(3);
    expect(items[0]?.label).toMatch(/63 MB/);
    expect(selectVoice('piper', items, 'nope')).toEqual({ value: items[0]?.id, store: items[0]?.id });
    expect(selectVoice('piper', items, items[2]?.id as string).store).toBeNull();
  });
});
