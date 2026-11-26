/**
 * Pure text rules of the player: cleaning text before it is spoken, splitting paragraphs into sentences and
 * grouping sentences into the chunks an engine reads in one go. No DOM, no settings: everything is a parameter,
 * so the rules are unit-tested (text.test.ts).
 */

/** Largest chunk (characters) read in one go (device voices have no pause inside an utterance). */
export const LOCAL_MAX = 220;
/** Largest piece handed to the native (Capacitor) voice in one call. */
export const NATIVE_PIECE = 3500;
/** Spoken at the end of a chapter before the next one starts. */
export const CHAPTER_CUE = 'Hết chương, chuẩn bị qua chương mới.';
export const RATES: readonly number[] = [0.75, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.75, 2];
/** Sleep-timer choices in minutes; -1 = at the end of the chapter. */
export const SLEEP_MINUTES: readonly number[] = [15, 30, 45, 60, 90];

const BAD = /[^\p{L}\p{M}\p{N}\s.,!?…:;"'“”‘’()\-–—]/gu;
const HAS_WORD = /[\p{L}\p{N}]/u;

/** True when the text holds something that can be spoken. */
export const speakable = (text: string): boolean => HAS_WORD.test(text);

/**
 * Text as it is sent to a voice. With `on` (the "ttsClean" setting) symbols are dropped and repeated punctuation
 * collapsed; without it only the outer whitespace goes. Returns '' when nothing speakable is left.
 */
export function clean(text: unknown, on = true): string {
  let t = String(text ?? '');
  if (!on) {
    t = t.replace(/\s+/g, ' ').trim();
    return speakable(t) ? t : '';
  }
  t = t
    .replace(BAD, ' ')
    .replace(/\.{3,}/g, '…')
    .replace(/([!?…,;:])\1+/g, '$1')
    .replace(/([-–—])\1+/g, '$1')
    .replace(/\(\s*\)|“\s*”|"\s*"/g, ' ')
    .replace(/\s+([.,!?…:;])/g, '$1')
    .replace(/\s+/g, ' ')
    .trim();
  return speakable(t) ? t : '';
}

/** A half-open range [s, e) of a paragraph's text. */
export interface Span {
  s: number;
  e: number;
}

const SENT_END = /[.!?…。]+["'”’»)\]]*(?:\s+|$)/gu;
const CLAUSE_END = /[,;:–—]+["'”’»)\]]*\s+/gu;

function cut(text: string, from: number, to: number, re: RegExp): Span[] {
  const out: Span[] = [];
  let at = from;
  re.lastIndex = from;
  for (;;) {
    const m = re.exec(text);
    if (!m || m.index >= to) break;
    const end = Math.min(to, m.index + m[0].length);
    if (end > at) out.push({ s: at, e: end });
    at = end;
    if (m[0].length === 0) re.lastIndex++;
  }
  if (at < to) out.push({ s: at, e: to });
  return out;
}

/**
 * Sentences of a text as contiguous spans that cover it completely (trailing white space belongs to the
 * sentence before it). A full stop inside a number or an abbreviation ("3.5", "v.v...") does not end a sentence
 * because it is not followed by white space.
 */
export function splitSentences(text: string): Span[] {
  if (!text) return [];
  const spans = cut(text, 0, text.length, SENT_END);
  // a span without a letter or digit (a lone quote mark, an ellipsis) joins its neighbour
  const out: Span[] = [];
  for (const sp of spans) {
    const last = out[out.length - 1];
    if (last && (!speakable(text.slice(sp.s, sp.e)) || !speakable(text.slice(last.s, last.e)))) last.e = sp.e;
    else out.push({ ...sp });
  }
  return out;
}

/** Splits one span that is longer than `max` at clause marks, then at spaces, then anywhere. */
function splitLong(text: string, sp: Span, max: number): Span[] {
  if (sp.e - sp.s <= max) return [sp];
  const out: Span[] = [];
  let cur: Span | null = null;
  const flush = (): void => {
    if (cur) out.push(cur);
    cur = null;
  };
  for (const c of cut(text, sp.s, sp.e, CLAUSE_END)) {
    if (c.e - c.s > max) {
      flush();
      let at = c.s;
      while (c.e - at > max) {
        let stop = text.lastIndexOf(' ', at + max);
        if (stop <= at) stop = at + max;
        else stop++;
        out.push({ s: at, e: stop });
        at = stop;
      }
      if (at < c.e) cur = { s: at, e: c.e };
    } else if (cur && c.e - cur.s <= max) cur.e = c.e;
    else {
      flush();
      cur = { ...c };
    }
  }
  flush();
  return out;
}

/** Sentences of a paragraph, none longer than `max` characters (long ones are split at clause marks). */
export function segments(text: string, max: number): Span[] {
  return splitSentences(text).flatMap((sp) => splitLong(text, sp, max));
}

/** One sentence of a chunk: where it is in the paragraph (`s`,`e`) and in the spoken text (`at`,`len`). */
export interface ChunkSent extends Span {
  at: number;
  len: number;
}

/** What an engine reads in one go. `p` is the paragraph index (-1 = the chapter title). */
export interface Chunk {
  p: number;
  text: string;
  sents: ChunkSent[];
}

/** The chapter title as it is spoken: a trailing "[…]" note is dropped, "Chương 6: Tên" becomes "Chương 6. Tên". */
export function titleText(title: string): string {
  return String(title || '')
    .replace(/\s*\[.*?\]\s*$/, '')
    .replace(/^((?:Quyển\s+\d+\s*[-:.–]?\s*)?Chương\s+\d+(?:[.-]\d+)?)\s*[:\-–]\s*/iu, '$1. ')
    .trim();
}

export interface ChunkOptions {
  /** Character limit of one chunk (LOCAL_MAX). */
  max: number;
  /** Read the chapter title first (it becomes the chunk with p = -1). */
  readTitle: boolean;
  /** The "ttsClean" setting. */
  clean: boolean;
}

/** Splits a chapter into chunks. Paragraphs without a letter or digit (scene breaks) are skipped. */
export function buildChunks(ch: { title?: string | null; paragraphs: string[] }, o: ChunkOptions): Chunk[] {
  const out: Chunk[] = [];
  if (o.readTitle && ch.title) {
    const t = clean(titleText(ch.title), o.clean);
    if (t) out.push({ p: -1, text: t, sents: [{ s: 0, e: ch.title.length, at: 0, len: t.length }] });
  }
  ch.paragraphs.forEach((para, p) => {
    if (!speakable(para)) return;
    let cur: Chunk | null = null;
    for (const sp of segments(para, o.max)) {
      const t = clean(para.slice(sp.s, sp.e), o.clean);
      if (!t) {
        // nothing to say: the span still belongs to the sentence before it, so the highlight has no holes
        const last = cur?.sents[cur.sents.length - 1];
        if (last) last.e = sp.e;
        continue;
      }
      if (cur && cur.text.length + 1 + t.length > o.max) {
        out.push(cur);
        cur = null;
      }
      if (!cur) cur = { p, text: t, sents: [{ ...sp, at: 0, len: t.length }] };
      else {
        cur.sents.push({ ...sp, at: cur.text.length + 1, len: t.length });
        cur.text += ' ' + t;
      }
    }
    if (cur) out.push(cur);
  });
  return out;
}

/**
 * Index of the chunk to start at for a wanted paragraph: -1 means "from the top" (the title chunk when there is
 * one), otherwise the first chunk at or after the paragraph. 0 when the chapter has no such chunk.
 */
export function startChunk(chunks: Chunk[], para: number): number {
  if (para < 0) return 0;
  const i = chunks.findIndex((c) => c.p >= para);
  return i < 0 ? Math.max(0, chunks.length - 1) : i;
}

/** Index of the sentence of a chunk that holds the spoken-text offset. */
export function sentAt(chunk: Chunk, offset: number): number {
  let k = 0;
  for (let i = 0; i < chunk.sents.length; i++) if (offset >= (chunk.sents[i] as ChunkSent).at) k = i;
  return k;
}

/**
 * Spoken-text offset reached after `time` seconds of an audio clip of the chunk. Uses the clip length when the
 * browser knows it, otherwise a typical speed of a Vietnamese voice (15 characters per second).
 */
export function offsetAtTime(chunk: Chunk, time: number, duration: number): number {
  const len = chunk.text.length;
  if (!(time > 0) || !len) return 0;
  const d = Number.isFinite(duration) && duration > 0 ? duration : len / 15;
  return Math.min(len - 1, Math.floor((time / d) * len));
}

/** Splits text into pieces of at most `max` characters at punctuation; each piece keeps its offset. */
export function pieces(text: string, max: number): { text: string; at: number }[] {
  if (text.length <= max) return text.trim() ? [{ text, at: 0 }] : [];
  return splitLong(text, { s: 0, e: text.length }, max)
    .map((sp) => ({ text: text.slice(sp.s, sp.e), at: sp.s }))
    .filter((x) => x.text.trim());
}

/** Remaining sleep time as shown on the dock: "29 phút", "45 giây". */
export function sleepLabel(msLeft: number): string {
  if (msLeft <= 0) return '';
  return msLeft >= 60_000 ? `${Math.ceil(msLeft / 60_000)} phút` : `${Math.ceil(msLeft / 1000)} giây`;
}
