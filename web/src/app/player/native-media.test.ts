import { beforeEach, describe, expect, it, vi } from 'vitest';

const native = { on: true };
vi.mock('../core/settings', async (orig) => ({ ...(await orig<typeof import('../core/settings')>()), isNative: () => native.on }));

import { initNativeMedia, resetNativeMedia } from './native-media';

function fakePlayer() {
  let st: Record<string, unknown> = { status: 'idle' };
  let fn: () => void = () => {};
  return {
    set(s: Record<string, unknown>) {
      st = s;
      fn();
    },
    p: {
      getState: () => st,
      onState: (f: () => void) => {
        fn = f;
        return () => {};
      },
      resume: vi.fn(),
      pause: vi.fn(),
      gotoChapter: vi.fn(),
    },
  };
}

describe('native media bridge', () => {
  let handler: (e: { action?: string }) => void = () => {};
  const plug = {
    start: vi.fn(async () => ({})),
    update: vi.fn(async () => ({})),
    stop: vi.fn(async () => ({})),
    addListener: vi.fn(async (_n: string, f: (e: { action?: string }) => void) => {
      handler = f;
      return { remove() {} };
    }),
  };
  beforeEach(() => {
    vi.clearAllMocks();
    resetNativeMedia();
    native.on = true;
    (globalThis as { Capacitor?: unknown }).Capacitor = { registerPlugin: () => plug };
  });

  it('does nothing in the browser', () => {
    native.on = false;
    const f = fakePlayer();
    initNativeMedia(f.p as never);
    f.set({ status: 'playing' });
    expect(plug.start).not.toHaveBeenCalled();
    expect(plug.addListener).not.toHaveBeenCalled();
  });

  it('starts, updates, and stops with the player', () => {
    const f = fakePlayer();
    initNativeMedia(f.p as never);
    f.set({ status: 'playing', chapterTitle: 'Ch 1', storyName: 'S' });
    expect(plug.start).toHaveBeenCalledWith({ title: 'Ch 1', artist: 'S' });
    f.set({ status: 'paused', chapterTitle: 'Ch 1', storyName: 'S' });
    expect(plug.update).toHaveBeenCalledWith({ title: 'Ch 1', artist: 'S', playing: false });
    f.set({ status: 'paused', chapterTitle: 'Ch 1', storyName: 'S' });
    expect(plug.update).toHaveBeenCalledTimes(1);
    f.set({ status: 'idle' });
    expect(plug.stop).toHaveBeenCalledTimes(1);
  });

  it('routes notification actions to the player', () => {
    const f = fakePlayer();
    initNativeMedia(f.p as never);
    f.set({ status: 'playing', idx: 4 });
    handler({ action: 'pause' });
    handler({ action: 'play' });
    handler({ action: 'next' });
    handler({ action: 'previous' });
    expect(f.p.pause).toHaveBeenCalled();
    expect(f.p.resume).toHaveBeenCalled();
    expect(f.p.gotoChapter).toHaveBeenCalledWith(5);
    expect(f.p.gotoChapter).toHaveBeenCalledWith(3);
  });
});
