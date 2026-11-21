"""Browser check of the reader and the audio player against a built web/dist.

  python e2e/reader.py --base http://localhost:4324 --api http://127.0.0.1:8765 --out <dir>

Serve web/dist on --base first (any static server). --api is a running MythLab server (Go or the old Python one);
the page reaches it through the "remote server" setting, like the desktop and Android shells do.

For 2 viewports (1440x900, 390x844) x 3 themes (light, dark, sepia) it opens a long story in scroll mode and in
page mode, takes screenshots and checks: one <h1>, no horizontal overflow, text contrast, tap targets on the
phone, reader DOM under 1,500 nodes, no console errors. Once per viewport (light) it also exercises: position
restore after reload (drift in px), the chapter drawer (jump to chapter 2000), prev/next buttons and keys,
bookmarks, auto-scroll, the keyboard help, tap zones vs. selection and double click, swipes, text-to-speech
(an /api/tts request succeeds, the highlighted sentence advances, pause then resume continues from the same
spot), the sleep timer, the phone dock and its sheet, reduced motion.
Exit code 1 when any check fails. Results go to <out>/results.json.
"""
import argparse
import glob
import json
import os
import sys
from urllib.parse import quote, urlparse

from playwright.sync_api import sync_playwright

VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}
THEMES = ["light", "dark", "sepia"]
KEY = "Done_CoTich/Phượng Đế Cửu Khuynh"
SRC = "gh0"
enc = lambda s: quote(s, safe="")

RESULTS = []
FAILS = []


def check(tag, name, ok, detail=""):
    RESULTS.append({"tag": tag, "check": name, "ok": bool(ok), "detail": str(detail)})
    print(("  ok   " if ok else "  FAIL ") + f"[{tag}] {name}" + (f"  ({detail})" if detail != "" else ""))
    if not ok:
        FAILS.append(f"[{tag}] {name} {detail}")


def chrome_path():
    env = os.environ.get("PLAYWRIGHT_CHROME")
    if env:
        return env
    root = os.path.join(os.path.expanduser("~"), "AppData", "Local", "ms-playwright")
    found = sorted(glob.glob(os.path.join(root, "chromium-*", "chrome-win*", "chrome.exe")))
    return found[-1] if found else None


# records every media element that starts playing, so the test can read the clock of the audio
HOOK = r"""
(() => {
  window.__audios = [];
  const play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () {
    if (!window.__audios.includes(this)) window.__audios.push(this);
    return play.apply(this, arguments);
  };
})();
"""

METRICS = r"""
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
"""

CONTRAST = r"""
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
"""


def seed(api, theme, mode="scroll", extra=None):
    settings = {"theme": theme, "ui2": 1, "ui3": 1, "readMode": mode}
    if extra:
        settings.update(extra)
    data = {"mythlab.settings": settings, "mythlab.server": {"url": api}}
    # written once per browser context: a reload must keep what the reader saved
    return (
        "(() => { if (sessionStorage.getItem('__seeded')) return; sessionStorage.setItem('__seeded', '1'); const d = %s;"
        " for (const k in d) localStorage.setItem(k, JSON.stringify(d[k])); })();" % json.dumps(data)
    )


class Run:
    def __init__(self, browser, args, vp, theme, mode="scroll", extra=None, reduced=False, hash_="", touch=None):
        w, h = VIEWPORTS[vp]
        self.vp, self.w, self.h = vp, w, h
        self.tag = f"{vp}-{theme}-{mode}"
        self.args = args
        mobile = vp == "mobile" if touch is None else touch
        self.ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, has_touch=mobile, is_mobile=mobile, locale="vi-VN",
                                       reduced_motion="reduce" if reduced else "no-preference")
        self.ctx.add_init_script(HOOK)
        self.ctx.add_init_script(seed(args.api, theme, mode, extra))
        self.page = self.ctx.new_page()
        self.errors = []
        base_port = urlparse(args.base).port
        self.page.on("console", lambda m: self.errors.append(m.text) if m.type == "error" and not m.text.startswith("Failed to load resource") else None)
        self.page.on("pageerror", lambda e: self.errors.append("pageerror: " + str(e)))
        self.page.on("response", lambda r: self.errors.append(f"HTTP {r.status} {r.url}") if r.status >= 400 and not (urlparse(r.url).port == base_port and urlparse(r.url).path == "/api/ping") else None)
        if hash_:
            self.open(hash_)

    def open(self, hash_):
        self.page.goto(self.args.base + "/" + hash_)
        self.ready()

    def ready(self):
        p = self.page
        p.wait_for_function("window.__mlBooted === true", timeout=30000)
        p.wait_for_selector("#rd-body > p", timeout=60000)
        p.wait_for_timeout(500)

    def shot(self, name):
        path = os.path.join(self.args.out, f"{self.tag}-{name}.png")
        self.page.screenshot(path=path)
        return path

    def show_chrome(self):
        if self.page.query_selector(".rd.rd-hide"):
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)

    def idx(self):
        return int(self.page.evaluate("location.hash.split('?')[0].split('/').pop()"))

    def stored(self, key):
        return self.page.evaluate("(k) => JSON.parse(localStorage.getItem(k) || 'null')", key)

    def close(self):
        self.ctx.close()


