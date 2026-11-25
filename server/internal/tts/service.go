package tts

import (
	"context"
	"crypto/rand"
	"crypto/sha1"
	"encoding/hex"
	"errors"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"
	"unicode"
	"unicode/utf8"
)

const (
	// MaxText is the longest text (in characters) one request may carry.
	MaxText = 3000
	// DefaultVoice is used when neither the request nor the config names one.
	DefaultVoice = "vi-VN-HoaiMyNeural"
	// DefaultMaxBytes caps the on-disk audio cache.
	DefaultMaxBytes = 2 << 30

	attempts   = 3
	concurrent = 2
)

var voiceRe = regexp.MustCompile(`^[A-Za-z]{2,3}-[A-Za-z]{2,4}-[A-Za-z0-9]+(Neural|Piper)$`)

// Error is a failure with the HTTP status the API should answer with.
type Error struct {
	Status int
	Code   string
	Msg    string
}

func (e *Error) Error() string { return e.Msg }

// VoiceInfo is one entry of /api/voices.
type VoiceInfo struct {
	ID     string `json:"id"`
	Name   string `json:"name"`
	Gender string `json:"gender"`
}

// Fallback is the voice list used when the service cannot be asked.
var Fallback = []VoiceInfo{
	{ID: "vi-VN-HoaiMyNeural", Name: "Hoài My (nữ)", Gender: "Female"},
	{ID: "vi-VN-NamMinhNeural", Name: "Nam Minh (nam)", Gender: "Male"},
}

// ServiceOptions configures a Service.
type ServiceOptions struct {
	Engine       Engine // nil = TTS unavailable
	Dir          string // <cache>/tts
	DefaultVoice string
	MaxBytes     int64 // cache size cap; 0 = DefaultMaxBytes, <0 = unlimited
	Logf         func(format string, args ...any)

	backoff time.Duration // tests: base delay between attempts (default 1.2 s)
}

type call struct {
	done    chan struct{}
	path    string
	err     error
	waiters int
	cancel  context.CancelFunc
}

// Service adds validation, an on-disk cache, per-key de-duplication, a
// concurrency limit and retries on top of an Engine.
type Service struct {
	eng      Engine
	dir      string
	voice    string
	maxBytes int64
	logf     func(string, ...any)
	backoff  time.Duration
	sem      chan struct{}

	mu       sync.Mutex
	calls    map[string]*call
	total    int64 // bytes in the cache; -1 until measured
	evicting bool

	vmu      sync.Mutex
	voices   []VoiceInfo
	voicesAt time.Time
	voicesOK bool
}

// NewService creates the service.
func NewService(o ServiceOptions) *Service {
	s := &Service{eng: o.Engine, dir: o.Dir, voice: o.DefaultVoice, maxBytes: o.MaxBytes, logf: o.Logf, backoff: o.backoff,
		sem: make(chan struct{}, concurrent), calls: map[string]*call{}, total: -1}
	if !voiceRe.MatchString(s.voice) {
		s.voice = DefaultVoice
	}
	if s.maxBytes == 0 {
		s.maxBytes = DefaultMaxBytes
	}
	if s.logf == nil {
		s.logf = func(string, ...any) {}
	}
	if s.backoff == 0 {
		s.backoff = 1200 * time.Millisecond
	}
	return s
}

// Available reports whether an engine is present.
func (s *Service) Available() bool { return s != nil && s.eng != nil }

// DefaultVoice returns the configured default voice.
func (s *Service) DefaultVoice() string {
	if s == nil {
		return DefaultVoice
	}
	return s.voice
}

func clamp(v, lo, hi int) int {
	if v < lo {
		return lo
	}
	if v > hi {
		return hi
	}
	return v
}

// CacheKey is the cache name of a request (after clamping).
func CacheKey(text, voice string, rate, pitch int) string {
	h := sha1.Sum([]byte(fmt.Sprintf("%s|%d|%d|%s", voice, rate, pitch, text)))
	return hex.EncodeToString(h[:])
}

