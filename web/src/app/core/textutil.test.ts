// Runs the fixture shared with the Go server (server/internal/library/testdata/textutil_cases.json) when the
// repository has it; the built-in cases below always run, so the suite also passes in a web-only checkout.
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { normKey, normTxt, searchMatch } from './format';
import { chapterJson, chapterList, cleanChapterText, countWords, infoSummary, naturalTitle, parseChapterName, pickCover, pyStrip, SCENE_BREAK } from './textutil';

const FIXTURE = resolve(process.cwd(), '../server/internal/library/testdata/textutil_cases.json');

interface Cases {
  parseChapterName: { file: string; expect: unknown }[];
  chapterList: { files: string[]; expect: unknown }[];
  cleanChapterText: { text: string; n?: number; expect: unknown }[];
  chapterJson: { text: string; file: string; expect: unknown }[];
  normTxt: { in: string; out: string }[];
  normKey: { in: string; out: string }[];
  searchMatch: { q: string; field: string; match: boolean }[];
  infoSummary: { info: unknown; fallback: string; expect: unknown }[];
  pickCover: { names: string[]; expect: string | null }[];
}

const has = existsSync(FIXTURE);

describe.skipIf(!has)('shared fixture textutil_cases.json', () => {
  const c = (has ? JSON.parse(readFileSync(FIXTURE, 'utf8')) : {}) as Cases;
  it('has cases for every function', () => {
    for (const k of ['parseChapterName', 'chapterList', 'cleanChapterText', 'chapterJson', 'normTxt', 'normKey', 'searchMatch', 'infoSummary', 'pickCover'] as const) {
      expect(Array.isArray(c[k]) && c[k].length > 0, k).toBe(true);
    }
  });
  it('parseChapterName', () => {
    for (const x of c.parseChapterName) expect(parseChapterName(x.file), x.file).toEqual(x.expect);
  });
  it('chapterList', () => {
    for (const x of c.chapterList) expect(chapterList(x.files), x.files.join(' | ')).toEqual(x.expect);
  });
  it('cleanChapterText', () => {
    for (const x of c.cleanChapterText) expect(cleanChapterText(x.text, x.n), JSON.stringify(x.text).slice(0, 80)).toEqual(x.expect);
  });
  it('chapterJson', () => {
    for (const x of c.chapterJson) expect(chapterJson(x.text, x.file), x.file).toEqual(x.expect);
  });
  it('normTxt and normKey', () => {
    for (const x of c.normTxt) expect(normTxt(x.in), x.in).toBe(x.out);
    for (const x of c.normKey) expect(normKey(x.in), x.in).toBe(x.out);
  });
  it('searchMatch', () => {
    for (const x of c.searchMatch) expect(searchMatch(x.q, x.field), `${x.q} in ${x.field}`).toBe(x.match);
  });
  it('infoSummary', () => {
    for (const x of c.infoSummary) expect(infoSummary(x.info, x.fallback), JSON.stringify(x.info).slice(0, 80)).toEqual(x.expect);
  });
  it('pickCover', () => {
    for (const x of c.pickCover) expect(pickCover(x.names), x.names.join(' | ')).toBe(x.expect);
  });
});

describe('textutil (built-in cases)', () => {
  it('strips like Python', () => {
    expect(pyStrip('  a b 　\n')).toBe('a b');
    expect(pyStrip('--a-b-.', '-.')).toBe('a-b');
    expect(naturalTitle('  - : Tỉnh lại. ')).toBe('Tỉnh lại');
  });

  it('parses chapter file names', () => {
    expect(parseChapterName('Chương 1 - Tỉnh lại.txt')).toEqual({ n: 1, title: 'Tỉnh lại', sub: 0, vol: 0 });
    expect(parseChapterName('chuong 12.5 Ngoại truyện.TXT')).toEqual({ n: 12, title: 'Ngoại truyện', sub: 5, vol: 0 });
    expect(parseChapterName('Quyển 2 - Chương 3: Mở đầu.txt')).toEqual({ n: 3, title: 'Mở đầu', sub: 0, vol: 2 });
    expect(parseChapterName('info.json')).toBeNull();
    expect(parseChapterName('Lời tựa.txt')).toBeNull();
  });

  it('sorts numerically and drops non-chapters', () => {
    expect(chapterList(['Chương 10 B.txt', 'Chương 2 A.txt', 'Chương 1.txt', 'info.json', 'cover.jpg'])).toEqual([
      { n: 1, title: '', file: 'Chương 1.txt' },
      { n: 2, title: 'A', file: 'Chương 2 A.txt' },
      { n: 10, title: 'B', file: 'Chương 10 B.txt' },
    ]);
  });

  it('cleans chapter text: header block, whitespace, scene breaks', () => {
    const rule = '='.repeat(40);
    expect(cleanChapterText(`﻿${rule}\r\nChương 1: Tỉnh lại\r\n${rule}\r\n\r\nĐoạn  một\t ở đây.\r\n\r\n  Đoạn hai.  \r\n`)).toEqual({
      title: 'Chương 1: Tỉnh lại',
      paragraphs: ['Đoạn một ở đây.', 'Đoạn hai.'],
    });
    expect(cleanChapterText('Chương 2: Tên\nA\n-----\n-----\nB\n*****', 2)).toEqual({ title: 'Chương 2: Tên', paragraphs: ['A', SCENE_BREAK, 'B'] });
    // the first paragraph names another chapter: it is text, not the title
    expect(cleanChapterText('Chương 7 đã qua.\nA', 2)).toEqual({ title: null, paragraphs: ['Chương 7 đã qua.', 'A'] });
  });

  it('builds the chapter JSON with a title from the file name', () => {
    expect(chapterJson('Nội dung một hai ba.\nBốn năm.', 'Chương 5 - Tên.txt')).toEqual({ title: 'Chương 5: Tên', paragraphs: ['Nội dung một hai ba.', 'Bốn năm.'], words: 7 });
    expect(countWords(['a b', SCENE_BREAK, 'c'])).toBe(3);
  });

  it('summarises info.json defensively', () => {
    expect(infoSummary(null, 'Thư mục')).toEqual({ name: 'Thư mục', author: null, synopsis: '', poster: null, genres: [], tags: [], status: null, declared_chapters: null, link: null });
    const s = infoSummary({ name: 'T', author: { name: 'A' }, poster: { default: 'd', '600': 'p600' }, genres: [{ name: 'G' }, 'x', null], chapter_count: '82' }, 'F');
    expect(s).toMatchObject({ name: 'T', author: 'A', poster: 'p600', genres: ['G'], declared_chapters: 82 });
  });

  it('picks the cover by name, then the first image', () => {
    expect(pickCover(['b.png', 'a.jpg', 'Chương 1.txt'])).toBe('a.jpg');
    expect(pickCover(['z.png', 'Poster.JPG', 'folder.gif'])).toBe('Poster.JPG');
    expect(pickCover(['Chương 1.txt'])).toBeNull();
  });
});
