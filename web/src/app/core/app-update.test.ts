import { afterEach, describe, expect, it, vi } from 'vitest';
import { appUpdate, isNewer, parseManifest } from './app-update';

const BASE = 'https://myth.xlabrnd.com/android/latest.json';
const SHA = 'a'.repeat(64);
const good = { versionCode: 10100, versionName: '1.1.0', url: 'MythLab.apk', sha256: SHA, size: 5000, notes: 'Mới' };

describe('parseManifest', () => {
  it('accepts a valid manifest and resolves a relative url', () => {
    expect(parseManifest(good, BASE)).toEqual({ versionCode: 10100, versionName: '1.1.0', url: 'https://myth.xlabrnd.com/android/MythLab.apk', sha256: SHA, size: 5000, notes: 'Mới' });
  });
  it('lower-cases the checksum and defaults the optional fields', () => {
    const m = parseManifest({ versionCode: 5, url: '/x.apk', sha256: 'A'.repeat(64) }, BASE);
    expect(m).toMatchObject({ sha256: SHA, size: 0, notes: '', versionName: '5' });
  });
  it.each([
    ['not an object', null],
    ['float version', { ...good, versionCode: 1.5 }],
    ['zero version', { ...good, versionCode: 0 }],
    ['string version', { ...good, versionCode: '10100' }],
    ['short checksum', { ...good, sha256: 'abc' }],
    ['missing url', { ...good, url: '' }],
    ['http url', { ...good, url: 'http://myth.xlabrnd.com/a.apk' }],
    ['other host', { ...good, url: 'https://evil.example/a.apk' }],
  ])('rejects %s', (_n, raw) => {
    expect(parseManifest(raw, BASE)).toBeNull();
  });
});

describe('isNewer', () => {
  it('compares version codes', () => {
    expect(isNewer({ versionCode: 2 }, { versionCode: 1 })).toBe(true);
    expect(isNewer({ versionCode: 1 }, { versionCode: 1 })).toBe(false);
    expect(isNewer({ versionCode: 1 }, { versionCode: 2 })).toBe(false);
  });
});

function fakeNative(over: Record<string, unknown> = {}) {
  const pl = {
    getInfo: vi.fn().mockResolvedValue({ versionCode: 10000, versionName: '1.0.0', canInstall: true }),
    fetchManifest: vi.fn().mockResolvedValue({ text: JSON.stringify(good) }),
    download: vi.fn().mockResolvedValue({ size: 5000 }),
    install: vi.fn().mockResolvedValue({}),
    addListener: vi.fn().mockResolvedValue({ remove: vi.fn() }),
    ...over,
  };
  (globalThis as { Capacitor?: unknown }).Capacitor = { isNativePlatform: () => true, Plugins: { AppUpdate: pl } };
  return pl;
}

describe('appUpdate', () => {
  afterEach(() => {
    delete (globalThis as { Capacitor?: unknown }).Capacitor;
    appUpdate._reset();
    localStorage.clear();
  });

  it('does nothing outside the Android app', async () => {
    expect(appUpdate.available()).toBe(false);
    expect((await appUpdate.check()).kind).toBe('idle');
  });

  it('offers a newer version', async () => {
    fakeNative();
    const s = await appUpdate.check();
    expect(s.kind).toBe('available');
    if (s.kind === 'available') expect(s.latest.versionName).toBe('1.1.0');
  });

  it('says up to date when the installed version is not older', async () => {
    fakeNative({ getInfo: vi.fn().mockResolvedValue({ versionCode: 10100, versionName: '1.1.0', canInstall: true }) });
    expect((await appUpdate.check()).kind).toBe('uptodate');
  });

  it('treats a missing or invalid manifest as up to date, not as an error', async () => {
    fakeNative({ fetchManifest: vi.fn().mockRejectedValue(new Error('HTTP 404')) });
    expect((await appUpdate.check()).kind).toBe('uptodate');
    appUpdate._reset();
    fakeNative({ fetchManifest: vi.fn().mockResolvedValue({ text: '<html>' }) });
    expect((await appUpdate.check()).kind).toBe('uptodate');
  });

  it('reports a network failure', async () => {
    fakeNative({ fetchManifest: vi.fn().mockRejectedValue(new Error('timeout')) });
    const s = await appUpdate.check();
    expect(s.kind).toBe('error');
  });

  it('downloads then opens the installer', async () => {
    const pl = fakeNative();
    await appUpdate.check();
    await appUpdate.start();
    expect(pl.download).toHaveBeenCalledWith({ url: 'https://myth.xlabrnd.com/android/MythLab.apk', sha256: SHA });
    expect(pl.install).toHaveBeenCalledOnce();
    expect(appUpdate.get()).toMatchObject({ kind: 'ready', needPermission: false });
  });

  it('asks for the install permission when Android has not granted it', async () => {
    fakeNative({ install: vi.fn().mockRejectedValue({ message: 'permission' }) });
    await appUpdate.check();
    await appUpdate.start();
    expect(appUpdate.get()).toMatchObject({ kind: 'ready', needPermission: true });
  });

  it('shows a checksum failure and can retry the download', async () => {
    const pl = fakeNative({ download: vi.fn().mockRejectedValueOnce(new Error('checksum')).mockResolvedValue({}) });
    await appUpdate.check();
    await appUpdate.start();
    const s = appUpdate.get();
    expect(s.kind).toBe('error');
    await appUpdate.start();
    expect(pl.download).toHaveBeenCalledTimes(2);
    expect(appUpdate.get().kind).toBe('ready');
  });

  it('announces a version once', () => {
    expect(appUpdate.firstSight(10100)).toBe(true);
    expect(appUpdate.firstSight(10100)).toBe(false);
    expect(appUpdate.firstSight(10200)).toBe(true);
  });
});
