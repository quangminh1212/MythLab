/* MythLab Truyện — đọc & nghe truyện định dạng Done_* */
"use strict";

// ---------------------------------------------------------------- utils
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const enc = encodeURIComponent;
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* ignore */ } },
};
// chuyển dữ liệu từ tên cũ (XLab) sang MythLab
try {
  for (const k of ["settings", "progress", "sort"]) {
    const old = localStorage.getItem("xlab." + k);
    if (old != null && localStorage.getItem("mythlab." + k) == null) localStorage.setItem("mythlab." + k, old);
    localStorage.removeItem("xlab." + k);
  }
} catch { /* ignore */ }
const hashHue = (s) => { let h = 0; for (const c of String(s)) h = (h * 31 + c.codePointAt(0)) >>> 0; return h % 360; };
const fmtNum = (n) => (n == null ? "" : Number(n).toLocaleString("vi-VN"));
let toastTimer;
function toast(msg, ms = 2800) {
  const t = $("#toast"); t.textContent = msg; t.classList.remove("hidden");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.add("hidden"), ms);
}
const apiCache = new Map();
async function api(path, { cache = true } = {}) {
  if (cache && apiCache.has(path)) return apiCache.get(path);
  const p = fetch("/api/" + path).then(async (r) => {
    const j = await r.json().catch(() => ({ error: `HTTP ${r.status}` }));
    if (!r.ok || j.error) throw new Error(j.error || `HTTP ${r.status}`);
    return j;
  });
  if (cache) { apiCache.set(path, p); p.catch(() => apiCache.delete(path)); }
  return p;
}
const loadingHTML = (msg = "Đang tải…") => `<div class="loading"><span class="spinner"></span>${esc(msg)}</div>`;
const sKey = (source, key) => `${source}|${key}`;

// ---------------------------------------------------------------- settings
const DEF = { theme: "light", font: "serif", size: 20, line: 1.8, width: 720, engine: "edge", voice: "vi-VN-HoaiMyNeural",
  rate: 1, autoNext: true, follow: true, readTitle: true };
const S = Object.assign({}, DEF, store.get("mythlab.settings", {}));
// v2 (XLab-style UI): the old default "sepia" becomes the new default "light" once.
if (!S.ui2) { if (S.theme === "sepia") S.theme = "light"; S.ui2 = 1; store.set("mythlab.settings", S); }
const saveS = () => store.set("mythlab.settings", S);
function applyS() {
  const r = document.documentElement;
  r.dataset.theme = S.theme;
  r.dataset.font = S.font;
  r.style.setProperty("--read-size", S.size + "px");
  r.style.setProperty("--read-line", S.line);
  r.style.setProperty("--read-width", S.width + "px");
  const bg = getComputedStyle(r).getPropertyValue("--bg").trim();
  document.querySelector('meta[name="theme-color"]').content = bg || "#ffffff";
}
applyS();

// ---------------------------------------------------------------- progress
const PROG = store.get("mythlab.progress", {});
function saveProgress(p) {
  PROG[sKey(p.source, p.key)] = { ...PROG[sKey(p.source, p.key)], ...p, ts: Date.now() };
  store.set("mythlab.progress", PROG);
}
const recentList = () => Object.values(PROG).sort((a, b) => b.ts - a.ts);

// ---------------------------------------------------------------- data
let SOURCES = [];
let TTS_INFO = { edge: false };
async function loadSources() {
  const j = await api("sources");
  SOURCES = j.sources; TTS_INFO = j.tts || TTS_INFO;
  if (!TTS_INFO.edge && S.engine === "edge") S.engine = "browser";
  renderSidebar();
}
const storiesOf = (source, repo) => api(`stories?source=${enc(source)}${repo ? `&repo=${enc(repo)}` : ""}`).then((j) => j.stories);
const storyOf = (source, key) => api(`story?source=${enc(source)}&key=${enc(key)}`);
const chapterOf = (source, key, file) => api(`chapter?source=${enc(source)}&key=${enc(key)}&file=${enc(file)}`);

// ---------------------------------------------------------------- sidebar
let ghFilter = "";
function renderSidebar() {
  const nav = $("#sources");
  const route = parseHash();
  nav.innerHTML = SOURCES.map((s) => {
    const activeSrc = route.source === s.id;
    if (s.kind === "github") {
      const repos = (s.repos || []).filter((r) => !ghFilter || r.repo.toLowerCase().includes(ghFilter.toLowerCase()));
      return `<div class="src">
        <a class="src-title ${activeSrc && !route.repo && route.view === "lib" ? "active" : ""}" href="#/lib/${enc(s.id)}">
          <svg viewBox="0 0 24 24"><path d="M9 19c-4 1.5-4-2-6-2m12 4v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1-.3-3.4 1.3a11.6 11.6 0 0 0-6 0C6.8 2.8 5.8 3.1 5.8 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4.4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/></svg>
          ${esc(s.name)} <small>${s.repos ? s.repos.length : ""}</small></a>
        ${s.error ? `<div class="err">${esc(s.error)}</div>` : ""}
        ${(s.repos || []).length > 8 ? `<input class="filter" id="ghFilter" placeholder="Lọc repo…" value="${esc(ghFilter)}">` : ""}
        ${repos.map((r) => `<a class="item ${activeSrc && route.repo === r.repo ? "active" : ""}" href="#/lib/${enc(s.id)}/${enc(r.repo)}" title="${esc(r.repo)}">${esc(r.repo.replace(/^Done_/, ""))}</a>`).join("")}
      </div>`;
    }
    return `<div class="src"><a class="src-title ${activeSrc ? "active" : ""}" href="#/lib/${enc(s.id)}" title="${esc(s.detail)}">
      <svg viewBox="0 0 24 24"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
      ${esc(s.name)}${s.available ? "" : ' <small>(không có)</small>'}</a></div>`;
  }).join("") || `<div class="pad muted">Chưa cấu hình nguồn nào.</div>`;
  const f = $("#ghFilter");
  if (f) f.oninput = () => { ghFilter = f.value; const pos = f.selectionStart; renderSidebar(); const g = $("#ghFilter"); g.focus(); g.setSelectionRange(pos, pos); };
}

