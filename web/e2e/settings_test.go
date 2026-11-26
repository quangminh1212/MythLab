package e2e

// Port of web/e2e/settings.py: the settings sheet against the built web/dist.
//
//   - every control of the sheet changes its CSS variable / data attribute and persists across a reload;
//   - the sheet is an accessible dialog (role, aria-modal, focus trap, Escape, focus return, tablist keys);
//   - on a phone the bottom sheet is at most ~55 % high and leaves the reading text visible and uncovered;
//   - presets, font picker and reset to defaults;
//   - the secrets inputs never contain a stored secret;
//   - export contains no secret by default.

import (
	"fmt"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/chromedp/chromedp/kb"
)

const settingsKey = "Mạt Thế Cổ Đại Cầu Sinh"

// the fake LAN key the test seeds to prove that it never reaches the DOM or the default export
const fakeLANKey = "SECRET-LAN-KEY-123"

func setSeed(api string) string {
	return seedScript(map[string]any{
		"mythlab.settings": map[string]any{"ui2": 1, "ui3": 1},
		"mythlab.server":   map[string]any{"url": api, "key": fakeLANKey},
	}, true)
}

func (p *Page) boot(u string) {
	p.t.Helper()
	p.goto_(u)
	p.must(p.waitFn("window.__mlBooted === true", 20*time.Second), "wait __mlBooted")
	p.sleep(300)
}

// clickNth clicks the n-th element matching sel (Playwright locator.nth(n).click()).
func (p *Page) clickNth(sel string, n int) {
	p.t.Helper()
	p.exec(fmt.Sprintf(`document.querySelectorAll(%s)[%d].setAttribute('data-e2e-nth', '1')`, jq(sel), n))
	defer p.exec(`document.querySelectorAll('[data-e2e-nth]').forEach((e) => e.removeAttribute('data-e2e-nth'))`)
	p.click("[data-e2e-nth]")
}

// setChecked clicks a checkbox only when its state differs (Playwright check / uncheck).
func (p *Page) setChecked(sel string, want bool) {
	p.t.Helper()
	p.mustWait("!!document.querySelector("+jq(sel)+")", 15*time.Second)
	p.exec(fmt.Sprintf(`((e) => { if (e.checked !== %v) e.click(); })(document.querySelector(%s))`, want, jq(sel)))
}

func (p *Page) cssVar(name string) string {
	return call[string](p, "(n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim()", name)
}

func (p *Page) settingsStored() map[string]any {
	m := ev[map[string]any](p, "JSON.parse(localStorage.getItem('mythlab.settings') || '{}')")
	if m == nil {
		m = map[string]any{}
	}
	return m
}

func (p *Page) openSheet(tab string) {
	p.t.Helper()
	if p.visible("#btn-settings") {
		p.click("#btn-settings")
	} else { // the reader hides the top bar: chrome "more" button, then "Cài đặt đọc"
		p.exec(`document.querySelector('#rd [data-act="more"]').click()`)
		p.click(`[data-more="settings"]`)
	}
	p.mustVisible(".ss-panel", 5*time.Second)
	if tab != "" {
		p.openGroup(tab)
		p.mustVisible(fmt.Sprintf("#ss-pane-%s:not([hidden])", tab), 15*time.Second)
	}
}

// openGroup expands a settings menu group (no-op when it is already open: clicking an open row collapses it).
func (p *Page) openGroup(tab string) {
	p.t.Helper()
	if p.attr(fmt.Sprintf("#ss-tab-%s", tab), "aria-expanded") != "true" {
		p.click(fmt.Sprintf(`#ss-tab-%s`, tab))
	}
}

func (p *Page) closeSheet() {
	p.t.Helper()
	p.key(kb.Escape)
	p.must(p.waitGone(".ss-panel", 3*time.Second), "sheet closes")
}

func num(v any) float64 {
	f, _ := v.(float64)
	return f
}

