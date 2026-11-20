/* MythLab — cài đặt đọc/nghe: schema, lưu trữ, áp CSS vars */
"use strict";
window.ML = window.ML || {};
(() => {
  const KEY = "mythlab.settings";
  const store = ML.store || {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* ignore */ } },
  };
  const native = !!window.Capacitor;
  const DEF = {
    theme: "light", font: "literata", weight: 400, size: 20, line: 1.8, letter: 0, word: 0, align: "justify", indent: 0, paraGap: 1,
    margin: 0, width: 720, dayPreset: "default", nightPreset: "default", readMode: "scroll", tapZones: true, brightness: 1,
    engine: native ? "native" : "edge", voice: "vi-VN-HoaiMyNeural", nativeVoice: "", browserVoice: "", rate: 1, pitch: 1,
    autoNext: true, follow: true, readTitle: true, ttsClean: true, ttsChapterCue: true, keepAwake: true,
  };
  // [min, max] cho khoá số; margin 0 = tự động (giữ padding mặc định của .reader)
  const RANGE = { weight: [300, 700], size: [14, 34], line: [1.3, 2.6], letter: [-0.5, 2], word: [0, 8], indent: [0, 2], paraGap: [0, 2],
    margin: [0, 64], width: [480, 1100], brightness: [0.3, 1], rate: [0.5, 3], pitch: [0.5, 2] };
  const ENUM = { theme: ["light", "sepia", "dark", "auto"], align: ["left", "justify"], readMode: ["scroll", "page"], engine: ["edge", "browser", "native"] };
  const presets = {
    day: [
      { id: "default", label: "Mặc định" },
      { id: "trang", label: "Trắng", bg: "#ffffff", fg: "#1f2328", accent: "#0d9488" },
      { id: "giay", label: "Giấy", bg: "#f4ecd8", fg: "#3b2f22", accent: "#0f766e" },
      { id: "xam", label: "Xám", bg: "#e9e9e9", fg: "#222222", accent: "#0f766e" },
      { id: "xanh", label: "Xanh dịu", bg: "#dfeedd", fg: "#22311f", accent: "#2e7d32" },
      { id: "hong", label: "Hồng nhạt", bg: "#f6e7e7", fg: "#3a2626", accent: "#b4495a" },
    ],
    night: [
      { id: "default", label: "Mặc định" },
      { id: "den", label: "Đen", bg: "#000000", fg: "#c8c8c8", accent: "#2dd4bf" },
      { id: "than", label: "Than", bg: "#1f2937", fg: "#e5e7eb", accent: "#5eead4" },
      { id: "nau", label: "Nâu tối", bg: "#2b2118", fg: "#e6d6bd", accent: "#e0a96d" },
      { id: "xanhdem", label: "Xanh đêm", bg: "#0f1b2a", fg: "#cfdcec", accent: "#7cc4ff" },
    ],
  };

  function norm(k, v) {
    const d = DEF[k];
    if (k in RANGE) {
      const n = Number(v);
      return Number.isFinite(n) ? Math.min(RANGE[k][1], Math.max(RANGE[k][0], n)) : d;
    }
    if (k in ENUM) return ENUM[k].includes(v) ? v : d;
    if (typeof d === "boolean") return !!v;
    if (k === "dayPreset" || k === "nightPreset") return presets[k === "dayPreset" ? "day" : "night"].some((p) => p.id === v) ? v : "default";
    return v == null ? d : v;
  }

  // chuyển dữ liệu từ tên cũ (XLab) — app.js cũng làm, nhưng settings.js chạy trước
  try {
    const old = localStorage.getItem("xlab.settings");
    if (old != null && localStorage.getItem(KEY) == null) localStorage.setItem(KEY, old);
  } catch { /* ignore */ }
  const saved = store.get(KEY, {}) || {};
  const S = Object.assign({}, DEF, saved);
  if (!S.ui2) { if (S.theme === "sepia") S.theme = "light"; S.ui2 = 1; }
  if (S.font === "serif") S.font = "literata";
  else if (S.font === "sans") S.font = "inter";
  if (S.engine === "native" && !native) S.engine = "edge";
  for (const k of Object.keys(DEF)) S[k] = norm(k, S[k]);
  const save = () => store.set(KEY, S);
  save();

  const listeners = new Set();
  const mq = window.matchMedia ? matchMedia("(prefers-color-scheme: dark)") : null;
  const isDark = () => S.theme === "dark" || (S.theme === "auto" && !!mq?.matches);

  function fontStack(id) {
    if (String(id).startsWith("local:")) return `"${String(id).slice(6).replace(/"/g, "")}", "Literata", Georgia, serif`;
    return ML.fonts?.cssStack?.(id) || "";
  }
  function apply(root = document.documentElement) {
    const st = root.style, set = (k, v) => (v === "" || v == null ? st.removeProperty(k) : st.setProperty(k, v));
    root.dataset.theme = S.theme;
    root.dataset.readmode = S.readMode;
    root.dataset.tapzones = S.tapZones ? "on" : "off";
    set("--read-size", S.size + "px");
    set("--read-line", S.line);
    set("--read-width", S.width + "px");
    set("--font-read", fontStack(S.font));
    set("--read-weight", S.weight);
    set("--read-letter", S.letter + "px");
    set("--read-word", S.word + "px");
    set("--read-align", S.align);
    set("--read-indent", S.indent + "em");
    set("--read-gap", S.paraGap + "em");
    set("--read-margin", S.margin > 0 ? S.margin + "px" : "");
    if (S.margin > 0) root.dataset.margin = "1"; else delete root.dataset.margin;
    const dark = isDark();
    const p = presets[dark ? "night" : "day"].find((x) => x.id === S[dark ? "nightPreset" : "dayPreset"]) || {};
    set("--read-bg", p.bg); set("--read-fg", p.fg); set("--read-accent", p.accent);
    set("--brightness", S.brightness);
    if (document.body && !document.getElementById("dim")) {
      const d = document.createElement("div"); d.id = "dim"; d.setAttribute("aria-hidden", "true"); document.body.appendChild(d);
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta && root === document.documentElement) meta.content = getComputedStyle(root).getPropertyValue("--bg").trim() || "#ffffff";
  }
  const emit = (k, v) => listeners.forEach((fn) => { try { fn(k, v); } catch (e) { console.error(e); } });
  function set(k, v) {
    const nv = norm(k, v);
    if (S[k] === nv) return;
    S[k] = nv; save(); apply(); emit(k, nv);
  }
  function reset() {
    const changed = Object.keys(DEF).filter((k) => S[k] !== DEF[k]);
    Object.assign(S, DEF); save(); apply();
    changed.forEach((k) => emit(k, S[k]));
  }
  mq?.addEventListener?.("change", () => S.theme === "auto" && apply());

  ML.settings = { DEF, S, RANGE, presets, isDark, fontStack, get: (k) => S[k], set, apply, reset, save,
    onChange(fn) { listeners.add(fn); return () => listeners.delete(fn); } };
  apply();
})();
