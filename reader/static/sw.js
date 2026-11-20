// MythLab service worker: tăng CACHE_VERSION mỗi khi đổi danh sách precache
const CACHE_VERSION = 'v3';
const SHELL = 'mythlab-shell-' + CACHE_VERSION;
const RUNTIME = 'mythlab-static';   // font, icon (cache-first, giữ qua các phiên bản)
const TTS = 'mythlab-tts';          // /api/tts (LRU)
const TTS_MAX = 200;
const COVERS = 'mythlab-covers';    // /api/cover (cache-first, LRU)
const COVERS_MAX = 300;
const PRECACHE = [
  './', 'index.html', 'app.js', 'style.css', 'manifest.webmanifest',
  'css/reader-settings.css', 'fonts/fonts.css',
  'js/store.js', 'js/textutil.js', 'js/fonts.js', 'js/settings.js',
  'js/backend-server.js', 'js/backend-github.js', 'js/backends.js',
  'js/tts.js', 'js/settings-panel.js', 'js/pwa.js',
  'icons/icon.svg', 'icons/icon-192.png', 'icons/icon-512.png',
  'icons/maskable-512.png', 'icons/apple-touch-icon.png', 'icons/favicon.ico',
  'icons/favicon-16x16.png', 'icons/favicon-32x32.png', 'icons/xlab-logo.png', 'icons/xlab-logo-dark.png',
];
const BASE = new URL('./', self.location).href;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => Promise.all(PRECACHE.map(p =>
    c.add(new Request(p, {cache: 'reload'})).catch(() => {})))).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks
    .filter(k => k.startsWith('mythlab-shell-') && k !== SHELL).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('message', e => { if (e.data === 'skipWaiting') self.skipWaiting(); });

async function networkFirst(req, nav) {
  const c = await caches.open(SHELL);
  try {
    const res = await fetch(req);
    if (res.ok && res.type === 'basic') c.put(nav ? BASE : req, res.clone());
    return res;
  } catch (err) {
    const hit = await c.match(nav ? BASE : req, {ignoreSearch: true})
      || (nav && await c.match('index.html', {ignoreSearch: true}));
    if (hit) return hit;
    throw err;
  }
}

async function cacheFirst(req) {
  const hit = await caches.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (res.ok) (await caches.open(RUNTIME)).put(req, res.clone());
  return res;
}

// cache-first + LRU: mục vừa dùng được chèn lại cuối danh sách, quá `max` thì xoá mục cũ nhất
async function lruCache(req, name, max) {
  const c = await caches.open(name);
  const hit = await c.match(req.url);
  if (hit) {
    // LRU: chèn lại để mục vừa dùng nằm cuối danh sách
    const body = await hit.clone().blob();
    c.delete(req.url).then(() => c.put(req.url, new Response(body, {headers: hit.headers}))).catch(() => {});
    return hit;
  }
  const res = await fetch(req.url, {credentials: 'same-origin', mode: req.mode === 'navigate' ? 'cors' : req.mode});
  if (res.status === 200) {
    // put song song cùng URL (vd. 2 thẻ <img> cùng ảnh) có thể lỗi "Entry already exists": bỏ qua, vẫn trả ảnh
    try {
      await c.put(req.url, res.clone());
      const keys = await c.keys();
      for (let i = 0; i < keys.length - max; i++) await c.delete(keys[i]);
    } catch {}
  }
  return res;
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.hostname === 'api.github.com') return;
  if (url.pathname.endsWith('/api/tts')) return e.respondWith(lruCache(req, TTS, TTS_MAX));
  if (url.pathname.endsWith('/api/cover')) return e.respondWith(lruCache(req, COVERS, COVERS_MAX));
  if (url.origin !== self.location.origin || url.pathname.includes('/api/')) return;
  if (req.mode === 'navigate') return e.respondWith(networkFirst(req, true));
  if (/\.(woff2?|ttf|otf|png|svg|ico|webp)$/i.test(url.pathname)) return e.respondWith(cacheFirst(req));
  if (/\.(html|js|css|webmanifest)$/i.test(url.pathname) || url.href === BASE) return e.respondWith(networkFirst(req, false));
});
