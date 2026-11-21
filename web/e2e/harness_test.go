// Package e2e holds the browser end-to-end tests of the MythLab web UI. They drive an installed Chromium-family
// browser (Edge, Chrome, Chromium) through chromedp, against a freshly started mythlab-server and the built web/dist.
//
// This is a separate Go module so the production server module does not depend on chromedp:
//
//	cd web/e2e && go test -count=1 -timeout 40m ./...
//
// Environment:
//
//	MYTHLAB_E2E_BROWSER  path of the browser executable (default: Edge, Chrome or Chromium found on this machine)
//	MYTHLAB_E2E_NO_SANDBOX  any value: start the browser with --no-sandbox (CI runners)
//	MYTHLAB_E2E_SERVER   path of a prebuilt mythlab-server (default: built from ../../server for this run)
//	MYTHLAB_E2E_OUT      directory for screenshots and results (default: <temp>/mythlab-e2e)
//	MYTHLAB_E2E_ONLY     TestBrowse / TestReader only: comma list of subtest name fragments to run
//
// Without a browser every test is skipped with a message. Ports 18900-18999 are used; never 8765 or 18765.
package e2e

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/chromedp/cdproto/browser"
	"github.com/chromedp/cdproto/cdp"
	"github.com/chromedp/cdproto/emulation"
	"github.com/chromedp/cdproto/fetch"
	"github.com/chromedp/cdproto/input"
	"github.com/chromedp/cdproto/log"
	"github.com/chromedp/cdproto/network"
	"github.com/chromedp/cdproto/page"
	cdpruntime "github.com/chromedp/cdproto/runtime"
	"github.com/chromedp/cdproto/storage"
	"github.com/chromedp/chromedp"
	"github.com/chromedp/chromedp/kb"
)

// ---------------------------------------------------------------------------------------------- run-wide setup

var (
	repoRoot    string
	webDist     string
	oldStatic   string // the legacy reader/static build (service-worker upgrade test only, read only)
	serverExe   string
	outDir      string
	sharedCache string
	browserPath string
	setupErr    error
	nextPort    atomic.Int32
)

func TestMain(m *testing.M) { os.Exit(realMain(m)) }

func realMain(m *testing.M) int {
	wd, _ := os.Getwd()
	repoRoot, _ = filepath.Abs(filepath.Join(wd, "..", ".."))
	webDist = filepath.Join(repoRoot, "web", "dist")
	oldStatic = filepath.Join(repoRoot, "reader", "static")
	outDir = os.Getenv("MYTHLAB_E2E_OUT")
	if outDir == "" {
		outDir = filepath.Join(os.TempDir(), "mythlab-e2e")
	}
	_ = os.MkdirAll(outDir, 0o755)
	nextPort.Store(18900)

	browserPath = findBrowser()
	if browserPath == "" {
		fmt.Println("e2e: SKIP - no Chromium-family browser found (install Microsoft Edge/Chrome or set MYTHLAB_E2E_BROWSER)")
		return m.Run() // every test calls needEnv and skips
	}
	fmt.Println("e2e: browser:", browserPath)
	tmp, err := os.MkdirTemp("", "mythlab-e2e-")
	if err != nil {
		setupErr = err
		return m.Run()
	}
	defer os.RemoveAll(tmp)
	// The GitHub library answers from this cache, shared by the servers of one run so the (rate limited) GitHub
	// calls are made once. It is a fresh temp directory: never reader/.cache.
	sharedCache = filepath.Join(tmp, "cache")
	_ = os.MkdirAll(sharedCache, 0o755)
	serverExe, err = buildServer(tmp)
	if err != nil {
		setupErr = err
		return m.Run()
	}
	if err := ensureDist(); err != nil {
		setupErr = err
	}
	return m.Run()
}

func buildServer(tmp string) (string, error) {
	if p := os.Getenv("MYTHLAB_E2E_SERVER"); p != "" {
		if _, err := os.Stat(p); err != nil {
			return "", fmt.Errorf("MYTHLAB_E2E_SERVER: %w", err)
		}
		return p, nil
	}
	exe := filepath.Join(tmp, "mythlab-server")
	if runtime.GOOS == "windows" {
		exe += ".exe"
	}
	cmd := exec.Command("go", "build", "-o", exe, "./cmd/mythlab-server")
	cmd.Dir = filepath.Join(repoRoot, "server")
	cmd.Env = append(os.Environ(), "CGO_ENABLED=0")
	out, err := cmd.CombinedOutput()
	if err != nil {
		prebuilt := filepath.Join(repoRoot, "apps", "desktop", "dist", "mythlab-server.exe")
		if _, e2 := os.Stat(prebuilt); e2 == nil {
			fmt.Println("e2e: go build failed, using", prebuilt)
			return prebuilt, nil
		}
		return "", fmt.Errorf("go build mythlab-server: %v\n%s", err, out)
	}
	return exe, nil
}

func ensureDist() error {
	if _, err := os.Stat(filepath.Join(webDist, "index.html")); err == nil {
		return nil
	}
	fmt.Println("e2e: web/dist missing, building with tools/build-web.ps1")
	cmd := exec.Command("powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", filepath.Join(repoRoot, "tools", "build-web.ps1"))
	cmd.Dir = repoRoot
	if out, err := cmd.CombinedOutput(); err != nil {
		return fmt.Errorf("build-web.ps1: %v\n%s", err, out)
	}
	return nil
}

