import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const ready = vi.hoisted(() => ({ value: false }));
vi.mock('./piper', async (orig) => ({ ...(await orig<typeof import('./piper')>()), piperReady: () => ready.value, piperSupported: () => true }));

import { S } from '../core/settings';
import { effectiveEngine, engines, ENGINE_LABEL, localEngine, playsClips, voices } from './engines';

beforeEach(() => {
  ready.value = false;
  S.engine = 'piper';
  vi.stubGlobal('speechSynthesis', { getVoices: () => [], addEventListener() {}, removeEventListener() {}, cancel() {} });
  vi.stubGlobal('SpeechSynthesisUtterance', class {});
});
afterEach(() => vi.unstubAllGlobals());

describe('engine choice with Piper', () => {
  it('speaks with Piper only when its voice is on the device', () => {
    expect(effectiveEngine()).toBe('browser');
    ready.value = true;
    expect(effectiveEngine()).toBe('piper');
  });

  it('keeps the saved choice and uses the device voice meanwhile', () => {
    expect(effectiveEngine()).toBe('browser');
    expect(S.engine).toBe('piper');
    expect(localEngine()).toBe('browser');
  });

  it('prefers the Android voice as the stand-in when the app has one', () => {
    vi.stubGlobal('Capacitor', { Plugins: { TextToSpeech: {} } });
    expect(localEngine()).toBe('native');
    expect(effectiveEngine()).toBe('native');
  });

  it('lists only the device engines and Piper, labels Piper offline and plays clips for Piper only', () => {
    expect(engines()).toEqual(['browser', 'piper']);
    expect(Object.keys(ENGINE_LABEL).sort()).toEqual(['browser', 'native', 'piper']);
    expect(ENGINE_LABEL.piper).toBe('Giọng Piper (offline, trên máy)');
    expect(playsClips('piper')).toBe(true);
    expect(playsClips('browser')).toBe(false);
    expect(playsClips('native')).toBe(false);
  });

  it('lists only Vietnamese voices of the browser and the app', async () => {
    const mk = (voiceURI: string, name: string, lang: string): object => ({ voiceURI, name, lang });
    const all = [mk('en', 'Aria', 'en-US'), mk('vn2', 'Linh', 'vi_VN'), mk('fr', 'Denise', 'fr-FR'), mk('vn1', 'HoaiMy', 'vi-VN')];
    vi.stubGlobal('speechSynthesis', { getVoices: () => all, addEventListener() {}, removeEventListener() {}, cancel() {} });
    expect((await voices('browser')).map((v) => v.id)).toEqual(['vn1', 'vn2']);
    vi.stubGlobal('Capacitor', { Plugins: { TextToSpeech: { getSupportedVoices: async () => ({ voices: all.map((v) => ({ ...v })) }) } } });
    expect((await voices('native')).map((v) => v.id)).toEqual(['vn1', 'vn2']);
  });

  it('offers every voice (with its speaker) for the picker', async () => {
    const vs = await voices('piper');
    expect(vs).toHaveLength(19);
    expect(vs.every((v) => v.lang === 'vi-VN')).toBe(true);
  });
});