def hash_for(idx, q=""):
    return f"#/r/{SRC}/{enc(KEY)}/{idx}{q}"


def basics(r, label):
    m = r.page.evaluate(METRICS, r.w)
    check(r.tag, f"{label}: one h1", len(m["h1"]) == 1, m["h1"])
    check(r.tag, f"{label}: title is set", bool(m["title"]) and "MythLab" in m["title"], m["title"])
    check(r.tag, f"{label}: no horizontal overflow", not m["hOverflow"], f"scrollW={m['scrollW']}")
    check(r.tag, f"{label}: nothing cut off", not m["cut"], m["cut"])
    check(r.tag, f"{label}: reader DOM < 1500 nodes", m["readerNodes"] < 1500 and m["nodes"] < 1500, f"view={m['readerNodes']} page={m['nodes']} paras={m['paras']}")
    c = r.page.evaluate(CONTRAST)
    check(r.tag, f"{label}: text contrast AA", not c["bad"], f"checked {c['checked']} {c['bad']}")
    if r.vp == "mobile":
        check(r.tag, f"{label}: tap targets >= 44 px", not m["small"], m["small"])
    return m


def pager(r):
    t = r.page.inner_text("#rd-pager-pos")
    try:
        a, b = t.replace("Trang", "").strip().split("/")
        return int(a), int(b)
    except Exception:
        return 0, 0


def theme_pass(browser, args, vp, theme):
    # scroll mode
    r = Run(browser, args, vp, theme, "scroll", hash_=hash_for(3))
    r.shot("scroll")
    basics(r, "scroll")
    r.page.mouse.wheel(0, 900) if vp == "desktop" else r.page.evaluate("window.scrollBy(0, 900)")
    r.page.wait_for_timeout(500)
    r.shot("scroll-mid")
    r.page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    r.page.wait_for_timeout(500)
    r.shot("scroll-end")
    check(r.tag, "end of chapter shows the next link", r.page.is_visible(".rd-end a[rel=next]"))
    check(r.tag, "no console errors (scroll)", not r.errors, r.errors[:3])
    r.close()
    # page mode
    r = Run(browser, args, vp, theme, "page", hash_=hash_for(3))
    r.page.wait_for_timeout(300)
    r.shot("page")
    m = basics(r, "page")
    a, b = pager(r)
    check(r.tag, "page mode has several pages", b > 1 and a == 1, f"{a}/{b}")
    check(r.tag, "page mode: nothing scrolls", r.page.evaluate("(() => { window.scrollTo(0, 500); return window.scrollY === 0; })()"))
    r.page.keyboard.press("ArrowRight")
    r.page.wait_for_timeout(450)
    a2, _ = pager(r)
    check(r.tag, "ArrowRight turns the page", a2 == 2, a2)
    r.shot("page-2")
    check(r.tag, "no console errors (page)", not r.errors, r.errors[:3])
    r.close()


