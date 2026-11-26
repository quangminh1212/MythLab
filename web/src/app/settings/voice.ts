/**
 * "Giọng đọc" tab: the engine picker and the voice list, driven by the pure helpers of voices.ts.
 *
 * The saved `engine` is never rewritten behind the user's back. When it cannot speak here (Piper without WebAssembly,
 * say) the tab shows the engine that will really be used, its voices, and why. Only Vietnamese voices are listed.
 */
import { html, render } from '../core/html';
import { S, set, type TtsEngine } from '../core/settings';
import { toast } from '../core/ui';
import { offerPiper } from '../player/engines';
import { onVoiceProgress, saveData, voiceProgress } from '../player/autovoice';
import { downloadBytes, megabytes, PIPER_SIZE_NOTE, piperChoice, piperInstalled, piperVoice, refreshPiper, removePiper } from '../player/piper';
import { effectiveEngine, engineChoices, listVoices, preview, readEnv, selectVoice, stopPreview, voiceKey, type VoiceItem } from './voices';

/** Wires the tab inside `root`. Returns the function that stops everything it started. */
export function mountVoice(root: HTMLElement): () => void {
  const engineRow = root.querySelector<HTMLElement>('#ss-engine-row') as HTMLElement;
  const engineBox = root.querySelector<HTMLElement>('#ss-engine') as HTMLElement;
  const engineNote = root.querySelector<HTMLElement>('#ss-engine-note') as HTMLElement;
  const select = root.querySelector<HTMLSelectElement>('#ss-voice') as HTMLSelectElement;
  const voiceNote = root.querySelector<HTMLElement>('#ss-voice-note') as HTMLElement;
  const test = root.querySelector<HTMLButtonElement>('#ss-voice-test') as HTMLButtonElement;
  const piperRow = root.querySelector<HTMLElement>('#ss-piper-row') as HTMLElement;
  const piperDl = root.querySelector<HTMLButtonElement>('#ss-piper-dl') as HTMLButtonElement;
  const piperRm = root.querySelector<HTMLButtonElement>('#ss-piper-rm') as HTMLButtonElement;
  const piperNote = root.querySelector<HTMLElement>('#ss-piper-note') as HTMLElement;
  let seq = 0;
  let shown: TtsEngine | null = null;
  let items: VoiceItem[] = [];

  async function refresh(): Promise<void> {
    const mine = ++seq;
    await refreshPiper();
    if (mine !== seq) return;
    const e = readEnv();
    const eff = effectiveEngine(S.engine, e);
    shown = eff;
    const choices = engineChoices(e);
    // one reader only (the plain web: Piper): no switch to show, just the voice list
    engineRow.hidden = choices.length < 2;
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
      voiceNote.textContent = 'Thiết bị này không chạy được giọng Piper (cần WebAssembly).';
      showPiper(null);
      return;
    }
    const sel = selectVoice(eff, items, S[voiceKey(eff)]);
    if (sel.store) set(voiceKey(eff), sel.store);
    const device = eff !== 'piper';
    const none = !items.length;
    render(select, html`${device ? html`<option value="">${none ? 'Chưa có giọng tiếng Việt' : 'Tự chọn giọng tiếng Việt của máy'}</option>` : ''}${items.map((v) => html`<option value="${v.id}">${v.label}</option>`)}`);
    select.value = sel.value;
    select.disabled = device && none;
    test.disabled = device && none;
    if (device && none) voiceNote.textContent = 'Máy chưa có giọng tiếng Việt: hãy cài thêm trong hệ điều hành, hoặc chọn bộ đọc Piper (offline).';
    else voiceNote.textContent = eff === 'piper' ? `Giọng Piper chạy trên máy (${piperChoice(S.piperVoice).model.note}).` : 'Giọng của thiết bị, đọc ngay trên máy.';
    showPiper(eff);
  }

  /** The download row of the on-device voice: size, download, delete. */
  function showPiper(eff: TtsEngine | null): void {
    piperRow.hidden = eff !== 'piper';
    if (eff !== 'piper') return;
    const v = piperVoice(S.piperVoice);
    const have = piperInstalled(v.id);
    piperDl.hidden = have;
    piperRm.hidden = !have;
    piperDl.textContent = `Tải giọng này (${megabytes(downloadBytes(v))})`;
    test.disabled = !have;
    const busy = voiceProgress();
    piperDl.disabled = busy >= 0 && !have;
    if (busy >= 0 && !have) {
      piperDl.textContent = `Đang tải… ${busy}%`;
    }
    const say = have
      ? `Đã lưu trên máy (${megabytes(downloadBytes(v))}). Đọc không cần mạng và không dùng máy chủ.`
      : `${PIPER_SIZE_NOTE} ${saveData() ? 'Đang bật tiết kiệm dữ liệu nên chưa tự tải: hãy nhấn “Tải giọng này”.' : 'Giọng được tự tải khi mở ứng dụng; chưa xong thì nhấn nghe sẽ chờ tải xong rồi đọc.'}`;
    piperNote.textContent = `${say} Nguồn giọng: ${v.credit}${v.kokoro ? '' : ' Phiên âm: espeak-ng (GPL-3.0).'} Chi tiết: THIRD_PARTY.md trong mã nguồn.`;
  }
  const onPiperDl = (): void => {
    piperDl.disabled = true;
    void offerPiper(S.piperVoice).finally(() => {
      piperDl.disabled = false;
      void refresh();
    });
  };
  const onPiperRm = (): void => {
    void removePiper(S.piperVoice).then(() => {
      toast('Đã xoá giọng Piper khỏi máy');
      void refresh();
    });
  };
  const onEngine = (e: Event): void => {
    const t = e.target as HTMLInputElement;
    if (t.name !== 'ss-engine' || !t.checked) return;
    stopPreview();
    set('engine', t.value);
    void refresh();
  };
  const onVoice = (): void => {
    if (!shown) return;
    stopPreview();
    set(voiceKey(shown), select.value);
    if (shown === 'piper') showPiper('piper');
  };
  const onTest = (): void => {
    if (!shown) return;
    const eng = shown;
    test.classList.add('is-busy');
    void preview(eng, S)
      .catch(() => toast({ message: 'Thiết bị không đọc thử được.', kind: 'error' }))
      .finally(() => test.classList.remove('is-busy'));
  };
  engineBox.addEventListener('change', onEngine);
  select.addEventListener('change', onVoice);
  test.addEventListener('click', onTest);
  piperDl.addEventListener('click', onPiperDl);
  piperRm.addEventListener('click', onPiperRm);
  // the automatic download of the voice reports here: show it, and show the result when it ends
  const offProgress = onVoiceProgress((p) => {
    if (p < 0) void refresh();
    else if (shown === 'piper' && !piperInstalled(piperVoice(S.piperVoice).id)) {
      piperDl.disabled = true;
      piperDl.textContent = `Đang tải… ${p}%`;
    }
  });
  void refresh();
  return () => {
    seq++;
    offProgress();
    stopPreview();
    engineBox.removeEventListener('change', onEngine);
    select.removeEventListener('change', onVoice);
    test.removeEventListener('click', onTest);
    piperDl.removeEventListener('click', onPiperDl);
    piperRm.removeEventListener('click', onPiperRm);
  };
}
