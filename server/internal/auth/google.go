// Package auth verifies Google ID tokens ("Sign in with Google") and keeps the
// server-side sessions that sign-ins turn into. Session tokens are opaque
// random strings; only their SHA-256 hash is stored.
package auth

import (
	"context"
	"crypto"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/big"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

var (
	// ErrBadToken: the ID token is malformed, forged, expired or not meant for this server.
	ErrBadToken = errors.New("auth: bad token")
	// ErrNotAllowed: a valid Google account that the server does not admit.
	ErrNotAllowed = errors.New("auth: account not allowed")
	// ErrUnavailable: Google's signing keys could not be fetched.
	ErrUnavailable = errors.New("auth: signing keys unavailable")
)

// GoogleCertsURL is where Google publishes the keys that sign ID tokens.
const GoogleCertsURL = "https://www.googleapis.com/oauth2/v3/certs"

const (
	clockSkew      = 60 * time.Second
	maxTokenLen    = 8 << 10
	maxJWKSBody    = 1 << 20
	defaultKeyTTL  = time.Hour
	minKeyTTL      = time.Minute
	maxKeyTTL      = 24 * time.Hour
	kidMissRefetch = time.Minute // a token with an unknown kid may refetch at most this often
	failRetry      = 5 * time.Second
)

// Claims are the verified fields of an ID token.
type Claims struct {
	Sub           string
	Email         string
	EmailVerified bool
	Name          string
	Picture       string
	Exp, Iat      int64 // seconds
}

// KeySource looks up the RSA public key of a key id.
type KeySource interface {
	Key(ctx context.Context, kid string) (*rsa.PublicKey, error)
}

// Verifier checks Google ID tokens against the allowed client IDs.
type Verifier struct {
	ids  map[string]bool
	keys KeySource
	now  func() time.Time
}

// NewVerifier builds a verifier. now may be nil (wall clock).
func NewVerifier(clientIDs []string, keys KeySource, now func() time.Time) *Verifier {
	if now == nil {
		now = time.Now
	}
	v := &Verifier{ids: map[string]bool{}, keys: keys, now: now}
	for _, id := range clientIDs {
		if id = strings.TrimSpace(id); id != "" {
			v.ids[id] = true
		}
	}
	return v
}

// flexNum reads a JSON number that may also arrive as a string.
type flexNum int64

func (n *flexNum) UnmarshalJSON(b []byte) error {
	s := strings.Trim(string(b), `"`)
	if s == "null" || s == "" {
		return nil
	}
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return err
	}
	*n = flexNum(f)
	return nil
}

// flexBool reads a JSON bool that may also arrive as "true".
type flexBool bool

func (b *flexBool) UnmarshalJSON(d []byte) error {
	*b = flexBool(strings.Trim(string(d), `"`) == "true")
	return nil
}

// audience is a string or an array of strings.
type audience []string

func (a *audience) UnmarshalJSON(d []byte) error {
	var one string
	if json.Unmarshal(d, &one) == nil {
		*a = audience{one}
		return nil
	}
	var many []string
	if err := json.Unmarshal(d, &many); err != nil {
		return err
	}
	*a = many
	return nil
}

type jwtHeader struct {
	Alg string `json:"alg"`
	Kid string `json:"kid"`
}

type jwtPayload struct {
	Iss           string   `json:"iss"`
	Aud           audience `json:"aud"`
	Sub           string   `json:"sub"`
	Exp           flexNum  `json:"exp"`
	Iat           flexNum  `json:"iat"`
	Nbf           flexNum  `json:"nbf"`
	Email         string   `json:"email"`
	EmailVerified flexBool `json:"email_verified"`
	Name          string   `json:"name"`
	Picture       string   `json:"picture"`
}

func bad(format string, a ...any) error {
	return fmt.Errorf("%w: %s", ErrBadToken, fmt.Sprintf(format, a...))
}

// Verify validates token and returns its claims. Errors wrap ErrBadToken
// (reject the caller) or ErrUnavailable (keys could not be fetched).
func (v *Verifier) Verify(ctx context.Context, token string) (*Claims, error) {
	if token == "" || len(token) > maxTokenLen {
		return nil, bad("size")
	}
	parts := strings.Split(token, ".")
	if len(parts) != 3 {
		return nil, bad("shape")
	}
	var hdr jwtHeader
	if err := decodePart(parts[0], &hdr); err != nil {
		return nil, bad("header")
	}
	if hdr.Alg != "RS256" || hdr.Kid == "" {
		return nil, bad("alg")
	}
	sig, err := base64.RawURLEncoding.DecodeString(parts[2])
	if err != nil || len(sig) == 0 {
		return nil, bad("signature encoding")
	}
	key, err := v.keys.Key(ctx, hdr.Kid)
	if err != nil {
		return nil, err
	}
	sum := sha256.Sum256([]byte(parts[0] + "." + parts[1]))
	if err := rsa.VerifyPKCS1v15(key, crypto.SHA256, sum[:], sig); err != nil {
		return nil, bad("signature")
	}
	var p jwtPayload
	if err := decodePart(parts[1], &p); err != nil {
		return nil, bad("payload")
	}
	if p.Iss != "accounts.google.com" && p.Iss != "https://accounts.google.com" {
		return nil, bad("issuer")
	}
	okAud := false
	for _, a := range p.Aud {
		if v.ids[a] {
			okAud = true
		}
	}
	if !okAud {
		return nil, bad("audience")
	}
	now := v.now()
	if p.Exp == 0 || now.After(time.Unix(int64(p.Exp), 0).Add(clockSkew)) {
		return nil, bad("expired")
	}
	if p.Iat != 0 && time.Unix(int64(p.Iat), 0).After(now.Add(clockSkew)) {
		return nil, bad("issued in the future")
	}
	if p.Nbf != 0 && time.Unix(int64(p.Nbf), 0).After(now.Add(clockSkew)) {
		return nil, bad("not yet valid")
	}
	if p.Sub == "" || len(p.Sub) > 255 {
		return nil, bad("subject")
	}
	if !bool(p.EmailVerified) || p.Email == "" {
		return nil, bad("email not verified")
	}
	return &Claims{Sub: p.Sub, Email: p.Email, EmailVerified: true, Name: p.Name, Picture: p.Picture,
		Exp: int64(p.Exp), Iat: int64(p.Iat)}, nil
}

