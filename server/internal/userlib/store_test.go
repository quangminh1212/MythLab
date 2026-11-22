package userlib

import (
	"encoding/json"
	"fmt"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"mythlab/internal/progress"
)

func follow(id string, ts int64, data string) Entry {
	return Entry{Kind: KindFollow, ID: id, Ts: ts, Data: json.RawMessage(data)}
}

func tomb(kind, id string, ts int64) Entry { return Entry{Kind: kind, ID: id, Ts: ts, Deleted: true} }

func fixedClock(s *Store, ms int64) { s.now = func() int64 { return ms } }

func TestSanitize(t *testing.T) {
	now := int64(1_000_000_000)
	for name, e := range map[string]Entry{
		"no kind":      {ID: "a", Ts: 1, Data: json.RawMessage(`{}`)},
		"bad kind":     {Kind: "star", ID: "a", Ts: 1, Data: json.RawMessage(`{}`)},
		"no id":        {Kind: KindFollow, Ts: 1, Data: json.RawMessage(`{}`)},
		"long id":      {Kind: KindFollow, ID: strings.Repeat("x", 601), Ts: 1, Data: json.RawMessage(`{}`)},
		"no ts":        {Kind: KindFollow, ID: "a", Data: json.RawMessage(`{}`)},
		"no data":      {Kind: KindFollow, ID: "a", Ts: 1},
		"null data":    {Kind: KindFollow, ID: "a", Ts: 1, Data: json.RawMessage(`null`)},
		"array data":   {Kind: KindFollow, ID: "a", Ts: 1, Data: json.RawMessage(`[1]`)},
		"too big":      {Kind: KindFollow, ID: "a", Ts: 1, Data: json.RawMessage(`{"x":"` + strings.Repeat("a", MaxData) + `"}`)},
		"invalid json": {Kind: KindFollow, ID: "a", Ts: 1, Data: json.RawMessage(`{"x":`)},
	} {
		if _, ok := Sanitize(e, now); ok {
			t.Errorf("%s accepted", name)
		}
	}
	e, ok := Sanitize(Entry{Kind: KindBookmark, ID: "b", Ts: now + 3600_000, At: 99, Data: json.RawMessage(" {\n \"a\" : 1 } ")}, now)
	if !ok || e.Ts != now+MaxSkew.Milliseconds() || e.At != 0 || string(e.Data) != `{"a":1}` {
		t.Fatalf("clamp/compact: %+v", e)
	}
	e, ok = Sanitize(Entry{Kind: KindFollow, ID: "a", Ts: 5, Deleted: true, At: 7, Data: json.RawMessage(`{"big":1}`)}, now)
	if !ok || e.Data != nil || !e.Deleted || e.At != 0 {
		t.Fatalf("tombstone keeps only kind,id,ts,deleted: %+v", e)
	}
}

func TestMerge(t *testing.T) {
	a, b := follow("x", 10, `{"v":1}`), follow("x", 20, `{"v":2}`)
	if Merge(a, b).Ts != 20 || Merge(b, a).Ts != 20 {
		t.Fatal("newer ts must win")
	}
	if !Merge(tomb(KindFollow, "x", 30), b).Deleted {
		t.Fatal("newer tombstone must win")
	}
	if Merge(tomb(KindFollow, "x", 5), b).Deleted {
		t.Fatal("older tombstone must lose")
	}
	// tie: live beats tombstone, both orders
	if Merge(tomb(KindFollow, "x", 20), b).Deleted || Merge(b, tomb(KindFollow, "x", 20)).Deleted {
		t.Fatal("on a tie the live entry wins")
	}
	// tie between two live entries converges regardless of order
	c, d := follow("x", 20, `{"v":3}`), follow("x", 20, `{"v":2}`)
	if string(Merge(c, d).Data) != string(Merge(d, c).Data) {
		t.Fatal("tie not deterministic")
	}
}

func TestApplyAndSince(t *testing.T) {
	s := Open("", nil)
	fixedClock(s, 1_000_000)
	out := s.Apply([]Entry{
		follow("gh1|a", 100, `{"name":"A"}`),
		{Kind: KindBookmark, ID: "bm1", Ts: 100, Data: json.RawMessage(`{"text":"hi"}`)},
		{Kind: "junk", ID: "z", Ts: 1}, // dropped
	})
	if len(out) != 2 || out[0].At == 0 || out[1].At <= out[0].At {
		t.Fatalf("apply: %+v", out)
	}
	// the same id under another kind is a different entry
	s.Apply([]Entry{{Kind: KindBookmark, ID: "gh1|a", Ts: 100, Data: json.RawMessage(`{}`)}})
	if got := s.Since(0); len(got) != 3 {
		t.Fatalf("kinds must not collide: %d", len(got))
	}
	at := out[1].At
	// older write: no change, no new stamp
	res := s.Apply([]Entry{follow("gh1|a", 50, `{"name":"old"}`)})
	if string(res[0].Data) != `{"name":"A"}` || res[0].Ts != 100 {
		t.Fatalf("older write won: %+v", res[0])
	}
	if got := s.Since(at + 1); len(got) != 1 { // only the third entry
		t.Fatalf("since: %+v", got)
	}
	// newer write updates
	res = s.Apply([]Entry{follow("gh1|a", 200, `{"name":"B"}`)})
	if string(res[0].Data) != `{"name":"B"}` {
		t.Fatalf("newer write lost: %+v", res[0])
	}
	// tombstone then older revival
	s.Apply([]Entry{tomb(KindFollow, "gh1|a", 300)})
	res = s.Apply([]Entry{follow("gh1|a", 250, `{"name":"zombie"}`)})
	if !res[0].Deleted || res[0].Data != nil {
		t.Fatalf("revived by an older write: %+v", res[0])
	}
	res = s.Apply([]Entry{follow("gh1|a", 400, `{"name":"back"}`)})
	if res[0].Deleted {
		t.Fatalf("newer re-follow must win: %+v", res[0])
	}
}

