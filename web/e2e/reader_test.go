package e2e

// Port of web/e2e/reader.py: the reader and the audio player against the built web/dist.
//
// For 2 viewports (1440x900, 390x844) x 3 themes (light, dark, sepia) a long story is opened in scroll mode and in
// page mode and checked (one h1, no horizontal overflow, text contrast, tap targets on the phone, DOM size, no console
// errors). Once per viewport (light) the functional scenario runs: position restore, chapter drawer, prev/next,
// bookmarks, auto-scroll, keyboard help, tap zones vs. selection, swipes, reduced motion; text-to-speech has its own
// test (it needs the TTS backend and the network); local stories are read too.

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"testing"
	"time"

	"github.com/chromedp/chromedp/kb"
)

type rdViewport struct {
	name string
	w, h int
}

var rdViewports = []rdViewport{{"desktop", 1440, 900}, {"mobile", 390, 844}}

// rdHook records every media element that starts playing, so the test can read the clock of the audio.
const rdHook = `
(() => {
  window.__audios = [];
  const play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () {
    if (!window.__audios.includes(this)) window.__audios.push(this);
    return play.apply(this, arguments);
  };
})();
`

type readerMetrics struct {
	ScrollW     float64  `json:"scrollW"`
	HOverflow   bool     `json:"hOverflow"`
	Nodes       int      `json:"nodes"`
	ReaderNodes int      `json:"readerNodes"`
	Small       [][]any  `json:"small"`
	Cut         [][]any  `json:"cut"`
	H1          []string `json:"h1"`
	Title       string   `json:"title"`
	Paras       int      `json:"paras"`
	Mode        string   `json:"mode"`
}

func rdSeed(api, theme, mode string, extra map[string]any) string {
	settings := map[string]any{"theme": theme, "ui2": 1, "ui3": 1, "readMode": mode}
	for k, v := range extra {
		settings[k] = v
	}
	// written once per browser context: a reload must keep what the reader saved
	return seedScript(map[string]any{"mythlab.settings": settings, "mythlab.server": map[string]any{"url": api}}, true)
}

// rdRun is one reader page (own browser) plus the checks recorded for it.
type rdRun struct {
	t    *testing.T
	p    *Page
	c    *Checker
	vp   rdViewport
	tag  string
	base string
}

type rdOpts struct {
	theme, mode string
	extra       map[string]any
	reduced     bool
	hash        string
}

func newRd(t *testing.T, c *Checker, br *Browser, host *Host, srv *Server, vp rdViewport, o rdOpts) *rdRun {
	t.Helper()
	if o.theme == "" {
		o.theme = "light"
	}
	if o.mode == "" {
		o.mode = "scroll"
	}
	p := br.newPage(t, PageOpts{W: vp.w, H: vp.h, Mobile: vp.name == "mobile", Reduced: o.reduced,
		Init: []string{rdHook, rdSeed(srv.URL, o.theme, o.mode, o.extra)}})
	r := &rdRun{t: t, p: p, c: c, vp: vp, tag: fmt.Sprintf("%s-%s-%s", vp.name, o.theme, o.mode), base: host.URL}
	if o.hash != "" {
		r.open(o.hash)
	}
	return r
}

func (r *rdRun) open(hash string) {
	r.t.Helper()
	r.p.goto_(r.base + "/" + hash)
	r.ready()
}

func (r *rdRun) ready() {
	r.t.Helper()
	r.p.must(r.p.waitFn("window.__mlBooted === true", 30*time.Second), "wait __mlBooted")
	r.p.mustVisible("#rd-body > p", 60*time.Second)
	r.p.sleep(500)
}

func (r *rdRun) shot(name string) { r.p.shot(sanitize(r.tag + "-" + name + ".png")) }

func sanitize(s string) string { return strings.NewReplacer("/", "_", " ", "_", ":", "_").Replace(s) }

func (r *rdRun) showChrome() {
	if r.p.exists(".rd.rd-hide") {
		r.p.key(kb.Escape)
		r.p.sleep(300)
	}
}

func (r *rdRun) idx() int {
	n, _ := strconv.Atoi(ev[string](r.p, "location.hash.split('?')[0].split('/').pop()"))
	return n
}

func (r *rdRun) stored(key string) any {
	return call[any](r.p, "(k) => JSON.parse(localStorage.getItem(k) || 'null')", key)
}