func decodePart(s string, v any) error {
	b, err := base64.RawURLEncoding.DecodeString(s)
	if err != nil {
		return err
	}
	return json.Unmarshal(b, v)
}

// JWKS fetches and caches a JSON Web Key Set, honouring Cache-Control.
type JWKS struct {
	url    string
	client *http.Client
	now    func() time.Time

	mu        sync.Mutex
	keys      map[string]*rsa.PublicKey
	expires   time.Time
	lastFetch time.Time
}

// NewJWKS builds a key source. url "" means Google's; client nil means a
// client with a 10 s timeout; now nil means the wall clock.
func NewJWKS(url string, client *http.Client, now func() time.Time) *JWKS {
	if url == "" {
		url = GoogleCertsURL
	}
	if client == nil {
		client = &http.Client{Timeout: 10 * time.Second}
	}
	if now == nil {
		now = time.Now
	}
	return &JWKS{url: url, client: client, now: now}
}

// Key implements KeySource.
func (j *JWKS) Key(ctx context.Context, kid string) (*rsa.PublicKey, error) {
	j.mu.Lock()
	defer j.mu.Unlock()
	now := j.now()
	fresh := j.keys != nil && now.Before(j.expires)
	k, have := j.keys[kid]
	if have && fresh {
		return k, nil
	}
	since := now.Sub(j.lastFetch)
	if (!fresh && since >= failRetry) || (fresh && since >= kidMissRefetch) {
		if err := j.fetch(ctx, now); err != nil {
			if have { // stale but usable beats failing
				return k, nil
			}
			return nil, fmt.Errorf("%w: %v", ErrUnavailable, err)
		}
		if k, ok := j.keys[kid]; ok {
			return k, nil
		}
		return nil, bad("unknown key id")
	}
	if have {
		return k, nil
	}
	if !fresh {
		return nil, ErrUnavailable
	}
	return nil, bad("unknown key id")
}

// fetch reloads the key set. Caller holds mu.
func (j *JWKS) fetch(ctx context.Context, now time.Time) error {
	j.lastFetch = now
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, j.url, nil)
	if err != nil {
		return err
	}
	resp, err := j.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	body, err := io.ReadAll(io.LimitReader(resp.Body, maxJWKSBody))
	if err != nil {
		return err
	}
	var set struct {
		Keys []struct {
			Kty string `json:"kty"`
			Kid string `json:"kid"`
			N   string `json:"n"`
			E   string `json:"e"`
		} `json:"keys"`
	}
	if err := json.Unmarshal(body, &set); err != nil {
		return err
	}
	keys := map[string]*rsa.PublicKey{}
	for _, k := range set.Keys {
		if k.Kty != "RSA" || k.Kid == "" {
			continue
		}
		nb, err1 := base64.RawURLEncoding.DecodeString(k.N)
		eb, err2 := base64.RawURLEncoding.DecodeString(k.E)
		if err1 != nil || err2 != nil || len(nb) == 0 || len(eb) == 0 || len(eb) > 4 {
			continue
		}
		e := new(big.Int).SetBytes(eb)
		if !e.IsInt64() || e.Int64() < 3 {
			continue
		}
		keys[k.Kid] = &rsa.PublicKey{N: new(big.Int).SetBytes(nb), E: int(e.Int64())}
	}
	if len(keys) == 0 {
		return errors.New("no usable keys")
	}
	ttl := keyTTL(resp.Header.Get("Cache-Control"))
	j.keys, j.expires = keys, now.Add(ttl)
	return nil
}

// keyTTL reads max-age from a Cache-Control value, bounded to [1 min, 24 h].
func keyTTL(cc string) time.Duration {
	ttl := defaultKeyTTL
	for _, d := range strings.Split(cc, ",") {
		d = strings.TrimSpace(strings.ToLower(d))
		if d == "no-store" || d == "no-cache" {
			ttl = minKeyTTL
		}
		if v, ok := strings.CutPrefix(d, "max-age="); ok {
			if n, err := strconv.Atoi(strings.Trim(v, `"`)); err == nil && n >= 0 {
				ttl = time.Duration(n) * time.Second
			}
		}
	}
	if ttl < minKeyTTL {
		ttl = minKeyTTL
	}
	if ttl > maxKeyTTL {
		ttl = maxKeyTTL
	}
	return ttl
}