func findBrowser() string {
	if p := os.Getenv("MYTHLAB_E2E_BROWSER"); p != "" {
		if st, err := os.Stat(p); err == nil && !st.IsDir() {
			return p
		}
		fmt.Println("e2e: MYTHLAB_E2E_BROWSER does not exist:", p)
		return ""
	}
	var c []string
	pf, pf86, local := os.Getenv("ProgramFiles"), os.Getenv("ProgramFiles(x86)"), os.Getenv("LOCALAPPDATA")
	for _, base := range []string{pf86, pf, local} {
		if base == "" {
			continue
		}
		c = append(c,
			filepath.Join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
			filepath.Join(base, "Google", "Chrome", "Application", "chrome.exe"),
			filepath.Join(base, "Chromium", "Application", "chrome.exe"))
	}
	if local != "" {
		g, _ := filepath.Glob(filepath.Join(local, "ms-playwright", "chromium-*", "chrome-win*", "chrome.exe"))
		sort.Strings(g)
		for i := len(g) - 1; i >= 0; i-- {
			c = append(c, g[i])
		}
	}
	c = append(c,
		"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
		"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
	for _, n := range []string{"msedge", "microsoft-edge", "google-chrome", "chromium", "chromium-browser", "chrome"} {
		if p, err := exec.LookPath(n); err == nil {
			c = append(c, p)
		}
	}
	for _, p := range c {
		if st, err := os.Stat(p); err == nil && !st.IsDir() {
			return p
		}
	}
	return ""
}

// needEnv skips (no browser) or fails (broken setup) a test; call first.
func needEnv(t *testing.T) {
	t.Helper()
	if browserPath == "" {
		t.Skip("no Chromium-family browser found (install Microsoft Edge/Chrome or set MYTHLAB_E2E_BROWSER)")
	}
	if setupErr != nil {
		t.Fatalf("setup failed: %v", setupErr)
	}
}

// only reports whether a subtest name is selected by MYTHLAB_E2E_ONLY.
func only(name string) bool {
	f := os.Getenv("MYTHLAB_E2E_ONLY")
	if f == "" {
		return true
	}
	for _, s := range strings.Split(f, ",") {
		if s != "" && strings.Contains(name, s) {
			return true
		}
	}
	return false
}

// ---------------------------------------------------------------------------------------------- servers

func takePort(t *testing.T) int {
	t.Helper()
	for i := 0; i < 100; i++ {
		p := int(nextPort.Add(1) - 1)
		if p > 18999 {
			nextPort.Store(18900)
			p = 18900
		}
		if p == 18765 || p == 8765 {
			continue
		}
		l, err := net.Listen("tcp", fmt.Sprintf("127.0.0.1:%d", p))
		if err != nil {
			continue
		}
		l.Close()
		return p
	}
	t.Fatal("no free port in 18900-18999")
	return 0
}

// Server is one mythlab-server process with its own config; URL is its API origin.
type Server struct {
	URL  string
	Port int
	cmd  *exec.Cmd
	cfg  string
}

// startServer runs mythlab-server on a free port of 18900-18999 with a temp config (the repository root as the
// "local0" source, the GitHub library like reader/config.json) and the run-wide temp cache.
func startServer(t *testing.T, withTTS bool) *Server {
	t.Helper()
	port := takePort(t)
	dir := t.TempDir()
	cfg := filepath.Join(dir, "config.json")
	local, _ := json.Marshal(filepath.ToSlash(repoRoot))
	conf := fmt.Sprintf(`{"local":[{"name":"MythLab","path":%s}],"github":[{"owner":"quangminh1212","prefix":"Done_","enabled":true}],"tts":{"default_voice":"vi-VN-HoaiMyNeural"}}`, local)
	if err := os.WriteFile(cfg, []byte(conf), 0o644); err != nil {
		t.Fatal(err)
	}
	args := []string{"--host", "127.0.0.1", "--port", fmt.Sprint(port), "--config", cfg, "--cache", sharedCache}
	if !withTTS {
		args = append(args, "--no-tts")
	}
	cmd := exec.Command(serverExe, args...)
	logf, _ := os.Create(filepath.Join(dir, "server.log"))
	cmd.Stdout, cmd.Stderr = logf, logf
	if err := cmd.Start(); err != nil {
		t.Fatalf("start server: %v", err)
	}
	s := &Server{URL: fmt.Sprintf("http://127.0.0.1:%d", port), Port: port, cmd: cmd, cfg: cfg}
	t.Cleanup(func() {
		_ = cmd.Process.Kill()
		_ = cmd.Wait()
		logf.Close()
	})
	deadline := time.Now().Add(30 * time.Second)
	for time.Now().Before(deadline) {
		resp, err := http.Get(s.URL + "/api/ping")
		if err == nil {
			ok := resp.StatusCode == 200
			resp.Body.Close()
			if ok {
				return s
			}
		}
		time.Sleep(100 * time.Millisecond)
	}
	b, _ := os.ReadFile(filepath.Join(dir, "server.log"))
	t.Fatalf("server did not answer /api/ping: %s", b)
	return nil
}

var warmOnce sync.Once

// warm fills the run-wide cache once: GitHub listings take about 25 s per repository when cold, which the
// pages would otherwise wait for (the former Python runs used a warm cache).
func (s *Server) warm(first string) {
	warmOnce.Do(func() {
		cl := &http.Client{Timeout: 150 * time.Second}
		for _, repo := range []string{first, "Done_CoTich"} {
			if repo == "" {
				continue
			}
			if resp, err := cl.Get(s.URL + "/api/stories?source=gh0&repo=" + repo); err == nil {
				_, _ = io.Copy(io.Discard, resp.Body)
				resp.Body.Close()
			}
		}
		// the search index is filled in the background after the listings: wait until it knows the test story
		for i := 0; i < 120; i++ {
			resp, err := cl.Get(s.URL + "/api/search?q=" + url.QueryEscape("phượng"))
			if err == nil {
				var v struct {
					Total int `json:"total"`
				}
				_ = json.NewDecoder(resp.Body).Decode(&v)
				resp.Body.Close()
				if v.Total > 0 {
					break
				}
			}
			time.Sleep(500 * time.Millisecond)
		}
	})
}

// ghReady reports whether the GitHub library of this server lists the repository the tests read.
func (s *Server) ghReady(t *testing.T) bool {
	t.Helper()
	cl := &http.Client{Timeout: 120 * time.Second}
	resp, err := cl.Get(s.URL + "/api/sources")
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	var v struct {
		Sources []struct {
			ID    string `json:"id"`
			Repos []struct {
				Repo     string `json:"repo"`
				PushedAt string `json:"pushed_at"`
			} `json:"repos"`
		} `json:"sources"`
	}
	if json.NewDecoder(resp.Body).Decode(&v) != nil {
		return false
	}
	for _, src := range v.Sources {
		if src.ID == "gh0" {
			firstRepo, newest := "", ""
			for _, r := range src.Repos {
				if r.PushedAt >= newest {
					newest, firstRepo = r.PushedAt, r.Repo
				}
			}
			for _, r := range src.Repos {
				if r.Repo == "Done_CoTich" {
					s.warm(firstRepo)
					return true
				}
			}
		}
	}
	return false
}

// Gate lets a test cut a listener off the network: while offline every connection is closed at once, which is
// what a dead network looks like to the page and to its service worker.
type Gate struct {
	offline atomic.Bool
}

func (g *Gate) SetOffline(v bool) { g.offline.Store(v) }

func (g *Gate) wrap(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if g.offline.Load() {
			if hj, ok := w.(http.Hijacker); ok {
				if c, _, err := hj.Hijack(); err == nil {
					c.Close()
					return
				}
			}
			http.Error(w, "offline", http.StatusServiceUnavailable)
			return
		}
		h.ServeHTTP(w, r)
	})
}

