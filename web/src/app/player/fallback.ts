import { Interrupted, Stopped } from './engines';

/** Errors that mean "not a voice failure": stop, system silence or a missing user gesture. */
export function isPlaybackSignal(e: unknown): boolean {
  return e instanceof Stopped || e instanceof Interrupted || (e as { name?: string } | null)?.name === 'NotAllowedError';
}

/**
 * Should a failed device-voice chunk be read by the server Edge voice instead?
 * Not when the run was superseded (`stale`), when the error is a playback signal, or when Edge is unavailable/down.
 */
export function shouldFallBackToEdge(e: unknown, stale: boolean, edgeUsable: boolean): boolean {
  if (stale || isPlaybackSignal(e)) return false;
  return edgeUsable;
}

export interface DeviceFallbackDeps {
  /** reads the chunk with the device voice */
  device: () => Promise<void>;
  /** reads the chunk with the server Edge voice */
  edge: () => Promise<void>;
  /** the generation changed since this run started */
  stale: () => boolean;
  /** Edge is available and not marked down */
  edgeUsable: () => boolean;
  /** announces and switches the live engine (never the saved preference) */
  onFallback: () => void;
}

/** Device voice with a one-chunk server-voice safety net. Rethrows the original error when no fallback applies. */
export async function speakDeviceWithEdgeFallback(d: DeviceFallbackDeps): Promise<void> {
  try {
    await d.device();
  } catch (e) {
    if (!shouldFallBackToEdge(e, d.stale(), d.edgeUsable())) throw e;
    d.onFallback();
    await d.edge();
  }
}
