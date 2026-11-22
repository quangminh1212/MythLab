package httpapi

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"mythlab/internal/auth"
	"mythlab/internal/progress"
	"mythlab/internal/userlib"
)

// fakeGoogle accepts credentials "good|<sub>|<email>" (the cryptographic
// checks have their own tests in package auth).
type fakeGoogle struct{}

func (fakeGoogle) Verify(_ context.Context, tok string) (*auth.Claims, error) {
	p := strings.Split(tok, "|")
	switch {
	case len(p) == 3 && p[0] == "good":
		return &auth.Claims{Sub: p[1], Email: p[2], EmailVerified: true, Name: "N " + p[1], Picture: "https://p/" + p[1]}, nil
	case tok == "down":
		return nil, fmt.Errorf("%w: offline", auth.ErrUnavailable)
	}
	return nil, fmt.Errorf("%w: nope", auth.ErrBadToken)
}

func withAuth(allowed ...string) func(*Options) {
	return func(o *Options) {
		o.Progress = progress.Open("", nil)
		o.Auth = auth.NewService([]string{"cid-1", "cid-2"}, fakeGoogle{}, auth.OpenSessions("", nil, nil), allowed)
		o.Users = userlib.NewManager("", nil)
	}
}

func bearer(tok string) reqOpt { return header("Authorization", "Bearer "+tok) }

func (f *fixture) post(target, body string, opts ...reqOpt) *httptest.ResponseRecorder {
	r := httptest.NewRequest(http.MethodPost, target, strings.NewReader(body))
	r.RemoteAddr, r.Host = "127.0.0.1:51234", "127.0.0.1:8765"
	r.Header.Set("Content-Type", "application/json")
	for _, o := range opts {
		o(r)
	}
	w := httptest.NewRecorder()
	f.s.ServeHTTP(w, r)
	return w
}

func (f *fixture) login(t *testing.T, sub string) string {
	t.Helper()
	w := f.post("/api/auth/google", fmt.Sprintf(`{"credential":"good|%s|%s@example.com"}`, sub, sub))
	wantStatus(t, w, 200)
	tok, _ := decode(t, w)["token"].(string)
	if tok == "" {
		t.Fatal("no token")
	}
	return tok
}

func TestPingAuth(t *testing.T) {
	f := newFixture(t, withAuth())
	if got := f.do("/api/ping").Body.String(); got != `{"ok":true,"app":"mythlab","api":2,"server":"go","features":["progress","auth","library"],"auth":{"google":true,"client_id":"cid-1"}}` {
		t.Fatalf("ping: %s", got)
	}
	// without Google configured the ping is unchanged
	g := newFixture(t, withProgress)
	if got := g.do("/api/ping").Body.String(); strings.Contains(got, "auth") {
		t.Fatalf("ping leaks auth: %s", got)
	}
}

func TestAuthDisabled(t *testing.T) {
	f := newFixture(t, withProgress)
	wantStatus(t, f.post("/api/auth/google", `{"credential":"good|a|a@x.y"}`), 404)
	wantStatus(t, f.do("/api/auth/me"), 404)
	wantStatus(t, f.post("/api/auth/logout", ``), 404)
	wantStatus(t, f.do("/api/library"), 404)
}

