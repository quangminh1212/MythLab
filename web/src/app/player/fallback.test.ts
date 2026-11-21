import { describe, expect, it, vi } from 'vitest';
import { S } from '../core/settings';
import { Interrupted, Stopped } from './engines';
import { shouldFallBackToEdge, speakDeviceWithEdgeFallback, type DeviceFallbackDeps } from './fallback';

function notAllowed(): Error {
  const e = new Error('blocked');
  e.name = 'NotAllowedError';
  return e;
}

function deps(over: Partial<DeviceFallbackDeps> & { fail?: unknown } = {}): DeviceFallbackDeps & { calls: string[] } {
  const calls: string[] = [];
  const { fail, ...rest } = over;
  return {
    calls,
    device: vi.fn(async () => {
      calls.push('device');
      if (fail !== undefined) throw fail;
    }),
    edge: vi.fn(async () => {
      calls.push('edge');
    }),
    stale: () => false,
    edgeUsable: () => true,
    onFallback: vi.fn(() => {
      calls.push('fallback');
    }),
    ...rest,
  };
}

describe('device voice to Edge fallback', () => {
  it('reads with the device voice and never touches Edge when it works', async () => {
    const d = deps();
    await speakDeviceWithEdgeFallback(d);
    expect(d.calls).toEqual(['device']);
    expect(d.onFallback).not.toHaveBeenCalled();
  });

  it('switches to Edge, announcing first, when the device voice fails', async () => {
    const d = deps({ fail: new Error('no tts engine') });
    await speakDeviceWithEdgeFallback(d);
    expect(d.calls).toEqual(['device', 'fallback', 'edge']);
  });

  it('propagates an Edge failure after falling back', async () => {
    const boom = new Error('edge failed');
    const d = deps({ fail: new Error('x'), edge: vi.fn(async () => { throw boom; }) });
    await expect(speakDeviceWithEdgeFallback(d)).rejects.toBe(boom);
  });

  it.each([
    ['Stopped', () => new Stopped()],
    ['Interrupted', () => new Interrupted()],
    ['NotAllowedError', notAllowed],
  ])('does not fall back on %s and rethrows it', async (_n, make) => {
    const err = make();
    const d = deps({ fail: err });
    await expect(speakDeviceWithEdgeFallback(d)).rejects.toBe(err);
    expect(d.edge).not.toHaveBeenCalled();
    expect(d.onFallback).not.toHaveBeenCalled();
  });

  it('does not fall back when the generation changed', async () => {
    const err = new Error('late failure');
    const d = deps({ fail: err, stale: () => true });
    await expect(speakDeviceWithEdgeFallback(d)).rejects.toBe(err);
    expect(d.edge).not.toHaveBeenCalled();
    expect(d.onFallback).not.toHaveBeenCalled();
  });

  it('does not fall back when Edge is unavailable or down', async () => {
    const err = new Error('no tts engine');
    const d = deps({ fail: err, edgeUsable: () => false });
    await expect(speakDeviceWithEdgeFallback(d)).rejects.toBe(err);
    expect(d.edge).not.toHaveBeenCalled();
    expect(d.onFallback).not.toHaveBeenCalled();
  });

  it('leaves the saved engine preference untouched', async () => {
    const before = S.engine;
    await speakDeviceWithEdgeFallback(deps({ fail: new Error('x') }));
    expect(S.engine).toBe(before);
  });

  it('shouldFallBackToEdge combines the three conditions', () => {
    const err = new Error('x');
    expect(shouldFallBackToEdge(err, false, true)).toBe(true);
    expect(shouldFallBackToEdge(err, true, true)).toBe(false);
    expect(shouldFallBackToEdge(err, false, false)).toBe(false);
    expect(shouldFallBackToEdge(null, false, true)).toBe(true);
  });
});
