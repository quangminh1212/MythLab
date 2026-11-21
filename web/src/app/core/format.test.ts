import { describe, expect, it } from 'vitest';
import { chapterLabel, chapterNumber, chapterTitle, fmtBytes, fmtNum, hashHue, normKey, normTxt, repoLabel, searchMatch, sKey, timeAgo } from './format';

describe('format', () => {
  it('formats a chapter as "Chương N: Tên" everywhere', () => {
    expect(chapterLabel({ n: 6, title: 'Tĩnh Tâm Uyển' })).toBe('Chương 6: Tĩnh Tâm Uyển');
    expect(chapterLabel({ n: 6, title: '' })).toBe('Chương 6');
    expect(chapterLabel({ n: 6, title: null })).toBe('Chương 6');
    expect(chapterLabel({ n: 6, title: 'Chương 6: Tĩnh Tâm Uyển' })).toBe('Chương 6: Tĩnh Tâm Uyển');
    expect(chapterLabel({ n: 6, title: 'chương 6 - bóc hoàng bảng' })).toBe('Chương 6: Bóc hoàng bảng');
    expect(chapterLabel({ n: 6, title: 'Chương 7 năm sau' })).toBe('Chương 6: Chương 7 năm sau');
    expect(chapterLabel({ n: 12, sub: 5, vol: 2, title: 'Ngoại truyện' })).toBe('Quyển 2 - Chương 12.5: Ngoại truyện');
    expect(chapterNumber({ n: 3, sub: 1 })).toBe('Chương 3.1');
    expect(chapterTitle({ n: 6, title: 'Tĩnh Tâm Uyển' })).toBe('Tĩnh Tâm Uyển');
    expect(chapterTitle({ n: 6 })).toBe('');
    expect(chapterLabel(null)).toBe('');
  });

  it('normalises Vietnamese for search', () => {
    expect(normTxt('ĐẠI Đế')).toBe('dai de');
    expect(normKey('Cổ-Tích:  Đường!')).toBe('co tich duong');
    expect(searchMatch('co tich', 'CoTich')).toBe(true);
    expect(searchMatch('cổ tích', 'Truyện Cổ Tích Việt Nam')).toBe(true);
    expect(searchMatch('kiếm hiệp', 'Truyện Cổ Tích')).toBe(false);
  });

  it('labels repositories without the technical prefix', () => {
    expect(repoLabel('Done_CoTich')).toBe('Co Tich');
    expect(repoLabel('Done_Tien_Hiep')).toBe('Tien Hiep');
    expect(repoLabel('Done_')).toBe('Done_');
    expect(repoLabel('KhoTruyen')).toBe('Kho Truyen');
  });

  it('formats numbers, sizes and relative time', () => {
    expect(fmtNum(2888)).toBe('2.888');
    expect(fmtNum(null)).toBe('');
    expect(fmtBytes(0)).toBe('0 MB');
    expect(fmtBytes(5 * 1024 * 1024)).toBe('5,0 MB');
    const now = Date.UTC(2026, 0, 10, 12);
    expect(timeAgo(now - 10_000, now)).toBe('vừa xong');
    expect(timeAgo(now - 5 * 60_000, now)).toBe('5 phút trước');
    expect(timeAgo(now - 86_400_000, now).toLowerCase()).toBe('hôm qua');
    expect(timeAgo(now - 90 * 86_400_000, now)).toMatch(/^\d{2}\/\d{2}\/\d{4}$/);
  });

  it('hashes to a stable hue and builds progress keys', () => {
    expect(hashHue('abc')).toBe(hashHue('abc'));
    expect(hashHue('abc')).toBeGreaterThanOrEqual(0);
    expect(hashHue('abc')).toBeLessThan(360);
    expect(sKey('gh0', 'a/b')).toBe('gh0|a/b');
  });
});