func listenOn(t *testing.T, port int, h http.Handler) {
	t.Helper()
	l, err := net.Listen("tcp", fmt.Sprintf("127.0.0.1:%d", port))
	if err != nil {
		t.Fatal(err)
	}
	srv := &http.Server{Handler: h, ReadHeaderTimeout: 10 * time.Second}
	go srv.Serve(l)
	t.Cleanup(func() { srv.Close() })
}

// gatedAPI puts a pass-through proxy in front of the server so the API can be cut off too.
func gatedAPI(t *testing.T, s *Server, g *Gate) string {
	t.Helper()
	target, _ := url.Parse(s.URL)
	rp := httputil.NewSingleHostReverseProxy(target)
	rp.FlushInterval = -1
	port := takePort(t)
	listenOn(t, port, g.wrap(rp))
	return fmt.Sprintf("http://127.0.0.1:%d", port)
}

func init() {
	for ext, typ := range map[string]string{".webmanifest": "application/manifest+json", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".json": "application/json"} {
		_ = mime.AddExtensionType(ext, typ)
	}
}

// Host serves a directory over HTTP on a fixed port. The root can be switched while it keeps listening, so the
// service-worker upgrade test serves the old build, then the new one, from one origin.
type Host struct {
	URL  string
	Port int
	Gate *Gate
	root atomic.Value // string
	mu   sync.Mutex
	Hits []string
}

func startHost(t *testing.T, root string) *Host {
	t.Helper()
	h := &Host{Gate: &Gate{}, Port: takePort(t)}
	h.URL = fmt.Sprintf("http://127.0.0.1:%d", h.Port)
	h.SetRoot(root)
	listenOn(t, h.Port, h.Gate.wrap(http.HandlerFunc(h.serve)))
	return h
}

func (h *Host) SetRoot(root string) {
	abs, _ := filepath.Abs(root)
	h.root.Store(abs)
}