// errs is what the page reported on the console, as pageerror and as HTTP >= 400 (the static host has no /api/ping).
func (r *rdRun) errs() []string {
	cons, perr, herr := r.p.snapshot()
	out := append([]string(nil), cons...)
	for _, e := range perr {
		out = append(out, "pageerror: "+e)
	}
	for _, h := range herr {
		if strings.HasPrefix(h.URL, r.base) && strings.HasSuffix(h.URL, "/api/ping") {
			continue
		}
		out = append(out, fmt.Sprintf("HTTP %d %s", h.Status, h.URL))
	}
	return out
}

func (r *rdRun) check(name string, ok bool, detail ...any) {
	r.t.Helper()
	r.c.check(r.tag, name, ok, detail...)
}

func (r *rdRun) scrollY() float64 { return ev[float64](r.p, "window.scrollY") }

func (r *rdRun) pager() (int, int) {
	t := strings.TrimSpace(strings.ReplaceAll(r.p.text("#rd-pager-pos"), "Trang", ""))
	parts := strings.Split(t, "/")
	if len(parts) != 2 {
		return 0, 0
	}
	a, e1 := strconv.Atoi(strings.TrimSpace(parts[0]))
	b, e2 := strconv.Atoi(strings.TrimSpace(parts[1]))
	if e1 != nil || e2 != nil {
		return 0, 0
	}
	return a, b
}

// tapAt is a touch tap on the phone and a mouse click on the desktop.
func (r *rdRun) tapAt(x, y float64) {
	if r.vp.name == "mobile" {
		r.p.tap(x, y)
	} else {
		r.p.mouseClick(x, y)
	}
}

func rdHash(idx int, q string) string {
	return fmt.Sprintf("#/r/%s/%s/%d%s", ghSource, enc(ghKey), idx, q)
}

func (r *rdRun) basics(label string) readerMetrics {
	r.t.Helper()
	m := call[readerMetrics](r.p, readerMetricsJS, r.vp.w)
	r.check(label+": one h1", len(m.H1) == 1, m.H1)
	r.check(label+": title is set", m.Title != "" && strings.Contains(m.Title, "MythLab"), m.Title)
	r.check(label+": no horizontal overflow", !m.HOverflow, fmt.Sprintf("scrollW=%v", m.ScrollW))
	r.check(label+": nothing cut off", len(m.Cut) == 0, m.Cut)
	r.check(label+": reader DOM < 1500 nodes", m.ReaderNodes < 1500 && m.Nodes < 1500, fmt.Sprintf("view=%d page=%d paras=%d", m.ReaderNodes, m.Nodes, m.Paras))
	c := ev[contrastResult](r.p, "("+readerContrastJS+")()")
	r.check(label+": text contrast AA", len(c.Bad) == 0, fmt.Sprintf("checked %d %v", c.Checked, c.Bad))
	if r.vp.name == "mobile" {
		r.check(label+": tap targets >= 44 px", len(m.Small) == 0, m.Small)
	}
	return m
}

// rdEnv starts what every reader test needs: the API server, the static host and the browser factory.
func rdEnv(t *testing.T, withTTS, needGH bool) (*Server, *Host, *Browser) {
	t.Helper()
	needEnv(t)
	srv := startServer(t, withTTS)
	if needGH && !srv.ghReady(t) {
		t.Skip("GitHub library unavailable (no token / no network): the gh0 story cannot be read")
	}
	return srv, startHost(t, webDist), newBrowser(t)
}

// clearServerProgress deletes every reading position the sync server holds (a deletion newer than each entry), after
// the closing page had time to push its last position.
func clearServerProgress(t *testing.T, srv *Server) {
	t.Helper()
	type entry struct {
		Source  string `json:"source"`
		Key     string `json:"key"`
		Ts      int64  `json:"ts"`
		Deleted bool   `json:"deleted,omitempty"`
	}
	var now int64
	list := func() []entry {
		resp, err := http.Get(srv.URL + "/api/progress")
		if err != nil {
			t.Fatalf("progress list: %v", err)
		}
		defer resp.Body.Close()
		var b struct {
			Entries []entry `json:"entries"`
			Now     int64   `json:"now"`
		}
		_ = json.NewDecoder(resp.Body).Decode(&b)
		now = b.Now
		var live []entry
		for _, e := range b.Entries {
			if !e.Deleted {
				live = append(live, e)
			}
		}
		return live
	}
	// the closing page pushes its last position on pagehide (keepalive), a moment after the page is gone: delete,
	// and delete again until nothing live is left after a quiet moment.
	time.Sleep(1200 * time.Millisecond)
	for i := 0; i < 6; i++ {
		var del []entry
		for _, e := range list() {
			del = append(del, entry{e.Source, e.Key, max(e.Ts+1, now), true})
		}
		if len(del) == 0 {
			return
		}
		body, _ := json.Marshal(map[string]any{"entries": del})
		req, _ := http.NewRequest(http.MethodPut, srv.URL+"/api/progress", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			t.Fatalf("progress delete: %v", err)
		}
		resp.Body.Close()
		time.Sleep(800 * time.Millisecond)
	}
}

