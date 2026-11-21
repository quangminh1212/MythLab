import { beforeEach, describe, expect, it, vi } from 'vitest';

const get = vi.fn();
vi.mock('./backend/index', () => ({ backend: { get: (...a: unknown[]) => get(...a) } }));

import { data } from './data';

beforeEach(() => {
  get.mockReset();
  data.invalidate();
});

describe('data cache', () => {
  it('serves repeated calls from the cache and refetches after invalidate', async () => {
    get.mockResolvedValue({ sources: [] });
    await data.sources();
    await data.sources();
    expect(get).toHaveBeenCalledTimes(1);
    data.invalidate();
    await data.sources();
    expect(get).toHaveBeenCalledTimes(2);
  });

  it('does not cache a failed request', async () => {
    get.mockRejectedValueOnce(new Error('boom')).mockResolvedValueOnce({ sources: [] });
    await expect(data.sources()).rejects.toThrow('boom');
    await Promise.resolve();
    await data.sources();
    expect(get).toHaveBeenCalledTimes(2);
  });

  it('rejects with AbortError on abort without cancelling the shared request', async () => {
    let resolve!: (v: unknown) => void;
    get.mockReturnValue(new Promise((r) => (resolve = r)));
    const ac = new AbortController();
    const p = data.sources({ signal: ac.signal });
    ac.abort();
    const err = await p.catch((e: unknown) => e);
    expect(data.isAbort(err)).toBe(true);
    resolve({ sources: [] });
    await expect(data.sources()).resolves.toEqual({ sources: [] });
    expect(get).toHaveBeenCalledTimes(1);
  });

  it('rejects at once when the signal is already aborted', async () => {
    get.mockResolvedValue({ sources: [] });
    const ac = new AbortController();
    ac.abort();
    expect(data.isAbort(await data.sources({ signal: ac.signal }).catch((e: unknown) => e))).toBe(true);
  });
});
