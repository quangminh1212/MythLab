package auth

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"os"
	"sort"
	"sync"
	"time"

	"mythlab/internal/library"
)

const (
	// SessionTTL is the sliding lifetime of a session.
	SessionTTL = 90 * 24 * time.Hour
	// MaxSessionsPerUser: signing in on an 11th device drops the oldest session.
	MaxSessionsPerUser = 10

	slideEvery = time.Hour // a lookup extends the expiry (and rewrites the file) at most this often
	tokenBytes = 32
)

// User is the Google account behind a session.
type User struct {
	ID      string `json:"id"` // Google "sub"
	Name    string `json:"name"`
	Email   string `json:"email"`
	Picture string `json:"picture"`
}

type sessionRec struct {
	Hash    string `json:"h"` // hex SHA-256 of the token
	User    string `json:"u"` // User.ID
	Created int64  `json:"c"` // ms
	Expires int64  `json:"e"` // ms
}

// Sessions is the persistent session store (users.json).
type Sessions struct {
	path string
	logf func(string, ...any)
	now  func() time.Time

	mu    sync.Mutex
	users map[string]User
	sess  map[string]*sessionRec // by hash
	dirty bool
}

// OpenSessions loads path (missing or broken = empty). An empty path keeps
// everything in memory. now may be nil.
func OpenSessions(path string, logf func(string, ...any), now func() time.Time) *Sessions {
	if logf == nil {
		logf = func(string, ...any) {}
	}
	if now == nil {
		now = time.Now
	}
	s := &Sessions{path: path, logf: logf, now: now, users: map[string]User{}, sess: map[string]*sessionRec{}}
	if path == "" {
		return s
	}
	data, err := os.ReadFile(path)
	if err != nil {
		if !os.IsNotExist(err) {
			logf("[auth] không đọc được %s: %v", path, err)
		}
		return s
	}
	var f struct {
		Users    []User       `json:"users"`
		Sessions []sessionRec `json:"sessions"`
	}
	if err := json.Unmarshal(data, &f); err != nil {
		logf("[auth] %s hỏng, bỏ qua: %v", path, err)
		return s
	}
	for _, u := range f.Users {
		if u.ID != "" {
			s.users[u.ID] = u
		}
	}
	nowMs := now().UnixMilli()
	for i := range f.Sessions {
		r := f.Sessions[i]
		if _, ok := s.users[r.User]; ok && r.Hash != "" && r.Expires > nowMs {
			s.sess[r.Hash] = &r
		}
	}
	return s
}

func hashToken(token string) string {
	sum := sha256.Sum256([]byte(token))
	return hex.EncodeToString(sum[:])
}

// Create starts a session for u (refreshing the stored profile) and returns
// the opaque token and its absolute expiry in ms. The token itself is never stored.
func (s *Sessions) Create(u User) (token string, expires int64, err error) {
	var b [tokenBytes]byte
	if _, err = rand.Read(b[:]); err != nil {
		return "", 0, err
	}
	token = base64.RawURLEncoding.EncodeToString(b[:])
	s.mu.Lock()
	defer s.mu.Unlock()
	now := s.now().UnixMilli()
	s.purge(now)
	s.users[u.ID] = u
	var mine []*sessionRec
	for _, r := range s.sess {
		if r.User == u.ID {
			mine = append(mine, r)
		}
	}
	if len(mine) >= MaxSessionsPerUser {
		sort.Slice(mine, func(i, j int) bool { return mine[i].Created < mine[j].Created })
		for _, r := range mine[:len(mine)-MaxSessionsPerUser+1] {
			delete(s.sess, r.Hash)
		}
	}
	h := hashToken(token)
	expires = now + SessionTTL.Milliseconds()
	s.sess[h] = &sessionRec{Hash: h, User: u.ID, Created: now, Expires: expires}
	s.persist()
	return token, expires, nil
}

// Lookup returns the user of a live session and slides its expiry.
func (s *Sessions) Lookup(token string) (User, bool) {
	if len(token) < 20 || len(token) > 200 {
		return User{}, false
	}
	h := hashToken(token)
	s.mu.Lock()
	defer s.mu.Unlock()
	r, ok := s.sess[h]
	if !ok {
		return User{}, false
	}
	now := s.now().UnixMilli()
	if r.Expires <= now {
		delete(s.sess, h)
		s.persist()
		return User{}, false
	}
	u, ok := s.users[r.User]
	if !ok {
		return User{}, false
	}
	if next := now + SessionTTL.Milliseconds(); next-r.Expires >= slideEvery.Milliseconds() {
		r.Expires = next
		s.persist()
	}
	return u, true
}

// Revoke ends the session of token and reports whether it existed.
func (s *Sessions) Revoke(token string) bool {
	h := hashToken(token)
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.sess[h]; !ok {
		return false
	}
	delete(s.sess, h)
	s.persist()
	return true
}

// Count is the number of live sessions of a user.
func (s *Sessions) Count(userID string) int {
	s.mu.Lock()
	defer s.mu.Unlock()
	n := 0
	now := s.now().UnixMilli()
	for _, r := range s.sess {
		if r.User == userID && r.Expires > now {
			n++
		}
	}
	return n
}

// purge drops expired sessions and users without any. Caller holds mu.
func (s *Sessions) purge(now int64) {
	live := map[string]bool{}
	for h, r := range s.sess {
		if r.Expires <= now {
			delete(s.sess, h)
		} else {
			live[r.User] = true
		}
	}
	for id := range s.users {
		if !live[id] {
			delete(s.users, id)
		}
	}
}

// persist writes the file; on failure the state stays dirty for Flush. Caller holds mu.
func (s *Sessions) persist() {
	s.dirty = true
	if s.path == "" {
		return
	}
	f := struct {
		Users    []User       `json:"users"`
		Sessions []sessionRec `json:"sessions"`
	}{Users: []User{}, Sessions: []sessionRec{}}
	for _, u := range s.users {
		f.Users = append(f.Users, u)
	}
	for _, r := range s.sess {
		f.Sessions = append(f.Sessions, *r)
	}
	sort.Slice(f.Users, func(i, j int) bool { return f.Users[i].ID < f.Users[j].ID })
	sort.Slice(f.Sessions, func(i, j int) bool { return f.Sessions[i].Created < f.Sessions[j].Created })
	data, err := json.Marshal(f)
	if err == nil {
		err = library.AtomicWrite(s.path, data)
	}
	if err != nil {
		s.logf("[auth] không lưu được %s: %v", s.path, err)
		return
	}
	s.dirty = false
}

// Flush retries a failed write.
func (s *Sessions) Flush() {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.dirty {
		s.persist()
	}
}

// Close flushes.
func (s *Sessions) Close() { s.Flush() }
