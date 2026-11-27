import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const h = vi.hoisted(() => ({
  have: new Set<string>(),
  install: null as null | ((id: string, p?: (f: number) => void) => Promise<void>),
  confirm: true,
}));

vi.mock('./piper', async (orig) => {
  const real = await orig<typeof import('./piper')>();
  return {
    ...real,
    piperSupported: () => true,
    refreshPiper: async () => {},
    piperInstalled: (id: string) => h.have.has(id),
    installPiper: (id: string, p?: (f: number) => void) => (h.install as NonNullable<typeof h.install>)(id, p),
  };
});
vi.mock('../core/ui', () => ({ toast: vi.fn(), confirmDialog: vi.fn(async () => h.confirm) }));

import { S } from '../core/settings';
import { confirmDialog, toast } from '../core/ui';
import { autoInstallVoice, Declined, ensureVoice, installVoiceOnce, voiceProgress } from './autovoice';

const installed: string[] = [];

beforeEach(() => {
  h.have.clear();
  h.confirm = true;
  installed.length = 0;
  h.install = async (id, p) => {
    installed.push(id);
    p?.(0.5);
    p?.(1);
    h.have.add(id);
  };
  S.engine = 'piper';
  S.piperVoice = 'vi_VN-vais1000-medium';
  vi.mocked(toast).mockClear();
  vi.mocked(confirmDialog).mockClear();
});
afterEach(() => vi.unstubAllGlobals());

describe('automatic voice download', () => {
  it('downloads only the selected voice (the light default), without a dialog', async () => {
    expect(await autoInstallVoice()).toBe(true);
    expect(installed).toEqual(['vi_VN-vais1000-medium']);
    expect(confirmDialog).not.toHaveBeenCalled();
    expect(voiceProgress()).toBe(-1);
  });

  it('downloads nothing when the voice is already on the device (later loads)', async () => {
    h.have.add('vi_VN-vais1000-medium');
    expect(await autoInstallVoice()).toBe(true);
    expect(installed).toEqual([]);
  });

  it('respects the data saver', async () => {
    vi.stubGlobal('navigator', { connection: { saveData: true }, onLine: true });
    expect(await autoInstallVoice()).toBe(false);
    expect(installed).toEqual([]);
  });

  it('does nothing for the Android voice engine', async () => {
    S.engine = 'native';
    expect(await autoInstallVoice()).toBe(false);
    expect(installed).toEqual([]);
  });

  it('survives a failure, tells the user, and tries again when the network is back', async () => {
    let fail = true;
    h.install = async (id) => {
      installed.push(id);
      if (fail) throw new Error('mất mạng');
      h.have.add(id);
    };
    expect(await autoInstallVoice()).toBe(false);
    expect(vi.mocked(toast).mock.calls.some((c) => JSON.stringify(c[0]).includes('Sẽ thử lại'))).toBe(true);
    fail = false;
    window.dispatchEvent(new Event('online'));
    await vi.waitFor(() => expect(h.have.has('vi_VN-vais1000-medium')).toBe(true));
    expect(installed).toHaveLength(2);
  });

  it('waits for the network instead of failing when offline', async () => {
    vi.stubGlobal('navigator', { onLine: false });
    expect(await autoInstallVoice()).toBe(false);
    expect(installed).toEqual([]);
  });
});

describe('ensureVoice (play pressed before the voice is ready)', () => {
  it('joins the download that is already running instead of starting a second one', async () => {
    let release: () => void = () => {};
    h.install = (id) =>
      new Promise<void>((res) => {
        installed.push(id);
        release = () => {
          h.have.add(id);
          res();
        };
      });
    const auto = autoInstallVoice();
    await vi.waitFor(() => expect(installed).toHaveLength(1));
    const play = ensureVoice();
    release();
    await Promise.all([auto, play]);
    expect(installed).toHaveLength(1);
    expect(confirmDialog).not.toHaveBeenCalled();
  });

  it('asks before a big voice the user picked, and stops when declined', async () => {
    h.confirm = false;
    await expect(ensureVoice('vi_VN-csa-voice-piper-v3-medium#0')).rejects.toBeInstanceOf(Declined);
    expect(installed).toEqual([]);
    h.confirm = true;
    await ensureVoice('vi_VN-csa-voice-piper-v3-medium#0');
    expect(installed).toEqual(['vi_VN-csa-voice-piper-v3-medium']);
  });

  it('manual downloads share one running download per model', async () => {
    let n = 0;
    h.install = async (id) => {
      n++;
      await new Promise((r) => setTimeout(r, 5));
      h.have.add(id);
    };
    await Promise.all([installVoiceOnce('vi_VN-csa-voice-piper-v3-medium#0'), installVoiceOnce('vi_VN-csa-voice-piper-v3-medium#3')]);
    expect(n).toBe(1);
  });
});

describe('low-memory phones (navigator.deviceMemory <= 2)', () => {
  const HEAVY = 'vi_VN-csa-voice-piper-v3-medium#0';
  beforeEach(() => vi.stubGlobal('navigator', { deviceMemory: 2, onLine: true }));

  it('the player gives a not-yet-downloaded heavy voice the lightest voice, with no heavy download and no dialog', async () => {
    S.piperVoice = HEAVY;
    await ensureVoice(HEAVY);
    expect(installed).toEqual(['vi_VN-vais1000-medium']);
    expect(S.piperVoice).toBe('vi_VN-vais1000-medium#0');
    expect(confirmDialog).not.toHaveBeenCalled();
  });

  it('the automatic download does the same', async () => {
    S.piperVoice = 'kokoro-vi-lite#0';
    expect(await autoInstallVoice()).toBe(true);
    expect(installed).toEqual(['vi_VN-vais1000-medium']);
    expect(S.piperVoice).toBe('vi_VN-vais1000-medium#0');
  });

  it('a heavy voice that is already on the device is kept', async () => {
    h.have.add('vi_VN-csa-voice-piper-v3-medium');
    S.piperVoice = HEAVY;
    await ensureVoice(HEAVY);
    expect(installed).toEqual([]);
    expect(S.piperVoice).toBe(HEAVY);
  });

  it('does not change anything on a phone with enough memory', async () => {
    vi.stubGlobal('navigator', { deviceMemory: 4, onLine: true });
    S.piperVoice = HEAVY;
    await ensureVoice(HEAVY);
    expect(installed).toEqual(['vi_VN-csa-voice-piper-v3-medium']);
    expect(S.piperVoice).toBe(HEAVY);
  });
});
