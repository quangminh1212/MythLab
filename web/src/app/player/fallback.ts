import { Interrupted, Stopped } from './engines';

/** Errors that mean "not a voice failure": stop, system silence or a missing user gesture. */
export function isPlaybackSignal(e: unknown): boolean {
  return e instanceof Stopped || e instanceof Interrupted || (e as { name?: string } | null)?.name === 'NotAllowedError';
}
