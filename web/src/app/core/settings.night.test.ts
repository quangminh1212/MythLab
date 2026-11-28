import { describe, expect, it } from 'vitest';
import { defaults, inNightWindow, normalise, parseTime } from './settings';

const m = (t: string): number => parseTime(t) as number;

describe('parseTime', () => {
  it('parses HH:MM and rejects the rest', () => {
    expect(parseTime('00:00')).toBe(0);
    expect(parseTime('19:30')).toBe(1170);
    expect(parseTime('24:00')).toBeNull();
    expect(parseTime('7:00')).toBeNull();
    expect(parseTime('')).toBeNull();
  });
});

describe('inNightWindow', () => {
  it('wraps midnight (19:00 to 06:00)', () => {
    expect(inNightWindow(m('19:00'), '19:00', '06:00')).toBe(true);
    expect(inNightWindow(m('23:59'), '19:00', '06:00')).toBe(true);
    expect(inNightWindow(m('00:00'), '19:00', '06:00')).toBe(true);
    expect(inNightWindow(m('05:59'), '19:00', '06:00')).toBe(true);
    expect(inNightWindow(m('06:00'), '19:00', '06:00')).toBe(false);
    expect(inNightWindow(m('12:00'), '19:00', '06:00')).toBe(false);
    expect(inNightWindow(m('18:59'), '19:00', '06:00')).toBe(false);
  });
  it('handles a same-day window', () => {
    expect(inNightWindow(m('13:00'), '12:00', '14:00')).toBe(true);
    expect(inNightWindow(m('14:00'), '12:00', '14:00')).toBe(false);
    expect(inNightWindow(m('11:59'), '12:00', '14:00')).toBe(false);
  });
  it('treats equal or malformed bounds as never night', () => {
    expect(inNightWindow(100, '08:00', '08:00')).toBe(false);
    expect(inNightWindow(100, 'xx', '06:00')).toBe(false);
  });
});

describe('new settings validation', () => {
  it('defaults', () => {
    const d = defaults();
    expect(d).toMatchObject({ padY: 0, brightnessAuto: true, nightSchedule: false, nightFrom: '19:00', nightTo: '06:00' });
  });
  it('validates times, colours and padding', () => {
    expect(normalise('nightFrom', '21:15')).toBe('21:15');
    expect(normalise('nightFrom', '25:00')).toBe('19:00');
    expect(normalise('customBg', '#ABCDEF')).toBe('#abcdef');
    expect(normalise('customBg', 'red')).toBe(defaults().customBg);
    expect(normalise('padY', 500)).toBe(64);
    expect(normalise('dayPreset', 'custom')).toBe('custom');
  });
});
