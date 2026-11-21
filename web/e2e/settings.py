"""Browser check of the settings sheet against a built web/dist.

  python e2e/settings.py --api http://127.0.0.1:8765 --out <dir> [--port 4326]

Serves web/dist itself (offline_static.Host) and asserts:
  - every control of the sheet changes its CSS variable / data attribute and persists across a reload;
  - the sheet is an accessible dialog (role, aria-modal, focus trap, Escape, focus return, tablist keys);
  - on a phone the bottom sheet is at most ~55 % high and leaves the reading text visible and uncovered;
  - presets, font picker and reset to defaults;
  - the secrets inputs never contain a stored secret;
  - export contains no secret by default.
Exit code 1 on any failure. Results go to <out>/settings-results.json plus screenshots.
"""
import argparse
import json
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from offline_static import Host  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from browse import chrome_path  # noqa: E402

KEY = "Mạt Thế Cổ Đại Cầu Sinh"
FAILS = []
CHECKS = []


sys.stdout.reconfigure(encoding="utf-8")


def check(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": str(detail)})
    if not ok:
        FAILS.append(f"{name}: {detail}")
        print("FAIL", name, detail)


def seed(api, extra=None):
    d = {"mythlab.settings": {"ui2": 1, "ui3": 1}, "mythlab.server": {"url": api, "key": "SECRET-LAN-KEY-123"}}
    if extra:
        d["mythlab.settings"].update(extra)
    return "(() => { if (sessionStorage.getItem('seeded')) return; sessionStorage.setItem('seeded','1'); const d = %s; for (const k in d) localStorage.setItem(k, JSON.stringify(d[k])); })();" % json.dumps(d)


def boot(page, url):
    page.goto(url)
    page.wait_for_function("window.__mlBooted === true", timeout=20000)
    page.wait_for_timeout(300)


def open_sheet(page, tab=None):
    if page.locator("#btn-settings").is_visible():
        page.click("#btn-settings")
    else:  # the reader hides the top bar: chrome "more" button, then "Cài đặt đọc"
        page.evaluate("document.querySelector('#rd [data-act=\"more\"]').click()")
        page.click('[data-more="settings"]')
    page.wait_for_selector(".ss-panel", timeout=5000)
    if tab:
        page.click(f'[data-tab="{tab}"]')
        page.wait_for_selector(f"#ss-pane-{tab}:not([hidden])")


def var(page, name):
    return page.evaluate("(n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim()", name)


def stored(page):
    return page.evaluate("() => JSON.parse(localStorage.getItem('mythlab.settings') || '{}')")


def close_sheet(page):
    page.keyboard.press("Escape")
    page.wait_for_selector(".ss-panel", state="detached", timeout=3000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://127.0.0.1:8765")
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=4326)
    ap.add_argument("--dist", default=os.path.join(os.path.dirname(__file__), "..", "dist"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    host = Host(args.dist, args.port).start()
    base = host.url + "/index.html"
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(executable_path=chrome_path(), headless=True)
            run(br, args, base)
            br.close()
    finally:
        host.stop()
    json.dump(CHECKS, open(os.path.join(args.out, "settings-results.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{len(CHECKS) - len(FAILS)}/{len(CHECKS)} checks passed")
    sys.exit(1 if FAILS else 0)


def run(br, args, base):
    # ------------------------------------------------------------ desktop: every control, persisted over a reload
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(seed(args.api))
    page = ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "404" not in m.text and "401" not in m.text else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    boot(page, base)
    open_sheet(page, "theme")
    page.screenshot(path=os.path.join(args.out, "settings-desktop-theme.png"))

    sliders = [
        ("theme", "brightness", "0.7", "--brightness", "0.7"),
        ("font", "weight", "600", "--read-weight", "600"),
        ("font", "size", "26", "--read-size", "26px"),
        ("font", "line", "2.2", "--read-line", "2.2"),
        ("font", "letter", "0.8", "--read-letter", "0.8px"),
        ("font", "word", "3", "--read-word", "3px"),
        ("layout", "indent", "1.5", "--read-indent", "1.5em"),
        ("layout", "paraGap", "1.8", "--read-gap", "1.8em"),
        ("layout", "margin", "40", "--read-margin", "40px"),
        ("layout", "width", "900", "--read-width", "900px"),
    ]
    for tab, key, val, cssvar, want in sliders:
        page.click(f'[data-tab="{tab}"]')
        page.fill(f'#ss-pane-{tab} input[data-range="{key}"]', val)
        got = var(page, cssvar)
        check(f"slider {key} -> {cssvar}", got == want, f"{got!r} != {want!r}")
        check(f"slider {key} stored", float(stored(page).get(key, -1)) == float(val), stored(page).get(key))

    page.click('[data-tab="layout"]')
    page.click('#ss-pane-layout [data-seg="align"] input[value="left"]', force=True)
    check("align -> --read-align", var(page, "--read-align") == "left", var(page, "--read-align"))
    page.click('#ss-pane-layout [data-seg="readMode"] input[value="page"]', force=True)
    check("readMode attribute", page.evaluate("document.documentElement.dataset.readmode") == "page")
    cb = page.locator('#ss-pane-layout input[data-bool="tapZones"]')
    cb.uncheck()
    check("tapZones attribute", page.evaluate("document.documentElement.dataset.tapzones") == "off")

    page.click('[data-tab="theme"]')
    page.click('#ss-pane-theme [data-seg="theme"] input[value="dark"]', force=True)
    check("theme attribute", page.evaluate("document.documentElement.dataset.scheme") == "dark")
    check("theme-color follows theme", page.evaluate("document.querySelector('meta[name=theme-color]').content") != "#ffffff")
    swatch = page.locator("#ss-pane-theme [data-swatches='nightPreset'] [data-preset]").nth(1)
    pid = swatch.get_attribute("data-preset")
    swatch.click()
    check("night preset stored", stored(page).get("nightPreset") == pid, stored(page).get("nightPreset"))

    page.click('[data-tab="font"]')
    before = var(page, "--font-read")
    fonts = page.locator("#ss-fonts [data-font]")
    nfonts = fonts.count()
    check("font picker lists the 20 bundled and system fonts", nfonts >= 20, nfonts)
    fonts.nth(5).click()
    check("font changes --font-read", var(page, "--font-read") != before, var(page, "--font-read"))
    page.screenshot(path=os.path.join(args.out, "settings-desktop-font.png"))
    page.locator("[data-typo-id='large']").click()
    check("typography preset applies", stored(page).get("size") is not None and page.locator("[data-typo-id='large']").get_attribute("aria-checked") == "true")

    # quick row
    size0 = stored(page)["size"]
    page.click('[data-step="1"]')
    check("quick row size +", stored(page)["size"] == size0 + 1, stored(page).get("size"))
    page.click('[data-step="-1"]')
    check("quick row size -", stored(page)["size"] == size0)
    snapshot = stored(page)
    close_sheet(page)

    page.reload()
    page.wait_for_function("window.__mlBooted === true")
    page.wait_for_timeout(300)
    after = stored(page)
    check("settings persist across reload", all(after.get(k) == snapshot.get(k) for k in snapshot), {k: (snapshot[k], after.get(k)) for k in snapshot if after.get(k) != snapshot[k]})
    check("variables re-applied after reload", var(page, "--read-width") == "%dpx" % snapshot["width"] and var(page, "--read-size") == "%dpx" % snapshot["size"] and page.evaluate("document.documentElement.dataset.scheme") == "dark", (var(page, "--read-width"), snapshot["width"]))

    # reset
    open_sheet(page)
    page.click("[data-reset]")
    page.click("[data-ok]")
    page.wait_for_timeout(200)
    check("reset restores defaults", stored(page).get("size") == 20 and var(page, "--read-width") != "%dpx" % snapshot["width"], stored(page).get("size"))

    # ------------------------------------------------------------ a11y
    close_sheet(page)
    page.focus("#btn-settings")
    page.keyboard.press("Enter")
    page.wait_for_selector(".ss-panel")
    dlg = page.locator(".ss-panel")
    check("dialog role+modal", dlg.get_attribute("role") == "dialog" and dlg.get_attribute("aria-modal") == "true")
    check("dialog is labelled", bool(dlg.get_attribute("aria-labelledby")))
    check("tablist roles", page.locator('[role="tablist"] [role="tab"]').count() == 5 and page.locator('[role="tabpanel"]').count() == 5)
    check("one tab selected", page.locator('[role="tab"][aria-selected="true"]').count() == 1)
    inside = page.evaluate("() => !!document.activeElement.closest('.ss-panel')")
    check("focus moves into the sheet", inside)
    escaped = 0
    for _ in range(45):
        page.keyboard.press("Tab")
        if not page.evaluate("() => !!document.activeElement.closest('.ss-panel')"):
            escaped += 1
    check("focus trap holds over 45 Tab presses", escaped == 0, escaped)
    for _ in range(45):
        page.keyboard.press("Shift+Tab")
        if not page.evaluate("() => !!document.activeElement.closest('.ss-panel')"):
            escaped += 1
    check("focus trap holds backwards", escaped == 0, escaped)
    page.focus('[role="tab"][aria-selected="true"]')
    cur = page.evaluate("document.activeElement.dataset.tab")
    page.keyboard.press("ArrowRight")
    nxt = page.evaluate("document.activeElement.dataset.tab")
    check("arrow keys move between tabs", cur != nxt and page.locator(f'#ss-pane-{nxt}:not([hidden])').count() == 1, (cur, nxt))
    page.keyboard.press("Escape")
    page.wait_for_selector(".ss-panel", state="detached")
    check("Escape closes and returns focus", page.evaluate("document.activeElement.id") == "btn-settings", page.evaluate("document.activeElement.id"))

    # ------------------------------------------------------------ data-source tab: no secret in the DOM
    open_sheet(page, "source")
    page.wait_for_selector("#ss-srv-url")
    dump = page.evaluate("() => document.querySelector('.ss-panel').outerHTML + [...document.querySelectorAll('.ss-panel input')].map(i => i.value).join('|')")
    check("stored server key not echoed into the sheet", "SECRET-LAN-KEY-123" not in dump)
    check("key field is a password input and empty", page.evaluate("() => { const i = document.querySelector('#ss-srv-key'); return i.type === 'password' && i.value === ''; }"))
    check("token field is a password input and empty", page.evaluate("() => { const i = document.querySelector('#ss-gh-tok'); return i.type === 'password' && i.value === ''; }"))
    check("saved-key hint shown", page.locator("#ss-srv-saved").is_visible())
    page.fill("#ss-srv-url", args.api)
    page.click("#ss-srv-test")
    page.wait_for_function("(() => { const t = document.querySelector('#ss-srv-msg').textContent.trim(); return t.length > 3 && !t.startsWith('Đang'); })()", timeout=15000)
    msg = page.inner_text("#ss-srv-msg")
    check("server test gives a verdict", msg.startswith("✓") or msg.startswith("✗"), msg)
    page.fill("#ss-gh-tok", "github_pat_not_real_xxxxxxxxxxxxxxxx")
    page.click("#ss-gh-test")
    page.wait_for_function("(() => { const t = document.querySelector('#ss-gh-msg').textContent.trim(); return t.length > 3 && !t.startsWith('Đang'); })()", timeout=20000)
    check("token test gives a verdict", page.inner_text("#ss-gh-msg").startswith(("✓", "✗")), page.inner_text("#ss-gh-msg"))
    page.screenshot(path=os.path.join(args.out, "settings-desktop-source.png"), full_page=False)
    page.fill("#ss-gh-tok", "")
    # export has no secret by default
    with page.expect_download() as dl:
        page.click("#ss-export")
    path = dl.value.path()
    text = open(path, encoding="utf8").read()
    check("export omits secrets by default", "SECRET-LAN-KEY-123" not in text and "github_pat" not in text)
    page.check("#ss-exp-secrets")
    with page.expect_download() as dl:
        page.click("#ss-export")
    text2 = open(dl.value.path(), encoding="utf8").read()
    check("export includes the key only when ticked", "SECRET-LAN-KEY-123" in text2)
    # import round trip
    page.set_input_files("#ss-import-file", path)
    page.wait_for_selector("#ss-import:not([hidden]) [data-imp='go']")
    page.click("[data-imp='go']")
    check("import finishes without error", page.locator(".toast, [role=status]").count() >= 1)
    check("no console errors", not errors, errors[:3])
    close_sheet(page)
    ctx.close()

    # ------------------------------------------------------------ phone: bottom sheet keeps the text visible
    ctx = br.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    ctx.add_init_script(seed(args.api))
    page = ctx.new_page()
    boot(page, base + "#/r/local0/" + quote(KEY) + "/0")
    page.wait_for_selector("#rd-body p", timeout=20000)
    page.wait_for_timeout(500)
    open_sheet(page, "font")
    page.wait_for_timeout(400)
    m = page.evaluate(
        """() => {
      const d = document.querySelector('.ss-panel').getBoundingClientRect();
      const ps = [...document.querySelectorAll('#rd-body p')];
      const vis = ps.filter(p => { const r = p.getBoundingClientRect(); return r.bottom > 60 && r.top < d.top - 4 && r.height > 0; });
      const mid = vis[0] ? vis[0].getBoundingClientRect() : null;
      let hit = null;
      if (mid) { const e = document.elementFromPoint(mid.left + 20, Math.min(mid.top + 10, d.top - 8)); hit = e ? !!e.closest('.ss-panel') : null; }
      return { top: d.top, height: d.height, vh: innerHeight, visible: vis.length, hitPanel: hit, ow: document.documentElement.scrollWidth };
    }"""
    )
    check("mobile sheet is at most 55 % high", m["height"] <= m["vh"] * 0.55 + 1 or m["height"] <= 301, m)
    check("reading text visible above the sheet", m["visible"] >= 1 and m["hitPanel"] is False, m)
    check("no horizontal overflow with the sheet open", m["ow"] <= 390, m["ow"])
    # the page above stays interactive: changing the size from the sheet updates the text immediately
    h0 = page.evaluate("document.querySelector('#rd-body p').getBoundingClientRect().height")
    page.click('[data-step="1"]')
    page.click('[data-step="1"]')
    page.wait_for_timeout(150)
    h1 = page.evaluate("document.querySelector('#rd-body p').getBoundingClientRect().height")
    check("live: the text behind the sheet reflows", h1 != h0, (h0, h1))
    page.screenshot(path=os.path.join(args.out, "settings-mobile-font.png"))
    small = page.evaluate(
        """() => [...document.querySelectorAll('.ss-panel button, .ss-panel input:not([type=range]), .ss-panel select, .ss-panel [role=tab]')].filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && cs.visibility !== 'hidden' && !e.closest('[hidden]') && (r.height < 43.5 || r.width < 43.5) && cs.opacity !== '0' && e.type !== 'radio' && e.type !== 'checkbox'; }).map(e => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height)).slice(0, 8)"""
    )
    check("tap targets >= 44 px in the sheet", not small, small)
    for tab in ("theme", "layout", "voice", "source"):
        page.click(f'[data-tab="{tab}"]')
        page.wait_for_timeout(250)
        page.screenshot(path=os.path.join(args.out, f"settings-mobile-{tab}.png"))
        ow = page.evaluate("document.documentElement.scrollWidth")
        pw_ = page.evaluate("(() => { const b = document.querySelector('.ss-panel .dialog-body'); return b.scrollWidth - b.clientWidth; })()")
        check(f"mobile tab {tab} has no horizontal overflow", ow <= 390 and pw_ <= 1, (ow, pw_))
    ctx.close()


if __name__ == "__main__":
    main()