func TestReaderThemes(t *testing.T) {
	srv, host, br := rdEnv(t, false, true)
	for _, vp := range rdViewports {
		for _, theme := range []string{"light", "dark", "sepia"} {
			vp, theme := vp, theme
			name := vp.name + "-" + theme
			if !only("reader-" + name) {
				continue
			}
			t.Run(name, func(t *testing.T) {
				c := &Checker{t: t}
				defer c.save("reader-themes-" + name + ".json")

				// scroll mode
				r := newRd(t, c, br, host, srv, vp, rdOpts{theme: theme, mode: "scroll", hash: rdHash(3, "")})
				r.shot("scroll")
				r.basics("scroll")
				if vp.name == "desktop" {
					r.p.wheel(float64(vp.w)/2, float64(vp.h)/2, 0, 900)
				} else {
					r.p.exec("window.scrollBy(0, 900)")
				}
				r.p.sleep(500)
				r.shot("scroll-mid")
				r.p.exec("window.scrollTo(0, document.documentElement.scrollHeight)")
				r.p.sleep(500)
				r.shot("scroll-end")
				r.check("end of chapter shows the next link", r.p.visible(".rd-end a[rel=next]"))
				r.check("no console errors (scroll)", len(r.errs()) == 0, first(r.errs(), 3))
				r.p.Close()

				// page mode: a new page is a new device (storage wiped), and the server would hand the saved position back
				// (progress sync), so the test starts from a library without progress.
				clearServerProgress(t, srv)
				r = newRd(t, c, br, host, srv, vp, rdOpts{theme: theme, mode: "page", hash: rdHash(3, "")})
				r.p.sleep(300)
				r.shot("page")
				r.basics("page")
				a, b := r.pager()
				r.check("page mode has several pages", b > 1 && a == 1, fmt.Sprintf("%d/%d", a, b))
				r.check("page mode: nothing scrolls", ev[bool](r.p, "(() => { window.scrollTo(0, 500); return window.scrollY === 0; })()"))
				r.p.key(kb.ArrowRight)
				r.p.sleep(450)
				a2, _ := r.pager()
				r.check("ArrowRight turns the page", a2 == 2, a2)
				r.shot("page-2")
				r.check("no console errors (page)", len(r.errs()) == 0, first(r.errs(), 3))
				r.p.Close()
			})
		}
	}
}

const rdSayIdxJS = `(document.querySelector('mark.rd-say') || {}).closest ? document.querySelector('mark.rd-say').closest('p').dataset.i : ''`
const rdMarkJS = `(document.querySelector('mark.rd-say') || {}).textContent || ''`
const rdLastAudioJS = `(() => { const a = (window.__audios || []); const x = a[a.length - 1]; return x ? [x.paused, x.currentTime] : null; })()`