func TestLoginFlow(t *testing.T) {
	f := newFixture(t, withAuth())
	w := f.post("/api/auth/google", `{"credential":"good|sub-1|me@example.com"}`)
	wantStatus(t, w, 200)
	body := decode(t, w)
	tok := body["token"].(string)
	user := body["user"].(map[string]any)
	if len(tok) != 43 || user["id"] != "sub-1" || user["email"] != "me@example.com" || user["name"] != "N sub-1" || user["picture"] == "" {
		t.Fatalf("login: %v", body)
	}
	if exp := int64(body["expires"].(float64)); exp < time.Now().Add(89*24*time.Hour).UnixMilli() {
		t.Fatalf("expires %d", exp)
	}
	if w.Header().Get("Cache-Control") != "no-store" {
		t.Fatal("login response must not be cached")
	}

	me := f.do("/api/auth/me", bearer(tok))
	wantStatus(t, me, 200)
	if decode(t, me)["user"].(map[string]any)["id"] != "sub-1" {
		t.Fatalf("me: %s", me.Body.String())
	}
	wantError(t, f.do("/api/auth/me"), 401, "unauthorized")
	wantError(t, f.do("/api/auth/me", bearer("x"+tok)), 401, "bad_token")

	// bad requests
	wantError(t, f.post("/api/auth/google", `{"credential":"forged"}`), 401, "bad_token")
	wantError(t, f.post("/api/auth/google", `{}`), 401, "bad_token")
	wantError(t, f.post("/api/auth/google", `{bad`), 400, "bad_body")
	wantError(t, f.post("/api/auth/google", `{"credential":"`+strings.Repeat("a", 20<<10)+`"}`), 413, "too_large")
	wantError(t, f.post("/api/auth/google", `{"credential":"down"}`), 502, "upstream")
	wantStatus(t, f.do("/api/auth/google"), 405)

	// logout revokes only that session
	tok2 := f.login(t, "sub-1")
	out := f.post("/api/auth/logout", ``, bearer(tok))
	wantStatus(t, out, 204)
	wantError(t, f.do("/api/auth/me", bearer(tok)), 401, "bad_token")
	wantStatus(t, f.do("/api/auth/me", bearer(tok2)), 200)
	wantError(t, f.post("/api/auth/logout", ``), 401, "unauthorized")
	wantError(t, f.post("/api/auth/logout", ``, bearer(tok)), 401, "bad_token")
	wantStatus(t, f.do("/api/auth/logout", bearer(tok2)), 405)
}

func TestLoginAllowedEmails(t *testing.T) {
	f := newFixture(t, withAuth("Me@Example.com"))
	wantError(t, f.post("/api/auth/google", `{"credential":"good|s|stranger@example.com"}`), 403, "not_allowed")
	wantStatus(t, f.post("/api/auth/google", `{"credential":"good|s|me@example.com"}`), 200)
}

func TestLoginNeedsNoKey(t *testing.T) {
	f := newFixture(t, with(withAuth(), func(o *Options) { o.AccessKey = func() string { return "sekret" } }))
	lan := []reqOpt{from("192.168.1.50:50000"), host("192.168.1.10:8765")}
	wantStatus(t, f.post("/api/auth/google", `{"credential":"good|s|a@x.y"}`, lan...), 200)
	wantStatus(t, f.lan("/api/sources"), 401)
}

func TestLoginRateLimit(t *testing.T) {
	f := newFixture(t, withAuth())
	for i := 0; i < loginsPerMin; i++ {
		wantStatus(t, f.post("/api/auth/google", `{"credential":"bad"}`), 401)
	}
	w := f.post("/api/auth/google", `{"credential":"good|s|a@x.y"}`)
	wantError(t, w, 429, "rate_limited")
	// another client is unaffected
	wantStatus(t, f.post("/api/auth/google", `{"credential":"good|s|a@x.y"}`, from("127.0.0.1:1"), header("X-Forwarded-For", "203.0.113.7")), 200)

	var l rateLimiter
	t0 := time.Now()
	for i := 0; i < loginsPerMin; i++ {
		if !l.allow("ip", t0) {
			t.Fatal("blocked early")
		}
	}
	if l.allow("ip", t0.Add(time.Second)) || !l.allow("ip", t0.Add(61*time.Second)) {
		t.Fatal("window")
	}
}

func TestBearerAuthorizesOnlyUserRoutes(t *testing.T) {
	f := newFixture(t, with(withAuth(), func(o *Options) { o.AccessKey = func() string { return "sekret" } }))
	tok := f.login(t, "u1")
	lan := func(extra ...reqOpt) []reqOpt {
		return append([]reqOpt{from("192.168.1.50:50000"), host("192.168.1.10:8765"), bearer(tok)}, extra...)
	}
	// no key, valid bearer: story content stays closed
	for _, p := range []string{"/api/sources", "/api/stories", "/api/story?source=local0&key=x", "/api/chapter?source=local0&key=x&n=1",
		"/api/cover?source=local0&key=x", "/api/search?q=a", "/api/voices", "/api/tts?text=a", "/api/ping"} {
		wantError(t, f.do(p, lan()...), 401, "unauthorized")
	}
	// ...while the user's own data is open
	wantStatus(t, f.do("/api/progress", lan()...), 200)
	wantStatus(t, f.do("/api/library", lan()...), 200)
	wantStatus(t, f.do("/api/auth/me", lan()...), 200)
	// without a bearer (or a key) the user routes are closed
	wantStatus(t, f.lan("/api/progress"), 401)
	wantError(t, f.lan("/api/library"), 401, "unauthorized")
	// a cross-site origin that is not allow-listed cannot use a stolen-token-less request, but a token holder passes
	wantStatus(t, f.do("/api/library", bearer(tok), header("Sec-Fetch-Site", "cross-site"), header("Origin", "https://evil.example")), 200)
	wantStatus(t, f.do("/api/library", header("Sec-Fetch-Site", "cross-site"), header("Origin", "https://evil.example")), 403)
	// with the key AND a bearer, content works as before
	wantStatus(t, f.do("/api/sources", append(lan(), header("X-MythLab-Key", "sekret"))...), 200)
	// loopback without a token: story content is open as before
	wantStatus(t, f.do("/api/sources"), 200)
}

