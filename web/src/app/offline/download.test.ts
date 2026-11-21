import { beforeEach, describe, expect, it, vi } from 'vitest';

const get = vi.fn();
vi.mock('../core/backend/index', () => ({ backend: { kind: 'server', get: (...a: unknown[]) => get(...a) } }));

import { data } from '../core/data';
import { offline } from './index';

/** Minimal in-memory Cache Storage. `putFail` makes the next N puts throw (quota / WebView quirks). */
const store = new Map<string, Map<string, Response>>();
let putFail = 0;
let dropWrites = false;
function fakeCaches(): CacheStorage {
  return {
    open: async (name: string) => {
      const m = store.get(name) ?? new Map<string, Response>();
      store.set(name, m);
      return {
        match: async (r: string | Request) => m.get(typeof r === 'string' ? r : r.url)?.clone(),
        put: async (r: string | Request, res: Response) => {
          if (putFail > 0) {
            putFail--;
            throw new DOMException('quota', 'QuotaExceededError');
          }
          if (!dropWrites) m.set(typeof r === 'string' ? r : r.url, res);
        },
        keys: async () => [...m.keys()].map((u) => new Request(u)),
        delete: async (r: string | Request) => m.delete(typeof r === 'string' ? r : r.url),
      } as unknown as Cache;
    },
  } as unknown as CacheStorage;
}

const chapters = Array.from({ length: 5 }, (_, i) => ({ file: `c${i + 1}.txt`, title: `C${i + 1}` })) as never[];
const body = (file: string) => ({ file, title: file, text: 'x' });
const run = (): Promise<{ done: number; total: number; failed: number; lastError?: string }> =>
  offline.startJob('s', 'k/story', { chapters, name: 'Story', total: 5 }).finished;
const stored = async (): Promise<number> => (await offline.storedFiles('s', 'k/story')).size;

beforeEach(() => {
  store.clear();
  putFail = 0;
  dropWrites = false;
  get.mockReset();
  data.invalidate();
  vi.stubGlobal('caches', fakeCaches());
  vi.useFakeTimers({ shouldAdvanceTime: true });
  vi.setSystemTime(Date.now());
});

describe('download job', () => {
  it('stores all chapters with zero failures when every fetch succeeds (repeated)', async () => {
    for (let n = 0; n < 15; n++) {
      store.clear();
      data.invalidate();
      get.mockImplementation(async (p: string) => {
        await new Promise((r) => setTimeout(r, Math.random() * 20));
        return body(new URL(p, 'http://x').searchParams.get('file') as string);
      });
      const pr = await run();
      expect(pr).toMatchObject({ done: 5, total: 5, failed: 0 });
      expect(await stored()).toBe(5);
    }
  });

  it('retries a chapter whose cache write failed and does not count it as failed', async () => {
    get.mockImplementation(async (p: string) => body(new URL(p, 'http://x').searchParams.get('file') as string));
    putFail = 3; // the story record, then two chapters
    const pr = await run();
    expect(pr.failed).toBe(0);
    expect(await stored()).toBe(5);
  });

  it('retries a request that timed out (AbortError not caused by the job)', async () => {
    let calls = 0;
    get.mockImplementation(async (p: string) => {
      if (++calls === 2) throw new DOMException('timeout', 'AbortError');
      return body(new URL(p, 'http://x').searchParams.get('file') as string);
    });
    const pr = await run();
    expect(pr).toMatchObject({ done: 5, failed: 0 });
    expect(await stored()).toBe(5);
  });

  it('retries a body that could not be read (HTTP 200 + broken JSON)', async () => {
    let calls = 0;
    get.mockImplementation(async (p: string) => {
      if (++calls === 3) throw new Error('HTTP 200');
      return body(new URL(p, 'http://x').searchParams.get('file') as string);
    });
    expect((await run()).failed).toBe(0);
    expect(await stored()).toBe(5);
  });

  it('reports the real reason when a chapter keeps failing, and counts it once', async () => {
    get.mockImplementation(async (p: string) => {
      const f = new URL(p, 'http://x').searchParams.get('file') as string;
      if (f === 'c3.txt') throw new Error('HTTP 500');
      return body(f);
    });
    const pr = await run();
    expect(pr).toMatchObject({ done: 5, total: 5, failed: 1, lastError: 'HTTP 500' });
    expect(await stored()).toBe(4);
  });

  it('does not report a chapter as stored when it cannot be read back', async () => {
    get.mockImplementation(async (p: string) => body(new URL(p, 'http://x').searchParams.get('file') as string));
    dropWrites = true;
    const pr = await run();
    expect(pr.failed).toBe(5);
    expect(pr.lastError).toContain('không đọc lại');
  }, 20_000);

  it('resumes every worker after a pause', async () => {
    get.mockImplementation(async (p: string) => body(new URL(p, 'http://x').searchParams.get('file') as string));
    const job = offline.startJob('s', 'k/story', { chapters, name: 'Story', total: 5 });
    job.pause();
    await new Promise((r) => setTimeout(r, 30));
    job.resume();
    expect(await job.finished).toMatchObject({ done: 5, failed: 0 });
  });
});