// Speak returns the path of the MP3 for text, synthesising it on a cache miss.
func (s *Service) Speak(ctx context.Context, text, voice string, rate, pitch int) (string, error) {
	text = strings.TrimFunc(text, unicode.IsSpace)
	if text == "" {
		return "", &Error{http.StatusBadRequest, "empty_text", "text rỗng"}
	}
	if utf8.RuneCountInString(text) > MaxText {
		return "", &Error{http.StatusRequestEntityTooLarge, "text_too_long", "text quá dài"}
	}
	if voice == "" {
		voice = s.DefaultVoice()
	}
	if !voiceRe.MatchString(voice) {
		return "", &Error{http.StatusBadRequest, "bad_voice", "voice không hợp lệ"}
	}
	if !s.Available() {
		return "", &Error{http.StatusServiceUnavailable, "tts_unavailable", "máy chủ này chưa có giọng đọc Edge"}
	}
	rate, pitch = clamp(rate, -50, 100), clamp(pitch, -50, 50)
	key := CacheKey(text, voice, rate, pitch)
	file := filepath.Join(s.dir, key[:2], key+Ext(voice))
	if st, err := os.Stat(file); err == nil && st.Mode().IsRegular() && st.Size() > 0 {
		if time.Since(st.ModTime()) > time.Hour {
			now := time.Now()
			os.Chtimes(file, now, now) // keeps recently used audio away from eviction
		}
		return file, nil
	}
	for {
		s.mu.Lock()
		c := s.calls[key]
		if c == nil {
			cctx, cancel := context.WithCancel(context.Background())
			c = &call{done: make(chan struct{}), cancel: cancel}
			s.calls[key] = c
			go s.run(cctx, c, key, file, text, voice, rate, pitch)
		}
		c.waiters++
		s.mu.Unlock()
		select {
		case <-c.done:
			if errors.Is(c.err, context.Canceled) && ctx.Err() == nil {
				continue // the flight was abandoned by its other listeners just as we joined
			}
			return c.path, c.err
		case <-ctx.Done():
			s.mu.Lock()
			c.waiters--
			if c.waiters == 0 {
				c.cancel() // nobody is listening any more: stop the synthesis
			}
			s.mu.Unlock()
			return "", ctx.Err()
		}
	}
}

func (s *Service) run(ctx context.Context, c *call, key, file, text, voice string, rate, pitch int) {
	defer func() {
		c.cancel()
		s.mu.Lock()
		delete(s.calls, key)
		s.mu.Unlock()
		close(c.done)
	}()
	select {
	case s.sem <- struct{}{}:
		defer func() { <-s.sem }()
	case <-ctx.Done():
		c.err = ctx.Err()
		return
	}
	var last error
	for i := 1; i <= attempts; i++ {
		data, err := s.eng.Synthesize(ctx, text, voice, rate, pitch)
		if err == nil && len(data) == 0 {
			err = errors.New("dịch vụ trả về rỗng")
		}
		if err == nil {
			if werr := atomicWrite(file, data); werr != nil {
				c.err = &Error{http.StatusServiceUnavailable, "tts_failed", "TTS lỗi: không ghi được cache"}
				s.logf("[tts] không ghi được cache: %v", werr)
				return
			}
			c.path = file
			s.added(int64(len(data)))
			return
		}
		if ctx.Err() != nil {
			c.err = ctx.Err()
			return
		}
		var te *Error
		if errors.As(err, &te) {
			c.err = te // the engine rejected the input: asking again cannot help
			return
		}
		last = err
		if i < attempts {
			t := time.NewTimer(s.backoff * time.Duration(i))
			select {
			case <-t.C:
			case <-ctx.Done():
				t.Stop()
				c.err = ctx.Err()
				return
			}
		}
	}
	c.err = &Error{http.StatusServiceUnavailable, "tts_failed", "TTS lỗi: " + last.Error()}
}

