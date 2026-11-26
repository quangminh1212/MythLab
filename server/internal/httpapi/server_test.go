package httpapi

import (
	"bytes"
	"compress/gzip"
	"context"
	"encoding/json"
	"image"
	"image/color"
	"image/jpeg"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"testing/fstest"

	"mythlab/internal/covers"
	"mythlab/internal/library"
	"mythlab/internal/tts"
)

const testKey = "test-key-0123456789abcdef"

type fakeEngine struct{ calls int }

func (f *fakeEngine) Synthesize(_ context.Context, text, voice string, _, _ int) ([]byte, error) {
	f.calls++
	return []byte("ID3-fake-mp3:" + voice + ":" + text + strings.Repeat("x", 200)), nil
}

func (f *fakeEngine) Voices(context.Context) ([]tts.Voice, error) {
	return []tts.Voice{{ShortName: "vi-VN-HoaiMyNeural", Locale: "vi-VN", Gender: "Female", FriendlyName: "Hoài My"}}, nil
}

func writeFile(t *testing.T, path, content string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

func testJPEG(w, h int) string {
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			img.Set(x, y, color.RGBA{uint8(x), uint8(y), 90, 255})
		}
	}
	var b bytes.Buffer
	jpeg.Encode(&b, img, nil)
	return b.String()
}

type fixture struct {
	s    *Server
	root string
	eng  *fakeEngine
	logs *[]string
}

func newFixture(t *testing.T, mut func(*Options)) *fixture {
	t.Helper()
	root := t.TempDir()
	cache := t.TempDir()
	writeFile(t, filepath.Join(root, "Truyện A", "Chương 1 - Một.txt"), "Chương 1: Một\n\nĐoạn một.\n\nĐoạn hai có bốn chữ.\n")
	writeFile(t, filepath.Join(root, "Truyện A", "Chương 2 - Hai.txt"), strings.Repeat("Một đoạn văn khá dài để nén.\n\n", 120))
	writeFile(t, filepath.Join(root, "Truyện A", "cover.jpg"), testJPEG(600, 900))
	writeFile(t, filepath.Join(root, "Truyện A", "info.json"),
		`{"name":"Cổ Tích","author":"Tác Giả","tags":[{"name":"Tiên hiệp"},{"name":"Hài"}],"status_name":"Hoàn thành","updated_at":"2024-01-02"}`)
	writeFile(t, filepath.Join(root, "Kho", "Truyện B", "Chương 1.txt"), "b1")
	writeFile(t, filepath.Join(root, "Kho", "Truyện B", "Chương 2.txt"), "b2")
	writeFile(t, filepath.Join(root, "Kho", "Truyện B", "Chương 3.txt"), "b3")
	writeFile(t, filepath.Join(root, "Kho", "Truyện B", "info.json"), `{"name":"Bê","genres":[{"name":"Hài"}],"status_name":"Đang ra","updated_at":"2025-06-01"}`)
	writeFile(t, filepath.Join(root, "Truyện D", "Chương 1.txt"), "d1")
	writeFile(t, filepath.Join(root, "secret.txt"), "secret")

	lib := library.NewLibrary(library.NewLocalProvider("local0", "Thử", root))
	eng := &fakeEngine{}
	var logs []string
	o := Options{
		Library: lib, Search: library.NewSearchIndex(lib),
		Covers: covers.New(covers.Options{Dir: filepath.Join(cache, "covers")}),
		TTS:    tts.NewService(tts.ServiceOptions{Engine: eng, Dir: filepath.Join(cache, "tts")}),
		Static: fstest.MapFS{
			"index.html":                   {Data: []byte("<!doctype html><title>MythLab</title>")},
			"app.js":                       {Data: []byte(strings.Repeat("console.log('mythlab');\n", 100))},
			"sw.js":                        {Data: []byte("// sw")},
			"icons/icon.png":               {Data: []byte("\x89PNG\r\n\x1a\n0123456789")},
			"_astro/app.abc123.js":         {Data: []byte("export{}")},
			"docs/index.html":              {Data: []byte("docs")},
			"tts/models/vi_VN-x.onnx":      {Data: []byte("0123456789abcdefghij")},
			"tts/models/vi_VN-x.onnx.json": {Data: []byte("{}")},
			".env":                         {Data: []byte("SECRET=1")},
		},
		AccessKey: func() string { return testKey },
		Hosts:     []string{"reader.example"},
	}
	if mut != nil {
		mut(&o)
	}
	o.Logf = func(f string, a ...any) { logs = append(logs, f); t.Logf(f, a...) }
	t.Cleanup(o.Covers.Close)
	return &fixture{s: New(o), root: root, eng: eng, logs: &logs}
}

