// Phone parity guards: whatever the desktop reader chrome shows (the .rd-wide buttons) must be reachable on a phone
// through the "Thêm" sheet, and the touch-size stylesheet must be loaded.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

const read = (p: string): string => readFileSync(resolve(process.cwd(), p), 'utf8');

describe('mobile parity', () => {
  const src = read('src/app/views/reader.ts');

  it('every wide-only reader action is in the phone "more" sheet', () => {
    const wide = new Set<string>();
    for (const m of src.matchAll(/data-act="(\w+)"[^>]*class="[^"]*rd-wide|class="[^"]*rd-wide[^"]*"[^>]*data-act="(\w+)"/g)) wide.add((m[1] ?? m[2]) as string);
    for (const m of src.matchAll(/\$\{btn\('(\w+)',[^\n]*'rd-wide'\)\}/g)) wide.add(m[1] as string);
    expect([...wide].sort()).toEqual(['auto', 'help', 'mark', 'settings']);
    const sheet = src.slice(src.indexOf('function moreSheet'), src.indexOf('function drawer'));
    for (const act of wide) expect(sheet, act).toContain(`['${act}'`);
  });

  it('loads the touch-size stylesheet', () => {
    expect(read('src/layouts/Base.astro')).toContain("../styles/mobile-parity.css");
    expect(read('src/styles/mobile-parity.css')).toContain('(pointer: coarse)');
  });
});
