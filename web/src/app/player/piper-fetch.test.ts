import { describe, expect, it, vi } from 'vitest';
import { fetchVerified, sha256Hex, type Artifact } from './piper-fetch';

const enc = (s: string): Uint8Array => new TextEncoder().encode(s);
const GOOD = enc('0123456789');

/** A response that streams `bytes` in two chunks. */
function ok(bytes: Uint8Array): Response {
  const mid = Math.floor(bytes.length / 2);
  return new Response(
    new ReadableStream({
      start(c) {
        c.enqueue(bytes.slice(0, mid));
        c.enqueue(bytes.slice(mid));
        c.close();
      },
    }),
    { status: 200 },
  );
}

async function artifact(sources: string[]): Promise<Artifact> {
  return { name: 'giọng thử', bytes: GOOD.length, sha256: await sha256Hex(new Blob([GOOD as BlobPart])), sources };
}

const text = async (b: Blob): Promise<string> => new TextDecoder().decode(await b.arrayBuffer());

describe('fetchVerified source fallback', () => {
  it('skips a 404 source and a corrupt one, then takes the third', async () => {
    const a = await artifact(['https://hf/x', '/tts/models/x', 'https://gh/x']);
    const bad = enc('9876543210'); // right size, wrong hash
    const fetchImpl = vi.fn(async (url: RequestInfo | URL) => {
      if (String(url) === a.sources[0]) return new Response('nope', { status: 404 });
      if (String(url) === a.sources[1]) return ok(bad);
      return ok(GOOD);
    });
    const seen: number[] = [];
    const progress: number[] = [];
    const r = await fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch, onSource: (i) => seen.push(i), onProgress: (p) => progress.push(p) });
    expect(r.index).toBe(2);
    expect(r.source).toBe('https://gh/x');
    expect(await text(r.blob)).toBe('0123456789');
    expect(seen).toEqual([0, 1, 2]);
    expect(fetchImpl).toHaveBeenCalledTimes(3);
    // progress restarts from 0 for every source and ends at 1
    expect(progress.filter((p) => p === 0).length).toBe(3);
    expect(progress.at(-1)).toBe(1);
  });

  it('falls back on a network error and on a short or oversized body', async () => {
    const a = await artifact(['a', 'b', 'c', 'd']);
    const fetchImpl = vi.fn(async (url: RequestInfo | URL) => {
      if (url === 'a') throw new TypeError('Failed to fetch');
      if (url === 'b') return ok(enc('0123'));
      if (url === 'c') return ok(enc('0123456789ABCDEF'));
      return ok(GOOD);
    });
    const r = await fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch });
    expect(r.index).toBe(3);
  });

  it('stops at the first good source and never touches the rest', async () => {
    const a = await artifact(['a', 'b']);
    const fetchImpl = vi.fn(async () => ok(GOOD));
    const r = await fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch });
    expect(r.index).toBe(0);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it('rejects with every reason, and no blob, when all sources are bad', async () => {
    const a = await artifact(['https://hf.example/x', 'https://mirror.example/x']);
    const fetchImpl = vi.fn(async (url: RequestInfo | URL) => (String(url).includes('hf') ? new Response('', { status: 503 }) : ok(enc('9876543210'))));
    await expect(fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch })).rejects.toThrow(/2 nguồn.*hf\.example.*503.*mirror\.example.*SHA-256/);
  });

  it('does not try other sources when the user cancels', async () => {
    const a = await artifact(['a', 'b']);
    const ac = new AbortController();
    const fetchImpl = vi.fn(async () => {
      ac.abort();
      throw new DOMException('Aborted', 'AbortError');
    });
    await expect(fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch, signal: ac.signal })).rejects.toThrow();
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });
});

describe('fetchVerified resume', () => {
  /** Streams `head` then errors, like a dropped connection. */
  const cut = (head: Uint8Array): Response =>
    new Response(
      new ReadableStream({
        start(c) {
          c.enqueue(head);
        },
        pull(c) {
          c.error(new TypeError('network error'));
        },
      }),
      { status: 200 },
    );
  const partial = (bytes: Uint8Array, from: number): Response =>
    new Response(bytes.slice(from) as BlobPart, { status: 206, headers: { 'Content-Range': `bytes ${from}-${bytes.length - 1}/${bytes.length}` } });
  const rangeOf = (init?: RequestInit): string | undefined => (init?.headers as Record<string, string> | undefined)?.Range;

  it('resumes a cut download on the same source with a Range request', async () => {
    const a = await artifact(['a', 'b']);
    const ranges: (string | undefined)[] = [];
    const fetchImpl = vi.fn(async (_u: RequestInfo | URL, init?: RequestInit) => {
      ranges.push(rangeOf(init));
      return ranges.length === 1 ? cut(GOOD.slice(0, 4)) : partial(GOOD, 4);
    });
    const progress: number[] = [];
    const r = await fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch, onProgress: (p) => progress.push(p) });
    expect(await text(r.blob)).toBe('0123456789');
    expect(r.index).toBe(0);
    expect(ranges).toEqual([undefined, 'bytes=4-']);
    expect(progress).toContain(0.4);
    expect(progress.at(-1)).toBe(1);
  });

  it('carries the partial bytes over to the next source', async () => {
    const a = await artifact(['a', 'b']);
    const fetchImpl = vi.fn(async (u: RequestInfo | URL, init?: RequestInit) => {
      if (u === 'a') return rangeOf(init) ? new Response('', { status: 503 }) : cut(GOOD.slice(0, 6));
      return partial(GOOD, 6);
    });
    const r = await fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch });
    expect(r.index).toBe(1);
    expect(await text(r.blob)).toBe('0123456789');
    expect(fetchImpl).toHaveBeenCalledTimes(3);
  });

  it('restarts from zero when the server answers 200 to a Range request', async () => {
    const a = await artifact(['a']);
    let n = 0;
    const fetchImpl = vi.fn(async () => (++n === 1 ? cut(GOOD.slice(0, 3)) : ok(GOOD)));
    const r = await fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch });
    expect(await text(r.blob)).toBe('0123456789');
    expect(n).toBe(2);
  });

  it('restarts when Content-Range does not continue where we stopped', async () => {
    const a = await artifact(['a']);
    let n = 0;
    const fetchImpl = vi.fn(async () => (++n === 1 ? cut(GOOD.slice(0, 3)) : new Response(GOOD as BlobPart, { status: 206, headers: { 'Content-Range': 'bytes 0-9/10' } })));
    const r = await fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch });
    expect(await text(r.blob)).toBe('0123456789');
  });

  it('a hash mismatch after resuming is discarded; the next source starts from byte 0', async () => {
    const a = await artifact(['a', 'b']);
    const bad = enc('0123XXXXXX');
    const ranges: (string | undefined)[] = [];
    const fetchImpl = vi.fn(async (u: RequestInfo | URL, init?: RequestInit) => {
      ranges.push(`${String(u)}:${rangeOf(init) ?? '-'}`);
      if (u === 'a') return rangeOf(init) ? partial(bad, 4) : cut(bad.slice(0, 4));
      return ok(GOOD);
    });
    const r = await fetchVerified(a, { fetchImpl: fetchImpl as unknown as typeof fetch });
    expect(r.index).toBe(1);
    expect(await text(r.blob)).toBe('0123456789');
    expect(ranges).toEqual(['a:-', 'a:bytes=4-', 'b:-']);
  });
});