type reqOpt func(*http.Request)

func from(addr string) reqOpt   { return func(r *http.Request) { r.RemoteAddr = addr } }
func host(h string) reqOpt      { return func(r *http.Request) { r.Host = h } }
func header(k, v string) reqOpt { return func(r *http.Request) { r.Header.Set(k, v) } }
func method(m string) reqOpt    { return func(r *http.Request) { r.Method = m } }
func (f *fixture) lan(target string, opts ...reqOpt) *httptest.ResponseRecorder {
	return f.do(target, append([]reqOpt{from("192.168.1.50:50000"), host("192.168.1.10:8765")}, opts...)...)
}

func (f *fixture) do(target string, opts ...reqOpt) *httptest.ResponseRecorder {
	r := httptest.NewRequest(http.MethodGet, target, nil)
	r.RemoteAddr = "127.0.0.1:51234"
	r.Host = "127.0.0.1:8765"
	for _, o := range opts {
		o(r)
	}
	w := httptest.NewRecorder()
	f.s.ServeHTTP(w, r)
	return w
}

func decode(t *testing.T, w *httptest.ResponseRecorder) map[string]any {
	t.Helper()
	var body io.Reader = w.Body
	if w.Header().Get("Content-Encoding") == "gzip" {
		gz, err := gzip.NewReader(w.Body)
		if err != nil {
			t.Fatal(err)
		}
		body = gz
	}
	raw, _ := io.ReadAll(body)
	var m map[string]any
	if err := json.Unmarshal(raw, &m); err != nil {
		t.Fatalf("not JSON (%d): %q", w.Code, raw)
	}
	return m
}

func wantStatus(t *testing.T, w *httptest.ResponseRecorder, code int) {
	t.Helper()
	if w.Code != code {
		t.Fatalf("status %d, want %d: %s", w.Code, code, w.Body.String())
	}
}

func wantError(t *testing.T, w *httptest.ResponseRecorder, status int, code string) {
	t.Helper()
	wantStatus(t, w, status)
	m := decode(t, w)
	if m["code"] != code || m["error"] == "" || m["error"] == nil {
		t.Fatalf("error body %v, want code %q", m, code)
	}
}

func qs(kv ...string) string {
	v := url.Values{}
	for i := 0; i+1 < len(kv); i += 2 {
		v.Set(kv[i], kv[i+1])
	}
	return v.Encode()
}

