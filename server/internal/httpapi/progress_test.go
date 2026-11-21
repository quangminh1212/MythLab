package httpapi

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"

	"mythlab/internal/progress"
)

func withProgress(o *Options) { o.Progress = progress.Open("", nil) }

func (f *fixture) put(target, body string, opts ...reqOpt) *httptest.ResponseRecorder {
	r := httptest.NewRequest(http.MethodPut, target, strings.NewReader(body))
	r.RemoteAddr, r.Host = "127.0.0.1:51234", "127.0.0.1:8765"
	r.Header.Set("Content-Type", "application/json")
	for _, o := range opts {
		o(r)
	}
	w := httptest.NewRecorder()
	f.s.ServeHTTP(w, r)
	return w
}

func TestProgressRoute(t *testing.T) {
	f := newFixture(t, withProgress)
	if got := f.do("/api/ping").Body.String(); got != `{"ok":true,"app":"mythlab","api":2,"server":"go","features":["progress"]}` {
		t.Fatalf("ping: %s", got)
	}
	now := f.s.o.Progress.Now()
	w := f.put("/api/progress", fmt.Sprintf(`{"entries":[{"source":"local0","key":"a","ts":%d,"idx":2,"maxIdx":4,"genres":[]}]}`, now))
	wantStatus(t, w, 200)
	out := decode(t, w)
	if es, _ := out["entries"].([]any); len(es) != 1 || out["now"] == nil {
		t.Fatalf("put: %v", out)
	}
	g := decode(t, f.do("/api/progress?since=0"))
	if es, _ := g["entries"].([]any); len(es) != 1 {
		t.Fatalf("get: %v", g)
	}
	wantStatus(t, f.do("/api/progress?since=abc"), 400)
	wantStatus(t, f.put("/api/progress", `{bad`), 400)
	wantStatus(t, f.put("/api/progress", `{"entries":[`+strings.Repeat(`{"source":"s","key":"k","ts":1},`, 200)+`{"source":"s","key":"k","ts":1}]}`), 413)
	wantStatus(t, f.put("/api/progress", `{"entries":[{"source":"s","key":"`+strings.Repeat("x", 300<<10)+`","ts":1}]}`), 413)
	wantStatus(t, f.put("/api/stories", `{}`), 405)
	wantStatus(t, f.do("/api/progress", method("POST")), 405)

	// key and cross-site rules apply to PUT as well
	wantStatus(t, f.put("/api/progress", `{"entries":[]}`, from("192.168.1.50:50000"), host("192.168.1.10:8765")), 401)
	wantStatus(t, f.put("/api/progress", `{"entries":[]}`, header("Sec-Fetch-Site", "cross-site"), header("Origin", "https://evil.example")), 403)
	wantStatus(t, f.put("/api/progress", `{"entries":[]}`, header("Sec-Fetch-Site", "cross-site"), header("Origin", "capacitor://localhost")), 200)

	p := f.do("/api/progress", method("OPTIONS"), header("Origin", "capacitor://localhost"))
	if p.Code != 204 || p.Header().Get("Access-Control-Allow-Methods") != "GET, HEAD, PUT, OPTIONS" {
		t.Fatalf("preflight: %d %v", p.Code, p.Header())
	}
}

func TestProgressDisabled(t *testing.T) {
	f := newFixture(t, nil)
	wantStatus(t, f.do("/api/progress"), 404)
	wantStatus(t, f.put("/api/progress", `{}`), 404)
}

func TestProgressConcurrentPut(t *testing.T) {
	f := newFixture(t, withProgress)
	now := f.s.o.Progress.Now()
	var wg sync.WaitGroup
	for i := 0; i < 16; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			body := fmt.Sprintf(`{"entries":[{"source":"local0","key":"same","ts":%d,"idx":%d,"maxIdx":%d},{"source":"local0","key":"k%d","ts":%d}]}`, now+int64(i), i, i, i, now)
			if w := f.put("/api/progress", body); w.Code != 200 {
				t.Errorf("put %d: %d", i, w.Code)
			}
			f.do("/api/progress?since=0")
		}(i)
	}
	wg.Wait()
	for _, e := range f.s.o.Progress.Since(0) {
		if e.Key == "same" && e.Idx != 15 {
			t.Fatalf("last writer: %+v", e)
		}
	}
}

func TestProgressPreflightForeignOrigin(t *testing.T) {
	f := newFixture(t, withProgress)
	p := f.do("/api/progress", method("OPTIONS"), header("Origin", "https://evil.example"), header("Access-Control-Request-Method", "PUT"))
	if p.Code != 403 || p.Header().Get("Access-Control-Allow-Origin") != "" {
		t.Fatalf("foreign preflight: %d %v", p.Code, p.Header())
	}
	p = f.do("/api/stories", method("OPTIONS"), header("Origin", "capacitor://localhost"))
	if m := p.Header().Get("Access-Control-Allow-Methods"); strings.Contains(m, "PUT") {
		t.Fatalf("PUT advertised on a read-only route: %s", m)
	}
}
