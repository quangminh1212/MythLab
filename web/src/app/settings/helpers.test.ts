import { describe, expect, it } from 'vitest';
import { apiRoute, parseRange } from '../../sw/shared';
import { defaults, RANGE } from '../core/settings';
import { clampRange } from '../offline/index';
import { RANGES } from './controls';
import { TYPO_PRESETS, matchPreset, presetValues } from './presets';
import { normaliseServerUrl, sourceStatusText } from './source';

describe('clampRange', () => {
  it('clamps and orders', () => {
    expect(clampRange(30)).toEqual({ from: 0, to: 29 });
    expect(clampRange(30, 5, 12)).toEqual({ from: 5, to: 12 });
    expect(clampRange(30, 20, 3)).toEqual({ from: 3, to: 20 });
    expect(clampRange(30, -4, 999)).toEqual({ from: 0, to: 29 });
    expect(clampRange(0)).toEqual({ from: 0, to: 0 });
  });
});

describe('typography presets', () => {
  it('apply and match back', () => {
    for (const p of TYPO_PRESETS) {
      expect(matchPreset({ ...defaults(), ...presetValues(p) })).toBe(p.id);
    }
    expect(matchPreset({ ...defaults(), size: 31 })).toBeNull();
  });
});

describe('controls', () => {
  it('format values and stay inside the setting ranges', () => {
    expect(RANGES.margin.fmt(0)).toBe('Tự động');
    expect(RANGES.size.fmt(20)).toBe('20 px');
    expect(RANGES.line.fmt(1.8)).toBe('1,8');
    for (const k of Object.keys(RANGES) as (keyof typeof RANGES)[]) {
      expect(RANGE[k][0]).toBeLessThan(RANGE[k][1]);
      expect(RANGES[k].step).toBeGreaterThan(0);
    }
  });
});

describe('source helpers', () => {
  it('normalises the server address', () => {
    expect(normaliseServerUrl('192.168.1.5:8765/')).toBe('http://192.168.1.5:8765');
    expect(normaliseServerUrl('https://a.b/c/')).toBe('https://a.b/c');
    expect(normaliseServerUrl('   ')).toBe('');
  });
  it('describes the source', () => {
    expect(sourceStatusText('github', null)).toMatch(/GitHub/);
    expect(sourceStatusText('server', 'http://h:1')).toMatch(/h:1/);
  });
});

describe('service worker helpers', () => {
  it('parses byte ranges', () => {
    expect(parseRange('bytes=0-9', 100)).toEqual({ start: 0, end: 9 });
    expect(parseRange('bytes=90-', 100)).toEqual({ start: 90, end: 99 });
    expect(parseRange('bytes=-10', 100)).toEqual({ start: 90, end: 99 });
    expect(parseRange(null, 100)).toBeNull();
  });
  it('routes api paths', () => {
    expect(apiRoute('/index.html')).toBeNull();
  });
});
