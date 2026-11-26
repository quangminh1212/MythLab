import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ACTION_TOAST_MS, announce, bindToasts, closeAllDialogs, confirmDialog, toast } from './ui';

beforeEach(() => {
  vi.useFakeTimers();
  document.body.innerHTML = '<div id="toasts"></div><div id="sr-status"></div>';
});
afterEach(() => vi.useRealTimers());

const host = (): HTMLElement => document.getElementById('toasts') as HTMLElement;

describe('toast', () => {
  it('hides a plain toast after a short time', () => {
    toast('Xong');
    expect(host().textContent).toContain('Xong');
    vi.advanceTimersByTime(3300);
    expect(host().childElementCount).toBe(0);
  });

  it('keeps an action toast long enough and pauses while focused', () => {
    const run = vi.fn();
    toast({ message: 'Đã xoá', action: { label: 'Hoàn tác', run } });
    vi.advanceTimersByTime(7000);
    expect(host().childElementCount).toBe(1);
    const box = host().firstElementChild as HTMLElement;
    box.dispatchEvent(new Event('focusin'));
    vi.advanceTimersByTime(ACTION_TOAST_MS * 3);
    expect(host().childElementCount).toBe(1);
    box.dispatchEvent(new Event('focusout'));
    vi.advanceTimersByTime(ACTION_TOAST_MS + 10);
    expect(host().childElementCount).toBe(0);
  });

  it('runs the action once and dismisses', () => {
    const run = vi.fn();
    toast({ message: 'm', action: { label: 'Hoàn tác', run } });
    (host().querySelector('.toast-act') as HTMLElement).click();
    expect(run).toHaveBeenCalledTimes(1);
    expect(host().childElementCount).toBe(0);
  });

  it('Alt+T focuses the action button', () => {
    bindToasts();
    toast({ message: 'm', action: { label: 'Hoàn tác', run: () => {} } });
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 't', altKey: true }));
    expect(document.activeElement).toBe(host().querySelector('.toast-act'));
  });
});

describe('announce', () => {
  it('writes to the status region', () => {
    announce('Trang mới');
    expect(document.getElementById('sr-status')?.textContent).toBe('Trang mới');
  });
});

describe('dialogs and route changes', () => {
  afterEach(() => {
    closeAllDialogs();
    document.body.innerHTML = '';
  });

  it('a route change closes a normal dialog but not a persistent one (the voice download question)', async () => {
    const plain = confirmDialog({ title: 'a', message: 'a' });
    const kept = confirmDialog({ title: 'b', message: 'b', persistent: true, cancelFirst: true });
    expect(document.activeElement?.hasAttribute('data-close')).toBe(true); // Huỷ has the focus
    expect(document.querySelectorAll('.dialog')).toHaveLength(2);
    closeAllDialogs();
    expect(await plain).toBe(false);
    expect(document.querySelectorAll('.dialog')).toHaveLength(1);

    (document.querySelector('[data-ok]') as HTMLElement).click();
    expect(await kept).toBe(true);
  });
});