func (h *Host) serve(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet && r.Method != http.MethodHead {
		http.Error(w, "method", http.StatusMethodNotAllowed)
		return
	}
	root := h.root.Load().(string)
	p := r.URL.Path
	h.mu.Lock()
	h.Hits = append(h.Hits, p)
	h.mu.Unlock()
	rel := strings.TrimPrefix(p, "/")
	if rel == "" {
		rel = "index.html"
	}
	full := filepath.Join(root, filepath.FromSlash(rel))
	if !strings.HasPrefix(full, root) {
		w.WriteHeader(http.StatusNotFound)
		return
	}
	st, err := os.Stat(full)
	if err != nil || st.IsDir() {
		w.Header().Set("Content-Length", "0")
		w.WriteHeader(http.StatusNotFound)
		return
	}
	f, err := os.Open(full)
	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		return
	}
	defer f.Close()
	body, _ := io.ReadAll(f)
	ct := mime.TypeByExtension(strings.ToLower(filepath.Ext(full)))
	if ct == "" {
		ct = "application/octet-stream"
	}
	w.Header().Set("Content-Type", ct)
	w.Header().Set("Content-Length", fmt.Sprint(len(body)))
	w.Header().Set("Cache-Control", "no-cache")
	w.WriteHeader(http.StatusOK)
	if r.Method == http.MethodGet {
		_, _ = w.Write(body)
	}
}

// ---------------------------------------------------------------------------------------------- browser

// Browser is one headless browser process; every page gets its own isolated browser context (own storage,
// service workers and caches), like a Playwright context.
type Browser struct {
	t   *testing.T
	ctx context.Context
}

func newBrowser(t *testing.T) *Browser {
	t.Helper()
	// The browser is started here, not by chromedp's launcher: Microsoft Edge does not print the "DevTools
	// listening" line that launcher waits for, so a fixed debugging port (18900-18999) and a remote allocator
	// work with every Chromium-family browser.
	port := takePort(t)
	udd, err := os.MkdirTemp("", "mythlab-e2e-browser-")
	if err != nil {
		t.Fatal(err)
	}
	args := []string{
		"--headless=new", "--hide-scrollbars", "--lang=vi-VN", "--autoplay-policy=no-user-gesture-required",
		"--disable-features=msEdgeSidebarV2,Translate,TranslateUI,msEdgeShopping",
		"--no-first-run", "--no-default-browser-check", "--disable-sync", "--disable-extensions",
		"--disable-background-networking", "--disable-default-apps", "--disable-popup-blocking",
		"--disable-background-timer-throttling", "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows",
		"--disable-component-update", "--metrics-recording-only", "--password-store=basic", "--use-mock-keychain",
		"--force-color-profile=srgb", "--window-size=1440,900",
		"--user-data-dir=" + udd, fmt.Sprintf("--remote-debugging-port=%d", port), "about:blank",
	}
	if os.Getenv("MYTHLAB_E2E_NO_SANDBOX") != "" { // CI containers/runners without user namespaces
		args = append(args, "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage")
	}
	cmd := exec.Command(browserPath, args...)
	if os.Getenv("MYTHLAB_E2E_DEBUG") != "" {
		cmd.Stdout, cmd.Stderr = os.Stderr, os.Stderr
	}
	if err := cmd.Start(); err != nil {
		t.Fatalf("cannot start the browser %s: %v", browserPath, err)
	}
	endpoint := fmt.Sprintf("http://127.0.0.1:%d", port)
	t.Cleanup(func() {
		if runtime.GOOS == "windows" {
			_ = exec.Command("taskkill", "/PID", fmt.Sprint(cmd.Process.Pid), "/T", "/F").Run()
		} else {
			_ = cmd.Process.Kill()
		}
		_ = cmd.Wait()
		for i := 0; i < 20; i++ { // the browser releases its profile a moment after it exits
			if os.RemoveAll(udd) == nil {
				break
			}
			time.Sleep(200 * time.Millisecond)
		}
	})
	deadline := time.Now().Add(30 * time.Second)
	for {
		resp, err := http.Get(endpoint + "/json/version")
		if err == nil {
			resp.Body.Close()
			break
		}
		if time.Now().After(deadline) {
			t.Fatalf("the browser %s did not open its debugging port %d: %v", browserPath, port, err)
		}
		time.Sleep(100 * time.Millisecond)
	}
	alloc, cancelA := chromedp.NewRemoteAllocator(context.Background(), endpoint)
	ctx, cancelC := chromedp.NewContext(alloc)
	t.Cleanup(func() { cancelC(); cancelA() })
	if err := chromedp.Run(ctx); err != nil {
		t.Fatalf("cannot attach to the browser: %v", err)
	}
	return &Browser{t: t, ctx: ctx}
}

// PageOpts is the emulation of one browser context.
type PageOpts struct {
	W, H    int
	Mobile  bool // phone: mobile viewport and touch
	Reduced bool // prefers-reduced-motion
	NoAPI   bool // every request to /api/ answers 404 (a browser with no reachable backend, even the default one)
	Init    []string
}

// Page is a tab in its own browser context plus what the tab reported.
type Page struct {
	t      *testing.T
	ctx    context.Context
	cancel context.CancelFunc
	W, H   int

	mu         sync.Mutex
	consoleErr []string
	pageErr    []string
	httpErr    []httpErr
	failedReq  []string
	ttsStatus  []int
	inflight   map[network.RequestID]struct{}
	lastNet    time.Time
	wiped      map[string]bool
}

type httpErr struct {
	Status int
	URL    string
}

