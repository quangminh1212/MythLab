package e2e

// The page-side measurement scripts, copied verbatim from the Python originals.

const browseMetricsJS = `
(W) => {
  // W is the configured viewport width: a phone browser widens innerWidth to fit overflowing content,
  // which would hide exactly the overflow this looks for
  const de = document.documentElement;
  const vis = (el) => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < W;
  };
  const label = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).join('.') : '');
  const small = new Map();
  document.querySelectorAll('a, button, select, input, summary, [role=button], [tabindex="0"]').forEach((el) => {
    if (!vis(el) || el.closest('[inert]')) return;
    // WCAG 2.5.8 exception: links inside a sentence
    if (el.tagName === 'A' && getComputedStyle(el).display === 'inline') return;
    if (el.tagName === 'MAIN') return;
    const r = el.getBoundingClientRect();
    if (r.width < 43.5 || r.height < 43.5) {
      const k = label(el);
      if (!small.has(k)) small.set(k, [k, Math.round(r.width), Math.round(r.height), (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 30)]);
    }
  });
  const noname = [];
  document.querySelectorAll('button, a, select, input, summary').forEach((el) => {
    if (!vis(el)) return;
    const has = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || ((el.textContent || '').trim() && el.tagName !== 'SELECT') || (el.labels && el.labels.length);
    if (!has) noname.push(label(el));
  });
  const over = [];
  if (de.scrollWidth > W) {
    document.querySelectorAll('body *').forEach((el) => {
      if (!vis(el) || el.closest('svg')) return;
      const r = el.getBoundingClientRect();
      if (r.right > W + 1) over.push([label(el), Math.round(r.left), Math.round(r.right)]);
    });
  }
  // content cut off at the right edge although the page itself does not scroll (a clipping ancestor hides it);
  // rows inside an intentional horizontal scroller are fine
  const inScroller = (el) => {
    for (let p = el.parentElement; p; p = p.parentElement) {
      const o = getComputedStyle(p).overflowX;
      if (o === 'auto' || o === 'scroll') return true;
    }
    return false;
  };
  const cut = [];
  document.querySelectorAll('main *, header *').forEach((el) => {
    if (!vis(el) || el.closest('svg') || el.classList.contains('sr-only')) return;
    const r = el.getBoundingClientRect();
    if (r.right > W + 1 && !inScroller(el)) cut.push([label(el), Math.round(r.left), Math.round(r.right)]);
  });
  return {
    cut: cut.slice(0, 8),
    scrollW: de.scrollWidth, innerW: W, layoutW: innerWidth, hOverflow: de.scrollWidth > W, docH: de.scrollHeight,
    nodes: document.querySelectorAll('*').length,
    small: [...small.values()], noname: [...new Set(noname)], over: over.slice(0, 12),
    h1: [...document.querySelectorAll('h1')].filter(vis).map((h) => h.textContent.trim().slice(0, 60)),
    title: document.title, view: document.body.dataset.view,
    scheme: de.dataset.scheme, theme: de.dataset.theme,
    skeletons: document.querySelectorAll('#view .sk, #view [class*="sk-"]').length,
    imgs: document.images.length,
  };
}
`

