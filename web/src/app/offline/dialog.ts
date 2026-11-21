/**
 * "Tải về để đọc offline": pick a chapter range of a story, follow the download, pause / resume / cancel it and
 * remove what is stored. The job belongs to the offline module, so closing the dialog does not stop it and
 * opening it again shows the running job.
 */
import type { ChapterRef } from '../core/contracts';
import { fmtBytes, fmtNum } from '../core/format';
import { html, render } from '../core/html';
import { icon } from '../core/icons';
import { progress as readingProgress } from '../core/progress';
import { confirmDialog, openDialog, toast, type DialogHandle } from '../core/ui';
import { clampRange, offline, type DownloadJob } from './index';

export interface DownloadDialogOptions {
  source: string;
  key: string;
  name: string;
  chapters: ChapterRef[];
}

let open: DialogHandle | null = null;

/** Opens the download dialog of a story (one at a time). */
export function openDownloadDialog(o: DownloadDialogOptions): DialogHandle | null {
  if (open && !open.closed) open.close();
  if (!offline.isAvailable()) {
    toast({ message: 'Thiết bị này chưa hỗ trợ lưu truyện để đọc khi không có mạng.', kind: 'error' });
    return null;
  }
  const count = o.chapters.length;
  const p = readingProgress.get(o.source, o.key);
  const cur = p ? readingProgress.resolveIdx(p, o.chapters) : -1;
  let off: (() => void) | null = null;

  const d = openDialog({
    title: 'Tải về để đọc offline',
    variant: 'sheet',
    className: 'st-dl',
    initialFocus: '#st-dl-from',
    onClose: () => {
      off?.();
      open = null;
    },
    body: html`<p class="dialog-text st-dl-name"><strong>${o.name}</strong> · ${fmtNum(count)} chương</p>
      <p class="st-dl-have" id="st-dl-have" role="status"></p>
      <div class="st-dl-range">
        <label class="field"
          ><span class="label">Từ chương</span>
          <input id="st-dl-from" class="input" type="number" inputmode="numeric" min="1" max="${count}" step="1" value="1" />
        </label>
        <label class="field"
          ><span class="label">Đến chương</span>
          <input id="st-dl-to" class="input" type="number" inputmode="numeric" min="1" max="${count}" step="1" value="${count}" />
        </label>
      </div>
      <div class="chips st-dl-quick" role="group" aria-label="Chọn nhanh">
        <button type="button" class="chip" data-quick="all">Tất cả</button>
        ${cur >= 0 ? html`<button type="button" class="chip" data-quick="cur">Từ chương đang đọc</button>` : ''}
        ${count > 50 ? html`<button type="button" class="chip" data-quick="next50">50 chương tiếp</button>` : ''}
        ${count > 200 ? html`<button type="button" class="chip" data-quick="next200">200 chương tiếp</button>` : ''}
      </div>
      <div class="st-dl-prog" id="st-dl-prog" hidden>
        <progress id="st-dl-bar" class="st-progress" max="100" value="0" aria-label="Tiến độ tải về"></progress>
        <p class="st-dl-status" id="st-dl-status" role="status" aria-live="polite"></p>
      </div>
      <p class="hint" id="st-dl-usage"></p>`,
    footer: html`<button type="button" class="btn btn-danger-ghost st-dl-remove" data-act="remove" hidden>${icon('trash')}<span>Xoá bản đã tải</span></button>
      <button type="button" class="btn" data-act="cancel" hidden>Huỷ</button>
      <button type="button" class="btn" data-act="pause" hidden>${icon('pause')}<span>Tạm dừng</span></button>
      <button type="button" class="btn btn-primary" data-act="resume" hidden>${icon('play')}<span>Tiếp tục</span></button>
      <button type="button" class="btn btn-primary" data-act="start">${icon('download')}<span>Tải về</span></button>`,
  });
  open = d;

  const q = <T extends HTMLElement>(sel: string): T => d.el.querySelector<T>(sel) as T;
  const from = q<HTMLInputElement>('#st-dl-from');
  const to = q<HTMLInputElement>('#st-dl-to');
  const bar = q<HTMLProgressElement>('#st-dl-bar');
  const status = q<HTMLElement>('#st-dl-status');
  const btn = (act: string): HTMLButtonElement => q<HTMLButtonElement>(`[data-act="${act}"]`);
  let have = 0;

  const range = (): { from: number; to: number } => clampRange(count, (Number(from.value) || 1) - 1, (Number(to.value) || count) - 1);
  const setRange = (a: number, b: number): void => {
    const r = clampRange(count, a, b);
    from.value = String(r.from + 1);
    to.value = String(r.to + 1);
  };

  async function refreshHave(): Promise<void> {
    have = (await offline.storyStatus(o.source, o.key)).chapters;
    if (d.closed) return;
    q('#st-dl-have').textContent = have >= count && count > 0 ? 'Đã tải đủ truyện này về máy.' : have > 0 ? `Đã có ${fmtNum(have)} / ${fmtNum(count)} chương trên máy.` : 'Chưa có chương nào trên máy.';
    const u = await offline.usage();
    if (d.closed) return;
    q('#st-dl-usage').textContent = u.quota ? `Bộ nhớ ứng dụng: đã dùng ${fmtBytes(u.used)} trên ${fmtBytes(u.quota)}.` : '';
    paint(offline.job(o.source, o.key));
  }

  function paint(job: DownloadJob | null): void {
    if (d.closed) return;
    const active = !!job && (job.state === 'running' || job.state === 'paused');
    btn('start').hidden = active;
    btn('pause').hidden = !job || job.state !== 'running';
    btn('resume').hidden = !job || job.state !== 'paused';
    btn('cancel').hidden = !active;
    btn('remove').hidden = active || have === 0;
    from.disabled = to.disabled = active;
    for (const c of d.el.querySelectorAll<HTMLButtonElement>('[data-quick]')) c.disabled = active;
    if (!job) return;
    q('#st-dl-prog').hidden = false;
    const pr = job.progress;
    const pct = pr.total ? Math.floor((pr.done / pr.total) * 100) : 0;
    bar.value = pct;
    const ok = pr.done - pr.failed;
    const why = pr.lastError ? ` (${pr.lastError})` : '';
    const fail = pr.failed ? ` · ${fmtNum(pr.failed)} chương lỗi${why}` : '';
    if (job.state === 'running') status.textContent = `Đang tải ${fmtNum(pr.done)} / ${fmtNum(pr.total)} chương (${pct}%)${fail}`;
    else if (job.state === 'paused') status.textContent = `Đã tạm dừng ở ${fmtNum(pr.done)} / ${fmtNum(pr.total)} chương${fail}`;
    else if (job.state === 'cancelled') status.textContent = `Đã huỷ. Đã lưu ${fmtNum(ok)} chương.`;
    else status.textContent = pr.failed ? `Đã lưu ${fmtNum(ok)} chương, ${fmtNum(pr.failed)} chương lỗi${why}. Bấm Tải về để thử lại.` : `Đã tải xong ${fmtNum(ok)} chương.`;
  }

  function follow(job: DownloadJob): void {
    off?.();
    off = job.onChange(paint);
    paint(job);
    void job.finished.then((pr) => {
      if (job.state === 'done' && !pr.failed && pr.total) toast({ message: `Đã tải ${fmtNum(pr.total)} chương để đọc khi không có mạng.`, kind: 'ok' });
      if (!d.closed) void refreshHave().then(() => paint(job));
    });
  }

  d.el.addEventListener('click', (e) => {
    const t = (e.target as Element).closest<HTMLElement>('[data-act],[data-quick]');
    if (!t) return;
    const quick = t.dataset.quick;
    if (quick) {
      const base = Math.max(0, cur);
      if (quick === 'all') setRange(0, count - 1);
      else if (quick === 'cur') setRange(base, count - 1);
      else if (quick === 'next50') setRange(base, base + 49);
      else if (quick === 'next200') setRange(base, base + 199);
      return;
    }
    const job = offline.job(o.source, o.key);
    switch (t.dataset.act) {
      case 'start': {
        const r = range();
        setRange(r.from, r.to);
        follow(offline.startJob(o.source, o.key, { chapters: o.chapters, name: o.name, total: count, from: r.from, to: r.to }));
        btn('pause').focus();
        break;
      }
      case 'pause':
        job?.pause();
        btn('resume').focus();
        break;
      case 'resume':
        job?.resume();
        btn('pause').focus();
        break;
      case 'cancel':
        job?.cancel();
        btn('start').focus();
        break;
      case 'remove':
        void (async () => {
          const ok = await confirmDialog({ title: 'Xoá bản đã tải?', message: `Xoá ${fmtNum(have)} chương của “${o.name}” khỏi máy. Lịch sử đọc và đánh dấu được giữ nguyên.`, confirmLabel: 'Xoá', danger: true });
          if (!ok) return;
          await offline.removeStory(o.source, o.key);
          toast('Đã xoá bản tải về.');
          if (!d.closed) {
            render(status, html``);
            q('#st-dl-prog').hidden = true;
            await refreshHave();
          }
        })();
        break;
    }
  });

  if (cur >= 0) setRange(cur, count - 1);
  const running = offline.job(o.source, o.key);
  if (running) follow(running);
  void refreshHave();
  return d;
}
