import { describe, expect, it } from 'vitest';
import { buildChunks, clean, edgePitch, EDGE_MAX, LOCAL_MAX, offsetAtTime, pieces, segments, sentAt, sleepLabel, splitSentences, startChunk, titleText } from './text';

const texts = (text: string, spans: { s: number; e: number }[]): string[] => spans.map((x) => text.slice(x.s, x.e));

describe('clean', () => {
  it('drops symbols and collapses punctuation', () => {
    expect(clean('Xin   chào *** bạn!!!   Thật.... sao ???')).toBe('Xin chào bạn! Thật… sao?');
    expect(clean('“ ” (  ) a')).toBe('a');
    expect(clean('~~~ *** ---')).toBe('');
  });
  it('keeps the text when cleaning is off, but still refuses unspeakable text', () => {
    expect(clean('  a  *b*  ', false)).toBe('a *b*');
    expect(clean('***', false)).toBe('');
  });
});

describe('splitSentences', () => {
  it('covers the text completely with contiguous spans', () => {
    const t = 'Trời đã sáng. Nàng mở mắt! “Đi thôi?” hắn hỏi… Không ai đáp';
    const sp = splitSentences(t);
    expect(texts(t, sp)).toEqual(['Trời đã sáng. ', 'Nàng mở mắt! ', '“Đi thôi?” ', 'hắn hỏi… ', 'Không ai đáp']);
    expect(sp[0]?.s).toBe(0);
    expect(sp[sp.length - 1]?.e).toBe(t.length);
    for (let i = 1; i < sp.length; i++) expect(sp[i]?.s).toBe(sp[i - 1]?.e);
  });
  it('does not split inside numbers or abbreviations', () => {
    const t = 'Giá là 3.5 lượng v.v... rồi thôi. Hết.';
    expect(texts(t, splitSentences(t))).toEqual(['Giá là 3.5 lượng v.v... ', 'rồi thôi. ', 'Hết.']);
  });
  it('joins spans that hold nothing speakable to a neighbour', () => {
    const t = '… Rồi nàng đi. ”';
    expect(texts(t, splitSentences(t))).toEqual(['… Rồi nàng đi. ”']);
    expect(splitSentences('')).toEqual([]);
  });
});

describe('segments', () => {
  it('splits a sentence longer than the limit at clause marks, then at spaces', () => {
    const t = 'một hai ba, bốn năm sáu, bảy tám chín mười mười một.';
    const sp = segments(t, 20);
    expect(sp.every((x) => x.e - x.s <= 20)).toBe(true);
    expect(texts(t, sp).join('')).toBe(t);
    const long = 'x'.repeat(50);
    expect(texts(long, segments(long, 20)).map((s) => s.length)).toEqual([20, 20, 10]);
  });
});

describe('buildChunks', () => {
  const ch = {
    title: 'Chương 6: Tĩnh Tâm Uyển [đã sửa]',
    paragraphs: ['Câu một. Câu hai! Câu ba?', '***', 'Đoạn ngắn.'],
  };
  it('reads the title first as chunk -1 and skips scene breaks', () => {
    const c = buildChunks(ch, { max: EDGE_MAX, readTitle: true, clean: true });
    expect(c.map((x) => x.p)).toEqual([-1, 0, 2]);
    expect(c[0]?.text).toBe('Chương 6. Tĩnh Tâm Uyển');
    expect(c[1]?.text).toBe('Câu một. Câu hai! Câu ba?');
    expect(c[1]?.sents.map((s) => c[1]?.text.slice(s.at, s.at + s.len))).toEqual(['Câu một.', 'Câu hai!', 'Câu ba?']);
    expect(c[1]?.sents.map((s) => ch.paragraphs[0]?.slice(s.s, s.e))).toEqual(['Câu một. ', 'Câu hai! ', 'Câu ba?']);
  });
  it('leaves the title out when the setting is off', () => {
    expect(buildChunks(ch, { max: EDGE_MAX, readTitle: false, clean: true }).map((x) => x.p)).toEqual([0, 2]);
  });
  it('groups sentences up to the limit and never exceeds it', () => {
    const para = Array.from({ length: 30 }, (_, i) => `Đây là câu số ${i} của đoạn văn dài.`).join(' ');
    const c = buildChunks({ title: null, paragraphs: [para] }, { max: LOCAL_MAX, readTitle: true, clean: true });
    expect(c.length).toBeGreaterThan(3);
    expect(c.every((x) => x.p === 0 && x.text.length <= LOCAL_MAX)).toBe(true);
    // every character of the paragraph belongs to exactly one sentence of one chunk
    const spans = c.flatMap((x) => x.sents);
    expect(spans[0]?.s).toBe(0);
    expect(spans[spans.length - 1]?.e).toBe(para.length);
    for (let i = 1; i < spans.length; i++) expect(spans[i]?.s).toBe(spans[i - 1]?.e);
  });
});

