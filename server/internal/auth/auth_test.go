package auth

import (
	"context"
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"math/big"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

const testClient = "client-1.apps.googleusercontent.com"

var testNow = time.Unix(1_800_000_000, 0)

func newKey(t *testing.T) *rsa.PrivateKey {
	t.Helper()
	k, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		t.Fatal(err)
	}
	return k
}

func b64(b []byte) string { return base64.RawURLEncoding.EncodeToString(b) }

// sign builds an RS256 JWT with the given header and claims.
func sign(t *testing.T, k *rsa.PrivateKey, kid string, claims map[string]any) string {
	t.Helper()
	hdr, _ := json.Marshal(map[string]any{"alg": "RS256", "typ": "JWT", "kid": kid})
	return signWith(t, k, string(hdr), claims)
}

func signWith(t *testing.T, k *rsa.PrivateKey, header string, claims map[string]any) string {
	t.Helper()
	pl, _ := json.Marshal(claims)
	in := b64([]byte(header)) + "." + b64(pl)
	sum := sha256.Sum256([]byte(in))
	sig, err := rsa.SignPKCS1v15(rand.Reader, k, crypto.SHA256, sum[:])
	if err != nil {
		t.Fatal(err)
	}
	return in + "." + b64(sig)
}

func goodClaims() map[string]any {
	return map[string]any{
		"iss": "https://accounts.google.com", "aud": testClient, "sub": "1234567890",
		"email": "Reader@Example.com", "email_verified": true, "name": "Reader", "picture": "https://p/x.png",
		"iat": testNow.Unix() - 10, "exp": testNow.Unix() + 3600,
	}
}

type staticKeys map[string]*rsa.PublicKey

func (s staticKeys) Key(_ context.Context, kid string) (*rsa.PublicKey, error) {
	if k, ok := s[kid]; ok {
		return k, nil
	}
	return nil, bad("unknown key id")
}

func testVerifier(k *rsa.PrivateKey) *Verifier {
	return NewVerifier([]string{testClient}, staticKeys{"k1": &k.PublicKey}, func() time.Time { return testNow })
}

func TestVerify(t *testing.T) {
	k, other := newKey(t), newKey(t)
	v := testVerifier(k)
	mut := func(f func(m map[string]any)) string {
		c := goodClaims()
		f(c)
		return sign(t, k, "k1", c)
	}
	cases := []struct {
		name  string
		token string
		bad   bool
	}{
		{"valid", mut(func(m map[string]any) {}), false},
		{"issuer without scheme", mut(func(m map[string]any) { m["iss"] = "accounts.google.com" }), false},
		{"aud array", mut(func(m map[string]any) { m["aud"] = []string{"x", testClient} }), false},
		{"email_verified string", mut(func(m map[string]any) { m["email_verified"] = "true" }), false},
		{"expired within skew", mut(func(m map[string]any) { m["exp"] = testNow.Unix() - 30 }), false},
		{"expired", mut(func(m map[string]any) { m["exp"] = testNow.Unix() - 61 }), true},
		{"no exp", mut(func(m map[string]any) { delete(m, "exp") }), true},
		{"iat in skew", mut(func(m map[string]any) { m["iat"] = testNow.Unix() + 30 }), false},
		{"iat in future", mut(func(m map[string]any) { m["iat"] = testNow.Unix() + 120 }), true},
		{"wrong aud", mut(func(m map[string]any) { m["aud"] = "other-client" }), true},
		{"aud array without ours", mut(func(m map[string]any) { m["aud"] = []string{"a", "b"} }), true},
		{"wrong iss", mut(func(m map[string]any) { m["iss"] = "https://evil.example" }), true},
		{"iss lookalike", mut(func(m map[string]any) { m["iss"] = "https://accounts.google.com.evil.example" }), true},
		{"unverified email", mut(func(m map[string]any) { m["email_verified"] = false }), true},
		{"missing email_verified", mut(func(m map[string]any) { delete(m, "email_verified") }), true},
		{"empty sub", mut(func(m map[string]any) { m["sub"] = "" }), true},
		{"missing sub", mut(func(m map[string]any) { delete(m, "sub") }), true},
		{"signed by another key", sign(t, other, "k1", goodClaims()), true},
		{"unknown kid", sign(t, k, "nope", goodClaims()), true},
		{"alg none", b64([]byte(`{"alg":"none","kid":"k1"}`)) + "." + b64([]byte(`{"iss":"accounts.google.com"}`)) + ".", true},
		{"alg HS256", signWith(t, k, `{"alg":"HS256","kid":"k1"}`, goodClaims()), true},
		{"no kid", signWith(t, k, `{"alg":"RS256"}`, goodClaims()), true},
		{"garbage", "not-a-jwt", true},
		{"two parts", "a.b", true},
		{"empty", "", true},
		{"huge", strings.Repeat("a", maxTokenLen+1), true},
	}
	for _, c := range cases {
		cl, err := v.Verify(context.Background(), c.token)
		if c.bad {
			if !errors.Is(err, ErrBadToken) {
				t.Errorf("%s: err %v, want ErrBadToken", c.name, err)
			}
			continue
		}
		if err != nil {
			t.Errorf("%s: %v", c.name, err)
			continue
		}
		if cl.Sub != "1234567890" || cl.Email != "Reader@Example.com" || cl.Name != "Reader" {
			t.Errorf("%s: claims %+v", c.name, cl)
		}
	}
}

