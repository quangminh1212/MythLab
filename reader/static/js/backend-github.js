/* MythLab — ML.GitHubBackend: bản JS của GitHubProvider (server.py), đọc repo Done_* qua api.github.com.
   Cache: trees theo tree sha, blobs theo blob sha (IndexedDB), ETag trong meta. Tối đa 4 request song song. */
(function () {
  "use strict";
  const ML = (window.ML = window.ML || {});
  const API = "https://api.github.com";
  const TTL = 600e3;
  const REASON = { 401: "Unauthorized", 403: "Forbidden", 404: "Not Found", 409: "Conflict", 422: "Unprocessable Entity", 429: "Too Many Requests" };

  let active = 0;
  const waiting = [];
  const acquire = () => (active < 4 ? (active++, Promise.resolve()) : new Promise((r) => waiting.push(r)));
  const release = () => { const n = waiting.shift(); if (n) n(); else active--; };

  let lastRate = null;
  let rateToastAt = 0;
  function noteRate(r) {
    const rem = r.headers.get("X-RateLimit-Remaining");
    if (rem == null) return;
    lastRate = +rem;
    if (lastRate < 100 && Date.now() - rateToastAt > 60e3) {
      rateToastAt = Date.now();
      const reset = new Date(+r.headers.get("X-RateLimit-Reset") * 1000);
      const hm = isNaN(reset) ? "" : ` (đặt lại lúc ${reset.toTimeString().slice(0, 5)})`;
      window.ML.toast?.(`GitHub: chỉ còn ${lastRate} lượt gọi API${hm}`);
    }
  }
  const err = (status, msg, extra) => Object.assign(new Error(msg), { status }, extra);
  const isNetErr = (e) => e && !e.ghStatus && (e.name === "TypeError" || e.name === "AbortError");
  const segs = (s) => String(s).split("/").map(encodeURIComponent).join("/");
  const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  // ảnh bìa trong thư mục truyện: cover.* > poster.* > folder.* > thumb.* > ảnh bất kỳ (như pick_cover của server.py)
  const IMG_RE = /\.(jpe?g|png|webp|gif|avif)$/i;
  const coverRank = (f) => { const i = ["cover", "poster", "folder", "thumb"].indexOf(f.replace(IMG_RE, "").toLowerCase()); return i < 0 ? 9 : i; };
  const betterCover = (a, b) => !b || coverRank(a) < coverRank(b) || (coverRank(a) === coverRank(b) && a < b);
  const TREE_V = 2; // tăng khi đổi cấu trúc tóm tắt cây

  ML.GitHubBackend = function (token, { owner = "", prefix = "Done_", sid = "gh0" } = {}) {
    const T = ML.textutil;
    const self = { kind: "github", sid, owner, prefix, name: `GitHub ${owner || "(tôi)"}/${prefix}*` };

    async function gh(url, { raw = false, bin = false, etag = null } = {}) {
      await acquire();
      try {
        const headers = { Accept: raw ? "application/vnd.github.raw" : "application/vnd.github+json" };
        const full = url.startsWith("http") ? url : API + url;
        if (!full.startsWith(API + "/")) throw err(400, "URL GitHub không hợp lệ");
        if (token) headers.Authorization = `Bearer ${token}`;
        if (etag) headers["If-None-Match"] = etag;
        const r = await fetch(full, { headers, cache: "no-store" });
        noteRate(r);
        const res = { status: r.status, etag: r.headers.get("ETag"), link: r.headers.get("Link") || "" };
        if (r.status === 304) return res;
        if (!r.ok) {
          const reason = r.statusText || REASON[r.status] || "Error";
          throw err(502, `GitHub ${r.status}: ${reason}`, { ghStatus: r.status });
        }
        res.body = bin ? await r.blob() : raw ? await r.text() : await r.json(); // text(): UTF-8, bỏ BOM, lỗi → U+FFFD (như utf-8-sig/replace)
        return res;
      } finally { release(); }
    }

    // JSON nhỏ có ETag (304 không tốn hạn mức); mất mạng → dùng bản đã lưu
    async function ghCached(url) {
      const mk = "etag:" + fp + ":" + url;
      const c = await ML.idb.get("meta", mk);
      let r;
      try { r = await gh(url, { etag: c?.etag }); } catch (e) { if (c && isNetErr(e)) return c; throw e; }
      if (r.status === 304) { if (c) return c; r = await gh(url); }
      if (r.etag) await ML.idb.put("meta", mk, { etag: r.etag, body: r.body, link: r.link });
      return r;
    }

    // dấu vân tay token (FNV-1a) để tách cache theo tài khoản, không lưu token
    let fp = 0x811c9dc5;
    for (const ch of String(token || "")) fp = Math.imul(fp ^ ch.codePointAt(0), 0x01000193) >>> 0;
    fp = fp.toString(16);

    async function ownerName() {
      if (!self.owner) {
        const mk = "login:" + fp;
        let login = await ML.idb.get("meta", mk);
        if (!login) { login = (await ghCached("/user")).body.login; await ML.idb.put("meta", mk, login); }
        self.owner = login;
        self.name = `GitHub ${self.owner}/${prefix}*`;
      }
      return self.owner;
    }

    const REPOS_URL = "/user/repos?per_page=100&affiliation=owner,collaborator,organization_member&sort=full_name";
    let reposP = null, reposAt = 0;
    function repos() {
      if (reposP && Date.now() - reposAt < TTL) return reposP;
      reposAt = Date.now();
      reposP = (async () => {
        const own = await ownerName();
        const mk = `repos:${fp}:${own}:${prefix}`;
        const c = await ML.idb.get("meta", mk);
        if (c && Date.now() - c.at < TTL) return c.list;
        let pages;
        try {
          const first = await ghCached(REPOS_URL);
          pages = [first];
          // có rel="last" → tải các trang còn lại song song; không thì lần theo rel="next"
          const next = /<([^>]+)>;\s*rel="next"/.exec(first.link || ""), last = /<([^>]+)>;\s*rel="last"/.exec(first.link || "");
          const lastN = last && +(/[?&]page=(\d+)/.exec(last[1]) || [])[1];
          if (next && lastN) {
            const urls = [];
            for (let i = 2; i <= lastN; i++) urls.push(next[1].replace(/([?&]page=)\d+/, `$1${i}`));
            pages.push(...(await Promise.all(urls.map(ghCached))));
          } else {
            for (let m = next; m; ) { const p = await ghCached(m[1]); pages.push(p); m = /<([^>]+)>;\s*rel="next"/.exec(p.link || ""); }
          }
        } catch (e) { if (c && isNetErr(e)) return c.list; throw e; }
        const out = [];
        for (const { body } of pages) for (const r of body) {
          if (r.owner.login.toLowerCase() === own.toLowerCase() && r.name.startsWith(prefix))
            out.push({ repo: r.name, branch: r.default_branch || "main", pushed_at: r.pushed_at ?? null, private: r.private ?? null });
        }
        out.sort((a, b) => cmp(a.repo.toLowerCase(), b.repo.toLowerCase()));
        await ML.idb.put("meta", mk, { at: Date.now(), list: out });
        return out;
      })();
      reposP.catch(() => { reposP = null; });
      return reposP;
    }

    // cây repo → tóm tắt {sha, stories: {truyện: {info, n}}} (nhẹ, giữ trong RAM) + danh sách chương từng truyện
    // lưu riêng trong store trees (khoá "<sha>/<truyện>") để không phải giữ cả cây hàng chục nghìn chương trong RAM
    function buildStories(entries) {
      const stories = new Map();
      for (const e of entries) {
        if (e.type !== "blob") continue;
        const parts = e.path.split("/");
        if (parts.length !== 2) continue;
        const [story, fname] = parts;
        if (!stories.has(story)) stories.set(story, { info: null, chapters: [], cover: null });
        const s = stories.get(story);
        if (fname === "info.json") s.info = e.sha;
        else if (IMG_RE.test(fname)) { if (betterCover(fname, s.cover?.[0])) s.cover = [fname, e.sha]; }
        else {
          const p = T.parseChapterName(fname);
          if (p) s.chapters.push([p[0], p[1], fname, e.sha]);
        }
      }
      for (const [k, s] of stories) {
        s.chapters.sort((a, b) => a[0] - b[0] || cmp(a[2], b[2]));
        if (!s.chapters.length && !s.info) stories.delete(k);
      }
      return stories;
    }

    async function treeSlow(own, repo, sha) {
      const top = (await gh(`/repos/${own}/${segs(repo)}/git/trees/${sha}`)).body;
      const subs = await Promise.all(top.tree.filter((t) => t.type === "tree").map(async (t) => {
        const sub = (await gh(`/repos/${own}/${segs(repo)}/git/trees/${t.sha}`)).body;
        return sub.tree.map((e) => ({ ...e, path: `${t.path}/${e.path}` }));
      }));
      return subs.flat();
    }

    async function loadTree(repo, force = false) {
      const mk = "tree:" + repo;
      const c = force ? null : await ML.idb.get("meta", mk);
      if (c && Date.now() - c.at < TTL) { const s = await ML.idb.get("trees", c.sha); if (s?.v === TREE_V) return s; }
      const offline = async (e) => { const s = c && isNetErr(e) && (await ML.idb.get("trees", c.sha)); if (s) return s; throw e; };
      let own, url, r;
      try {
        own = await ownerName();
        const branch = (await repos()).find((x) => x.repo === repo)?.branch || "main";
        url = `/repos/${own}/${segs(repo)}/git/trees/${segs(branch)}?recursive=1`;
        r = await gh(url, { etag: c && c.url === url ? c.etag : null });
      } catch (e) { return offline(e); }
      if (r.status === 304) {
        const s = await ML.idb.get("trees", c.sha);
        if (s?.v === TREE_V) { await ML.idb.put("meta", mk, { ...c, at: Date.now() }); return s; }
        r = await gh(url);
      }
      const sha = r.body.sha;
      let sum = force ? null : await ML.idb.get("trees", sha);
      if (sum?.v !== TREE_V) {
        const stories = buildStories(r.body.truncated ? await treeSlow(own, repo, sha) : r.body.tree || []);
        r = { etag: r.etag }; // bỏ JSON cây lớn khỏi RAM
        sum = { v: TREE_V, sha, stories: Object.create(null) };
        await Promise.all([...stories].map(([k, s]) => {
          sum.stories[k] = { info: s.info, n: s.chapters.length, c: s.cover?.[1] || null };
          return ML.idb.put("trees", `${sha}/${k}`, s.chapters);
        }));
        await ML.idb.put("trees", sha, sum);
      }
      await ML.idb.put("meta", mk, { etag: r.etag, sha, url, at: Date.now() });
      return sum;
    }

    const trees = new Map();
    function tree(repo, force = false) {
      const hit = trees.get(repo);
      if (!force && hit && Date.now() - hit.at < TTL) return hit.p;
      const p = loadTree(repo, force);
      trees.set(repo, { at: Date.now(), p });
      p.catch(() => trees.delete(repo));
      return p;
    }
    const own = (o, k) => (Object.prototype.hasOwnProperty.call(o, k) ? o[k] : undefined);
    // [[n, title, file, sha]] của 1 truyện; mất bản lưu (xoá cache) → tải lại cây
    async function chaptersOf(repo, story) {
      let sum = await tree(repo);
      if (!own(sum.stories, story)) return [];
      let ch = await ML.idb.get("trees", `${sum.sha}/${story}`);
      if (!ch) { sum = await tree(repo, true); ch = own(sum.stories, story) ? await ML.idb.get("trees", `${sum.sha}/${story}`) : []; }
      return ch || [];
    }
    // đọc chương: dùng cây đã lưu nếu có file đó (không cần mạng), không thì tải cây
    async function chaptersForRead(repo, story, file) {
      const c = await ML.idb.get("meta", "tree:" + repo);
      const ch = c && (await ML.idb.get("trees", `${c.sha}/${story}`));
      if (ch && ch.some((x) => x[2] === file)) return ch;
      return chaptersOf(repo, story);
    }

    const blobsP = new Map();
    async function blob(repo, sha) {
      const hit = await ML.idb.get("blobs", sha);
      if (typeof hit === "string") return hit;
      if (!blobsP.has(sha)) {
        const p = (async () => {
          const own = await ownerName();
          const text = (await gh(`/repos/${own}/${segs(repo)}/git/blobs/${sha}`, { raw: true })).body;
          await ML.idb.put("blobs", sha, text);
          return text;
        })();
        blobsP.set(sha, p);
        p.finally(() => blobsP.delete(sha)).catch(() => {});
      }
      return blobsP.get(sha);
    }

    // ảnh bìa trong repo: tải blob khi cần (IndexedDB "blobs", khoá "img:<sha>") → object URL
    const coverUrls = new Map();
    function coverBlobUrl(repo, sha) {
      if (!coverUrls.has(sha)) {
        const p = (async () => {
          let b = await ML.idb.get("blobs", "img:" + sha);
          if (!(b instanceof Blob)) {
            b = (await gh(`/repos/${await ownerName()}/${segs(repo)}/git/blobs/${sha}`, { raw: true, bin: true })).body;
            await ML.idb.put("blobs", "img:" + sha, b);
          }
          return URL.createObjectURL(b);
        })();
        coverUrls.set(sha, p);
        p.catch(() => coverUrls.delete(sha));
      }
      return coverUrls.get(sha);
    }
    // 'cover': poster khi thư mục không có ảnh; có ảnh thì 'cover_sha' → coverUrl() lấy blob (lười)
    const withCover = (st, c) => Object.assign(st, { cover: c ? null : st.poster, cover_sha: c || null });
    function coverUrl(st) { // chuỗi/null; Promise<object URL> nếu ảnh nằm trong repo
      if (st?.cover_sha && st.key) return coverBlobUrl(split(st.key)[0], st.cover_sha);
      return [st?.cover, st?.poster].find((u) => typeof u === "string" && /^https?:\/\//i.test(u)) || null;
    }

    async function infoFor(repo, story) {
      const s = own((await tree(repo)).stories, story);
      if (!s || !s.info) return null;
      try { return JSON.parse(await blob(repo, s.info)); } catch { return null; }
    }

    async function listStories(repo) {
      const list = repo ? [repo] : (await repos()).map((r) => r.repo);
      const parts = await Promise.all(list.map(async (rp) => {
        const t = (await tree(rp)).stories;
        return Promise.all(Object.keys(t).sort(cmp).map(async (story) => withCover({
          key: `${rp}/${story}`, folder: story, group: rp, chapter_files: t[story].n,
          ...T.infoSummary(await infoFor(rp, story), story),
        }, t[story].c)));
      }));
      return parts.flat();
    }

    const split = (key) => { const i = key.indexOf("/"); return i < 0 ? [key, ""] : [key.slice(0, i), key.slice(i + 1)]; };

    async function describe() {
      const d = { id: sid, name: self.name, kind: "github", detail: `${self.owner}/${prefix}*`, available: true };
      try {
        d.repos = await repos();
        d.name = self.name;
        d.detail = `${self.owner}/${prefix}*`;
      } catch (e) { d.available = false; d.error = e.message; }
      return d;
    }

    async function route(path) {
      const u = new URL("/" + String(path || "").replace(/^\/+/, "").replace(/^api\//, ""), "http://x");
      const q = {};
      for (const [k, v] of u.searchParams) if (v !== "") q[k] = v; // parse_qs bỏ giá trị rỗng
      const need = (k) => { if (!(k in q)) throw err(400, `thiếu/không đúng tham số: '${k}'`); return q[k]; };
      const src = () => { const s = need("source"); if (s !== sid) throw err(400, `thiếu/không đúng tham số: '${s}'`); };
      switch (u.pathname.slice(1)) {
        case "sources":
          return { sources: [await describe()], tts: { edge: false, default_voice: "vi-VN-HoaiMyNeural" } };
        case "stories":
          src();
          return { stories: await listStories(q.repo || null) };
        case "story": {
          src();
          const key = need("key");
          const [repo, story] = split(key);
          const info = await infoFor(repo, story);
          const chs = await chaptersOf(repo, story);
          const c = own((await tree(repo)).stories, story)?.c;
          return { ...withCover({ key, source: q.source, ...T.infoSummary(info, key.split("/").pop()) }, c),
            chapters: chs.map((c) => ({ n: c[0], title: c[1], file: c[2] })) };
        }
        case "chapter": {
          src();
          const key = need("key"), file = need("file");
          const [repo, story] = split(key);
          const c = (await chaptersForRead(repo, story, file)).find((ch) => ch[2] === file);
          if (!c) throw err(404, `không tìm thấy: ${file}`);
          return T.chapterJson(await blob(repo, c[3]), file);
        }
        case "voices":
          return { voices: [], edge: false };
        case "tts":
          throw err(503, "Không có server TTS (đang đọc trực tiếp từ GitHub)");
        default:
          throw err(404, "không có API này");
      }
    }

    async function get(path) {
      try { return await route(path); } catch (e) {
        if (e.status) throw e;
        throw err(500, `${e.name || "Error"}: ${e.message}`, { cause: e });
      }
    }

    async function testToken() {
      try {
        const me = await gh("/user");
        if (!self.owner) { self.owner = me.body.login; self.name = `GitHub ${self.owner}/${prefix}*`; }
        const rs = await repos();
        return { ok: true, login: me.body.login, repos: rs.length, rateRemaining: lastRate, error: null };
      } catch (e) {
        return { ok: false, login: null, repos: 0, rateRemaining: lastRate,
          error: e.ghStatus === 401 ? "Token không hợp lệ hoặc đã hết hạn" : e.message };
      }
    }

    return Object.assign(self, { get, ttsUrl: () => null, coverUrl, repos, testToken, describe });
  };
})();
