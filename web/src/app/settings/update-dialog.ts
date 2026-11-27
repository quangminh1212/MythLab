/** Android app: the "Có bản mới" dialog (version, size, what changed, progress, install). Logic is in core/app-update.ts. */
import { appUpdate, fmtMB, type UpdateState } from '../core/app-update';
import { html, render, type SafeHtml } from '../core/html';
import { openDialog, type DialogHandle } from '../core/ui';

let open: DialogHandle | null = null;

export function dialogView(s: UpdateState): { title: string; body: SafeHtml; footer: SafeHtml } {
  const later = html`<button type="button" class="btn" data-close>Để sau</button>`;
  switch (s.kind) {
    case 'available':
      return {
        title: `Có bản mới ${s.latest.versionName}`,
        body: html`<p class="dialog-text">Bản đang cài: ${s.current.versionName}${s.latest.size ? `. Dung lượng tải: ${fmtMB(s.latest.size)}.` : '.'}</p>
          ${s.latest.notes ? html`<p class="hint up-notes">${s.latest.notes}</p>` : ''}
          <p class="hint">Truyện đã tải, lịch sử đọc và cài đặt vẫn được giữ.</p>`,
        footer: html`${later}<button type="button" class="btn btn-primary" data-up="start">Tải và cài đặt</button>`,
      };
    case 'downloading': {
      const pct = s.total > 0 ? Math.min(100, Math.round((s.loaded / s.total) * 100)) : 0;
      return {
        title: `Đang tải bản ${s.latest.versionName}`,
        body: html`<p class="dialog-text" role="status" aria-live="polite">${s.total > 0 ? `${fmtMB(s.loaded)} / ${fmtMB(s.total)} (${pct}%)` : fmtMB(s.loaded)}</p>
          <progress class="up-bar" max="100" value="${pct}" aria-label="Tiến độ tải bản cập nhật"></progress>`,
        footer: html`<button type="button" class="btn" disabled>Đang tải…</button>`,
      };
    }
    case 'ready':
      return {
        title: s.needPermission ? 'Cần cho phép cài đặt' : 'Đã tải xong',
        body: html`<p class="dialog-text">${s.needPermission ? 'Bật công tắc "Cho phép từ nguồn này" trong màn hình Android vừa mở rồi quay lại đây; ứng dụng sẽ tự mở trình cài đặt.' : 'Làm theo màn hình cài đặt của Android. Nếu lỡ đóng, bấm Cài đặt để mở lại.'}</p>`,
        footer: html`${later}<button type="button" class="btn btn-primary" data-up="install">Cài đặt</button>`,
      };
    case 'error':
      return {
        title: 'Không cập nhật được',
        body: html`<p class="dialog-text">${s.message}</p>`,
        footer: html`${later}<button type="button" class="btn btn-primary" data-up="start">Thử lại</button>`,
      };
    default:
      return { title: 'Cập nhật ứng dụng', body: html`<p class="dialog-text">Đang kiểm tra…</p>`, footer: later };
  }
}

export function openUpdateDialog(): void {
  if (open && !open.closed) return;
  const v = dialogView(appUpdate.get());
  const d = openDialog({ title: v.title, body: v.body, footer: v.footer, className: 'dialog-sm', persistent: true, dismissable: false, onClose: () => off() });
  open = d;
  const paint = (): void => {
    if (d.closed) return;
    const n = dialogView(appUpdate.get());
    const t = d.el.querySelector('.dialog-title');
    if (t) t.textContent = n.title;
    // the dialog helper renders once: swap the body and footer markup in place
    const foot = d.el.querySelector('.dialog-foot');
    render(d.body, n.body);
    if (foot) render(foot as HTMLElement, n.footer);
  };
  const off = appUpdate.on(paint);
  d.el.addEventListener('click', (e) => {
    const b = (e.target as Element).closest<HTMLElement>('[data-up]');
    if (!b) return;
    if (b.dataset.up === 'start') void appUpdate.start();
    else if (b.dataset.up === 'install') void appUpdate.install();
  });
}
