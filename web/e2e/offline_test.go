package e2e

// Port of web/e2e/offline.py and web/e2e/offline_static.py (the switchable static host is Host in harness_test.go).
//
//  1. download a 30-chapter range from the story page, go offline (CDP offline emulation plus the Gate that closes every
//     connection to the page host and the API, so the service worker is cut off too) and read those 30 chapters;
//     a chapter that was not downloaded fails with a message, not a blank page;
//  2. the app shell itself opens offline (navigation falls back to the cached shell);
//  3. "Xoá cả truyện đã tải" empties every layer (Cache Storage, IndexedDB bookkeeping) and offline reading stops;
//  4. upgrade from the OLD reader/static service worker: the old build is served on a port, loaded, then the new
//     build is served on the SAME port; the new shell must take over without a blank page, the old caches are
//     purged and exactly one mythlab-shell-* cache remains;
//  5. a navigation response that is not the shell is never stored as the shell (bug W1).

import (
	"archive/tar"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/chromedp/chromedp/kb"
)

const offlineKey = "Mạt Thế Cổ Đại Cầu Sinh"

func offSeed(api string) string {
	return seedScript(map[string]any{"mythlab.settings": map[string]any{"ui2": 1, "ui3": 1}, "mythlab.server": map[string]any{"url": api}}, true)
}

func (p *Page) waitControlled(timeout time.Duration) error {
	return p.waitFn("navigator.serviceWorker && navigator.serviceWorker.controller", timeout)
}

func (p *Page) cacheState() map[string]int {
	p.t.Helper()
	return ev[map[string]int](p, `(async () => {
      const out = {};
      for (const k of await caches.keys()) out[k] = (await (await caches.open(k)).keys()).length;
      return out;
    })()`)
}

// offline cuts the page off the network: CDP emulation for the page, the Gate for everything else (service worker).
func (p *Page) offline(g *Gate, off bool) {
	p.t.Helper()
	g.SetOffline(off)
	p.setOffline(off)
}

