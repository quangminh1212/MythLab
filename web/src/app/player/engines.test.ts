import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const ready = vi.hoisted(() => ({ value: false }));
vi.mock('./piper', async (orig) => ({ ...(await orig<typeof import('./piper')>()), piperReady: () => ready.value, piperSupported: () => true }));

import { S } from '../core/settings';
import { effectiveEngine, engines, ENGINE_LABEL, localEngine, playsClips, voices } from './engines';

beforeEach(() => {
  ready.value = false;
  S.engine = 'piper';
  // a browser with speechSynthesis and no Vietnamese voice: it must play no part
  vi.stubGlobal('speechSynthesis', { getVoices: () => [], addEventListener() {}, removeEventListener() {}, cancel() {} });
  vi.stubGlobal('SpeechSynthesisUtterance', class {});
});
afterEach(() => vi.unstubAllGlobals());

describe('engine choice (Piper on the web, the phone voice only in the Android app)', () => {
  it('speaks with Piper on the plain web, ready or still downloading (the player waits, never another voice)', () => {
    expect(effectiveEngine()).toBe('piper');
    ready.value = true;
    expect(effectiveEngine()).toBe('piper');
    expect(localEngine()).toBeNull();
  });

  it('a saved engine the host cannot run still ends on Piper on the web', () => {
    S.engine = 'native';
    expect(effectiveEngine()).toBe('piper');
  });

  it('uses the Android text-to-speech only when that plugin exists', () => {
    vi.stubGlobal('Capacitor', { Plugins: { TextToSpeech: {} } });
    expect(localEngine()).toBe('native');
    S.engine = 'native';
    expect(effectiveEngine()).toBe('native');
    S.engine = 'piper';
    expect(effectiveEngine()).toBe('piper');
  });

  it('lists Piper alone on the web (no browser engine), plus native in the app; Piper plays clips only', () => {
    expect(engines()).toEqual(['piper']);
    vi.stubGlobal('Capacitor', { Plugins: { TextToSpeech: {} } });
    expect(engines()).toEqual(['native', 'piper']);
    expect(Object.keys(ENGINE_LABEL).sort()).toEqual(['native', 'piper']);
    expect(ENGINE_LABEL.piper).toBe('Giọng Piper (offline, trên máy)');
    expect(playsClips('piper')).toBe(true);
    expect(playsClips('native')).toBe(false);
  });

  it('lists only Vietnamese voices of the app', async () => {
    const mk = (voiceURI: string, name: string, lang: string): object => ({ voiceURI, name, lang });
    const all = [mk('en', 'Aria', 'en-US'), mk('vn2', 'Linh', 'vi_VN'), mk('fr', 'Denise', 'fr-FR'), mk('vn1', 'HoaiMy', 'vi-VN')];
    vi.stubGlobal('Capacitor', { Plugins: { TextToSpeech: { getSupportedVoices: async () => ({ voices: all.map((v) => ({ ...v })) }) } } });
    expect((await voices('native')).map((v) => v.id)).toEqual(['vn1', 'vn2']);
  });

  it('offers every voice (with its speaker) for the picker', async () => {
    const vs = await voices('piper');
    expect(vs).toHaveLength(19);
    expect(vs.every((v) => v.lang === 'vi-VN')).toBe(true);
  });
});
