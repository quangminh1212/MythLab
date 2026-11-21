package library

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"

	"golang.org/x/text/collate"
	"golang.org/x/text/language"
)

// Error is an API-visible failure: an HTTP status, a stable machine code and a
// message that never contains absolute paths.
type Error struct {
	Status int
	Code   string
	Msg    string
}

func (e *Error) Error() string { return e.Msg }

// ErrBadParam mirrors the old "missing/invalid parameter" message.
func ErrBadParam(name string) *Error {
	return &Error{http.StatusBadRequest, "bad_param", "thiếu/không đúng tham số: '" + name + "'"}
}

// ErrNotFound is a 404 for a missing story, chapter or repo.
func ErrNotFound(what string) *Error {
	return &Error{http.StatusNotFound, "not_found", "không tìm thấy: " + what}
}

// ErrForbidden is a 403 (path escape, bad chapter file).
func ErrForbidden(msg string) *Error {
	code := "forbidden"
	if msg == "path escape" {
		code = "path_escape"
	} else if msg == "bad chapter file" {
		code = "bad_chapter_file"
	}
	return &Error{http.StatusForbidden, code, msg}
}

// ErrUpstream is a 502 for a failing GitHub call.
func ErrUpstream(msg string) *Error { return &Error{http.StatusBadGateway, "upstream", msg} }

// AsError extracts an *Error from err.
func AsError(err error) (*Error, bool) {
	var e *Error
	if errors.As(err, &e) {
		return e, true
	}
	return nil, false
}

// Repo is one GitHub repository of a source.
type Repo struct {
	Repo     string  `json:"repo"`
	Branch   string  `json:"branch"`
	PushedAt *string `json:"pushed_at"`
	Private  *bool   `json:"private"`
}

// SourceInfo is one entry of /api/sources.
type SourceInfo struct {
	ID        string  `json:"id"`
	Name      string  `json:"name"`
	Kind      string  `json:"kind"`
	Detail    string  `json:"detail"`
	Available bool    `json:"available"`
	Repos     *[]Repo `json:"repos,omitempty"`
	Error     string  `json:"error,omitempty"`
	Stale     bool    `json:"stale,omitempty"`
}

// StoryItem is the list form of a story (key order matches the old server).
type StoryItem struct {
	Key          string  `json:"key"`
	Folder       string  `json:"folder"`
	Group        *string `json:"group"`
	ChapterFiles int     `json:"chapter_files"`
	Summary
	Cover *string `json:"cover"`
	// additive, only set by /api/search
	Source string `json:"source,omitempty"`
	Repo   string `json:"repo,omitempty"`
}

// StoryDetail is the /api/story payload.
type StoryDetail struct {
	Key    string `json:"key"`
	Source string `json:"source"`
	Summary
	Cover    *string   `json:"cover"`
	Chapters []Chapter `json:"chapters"`
	Stale    bool      `json:"stale,omitempty"`
}

// CoverRef describes where a story's cover comes from. Exactly one of Path,
// Data or Poster is set; all empty means the story has no cover.
type CoverRef struct {
	Path    string // image file on disk
	Data    []byte // image bytes (GitHub blob)
	Ctype   string // MIME type of Path/Data
	Tag     string // identity for caching (changes when the image changes)
	ModTime time.Time
	Poster  string // remote poster URL
}

// Provider is one story source.
type Provider interface {
	ID() string
	Kind() string
	Describe(ctx context.Context) SourceInfo
	// ListStories lists stories; repo is only meaningful for GitHub ("" = all repos).
	ListStories(ctx context.Context, repo string) (items []StoryItem, stale bool, err error)
	Story(ctx context.Context, key string) (*StoryDetail, error)
	// ReadChapter returns the raw bytes of a chapter file and an identity tag.
	ReadChapter(ctx context.Context, key, file string) (data []byte, tag string, err error)
	Cover(ctx context.Context, key string) (CoverRef, error)
	// IndexEntries returns what is known without network access, for the search index.
	IndexEntries() (groups map[string][]StoryItem, reposTotal int)
}

