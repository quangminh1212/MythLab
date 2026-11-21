import { describe, expect, it } from 'vitest';
import { silentWav } from './mediasession';
import { isPipSupported } from './pip';

describe('media popup helpers', () => {
  it('builds a valid one-second silent WAV data URI', () => {
    const u = silentWav();
    expect(u.startsWith('data:audio/wav;base64,')).toBe(true);
    const b = atob(u.split(',')[1] as string);
    expect(b.slice(0, 4)).toBe('RIFF');
    expect(b.length).toBe(44 + 8000);
  });
  it('hides picture-in-picture where the browser has no API', () => {
    expect(isPipSupported()).toBe(false);
  });
  it('detects documentPictureInPicture when present', () => {
    (window as unknown as { documentPictureInPicture: unknown }).documentPictureInPicture = { requestWindow: async () => window };
    expect(isPipSupported()).toBe(true);
    delete (window as unknown as { documentPictureInPicture?: unknown }).documentPictureInPicture;
  });
});
