import { describe, expect, it } from 'vitest';
import { shortcutAllowed, typingTarget } from './keys';

const ev = (init: KeyboardEventInit = {}): KeyboardEvent => new KeyboardEvent('keydown', init);

describe('single-key shortcuts (WCAG 2.1.4)', () => {
  it('lets single keys through only while the setting is on', () => {
    expect(shortcutAllowed(ev({ key: 'm' }), true, true)).toBe(true);
    expect(shortcutAllowed(ev({ key: 'm' }), false, true)).toBe(false);
  });
  it('always allows navigation keys', () => {
    expect(shortcutAllowed(ev({ key: 'ArrowLeft' }), false, false)).toBe(true);
  });
  it('never fires with Ctrl, Meta or Alt held', () => {
    expect(shortcutAllowed(ev({ key: ' ', ctrlKey: true }), true, true)).toBe(false);
    expect(shortcutAllowed(ev({ key: 'a', altKey: true }), true, true)).toBe(false);
    expect(shortcutAllowed(ev({ key: 'ArrowLeft', metaKey: true }), true, false)).toBe(false);
  });
  it('treats focused controls as typing targets so Space activates them', () => {
    const b = document.createElement('button');
    document.body.append(b);
    let hit = false;
    b.addEventListener('keydown', (e) => (hit = typingTarget(e)));
    b.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', bubbles: true }));
    expect(hit).toBe(true);
    b.remove();
  });
});
