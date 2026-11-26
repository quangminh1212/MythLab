import { describe, expect, it } from 'vitest';
import { Interrupted, Stopped } from './engines';
import { isPlaybackSignal } from './fallback';

function notAllowed(): Error {
  const e = new Error('blocked');
  e.name = 'NotAllowedError';
  return e;
}

describe('isPlaybackSignal', () => {
  it.each([
    ['Stopped', () => new Stopped()],
    ['Interrupted', () => new Interrupted()],
    ['NotAllowedError', notAllowed],
  ])('treats %s as a signal, not as a voice failure', (_n, make) => {
    expect(isPlaybackSignal(make())).toBe(true);
  });

  it('treats real errors and non-errors as voice failures', () => {
    expect(isPlaybackSignal(new Error('boom'))).toBe(false);
    expect(isPlaybackSignal(null)).toBe(false);
    expect(isPlaybackSignal('x')).toBe(false);
  });
});
