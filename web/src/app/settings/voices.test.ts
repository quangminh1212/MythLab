import { describe, expect, it } from 'vitest';
import { DEFAULT_PIPER_VOICE } from '../player/piper';
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
    expect(selectVoice('native', items, 'c')).toEqual({ value: 'c', store: null });
    expect(selectVoice('native', items, 'b')).toEqual({ value: '', store: null });
    expect(selectVoice('native', items, 'vi-VN-HoaiMyNeural')).toEqual({ value: '', store: null });
  });
});

describe('engines of the picker', () => {
  const env: EngineEnv = { native: false, piper: true };

  it('offers Piper alone on the web and the phone voice plus Piper in the app, never the browser or a server voice', () => {
    expect(engineChoices(env).map((c) => c.id)).toEqual(['piper']);
    expect(engineChoices({ ...env, native: true }).map((c) => c.id)).toEqual(['native', 'piper']);
  });

  it('marks Piper unavailable when the host cannot run it', () => {
    expect(engineChoices(env).find((c) => c.id === 'piper')?.available).toBe(true);
    expect(engineChoices({ ...env, piper: false }).find((c) => c.id === 'piper')).toMatchObject({ available: false });
  });

  it('is kept as the saved choice, and falls back to the other engine when unusable', () => {
    expect(effectiveEngine('piper', env)).toBe('piper');
    expect(effectiveEngine('piper', { native: true, piper: false })).toBe('native');
    expect(effectiveEngine('native', { ...env, native: true })).toBe('native');
    expect(effectiveEngine('native', env)).toBe('piper');
    expect(effectiveEngine('piper', { native: false, piper: false })).toBeNull();
  });

  it('stores the voice of Piper in piperVoice and lists the voices with gender and sizes, lightest first', () => {
    expect(voiceKey('piper')).toBe('piperVoice');
    expect(voiceKey('native')).toBe('nativeVoice');
    const items = piperItems();
    expect(items.length).toBe(23);
    expect(items.find((i) => i.id === DEFAULT_PIPER_VOICE)?.label).toMatch(/63 MB/);
    expect(items[0]?.label).toMatch(/63 MB/);
    expect(items.some((i) => /^Nam · Thành Đạt · 153 MB/.test(i.label))).toBe(true);
    expect(items.some((i) => /^Nam · /.test(i.label))).toBe(true);
    expect(items.some((i) => /^Nữ · Mai · 63 MB/.test(i.label))).toBe(true);
    expect(selectVoice('piper', items, 'vi_VN-vais1000-medium')).toEqual({ value: DEFAULT_PIPER_VOICE, store: DEFAULT_PIPER_VOICE });
    expect(selectVoice('piper', items, 'nope')).toEqual({ value: DEFAULT_PIPER_VOICE, store: DEFAULT_PIPER_VOICE });
    expect(selectVoice('piper', items, items[2]?.id as string).store).toBeNull();
  });
});