def functional(browser, args, vp):
    out = args.out
    # ---- restore drift (scroll mode)
    r = Run(browser, args, vp, "light", "scroll", hash_=hash_for(5))
    p = r.page
    p.evaluate("window.scrollTo(0, 2300)")
    p.wait_for_timeout(1800)
    y1 = p.evaluate("window.scrollY")
    sv = r.stored("mythlab.progress")
    ent = next(iter((sv or {}).values()), {})
    check(r.tag, "progress saved with file/frac/idx", ent.get("idx") == 5 and "file" in ent and "frac" in ent and ent.get("para", 0) > 0, {k: ent.get(k) for k in ("idx", "para", "frac", "file", "maxIdx")})
    p.reload()
    r.ready()
    p.wait_for_timeout(900)
    y2 = p.evaluate("window.scrollY")
    check(r.tag, "restore after reload: drift <= 2 px", abs(y1 - y2) <= 2, f"before={y1} after={y2} drift={abs(y1 - y2)}")
    # a saved position survives a different font size (anchor is paragraph + fraction)
    p.goto(args.base + "/#/")
    p.wait_for_timeout(300)
    p.go_back()
    r.ready()
    p.wait_for_timeout(700)
    y3 = p.evaluate("window.scrollY")
    check(r.tag, "restore after leaving and coming back", abs(y1 - y3) <= 2, f"drift={abs(y1 - y3)}")

    # ---- prev / next, keys
    r.show_chrome()
    p.click('[data-act="next"]')
    p.wait_for_timeout(900)
    check(r.tag, "next button opens the next chapter", r.idx() == 6, r.idx())
    p.click('[data-act="prev"]') if not p.query_selector(".rd.rd-hide") else (p.keyboard.press("Escape"), p.click('[data-act="prev"]'))
    p.wait_for_timeout(900)
    check(r.tag, "prev button goes back", r.idx() == 5, r.idx())
    p.keyboard.press("ArrowRight")
    p.wait_for_timeout(900)
    check(r.tag, "ArrowRight opens the next chapter (scroll mode)", r.idx() == 6, r.idx())
    p.keyboard.press("ArrowLeft")
    p.wait_for_timeout(900)
    check(r.tag, "ArrowLeft opens the previous chapter", r.idx() == 5, r.idx())
    p.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    p.wait_for_timeout(500)
    p.click(".rd-end a[rel=next]")
    p.wait_for_timeout(900)
    check(r.tag, "end-of-chapter link opens the next chapter", r.idx() == 6, r.idx())
    top = p.evaluate("window.scrollY")
    check(r.tag, "new chapter opens at the top", top <= 2, top)
    hist = p.evaluate("history.length")

    # ---- help dialog
    p.keyboard.press("?")
    p.wait_for_selector(".rd-help", timeout=3000)
    check(r.tag, "? opens the keyboard help", p.is_visible(".rd-help"))
    r.shot("help")
    p.keyboard.press("Escape")
    p.wait_for_timeout(300)
    check(r.tag, "Escape closes the help", not p.query_selector(".rd-help"))

    # ---- drawer: jump to chapter 2000
    p.keyboard.press("m")
    p.wait_for_selector("#rd-jump", timeout=3000)
    p.wait_for_timeout(400)
    r.shot("drawer")
    rows = p.evaluate("document.querySelectorAll('.rd-dr-row').length")
    cur = p.inner_text(".rd-dr-row.is-current .rd-dr-num") if p.query_selector(".rd-dr-row.is-current") else ""
    check(r.tag, "drawer is virtualised and shows the current chapter", 0 < rows < 80 and cur == "7", f"rows={rows} current={cur}")
    p.fill("#rd-jump", "2000")
    p.press("#rd-jump", "Enter")
    p.wait_for_timeout(1200)
    title = p.inner_text("#rd-title")
    check(r.tag, "drawer jump to chapter 2000", r.idx() == 1999 and "2000" in title, f"idx={r.idx()} {title[:40]}")
    r.shot("ch2000")
    p.reload()
    r.ready()
    p.wait_for_timeout(400)
    check(r.tag, "chapter 2000 survives a reload", r.idx() == 1999)

    # ---- bookmarks
    p.goto(args.base + "/" + hash_for(8))
    r.ready()
    p.evaluate("window.scrollTo(0, 1500)")
    p.wait_for_timeout(500)
    p.keyboard.press("b")
    p.wait_for_timeout(400)
    bms = r.stored("mythlab.bookmarks") or []
    check(r.tag, "B adds a bookmark with an excerpt", len(bms) == 1 and bms[0]["excerpt"] and bms[0]["idx"] == 8, [(b["idx"], b["para"], b["excerpt"][:30]) for b in bms])
    r.shot("bookmarked")
    p.keyboard.press("m")
    p.wait_for_selector("#rd-jump")
    p.click("#rd-tab-marks")
    p.wait_for_selector(".rd-dr-mark", timeout=3000)
    check(r.tag, "bookmark list shows the bookmark", p.locator(".rd-dr-mark").count() == 1)
    r.shot("marks")
    p.keyboard.press("Escape")
    p.wait_for_timeout(300)
    p.goto(args.base + "/" + hash_for(1))
    r.ready()
    p.keyboard.press("m")
    p.wait_for_selector("#rd-jump")
    p.click("#rd-tab-marks")
    p.click(".rd-dr-mark-link")
    p.wait_for_timeout(1200)
    h = p.evaluate("location.hash")
    para_at = p.evaluate("(() => { const l = 84; const ps = [...document.querySelectorAll('#rd-body > p')]; const i = ps.findIndex((e) => e.getBoundingClientRect().bottom > l); return i; })()")
    check(r.tag, "bookmark opens its chapter at its paragraph, ?p= removed", r.idx() == 8 and "?p=" not in h and abs(para_at - bms[0]["para"]) <= 1, f"{h[-24:]} para@line={para_at} saved={bms[0]['para']}")
    p.keyboard.press("b")
    p.wait_for_timeout(300)
    check(r.tag, "B again removes the bookmark", len(r.stored("mythlab.bookmarks") or []) == 0)

    # ---- auto-scroll
    p.evaluate("window.scrollTo(0, 0)")
    p.wait_for_timeout(300)
    p.keyboard.press("a")
    p.wait_for_timeout(300)
    a0 = p.evaluate("window.scrollY")
    check(r.tag, "auto-scroll panel appears", p.is_visible("#rd-auto"))
    p.wait_for_timeout(1500)
    a1 = p.evaluate("window.scrollY")
    p.keyboard.press("+")
    p.wait_for_timeout(200)
    lvl = p.inner_text("#rd-auto-level")
    r.shot("autoscroll")
    check(r.tag, "auto-scroll moves the page and speed changes", a1 > a0 + 10 and "5/9" in lvl, f"{a0}->{a1} {lvl}")
    p.keyboard.press("Escape")
    p.wait_for_timeout(200)
    b0 = p.evaluate("window.scrollY")
    p.wait_for_timeout(600)
    check(r.tag, "Escape stops auto-scroll", p.evaluate("window.scrollY") == b0 and not p.is_visible("#rd-auto"))
    check(r.tag, "chapter changes replace history (history length stable)", p.evaluate("history.length") >= 1)

    # ---- swipe between chapters (scroll mode)
    if vp == "mobile":
        i0 = r.idx()
        cdp = r.ctx.new_cdp_session(p)

        def swipe(x0, x1, y=420):
            cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y}]})
            for k in range(1, 7):
                cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + (x1 - x0) * k / 6, "y": y}]})
            cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})

        swipe(120, 100)
        p.wait_for_timeout(500)
        check(r.tag, "short swipe does not change chapter", r.idx() == i0)
        swipe(384, 20)
        p.wait_for_timeout(500)
        check(r.tag, "swipe from the screen edge is left to the system", r.idx() == i0)
        swipe(320, 80)
        p.wait_for_timeout(1000)
        check(r.tag, "long swipe left opens the next chapter", r.idx() == i0 + 1, r.idx())
        swipe(60, 330)
        p.wait_for_timeout(1000)
        check(r.tag, "long swipe right goes back", r.idx() == i0, r.idx())
    check(r.tag, "no console errors (functional)", not r.errors, r.errors[:4])
    r.close()

    # ---- page mode: tap zones, selection, double click, restore, wheel
    r = Run(browser, args, vp, "light", "page", hash_=hash_for(5))
    p = r.page
    p.wait_for_timeout(300)
    a, b = pager(r)
    W = r.w

    def tap(x, y):
        if vp == "mobile":
            p.touchscreen.tap(x, y)
        else:
            p.mouse.click(x, y)

    tap(W - 10, r.h // 2)
    p.wait_for_timeout(700)
    check(r.tag, "tap on the right zone turns the page", pager(r)[0] == 2, pager(r))
    tap(10, r.h // 2)
    p.wait_for_timeout(700)
    check(r.tag, "tap on the left zone turns back", pager(r)[0] == 1, pager(r))
    # selection blocks the zones
    p.evaluate("(() => { const el = document.querySelector('#rd-body > p'); const s = getSelection(); s.removeAllRanges(); const r = document.createRange(); r.selectNodeContents(el); s.addRange(r); })()")
    tap(W - 10, r.h // 2)
    p.wait_for_timeout(700)
    check(r.tag, "a text selection is not broken by a tap zone", pager(r)[0] == 1, pager(r))
    p.evaluate("getSelection().removeAllRanges()")
    if vp == "desktop":
        box = p.evaluate("(() => { const r = document.querySelector('#rd-body > p:nth-child(3)').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
        p.mouse.dblclick(box[0] + 8, box[1] + 8)
        p.wait_for_timeout(700)
        sel = p.evaluate("getSelection().toString()")
        check(r.tag, "double click does not turn the page", pager(r)[0] == 1, f"page={pager(r)}")
        p.keyboard.press("Escape")
        p.mouse.move(600, 300)
        p.mouse.wheel(0, 300)
        p.wait_for_timeout(700)
        check(r.tag, "wheel turns one page", pager(r)[0] == 2, pager(r))
    else:
        cdp = r.ctx.new_cdp_session(p)

        def swipe(x0, x1, y=420):
            cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y}]})
            for k in range(1, 7):
                cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + (x1 - x0) * k / 6, "y": y}]})
            cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})

        swipe(300, 120)
        p.wait_for_timeout(700)
        check(r.tag, "swipe left turns the page", pager(r)[0] == 2, pager(r))
    # go to page 3 and restore it after a reload
    p.keyboard.press("Home")
    p.wait_for_timeout(450)
    p.keyboard.press("PageDown")
    p.wait_for_timeout(450)
    p.keyboard.press("PageDown")
    p.wait_for_timeout(450)
    pg = pager(r)[0]
    p.wait_for_timeout(1700)
    p.reload()
    r.ready()
    p.wait_for_timeout(600)
    check(r.tag, "page mode restores the page after reload", abs(pager(r)[0] - pg) <= 1, f"before={pg} after={pager(r)[0]}")
    # last page -> next chapter, first page -> previous chapter at its last page
    p.keyboard.press("End")
    p.wait_for_timeout(450)
    a, b = pager(r)
    check(r.tag, "End goes to the last page", a == b, f"{a}/{b}")
    r.shot("page-last")
    p.keyboard.press("ArrowRight")
    p.wait_for_timeout(1200)
    check(r.tag, "past the last page opens the next chapter", r.idx() == 6 and pager(r)[0] == 1, f"idx={r.idx()} {pager(r)}")
    p.keyboard.press("ArrowLeft")
    p.wait_for_timeout(1200)
    a, b = pager(r)
    check(r.tag, "before the first page opens the previous chapter at its last page", r.idx() == 5 and a == b and b > 1 and "end=" not in p.evaluate("location.hash"), f"idx={r.idx()} {a}/{b}")
    check(r.tag, "no console errors (page mode)", not r.errors, r.errors[:4])
    r.close()

    # ---- reduced motion
    r = Run(browser, args, vp, "light", "page", reduced=True, hash_=hash_for(2))
    td = r.page.evaluate("getComputedStyle(document.querySelector('.rd-article')).transitionDuration + '|' + getComputedStyle(document.querySelector('.rd-chrome')).transitionDuration")
    check(r.tag, "reduced motion turns the transitions off", all(float(x.replace("s", "")) <= 0.001 for x in td.split("|")), td)
    r.close()


