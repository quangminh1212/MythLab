// Downloads the Vietnamese Piper models from Hugging Face (pinned commits) into a local folder, verifying size and
// SHA-256, e.g. to (re)upload them to the GitHub release "piper-models" (the app's second download source, after
// Hugging Face). Nothing is served by our own server. NOT part of predev/prebuild.
//
//   node scripts/fetch-models.mjs                      every model -> public/tts/models
//   node scripts/fetch-models.mjs vais1000 vivos       only ids containing these words
//   node scripts/fetch-models.mjs --out D:/models      another folder
//
// Files already present with the right size and hash are kept. A failed download leaves no file behind.
import { createHash } from 'node:crypto';
import { createReadStream, createWriteStream, existsSync, mkdirSync, renameSync, rmSync, statSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const catalog = JSON.parse(await readFile(join(here, 'piper-models.json'), 'utf8'));

const args = process.argv.slice(2);
let out = join(here, '..', 'public', 'tts', 'models');
const words = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--out') out = resolve(args[++i] ?? '');
  else words.push(args[i].toLowerCase());
}
const picked = catalog.models.filter((m) => !words.length || words.some((w) => m.id.toLowerCase().includes(w)));
if (!picked.length) {
  console.error(`fetch-models: no voice matches ${words.join(', ')}. Known: ${catalog.models.map((m) => m.id).join(', ')}`);
  process.exit(1);
}

function sha256(file) {
  return new Promise((ok, bad) => {
    const h = createHash('sha256');
    createReadStream(file).on('data', (d) => h.update(d)).on('end', () => ok(h.digest('hex'))).on('error', bad);
  });
}

async function valid(file, bytes, hash) {
  return existsSync(file) && statSync(file).size === bytes && (await sha256(file)) === hash;
}

async function get(url, file, bytes, hash) {
  if (await valid(file, bytes, hash)) return console.log(`  ok (already there) ${file}`);
  const tmp = `${file}.part`;
  try {
    const res = await fetch(url);
    if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
    await pipeline(Readable.fromWeb(res.body), createWriteStream(tmp));
    if (statSync(tmp).size !== bytes) throw new Error(`size ${statSync(tmp).size}, expected ${bytes}`);
    const got = await sha256(tmp);
    if (got !== hash) throw new Error(`sha256 ${got}, expected ${hash}`);
    renameSync(tmp, file);
    console.log(`  ok ${file} (${bytes} bytes, sha256 verified)`);
  } catch (e) {
    rmSync(tmp, { force: true });
    throw new Error(`${url}: ${e.message}`);
  }
}

mkdirSync(out, { recursive: true });
let failed = 0;
for (const m of picked) {
  console.log(m.id);
  const base = `${m.repo}${m.id}.onnx`;
  try {
    await get(`${base}.json`, join(out, `${m.id}.onnx.json`), m.configBytes, m.configSha256);
    await get(base, join(out, `${m.id}.onnx`), m.bytes, m.sha256);
  } catch (e) {
    failed++;
    console.error(`  FAILED ${e.message}`);
  }
}
console.log(failed ? `fetch-models: ${failed} voice(s) failed` : `fetch-models: done, upload ${out}/* to the GitHub release piper-models`);
process.exit(failed ? 1 : 0);
