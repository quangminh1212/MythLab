/** The keyboard help of the reader ("?"). */
import { html, type SafeHtml } from '../core/html';
import { openDialog, type DialogHandle } from '../core/ui';

const GROUPS: { title: string; keys: [string[], string][] }[] = [
  {
    title: 'Đọc',
    keys: [
      [['←', '→'], 'Chương trước / sau (chế độ cuộn) · trang trước / sau (chế độ trang)'],
      [['Shift', '←/→'], 'Chương trước / sau (khi đang nghe: chương của trình nghe)'],
      [['PgUp', 'PgDn'], 'Lật một trang'],
      [['Home', 'End'], 'Đầu / cuối chương'],
      [['M'], 'Mở mục lục chương'],
      [['B'], 'Đánh dấu đoạn đang đọc'],
      [['A'], 'Bật / tắt tự cuộn'],
      [['+', '−'], 'Tự cuộn nhanh hơn / chậm hơn'],
      [['Esc'], 'Dừng tự cuộn · hiện thanh điều khiển'],
      [['?'], 'Mở bảng phím tắt này'],
    ],
  },
  {
    title: 'Nghe',
    keys: [
      [['Phím cách'], 'Nghe từ đoạn đang đọc · tạm dừng / nghe tiếp'],
      [['J', 'K'], 'Tới / lùi một đoạn'],
      [['Nhấp đúp'], 'Nghe từ đoạn văn được nhấp'],
    ],
  },
  {
    title: 'Cảm ứng (điện thoại)',
    keys: [
      [['Chạm'], 'Hiện / ẩn thanh điều khiển · chế độ trang: chạm mép trái / phải để lật trang'],
      [['Vuốt ngang'], 'Chế độ trang: lật trang · chế độ cuộn: chuyển chương (vuốt xa khỏi mép màn hình)'],
      [['Chạm hai lần'], 'Nghe từ đoạn văn được chạm'],
      [['Nút “…”'], 'Đánh dấu, tự cuộn, về đầu / cuối chương, cài đặt, danh mục'],
      [['Nút ⌃ ở thanh nghe'], 'Mở bảng nghe: đoạn / chương trước sau, tốc độ, hẹn giờ, giọng đọc'],
    ],
  },
];

function body(): SafeHtml {
  return html`<div class="rd-help">
    ${GROUPS.map(
      (g) =>
        html`<section>
          <h3 class="rd-help-title">${g.title}</h3>
          <dl class="rd-help-list">
            ${g.keys.map(([keys, what]) => html`<div class="rd-help-row"><dt>${keys.map((k) => html`<kbd>${k}</kbd>`)}</dt><dd>${what}</dd></div>`)}
          </dl>
        </section>`,
    )}
  </div>`;
}

let open: DialogHandle | null = null;

export function openHelp(): void {
  if (open && !open.closed) return;
  open = openDialog({
    title: 'Phím tắt',
    body: body(),
    className: 'rd-help-dialog',
    onClose: () => {
      open = null;
    },
  });
}
