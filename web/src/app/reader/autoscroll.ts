/**
 * Auto-scroll of the scroll reading mode: moves the page down at a steady speed, waits while the reader
 * scrolls by hand and stops at the end of the chapter. The speed level is remembered.
 */
import { store } from '../core/store';

const KEY = 'mythlab.reader.autospeed';
/** Pixels per second of each speed level (1-based). */
export const SPEEDS = [10, 16, 24, 34, 46, 60, 78, 100, 130] as const;
export const DEFAULT_LEVEL = 4;

export const clampLevel = (n: number): number => Math.max(1, Math.min(SPEEDS.length, Math.round(Number(n)) || DEFAULT_LEVEL));
export const speedOf = (level: number): number => SPEEDS[clampLevel(level) - 1] as number;

/** Whole pixels to scroll after `dt` ms at a level, plus the fraction carried to the next frame. */
export function advance(level: number, dt: number, carry: number): { px: number; carry: number } {
  // a background tab delivers one huge frame: never jump more than a tenth of a second's worth
  const total = carry + (speedOf(level) * Math.max(0, Math.min(dt, 100))) / 1000;
  const px = Math.floor(total);
  return { px, carry: total - px };
}

export interface AutoScroll {
  readonly running: boolean;
  readonly level: number;
  start(): void;
  stop(): void;
  toggle(): void;
  /** Changes the speed by `d` levels. */
  nudge(d: number): void;
  /** The reader scrolled by hand: wait `ms` before moving again. */
  hold(ms?: number): void;
}

export function createAutoScroll(o: {
  /** Called when it starts, stops or changes speed. */
  onChange(running: boolean, level: number): void;
  /** Called when the bottom of the page is reached. */
  onEnd(): void;
  /** Called before every programmatic scroll, so the view can tell it from the reader's own. */
  onStep?(): void;
}): AutoScroll {
  let running = false;
  let level = clampLevel(store.get<number>(KEY, DEFAULT_LEVEL));
  let raf = 0;
  let last = 0;
  let carry = 0;
  let holdUntil = 0;

  function frame(now: number): void {
    raf = 0;
    if (!running) return;
    const dt = last ? now - last : 0;
    last = now;
    if (now >= holdUntil && !document.hidden) {
      const step = advance(level, dt, carry);
      carry = step.carry;
      if (step.px > 0) {
        const root = document.scrollingElement || document.documentElement;
        const max = root.scrollHeight - window.innerHeight;
        if (window.scrollY >= max - 1) {
          api.stop();
          o.onEnd();
          return;
        }
        o.onStep?.();
        window.scrollBy(0, step.px);
      }
    }
    raf = requestAnimationFrame(frame);
  }

  const api: AutoScroll = {
    get running() {
      return running;
    },
    get level() {
      return level;
    },
    start() {
      if (running) return;
      running = true;
      last = 0;
      carry = 0;
      holdUntil = 0;
      raf = requestAnimationFrame(frame);
      o.onChange(true, level);
    },
    stop() {
      if (!running) return;
      running = false;
      if (raf) cancelAnimationFrame(raf);
      raf = 0;
      o.onChange(false, level);
    },
    toggle() {
      if (running) api.stop();
      else api.start();
    },
    nudge(d) {
      const next = clampLevel(level + d);
      if (next === level) return;
      level = next;
      store.set(KEY, level);
      o.onChange(running, level);
    },
    hold(ms = 1200) {
      holdUntil = performance.now() + ms;
    },
  };
  return api;
}
