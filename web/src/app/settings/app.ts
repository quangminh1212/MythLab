/**
 * "Ứng dụng" tab (Android app only): installed version, "Kiểm tra cập nhật" and, when the server has a newer APK,
 * "Tải và cài đặt" with a progress bar. All work is in `core/app-update.ts`.
 */
import { appUpdate, fmtMB, type UpdateState } from '../core/app-update';
import { html, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';

function body(s: UpdateState, installed: string): { text: string; err: boolean; actions: SafeHtml; extra: SafeHtml } {
  const check = (primary: boolean): SafeHtml =>
    html`<button type="button" class="btn ${primary ? 'btn-primary' : ''}" data-up="check">${icon('refresh')}<span>Kiểm tra cập nhật</span></button>`;
  const none = html``;
  switch (s.kind) {
    case 'checking':
      return { text: 'Đang kiểm tra…', err: false, actions: html`<button type="button" class="btn" disabled>${icon('refresh')}<span>Đang kiểm tra…</span></button>`, extra: none };
    case 'uptodate':
      return { text: 'Bạn đang dùng bản mới nhất.', err: false, actions: check(false), extra: none };
    case 'available':
      return {
        text: `Có bản mới ${s.latest.versionName}${s.latest.size ? ` (${fmtMB(s.latest.size)})` : ''}.`,
        err: false,
        actions: html`<button type="button" class="btn btn-primary" data-up="start">Tải và cài đặt</button>${check(false)}`,
        extra: s.latest.notes ? html`<p class="hint up-notes">${s.latest.notes}</p>` : none,
      };
    case 'downloading': {
      const pct = s.total > 0 ? Math.min(100, Math.round((s.loaded / s.total) * 100)) : 0;
      return {
        text: s.total > 0 ? `Đang tải ${fmtMB(s.loaded)} / ${fmtMB(s.total)}…` : `Đang tải ${fmtMB(s.loaded)}…`,
        err: false,
        actions: html`<button type="button" class="btn" disabled>Đang tải…</button>`,
        extra: html`<progress class="up-bar" max="100" value="${pct}" aria-label="Tiến độ tải bản cập nhật"></progress>`,
      };
    }
    case 'ready':
      return s.needPermission
        ? {
            text: 'Android cần bạn cho phép MythLab cài ứng dụng. Bật công tắc trong màn hình vừa mở, quay lại đây rồi bấm Cài đặt.',
            err: false,
            actions: html`<button type="button" class="btn btn-primary" data-up="install">Cài đặt</button>`,
            extra: none,
          }
        : {
            text: 'Đã tải xong. Làm theo màn hình cài đặt của Android; nếu vừa đóng nó, bấm Cài đặt để mở lại.',
            err: false,
            actions: html`<button type="button" class="btn btn-primary" data-up="install">Cài đặt</button>`,
            extra: none,
          };
    case 'error':
      return { text: s.message, err: true, actions: check(true), extra: none };
    default:
      return { text: `Phiên bản ${installed || 'chưa rõ'}.`, err: false, actions: check(true), extra: none };
  }
}

export function mountApp(el: HTMLElement): () => void {
  let alive = true;
  let installed = '';

  const paint = (): void => {
    if (!alive) return;
    const s = appUpdate.get();
    const cur = s.kind === 'uptodate' || s.kind === 'available' ? s.current : s.kind === 'error' ? s.current : undefined;
    if (cur?.versionName) installed = cur.versionName;
    const b = body(s, installed);
    render(
      el,
      html`<section class="ss-sec" aria-labelledby="ss-h-app">
        <h3 class="ss-h" id="ss-h-app">Cập nhật ứng dụng</h3>
        ${installed ? html`<p class="hint">Đang cài: bản ${installed}.</p>` : ''}
        <p class="ss-status ${b.err ? 'is-error' : ''}" role="status" aria-live="polite">${b.text}</p>
        ${b.extra}
        <div class="ss-actions">${b.actions}</div>
        <p class="hint">Bản mới được tải từ máy chủ MythLab và cài đè lên bản hiện tại; truyện đã tải, lịch sử đọc và cài đặt vẫn được giữ.</p>
      </section>`,
    );
  };

  const onClick = (e: Event): void => {
    const b = (e.target as Element).closest<HTMLElement>('[data-up]');
    if (!b) return;
    const act = b.dataset.up;
    if (act === 'check') void appUpdate.check();
    else if (act === 'start') void appUpdate.start();
    else if (act === 'install') void appUpdate.install();
  };

  el.addEventListener('click', onClick);
  const off = appUpdate.on(paint);
  paint();
  // opening the tab refreshes the answer once, unless a download is in flight
  const k = appUpdate.get().kind;
  if (k === 'idle' || k === 'uptodate' || k === 'error') void appUpdate.check();

  return () => {
    alive = false;
    off();
    el.removeEventListener('click', onClick);
  };
}
