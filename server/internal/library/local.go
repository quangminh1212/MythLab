package library

import (
	"context"
	"fmt"
	"io"
	"os"
	"path"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"golang.org/x/text/unicode/norm"
)

const (
	localScanTTL  = 3 * time.Second
	maxInfoBytes  = 8 << 20
	maxLocalCover = 12 << 20
	maxChapterLen = 32 << 20
)

var localSkip = map[string]bool{"reader": true, "apk": true, "node_modules": true}

type localStory struct {
	key, folder, dir string
}

type localEntry struct {
	dirMod, infoMod time.Time
	infoSize        int64
	sum             Summary
	chapters        []Chapter // sorted, de-duplicated
	cover           string    // image file name or ""
}

// LocalProvider serves stories from a folder: <root>/<story> or <root>/<repo dir>/<story>.
type LocalProvider struct {
	id, name, root string

	mu      sync.Mutex
	scanAt  time.Time
	stories []localStory
	byKey   map[string]localStory
	entries map[string]*localEntry
}

// NewLocalProvider creates a provider rooted at an absolute directory.
func NewLocalProvider(id, name, root string) *LocalProvider {
	if name == "" {
		name = filepath.Base(root)
	}
	return &LocalProvider{id: id, name: name, root: root, entries: map[string]*localEntry{}}
}

func (p *LocalProvider) ID() string   { return p.id }
func (p *LocalProvider) Kind() string { return "local" }

// Root returns the absolute root directory.
func (p *LocalProvider) Root() string { return p.root }

func isDir(path string) bool {
	st, err := os.Stat(path)
	return err == nil && st.IsDir()
}

func (p *LocalProvider) Describe(context.Context) SourceInfo {
	return SourceInfo{ID: p.id, Name: p.name, Kind: "local", Detail: p.root, Available: isDir(p.root)}
}

func hidden(name string) bool { return strings.HasPrefix(name, ".") || strings.HasPrefix(name, "_") }

// looksLikeStory reports whether dir holds a chapter file or an info.json.
func looksLikeStory(dir string) bool {
	ents, err := os.ReadDir(dir)
	if err != nil {
		return false
	}
	for _, e := range ents {
		if e.IsDir() {
			continue
		}
		if e.Name() == "info.json" {
			return true
		}
		if _, ok := ParseChapterName(e.Name()); ok {
			return true
		}
	}
	return false
}

func (p *LocalProvider) scan(force bool) []localStory {
	p.mu.Lock()
	defer p.mu.Unlock()
	if !force && p.byKey != nil && time.Since(p.scanAt) < localScanTTL {
		return p.stories
	}
	var out []localStory
	top, _ := os.ReadDir(p.root)
	for _, d := range top {
		name := d.Name()
		if hidden(name) || localSkip[name] || !isDir(filepath.Join(p.root, name)) {
			continue
		}
		dir := filepath.Join(p.root, name)
		if looksLikeStory(dir) {
			out = append(out, localStory{name, name, dir})
			continue
		}
		subs, err := os.ReadDir(dir)
		if err != nil {
			continue
		}
		for _, s := range subs {
			sn := s.Name()
			if hidden(sn) || sn == "node_modules" {
				continue
			}
			sd := filepath.Join(dir, sn)
			if isDir(sd) && looksLikeStory(sd) {
				out = append(out, localStory{name + "/" + sn, sn, sd})
			}
		}
	}
	SortVi(out, func(s localStory) string { return s.key })
	by := make(map[string]localStory, len(out))
	for _, s := range out {
		by[s.key] = s
	}
	for k := range p.entries {
		if _, ok := by[k]; !ok {
			delete(p.entries, k)
		}
	}
	p.stories, p.byKey, p.scanAt = out, by, time.Now()
	return out
}

func (p *LocalProvider) lookup(key string) (localStory, error) {
	p.scan(false)
	p.mu.Lock()
	s, ok := p.byKey[key]
	p.mu.Unlock()
	if !ok {
		p.scan(true)
		p.mu.Lock()
		s, ok = p.byKey[key]
		p.mu.Unlock()
	}
	if ok {
		return s, nil
	}
	if key == "" {
		return s, ErrBadParam("key")
	}
	// NFC and NFD spellings of the same name are one story (macOS, copied links)
	p.mu.Lock()
	s, ok = p.byNormalizedKey(key)
	p.mu.Unlock()
	if ok {
		return s, nil
	}
	segs := strings.Split(key, "/")
	for _, seg := range segs {
		if !validSegment(seg) {
			return s, ErrForbidden("path escape")
		}
	}
	if filepath.IsAbs(key) || len(segs) > 2 {
		return s, ErrForbidden("path escape")
	}
	return s, ErrNotFound(safeEcho(key))
}

// byNormalizedKey finds a story whose key equals key after Unicode NFC
// normalisation. The caller holds p.mu.
func (p *LocalProvider) byNormalizedKey(key string) (localStory, bool) {
	want := norm.NFC.String(key)
	for k, s := range p.byKey {
		if norm.NFC.String(k) == want {
			return s, true
		}
	}
	return localStory{}, false
}