func TestReaderFunctional(t *testing.T) {
	srv, host, br := rdEnv(t, false, true)
	for _, vp := range rdViewports {
		vp := vp
		if !only("reader-functional-" + vp.name) {
			continue
		}
		t.Run(vp.name, func(t *testing.T) {
			c := &Checker{t: t}
			defer c.save("reader-functional-" + vp.name + ".json")

			// ---- restore drift (scroll mode)
			r := newRd(t, c, br, host, srv, vp, rdOpts{mode: "scroll", hash: rdHash(5, "")})
			p := r.p
			p.exec("window.scrollTo(0, 2300)")
			p.sleep(1800)
			y1 := r.scrollY()
			sv, _ := r.stored("mythlab.progress").(map[string]any)
			var ent map[string]any
			for _, v := range sv {
				ent, _ = v.(map[string]any)
				break
			}
			para, _ := ent["para"].(float64)
			_, hasFile := ent["file"]
			_, hasFrac := ent["frac"]
			idx5, _ := ent["idx"].(float64)
			r.check("progress saved with file/frac/idx", idx5 == 5 && hasFile && hasFrac && para > 0,
				fmt.Sprintf("idx=%v para=%v frac=%v file=%v maxIdx=%v", ent["idx"], ent["para"], ent["frac"], ent["file"], ent["maxIdx"]))
			p.reload()
			r.ready()
			p.sleep(900)
			y2 := r.scrollY()
			r.check("restore after reload: drift <= 2 px", absF(y1-y2) <= 2, fmt.Sprintf("before=%v after=%v drift=%v", y1, y2, absF(y1-y2)))
			// a saved position survives a different font size (anchor is paragraph + fraction)
			p.goto_(r.base + "/#/")
			p.sleep(300)
			p.back()
			r.ready()
			p.sleep(700)
			y3 := r.scrollY()
			r.check("restore after leaving and coming back", absF(y1-y3) <= 2, fmt.Sprintf("drift=%v", absF(y1-y3)))

			// ---- prev / next, keys
			r.showChrome()
			p.click(`[data-act="next"]`)
			p.sleep(900)
			r.check("next button opens the next chapter", r.idx() == 6, r.idx())
			if !p.exists(".rd.rd-hide") {
				p.click(`[data-act="prev"]`)
			} else {
				p.key(kb.Escape)
				p.click(`[data-act="prev"]`)
			}
			p.sleep(900)
			r.check("prev button goes back", r.idx() == 5, r.idx())
			p.key(kb.ArrowRight)
			p.sleep(900)
			r.check("ArrowRight opens the next chapter (scroll mode)", r.idx() == 6, r.idx())
			p.key(kb.ArrowLeft)
			p.sleep(900)
			r.check("ArrowLeft opens the previous chapter", r.idx() == 5, r.idx())
			p.exec("window.scrollTo(0, document.documentElement.scrollHeight)")
			p.sleep(500)
			p.click(".rd-end a[rel=next]")
			p.sleep(900)
			r.check("end-of-chapter link opens the next chapter", r.idx() == 6, r.idx())
			top := r.scrollY()
			r.check("new chapter opens at the top", top <= 2, top)

			// ---- help dialog
			p.key("?")
			p.mustVisible(".rd-help", 3*time.Second)
			r.check("? opens the keyboard help", p.visible(".rd-help"))
			r.shot("help")
			p.key(kb.Escape)
			p.sleep(300)
			r.check("Escape closes the help", !p.exists(".rd-help"))

			// ---- drawer: jump to chapter 2000
			p.key("m")
			p.mustVisible("#rd-jump", 3*time.Second)
			p.sleep(400)
			r.shot("drawer")
			rows := p.count(".rd-dr-row")
			cur := ""
			if p.exists(".rd-dr-row.is-current") {
				cur = p.text(".rd-dr-row.is-current .rd-dr-num")
			}
			r.check("drawer is virtualised and shows the current chapter", rows > 0 && rows < 80 && cur == "7", fmt.Sprintf("rows=%d current=%s", rows, cur))
			p.fill("#rd-jump", "2000")
			p.pressOn("#rd-jump", kb.Enter)
			p.sleep(1200)
			title := p.text("#rd-title")
			r.check("drawer jump to chapter 2000", r.idx() == 1999 && strings.Contains(title, "2000"), fmt.Sprintf("idx=%d %s", r.idx(), short2(title, 40)))
			r.shot("ch2000")
			p.reload()
			r.ready()
			p.sleep(400)
			r.check("chapter 2000 survives a reload", r.idx() == 1999)

			// ---- bookmarks
			p.goto_(r.base + "/" + rdHash(8, ""))
			r.ready()
			p.exec("window.scrollTo(0, 1500)")
			p.sleep(500)
			p.key("b")
			p.sleep(400)
			bms, _ := r.stored("mythlab.bookmarks").([]any)
			bm0 := map[string]any{}
			if len(bms) > 0 {
				bm0, _ = bms[0].(map[string]any)
			}
			exc, _ := bm0["excerpt"].(string)
			bidx, _ := bm0["idx"].(float64)
			bpara, _ := bm0["para"].(float64)
			r.check("B adds a bookmark with an excerpt", len(bms) == 1 && exc != "" && bidx == 8, fmt.Sprintf("%d bookmarks idx=%v para=%v %s", len(bms), bidx, bpara, short2(exc, 30)))
			r.shot("bookmarked")
			p.key("m")
			p.mustVisible("#rd-jump", 15*time.Second)
			p.click("#rd-tab-marks")
			p.mustVisible(".rd-dr-mark", 3*time.Second)
			r.check("bookmark list shows the bookmark", p.count(".rd-dr-mark") == 1)
			r.shot("marks")
			p.key(kb.Escape)
			p.sleep(300)
			p.goto_(r.base + "/" + rdHash(1, ""))
			r.ready()
			p.key("m")
			p.mustVisible("#rd-jump", 15*time.Second)
			p.click("#rd-tab-marks")
			p.click(".rd-dr-mark-link")
			p.sleep(1200)
			h := ev[string](p, "location.hash")
			paraAt := ev[int](p, `(() => { const l = 84; const ps = [...document.querySelectorAll('#rd-body > p')]; const i = ps.findIndex((e) => e.getBoundingClientRect().bottom > l); return i; })()`)
			r.check("bookmark opens its chapter at its paragraph, ?p= removed",
				r.idx() == 8 && !strings.Contains(h, "?p=") && absF(float64(paraAt)-bpara) <= 1,
				fmt.Sprintf("%s para@line=%d saved=%v", tail(h, 24), paraAt, bpara))
			p.key("b")
			p.sleep(300)
			left, _ := r.stored("mythlab.bookmarks").([]any)
			r.check("B again removes the bookmark", len(left) == 0)

			// ---- auto-scroll
			p.exec("window.scrollTo(0, 0)")
			p.sleep(300)
			p.key("a")
			p.sleep(300)
			a0 := r.scrollY()
			r.check("auto-scroll panel appears", p.visible("#rd-auto"))
			p.sleep(1500)
			a1 := r.scrollY()
			p.key("+")
			p.sleep(200)
			lvl := p.text("#rd-auto-level")
			r.shot("autoscroll")
			r.check("auto-scroll moves the page and speed changes", a1 > a0+10 && strings.Contains(lvl, "5/9"), fmt.Sprintf("%v->%v %s", a0, a1, lvl))
			p.key(kb.Escape)
			p.sleep(200)
			b0 := r.scrollY()
			p.sleep(600)
			r.check("Escape stops auto-scroll", r.scrollY() == b0 && !p.visible("#rd-auto"))
			r.check("chapter changes replace history (history length stable)", ev[int](p, "history.length") >= 1)

			// ---- swipe between chapters (scroll mode)
			if vp.name == "mobile" {
				i0 := r.idx()
				p.swipe(120, 100, 420)
				p.sleep(500)
				r.check("short swipe does not change chapter", r.idx() == i0)
				p.swipe(384, 20, 420)
				p.sleep(500)
				r.check("swipe from the screen edge is left to the system", r.idx() == i0)
				p.swipe(320, 80, 420)
				p.sleep(1000)
				r.check("long swipe left opens the next chapter", r.idx() == i0+1, r.idx())
				p.swipe(60, 330, 420)
				p.sleep(1000)
				r.check("long swipe right goes back", r.idx() == i0, r.idx())
			}
			r.check("no console errors (functional)", len(r.errs()) == 0, first(r.errs(), 4))
			p.Close()

			// ---- page mode: tap zones, selection, double click, restore, wheel
			r = newRd(t, c, br, host, srv, vp, rdOpts{mode: "page", hash: rdHash(5, "")})
			p = r.p
			p.sleep(300)
			W := float64(r.vp.w)
			H := float64(r.vp.h)

			r.tapAt(W-10, H/2)
			p.sleep(700)
			pa, pb := r.pager()
			r.check("tap on the right zone turns the page", pa == 2, fmt.Sprintf("%d/%d", pa, pb))
			r.tapAt(10, H/2)
			p.sleep(700)
			pa, pb = r.pager()
			r.check("tap on the left zone turns back", pa == 1, fmt.Sprintf("%d/%d", pa, pb))
			// selection blocks the zones
			p.exec(`(() => { const el = document.querySelector('#rd-body > p'); const s = getSelection(); s.removeAllRanges(); const r = document.createRange(); r.selectNodeContents(el); s.addRange(r); })()`)
			r.tapAt(W-10, H/2)
			p.sleep(700)
			pa, pb = r.pager()
			r.check("a text selection is not broken by a tap zone", pa == 1, fmt.Sprintf("%d/%d", pa, pb))
			p.exec("getSelection().removeAllRanges()")
			if vp.name == "desktop" {
				box := ev[[]float64](p, `(() => { const r = document.querySelector('#rd-body > p:nth-child(3)').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()`)
				p.mouseDblClick(box[0]+8, box[1]+8)
				p.sleep(700)
				pa, pb = r.pager()
				r.check("double click does not turn the page", pa == 1, fmt.Sprintf("page=%d/%d", pa, pb))
				p.key(kb.Escape)
				p.mouseMove(600, 300)
				p.wheel(600, 300, 0, 300)
				p.sleep(700)
				pa, pb = r.pager()
				r.check("wheel turns one page", pa == 2, fmt.Sprintf("%d/%d", pa, pb))
			} else {
				p.swipe(300, 120, 420)
				p.sleep(700)
				pa, pb = r.pager()
				r.check("swipe left turns the page", pa == 2, fmt.Sprintf("%d/%d", pa, pb))
			}
			// go to page 3 and restore it after a reload
			p.key(kb.Home)
			p.sleep(450)
			p.key(kb.PageDown)
			p.sleep(450)
			p.key(kb.PageDown)
			p.sleep(450)
			pg, _ := r.pager()
			p.sleep(1700)
			p.reload()
			r.ready()
			p.sleep(600)
			pa, _ = r.pager()
			r.check("page mode restores the page after reload", absInt(pa-pg) <= 1, fmt.Sprintf("before=%d after=%d", pg, pa))
			// last page -> next chapter, first page -> previous chapter at its last page
			p.key(kb.End)
			p.sleep(450)
			pa, pb = r.pager()
			r.check("End goes to the last page", pa == pb, fmt.Sprintf("%d/%d", pa, pb))
			r.shot("page-last")
			p.key(kb.ArrowRight)
			p.sleep(1200)
			pa, pb = r.pager()
			r.check("past the last page opens the next chapter", r.idx() == 6 && pa == 1, fmt.Sprintf("idx=%d %d/%d", r.idx(), pa, pb))
			p.key(kb.ArrowLeft)
			p.sleep(1200)
			pa, pb = r.pager()
			r.check("before the first page opens the previous chapter at its last page",
				r.idx() == 5 && pa == pb && pb > 1 && !strings.Contains(ev[string](p, "location.hash"), "end="), fmt.Sprintf("idx=%d %d/%d", r.idx(), pa, pb))
			r.check("no console errors (page mode)", len(r.errs()) == 0, first(r.errs(), 4))
			p.Close()

			// ---- reduced motion
			r = newRd(t, c, br, host, srv, vp, rdOpts{mode: "page", reduced: true, hash: rdHash(2, "")})
			td := ev[string](r.p, `getComputedStyle(document.querySelector('.rd-article')).transitionDuration + '|' + getComputedStyle(document.querySelector('.rd-chrome')).transitionDuration`)
			okTd := true
			for _, x := range strings.Split(td, "|") {
				// a list of durations ("0s, 0s") is fine when every entry is 0
				for _, y := range strings.Split(x, ",") {
					f, err := strconv.ParseFloat(strings.TrimSuffix(strings.TrimSpace(y), "s"), 64)
					if err != nil || f > 0.001 {
						okTd = false
					}
				}
			}
			r.check("reduced motion turns the transitions off", okTd, td)
			r.p.Close()
		})
	}
}

