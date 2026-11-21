/**
 * Text rules shared with the Go server (`server/internal/library`). Both sides are tested against
 * server/internal/library/testdata/textutil_cases.json (its `_doc` is the specification), so the GitHub-direct
 * backend yields the same chapter list, titles and paragraphs as the server.
 */
import { normKey } from './format';

// Python's str.isspace() class, which differs from JS \s (\x1c-\x1f and \x85 are spaces, U+FEFF is not).
const WS = '\\t-\\r\\x1c-\\x20\\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000';
const D = '(\\p{Nd}{1,15})(?!\\p{Nd})';
const CHAPTER_RE = new RegExp(
  `^(?:(?:Quyển|Quyen|Tập|Tap)[${WS}]+${D}[${WS}]*[-:.,\\u2013]?[${WS}]*)?` +
    `(?:Chương|Chuong)[${WS}]+${D}(?:[.\\-](\\p{Nd}{1,15})(?=[${WS}]|$))?[${WS}]*[-:.\\u2013]?[${WS}]*([\\s\\S]*)$`,
  'iu',
);
const RULE = new RegExp(`^[${WS}]*[=\\-_*]{5,}[${WS}]*$`, 'u');
const CHAP_HEAD = new RegExp(`^(?:Chương|Chuong)[${WS}]+(\\p{Nd}+)`, 'iu');
const WS_RUN = new RegExp(`[${WS}]+`, 'u');
const ND = /\p{Nd}/u;

/** Scene-break paragraph produced for a rule line inside the text. */
export const SCENE_BREAK = '***';

const escCls = (s: string): string => s.replace(/[\\\]\-^]/g, '\\$&');

/** Python `str.strip([chars])`. */
export function pyStrip(s: string, chars?: string | null): string {
  const cls = chars == null ? WS : escCls(chars);
  return s.replace(new RegExp(`^[${cls}]+|[${cls}]+$`, 'gu'), '');
}

/** Value of a run of Unicode decimal digits, digit by digit (so full-width digits work). */
function digitsValue(s: string): number {
  let v = 0;
  for (const ch of s) {
    const cp = ch.codePointAt(0) as number;
    let d: number;
    if (cp >= 48 && cp <= 57) d = cp - 48;
    else {
      // decimal digits come in contiguous runs of ten: distance from the start of the run, modulo 10
      let start = cp;
      while (start > 0 && cp - start < 60 && ND.test(String.fromCodePoint(start - 1))) start--;
      d = (cp - start) % 10;
    }
    v = v * 10 + d;
  }
  return v;
}

const pyLen = (s: string): number => [...s].length;
const isDict = (v: unknown): v is Record<string, unknown> => v != null && typeof v === 'object' && !Array.isArray(v);
const get = (o: Record<string, unknown>, k: string): unknown => (Object.prototype.hasOwnProperty.call(o, k) ? o[k] : undefined);

export function naturalTitle(raw: string): string {
  return pyStrip(pyStrip(pyStrip(raw), '-:. '));
}

export interface ChapterName {
  n: number;
  title: string;
  /** Sub-number ("Chương 12.5" → 5); 0 when absent. */
  sub: number;
  /** Volume ("Quyển 2 Chương 1" → 2); 0 when absent. */
  vol: number;
}

/** "Chương 001 - Đất Rộng Lên.txt" → {n: 1, title: "Đất Rộng Lên", sub: 0, vol: 0}; null when not a chapter file. */
export function parseChapterName(filename: string): ChapterName | null {
  const name = String(filename).normalize('NFC');
  if (!/\.txt$/i.test(name)) return null;
  const m = CHAPTER_RE.exec(name.slice(0, -4));
  if (!m) return null;
  return {
    n: digitsValue(m[2] as string),
    title: naturalTitle(m[4] ?? ''),
    sub: m[3] ? digitsValue(m[3]) : 0,
    vol: m[1] ? digitsValue(m[1]) : 0,
  };
}

export interface ChapterEntry {
  n: number;
  title: string;
  file: string;
  sub?: number;
  vol?: number;
}

const cmpCp = (a: string, b: string): number => {
  // code point order (JS `<` compares UTF-16 units, which differs for astral characters)
  const x = [...a];
  const y = [...b];
  for (let i = 0; i < x.length && i < y.length; i++) {
    const d = (x[i] as string).codePointAt(0)! - (y[i] as string).codePointAt(0)!;
    if (d) return d;
  }
  return x.length - y.length;
};

/** Chapter list of a story folder: parsed, sorted by (vol, n, sub, file) and de-duplicated. */
export function chapterList(files: string[]): ChapterEntry[] {
  const rows: { p: ChapterName; file: string }[] = [];
  for (const file of files) {
    const p = parseChapterName(file);
    if (p) rows.push({ p, file });
  }
  rows.sort((a, b) => a.p.vol - b.p.vol || a.p.n - b.p.n || a.p.sub - b.p.sub || cmpCp(a.file, b.file));
  const out: ChapterEntry[] = [];
  const seen = new Set<string>();
  for (const { p, file } of rows) {
    const k = `${p.vol}|${p.n}|${p.sub}|${normKey(p.title).replace(/ /g, '')}`;
    if (seen.has(k)) continue;
    seen.add(k);
    const e: ChapterEntry = { n: p.n, title: p.title, file };
    if (p.sub) e.sub = p.sub;
    if (p.vol) e.vol = p.vol;
    out.push(e);
  }
  return out;
}

export interface CleanChapter {
  title: string | null;
  paragraphs: string[];
}

