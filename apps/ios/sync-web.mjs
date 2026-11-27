// iOS: chep web/dist (Astro) vao www (webDir cua Capacitor). Giong apps/android/sync-web.mjs: bo viewport-fit=cover
// (config dung ios.contentInset = "always", WebView nam duoi thanh trang thai va tren thanh Home, khong can safe-area CSS).
// Tuy chon: IOS_GOOGLE_CLIENT_ID=<ma khach OAuth loai iOS> ghi vao <meta name="mythlab-ios-google-client-id"> de dang nhap Google native.
// Chua chay thu tren Mac, nhung chay duoc tren Windows/Linux vi chi dung node: `node sync-web.mjs`.
import { cpSync, rmSync, existsSync, readFileSync, writeFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, "../../web/dist");
const dst = join(here, "www");

function fail(msg) {
  console.error("sync-web (ios): " + msg);
  process.exit(1);
}

const srcIndex = join(src, "index.html");
if (!existsSync(srcIndex)) fail("khong thay " + srcIndex + " - hay build giao dien truoc (cd web; npm run build)");
if (!/<script[^>]+type="module"/i.test(readFileSync(srcIndex, "utf8"))) fail(srcIndex + " khong co script module: khong phai ban build cua Astro?");

rmSync(dst, { recursive: true, force: true });
// sw.js/manifest van chep (pwa.ts tu bo qua khi chay trong Capacitor)
cpSync(src, dst, { recursive: true, filter: (p) => !/(^|[\/])(\.DS_Store|Thumbs\.db)$/.test(p) });

const idx = join(dst, "index.html");
let html = readFileSync(idx, "utf8");
const VIEWPORT_FIT = /,\s*viewport-fit=cover/;
if (!VIEWPORT_FIT.test(html)) fail("khong tim thay 'viewport-fit=cover' trong " + idx + " - ban build da doi, hay sua sync-web.mjs");
html = html.replace(VIEWPORT_FIT, "");
if (/viewport-fit=cover/.test(html)) fail("van con viewport-fit=cover sau khi thay trong " + idx);

const gid = (process.env.IOS_GOOGLE_CLIENT_ID || "").trim();
if (gid) {
  if (!/^[\w.-]+\.apps\.googleusercontent\.com$/.test(gid)) fail("IOS_GOOGLE_CLIENT_ID khong phai dang <so>-<ma>.apps.googleusercontent.com");
  if (!/<head[^>]*>/i.test(html)) fail("khong thay <head> de chen meta");
  html = html.replace(/<head[^>]*>/i, (m) => m + `<meta name="mythlab-ios-google-client-id" content="${gid}">`);
} else {
  console.warn("sync-web (ios): chua dat IOS_GOOGLE_CLIENT_ID - dang nhap Google native se bao chua cau hinh");
}
writeFileSync(idx, html);

const astroDir = join(dst, "_astro");
const js = existsSync(astroDir) ? readdirSync(astroDir).filter((f) => f.endsWith(".js")) : [];
if (!js.length) fail("khong co tep .js nao trong " + astroDir);
const missing = [];
for (const m of html.matchAll(/\b(?:src|href)="\.\/([^"#?]+)"/g)) if (!existsSync(join(dst, m[1]))) missing.push(m[1]);
if (missing.length) fail("index.html tro toi tep khong co trong ban chep: " + missing.join(", "));

console.log("Da chep " + src + " -> " + dst + " (" + js.length + " tep JS bam ten, bo viewport-fit=cover" + (gid ? ", co iOS client id" : "") + ")");
