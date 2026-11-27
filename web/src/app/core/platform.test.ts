import { describe, expect, it } from 'vitest';
import { isIOS, isIosSafari } from './platform';
import { iosHintDue } from '../pwa';

const IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1';
const MAC = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15';

describe('iOS detection', () => {
  it('iPhone and iPad user agents', () => {
    expect(isIOS({ userAgent: IPHONE, platform: 'iPhone', maxTouchPoints: 5 })).toBe(true);
    expect(isIOS({ userAgent: 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X)' })).toBe(true);
  });
  it('iPadOS in desktop mode is a Mac with touch', () => {
    expect(isIOS({ userAgent: MAC, platform: 'MacIntel', maxTouchPoints: 5 })).toBe(true);
  });
  it('a real Mac and Android are not iOS', () => {
    expect(isIOS({ userAgent: MAC, platform: 'MacIntel', maxTouchPoints: 0 })).toBe(false);
    expect(isIOS({ userAgent: 'Mozilla/5.0 (Linux; Android 14) Chrome/120', platform: 'Linux armv8l', maxTouchPoints: 5 })).toBe(false);
    expect(isIOS({})).toBe(false);
  });
  it('Safari versus other iOS browsers', () => {
    expect(isIosSafari({ userAgent: IPHONE, platform: 'iPhone', maxTouchPoints: 5 })).toBe(true);
    expect(isIosSafari({ userAgent: IPHONE + ' CriOS/120', platform: 'iPhone', maxTouchPoints: 5 })).toBe(false);
    expect(isIosSafari({ userAgent: MAC, platform: 'MacIntel', maxTouchPoints: 0 })).toBe(false);
  });
});

describe('iOS install hint', () => {
  it('shows once, only in Safari and not when installed', () => {
    expect(iosHintDue(false, 0, true)).toBe(true);
    expect(iosHintDue(true, 0, true)).toBe(false);
    expect(iosHintDue(false, 123, true)).toBe(false);
    expect(iosHintDue(false, 0, false)).toBe(false);
  });
});