const browseContrastJS = `
() => {
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[, /]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = ({ r, g, b }) => { const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const bgOf = (el) => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e); const c = parse(cs.backgroundColor);
      if (cs.backgroundImage !== 'none' && !(c && c.a >= 1)) return null;
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    if (!layers.length || layers[layers.length - 1].a < 1) return null;
    let out = layers.pop();
    while (layers.length) { const t = layers.pop(); out = { r: t.r * t.a + out.r * (1 - t.a), g: t.g * t.a + out.g * (1 - t.a), b: t.b * t.a + out.b * (1 - t.a), a: 1 }; }
    return out;
  };
  const bad = new Map(); let checked = 0;
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.nodeValue.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('svg') || el.closest('.sr-only') || el.closest('noscript')) continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height || r.bottom < 0 || r.top > innerHeight) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const fg = parse(cs.color); const bg = bgOf(el); if (!fg || !bg || fg.a === 0) continue;
    checked++;
    const f = { r: fg.r * fg.a + bg.r * (1 - fg.a), g: fg.g * fg.a + bg.g * (1 - fg.a), b: fg.b * fg.a + bg.b * (1 - fg.a) };
    const L1 = lum(f), L2 = lum(bg); const cr = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
    const size = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700; const need = (size >= 24 || (size >= 18.66 && bold)) ? 3 : 4.5;
    if (cr < need) {
      const k = el.tagName.toLowerCase() + '.' + (typeof el.className === 'string' ? el.className.trim().split(/\s+/).join('.') : '');
      if (!bad.has(k)) bad.set(k, [k, +cr.toFixed(2), need, cs.color, 'rgb(' + Math.round(bg.r) + ',' + Math.round(bg.g) + ',' + Math.round(bg.b) + ')', n.nodeValue.trim().slice(0, 24)]);
    }
  }
  return { checked, bad: [...bad.values()] };
}
`

const readerMetricsJS = `
(W) => {
  const de = document.documentElement;
  const vis = (el) => {
    const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < W;
  };
  const label = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).join('.') : '');
  const small = [];
  const hidden = !!document.querySelector('.rd-hide');
  document.querySelectorAll('.rd-chrome a, .rd-chrome button, .pl-dock a, .pl-dock button, .pl-dock select').forEach((el) => {
    if (!vis(el) || (hidden && el.closest('.rd-chrome'))) return;
    const r = el.getBoundingClientRect();
    if (r.width < 43.5 || r.height < 35.5) small.push([label(el), Math.round(r.width), Math.round(r.height)]);
  });
  const cut = [];
  document.querySelectorAll('.rd *').forEach((el) => {
    if (!vis(el) || el.closest('svg') || el.closest('.rd-article') && getComputedStyle(document.querySelector('.rd')).getPropertyValue('--pw')) return;
    const r = el.getBoundingClientRect();
    if (r.right > W + 1) cut.push([label(el), Math.round(r.right)]);
  });
  return {
    scrollW: de.scrollWidth, hOverflow: de.scrollWidth > W, nodes: document.querySelectorAll('*').length,
    readerNodes: document.querySelectorAll('#view *').length, small, cut: cut.slice(0, 6),
    h1: [...document.querySelectorAll('h1')].filter((h) => !h.classList.contains('sr-only')).map((h) => h.textContent.trim().slice(0, 60)),
    title: document.title, paras: document.querySelectorAll('#rd-body > p').length,
    mode: document.querySelector('.rd')?.dataset.mode,
  };
}
`

const readerContrastJS = `
() => {
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[, /]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = ({ r, g, b }) => { const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const bgOf = (el) => { for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a >= 1) return c; } return { r: 255, g: 255, b: 255, a: 1 }; };
  const bad = []; let checked = 0;
  const w = document.createTreeWalker(document.querySelector('.rd'), NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.nodeValue.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('svg') || el.closest('.sr-only') || el.closest('.rd-hide')) continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height || r.bottom < 0 || r.top > innerHeight) continue;
    const cs = getComputedStyle(el); const fg = parse(cs.color); const bg = bgOf(el); if (!fg) continue;
    const f = { r: fg.r * fg.a + bg.r * (1 - fg.a), g: fg.g * fg.a + bg.g * (1 - fg.a), b: fg.b * fg.a + bg.b * (1 - fg.a) };
    const L1 = lum(f), L2 = lum(bg); const cr = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
    const size = parseFloat(cs.fontSize); const need = size >= 24 ? 3 : 4.5; checked++;
    if (cr < need) bad.push([el.className || el.tagName, +cr.toFixed(2), need, n.nodeValue.trim().slice(0, 20)]);
  }
  return { checked, bad: bad.slice(0, 6) };
}
`
