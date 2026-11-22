import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const native = vi.hoisted(() => ({ on: true }));
vi.mock('../settings', async (orig) => ({ ...(await orig<typeof import('../settings')>()), isNative: () => native.on }));

import { CACHE, chapterKey, fingerprint, HDR_AT, identUrl, LIMIT, scopeOf } from '../../../sw/shared';
import { createServerBackend } from './server';
import { pinnedNativeServer } from './index';

const store = new Map<string, Map<string, Response>>();
function fakeCaches(): CacheStorage {
  return {
    open: async (name: string) => {
      const m = store.get(name) ?? new Map<string, Response>();
      store.set(name, m);
      return {
        match: async (r: string | Request) => m.get(typeof r === 'string' ? r : r.url)?.clone(),
        put: async (r: string | Request, res: Response) => void m.set(typeof r === 'string' ? r : r.url, res),
        keys: async () => [...m.keys()].map((url) => ({ url }) as Request),
        delete: async (r: string | Request) => m.delete(typeof r === 'string' ? r : r.url),
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
    void vi.stubGlobal('fetch', (_u: string, init?: RequestInit) => new Promise<Response>((_res, rej) => {
      const fail = (): void => rej(new DOMException('x', 'AbortError'));
      if (init?.signal?.aborted) fail();
      else init?.signal?.addEventListener('abort', fail);
    }));
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

  it('turns a timeout into a non-abort error so the reader shows an error instead of a spinner', async () => {
    instantTimers();
    vi.stubGlobal('fetch', (_u: string, init?: RequestInit) => new Promise<Response>((_, rej) => init?.signal?.addEventListener('abort', () => rej(new DOMException('Aborted', 'AbortError')))));
    const err = await createServerBackend('http://192.168.1.113:18980', 'k').get('/chapter?source=local0&key=story&file=zz.txt', { timeout: 60_000 }).catch((e) => e);
    expect(err).toBeInstanceOf(Error);
    expect((err as Error).name).not.toBe('AbortError');
  });

  it('keeps AbortError when the caller aborts', async () => {
    const real = globalThis.setTimeout;
    const ctl = new AbortController();
    vi.stubGlobal('fetch', (_u: string, init?: RequestInit) => new Promise<Response>((_, rej) => init?.signal?.addEventListener('abort', () => rej(new DOMException('Aborted', 'AbortError')))));
    const p = createServerBackend('http://h:1', 'k').get('/story?source=a&key=b', { timeout: 60_000, signal: ctl.signal }).catch((e) => e);
    await new Promise((r) => real(r, 20));
    ctl.abort();
    expect(((await p) as Error).name).toBe('AbortError');
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

  it('does not serve a saved copy when the server answers with an error', async () => {
    const base = 'http://h:1';
    await saveStory(base, 'k');
    vi.stubGlobal('fetch', async () => new Response(JSON.stringify({ error: 'not found' }), { status: 404 }));
    await expect(createServerBackend(base, 'k').get('/story?source=local0&key=story')).rejects.toMatchObject({ status: 404 });
  });

  it('does not serve a saved copy when the caller aborts', async () => {
    const base = 'http://h:1';
    await saveStory(base, 'k');
    silent();
    const ctl = new AbortController();
    const p = createServerBackend(base, 'k').get('/story?source=local0&key=story', { signal: ctl.signal });
    ctl.abort();
    await expect(p).rejects.toBeTruthy();
  });

  it('never serves a copy saved for another key', async () => {
    await saveStory('http://h:1', 'old');
    vi.stubGlobal('fetch', async () => Promise.reject(new TypeError('offline')));
    await expect(createServerBackend('http://h:1', 'new').get('/story?source=local0&key=story')).rejects.toBeTruthy();
  });

  describe('native api cache trim', () => {
    const seed = async (n: number): Promise<Cache> => {
      const c = await caches.open(CACHE.api);
      for (let i = 0; i < n; i++) await c.put(`http://x/__native/api/e${i}?__ml=z`, new Response('{}', { headers: { [HDR_AT]: String(1000 + i) } }));
      return c;
    };
    const settle = (): Promise<void> => new Promise((r) => setTimeout(r, 30));
    const live = (): void => void vi.stubGlobal('fetch', async () => new Response(JSON.stringify({ title: 'live' })));

    it('drops the oldest native entries beyond the cap and keeps the newest', async () => {
      const c = await seed(LIMIT.api + 20);
      live();
      await createServerBackend('http://h:1', 'k').get('/story?source=local0&key=story');
      await settle();
      const left = (await c.keys!()).map((r) => r.url);
      expect(left.filter((u) => u.includes('__native')).length).toBe(LIMIT.api);
      expect(left).not.toContain('http://x/__native/api/e0?__ml=z');
      expect(left).toContain(`http://x/__native/api/e${LIMIT.api + 19}?__ml=z`);
      expect(left.some((u) => u.includes('/api/story'))).toBe(true);
    });

    it('leaves a bucket under the cap alone and ignores non-native entries', async () => {
      const c = await seed(10);
      await c.put('http://x/other/thing', new Response('{}'));
      live();
      await createServerBackend('http://h:1', 'k').get('/story?source=local0&key=story');
      await settle();
      expect((await c.keys!()).length).toBe(12);
    });

    it('does not delay the read path while trimming', async () => {
      await seed(LIMIT.api + 5);
      live();
      const t = await createServerBackend('http://h:1', 'k').get<{ title: string }>('/story?source=local0&key=story');
      expect(t.title).toBe('live');
    });
  });

  it('pins the native app to myth.xlabrnd.com and leaves other builds alone', () => {
    expect(pinnedNativeServer(null, false)).toBeNull();
    expect(pinnedNativeServer({ url: 'http://192.168.1.113:8765', key: 'k' }, false)?.url).toBe('http://192.168.1.113:8765');
    expect(pinnedNativeServer(null, true)).toEqual({ url: 'https://myth.xlabrnd.com', key: '' });
    expect(pinnedNativeServer({ url: 'http://192.168.1.9:8765', key: 'lan' }, true)).toEqual({ url: 'https://myth.xlabrnd.com', key: '' });
    expect(pinnedNativeServer({ url: 'https://myth.xlabrnd.com/truyen', key: 'kept' }, true)).toEqual({ url: 'https://myth.xlabrnd.com/truyen', key: 'kept' });
  });

  it('serves the saved copy when the network fails, and remembers live answers', async () => {
    const base = 'http://h:1';
    vi.stubGlobal('fetch', async () => new Response(JSON.stringify({ title: 'live' })));
    const b = createServerBackend(base, 'k');
    expect((await b.get<{ title: string }>('/story?source=local0&key=story')).title).toBe('live');
    await new Promise((r) => setTimeout(r, 20));
    vi.stubGlobal('fetch', async () => Promise.reject(new TypeError('offline')));
    expect((await b.get<{ title: string }>('/story?source=local0&key=story')).title).toBe('live');
  });
});