func (b *Browser) newPage(t *testing.T, o PageOpts) *Page {
	t.Helper()
	if o.W == 0 {
		o.W, o.H = 1280, 860
	}
	ctx, cancel := chromedp.NewContext(b.ctx)
	p := &Page{t: t, ctx: ctx, cancel: cancel, W: o.W, H: o.H, inflight: map[network.RequestID]struct{}{}, lastNet: time.Now()}
	chromedp.ListenTarget(ctx, p.onEvent)
	acts := []chromedp.Action{
		network.Enable(),
		log.Enable(),
		cdpruntime.Enable(),
		emulation.SetDeviceMetricsOverride(int64(o.W), int64(o.H), 1, o.Mobile),
		emulation.SetTouchEmulationEnabled(o.Mobile),
	}
	if o.NoAPI {
		acts = append(acts, fetch.Enable().WithPatterns([]*fetch.RequestPattern{{URLPattern: "*/api/*"}}))
		chromedp.ListenTarget(ctx, func(ev any) {
			if e, ok := ev.(*fetch.EventRequestPaused); ok {
				go func() {
					c := chromedp.FromContext(ctx)
					_ = fetch.FulfillRequest(e.RequestID, 404).
						WithResponseHeaders([]*fetch.HeaderEntry{{Name: "Content-Type", Value: "application/json"}}).
						WithBody("e30=").Do(cdp.WithExecutor(ctx, c.Target))
				}()
			}
		})
	}
	if o.Reduced {
		acts = append(acts, emulation.SetEmulatedMedia().WithFeatures([]*emulation.MediaFeature{{Name: "prefers-reduced-motion", Value: "reduce"}}))
	}
	for _, src := range o.Init {
		src := src
		acts = append(acts, chromedp.ActionFunc(func(ctx context.Context) error {
			_, err := page.AddScriptToEvaluateOnNewDocument(src).Do(ctx)
			return err
		}))
	}
	if err := chromedp.Run(ctx, acts...); err != nil {
		cancel()
		t.Fatalf("cannot open a browser page: %v", err)
	}
	t.Cleanup(cancel)
	return p
}

func (p *Page) Close() { p.cancel() }

func (p *Page) onEvent(ev any) {
	p.mu.Lock()
	defer p.mu.Unlock()
	switch e := ev.(type) {
	case *cdpruntime.EventConsoleAPICalled:
		if e.Type == cdpruntime.APITypeError {
			var parts []string
			for _, a := range e.Args {
				switch {
				case len(a.Value) > 0:
					var s string
					if json.Unmarshal(a.Value, &s) == nil {
						parts = append(parts, s)
					} else {
						parts = append(parts, string(a.Value))
					}
				case a.Description != "":
					parts = append(parts, a.Description)
				}
			}
			txt := strings.Join(parts, " ")
			if !strings.HasPrefix(txt, "Failed to load resource") {
				p.consoleErr = append(p.consoleErr, txt)
			}
		}
	case *log.EventEntryAdded:
		if e.Entry.Level == log.LevelError && !strings.HasPrefix(e.Entry.Text, "Failed to load resource") {
			p.consoleErr = append(p.consoleErr, e.Entry.Text)
		}
	case *cdpruntime.EventExceptionThrown:
		txt := e.ExceptionDetails.Text
		if e.ExceptionDetails.Exception != nil && e.ExceptionDetails.Exception.Description != "" {
			txt = e.ExceptionDetails.Exception.Description
		}
		p.pageErr = append(p.pageErr, txt)
	case *network.EventResponseReceived:
		if e.Response.Status >= 400 {
			p.httpErr = append(p.httpErr, httpErr{int(e.Response.Status), e.Response.URL})
		}
		if strings.Contains(e.Response.URL, "/api/tts") {
			p.ttsStatus = append(p.ttsStatus, int(e.Response.Status))
		}
	case *network.EventRequestWillBeSent:
		p.inflight[e.RequestID] = struct{}{}
		p.lastNet = time.Now()
	case *network.EventLoadingFinished:
		delete(p.inflight, e.RequestID)
		p.lastNet = time.Now()
	case *network.EventLoadingFailed:
		delete(p.inflight, e.RequestID)
		p.lastNet = time.Now()
		p.failedReq = append(p.failedReq, string(e.RequestID))
	}
}

func (p *Page) snapshot() (console, pageErr []string, http []httpErr) {
	p.mu.Lock()
	defer p.mu.Unlock()
	return append([]string(nil), p.consoleErr...), append([]string(nil), p.pageErr...), append([]httpErr(nil), p.httpErr...)
}

func (p *Page) run(a ...chromedp.Action) error { return chromedp.Run(p.ctx, a...) }

func (p *Page) must(err error, what string) {
	p.t.Helper()
	if err != nil {
		p.t.Fatalf("%s: %v", what, err)
	}
}

func jq(s string) string { b, _ := json.Marshal(s); return string(b) }

var awaitPromise = func(ep *cdpruntime.EvaluateParams) *cdpruntime.EvaluateParams { return ep.WithAwaitPromise(true) }

// ev evaluates a JavaScript expression (promises are awaited) and decodes the JSON-able result.
func ev[T any](p *Page, js string) T {
	p.t.Helper()
	var out T
	if err := chromedp.Run(p.ctx, chromedp.Evaluate(js, &out, awaitPromise)); err != nil {
		p.t.Fatalf("evaluate %.100q: %v", js, err)
	}
	return out
}

// evTry is ev that reports the error instead of failing.
func evTry[T any](p *Page, js string) (T, error) {
	var out T
	err := chromedp.Run(p.ctx, chromedp.Evaluate(js, &out, awaitPromise))
	return out, err
}

