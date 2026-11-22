package httpapi

import (
	"encoding/json"
	"errors"
	"net"
	"net/http"
	"strings"
	"sync"
	"time"

	"mythlab/internal/auth"
	"mythlab/internal/library"
)

const (
	authGooglePath = "/api/auth/google"
	authMePath     = "/api/auth/me"
	authLogoutPath = "/api/auth/logout"

	maxAuthBody    = 16 << 10
	loginsPerMin   = 20
	maxLimiterKeys = 4096
)

// bearerToken extracts the token of an "Authorization: Bearer" header.
func bearerToken(r *http.Request) string {
	h := strings.TrimSpace(r.Header.Get("Authorization"))
	if len(h) > 7 && strings.EqualFold(h[:7], "bearer ") {
		return strings.TrimSpace(h[7:])
	}
	return ""
}

// sessionUser resolves the Bearer token for the routes a session may use.
// ok is false when a response (401) has already been written: a presented
// token that is unknown or expired is refused, never silently ignored, so the
// client can tell that it has been signed out.
func (s *Server) sessionUser(w http.ResponseWriter, r *http.Request, route string) (*auth.User, bool) {
	if s.o.Auth == nil {
		return nil, true
	}
	switch route {
	case "progress", "library", "auth/me", "auth/logout":
	default:
		return nil, true
	}
	tok := bearerToken(r)
	if tok == "" {
		return nil, true
	}
	u, ok := s.o.Auth.Sessions.Lookup(tok)
	if !ok {
		s.writeErr(w, r, http.StatusUnauthorized, "bad_token", "phiên đăng nhập không hợp lệ hoặc đã hết hạn")
		return nil, false
	}
	return &u, true
}

// apiAuth serves POST /api/auth/google, GET /api/auth/me and POST /api/auth/logout.
func (s *Server) apiAuth(w http.ResponseWriter, r *http.Request, route string, user *auth.User) {
	if s.o.Auth == nil {
		s.writeErr(w, r, http.StatusNotFound, "no_route", "chưa cấu hình đăng nhập Google")
		return
	}
	switch route {
	case "auth/google":
		s.apiLogin(w, r)
	case "auth/me":
		if r.Method != http.MethodGet && r.Method != http.MethodHead {
			w.Header().Set("Allow", "GET, HEAD, OPTIONS")
			s.writeErr(w, r, http.StatusMethodNotAllowed, "method_not_allowed", "chỉ hỗ trợ GET")
			return
		}
		if user == nil {
			s.writeErr(w, r, http.StatusUnauthorized, "unauthorized", "chưa đăng nhập")
			return
		}
		s.writeJSON(w, r, http.StatusOK, map[string]any{"user": user}, "")
	case "auth/logout":
		if r.Method != http.MethodPost {
			w.Header().Set("Allow", "POST, OPTIONS")
			s.writeErr(w, r, http.StatusMethodNotAllowed, "method_not_allowed", "chỉ hỗ trợ POST")
			return
		}
		if user == nil {
			s.writeErr(w, r, http.StatusUnauthorized, "unauthorized", "chưa đăng nhập")
			return
		}
		s.o.Auth.Sessions.Revoke(bearerToken(r))
		w.Header().Set("Cache-Control", "no-store")
		w.WriteHeader(http.StatusNoContent)
	}
}

func (s *Server) apiLogin(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.Header().Set("Allow", "POST, OPTIONS")
		s.writeErr(w, r, http.StatusMethodNotAllowed, "method_not_allowed", "chỉ hỗ trợ POST")
		return
	}
	if !s.logins.allow(clientIP(r), time.Now()) {
		w.Header().Set("Retry-After", "60")
		s.writeErr(w, r, http.StatusTooManyRequests, "rate_limited", "thử đăng nhập quá nhiều, hãy đợi một phút")
		return
	}
	var in struct {
		Credential string `json:"credential"`
	}
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, maxAuthBody)).Decode(&in); err != nil {
		var mbe *http.MaxBytesError
		if errors.As(err, &mbe) {
			s.writeErr(w, r, http.StatusRequestEntityTooLarge, "too_large", "dữ liệu quá lớn")
		} else {
			s.fail(w, r, &library.Error{Status: http.StatusBadRequest, Code: "bad_body", Msg: "nội dung không hợp lệ"})
		}
		return
	}
	token, expires, u, err := s.o.Auth.Login(r.Context(), in.Credential)
	switch {
	case err == nil:
		s.writeJSON(w, r, http.StatusOK, map[string]any{"token": token, "expires": expires, "user": u}, "")
	case errors.Is(err, auth.ErrNotAllowed):
		s.writeErr(w, r, http.StatusForbidden, "not_allowed", "tài khoản này không được phép đăng nhập")
	case errors.Is(err, auth.ErrBadToken):
		s.writeErr(w, r, http.StatusUnauthorized, "bad_token", "mã đăng nhập Google không hợp lệ")
	case errors.Is(err, auth.ErrUnavailable):
		s.o.Logf("[auth] không lấy được khoá của Google: %v", err)
		s.writeErr(w, r, http.StatusBadGateway, "upstream", "không kết nối được Google, thử lại sau")
	default:
		s.fail(w, r, err)
	}
}

// clientIP is the peer address; behind a reverse proxy on this machine the
// proxy's own X-Forwarded-For entry (the last one) names the real client.
func clientIP(r *http.Request) string {
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		host = r.RemoteAddr
	}
	if IsLoopback(r.RemoteAddr) {
		if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
			parts := strings.Split(xff, ",")
			if ip := strings.TrimSpace(parts[len(parts)-1]); ip != "" && len(ip) <= 64 {
				return ip
			}
		}
	}
	return host
}

// rateLimiter is a fixed one-minute window per key.
type rateLimiter struct {
	mu sync.Mutex
	m  map[string]*window
}

type window struct {
	start time.Time
	n     int
}

func (l *rateLimiter) allow(key string, now time.Time) bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	if l.m == nil {
		l.m = map[string]*window{}
	}
	if len(l.m) >= maxLimiterKeys {
		for k, w := range l.m {
			if now.Sub(w.start) >= time.Minute {
				delete(l.m, k)
			}
		}
	}
	w := l.m[key]
	if w == nil || now.Sub(w.start) >= time.Minute {
		if w == nil && len(l.m) >= maxLimiterKeys {
			return false // table full of live windows: refuse rather than grow
		}
		w = &window{start: now}
		l.m[key] = w
	}
	w.n++
	return w.n <= loginsPerMin
}