func TestAuth(t *testing.T) {
	f := newFixture(t, nil)
	// loopback peers need no key, over IPv4, IPv6 and the mapped form
	for _, addr := range []string{"127.0.0.1:5000", "[::1]:5000", "[::ffff:127.0.0.1]:5000", "127.8.9.10:1"} {
		wantStatus(t, f.do("/api/ping", from(addr)), 200)
	}
	// every other peer does, whatever Host it names
	for _, addr := range []string{"192.168.1.50:5000", "10.0.0.7:1", "[fe80::1%eth0]:5000", "[2001:db8::1]:443", "8.8.8.8:53", "garbage", ""} {
		w := f.do("/api/ping", from(addr), host("localhost:8765"))
		if !strings.Contains(w.Body.String(), "cần khoá truy cập (X-MythLab-Key)") {
			t.Fatalf("401 message changed: %s", w.Body.String())
		}
		wantError(t, w, 401, "unauthorized")
	}
	wantStatus(t, f.lan("/api/ping", header(KeyHeader, testKey)), 200)
	wantStatus(t, f.lan("/api/ping?k="+testKey), 200)
	wantStatus(t, f.lan("/api/ping", header("Cookie", "a=b; "+KeyCookie+"="+testKey)), 200)
	for _, bad := range []string{"", "x", testKey + "x", testKey[:len(testKey)-1], strings.ToUpper(testKey)} {
		wantStatus(t, f.lan("/api/ping", header(KeyHeader, bad)), 401)
		wantStatus(t, f.lan("/api/ping?k="+bad), 401)
		wantStatus(t, f.lan("/api/ping", header("Cookie", KeyCookie+"="+bad)), 401)
	}
	// a wrong header does not mask a right cookie
	wantStatus(t, f.lan("/api/ping", header(KeyHeader, "nope"), header("Cookie", KeyCookie+"="+testKey)), 200)
	// every route is guarded, also unknown ones and HEAD
	for _, p := range []string{"sources", "stories?source=local0", "story?source=local0&key=x", "chapter", "cover", "voices", "tts?text=a", "search?q=a", "nope"} {
		wantStatus(t, f.lan("/api/"+p), 401)
		wantStatus(t, f.lan("/api/"+p, method("HEAD")), 401)
	}

	// no key available at all: remote peers are refused, even with an empty key
	f2 := newFixture(t, func(o *Options) { o.AccessKey = func() string { return "" } })
	wantStatus(t, f2.lan("/api/ping"), 401)
	wantStatus(t, f2.lan("/api/ping?k="), 401)
	wantStatus(t, f2.lan("/api/ping", header(KeyHeader, "")), 401)
	wantStatus(t, f2.do("/api/ping"), 200)

	// behind a local reverse proxy loopback is not trusted either
	f3 := newFixture(t, func(o *Options) { o.DistrustLoopback = true })
	wantStatus(t, f3.do("/api/ping"), 401)
	wantStatus(t, f3.do("/api/ping", header(KeyHeader, testKey)), 200)

	// the key never reaches the log
	f.lan("/api/ping?k=" + testKey + "&x=1")
	if got := MaskKey("/api/tts?text=a&k=" + testKey + "&rate=1"); got != "/api/tts?text=a&k=***&rate=1" {
		t.Fatalf("MaskKey: %s", got)
	}
	if got := MaskKey("/?k=" + testKey); got != "/?k=***" {
		t.Fatalf("MaskKey: %s", got)
	}
	// an encoded parameter name is accepted by lastQuery, so it must be masked too
	for in, want := range map[string]string{
		"/api/ping?%6b=" + testKey:                "/api/ping?%6b=***",
		"/api/ping?k=bad&%6B=" + testKey + "&x=1": "/api/ping?k=***&%6B=***&x=1",
		"/api/ping?kk=1&x=k=2":                    "/api/ping?kk=1&x=k=2",
		"/plain":                                  "/plain",
	} {
		if got := MaskKey(in); got != want {
			t.Fatalf("MaskKey(%q) = %q, want %q", in, got, want)
		}
	}
	f.lan("/api/ping?%6b=" + testKey)
	for _, l := range *f.logs {
		if strings.Contains(l, testKey) {
			t.Fatalf("key in log: %s", l)
		}
	}
}

func TestHostCheck(t *testing.T) {
	f := newFixture(t, nil)
	hn, _ := os.Hostname()
	ok := []string{"127.0.0.1:8765", "localhost:8765", "LOCALHOST", "localhost.:80", "[::1]:8765", "192.168.1.10:8765", "10.0.0.5",
		"reader.example", "Reader.Example:8765", ""}
	if hn != "" {
		ok = append(ok, hn, strings.ToUpper(hn)+":8765", hn+".local:8765")
	}
	for _, h := range ok {
		if w := f.do("/api/ping", host(h)); w.Code != 200 {
			t.Errorf("Host %q: status %d, want 200", h, w.Code)
		}
	}
	for _, h := range []string{"evil.example", "evil.example:8765", "127.0.0.1.evil.example", "localhost.evil.example:8765", "reader.example.evil", "[", ":8765"} {
		if w := f.do("/api/ping", host(h)); w.Code != 403 {
			t.Errorf("Host %q: status %d, want 403", h, w.Code)
		} else if decode(t, w)["code"] != "bad_host" {
			t.Errorf("Host %q: wrong body", h)
		}
		if w := f.do("/", host(h)); w.Code != 403 {
			t.Errorf("static, Host %q: status %d, want 403", h, w.Code)
		}
	}
}

