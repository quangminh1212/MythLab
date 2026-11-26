//go:build windows

package main

import (
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestParseArgs(t *testing.T) {
	t.Setenv("MYTHLAB_DATA_DIR", "")
	opt, usage, err := parseArgs(nil)
	if err != nil || usage != "" || opt.port != preferredPort || opt.portSet || opt.noWindow || opt.dataDir != "" {
		t.Fatalf("defaults: %+v %q %v", opt, usage, err)
	}
	opt, _, err = parseArgs([]string{"--port", "18805", "--port-file", "p.txt", "--no-window", "--data-dir", `C:\x`, "--no-tts", "--debug"})
	if err != nil || opt.port != 18805 || !opt.portSet || opt.portFile != "p.txt" || !opt.noWindow || opt.dataDir != `C:\x` || !opt.debug {
		t.Fatalf("flags: %+v %v", opt, err)
	}
	// an explicit default port is still explicit: no silent move to another origin
	if opt, _, _ = parseArgs([]string{"--port=18765"}); !opt.portSet {
		t.Fatal("--port=18765 must count as explicit")
	}
	for _, bad := range [][]string{{"--port", "0"}, {"--port", "70000"}, {"--port", "abc"}, {"extra"}, {"--nope"}} {
		if _, usage, err := parseArgs(bad); err == nil || !strings.Contains(usage, "-port") {
			t.Errorf("%v: err=%v usage=%q", bad, err, usage)
		}
	}
	if _, usage, err := parseArgs([]string{"--help"}); err != nil || !strings.Contains(usage, "-no-window") {
		t.Errorf("--help: err=%v usage=%q", err, usage)
	}
	t.Setenv("MYTHLAB_DATA_DIR", `D:\env`)
	if opt, _, _ = parseArgs(nil); opt.dataDir != `D:\env` {
		t.Errorf("env data dir: %q", opt.dataDir)
	}
	if opt, _, _ = parseArgs([]string{"--data-dir", `D:\flag`}); opt.dataDir != `D:\flag` {
		t.Errorf("the flag wins over the environment: %q", opt.dataDir)
	}
}

func TestListenLoopback(t *testing.T) {
	const port = 18804
	first, fellBack, err := listenLoopback(port, true)
	if err != nil || fellBack {
		t.Fatalf("free port: %v fellBack=%v", err, fellBack)
	}
	defer first.Close()
	if got := first.Addr().(*net.TCPAddr); got.Port != port || !got.IP.IsLoopback() {
		t.Fatalf("bound %v", got)
	}
	if ln, _, err := listenLoopback(port, true); err == nil {
		ln.Close()
		t.Fatal("an explicit busy port must fail")
	}
	ln, fellBack, err := listenLoopback(port, false)
	if err != nil || !fellBack {
		t.Fatalf("fallback: %v fellBack=%v", err, fellBack)
	}
	defer ln.Close()
	if got := ln.Addr().(*net.TCPAddr); got.Port == port || got.Port == 0 || !got.IP.IsLoopback() {
		t.Fatalf("fallback bound %v", got)
	}
}

func TestMythlabAt(t *testing.T) {
	port := func(s *httptest.Server) int { return s.Listener.Addr().(*net.TCPAddr).Port }
	yes := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/ping" {
			http.NotFound(w, r)
			return
		}
		w.Write([]byte(`{"ok": true, "app": "mythlab"}`))
	}))
	defer yes.Close()
	no := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.Write([]byte("<html>")) }))
	defer no.Close()
	if !mythlabAt(port(yes)) {
		t.Error("a MythLab server was not recognised")
	}
	if mythlabAt(port(no)) {
		t.Error("a foreign server was taken for MythLab")
	}
	closed := port(no)
	no.Close()
	if mythlabAt(closed) {
		t.Error("a closed port was taken for MythLab")
	}
}

func TestWinState(t *testing.T) {
	dir := t.TempDir()
	file := filepath.Join(dir, "sub", "window.json")
	def := winState{Width: defaultWidth, Height: defaultHeight}
	if got := loadWinState(file); got != def {
		t.Fatalf("missing file: %+v", got)
	}
	if err := saveWinState(file, winState{Width: 1500, Height: 900, Maximized: true}); err != nil {
		t.Fatal(err)
	}
	if got := loadWinState(file); got != (winState{Width: 1500, Height: 900, Maximized: true}) {
		t.Fatalf("round trip: %+v", got)
	}
	if entries, _ := os.ReadDir(filepath.Dir(file)); len(entries) != 1 {
		t.Fatalf("temporary files left behind: %v", entries)
	}
	for content, want := range map[string]winState{
		`{"width": 1200, "height": 820}`:                     {Width: 1200, Height: 820}, // written by the old app
		`{"width": 1280.0, "height": 700.5}`:                 {Width: 1280, Height: 700},
		"\xef\xbb\xbf" + `{"width": 900, "height": 700}`:     {Width: 900, Height: 700},
		`{"width": 100, "height": 100}`:                      {Width: minWidth, Height: minHeight},
		`{"width": 99999, "height": 99999}`:                  {Width: 16384, Height: 16384},
		`{"width": 800, "height": 700, "maximized": true}`:   {Width: 800, Height: 700, Maximized: true},
		`{"width": -5, "height": 700}`:                       def,
		`{"width": "wide", "height": 700}`:                   def,
		`{"height": 700}`:                                    def,
		`{"width": 1e300, "height": 700}`:                    def,
		`not json`:                                           def,
		``:                                                   def,
		`[1200, 820]`:                                        def,
		`{"width": 1000, "height": 800, "future": {"x": 1}}`: {Width: 1000, Height: 800},
	} {
		if err := os.WriteFile(file, []byte(content), 0o644); err != nil {
			t.Fatal(err)
		}
		if got := loadWinState(file); got != want {
			t.Errorf("%q: got %+v, want %+v", content, got, want)
		}
	}
	// the file keeps the shape the old app wrote
	saveWinState(file, winState{Width: 1200, Height: 820})
	if data, _ := os.ReadFile(file); string(data) != `{"width":1200,"height":820}` {
		t.Errorf("window.json = %s", data)
	}
}

