package httpapi

import (
	"bytes"
	"crypto/sha1"
	"encoding/hex"
	"io"
	"io/fs"
	"net/http"
	"path"
	"strconv"
	"strings"
	"sync"
	"time"
)

// maxInlineStatic is the largest text asset compressed in memory.
const maxInlineStatic = 8 << 20

var staticTypes = map[string]string{
	".html": "text/html; charset=utf-8", ".htm": "text/html; charset=utf-8",
	".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
	".css": "text/css; charset=utf-8", ".json": "application/json", ".map": "application/json",
	".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
	".webp": "image/webp", ".gif": "image/gif", ".avif": "image/avif",
	".webmanifest": "application/manifest+json", ".txt": "text/plain; charset=utf-8", ".xml": "application/xml",
	".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".otf": "font/otf",
	".mp3": "audio/mpeg", ".wasm": "application/wasm", ".onnx": "application/octet-stream",
}

var staticText = map[string]bool{".html": true, ".htm": true, ".js": true, ".mjs": true, ".css": true, ".json": true,
	".map": true, ".svg": true, ".webmanifest": true, ".txt": true, ".xml": true}

type staticFiles struct {
	fsys fs.FS
	mu   sync.Mutex
	tags map[string]string // content tags of files without a modification time (embedded)
}

func newStaticFiles(fsys fs.FS) *staticFiles {
	return &staticFiles{fsys: fsys, tags: map[string]string{}}
}

// staticName maps a URL path to a name inside the file system, or "".
func staticName(urlPath string) string {
	if urlPath == "" || urlPath[0] != '/' || strings.ContainsAny(urlPath, "\\:\x00") {
		return ""
	}
	for _, seg := range strings.Split(urlPath, "/") {
		if seg == ".." || (strings.HasPrefix(seg, ".") && seg != "." && seg != ".well-known") {
			return "" // no traversal, no dotfiles
		}
	}
	name := strings.TrimPrefix(path.Clean(urlPath), "/")
	if name == "" {
		name = "index.html"
	} else if strings.HasSuffix(urlPath, "/") {
		name += "/index.html"
	}
	if !fs.ValidPath(name) {
		return ""
	}
	return name
}

func (sf *staticFiles) open(name string) (fs.File, fs.FileInfo, bool) {
	if sf.fsys == nil || name == "" {
		return nil, nil, false
	}
	f, err := sf.fsys.Open(name)
	if err != nil {
		return nil, nil, false
	}
	st, err := f.Stat()
	if err != nil || !st.Mode().IsRegular() {
		f.Close()
		return nil, nil, false
	}
	return f, st, true
}

func (sf *staticFiles) notFound(w http.ResponseWriter, r *http.Request) {
	h := w.Header()
	h.Set("Cache-Control", "no-store")
	if f, st, ok := sf.open("404.html"); ok {
		defer f.Close()
		if st.Size() <= maxInlineStatic {
			if body, err := io.ReadAll(f); err == nil {
				h.Set("Content-Type", "text/html; charset=utf-8")
				h.Set("Content-Length", strconv.Itoa(len(body)))
				w.WriteHeader(http.StatusNotFound)
				if r.Method != http.MethodHead {
					w.Write(body)
				}
				return
			}
		}
	}
	http.Error(w, "404 Not Found", http.StatusNotFound)
}

func (sf *staticFiles) contentTag(name string, st fs.FileInfo, body []byte) string {
	if !st.ModTime().IsZero() && st.ModTime().Unix() > 0 {
		return `"` + strconv.FormatInt(st.ModTime().UnixNano(), 36) + "-" + strconv.FormatInt(st.Size(), 36) + `"`
	}
	sf.mu.Lock()
	defer sf.mu.Unlock()
	if t, ok := sf.tags[name]; ok {
		return t
	}
	if body == nil {
		return ""
	}
	h := sha1.Sum(body)
	t := `"` + hex.EncodeToString(h[:10]) + `"`
	sf.tags[name] = t
	return t
}

func (s *Server) serveStatic(w http.ResponseWriter, r *http.Request) {
	sf := s.static
	name := staticName(r.URL.Path)
	f, st, ok := sf.open(name)
	if !ok && name != "" && !strings.HasSuffix(name, "/index.html") && path.Ext(name) == "" {
		// "/doc" -> "/doc.html" or "/doc/index.html" (static site generators emit either)
		for _, alt := range []string{name + ".html", name + "/index.html"} {
			if f, st, ok = sf.open(alt); ok {
				name = alt
				break
			}
		}
	}
	if !ok {
		sf.notFound(w, r)
		return
	}
	defer f.Close()
	ext := strings.ToLower(path.Ext(name))
	ctype := staticTypes[ext]
	if ctype == "" {
		ctype = "application/octet-stream"
	}
	h := w.Header()
	if strings.HasPrefix(name, "_astro/") {
		h.Set("Cache-Control", "public, max-age=31536000, immutable") // content-hashed names
	} else {
		h.Set("Cache-Control", "no-cache")
	}
	h.Set("Content-Type", ctype)
	if staticText[ext] && st.Size() <= maxInlineStatic && r.Header.Get("Range") == "" {
		body, err := io.ReadAll(io.LimitReader(f, maxInlineStatic+1))
		if err != nil {
			sf.notFound(w, r)
			return
		}
		etag := sf.contentTag(name, st, body)
		if etag != "" {
			h.Set("ETag", etag)
			if etagMatch(r, etag) {
				h.Add("Vary", "Accept-Encoding")
				w.WriteHeader(http.StatusNotModified)
				return
			}
		}
		s.writeBody(w, r, http.StatusOK, ctype, body, true)
		return
	}
	rs, seekable := f.(io.ReadSeeker)
	if !seekable {
		body, err := io.ReadAll(f)
		if err != nil {
			sf.notFound(w, r)
			return
		}
		rs = bytes.NewReader(body)
	}
	etag := sf.contentTag(name, st, nil)
	if etag == "" { // embedded binary asset: hash it once
		if body, err := io.ReadAll(rs); err == nil {
			etag = sf.contentTag(name, st, body)
			rs = bytes.NewReader(body)
		}
	}
	if etag != "" {
		h.Set("ETag", etag)
	}
	mod := st.ModTime()
	if mod.Unix() <= 0 {
		mod = time.Time{}
	}
	http.ServeContent(w, r, "", mod, rs)
}
