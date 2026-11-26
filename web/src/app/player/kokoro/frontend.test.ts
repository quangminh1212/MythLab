import { describe, expect, it } from 'vitest';
import { normalizeKokoroText, phonemizeChunks, SeaDictionary } from './frontend';

/** A tiny dictionary in the SEAP v2 layout: header, strings, string offsets, rare words (key, value), common words (key, vi, en). */
function seap(rare: Record<string, string>, common: Record<string, [string, string]> = {}): Uint8Array<ArrayBuffer> {
  const strings = [...new Set([...Object.keys(rare), ...Object.values(rare), ...Object.keys(common), ...Object.values(common).flat()])];
  const id = new Map(strings.map((s, i) => [s, i]));
  const enc = new TextEncoder();
  const data: number[] = [];
  const offsets = strings.map((s) => {
    const at = data.length;
    data.push(...enc.encode(s), 0);
    return at;
  });
  const rows = (o: Record<string, string[] | string>, n: number): number[][] =>
    Object.keys(o)
      .sort()
      .map((k) => [id.get(k) as number, ...[o[k]].flat().map((v) => id.get(v as string) as number)].slice(0, n));
  const rareRows = rows(rare, 2);
  const commonRows = rows(common, 3);
  const offsetAt = 48 + data.length;
  const rareAt = offsetAt + offsets.length * 4;
  const commonAt = rareAt + rareRows.length * 8;
  const out = new Uint8Array(commonAt + commonRows.length * 12);
  const view = new DataView(out.buffer);
  out.set(enc.encode('SEAP'), 0);
  [2, strings.length, rareRows.length, commonRows.length, offsetAt, rareAt, commonAt].forEach((v, i) => view.setUint32(4 + i * 4, v, true));
  out.set(data, 48);
  offsets.forEach((o, i) => view.setUint32(offsetAt + i * 4, o, true));
  rareRows.forEach((r, i) => r.forEach((v, j) => view.setUint32(rareAt + i * 8 + j * 4, v, true)));
  commonRows.forEach((r, i) => r.forEach((v, j) => view.setUint32(commonAt + i * 12 + j * 4, v, true)));
  return out;
}

const dict = new SeaDictionary(seap({ xin: 'sin1', chào: 'tʃaw2', là: 'la2' }, { ok: ['ok', '<en>oʊkˈeɪ'] }));
/** One id per character the readings can contain (ids start at 1; 0 is the pad). */
const vocab = Object.fromEntries(Array.from('sin→↘ʧawla ,.!?-<>eɪʊkˈoʔ↗↓', (c, i) => [c, i + 1]));

describe('SeaDictionary', () => {
  it('finds words in either table, case-insensitively, and returns null for unknown words', () => {
    expect(dict.lookup('xin')).toBe('sin1');
    expect(dict.lookup('XIN')).toBe('sin1');
    expect(dict.lookup('chào')).toBe('tʃaw2');
    expect(dict.lookup('ok')).toBe('ok');
    expect(dict.lookup('ok', true)).toBe('<en>oʊkˈeɪ');
    expect(dict.lookup('nope')).toBeNull();
  });

  it('refuses a file that is not a SEAP v2 dictionary or whose index runs past its end', () => {
    expect(() => new SeaDictionary(new Uint8Array(100))).toThrow(/SEAP/);
    const bad = seap({ a: 'b' });
    new DataView(bad.buffer).setUint32(24, 1e6, true);
    expect(() => new SeaDictionary(bad)).toThrow(/bounds/);
  });
});

describe('normalizeKokoroText', () => {
  it('writes numbers as Vietnamese words and rejects empty or oversized text', () => {
    expect(normalizeKokoroText('Có 5 người')).toMatch(/năm/);
    expect(() => normalizeKokoroText('   ')).toThrow();
    expect(() => normalizeKokoroText('a'.repeat(2001))).toThrow();
  });
});

describe('phonemizeChunks', () => {
  it('turns a line into one chunk of pad-wrapped token ids from the vocabulary', () => {
    const r = phonemizeChunks('Xin chào, là.', dict, vocab);
    expect(r.chunks).toHaveLength(1);
    const c = r.chunks[0]!;
    expect(c.phonemes).toBe('sin→ ʧaw↘ , la↘ .');
    expect(c.tokens[0]).toBe(0);
    expect(c.tokens.at(-1)).toBe(0);
    expect(c.tokens).toHaveLength(Array.from(c.phonemes).length + 2);
    expect(c.tokens.slice(1, 4)).toEqual([vocab['s'], vocab['i'], vocab['n']]);
    expect(r.warnings).toEqual([]);
  });

  it('spells words the dictionary lacks and reports them, instead of failing the line', () => {
    const r = phonemizeChunks('xin kko', dict, { ...vocab, ...Object.fromEntries(Array.from('ɛkoʊ', (c, i) => [c, 100 + i])) });
    expect(r.warnings.some((w) => w.includes('kko'))).toBe(true);
    expect(r.chunks[0]!.tokens.length).toBeGreaterThan(5);
  });

  it('throws, not silently drops text, when a phoneme is missing from the vocabulary', () => {
    expect(() => phonemizeChunks('xin', dict, { s: 1 })).toThrow(/Unsupported phoneme/);
  });

  it('splits long text into chunks that each fit the model (at most 512 tokens)', () => {
    const r = phonemizeChunks(Array.from({ length: 150 }, () => 'xin chào.').join(' '), dict, vocab);
    expect(r.chunks.length).toBeGreaterThan(1);
    for (const c of r.chunks) expect(c.tokens.length).toBeLessThanOrEqual(512);
  });

  it('says a pause for a line with nothing to speak', () => {
    const r = phonemizeChunks('[Music]', dict, vocab);
    expect(r.chunks).toHaveLength(1);
  });
});