/** Splits raw chapter text into title and paragraphs exactly like the server. `n` is the chapter number when known. */
export function cleanChapterText(textIn: string, n?: number): CleanChapter {
  const text = textIn.replace(/\r\n/g, '\n').replace(/\r/g, '\n').replace(/^﻿+/, '');
  let lines = text.split('\n');
  let title: string | null = null;
  const head: number[] = [];
  lines.slice(0, 8).forEach((ln, i) => {
    if (RULE.test(ln)) head.push(i);
  });
  const h0 = head[0];
  const h1 = head[1];
  if (h0 !== undefined && h1 !== undefined && h1 - h0 <= 4 && lines.slice(0, h0).every((ln) => pyStrip(ln) === '')) {
    const inner = lines
      .slice(h0 + 1, h1)
      .map((ln) => pyStrip(ln))
      .filter(Boolean);
    if (inner.length) title = inner.join(' ');
    lines = lines.slice(h1 + 1);
  }
  let paras: string[] = [];
  for (const ln of lines) {
    const p = pyStrip(ln.replace(/[ \t]+/g, ' '));
    if (!p) continue;
    paras.push(RULE.test(p) ? SCENE_BREAK : p);
  }
  // a lone rule above the heading is decoration (same rule as the Go server: library.CleanChapterText)
  while (paras[0] === SCENE_BREAK) paras.shift();
  const first = paras[0];
  if (title == null && first !== undefined && pyLen(first) < 160) {
    const m = CHAP_HEAD.exec(first);
    if (m && (n === undefined || ((m[1] as string).length <= 15 && digitsValue(m[1] as string) === n))) title = paras.shift() as string;
  }
  paras = paras.filter((p, i) => !(p === SCENE_BREAK && paras[i - 1] === SCENE_BREAK));
  while (paras[0] === SCENE_BREAK) paras.shift();
  while (paras[paras.length - 1] === SCENE_BREAK) paras.pop();
  return { title, paragraphs: paras };
}

export const countWords = (paras: string[]): number =>
  paras.reduce((n, p) => (p === SCENE_BREAK ? n : n + p.split(WS_RUN).filter(Boolean).length), 0);

export interface InfoSummary {
  name: string;
  author: string | null;
  synopsis: string;
  poster: string | null;
  genres: string[];
  tags: string[];
  status: string | null;
  declared_chapters: number | null;
  link: string | null;
}

const text = (v: unknown): string | null => {
  if (typeof v === 'string') return v !== '' ? v : null;
  if (typeof v === 'number' && Number.isInteger(v)) return String(v);
  return null;
};

/** Summary of a story's info.json, field for field what `/api/stories` returns. */
export function infoSummary(infoIn: unknown, fallbackName: string): InfoSummary {
  const info = isDict(infoIn) ? infoIn : {};
  let poster = get(info, 'poster');
  if (isDict(poster)) {
    const vals = Object.values(poster);
    poster = get(poster, '600') || get(poster, 'default') || (vals.length ? vals[0] : null);
  }
  const names = (arr: unknown): string[] => {
    const out: string[] = [];
    if (Array.isArray(arr))
      for (const x of arr) {
        const nm = isDict(x) ? get(x, 'name') : null;
        if (typeof nm === 'string' && nm) out.push(nm);
      }
    return out;
  };
  const author = get(info, 'author');
  const cc = get(info, 'chapter_count');
  let declared: number | null = null;
  if (typeof cc === 'number' && Number.isInteger(cc)) declared = cc;
  else if (typeof cc === 'string' && /^\d{1,15}$/.test(cc)) declared = parseInt(cc, 10);
  return {
    name: text(get(info, 'name')) || fallbackName,
    author: text(isDict(author) ? get(author, 'name') : author),
    synopsis: text(get(info, 'synopsis')) || text(get(info, 'description')) || '',
    poster: typeof poster === 'string' && poster ? poster : null,
    genres: names(get(info, 'genres')),
    tags: names(get(info, 'tags')),
    status: text(get(info, 'status_name')) || text(get(info, 'state')),
    declared_chapters: declared,
    link: text(get(info, 'link')),
  };
}

const IMG_RE = /\.(jpe?g|png|webp|gif|avif)$/i;
/** True for file names the cover picker considers. */
export const isImageName = (name: string): boolean => IMG_RE.test(name);

/** Cover file of a story folder: cover.* > poster.* > folder.* > thumb.* > first image by code point; null if none. */
export function pickCover(names: string[]): string | null {
  const imgs = names.filter(isImageName).sort(cmpCp);
  for (const want of ['cover', 'poster', 'folder', 'thumb']) {
    const hit = imgs.find((f) => f.replace(IMG_RE, '').toLowerCase() === want);
    if (hit) return hit;
  }
  return imgs[0] ?? null;
}

export interface ChapterJson {
  title: string | null;
  paragraphs: string[];
  words: number;
}

/** Display title built from a parsed file name: "Quyển 2 - Chương 12.5: Tên". */
export function chapterNameTitle(p: ChapterName): string {
  return (p.vol ? `Quyển ${p.vol} - ` : '') + `Chương ${p.n}` + (p.sub ? `.${p.sub}` : '') + (p.title ? `: ${p.title}` : '');
}

/** Same JSON as the `/api/chapter` route. */
export function chapterJson(rawText: string, file: string): ChapterJson {
  const p = parseChapterName(file);
  const c = cleanChapterText(rawText, p ? p.n : undefined);
  let title = c.title;
  if (!title && p) title = chapterNameTitle(p);
  return { title, paragraphs: c.paragraphs, words: countWords(c.paragraphs) };
}
