import { afterEach, describe, expect, it, vi } from 'vitest';
import { copyText, saveTextFile } from './export-file';

const g = globalThis as Record<string, unknown>;
afterEach(() => {
  delete g.Capacitor;
  vi.restoreAllMocks();
});

describe('saveTextFile', () => {
  it('writes to cache and shares through the Capacitor plugins', async () => {
    const writeFile = vi.fn().mockResolvedValue({ uri: 'file:///cache/b.json' });
    const share = vi.fn().mockResolvedValue({});
    g.Capacitor = { isNativePlatform: () => true, Plugins: { Filesystem: { writeFile }, Share: { share } } };
    expect(await saveTextFile('b.json', '{}')).toBe('shared');
    expect(writeFile).toHaveBeenCalledWith(expect.objectContaining({ path: 'b.json', data: '{}', directory: 'CACHE' }));
    expect(share).toHaveBeenCalledWith(expect.objectContaining({ url: 'file:///cache/b.json' }));
  });
  it('asks the caller to show the text when the native shell has no way to save', async () => {
    g.Capacitor = { isNativePlatform: () => true, Plugins: {} };
    expect(await saveTextFile('b.json', '{}')).toBe('manual');
  });
  it('downloads through a link in a plain browser', async () => {
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    URL.createObjectURL = vi.fn(() => 'blob:x');
    URL.revokeObjectURL = vi.fn();
    expect(await saveTextFile('b.json', '{}')).toBe('saved');
    expect(click).toHaveBeenCalled();
  });
});

describe('copyText', () => {
  it('falls back to execCommand when the Clipboard API is denied', async () => {
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: vi.fn().mockRejectedValue(new Error('denied')) } });
    document.execCommand = vi.fn(() => true);
    expect(await copyText('hi')).toBe(true);
    expect(document.execCommand).toHaveBeenCalledWith('copy');
  });
});
