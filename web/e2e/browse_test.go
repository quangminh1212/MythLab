package e2e

import (
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// Port of browse.py: the shell and every browse view, 2 viewports x 3 themes. Asserts no console errors, no
// horizontal overflow, AA contrast, tap targets >= 44 px on the phone, one <h1>, a route-specific title and
// fewer than 1000 DOM nodes on home.

type browseMetrics struct {
	Cut       [][]any  `json:"cut"`
	ScrollW   float64  `json:"scrollW"`
	InnerW    float64  `json:"innerW"`
	HOverflow bool     `json:"hOverflow"`
	DocH      float64  `json:"docH"`
	Nodes     int      `json:"nodes"`
	Small     [][]any  `json:"small"`
	Noname    []string `json:"noname"`
	Over      [][]any  `json:"over"`
	H1        []string `json:"h1"`
	Title     string   `json:"title"`
	View      string   `json:"view"`
	Scheme    string   `json:"scheme"`
	Theme     string   `json:"theme"`
	Skeletons int      `json:"skeletons"`
	Imgs      int      `json:"imgs"`
}

type contrastResult struct {
	Checked int     `json:"checked"`
	Bad     [][]any `json:"bad"`
}

func enc(s string) string { return strings.ReplaceAll(url.QueryEscape(s), "+", "%20") }

const (
	ghSource = "gh0"
	ghKey    = "Done_CoTich/Phượng Đế Cửu Khuynh"
	ghRepo   = "Done_CoTich"
)

func browseSeed(api, theme string, withData, hasAPI bool) string {
	data := map[string]any{"mythlab.settings": map[string]any{"theme": theme, "ui2": 1, "ui3": 1}}
	if hasAPI {
		data["mythlab.server"] = map[string]any{"url": api}
	}
	if withData {
		now := int64(1795000000000)
		prog := map[string]any{}
		type st struct {
			src, key, name string
			total, idx     int
		}
		for i, s := range []st{
			{"local0", "Mạt Thế Cổ Đại Cầu Sinh", "Mạt Thế Cổ Đại Cầu Sinh", 1000, 41},
			{"gh0", "Done_CoTich/Phượng Đế Cửu Khuynh", "Phượng Đế Cửu Khuynh", 2888, 1203},
			{"local0", "Niên Đại Thương Gia", "Niên Đại Thương Gia", 693, 5},
		} {
			var group any
			if strings.Contains(s.key, "/") {
				group = strings.SplitN(s.key, "/", 2)[0]
			}
			prog[s.src+"|"+s.key] = map[string]any{
				"source": s.src, "key": s.key, "name": s.name, "poster": nil, "cover": nil, "cover_sha": nil, "author": nil,
				"genres": []any{}, "group": group, "idx": s.idx, "n": s.idx + 1, "total": s.total,
				"para": 3, "ts": now - int64(i)*3600_000, "title": fmt.Sprintf("Chương %d: Tĩnh Tâm Uyển", s.idx+1), "maxIdx": s.idx,
			}
		}
		data["mythlab.progress"] = prog
		var bms []any
		for _, np := range [][2]int{{3, 4}, {17, 0}, {42, 12}} {
			n, p := np[0], np[1]
			bms = append(bms, map[string]any{
				"id": fmt.Sprintf("local0|Mạt Thế Cổ Đại Cầu Sinh|Chương %d.txt|%d", n, p), "source": "local0", "key": "Mạt Thế Cổ Đại Cầu Sinh",
				"name": "Mạt Thế Cổ Đại Cầu Sinh", "idx": n - 1, "n": n, "file": fmt.Sprintf("Chương %d.txt", n), "title": fmt.Sprintf("Chương %d: Bóc hoàng bảng", n),
				"para": p, "excerpt": "Nàng ngẩng đầu nhìn bầu trời xám xịt, trong lòng bỗng dâng lên một dự cảm chẳng lành về những ngày sắp tới.",
				"ts": now - int64(n)*60_000,
			})
		}
		data["mythlab.bookmarks"] = bms
	}
	return seedScript(data, false)
}

func TestBrowse(t *testing.T) {
	needEnv(t)
	srv := startServer(t, false)
	host := startHost(t, webDist)
	br := newBrowser(t)
	gh := srv.ghReady(t)
	if !gh {
		t.Log("GitHub library unavailable (no token / no network): the gh0 routes are skipped")
	}

	type route struct {
		name, hash string
		withData   int // 1 data, 0 empty, -1 no backend (onboarding)
		needGH     bool
	}
	routes := []route{
		{"home", "#/", 1, false},
		{"source", "#/lib/local0", 1, false},
		{"repos", "#/lib/" + ghSource, 1, true},
		{"repo", "#/lib/" + ghSource + "/" + enc(ghRepo), 1, true},
		{"search", "#/search?q=" + enc("phượng"), 1, true},
		{"search-none", "#/search?q=" + enc("zzzqqq không có"), 1, false},
		{"story", "#/s/" + ghSource + "/" + enc(ghKey), 1, true},
		{"story-local", "#/s/local0/" + enc("Mạt Thế Cổ Đại Cầu Sinh"), 1, false},
		{"history", "#/history", 1, false},
		{"bookmarks", "#/bookmarks", 1, false},
		{"history-empty", "#/history", 0, false},
		{"bookmarks-empty", "#/bookmarks", 0, false},
		{"notfound", "#/s/local0/" + enc("Không Có Truyện Này"), 1, false},
		{"onboarding", "#/", -1, false},
	}
	type exp struct {
		sel   string
		least int
	}
	expect := map[string]exp{
		"home": {"a.card", 4}, "source": {"a.card", 2}, "repos": {".tile", 20}, "repo": {"a.card", 12},
		"search": {"a.card", 1}, "search-none": {".state:not(.state-error)", 1}, "story": {".ch", 10},
		"story-local": {".ch", 10}, "history": {".row", 3}, "bookmarks": {".row", 3},
		"history-empty": {".state:not(.state-error)", 1}, "bookmarks-empty": {".state:not(.state-error)", 1},
		"notfound": {".state-error", 1}, "onboarding": {".onboard-grid input", 3},
	}
	viewports := []struct {
		name string
		w, h int
	}{{"desktop", 1440, 900}, {"mobile", 390, 844}}
	themes := []string{"light", "dark", "sepia"}
	var results []map[string]any
	baseURL := host.URL
	basePort := host.Port

	for _, vp := range viewports {
		for _, theme := range themes {
			tag := vp.name + "-" + theme
			for _, rt := range routes {
				name := tag + "-" + rt.name
				if !only(name) {
					continue
				}
				rt, vp, theme := rt, vp, theme
				t.Run(name, func(t *testing.T) {
					if rt.needGH && !gh {
						t.Skip("GitHub library unavailable")
					}
					p := br.newPage(t, PageOpts{W: vp.w, H: vp.h, Mobile: vp.name == "mobile",
						NoAPI: rt.withData < 0, Init: []string{browseSeed(srv.URL, theme, rt.withData >= 1, rt.withData >= 0)}})
					defer p.Close()
					var errs []string
					p.goto_(baseURL + "/" + rt.hash)
					// settle
					if err := p.waitFn("window.__mlBooted === true", 20*time.Second); err != nil {
						errs = append(errs, "settle: "+short2(err.Error(), 200))
					}
					p.networkIdle(20 * time.Second)
					_ = p.waitFn("!document.querySelector('#view .loading, #view .sk-card, #view .sk-rows')", 20*time.Second)
					p.sleep(450)

					m := call[browseMetrics](p, browseMetricsJS, vp.w)
					c := ev[contrastResult](p, "("+browseContrastJS+")()")
					p.shot(name + ".png")

					cons, perr, herr := p.snapshot()
					errs = append(errs, cons...)
					for _, e := range perr {
						errs = append(errs, "pageerror: "+e)
					}
					for _, h := range herr {
						u, _ := url.Parse(h.URL)
						port := u.Port()
						if port == fmt.Sprint(basePort) && u.Path == "/api/ping" {
							continue // the static test host has no API (the app probes the page origin first)
						}
						if rt.name == "notfound" && h.Status == 404 && strings.HasPrefix(u.Path, "/api/") {
							continue
						}
						errs = append(errs, fmt.Sprintf("HTTP %d %s", h.Status, h.URL))
					}
					if rt.name == "onboarding" { // no backend: the same-origin probe of /api answers 404
						var kept []string
						for _, e := range errs {
							if !strings.Contains(e, "404") {
								kept = append(kept, e)
							}
						}
						errs = kept
					}

					var f []string
					if len(errs) > 0 {
						f = append(f, fmt.Sprintf("console errors: %v", first(errs, 3)))
					}
					if m.HOverflow {
						f = append(f, fmt.Sprintf("horizontal overflow %v > %v: %v", m.ScrollW, m.InnerW, first(m.Over, 4)))
					}
					if len(c.Bad) > 0 {
						f = append(f, fmt.Sprintf("contrast: %v", first(c.Bad, 4)))
					}
					if strings.HasPrefix(rt.name, "story") {
						// the chapter list is virtualised: bring it on screen before counting its rows
						p.exec("document.querySelector('#st-ch')?.scrollIntoView({ block: 'start' })")
						p.sleep(500)
						p.shot(name + "-chapters.png")
						m2 := call[browseMetrics](p, browseMetricsJS, vp.w)
						for _, x := range m2.Small {
							if !containsRow(m.Small, x) {
								m.Small = append(m.Small, x)
							}
						}
						m.Cut = append(m.Cut, m2.Cut...)
					}
					e := expect[rt.name]
					got := ev[int](p, "document.querySelectorAll('main ' + "+jq(e.sel)+").length")
					if got < e.least {
						f = append(f, fmt.Sprintf("expected >= %d x '%s', found %d", e.least, e.sel, got))
					}
					if rt.name != "notfound" && ev[bool](p, "!!document.querySelector('main .state-error')") {
						f = append(f, "an error state is shown")
					}
					if len(m.Cut) > 0 {
						f = append(f, fmt.Sprintf("content cut off at the right edge: %v", first(m.Cut, 4)))
					}
					if vp.name == "mobile" && len(m.Small) > 0 {
						f = append(f, fmt.Sprintf("tap targets < 44px: %v", first(m.Small, 6)))
					}
					if len(m.Noname) > 0 {
						f = append(f, fmt.Sprintf("controls without a name: %v", first(m.Noname, 6)))
					}
					if len(m.H1) != 1 {
						f = append(f, fmt.Sprintf("h1 count %d: %v", len(m.H1), m.H1))
					}
					if m.Scheme != theme {
						f = append(f, fmt.Sprintf("scheme %s != %s", m.Scheme, theme))
					}
					if rt.name == "home" && m.Nodes >= 1000 {
						f = append(f, fmt.Sprintf("home has %d DOM nodes", m.Nodes))
					}
					if rt.name != "home" && rt.name != "onboarding" {
						ti := strings.TrimSpace(m.Title)
						if ti == "MythLab" || ti == "MythLab — Đọc & nghe truyện" {
							f = append(f, fmt.Sprintf("title not set for the route: %q", m.Title))
						}
					}
					if m.Skeletons > 0 {
						f = append(f, fmt.Sprintf("%d skeleton nodes still shown", m.Skeletons))
					}
					results = append(results, map[string]any{"case": name, "route": rt.hash, "metrics": m, "contrastChecked": c.Checked, "contrastBad": c.Bad, "errors": errs, "failures": f})
					t.Logf("view=%s nodes=%d h=%v small=%d contrastBad=%d checked=%d err=%d title=%.50q", m.View, m.Nodes, m.DocH, len(m.Small), len(c.Bad), c.Checked, len(errs), m.Title)
					for _, x := range f {
						t.Error(x)
					}
				})
			}
		}
	}
	b, _ := json.MarshalIndent(results, "", " ")
	_ = os.WriteFile(filepath.Join(outDir, "browse-results.json"), b, 0o644)
}

func first[T any](s []T, n int) []T {
	if len(s) > n {
		return s[:n]
	}
	return s
}

func short2(s string, n int) string {
	if len(s) > n {
		return s[:n]
	}
	return s
}

func containsRow(rows [][]any, x []any) bool {
	for _, r := range rows {
		if fmt.Sprint(r) == fmt.Sprint(x) {
			return true
		}
	}
	return false
}