func readLimited(file string, max int64) ([]byte, error) {
	f, err := os.Open(file)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	b, err := io.ReadAll(io.LimitReader(f, max+1))
	if err != nil {
		return nil, err
	}
	if int64(len(b)) > max {
		return nil, fmt.Errorf("file too large")
	}
	return b, nil
}

// entry returns the cached per-story data, refreshing it when the folder or info.json changed.
func (p *LocalProvider) entry(s localStory) (*localEntry, error) {
	st, err := os.Stat(s.dir)
	if err != nil || !st.IsDir() {
		return nil, ErrNotFound(safeEcho(s.key))
	}
	var infoMod time.Time
	var infoSize int64 = -1
	if ist, err := os.Stat(filepath.Join(s.dir, "info.json")); err == nil && !ist.IsDir() {
		infoMod, infoSize = ist.ModTime(), ist.Size()
	}
	p.mu.Lock()
	e := p.entries[s.key]
	p.mu.Unlock()
	if e != nil && e.dirMod.Equal(st.ModTime()) && e.infoMod.Equal(infoMod) && e.infoSize == infoSize {
		return e, nil
	}
	ents, err := os.ReadDir(s.dir)
	if err != nil {
		return nil, ErrNotFound(safeEcho(s.key))
	}
	names := make([]string, 0, len(ents))
	for _, d := range ents {
		if !d.IsDir() {
			names = append(names, d.Name())
		}
	}
	var info []byte
	if infoSize >= 0 {
		info, _ = readLimited(filepath.Join(s.dir, "info.json"), maxInfoBytes) // unreadable = no info
	}
	e = &localEntry{dirMod: st.ModTime(), infoMod: infoMod, infoSize: infoSize,
		sum: InfoSummary(info, s.folder), chapters: ChapterList(names), cover: PickCover(names)}
	p.mu.Lock()
	p.entries[s.key] = e
	p.mu.Unlock()
	return e, nil
}

func (p *LocalProvider) item(s localStory, e *localEntry) StoryItem {
	it := StoryItem{Key: s.key, Folder: s.folder, ChapterFiles: len(e.chapters), Summary: e.sum}
	if i := strings.IndexByte(s.key, '/'); i >= 0 {
		g := s.key[:i]
		it.Group = &g
	}
	it.Cover = CoverURL(p.id, s.key, e.cover != "", e.sum.Poster)
	return it
}

func (p *LocalProvider) ListStories(context.Context, string) ([]StoryItem, bool, error) {
	out := []StoryItem{}
	for _, s := range p.scan(false) {
		e, err := p.entry(s)
		if err != nil {
			continue // vanished between scan and read
		}
		out = append(out, p.item(s, e))
	}
	return out, false, nil
}

func (p *LocalProvider) Story(_ context.Context, key string) (*StoryDetail, error) {
	s, err := p.lookup(key)
	if err != nil {
		return nil, err
	}
	e, err := p.entry(s)
	if err != nil {
		return nil, err
	}
	return &StoryDetail{Key: key, Source: p.id, Summary: e.sum,
		Cover: CoverURL(p.id, key, e.cover != "", e.sum.Poster), Chapters: e.chapters}, nil
}

func (p *LocalProvider) ReadChapter(_ context.Context, key, file string) ([]byte, string, error) {
	s, err := p.lookup(key)
	if err != nil {
		return nil, "", err
	}
	if !validSegment(file) {
		return nil, "", ErrForbidden("bad chapter file")
	}
	if _, ok := ParseChapterName(file); !ok {
		return nil, "", ErrForbidden("bad chapter file")
	}
	full := filepath.Join(s.dir, file)
	st, err := os.Lstat(full)
	if err != nil || !st.Mode().IsRegular() {
		return nil, "", ErrNotFound(safeEcho(file))
	}
	b, err := readLimited(full, maxChapterLen)
	if err != nil {
		return nil, "", ErrNotFound(safeEcho(file))
	}
	return b, fmt.Sprintf("%x-%x", st.ModTime().UnixNano(), st.Size()), nil
}

func (p *LocalProvider) Cover(_ context.Context, key string) (CoverRef, error) {
	s, err := p.lookup(key)
	if err != nil {
		return CoverRef{}, err
	}
	e, err := p.entry(s)
	if err != nil {
		return CoverRef{}, err
	}
	if e.cover != "" {
		full := filepath.Join(s.dir, e.cover)
		if st, err := os.Stat(full); err == nil && st.Mode().IsRegular() && st.Size() <= maxLocalCover {
			return CoverRef{Path: full, Ctype: ImgExt[strings.ToLower(path.Ext(e.cover))], ModTime: st.ModTime(),
				Tag: fmt.Sprintf("l-%x-%x", st.ModTime().UnixNano(), st.Size())}, nil
		}
	}
	if e.sum.Poster != nil && IsHTTPURL(*e.sum.Poster) {
		return CoverRef{Poster: *e.sum.Poster}, nil
	}
	return CoverRef{}, nil
}

func (p *LocalProvider) IndexEntries() (map[string][]StoryItem, int) {
	items, _, _ := p.ListStories(context.Background(), "")
	return map[string][]StoryItem{"": items}, 0
}
