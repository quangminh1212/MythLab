// Copies the self-hosted Piper runtime from node_modules into public/tts/ (generated, git-ignored):
//   onnxruntime-web -> ort/ (the plain single-thread WASM build only, not the 22 MB WebGPU one)
//   @diffusionstudio/piper-wasm -> piper/ (espeak-ng phonemizer), with its 18 MB all-languages data trimmed to the
//   Vietnamese subset (~0.9 MB) by espeak-trim.mjs and checked to phonemize Vietnamese exactly like the original.
// The runtime is served from our own origin, never fetched from a third party, so it needs no fallback source.
// Runs before dev/build; `npm ci` first. Skips quietly when the packages are missing (a web-only checkout).
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { trimEspeak, verifyTrim } from './espeak-trim.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const nm = join(root, 'node_modules');
const out = join(root, 'public', 'tts');
const jobs = [
  ['onnxruntime-web/dist', 'ort', ['ort.wasm.min.mjs', 'ort-wasm-simd-threaded.mjs', 'ort-wasm-simd-threaded.wasm']],
  // onnxruntime-web 1.30 for the 14-voice Kokoro model (1.22 above gives wrong audio with it); only that worker loads it
  ['onnxruntime-web-130/dist', 'ort130', ['ort.wasm.min.mjs', 'ort-wasm-simd-threaded.mjs', 'ort-wasm-simd-threaded.wasm']],
  ['@diffusionstudio/piper-wasm/build', 'piper', ['piper_phonemize.wasm']],
];
for (const [from, to, files] of jobs) {
  if (!existsSync(join(nm, from))) {
    console.warn(`copy-tts: ${from} is not installed, Piper will be unavailable`);
    continue;
  }
  mkdirSync(join(out, to), { recursive: true });
  for (const f of files) copyFileSync(join(nm, from, f), join(out, to, f));
}

const src = join(nm, '@diffusionstudio/piper-wasm/build');
if (existsSync(src)) {
  const js = readFileSync(join(src, 'piper_phonemize.js'), 'utf8');
  const wasm = readFileSync(join(src, 'piper_phonemize.wasm'));
  const data = new Uint8Array(readFileSync(join(src, 'piper_phonemize.data')));
  const trimmed = trimEspeak(js, data);
  const dst = join(out, 'piper');
  const same = (name, bytes) => existsSync(join(dst, name)) && Buffer.compare(readFileSync(join(dst, name)), Buffer.from(bytes)) === 0;
  if (!(same('piper_phonemize.data', trimmed.data) && same('piper_phonemize.js', Buffer.from(trimmed.js)))) {
    await verifyTrim(js, wasm, data, trimmed); // throws (build fails) if Vietnamese would sound different
    writeFileSync(join(dst, 'piper_phonemize.data'), trimmed.data);
    writeFileSync(join(dst, 'piper_phonemize.js'), trimmed.js);
    console.log(`copy-tts: espeak data trimmed to Vietnamese, ${data.length} -> ${trimmed.data.length} bytes`);
  }
}

// Kokoro-Vietnamese-Lite text frontend (src/app/player/kokoro/*.ts, vendored, dependency-free) compiled to plain ES
// modules for kokoro-worker.js. The compiler is the project's own TypeScript; the import is renamed to a real file.
if (existsSync(join(nm, 'typescript'))) {
  const { default: ts } = await import('typescript');
  const kdir = join(out, 'kokoro');
  mkdirSync(kdir, { recursive: true });
  for (const f of ['frontend', 'normalize-text']) {
    const code = readFileSync(join(root, 'src', 'app', 'player', 'kokoro', `${f}.ts`), 'utf8');
    const js = ts.transpileModule(code, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 } }).outputText.replace("from './normalize-text'", "from './normalize-text.js'");
    writeFileSync(join(kdir, `${f}.js`), js);
  }
} else {
  console.warn('copy-tts: typescript is not installed, the Kokoro voice will be unavailable');
}
