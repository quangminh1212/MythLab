/** What the account panel shows about syncing: when it last worked, whether it is running, whether it is failing. */
import { Emitter } from './events';

export type SyncKind = 'progress' | 'library';

export interface SyncStatus {
  /** Time of the last completed sync round (ms), null before the first one. */
  lastOk: number | null;
  running: boolean;
  /** True while the latest round failed (offline, server error). */
  failing: boolean;
}

const state: Record<SyncKind, { ok: number | null; running: boolean; failing: boolean }> = {
  progress: { ok: null, running: false, failing: false },
  library: { ok: null, running: false, failing: false },
};
const changes = new Emitter<void>();

export const syncStatus = {
  start(k: SyncKind): void {
    state[k].running = true;
    changes.emit();
  },
  ok(k: SyncKind, now = Date.now()): void {
    state[k] = { ok: now, running: false, failing: false };
    changes.emit();
  },
  fail(k: SyncKind): void {
    state[k].running = false;
    state[k].failing = true;
    changes.emit();
  },
  /** Syncing stopped (signed out, backend changed): forget the state. */
  reset(k: SyncKind): void {
    state[k] = { ok: null, running: false, failing: false };
    changes.emit();
  },
  get(): SyncStatus {
    const a = state.progress;
    const b = state.library;
    const oks = [a.ok, b.ok].filter((x): x is number => x !== null);
    return { lastOk: oks.length ? Math.min(...oks) : null, running: a.running || b.running, failing: a.failing || b.failing };
  },
  on: (fn: () => void): (() => void) => changes.on(fn),
};
