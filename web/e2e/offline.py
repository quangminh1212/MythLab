"""Browser check of offline reading, cache management and the service-worker upgrade path.

  python e2e/offline.py --api http://127.0.0.1:8765 --out <dir> [--port 4326] [--old <reader/static>]

Serves web/dist itself (offline_static.Host; never 8765 / 18765) and asserts:
  1. download a 30-chapter range from the story page, switch the browser offline (context.set_offline) and read
     those 30 chapters; a chapter that was not downloaded fails with a message, not a blank page;
  2. the app shell itself opens offline (navigation falls back to the cached shell);
  3. "Xoá cả truyện đã tải" empties every layer (Cache Storage, IndexedDB bookkeeping) and offline reading stops;
  4. upgrade from the OLD reader/static service worker: the old build is served on a port, loaded, then the new
     build is served on the SAME port; the new shell must take over without a blank page, the old caches are
     purged and exactly one mythlab-shell-* cache remains;
  5. a navigation response that is not the shell is never stored as the shell (bug W1).
Exit code 1 on any failure. Results go to <out>/offline-results.json plus screenshots.
"""
import argparse
import json
import os
import sys
import time
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from offline_static import Host  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from browse import chrome_path  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
KEY = "Mạt Thế Cổ Đại Cầu Sinh"
FAILS = []
CHECKS = []
NUMBERS = {}


