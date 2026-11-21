/**
 * "Giọng đọc" tab: the engine picker and the voice list, driven by the pure helpers of voices.ts.
 *
 * The saved `engine` is never rewritten behind the user's back. When it cannot speak here (Edge on a GitHub-direct
 * connection, say) the tab shows the engine that will really be used, its voices, and why.
 */
import { backend } from '../core/backend/index';
import { on } from '../core/events';
import { html, render } from '../core/html';
import { S, set, type TtsEngine } from '../core/settings';
import { toast } from '../core/ui';
import { effectiveEngine, engineChoices, listVoices, preview, readEnv, selectVoice, stopPreview, voiceKey, type EngineEnv, type VoiceItem } from './voices';

/** Wires the tab inside `root`. Returns the function that stops everything it started. */
export function mountVoice(root: HTMLElement): () => void {
  const engineBox = root.querySelector<HTMLElement>('#ss-engine') as HTMLElement;
  const engineNote = root.querySelector<HTMLElement>('#ss-engine-note') as HTMLElement;
  const select = root.querySelector<HTMLSelectElement>('#ss-voice') as HTMLSelectElement;
  const voiceNote = root.querySelector<HTMLElement>('#ss-voice-note') as HTMLElement;
  const test = root.querySelector<HTMLButtonElement>('#ss-voice-test') as HTMLButtonElement;
  let seq = 0;
  let env: EngineEnv | null = null;
  let shown: TtsEngine | null = null;
  let items: VoiceItem[] = [];

  async function refresh(): Promise<void> {
    const mine = ++seq;
    const e = await readEnv();
    if (mine !== seq) return;
    env = e;
    const eff = effectiveEngine(S.engine, e);
    shown = eff;
    const choices = engineChoices(e);
    render(
      engineBox,
      html`${choices.map(
        (c) =>
          html`<label class="ss-opt ${c.available ? '' : 'is-off'}"><input type="radio" name="ss-engine" value="${c.id}" ${c.id === eff ? html`checked` : ''} ${c.available ? '' : html`disabled`} /><span>${c.label}</span></label>`,
      )}`,
    );
    const saved = choices.find((c) => c.id === S.engine);
    engineNote.textContent = saved && !saved.available ? `${saved.reason ?? ''} Lựa chọn của bạn được giữ lại và sẽ dùng lại khi có thể.` : '';
    if (!eff) {
      items = [];
      fillVoices(null);
      return;
    }
    select.disabled = true;
    const list = await listVoices(eff);
    if (mine !== seq) return;
    items = list;
    fillVoices(eff);
  }

  function fillVoices(eff: TtsEngine | null): void {
    test.disabled = !eff;
    if (!eff) {
      render(select, html`<option value="">Chưa có bộ đọc nào dùng được</option>`);
      select.disabled = true;
      voiceNote.textContent = 'Thiết bị này không hỗ trợ đọc thành tiếng.';
      return;
    }
    const sel = selectVoice(eff, items, S[voiceKey(eff)]);
    if (sel.store) set(voiceKey(eff), sel.store);
    const device = eff !== 'edge';
    const none = !items.length;
    render(select, html`${device ? html`<option value="">Tự chọn giọng tiếng Việt của máy</option>` : ''}${none && !device ? html`<option value="">Không có giọng nào</option>` : ''}${items.map((v) => html`<option value="${v.id}">${v.label}</option>`)}`);
    select.value = sel.value;
    select.disabled = none && !device;
    test.disabled = none || (eff === 'edge' && backend.kind !== 'server');
    if (none && !device) voiceNote.textContent = 'Không lấy được danh sách giọng từ máy chủ. Hãy kiểm tra kết nối rồi mở lại tab này.';
    else if (device && !items.some((v) => v.vi)) voiceNote.textContent = 'Không có giọng tiếng Việt: hãy cài thêm trong hệ điều hành.';
    else voiceNote.textContent = eff === 'edge' ? 'Giọng Edge do máy chủ MythLab tạo ra.' : 'Giọng của thiết bị, đọc ngay trên máy.';
  }

  const onEngine = (e: Event): void => {
    const t = e.target as HTMLInputElement;
    if (t.name !== 'ss-engine' || !t.checked) return;
    stopPreview();
    if (t.value === 'edge' && env && !engineChoices(env).find((c) => c.id === 'edge')?.available) {
      toast('Giọng Edge cần máy chủ MythLab.');
      void refresh();
      return;
    }
    set('engine', t.value);
    void refresh();
  };
  const onVoice = (): void => {
    if (!shown) return;
    stopPreview();
    set(voiceKey(shown), select.value);
  };
  const onTest = (): void => {
    if (!shown) return;
    const eng = shown;
    test.classList.add('is-busy');
    void preview(eng, S)
      .catch(() => toast({ message: eng === 'edge' ? 'Không tạo được giọng Edge. Hãy kiểm tra kết nối tới máy chủ.' : 'Thiết bị không đọc thử được.', kind: 'error' }))
      .finally(() => test.classList.remove('is-busy'));
  };
  engineBox.addEventListener('change', onEngine);
  select.addEventListener('change', onVoice);
  test.addEventListener('click', onTest);
  const offBackend = on('backend', () => void refresh());
  void refresh();
  return () => {
    seq++;
    stopPreview();
    engineBox.removeEventListener('change', onEngine);
    select.removeEventListener('change', onVoice);
    test.removeEventListener('click', onTest);
    offBackend();
  };
}
