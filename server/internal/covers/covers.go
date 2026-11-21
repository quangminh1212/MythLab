// Package covers keeps the on-disk poster cache (downloaded once, SSRF-safe)
// and produces resized JPEG covers.
package covers

import (
	"context"
	"crypto/sha1"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net"
	"net/http"
	"net/netip"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"syscall"
	"time"

	"golang.org/x/sync/singleflight"

	"mythlab/internal/library"
)

const (
	// MaxPoster is the largest poster that is downloaded.
	MaxPoster = 3 << 20
	missTTL   = 24 * time.Hour
	fetchTime = 15 * time.Second
)

// ErrNoCover means the poster cannot be had (bad URL, download failed, not an image).
var ErrNoCover = errors.New("no cover")

var httpURL = regexp.MustCompile(`(?i)^https?://`)

// exts are the cache suffixes of a hit, in lookup order.
var exts = []string{".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".img"}

// Options configures a Store.
type Options struct {
	Dir  string // <cache>/covers
	Logf func(format string, args ...any)

	allowPrivate bool // tests only: let the downloader reach loopback
}

// Store is the cover cache.
type Store struct {
	dir  string
	logf func(string, ...any)
	hc   *http.Client
	sf   singleflight.Group
	sem  chan struct{} // bounds concurrent resizes
}

var blockedNets = func() []netip.Prefix {
	var out []netip.Prefix
	for _, s := range []string{
		"0.0.0.0/8", "100.64.0.0/10", "192.0.0.0/24", "192.0.2.0/24", "192.88.99.0/24", "198.18.0.0/15",
		"198.51.100.0/24", "203.0.113.0/24", "240.0.0.0/4",
		"64:ff9b::/96", "64:ff9b:1::/48", "100::/64", "2001::/32", "2001:db8::/32", "2002::/16", "fec0::/10",
	} {
		out = append(out, netip.MustParsePrefix(s))
	}
	return out
}()

// IsPublicIP reports whether ip is a globally routable unicast address: not
// loopback, private, link-local, CGNAT, multicast, documentation, or an
// IPv6 form that embeds an IPv4 address (NAT64, 6to4, Teredo).
func IsPublicIP(ip netip.Addr) bool {
	if !ip.IsValid() {
		return false
	}
	ip = ip.Unmap().WithZone("")
	if ip.IsUnspecified() || ip.IsLoopback() || ip.IsPrivate() || ip.IsMulticast() ||
		ip.IsLinkLocalUnicast() || ip.IsLinkLocalMulticast() || ip.IsInterfaceLocalMulticast() {
		return false
	}
	for _, p := range blockedNets {
		if p.Contains(ip) {
			return false
		}
	}
	return true
}

// New creates the store; the HTTP client refuses to connect to non-public addresses.
func New(o Options) *Store {
	logf := o.Logf
	if logf == nil {
		logf = func(string, ...any) {}
	}
	d := &net.Dialer{Timeout: 10 * time.Second}
	if !o.allowPrivate {
		// checked on the address actually dialled, so DNS tricks cannot bypass it
		d.Control = func(network, address string, _ syscall.RawConn) error {
			ap, err := netip.ParseAddrPort(address)
			if err != nil || !IsPublicIP(ap.Addr()) {
				return fmt.Errorf("địa chỉ không công khai")
			}
			return nil
		}
	}
	tr := &http.Transport{Proxy: nil, DialContext: d.DialContext, TLSHandshakeTimeout: 10 * time.Second,
		ResponseHeaderTimeout: fetchTime, MaxIdleConnsPerHost: 6, IdleConnTimeout: 60 * time.Second, ForceAttemptHTTP2: true}
	hc := &http.Client{Transport: tr, Timeout: fetchTime, CheckRedirect: func(req *http.Request, via []*http.Request) error {
		if len(via) >= 5 {
			return errors.New("quá nhiều chuyển hướng")
		}
		if req.URL.Scheme != "http" && req.URL.Scheme != "https" {
			return errors.New("chuyển hướng không hợp lệ")
		}
		return nil
	}}
	n := 4
	return &Store{dir: o.Dir, logf: logf, hc: hc, sem: make(chan struct{}, n)}
}

// Prune bounds the cache directory: files not modified for maxAge are removed,
// then the oldest files go until the total size is at most maxBytes. Zero
// disables the matching limit. Temporary files being written are left alone
// for a minute.
func (s *Store) Prune(maxBytes int64, maxAge time.Duration) {
	type entry struct {
		path string
		size int64
		mod  time.Time
	}
	var files []entry
	var total int64
	now := time.Now()
	filepath.WalkDir(s.dir, func(p string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() {
			return nil
		}
		info, err := d.Info()
		if err != nil || now.Sub(info.ModTime()) < time.Minute {
			return nil
		}
		if maxAge > 0 && now.Sub(info.ModTime()) > maxAge {
			if os.Remove(p) == nil {
				return nil
			}
		}
		files = append(files, entry{p, info.Size(), info.ModTime()})
		total += info.Size()
		return nil
	})
	if maxBytes <= 0 || total <= maxBytes {
		return
	}
	sort.Slice(files, func(i, j int) bool { return files[i].mod.Before(files[j].mod) })
	for _, f := range files {
		if total <= maxBytes {
			break
		}
		if os.Remove(f.path) == nil {
			total -= f.size
		}
	}
}

// Dir is the directory the store keeps its files in.
func (s *Store) Dir() string { return s.dir }

// Close releases idle connections.
func (s *Store) Close() { s.hc.CloseIdleConnections() }

// Key is the cache name of a poster URL.
func Key(url string) string {
	h := sha1.Sum([]byte(url))
	return hex.EncodeToString(h[:])
}

// Sniff recognises raster image formats by content. It returns "" for
// anything else (SVG and HTML included).
func Sniff(b []byte) (ext, ctype string) {
	switch {
	case len(b) >= 3 && b[0] == 0xff && b[1] == 0xd8 && b[2] == 0xff:
		return ".jpg", "image/jpeg"
	case len(b) >= 8 && string(b[:8]) == "\x89PNG\r\n\x1a\n":
		return ".png", "image/png"
	case len(b) >= 6 && (string(b[:6]) == "GIF87a" || string(b[:6]) == "GIF89a"):
		return ".gif", "image/gif"
	case len(b) >= 12 && string(b[:4]) == "RIFF" && string(b[8:12]) == "WEBP":
		return ".webp", "image/webp"
	case len(b) >= 12 && string(b[4:8]) == "ftyp" && (string(b[8:12]) == "avif" || string(b[8:12]) == "avis"):
		return ".avif", "image/avif"
	}
	return "", ""
}

func sniffFile(path string) (string, bool) {
	f, err := os.Open(path)
	if err != nil {
		return "", false
	}
	defer f.Close()
	head := make([]byte, 16)
	n, _ := io.ReadFull(f, head)
	_, ct := Sniff(head[:n])
	return ct, ct != ""
}

// Lookup returns a cached poster without touching the network.
func (s *Store) Lookup(url string) (path, ctype string, ok bool) {
	if !httpURL.MatchString(url) {
		return "", "", false
	}
	base := filepath.Join(s.dir, Key(url))
	for _, ext := range exts {
		p := base + ext
		st, err := os.Stat(p)
		if err != nil || !st.Mode().IsRegular() || st.Size() == 0 {
			continue
		}
		// the content decides the type: never serve something that is not a raster image
		if ct, ok := sniffFile(p); ok {
			return p, ct, true
		}
	}
	return "", "", false
}

func (s *Store) missed(url string) bool {
	st, err := os.Stat(filepath.Join(s.dir, Key(url)+".miss"))
	return err == nil && time.Since(st.ModTime()) < missTTL
}

// Poster returns the cached file of a poster URL, downloading it once.
// retry ignores the 24 h negative cache.
func (s *Store) Poster(ctx context.Context, url string, retry bool) (path, ctype string, err error) {
	if !httpURL.MatchString(url) {
		return "", "", ErrNoCover
	}
	if p, ct, ok := s.Lookup(url); ok {
		return p, ct, nil
	}
	if !retry && s.missed(url) {
		return "", "", ErrNoCover
	}
	type res struct{ path, ctype string }
	ch := s.sf.DoChan("p:"+Key(url), func() (any, error) {
		if p, ct, ok := s.Lookup(url); ok {
			return res{p, ct}, nil
		}
		c, cancel := context.WithTimeout(context.Background(), fetchTime)
		defer cancel()
		data, ext, ct, err := s.download(c, url)
		base := filepath.Join(s.dir, Key(url))
		if err != nil {
			msg := url + "\n" + err.Error()
			if werr := library.AtomicWrite(base+".miss", []byte(msg)); werr != nil {
				s.logf("[covers] không ghi được .miss: %v", werr)
			}
			return nil, ErrNoCover
		}
		if err := library.AtomicWrite(base+ext, data); err != nil {
			s.logf("[covers] không ghi được ảnh bìa: %v", err)
			return nil, ErrNoCover
		}
		return res{base + ext, ct}, nil
	})
	select {
	case r := <-ch:
		if r.Err != nil {
			return "", "", r.Err
		}
		x := r.Val.(res)
		return x.path, x.ctype, nil
	case <-ctx.Done():
		return "", "", ctx.Err()
	}
}

func (s *Store) download(ctx context.Context, url string) (data []byte, ext, ctype string, err error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, "", "", errors.New("URL không hợp lệ")
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (mythlab-reader)")
	req.Header.Set("Accept", "image/*")
	resp, err := s.hc.Do(req)
	if err != nil {
		return nil, "", "", errors.New("không tải được: " + shortErr(err))
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, "", "", fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	data, err = io.ReadAll(io.LimitReader(resp.Body, MaxPoster+1))
	if err != nil {
		return nil, "", "", errors.New("tải dở dang")
	}
	if len(data) == 0 || len(data) > MaxPoster {
		return nil, "", "", errors.New("ảnh rỗng hoặc quá lớn")
	}
	ext, ctype = Sniff(data)
	if ext == "" {
		return nil, "", "", errors.New("không phải ảnh")
	}
	return data, ext, ctype, nil
}

// shortErr keeps the cause of a network error without the URL.
func shortErr(err error) string {
	msg := err.Error()
	if i := strings.LastIndex(msg, ": "); i >= 0 {
		msg = msg[i+2:]
	}
	return msg
}