// ---------------------------------------------------------------- router
function parseHash() {
  const parts = location.hash.replace(/^#\/?/, "").split("/").map((x) => { try { return decodeURIComponent(x); } catch { return x; } });
  const [v, a, b, c] = parts;
  if (v === "lib") return { view: "lib", source: a, repo: b || null };
  if (v === "s") return { view: "story", source: a, key: b };
  if (v === "r") return { view: "read", source: a, key: b, idx: Number(c) || 0 };
  return { view: "home" };
}
const storyHref = (source, key) => `#/s/${enc(source)}/${enc(key)}`;
const readHref = (source, key, idx) => `#/r/${enc(source)}/${enc(key)}/${idx}`;
let renderToken = 0;
async function route() {
  const r = parseHash(); const tok = ++renderToken;
  document.body.classList.remove("side-open");
  renderSidebar();
  const view = $("#view");
  try {
    if (r.view === "home") await renderHome(view, tok);
    else if (r.view === "lib") await renderLib(view, r, tok);
    else if (r.view === "story") await renderStory(view, r, tok);
    else if (r.view === "read") await renderReader(view, r, tok);
  } catch (e) {
    if (tok !== renderToken) return;
    view.innerHTML = `<div class="empty">Lỗi: ${esc(e.message)}<br><br><button class="btn" onclick="location.reload()">Thử lại</button></div>`;
  }
}
window.addEventListener("hashchange", route);
const stale = (tok) => tok !== renderToken;
function setCrumb(html) { $("#crumb").innerHTML = html; }

// ---------------------------------------------------------------- cards
function coverHTML(st, extra = "") {
  const name = st.name || st.folder;
  const img = st.poster ? `<img loading="lazy" referrerpolicy="no-referrer" src="${esc(st.poster)}" alt="" onerror="this.remove()">` : "";
  return `<div class="cover" style="--h:${hashHue(name)}"><div class="ph">${esc(name)}</div>${img}${extra}</div>`;
}
const secHead = (title, href, extra = "") => `<div class="sec-head"><h2>${title}${extra ? ` <small>${extra}</small>` : ""}</h2>${href ? `<a href="${href}">Xem tất cả</a>` : ""}</div>`;
const normTxt = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/gi, "d").toLowerCase();
function repoCard(sid, repo, sub = "") {
  const name = repo.replace(/^Done_/, "");
  return `<a class="card" style="--h:${hashHue(repo)}" href="#/lib/${enc(sid)}/${enc(repo)}" title="${esc(repo)}" data-q="${esc(normTxt(repo))}">
    <div class="cover"><div class="ph">${esc(name)}</div><span class="badge">Repo</span></div>
    <div class="cb"><div class="cat">GitHub · Done_</div><div class="t">${esc(name)}</div>${sub ? `<div class="m">${esc(sub)}</div>` : ""}</div></a>`;
}
function storyCard(source, st) {
  const p = PROG[sKey(source, st.key)];
  const total = st.chapter_files || 0;
  const pct = p && total ? Math.min(100, Math.round(((p.idx + 1) / total) * 100)) : 0;
  const q = normTxt([st.name, st.author, ...(st.genres || []), ...(st.tags || [])].join(" "));
  return `<a class="card" style="--h:${hashHue(st.name || st.folder)}" href="${storyHref(source, st.key)}" title="${esc(st.name)}" data-q="${esc(q)}">
    ${coverHTML(st, `<span class="badge">${fmtNum(total)} chương</span>${pct ? `<div class="prog"><i style="width:${pct}%"></i></div>` : ""}`)}
    <div class="cb">
      <div class="cat">${esc(st.genres?.[0] || st.group?.replace(/^Done_/, "") || "Truyện")}</div>
      <div class="t">${esc(st.name)}</div>
      ${st.author ? `<div class="m">${esc(st.author)}</div>` : ""}
      <div class="stats">${st.status ? `<span>${esc(st.status)}</span>` : ""}${pct ? `<span class="ok">Đã đọc ${pct}%</span>` : ""}</div>
    </div>
  </a>`;
}
function recentHTML() {
  const list = recentList().slice(0, 12);
  if (!list.length) return "";
  return `${secHead("Đang đọc dở", "", String(list.length))}<div class="recent">${list.map((p) => `
    <a class="rcard" href="${readHref(p.source, p.key, p.idx)}">
      ${coverHTML({ name: p.name, poster: p.poster })}
      <div style="min-width:0"><div class="t">${esc(p.name)}</div>
      <div class="m"><b>Chương ${esc(p.n)}</b>${p.total ? ` / ${fmtNum(p.total)}` : ""}${p.para ? ` · đoạn ${p.para + 1}` : ""}</div>
      <div class="m">${new Date(p.ts).toLocaleString("vi-VN", { dateStyle: "short", timeStyle: "short" })}</div></div>
    </a>`).join("")}</div>`;
}

