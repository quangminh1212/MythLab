import { describe, expect, it } from 'vitest';
import { DEF, normalise } from '../core/settings';
import { getNowReading } from './index';

describe('now reading', () => {
  it('is nothing while the player is idle', () => {
    expect(getNowReading()).toBeNull();
  });
  it('opens the reader automatically by default and accepts only booleans', () => {
    expect(DEF.autoOpenReader).toBe(true);
    expect(normalise('autoOpenReader', false)).toBe(false);
    expect(normalise('autoOpenReader', 'no')).toBe(true);
  });
});
