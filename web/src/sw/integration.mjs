// Astro integration: after `astro build` wrote dist/, bundle src/sw/sw.ts into dist/sw.js with the list of shell
// files of this build. It must run after every step that rewrites files in dist/ (the hashes below describe the
// final bytes), so it is registered last in astro.config.mjs.
import { createHash } from 'node:crypto';
import { readdir, readFile, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { build } from 'vite';

/** Font files of the default UI and reading fonts (latin + vietnamese, ~120 kB): precached so they work offline at once. */
export const CRITICAL_FONTS = ['inter-latin-wght-normal', 'inter-vietnamese-wght-normal', 'literata-latin-wght-normal', 'literata-vietnamese-wght-normal'].map((f) => `fonts/files/${f}.woff2`);

/** Files never precached: the worker itself, the self-hosted Piper runtime (tts/, fetched on demand), source maps, the other font files (cached when first used). */
const skip = (rel) => rel === 'sw.js' || rel.endsWith('.map') || (rel.startsWith('fonts/files/') && !CRITICAL_FONTS.includes(rel)) || rel.endsWith('.txt') || rel.endsWith('.md') || rel.startsWith('tts/');

async function walk(dir, base = '') {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const rel = base + e.name;
    if (e.isDirectory()) out.push(...(await walk(new URL(e.name + '/', dir), rel + '/')));
    else if (e.isFile()) out.push(rel);
  }
  return out;
}

/** The precache manifest of a built directory: sorted relative paths and a build id over names + contents. */
export async function shellManifest(dir) {
  const files = (await walk(dir)).filter((f) => !skip(f)).sort();
  const hash = createHash('sha256');
  let bytes = 0;
  for (const f of files) {
    const buf = await readFile(new URL(f, dir));
    bytes += buf.length;
    hash.update(f).update('\0').update(buf).update('\0');
  }
  return { v: hash.digest('hex').slice(0, 12), files, bytes };
}

export default function serviceWorker() {
  return {
    name: 'mythlab-service-worker',
    hooks: {
      'astro:build:done': async ({ dir, logger }) => {
        const m = await shellManifest(dir);
        if (!m.files.includes('index.html')) throw new Error('service worker: dist/index.html is missing');
        await build({
          configFile: false,
          logLevel: 'warn',
          publicDir: false,
          define: { __SW_MANIFEST__: JSON.stringify({ v: m.v, files: m.files }) },
          build: {
            outDir: fileURLToPath(dir),
            emptyOutDir: false,
            copyPublicDir: false,
            target: 'es2022',
            minify: true,
            sourcemap: false,
            lib: { entry: fileURLToPath(new URL('./sw.ts', import.meta.url)), formats: ['iife'], name: 'MythLabSw', fileName: () => 'sw.js' },
          },
        });
        const size = (await stat(new URL('sw.js', dir))).size;
        logger.info(`sw.js ${(size / 1024).toFixed(1)} kB, build ${m.v}, precache ${m.files.length} files (${(m.bytes / 1024).toFixed(0)} kB)`);
      },
    },
  };
}
