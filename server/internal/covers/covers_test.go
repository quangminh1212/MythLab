package covers

import (
	"bytes"
	"context"
	"errors"
	"image"
	"image/color"
	"image/jpeg"
	"image/png"
	"net/http"
	"net/http/httptest"
	"net/netip"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func TestIsPublicIP(t *testing.T) {
	private := []string{"127.0.0.1", "10.1.2.3", "172.16.0.1", "192.168.1.10", "169.254.169.254", "0.0.0.0", "100.64.0.1",
		"224.0.0.1", "255.255.255.255", "198.18.0.1", "192.0.2.5", "::1", "::", "fe80::1", "fc00::1", "fd12::1", "ff02::1",
		"::ffff:127.0.0.1", "::ffff:10.0.0.1", "64:ff9b::7f00:1", "64:ff9b::a00:1", "2002:7f00:1::1", "2001:db8::1", "2001::1"}
	for _, s := range private {
		if IsPublicIP(netip.MustParseAddr(s)) {
			t.Errorf("%s must not be public", s)
		}
	}
	for _, s := range []string{"8.8.8.8", "1.1.1.1", "140.82.112.3", "2606:4700:4700::1111", "::ffff:8.8.8.8"} {
		if !IsPublicIP(netip.MustParseAddr(s)) {
			t.Errorf("%s must be public", s)
		}
	}
	if IsPublicIP(netip.Addr{}) {
		t.Error("zero address must not be public")
	}
}

func testJPEG(w, h int) []byte {
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			img.Set(x, y, color.RGBA{uint8(x), uint8(y), 90, 255})
		}
	}
	var b bytes.Buffer
	jpeg.Encode(&b, img, nil)
	return b.Bytes()
}

func testPNG(w, h int) []byte {
	img := image.NewNRGBA(image.Rect(0, 0, w, h))
	var b bytes.Buffer
	png.Encode(&b, img)
	return b.Bytes()
}

func TestSniff(t *testing.T) {
	if _, ct := Sniff(testJPEG(4, 4)); ct != "image/jpeg" {
		t.Error("jpeg")
	}
	if _, ct := Sniff(testPNG(4, 4)); ct != "image/png" {
		t.Error("png")
	}
	if _, ct := Sniff([]byte("RIFF\x00\x00\x00\x00WEBPVP8 ")); ct != "image/webp" {
		t.Error("webp")
	}
	if _, ct := Sniff([]byte("GIF89a...")); ct != "image/gif" {
		t.Error("gif")
	}
	for _, bad := range []string{"<svg xmlns='http://www.w3.org/2000/svg'><script>1</script></svg>", "<html>", "", "\xff"} {
		if ext, _ := Sniff([]byte(bad)); ext != "" {
			t.Errorf("%q must not be an image", bad)
		}
	}
}

func TestPosterCache(t *testing.T) {
	var hits atomic.Int64
	jpg := testJPEG(600, 900)
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		hits.Add(1)
		switch r.URL.Path {
		case "/ok.jpg":
			w.Header().Set("Content-Type", "application/octet-stream") // the content decides
			w.Write(jpg)
		case "/redir":
			http.Redirect(w, r, "/ok.jpg", http.StatusFound)
		case "/svg":
			w.Header().Set("Content-Type", "image/svg+xml")
			w.Write([]byte("<svg xmlns='http://www.w3.org/2000/svg'/>"))
		case "/big":
			w.Header().Set("Content-Type", "image/jpeg")
			w.Write(append(append([]byte{}, jpg...), make([]byte, MaxPoster)...))
		case "/empty":
			w.Header().Set("Content-Type", "image/jpeg")
		default:
			http.NotFound(w, r)
		}
	}))
	defer srv.Close()
	dir := t.TempDir()
	s := New(Options{Dir: dir, allowPrivate: true})
	defer s.Close()
	ctx := context.Background()

	p, ct, err := s.Poster(ctx, srv.URL+"/ok.jpg", false)
	if err != nil || ct != "image/jpeg" || filepath.Ext(p) != ".jpg" || filepath.Base(p) != Key(srv.URL+"/ok.jpg")+".jpg" {
		t.Fatalf("poster: %q %q %v", p, ct, err)
	}
	n := hits.Load()
	if _, _, err := s.Poster(ctx, srv.URL+"/ok.jpg", false); err != nil || hits.Load() != n {
		t.Fatal("second call must come from disk")
	}
	if _, _, err := s.Poster(ctx, srv.URL+"/redir", false); err != nil {
		t.Fatalf("redirect: %v", err)
	}
	for _, path := range []string{"/svg", "/big", "/empty", "/404"} {
		if _, _, err := s.Poster(ctx, srv.URL+path, false); !errors.Is(err, ErrNoCover) {
			t.Errorf("%s: want ErrNoCover, got %v", path, err)
		}
		if _, err := os.Stat(filepath.Join(dir, Key(srv.URL+path)+".miss")); err != nil {
			t.Errorf("%s: missing .miss file", path)
		}
	}
	n = hits.Load()
	s.Poster(ctx, srv.URL+"/404", false)
	if hits.Load() != n {
		t.Error("negative cache must prevent a second download")
	}
	s.Poster(ctx, srv.URL+"/404", true)
	if hits.Load() != n+1 {
		t.Error("retry must ignore the negative cache")
	}
	for _, bad := range []string{"", "ftp://x/y.jpg", "file:///etc/passwd", "javascript:alert(1)", "//host/x.jpg"} {
		if _, _, err := s.Poster(ctx, bad, false); !errors.Is(err, ErrNoCover) {
			t.Errorf("%q must be refused", bad)
		}
	}
	entries, _ := os.ReadDir(dir)
	for _, e := range entries {
		if strings.HasSuffix(e.Name(), ".tmp") {
			t.Errorf("leftover temp file %s", e.Name())
		}
	}

	// an old ".img" file is served only when it really is an image
	u1, u2 := "https://example.com/a", "https://example.com/b"
	os.WriteFile(filepath.Join(dir, Key(u1)+".img"), testPNG(3, 3), 0o644)
	os.WriteFile(filepath.Join(dir, Key(u2)+".img"), []byte("<html>not an image</html>"), 0o644)
	if _, ct, ok := s.Lookup(u1); !ok || ct != "image/png" {
		t.Errorf(".img with PNG content: %v %q", ok, ct)
	}
	if _, _, ok := s.Lookup(u2); ok {
		t.Error(".img with HTML content must not be served")
	}
}

