/** Inline SVG icons (24 px grid, stroke = currentColor). Constants only: safe to pass through raw(). */
import { raw, type SafeHtml } from './html';

const P: Record<string, string> = {
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  close: '<path d="M6 6l12 12M18 6 6 18"/>',
  home: '<path d="M4 11 12 4l8 7"/><path d="M6 10v10h12V10"/>',
  history: '<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/><path d="M12 8v4l3 2"/>',
  bookmark: '<path d="M7 4h10v16l-5-4-5 4z"/>',
  settings:
    '<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.3.9a7 7 0 0 0-2-1.2L14.2 3h-4l-.4 2.6a7 7 0 0 0-2 1.2l-2.3-.9-2 3.4 2 1.5a7 7 0 0 0 0 2.4l-2 1.5 2 3.4 2.3-.9a7 7 0 0 0 2 1.2l.4 2.6h4l.4-2.6a7 7 0 0 0 2-1.2l2.3.9 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z"/>',
  book: '<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h11"/>',
  right: '<path d="m9 6 6 6-6 6"/>',
  left: '<path d="m15 6-6 6 6 6"/>',
  down: '<path d="m6 9 6 6 6-6"/>',
  up: '<path d="m6 15 6-6 6 6"/>',
  play: '<path d="M8 5v14l11-7z" fill="currentColor"/>',
  pause: '<path d="M8 5v14M16 5v14"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="1.5" fill="currentColor"/>',
  headphones: '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/>',
  download: '<path d="M12 4v11"/><path d="m7 11 5 5 5-5"/><path d="M5 20h14"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  trash: '<path d="M4 7h16"/><path d="M9 7V4h6v3"/><path d="M6 7l1 13h10l1-13"/>',
  sort: '<path d="M7 5v14"/><path d="m3 15 4 4 4-4"/><path d="M17 19V5"/><path d="m13 9 4-4 4 4"/>',
  check: '<path d="m5 12 5 5 9-10"/>',
  alert: '<path d="M12 4 2.5 20h19z"/><path d="M12 10v5"/><path d="M12 17.5v.5"/>',
  refresh: '<path d="M20 12a8 8 0 1 1-2.6-5.9"/><path d="M20 4v5h-5"/>',
  heart: '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.600-7 10-7 10z"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  cloud: '<path d="M7 18a4 4 0 0 1-.5-8A6 6 0 0 1 18 9.500a4.300 4.300 0 0 1-.5 8.500z"/>',
  server: '<rect x="4" y="4" width="16" height="7" rx="2"/><rect x="4" y="13" width="16" height="7" rx="2"/><path d="M8 7.500h.01M8 16.500h.01"/>',
  filter: '<path d="M4 5h16l-6 8v6l-4-2v-4z"/>',
  inbox: '<path d="M4 13 6.500 5h11L20 13v6H4z"/><path d="M4 13h5a3 3 0 0 0 6 0h5"/>',
  wifiOff: '<path d="M3 3l18 18"/><path d="M5 12.500a10 10 0 0 1 4-2.600M19 12.500a10 10 0 0 0-5-3"/><path d="M8.500 16a5 5 0 0 1 7 0"/><path d="M12 19.500v.5"/>',
  external: '<path d="M14 5h5v5"/><path d="M19 5l-8 8"/><path d="M18 14v5H5V6h5"/>',
  list: '<path d="M8 6h12M8 12h12M8 18h12"/><path d="M4 6h.01M4 12h.01M4 18h.01"/>',
};

export type IconName = keyof typeof P;

const cache = new Map<string, SafeHtml>();

/** `<svg>` markup for an icon; decorative (aria-hidden), sized by CSS (`.ic`, 20 px by default). */
export function icon(name: IconName, cls = ''): SafeHtml {
  const k = name + '|' + cls;
  let v = cache.get(k);
  if (!v) {
    const c = /^[\w -]*$/.test(cls) ? cls : '';
    v = raw(
      `<svg class="ic${c ? ' ' + c : ''}" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${P[name] ?? ''}</svg>`,
    );
    cache.set(k, v);
  }
  return v;
}
