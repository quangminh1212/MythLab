import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const native = vi.hoisted(() => ({ on: true }));
vi.mock('../settings', async (orig) => ({ ...(await orig<typeof import('../settings')>()), isNative: () => native.on }));

import { CACHE, chapterKey, fingerprint, identUrl, scopeOf } from '../../../sw/shared';
import { createServerBackend } from './server';

const store = new Map<string, Map<string, Response>>();
function fakeCaches(): CacheStorage {
  return {
    open: async (name: string) => {
      const m = store.get(name) ?? new Map<string, Response>();
      store.set(name, m);
      return {
        match: async (r: string | Request) => m.get(typeof r === 'string' ? r : r.url)?.clone(),
        put: async (r: string | Request, res: Response) => void m.set(typeof r === 'string' ? r : r.url, res),
      } as unknown as Cache;
    },
  } as unknown as CacheStorage;
}

const pin = async (file: string, text: string): Promise<void> => {
  const c = await caches.open(CACHE.pinned);
  await c.put(chapterKey(scopeOf(location.href), 'local0', 'story', file), new Response(JSON.stringify({ file, text })));
};

beforeEach(() => {
  store.clear();
  native.on = true;
  vi.stubGlobal('caches', fakeCaches());
});
afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe('native offline reading', () => {
  it('serves a downloaded chapter without touching the network', async () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => {})); // a host that drops packets: never answers
    vi.stubGlobal('fetch', fetchMock);
    await pin('c1.txt', 'xin chao');
    const b = createServerBackend('http://192.168.1.113:18980', 'k');
    const r = await b.get<{ text: string }>('/chapter?source=local0&key=story&file=c1.txt');
    expect(r.text).toBe('xin chao');
    expect(fetchMock).not.toHaveBeenCalled();
  });

  const silent = (): void =>
    void vi.stubGlobal('fetch', (_u: string, init?: RequestInit) => new Promise<Response>((_res, rej) => init?.signal?.addEventListener('abort', () => rej(new DOMException('x', 'AbortError')))));
  const saveStory = async (base: string, key: string): Promise<void> => {
    const k = identUrl(scopeOf(location.href) + '__native/api/story?source=local0&key=story', await fingerprint(base, key));
    await (await caches.open(CACHE.api)).put(k, new Response(JSON.stringify({ title: 'saved' })));
  };

  /** Records the delay of every timer the backend arms and fires it at once. */
  const delays: number[] = [];
  const instantTimers = (): void => {
    delays.length = 0;
    const real = globalThis.setTimeout;
    vi.spyOn(globalThis, 'setTimeout').mockImplementation(((fn: () => void, ms?: number) => {
      delays.push(ms ?? 0);
      return real(fn, 0);
    }) as typeof setTimeout);
  };

  it('uses the saved copy, after a short delay, when the server is silent', async () => {
    const base = 'http://192.168.1.113:18980';
    await saveStory(base, 'k');
    instantTimers();
    silent();
    const r = await createServerBackend(base, 'k').get<{ title: string }>('/story?source=local0&key=story', { timeout: 60_000 });
    expect(r.title).toBe('saved');
    expect(delays).toContain(8_000);
    expect(delays).not.toContain(60_000);
  });

  it('keeps the caller timeout when there is no saved copy (a slow server still answers)', async () => {
    instantTimers();
    silent();
    await expect(createServerBackend('http://192.168.1.113:18980', 'k').get('/story?source=local0&key=story', { timeout: 60_000 })).rejects.toBeTruthy();
    expect(delays).toContain(60_000);
    expect(delays).not.toContain(8_000);
  });

  it('does not read the device first outside the native app', async () => {
    native.on = false;
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ file: 'c1.txt', text: 'live' })));
    vi.stubGlobal('fetch', fetchMock);
    await pin('c1.txt', 'cached');
    const b = createServerBackend('http://h:1', 'k');
    const r = await b.get<{ text: string }>('/chapter?source=local0&key=story&file=c1.txt');
    expect(r.text).toBe('live');
    expect(fetchMock).toHaveBeenCalled();
  });
});