// ---------------------------------------------------------------- home
async function renderHome(view, tok) {
  setCrumb("");
  view.innerHTML = `<section class="hero">
      <h1 class="hero-title"><span>Myth</span><b>Lab</b></h1>
      <p class="hero-slogan">Đọc truyện hay, nghe truyện mọi lúc!</p>
      <div class="hero-search"><input id="hq" placeholder="Tìm truyện theo tên, tác giả, thể loại…" autocomplete="off">
        <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg></div>
      <div class="hero-stats" id="heroStats"></div>
    </section>
    ${recentHTML()}<div id="homeLib">${loadingHTML()}</div>`;
  const hq = $("#hq");
  hq.oninput = () => {
    const n = normTxt(hq.value.trim());
    document.querySelectorAll("#homeLib .card").forEach((c) => c.classList.toggle("hidden", !!n && !(c.dataset.q || "").includes(n)));
  };
  const locals = SOURCES.filter((s) => s.kind === "local" && s.available);
  const ghs = SOURCES.filter((s) => s.kind === "github");
  let html = "", nStories = 0, nRepos = 0;
  for (const s of locals) {
    const stories = await storiesOf(s.id).catch(() => []);
    if (stale(tok)) return;
    if (!stories.length) continue;
    nStories += stories.length;
    html += `${secHead(esc(s.name), `#/lib/${enc(s.id)}`, fmtNum(stories.length) + " truyện")}<div class="grid">${stories.map((st) => storyCard(s.id, st)).join("")}</div>`;
  }
  for (const s of ghs) {
    if (!s.repos?.length) continue;
    nRepos += s.repos.length;
    html += `${secHead(esc(s.name), `#/lib/${enc(s.id)}/*`, s.repos.length + " repo")}
      <div class="grid">${s.repos.map((r) => repoCard(s.id, r.repo, r.pushed_at ? "Cập nhật " + new Date(r.pushed_at).toLocaleDateString("vi-VN") : "")).join("")}</div>`;
  }
  $("#heroStats").innerHTML = [nStories && `${fmtNum(nStories)} truyện trên máy`, nRepos && `${fmtNum(nRepos)} repo GitHub`, "Giọng đọc Edge tự nhiên"]
    .filter(Boolean).map((t) => `<span class="pill"><i></i>${t}</span>`).join("");
  $("#homeLib").innerHTML = html || `<div class="empty">Chưa có truyện. Thêm thư mục vào <code>reader/config.json</code> hoặc chạy <code>python sync_done.py</code>.</div>`;
}

// ---------------------------------------------------------------- library
async function renderLib(view, r, tok) {
  const src = SOURCES.find((s) => s.id === r.source);
  if (!src) throw new Error("Không có nguồn " + r.source);
  setCrumb(`/ <a href="#/lib/${enc(src.id)}">${esc(src.name)}</a>${r.repo ? ` / ${esc(r.repo)}` : ""}`);
  if (src.kind === "github" && !r.repo) {
    view.innerHTML = `<h1 class="h1">${esc(src.name)}</h1><p class="sub">${src.repos?.length || 0} repo. Chọn một repo để xem truyện, hoặc tải tất cả (lần đầu có thể mất 1–2 phút).</p>
      <div class="toolbar"><button class="btn primary" id="loadAll">Tải tất cả truyện</button></div>
      <div class="grid">${(src.repos || []).map((x) => repoCard(src.id, x.repo)).join("")}</div>`;
    $("#loadAll").onclick = () => { location.hash = `#/lib/${enc(src.id)}/*`; };
    return;
  }
  const repo = r.repo === "*" ? null : r.repo;
  view.innerHTML = `<h1 class="h1">${esc(repo || src.name)}</h1><p class="sub" id="libSub">&nbsp;</p>${loadingHTML(src.kind === "github" ? "Đang đọc danh sách truyện từ GitHub…" : "Đang quét thư mục…")}`;
  const stories = await storiesOf(src.id, repo);
  if (stale(tok)) return;
  const sortKey = store.get("mythlab.sort", "name");
  view.innerHTML = `<h1 class="h1">${esc(repo || src.name)}</h1>
    <p class="sub">${fmtNum(stories.length)} truyện · ${fmtNum(stories.reduce((a, s) => a + (s.chapter_files || 0), 0))} chương</p>
    <div class="toolbar">
      <input class="search" id="q" placeholder="Tìm theo tên, thể loại, tag…" autocomplete="off">
      <select id="sort"><option value="name">Tên A→Z</option><option value="chapters">Nhiều chương nhất</option><option value="recent">Đọc gần đây</option></select>
    </div><div class="grid" id="grid"></div>`;
  const q = $("#q"), sortSel = $("#sort"); sortSel.value = sortKey;
  const norm = normTxt;
  const draw = () => {
    const needle = norm(q.value.trim());
    let list = stories.filter((s) => !needle || norm([s.name, s.folder, s.author, ...(s.genres || []), ...(s.tags || []), s.group].join(" ")).includes(needle));
    const sk = sortSel.value;
    list = list.slice().sort((a, b) => sk === "chapters" ? (b.chapter_files || 0) - (a.chapter_files || 0)
      : sk === "recent" ? (PROG[sKey(src.id, b.key)]?.ts || 0) - (PROG[sKey(src.id, a.key)]?.ts || 0)
      : a.name.localeCompare(b.name, "vi"));
    $("#grid").innerHTML = list.map((st) => storyCard(src.id, st)).join("") || `<div class="empty" style="grid-column:1/-1">Không có truyện phù hợp.</div>`;
  };
  q.oninput = draw; sortSel.onchange = () => { store.set("mythlab.sort", sortSel.value); draw(); };
  draw();
}

