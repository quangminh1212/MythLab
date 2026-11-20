/* MythLab — ML.textutil: bản JS của các hàm xử lý chữ trong server.py (cùng kết quả với Python) */
(function () {
  "use strict";
  const ML = (window.ML = window.ML || {});

  // \s của Python (str.isspace) — khác \s của JS (\x1c-\x1f, \x85 có; ﻿ không)
  const WS = "\\t-\\r\\x1c-\\x20\\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000";
  const CHAPTER_RE = new RegExp(`^Chương[${WS}]+(\\d+)[${WS}]*[-:.–]?[${WS}]*(.*?)\\.txt$`, "iu");
  const HEADER_RULE = new RegExp(`^[${WS}]*[=\\-_*]{5,}[${WS}]*$`, "u");
  const CHAP_HEAD = new RegExp(`^Chương[${WS}]+\\d+`, "iu");
  const WS_RUN = new RegExp(`[${WS}]+`, "u");

  const escCls = (s) => s.replace(/[\\\]\-^]/g, "\\$&");
  function strip(s, chars) {
    const cls = chars == null ? WS : escCls(chars);
    return s.replace(new RegExp(`^[${cls}]+|[${cls}]+$`, "gu"), "");
  }
  const pyLen = (s) => [...s].length;
  const truthy = (v) => !(v == null || v === false || v === 0 || v === "" || (Array.isArray(v) && !v.length) ||
    (isDict(v) && !Object.keys(v).length));
  const isDict = (v) => v != null && typeof v === "object" && !Array.isArray(v);
  const or = (...vs) => { for (const v of vs) if (truthy(v)) return v; return vs[vs.length - 1]; };
  const get = (o, k) => (Object.prototype.hasOwnProperty.call(o, k) && o[k] !== undefined ? o[k] : null);

  function naturalTitle(raw) {
    return strip(strip(strip(raw), "-:. "));
  }

  function parseChapterName(filename) {
    const m = CHAPTER_RE.exec(filename);
    if (!m) return null;
    return [parseInt(m[1], 10), naturalTitle(m[2])];
  }

  function cleanChapterText(text) {
    text = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n").replace(/^﻿+/, "");
    let lines = text.split("\n");
    let title = null;
    const head = [];
    lines.slice(0, 8).forEach((ln, i) => { if (HEADER_RULE.test(ln)) head.push(i); });
    if (head.length >= 2 && head[1] - head[0] <= 4) {
      const inner = lines.slice(head[0] + 1, head[1]).map((ln) => strip(ln)).filter(Boolean);
      if (inner.length) title = inner.join(" ");
      lines = lines.slice(head[1] + 1);
    }
    const paras = lines.map((ln) => strip(ln.replace(/[ \t]+/g, " "))).filter((p) => p && !HEADER_RULE.test(p));
    if (title == null && paras.length && CHAP_HEAD.test(paras[0]) && pyLen(paras[0]) < 160) title = paras.shift();
    return [title, paras];
  }

  const countWords = (paras) => paras.reduce((n, p) => n + p.split(WS_RUN).filter(Boolean).length, 0);

  function infoSummary(info, fallbackName) {
    info = isDict(info) ? info : {};
    let poster = get(info, "poster");
    if (isDict(poster)) {
      const vals = Object.values(poster);
      poster = or(get(poster, "600"), get(poster, "default"), vals.length ? vals[0] : null);
    }
    const names = (arr) => (Array.isArray(arr) ? arr : []).filter((x) => isDict(x) && truthy(get(x, "name"))).map((x) => x.name);
    let author = get(info, "author");
    if (isDict(author)) author = get(author, "name");
    return {
      name: or(get(info, "name"), fallbackName),
      author,
      synopsis: or(get(info, "synopsis"), get(info, "description"), ""),
      poster: typeof poster === "string" ? poster : null,
      genres: names(get(info, "genres")),
      tags: names(get(info, "tags")),
      status: or(get(info, "status_name"), get(info, "state")),
      declared_chapters: get(info, "chapter_count"),
      link: get(info, "link"),
    };
  }

  // JSON giống route /api/chapter của server.py
  function chapterJson(raw, file) {
    let [title, paras] = cleanChapterText(raw);
    const pn = parseChapterName(file);
    if (!title && pn) title = `Chương ${pn[0]}` + (pn[1] ? `: ${pn[1]}` : "");
    return { title, paragraphs: paras, words: countWords(paras) };
  }

  ML.textutil = { naturalTitle, parseChapterName, cleanChapterText, infoSummary, chapterJson, countWords, pyStrip: strip };
})();
