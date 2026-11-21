/**
 * First-run screen, shown instead of the browse views while no story source is connected (the page is not
 * served by a MythLab server and neither a server address nor a GitHub token is stored).
 * Two ways in: the address of a MythLab server on the network, or a GitHub access token.
 */
import { backend } from '../core/backend/index';
import type { Route, ViewContext } from '../core/contracts';
import { html, render } from '../core/html';
import { icon } from '../core/icons';
import { toast } from '../core/ui';
import { setCrumbs } from '../shell';

let busy = false;

function setStatus(form: HTMLFormElement, text: string, kind: 'info' | 'error' | 'ok' = 'info'): void {
  const el = form.querySelector<HTMLElement>('.form-status');
  if (!el) return;
  el.textContent = text;
  el.className = `form-status is-${kind}`;
  el.hidden = !text;
}

function setBusy(form: HTMLFormElement, on: boolean, label: string): void {
  busy = on;
  const btn = form.querySelector<HTMLButtonElement>('button[type="submit"]');
  if (!btn) return;
  btn.disabled = on;
  const span = btn.querySelector('span');
  if (span) span.textContent = label;
}

/** "192.168.1.5:8765" → "http://192.168.1.5:8765"; null when it cannot be an address. */
export function normaliseServerUrl(input: string): string | null {
  let v = input.trim();
  if (!v) return null;
  if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(v)) v = 'http://' + v;
  try {
    const u = new URL(v);
    if (u.protocol !== 'http:' && u.protocol !== 'https:') return null;
    if (!u.hostname) return null;
    return u.origin + u.pathname.replace(/\/+$/, '');
  } catch {
    return null;
  }
}

async function connectServer(form: HTMLFormElement): Promise<void> {
  if (busy) return;
  const urlIn = form.querySelector<HTMLInputElement>('#ob-url') as HTMLInputElement;
  const keyIn = form.querySelector<HTMLInputElement>('#ob-key') as HTMLInputElement;
  const url = normaliseServerUrl(urlIn.value);
  if (!url) {
    setStatus(form, 'Hãy nhập địa chỉ máy chủ, ví dụ 192.168.1.10:8765.', 'error');
    urlIn.setAttribute('aria-invalid', 'true');
    urlIn.focus();
    return;
  }
  urlIn.removeAttribute('aria-invalid');
  keyIn.removeAttribute('aria-invalid');
  setBusy(form, true, 'Đang kết nối…');
  setStatus(form, 'Đang kiểm tra máy chủ…');
  try {
    const res = await backend.testServer(url, keyIn.value.trim());
    if (res === 'ok') {
      setStatus(form, 'Đã kết nối. Đang mở thư viện…', 'ok');
      await backend.useServer(url, keyIn.value.trim());
      toast({ message: 'Đã kết nối tới máy chủ truyện.', kind: 'ok' });
      return;
    }
    if (res === 'auth') {
      setStatus(form, keyIn.value ? 'Mã truy cập không đúng. Kiểm tra lại mã trên máy chủ.' : 'Máy chủ này cần mã truy cập. Hãy nhập mã rồi thử lại.', 'error');
      keyIn.setAttribute('aria-invalid', 'true');
      keyIn.focus();
      return;
    }
    const mixed = location.protocol === 'https:' && url.startsWith('http://');
    setStatus(
      form,
      mixed
        ? 'Không kết nối được. Trang này đang mở qua https nên trình duyệt chặn máy chủ dùng http. Hãy mở MythLab từ chính địa chỉ của máy chủ.'
        : 'Không kết nối được tới máy chủ. Kiểm tra địa chỉ, máy chủ đang chạy và hai thiết bị cùng mạng.',
      'error',
    );
    urlIn.focus();
  } catch {
    setStatus(form, 'Không kết nối được tới máy chủ. Vui lòng thử lại.', 'error');
  } finally {
    setBusy(form, false, 'Kết nối');
  }
}

