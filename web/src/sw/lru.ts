/**
 * Least-recently-used bookkeeping for a Cache Storage bucket. It only tracks keys: a hit bumps a counter in
 * memory, so cached bodies are never rewritten to record a use (bugs.md W3). The state serialises to a small
 * JSON document that the service worker stores next to the caches.
 */

export interface LruSnapshot {
  /** Clock value of the latest use. */
  c: number;
  /** [key, last use] pairs. */
  u: [string, number][];
}

export class Lru {
  readonly max: number;
  private used = new Map<string, number>();
  private clock = 0;
  /** True when the state changed since the last `toJSON()`. */
  dirty = false;

  constructor(max: number, saved?: unknown) {
    this.max = Math.max(1, Math.floor(max));
    const s = saved as Partial<LruSnapshot> | null | undefined;
    if (s && typeof s === 'object' && Array.isArray(s.u)) {
      for (const row of s.u) {
        if (Array.isArray(row) && typeof row[0] === 'string' && typeof row[1] === 'number' && Number.isFinite(row[1])) this.used.set(row[0], row[1]);
      }
      let top = typeof s.c === 'number' && Number.isFinite(s.c) ? s.c : 0;
      for (const n of this.used.values()) if (n > top) top = n;
      this.clock = top;
    }
  }

  get size(): number {
    return this.used.size;
  }

  has(key: string): boolean {
    return this.used.has(key);
  }

  /** Records a use of an existing key. Unknown keys are ignored. */
  touch(key: string): void {
    if (!this.used.has(key)) return;
    this.used.set(key, ++this.clock);
    this.dirty = true;
  }

  /** Adds (or uses) a key and returns the keys that must be evicted to stay within `max`. */
  add(key: string): string[] {
    this.used.set(key, ++this.clock);
    this.dirty = true;
    return this.evict();
  }

  delete(key: string): void {
    if (this.used.delete(key)) this.dirty = true;
  }

  clear(): void {
    if (this.used.size) this.dirty = true;
    this.used.clear();
  }

  /** Keys from the least to the most recently used. */
  keys(): string[] {
    return [...this.used.entries()].sort((a, b) => a[1] - b[1]).map((e) => e[0]);
  }

  /**
   * Aligns the bookkeeping with the keys really present in the cache (in cache order): entries that are gone
   * are dropped, entries the index never saw (written by an older worker) count as older than everything
   * known, in their cache order. Returns the keys to evict.
   */
  sync(present: string[]): string[] {
    const here = new Set(present);
    for (const k of [...this.used.keys()]) {
      if (!here.has(k)) {
        this.used.delete(k);
        this.dirty = true;
      }
    }
    const unknown = present.filter((k) => !this.used.has(k));
    if (unknown.length) {
      let low = 0;
      for (const n of this.used.values()) if (n < low) low = n;
      let stamp = low - unknown.length;
      for (const k of unknown) this.used.set(k, stamp++);
      this.dirty = true;
    }
    return this.evict();
  }

  private evict(): string[] {
    const over = this.used.size - this.max;
    if (over <= 0) return [];
    const out = this.keys().slice(0, over);
    for (const k of out) this.used.delete(k);
    this.dirty = true;
    return out;
  }

  toJSON(): LruSnapshot {
    this.dirty = false;
    return { c: this.clock, u: [...this.used.entries()] };
  }
}
