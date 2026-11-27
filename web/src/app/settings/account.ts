/**
 * "Tài khoản" tab: sign in with Google so reading history, followed stories and bookmarks follow the account to
 * every device. Signed out: the official Google button (browser, desktop) or a native button (Android). Signed in:
 * avatar, name, e-mail, sync state with the time of the last sync, "Đồng bộ ngay" and "Đăng xuất".
 *
 * Nothing secret is shown or put in the DOM: the session token never leaves `core/auth-token.ts`.
 */
import { auth, AuthError } from '../core/auth';
import { fmtNum, timeAgo } from '../core/format';
import { html, render } from '../core/html';
import { icon } from '../core/icons';
import { library } from '../core/library';
import { librarySync } from '../core/library-sync';
import { progressSync } from '../core/progress-sync';
import { syncStatus } from '../core/sync-status';
import { confirmDialog, toast } from '../core/ui';

/** One line about syncing for the signed-in view. */
export function syncLine(s: { lastOk: number | null; running: boolean; failing: boolean }, now = Date.now()): string {
  if (s.running && s.lastOk === null) return 'Đang đồng bộ…';
  if (s.failing) return s.lastOk ? `Chưa đồng bộ được, sẽ thử lại. Lần cuối ${timeAgo(s.lastOk, now)}.` : 'Chưa đồng bộ được, sẽ thử lại.';
  if (s.running) return 'Đang đồng bộ…';
  if (s.lastOk) return `Đồng bộ lần cuối ${timeAgo(s.lastOk, now)}.`;
  return 'Chưa đồng bộ.';
}

