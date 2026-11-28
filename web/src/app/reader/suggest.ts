/** "Đề cử đọc": other stories of the same source to offer at the end of the last chapter. Pure, so it is unit-tested. */
import type { StorySummary } from '../core/contracts';

export interface SuggestOptions {
  limit?: number;
  /** True when the reader has opened this story already (it is ranked lower than an unread one). */
  seen?(key: string): boolean;
}

const norm = (s: string): string => s.trim().toLowerCase();
const labels = (genres?: string[], tags?: string[]): Set<string> => new Set([...(genres || []), ...(tags || [])].map(norm).filter(Boolean));
const time = (s: StorySummary): number => {
  const t = s.updated ? Date.parse(s.updated) : NaN;
  return Number.isFinite(t) ? t : 0;
};

export function pickSuggestions(list: StorySummary[], current: { key: string; author?: string | null; genres?: string[]; tags?: string[] }, o: SuggestOptions = {}): StorySummary[] {
  const limit = o.limit ?? 6;
  const author = current.author ? norm(current.author) : '';
  const mine = labels(current.genres, current.tags);
  const done = new Set<string>();
  const scored: { s: StorySummary; score: number; i: number }[] = [];
  list.forEach((s, i) => {
    if (!s.key || s.key === current.key || done.has(s.key)) return;
    done.add(s.key);
    let score = 0;
    if (author && s.author && norm(s.author) === author) score += 100;
    for (const l of labels(s.genres, s.tags)) if (mine.has(l)) score += 5;
    if (!o.seen?.(s.key)) score += 2;
    scored.push({ s, score, i });
  });
  scored.sort((a, b) => b.score - a.score || time(b.s) - time(a.s) || a.i - b.i);
  return scored.slice(0, Math.max(0, limit)).map((x) => x.s);
}