// ---------------------------------------------------------------- story
const PAGE = 100;
async function renderStory(view, r, tok) {
  view.innerHTML = loadingHTML();
  const st = await storyOf(r.source, r.key);
  if (stale(tok)) return;
  const src = SOURCES.find((s) => s.id === r.source);
  const group = r.key.includes("/") ? r.key.split("/")[0] : null;
  setCrumb(`/ <a href="#/lib/${enc(r.source)}${group && src?.kind === "github" ? "/" + enc(group) : ""}">${esc(group || src?.name || "")}</a> / ${esc(st.name)}`);
  const p = PROG[sKey(r.source, r.key)];
  const chs = st.chapters;
  const words = null;
  view.innerHTML = `<div class="story-head">
      ${coverHTML(st)}
      <div>
        <h1>${esc(st.name)}</h1>
        <div class="meta">
          ${st.author ? `<span>✍ ${esc(st.author)}</span>` : ""}
          <span>${fmtNum(chs.length)} chương${st.declared_chapters && st.declared_chapters != chs.length ? ` (gốc ${fmtNum(st.declared_chapters)})` : ""}</span>
          ${st.status ? `<span>${esc(st.status)}</span>` : ""}
          ${st.link ? `<a href="${esc(st.link)}" target="_blank" rel="noreferrer noopener">Nguồn ↗</a>` : ""}
        </div>
        <div class="chips">${(st.genres || []).map((g) => `<span class="chip accent">${esc(g)}</span>`).join("")}${(st.tags || []).map((t) => `<span class="chip">${esc(t)}</span>`).join("")}</div>
        ${st.synopsis ? `<div class="synopsis" id="syn">${esc(st.synopsis)}</div><button class="linkish" id="synMore">Xem thêm</button>` : ""}
        <div class="actions">
          ${chs.length ? (p ? `<a class="btn primary" href="${readHref(r.source, r.key, p.idx)}">▶ Đọc tiếp · Chương ${esc(p.n)}</a>
            <a class="btn" href="${readHref(r.source, r.key, 0)}">Đọc từ đầu</a>`
          : `<a class="btn primary" href="${readHref(r.source, r.key, 0)}">Đọc từ đầu</a>`) : ""}
          ${chs.length ? `<button class="btn" id="listen"><svg viewBox="0 0 24 24"><path d="M3 14v-2a9 9 0 0 1 18 0v2"/><rect x="2" y="14" width="5" height="7" rx="2"/><rect x="17" y="14" width="5" height="7" rx="2"/></svg>${p ? "Nghe tiếp" : "Nghe truyện"}</button>` : ""}
        </div>
      </div>
    </div>
    <div class="chap-tools"><b>Danh sách chương</b><div class="spacer"></div>
      <input class="search" id="cq" placeholder="Tìm chương (số hoặc tên)…" autocomplete="off">
      <button class="btn" id="rev" title="Đảo thứ tự">⇅</button></div>
    <div class="pager" id="pager"></div><ul class="chap-list" id="clist"></ul>`;
  const syn = $("#syn");
  if (syn) {
    const more = $("#synMore");
    if (syn.scrollHeight <= syn.clientHeight + 4) { syn.classList.add("open"); more.remove(); }
    else more.onclick = () => { syn.classList.toggle("open"); more.textContent = syn.classList.contains("open") ? "Thu gọn" : "Xem thêm"; };
  }
  const lb = $("#listen");
  if (lb) lb.onclick = async () => {
    const idx = p ? p.idx : 0;
    location.hash = readHref(r.source, r.key, idx);
    Player.start({ source: r.source, key: r.key, story: st, idx, para: p && p.idx === idx ? p.para || 0 : 0 });
  };
  let page = p ? Math.floor(p.idx / PAGE) : 0, rev = false;
  const items = chs.map((c, i) => ({ ...c, i }));
  const draw = () => {
    const needle = $("#cq").value.trim().toLowerCase();
    let list = needle ? items.filter((c) => String(c.n) === needle || String(c.n).startsWith(needle) || c.title.toLowerCase().includes(needle)) : items;
    if (rev) list = list.slice().reverse();
    const pages = Math.ceil(list.length / PAGE);
    page = Math.min(page, Math.max(0, pages - 1));
    $("#pager").innerHTML = pages > 1 ? Array.from({ length: pages }, (_, k) => {
      const a = list[k * PAGE], b = list[Math.min(list.length, (k + 1) * PAGE) - 1];
      return `<button data-k="${k}" class="${k === page ? "on" : ""}">${a.n}–${b.n}</button>`;
    }).join("") : "";
    $("#clist").innerHTML = list.slice(page * PAGE, (page + 1) * PAGE).map((c) =>
      `<li><a href="${readHref(r.source, r.key, c.i)}" class="${p && p.idx === c.i ? "cur" : p && c.i < p.idx ? "read" : ""}">
        <span class="n">${c.n}</span><span class="tt">${esc(c.title || "Chương " + c.n)}</span></a></li>`).join("")
      || `<li class="muted pad">Không có chương nào.</li>`;
  };
  $("#pager").onclick = (e) => { const k = e.target.dataset.k; if (k != null) { page = +k; draw(); } };
  $("#cq").oninput = () => { page = 0; draw(); };
  $("#rev").onclick = () => { rev = !rev; page = 0; draw(); };
  draw();
}

