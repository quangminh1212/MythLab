/**
 * Number / symbol reading rules shared by every voice (device, Piper, Kokoro). Wraps the vendored strict Kokoro
 * normaliser, which throws on ambiguous input, so a failure leaves the text as it was.
 */
import { normalizeVietnameseSpeech } from './kokoro/normalize-text';

const FJWZ = /\b[a-z]*[fjwz][a-z]*\b/giu;

/**
 * Digits, percent, times, dates and arithmetic signs as Vietnamese words ("5%" -> "năm phần trăm"). Words with
 * f/j/w/z (web, wifi) are kept: the vendored rules would spell them letter by letter. Returns the input unchanged
 * when the rules reject the text (ambiguous codes, "1.000", very long text).
 */
export function safeSpeechNormalize(text: string): string {
  if (!text || !/[\d%&+=×÷°−]/u.test(text)) return text;
  try {
    const kept: string[] = [];
    const guarded = text.replace(FJWZ, (w) => {
      kept.push(w);
      return String.fromCharCode(0xe000 + kept.length - 1);
    });
    const out = normalizeVietnameseSpeech(guarded).replace(/[-]/gu, (m) => kept[m.charCodeAt(0) - 0xe000] ?? m);
    return out || text;
  } catch {
    return text;
  }
}
