package app

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"testing/fstest"
	"time"

	"mythlab/internal/tts"
)

func write(t *testing.T, path, content string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestParseConfig(t *testing.T) {
	base := t.TempDir()
	abs := filepath.Join(t.TempDir(), "abs")
	cfg, err := ParseConfig(nil, base, false)
	if err != nil || len(cfg.Local) != 2 || cfg.Local[0].Path != filepath.Dir(base) || cfg.Local[1].Path != filepath.Join(base, "library") ||
		len(cfg.GitHub) != 1 || cfg.GitHub[0].Prefix != "Done_" || cfg.GitHub[0].Owner != "" || cfg.DefaultVoice != "vi-VN-HoaiMyNeural" || !cfg.TrustLoopback {
		t.Fatalf("defaults: %+v %v", cfg, err)
	}
	cfg, _ = ParseConfig(nil, base, true)
	if len(cfg.Local) != 1 || cfg.Local[0].Name != "Thư viện (library/)" || cfg.Local[0].Path != filepath.Join(base, "library") {
		t.Fatalf("first run: %+v", cfg.Local)
	}

	// BOM, github as one object, entries without a path, disabled sources, extras
	data := "\xef\xbb\xbf" + `{
	  "local": [{"name": "A", "path": "x"}, {"name": "no path"}, "junk", {"path": ` + string(mustJSON(abs)) + `}],
	  "github": {"owner": " me ", "prefix": "P_", "name": "Kho"},
	  "tts": {"default_voice": "vi-VN-NamMinhNeural", "cache_max_mb": 10},
	  "server": {"access_key": "k1", "hosts": ["reader.lan"], "trust_loopback": false}
	}`
	cfg, err = ParseConfig([]byte(data), base, false)
	if err != nil {
		t.Fatal(err)
	}
	if len(cfg.Local) != 2 || cfg.Local[0].Index != 0 || cfg.Local[0].Path != filepath.Join(base, "x") ||
		cfg.Local[1].Index != 3 || cfg.Local[1].Path != abs || cfg.Local[1].Name != "abs" {
		t.Fatalf("local: %+v", cfg.Local)
	}
	if len(cfg.GitHub) != 1 || cfg.GitHub[0] != (GitHubSource{0, "Kho", "me", "P_"}) {
		t.Fatalf("github: %+v", cfg.GitHub)
	}
	if cfg.DefaultVoice != "vi-VN-NamMinhNeural" || cfg.TTSCacheBytes != 10<<20 || cfg.AccessKey != "k1" ||
		len(cfg.Hosts) != 1 || cfg.TrustLoopback {
		t.Fatalf("extras: %+v", cfg)
	}
	// the merge is shallow: a given key replaces the default one, the others stay
	cfg, _ = ParseConfig([]byte(`{"github": [{"owner":"a","enabled":false},{"owner":"b"}]}`), base, false)
	if len(cfg.Local) != 2 || len(cfg.GitHub) != 1 || cfg.GitHub[0].Index != 1 || cfg.GitHub[0].Owner != "b" || cfg.GitHub[0].Prefix != "Done_" {
		t.Fatalf("merge: %+v", cfg)
	}
	cfg, _ = ParseConfig([]byte(`{"local": [], "github": null}`), base, false)
	if len(cfg.Local) != 0 || len(cfg.GitHub) != 0 {
		t.Fatalf("empty: %+v", cfg)
	}
	// broken file: defaults plus an error to log
	for _, bad := range []string{"{ nope", "[]", "null", ""} {
		cfg, err = ParseConfig([]byte(bad), base, false)
		if err == nil || len(cfg.Local) != 2 {
			t.Fatalf("broken config %q: %+v %v", bad, cfg, err)
		}
	}
}

func mustJSON(v any) []byte {
	b, err := json.Marshal(v)
	if err != nil {
		panic(err)
	}
	return b
}

func TestDiscover(t *testing.T) {
	root := t.TempDir()
	// hermetic: never see the developer's real per-user config
	t.Setenv("APPDATA", filepath.Join(root, "appdata"))
	t.Setenv("LOCALAPPDATA", filepath.Join(root, "localappdata"))
	t.Setenv("XDG_CONFIG_HOME", filepath.Join(root, "xdgcfg"))
	t.Setenv("XDG_CACHE_HOME", filepath.Join(root, "xdgcache"))
	userCfg, userCache := userDirs()

	// nothing anywhere: the per-user location, first run
	empty := filepath.Join(root, "empty")
	os.MkdirAll(empty, 0o755)
	p, err := discover("", "", filepath.Join(root, "bin"), empty)
	if err != nil || p.Config != filepath.Join(userCfg, "config.json") || p.Cache != userCache || p.Base != userCfg {
		t.Fatalf("user location: %+v %v", p, err)
	}
	if p.FirstRun == isFile(p.Config) {
		t.Fatalf("FirstRun must mirror the missing file: %+v", p)
	}

	// repository mode: nearest reader/config.json walking up
	repo := filepath.Join(root, "repo")
	write(t, filepath.Join(repo, "reader", "config.json"), "{}")
	deep := filepath.Join(repo, "server", "cmd")
	os.MkdirAll(deep, 0o755)
	p, _ = discover("", "", filepath.Join(root, "bin"), deep)
	if p.Config != filepath.Join(repo, "reader", "config.json") || p.Cache != filepath.Join(repo, "reader", ".cache") ||
		p.Base != filepath.Join(repo, "reader") || p.FirstRun {
		t.Fatalf("repo mode: %+v", p)
	}

	// config beside the executable wins over the repository
	write(t, filepath.Join(root, "bin", "config.json"), "{}")
	p, _ = discover("", "", filepath.Join(root, "bin"), deep)
	if p.Config != filepath.Join(root, "bin", "config.json") || p.Cache != userCache {
		t.Fatalf("exe dir: %+v", p)
	}

	// repository mode also works from the executable's checkout when the cwd is elsewhere
	p, _ = discover("", "", filepath.Join(repo, "apps", "desktop", "dist"), empty)
	if p.Config != filepath.Join(repo, "reader", "config.json") {
		t.Fatalf("repo next to exe: %+v", p)
	}

	// per-user config beats the working directory's checkout
	write(t, filepath.Join(userCfg, "config.json"), "{}")
	p, _ = discover("", "", filepath.Join(root, "nobin"), deep)
	if p.Config != filepath.Join(userCfg, "config.json") || p.Cache != userCache || p.FirstRun {
		t.Fatalf("user config before cwd: %+v", p)
	}
	os.Remove(filepath.Join(userCfg, "config.json"))

	// explicit flags win over everything
	other := filepath.Join(root, "other", "my.json")
	write(t, other, "{}")
	p, _ = discover(other, "", filepath.Join(root, "bin"), deep)
	if p.Config != other || p.Base != filepath.Dir(other) || p.Cache != userCache {
		t.Fatalf("--config: %+v", p)
	}
	p, _ = discover(filepath.Join(repo, "reader", "config.json"), "", "", empty)
	if p.Cache != filepath.Join(repo, "reader", ".cache") {
		t.Fatalf("--config in a checkout keeps the checkout's cache: %+v", p)
	}
	p, _ = discover(other, filepath.Join(root, "c"), "", empty)
	if p.Cache != filepath.Join(root, "c") {
		t.Fatalf("--cache: %+v", p)
	}
	if _, err := discover(filepath.Join(root, "missing.json"), "", "", empty); err == nil {
		t.Fatal("a missing --config file is an error")
	}
}

type fakeEngine struct{}

func (fakeEngine) Synthesize(context.Context, string, string, int, int) ([]byte, error) {
	return []byte("ID3 fake audio"), nil
}
func (fakeEngine) Voices(context.Context) ([]tts.Voice, error) { return nil, nil }

func newApp(t *testing.T, cfgJSON string, mut func(*Options)) (*App, *bytes.Buffer) {
	t.Helper()
	dir := t.TempDir()
	write(t, filepath.Join(dir, "config.json"), cfgJSON)
	write(t, filepath.Join(dir, "lib", "Truyện A", "Chương 1.txt"), "Nội dung chương một.")
	var logs bytes.Buffer
	o := Options{ConfigPath: filepath.Join(dir, "config.json"), CacheDir: filepath.Join(dir, "cache"),
		StaticFS: fstest.MapFS{"index.html": {Data: []byte("ui")}}, Logger: log.New(&logs, "", 0)}
	if mut != nil {
		mut(&o)
	}
	a, err := New(o)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(a.Close)
	return a, &logs
}

const localOnly = `{"local": [{"name": "Thử", "path": "lib"}], "github": []}`

func TestAccessKey(t *testing.T) {
	a, _ := newApp(t, localOnly, nil)
	file := filepath.Join(a.Paths().Cache, "server.json")
	if a.Exposed() || a.accessKey(false) != "" {
		t.Fatal("a loopback server has no key until one is asked for")
	}
	if _, err := os.Stat(file); err == nil {
		t.Fatal("no key file may be created on a loopback server")
	}
	k := a.AccessKey()
	if len(k) != 24 || strings.ContainsAny(k, "+/=") {
		t.Fatalf("key format: %d characters", len(k))
	}
	var saved struct {
		AccessKey string `json:"access_key"`
	}
	data, _ := os.ReadFile(file)
	if json.Unmarshal(data, &saved) != nil || saved.AccessKey != k {
		t.Fatal("the key must be stored in <cache>/server.json")
	}
	// a second app on the same cache reuses it
	b, err := New(Options{ConfigPath: a.Paths().Config, CacheDir: a.Paths().Cache, StaticFS: fstest.MapFS{}, Logger: log.New(io.Discard, "", 0)})
	if err != nil {
		t.Fatal(err)
	}
	defer b.Close()
	if b.AccessKey() != k {
		t.Fatal("the stored key must be reused")
	}
	// the config wins
	c, _ := newApp(t, `{"local": [], "github": [], "server": {"access_key": "from-config"}}`, nil)
	if c.AccessKey() != "from-config" {
		t.Fatal("config server.access_key must win")
	}
	if _, err := os.Stat(filepath.Join(c.Paths().Cache, "server.json")); err == nil {
		t.Fatal("no key file when the config has the key")
	}
}

func TestBannerAndModes(t *testing.T) {
	a, _ := newApp(t, localOnly, func(o *Options) { o.Port = 8765 })
	if a.Addr() != "127.0.0.1:8765" || a.Exposed() {
		t.Fatalf("default bind: %s", a.Addr())
	}
	lines := strings.Split(strings.TrimSpace(a.Banner(8765)), "\n")
	if lines[0] != "MythLab Reader: http://127.0.0.1:8765  (edge-tts: không)" ||
		lines[1] != "  nguồn: Thử - "+filepath.Join(filepath.Dir(a.Paths().Config), "lib") || len(lines) != 2 {
		t.Fatalf("banner: %q", lines)
	}

	cfg := `{"local": [], "github": [{"owner": "someone", "prefix": "Done_"}], "server": {"access_key": "banner-key"}}`
	l, _ := newApp(t, cfg, func(o *Options) { o.LAN = true; o.Port = 9000; o.TTS = fakeEngine{} })
	if l.Addr() != "0.0.0.0:9000" || !l.Exposed() {
		t.Fatalf("LAN bind: %s", l.Addr())
	}
	text := l.Banner(9000)
	if !strings.HasPrefix(text, "MythLab Reader (LAN): http://127.0.0.1:9000  (edge-tts: có)\n  khoá truy cập: banner-key\n") ||
		!strings.HasSuffix(text, "  nguồn: GitHub someone/Done_* - someone/Done_*\n") {
		t.Fatalf("LAN banner: %q", text)
	}
	for _, ip := range LANIPs() {
		if strings.HasPrefix(ip, "127.") || strings.HasPrefix(ip, "169.254.") || net.ParseIP(ip).To4() == nil {
			t.Errorf("LANIPs: %s", ip)
		}
		if !strings.Contains(text, "  LAN: http://"+ip+":9000/?k=banner-key\n") {
			t.Errorf("banner lacks the link for %s", ip)
		}
	}
	// an explicit non-loopback host is exposed even without --lan
	h, _ := newApp(t, localOnly, func(o *Options) { o.Host = "0.0.0.0" })
	if !h.Exposed() {
		t.Fatal("0.0.0.0 without --lan must still require the key")
	}
	for _, host := range []string{"localhost", "::1", "127.0.0.2"} {
		x, _ := newApp(t, localOnly, func(o *Options) { o.Host = host })
		if x.Exposed() {
			t.Errorf("%s is loopback", host)
		}
	}
	if _, err := New(Options{ConfigPath: a.Paths().Config, StaticDir: filepath.Join(t.TempDir(), "nope")}); err == nil {
		t.Fatal("a missing --static directory is an error")
	}
	if _, err := New(Options{ConfigPath: a.Paths().Config, Port: 70000}); err == nil {
		t.Fatal("a bad port is an error")
	}
}

func get(t *testing.T, url string, hdr ...string) (int, string, http.Header) {
	t.Helper()
	req, _ := http.NewRequest(http.MethodGet, url, nil)
	for i := 0; i+1 < len(hdr); i += 2 {
		req.Header.Set(hdr[i], hdr[i+1])
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	return resp.StatusCode, string(body), resp.Header
}

// TestServe runs the whole stack on a real socket (test port 18803).
func TestServe(t *testing.T) {
	a, logs := newApp(t, localOnly, func(o *Options) { o.Port = 18803; o.TTS = fakeEngine{} })
	ln, err := a.Listen()
	if err != nil {
		t.Skipf("port 18803 is busy: %v", err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	errc := make(chan error, 1)
	go func() { errc <- a.Serve(ctx, ln) }()
	base := "http://127.0.0.1:18803"

	if code, body, _ := get(t, base+"/api/ping"); code != 200 || body != `{"ok":true,"app":"mythlab","api":2,"server":"go"}` {
		t.Fatalf("ping: %d %s", code, body)
	}
	if code, body, _ := get(t, base+"/"); code != 200 || body != "ui" {
		t.Fatalf("ui: %d %s", code, body)
	}
	code, body, _ := get(t, base+"/api/stories?source=local0")
	if code != 200 || !strings.Contains(body, `"key":"Truyện A"`) {
		t.Fatalf("stories: %d %s", code, body)
	}
	if code, body, _ := get(t, base+"/api/search?q=truyen"); code != 200 || !strings.Contains(body, `"total":1`) {
		t.Fatalf("search: %d %s", code, body)
	}
	if code, body, h := get(t, base+"/api/tts?text=xin+ch%C3%A0o"); code != 200 || body != "ID3 fake audio" || h.Get("Content-Type") != "audio/mpeg" {
		t.Fatalf("tts: %d %q", code, body)
	}
	if _, err := os.Stat(filepath.Join(a.Paths().Cache, "tts")); err != nil {
		t.Fatal("audio must be cached under <cache>/tts")
	}
	// DNS rebinding: a foreign name in Host is refused even from loopback
	if code, _, _ := get(t, base+"/api/ping", "Host", "evil.example"); code != 200 {
		// net/http's client sends the URL host; set it explicitly below
		t.Logf("host header via client: %d", code)
	}
	req, _ := http.NewRequest(http.MethodGet, base+"/api/ping", nil)
	req.Host = "evil.example"
	if resp, err := http.DefaultClient.Do(req); err != nil || resp.StatusCode != 403 {
		t.Fatalf("foreign Host must be refused: %v", err)
	} else {
		resp.Body.Close()
	}
	// oversized request headers are refused by the server limits
	if code, _, _ := get(t, base+"/api/ping", "X-Big", strings.Repeat("a", 200<<10)); code != http.StatusRequestHeaderFieldsTooLarge {
		t.Fatalf("header limit: %d", code)
	}

	cancel()
	select {
	case err := <-errc:
		if err != nil {
			t.Fatalf("graceful shutdown: %v", err)
		}
	case <-time.After(15 * time.Second):
		t.Fatal("the server did not stop")
	}
	if c, err := net.DialTimeout("tcp", "127.0.0.1:18803", time.Second); err == nil {
		c.Close()
		t.Fatal("the port must be released")
	}
	if !strings.Contains(logs.String(), `"GET /api/ping HTTP/1.1" 200`) || strings.Contains(logs.String(), "/api/tts") {
		t.Fatalf("request log: %s", logs.String())
	}
}

func TestPrefetchCoversLocal(t *testing.T) {
	// the stories exist before the app starts (the local scan is cached for a few seconds)
	a, _ := newApp(t, localOnly, func(o *Options) {
		lib := filepath.Join(filepath.Dir(o.ConfigPath), "lib")
		write(t, filepath.Join(lib, "Truyện B", "Chương 1.txt"), "b")
		write(t, filepath.Join(lib, "Truyện B", "cover.png"), pngMagic)
		write(t, filepath.Join(lib, "Truyện C", "Chương 1.txt"), "c")
		// a poster on a non-public address: refused by the SSRF guard, counted as a failure
		write(t, filepath.Join(lib, "Truyện C", "info.json"), `{"poster": "http://127.0.0.1:9/x.jpg"}`)
	})
	var out bytes.Buffer
	st := a.PrefetchCovers(context.Background(), &out, 2)
	if st.Stories != 3 || st.FolderImg != 1 || st.NoCover != 1 || st.Posters != 1 || st.OK != 0 || st.Fail != 1 {
		t.Fatalf("stats: %+v\n%s", st, out.String())
	}
	if !strings.Contains(out.String(), "[covers] Thử: 3 truyện") || !strings.Contains(out.String(), "[covers] 1/1  ok=0 lỗi=1") ||
		!strings.Contains(out.String(), "[covers] xong: 3 truyện") {
		t.Fatalf("output: %s", out.String())
	}
}

const pngMagic = "PNG-PLACEHOLDER"