func TestOfflineReading(t *testing.T) {
	needEnv(t)
	srv := startServer(t, false)
	host := startHost(t, webDist)
	api := gatedAPI(t, srv, host.Gate)
	br := newBrowser(t)
	base := host.URL + "/index.html"
	c := &Checker{t: t}
	numbers := map[string]any{}
	defer func() {
		b, _ := json.MarshalIndent(map[string]any{"checks": c.Results, "numbers": numbers}, "", " ")
		_ = os.WriteFile(filepath.Join(outDir, "offline-results.json"), b, 0o644)
	}()
	ck := func(name string, ok bool, detail ...any) { t.Helper(); c.check("offline", name, ok, detail...) }

	p := br.newPage(t, PageOpts{W: 1280, H: 860, Init: []string{offSeed(api)}})
	defer p.Close()
	p.boot(base)
	p.must(p.waitFn("navigator.serviceWorker && navigator.serviceWorker.ready", 20*time.Second), "service worker ready")
	_ = ev[bool](p, "navigator.serviceWorker.ready.then(() => true)")
	p.reload()
	p.must(p.waitFn("window.__mlBooted === true", 30*time.Second), "wait __mlBooted")
	ctl := p.waitControlled(15 * time.Second)
	ck("service worker controls the page", ctl == nil, ctl)
	st := p.cacheState()
	var shell []string
	for k := range st {
		if strings.HasPrefix(k, "mythlab-shell-") {
			shell = append(shell, k)
		}
	}
	ck("exactly one shell cache with the precache", len(shell) == 1 && st[shell[0]] >= 20, st)
	if len(shell) == 1 {
		numbers["shell_cache_entries"] = st[shell[0]]
	}

	p.goto_(base + "#/s/local0/" + enc(offlineKey))
	p.mustVisible(`[data-act="download"]`, 20*time.Second)
	p.click(`#view [data-act="download"]`)
	p.mustVisible("#st-dl-from", 15*time.Second)
	p.fill("#st-dl-from", "1")
	p.fill("#st-dl-to", "30")
	t0 := time.Now()
	p.click(`.overlay [data-act="start"]`)
	p.must(p.waitFn(`(() => { const b = document.querySelector('#st-dl-bar'); return b && Number(b.value) >= 100; })()`, 120*time.Second), "download finishes")
	numbers["download_30_chapters_s"] = time.Since(t0).Seconds()
	p.sleep(500)
	p.shot("offline-dialog-done.png")
	status := p.text("#st-dl-status")
	ck("dialog reports the finished download", strings.Contains(status, "30") || strings.Contains(strings.ToLower(status), "xong") || strings.Contains(status, "Đã"), status)
	st = p.cacheState()
	pinned := st["mythlab-offline"]
	numbers["pinned_entries"] = pinned
	ck("30 chapters are pinned in Cache Storage", pinned >= 30, st)
	numbers["storage_usage_bytes"] = ev[float64](p, "navigator.storage.estimate().then((e) => e.usage)")
	p.key(kb.Escape)

	// ------------------------------------------------------------ offline
	p.offline(host.Gate, true)
	p.sleep(300)
	p.reload()
	p.must(p.waitFn("window.__mlBooted === true", 20*time.Second), "shell boots offline")
	body := ev[int](p, "document.body.innerText.length")
	ck("the shell opens offline (not blank)", body > 20, body)
	_ = p.waitFn("!!document.querySelector('#st-offline') && document.querySelector('#st-offline').getClientRects().length > 0", 10*time.Second) // the story view renders after boot
	ck("offline indicator visible", ev[bool](p, "document.documentElement.classList.contains('is-offline')") && p.visible("#st-offline"))
	p.shot("offline-home.png")
	okChapters := 0
	var bad []string
	for i := 0; i < 30; i++ {
		p.goto_(fmt.Sprintf("%s#/r/local0/%s/%d", base, enc(offlineKey), i))
		if i == 0 {
			p.reload()
		}
		if err := p.waitVisible("#rd-body p", 8*time.Second); err != nil {
			bad = append(bad, fmt.Sprintf("%d:timeout", i))
			continue
		}
		if n := p.count("#rd-body p"); n > 3 {
			okChapters++
		} else {
			bad = append(bad, fmt.Sprintf("%d:%d", i, n))
		}
	}
	numbers["offline_chapters_read"] = okChapters
	ck("all 30 downloaded chapters read offline", okChapters == 30, bad)
	p.shot("offline-reading.png")
	p.goto_(fmt.Sprintf("%s#/r/local0/%s/400", base, enc(offlineKey)))
	p.sleep(2500)
	txt := ev[string](p, "document.body.innerText")
	ck("a chapter that was not downloaded fails with a message, not a blank page", len(strings.TrimSpace(txt)) > 20 && p.count("#rd-body p") == 0, short2(txt, 80))
	p.shot("offline-missing.png")

	// ------------------------------------------------------------ back online: storage tab, clear everything
	p.offline(host.Gate, false)
	p.goto_(base)
	p.must(p.waitFn("window.__mlBooted === true", 30*time.Second), "wait __mlBooted")
	p.sleep(500)
	p.click("#btn-settings")
	p.mustVisible(".ss-panel", 15*time.Second)
	p.click(`[data-tab="source"]`)
	p.mustVisible("#ss-layers li", 15*time.Second)
	layers := p.text("#ss-layers")
	ck("storage tab shows sizes per layer", strings.Contains(layers, "B") && strings.Contains(layers, "KB") || strings.Contains(layers, "MB"), short2(layers, 200))
	ck("downloaded story is listed", p.count("#ss-downloads li:not(.ss-empty)") == 1)
	p.shot("offline-storage-tab.png")
	p.click("#ss-clear")
	p.click("[data-ok]")
	p.sleep(800)
	st = p.cacheState()
	ck("'Xoá bộ nhớ đệm' keeps downloads", st["mythlab-offline"] >= 30, st)
	p.click("#ss-clear-all")
	p.click("[data-ok]")
	p.sleep(1200)
	st = p.cacheState()
	left := map[string]int{}
	for k, v := range st {
		switch k {
		case "mythlab-offline", "mythlab-chapters", "mythlab-covers", "mythlab-tts", "mythlab-api":
			if v != 0 {
				left[k] = v
			}
		}
	}
	ck("clearing removes every data cache", len(left) == 0, st)
	shellKept := false
	for k, v := range st {
		if strings.HasPrefix(k, "mythlab-shell-") && v > 0 {
			shellKept = true
		}
	}
	ck("shell cache survives the clear", shellKept, st)
	ck("downloads list is empty after clearing", p.count("#ss-downloads .ss-empty") == 1)
	p.shot("offline-cleared.png")
	p.key(kb.Escape)
	p.offline(host.Gate, true)
	p.goto_(fmt.Sprintf("%s#/r/local0/%s/3", base, enc(offlineKey)))
	p.sleep(2500)
	ck("after clearing, offline reading no longer works (and says so)", p.count("#rd-body p") == 0 && len(strings.TrimSpace(ev[string](p, "document.body.innerText"))) > 20)
	_, perr, _ := p.snapshot()
	ck("no uncaught page errors", len(perr) == 0, first(perr, 3))
}

