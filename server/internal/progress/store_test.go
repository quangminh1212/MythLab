package progress

import (
	"fmt"
	"path/filepath"
	"sync"
	"testing"
	"time"
	"unicode/utf8"
)

func e(src, key string, ts int64, idx, maxIdx int) Entry {
	return Entry{Source: src, Key: key, Ts: ts, Idx: idx, MaxIdx: maxIdx}
}

func TestMerge(t *testing.T) {
	// newer ts wins, maxIdx is max-merged
	m := Merge(e("s", "k", 100, 2, 5), e("s", "k", 200, 1, 1))
	if m.Ts != 200 || m.Idx != 1 || m.MaxIdx != 5 {
		t.Fatalf("newer wins: %+v", m)
	}
	// tie: larger maxIdx wins; symmetric
	a, b := e("s", "k", 100, 1, 3), e("s", "k", 100, 2, 4)
	if x, y := Merge(a, b), Merge(b, a); x.Idx != 2 || y.Idx != 2 {
		t.Fatalf("tie: %+v %+v", x, y)
	}
	// listen follows the winner, falls back to the other side
	a = e("s", "k", 100, 0, 0)
	a.Listen = &Listen{Idx: 3, Para: 4}
	b = e("s", "k", 200, 0, 0)
	if m := Merge(a, b); m.Listen == nil || m.Listen.Idx != 3 {
		t.Fatalf("listen fallback: %+v", m)
	}
	b.Listen = &Listen{Idx: 9}
	if m := Merge(a, b); m.Listen.Idx != 9 {
		t.Fatalf("listen newer: %+v", m)
	}
	// tombstones
	d := Entry{Source: "s", Key: "k", Ts: 300, Deleted: true}
	if m := Merge(e("s", "k", 200, 1, 4), d); !m.Deleted || m.MaxIdx != 0 {
		t.Fatalf("tombstone wins: %+v", m)
	}
	d.Ts = 100
	if m := Merge(e("s", "k", 200, 1, 4), d); m.Deleted || m.MaxIdx != 4 {
		t.Fatalf("older tombstone loses: %+v", m)
	}
}

func TestSanitizeClampsTs(t *testing.T) {
	now := int64(1_000_000)
	got, ok := Sanitize(e("s", "k", now+int64(time.Hour/time.Millisecond), 0, 0), now)
	if !ok || got.Ts != now+MaxSkew.Milliseconds() {
		t.Fatalf("clamp: %+v %v", got, ok)
	}
	if _, ok := Sanitize(Entry{Source: "s"}, now); ok {
		t.Fatal("missing key accepted")
	}
	if g, _ := Sanitize(Entry{Source: "s", Key: "k", Ts: 5, Idx: -3, Genres: []string{"a", "b", "c", "d"}}, now); g.Idx != 0 || len(g.Genres) != 3 {
		t.Fatalf("bounds: %+v", g)
	}
}

func TestApplySinceAndPersist(t *testing.T) {
	path := filepath.Join(t.TempDir(), "sub", "progress.json")
	s := Open(path, nil)
	now := s.Now()
	s.Apply([]Entry{e("s", "a", now-1000, 1, 1), e("s", "b", now-900, 2, 2)})
	if got := s.Since(0); len(got) != 2 {
		t.Fatalf("since 0: %d", len(got))
	}
	cut := s.Now() + 5
	time.Sleep(10 * time.Millisecond)
	s.Apply([]Entry{e("s", "a", now-500, 3, 3)})
	if got := s.Since(cut); len(got) != 1 || got[0].Key != "a" || got[0].Idx != 3 {
		t.Fatalf("since: %+v", got)
	}
	// a stale write changes nothing and keeps its At
	before := s.Since(0)
	s.Apply([]Entry{e("s", "a", now-5000, 0, 0)})
	after := s.Since(0)
	if fmt.Sprint(before) != fmt.Sprint(after) {
		t.Fatalf("stale write changed state")
	}
	s.Close()
	r := Open(path, nil)
	if got := r.Since(0); len(got) != 2 {
		t.Fatalf("reload: %d", len(got))
	}
	r.Close()
}

func TestPruneCapAndTombstones(t *testing.T) {
	s := Open("", nil)
	now := s.Now()
	in := make([]Entry, 0, 200)
	for i := 0; i < MaxEntries+20; i++ {
		in = append(in, e("s", fmt.Sprint("k", i), now-int64(i)*1000-1000, 0, 0))
		if len(in) == 200 {
			s.Apply(in)
			in = in[:0]
		}
	}
	s.Apply(in)
	live := 0
	for _, x := range s.Since(0) {
		if !x.Deleted {
			live++
		}
	}
	if live != MaxEntries {
		t.Fatalf("cap: %d", live)
	}
	old := now - (TombstoneAge.Milliseconds() + 1000)
	s.Apply([]Entry{{Source: "s", Key: "gone", Ts: old, Deleted: true}, e("s", "new", now, 0, 0)})
	for _, x := range s.Since(0) {
		if x.Key == "gone" {
			t.Fatal("old tombstone kept")
		}
	}
}

func TestConcurrentApply(t *testing.T) {
	s := Open(filepath.Join(t.TempDir(), "p.json"), nil)
	now := s.Now()
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 50; i++ {
				s.Apply([]Entry{e("s", "same", now+int64(i), i, i), e("s", fmt.Sprint("k", g), now, 0, 0)})
				s.Since(0)
			}
		}(g)
	}
	wg.Wait()
	s.Close()
	for _, x := range s.Since(0) {
		if x.Key == "same" && x.Idx != 49 {
			t.Fatalf("same: %+v", x)
		}
	}
}

func TestSanitizeSourceAndUTF8(t *testing.T) {
	if _, ok := Sanitize(Entry{Source: "a|b", Key: "k", Ts: 5}, 10); ok {
		t.Fatal("source with | accepted (id collision)")
	}
	long := ""
	for len(long) < maxStr+10 {
		long += "ế"
	}
	g, ok := Sanitize(Entry{Source: "s", Key: "k", Ts: 5, Name: long}, 10)
	if !ok || !utf8.ValidString(g.Name) || len(g.Name) > maxStr {
		t.Fatalf("clip: %v %d", ok, len(g.Name))
	}
}