describe('startChunk', () => {
  const c = buildChunks({ title: 'Chương 1', paragraphs: ['A.', '***', 'B.', 'C.'] }, { max: 100, readTitle: true, clean: true });
  it('starts at the title for "from the top" and at the paragraph otherwise', () => {
    expect(startChunk(c, -1)).toBe(0);
    expect(c[startChunk(c, 0)]?.p).toBe(0);
    expect(c[startChunk(c, 1)]?.p).toBe(2); // paragraph 1 is a scene break: the next spoken one
    expect(c[startChunk(c, 3)]?.p).toBe(3);
    expect(startChunk(c, 99)).toBe(c.length - 1);
    expect(startChunk([], 0)).toBe(0);
  });
});

describe('sentence position', () => {
  const [c] = buildChunks({ title: null, paragraphs: ['Câu một. Câu hai! Câu ba?'] }, { max: 100, readTitle: false, clean: true });
  if (!c) throw new Error('no chunk');
  it('maps a spoken offset to its sentence', () => {
    expect(sentAt(c, 0)).toBe(0);
    expect(sentAt(c, 8)).toBe(0);
    expect(sentAt(c, 9)).toBe(1);
    expect(sentAt(c, 18)).toBe(2);
    expect(sentAt(c, 999)).toBe(2);
  });
  it('estimates the offset from the playback time', () => {
    expect(offsetAtTime(c, 0, 10)).toBe(0);
    expect(offsetAtTime(c, 5, 10)).toBe(Math.floor(c.text.length / 2));
    expect(offsetAtTime(c, 10, 10)).toBe(c.text.length - 1);
    expect(offsetAtTime(c, 1, NaN)).toBe(15);
    expect(offsetAtTime(c, 1, Infinity)).toBe(15);
  });
});

describe('pieces', () => {
  it('keeps short text whole and offsets of long text', () => {
    expect(pieces('ngắn', 10)).toEqual([{ text: 'ngắn', at: 0 }]);
    expect(pieces('   ', 10)).toEqual([]);
    const t = 'một hai, ba bốn, năm sáu bảy tám chín';
    const p = pieces(t, 12);
    expect(p.every((x) => x.text.length <= 12)).toBe(true);
    expect(p.every((x) => t.slice(x.at, x.at + x.text.length) === x.text)).toBe(true);
  });
});

describe('small helpers', () => {
  it('titleText', () => {
    expect(titleText('Chương 12 - Về nhà')).toBe('Chương 12. Về nhà');
    expect(titleText('Quyển 2 - Chương 1: Mở đầu [1]')).toBe('Quyển 2 - Chương 1. Mở đầu');
    expect(titleText('Ngoại truyện')).toBe('Ngoại truyện');
  });
  it('edgePitch maps the slider to Hz and skips values the server ignores', () => {
    expect(edgePitch(1)).toBeUndefined();
    expect(edgePitch(1.05)).toBeUndefined();
    expect(edgePitch(1.2)).toBe(10);
    expect(edgePitch(0.5)).toBe(-25);
    expect(edgePitch(2)).toBe(50);
  });
  it('sleepLabel', () => {
    expect(sleepLabel(0)).toBe('');
    expect(sleepLabel(29.2 * 60_000)).toBe('30 phút');
    expect(sleepLabel(45_000)).toBe('45 giây');
  });
});
