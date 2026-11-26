import { describe, expect, it } from 'vitest';
import { effectiveEngine, engineChoices, isVi, piperItems, selectVoice, voiceItems, voiceKey, type EngineEnv } from './voices';

describe('Vietnamese-only device voices', () => {
  const raw = [
    { id: 'a', name: 'Microsoft HoaiMy Online (Natural) - Vietnamese (Vietnam)', lang: 'vi-VN' },
    { id: 'b', name: 'Aria', lang: 'en-US' },
    { id: 'c', name: 'Linh', lang: 'vi_VN' },
    { id: 'd', name: 'Viking', lang: 'vi' },
    { id: 'e', name: 'Mystery' },
    { id: 'f', name: 'Vivian', lang: 'vie-X' },
  ];

  it('recognises vi, vi-VN and vi_VN only', () => {
    expect(['vi', 'vi-VN', 'vi_VN', 'VI-vn'].every(isVi)).toBe(true);
    expect(['en-US', 'fr-FR', '', undefined, 'vie'].some(isVi)).toBe(false);
  });

  it('lists no voice of another language', () => {
    const items = voiceItems(raw);
    expect(items.map((v) => v.id).sort()).toEqual(['a', 'c', 'd']);
    expect(items.find((v) => v.id === 'a')?.label).toBe('HoaiMy - Vietnamese (Vietnam) (vi-VN)');
  });

  it('lets the device choose when the saved voice is not a listed Vietnamese voice', () => {
    const items = voiceItems(raw);
    expect(selectVoice('browser', items, 'c')).toEqual({ value: 'c', store: null });
    expect(selectVoice('browser', items, 'b')).toEqual({ value: '', store: null });
    expect(selectVoice('native', items, 'vi-VN-HoaiMyNeural')).toEqual({ value: '', store: null });
  });
});

describe('engines of the picker', () => {
  const env: EngineEnv = { browser: true, native: false, piper: true };

  it('offers the browser voice and Piper, never a server voice', () => {
    expect(engineChoices(env).map((c) => c.id)).toEqual(['browser', 'piper']);
    expect(engineChoices({ ...env, native: true }).map((c) => c.id)).toEqual(['browser', 'native', 'piper']);
  });

  it('marks Piper unavailable when the host cannot run it', () => {
    expect(engineChoices(env).find((c) => c.id === 'piper')?.available).toBe(true);
    expect(engineChoices({ ...env, piper: false }).find((c) => c.id === 'piper')).toMatchObject({ available: false });
  });

  it('is kept as the saved choice, and falls back to the device voice when unsupported', () => {
    expect(effectiveEngine('piper', env)).toBe('piper');
    expect(effectiveEngine('piper', { ...env, piper: false })).toBe('browser');
    expect(effectiveEngine('native', { ...env, native: true })).toBe('native');
    expect(effectiveEngine('browser', { browser: false, native: false })).toBeNull();
  });

  it('stores the voice of Piper in piperVoice and lists the three voices with sizes', () => {
    expect(voiceKey('piper')).toBe('piperVoice');
    expect(voiceKey('browser')).toBe('browserVoice');
    expect(voiceKey('native')).toBe('nativeVoice');
    const items = piperItems();
    expect(items).toHaveLength(3);
    expect(items[0]?.label).toMatch(/63 MB/);
    expect(selectVoice('piper', items, 'nope')).toEqual({ value: items[0]?.id, store: items[0]?.id });
    expect(selectVoice('piper', items, items[2]?.id as string).store).toBeNull();
  });
});
