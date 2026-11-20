/* MythLab — ML.backend: chọn nguồn dữ liệu (server cùng origin → server theo URL → GitHub token → none) */
(function () {
  "use strict";
  const ML = (window.ML = window.ML || {});

  let impl = null;

  const backend = (ML.backend = {
    kind: "none",
    async init() {
      impl = null; backend.kind = "none";
      const loc = typeof location !== "undefined" ? location : null;
      if (loc && /^https?:$/.test(loc.protocol) && !window.Capacitor) {
        const b = ML.ServerBackend("");
        if (await b.ping(5000)) impl = b;
      }
      const srv = ML.store.get("mythlab.server", null);
      if (!impl && srv && srv.url) {
        const b = ML.ServerBackend(srv.url, srv.key || "");
        if (await b.ping(6000)) impl = b;
      }
      const tok = ML.store.get("mythlab.ghToken", "");
      if (!impl && tok) impl = ML.GitHubBackend(tok, ML.store.get("mythlab.ghSource", {}) || {});
      backend.kind = impl ? impl.kind : "none";
      return backend.kind;
    },
    get(path) {
      if (!impl) return Promise.reject(Object.assign(new Error("Chưa cấu hình nguồn dữ liệu (server hoặc GitHub token)"), { status: 503 }));
      return impl.get("/" + String(path || "").replace(/^\/+/, ""));
    },
    ttsUrl(opts) { return impl && impl.kind === "server" ? impl.ttsUrl(opts || {}) : null; },
    testToken(token) {
      if (!token) return Promise.resolve({ ok: false, login: null, repos: 0, rateRemaining: null, error: "Chưa nhập token" });
      return ML.GitHubBackend(token, ML.store.get("mythlab.ghSource", {}) || {}).testToken();
    },
    get impl() { return impl; },
  });
})();
