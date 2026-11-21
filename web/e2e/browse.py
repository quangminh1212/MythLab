"""Browser check of the shell and the browse views against a built web/dist.

  python e2e/browse.py --base http://localhost:4322 --api http://127.0.0.1:18801 --out <dir>

Serve web/dist on --base first (any static server). --api is a running MythLab server (Go or the old Python one);
the page reaches it through the "remote server" setting, exactly like the desktop and Android shells do.
For 2 viewports x 3 themes it opens every browse view, takes a screenshot and asserts:
no console errors, no horizontal overflow, WCAG AA contrast of the visible text, tap targets >= 44 px on the
phone viewport, one <h1>, a route-specific document.title, and < 1,000 DOM nodes on home.
Exit code 1 when any assertion fails. Results are written to <out>/results.json.
"""
import argparse
import glob
from urllib.parse import urlparse
import json
import os
import sys
from urllib.parse import quote

from playwright.sync_api import sync_playwright

VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}
THEMES = ["light", "dark", "sepia"]

METRICS = r"""
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
"""

CONTRAST = r"""
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
"""


def seed_script(api, theme, with_data):
    """Runs before the app on every load: the remote server, the theme and (optionally) history and bookmarks."""
    data = {
        "mythlab.settings": {"theme": theme, "ui2": 1, "ui3": 1},
    }
    if api:
        data["mythlab.server"] = {"url": api}
    if with_data:
        now = 1795000000000
        prog = {}
        for i, (src, key, name, total, idx) in enumerate(
            [
                ("local0", "Mạt Thế Cổ Đại Cầu Sinh", "Mạt Thế Cổ Đại Cầu Sinh", 1000, 41),
                ("gh0", "Done_CoTich/Phượng Đế Cửu Khuynh", "Phượng Đế Cửu Khuynh", 2888, 1203),
                ("local0", "Niên Đại Thương Gia", "Niên Đại Thương Gia", 693, 5),
            ]
        ):
            prog[f"{src}|{key}"] = {
                "source": src, "key": key, "name": name, "poster": None, "cover": None, "cover_sha": None, "author": None,
                "genres": [], "group": key.split("/")[0] if "/" in key else None, "idx": idx, "n": idx + 1, "total": total,
                "para": 3, "ts": now - i * 3600_000, "title": f"Chương {idx + 1}: Tĩnh Tâm Uyển", "maxIdx": idx,
            }
        data["mythlab.progress"] = prog
        data["mythlab.bookmarks"] = [
            {
                "id": f"local0|Mạt Thế Cổ Đại Cầu Sinh|Chương {n}.txt|{p}", "source": "local0", "key": "Mạt Thế Cổ Đại Cầu Sinh",
                "name": "Mạt Thế Cổ Đại Cầu Sinh", "idx": n - 1, "n": n, "file": f"Chương {n}.txt", "title": f"Chương {n}: Bóc hoàng bảng",
                "para": p, "excerpt": "Nàng ngẩng đầu nhìn bầu trời xám xịt, trong lòng bỗng dâng lên một dự cảm chẳng lành về những ngày sắp tới.",
                "ts": now - n * 60_000,
            }
            for n, p in [(3, 4), (17, 0), (42, 12)]
        ]
    return "(() => { const d = %s; for (const k in d) localStorage.setItem(k, JSON.stringify(d[k])); })();" % json.dumps(data)


BASE = ["http://localhost:4322"]


def chrome_path():
    """PLAYWRIGHT_CHROME, else the newest Chromium that Playwright downloaded, else Playwright's own default."""
    env = os.environ.get("PLAYWRIGHT_CHROME")
    if env:
        return env
    root = os.path.join(os.path.expanduser("~"), "AppData", "Local", "ms-playwright")
    found = sorted(glob.glob(os.path.join(root, "chromium-*", "chrome-win*", "chrome.exe")))
    return found[-1] if found else None


