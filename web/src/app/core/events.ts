/** Tiny typed event bus shared by all stages. Listeners never throw into the emitter. */
import type { AppEvents } from './contracts';

type Fn<T> = (payload: T) => void;
const map = new Map<string, Set<Fn<never>>>();

/** Subscribes to an app event; returns the unsubscribe function. */
export function on<K extends keyof AppEvents>(type: K, fn: Fn<AppEvents[K]>): () => void {
  let set = map.get(type);
  if (!set) map.set(type, (set = new Set()));
  const s = set;
  s.add(fn as Fn<never>);
  return () => {
    s.delete(fn as Fn<never>);
  };
}

export function emit<K extends keyof AppEvents>(type: K, payload: AppEvents[K]): void {
  const set = map.get(type);
  if (!set) return;
  for (const fn of [...set]) {
    try {
      (fn as Fn<AppEvents[K]>)(payload);
    } catch (e) {
      console.error(e);
    }
  }
}

/** Generic emitter for module-local state (player, settings...). */
export class Emitter<T> {
  private fns = new Set<Fn<T>>();
  on(fn: Fn<T>): () => void {
    this.fns.add(fn);
    return () => {
      this.fns.delete(fn);
    };
  }
  emit(v: T): void {
    for (const fn of [...this.fns]) {
      try {
        fn(v);
      } catch (e) {
        console.error(e);
      }
    }
  }
}

/** Debounce with cancel() and flush() (flush runs a pending call immediately). */
export function debounce<A extends unknown[]>(fn: (...a: A) => void, ms: number): ((...a: A) => void) & { cancel(): void; flush(): void } {
  let t: ReturnType<typeof setTimeout> | undefined;
  let last: A | undefined;
  const run = (): void => {
    t = undefined;
    const a = last;
    last = undefined;
    if (a) fn(...a);
  };
  const d = (...a: A): void => {
    last = a;
    if (t !== undefined) clearTimeout(t);
    t = setTimeout(run, ms);
  };
  d.cancel = (): void => {
    if (t !== undefined) clearTimeout(t);
    t = undefined;
    last = undefined;
  };
  d.flush = (): void => {
    if (t !== undefined) {
      clearTimeout(t);
      run();
    }
  };
  return d;
}
