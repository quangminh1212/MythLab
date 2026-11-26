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

  it('lists Piper, labels it offline and plays clips like Edge', () => {
    expect(engines()).toContain('piper');
    expect(ENGINE_LABEL.piper).toBe('Giọng Piper (offline, trên máy)');
    expect(playsClips('piper')).toBe(true);
    expect(playsClips('edge')).toBe(true);
    expect(playsClips('browser')).toBe(false);
  });

  it('offers the three voices for the picker', async () => {
    const vs = await voices('piper');
    expect(vs).toHaveLength(3);
    expect(vs.every((v) => v.lang === 'vi-VN')).toBe(true);
  });
});