func TestLibraryRequiresSession(t *testing.T) {
	f := newFixture(t, withAuth())
	wantError(t, f.do("/api/library"), 401, "unauthorized")
	wantError(t, f.put("/api/library", `{"entries":[]}`), 401, "unauthorized")
	wantError(t, f.do("/api/library", bearer("garbage-token-garbage-token-garbage")), 401, "bad_token")
}

func TestLibraryRoundTrip(t *testing.T) {
	f := newFixture(t, withAuth())
	tok := f.login(t, "u1")
	now := time.Now().UnixMilli()
	put := fmt.Sprintf(`{"entries":[
		{"kind":"follow","id":"local0|a","ts":%d,"data":{"source":"local0","key":"a","name":"A"}},
		{"kind":"bookmark","id":"bm-1","ts":%d,"data":{"id":"bm-1","note":"x"}},
		{"kind":"bookmark","id":"bm-2","ts":%d,"deleted":true,"data":{"ignored":1}},
		{"kind":"nope","id":"z","ts":1,"data":{}}]}`, now, now, now)
	w := f.put("/api/library", put, bearer(tok))
	wantStatus(t, w, 200)
	out := decode(t, w)
	es := out["entries"].([]any)
	if len(es) != 3 || out["now"] == nil {
		t.Fatalf("put: %v", out)
	}
	for _, e := range es {
		m := e.(map[string]any)
		if m["at"] == nil || m["at"].(float64) == 0 {
			t.Fatalf("server stamp missing: %v", m)
		}
		if m["deleted"] == true && m["data"] != nil {
			t.Fatalf("tombstone kept data: %v", m)
		}
	}
	g := decode(t, f.do("/api/library?since=0", bearer(tok)))
	if len(g["entries"].([]any)) != 3 {
		t.Fatalf("get: %v", g)
	}
	// since cursor
	next := int64(out["now"].(float64))
	if g := decode(t, f.do(fmt.Sprintf("/api/library?since=%d", next+1000), bearer(tok))); len(g["entries"].([]any)) != 0 {
		t.Fatalf("since: %v", g)
	}
	// last-writer-wins: an older edit is ignored
	w = f.put("/api/library", fmt.Sprintf(`{"entries":[{"kind":"follow","id":"local0|a","ts":%d,"data":{"name":"OLD"}}]}`, now-5000), bearer(tok))
	wantStatus(t, w, 200)
	if got := decode(t, w)["entries"].([]any)[0].(map[string]any)["data"].(map[string]any)["name"]; got != "A" {
		t.Fatalf("older write won: %v", got)
	}
	// limits and errors
	wantStatus(t, f.do("/api/library?since=abc", bearer(tok)), 400)
	wantStatus(t, f.put("/api/library", `{bad`, bearer(tok)), 400)
	wantStatus(t, f.put("/api/library", `{"entries":[`+strings.Repeat(`{"kind":"follow","id":"k","ts":1,"data":{}},`, 200)+`{"kind":"follow","id":"k","ts":1,"data":{}}]}`, bearer(tok)), 413)
	wantStatus(t, f.put("/api/library", `{"entries":[{"kind":"follow","id":"`+strings.Repeat("x", 300<<10)+`","ts":1}]}`, bearer(tok)), 413)
	wantStatus(t, f.do("/api/library", method("POST"), bearer(tok)), 405)
}