func (p *Page) exec(js string) {
	p.t.Helper()
	var out any
	if err := chromedp.Run(p.ctx, chromedp.Evaluate(js, &out, awaitPromise)); err != nil {
		p.t.Fatalf("evaluate %.100q: %v", js, err)
	}
}

// call evaluates `(fn)(arg)` where fn is a JavaScript function expression and arg is JSON-encoded.
func call[T any](p *Page, fn string, arg any) T {
	p.t.Helper()
	b, _ := json.Marshal(arg)
	return ev[T](p, "("+fn+")("+string(b)+")")
}

func (p *Page) sleep(ms int) { time.Sleep(time.Duration(ms) * time.Millisecond) }

// waitFn polls a JavaScript expression until it is truthy (like Playwright's wait_for_function).
func (p *Page) waitFn(js string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	var last error
	for {
		ok, err := evTry[bool](p, "!!("+js+")")
		if err == nil && ok {
			return nil
		}
		last = err
		if time.Now().After(deadline) {
			if last != nil {
				return fmt.Errorf("timeout %v waiting for %.120s: %w", timeout, js, last)
			}
			return fmt.Errorf("timeout %v waiting for %.120s", timeout, js)
		}
		time.Sleep(50 * time.Millisecond)
	}
}

func (p *Page) mustWait(js string, timeout time.Duration) {
	p.t.Helper()
	p.must(p.waitFn(js, timeout), "wait")
}

const visJS = `((s) => { const e = document.querySelector(s); if (!e) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden'; })`

// waitVisible waits for an element that exists and is visible (Playwright's default wait_for_selector).
func (p *Page) waitVisible(sel string, timeout time.Duration) error {
	return p.waitFn(visJS+"("+jq(sel)+")", timeout)
}

func (p *Page) mustVisible(sel string, timeout time.Duration) {
	p.t.Helper()
	if err := p.waitVisible(sel, timeout); err != nil {
		p.t.Fatalf("selector %q: %v", sel, err)
	}
}

func (p *Page) waitGone(sel string, timeout time.Duration) error {
	return p.waitFn("!document.querySelector("+jq(sel)+")", timeout)
}

func (p *Page) exists(sel string) bool {
	return ev[bool](p, "!!document.querySelector("+jq(sel)+")")
}

func (p *Page) visible(sel string) bool { return ev[bool](p, visJS+"("+jq(sel)+")") }

func (p *Page) count(sel string) int {
	return ev[int](p, "document.querySelectorAll("+jq(sel)+").length")
}

func (p *Page) text(sel string) string {
	return ev[string](p, "((e) => e ? e.innerText : '')(document.querySelector("+jq(sel)+"))")
}

func (p *Page) attr(sel, name string) string {
	return ev[string](p, "((e) => e ? (e.getAttribute("+jq(name)+") || '') : '')(document.querySelector("+jq(sel)+"))")
}

// gotoTry navigates and waits for the load event. The first navigation to an origin from a page wipes that origin's
// storage: every tab shares the browser's default context, so without this a scenario would see the previous one's
// settings, history and service workers.
func (p *Page) gotoTry(u string) error {
	if pu, err := url.Parse(u); err == nil && pu.Host != "" {
		origin := pu.Scheme + "://" + pu.Host
		if p.wiped == nil {
			p.wiped = map[string]bool{}
		}
		if !p.wiped[origin] {
			p.wiped[origin] = true
			_ = p.run(chromedp.ActionFunc(func(ctx context.Context) error {
				return storage.ClearDataForOrigin(origin, "all").Do(ctx)
			}))
		}
	}
	return p.run(chromedp.Navigate(u))
}
func (p *Page) goto_(u string) {
	p.t.Helper()
	p.must(p.gotoTry(u), "navigate "+u)
}

func (p *Page) reload() {
	p.t.Helper()
	p.must(p.run(chromedp.Reload()), "reload")
}

func (p *Page) back() {
	p.t.Helper()
	p.must(p.run(chromedp.NavigateBack()), "back")
}

func (p *Page) shot(name string) {
	var buf []byte
	if err := p.run(chromedp.CaptureScreenshot(&buf)); err == nil {
		_ = os.WriteFile(filepath.Join(outDir, name), buf, 0o644)
	}
}

// networkIdle waits until nothing was in flight for 500 ms (best effort, like Playwright's networkidle).
func (p *Page) networkIdle(timeout time.Duration) bool {
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		p.mu.Lock()
		idle := len(p.inflight) == 0 && time.Since(p.lastNet) >= 500*time.Millisecond
		p.mu.Unlock()
		if idle {
			return true
		}
		time.Sleep(50 * time.Millisecond)
	}
	return false
}

func (p *Page) setOffline(off bool) {
	p.t.Helper()
	p.must(p.run(network.EmulateNetworkConditions(off, 0, -1, -1)), "offline emulation")
}

// ------------------------------------------------------------------------------------------- input

type pt struct{ x, y float64 }

func (p *Page) mouse(typ input.MouseType, x, y float64, clicks int64) error {
	return p.run(chromedp.ActionFunc(func(ctx context.Context) error {
		e := input.DispatchMouseEvent(typ, x, y)
		if typ == input.MousePressed || typ == input.MouseReleased {
			e = e.WithButton(input.Left).WithClickCount(clicks)
		}
		return e.Do(ctx)
	}))
}

