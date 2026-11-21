package tts

import (
	"context"
	"crypto/sha1"
	"encoding/hex"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

type fakeEngine struct {
	calls     atomic.Int64
	active    atomic.Int64
	maxActive atomic.Int64
	failFirst int64
	block     chan struct{}
	empty     bool
	voicesErr error
	lastRate  atomic.Int64
	lastPitch atomic.Int64
	cancelled atomic.Int64
}

func (f *fakeEngine) Synthesize(ctx context.Context, text, voice string, rate, pitch int) ([]byte, error) {
	n := f.calls.Add(1)
	a := f.active.Add(1)
	defer f.active.Add(-1)
	for {
		m := f.maxActive.Load()
		if a <= m || f.maxActive.CompareAndSwap(m, a) {
			break
		}
	}
	f.lastRate.Store(int64(rate))
	f.lastPitch.Store(int64(pitch))
	if f.block != nil {
		select {
		case <-f.block:
		case <-ctx.Done():
			f.cancelled.Add(1)
			return nil, ctx.Err()
		}
	}
	if n <= f.failFirst {
		return nil, errors.New("boom")
	}
	if f.empty {
		return nil, nil
	}
	return []byte("MP3:" + voice + ":" + text), nil
}

func (f *fakeEngine) Voices(context.Context) ([]Voice, error) {
	if f.voicesErr != nil {
		return nil, f.voicesErr
	}
	return []Voice{
		{ShortName: "en-US-AvaMultilingualNeural", Locale: "en-US", Gender: "Female", FriendlyName: "Ava"},
		{ShortName: "en-US-GuyNeural", Locale: "en-US", Gender: "Male", FriendlyName: "Guy"},
		{ShortName: "vi-VN-NamMinhNeural", Locale: "vi-VN", Gender: "Male"},
		{ShortName: "vi-VN-HoaiMyNeural", Locale: "vi-VN", Gender: "Female", FriendlyName: "Microsoft HoaiMy"},
	}, nil
}

func newSvc(t *testing.T, e Engine) *Service {
	return NewService(ServiceOptions{Engine: e, Dir: t.TempDir(), backoff: time.Millisecond, Logf: t.Logf})
}

func wantErr(t *testing.T, err error, status int) {
	t.Helper()
	var e *Error
	if !errors.As(err, &e) || e.Status != status {
		t.Fatalf("want status %d, got %v", status, err)
	}
}

func TestSpeakValidationAndCache(t *testing.T) {
	f := &fakeEngine{}
	s := newSvc(t, f)
	ctx := context.Background()
	_, err := s.Speak(ctx, "  \n ", "", 0, 0)
	wantErr(t, err, 400)
	_, err = s.Speak(ctx, strings.Repeat("ă", MaxText+1), "", 0, 0)
	wantErr(t, err, 413)
	for _, v := range []string{"x", "vi-VN-HoaiMy", "vi-VN-HoaiMyNeural;rm", "../../etc", "vi-VN-HoaiMyNeural\n"} {
		_, err = s.Speak(ctx, "a", v, 0, 0)
		wantErr(t, err, 400)
	}
	if f.calls.Load() != 0 {
		t.Fatal("invalid requests must not reach the engine")
	}

	p, err := s.Speak(ctx, " Xin chào. ", "", 500, -500)
	if err != nil {
		t.Fatal(err)
	}
	if f.lastRate.Load() != 100 || f.lastPitch.Load() != -50 {
		t.Fatalf("clamping: rate %d pitch %d", f.lastRate.Load(), f.lastPitch.Load())
	}
	h := sha1.Sum([]byte("vi-VN-HoaiMyNeural|100|-50|Xin chào."))
	key := hex.EncodeToString(h[:])
	if want := filepath.Join(s.dir, key[:2], key+".mp3"); p != want {
		t.Fatalf("cache path %s, want %s", p, want)
	}
	if b, _ := os.ReadFile(p); string(b) != "MP3:vi-VN-HoaiMyNeural:Xin chào." {
		t.Fatalf("content %q", b)
	}
	if _, err := s.Speak(ctx, "Xin chào.", "vi-VN-HoaiMyNeural", 100, -50); err != nil || f.calls.Load() != 1 {
		t.Fatalf("second request must hit the cache (calls=%d, err=%v)", f.calls.Load(), err)
	}
	if strings.Repeat("ă", MaxText) != "" {
		if _, err := s.Speak(ctx, strings.Repeat("ă", MaxText), "", 0, 0); err != nil {
			t.Fatalf("3000 characters must be accepted: %v", err)
		}
	}
	left, _ := filepath.Glob(filepath.Join(s.dir, "*", "*.tmp"))
	if len(left) != 0 {
		t.Fatalf("temp files left: %v", left)
	}

	var nilSvc = NewService(ServiceOptions{Dir: t.TempDir()})
	_, err = nilSvc.Speak(ctx, "a", "", 0, 0)
	wantErr(t, err, 503)
	if v, edge := nilSvc.Voices(ctx); edge || len(v) != 0 || v == nil {
		t.Fatalf("no engine: %v %v", v, edge)
	}
}

func TestSpeakRetryAndFailure(t *testing.T) {
	f := &fakeEngine{failFirst: 2}
	s := newSvc(t, f)
	if _, err := s.Speak(context.Background(), "a", "", 0, 0); err != nil || f.calls.Load() != 3 {
		t.Fatalf("third attempt must succeed: %v calls=%d", err, f.calls.Load())
	}
	f2 := &fakeEngine{failFirst: 99}
	s2 := newSvc(t, f2)
	_, err := s2.Speak(context.Background(), "a", "", 0, 0)
	wantErr(t, err, 503)
	if f2.calls.Load() != 3 {
		t.Fatalf("want 3 attempts, got %d", f2.calls.Load())
	}
	f3 := &fakeEngine{empty: true}
	s3 := newSvc(t, f3)
	_, err = s3.Speak(context.Background(), "a", "", 0, 0)
	wantErr(t, err, 503)
}

func TestSpeakDedupeLimitAndCancel(t *testing.T) {
	f := &fakeEngine{block: make(chan struct{})}
	s := newSvc(t, f)
	var wg sync.WaitGroup
	for i := 0; i < 5; i++ { // five listeners, one text
		wg.Add(1)
		go func() { defer wg.Done(); s.Speak(context.Background(), "same", "", 0, 0) }()
	}
	for _, text := range []string{"b", "c", "d"} { // four keys in total, two may run
		wg.Add(1)
		go func(x string) { defer wg.Done(); s.Speak(context.Background(), x, "", 0, 0) }(text)
	}
	time.Sleep(150 * time.Millisecond)
	if n := f.calls.Load(); n != 2 {
		t.Fatalf("want 2 concurrent syntheses, got %d", n)
	}
	close(f.block)
	wg.Wait()
	if n, m := f.calls.Load(), f.maxActive.Load(); n != 4 || m > 2 {
		t.Fatalf("calls=%d (want 4) maxActive=%d (want <=2)", n, m)
	}

	// the request context aborts the synthesis when the last listener leaves
	f2 := &fakeEngine{block: make(chan struct{})}
	s2 := newSvc(t, f2)
	ctx, cancel := context.WithCancel(context.Background())
	errc := make(chan error, 1)
	go func() { _, err := s2.Speak(ctx, "x", "", 0, 0); errc <- err }()
	time.Sleep(50 * time.Millisecond)
	cancel()
	if err := <-errc; !errors.Is(err, context.Canceled) {
		t.Fatalf("want context.Canceled, got %v", err)
	}
	deadline := time.Now().Add(2 * time.Second)
	for f2.cancelled.Load() == 0 && time.Now().Before(deadline) {
		time.Sleep(5 * time.Millisecond)
	}
	if f2.cancelled.Load() != 1 {
		t.Fatal("the engine call must be cancelled")
	}
}

func TestEviction(t *testing.T) {
	f := &fakeEngine{}
	s := NewService(ServiceOptions{Engine: f, Dir: t.TempDir(), MaxBytes: 400, backoff: time.Millisecond})
	old := time.Now().Add(-2 * time.Hour)
	var paths []string
	for i := 0; i < 6; i++ {
		p, err := s.Speak(context.Background(), strings.Repeat("x", 80)+string(rune('a'+i)), "", 0, 0)
		if err != nil {
			t.Fatal(err)
		}
		os.Chtimes(p, old.Add(time.Duration(i)*time.Minute), old.Add(time.Duration(i)*time.Minute))
		paths = append(paths, p)
	}
	if _, err := s.Speak(context.Background(), "trigger", "", 0, 0); err != nil {
		t.Fatal(err)
	}
	deadline := time.Now().Add(3 * time.Second)
	for time.Now().Before(deadline) {
		if _, err := os.Stat(paths[0]); err != nil {
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
	if _, err := os.Stat(paths[0]); err == nil {
		t.Fatal("the oldest file must be evicted")
	}
	if _, err := os.Stat(paths[5]); err != nil {
		t.Fatal("the newest old file must survive")
	}
	_, total := s.scan()
	if total > 400 {
		t.Fatalf("cache still over the cap: %d", total)
	}
}

func TestVoices(t *testing.T) {
	s := newSvc(t, &fakeEngine{})
	v, edge := s.Voices(context.Background())
	if !edge || len(v) != 3 || v[0].ID != "vi-VN-NamMinhNeural" || v[0].Name != "vi-VN-NamMinhNeural" ||
		v[1].Name != "Microsoft HoaiMy" || v[2].ID != "en-US-AvaMultilingualNeural" {
		t.Fatalf("voices: %+v", v)
	}
	s2 := newSvc(t, &fakeEngine{voicesErr: errors.New("offline")})
	v, edge = s2.Voices(context.Background())
	if !edge || len(v) != 2 || v[0].Name != "Hoài My (nữ)" || s2.voicesOK {
		t.Fatalf("fallback: %+v", v)
	}
}
