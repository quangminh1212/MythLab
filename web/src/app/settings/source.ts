/**
 * "Nguồn dữ liệu" tab: which source the app reads from (server or GitHub), credentials, storage and caches,
 * export / import of the reader's data and the app itself (install, update).
 *
 * Secrets (server key, GitHub token) are never written into the DOM: their inputs start empty, a stored secret is
 * only announced ("Đã lưu") and can be replaced or forgotten. What the user types lives in the input only.
 */
import { backend } from '../core/backend/index';
import { peekToken, protectionHint } from '../core/secret';
import { on } from '../core/events';
import { fmtBytes, fmtNum } from '../core/format';
import { html, render } from '../core/html';
import { icon } from '../core/icons';
import { data } from '../core/data';
import { href } from '../core/router';
import { confirmDialog, toast } from '../core/ui';
import { offline, type DownloadedStory } from '../offline/index';
import { applyBackup, backupFileName, buildBackup, parseBackup, BackupError, type Backup } from './backup';

const GH_TOKEN_URL = 'https://github.com/settings/personal-access-tokens/new';

export function sourceStatusText(kind: string, base: string | null): string {
  if (kind === 'server') return base ? `Đang dùng: máy chủ MythLab tại ${base.replace(/^https?:\/\//, '')}` : 'Đang dùng: máy chủ MythLab của trang này';
  if (kind === 'github') return 'Đang dùng: GitHub (đọc trực tiếp)';
  return 'Chưa có nguồn truyện nào';
}