// legacyStatic returns a directory with the old reader/static build: the working tree copy when it is still there,
// otherwise the one in git HEAD (read only; nothing in the repository is touched).
func legacyStatic(t *testing.T) string {
	t.Helper()
	if _, err := os.Stat(filepath.Join(oldStatic, "index.html")); err == nil {
		return oldStatic
	}
	dir := t.TempDir()
	cmd := exec.Command("git", "-C", repoRoot, "archive", "--format=tar", "HEAD", "reader/static")
	out, err := cmd.StdoutPipe()
	if err != nil {
		t.Skipf("the old reader/static build is gone and git is not usable: %v", err)
	}
	if err := cmd.Start(); err != nil {
		t.Skipf("the old reader/static build is gone and git is not usable: %v", err)
	}
	tr := tar.NewReader(out)
	n := 0
	for {
		h, err := tr.Next()
		if err != nil {
			break
		}
		if h.Typeflag != tar.TypeReg {
			continue
		}
		rel := strings.TrimPrefix(path.Clean(h.Name), "reader/static/")
		dst := filepath.Join(dir, filepath.FromSlash(rel))
		if !strings.HasPrefix(dst, dir) {
			continue
		}
		_ = os.MkdirAll(filepath.Dir(dst), 0o755)
		f, err := os.Create(dst)
		if err != nil {
			continue
		}
		_, _ = io.Copy(f, tr)
		f.Close()
		n++
	}
	_ = cmd.Wait()
	if n == 0 {
		t.Skip("the old reader/static build exists neither in the working tree nor in git HEAD")
	}
	return dir
}

