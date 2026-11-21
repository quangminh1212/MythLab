// Package progress keeps the reading progress that devices sync through the
// server: one entry per story ("source|key"), merged last-writer-wins and
// persisted to progress.json in the config directory.
package progress

import (
	"encoding/json"
	"math"
	"os"
	"sort"
	"strings"
	"sync"
	"time"
	"unicode/utf8"

	"mythlab/internal/library"
)

const (
	// MaxEntries is the number of live stories kept; the oldest are dropped.
	MaxEntries = 500
	// TombstoneAge is how long a deletion is remembered.
	TombstoneAge = 60 * 24 * time.Hour
	// MaxSkew is how far in the future a client timestamp may lie.
	MaxSkew = 5 * time.Minute

	flushDelay = 2 * time.Second
	maxStr     = 500
)

// Listen is the listening position of a story.
type Listen struct {
	Idx  int    `json:"idx"`
	Para int    `json:"para"`
	File string `json:"file,omitempty"`
}

// Entry is the progress of one story (the web app's Progress, plus the
// server-side change stamp At and the Deleted tombstone flag).
type Entry struct {
	Source   string   `json:"source"`
	Key      string   `json:"key"`
	Ts       int64    `json:"ts"`
	At       int64    `json:"at,omitempty"` // server time of the last change; drives ?since=
	Deleted  bool     `json:"deleted,omitempty"`
	Name     string   `json:"name,omitempty"`
	Poster   *string  `json:"poster"`
	Cover    *string  `json:"cover"`
	CoverSha *string  `json:"cover_sha"`
	Author   *string  `json:"author"`
	Genres   []string `json:"genres"`
	Group    *string  `json:"group"`
	Idx      int      `json:"idx"`
	N        int      `json:"n"`
	Total    int      `json:"total"`
	Para     int      `json:"para"`
	Frac     float64  `json:"frac,omitempty"`
	File     string   `json:"file,omitempty"`
	Title    string   `json:"title,omitempty"`
	MaxIdx   int      `json:"maxIdx"`
	Listen   *Listen  `json:"listen,omitempty"`
}

// ID is the map key of an entry.
func (e Entry) ID() string { return e.Source + "|" + e.Key }

func clip(s string) string {
	if len(s) > maxStr {
		n := maxStr
		for n > 0 && !utf8.RuneStart(s[n]) { // never cut a multi-byte character in half
			n--
		}
		return s[:n]
	}
	return s
}

func clipPtr(p *string) *string {
	if p == nil {
		return nil
	}
	s := clip(*p)
	return &s
}

func nonNeg(n int) int {
	if n < 0 {
		return 0
	}
	return n
}

// Sanitize bounds the fields of an entry from a client; ok is false when it
// cannot be used. now is the server clock in ms.
func Sanitize(e Entry, now int64) (Entry, bool) {
	if e.Source == "" || e.Key == "" || strings.Contains(e.Source, "|") || len(e.Source) > 200 || len(e.Key) > 500 || e.Ts <= 0 {
		return e, false
	}
	if max := now + MaxSkew.Milliseconds(); e.Ts > max {
		e.Ts = max
	}
	e.At = 0
	e.Name, e.File, e.Title = clip(e.Name), clip(e.File), clip(e.Title)
	e.Poster, e.Cover, e.CoverSha, e.Author, e.Group = clipPtr(e.Poster), clipPtr(e.Cover), clipPtr(e.CoverSha), clipPtr(e.Author), clipPtr(e.Group)
	if len(e.Genres) > 3 {
		e.Genres = e.Genres[:3]
	}
	for i := range e.Genres {
		e.Genres[i] = clip(e.Genres[i])
	}
	e.Idx, e.N, e.Total, e.Para, e.MaxIdx = nonNeg(e.Idx), nonNeg(e.N), nonNeg(e.Total), nonNeg(e.Para), nonNeg(e.MaxIdx)
	if math.IsNaN(e.Frac) || e.Frac < 0 || e.Frac > 1 {
		e.Frac = 0
	}
	if e.Listen != nil {
		l := *e.Listen
		l.Idx, l.Para, l.File = nonNeg(l.Idx), nonNeg(l.Para), clip(l.File)
		e.Listen = &l
	}
	if e.Deleted {
		e = Entry{Source: e.Source, Key: e.Key, Ts: e.Ts, Deleted: true}
	}
	return e, true
}

// Merge combines two versions of one story. The newer ts wins; on a tie the
// larger maxIdx (then idx) does. maxIdx is the maximum of both; the listening
// position follows the winner (or the other side when the winner has none). A
// winning tombstone wipes the story.
func Merge(a, b Entry) Entry {
	win, lose := a, b
	if b.Ts > a.Ts || (b.Ts == a.Ts && (b.MaxIdx > a.MaxIdx || (b.MaxIdx == a.MaxIdx && b.Idx > a.Idx))) {
		win, lose = b, a
	}
	if win.Deleted {
		return Entry{Source: win.Source, Key: win.Key, Ts: win.Ts, Deleted: true}
	}
	if lose.Deleted {
		return win // a deletion older than the winner must not leak into it
	}
	if lose.MaxIdx > win.MaxIdx {
		win.MaxIdx = lose.MaxIdx
	}
	if win.MaxIdx < win.Idx {
		win.MaxIdx = win.Idx
	}
	if win.Listen == nil {
		win.Listen = lose.Listen
	}
	return win
}

