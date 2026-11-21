/**
 * The sentence the player is speaking right now. A tiny module of its own so the reader can follow the voice
 * without loading the player (the player chunk is only fetched when somebody presses "listen").
 */
import { Emitter } from '../core/events';

export interface SpeechMark {
  source: string;
  key: string;
  /** 0-based chapter index. */
  idx: number;
  /** Paragraph index; -1 = the chapter title. */
  para: number;
  /** Character range [s, e) of the sentence inside the paragraph text. */
  s: number;
  e: number;
}

let mark: SpeechMark | null = null;
const changes = new Emitter<SpeechMark | null>();

export const currentMark = (): SpeechMark | null => mark;

export function setMark(m: SpeechMark | null): void {
  if (m === mark) return;
  if (m && mark && m.source === mark.source && m.key === mark.key && m.idx === mark.idx && m.para === mark.para && m.s === mark.s && m.e === mark.e) return;
  mark = m;
  changes.emit(m);
}

export const onMark = (fn: (m: SpeechMark | null) => void): (() => void) => changes.on(fn);