// ---------------------------------------------------------------- reader
let READ = null; // {source,key,story,idx,chapter}
let scrollSaveTimer;
async function renderReader(view, r, tok) {
  view.innerHTML = loadingHTML();
  const st = await storyOf(r.source, r.key);
  if (stale(tok)) return;
  const chs = st.chapters;
  if (!chs.length) { view.innerHTML = `<div class="empty">Truyện chưa có chương nào.</div>`; return; }
  const idx = Math.max(0, Math.min(chs.length - 1, r.idx));
  const c = chs[idx];
  const ch = await chapterOf(r.source, r.key, c.file);
  if (stale(tok)) return;
  READ = { source: r.source, key: r.key, story: st, idx, chapter: ch };
  setCrumb(`/ <a href="${storyHref(r.source, r.key)}">${esc(st.name)}</a> / Chương ${c.n}`);
  document.title = `${ch.title || "Chương " + c.n} — ${st.name}`;
  const prev = chs[idx - 1], next = chs[idx + 1];
  const mins = Math.max(1, Math.round(ch.words / 230));
  view.innerHTML = `<article class="reader">
    <div class="ch-head">
      <a class="ch-story" href="${storyHref(r.source, r.key)}">${esc(st.name)}</a>
      <h1 class="ch-title">${esc(ch.title || "Chương " + c.n)}</h1>
      <div class="ch-meta">Chương ${idx + 1}/${fmtNum(chs.length)} · ${fmtNum(ch.words)} chữ · ~${mins} phút đọc</div>
      <div class="ch-actions">
        <button class="btn primary" id="listenCh"><svg viewBox="0 0 24 24"><path d="M3 14v-2a9 9 0 0 1 18 0v2"/><rect x="2" y="14" width="5" height="7" rx="2"/><rect x="17" y="14" width="5" height="7" rx="2"/></svg>Nghe chương này</button>
        <select id="jump" title="Chuyển chương">${chs.map((x, i) => `<option value="${i}" ${i === idx ? "selected" : ""}>Chương ${x.n}${x.title ? ": " + esc(x.title.slice(0, 60)) : ""}</option>`).join("")}</select>
      </div>
    </div>
    <div class="content" id="content">${ch.paragraphs.map((t, i) => `<p data-i="${i}">${esc(t)}</p>`).join("")}</div>
    <nav class="ch-nav">
      ${prev ? `<a class="btn" href="${readHref(r.source, r.key, idx - 1)}">← <span>Chương ${prev.n}</span></a>` : "<span></span>"}
      ${next ? `<a class="btn primary" href="${readHref(r.source, r.key, idx + 1)}"><span>Chương ${next.n}</span> →</a>` : `<span class="ch-end">— Hết truyện —</span>`}
    </nav></article>`;
  $("#jump").onchange = (e) => { location.hash = readHref(r.source, r.key, e.target.value); };
  $("#listenCh").onclick = () => Player.start({ source: r.source, key: r.key, story: st, idx, chapter: ch, para: firstVisiblePara() });
  $("#content").ondblclick = (e) => {
    const pEl = e.target.closest("p[data-i]"); if (!pEl) return;
    window.getSelection()?.removeAllRanges();
    Player.start({ source: r.source, key: r.key, story: st, idx, chapter: ch, para: +pEl.dataset.i });
  };
  // vị trí: nếu đang phát đúng chương này → highlight; nếu không, khôi phục đoạn đã đọc
  const pr = PROG[sKey(r.source, r.key)];
  saveProgress({ source: r.source, key: r.key, name: st.name, poster: st.poster, idx, n: c.n, total: chs.length,
    para: pr && pr.idx === idx ? pr.para || 0 : 0 });
  if (Player.matches(r.source, r.key, idx)) Player.highlight(true);
  else if (pr && pr.idx === idx && pr.para > 0) {
    const el = $(`#content p[data-i="${pr.para}"]`);
    if (el) el.scrollIntoView({ block: "start" }); window.scrollBy(0, -80);
  } else window.scrollTo(0, 0);
  // prefetch chương sau
  if (next) chapterOf(r.source, r.key, next.file).catch(() => {});
}
function firstVisiblePara() {
  const ps = document.querySelectorAll("#content p[data-i]");
  const top = 70;
  for (const p of ps) { const b = p.getBoundingClientRect(); if (b.bottom > top) return +p.dataset.i; }
  return 0;
}
window.addEventListener("scroll", () => {
  if (!READ || parseHash().view !== "read" || Player.matches(READ.source, READ.key, READ.idx)) return;
  clearTimeout(scrollSaveTimer);
  scrollSaveTimer = setTimeout(() => {
    if (!READ || parseHash().view !== "read") return;
    saveProgress({ source: READ.source, key: READ.key, idx: READ.idx, n: READ.story.chapters[READ.idx].n, para: firstVisiblePara() });
  }, 600);
}, { passive: true });