func TestCORSAndPreflight(t *testing.T) {
	f := newFixture(t, nil)
	allowed := []string{"https://localhost", "http://localhost", "capacitor://localhost", "tauri://localhost",
		"http://localhost:4321", "http://127.0.0.1:8765", "http://127.0.0.1"}
	denied := []string{"https://evil.example", "http://localhost.evil.example", "http://localhost:4321.evil.example", "null",
		"https://127.0.0.1:8765", "http://192.168.1.10:8765", "http://localhost:123456", "file://"}
	for _, o := range allowed {
		w := f.do("/api/ping", header("Origin", o))
		if w.Code != 200 || w.Header().Get("Access-Control-Allow-Origin") != o || !strings.Contains(strings.Join(w.Header().Values("Vary"), ","), "Origin") {
			t.Errorf("origin %q: %d %v", o, w.Code, w.Header())
		}
		p := f.do("/api/tts", method("OPTIONS"), header("Origin", o), header("Access-Control-Request-Private-Network", "true"))
		h := p.Header()
		if p.Code != 204 || h.Get("Access-Control-Allow-Origin") != o || h.Get("Access-Control-Allow-Methods") != "GET, HEAD, OPTIONS" ||
			h.Get("Access-Control-Allow-Headers") != "X-MythLab-Key, Content-Type, Range, Authorization" || h.Get("Access-Control-Max-Age") != "600" ||
			h.Get("Access-Control-Allow-Private-Network") != "true" || h.Get("Content-Length") != "0" || p.Body.Len() != 0 {
			t.Errorf("preflight %q: %d %v", o, p.Code, h)
		}
	}
	for _, o := range denied {
		w := f.do("/api/ping", header("Origin", o))
		if w.Header().Get("Access-Control-Allow-Origin") != "" {
			t.Errorf("origin %q must not get CORS headers", o)
		}
		if p := f.do("/api/ping", method("OPTIONS"), header("Origin", o)); p.Code != 403 || p.Header().Get("Access-Control-Allow-Origin") != "" {
			t.Errorf("preflight %q: %d", o, p.Code)
		}
	}
	if p := f.do("/api/ping", method("OPTIONS"), header("Origin", "http://localhost")); p.Header().Get("Access-Control-Allow-Private-Network") != "" {
		t.Error("private-network header only on request")
	}
	wantStatus(t, f.do("/index.html", method("OPTIONS"), header("Origin", "http://localhost")), 403)
	// a preflight needs no key (browsers never send credentials with it); the real call does
	wantStatus(t, f.lan("/api/ping", method("OPTIONS"), header("Origin", "https://localhost")), 204)
	w := f.lan("/api/ping", header("Origin", "https://localhost"))
	if w.Code != 401 || w.Header().Get("Access-Control-Allow-Origin") != "https://localhost" {
		t.Errorf("401 must stay readable for the app: %d %v", w.Code, w.Header())
	}

	// other sites cannot use a local browser as a proxy
	cross := header("Sec-Fetch-Site", "cross-site")
	wantError(t, f.do("/api/tts?text=a", cross, header("Referer", "https://evil.example/page")), 403, "cross_site")
	wantError(t, f.do("/api/sources", cross, header("Origin", "https://evil.example")), 403, "cross_site")
	wantError(t, f.do("/api/sources", cross), 403, "cross_site")
	wantStatus(t, f.do("/api/ping", cross, header("Origin", "http://localhost:4321")), 200)
	wantStatus(t, f.do("/api/ping", cross, header("Referer", "capacitor://localhost/index.html")), 200)
	wantStatus(t, f.do("/api/ping", cross, header(KeyHeader, testKey), header("Origin", "https://app.example")), 200)
	wantStatus(t, f.do("/api/ping", header("Sec-Fetch-Site", "same-origin")), 200)
	wantStatus(t, f.do("/api/ping", header("Sec-Fetch-Site", "none")), 200)

	// methods
	for _, m := range []string{"POST", "PUT", "DELETE", "PATCH"} {
		w := f.do("/api/ping", method(m))
		if w.Code != 405 || w.Header().Get("Allow") != "GET, HEAD, OPTIONS" || decode(t, w)["code"] != "method_not_allowed" {
			t.Errorf("%s: %d", m, w.Code)
		}
		wantStatus(t, f.do("/", method(m)), 405)
	}
}