// Store is the in-memory map with debounced, atomic persistence.
type Store struct {
	path string
	logf func(string, ...any)
	now  func() int64

	flushMu sync.Mutex // one file write at a time: an older snapshot must not land after a newer one
	mu      sync.Mutex
	m       map[string]Entry
	lastAt  int64
	dirty   bool
	timer   *time.Timer
	closed  bool
}

// Open loads path (a missing or unreadable file starts empty). An empty path
// keeps everything in memory.
func Open(path string, logf func(string, ...any)) *Store {
	if logf == nil {
		logf = func(string, ...any) {}
	}
	s := &Store{path: path, logf: logf, m: map[string]Entry{}, now: func() int64 { return time.Now().UnixMilli() }}
	if path == "" {
		return s
	}
	data, err := os.ReadFile(path)
	if err != nil {
		if !os.IsNotExist(err) {
			logf("[progress] không đọc được %s: %v", path, err)
		}
		return s
	}
	var f struct {
		Entries []Entry `json:"entries"`
	}
	if err := json.Unmarshal(data, &f); err != nil {
		logf("[progress] %s hỏng, bỏ qua: %v", path, err)
		return s
	}
	for _, e := range f.Entries {
		if e.Source != "" && e.Key != "" {
			s.m[e.ID()] = e
			if e.At > s.lastAt {
				s.lastAt = e.At
			}
		}
	}
	return s
}

// Now is the server clock in ms.
func (s *Store) Now() int64 { return s.now() }

// stamp returns a strictly increasing change stamp. Caller holds mu.
func (s *Store) stamp() int64 {
	t := s.now()
	if t <= s.lastAt {
		t = s.lastAt + 1
	}
	s.lastAt = t
	return t
}

// Since lists the entries (tombstones included) changed at or after since.
func (s *Store) Since(since int64) []Entry {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := []Entry{}
	for _, e := range s.m {
		if e.At >= since {
			out = append(out, e)
		}
	}
	sort.Slice(out, func(i, j int) bool { return out[i].At < out[j].At })
	return out
}

// Apply merges incoming entries and returns the resulting state of each.
func (s *Store) Apply(in []Entry) []Entry {
	s.mu.Lock()
	defer s.mu.Unlock()
	now := s.now()
	out := make([]Entry, 0, len(in))
	changed := false
	for _, raw := range in {
		e, ok := Sanitize(raw, now)
		if !ok {
			continue
		}
		id := e.ID()
		cur, had := s.m[id]
		merged := e
		if had {
			merged = Merge(cur, e)
		}
		merged.At = cur.At
		if !had || !sameEntry(cur, merged) {
			merged.At = s.stamp()
			s.m[id] = merged
			changed = true
		}
		out = append(out, merged)
	}
	if changed {
		s.prune(now)
		s.markDirty()
	}
	return out
}

func sameEntry(a, b Entry) bool {
	a.At, b.At = 0, 0
	x, _ := json.Marshal(a)
	y, _ := json.Marshal(b)
	return string(x) == string(y)
}

// prune drops old tombstones and the oldest live entries over the cap.
func (s *Store) prune(now int64) {
	var live []string
	for id, e := range s.m {
		if e.Deleted {
			if now-e.Ts > TombstoneAge.Milliseconds() {
				delete(s.m, id)
			}
		} else {
			live = append(live, id)
		}
	}
	if len(live) > MaxEntries {
		sort.Slice(live, func(i, j int) bool { return s.m[live[i]].Ts > s.m[live[j]].Ts })
		for _, id := range live[MaxEntries:] {
			delete(s.m, id)
		}
	}
}

// markDirty schedules a flush. Caller holds mu.
func (s *Store) markDirty() {
	s.dirty = true
	if s.path == "" || s.closed || s.timer != nil {
		return
	}
	s.timer = time.AfterFunc(flushDelay, func() {
		s.mu.Lock()
		s.timer = nil
		s.mu.Unlock()
		s.Flush()
	})
}

// Flush writes the file now when something changed.
func (s *Store) Flush() error {
	s.flushMu.Lock()
	defer s.flushMu.Unlock()
	s.mu.Lock()
	if !s.dirty || s.path == "" {
		s.mu.Unlock()
		return nil
	}
	s.dirty = false
	list := make([]Entry, 0, len(s.m))
	for _, e := range s.m {
		list = append(list, e)
	}
	s.mu.Unlock()
	sort.Slice(list, func(i, j int) bool { return list[i].At < list[j].At })
	data, err := json.Marshal(struct {
		Entries []Entry `json:"entries"`
	}{list})
	if err == nil {
		err = library.AtomicWrite(s.path, data)
	}
	if err != nil {
		s.mu.Lock()
		s.markDirty() // retry later
		s.mu.Unlock()
		s.logf("[progress] không lưu được %s: %v", s.path, err)
	}
	return err
}

// Close flushes and stops the timer.
func (s *Store) Close() {
	s.mu.Lock()
	s.closed = true
	if s.timer != nil {
		s.timer.Stop()
		s.timer = nil
	}
	s.mu.Unlock()
	s.Flush()
}