func atomicWrite(path string, data []byte) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	var rnd [6]byte
	rand.Read(rnd[:])
	tmp := fmt.Sprintf("%s.%d%s.tmp", strings.TrimSuffix(path, filepath.Ext(path)), os.Getpid(), hex.EncodeToString(rnd[:]))
	if err := os.WriteFile(tmp, data, 0o644); err != nil {
		os.Remove(tmp)
		return err
	}
	var err error
	for i := 0; i < 5; i++ {
		if err = os.Rename(tmp, path); err == nil {
			return nil
		}
		time.Sleep(time.Duration(20*(i+1)) * time.Millisecond)
	}
	os.Remove(tmp)
	return err
}

type cacheFile struct {
	path string
	size int64
	mod  time.Time
}

func (s *Service) scan() (files []cacheFile, total int64) {
	filepath.WalkDir(s.dir, func(p string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() || !(strings.HasSuffix(p, ".mp3") || strings.HasSuffix(p, ".wav")) {
			return nil
		}
		if info, err := d.Info(); err == nil {
			files = append(files, cacheFile{p, info.Size(), info.ModTime()})
			total += info.Size()
		}
		return nil
	})
	return files, total
}

// added accounts for a new cache file and evicts the least recently used
// audio when the cache grows past its cap.
func (s *Service) added(n int64) {
	if s.maxBytes < 0 {
		return
	}
	s.mu.Lock()
	if s.total >= 0 {
		s.total += n
	}
	need := (s.total < 0 || s.total > s.maxBytes) && !s.evicting
	if need {
		s.evicting = true
	}
	s.mu.Unlock()
	if !need {
		return
	}
	go func() {
		files, total := s.scan()
		if total > s.maxBytes {
			sort.Slice(files, func(i, j int) bool { return files[i].mod.Before(files[j].mod) })
			target := s.maxBytes / 10 * 9
			for _, f := range files {
				if total <= target {
					break
				}
				if time.Since(f.mod) < time.Minute {
					continue // may be on its way to a client
				}
				if os.Remove(f.path) == nil {
					total -= f.size
				}
			}
		}
		s.mu.Lock()
		s.total, s.evicting = total, false
		s.mu.Unlock()
	}()
}

// Voices returns the voices offered to readers: Vietnamese first, then the
// multilingual ones. edge is false when there is no engine.
func (s *Service) Voices(ctx context.Context) (list []VoiceInfo, edge bool) {
	if !s.Available() {
		return []VoiceInfo{}, false
	}
	s.vmu.Lock()
	defer s.vmu.Unlock()
	if s.voices != nil && (s.voicesOK || time.Since(s.voicesAt) < time.Minute) {
		return s.voices, true
	}
	c, cancel := context.WithTimeout(ctx, 20*time.Second)
	defer cancel()
	all, err := s.eng.Voices(c)
	var vi, multi []VoiceInfo
	if len(all) > 0 {
		for _, v := range all {
			if !voiceRe.MatchString(v.ShortName) {
				continue
			}
			name := v.FriendlyName
			if name == "" {
				name = v.ShortName
			}
			item := VoiceInfo{ID: v.ShortName, Name: name, Gender: v.Gender}
			if strings.HasPrefix(v.Locale, "vi-") {
				vi = append(vi, item)
			} else if strings.Contains(v.ShortName, "Multilingual") {
				multi = append(multi, item)
			}
		}
	}
	if out := append(vi, multi...); len(out) > 0 {
		s.voices, s.voicesOK = out, err == nil // partial lists (Edge down, Piper up) are retried in a minute
	} else {
		s.voices, s.voicesOK = Fallback, false // asked again in a minute
		if err != nil && ctx.Err() == nil {
			s.logf("[tts] không lấy được danh sách giọng: %v", err)
		}
	}
	s.voicesAt = time.Now()
	return s.voices, true
}
