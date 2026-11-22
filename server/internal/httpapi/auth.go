package httpapi

import (
	"crypto/sha256"
	"crypto/subtle"
	"net"
	"net/http"
	"net/netip"
	"net/url"
	"os"
	"regexp"
	"strings"
	"sync"
)

// KeyCookie is the cookie that carries the access key for same-origin calls.
const KeyCookie = "mythlab_key"

// KeyHeader is the request header that carries the access key.
const KeyHeader = "X-MythLab-Key"

var (
	corsFixed = map[string]bool{"https://localhost": true, "http://localhost": true,
		"capacitor://localhost": true, "tauri://localhost": true}
	corsLocal = regexp.MustCompile(`^http://(localhost|127\.0\.0\.1)(:\d{1,5})?$`)

	hostnameOnce sync.Once
	hostnames    []string
)

// OriginAllowed reports whether a cross-origin page may call the API.
func OriginAllowed(origin string) bool {
	return origin != "" && (corsFixed[origin] || corsLocal.MatchString(origin))
}

func machineNames() []string {
	hostnameOnce.Do(func() {
		if h, err := os.Hostname(); err == nil && h != "" {
			h = strings.ToLower(h)
			hostnames = []string{h, h + ".local", h + ".lan"}
		}
	})
	return hostnames
}

// hostOK guards against DNS rebinding: a browser tricked into resolving an
// attacker's name to this machine still sends that name in Host. IP literals,
// localhost, this machine's name and configured extras are accepted.
func (s *Server) hostOK(hostport string) bool {
	if hostport == "" {
		return true // HTTP/1.0 clients; a browser always sends Host
	}
	host := hostport
	if h, _, err := net.SplitHostPort(hostport); err == nil {
		host = h
	}
	host = strings.ToLower(strings.TrimSuffix(strings.Trim(host, "[]"), "."))
	if host == "" {
		return false
	}
	if i := strings.IndexByte(host, '%'); i >= 0 { // IPv6 zone
		host = host[:i]
	}
	if _, err := netip.ParseAddr(host); err == nil {
		return true
	}
	if s.hosts[host] {
		return true
	}
	for _, n := range machineNames() {
		if host == n {
			return true
		}
	}
	return false
}

// IsLoopback reports whether a RemoteAddr ("ip:port") is this machine.
func IsLoopback(remoteAddr string) bool {
	host := remoteAddr
	if h, _, err := net.SplitHostPort(remoteAddr); err == nil {
		host = h
	}
	if i := strings.IndexByte(host, '%'); i >= 0 {
		host = host[:i]
	}
	ip, err := netip.ParseAddr(strings.Trim(host, "[]"))
	if err != nil {
		return false
	}
	return ip.Unmap().IsLoopback()
}

// keyMatches compares k with the access key in constant time.
func (s *Server) keyMatches(k string) bool {
	want := s.o.AccessKey()
	if want == "" || k == "" {
		return false
	}
	a, b := sha256.Sum256([]byte(k)), sha256.Sum256([]byte(want))
	return subtle.ConstantTimeCompare(a[:], b[:]) == 1
}

// presentedKey reports whether the request carries the right key in the
// header, the ?k= parameter or the cookie.
func (s *Server) presentedKey(r *http.Request, q map[string]string) bool {
	if s.keyMatches(r.Header.Get(KeyHeader)) || s.keyMatches(q["k"]) {
		return true
	}
	for _, c := range r.Cookies() {
		if c.Name != KeyCookie {
			continue
		}
		v := c.Value
		if d, err := url.QueryUnescape(v); err == nil {
			v = d
		}
		if s.keyMatches(v) || s.keyMatches(c.Value) {
			return true
		}
	}
	return false
}

// keyRequired: every peer that is not this machine must present the key,
// whatever address the server is bound to.
func (s *Server) keyRequired(r *http.Request) bool {
	return s.o.DistrustLoopback || !IsLoopback(r.RemoteAddr)
}

// Authorized is the access decision for one API request.
func (s *Server) Authorized(r *http.Request) bool {
	if !s.keyRequired(r) {
		return true
	}
	return s.presentedKey(r, lastQuery(r.URL.RawQuery))
}

// requestOrigin is the origin of the page that issued the request, from
// Origin or, failing that, Referer.
func requestOrigin(r *http.Request) string {
	if o := r.Header.Get("Origin"); o != "" {
		return o
	}
	if ref := r.Header.Get("Referer"); ref != "" {
		if u, err := url.Parse(ref); err == nil && u.Scheme != "" && u.Host != "" {
			return u.Scheme + "://" + u.Host
		}
	}
	return ""
}

// crossSiteBlocked stops other web sites from making a local browser call
// the API on their behalf (<img>, <audio>, fetch no-cors) when the peer is
// exempt from the key. Allow-listed app origins and holders of the key pass.
func (s *Server) crossSiteBlocked(r *http.Request, hasKey bool) bool {
	if hasKey || !strings.EqualFold(r.Header.Get("Sec-Fetch-Site"), "cross-site") {
		return false
	}
	return !OriginAllowed(requestOrigin(r))
}

// cors adds the CORS headers for an allowed origin.
func (s *Server) cors(w http.ResponseWriter, r *http.Request) bool {
	origin := r.Header.Get("Origin")
	if !OriginAllowed(origin) {
		return false
	}
	h := w.Header()
	h.Set("Access-Control-Allow-Origin", origin)
	h.Add("Vary", "Origin")
	return true
}

func (s *Server) preflight(w http.ResponseWriter, r *http.Request, isAPI bool) {
	h := w.Header()
	h.Set("Content-Length", "0")
	if !isAPI || !s.cors(w, r) {
		w.WriteHeader(http.StatusForbidden)
		return
	}
	methods := "GET, HEAD, OPTIONS"
	switch r.URL.Path {
	case progressPath, libraryPath:
		methods = "GET, HEAD, PUT, OPTIONS"
	case authGooglePath, authLogoutPath:
		methods = "POST, OPTIONS"
	}
	h.Set("Access-Control-Allow-Methods", methods)
	h.Set("Access-Control-Allow-Headers", "X-MythLab-Key, Content-Type, Range, Authorization")
	h.Set("Access-Control-Max-Age", "600")
	if r.Header.Get("Access-Control-Request-Private-Network") != "" {
		h.Set("Access-Control-Allow-Private-Network", "true")
	}
	w.WriteHeader(http.StatusNoContent)
}