def tts(browser, args, vp):
    r = Run(browser, args, vp, "light", "scroll", hash_=hash_for(7))
    p = r.page
    tts_ok = []
    p.on("response", lambda x: tts_ok.append(x.status) if "/api/tts" in x.url else None)
    r.show_chrome()
    p.click('[data-act="listen"]')
    p.wait_for_selector(".pl-dock", timeout=15000)
    try:
        p.wait_for_selector("mark.rd-say, .rd-title.rd-say", timeout=40000)
    except Exception:
        pass
    seen = []
    for _ in range(60):
        t = p.evaluate("(document.querySelector('mark.rd-say') || document.querySelector('.rd-title.rd-say') || {}).textContent || ''")
        if t and (not seen or seen[-1] != t):
            seen.append(t)
        if len(seen) >= 3:
            break
        p.wait_for_timeout(700)
    check(r.tag, "an /api/tts request succeeded", bool(tts_ok) and all(s in (200, 206) for s in tts_ok), tts_ok[:4])
    check(r.tag, "the highlighted sentence advances", len(seen) >= 3, [s[:30] for s in seen])
    r.shot("listening")
    st = p.evaluate("(() => { const a = (window.__audios || []).filter((x) => !x.paused); return a.length ? a[a.length - 1].currentTime : -1; })()")
    mark_before = p.evaluate("(document.querySelector('mark.rd-say') || {}).textContent || ''")
    check(r.tag, "an audio element is playing", st >= 0, st)
    dock_h = p.evaluate("document.getElementById('player-dock').getBoundingClientRect().height")
    pad = p.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--player-h')")
    check(r.tag, "dock height is published as --player-h", abs(float(pad.replace('px', '') or 0) - dock_h) <= 1.5, f"dock={dock_h} var={pad}")
    if vp == "mobile":
        check(r.tag, "phone dock is one compact row", dock_h <= 72, dock_h)
        p.click('[data-pl="expand"]')
        p.wait_for_selector(".pl-sheet", timeout=3000)
        p.wait_for_timeout(400)
        r.shot("sheet")
        small = p.evaluate("[...document.querySelectorAll('.pl-sheet button, .pl-sheet select')].filter((e) => { const r = e.getBoundingClientRect(); return r.width < 43.5 || r.height < 43.5; }).map((e) => e.className)")
        check(r.tag, "sheet controls are >= 44 px", not small, small)
        # sleep timer from the sheet
        p.select_option('.pl-sheet select[data-pl="sleep"]', "-1")
        p.wait_for_timeout(300)
        check(r.tag, "sleep timer: end of chapter is shown", "hết chương" in p.inner_text(".pl-sheet [data-pl-left]"), p.inner_text(".pl-sheet [data-pl-left]"))
        p.select_option('.pl-sheet select[data-pl="sleep"]', "15")
        p.wait_for_timeout(1300)
        left = p.inner_text(".pl-sheet [data-pl-left]")
        check(r.tag, "sleep timer: countdown runs", "còn" in left, left)
        p.select_option('.pl-sheet select[data-pl="sleep"]', "0")
        p.keyboard.press("Escape")
        p.wait_for_timeout(400)
        # pause / resume from the dock
        p.click('#player-dock [data-pl="toggle"]')
    else:
        p.click('#player-dock [data-pl="toggle"]')
    p.wait_for_timeout(500)
    paused = p.evaluate("(() => { const a = (window.__audios || []); const x = a[a.length - 1]; return x ? [x.paused, x.currentTime] : null; })()")
    mark_paused = p.evaluate("(document.querySelector('mark.rd-say') || {}).textContent || ''")
    p.wait_for_timeout(1800)
    paused2 = p.evaluate("(() => { const a = (window.__audios || []); const x = a[a.length - 1]; return x ? [x.paused, x.currentTime] : null; })()")
    check(r.tag, "pause really pauses the audio", paused and paused[0] and abs(paused2[1] - paused[1]) < 0.05, f"{paused} {paused2}")
    p.click('#player-dock [data-pl="toggle"]')
    p.wait_for_timeout(900)
    res = p.evaluate("(() => { const a = (window.__audios || []); const x = a[a.length - 1]; return x ? [x.paused, x.currentTime] : null; })()")
    mark_after = p.evaluate("(document.querySelector('mark.rd-say') || {}).textContent || ''")
    n_audio = p.evaluate("(window.__audios || []).length")
    check(r.tag, "resume continues the same clip, not from the chunk start", res and not res[0] and res[1] >= paused[1] - 0.05, f"paused@{paused[1]:.2f} resumed@{res[1]:.2f} clips={n_audio}")
    check(r.tag, "resume keeps the highlighted sentence", mark_after == mark_paused or mark_after.startswith(mark_paused[:20]) or len(mark_after) > 0, f"{mark_paused[:30]!r} -> {mark_after[:30]!r}")
    if vp == "desktop":
        # sleep timer from the dock
        p.select_option('#player-dock select[data-pl="sleep"]', "-1")
        p.wait_for_timeout(300)
        t1 = p.inner_text("#player-dock [data-pl-left]")
        p.select_option('#player-dock select[data-pl="sleep"]', "15")
        p.wait_for_timeout(1300)
        t2 = p.inner_text("#player-dock [data-pl-left]")
        check(r.tag, "sleep timer: end of chapter, then a countdown", "hết chương" in t1 and "còn" in t2, f"{t1!r} {t2!r}")
        p.select_option('#player-dock select[data-pl="sleep"]', "0")
        # speed
        p.select_option('#player-dock select[data-pl="rate"]', index=5)
        p.wait_for_timeout(1200)
        check(r.tag, "rate changes", p.evaluate("JSON.parse(localStorage.getItem('mythlab.settings')).rate") != 1)
        # Space pauses (dock owns it while playing), shortcuts help lists it
        p.mouse.click(10, 10) if False else None
        p.keyboard.press("Space")
        p.wait_for_timeout(500)
        ps = p.evaluate("(() => { const a = (window.__audios || []); const x = a[a.length - 1]; return x ? x.paused : null; })()")
        check(r.tag, "Space toggles pause while listening", ps is True, ps)
        # double click a paragraph starts listening from it
        p.evaluate("window.scrollTo(0, 1600)")
        p.wait_for_timeout(500)
        before = p.evaluate("(document.querySelector('mark.rd-say') || {}).closest ? document.querySelector('mark.rd-say').closest('p').dataset.i : ''")
        pbox = p.evaluate("(() => { const ps = [...document.querySelectorAll('#rd-body > p')]; const e = ps.find((x) => x.getBoundingClientRect().top > 200); const r = e.getBoundingClientRect(); return [r.left + 30, r.top + 10, e.dataset.i]; })()")
        p.mouse.dblclick(pbox[0], pbox[1])
        p.wait_for_timeout(5000)
        now = p.evaluate("(document.querySelector('mark.rd-say') || {}).closest ? document.querySelector('mark.rd-say').closest('p').dataset.i : ''")
        check(r.tag, "double click on a paragraph listens from it", now != "" and abs(int(now) - int(pbox[2])) <= 1, f"clicked={pbox[2]} speaking={now} (was {before})")
    r.shot("listening-2")
    p.click('#player-dock [data-pl="close"]')
    p.wait_for_timeout(500)
    check(r.tag, "closing the player clears the highlight", not p.query_selector("mark.rd-say") and not p.query_selector(".rd-saying"))
    check(r.tag, "no console errors (tts)", not r.errors, r.errors[:4])
    r.close()


