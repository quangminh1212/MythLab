// Package httpapi is the HTTP layer of the MythLab reader: the JSON API
// under /api/ and the static web UI.
package httpapi

import (
	"bytes"
	"compress/gzip"
	"encoding/json"
	"io"
	"io/fs"
	"net/http"
	"net/url"
	"runtime/debug"
	"strconv"
	"strings"
	"sync"
	"time"

	"mythlab/internal/covers"
	"mythlab/internal/library"
	"mythlab/internal/tts"
)

// Options wires the HTTP layer to the rest of the server.
type Options struct {
	Library *library.Library
	Search  *library.SearchIndex
	Covers  *covers.Store
	TTS     *tts.Service // may wrap a nil engine: TTS unavailable
	Static  fs.FS        // the web UI (index.html at the root)

	// AccessKey returns the key non-loopback clients must present. It is
	// called lazily; "" means no key can be had and such clients are refused.
	AccessKey func() string
	// DistrustLoopback also demands the key from loopback clients (use
	// behind a reverse proxy or tunnel on the same machine).
	DistrustLoopback bool
	// Hosts are extra names accepted in the Host header.
	Hosts []string
	Logf  func(format string, args ...any)
}

// Server is the http.Handler.
type Server struct {
	o      Options
	hosts  map[string]bool
	static *staticFiles
	gzPool sync.Pool
}

// New builds the handler.
func New(o Options) *Server {
	if o.Logf == nil {
		o.Logf = func(string, ...any) {}
	}
	if o.AccessKey == nil {
		o.AccessKey = func() string { return "" }
	}
	if o.TTS == nil {
		o.TTS = tts.NewService(tts.ServiceOptions{})
	}
	s := &Server{o: o, hosts: map[string]bool{"localhost": true}}
	for _, h := range o.Hosts {
		if h = strings.ToLower(strings.TrimSpace(h)); h != "" {
			s.hosts[h] = true
		}
	}
	s.static = newStaticFiles(o.Static)
	s.gzPool.New = func() any { w, _ := gzip.NewWriterLevel(io.Discard, gzip.BestSpeed); return w }
	return s
}

type statusWriter struct {
	http.ResponseWriter
	status int
	wrote  bool
}

func (w *statusWriter) WriteHeader(code int) {
	if !w.wrote {
		w.status, w.wrote = code, true
	}
	w.ResponseWriter.WriteHeader(code)
}

func (w *statusWriter) Write(b []byte) (int, error) {
	if !w.wrote {
		w.status, w.wrote = http.StatusOK, true
	}
	return w.ResponseWriter.Write(b)
}

func (w *statusWriter) Flush() {
	if f, ok := w.ResponseWriter.(http.Flusher); ok {
		f.Flush()
	}
}

// MaskKey hides the access key in a request URI for logging. Parameter names
// are percent-decoded first (lastQuery accepts "%6b" as "k"), so every spelling
// of the name is redacted.
func MaskKey(uri string) string {
	i := strings.IndexByte(uri, '?')
	if i < 0 {
		return uri
	}
	query, frag := uri[i+1:], ""
	if j := strings.IndexByte(query, '#'); j >= 0 {
		query, frag = query[:j], query[j:]
	}
	parts := strings.Split(query, "&")
	for n, part := range parts {
		name, _, found := strings.Cut(part, "=")
		if !found {
			continue
		}
		if d, err := url.QueryUnescape(name); err == nil {
			name = d
		}
		if name == "k" {
			parts[n] = part[:strings.IndexByte(part, '=')+1] + "***"
		}
	}
	return uri[:i+1] + strings.Join(parts, "&") + frag
}

// webCSP is sent with every non-API response. The UI has no inline scripts or
// styles and loads fonts and icons from its own origin. connect-src, img-src
// and media-src stay open to http(s) because the user chooses the API server
// (LAN or remote), GitHub (api.github.com) and the poster hosts at runtime.
const webCSP = "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; " +
	"img-src 'self' data: blob: http: https:; media-src 'self' blob: http: https:; " +
	"connect-src 'self' https://api.github.com http: https:; worker-src 'self'; manifest-src 'self'; " +
	"object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"

func (s *Server) ServeHTTP(rw http.ResponseWriter, r *http.Request) {
	w := &statusWriter{ResponseWriter: rw, status: http.StatusOK}
	defer func() {
		if v := recover(); v != nil {
			if v == http.ErrAbortHandler {
				panic(v)
			}
			s.o.Logf("[panic] %s %s: %v\n%s", r.Method, MaskKey(r.URL.RequestURI()), v, debug.Stack())
			if !w.wrote {
				s.writeErr(w, r, http.StatusInternalServerError, "internal", "lỗi máy chủ")
			}
		}
		if !(w.status == http.StatusOK && strings.HasPrefix(r.URL.Path, "/api/tts")) {
			s.o.Logf("[%s] \"%s %s %s\" %d", time.Now().Format("15:04:05"), r.Method, MaskKey(r.URL.RequestURI()), r.Proto, w.status)
		}
	}()
	h := w.Header()
	h.Set("X-Content-Type-Options", "nosniff")
	h.Set("Referrer-Policy", "no-referrer")
	isAPI := strings.HasPrefix(r.URL.Path, "/api/")
	if !isAPI {
		h.Set("Content-Security-Policy", webCSP)
		h.Set("X-Frame-Options", "DENY")
	}
	if !s.hostOK(r.Host) {
		if isAPI {
			s.writeErr(w, r, http.StatusForbidden, "bad_host", "Host không được phép")
		} else {
			http.Error(w, "403 Forbidden", http.StatusForbidden)
		}
		return
	}
	switch r.Method {
	case http.MethodGet, http.MethodHead:
	case http.MethodOptions:
		s.preflight(w, r, isAPI)
		return
	default:
		h.Set("Allow", "GET, HEAD, OPTIONS")
		if isAPI {
			s.cors(w, r)
			s.writeErr(w, r, http.StatusMethodNotAllowed, "method_not_allowed", "chỉ hỗ trợ GET/HEAD")
		} else {
			http.Error(w, "405 Method Not Allowed", http.StatusMethodNotAllowed)
		}
		return
	}
	if isAPI {
		s.api(w, r)
		return
	}
	// LAN: opening http://ip:port/?k=<key> once sets the cookie for same-origin /api/* calls
	if k := lastQuery(r.URL.RawQuery)["k"]; k != "" && s.keyMatches(k) {
		h.Set("Set-Cookie", KeyCookie+"="+url.QueryEscape(k)+"; Path=/; Max-Age=31536000; SameSite=Strict; HttpOnly")
		// the key must not stay in the address bar, history or a bookmark: continue without it
		h.Set("Cache-Control", "no-store")
		http.Redirect(w, r, withoutKey(r.URL), http.StatusSeeOther)
		return
	}
	s.serveStatic(w, r)
}