/** Adds http:// to an address typed without a scheme and drops trailing slashes; '' when it cannot be a URL. */
export function normaliseServerUrl(raw: string): string {
  let v = raw.trim();
  if (!v) return '';
  if (!/^https?:\/\//i.test(v)) v = 'http://' + v;
  try {
    const u = new URL(v);
    return u.origin + u.pathname.replace(/\/+$/, '');
  } catch {
    return '';
  }
}

const secretField = (id: string, label: string, placeholder: string): ReturnType<typeof html> => html`<div class="ss-secret">
  <input id="${id}" class="input" type="password" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="${placeholder}" aria-label="${label}" />
  <button type="button" class="btn btn-sm" data-reveal="${id}" aria-pressed="false" aria-label="Hiện ${label}">Hiện</button>
</div>`;

export function mountSource(el: HTMLElement): () => void {
  render(
    el,
    html`<section class="ss-sec" aria-labelledby="ss-h-src">
        <h3 class="ss-h" id="ss-h-src">Nguồn truyện</h3>
        <p class="ss-status" id="ss-src-status" role="status"></p>

        <div class="ss-row">
          <label class="ss-label" for="ss-srv-url">Máy chủ MythLab (địa chỉ)</label>
          <input id="ss-srv-url" class="input" type="url" inputmode="url" autocomplete="off" spellcheck="false" placeholder="http://192.168.1.10:8765" />
        </div>
        <div class="ss-row">
          <label class="ss-label" for="ss-srv-key">Khoá máy chủ</label>
          ${secretField('ss-srv-key', 'khoá máy chủ', 'Để trống nếu máy chủ không đặt khoá')}
          <p class="hint" id="ss-srv-saved" hidden>Đã lưu một khoá trên thiết bị này. Nhập khoá mới để thay.</p>
        </div>
        <div class="ss-actions">
          <button type="button" class="btn" id="ss-srv-test">Kiểm tra</button>
          <button type="button" class="btn btn-primary" id="ss-srv-save">Lưu và dùng</button>
        </div>
        <p class="form-status" id="ss-srv-msg" role="status" aria-live="polite" hidden></p>

        <div class="ss-row">
          <label class="ss-label" for="ss-gh-tok">GitHub token (đọc trực tiếp, chỉ đọc)</label>
          ${secretField('ss-gh-tok', 'GitHub token', 'github_pat_…')}
          <p class="hint" id="ss-gh-saved" hidden>Đã lưu một token trên thiết bị này. Nhập token mới để thay.</p>
          <p class="hint" id="ss-gh-prot"></p>
          <p class="hint">Tạo token chi tiết với quyền <em>Contents</em> và <em>Metadata</em> chỉ đọc. <a href="${GH_TOKEN_URL}" target="_blank" rel="noopener noreferrer">Mở trang tạo token</a></p>
        </div>
        <div class="ss-actions">
          <button type="button" class="btn" id="ss-gh-test">Kiểm tra</button>
          <button type="button" class="btn btn-primary" id="ss-gh-save">Lưu và dùng</button>
        </div>
        <p class="form-status" id="ss-gh-msg" role="status" aria-live="polite" hidden></p>

        <div class="ss-actions">
          <button type="button" class="btn btn-danger-ghost" id="ss-forget">${icon('close')}<span>Đăng xuất: quên máy chủ và token</span></button>
        </div>
      </section>

      <section class="ss-sec" aria-labelledby="ss-h-store">
        <h3 class="ss-h" id="ss-h-store">Lưu trữ và bộ nhớ đệm</h3>
        <p class="ss-status" id="ss-usage" role="status"></p>
        <ul class="ss-layers" id="ss-layers" aria-label="Dung lượng từng loại dữ liệu"></ul>
        <div class="ss-actions">
          <button type="button" class="btn" id="ss-clear">${icon('trash')}<span>Xoá bộ nhớ đệm</span></button>
          <button type="button" class="btn btn-danger-ghost" id="ss-clear-all">Xoá cả truyện đã tải</button>
        </div>
        <p class="hint">“Xoá bộ nhớ đệm” dọn ảnh bìa, âm thanh, danh sách và chương đã đọc; truyện bạn đã tải về được giữ lại. Cài đặt, lịch sử và đánh dấu không bị ảnh hưởng.</p>
        <h4 class="ss-h2" id="ss-h-dl">Truyện đã tải về</h4>
        <ul class="ss-downloads" id="ss-downloads" aria-labelledby="ss-h-dl"></ul>
      </section>

      <section class="ss-sec" aria-labelledby="ss-h-backup">
        <h3 class="ss-h" id="ss-h-backup">Sao lưu dữ liệu</h3>
        <p class="hint">Gồm cài đặt, tiến độ đọc, đánh dấu và truyện theo dõi, lưu thành một tệp JSON.</p>
        <div class="ss-check ss-row">
          <input id="ss-exp-secrets" type="checkbox" />
          <label for="ss-exp-secrets"><span>Kèm khoá máy chủ và GitHub token</span><small class="hint">Chỉ tick khi tệp được cất ở nơi an toàn: ai có tệp sẽ dùng được các khoá này.</small></label>
        </div>
        <div class="ss-actions">
          <button type="button" class="btn" id="ss-export">${icon('download')}<span>Xuất ra tệp</span></button>
          <label class="btn" for="ss-import-file" id="ss-import-btn" tabindex="-1">Nhập từ tệp…</label>
          <input id="ss-import-file" class="sr-only" type="file" accept="application/json,.json" />
        </div>
        <div class="ss-import" id="ss-import" hidden></div>
      </section>

      <section class="ss-sec" aria-labelledby="ss-h-app">
        <h3 class="ss-h" id="ss-h-app">Ứng dụng</h3>
        <p class="ss-status" id="ss-app-status" role="status"></p>
        <div class="ss-actions">
          <button type="button" class="btn" id="ss-install" hidden>${icon('download')}<span>Cài MythLab như ứng dụng</span></button>
          <button type="button" class="btn" id="ss-update">${icon('refresh')}<span>Kiểm tra bản mới</span></button>
        </div>
      </section>`,
  );

  const $ = <T extends HTMLElement>(sel: string): T => el.querySelector<T>(sel) as T;
  const offs: (() => void)[] = [];
  let alive = true;

  const say = (box: HTMLElement, text: string, kind: 'ok' | 'error' | 'info' = 'info'): void => {
    box.hidden = !text;
    box.textContent = text;
    box.classList.toggle('is-error', kind === 'error');
    box.classList.toggle('is-ok', kind === 'ok');
  };

  // ------------------------------------------------------------ status and stored-secret hints

  function status(): void {
    $('#ss-src-status').textContent = sourceStatusText(backend.kind, backend.serverBase);
    const cfg = backend.serverConfig();
    const url = $<HTMLInputElement>('#ss-srv-url');
    if (document.activeElement !== url && !url.value) url.value = cfg?.url ?? '';
    $('#ss-srv-saved').hidden = !cfg?.key;
    const tok = peekToken();
    $('#ss-gh-saved').hidden = !tok;
    $('#ss-gh-prot').textContent = protectionHint();
    $('#ss-forget').hidden = !cfg && !tok;
  }
  status();
  offs.push(on('backend', status));

  el.addEventListener('click', (e) => {
    const b = (e.target as Element).closest<HTMLElement>('[data-reveal]');
    if (!b) return;
    const input = $<HTMLInputElement>('#' + (b.dataset.reveal as string));
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    b.textContent = show ? 'Ẩn' : 'Hiện';
    b.setAttribute('aria-pressed', String(show));
  });

  // ------------------------------------------------------------ server

  const srvMsg = $('#ss-srv-msg');
  async function checkServer(): Promise<{ url: string; key: string } | null> {
    const url = normaliseServerUrl($<HTMLInputElement>('#ss-srv-url').value);
    if (!url) {
      say(srvMsg, 'Nhập địa chỉ máy chủ, ví dụ http://192.168.1.10:8765', 'error');
      return null;
    }
    const cfg = backend.serverConfig();
    const typed = $<HTMLInputElement>('#ss-srv-key').value;
    // an empty key field keeps the stored key when the address is the stored one
    const key = typed || (cfg && cfg.url.replace(/\/+$/, '') === url ? (cfg.key ?? '') : '');
    say(srvMsg, 'Đang kiểm tra…');
    const r = await backend.testServer(url, key);
    if (!alive) return null;
    if (r === 'ok') {
      say(srvMsg, '✓ Kết nối được máy chủ MythLab', 'ok');
      return { url, key };
    }
    say(srvMsg, r === 'auth' ? '✗ Máy chủ yêu cầu khoá hoặc khoá chưa đúng' : '✗ Không kết nối được tới máy chủ. Kiểm tra địa chỉ và mạng.', 'error');
    return null;
  }
  $('#ss-srv-test').addEventListener('click', () => void checkServer());
  $('#ss-srv-save').addEventListener('click', () => {
    void (async () => {
      const ok = await checkServer();
      if (!ok) return;
      await backend.useServer(ok.url, ok.key);
      data.invalidate();
      $<HTMLInputElement>('#ss-srv-key').value = '';
      status();
      toast({ message: 'Đã lưu và chuyển sang máy chủ này.', kind: 'ok' });
    })();
  });

  // ------------------------------------------------------------ GitHub

  const ghMsg = $('#ss-gh-msg');
  async function checkToken(): Promise<string | null> {
    const token = $<HTMLInputElement>('#ss-gh-tok').value.trim() || peekToken();
    if (!token) {
      say(ghMsg, 'Nhập token trước.', 'error');
      return null;
    }
    say(ghMsg, 'Đang kiểm tra…');
    const r = await backend.testToken(token);
    if (!alive) return null;
    if (!r.ok) {
      say(ghMsg, `✗ ${r.error || 'Token không dùng được'}`, 'error');
      return null;
    }
    const rate = r.rateRemaining != null ? ` · còn ${fmtNum(r.rateRemaining)} lượt gọi API` : '';
    say(ghMsg, `✓ ${r.login ?? 'Token hợp lệ'} · ${fmtNum(r.repos)} kho truyện${rate}`, 'ok');
    return token;
  }
  $('#ss-gh-test').addEventListener('click', () => void checkToken());
  $('#ss-gh-save').addEventListener('click', () => {
    void (async () => {
      const token = await checkToken();
      if (!token) return;
      await backend.useToken(token);
      data.invalidate();
      $<HTMLInputElement>('#ss-gh-tok').value = '';
      status();
      toast({ message: 'Đã lưu token GitHub.', kind: 'ok' });
    })();
  });

  $('#ss-forget').addEventListener('click', () => {
    void (async () => {
      const ok = await confirmDialog({
        title: 'Đăng xuất khỏi nguồn truyện?',
        message: 'Ứng dụng quên địa chỉ máy chủ, khoá và token đã lưu trên thiết bị này. Lịch sử đọc, đánh dấu và truyện đã tải về được giữ nguyên.',
        confirmLabel: 'Đăng xuất',
        cancelLabel: 'Giữ nguyên',
        danger: true,
      });
      if (!ok) return;
      $<HTMLInputElement>('#ss-srv-url').value = '';
      $<HTMLInputElement>('#ss-srv-key').value = '';
      $<HTMLInputElement>('#ss-gh-tok').value = '';
      await backend.forget('all');
      data.invalidate();
      say(srvMsg, '');
      say(ghMsg, '');
      status();
      toast('Đã đăng xuất khỏi nguồn truyện.');
    })();
  });

  // ------------------------------------------------------------ storage

  let paintSeq = 0;
  async function paintStorage(): Promise<void> {
    const mine = ++paintSeq;
    const [layers, usage, list] = await Promise.all([offline.layers(), offline.usage(), offline.list()]);
    if (!alive || mine !== paintSeq) return;
    $('#ss-usage').textContent = usage.quota ? `Đã dùng ${fmtBytes(usage.used)} trên ${fmtBytes(usage.quota)} dung lượng cho phép.` : 'Trình duyệt không báo dung lượng đã dùng.';
    render(
      $('#ss-layers'),
      html`${layers.map((l) => html`<li><span>${l.label}</span><span class="ss-size-v">${l.entries ? `${fmtNum(l.entries)} mục · ` : ''}${fmtBytes(l.bytes)}</span></li>`)}`,
    );
    render(
      $('#ss-downloads'),
      list.length
        ? html`${list.map((s: DownloadedStory) => downloadItem(s))}`
        : html`<li class="ss-empty">Chưa tải truyện nào. Mở một truyện và bấm “Tải về” để đọc khi không có mạng.</li>`,
    );
  }
  const downloadItem = (s: DownloadedStory): ReturnType<typeof html> =>
    html`<li>
      <a class="ss-dl-name" href="${href.story(s.source, s.key)}" data-close>${s.name}</a>
      <span class="ss-size-v">${fmtNum(s.chapters)}${s.total ? ` / ${fmtNum(s.total)}` : ''} chương · ${fmtBytes(s.bytes)}</span>
      <button type="button" class="btn btn-sm btn-danger-ghost" data-rm-source="${s.source}" data-rm-key="${s.key}" aria-label="Xoá bản đã tải của ${s.name}">${icon('trash')}</button>
    </li>`;
  void paintStorage();
  offs.push(offline.onChange(() => void paintStorage()));

  $('#ss-downloads').addEventListener('click', (e) => {
    const b = (e.target as Element).closest<HTMLElement>('[data-rm-source]');
    if (!b) return;
    void (async () => {
      const ok = await confirmDialog({ title: 'Xoá bản đã tải?', message: 'Các chương đã tải của truyện này sẽ bị xoá khỏi máy. Lịch sử đọc được giữ nguyên.', confirmLabel: 'Xoá', danger: true });
      if (!ok) return;
      await offline.removeStory(b.dataset.rmSource as string, b.dataset.rmKey as string);
      toast('Đã xoá bản tải về.');
    })();
  });

  async function clearCaches(keepDownloads: boolean): Promise<void> {
    const ok = await confirmDialog({
      title: keepDownloads ? 'Xoá bộ nhớ đệm?' : 'Xoá cả truyện đã tải?',
      message: keepDownloads ? 'Ảnh bìa, âm thanh, danh sách truyện và chương đã đọc gần đây sẽ được tải lại khi cần.' : 'Toàn bộ bộ nhớ đệm và mọi truyện đã tải về sẽ bị xoá. Bạn sẽ cần mạng để đọc lại.',
      confirmLabel: 'Xoá',
      cancelLabel: 'Giữ nguyên',
      danger: !keepDownloads,
    });
    if (!ok) return;
    const freed = await offline.clearAll({ keepDownloads });
    toast({ message: freed ? `Đã xoá bộ nhớ đệm, giải phóng ${fmtBytes(freed)}.` : 'Đã xoá bộ nhớ đệm.', kind: 'ok' });
    void paintStorage();
  }
  $('#ss-clear').addEventListener('click', () => void clearCaches(true));
  $('#ss-clear-all').addEventListener('click', () => void clearCaches(false));

  // ------------------------------------------------------------ export / import

  $('#ss-export').addEventListener('click', () => {
    const b = buildBackup({ includeSecrets: $<HTMLInputElement>('#ss-exp-secrets').checked });
    const blob = new Blob([JSON.stringify(b, null, 1)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = backupFileName();
    a.rel = 'noopener';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10_000);
    toast({ message: `Đã xuất ${fmtNum(Object.keys(b.progress).length)} truyện đang đọc, ${fmtNum(b.bookmarks.length)} đánh dấu.`, kind: 'ok' });
  });

  const impBox = $('#ss-import');
  const fileIn = $<HTMLInputElement>('#ss-import-file');
  function showImport(b: Backup): void {
    impBox.hidden = false;
    render(
      impBox,
      html`<p class="ss-status">Tệp có ${fmtNum(Object.keys(b.progress).length)} truyện đang đọc, ${fmtNum(b.bookmarks.length)} đánh dấu, ${fmtNum(b.follows.length)} truyện theo dõi và ${fmtNum(Object.keys(b.settings).length)} cài đặt.</p>
        <div class="ss-row" role="radiogroup" aria-label="Cách nhập">
          <label class="ss-radio"><input type="radio" name="ss-imp-mode" value="merge" checked /><span>Gộp với dữ liệu trên máy (giữ bản mới hơn)</span></label>
          <label class="ss-radio"><input type="radio" name="ss-imp-mode" value="replace" /><span>Thay thế hoàn toàn dữ liệu trên máy</span></label>
        </div>
        ${b.secrets ? html`<div class="ss-check ss-row"><input id="ss-imp-secrets" type="checkbox" /><label for="ss-imp-secrets"><span>Khôi phục cả khoá máy chủ và GitHub token trong tệp</span></label></div>` : ''}
        <div class="ss-actions"><button type="button" class="btn btn-primary" data-imp="go">Nhập dữ liệu</button><button type="button" class="btn" data-imp="no">Bỏ qua</button></div>`,
    );
    pending = b;
  }
  let pending: Backup | null = null;
  fileIn.addEventListener('change', () => {
    const f = fileIn.files?.[0];
    fileIn.value = '';
    if (!f) return;
    void (async () => {
      try {
        showImport(parseBackup(await f.text()));
      } catch (e) {
        impBox.hidden = false;
        render(impBox, html`<p class="form-status is-error" role="alert">${e instanceof BackupError ? e.message : 'Không đọc được tệp này.'}</p>`);
        pending = null;
      }
    })();
  });
  impBox.addEventListener('click', (e) => {
    const t = (e.target as Element).closest<HTMLElement>('[data-imp]');
    if (!t) return;
    const b = pending;
    pending = null;
    impBox.hidden = true;
    if (t.dataset.imp !== 'go' || !b) return;
    try {
      const mode = (impBox.querySelector<HTMLInputElement>('input[name="ss-imp-mode"]:checked')?.value ?? 'merge') as 'merge' | 'replace';
      const withSecrets = !!impBox.querySelector<HTMLInputElement>('#ss-imp-secrets')?.checked;
      const r = applyBackup(b, { mode, includeSecrets: withSecrets });
      toast({ message: `Đã nhập ${fmtNum(r.progress)} truyện đang đọc, ${fmtNum(r.bookmarks)} đánh dấu, ${fmtNum(r.follows)} truyện theo dõi.`, kind: 'ok' });
      if (r.secrets) void backend.reinit().then(() => data.invalidate());
      status();
    } catch (err) {
      toast({ message: err instanceof BackupError ? err.message : 'Không nhập được dữ liệu.', kind: 'error' });
    }
  });

  // ------------------------------------------------------------ the app itself

  const install = $<HTMLButtonElement>('#ss-install');
  const appStatus = $('#ss-app-status');
  void import('../pwa').then(({ pwa }) => {
    if (!alive) return;
    const paint = async (): Promise<void> => {
      install.hidden = !pwa.installAvailable() || pwa.standalone();
      const v = await pwa.version();
      if (!alive) return;
      const parts = [pwa.standalone() ? 'Đang chạy như ứng dụng đã cài.' : '', v ? `Bản ${v.version}, ${fmtNum(v.files.length)} tệp lưu sẵn để mở khi không có mạng.` : pwa.controlled() ? '' : 'Chưa lưu ứng dụng để mở khi không có mạng (cần tải lại trang một lần).', pwa.updateAvailable() ? 'Có bản mới đang chờ.' : ''];
      appStatus.textContent = parts.filter(Boolean).join(' ');
    };
    void paint();
    offs.push(pwa.onInstallChange(() => void paint()), pwa.onUpdateChange(() => void paint()));
    install.addEventListener('click', () => void pwa.install().then((ok) => ok && toast({ message: 'Đã cài MythLab.', kind: 'ok' })));
    $('#ss-update').addEventListener('click', () => {
      void (async () => {
        if (pwa.updateAvailable()) return pwa.applyUpdate();
        await pwa.checkForUpdate();
        await new Promise((r) => setTimeout(r, 1200));
        if (pwa.updateAvailable()) return;
        toast({ message: pwa.controlled() ? 'Bạn đang dùng bản mới nhất.' : 'Không có dịch vụ cập nhật trên thiết bị này.' });
      })();
    });
  });

  return () => {
    alive = false;
    for (const off of offs) off();
  };
}
