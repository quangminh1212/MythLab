import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { KEEP, phonemizeIds, readMeta, SAMPLES, trimEspeak, verifyTrim } from '../../../scripts/espeak-trim.mjs';

// vitest runs in web/; the happy-dom environment has no file: import.meta.url
const dir = join(process.cwd(), 'node_modules', '@diffusionstudio', 'piper-wasm', 'build');
const have = existsSync(join(dir, 'piper_phonemize.data'));

describe.skipIf(!have)('espeak data trimmed to Vietnamese', () => {
  const js = have ? readFileSync(join(dir, 'piper_phonemize.js'), 'utf8') : '';
  const wasm = have ? readFileSync(join(dir, 'piper_phonemize.wasm')) : Buffer.alloc(0);
  const data = have ? new Uint8Array(readFileSync(join(dir, 'piper_phonemize.data'))) : new Uint8Array();

  it('keeps only Vietnamese (plus en_dict for Latin words) and is deterministic', () => {
    const a = trimEspeak(js, data);
    const b = trimEspeak(js, data);
    expect(a.data.length).toBeLessThan(1_000_000);
    expect(Buffer.compare(Buffer.from(a.data), Buffer.from(b.data))).toBe(0);
    expect(a.js).toBe(b.js);
    const meta = readMeta(a.js) as { files: { filename: string; start: number; end: number }[]; remote_package_size: number };
    expect(meta.files.map((f) => f.filename)).toEqual(KEEP);
    expect(meta.remote_package_size).toBe(a.data.length);
    expect(meta.files.at(-1)?.end).toBe(a.data.length);
    expect(meta.files.filter((f) => /_dict$/.test(f.filename)).map((f) => f.filename.split('/').pop())).toEqual(['vi_dict', 'en_dict']);
    expect(a.js).not.toContain('/espeak-ng-data/lang/art');
  });

  it('phonemizes Vietnamese with the same ids as the full data', async () => {
    const t = trimEspeak(js, data);
    await verifyTrim(js, wasm, data, t);
    const ids = (await phonemizeIds(t.js, wasm, t.data, SAMPLES[0])) as unknown as number[];
    expect(ids.length).toBeGreaterThan(20);
  }, 60_000);
});
