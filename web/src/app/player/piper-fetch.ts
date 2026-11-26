/**
 * Verified download with fallback sources. A file is described by its exact size and SHA-256 and an ordered list of
 * URLs that all serve the same bytes (pinned Hugging Face, our own mirror, a GitHub release). Sources are tried in
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
  /** 0..1 of the CURRENT source; goes back to 0 when the next source starts. */
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

/** One attempt on one source. Throws a short Vietnamese reason on any failure. */
async function attempt(a: Artifact, url: string, o: FetchOptions): Promise<Blob> {
  const f = o.fetchImpl ?? fetch;
  const res = await f(url, { signal: o.signal });
  if (!res.ok) throw new Error(`máy chủ trả lỗi ${res.status}`);
  const parts: Uint8Array[] = [];
  let got = 0;
  if (res.body) {
    const reader = res.body.getReader();
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      parts.push(value);
      got += value.length;
      if (got > a.bytes) {
        void reader.cancel().catch(() => {});
        throw new Error('tệp lớn hơn dự kiến');
      }
      o.onProgress?.(Math.min(1, got / a.bytes));
    }
  } else {
    const buf = new Uint8Array(await res.arrayBuffer());
    parts.push(buf);
    got = buf.length;
    o.onProgress?.(Math.min(1, got / a.bytes));
  }
  if (got !== a.bytes) throw new Error('tệp tải về bị thiếu');
  const blob = new Blob(parts as BlobPart[]);
  parts.length = 0;
  if (globalThis.crypto?.subtle && a.sha256 && (await sha256Hex(blob)) !== a.sha256) throw new Error('tệp tải về không đúng (sai mã SHA-256)');
  return blob;
}

/** Downloads `a` from the first source that delivers the right bytes. Rejects with every reason when all fail. */
export async function fetchVerified(a: Artifact, o: FetchOptions = {}): Promise<{ blob: Blob; source: string; index: number }> {
  const reasons: string[] = [];
  for (let i = 0; i < a.sources.length; i++) {
    const url = a.sources[i] as string;
    if (o.signal?.aborted) throw o.signal.reason ?? new DOMException('Aborted', 'AbortError');
    o.onSource?.(i, a.sources.length, url);
    o.onProgress?.(0);
    try {
      return { blob: await attempt(a, url, o), source: url, index: i };
    } catch (e) {
      if (o.signal?.aborted || (e as Error)?.name === 'AbortError') throw e;
      reasons.push(`${hostOf(url)}: ${(e as Error).message || e}`);
    }
  }
  throw new Error(`Không tải được ${a.name} từ ${a.sources.length} nguồn (${reasons.join('; ')})`);
}
