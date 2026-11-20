/* MythLab — ngăn cài đặt (#settings .drawer-body) */
"use strict";
window.ML = window.ML || {};
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const st = () => ML.settings;
  const say = (m) => (ML.toast || window.toast || console.log)(m);
  const store = () => ML.store || { get: (k, d) => d, set() {}, del() {} };
  const GROUPS = [["serif", "Có chân"], ["sans", "Không chân"], ["system", "Font máy"]];
  const VOICE_KEY = { edge: "voice", browser: "browserVoice", native: "nativeVoice" };
  const SLIDERS = {
    weight: ["Độ đậm", 100, (v) => v],
    size: ["Cỡ chữ", 1, (v) => v + "px"],
    line: ["Giãn dòng", 0.1, (v) => Number(v).toFixed(1)],
    letter: ["Giãn chữ", 0.1, (v) => Number(v).toFixed(1) + "px"],
    word: ["Giãn từ", 0.5, (v) => v + "px"],
    indent: ["Thụt đầu dòng", 0.25, (v) => v + "em"],
    paraGap: ["Cách đoạn", 0.1, (v) => Number(v).toFixed(1) + "em"],
    margin: ["Lề hai bên", 2, (v) => (+v ? v + "px" : "Tự động")],
    width: ["Độ rộng cột", 20, (v) => v + "px"],
    brightness: ["Độ sáng", 0.05, (v) => Math.round(v * 100) + "%"],
    pitch: ["Cao độ giọng", 0.05, (v) => Number(v).toFixed(2)],
  };
  const CHECKS = { autoNext: ["sAutoNext", "Tự chuyển chương khi nghe hết"], follow: ["sFollow", "Tự cuộn theo đoạn đang đọc"],
    readTitle: ["sReadTitle", "Đọc tiêu đề chương"], ttsChapterCue: ["sChapterCue", "Báo “Hết chương” trước khi qua chương mới"],
    ttsClean: ["sTtsClean", "Lọc ký tự lạ trước khi đọc"], keepAwake: ["sKeepAwake", "Giữ màn hình sáng khi nghe"],
    tapZones: ["sTapZones", "Chạm hai bên màn hình để lật trang"] };
  const segIds = { theme: "sTheme", engine: "sEngine", align: "sAlign", readMode: "sReadMode" };
  let body, inited = false, fontList = [];

  const slider = (k) => {
    const [label, step] = SLIDERS[k], [min, max] = st().RANGE[k], id = "s" + k[0].toUpperCase() + k.slice(1);
    return `<label>${label} <span id="${id}V"></span><input type="range" id="${id}" data-k="${k}" min="${min}" max="${max}" step="${step}"></label>`;
  };
  const seg = (k, label, opts) => `<label>${label}<div class="seg" id="${segIds[k]}" data-k="${k}">${opts.map(([v, t]) => `<button type="button" data-v="${v}">${t}</button>`).join("")}</div></label>`;
  const check = (k) => `<label class="row"><input type="checkbox" id="${CHECKS[k][0]}" data-k="${k}"> ${CHECKS[k][1]}</label>`;
  const swatches = (kind) => `<div class="swatches" data-k="${kind}Preset">${st().presets[kind].map((p) =>
    `<button type="button" class="swatch${p.bg ? "" : " def"}" data-v="${p.id}" title="${esc(p.label)}" style="${p.bg ? `--sw-bg:${p.bg};--sw-fg:${p.fg}` : ""}"><i>Aa</i><span>${esc(p.label)}</span></button>`).join("")}</div>`;

  function render() {
    const engines = [["edge", "Edge (tự nhiên)"], ["browser", "Trình duyệt"]];
    if (window.Capacitor) engines.push(["native", "Máy (Android)"]);
    const srv = store().get("mythlab.server", null) || {};
    body.innerHTML = `
    <h4>Giao diện</h4>
    ${seg("theme", "Chế độ", [["light", "Sáng"], ["sepia", "Giấy"], ["dark", "Tối"], ["auto", "Tự động"]])}
    <div class="s-preview content" id="sPreview"><p>Nguyễn Thị Ẩn ngồi bên hiên, ỡ ự ặ — trời về chiều.</p></div>
    <div class="s-label">Màu nền ban ngày</div>${swatches("day")}
    <div class="s-label">Màu nền ban đêm</div>${swatches("night")}
    ${slider("brightness")}
    <h4>Phông chữ</h4>
    <div class="fontpick" id="sFonts"><div class="muted small">Đang tải phông…</div></div>
    ${"queryLocalFonts" in window ? `<button type="button" class="btn s-btn" id="sLocalFonts">Font của máy…</button><select id="sLocalSel" class="hidden"></select>` : ""}
    ${slider("weight")}${slider("size")}${slider("line")}${slider("letter")}${slider("word")}
    <h4>Trình bày</h4>
    ${seg("align", "Căn lề", [["left", "Trái"], ["justify", "Đều hai bên"]])}
    ${slider("indent")}${slider("paraGap")}${slider("margin")}${slider("width")}
    ${seg("readMode", "Kiểu đọc", [["scroll", "Cuộn dọc"], ["page", "Lật trang"]])}
    ${check("tapZones")}
    <h4>Giọng đọc</h4>
    ${seg("engine", "Bộ đọc", engines)}
    <label>Giọng <select id="sVoice"></select></label>
    ${slider("pitch")}
    ${check("autoNext")}${check("follow")}${check("readTitle")}${check("ttsChapterCue")}${check("ttsClean")}${check("keepAwake")}
    <h4>Nguồn dữ liệu</h4>
    <div class="muted small" id="sBackendKind"></div>
    <label>GitHub token
      <div class="s-inline"><input type="password" id="sGhToken" autocomplete="off" spellcheck="false" placeholder="ghp_… / github_pat_…" value="${esc(store().get("mythlab.ghToken", "") || "")}">
      <button type="button" class="btn s-btn" id="sGhShow" title="Hiện / ẩn">Hiện</button><button type="button" class="btn s-btn" id="sGhTest">Kiểm tra</button></div>
    </label>
    <div class="s-status small" id="sGhStatus"></div>
    <label>Máy chủ MythLab (URL)<input type="url" id="sSrvUrl" class="s-input" placeholder="http://192.168.1.10:8765" value="${esc(srv.url || "")}"></label>
    <label>Khoá máy chủ<input type="password" id="sSrvKey" class="s-input" autocomplete="off" value="${esc(srv.key || "")}"></label>
    <div class="s-status small hidden" id="sReloadHint">Đã lưu. <button type="button" class="linkish" id="sReload">Tải lại để áp dụng</button></div>
    <div class="s-actions"><button type="button" class="btn s-btn" id="sClearCache">Xoá bộ nhớ đệm</button><button type="button" class="btn s-btn" id="sReset">Mặc định</button></div>
    <p class="muted small">Mẹo: nhấp đúp vào một đoạn để nghe từ đó. Phím tắt: <kbd>Space</kbd> phát/dừng, <kbd>←</kbd>/<kbd>→</kbd> chương trước/sau (lật trang khi ở kiểu Lật trang), <kbd>J</kbd>/<kbd>K</kbd> đoạn sau/trước.</p>`;
    bind();
    paintAll();
    renderFonts();
    fillVoices();
  }

  function paint(k) {
    const S = st().S;
    if (segIds[k]) document.querySelectorAll(`#${segIds[k]} button`).forEach((b) => b.classList.toggle("on", b.dataset.v === String(S[k])));
    if (SLIDERS[k]) {
      const inp = body.querySelector(`input[type=range][data-k="${k}"]`); if (!inp) return;
      if (document.activeElement !== inp) inp.value = S[k];
      $("#" + inp.id + "V").textContent = SLIDERS[k][2](S[k]);
    }
    if (CHECKS[k]) { const c = $("#" + CHECKS[k][0]); if (c) c.checked = !!S[k]; }
    if (k === "dayPreset" || k === "nightPreset") body.querySelectorAll(`.swatches[data-k="${k}"] button`).forEach((b) => b.classList.toggle("on", b.dataset.v === S[k]));
    if (k === "font") body.querySelectorAll("#sFonts .fontopt").forEach((b) => b.classList.toggle("on", b.dataset.id === S.font));
    if (k === VOICE_KEY[S.engine]) { const sel = $("#sVoice"); if (sel && [...sel.options].some((o) => o.value === S[k])) sel.value = S[k]; }
  }
  const paintAll = () => Object.keys(st().DEF).forEach(paint);
  const kindText = () => { const k = ML.backend?.kind; return k ? `Đang dùng: ${{ server: "máy chủ MythLab", github: "GitHub (trực tiếp)", none: "chưa có nguồn" }[k] || k}` : ""; };

  function bind() {
    body.onclick = (e) => {
      const b = e.target.closest("button"); if (!b) return;
      const box = b.closest(".seg[data-k], .swatches[data-k]");
      if (box && b.dataset.v) return pick(box.dataset.k, b.dataset.v);
      if (b.classList.contains("fontopt")) return st().set("font", b.dataset.id);
    };
    body.oninput = (e) => { const t = e.target; if (t.type === "range" && t.dataset.k) st().set(t.dataset.k, +t.value); };
    body.onchange = (e) => { const t = e.target; if (t.type === "checkbox" && t.dataset.k) st().set(t.dataset.k, t.checked); };
    $("#sVoice").onchange = (e) => st().set(VOICE_KEY[st().S.engine], e.target.value);
    const tok = $("#sGhToken");
    tok.onchange = () => { const v = tok.value.trim(); v ? store().set("mythlab.ghToken", v) : store().del("mythlab.ghToken"); reloadHint(); };
    $("#sGhShow").onclick = (e) => { const show = tok.type === "password"; tok.type = show ? "text" : "password"; e.target.textContent = show ? "Ẩn" : "Hiện"; };
    $("#sGhTest").onclick = testToken;
    const saveSrv = () => {
      const url = $("#sSrvUrl").value.trim().replace(/\/+$/, ""), key = $("#sSrvKey").value.trim();
      url ? store().set("mythlab.server", { url, key }) : store().del("mythlab.server"); reloadHint();
    };
    $("#sSrvUrl").onchange = saveSrv; $("#sSrvKey").onchange = saveSrv;
    $("#sReload").onclick = () => location.reload();
    $("#sClearCache").onclick = async () => {
      try { await ML.idb?.clear(); say("Đã xoá bộ nhớ đệm"); } catch (e) { say("Không xoá được bộ nhớ đệm: " + e.message); }
    };
    $("#sReset").onclick = () => {
      if (!confirm("Đưa toàn bộ cài đặt đọc/nghe về mặc định?")) return;
      st().reset(); paintAll(); fillVoices(); say("Đã đặt lại cài đặt mặc định");
    };
    const lf = $("#sLocalFonts");
    if (lf) lf.onclick = localFonts;
    $("#sBackendKind").textContent = kindText();
  }
  const reloadHint = () => $("#sReloadHint").classList.remove("hidden");

  function pick(k, v) {
    if (k === "engine" && v === "edge" && ML.backend?.kind && ML.backend.ttsUrl?.({ text: "a", voice: st().S.voice, rate: 1, pitch: 1 }) == null) {
      say("Giọng Edge cần máy chủ MythLab (server.py)"); return;
    }
    st().set(k, v);
  }

  async function renderFonts() {
    const box = $("#sFonts"); if (!box) return;
    try { fontList = ML.fonts ? await ML.fonts.available() : []; } catch { fontList = ML.fonts?.list || []; }
    if (!fontList.length) fontList = [{ id: "literata", label: "Literata", group: "serif" }, { id: "inter", label: "Inter", group: "sans" }];
    const S = st().S;
    const extra = String(S.font).startsWith("local:") ? [{ id: S.font, label: S.font.slice(6), group: "system" }] : [];
    const all = fontList.concat(extra);
    box.innerHTML = GROUPS.map(([g, t]) => {
      const fs = all.filter((f) => f.group === g); if (!fs.length) return "";
      return `<div class="s-label">${t}</div><div class="fontgrid">${fs.map((f) =>
        `<button type="button" class="fontopt${f.id === S.font ? " on" : ""}" data-id="${esc(f.id)}" title="${esc(f.label)}${f.license ? " · " + esc(f.license) : ""}" style="font-family:${esc(st().fontStack(f.id))}">${esc(f.label)}</button>`).join("")}</div>`;
    }).join("");
  }
  async function localFonts() {
    const sel = $("#sLocalSel");
    try {
      const fams = [...new Set((await window.queryLocalFonts()).map((f) => f.family))].sort((a, b) => a.localeCompare(b));
      sel.innerHTML = `<option value="">— Chọn font của máy (${fams.length}) —</option>` + fams.map((f) => `<option value="${esc(f)}">${esc(f)}</option>`).join("");
      sel.classList.remove("hidden");
      sel.onchange = () => { if (sel.value) { st().set("font", "local:" + sel.value); renderFonts(); } };
    } catch (e) { say("Không đọc được font của máy: " + e.message); }
  }

  let voiceGen = 0;
  async function fillVoices() {
    const sel = $("#sVoice"); if (!sel) return;
    const my = ++voiceGen, S = st().S, eng = S.engine, key = VOICE_KEY[eng];
    sel.innerHTML = `<option value="">Đang tải giọng…</option>`;
    let vs = [];
    try {
      if (ML.tts?.voices) vs = await ML.tts.voices(eng);
      else if (eng === "edge" && ML.backend?.get) vs = (await ML.backend.get("/voices")).voices || [];
    } catch { vs = []; }
    if (my !== voiceGen) return;
    vs = vs || [];
    const vi = vs.filter((v) => /^vi/i.test(v.lang || v.id || ""));
    const name = (v) => String(v.name || v.id).replace(/^Microsoft\s+/, "").replace(/ Online \(Natural\)/, "");
    const list = eng === "edge" ? vs : vi.concat(vs.filter((v) => !vi.includes(v)));
    sel.innerHTML = (eng !== "edge" && !vi.length ? `<option value="">(Không có giọng tiếng Việt — cài thêm trong hệ điều hành)</option>` : "") +
      list.map((v) => `<option value="${esc(v.id)}">${esc(name(v))}${eng === "edge" ? " — " + esc(v.id) : v.lang ? ` (${esc(v.lang)})` : ""}</option>`).join("");
    if (list.some((v) => v.id === S[key])) sel.value = S[key];
    else if (eng === "edge" && list[0]) { sel.value = list[0].id; st().set(key, list[0].id); }
    else sel.value = vi[0]?.id ?? "";
  }

  async function testToken() {
    const out = $("#sGhStatus"), tok = $("#sGhToken").value.trim();
    if (!tok) { out.textContent = "Nhập token trước."; out.className = "s-status small err"; return; }
    out.textContent = "Đang kiểm tra…"; out.className = "s-status small";
    try {
      const r = await ML.backend.testToken(tok);
      if (!r || !r.ok) throw new Error(r?.error || "Token không hợp lệ");
      out.textContent = `✓ ${r.login || "OK"} · ${r.repos ?? 0} kho truyện${r.rateRemaining != null ? ` · còn ${r.rateRemaining} lượt gọi API` : ""}`;
      out.className = "s-status small ok";
      store().set("mythlab.ghToken", tok);
    } catch (e) { out.textContent = "✗ " + e.message; out.className = "s-status small err"; }
  }

  function init() {
    const dr = $("#settings"); body = dr && $(".drawer-body", dr);
    if (!body) return;
    render();
    const btn = $("#btnSettings"), cls = $("#sClose");
    if (btn) btn.onclick = () => (dr.classList.contains("hidden") ? open() : close());
    if (cls) cls.onclick = close;
    if (inited) return;
    inited = true;
    st().onChange((k) => {
      if (!body) return;
      paint(k);
      if (k === "engine") fillVoices();
    });
    if ("speechSynthesis" in window) speechSynthesis.addEventListener?.("voiceschanged", () => st().S.engine === "browser" && fillVoices());
  }
  function open() {
    const dr = $("#settings"); if (!dr) return;
    if (!body) init();
    dr.classList.remove("hidden");
    const el = $("#sBackendKind"); if (el) el.textContent = kindText();
  }
  function close() { $("#settings")?.classList.add("hidden"); }

  ML.settingsPanel = { init, open, close, refreshVoices: fillVoices };
})();