def expected_http(resp, case):
    """HTTP errors that belong to the scenario: the static test host has no API (the app probes the page origin
    first), and the not-found case asks for a story that does not exist."""
    path = urlparse(resp.url)
    if path.port == urlparse(BASE[0]).port and path.path == "/api/ping":
        return True
    return case == "notfound" and resp.status == 404 and path.path.startswith("/api/")


def settle(page, timeout=20000):
    page.wait_for_function("window.__mlBooted === true", timeout=timeout)
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        pass
    try:
        page.wait_for_function("!document.querySelector('#view .loading, #view .sk-card, #view .sk-rows')", timeout=timeout)
    except Exception:
        pass
    page.wait_for_timeout(450)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4322")
    ap.add_argument("--api", default="http://127.0.0.1:18801")
    ap.add_argument("--out", required=True)
    ap.add_argument("--story-source", default="gh0")
    ap.add_argument("--story-key", default="Done_CoTich/Phượng Đế Cửu Khuynh")
    ap.add_argument("--repo", default="Done_CoTich")
    ap.add_argument("--only", default="", help="comma list of viewport-theme, e.g. mobile-dark")
    args = ap.parse_args()
    BASE[0] = args.base
    os.makedirs(args.out, exist_ok=True)
    enc = lambda s: quote(s, safe="")
    routes = [
        ("home", "#/", True),
        ("source", "#/lib/local0", True),
        ("repos", f"#/lib/{args.story_source}", True),
        ("repo", f"#/lib/{args.story_source}/{enc(args.repo)}", True),
        ("search", "#/search?q=" + enc("phượng"), True),
        ("search-none", "#/search?q=" + enc("zzzqqq không có"), True),
        ("story", f"#/s/{args.story_source}/{enc(args.story_key)}", True),
        ("story-local", "#/s/local0/" + enc("Mạt Thế Cổ Đại Cầu Sinh"), True),
        ("history", "#/history", True),
        ("bookmarks", "#/bookmarks", True),
        ("history-empty", "#/history", False),
        ("bookmarks-empty", "#/bookmarks", False),
        ("notfound", "#/s/local0/" + enc("Không Có Truyện Này"), True),
        ("onboarding", "#/", None),
    ]
    # what must be on screen: (selector inside <main>, minimum count); the error state must not be shown
    expect = {
        "home": ("a.card", 4), "source": ("a.card", 2), "repos": (".tile", 20), "repo": ("a.card", 12),
        "search": ("a.card", 1), "search-none": (".state:not(.state-error)", 1), "story": (".ch", 10),
        "story-local": (".ch", 10), "history": (".row", 3), "bookmarks": (".row", 3),
        "history-empty": (".state:not(.state-error)", 1), "bookmarks-empty": (".state:not(.state-error)", 1),
        "notfound": (".state-error", 1), "onboarding": (".onboard-grid input", 3),
    }
    results = []
    failures = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chrome_path(), headless=True)
        for vp_name, (w, h) in VIEWPORTS.items():
            for theme in THEMES:
                tag = f"{vp_name}-{theme}"
                if args.only and tag not in args.only.split(","):
                    continue
                for name, route, with_data in routes:
                    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, has_touch=vp_name == "mobile", is_mobile=vp_name == "mobile", locale="vi-VN")
                    ctx.add_init_script(seed_script(None if with_data is None else args.api, theme, bool(with_data)))
                    if with_data is None:
                        # no backend: when the page itself comes from a MythLab server, hide that server's /api
                        ctx.route("**/api/**", lambda r: r.fulfill(status=404, content_type="application/json", body="{}"))
                    page = ctx.new_page()
                    errors = []
                    page.on("console", lambda m, errors=errors: errors.append(m.text) if m.type == "error" and not m.text.startswith("Failed to load resource") else None)
                    page.on("pageerror", lambda e, errors=errors: errors.append("pageerror: " + str(e)))
                    failed_req = []
                    page.on("requestfailed", lambda r, failed_req=failed_req: failed_req.append(r.url))
                    page.on("response", lambda r, errors=errors, name=name: errors.append(f"HTTP {r.status} {r.url}") if r.status >= 400 and not expected_http(r, name) else None)
                    page.goto(args.base + "/" + route)
                    try:
                        settle(page)
                    except Exception as e:
                        errors.append("settle: " + str(e)[:200])
                    m = page.evaluate(METRICS, w)
                    c = page.evaluate(CONTRAST)
                    shot = os.path.join(args.out, f"{tag}-{name}.png")
                    page.screenshot(path=shot, full_page=False)
                    # the onboarding page has no backend: the same-origin probe of /api answers 404, which Chromium logs
                    if name == "onboarding":
                        errors = [e for e in errors if "404" not in e]
                    row = {"case": f"{tag}-{name}", "route": route, **m, "contrastChecked": c["checked"], "contrastBad": c["bad"], "errors": errors, "failedRequests": failed_req[:5]}
                    results.append(row)
                    f = []
                    if errors:
                        f.append(f"console errors: {errors[:3]}")
                    if m["hOverflow"]:
                        f.append(f"horizontal overflow {m['scrollW']} > {m['innerW']}: {m['over'][:4]}")
                    if c["bad"]:
                        f.append(f"contrast: {c['bad'][:4]}")
                    if name.startswith("story"):
                        # the chapter list is virtualised: bring it on screen before counting its rows
                        page.evaluate("() => document.querySelector('#st-ch')?.scrollIntoView({ block: 'start' })")
                        page.wait_for_timeout(500)
                        page.screenshot(path=os.path.join(args.out, f"{tag}-{name}-chapters.png"), full_page=False)
                        m2 = page.evaluate(METRICS, w)
                        m["small"] += [x for x in m2["small"] if x not in m["small"]]
                        m["cut"] += m2["cut"]
                        m["chapterNodes"] = m2["nodes"]
                    sel, least = expect[name]
                    got = page.evaluate("(s) => document.querySelectorAll('main ' + s).length", sel)
                    if got < least:
                        f.append(f"expected >= {least} x '{sel}', found {got}")
                    if name != "notfound" and page.evaluate("() => !!document.querySelector('main .state-error')"):
                        f.append("an error state is shown")
                    if m["cut"]:
                        f.append(f"content cut off at the right edge: {m['cut'][:4]}")
                    if vp_name == "mobile" and m["small"]:
                        f.append(f"tap targets < 44px: {m['small'][:6]}")
                    if m["noname"]:
                        f.append(f"controls without a name: {m['noname'][:6]}")
                    if len(m["h1"]) != 1:
                        f.append(f"h1 count {len(m['h1'])}: {m['h1']}")
                    if m["scheme"] != theme:
                        f.append(f"scheme {m['scheme']} != {theme}")
                    if name == "home" and m["nodes"] >= 1000:
                        f.append(f"home has {m['nodes']} DOM nodes")
                    if name not in ("home", "onboarding") and m["title"].strip() in ("MythLab", "MythLab — Đọc & nghe truyện"):
                        f.append(f"title not set for the route: {m['title']!r}")
                    if m["skeletons"]:
                        f.append(f"{m['skeletons']} skeleton nodes still shown")
                    if f:
                        failures.append((row["case"], f))
                    print(f"{row['case']:28} view={m['view']:9} nodes={m['nodes']:5} h={m['docH']:6} small={len(m['small']):2} contrastBad={len(c['bad']):2} checked={c['checked']:4} err={len(errors)} title={m['title'][:50]!r}")
                    ctx.close()
        browser.close()
    with open(os.path.join(args.out, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)
    print(f"\n{len(results)} cases, {len(failures)} with failures")
    for case, f in failures:
        print("FAIL", case)
        for x in f:
            print("   ", x)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