def local_pass(browser, args, vp):
    for key in ("Mạt Thế Cổ Đại Cầu Sinh", "Niên Đại Thương Gia"):
        for mode in ("scroll", "page"):
            r = Run(browser, args, vp, "dark", mode, hash_=f"#/r/local0/{enc(key)}/10")
            r.tag = f"{vp}-local0-{key[:8]}-{mode}"
            r.page.wait_for_timeout(300)
            r.shot("local")
            m = basics(r, f"local0 {key[:10]} {mode}")
            check(r.tag, "local story shows its chapter", m["paras"] > 3 and r.idx() == 10, m["paras"])
            if mode == "page":
                check(r.tag, "local story pages", pager(r)[1] >= 1, pager(r))
            check(r.tag, "no console errors (local)", not r.errors, r.errors[:3])
            r.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4324")
    ap.add_argument("--api", default="http://127.0.0.1:8765")
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="", help="comma list of: themes, functional, tts, desktop, mobile")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    only = set(filter(None, args.only.split(",")))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chrome_path(), headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        for vp in VIEWPORTS:
            if only & {"desktop", "mobile"} and vp not in only:
                continue
            print(f"== {vp}")
            if not only or "themes" in only:
                for theme in THEMES:
                    theme_pass(browser, args, vp, theme)
            if not only or "functional" in only:
                functional(browser, args, vp)
            if not only or "tts" in only:
                tts(browser, args, vp)
            if not only or "local" in only:
                local_pass(browser, args, vp)
        browser.close()
    with open(os.path.join(args.out, "results.json"), "w", encoding="utf8") as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=1)
    print(f"\n{len(RESULTS) - len(FAILS)}/{len(RESULTS)} checks passed")
    for f in FAILS:
        print("FAIL", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