func TestPerUserIsolation(t *testing.T) {
	f := newFixture(t, withAuth())
	alice, bob := f.login(t, "alice"), f.login(t, "bob")
	now := time.Now().UnixMilli()
	entry := fmt.Sprintf(`{"entries":[{"source":"local0","key":"k","ts":%d,"idx":4,"maxIdx":4,"genres":[]}]}`, now)
	wantStatus(t, f.put("/api/progress", entry, bearer(alice)), 200)
	wantStatus(t, f.put("/api/library", fmt.Sprintf(`{"entries":[{"kind":"follow","id":"local0|k","ts":%d,"data":{}}]}`, now), bearer(alice)), 200)

	count := func(target string, opts ...reqOpt) int {
		return len(decode(t, f.do(target, opts...))["entries"].([]any))
	}
	if count("/api/progress", bearer(alice)) != 1 || count("/api/library", bearer(alice)) != 1 {
		t.Fatal("alice lost her data")
	}
	if count("/api/progress", bearer(bob)) != 0 || count("/api/library", bearer(bob)) != 0 {
		t.Fatal("bob sees alice's data")
	}
	// the global store is untouched by user writes and still serves the keyless/global mode
	if count("/api/progress") != 0 {
		t.Fatal("user progress leaked into the global store")
	}
	wantStatus(t, f.put("/api/progress", entry), 200)
	if count("/api/progress") != 1 || count("/api/progress", bearer(bob)) != 0 {
		t.Fatal("global progress must stay separate")
	}
	// a second device of alice shares her data
	alice2 := f.login(t, "alice")
	if count("/api/progress", bearer(alice2)) != 1 {
		t.Fatal("second device does not see the account's progress")
	}
	// a revoked/unknown token never falls back to the global store
	wantError(t, f.do("/api/progress", bearer("unknown-token-unknown-token-unknown")), 401, "bad_token")
}

func TestAuthCORS(t *testing.T) {
	f := newFixture(t, withAuth())
	o := header("Origin", "capacitor://localhost")
	for path, methods := range map[string]string{
		"/api/auth/google": "POST, OPTIONS",
		"/api/auth/logout": "POST, OPTIONS",
		"/api/auth/me":     "GET, HEAD, OPTIONS",
		"/api/library":     "GET, HEAD, PUT, OPTIONS",
		"/api/progress":    "GET, HEAD, PUT, OPTIONS",
		"/api/story":       "GET, HEAD, OPTIONS",
	} {
		p := f.do(path, method("OPTIONS"), o, header("Access-Control-Request-Method", "POST"))
		if p.Code != 204 || p.Header().Get("Access-Control-Allow-Methods") != methods {
			t.Errorf("%s preflight: %d %q", path, p.Code, p.Header().Get("Access-Control-Allow-Methods"))
		}
		if !strings.Contains(p.Header().Get("Access-Control-Allow-Headers"), "Authorization") {
			t.Errorf("%s: Authorization header not allowed: %v", path, p.Header())
		}
	}
	wantStatus(t, f.do("/api/auth/google", method("OPTIONS"), header("Origin", "https://evil.example")), 403)
	// POST elsewhere stays closed
	wantStatus(t, f.post("/api/story", `{}`), 405)
	wantStatus(t, f.post("/api/progress", `{}`), 405)
	wantStatus(t, f.put("/api/auth/me", `{}`), 405)
	// responses to allow-listed origins carry the CORS headers
	w := f.post("/api/auth/google", `{"credential":"good|s|a@x.y"}`, o)
	if w.Code != 200 || w.Header().Get("Access-Control-Allow-Origin") != "capacitor://localhost" {
		t.Fatalf("login CORS: %d %v", w.Code, w.Header())
	}
}

func TestTokenNeverLogged(t *testing.T) {
	var logs strings.Builder
	f := newFixture(t, with(withAuth(), func(o *Options) { o.Logf = func(format string, a ...any) { fmt.Fprintf(&logs, format+"\n", a...) } }))
	tok := f.login(t, "u1")
	f.do("/api/library", bearer(tok))
	f.do("/api/auth/me", bearer(tok))
	f.post("/api/auth/google", `{"credential":"good|u1|u1@example.com"}`)
	if strings.Contains(logs.String(), tok) || strings.Contains(logs.String(), "good|u1") {
		t.Fatalf("secrets in the log:\n%s", logs.String())
	}
}

// with chains option mutators (newFixture takes one).
func with(muts ...func(*Options)) func(*Options) {
	return func(o *Options) {
		for _, m := range muts {
			m(o)
		}
	}
}