func TestVerifyTamperedPayload(t *testing.T) {
	k := newKey(t)
	v := testVerifier(k)
	tok := sign(t, k, "k1", goodClaims())
	parts := strings.Split(tok, ".")
	c := goodClaims()
	c["sub"] = "attacker"
	pl, _ := json.Marshal(c)
	forged := parts[0] + "." + b64(pl) + "." + parts[2]
	if _, err := v.Verify(context.Background(), forged); !errors.Is(err, ErrBadToken) {
		t.Fatalf("forged payload accepted: %v", err)
	}
}

// jwksServer serves the public key of k under kid and counts requests.
func jwksServer(t *testing.T, cacheControl string, keys map[string]*rsa.PublicKey, hits *atomic.Int32) *httptest.Server {
	t.Helper()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		hits.Add(1)
		var list []map[string]string
		for kid, pk := range keys {
			list = append(list, map[string]string{"kty": "RSA", "kid": kid, "alg": "RS256", "use": "sig",
				"n": b64(pk.N.Bytes()), "e": b64(big.NewInt(int64(pk.E)).Bytes())})
		}
		if cacheControl != "" {
			w.Header().Set("Cache-Control", cacheControl)
		}
		json.NewEncoder(w).Encode(map[string]any{"keys": list})
	}))
	t.Cleanup(srv.Close)
	return srv
}

func TestJWKSCacheAndRefetch(t *testing.T) {
	k1, k2 := newKey(t), newKey(t)
	keys := map[string]*rsa.PublicKey{"k1": &k1.PublicKey}
	var hits atomic.Int32
	srv := jwksServer(t, "public, max-age=3600, must-revalidate", keys, &hits)
	now := testNow
	clock := func() time.Time { return now }
	j := NewJWKS(srv.URL, srv.Client(), clock)
	v := NewVerifier([]string{testClient}, j, clock)
	ctx := context.Background()

	long := goodClaims()
	long["exp"] = testNow.Unix() + 24*3600
	tok := sign(t, k1, "k1", long)
	for i := 0; i < 3; i++ {
		if _, err := v.Verify(ctx, tok); err != nil {
			t.Fatal(err)
		}
	}
	if hits.Load() != 1 {
		t.Fatalf("hits %d, want 1 (cached)", hits.Load())
	}

	// a key rotation: unknown kid triggers one refetch, then is throttled
	keys["k2"] = &k2.PublicKey
	tok2 := sign(t, k2, "k2", long)
	if _, err := v.Verify(ctx, tok2); !errors.Is(err, ErrBadToken) {
		t.Fatalf("kid miss inside throttle window must not refetch: %v", err)
	}
	if hits.Load() != 1 {
		t.Fatalf("throttled refetch happened: %d", hits.Load())
	}
	now = now.Add(2 * time.Minute)
	if _, err := v.Verify(ctx, tok2); err != nil {
		t.Fatalf("after throttle: %v", err)
	}
	if hits.Load() != 2 {
		t.Fatalf("hits %d, want 2", hits.Load())
	}
	// junk kids cannot hammer the endpoint
	for i := 0; i < 5; i++ {
		v.Verify(ctx, sign(t, k1, "junk", goodClaims()))
	}
	if hits.Load() != 2 {
		t.Fatalf("junk kid refetched: %d", hits.Load())
	}
	// expiry of the cache refetches
	now = now.Add(2 * time.Hour)
	if _, err := v.Verify(ctx, tok); err != nil {
		t.Fatal(err)
	}
	if hits.Load() != 3 {
		t.Fatalf("hits %d, want 3 after max-age", hits.Load())
	}
}

func TestJWKSFailure(t *testing.T) {
	var hits atomic.Int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		hits.Add(1)
		http.Error(w, "boom", 500)
	}))
	defer srv.Close()
	k := newKey(t)
	v := NewVerifier([]string{testClient}, NewJWKS(srv.URL, srv.Client(), func() time.Time { return testNow }), func() time.Time { return testNow })
	_, err := v.Verify(context.Background(), sign(t, k, "k1", goodClaims()))
	if !errors.Is(err, ErrUnavailable) {
		t.Fatalf("err %v, want ErrUnavailable", err)
	}
	// immediate retries do not hit the network again
	v.Verify(context.Background(), sign(t, k, "k1", goodClaims()))
	if hits.Load() != 1 {
		t.Fatalf("hits %d", hits.Load())
	}
}

func TestKeyTTL(t *testing.T) {
	cases := map[string]time.Duration{
		"":                        time.Hour,
		"public, max-age=19000":   19000 * time.Second,
		"max-age=5":               time.Minute,
		"max-age=999999999":       24 * time.Hour,
		"no-store":                time.Minute,
		"max-age=abc":             time.Hour,
		"public, MAX-AGE=7200, x": 2 * time.Hour,
	}
	for in, want := range cases {
		if got := keyTTL(in); got != want {
			t.Errorf("keyTTL(%q) = %v, want %v", in, got, want)
		}
	}
}

