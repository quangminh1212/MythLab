// Chép reader/static vào www (webDir của Capacitor); www không đưa lên repo
import { cpSync, rmSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, "../../reader/static");
const dst = join(here, "www");
if (!existsSync(join(src, "index.html"))) { console.error("Không thấy " + src); process.exit(1); }
rmSync(dst, { recursive: true, force: true });
// sw.js/manifest vẫn chép (pwa.js tự bỏ qua khi chạy trong Capacitor)
cpSync(src, dst, { recursive: true, filter: (p) => !/(^|[\/])(\.DS_Store|Thumbs\.db)$/.test(p) });
// bỏ viewport-fit=cover: Capacitor sẽ chừa chỗ cho thanh trạng thái (nền teal) thay vì vẽ đè lên header
const idx = join(dst, "index.html");
writeFileSync(idx, readFileSync(idx, "utf8").replace(/,\s*viewport-fit=cover/, ""));
console.log("Đã chép " + src + " -> " + dst);
