import { afterEach, describe, expect, it, vi } from 'vitest';
import { iosGoogleClientId, isNativeIOS, nativePlatform } from './native-platform';
import { appUpdate } from './app-update';
import { engineChoices } from '../settings/voices';
import { initNativeMedia, resetNativeMedia } from '../player/native-media';

const g = globalThis as { Capacitor?: unknown };
const cap = (platform: string | undefined, plugins: Record<string, unknown> = {}) => {
  g.Capacitor = { isNativePlatform: () => true, ...(platform ? { getPlatform: () => platform } : {}), Plugins: plugins };
};
afterEach(() => {
  delete g.Capacitor;
  appUpdate._reset();
  resetNativeMedia();
});

describe('nativePlatform', () => {
  it('web without Capacitor, or when the bridge says not native', () => {
    expect(nativePlatform()).toBe('web');
    g.Capacitor = { isNativePlatform: () => false, getPlatform: () => 'ios' };
    expect(nativePlatform()).toBe('web');
    expect(isNativeIOS()).toBe(false);
  });
  it('reads getPlatform; a bridge without it counts as Android', () => {
    cap('ios');
    expect(nativePlatform()).toBe('ios');
    expect(isNativeIOS()).toBe(true);
    cap('android');
    expect(nativePlatform()).toBe('android');
    cap(undefined);
    expect(nativePlatform()).toBe('android');
  });
});

describe('no APK self-update on iOS', () => {
  const update = { getInfo: vi.fn(), fetchManifest: vi.fn(), download: vi.fn(), install: vi.fn(), addListener: vi.fn() };
  it('is available on Android with the plugin', () => {
    cap('android', { AppUpdate: update });
    expect(appUpdate.available()).toBe(true);
  });
  it('is never offered on iOS, even if an AppUpdate plugin were present, and never touches the network', async () => {
    cap('ios', { AppUpdate: update });
    expect(appUpdate.available()).toBe(false);
    expect((await appUpdate.check()).kind).toBe('idle');
    expect((await appUpdate.checkIfDue()).kind).toBe('idle');
    await appUpdate.start();
    expect(update.getInfo).not.toHaveBeenCalled();
    expect(update.fetchManifest).not.toHaveBeenCalled();
    expect(update.download).not.toHaveBeenCalled();
  });
});

describe('Android-only native media service', () => {
  it('is not started on iOS', () => {
    const plugin = { start: vi.fn(), update: vi.fn(), stop: vi.fn(), addListener: vi.fn() };
    cap('ios', { MediaPlayback: plugin });
    const onState = vi.fn();
    initNativeMedia({ onState, getState: () => ({ status: 'idle' }) } as never);
    expect(onState).not.toHaveBeenCalled();
    expect(plugin.addListener).not.toHaveBeenCalled();
  });
});

describe('engine label', () => {
  it('names the device voice after the platform', () => {
    expect(engineChoices({ native: true, piper: true, ios: true })[0].label).toBe('Máy (iPhone/iPad)');
    expect(engineChoices({ native: true, piper: true })[0].label).toBe('Máy (Android)');
  });
});

describe('iosGoogleClientId', () => {
  const doc = (content: string | null) => ({ querySelector: () => (content === null ? null : { getAttribute: () => content }) }) as never;
  it('reads a valid iOS client id from the meta tag', () => {
    expect(iosGoogleClientId(doc(' 123-abc.apps.googleusercontent.com '))).toBe('123-abc.apps.googleusercontent.com');
  });
  it('is empty when missing or malformed', () => {
    expect(iosGoogleClientId(doc(null))).toBe('');
    expect(iosGoogleClientId(doc('evil"><script>'))).toBe('');
    expect(iosGoogleClientId(undefined)).toBe('');
  });
});