// Library is the ordered set of providers.
type Library struct {
	order []string
	by    map[string]Provider
}

// NewLibrary builds a library from providers in order.
func NewLibrary(ps ...Provider) *Library {
	l := &Library{by: map[string]Provider{}}
	for _, p := range ps {
		l.order = append(l.order, p.ID())
		l.by[p.ID()] = p
	}
	return l
}

// Get returns a provider or a 400 "bad parameter" error naming the id.
func (l *Library) Get(id string) (Provider, error) {
	p, ok := l.by[id]
	if !ok {
		// never echo control characters or very long input
		return nil, ErrBadParam(safeEcho(id))
	}
	return p, nil
}

// Providers returns the providers in configuration order.
func (l *Library) Providers() []Provider {
	out := make([]Provider, 0, len(l.order))
	for _, id := range l.order {
		out = append(out, l.by[id])
	}
	return out
}

func safeEcho(s string) string {
	var b strings.Builder
	for i, r := range s {
		if i >= 80 {
			b.WriteString("…")
			break
		}
		if r < 0x20 || r == 0x7f || r == '\'' || r == '\\' {
			r = '?'
		}
		b.WriteRune(r)
	}
	return b.String()
}

// PyQuote is urllib.parse.quote(s) with the default safe="/".
func PyQuote(s string) string {
	const hex = "0123456789ABCDEF"
	var b strings.Builder
	for i := 0; i < len(s); i++ {
		c := s[i]
		switch {
		case c >= 'a' && c <= 'z', c >= 'A' && c <= 'Z', c >= '0' && c <= '9', c == '_', c == '.', c == '-', c == '~', c == '/':
			b.WriteByte(c)
		default:
			b.WriteByte('%')
			b.WriteByte(hex[c>>4])
			b.WriteByte(hex[c&15])
		}
	}
	return b.String()
}

var httpURL = regexp.MustCompile(`(?i)^https?://`)

// IsHTTPURL reports whether s is an http(s) URL.
func IsHTTPURL(s string) bool { return httpURL.MatchString(s) }

// CoverURL returns the /api/cover URL of a story, or nil when it has neither an image nor a usable poster.
func CoverURL(sid, key string, hasImage bool, poster *string) *string {
	if !hasImage && (poster == nil || !IsHTTPURL(*poster)) {
		return nil
	}
	u := "/api/cover?source=" + PyQuote(sid) + "&key=" + PyQuote(key)
	return &u
}

var (
	viMu       sync.Mutex
	viCollator = collate.New(language.Vietnamese)
)

// ViKey returns the Vietnamese collation key of s.
func ViKey(s string) []byte {
	viMu.Lock()
	defer viMu.Unlock()
	var buf collate.Buffer
	k := viCollator.KeyFromString(&buf, s)
	return append([]byte(nil), k...)
}

// SortVi sorts items by Vietnamese collation of name(i), ties by the raw string.
func SortVi[T any](items []T, name func(T) string) {
	type row struct {
		k []byte
		s string
		v T
	}
	rows := make([]row, len(items))
	viMu.Lock()
	var buf collate.Buffer
	for i, it := range items {
		s := name(it)
		rows[i] = row{append([]byte(nil), viCollator.KeyFromString(&buf, s)...), s, it}
		buf.Reset()
	}
	viMu.Unlock()
	sort.SliceStable(rows, func(i, j int) bool {
		if c := strings.Compare(string(rows[i].k), string(rows[j].k)); c != 0 {
			return c < 0
		}
		return rows[i].s < rows[j].s
	})
	for i := range rows {
		items[i] = rows[i].v
	}
}

// validSegment rejects path traversal in one path segment of a key.
func validSegment(s string) bool {
	if s == "" || s == "." || s == ".." || strings.ContainsAny(s, "/\\:\x00") {
		return false
	}
	return true
}

func fmtErr(format string, a ...any) error { return fmt.Errorf(format, a...) }
