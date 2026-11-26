/**
 * Verified download with fallback sources. A file is described by its exact size and SHA-256 and an ordered list of
 * URLs that all serve the same bytes (pinned Hugging Face, a GitHub release). Sources are tried in
 * order; a network error, an HTTP error, a wrong size or a wrong hash moves on to the next one. Nothing is returned
 * (so nothing can be cached) unless a source delivered exactly the expected bytes.
 */

export interface Artifact {
  /** For messages only. */
  name: string;
  /** Exact byte length. */
  bytes: number;
  /** Lower-case hex SHA-256; checked when the browser has crypto.subtle (secure contexts). */
  sha256: string;
  /** Tried in this order. */
  sources: readonly string[];
}

export interface FetchOptions {
  /** 0..1 of the whole file; a resumed download continues from what it already has, a restart goes back to 0. */
  onProgress?: (done: number) => void;
  /** Called when a source starts (index 0-based), so the UI can say "nguồn dự phòng 2/3". */
  onSource?: (index: number, total: number, url: string) => void;
  signal?: AbortSignal;
  /** Test seam. */
  fetchImpl?: typeof fetch;
}

const hex = (h: ArrayBuffer): string => Array.from(new Uint8Array(h), (b) => b.toString(16).padStart(2, '0')).join('');

export async function sha256Hex(blob: Blob): Promise<string> {
  return hex(await crypto.subtle.digest('SHA-256', await blob.arrayBuffer()));
}

const hostOf = (url: string): string => {
  try {
    return new URL(url).host;
  } catch {
    return url;
  }
};

/** Bytes already received for the file; survives a cut connection so the next try (same or next source) can resume. */
interface Held {
  parts: Uint8Array[];
  got: number;
}

const reset = (p: Held): void => {
  p.parts = [];
  p.got = 0;
};

/**
 * One attempt on one source. Asks for the missing tail with a Range request when `p` already holds bytes; a server that
 * answers 200 (no Range support) or a Content-Range that does not start where we stopped means a clean restart.
 * On a cut the bytes received so far stay in `p`. Throws a short Vietnamese reason on any failure.
 */
async function attempt(a: Artifact, url: string, o: FetchOptions, p: Held): Promise<Blob> {
  const f = o.fetchImpl ?? fetch;
  const resuming = p.got > 0;
  const res = await f(url, resuming ? { signal: o.signal, headers: { Range: `bytes=${p.got}-` } } : { signal: o.signal });
  if (resuming) {
    if (res.status === 206) {
      // Content-Range may be hidden from cross-origin scripts; when visible it must continue exactly where we stopped.
      const m = /^bytes (\d+)-/.exec(res.headers.get('Content-Range') ?? '');
      if (m && Number(m[1]) !== p.got) {
        reset(p);
        o.onProgress?.(0);
      }
    } else if (res.ok || res.status === 416) {
      reset(p); // 200 (Range ignored) or 416: start this source from byte 0
      o.onProgress?.(0);
    } // other errors keep the bytes for the next source
  }
  if (!res.ok) throw new Error(`máy chủ trả lỗi ${res.status}`);
  const parts = p.parts;
  if (res.body) {
    const reader = res.body.getReader();
    for (;;) {
      let r: ReadableStreamReadResult<Uint8Array>;
      try {
        r = await reader.read();
      } catch (e) {
        if ((e as Error)?.name !== 'AbortError') (e as { cut?: boolean }).cut = true;
        throw e;
      }
      const { done, value } = r;
      if (done) break;
      parts.push(value);
      p.got += value.length;
      if (p.got > a.bytes) {
        void reader.cancel().catch(() => {});
        reset(p);
        throw new Error('tệp lớn hơn dự kiến');
      }
      o.onProgress?.(Math.min(1, p.got / a.bytes));
    }
  } else {
    const buf = new Uint8Array(await res.arrayBuffer());
    parts.push(buf);
    p.got += buf.length;
    if (p.got > a.bytes) {
      reset(p);
      throw new Error('tệp lớn hơn dự kiến');
    }
    o.onProgress?.(Math.min(1, p.got / a.bytes));
  }
  if (p.got !== a.bytes) throw new Error('tệp tải về bị thiếu'); // kept: the next try resumes from here
  const blob = new Blob(parts as BlobPart[]);
  if (globalThis.crypto?.subtle && a.sha256 && (await sha256Hex(blob)) !== a.sha256) {
    reset(p); // never resume on top of bad bytes
    throw new Error('tệp tải về không đúng (sai mã SHA-256)');
  }
  return blob;
}

/** Downloads `a` from the first source that delivers the right bytes. Rejects with every reason when all fail. */
export async function fetchVerified(a: Artifact, o: FetchOptions = {}): Promise<{ blob: Blob; source: string; index: number }> {
  const reasons: string[] = [];
  const have: Held = { parts: [], got: 0 };
  for (let i = 0; i < a.sources.length; i++) {
    const url = a.sources[i] as string;
    if (o.signal?.aborted) throw o.signal.reason ?? new DOMException('Aborted', 'AbortError');
    o.onSource?.(i, a.sources.length, url);
    o.onProgress?.(have.got / a.bytes);
    // A connection cut mid-stream that still delivered new bytes gets one immediate resume on the same source before falling through.
    for (let retry = 0; ; retry++) {
      const before = have.got;
      try {
        return { blob: await attempt(a, url, o, have), source: url, index: i };
      } catch (e) {
        if (o.signal?.aborted || (e as Error)?.name === 'AbortError') throw e;
        if (retry === 0 && (e as { cut?: boolean })?.cut && have.got > before) continue;
        reasons.push(`${hostOf(url)}: ${(e as Error).message || e}`);
        break;
      }
    }
  }
  throw new Error(`Không tải được ${a.name} từ ${a.sources.length} nguồn (${reasons.join('; ')})`);
}