func TestSessions(t *testing.T) {
	path := filepath.Join(t.TempDir(), "sub", "users.json")
	now := testNow
	clock := func() time.Time { return now }
	s := OpenSessions(path, nil, clock)
	u := User{ID: "sub-1", Name: "A", Email: "a@x.y"}
	tok, exp, err := s.Create(u)
	if err != nil {
		t.Fatal(err)
	}
	if len(tok) != 43 || exp != now.Add(SessionTTL).UnixMilli() {
		t.Fatalf("token %q exp %d", tok, exp)
	}
	got, ok := s.Lookup(tok)
	if !ok || got != u {
		t.Fatalf("lookup %v %v", got, ok)
	}
	if _, ok := s.Lookup(tok + "x"); ok {
		t.Fatal("wrong token accepted")
	}
	if _, ok := s.Lookup(""); ok {
		t.Fatal("empty token accepted")
	}

	// only the hash is on disk
	raw := readFile(t, path)
	if strings.Contains(raw, tok) || !strings.Contains(raw, hashToken(tok)) {
		t.Fatalf("users.json content: %s", raw)
	}

	// survives a restart
	s2 := OpenSessions(path, nil, clock)
	if _, ok := s2.Lookup(tok); !ok {
		t.Fatal("session lost on reopen")
	}

	// sliding expiry
	now = now.Add(30 * 24 * time.Hour)
	if _, ok := s2.Lookup(tok); !ok {
		t.Fatal("lookup after 30d")
	}
	now = now.Add(80 * 24 * time.Hour) // 110d after creation, 80d after the slide
	if _, ok := s2.Lookup(tok); !ok {
		t.Fatal("sliding expiry did not extend the session")
	}
	// hard expiry
	now = now.Add(91 * 24 * time.Hour)
	if _, ok := s2.Lookup(tok); ok {
		t.Fatal("expired session accepted")
	}
	if s3 := OpenSessions(path, nil, clock); s3.Count("sub-1") != 0 {
		t.Fatal("expired session reloaded")
	}
}

func readFile(t *testing.T, p string) string {
	t.Helper()
	b, err := os.ReadFile(p)
	if err != nil {
		t.Fatal(err)
	}
	return string(b)
}

func TestSessionRevokeAndCap(t *testing.T) {
	now := testNow
	s := OpenSessions("", nil, func() time.Time { now = now.Add(time.Second); return now })
	u := User{ID: "u1"}
	var toks []string
	for i := 0; i < MaxSessionsPerUser+3; i++ {
		tok, _, _ := s.Create(u)
		toks = append(toks, tok)
	}
	if n := s.Count("u1"); n != MaxSessionsPerUser {
		t.Fatalf("sessions %d, want %d", n, MaxSessionsPerUser)
	}
	for _, tok := range toks[:3] {
		if _, ok := s.Lookup(tok); ok {
			t.Fatal("oldest session survived the cap")
		}
	}
	if _, ok := s.Lookup(toks[3]); !ok {
		t.Fatal("recent session dropped")
	}
	other, _, _ := s.Create(User{ID: "u2"})
	if s.Count("u1") != MaxSessionsPerUser || s.Count("u2") != 1 {
		t.Fatal("cap is per user")
	}
	if !s.Revoke(toks[5]) || s.Revoke(toks[5]) {
		t.Fatal("revoke result")
	}
	if _, ok := s.Lookup(toks[5]); ok {
		t.Fatal("revoked session still valid")
	}
	if _, ok := s.Lookup(other); !ok {
		t.Fatal("other user's session affected")
	}
}

func TestServiceLogin(t *testing.T) {
	k := newKey(t)
	v := testVerifier(k)
	sess := OpenSessions("", nil, func() time.Time { return testNow })
	svc := NewService([]string{testClient}, v, sess, []string{" Reader@example.com "})
	if svc.ClientID() != testClient {
		t.Fatal("client id")
	}
	tok, exp, u, err := svc.Login(context.Background(), sign(t, k, "k1", goodClaims()))
	if err != nil || tok == "" || exp == 0 || u.ID != "1234567890" || u.Email != "Reader@Example.com" {
		t.Fatalf("login %v %v %v", u, exp, err)
	}
	c := goodClaims()
	c["email"] = "stranger@example.com"
	if _, _, _, err := svc.Login(context.Background(), sign(t, k, "k1", c)); !errors.Is(err, ErrNotAllowed) {
		t.Fatalf("stranger: %v", err)
	}
	if _, _, _, err := svc.Login(context.Background(), "junk"); !errors.Is(err, ErrBadToken) {
		t.Fatalf("junk: %v", err)
	}
	open := NewService([]string{testClient}, v, sess, nil)
	c["email"] = "anyone@example.com"
	if _, _, _, err := open.Login(context.Background(), sign(t, k, "k1", c)); err != nil {
		t.Fatalf("open service: %v", err)
	}
}