func TestSSRFBlocked(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.Write(testJPEG(2, 2)) }))
	defer srv.Close()
	s := New(Options{Dir: t.TempDir()})
	defer s.Close()
	if _, _, err := s.Poster(context.Background(), srv.URL+"/x.jpg", false); !errors.Is(err, ErrNoCover) {
		t.Fatalf("loopback poster must be refused, got %v", err)
	}
	if _, _, err := s.Poster(context.Background(), "http://localhost:"+strings.Split(srv.URL, ":")[2]+"/x.jpg", false); !errors.Is(err, ErrNoCover) {
		t.Fatalf("localhost poster must be refused, got %v", err)
	}
}

func TestPrune(t *testing.T) {
	dir := t.TempDir()
	s := New(Options{Dir: dir})
	now := time.Now()
	put := func(name string, size int, age time.Duration) string {
		p := filepath.Join(dir, name)
		if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(p, make([]byte, size), 0o644); err != nil {
			t.Fatal(err)
		}
		os.Chtimes(p, now.Add(-age), now.Add(-age))
		return p
	}
	stale := put("stale.jpg", 10, 48*time.Hour)
	a := put("r/a.jpg", 100, 5*time.Hour)
	b := put("b.jpg", 100, 4*time.Hour)
	c := put("c.jpg", 100, 3*time.Hour)
	fresh := put("fresh.tmp", 1000, 0)
	s.Prune(250, 24*time.Hour)
	gone := func(p string) bool { _, err := os.Stat(p); return err != nil }
	if !gone(stale) || !gone(a) || gone(b) || gone(c) || gone(fresh) {
		t.Fatalf("prune: stale=%v a=%v b=%v c=%v fresh=%v", gone(stale), gone(a), gone(b), gone(c), gone(fresh))
	}
}

func TestResize(t *testing.T) {
	out, err := Resize(testJPEG(600, 900), 240)
	if err != nil {
		t.Fatal(err)
	}
	cfg, format, err := image.DecodeConfig(bytes.NewReader(out))
	if err != nil || format != "jpeg" || cfg.Width != 240 || cfg.Height != 360 {
		t.Fatalf("resized: %v %s %dx%d", err, format, cfg.Width, cfg.Height)
	}
	if out, err = Resize(testPNG(500, 500), 160); err != nil {
		t.Fatal(err)
	}
	if cfg, _, _ = image.DecodeConfig(bytes.NewReader(out)); cfg.Width != 160 || cfg.Height != 160 {
		t.Fatalf("png resize: %dx%d", cfg.Width, cfg.Height)
	}
	for name, src := range map[string][]byte{"small": testJPEG(100, 150), "garbage": []byte("nope"), "empty": nil} {
		if _, err := Resize(src, 240); !errors.Is(err, ErrNoResize) {
			t.Errorf("%s: want ErrNoResize, got %v", name, err)
		}
	}

	s := New(Options{Dir: t.TempDir()})
	ctx := context.Background()
	loads := 0
	load := func() ([]byte, error) { loads++; return testJPEG(600, 900), nil }
	p1, err := s.Resized(ctx, "tag-1", 320, load)
	if err != nil {
		t.Fatal(err)
	}
	p2, err := s.Resized(ctx, "tag-1", 320, load)
	if err != nil || p1 != p2 || loads != 1 {
		t.Fatalf("resize cache: %v %d", err, loads)
	}
	if _, err := s.Resized(ctx, "tag-1", 333, load); !errors.Is(err, ErrNoResize) {
		t.Error("unlisted width must not be resized")
	}
	small := func() ([]byte, error) { loads++; return testJPEG(100, 100), nil }
	s.Resized(ctx, "tag-small", 320, small)
	n := loads
	if _, err := s.Resized(ctx, "tag-small", 320, small); !errors.Is(err, ErrNoResize) || loads != n {
		t.Error("serve-original decision must be remembered")
	}
}
