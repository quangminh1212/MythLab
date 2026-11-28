/** "Báo lỗi chương": a prefilled GitHub issue link. */
export const ISSUES_URL = 'https://github.com/quangminh1212/MythLab/issues/new';

export function reportUrl(o: { story: string; source: string; key: string; chapter: string; idx: number; page?: string }): string {
  const q = new URLSearchParams({
    title: `Lỗi chương: ${o.story} - ${o.chapter}`.slice(0, 200),
    body: `Truyện: ${o.story}\nNguồn: ${o.source}\nKhóa: ${o.key}\nChương: ${o.chapter} (số thứ tự ${o.idx + 1})${o.page ? `\nVị trí: ${o.page}` : ''}\n\nMô tả lỗi:\n`,
  });
  return `${ISSUES_URL}?${q.toString()}`;
}
