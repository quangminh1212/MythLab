/** Keyboard helpers shared by the reader and the player dock. */

/** True when a key press belongs to a control (so a shortcut must not fire as well). */
export function typingTarget(e: KeyboardEvent): boolean {
  const t = e.target as HTMLElement | null;
  if (!t || !t.closest) return false;
  return !!t.closest('input, textarea, select, button, a[href], summary, [contenteditable=""], [contenteditable="true"], [role="button"], [role="tab"], [role="slider"]');
}

/** The key of an event with letters lower-cased, so shortcuts work with Caps Lock and Shift. */
export const keyOf = (e: KeyboardEvent): string => (e.key.length === 1 ? e.key.toLowerCase() : e.key);

/**
 * True when a bare key may trigger a reader shortcut: the user has not switched single-key shortcuts off, and no
 * modifier is held. Arrow / page keys are navigation and always allowed; `singleKey` marks letters, Space, ?, +/-.
 */
export function shortcutAllowed(e: KeyboardEvent, enabled: boolean, singleKey: boolean): boolean {
  if (e.ctrlKey || e.metaKey || e.altKey) return false;
  return !singleKey || enabled;
}