func TestOfflineUpgrade(t *testing.T) {
	needEnv(t)
	oldDir := legacyStatic(t)
	host := startHost(t, oldDir)
	br := newBrowser(t)
	base := host.URL + "/"
	c := &Checker{t: t}
	numbers := map[string]any{}
	defer func() {
		b, _ := json.MarshalIndent(map[string]any{"checks": c.Results, "numbers": numbers}, "", " ")
		_ = os.WriteFile(filepath.Join(outDir, "offline-upgrade-results.json"), b, 0o644)
	}()
	ck := func(name string, ok bool, detail ...any) { t.Helper(); c.check("upgrade", name, ok, detail...) }

	p := br.newPage(t, PageOpts{W: 1280, H: 860})
	defer p.Close()
	p.goto_(base)
	if err := p.waitControlled(8 * time.Second); err != nil {
		p.reload()
		p.must(p.waitControlled(15*time.Second), "old service worker controls the page")
	}
	oldCaches := p.cacheState()
	oldSW := ev[string](p, "navigator.serviceWorker.controller.scriptURL")
	numbers["old_sw_caches"] = oldCaches
	ck("old build installed its service worker", oldSW != "" && len(oldCaches) >= 1, oldCaches)
	p.shot("upgrade-1-old.png")

	host.SetRoot(webDist) // same port, new build
	blank, attempts, booted := 0, 0, false
	for attempts = 1; attempts < 5; attempts++ {
		p.reload()
		p.sleep(1200)
		n, _ := evTry[int](p, "document.body ? document.body.innerText.trim().length : 0")
		if n < 20 {
			blank++
		}
		if b, _ := evTry[bool](p, "window.__mlBooted === true"); b {
			booted = true
			break
		}
	}
	numbers["upgrade_reloads_until_new_shell"] = attempts
	ck("the new shell takes over", booted, fmt.Sprintf("after %d reloads", attempts))
	ck("no blank page during the upgrade", blank == 0, fmt.Sprintf("%d blank loads", blank))
	p.shot("upgrade-2-new.png")
	_ = p.waitFn("navigator.serviceWorker.controller && navigator.serviceWorker.controller.scriptURL.endsWith('sw.js')", 10*time.Second)
	// let activation and the purge of old caches finish
	p.sleep(2500)
	p.reload()
	p.must(p.waitFn("window.__mlBooted === true", 20*time.Second), "new shell boots")
	p.sleep(1500)
	st := p.cacheState()
	var shells []string
	for k := range st {
		if strings.HasPrefix(k, "mythlab-shell-") {
			shells = append(shells, k)
		}
	}
	numbers["caches_after_upgrade"] = st
	ck("exactly one shell cache after the upgrade", len(shells) == 1, st)
	oldGone := true
	for k := range oldCaches {
		if strings.HasPrefix(k, "mythlab-static") || strings.HasPrefix(k, "mythlab-shell-") {
			isShell := false
			for _, s := range shells {
				if s == k {
					isShell = true
				}
			}
			if _, still := st[k]; still && !isShell {
				oldGone = false
			}
		}
	}
	ck("old shell caches are gone", oldGone, fmt.Sprintf("old=%v now=%v", keysOf(oldCaches), keysOf(st)))
	ver := ev[any](p, `new Promise((res) => { const ch = new MessageChannel(); ch.port1.onmessage = (e) => res(e.data); navigator.serviceWorker.controller.postMessage({ type: 'GET_VERSION' }, [ch.port2]); setTimeout(() => res(null), 3000); })`)
	ck("the new worker answers GET_VERSION", ver != nil && ver != "" && ver != false, ver)

	// bug W1: a non-shell response to a navigation must never become the shell
	const shellKeysJS = `(async () => { const k = (await caches.keys()).find(x => x.startsWith('mythlab-shell-')); return (await (await caches.open(k)).keys()).map(r => new URL(r.url).pathname); })()`
	shellKeys := ev[[]string](p, shellKeysJS)
	_ = p.gotoTry(base + "no-such-page.html") // a 404 document is reported by the browser as a failed navigation
	p.sleep(800)
	p.goto_(base)
	p.must(p.waitFn("window.__mlBooted === true", 20*time.Second), "shell boots after the 404")
	afterKeys := ev[[]string](p, shellKeysJS)
	has404 := false
	for _, k := range afterKeys {
		if k == "/no-such-page.html" {
			has404 = true
		}
	}
	ck("a 404 navigation is not cached into the shell (W1)", !has404 && len(afterKeys) == len(shellKeys), fmt.Sprintf("%d %d", len(shellKeys), len(afterKeys)))
	p.offline(host.Gate, true)
	err := p.gotoTry(base)
	if err != nil {
		t.Logf("offline navigation: %v", err)
	}
	p.must(p.waitFn("window.__mlBooted === true", 20*time.Second), "shell boots offline after the upgrade")
	ck("new shell opens offline after the upgrade", ev[int](p, "document.body.innerText.trim().length") > 20)
}

func keysOf(m map[string]int) []string {
	var out []string
	for k := range m {
		out = append(out, k)
	}
	return out
}