// ---------------------------------------------------------------- player
const RATES = [0.75, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.75, 2];
const Player = (() => {
  const audio = new Audio();
  audio.preload = "auto";
  audio.preservesPitch = true;
  let ctx = null;        // {source,key,story,idx,chapter}
  let chunks = [];       // [{p, text}]
  let pos = 0, playing = false, gen = 0, sleepTimer = null, sleepEndOfChapter = false, retry = 0;
  const prefetched = new Set();
  const el = { bar: $("#player"), title: $("#pTitle"), sub: $("#pSub"), play: $("#pPlay"), icon: $("#pPlayIcon"), prog: $("#pProg") };

  function buildChunks(ch) {
    const out = [];
    const max = S.engine === "edge" ? 1200 : 220;
    if (S.readTitle && ch.title) out.push({ p: -1, text: ch.title.replace(/\s*\[.*?\]\s*$/, "").replace(/^(Chương\s+\d+)\s*[:\-–]\s*/i, "$1. ") });
    ch.paragraphs.forEach((t, i) => {
      if (!/[\p{L}\p{N}]/u.test(t)) return;
      if (t.length <= max) { out.push({ p: i, text: t }); return; }
      const sents = t.match(/[^.!?…。]+[.!?…。]*["'”’)\]]*\s*/gu) || [t];
      let buf = "";
      for (const s of sents) {
        if ((buf + s).length > max && buf) { out.push({ p: i, text: buf.trim() }); buf = ""; }
        if (s.length > max) { for (let k = 0; k < s.length; k += max) out.push({ p: i, text: s.slice(k, k + max) }); }
        else buf += s;
      }
      if (buf.trim()) out.push({ p: i, text: buf.trim() });
    });
    return out;
  }
  const ttsUrl = (text) => `/api/tts?voice=${enc(S.voice)}&text=${enc(text)}`;
  function prefetch(from) {
    if (S.engine !== "edge") return;
    for (let k = from; k < Math.min(chunks.length, from + 2); k++) {
      const u = ttsUrl(chunks[k].text);
      if (prefetched.has(u)) continue;
      prefetched.add(u);
      fetch(u).catch(() => prefetched.delete(u));
    }
  }
  function setIcon() {
    el.icon.innerHTML = playing ? '<path d="M7 5h4v14H7zM13 5h4v14h-4z"/>' : '<path d="M8 5l11 7-11 7z"/>';
    el.play.setAttribute("aria-label", playing ? "Dừng" : "Phát");
    if ("mediaSession" in navigator) navigator.mediaSession.playbackState = playing ? "playing" : "paused";
  }
  const busy = (b) => el.play.classList.toggle("busy", b);
  function updateUI() {
    if (!ctx) return;
    const c = ctx.story.chapters[ctx.idx];
    el.title.textContent = ctx.chapter?.title || `Chương ${c.n}`;
    el.sub.textContent = `${ctx.story.name} · ${chunks.length ? Math.min(pos + 1, chunks.length) : 0}/${chunks.length} đoạn`;
    el.prog.style.width = chunks.length ? `${(pos / chunks.length) * 100}%` : "0";
    $("#pPrevCh").disabled = ctx.idx <= 0;
    $("#pNextCh").disabled = ctx.idx >= ctx.story.chapters.length - 1;
  }
  function highlight(scroll) {
    document.querySelectorAll("#content p.speaking").forEach((x) => x.classList.remove("speaking"));
    if (!ctx || !READ || !matches(READ.source, READ.key, READ.idx)) return;
    const ch = chunks[pos]; if (!ch || ch.p < 0) return;
    const p = document.querySelector(`#content p[data-i="${ch.p}"]`);
    if (!p) return;
    p.classList.add("speaking");
    if (scroll && S.follow) {
      const b = p.getBoundingClientRect(), vh = innerHeight - (document.body.classList.contains("playing") ? el.bar.offsetHeight : 0);
      if (b.top < 70 || b.bottom > vh - 20) p.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }
  const matches = (source, key, idx) => !!ctx && ctx.source === source && ctx.key === key && ctx.idx === idx;
  function media() {
    if (!("mediaSession" in navigator) || !ctx) return;
    const c = ctx.story.chapters[ctx.idx];
    navigator.mediaSession.metadata = new MediaMetadata({ title: ctx.chapter?.title || `Chương ${c.n}`, artist: ctx.story.name, album: "MythLab Truyện",
      artwork: ctx.story.poster ? [{ src: ctx.story.poster, sizes: "600x900" }] : [] });
  }
  function save() {
    if (!ctx) return;
    const c = ctx.story.chapters[ctx.idx];
    saveProgress({ source: ctx.source, key: ctx.key, name: ctx.story.name, poster: ctx.story.poster, idx: ctx.idx, n: c.n,
      total: ctx.story.chapters.length, para: Math.max(0, chunks[pos]?.p ?? 0) });
  }

  function speak() {
    const my = ++gen;
    if (pos >= chunks.length) return chapterEnd();
    updateUI(); highlight(true); save();
    const text = chunks[pos].text;
    if (S.engine === "edge" && TTS_INFO.edge) {
      busy(true);
      audio.src = ttsUrl(text);
      audio.playbackRate = S.rate;
      audio.play().then(() => { if (my === gen) { busy(false); retry = 0; edgeFails = 0; } }).catch((e) => {
        if (my !== gen || e.name === "AbortError") return;
        busy(false);
        if (e.name === "NotAllowedError") { playing = false; setIcon(); toast("Nhấn ▶ để bắt đầu phát"); return; }
        onError();
      });
      prefetch(pos + 1);
    } else {
      if (!("speechSynthesis" in window)) { toast("Trình duyệt không hỗ trợ đọc"); return stop(); }
      speakBrowser(text, my);
    }
  }
  // đọc 1 đoạn bằng Web Speech API của trình duyệt; xong thì sang đoạn kế
  function speakBrowser(text, my) {
    speechSynthesis.cancel();
    const pieces = text.length > 230 ? (text.match(/[^.!?…,;:]+[.!?…,;:]*\s*/gu) || [text]).reduce((a, s) => {
      if (a.length && (a[a.length - 1] + s).length <= 230) a[a.length - 1] += s; else a.push(s); return a; }, []) : [text];
    const vs = speechSynthesis.getVoices();
    const voice = vs.find((v) => v.voiceURI === S.browserVoice) || vs.find((v) => /^vi/i.test(v.lang) && /natural|online/i.test(v.name))
      || vs.find((v) => /^vi/i.test(v.lang)) || null;
    pieces.forEach((piece, k) => {
      const u = new SpeechSynthesisUtterance(piece);
      u.lang = "vi-VN"; u.rate = S.rate; u.voice = voice;
      if (k === pieces.length - 1) u.onend = () => { if (my === gen && playing) { pos++; speak(); } };
      u.onerror = (ev) => {
        if (my === gen && playing && ev.error !== "interrupted" && ev.error !== "canceled") { speechSynthesis.cancel(); pos++; speak(); }
      };
      speechSynthesis.speak(u);
    });
    busy(false);
  }
  let edgeFails = 0;
  function onError() {
    if (!playing) return;
    if (retry < 1) { retry++; setTimeout(() => playing && speak(), 1500); return; }
    retry = 0; edgeFails++;
    const canBrowser = "speechSynthesis" in window && speechSynthesis.getVoices().some((v) => /^vi/i.test(v.lang));
    if (edgeFails >= 3 && canBrowser) {
      edgeFails = 0; S.engine = "browser"; saveS(); document.querySelectorAll("#sEngine button").forEach((b) => b.classList.toggle("on", b.dataset.v === S.engine)); fillVoices();
      toast("Dịch vụ giọng Edge đang lỗi — đã chuyển sang giọng của trình duyệt", 4500);
      return speak();
    }
    if (canBrowser) { toast("Đoạn này đọc bằng giọng trình duyệt (Edge TTS lỗi)"); return speakBrowser(chunks[pos].text, ++gen); }
    toast("Không tạo được giọng đọc cho đoạn này — bỏ qua");
    pos++; speak();
  }
  audio.addEventListener("ended", () => { if (playing) { pos++; speak(); } });
  audio.addEventListener("error", () => { if (playing && audio.src) { busy(false); onError(); } });
  audio.addEventListener("waiting", () => playing && busy(true));
  audio.addEventListener("playing", () => busy(false));

  async function chapterEnd() {
    if (sleepEndOfChapter) { sleepEndOfChapter = false; $("#pSleep").value = "0"; stop(); toast("Đã hết chương — dừng theo hẹn giờ"); return; }
    if (!S.autoNext || ctx.idx >= ctx.story.chapters.length - 1) {
      stop(); pos = Math.max(0, chunks.length - 1); updateUI();
      toast(ctx.idx >= ctx.story.chapters.length - 1 ? "Đã nghe hết truyện" : "Hết chương");
      return;
    }
    await gotoChapter(ctx.idx + 1, 0, true);
  }
  async function gotoChapter(idx, para = 0, autoplay = playing) {
    const my = ++gen;
    stopAudio();
    const c = ctx.story.chapters[idx];
    busy(true);
    let ch;
    try { ch = await chapterOf(ctx.source, ctx.key, c.file); }
    catch (e) { busy(false); toast("Lỗi tải chương: " + e.message); playing = false; setIcon(); return; }
    if (my !== gen) return;
    busy(false);
    ctx.idx = idx; ctx.chapter = ch;
    chunks = buildChunks(ch);
    pos = Math.max(0, chunks.findIndex((x) => x.p >= para)); if (pos < 0) pos = 0;
    media();
    // nếu đang xem chương cũ của cùng truyện trong reader → đi theo
    const r = parseHash();
    if (r.view === "read" && r.source === ctx.source && r.key === ctx.key && r.idx !== idx) location.hash = readHref(ctx.source, ctx.key, idx);
    playing = autoplay; setIcon();
    if (autoplay) speak(); else { updateUI(); highlight(true); }
  }
  function stopAudio() {
    audio.pause(); audio.removeAttribute("src"); audio.load();
    if ("speechSynthesis" in window) speechSynthesis.cancel();
  }
  function stop() { gen++; playing = false; stopAudio(); busy(false); setIcon(); }

  async function start({ source, key, story, idx, chapter, para = 0 }) {
    stop();
    ctx = { source, key, story, idx, chapter: chapter || null };
    document.body.classList.add("playing"); el.bar.classList.remove("hidden");
    if (!chapter) return gotoChapter(idx, para, true);
    chunks = buildChunks(chapter);
    pos = Math.max(0, chunks.findIndex((x) => x.p >= para));
    media(); playing = true; setIcon(); speak();
  }
  function toggle() {
    if (!ctx) {
      if (READ) return start({ ...READ, para: firstVisiblePara() });
      return;
    }
    if (playing) { stop(); updateUI(); highlight(false); }
    else {
      playing = true; setIcon();
      if (S.engine === "edge" && audio.src && audio.paused && audio.currentTime > 0 && !audio.ended) { gen++; const my = gen; audio.play().catch(() => my === gen && speak()); }
      else speak();
    }
  }
  function step(d) {
    if (!ctx) return;
    pos = Math.max(0, Math.min(chunks.length - 1, pos + d));
    if (playing) speak(); else { updateUI(); highlight(true); save(); }
  }
  function close() { stop(); ctx = null; chunks = []; el.bar.classList.add("hidden"); document.body.classList.remove("playing"); highlight(false); clearSleep(); }
  function clearSleep() { clearTimeout(sleepTimer); sleepTimer = null; sleepEndOfChapter = false; }
  function setSleep(min) {
    clearSleep();
    if (min === -1) { sleepEndOfChapter = true; toast("Sẽ dừng khi hết chương"); }
    else if (min > 0) {
      sleepTimer = setTimeout(() => { stop(); updateUI(); $("#pSleep").value = "0"; toast("Đã dừng theo hẹn giờ"); }, min * 60000);
      toast(`Sẽ dừng sau ${min} phút`);
    }
  }
  function rateChanged() {
    audio.playbackRate = S.rate;
    if (S.engine === "browser" && playing) speak();
  }
  function engineChanged() {
    const was = playing; stop();
    if (ctx?.chapter) { const p = chunks[pos]?.p ?? 0; chunks = buildChunks(ctx.chapter); pos = Math.max(0, chunks.findIndex((x) => x.p >= p)); }
    prefetched.clear();
    if (was) { playing = true; setIcon(); speak(); }
  }

  // controls
  el.play.onclick = toggle;
  $("#pBack").onclick = () => step(-1);
  $("#pFwd").onclick = () => step(1);
  $("#pPrevCh").onclick = () => ctx && ctx.idx > 0 && gotoChapter(ctx.idx - 1, 0, playing);
  $("#pNextCh").onclick = () => ctx && ctx.idx < ctx.story.chapters.length - 1 && gotoChapter(ctx.idx + 1, 0, playing);
  $("#pClose").onclick = close;
  $("#pSleep").onchange = (e) => setSleep(+e.target.value);
  el.title.onclick = () => { if (ctx) location.hash = readHref(ctx.source, ctx.key, ctx.idx); };
  if ("mediaSession" in navigator) {
    const ms = navigator.mediaSession;
    ms.setActionHandler("play", () => !playing && toggle());
    ms.setActionHandler("pause", () => playing && toggle());
    ms.setActionHandler("nexttrack", () => $("#pNextCh").click());
    ms.setActionHandler("previoustrack", () => $("#pPrevCh").click());
    try { ms.setActionHandler("seekforward", () => step(1)); ms.setActionHandler("seekbackward", () => step(-1)); } catch { /* */ }
  }
  return { start, toggle, step, close, highlight, matches, rateChanged, engineChanged, get active() { return !!ctx; },
    get chapterIdx() { return ctx?.idx; }, gotoChapter: (i) => ctx && gotoChapter(i, 0, playing) };
})();

// ---------------------------------------------------------------- settings UI
function bindSeg(id, key, after) {
  const seg = $(id);
  const paint = () => seg.querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.v === String(S[key])));
  seg.onclick = (e) => { const v = e.target.dataset.v; if (!v) return; S[key] = v; saveS(); paint(); applyS(); after?.(); };
  paint();
}
function bindRange(id, key, fmt) {
  const inp = $(id), lbl = $(id + "V");
  inp.value = S[key]; lbl.textContent = fmt(S[key]);
  inp.oninput = () => { S[key] = +inp.value; lbl.textContent = fmt(S[key]); saveS(); applyS(); };
}
function bindCheck(id, key) { const c = $(id); c.checked = !!S[key]; c.onchange = () => { S[key] = c.checked; saveS(); }; }
async function fillVoices() {
  const sel = $("#sVoice");
  if (S.engine === "edge") {
    const j = await api("voices").catch(() => ({ voices: [] }));
    const vs = j.voices || [];
    sel.innerHTML = vs.map((v) => `<option value="${esc(v.id)}">${esc(v.name.replace(/^Microsoft\s+/, "").replace(/ Online \(Natural\)/, ""))} — ${esc(v.id)}</option>`).join("");
    if (!vs.some((v) => v.id === S.voice) && vs[0]) S.voice = vs[0].id;
    sel.value = S.voice;
    sel.onchange = () => { S.voice = sel.value; saveS(); Player.engineChanged(); };
  } else {
    const load = () => {
      const vs = speechSynthesis.getVoices();
      const vi = vs.filter((v) => /^vi/i.test(v.lang));
      const list = vi.length ? vi : vs;
      sel.innerHTML = (vi.length ? "" : `<option value="">(Không có giọng tiếng Việt — cài thêm trong Windows)</option>`) +
        list.map((v) => `<option value="${esc(v.voiceURI)}">${esc(v.name)} (${esc(v.lang)})</option>`).join("");
      sel.value = S.browserVoice || (vi[0]?.voiceURI ?? "");
    };
    load(); if ("speechSynthesis" in window) speechSynthesis.onvoiceschanged = load;
    sel.onchange = () => { S.browserVoice = sel.value; saveS(); Player.engineChanged(); };
  }
}
function initSettings() {
  bindSeg("#sTheme", "theme");
  bindSeg("#sFont", "font");
  bindSeg("#sEngine", "engine", () => {
    if (S.engine === "edge" && !TTS_INFO.edge) { toast("Server chưa có edge-tts (pip install edge-tts)"); S.engine = "browser"; saveS(); bindSeg("#sEngine", "engine"); }
    fillVoices(); Player.engineChanged();
  });
  bindRange("#sSize", "size", (v) => v + "px");
  bindRange("#sLine", "line", (v) => Number(v).toFixed(1));
  bindRange("#sWidth", "width", (v) => v + "px");
  bindCheck("#sAutoNext", "autoNext"); bindCheck("#sFollow", "follow"); bindCheck("#sReadTitle", "readTitle");
  fillVoices();
  const rate = $("#pRate");
  rate.innerHTML = RATES.map((r) => `<option value="${r}">${r}×</option>`).join("");
  rate.value = String(S.rate);
  rate.onchange = () => { S.rate = +rate.value; saveS(); Player.rateChanged(); };
  const dr = $("#settings");
  $("#btnSettings").onclick = () => dr.classList.toggle("hidden");
  $("#sClose").onclick = () => dr.classList.add("hidden");
  $("#btnMenu").onclick = () => document.body.classList.toggle("side-open");
  $("#scrim").onclick = () => document.body.classList.remove("side-open");
}

// ---------------------------------------------------------------- keys
document.addEventListener("keydown", (e) => {
  if (e.target.closest("input, select, textarea") || e.ctrlKey || e.metaKey || e.altKey) return;
  const r = parseHash();
  if (e.key === " " && (r.view === "read" || Player.active)) { e.preventDefault(); Player.toggle(); }
  else if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && r.view === "read" && READ) {
    const d = e.key === "ArrowRight" ? 1 : -1, ni = READ.idx + d;
    if (ni < 0 || ni >= READ.story.chapters.length) return;
    if (e.shiftKey && Player.active) Player.gotoChapter(Player.chapterIdx + d);
    else location.hash = readHref(READ.source, READ.key, ni);
  } else if (e.key === "j") Player.step(1);
  else if (e.key === "k") Player.step(-1);
  else if (e.key === "Escape") { $("#settings").classList.add("hidden"); document.body.classList.remove("side-open"); }
});

// ---------------------------------------------------------------- boot
(async () => {
  initSettings();
  try { await loadSources(); } catch (e) { $("#sources").innerHTML = `<div class="pad err">${esc(e.message)}</div>`; }
  if (!TTS_INFO.edge) bindSeg("#sEngine", "engine");
  route();
})();
