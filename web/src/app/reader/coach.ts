/** First-run coach marks of the reader: shown once, can be re-opened from the help dialog. */
import { html } from '../core/html';
import { store } from '../core/store';
import { openDialog, type DialogHandle } from '../core/ui';

export const COACH_KEY = 'mythlab.reader.coach';

export const coachSeen = (): boolean => store.get<boolean>(COACH_KEY, false) === true;
export const markCoachSeen = (): void => void store.set(COACH_KEY, true);

let open: DialogHandle | null = null;

export function openCoach(o: { paged: boolean }): void {
  if (open && !open.closed) return;
  const tips: [string, string][] = [
    ['Chạm giữa màn hình', 'Hiện / ẩn thanh điều khiển (mục lục, đánh dấu, nghe đọc, cài đặt).'],
    o.paged
      ? ['Chạm mép trái / phải hoặc vuốt ngang', 'Lật trang trước / sau.']
      : ['Cuộn, hoặc vuốt ngang từ trong màn hình', 'Cuộn để đọc tiếp; vuốt ngang để sang chương trước / sau.'],
    ['Chạm hai lần vào một đoạn', 'Nghe đọc từ đoạn đó.'],
    ['Nút “…” hoặc phím ?', 'Xem thêm tính năng và phím tắt.'],
  ];
  const d = openDialog({
    title: 'Mẹo đọc truyện',
    className: 'rd-coach-dialog',
    body: html`<ul class="rd-coach">${tips.map(([t, w]) => html`<li><strong>${t}</strong><span>${w}</span></li>`)}</ul>`,
    footer: html`<button type="button" class="btn btn-primary" data-coach-ok>Đã hiểu</button>`,
    onClose: () => {
      open = null;
      markCoachSeen();
    },
  });
  open = d;
  d.el.querySelector('[data-coach-ok]')?.addEventListener('click', () => d.close());
}