// withoutKey rebuilds the request target with every k= parameter removed.
func withoutKey(u *url.URL) string {
	var keep []string
	for _, part := range strings.Split(u.RawQuery, "&") {
		name, _, _ := strings.Cut(part, "=")
		if d, err := url.QueryUnescape(name); err == nil {
			name = d
		}
		if part != "" && name != "k" {
			keep = append(keep, part)
		}
	}
	p := u.EscapedPath()
	if p == "" {
		p = "/"
	}
	if len(keep) > 0 {
		p += "?" + strings.Join(keep, "&")
	}
	return p
}

// lastQuery parses a query string like Python's parse_qs: the last value
// wins, blank values are dropped, malformed escapes are kept verbatim.
func lastQuery(raw string) map[string]string {
	q := map[string]string{}
	for _, part := range strings.Split(raw, "&") {
		if part == "" {
			continue
		}
		k, v, _ := strings.Cut(part, "=")
		if v == "" {
			continue
		}
		if d, err := url.QueryUnescape(k); err == nil {
			k = d
		}
		if d, err := url.QueryUnescape(v); err == nil {
			v = d
		}
		q[k] = strings.ToValidUTF8(v, "\xef\xbf\xbd")
	}
	return q
}

func marshal(v any) []byte {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(v); err != nil {
		return []byte(`{"error":"lỗi máy chủ","code":"internal"}`)
	}
	return bytes.TrimRight(buf.Bytes(), "\n")
}

func acceptsGzip(r *http.Request) bool {
	for _, p := range strings.Split(r.Header.Get("Accept-Encoding"), ",") {
		name, params, _ := strings.Cut(strings.TrimSpace(p), ";")
		if strings.EqualFold(strings.TrimSpace(name), "gzip") {
			return !strings.Contains(strings.ReplaceAll(params, " ", ""), "q=0") || strings.Contains(params, "q=0.")
		}
	}
	return false
}

// etagMatch implements If-None-Match for a strong or weak tag.
func etagMatch(r *http.Request, etag string) bool {
	inm := r.Header.Get("If-None-Match")
	if inm == "" || etag == "" {
		return false
	}
	if strings.TrimSpace(inm) == "*" {
		return true
	}
	bare := strings.TrimPrefix(etag, "W/")
	for _, c := range strings.Split(inm, ",") {
		if strings.TrimPrefix(strings.TrimSpace(c), "W/") == bare {
			return true
		}
	}
	return false
}

// writeBody sends a complete in-memory body with optional gzip, honouring HEAD.
func (s *Server) writeBody(w http.ResponseWriter, r *http.Request, status int, ctype string, body []byte, compress bool) {
	h := w.Header()
	h.Set("Content-Type", ctype)
	if compress {
		h.Add("Vary", "Accept-Encoding")
		if len(body) >= 1024 && acceptsGzip(r) && r.Header.Get("Range") == "" {
			var buf bytes.Buffer
			gz := s.gzPool.Get().(*gzip.Writer)
			gz.Reset(&buf)
			gz.Write(body)
			gz.Close()
			s.gzPool.Put(gz)
			if buf.Len() < len(body) {
				h.Set("Content-Encoding", "gzip")
				body = buf.Bytes()
			}
		}
	}
	h.Set("Content-Length", strconv.Itoa(len(body)))
	w.WriteHeader(status)
	if r.Method != http.MethodHead {
		w.Write(body)
	}
}

// writeJSON sends v as JSON. etag (optional) enables conditional requests.
func (s *Server) writeJSON(w http.ResponseWriter, r *http.Request, status int, v any, etag string) {
	h := w.Header()
	if etag != "" && status == http.StatusOK {
		h.Set("ETag", etag)
		h.Set("Cache-Control", "private, no-cache")
		if etagMatch(r, etag) {
			h.Add("Vary", "Accept-Encoding")
			w.WriteHeader(http.StatusNotModified)
			return
		}
	} else {
		h.Set("Cache-Control", "no-store")
	}
	s.writeBody(w, r, status, "application/json; charset=utf-8", marshal(v), true)
}

type errBody struct {
	Error string `json:"error"`
	Code  string `json:"code"`
}

func (s *Server) writeErr(w http.ResponseWriter, r *http.Request, status int, code, msg string) {
	w.Header().Del("ETag")
	s.writeJSON(w, r, status, errBody{msg, code}, "")
}
