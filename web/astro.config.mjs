// MythLab web UI — Astro 7 static build. One client-rendered page (hash routing) that must work unchanged from
// "/" on four hosts: the Go server, the desktop WebView2 shell, Capacitor (https://localhost) and the installed PWA.
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { defineConfig } from 'astro/config';
import serviceWorker from './src/sw/integration.mjs';

// `astro dev` proxies /api to a running MythLab server so the app is same-origin in development.
const API = process.env.MYTHLAB_API || 'http://127.0.0.1:8765';

// With the relative assetsPrefix, Vite's preload list holds "./_astro/x.js" but its helper resolves each entry
// against the importing chunk (itself inside _astro/), which asks for "_astro/_astro/x.js" and 404s. Every chunk
// lives in that one folder, so after the build the entries are rewritten to "./x.js".
function relativePreload() {
  return {
    name: 'mythlab-relative-preload',
    hooks: {
      'astro:build:done': async ({ dir }) => {
        const root = new URL('_astro/', dir);
        for (const name of await readdir(root)) {
          if (!name.endsWith('.js')) continue;
          const file = new URL(name, root);
          const code = await readFile(file, 'utf8');
          if (!code.includes('__vite__mapDeps')) continue;
          const fixed = code.replace(/(m\.f=\[)([^\]]*)(\])/, (_m, open, list, close) => open + list.replaceAll('"./_astro/', '"./') + close);
          if (fixed !== code) await writeFile(file, fixed);
        }
      },
    },
  };
}

export default defineConfig({
  output: 'static',
  compressHTML: true,
  devToolbar: { enabled: false },
  integrations: [relativePreload(), serviceWorker()], // serviceWorker last: it hashes the final files of dist/
  server: { host: '127.0.0.1', port: 4321 },
  build: {
    format: 'file', // dist/index.html, no directory pages
    assets: '_astro', // hashed, immutable (the Go server and the service worker rely on this prefix)
    assetsPrefix: '.', // "./_astro/…": relative to index.html, never to the origin root
    inlineStylesheets: 'never', // no inline <style>: keeps a strict CSP possible
  },
  vite: {
    build: { assetsInlineLimit: 0, target: 'es2022', cssMinify: true },
    server: { proxy: { '/api': { target: API, changeOrigin: false } } },
  },
});
