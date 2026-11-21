/**
 * Icons used only by the reader and the player (the shared set lives in core/icons.ts). Same drawing rules:
 * 24x24 grid, stroke 1.8, round caps, `currentColor`.
 */
import { raw, type SafeHtml } from '../core/html';

const P = {
  chapterPrev: '<path d="M18 6v12L9 12z"/><path d="M6 6v12"/>',
  chapterNext: '<path d="M6 6v12l9-6z"/><path d="M18 6v12"/>',
  stepBack: '<path d="M11 7l-6 5 6 5z"/><path d="M19 7l-6 5 6 5z"/>',
  stepNext: '<path d="M13 7l6 5-6 5z"/><path d="M5 7l6 5-6 5z"/>',
  timer: '<circle cx="12" cy="13" r="7.5"/><path d="M12 9v4l2.5 2"/><path d="M9.5 2.5h5"/>',
  autoScroll: '<path d="M12 4v15"/><path d="M6.5 13.5L12 19l5.5-5.5"/><path d="M5 4h14"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.2a2.6 2.6 0 1 1 3.6 2.4c-.7.4-1.1.9-1.1 1.8"/><path d="M12 17h.01"/>',
  bookmarkOn: '<path d="M6.5 3.5h11a1 1 0 0 1 1 1V21l-6.5-4.2L5.5 21V4.5a1 1 0 0 1 1-1z" fill="currentColor"/>',
  expand: '<path d="M6 14l6-6 6 6"/>',
  minus: '<path d="M6 12h12"/>',
  plus: '<path d="M12 6v12"/><path d="M6 12h12"/>',
  more: '<circle cx="5" cy="12" r="1.2" fill="currentColor"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/><circle cx="19" cy="12" r="1.2" fill="currentColor"/>',
} as const;

export type XIconName = keyof typeof P;

export function xicon(name: XIconName, cls = ''): SafeHtml {
  return raw(
    `<svg class="ic${cls ? ' ' + cls.replace(/[^\w -]/g, '') : ''}" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${P[name]}</svg>`,
  );
}
