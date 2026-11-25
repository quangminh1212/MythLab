import { describe, expect, it } from 'vitest';
import { isPiperVoice, selectVoice, voiceDisplayName, voiceItems } from './voices';

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
