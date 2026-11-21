/**
 * Small always-on-top controller (Document Picture-in-Picture, Chromium): previous / play-pause / next and
 * the sentence being read. Hidden where the browser has no such API.
 */
import type { Player } from './index';
import { onMark } from './mark';

type DocPip = { requestWindow(o?: { width?: number; height?: number }): Promise<Window> };

let p: Player | null = null;
let win: Window | null = null;
let opening = false;
let offs: Array<() => void> = [];

const api = (): DocPip | null => (typeof window !== 'undefined' ? ((window as unknown as { documentPictureInPicture?: DocPip }).documentPictureInPicture ?? null) : null);

export const isPipSupported = (): boolean => typeof api()?.requestWindow === 'function';

function release(): void {
  for (const f of offs) f();
  offs = [];
}

export function closePip(): void {
  const w = win;
  win = null;
  release();
  try {
    w?.close();
  } catch {
    // already gone
  }
}

export function initPip(player: Player): void {
  p = player;
  player.onState((s) => {
    if (s.status === 'idle') closePip();
  });
  if (typeof window !== 'undefined') window.addEventListener('pagehide', closePip);
}

function sentence(): string {
  const n = p?.getNowReading();
  if (!n) return p?.getState().chapterTitle || '';
  const t = n.para < 0 ? n.title : (n.paragraphs[n.para] ?? '');
  return (n.e > n.s ? t.slice(n.s, n.e) : t).trim();
}

export async function openPip(): Promise<void> {
  const d = api();
  if (!d || !p || win || opening) return;
  const player = p;
  let w: Window;
  opening = true;
  try {
    w = await d.requestWindow({ width: 360, height: 220 });
  } catch {
    return;
  } finally {
    opening = false;
  }
  if (player.getState().status === 'idle' || win) {
    try {
      w.close();
    } catch {
      // already gone
    }
    return;
  }
  win = w;
  const doc = w.document;
  for (const sheet of Array.from(document.styleSheets)) {
    try {
      const st = doc.createElement('style');
      st.textContent = Array.from(sheet.cssRules)
        .map((r) => r.cssText)
        .join('\n');
      doc.head.append(st);
    } catch {
      if (sheet.href) {
        const l = doc.createElement('link');
        l.rel = 'stylesheet';
        l.href = sheet.href;
        doc.head.append(l);
      }
    }
  }
  doc.documentElement.className = document.documentElement.className;
  doc.documentElement.lang = 'vi';
  doc.body.style.cssText = 'margin:0;padding:12px;display:grid;gap:10px;grid-template-rows:auto 1fr auto;height:100vh;box-sizing:border-box;background:var(--bg,#fff);color:var(--text,#111)';
  const title = doc.createElement('div');
  title.style.cssText = 'font-weight:600;font-size:.85rem;opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis';
  const line = doc.createElement('div');
  line.style.cssText = 'overflow:auto;font-size:1rem;line-height:1.5';
  const bar = doc.createElement('div');
  bar.style.cssText = 'display:flex;justify-content:center;gap:12px';
  const btn = (label: string, fn: () => void): HTMLButtonElement => {
    const b = doc.createElement('button');
    b.type = 'button';
    b.className = 'btn';
    b.textContent = label;
    b.addEventListener('click', fn);
    return b;
  };
  const idx = (): number => player.getState().idx ?? 0;
  const play = btn('', () => player.toggle());
  bar.append(btn('« Chương trước', () => player.gotoChapter(idx() - 1)), play, btn('Chương sau »', () => player.gotoChapter(idx() + 1)));
  doc.body.append(title, line, bar);
  const sync = (): void => {
    const st = player.getState();
    const t = [st.storyName, st.chapterTitle].filter(Boolean).join(' · ');
    if (title.textContent !== t) title.textContent = t;
    const s = sentence();
    if (line.textContent !== s) line.textContent = s;
    play.textContent = st.status === 'playing' || st.status === 'loading' ? 'Tạm dừng' : 'Nghe tiếp';
  };
  offs = [player.onChange(sync), onMark(sync)];
  sync();
  w.addEventListener('pagehide', () => {
    if (win === w) {
      win = null;
      release();
    }
  });
}

export function togglePip(): void {
  if (win) closePip();
  else void openPip();
}