def check(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": str(detail)})
    if not ok:
        FAILS.append(name)
        print("FAIL", name, detail)


def seed(api):
    d = {"mythlab.settings": {"ui2": 1, "ui3": 1}, "mythlab.server": {"url": api}}
    return "(() => { if (sessionStorage.getItem('seeded')) return; sessionStorage.setItem('seeded','1'); const d = %s; for (const k in d) localStorage.setItem(k, JSON.stringify(d[k])); })();" % json.dumps(d)


def boot(page, url, timeout=20000):
    page.goto(url)
    page.wait_for_function("window.__mlBooted === true", timeout=timeout)
    page.wait_for_timeout(300)


def wait_controlled(page, timeout=15000):
    page.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller", timeout=timeout)


def cache_state(page):
    return page.evaluate(
        """async () => {
      const out = {};
      for (const k of await caches.keys()) out[k] = (await (await caches.open(k)).keys()).length;
      return out;
    }"""
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://127.0.0.1:8765")
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=4326)
    ap.add_argument("--dist", default=os.path.join(os.path.dirname(__file__), "..", "dist"))
    ap.add_argument("--old", default=os.path.join(os.path.dirname(__file__), "..", "..", "reader", "static"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    host = Host(args.dist, args.port).start()
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(executable_path=chrome_path(), headless=True)
            reading(br, args, host)
            upgrade(br, args, host)
            br.close()
    finally:
        host.stop()
    json.dump({"checks": CHECKS, "numbers": NUMBERS}, open(os.path.join(args.out, "offline-results.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(json.dumps(NUMBERS, ensure_ascii=False))
    print(f"{len(CHECKS) - len(FAILS)}/{len(CHECKS)} checks passed")
    sys.exit(1 if FAILS else 0)


def reading(br, args, host):
    host.root = os.path.abspath(args.dist)
    base = host.url + "/index.html"
    ctx = br.new_context(viewport={"width": 1280, "height": 860})
    ctx.add_init_script(seed(args.api))
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    boot(page, base)
    page.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.ready")
    page.reload()
    page.wait_for_function("window.__mlBooted === true")
    wait_controlled(page)
    check("service worker controls the page", True)
    st = cache_state(page)
    shell = [k for k in st if k.startswith("mythlab-shell-")]
    check("exactly one shell cache with the precache", len(shell) == 1 and st[shell[0]] >= 20, st)
    NUMBERS["shell_cache_entries"] = st.get(shell[0]) if shell else None

    page.goto(base + "#/s/local0/" + quote(KEY))
    page.wait_for_selector('[data-act="download"]', timeout=20000)
    page.click('#view [data-act="download"]')
    page.wait_for_selector("#st-dl-from")
    page.fill("#st-dl-from", "1")
    page.fill("#st-dl-to", "30")
    t0 = time.time()
    page.click('.overlay [data-act="start"]')
    page.wait_for_function("(() => { const b = document.querySelector('#st-dl-bar'); return b && Number(b.value) >= 100; })()", timeout=120000)
    NUMBERS["download_30_chapters_s"] = round(time.time() - t0, 2)
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(args.out, "offline-dialog-done.png"))
    status = page.inner_text("#st-dl-status")
    check("dialog reports the finished download", "30" in status or "xong" in status.lower() or "Đã" in status, status)
    st = cache_state(page)
    pinned = st.get("mythlab-offline", 0)
    NUMBERS["pinned_entries"] = pinned
    check("30 chapters are pinned in Cache Storage", pinned >= 30, st)
    usage = page.evaluate("async () => (await navigator.storage.estimate()).usage")
    NUMBERS["storage_usage_bytes"] = usage
    page.keyboard.press("Escape")

    # ------------------------------------------------------------ offline
    ctx.set_offline(True)
    page.wait_for_timeout(300)
    page.reload()
    page.wait_for_function("window.__mlBooted === true", timeout=20000)
    body = page.evaluate("document.body.innerText.length")
    check("the shell opens offline (not blank)", body > 20, body)
    check("offline indicator visible", page.evaluate("document.documentElement.classList.contains('is-offline')") and page.locator("#st-offline").is_visible())
    page.screenshot(path=os.path.join(args.out, "offline-home.png"))
    ok_chapters = 0
    bad = []
    for i in range(30):
        page.goto(base + "#/r/local0/" + quote(KEY) + f"/{i}")
        page.reload() if i == 0 else None
        try:
            page.wait_for_selector("#rd-body p", timeout=8000)
            n = page.evaluate("document.querySelectorAll('#rd-body p').length")
            if n > 3:
                ok_chapters += 1
            else:
                bad.append((i, n))
        except Exception:
            bad.append((i, "timeout"))
    NUMBERS["offline_chapters_read"] = ok_chapters
    check("all 30 downloaded chapters read offline", ok_chapters == 30, bad)
    page.screenshot(path=os.path.join(args.out, "offline-reading.png"))
    page.goto(base + "#/r/local0/" + quote(KEY) + "/400")
    page.wait_for_timeout(2500)
    txt = page.evaluate("document.body.innerText")
    check("a chapter that was not downloaded fails with a message, not a blank page", len(txt.strip()) > 20 and page.locator("#rd-body p").count() == 0, txt[:80])
    page.screenshot(path=os.path.join(args.out, "offline-missing.png"))

    # ------------------------------------------------------------ back online: storage tab, clear everything
    ctx.set_offline(False)
    page.goto(base)
    page.wait_for_function("window.__mlBooted === true")
    page.wait_for_timeout(500)
    page.click("#btn-settings")
    page.wait_for_selector(".ss-panel")
    page.click('[data-tab="source"]')
    page.wait_for_selector("#ss-layers li")
    layers = page.inner_text("#ss-layers")
    check("storage tab shows sizes per layer", "B" in layers and "KB" in layers or "MB" in layers, layers[:200])
    check("downloaded story is listed", page.locator("#ss-downloads li:not(.ss-empty)").count() == 1)
    page.screenshot(path=os.path.join(args.out, "offline-storage-tab.png"))
    page.click("#ss-clear")
    page.click("[data-ok]")
    page.wait_for_timeout(800)
    st = cache_state(page)
    check("'Xoá bộ nhớ đệm' keeps downloads", st.get("mythlab-offline", 0) >= 30, st)
    page.click("#ss-clear-all")
    page.click("[data-ok]")
    page.wait_for_timeout(1200)
    st = cache_state(page)
    left = {k: v for k, v in st.items() if k in ("mythlab-offline", "mythlab-chapters", "mythlab-covers", "mythlab-tts", "mythlab-api") and v}
    check("clearing removes every data cache", not left, st)
    check("shell cache survives the clear", any(k.startswith("mythlab-shell-") and v > 0 for k, v in st.items()), st)
    check("downloads list is empty after clearing", page.locator("#ss-downloads .ss-empty").count() == 1)
    page.screenshot(path=os.path.join(args.out, "offline-cleared.png"))
    page.keyboard.press("Escape")
    ctx.set_offline(True)
    page.goto(base + "#/r/local0/" + quote(KEY) + "/3")
    page.wait_for_timeout(2500)
    check("after clearing, offline reading no longer works (and says so)", page.locator("#rd-body p").count() == 0 and len(page.evaluate("document.body.innerText").strip()) > 20)
    check("no uncaught page errors", not errors, errors[:3])
    ctx.close()


def upgrade(br, args, host):
    """The old reader/static service worker, then the new build on the same port."""
    host.root = os.path.abspath(args.old)
    base = host.url + "/"
    ctx = br.new_context(viewport={"width": 1280, "height": 860})
    page = ctx.new_page()
    page.goto(base)
    page.wait_for_load_state("load")
    try:
        page.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller", timeout=8000)
    except Exception:
        page.reload()
        page.wait_for_load_state("load")
        page.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller", timeout=15000)
    old_caches = cache_state(page)
    old_sw = page.evaluate("navigator.serviceWorker.controller.scriptURL")
    NUMBERS["old_sw_caches"] = old_caches
    check("old build installed its service worker", bool(old_sw) and len(old_caches) >= 1, old_caches)
    page.screenshot(path=os.path.join(args.out, "upgrade-1-old.png"))

    host.root = os.path.abspath(args.dist)  # same port, new build
    blank = 0
    attempts = 0
    booted = False
    for attempts in range(1, 5):
        page.reload()
        page.wait_for_load_state("load")
        page.wait_for_timeout(1200)
        n = page.evaluate("document.body ? document.body.innerText.trim().length : 0")
        if n < 20:
            blank += 1
        if page.evaluate("window.__mlBooted === true"):
            booted = True
            break
    NUMBERS["upgrade_reloads_until_new_shell"] = attempts
    check("the new shell takes over", booted, f"after {attempts} reloads")
    check("no blank page during the upgrade", blank == 0, f"{blank} blank loads")
    page.screenshot(path=os.path.join(args.out, "upgrade-2-new.png"))
    try:
        page.wait_for_function("navigator.serviceWorker.controller && navigator.serviceWorker.controller.scriptURL.endsWith('sw.js')", timeout=10000)
    except Exception:
        pass
    # let activation and the purge of old caches finish
    page.wait_for_timeout(2500)
    page.reload()
    page.wait_for_function("window.__mlBooted === true", timeout=20000)
    page.wait_for_timeout(1500)
    st = cache_state(page)
    shells = [k for k in st if k.startswith("mythlab-shell-")]
    NUMBERS["caches_after_upgrade"] = st
    check("exactly one shell cache after the upgrade", len(shells) == 1, st)
    check("old shell caches are gone", not any(k in st for k in old_caches if k.startswith(("mythlab-static", "mythlab-shell-")) and k not in shells), {"old": list(old_caches), "now": list(st)})
    ver = page.evaluate(
        """() => new Promise((res) => { const ch = new MessageChannel(); ch.port1.onmessage = (e) => res(e.data); navigator.serviceWorker.controller.postMessage({ type: 'GET_VERSION' }, [ch.port2]); setTimeout(() => res(null), 3000); })"""
    )
    check("the new worker answers GET_VERSION", bool(ver), ver)

    # bug W1: a non-shell response to a navigation must never become the shell
    shell_keys = page.evaluate(
        """async () => { const k = (await caches.keys()).find(x => x.startsWith('mythlab-shell-')); return (await (await caches.open(k)).keys()).map(r => new URL(r.url).pathname); }"""
    )
    try:
        page.goto(base + "no-such-page.html")
    except Exception:
        pass  # a 404 document is reported by the browser as a failed navigation
    page.wait_for_timeout(800)
    page.goto(base)
    page.wait_for_function("window.__mlBooted === true", timeout=20000)
    after_keys = page.evaluate(
        """async () => { const k = (await caches.keys()).find(x => x.startsWith('mythlab-shell-')); return (await (await caches.open(k)).keys()).map(r => new URL(r.url).pathname); }"""
    )
    check("a 404 navigation is not cached into the shell (W1)", "/no-such-page.html" not in after_keys and len(after_keys) == len(shell_keys), (len(shell_keys), len(after_keys)))
    ctx.set_offline(True)
    page.goto(base)
    page.wait_for_function("window.__mlBooted === true", timeout=20000)
    check("new shell opens offline after the upgrade", page.evaluate("document.body.innerText.trim().length") > 20)
    ctx.close()


if __name__ == "__main__":
    main()
