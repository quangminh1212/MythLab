// Chép giao diện đã build (web/dist, Astro) vào www (webDir của Capacitor); www không đưa lên repo.
// Dừng ngay với mã lỗi khác 0 nếu thiếu web/dist hoặc nếu bản build không còn đúng dạng mong đợi,
// để không bao giờ đóng gói một APK với giao diện cũ hoặc hỏng mà không biết.
import { cpSync, rmSync, existsSync, readFileSync, writeFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, "../../web/dist");
const dst = join(here, "www");

function fail(msg) {
  console.error("sync-web: " + msg);
  process.exit(1);
}

const srcIndex = join(src, "index.html");
if (!existsSync(srcIndex)) fail("không thấy " + srcIndex + " - hãy build giao diện trước (cd web; npm run build) hoặc chạy build.ps1");
const srcHtml = readFileSync(srcIndex, "utf8");
if (!/<script[^>]+type="module"/i.test(srcHtml)) fail(srcIndex + " không có script module: không phải bản build của Astro?");

rmSync(dst, { recursive: true, force: true });
// sw.js/manifest vẫn chép (pwa.ts tự bỏ qua khi chạy trong Capacitor)
cpSync(src, dst, { recursive: true, filter: (p) => !/(^|[\/])(\.DS_Store|Thumbs\.db)$/.test(p) });

// Bỏ viewport-fit=cover: Capacitor sẽ chừa chỗ cho thanh trạng thái (nền teal) thay vì vẽ đè lên header.
// Nếu Astro đổi cách in thẻ meta này thì mẫu không khớp nữa: báo lỗi thay vì âm thầm không làm gì.
const idx = join(dst, "index.html");
const html = readFileSync(idx, "utf8");
const VIEWPORT_FIT = /,\s*viewport-fit=cover/;
if (!VIEWPORT_FIT.test(html)) fail("không tìm thấy 'viewport-fit=cover' trong " + idx + " - bản build đã đổi, hãy sửa sync-web.mjs");
const fixed = html.replace(VIEWPORT_FIT, "");
if (/viewport-fit=cover/.test(fixed)) fail("vẫn còn viewport-fit=cover sau khi thay trong " + idx);
writeFileSync(idx, fixed);

// Kiểm tra bản chép: có JS băm tên và mọi tệp mà index.html trỏ tới (đường dẫn tương đối) đều tồn tại
const astroDir = join(dst, "_astro");
const js = existsSync(astroDir) ? readdirSync(astroDir).filter((f) => f.endsWith(".js")) : [];
if (!js.length) fail("không có tệp .js nào trong " + astroDir);
const missing = [];
for (const m of fixed.matchAll(/\b(?:src|href)="\.\/([^"#?]+)"/g)) {
  if (!existsSync(join(dst, m[1]))) missing.push(m[1]);
}
if (missing.length) fail("index.html trỏ tới tệp không có trong bản chép: " + missing.join(", "));

console.log("Đã chép " + src + " -> " + dst + " (" + js.length + " tệp JS băm tên, bỏ viewport-fit=cover)");