func TestTombstoneExpiry(t *testing.T) {
	s := Open("", nil)
	now := int64(10_000_000_000_000)
	fixedClock(s, now)
	old := now - TombstoneAge.Milliseconds() - 1000
	recent := now - TombstoneAge.Milliseconds() + 3_600_000
	s.Apply([]Entry{tomb(KindFollow, "old", old), tomb(KindFollow, "recent", recent)})
	got := s.Since(0)
	if len(got) != 1 || got[0].ID != "recent" {
		t.Fatalf("tombstones: %+v", got)
	}
}

func TestCaps(t *testing.T) {
	s := Open("", nil)
	now := int64(5_000_000_000)
	fixedClock(s, now)
	var batch []Entry
	for i := 0; i < MaxFollows+20; i++ {
		batch = append(batch, follow(fmt.Sprintf("s|%d", i), now-int64(i)*1000-1, `{}`))
		if len(batch) == 100 {
			s.Apply(batch)
			batch = nil
		}
	}
	s.Apply(batch)
	for i := 0; i < MaxBookmarks+5; i++ {
		s.Apply([]Entry{{Kind: KindBookmark, ID: fmt.Sprint("b", i), Ts: now - int64(i)*1000 - 1, Data: json.RawMessage(`{}`)}})
	}
	var f, b int
	ids := map[string]bool{}
	for _, e := range s.Since(0) {
		switch e.Kind {
		case KindFollow:
			f++
			ids[e.ID] = true
		case KindBookmark:
			b++
		}
	}
	if f != MaxFollows || b != MaxBookmarks {
		t.Fatalf("follows %d bookmarks %d", f, b)
	}
	if !ids["s|0"] || ids[fmt.Sprintf("s|%d", MaxFollows+19)] {
		t.Fatal("the oldest follows must be dropped, the newest kept")
	}
}

func TestPersistence(t *testing.T) {
	path := filepath.Join(t.TempDir(), "u", "library.json")
	s := Open(path, nil)
	ts := time.Now().UnixMilli()
	s.Apply([]Entry{follow("a|b", ts, `{"name":"N"}`), tomb(KindBookmark, "bm", ts)})
	s.Close()
	s2 := Open(path, nil)
	got := s2.Since(0)
	if len(got) != 2 {
		t.Fatalf("reload: %+v", got)
	}
	prev := s2.Since(0)[1].At
	s2.Apply([]Entry{follow("c|d", 1, `{}`)})
	if last := s2.Since(prev + 1); len(last) != 1 || last[0].At <= prev {
		t.Fatal("stamps must keep increasing after a reload")
	}
	s2.Close()
	if err := s2.Flush(); err != nil {
		t.Fatal(err)
	}
}

func TestManagerIsolation(t *testing.T) {
	dir := t.TempDir()
	m := NewManager(dir, nil)
	now := time.Now().UnixMilli()
	pa := m.Progress("alice")
	pa.Apply([]progress.Entry{{Source: "s", Key: "k", Ts: now, Idx: 3}})
	if len(m.Progress("bob").Since(0)) != 0 {
		t.Fatal("bob sees alice's progress")
	}
	if len(m.Progress("alice").Since(0)) != 1 {
		t.Fatal("alice lost her progress")
	}
	m.Library("alice").Apply([]Entry{follow("s|k", now, `{}`)})
	if len(m.Library("bob").Since(0)) != 0 {
		t.Fatal("bob sees alice's library")
	}
	m.Close()

	// files live under users/<sha256(sub)>/, and a restart finds them again
	if UserKey("alice") == "alice" || len(UserKey("alice")) != 64 {
		t.Fatal("user key must be a sha256 hex")
	}
	if _, err := filepath.Glob(filepath.Join(dir, UserKey("alice"), "*.json")); err != nil {
		t.Fatal(err)
	}
	m2 := NewManager(dir, nil)
	defer m2.Close()
	if len(m2.Progress("alice").Since(0)) != 1 || len(m2.Library("alice").Since(0)) != 1 || len(m2.Library("bob").Since(0)) != 0 {
		t.Fatal("reload by user")
	}
	matches, _ := filepath.Glob(filepath.Join(dir, UserKey("alice"), "*.json"))
	if len(matches) != 2 {
		t.Fatalf("files: %v", matches)
	}
}