func tail(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[len(s)-n:]
}

func TestReaderTTS(t *testing.T) {
	srv, host, br := rdEnv(t, true, true)
	for _, vp := range rdViewports {
		vp := vp
		if !only("reader-tts-" + vp.name) {
			continue
		}
		t.Run(vp.name, func(t *testing.T) {
			c := &Checker{t: t}
			defer c.save("reader-tts-" + vp.name + ".json")
			r := newRd(t, c, br, host, srv, vp, rdOpts{mode: "scroll", hash: rdHash(7, "")})
			p := r.p
			r.showChrome()
			p.click(`[data-act="listen"]`)
			p.mustVisible(".pl-dock", 15*time.Second)
			_ = p.waitVisible("mark.rd-say, .rd-title.rd-say", 40*time.Second)
			var seen []string
			for i := 0; i < 60; i++ {
				tx := ev[string](p, `(document.querySelector('mark.rd-say') || document.querySelector('.rd-title.rd-say') || {}).textContent || ''`)
				if tx != "" && (len(seen) == 0 || seen[len(seen)-1] != tx) {
					seen = append(seen, tx)
				}
				if len(seen) >= 3 {
					break
				}
				p.sleep(700)
			}
			p.mu.Lock()
			ttsOK := append([]int(nil), p.ttsStatus...)
			p.mu.Unlock()
			allOK := true // voices run on-device; any /api/tts request that does happen must still succeed
			for _, s := range ttsOK {
				if s != 200 && s != 206 {
					allOK = false
				}
			}
			r.check("no failing /api/tts request", allOK, first(ttsOK, 4))
			var shortSeen []string
			for _, s := range seen {
				shortSeen = append(shortSeen, short2(s, 30))
			}
			r.check("the highlighted sentence advances", len(seen) >= 3, shortSeen)
			r.shot("listening")
			st := ev[float64](p, `(() => { const a = (window.__audios || []).filter((x) => !x.paused); return a.length ? a[a.length - 1].currentTime : -1; })()`)
			markBefore := ev[string](p, rdMarkJS)
			_ = markBefore
			r.check("an audio element is playing", st >= 0, st)
			dockH := ev[float64](p, "document.getElementById('player-dock').getBoundingClientRect().height")
			padS := ev[string](p, "getComputedStyle(document.documentElement).getPropertyValue('--player-h')")
			pad, _ := strconv.ParseFloat(strings.TrimSpace(strings.TrimSuffix(strings.TrimSpace(padS), "px")), 64)
			r.check("dock height is published as --player-h", absF(pad-dockH) <= 1.5, fmt.Sprintf("dock=%v var=%s", dockH, padS))
			if vp.name == "mobile" {
				r.check("phone dock is one compact row", dockH <= 72, dockH)
				p.click(`[data-pl="expand"]`)
				p.mustVisible(".pl-sheet", 3*time.Second)
				p.sleep(400)
				r.shot("sheet")
				small := ev[[]string](p, `[...document.querySelectorAll('.pl-sheet button, .pl-sheet select')].filter((e) => { const r = e.getBoundingClientRect(); return r.width < 43.5 || r.height < 43.5; }).map((e) => e.className)`)
				r.check("sheet controls are >= 44 px", len(small) == 0, small)
				// sleep timer from the sheet
				p.selectValue(`.pl-sheet select[data-pl="sleep"]`, "-1")
				p.sleep(300)
				lt := p.text(".pl-sheet [data-pl-left]")
				r.check("sleep timer: end of chapter is shown", strings.Contains(lt, "hết chương"), lt)
				p.selectValue(`.pl-sheet select[data-pl="sleep"]`, "15")
				p.sleep(1300)
				lt = p.text(".pl-sheet [data-pl-left]")
				r.check("sleep timer: countdown runs", strings.Contains(lt, "còn"), lt)
				p.selectValue(`.pl-sheet select[data-pl="sleep"]`, "0")
				p.key(kb.Escape)
				p.sleep(400)
			}
			// pause / resume from the dock
			p.click(`#player-dock [data-pl="toggle"]`)
			p.sleep(500)
			paused := ev[[]any](p, rdLastAudioJS)
			markPaused := ev[string](p, rdMarkJS)
			// the on-device clips are real speech of unknown length: a short one legitimately ends (and the next one
			// starts on the same element) within the 900 ms below, which is not a restart from the chunk start
			clipDur := ev[float64](p, `(() => { const a = (window.__audios || []); const x = a[a.length - 1]; return x && isFinite(x.duration) ? x.duration : -1; })()`)
			p.sleep(1800)
			paused2 := ev[[]any](p, rdLastAudioJS)
			pausedOK := len(paused) == 2 && len(paused2) == 2 && paused[0] == true
			if pausedOK {
				pausedOK = absF(paused2[1].(float64)-paused[1].(float64)) < 0.05
			}
			r.check("pause really pauses the audio", pausedOK, fmt.Sprintf("%v %v", paused, paused2))
			p.click(`#player-dock [data-pl="toggle"]`)
			p.sleep(900)
			res := ev[[]any](p, rdLastAudioJS)
			markAfter := ev[string](p, rdMarkJS)
			nAudio := ev[int](p, "(window.__audios || []).length")
			resumeOK := len(res) == 2 && len(paused) == 2 && res[0] == false && (res[1].(float64) >= paused[1].(float64)-0.05 || (clipDur > 0 && clipDur-paused[1].(float64) < 1.2))
			pc := 0.0
			if len(paused) == 2 {
				pc, _ = paused[1].(float64)
			}
			rc := 0.0
			if len(res) == 2 {
				rc, _ = res[1].(float64)
			}
			r.check("resume continues the same clip, not from the chunk start", resumeOK, fmt.Sprintf("paused@%.2f resumed@%.2f clips=%d", pc, rc, nAudio))
			// as in the original, the third alternative (any highlight at all) is what is asserted
			r.check("resume keeps the highlighted sentence",
				markAfter == markPaused || strings.HasPrefix(markAfter, short2(markPaused, 20)) || len(markAfter) > 0,
				fmt.Sprintf("%q -> %q", short2(markPaused, 30), short2(markAfter, 30)))
			if vp.name == "desktop" {
				// sleep timer from the dock
				p.selectValue(`#player-dock select[data-pl="sleep"]`, "-1")
				p.sleep(300)
				t1 := p.text(`#player-dock [data-pl-left]`)
				p.selectValue(`#player-dock select[data-pl="sleep"]`, "15")
				p.sleep(1300)
				t2 := p.text(`#player-dock [data-pl-left]`)
				r.check("sleep timer: end of chapter, then a countdown", strings.Contains(t1, "hết chương") && strings.Contains(t2, "còn"), fmt.Sprintf("%q %q", t1, t2))
				p.selectValue(`#player-dock select[data-pl="sleep"]`, "0")
				// speed
				p.selectIndex(`#player-dock select[data-pl="rate"]`, 5)
				p.sleep(1200)
				r.check("rate changes", ev[bool](p, "JSON.parse(localStorage.getItem('mythlab.settings')).rate != 1"))
				// Space pauses (dock owns it while playing)
				p.key(" ")
				p.sleep(500)
				ps := ev[any](p, `(() => { const a = (window.__audios || []); const x = a[a.length - 1]; return x ? x.paused : null; })()`)
				r.check("Space toggles pause while listening", ps == true, ps)
				// double click a paragraph starts listening from it
				p.exec("window.scrollTo(0, 1600)")
				p.sleep(500)
				before := ev[string](p, rdSayIdxJS)
				pbox := ev[[]any](p, `(() => { const ps = [...document.querySelectorAll('#rd-body > p')]; const e = ps.find((x) => x.getBoundingClientRect().top > 200); const r = e.getBoundingClientRect(); return [r.left + 30, r.top + 10, e.dataset.i]; })()`)
				p.mouseDblClick(pbox[0].(float64), pbox[1].(float64))
				p.sleep(5000)
				now := ev[string](p, rdSayIdxJS)
				clicked, _ := strconv.Atoi(fmt.Sprint(pbox[2]))
				nowI, err := strconv.Atoi(now)
				r.check("double click on a paragraph listens from it", now != "" && err == nil && absInt(nowI-clicked) <= 1, fmt.Sprintf("clicked=%v speaking=%s (was %s)", pbox[2], now, before))
			}
			r.shot("listening-2")
			p.click(`#player-dock [data-pl="close"]`)
			p.sleep(500)
			r.check("closing the player clears the highlight", !p.exists("mark.rd-say") && !p.exists(".rd-saying"))
			r.check("no console errors (tts)", len(r.errs()) == 0, first(r.errs(), 4))
			p.Close()
		})
	}
}

