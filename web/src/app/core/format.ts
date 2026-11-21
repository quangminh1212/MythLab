/** Shared formatting helpers. One chapter-label formatter for lists, headers, drawers, player and MediaSession. */

/** Diacritics-insensitive form (unchanged from the old app): NFD, strip combining marks, đ→d, lower-case. */
export function normTxt(s: unknown): string {
  return String(s || '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[đĐ]/g, 'd')
    .toLowerCase();
}

/**
 * Search key, identical to the server index: normTxt, then every run of characters that are not Unicode letters or
 * digits becomes one space, trimmed. Compare with {@link matchTokens}.
 */
export function normKey(s: unknown): string {
  return normTxt(s)
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
}

/** Tokens of a query (normKey, non-empty). */
export const tokens = (q: string): string[] => normKey(q).split(' ').filter(Boolean);

/**
 * True when every query token is a substring of the key or of the key without spaces (`hay` must be a normKey
 * result), so "co tich" matches "CoTich".
 */
export function matchTokens(hay: string, toks: string[]): boolean {
  if (!toks.length) return true;
  const compact = hay.replace(/ /g, '');
  return toks.every((t) => hay.includes(t) || compact.includes(t));
}

/** Search rule of the shared fixture: does query `q` match the raw field? */
export const searchMatch = (q: string, field: string): boolean => matchTokens(normKey(field), tokens(q));

const nf = new Intl.NumberFormat('vi-VN');
export const fmtNum = (n: number | null | undefined): string => (n == null || !Number.isFinite(Number(n)) ? '' : nf.format(Number(n)));

/** Upper-cases the first letter of a stored title that starts lower-case ("bóc hoàng bảng" → "Bóc hoàng bảng"). */
function tidyTitle(t: string): string {
  const s = t.trim();
  if (!s) return '';
  const first = s.charAt(0);
  const up = first.toLocaleUpperCase('vi');
  return first !== up ? up + s.slice(1) : s;
}

/** What the chapter formatters need: ChapterRef, Progress and Bookmark entries all fit. */
export interface ChapterLike {
  n: number;
  title?: string | null;
  sub?: number;
  vol?: number;
}

/** "Chương 6", "Chương 12.5", "Quyển 2 - Chương 1": the number part of a chapter label. */
export function chapterNumber(ch: ChapterLike): string {
  const head = `Chương ${ch.n}${ch.sub ? '.' + ch.sub : ''}`;
  return ch.vol ? `Quyển ${ch.vol} - ${head}` : head;
}

/**
 * The one chapter formatter: "Chương 6: Tĩnh Tâm Uyển" (or "Chương 6" without a title). A "Chương 6" prefix
 * repeated inside the stored title is dropped.
 */
export function chapterLabel(ch: ChapterLike | null | undefined): string {
  if (!ch) return '';
  const head = chapterNumber(ch);
  let t = String(ch.title ?? '').trim();
  const dup = /^(?:quyển\s+\d+\s*[-:.–]?\s*)?chương\s+(\d+)(?:[.-]\d+)?\s*[-:.–]?\s*/iu.exec(t);
  if (dup && Number(dup[1]) === ch.n) t = t.slice(dup[0].length);
  t = tidyTitle(t);
  return t ? `${head}: ${t}` : head;
}

/** Only the title part of a chapter ("Tĩnh Tâm Uyển"), '' when there is none. */
export function chapterTitle(ch: ChapterLike): string {
  const l = chapterLabel(ch);
  const i = l.indexOf(': ');
  return i < 0 ? '' : l.slice(i + 2);
}

/** Repository name for display: "Done_CoTich" → "Co Tich". */
export function repoLabel(repo: string, prefix = 'Done_'): string {
  const s = repo.startsWith(prefix) ? repo.slice(prefix.length) : repo;
  return s.replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/_/g, ' ').trim() || repo;
}

const rtf = typeof Intl !== 'undefined' && 'RelativeTimeFormat' in Intl ? new Intl.RelativeTimeFormat('vi', { numeric: 'auto' }) : null;
/** "5 phút trước", "hôm qua", or a short date for anything older than a month. */
export function timeAgo(ts: number, now = Date.now()): string {
  const s = Math.round((ts - now) / 1000);
  const a = Math.abs(s);
  if (!rtf || !Number.isFinite(s)) return '';
  if (a < 45) return 'vừa xong';
  if (a < 3600) return rtf.format(Math.round(s / 60), 'minute');
  if (a < 86400) return rtf.format(Math.round(s / 3600), 'hour');
  if (a < 30 * 86400) return rtf.format(Math.round(s / 86400), 'day');
  return fmtDate(ts);
}

export function fmtDate(v: string | number | null | undefined): string {
  if (v == null || v === '') return '';
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

export function fmtBytes(n: number): string {
  if (!Number.isFinite(n) || n <= 0) return '0 MB';
  if (n < 1024 * 1024) return `${Math.max(1, Math.round(n / 1024))} KB`;
  if (n < 1024 ** 3) return `${(n / 1024 ** 2).toFixed(1).replace('.', ',')} MB`;
  return `${(n / 1024 ** 3).toFixed(2).replace('.', ',')} GB`;
}

/** Stable hue (0-359) from a string; drives generated covers and placeholder tints. */
export function hashHue(s: unknown): number {
  let h = 0;
  for (const c of String(s ?? '')) h = (h * 31 + (c.codePointAt(0) as number)) >>> 0;
  return h % 360;
}

/** Progress map key: "<source>|<key>". */
export const sKey = (source: string, key: string): string => `${source}|${key}`;

/** Vietnamese collation for client-side sorting. */
export const viCompare: (a: string, b: string) => number = new Intl.Collator('vi', { numeric: true, sensitivity: 'base' }).compare;

/** Turns any thrown value into a message that is safe to show. */
export function errMsg(e: unknown): string {
  if (e instanceof Error) return e.message;
  return typeof e === 'string' ? e : 'Lỗi không xác định';
}