func TestStatic(t *testing.T) {
	f := newFixture(t, nil)
	w := f.do("/")
	if w.Code != 200 || !strings.Contains(w.Body.String(), "MythLab") || w.Header().Get("Cache-Control") != "no-cache" ||
		w.Header().Get("Content-Type") != "text/html; charset=utf-8" || w.Header().Get("X-Content-Type-Options") != "nosniff" {
		t.Fatalf("index: %d %v", w.Code, w.Header())
	}
	csp := w.Header().Get("Content-Security-Policy")
	for _, want := range []string{"default-src 'self'", "script-src 'self'", "frame-ancestors 'none'", "object-src 'none'", "https://api.github.com",
		"script-src 'self' 'wasm-unsafe-eval' https://accounts.google.com/gsi/client", "style-src 'self' https://accounts.google.com/gsi/style",
		"frame-src https://accounts.google.com/gsi/", "connect-src 'self' https://api.github.com https://accounts.google.com/gsi/"} {
		if !strings.Contains(csp, want) {
			t.Fatalf("CSP lacks %q: %s", want, csp)
		}
	}
	if strings.Contains(csp, "'unsafe-eval'") || strings.Contains(csp, "'unsafe-inline'") || w.Header().Get("X-Frame-Options") != "DENY" || w.Header().Get("Referrer-Policy") != "no-referrer" {
		t.Fatalf("headers: %v", w.Header())
	}
	if f.do("/missing").Header().Get("Content-Security-Policy") == "" {
		t.Fatal("404 pages need the CSP too")
	}
	if f.do("/api/ping").Header().Get("Content-Security-Policy") != "" {
		t.Fatal("API responses carry no CSP")
	}
	etag := w.Header().Get("ETag")
	if etag == "" {
		t.Fatal("index needs an ETag")
	}
	wantStatus(t, f.do("/", header("If-None-Match", etag)), 304)
	wantStatus(t, f.do("/index.html?v=3"), 200)
	if w := f.do("/sw.js"); w.Code != 200 || w.Header().Get("Cache-Control") != "no-cache" || !strings.HasPrefix(w.Header().Get("Content-Type"), "text/javascript") {
		t.Fatalf("sw.js: %v", w.Header())
	}
	if w := f.do("/_astro/app.abc123.js"); w.Header().Get("Cache-Control") != "public, max-age=31536000, immutable" {
		t.Fatalf("hashed asset: %v", w.Header())
	}
	if w := f.do("/app.js", header("Accept-Encoding", "gzip, br")); w.Header().Get("Content-Encoding") != "gzip" || w.Body.Len() > 500 {
		t.Fatalf("app.js must be compressed: %v %d", w.Header(), w.Body.Len())
	}
	if w := f.do("/app.js"); w.Header().Get("Content-Encoding") != "" || w.Body.Len() != 2400 {
		t.Fatalf("app.js uncompressed: %d", w.Body.Len())
	}
	if w := f.do("/app.js", method("HEAD")); w.Code != 200 || w.Body.Len() != 0 || w.Header().Get("Content-Length") != "2400" {
		t.Fatalf("HEAD: %d %d %v", w.Code, w.Body.Len(), w.Header())
	}
	if w := f.do("/icons/icon.png", header("Range", "bytes=0-3")); w.Code != 206 || w.Body.String() != "\x89PNG" || w.Header().Get("Content-Type") != "image/png" {
		t.Fatalf("range: %d %q", w.Code, w.Body.String())
	}
	if w := f.do("/docs/"); w.Code != 200 || w.Body.String() != "docs" {
		t.Fatalf("/docs/: %d", w.Code)
	}
	if w := f.do("/docs"); w.Code != 200 || w.Body.String() != "docs" {
		t.Fatalf("/docs: %d", w.Code)
	}
	// no listings, no dotfiles, no traversal, no fallback to the shell
	for _, p := range []string{"/icons/", "/icons", "/_astro/", "/.env", "/nope.js", "/a/b/c", "/..%2f..%2fsecret.txt", "/%2e%2e/secret.txt",
		"/icons/..%5c..%5csecret.txt", "/C:/Windows/win.ini", "/icons/%00", "//etc/passwd", "/index.html/"} {
		if w := f.do(p); w.Code != 404 {
			t.Errorf("%s: status %d, want 404 (%q)", p, w.Code, w.Body.String())
		}
	}
	// the shell is public in LAN mode; the right ?k= sets the cookie, a wrong one does not
	w = f.lan("/?k=" + testKey)
	if c := w.Header().Get("Set-Cookie"); w.Code != 303 || c != KeyCookie+"="+testKey+"; Path=/; Max-Age=31536000; SameSite=Strict; HttpOnly" {
		t.Fatalf("cookie: %d %q", w.Code, c)
	}
	// ... and the redirect drops the key (and only the key) from the address
	if loc := w.Header().Get("Location"); loc != "/" {
		t.Fatalf("redirect target %q, want /", loc)
	}
	if w := f.lan("/docs?x=1&k=" + testKey + "&y=2"); w.Header().Get("Location") != "/docs?x=1&y=2" {
		t.Fatalf("redirect keeps other params: %q", w.Header().Get("Location"))
	}
	if w := f.lan("/?k=wrong"); w.Code != 200 || w.Header().Get("Set-Cookie") != "" {
		t.Fatalf("wrong key must not set a cookie")
	}
	if w := f.lan("/"); w.Code != 200 || w.Header().Get("Set-Cookie") != "" {
		t.Fatal("shell must be reachable without a key")
	}

	// a real directory on disk behaves the same
	dir := t.TempDir()
	writeFile(t, filepath.Join(dir, "index.html"), "disk")
	writeFile(t, filepath.Join(dir, "css", "a.css"), "body{}")
	writeFile(t, filepath.Join(filepath.Dir(dir), "outside.txt"), "outside")
	fd := newFixture(t, func(o *Options) { o.Static = os.DirFS(dir) })
	if w := fd.do("/"); w.Body.String() != "disk" || w.Header().Get("ETag") == "" {
		t.Fatalf("disk index: %q", w.Body.String())
	}
	if w := fd.do("/css/a.css"); w.Code != 200 || !strings.HasPrefix(w.Header().Get("Content-Type"), "text/css") {
		t.Fatalf("css: %d", w.Code)
	}
	for _, p := range []string{"/css/", "/css", "/../outside.txt", "/css/../../outside.txt", "/..%5coutside.txt", "/nul", "/con"} {
		if w := fd.do(p); w.Code != 404 {
			t.Errorf("disk %s: status %d, want 404", p, w.Code)
		}
	}
	// no UI at all
	fn := newFixture(t, func(o *Options) { o.Static = nil })
	wantStatus(t, fn.do("/"), 404)
	wantStatus(t, fn.do("/api/ping"), 200)
}