func TestSettings(t *testing.T) {
	needEnv(t)
	srv := startServer(t, false)
	host := startHost(t, webDist)
	br := newBrowser(t)
	base := host.URL + "/index.html"

	t.Run("desktop", func(t *testing.T) {
		c := &Checker{t: t}
		defer c.save("settings-desktop.json")
		ck := func(name string, ok bool, detail ...any) { t.Helper(); c.check("settings", name, ok, detail...) }
		p := br.newPage(t, PageOpts{W: 1440, H: 900, Init: []string{setSeed(srv.URL)}})
		defer p.Close()
		dlDir := t.TempDir()
		p.downloadsTo(dlDir)
		p.boot(base)
		p.openSheet("theme")
		p.shot("settings-desktop-theme.png")

		sliders := []struct{ tab, key, val, cssvar, want string }{
			{"theme", "brightness", "0.7", "--brightness", "0.7"},
			{"font", "weight", "600", "--read-weight", "600"},
			{"font", "size", "26", "--read-size", "26px"},
			{"font", "line", "2.2", "--read-line", "2.2"},
			{"font", "letter", "0.8", "--read-letter", "0.8px"},
			{"font", "word", "3", "--read-word", "3px"},
			{"layout", "indent", "1.5", "--read-indent", "1.5em"},
			{"layout", "paraGap", "1.8", "--read-gap", "1.8em"},
			{"layout", "margin", "40", "--read-margin", "40px"},
			{"layout", "width", "900", "--read-width", "900px"},
		}
		for _, s := range sliders {
			p.openGroup(s.tab)
			p.fill(fmt.Sprintf(`#ss-pane-%s input[data-range="%s"]`, s.tab, s.key), s.val)
			got := p.cssVar(s.cssvar)
			ck(fmt.Sprintf("slider %s -> %s", s.key, s.cssvar), got == s.want, fmt.Sprintf("%q != %q", got, s.want))
			var want float64
			fmt.Sscan(s.val, &want)
			st := p.settingsStored()
			cur, has := st[s.key]
			ck(fmt.Sprintf("slider %s stored", s.key), has && num(cur) == want, cur)
		}

		p.openGroup("layout")
		p.clickForce(`#ss-pane-layout [data-seg="align"] input[value="left"]`)
		ck("align -> --read-align", p.cssVar("--read-align") == "left", p.cssVar("--read-align"))
		p.clickForce(`#ss-pane-layout [data-seg="readMode"] input[value="page"]`)
		ck("readMode attribute", ev[string](p, "document.documentElement.dataset.readmode || ''") == "page")
		p.setChecked(`#ss-pane-layout input[data-bool="tapZones"]`, false)
		ck("tapZones attribute", ev[string](p, "document.documentElement.dataset.tapzones || ''") == "off")

		p.openGroup("theme")
		p.clickForce(`#ss-pane-theme [data-seg="theme"] input[value="dark"]`)
		ck("theme attribute", ev[string](p, "document.documentElement.dataset.scheme || ''") == "dark")
		ck("theme-color follows theme", ev[string](p, "document.querySelector('meta[name=theme-color]').content") != "#ffffff")
		const swatches = `#ss-pane-theme [data-swatches='nightPreset'] [data-preset]`
		pid := ev[string](p, fmt.Sprintf("document.querySelectorAll(%s)[1].getAttribute('data-preset')", jq(swatches)))
		p.clickNth(swatches, 1)
		np, _ := p.settingsStored()["nightPreset"].(string)
		ck("night preset stored", np == pid, p.settingsStored()["nightPreset"])

		p.openGroup("font")
		before := p.cssVar("--font-read")
		nfonts := p.count("#ss-fonts [data-font]")
		ck("font picker lists the 20 bundled and system fonts", nfonts >= 20, nfonts)
		p.clickNth("#ss-fonts [data-font]", 5)
		ck("font changes --font-read", p.cssVar("--font-read") != before, p.cssVar("--font-read"))
		p.shot("settings-desktop-font.png")
		p.click("[data-typo-id='large']")
		_, hasSize := p.settingsStored()["size"]
		ck("typography preset applies", hasSize && p.attr("[data-typo-id='large']", "aria-checked") == "true")

		// quick row
		size0 := num(p.settingsStored()["size"])
		p.click(`[data-step="1"]`)
		ck("quick row size +", num(p.settingsStored()["size"]) == size0+1, p.settingsStored()["size"])
		p.click(`[data-step="-1"]`)
		ck("quick row size -", num(p.settingsStored()["size"]) == size0)
		snapshot := p.settingsStored()
		p.closeSheet()

		p.reload()
		p.must(p.waitFn("window.__mlBooted === true", 30*time.Second), "wait __mlBooted")
		p.sleep(300)
		after := p.settingsStored()
		diff := map[string][2]any{}
		for k, v := range snapshot {
			if fmt.Sprint(after[k]) != fmt.Sprint(v) {
				diff[k] = [2]any{v, after[k]}
			}
		}
		ck("settings persist across reload", len(diff) == 0, diff)
		ck("variables re-applied after reload",
			p.cssVar("--read-width") == fmt.Sprintf("%dpx", int(num(snapshot["width"]))) &&
				p.cssVar("--read-size") == fmt.Sprintf("%dpx", int(num(snapshot["size"]))) &&
				ev[string](p, "document.documentElement.dataset.scheme || ''") == "dark",
			p.cssVar("--read-width"), snapshot["width"])

		// reset
		p.openSheet("")
		p.click("[data-reset]")
		p.click("[data-ok]")
		p.sleep(200)
		ck("reset restores defaults", num(p.settingsStored()["size"]) == 20 && p.cssVar("--read-width") != fmt.Sprintf("%dpx", int(num(snapshot["width"]))), p.settingsStored()["size"])

		// ------------------------------------------------------------ a11y
		p.closeSheet()
		p.focus("#btn-settings")
		p.key(kb.Enter)
		p.mustVisible(".ss-panel", 15*time.Second)
		ck("dialog role+modal", p.attr(".ss-panel", "role") == "dialog" && p.attr(".ss-panel", "aria-modal") == "true")
		ck("dialog is labelled", p.attr(".ss-panel", "aria-labelledby") != "")
		ck("menu rows are disclosure buttons", p.count(`.ss-menu button.ss-group-btn[aria-expanded][aria-controls]`) >= 5 && p.count(`.ss-menu [role="region"]`) >= 5)
		ck("exactly one group expanded", p.count(`.ss-group-btn[aria-expanded="true"]`) == 1 && p.count(`.ss-pane:not([hidden])`) == 1)
		const inPanel = "!!document.activeElement.closest('.ss-panel')"
		ck("focus moves into the sheet", ev[bool](p, inPanel))
		escaped := 0
		for i := 0; i < 45; i++ {
			p.key(kb.Tab)
			if !ev[bool](p, inPanel) {
				escaped++
			}
		}
		ck("focus trap holds over 45 Tab presses", escaped == 0, escaped)
		for i := 0; i < 45; i++ {
			p.keyShift(kb.Tab)
			if !ev[bool](p, inPanel) {
				escaped++
			}
		}
		ck("focus trap holds backwards", escaped == 0, escaped)
		p.focus(`.ss-group-btn[aria-expanded="true"]`)
		cur := ev[string](p, "document.activeElement.dataset.tab || ''")
		p.key(kb.ArrowDown)
		nxt := ev[string](p, "document.activeElement.dataset.tab || ''")
		ck("arrow keys move between menu rows", cur != nxt && nxt != "", cur, nxt)
		p.key(kb.Enter)
		ck("Enter expands the focused row", p.count(fmt.Sprintf("#ss-pane-%s:not([hidden])", nxt)) == 1 && p.attr(fmt.Sprintf("#ss-tab-%s", nxt), "aria-expanded") == "true", nxt)
		p.key(kb.Enter)
		ck("Enter again collapses it", p.count(".ss-pane:not([hidden])") == 0)
		p.key(kb.Escape)
		p.must(p.waitGone(".ss-panel", 5*time.Second), "sheet closes")
		ck("Escape closes and returns focus", ev[string](p, "document.activeElement.id") == "btn-settings", ev[string](p, "document.activeElement.id"))

		// ------------------------------------------------------------ data-source tab: no secret in the DOM
		p.openSheet("source")
		p.mustVisible("#ss-srv-url", 15*time.Second)
		dump := ev[string](p, "document.querySelector('.ss-panel').outerHTML + [...document.querySelectorAll('.ss-panel input')].map(i => i.value).join('|')")
		ck("stored server key not echoed into the sheet", !strings.Contains(dump, fakeLANKey))
		ck("key field is a password input and empty", ev[bool](p, "(() => { const i = document.querySelector('#ss-srv-key'); return i.type === 'password' && i.value === ''; })()"))
		ck("token field is a password input and empty", ev[bool](p, "(() => { const i = document.querySelector('#ss-gh-tok'); return i.type === 'password' && i.value === ''; })()"))
		ck("saved-key hint shown", p.visible("#ss-srv-saved"))
		p.fill("#ss-srv-url", srv.URL)
		p.click("#ss-srv-test")
		p.must(p.waitFn(`(() => { const t = document.querySelector('#ss-srv-msg').textContent.trim(); return t.length > 3 && !t.startsWith('Đang'); })()`, 15*time.Second), "server test verdict")
		msg := p.text("#ss-srv-msg")
		ck("server test gives a verdict", strings.HasPrefix(msg, "✓") || strings.HasPrefix(msg, "✗"), msg)
		p.fill("#ss-gh-tok", "github_pat_not_real_xxxxxxxxxxxxxxxx")
		p.click("#ss-gh-test")
		p.must(p.waitFn(`(() => { const t = document.querySelector('#ss-gh-msg').textContent.trim(); return t.length > 3 && !t.startsWith('Đang'); })()`, 20*time.Second), "token test verdict")
		gm := p.text("#ss-gh-msg")
		ck("token test gives a verdict", strings.HasPrefix(gm, "✓") || strings.HasPrefix(gm, "✗"), gm)
		p.shot("settings-desktop-source.png")
		p.fill("#ss-gh-tok", "")
		// export has no secret by default
		seen := map[string]bool{}
		p.click("#ss-export")
		path, err := waitNewDownload(dlDir, seen, 15*time.Second)
		if err != nil {
			t.Fatalf("export download: %v", err)
		}
		raw, _ := os.ReadFile(path)
		text := string(raw)
		ck("export omits secrets by default", !strings.Contains(text, fakeLANKey) && !strings.Contains(text, "github_pat"))
		p.setChecked("#ss-exp-secrets", true)
		p.click("#ss-export")
		path2, err := waitNewDownload(dlDir, seen, 15*time.Second)
		if err != nil {
			t.Fatalf("second export download: %v", err)
		}
		raw2, _ := os.ReadFile(path2)
		ck("export includes the key only when ticked", strings.Contains(string(raw2), fakeLANKey))
		// import round trip
		p.uploadFile("#ss-import-file", path)
		p.mustVisible("#ss-import:not([hidden]) [data-imp='go']", 15*time.Second)
		p.click("[data-imp='go']")
		ck("import finishes without error", p.count(".toast, [role=status]") >= 1)
		cons, perr, _ := p.snapshot()
		var errs []string
		for _, e := range cons {
			if !strings.Contains(e, "404") && !strings.Contains(e, "401") {
				errs = append(errs, e)
			}
		}
		for _, e := range perr {
			errs = append(errs, "pageerror: "+e)
		}
		ck("no console errors", len(errs) == 0, first(errs, 3))
		p.closeSheet()
	})

	t.Run("mobile", func(t *testing.T) {
		c := &Checker{t: t}
		defer c.save("settings-mobile.json")
		ck := func(name string, ok bool, detail ...any) { t.Helper(); c.check("settings", name, ok, detail...) }
		p := br.newPage(t, PageOpts{W: 390, H: 844, Mobile: true, Init: []string{setSeed(srv.URL)}})
		defer p.Close()
		p.boot(base + "#/r/local0/" + enc(settingsKey) + "/0")
		p.mustVisible("#rd-body p", 20*time.Second)
		p.sleep(500)
		p.openSheet("font")
		p.sleep(400)
		type sheetM struct {
			Top      float64 `json:"top"`
			Height   float64 `json:"height"`
			VH       float64 `json:"vh"`
			Visible  int     `json:"visible"`
			HitPanel *bool   `json:"hitPanel"`
			OW       float64 `json:"ow"`
		}
		m := ev[sheetM](p, `(() => {
      const d = document.querySelector('.ss-panel').getBoundingClientRect();
      const ps = [...document.querySelectorAll('#rd-body p')];
      const vis = ps.filter(p => { const r = p.getBoundingClientRect(); return r.bottom > 60 && r.top < d.top - 4 && r.height > 0; });
      const mid = vis[0] ? vis[0].getBoundingClientRect() : null;
      let hit = null;
      if (mid) { const e = document.elementFromPoint(mid.left + 20, Math.min(mid.top + 10, d.top - 8)); hit = e ? !!e.closest('.ss-panel') : null; }
      return { top: d.top, height: d.height, vh: innerHeight, visible: vis.length, hitPanel: hit, ow: document.documentElement.scrollWidth };
    })()`)
		ck("mobile sheet is at most 55 % high", m.Height <= m.VH*0.55+1 || m.Height <= 301, fmt.Sprintf("%+v", m))
		ck("reading text visible above the sheet", m.Visible >= 1 && m.HitPanel != nil && !*m.HitPanel, fmt.Sprintf("%+v", m))
		ck("no horizontal overflow with the sheet open", m.OW <= 390, m.OW)
		// the page above stays interactive: changing the size from the sheet updates the text immediately
		h0 := ev[float64](p, "document.querySelector('#rd-body p').getBoundingClientRect().height")
		p.click(`[data-step="1"]`)
		p.click(`[data-step="1"]`)
		p.sleep(150)
		h1 := ev[float64](p, "document.querySelector('#rd-body p').getBoundingClientRect().height")
		ck("live: the text behind the sheet reflows", h1 != h0, h0, h1)
		p.shot("settings-mobile-font.png")
		small := ev[[]string](p, `[...document.querySelectorAll('.ss-panel button, .ss-panel input:not([type=range]), .ss-panel select, .ss-panel .ss-group-btn')].filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && cs.visibility !== 'hidden' && !e.closest('[hidden]') && (r.height < 43.5 || r.width < 43.5) && cs.opacity !== '0' && e.type !== 'radio' && e.type !== 'checkbox'; }).map(e => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height)).slice(0, 8)`)
		ck("tap targets >= 44 px in the sheet", len(small) == 0, small)
		for _, tab := range []string{"theme", "layout", "voice", "source"} {
			p.openGroup(tab)
			p.sleep(250)
			p.shot("settings-mobile-" + tab + ".png")
			ow := ev[float64](p, "document.documentElement.scrollWidth")
			pw := ev[float64](p, "(() => { const b = document.querySelector('.ss-panel .dialog-body'); return b.scrollWidth - b.clientWidth; })()")
			ck(fmt.Sprintf("mobile tab %s has no horizontal overflow", tab), ow <= 390 && pw <= 1, ow, pw)
		}
	})
}
