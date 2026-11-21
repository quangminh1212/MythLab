import { describe, expect, it } from 'vitest';
import { CACHE, fingerprint, identUrl, LIMIT } from './shared';

describe('server identity', () => {
  it('fingerprints origin + key without exposing the key', async () => {
    const a = await fingerprint('http://a', 'secret');
    expect(a).toMatch(/^[0-9a-f]{16}$/);
    expect(a).not.toContain('secret');
    expect(await fingerprint('http://a', 'secret')).toBe(a);
    expect(await fingerprint('http://a', 'other')).not.toBe(a);
    expect(await fingerprint('http://b', 'secret')).not.toBe(a);
  });

  it('adds the identity to a URL with or without a query', () => {
    expect(identUrl('http://a/api/story?x=1', 'ff')).toBe('http://a/api/story?x=1&__ml=ff');
    expect(identUrl('http://a/api/sources', 'ff')).toBe('http://a/api/sources?__ml=ff');
  });

  it('uses new bucket names and deletes the identity-less ones', () => {
    for (const n of [CACHE.api, CACHE.covers, CACHE.tts]) expect(CACHE.legacyIdentity).not.toContain(n);
    expect(CACHE.legacyIdentity.length).toBe(3);
    expect(LIMIT.api).toBeGreaterThanOrEqual(300);
  });
});