func TestScale(t *testing.T) {
	for _, dpi := range []int{96, 120, 144, 168, 192, 240} {
		for _, v := range []int{420, 600, 820, 1200, 1917} {
			if got := unscale(scale(v, dpi), dpi); got != v {
				t.Errorf("dpi %d: %d -> %d -> %d", dpi, v, scale(v, dpi), got)
			}
		}
	}
	if scale(1200, 144) != 1800 || scale(820, 120) != 1025 {
		t.Error("scale is wrong")
	}
}

func TestDirsAndInstanceName(t *testing.T) {
	d, err := resolveDirs("")
	if err != nil {
		t.Fatal(err)
	}
	local, roaming := os.Getenv("LOCALAPPDATA"), os.Getenv("APPDATA")
	if d.override || d.webview() != filepath.Join(local, "MythLab", "webview") || d.logFile() != filepath.Join(local, "MythLab", "desktop.log") ||
		d.windowFile() != filepath.Join(roaming, "MythLab", "window.json") {
		t.Fatalf("standard dirs: %+v", d)
	}
	if instanceName(d) != "MythLab.Desktop" {
		t.Fatalf("instance name %q", instanceName(d))
	}
	tmp := t.TempDir()
	o, err := resolveDirs(tmp)
	if err != nil || !o.override || o.webview() != filepath.Join(tmp, "webview") || o.windowFile() != filepath.Join(tmp, "window.json") ||
		o.logFile() != filepath.Join(tmp, "desktop.log") || o.edgeApp() != filepath.Join(tmp, "edge-app") {
		t.Fatalf("override dirs: %+v %v", o, err)
	}
	n := instanceName(o)
	if n == "MythLab.Desktop" || !strings.HasPrefix(n, "MythLab.Desktop.") || strings.ContainsAny(n, `\/`) {
		t.Fatalf("override instance name %q", n)
	}
	same, _ := resolveDirs(strings.ToUpper(tmp) + `\.`)
	other, _ := resolveDirs(t.TempDir())
	if instanceName(same) != n || instanceName(other) == n {
		t.Fatalf("instance names: %q %q %q", n, instanceName(same), instanceName(other))
	}
}

func TestLogSink(t *testing.T) {
	file := filepath.Join(t.TempDir(), "logs", "desktop.log")
	s, err := openLog(file)
	if err != nil {
		t.Fatal(err)
	}
	var fatal []string
	s.setFatalHook(func(msg string) { fatal = append(fatal, msg) })
	s.logf("xin chào %d", 1)
	s.Write([]byte("2026/01/01 Creating environment failed with 80070005\n"))
	s.Write([]byte("an ordinary line\n"))
	s.setFatalHook(nil)
	s.Write([]byte("Creating controller failed with 1\n"))
	s.file().Close()
	data, _ := os.ReadFile(file)
	text := string(data)
	if !strings.Contains(text, " [desktop] xin chào 1\n") || !strings.Contains(text, "an ordinary line\n") || !strings.Contains(text, "Creating controller failed") {
		t.Errorf("log content: %q", text)
	}
	if len(fatal) != 1 || fatal[0] != "2026/01/01 Creating environment failed with 80070005" {
		t.Errorf("fatal hook calls: %q", fatal)
	}

	// rotation: an oversized log moves to .1 and a fresh one starts
	if err := os.WriteFile(file, make([]byte, maxLogBytes+1), 0o644); err != nil {
		t.Fatal(err)
	}
	s, err = openLog(file)
	if err != nil {
		t.Fatal(err)
	}
	s.logf("mới")
	s.file().Close()
	if st, err := os.Stat(file + ".1"); err != nil || st.Size() != maxLogBytes+1 {
		t.Errorf("rotated log: %v", err)
	}
	if st, err := os.Stat(file); err != nil || st.Size() > 200 {
		t.Errorf("fresh log: %v", err)
	}
}

func TestRequestQuitWithoutInstance(t *testing.T) {
	d, _ := resolveDirs(t.TempDir())
	if code := requestQuit(instanceName(d)); code != exitError {
		t.Fatalf("--quit with nothing running returned %d", code)
	}
}

func TestExternalTarget(t *testing.T) {
	const app = "http://127.0.0.1:18765/"
	cases := map[string]bool{
		"https://github.com/x/y":         true,
		"http://example.com/":            true,
		"http://127.0.0.1:18765/#/story": false,
		"http://127.0.0.1:9999/":         true,
		"http://localhost:18765/":        true,
		"file:///C:/Windows/win.ini":     false,
		"javascript:alert(1)":            false,
		"mailto:a@b.c":                   false,
		"ms-msdt:/id":                    false,
		"":                               false,
		"//evil.example/":                false,
	}
	for in, want := range cases {
		if got := externalTarget(in, app); got != want {
			t.Errorf("externalTarget(%q) = %v, want %v", in, got, want)
		}
	}
}