/** Google serves the avatar from https hosts only; anything else is ignored. */
const avatarUrl = (u: string): string => (/^https:\/\//i.test(u) ? u : '');

export function mountAccount(el: HTMLElement): () => void {
  let alive = true;
  let error = '';
  let busy = false;
  let host: HTMLElement | null = null;

  const paint = (): void => {
    if (!alive) return;
    const u = auth.user();
    if (u) {
      const pic = avatarUrl(u.picture);
      const s = syncStatus.get();
      const nFollow = library.follows().length;
      const nMarks = library.bookmarks().length;
      render(
        el,
        html`<section class="ss-sec ac" aria-labelledby="ss-h-acc">
          <h3 class="ss-h" id="ss-h-acc">Tài khoản</h3>
          <div class="ac-card">
            <span class="ac-avatar-wrap">
              ${pic ? html`<img class="ac-avatar" src="${pic}" alt="" width="56" height="56" referrerpolicy="no-referrer" />` : html`<span class="ac-avatar ac-avatar-fb" aria-hidden="true">${(u.name || u.email || '?').slice(0, 1).toUpperCase()}</span>`}
              <span class="ac-badge ${s.failing ? 'is-error' : ''}" aria-hidden="true">${icon(s.failing ? 'refresh' : 'check')}</span>
            </span>
            <div class="ac-who">
              <p class="ac-name">${u.name || u.email}</p>
              ${u.name && u.email ? html`<p class="ac-mail">${u.email}</p>` : ''}
              <p class="ac-provider"><svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path fill="#4285F4" d="M22.5 12.2c0-.8-.1-1.5-.2-2.2H12v4.2h5.9a5 5 0 0 1-2.2 3.3v2.7h3.5c2.1-1.900 3.300-4.700 3.300-8z"/><path fill="#34A853" d="M12 23c3 0 5.500-1 7.300-2.700l-3.500-2.700c-1 .7-2.200 1.100-3.800 1.100-2.900 0-5.400-2-6.300-4.600H2.100v2.800A11 11 0 0 0 12 23z"/><path fill="#FBBC05" d="M5.700 14.100a6.600 6.600 0 0 1 0-4.200V7.100H2.100a11 11 0 0 0 0 9.800z"/><path fill="#EA4335" d="M12 5.400c1.600 0 3.100.6 4.200 1.600l3.100-3.100A11 11 0 0 0 2.100 7.100l3.600 2.800C6.600 7.400 9.100 5.400 12 5.400z"/></svg><span>Google</span></p>
            </div>
          </div>
          <div class="ac-stats">
            <div class="ac-stat"><strong>${fmtNum(nFollow)}</strong><span>Truyện theo dõi</span></div>
            <div class="ac-stat"><strong>${fmtNum(nMarks)}</strong><span>Đánh dấu</span></div>
          </div>
          <p class="ac-sync ${s.failing ? 'is-error' : ''} ${s.running ? 'is-running' : ''}" id="ac-sync" role="status" aria-live="polite"><span class="ac-dot" aria-hidden="true"></span><span class="ac-sync-t">${syncLine(s)}</span></p>
          <p class="hint">Lịch sử đọc, truyện theo dõi và đánh dấu được đồng bộ giữa các thiết bị đăng nhập cùng tài khoản. Dữ liệu trên máy này luôn được giữ lại.</p>
          <div class="ss-actions ac-actions">
            <button type="button" class="btn btn-primary" id="ac-sync-now" ${s.running || busy ? html`disabled` : ''}>${icon('refresh')}<span>Đồng bộ ngay</span></button>
            <button type="button" class="btn btn-danger-ghost" id="ac-out" ${busy ? html`disabled` : ''}>Đăng xuất</button>
          </div>
        </section>`,
      );
      host = null;
      return;
    }
    const native = auth.mode() === 'native';
    render(
      el,
      html`<section class="ss-sec ac" aria-labelledby="ss-h-acc">
        <h3 class="ss-h" id="ss-h-acc">Tài khoản</h3>
        <div class="ac-hero">
          <span class="ac-hero-ico" aria-hidden="true">${icon('cloud')}</span>
          <p class="ac-hero-t">Đọc tiếp ở mọi thiết bị</p>
        </div>
        <ul class="ac-perks">
          <li>${icon('check')}<span>Đồng bộ lịch sử đọc, truyện theo dõi và đánh dấu giữa điện thoại, máy tính và trình duyệt.</span></li>
          <li>${icon('check')}<span>Dữ liệu đang có trên máy được gộp lên tài khoản, không bị xoá.</span></li>
          <li>${icon('check')}<span>Chỉ dùng tên, email và ảnh Google để nhận diện. Không đăng bài, không gửi thư.</span></li>
        </ul>
        ${native
          ? html`<div class="ss-actions"><button type="button" class="btn btn-primary" id="ac-in" ${busy ? html`disabled` : ''}>${icon('user')}<span>Đăng nhập bằng Google</span></button></div>`
          : html`<div class="ac-gsi" id="ac-gsi" aria-label="Đăng nhập bằng Google"></div>`}
        <p class="form-status is-error" id="ac-err" role="alert" ${error ? '' : html`hidden`}>${error}</p>
        <p class="hint">Chưa đăng nhập vẫn đọc bình thường; tiến độ đọc khi đó chỉ nằm trên máy.</p>
      </section>`,
    );
    host = el.querySelector<HTMLElement>('#ac-gsi');
    if (host) void drawButton(host);
  };

  const fail = (e: unknown): void => {
    const x = e instanceof AuthError ? e : null;
    if (x?.code === 'cancelled') error = '';
    else error = x ? x.message : 'Không đăng nhập được.';
    busy = false;
    paint();
  };

  async function drawButton(h: HTMLElement): Promise<void> {
    try {
      await auth.renderButton(h, (r) => {
        if ('error' in r) fail(r.error);
        else paint();
      });
    } catch (e) {
      if (alive && host === h) fail(e);
    }
  }

  el.addEventListener('click', (e) => {
    const t = e.target as Element;
    if (t.closest('#ac-in')) {
      busy = true;
      error = '';
      paint();
      auth.signInNative().then(
        () => {
          busy = false;
          paint();
        },
        fail,
      );
    } else if (t.closest('#ac-sync-now')) {
      void Promise.all([progressSync.sync(), librarySync.sync()]).then(() => {
        const s = syncStatus.get();
        toast(s.failing ? { message: 'Chưa đồng bộ được. Sẽ thử lại sau.', kind: 'error' } : { message: 'Đã đồng bộ.', kind: 'ok' });
      });
    } else if (t.closest('#ac-out')) {
      void (async () => {
        const ok = await confirmDialog({
          title: 'Đăng xuất khỏi Google?',
          message: 'Máy này ngừng đồng bộ. Lịch sử đọc, truyện yêu thích và đánh dấu trên máy được giữ nguyên; dữ liệu trên tài khoản cũng không bị xoá.',
          confirmLabel: 'Đăng xuất',
          cancelLabel: 'Giữ nguyên',
          danger: true,
        });
        if (!ok) return;
        busy = true;
        paint();
        await auth.signOut();
        busy = false;
        toast('Đã đăng xuất. Dữ liệu trên máy được giữ nguyên.');
        paint();
      })();
    }
  });

  paint();
  const offs = [auth.onChange(paint), syncStatus.on(() => alive && auth.user() && patchStatus())];
  /** Only the status line changes while syncing, so the buttons keep focus. */
  function patchStatus(): void {
    const line = el.querySelector<HTMLElement>('#ac-sync');
    const btn = el.querySelector<HTMLButtonElement>('#ac-sync-now');
    if (!line || !btn) return paint();
    const s = syncStatus.get();
    const t = line.querySelector<HTMLElement>('.ac-sync-t');
    if (t) t.textContent = syncLine(s);
    line.classList.toggle('is-error', s.failing);
    line.classList.toggle('is-running', s.running);
    btn.disabled = s.running;
  }
  return () => {
    alive = false;
    for (const off of offs) off();
  };
}
