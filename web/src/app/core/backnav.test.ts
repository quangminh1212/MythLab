import { afterEach, describe, expect, it, vi } from 'vitest';
import { decideBack, handleBack, init, EXIT_WINDOW_MS } from './backnav';

describe('decideBack', () => {
  it('goes back on inner pages when history exists, else home', () => {
    for (const v of ['story', 'read', 'lib', 'search', 'history', 'bookmarks']) {
      expect(decideBack(v, true, 0, -Infinity)).toBe('back');
      expect(decideBack(v, false, 0, -Infinity)).toBe('home');
    }
  });
  it('never exits from an inner page, even right after a home warning', () => {
    expect(decideBack('read', false, 100, 99)).toBe('home');
  });
  it('home warns first, exits on the second press within the window only', () => {
    expect(decideBack('home', true, 5000, -Infinity)).toBe('warn');
    expect(decideBack('home', false, 5000, 4000)).toBe('exit');
    expect(decideBack('home', false, 5000 + EXIT_WINDOW_MS + 1, 5000)).toBe('warn');
  });
});

describe('handleBack', () => {
  afterEach(() => {
    location.hash = '';
    document.body.innerHTML = '';
    delete (globalThis as { Capacitor?: unknown }).Capacitor;
  });

  it('on the home route: warn then exit', () => {
    location.hash = '#/';
    document.body.innerHTML = '<div id="toasts"></div>';
    const exit = vi.fn();
    const st = { lastWarnAt: -Infinity };
    expect(handleBack({ canGoBack: true }, exit, 1000, st)).toBe('warn');
    expect(exit).not.toHaveBeenCalled();
    expect(document.getElementById('toasts')?.textContent).toContain('Nhấn Back lần nữa để thoát');
    expect(handleBack({ canGoBack: true }, exit, 1500, st)).toBe('exit');
    expect(exit).toHaveBeenCalledOnce();
  });

  it('on an inner route without history it replaces with home instead of exiting', () => {
    location.hash = '#/r/local0/k/3';
    const exit = vi.fn();
    expect(handleBack({ canGoBack: false }, exit, 1, { lastWarnAt: -Infinity })).toBe('home');
    expect(exit).not.toHaveBeenCalled();
    expect(location.hash).toBe('#/');
  });

  it('registers only inside Capacitor', () => {
    expect(init()).toBe(false);
    const addListener = vi.fn();
    (globalThis as { Capacitor?: unknown }).Capacitor = { Plugins: { App: { addListener, exitApp: vi.fn() } } };
    expect(init()).toBe(true);
    expect(addListener).toHaveBeenCalledWith('backButton', expect.any(Function));
  });
});
