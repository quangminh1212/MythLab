// Package userlib keeps the per-account data that syncs through Google
// sign-in: followed stories and bookmarks (the "library"), plus one progress
// store per user. Entries merge last-writer-wins and persist atomically.
package userlib

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
	"sync"
	"time"

	"mythlab/internal/library"
	"mythlab/internal/progress"
)

const (
	KindFollow   = "follow"
	KindBookmark = "bookmark"

	MaxFollows   = 500
	MaxBookmarks = 1000
	// TombstoneAge is how long a deletion is remembered.
	TombstoneAge = 60 * 24 * time.Hour
	// MaxSkew is how far in the future a client timestamp may lie.
	MaxSkew = 5 * time.Minute
	// MaxData is the size limit of an entry's data object.
	MaxData = 4 << 10

	maxID      = 600
	flushDelay = 2 * time.Second
)

// Entry is one followed story or bookmark.
type Entry struct {
	Kind    string          `json:"kind"`
	ID      string          `json:"id"` // follow: "source|key"; bookmark: the client's bookmark id
	Ts      int64           `json:"ts"`
	At      int64           `json:"at,omitempty"` // server stamp; drives ?since=
	Deleted bool            `json:"deleted,omitempty"`
	Data    json.RawMessage `json:"data,omitempty"`
}

func (e Entry) key() string { return e.Kind + "\x00" + e.ID }

// Sanitize bounds an entry from a client; ok is false when it cannot be used.
func Sanitize(e Entry, now int64) (Entry, bool) {
	if (e.Kind != KindFollow && e.Kind != KindBookmark) || e.ID == "" || len(e.ID) > maxID || e.Ts <= 0 {
		return e, false
	}
	if max := now + MaxSkew.Milliseconds(); e.Ts > max {
		e.Ts = max
	}
	e.At = 0
	if e.Deleted {
		return Entry{Kind: e.Kind, ID: e.ID, Ts: e.Ts, Deleted: true}, true
	}
	d := bytes.TrimSpace(e.Data)
	if len(d) == 0 || d[0] != '{' || len(d) > MaxData || !json.Valid(d) {
		return e, false
	}
	var buf bytes.Buffer
	if err := json.Compact(&buf, d); err != nil {
		return e, false
	}
	e.Data = json.RawMessage(buf.Bytes())
	return e, true
}

// Merge combines two versions of one entry: the newer ts wins; on a tie a
// live entry beats a tombstone, and between two live ones the greater data
// does (so every replica converges).
func Merge(a, b Entry) Entry {
	switch {
	case b.Ts > a.Ts:
		return b
	case b.Ts < a.Ts:
		return a
	case a.Deleted != b.Deleted:
		if a.Deleted {
			return b
		}
		return a
	case bytes.Compare(b.Data, a.Data) > 0:
		return b
	}
	return a
}

// Store is the in-memory map with debounced, atomic persistence.
type Store struct {
	path string
	logf func(string, ...any)
	now  func() int64

	flushMu sync.Mutex
	mu      sync.Mutex
	m       map[string]Entry
	lastAt  int64
	dirty   bool
	timer   *time.Timer
	closed  bool
}

// Open loads path (missing or unreadable = empty). An empty path keeps
// everything in memory.
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
			logf("[userlib] không đọc được %s: %v", path, err)
		}
		return s
	}
	var f struct {
		Entries []Entry `json:"entries"`
	}
	if err := json.Unmarshal(data, &f); err != nil {
		logf("[userlib] %s hỏng, bỏ qua: %v", path, err)
		return s
	}
	for _, e := range f.Entries {
		if e.ID != "" && (e.Kind == KindFollow || e.Kind == KindBookmark) {
			s.m[e.key()] = e
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
		k := e.key()
		cur, had := s.m[k]
		merged := e
		if had {
			merged = Merge(cur, e)
		}
		merged.At = cur.At
		if !had || !sameEntry(cur, merged) {
			merged.At = s.stamp()
			s.m[k] = merged
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
	return a.Kind == b.Kind && a.ID == b.ID && a.Ts == b.Ts && a.Deleted == b.Deleted && bytes.Equal(a.Data, b.Data)
}

// prune drops old tombstones and the oldest live entries over each kind's cap.
func (s *Store) prune(now int64) {
	live := map[string][]string{}
	for k, e := range s.m {
		if e.Deleted {
			if now-e.Ts > TombstoneAge.Milliseconds() {
				delete(s.m, k)
			}
		} else {
			live[e.Kind] = append(live[e.Kind], k)
		}
	}
	for kind, max := range map[string]int{KindFollow: MaxFollows, KindBookmark: MaxBookmarks} {
		keys := live[kind]
		if len(keys) <= max {
			continue
		}
		sort.Slice(keys, func(i, j int) bool { return s.m[keys[i]].Ts > s.m[keys[j]].Ts })
		for _, k := range keys[max:] {
			delete(s.m, k)
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
		s.markDirty()
		s.mu.Unlock()
		s.logf("[userlib] không lưu được %s: %v", s.path, err)
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

// UserKey is the directory name of a Google subject: the hex SHA-256 of it.
func UserKey(sub string) string {
	sum := sha256.Sum256([]byte(sub))
	return hex.EncodeToString(sum[:])
}

// Manager opens the per-user stores lazily under <dir>/<UserKey>/.
type Manager struct {
	dir  string
	logf func(string, ...any)

	mu   sync.Mutex
	prog map[string]*progress.Store
	lib  map[string]*Store
}

// NewManager keeps the stores under dir; "" keeps them in memory.
func NewManager(dir string, logf func(string, ...any)) *Manager {
	return &Manager{dir: dir, logf: logf, prog: map[string]*progress.Store{}, lib: map[string]*Store{}}
}

func (m *Manager) path(sub, file string) string {
	if m.dir == "" {
		return ""
	}
	return filepath.Join(m.dir, UserKey(sub), file)
}

// Progress is the reading progress store of a user.
func (m *Manager) Progress(sub string) *progress.Store {
	m.mu.Lock()
	defer m.mu.Unlock()
	k := UserKey(sub)
	st := m.prog[k]
	if st == nil {
		st = progress.Open(m.path(sub, "progress.json"), m.logf)
		m.prog[k] = st
	}
	return st
}

// Library is the follows and bookmarks store of a user.
func (m *Manager) Library(sub string) *Store {
	m.mu.Lock()
	defer m.mu.Unlock()
	k := UserKey(sub)
	st := m.lib[k]
	if st == nil {
		st = Open(m.path(sub, "library.json"), m.logf)
		m.lib[k] = st
	}
	return st
}

// Close flushes every open store.
func (m *Manager) Close() {
	m.mu.Lock()
	defer m.mu.Unlock()
	for _, p := range m.prog {
		p.Close()
	}
	for _, l := range m.lib {
		l.Close()
	}
}