// The Piper voice models are the app's mirror download source: raw bytes, long cache, resumable ranges.
func TestPiperModelMirror(t *testing.T) {
	f := newFixture(t, nil)
	w := f.do("/tts/models/vi_VN-x.onnx")
	if w.Code != 200 || w.Body.String() != "0123456789abcdefghij" || w.Header().Get("Content-Type") != "application/octet-stream" ||
		w.Header().Get("Cache-Control") != "public, max-age=31536000" || w.Header().Get("Content-Encoding") != "" || w.Header().Get("Accept-Ranges") != "bytes" {
		t.Fatalf("model: %d %v", w.Code, w.Header())
	}
	w = f.do("/tts/models/vi_VN-x.onnx", header("Range", "bytes=5-9"))
	if w.Code != 206 || w.Body.String() != "56789" || w.Header().Get("Content-Range") != "bytes 5-9/20" {
		t.Fatalf("range: %d %q %v", w.Code, w.Body.String(), w.Header())
	}
	if w := f.do("/tts/models/vi_VN-x.onnx.json"); w.Code != 200 || w.Header().Get("Content-Type") != "application/json" {
		t.Fatalf("config: %d %v", w.Code, w.Header())
	}
	if w := f.do("/tts/models/none.onnx"); w.Code != 404 {
		t.Fatalf("missing model: %d", w.Code)
	}
}