async function connectGitHub(form: HTMLFormElement): Promise<void> {
  if (busy) return;
  const tokIn = form.querySelector<HTMLInputElement>('#ob-token') as HTMLInputElement;
  const token = tokIn.value.trim();
  if (!token) {
    setStatus(form, 'Hãy dán mã truy cập GitHub vào ô trên.', 'error');
    tokIn.setAttribute('aria-invalid', 'true');
    tokIn.focus();
    return;
  }
  tokIn.removeAttribute('aria-invalid');
  setBusy(form, true, 'Đang kiểm tra…');
  setStatus(form, 'Đang kiểm tra mã truy cập…');
  try {
    const res = await backend.testToken(token);
    if (!res.ok) {
      setStatus(form, 'GitHub không chấp nhận mã này. Kiểm tra lại mã hoặc tạo mã mới có quyền đọc kho truyện.', 'error');
      tokIn.setAttribute('aria-invalid', 'true');
      tokIn.focus();
      return;
    }
    if (!res.repos) {
      setStatus(form, `Mã hợp lệ${res.login ? ` (tài khoản ${res.login})` : ''} nhưng chưa thấy kho truyện nào. Hãy cấp quyền đọc các kho truyện cho mã này.`, 'error');
      return;
    }
    setStatus(form, `Đã nhận ${res.repos} kho truyện. Đang mở thư viện…`, 'ok');
    await backend.useToken(token);
    toast({ message: 'Đã kết nối tới GitHub.', kind: 'ok' });
  } catch {
    setStatus(form, navigator.onLine === false ? 'Bạn đang ngoại tuyến. Kiểm tra kết nối mạng rồi thử lại.' : 'Không kết nối được tới GitHub. Vui lòng thử lại.', 'error');
  } finally {
    setBusy(form, false, 'Dùng mã này');
  }
}

export function mount(el: HTMLElement, _route: Route, ctx: ViewContext): void {
  busy = false;
  ctx.setTitle('Kết nối nguồn truyện');
  setCrumbs([]);
  const saved = backend.serverConfig();
  render(
    el,
    html`<div class="page page-onboard">
      <header class="onboard-head">
        <h1 class="page-title">Chào mừng đến với MythLab</h1>
        <p class="page-sub">Để bắt đầu đọc, hãy cho ứng dụng biết truyện của bạn nằm ở đâu. Bạn chỉ cần làm một lần; thông tin được lưu trên thiết bị này.</p>
      </header>
      <div class="onboard-grid">
        <form class="panel" id="ob-server" novalidate>
          <h2 class="panel-title">${icon('server')}<span>Máy chủ MythLab</span></h2>
          <p class="panel-text">Dùng khi bạn đang chạy MythLab trên máy tính trong nhà. Địa chỉ được hiện trên cửa sổ máy chủ khi khởi động.</p>
          <div class="form-row">
            <label class="label" for="ob-url">Địa chỉ máy chủ</label>
            <input id="ob-url" class="input" type="url" inputmode="url" placeholder="192.168.1.10:8765" autocomplete="url" autocapitalize="off" spellcheck="false" value="${saved?.url || ''}" aria-describedby="ob-url-hint" />
            <p id="ob-url-hint" class="hint">Ví dụ: 192.168.1.10:8765</p>
          </div>
          <div class="form-row">
            <label class="label" for="ob-key">Mã truy cập <span class="muted">(nếu máy chủ yêu cầu)</span></label>
            <input id="ob-key" class="input" type="password" autocomplete="off" autocapitalize="off" spellcheck="false" />
          </div>
          <p class="form-status" role="status" aria-live="polite" hidden></p>
          <button type="submit" class="btn btn-primary btn-lg">${icon('server')}<span>Kết nối</span></button>
        </form>
        <form class="panel" id="ob-github" novalidate>
          <h2 class="panel-title">${icon('cloud')}<span>Kho truyện trên GitHub</span></h2>
          <p class="panel-text">Dùng khi truyện được lưu trong các kho GitHub của bạn. Ứng dụng đọc thẳng từ GitHub, không cần máy chủ.</p>
          <div class="form-row">
            <label class="label" for="ob-token">Mã truy cập GitHub</label>
            <input id="ob-token" class="input" type="password" placeholder="github_pat_…" autocomplete="off" autocapitalize="off" spellcheck="false" aria-describedby="ob-token-hint" />
            <p id="ob-token-hint" class="hint">Tạo mã chỉ có quyền đọc nội dung kho truyện. Mã chỉ được lưu trên thiết bị này và chỉ gửi tới GitHub.</p>
          </div>
          <p class="form-status" role="status" aria-live="polite" hidden></p>
          <button type="submit" class="btn btn-primary btn-lg">${icon('cloud')}<span>Dùng mã này</span></button>
        </form>
      </div>
    </div>`,
  );
  el.querySelector<HTMLFormElement>('#ob-server')?.addEventListener('submit', (e) => {
    e.preventDefault();
    void connectServer(e.currentTarget as HTMLFormElement);
  });
  el.querySelector<HTMLFormElement>('#ob-github')?.addEventListener('submit', (e) => {
    e.preventDefault();
    void connectGitHub(e.currentTarget as HTMLFormElement);
  });
}

export function unmount(): void {
  busy = false;
}