func TestReaderLocal(t *testing.T) {
	srv, host, br := rdEnv(t, false, false)
	for _, vp := range rdViewports {
		for _, key := range []string{"Mạt Thế Cổ Đại Cầu Sinh", "Niên Đại Thương Gia"} {
			for _, mode := range []string{"scroll", "page"} {
				vp, key, mode := vp, key, mode
				name := fmt.Sprintf("%s-%s-%s", vp.name, strings.ReplaceAll(key, " ", "_"), mode)
				if !only("reader-local-" + name) {
					continue
				}
				t.Run(name, func(t *testing.T) {
					c := &Checker{t: t}
					r := newRd(t, c, br, host, srv, vp, rdOpts{theme: "dark", mode: mode, hash: fmt.Sprintf("#/r/local0/%s/10", enc(key))})
					r.tag = fmt.Sprintf("%s-local0-%s-%s", vp.name, string([]rune(key)[:8]), mode)
					r.p.sleep(300)
					r.shot("local")
					m := r.basics(fmt.Sprintf("local0 %s %s", string([]rune(key)[:10]), mode))
					r.check("local story shows its chapter", m.Paras > 3 && r.idx() == 10, m.Paras)
					if mode == "page" {
						_, b := r.pager()
						r.check("local story pages", b >= 1, b)
					}
					r.check("no console errors (local)", len(r.errs()) == 0, first(r.errs(), 3))
					r.p.Close()
					c.save("reader-local-" + sanitize(name) + ".json")
				})
			}
		}
	}
}
