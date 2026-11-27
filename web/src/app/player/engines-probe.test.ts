import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

// the module remembers the device voice list, so every test gets a fresh copy
const h = vi.hoisted(() => ({ confirm: vi.fn(async (_o: unknown) => false), install: vi.fn(async (_id: string) => {}) }));
vi.mock('./piper', async (orig) => ({ ...(await orig<typeof import('./piper')>()), piperSupported: () => true, piperInstalled: () => false }));
vi.mock('./autovoice', () => ({ installVoiceOnce: h.install }));
vi.mock('../core/ui', () => ({ toast: vi.fn(), confirmDialog: h.confirm }));

async function load(voices: Array<{ voiceURI: string; lang: string }>, delay = 0) {
  vi.resetModules();
  const { S } = await import('../core/settings');
  S.engine = 'native';
  vi.stubGlobal('Capacitor', {
    Plugins: { TextToSpeech: { getSupportedVoices: () => new Promise((r) => setTimeout(() => r({ voices }), delay)), speak: vi.fn(), stop: vi.fn(async () => {}) } },
  });
  return import('./engines');
}

beforeEach(() => {
  h.confirm.mockClear();
  h.install.mockClear();
});
afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe('Android app: the player waits for the device voice probe', () => {
  it('settleEngine resolves only after the voices are listed; no Vietnamese voice makes Piper the engine and no fallback', async () => {
    const e = await load([{ voiceURI: 'en', lang: 'en-US' }], 30);
    expect(e.effectiveEngine()).toBe('native'); // before the probe
    let settled = false;
    const p = e.settleEngine().then(() => (settled = true));
    await Promise.resolve();
    expect(settled).toBe(false);
    await p;
    expect(e.effectiveEngine()).toBe('piper');
    expect(e.localEngine()).toBeNull(); // never the foreign device voice as a fallback
  });

  it('a device with a Vietnamese voice keeps reading with it', async () => {
    const e = await load([{ voiceURI: 'vn', lang: 'vi-VN' }]);
    await e.settleEngine();
    expect(e.effectiveEngine()).toBe('native');
    expect(e.localEngine()).toBe('native');
  });

  it('a probe that never answers does not block the player for ever', async () => {
    vi.useFakeTimers();
    const e = await load([{ voiceURI: 'vn', lang: 'vi-VN' }], 60_000);
    const p = e.settleEngine();
    await vi.advanceTimersByTimeAsync(6100);
    await p;
    expect(e.effectiveEngine()).toBe('native');
  });

  it('the device engine never speaks with a non-Vietnamese voice', async () => {
    const e = await load([{ voiceURI: 'en', lang: 'en-US' }]);
    const chunk = { p: 0, text: 'Xin chào.', sents: [{ s: 0, e: 9, at: 0, len: 9 }] };
    await expect(e.speak('native', chunk, { from: 0, rate: 1, pitch: 1, onSent() {} })).rejects.toThrow(/giọng tiếng Việt/);
    const tts = (globalThis as unknown as { Capacitor: { Plugins: { TextToSpeech: { speak: ReturnType<typeof vi.fn> } } } }).Capacitor.Plugins.TextToSpeech;
    expect(tts.speak).not.toHaveBeenCalled();
  });
});

describe('low-memory phones: explicit heavy voice downloads refuse by default', () => {
  it('offerPiper asks with Huỷ focused and downloads nothing when declined', async () => {
    vi.stubGlobal('navigator', { deviceMemory: 1, onLine: true });
    const e = await load([]);
    expect(await e.offerPiper('vi_VN-csa-voice-piper-v3-medium#0')).toBe(false);
    expect(h.confirm).toHaveBeenCalledOnce();
    expect(h.confirm.mock.calls[0]?.[0]).toMatchObject({ cancelFirst: true, confirmLabel: 'Vẫn tải' });
    expect(h.install).not.toHaveBeenCalled();
  });

  it('a light voice keeps the normal dialog', async () => {
    vi.stubGlobal('navigator', { deviceMemory: 1, onLine: true });
    const e = await load([]);
    await e.offerPiper('vi_VN-vais1000-medium');
    expect(h.confirm.mock.calls[0]?.[0]).not.toMatchObject({ cancelFirst: true });
  });
});