func (p *Page) mouseClick(x, y float64) {
	p.t.Helper()
	p.must(p.mouse(input.MouseMoved, x, y, 0), "mouse move")
	p.must(p.mouse(input.MousePressed, x, y, 1), "mouse down")
	p.must(p.mouse(input.MouseReleased, x, y, 1), "mouse up")
}

func (p *Page) mouseDblClick(x, y float64) {
	p.t.Helper()
	p.must(p.mouse(input.MouseMoved, x, y, 0), "mouse move")
	for i := int64(1); i <= 2; i++ {
		p.must(p.mouse(input.MousePressed, x, y, i), "mouse down")
		p.must(p.mouse(input.MouseReleased, x, y, i), "mouse up")
	}
}

func (p *Page) mouseMove(x, y float64) {
	p.t.Helper()
	p.must(p.mouse(input.MouseMoved, x, y, 0), "mouse move")
}

func (p *Page) wheel(x, y, dx, dy float64) {
	p.t.Helper()
	p.must(p.run(chromedp.ActionFunc(func(ctx context.Context) error {
		return input.DispatchMouseEvent(input.MouseWheel, x, y).WithDeltaX(dx).WithDeltaY(dy).Do(ctx)
	})), "wheel")
}

func (p *Page) touch(typ input.TouchType, pts ...pt) error {
	return p.run(chromedp.ActionFunc(func(ctx context.Context) error {
		var tp []*input.TouchPoint
		for _, q := range pts {
			tp = append(tp, &input.TouchPoint{X: q.x, Y: q.y})
		}
		return input.DispatchTouchEvent(typ, tp).Do(ctx)
	}))
}

// tap is a touchscreen tap.
func (p *Page) tap(x, y float64) {
	p.t.Helper()
	p.must(p.touch(input.TouchStart, pt{x, y}), "touch start")
	p.sleep(40)
	p.must(p.touch(input.TouchEnd), "touch end")
}

// swipe is a horizontal finger drag in 6 steps, as the original scripts did.
func (p *Page) swipe(x0, x1, y float64) {
	p.t.Helper()
	p.must(p.touch(input.TouchStart, pt{x0, y}), "touch start")
	for k := 1; k <= 6; k++ {
		p.must(p.touch(input.TouchMove, pt{x0 + (x1-x0)*float64(k)/6, y}), "touch move")
	}
	p.must(p.touch(input.TouchEnd), "touch end")
}

// key presses one key: a kb constant (kb.Escape...) or a printable character.
func (p *Page) key(k string) {
	p.t.Helper()
	p.must(p.run(chromedp.KeyEvent(k)), "key")
}

func (p *Page) keyShift(k string) {
	p.t.Helper()
	p.must(p.run(chromedp.KeyEvent(k, chromedp.KeyModifiers(input.ModifierShift))), "shift+key")
}

const centerJS = `((s) => { const e = document.querySelector(s); if (!e) return null;
  e.scrollIntoView({ block: 'center', inline: 'center', behavior: 'instant' });
  const r = e.getBoundingClientRect(); if (r.width <= 0 || r.height <= 0) return null;
  const x = r.left + r.width / 2, y = r.top + r.height / 2; const h = document.elementFromPoint(x, y);
  return { x, y, hit: !!h && (h === e || e.contains(h)) }; })`

// click waits for the element to be visible and not covered, then clicks its centre with the mouse.
func (p *Page) click(sel string) {
	p.t.Helper()
	p.must(p.clickTry(sel, 15*time.Second, false), "click "+sel)
}

func (p *Page) clickTry(sel string, timeout time.Duration, force bool) error {
	deadline := time.Now().Add(timeout)
	var last string
	for {
		c, err := evTry[*struct {
			X, Y float64
			Hit  bool
		}](p, centerJS+"("+jq(sel)+")")
		if err == nil && c != nil && (c.Hit || force) {
			p.sleep(30) // let a moving element settle
			c2, err2 := evTry[*struct {
				X, Y float64
				Hit  bool
			}](p, centerJS+"("+jq(sel)+")")
			if err2 == nil && c2 != nil && c2.X == c.X && c2.Y == c.Y {
				if e := p.mouse(input.MouseMoved, c.X, c.Y, 0); e != nil {
					return e
				}
				if e := p.mouse(input.MousePressed, c.X, c.Y, 1); e != nil {
					return e
				}
				return p.mouse(input.MouseReleased, c.X, c.Y, 1)
			}
		}
		if err != nil {
			last = err.Error()
		} else if c == nil {
			last = "not visible"
		} else {
			last = "covered by another element"
		}
		if time.Now().After(deadline) {
			return fmt.Errorf("%s", last)
		}
		time.Sleep(60 * time.Millisecond)
	}
}

// clickForce clicks through the DOM (an input whose box is hidden behind a styled label, Playwright force=True).
func (p *Page) clickForce(sel string) {
	p.t.Helper()
	p.mustVisibleOrExists(sel)
	p.exec("document.querySelector(" + jq(sel) + ").click()")
}

