/* MythLab — ML.ServerBackend: gọi /api/* của server.py (cùng máy hoặc qua URL + key) */
(function () {
  "use strict";
  const ML = (window.ML = window.ML || {});

  const norm = (p) => "/" + String(p || "").replace(/^\/+/, "").replace(/^api\//, "");

  ML.ServerBackend = function (base = "", key = "") {
    base = String(base || "").replace(/\/+$/, "");
    const headers = key ? { "X-MythLab-Key": key } : {};
    async function get(path, { timeout = 0 } = {}) {
      const ctl = timeout && typeof AbortController !== "undefined" ? new AbortController() : null;
      const t = ctl ? setTimeout(() => ctl.abort(), timeout) : 0;
      try {
        const r = await fetch(base + "/api" + norm(path), { headers, signal: ctl?.signal });
        const j = await r.json().catch(() => ({ error: `HTTP ${r.status}` }));
        if (!r.ok || j.error) throw Object.assign(new Error(j.error || `HTTP ${r.status}`), { status: r.status, json: j });
        return j;
      } finally { clearTimeout(t); }
    }
    function ttsUrl({ text, voice, rate, pitch } = {}) {
      // thứ tự tham số giống app.js cũ (voice, text) để cache audio/SW không bị lệch
      let u = `${base}/api/tts?voice=${encodeURIComponent(voice || "vi-VN-HoaiMyNeural")}&text=${encodeURIComponent(text || "")}`;
      // rate/pitch của edge-tts là số nguyên (% / Hz); giá trị |v| <= 4 là hệ số (1×, 1.5×) của <audio> → bỏ qua
      const edgeInt = (v) => Number.isInteger(v) && Math.abs(v) > 4;
      if (edgeInt(rate)) u += `&rate=${rate}`;
      if (edgeInt(pitch)) u += `&pitch=${pitch}`;
      if (key) u += `&k=${encodeURIComponent(key)}`;
      return u;
    }
    // dò nhanh: route lạ trả JSON (404 "không có API này") ngay cả khi /api/sources đang chậm vì gọi GitHub
    async function ping(timeout = 5000) {
      const ctl = typeof AbortController !== "undefined" ? new AbortController() : null;
      const t = ctl ? setTimeout(() => ctl.abort(), timeout) : 0;
      try {
        const r = await fetch(base + "/api/ping", { headers, signal: ctl?.signal });
        return r.status !== 401 && r.status !== 403 && /json/i.test(r.headers.get("Content-Type") || "") && !!(await r.json());
      } catch { return false; } finally { clearTimeout(t); }
    }
    // ảnh bìa: /api/cover của server (ảnh trong thư mục truyện hoặc poster đã cache); không có thì poster gốc
    function coverUrl(st) {
      const c = st && st.cover;
      if (typeof c === "string" && c.startsWith("/api/")) return base + c + (key ? `&k=${encodeURIComponent(key)}` : "");
      const u = (st && (c || st.poster)) || "";
      return /^https?:\/\//i.test(u) ? u : null;
    }
    return { kind: "server", base, key, get, ttsUrl, coverUrl, ping };
  };
})();