func (p *Page) mustVisibleOrExists(sel string) {
	p.t.Helper()
	p.mustWait("!!document.querySelector("+jq(sel)+")", 15*time.Second)
}

// fill sets the value of an input and fires input and change.
func (p *Page) fill(sel, val string) {
	p.t.Helper()
	p.mustWait("!!document.querySelector("+jq(sel)+")", 15*time.Second)
	p.exec(`((s, v) => { const e = document.querySelector(s); e.focus();
      const proto = e.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, 'value').set.call(e, v);
      e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); })(` + jq(sel) + `, ` + jq(val) + `)`)
}

func (p *Page) focus(sel string) {
	p.t.Helper()
	p.mustWait("!!document.querySelector("+jq(sel)+")", 15*time.Second)
	p.exec("document.querySelector(" + jq(sel) + ").focus()")
}

// pressOn focuses an element and presses a key.
func (p *Page) pressOn(sel, k string) {
	p.t.Helper()
	p.focus(sel)
	p.key(k)
}

func (p *Page) selectValue(sel, val string) {
	p.t.Helper()
	p.mustWait("!!document.querySelector("+jq(sel)+")", 15*time.Second)
	p.exec(`((s, v) => { const e = document.querySelector(s); e.value = v;
      e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); })(` + jq(sel) + `, ` + jq(val) + `)`)
}

func (p *Page) selectIndex(sel string, idx int) {
	p.t.Helper()
	p.mustWait("!!document.querySelector("+jq(sel)+")", 15*time.Second)
	p.exec(fmt.Sprintf(`((s, i) => { const e = document.querySelector(s); e.selectedIndex = i;
      e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); })(%s, %d)`, jq(sel), idx))
}

// downloadsTo makes this browser save downloads into dir.
func (p *Page) downloadsTo(dir string) {
	p.t.Helper()
	c := chromedp.FromContext(p.ctx)
	params := browser.SetDownloadBehavior(browser.SetDownloadBehaviorBehaviorAllow).WithDownloadPath(dir)
	if c.BrowserContextID != "" {
		params = params.WithBrowserContextID(c.BrowserContextID)
	}
	p.must(params.Do(cdp.WithExecutor(p.ctx, c.Browser)), "download behaviour")
}

// waitNewDownload waits for a finished file that is not in `seen` and returns its path.
func waitNewDownload(dir string, seen map[string]bool, timeout time.Duration) (string, error) {
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		ents, _ := os.ReadDir(dir)
		for _, e := range ents {
			n := e.Name()
			if seen[n] || strings.HasPrefix(n, "got-") || strings.HasSuffix(n, ".crdownload") || strings.HasSuffix(n, ".tmp") {
				continue
			}
			// move it aside so a later download with the same name is a fresh file
			moved := fmt.Sprintf("got-%d-%s", len(seen), n)
			if os.Rename(filepath.Join(dir, n), filepath.Join(dir, moved)) != nil {
				seen[n] = true
				return filepath.Join(dir, n), nil
			}
			seen[moved] = true
			return filepath.Join(dir, moved), nil
		}
		time.Sleep(100 * time.Millisecond)
	}
	return "", errors.New("no download arrived")
}

func (p *Page) uploadFile(sel, path string) {
	p.t.Helper()
	p.must(p.run(chromedp.SetUploadFiles(sel, []string{path}, chromedp.ByQuery)), "upload")
}

// ------------------------------------------------------------------------------------------- checks

var (
	_ = kb.Escape
	_ = fmt.Sprint
)

// Checker records named assertions; a failing one fails the test but the scenario goes on, like the originals.
type Checker struct {
	t       *testing.T
	Results []CheckResult
}

type CheckResult struct {
	Tag    string `json:"tag"`
	Check  string `json:"check"`
	OK     bool   `json:"ok"`
	Detail string `json:"detail"`
}

func (c *Checker) check(tag, name string, ok bool, detail ...any) {
	c.t.Helper()
	d := ""
	if len(detail) > 0 {
		d = fmt.Sprint(detail...)
		if len(detail) == 1 {
			d = fmt.Sprintf("%v", detail[0])
		}
	}
	c.Results = append(c.Results, CheckResult{tag, name, ok, d})
	if ok {
		c.t.Logf("ok   [%s] %s %s", tag, name, short(d))
		return
	}
	c.t.Errorf("FAIL [%s] %s (%s)", tag, name, short(d))
}

func short(s string) string {
	if len(s) > 300 {
		s = s[:300] + "..."
	}
	if s == "" {
		return ""
	}
	return "(" + s + ")"
}

func (c *Checker) save(name string) {
	b, _ := json.MarshalIndent(c.Results, "", " ")
	_ = os.WriteFile(filepath.Join(outDir, name), b, 0o644)
}

func seedScript(data map[string]any, once bool) string {
	b, _ := json.Marshal(data)
	guard := ""
	if once {
		guard = "if (sessionStorage.getItem('__seeded')) return; sessionStorage.setItem('__seeded', '1'); "
	}
	return "(() => { " + guard + "const d = " + string(b) + "; for (const k in d) localStorage.setItem(k, JSON.stringify(d[k])); })();"
}

func absInt(a int) int {
	if a < 0 {
		return -a
	}
	return a
}

func absF(a float64) float64 {
	if a < 0 {
		return -a
	}
	return a
}
