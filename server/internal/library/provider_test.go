package library

import (
	"context"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
)

func writeFile(t *testing.T, path, content string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

func wantStatus(t *testing.T, err error, status int, what string) {
	t.Helper()
	e, ok := AsError(err)
	if !ok || e.Status != status {
		t.Fatalf("%s: want status %d, got %v", what, status, err)
	}
	if strings.Contains(e.Msg, ":\\") || strings.Contains(e.Msg, os.TempDir()) {
		t.Fatalf("%s: message leaks a path: %q", what, e.Msg)
	}
}

func TestPyQuote(t *testing.T) {
	cases := map[string]string{
		"gh0":             "gh0",
		"Done_A/Biên Qua": "Done_A/Bi%C3%AAn%20Qua",
		"a&b=c?d#e+f":     "a%26b%3Dc%3Fd%23e%2Bf",
		"x~y_z.w-v":       "x~y_z.w-v",
	}
	for in, want := range cases {
		if got := PyQuote(in); got != want {
			t.Errorf("PyQuote(%q) = %q, want %q", in, got, want)
		}
	}
}

func TestLocalProvider(t *testing.T) {
	root := t.TempDir()
	writeFile(t, filepath.Join(root, "Truyện A", "Chương 2 - Hai.txt"), "hai")
	writeFile(t, filepath.Join(root, "Truyện A", "Chương 1 - Một.txt"), "một")
	writeFile(t, filepath.Join(root, "Truyện A", "cover.png"), "\x89PNG")
	writeFile(t, filepath.Join(root, "Truyện A", "ghi chú.txt"), "x")
	writeFile(t, filepath.Join(root, "Kho", "Truyện B", "Chương 1.txt"), "b1")
	writeFile(t, filepath.Join(root, "Kho", "Truyện B", "info.json"), "{ this is not json")
	writeFile(t, filepath.Join(root, "Kho", "Truyện C", "info.json"), `{"name":"Tên C","author":{"name":"Tác Giả"},"poster":"https://example.com/c.jpg"}`)
	writeFile(t, filepath.Join(root, ".git", "Chương 1.txt"), "no")
	writeFile(t, filepath.Join(root, "_tmp", "Chương 1.txt"), "no")
	writeFile(t, filepath.Join(root, "reader", "Chương 1.txt"), "no")
	writeFile(t, filepath.Join(root, "secret.txt"), "secret")
	ctx := context.Background()
	p := NewLocalProvider("local0", "Thử", root)

	if d := p.Describe(ctx); !d.Available || d.Kind != "local" || d.ID != "local0" {
		t.Fatalf("describe: %+v", d)
	}
	items, _, err := p.ListStories(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	var keys []string
	for _, it := range items {
		keys = append(keys, it.Key)
	}
	if got := strings.Join(keys, "|"); got != "Kho/Truyện B|Kho/Truyện C|Truyện A" {
		t.Fatalf("keys = %s", got)
	}
	if b := items[0]; b.Name != "Truyện B" || b.ChapterFiles != 1 || b.Group == nil || *b.Group != "Kho" || b.Cover != nil {
		t.Fatalf("bad info.json must fall back: %+v", b)
	}
	if c := items[1]; c.Name != "Tên C" || c.Author == nil || *c.Author != "Tác Giả" || c.Cover == nil {
		t.Fatalf("story C: %+v", c)
	}
	if a := items[2]; a.Group != nil || a.ChapterFiles != 2 || a.Cover == nil || *a.Cover != "/api/cover?source=local0&key=Truy%E1%BB%87n%20A" {
		t.Fatalf("story A: %+v", a)
	}

	d, err := p.Story(ctx, "Truyện A")
	if err != nil || len(d.Chapters) != 2 || d.Chapters[0].File != "Chương 1 - Một.txt" || d.Chapters[0].Title != "Một" {
		t.Fatalf("story: %+v %v", d, err)
	}
	for _, key := range []string{"..", "../x", ".", "Kho/../..", "Kho\\Truyện B", "C:/Windows", "/etc", "a/b/c"} {
		_, err := p.Story(ctx, key)
		wantStatus(t, err, 403, "story "+key)
	}
	for _, key := range []string{"khongco", "Kho", "Kho/khongco", "reader", ".git"} {
		_, err := p.Story(ctx, key)
		wantStatus(t, err, 404, "story "+key)
	}
	_, err = p.Story(ctx, "")
	wantStatus(t, err, 400, "empty key")

	b, tag, err := p.ReadChapter(ctx, "Truyện A", "Chương 1 - Một.txt")
	if err != nil || string(b) != "một" || tag == "" {
		t.Fatalf("chapter: %q %q %v", b, tag, err)
	}
	for _, f := range []string{"../secret.txt", "ghi chú.txt", "..\\secret.txt", "x/Chương 1.txt", "cover.png", ""} {
		_, _, err := p.ReadChapter(ctx, "Truyện A", f)
		wantStatus(t, err, 403, "file "+f)
	}
	_, _, err = p.ReadChapter(ctx, "Truyện A", "Chương 99.txt")
	wantStatus(t, err, 404, "missing chapter")

	c, err := p.Cover(ctx, "Truyện A")
	if err != nil || c.Path == "" || c.Ctype != "image/png" {
		t.Fatalf("cover: %+v %v", c, err)
	}
	if c, _ := p.Cover(ctx, "Kho/Truyện C"); c.Poster != "https://example.com/c.jpg" {
		t.Fatalf("poster cover: %+v", c)
	}
	if c, _ := p.Cover(ctx, "Kho/Truyện B"); c.Path != "" || c.Poster != "" || c.Data != nil {
		t.Fatalf("no cover expected: %+v", c)
	}

	// a new chapter shows up without restarting
	writeFile(t, filepath.Join(root, "Truyện A", "Chương 3.txt"), "ba")
	if d, _ := p.Story(ctx, "Truyện A"); len(d.Chapters) != 3 {
		t.Fatalf("want 3 chapters after adding one, got %d", len(d.Chapters))
	}

	missing := NewLocalProvider("local1", "", filepath.Join(root, "nope"))
	if d := missing.Describe(ctx); d.Available {
		t.Fatal("missing root must be unavailable")
	}
	if items, _, err := missing.ListStories(ctx, ""); err != nil || len(items) != 0 || items == nil {
		t.Fatalf("missing root: %v %v", items, err)
	}
}

func gitSha(content string) string {
	h := sha1.New()
	fmt.Fprintf(h, "blob %d\x00", len(content))
	h.Write([]byte(content))
	return hex.EncodeToString(h.Sum(nil))
}

// fakeGitHub is a tiny GitHub API with one owner.
type fakeGitHub struct {
	mu       sync.Mutex
	repos    map[string]map[string]string // repo -> path -> content
	treeSha  map[string]string
	pushed   map[string]string
	calls    atomic.Int64
	down     atomic.Bool
	limited  atomic.Bool
	truncate atomic.Bool
	srv      *httptest.Server
}

func newFakeGitHub(t *testing.T) *fakeGitHub {
	f := &fakeGitHub{repos: map[string]map[string]string{}, treeSha: map[string]string{}, pushed: map[string]string{}}
	f.srv = httptest.NewServer(http.HandlerFunc(f.serve))
	t.Cleanup(f.srv.Close)
	return f
}

func (f *fakeGitHub) set(repo, sha string, files map[string]string) {
	f.mu.Lock()
	f.repos[repo], f.treeSha[repo], f.pushed[repo] = files, sha, "2026-01-01T00:00:00Z-"+sha[:4]
	f.mu.Unlock()
}

func (f *fakeGitHub) serve(w http.ResponseWriter, r *http.Request) {
	f.calls.Add(1)
	if r.Header.Get("Authorization") != "Bearer test-token" {
		http.Error(w, "no auth", 401)
		return
	}
	if f.down.Load() {
		http.Error(w, "boom", 500)
		return
	}
	if f.limited.Load() {
		w.Header().Set("X-RateLimit-Remaining", "0")
		w.Header().Set("X-RateLimit-Reset", "99999999999")
		http.Error(w, "rate", 403)
		return
	}
	f.mu.Lock()
	defer f.mu.Unlock()
	j := func(v any) { json.NewEncoder(w).Encode(v) }
	type ent struct {
		Path string `json:"path"`
		Type string `json:"type"`
		Sha  string `json:"sha"`
	}
	parts := strings.Split(strings.Trim(r.URL.Path, "/"), "/")
	switch {
	case r.URL.Path == "/user/repos":
		var out []map[string]any
		for name := range f.repos {
			out = append(out, map[string]any{"name": name, "owner": map[string]string{"login": "Owner"},
				"default_branch": "main", "pushed_at": f.pushed[name], "private": true})
		}
		out = append(out, map[string]any{"name": "Done_Foreign", "owner": map[string]string{"login": "someone"}, "default_branch": "main"},
			map[string]any{"name": "Other", "owner": map[string]string{"login": "owner"}, "default_branch": "main"})
		j(out)
	case len(parts) == 5 && parts[0] == "repos" && parts[3] == "commits":
		sha, ok := f.treeSha[parts[2]]
		if !ok {
			http.Error(w, "nf", 404)
			return
		}
		j(map[string]any{"commit": map[string]any{"tree": map[string]string{"sha": sha}}})
	case len(parts) == 6 && parts[4] == "trees":
		files := f.repos[parts[2]]
		subSha := func(dir string) string { return gitSha("dir:" + parts[2] + ":" + dir) }
		if parts[5] == f.treeSha[parts[2]] {
			if r.URL.Query().Get("recursive") == "1" {
				if f.truncate.Load() {
					j(map[string]any{"tree": []ent{}, "truncated": true})
					return
				}
				var out []ent
				for p, c := range files {
					out = append(out, ent{p, "blob", gitSha(c)})
				}
				j(map[string]any{"tree": out, "truncated": false})
				return
			}
			seen := map[string]bool{}
			var out []ent
			for p := range files {
				if i := strings.IndexByte(p, '/'); i > 0 && !seen[p[:i]] {
					seen[p[:i]] = true
					out = append(out, ent{p[:i], "tree", subSha(p[:i])})
				}
			}
			j(map[string]any{"tree": out})
			return
		}
		var out []ent
		for p, c := range files {
			if i := strings.IndexByte(p, '/'); i > 0 && subSha(p[:i]) == parts[5] && !strings.Contains(p[i+1:], "/") {
				out = append(out, ent{p[i+1:], "blob", gitSha(c)})
			}
		}
		j(map[string]any{"tree": out})
	case len(parts) == 6 && parts[4] == "blobs":
		for _, c := range f.repos[parts[2]] {
			if gitSha(c) == parts[5] {
				w.Write([]byte(c))
				return
			}
		}
		http.Error(w, "nf", 404)
	default:
		http.Error(w, "nf", 404)
	}
}

func (f *fakeGitHub) provider(t *testing.T, cache string) *GitHubProvider {
	p := NewGitHubProvider(GitHubOptions{ID: "gh0", Owner: "owner", Prefix: "Done_", CacheDir: cache, APIBase: f.srv.URL,
		Token: func() string { return "test-token" }, Logf: t.Logf})
	t.Cleanup(p.Close)
	return p
}

const treeA = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
const treeA2 = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

func filesA() map[string]string {
	return map[string]string{
		"Truyện Một/info.json":           `{"name":"Truyện Một","author":"Tác Giả X","tags":[{"name":"Cổ Tích"}],"poster":{"600":"https://example.com/p.jpg"},"chapter_count":2}`,
		"Truyện Một/Chương 1 - Mở.txt":   "nội dung 1",
		"Truyện Một/Chương 2 - Hai.txt":  "nội dung 2",
		"Truyện Một/Chương 2 -  Hai.txt": "nội dung 2 trùng",
		"Truyện Một/sub/Chương 9.txt":    "too deep",
		"Truyện Hai/Chương 1.txt":        "hai 1",
		"Truyện Hai/cover.jpg":           "JPEGDATA",
		"README.md":                      "top level file",
		".github/workflow.yml":           "ignored",
	}
}

func TestGitHubProvider(t *testing.T) {
	f := newFakeGitHub(t)
	f.set("Done_A", treeA, filesA())
	f.set("Done_B", treeA2, map[string]string{"Truyện Ba/Chương 1.txt": "ba"})
	cache := t.TempDir()
	ctx := context.Background()
	p := f.provider(t, cache)

	d := p.Describe(ctx)
	if !d.Available || d.Repos == nil || len(*d.Repos) != 2 || (*d.Repos)[0].Repo != "Done_A" || d.Detail != "owner/Done_*" {
		t.Fatalf("describe: %+v", d)
	}
	items, stale, err := p.ListStories(ctx, "Done_A")
	if err != nil || stale || len(items) != 2 {
		t.Fatalf("list: %+v %v %v", items, stale, err)
	}
	if it := items[1]; it.Key != "Done_A/Truyện Một" || it.ChapterFiles != 2 || it.Author == nil || *it.Author != "Tác Giả X" ||
		it.Poster == nil || *it.Poster != "https://example.com/p.jpg" || it.Cover == nil || *it.Group != "Done_A" || it.Declared == nil || *it.Declared != 2 {
		t.Fatalf("item: %+v", it)
	}
	if it := items[0]; it.Key != "Done_A/Truyện Hai" || it.Name != "Truyện Hai" || it.Cover == nil {
		t.Fatalf("item: %+v", it)
	}
	all, _, err := p.ListStories(ctx, "")
	if err != nil || len(all) != 3 {
		t.Fatalf("all: %d %v", len(all), err)
	}

	st, err := p.Story(ctx, "Done_A/Truyện Một")
	if err != nil || len(st.Chapters) != 2 || st.Chapters[1].File != "Chương 2 -  Hai.txt" || st.Name != "Truyện Một" {
		t.Fatalf("story: %+v %v", st, err)
	}
	b, tag, err := p.ReadChapter(ctx, "Done_A/Truyện Một", "Chương 1 - Mở.txt")
	if err != nil || string(b) != "nội dung 1" || tag != gitSha("nội dung 1") {
		t.Fatalf("chapter: %q %v", b, err)
	}
	c, err := p.Cover(ctx, "Done_A/Truyện Hai")
	if err != nil || string(c.Data) != "JPEGDATA" || c.Ctype != "image/jpeg" {
		t.Fatalf("cover: %+v %v", c, err)
	}
	if c, _ := p.Cover(ctx, "Done_A/Truyện Một"); c.Poster != "https://example.com/p.jpg" {
		t.Fatalf("poster: %+v", c)
	}

	_, err = p.Story(ctx, "Done_Zzz/x")
	wantStatus(t, err, 404, "unknown repo")
	for _, repo := range []string{"Other", "Done_Foreign", "..", "Done_A/..", "Done_%2e", "Done_ A"} {
		_, _, err = p.ListStories(ctx, repo)
		wantStatus(t, err, 404, "repo "+repo)
	}
	_, err = p.Story(ctx, "Done_A/khongco")
	wantStatus(t, err, 404, "unknown story")
	_, err = p.Story(ctx, "Done_A/a/b")
	wantStatus(t, err, 403, "deep key")
	_, _, err = p.ReadChapter(ctx, "Done_A/Truyện Một", "info.json")
	wantStatus(t, err, 403, "bad chapter file")
	_, _, err = p.ReadChapter(ctx, "Done_A/Truyện Một", "Chương 77.txt")
	wantStatus(t, err, 404, "chapter not in tree")

	// everything is cached now: no further API calls
	before := f.calls.Load()
	p.ListStories(ctx, "")
	p.Story(ctx, "Done_A/Truyện Một")
	p.ReadChapter(ctx, "Done_A/Truyện Một", "Chương 1 - Mở.txt")
	if n := f.calls.Load() - before; n != 0 {
		t.Fatalf("expected no API calls when warm, got %d", n)
	}

	// the tree file stays readable by the old server
	treeFile, sumFile := p.CacheFiles("Done_A")
	raw, err := os.ReadFile(treeFile)
	if err != nil {
		t.Fatal(err)
	}
	var disk struct {
		V       int
		Sha     string
		Stories map[string]struct {
			Info     *string
			Chapters [][]any
			Cover    []string
		}
	}
	if err := json.Unmarshal(raw, &disk); err != nil || disk.V != 2 || disk.Sha != treeA || len(disk.Stories["Truyện Một"].Chapters) != 3 ||
		len(disk.Stories["Truyện Một"].Chapters[0]) != 4 || disk.Stories["Truyện Hai"].Cover[0] != "cover.jpg" {
		t.Fatalf("tree file: %v %s", err, raw)
	}

	// a second process: offline, everything comes from disk and is flagged stale
	f.down.Store(true)
	p2 := f.provider(t, cache)
	d2 := p2.Describe(ctx)
	if !d2.Available || d2.Repos == nil || len(*d2.Repos) != 2 {
		t.Fatalf("offline describe: %+v", d2)
	}
	items, _, err = p2.ListStories(ctx, "Done_A")
	if err != nil || len(items) != 2 || items[1].Author == nil {
		t.Fatalf("offline list: %+v %v", items, err)
	}
	if st, err := p2.Story(ctx, "Done_A/Truyện Một"); err != nil || len(st.Chapters) != 2 {
		t.Fatalf("offline story: %v", err)
	}
	groups, total := p2.IndexEntries()
	if total != 2 || len(groups["Done_A"]) != 2 || len(groups["Done_B"]) != 1 {
		t.Fatalf("index entries: %d %v", total, groups)
	}
	f.down.Store(false)

	// corrupt cache files are a miss, not an error
	os.WriteFile(treeFile, []byte("{broken"), 0o644)
	os.WriteFile(sumFile, []byte("nope"), 0o644)
	os.WriteFile(blobPath(cache, gitSha("nội dung 1")), []byte("tampered"), 0o644)
	p3 := f.provider(t, cache)
	if st, err := p3.Story(ctx, "Done_A/Truyện Một"); err != nil || len(st.Chapters) != 2 {
		t.Fatalf("after corruption: %v", err)
	}
	if b, _, err := p3.ReadChapter(ctx, "Done_A/Truyện Một", "Chương 1 - Mở.txt"); err != nil || string(b) != "nội dung 1" {
		t.Fatalf("tampered blob must be refetched: %q %v", b, err)
	}

	// a push changes the head: the new tree is picked up by a fresh process
	nf := filesA()
	nf["Truyện Một/Chương 3.txt"] = "ba"
	f.set("Done_A", treeA2, nf)
	p4 := f.provider(t, cache)
	p4.mu.Lock()
	p4.reposDisk = true // force a fresh repo listing
	p4.mu.Unlock()
	if st, err := p4.Story(ctx, "Done_A/Truyện Một"); err != nil || len(st.Chapters) != 3 {
		t.Fatalf("after push: %+v %v", st, err)
	}

	// rate limited: serve the cache, then stop calling GitHub
	f.limited.Store(true)
	p5 := f.provider(t, cache)
	p5.mu.Lock()
	p5.reposDisk = true
	p5.mu.Unlock()
	if d := p5.Describe(ctx); !d.Available || !d.Stale || d.Repos == nil || len(*d.Repos) == 0 {
		t.Fatalf("no saved list + rate limit must fall back to the cached trees: %+v", d)
	}
	n := f.calls.Load()
	p5.Describe(ctx)
	if f.calls.Load() != n {
		t.Fatal("must not call GitHub while rate limited")
	}
}

func TestGitHubTruncatedTreeAndOldCache(t *testing.T) {
	f := newFakeGitHub(t)
	f.set("Done_A", treeA, filesA())
	f.truncate.Store(true)
	cache := t.TempDir()
	ctx := context.Background()
	p := f.provider(t, cache)
	st, err := p.Story(ctx, "Done_A/Truyện Một")
	if err != nil || len(st.Chapters) != 2 {
		t.Fatalf("truncated tree: %+v %v", st, err)
	}
	p.Close()
	f.truncate.Store(false)

	// a tree file written by the old server (no parser marker, strict names only) is used at once and upgraded
	h := gitSha("nội dung 1")
	old := fmt.Sprintf(`{"v": 2, "sha": %q, "stories": {"Truyện Một": {"info": null, "chapters": [[1, "Mở", "Chương 1 - Mở.txt", %q]], "cover": null}}}`, treeA, h)
	cache2 := t.TempDir()
	writeFile(t, treePath(cache2, "Done_A"), old)
	p2 := f.provider(t, cache2)
	st, err = p2.Story(ctx, "Done_A/Truyện Một")
	if err != nil || len(st.Chapters) < 1 {
		t.Fatalf("old cache: %+v %v", st, err)
	}
	p2.wg.Wait()
	st, err = p2.Story(ctx, "Done_A/Truyện Một")
	if err != nil || len(st.Chapters) != 2 {
		t.Fatalf("after upgrade: %+v %v", st, err)
	}
	if t2 := loadTreeFile(cache2, "Done_A"); t2 == nil || !t2.marked {
		t.Fatal("upgraded tree file must carry the parser marker")
	}
}

func TestSearchIndex(t *testing.T) {
	root := t.TempDir()
	mk := func(dir, info string) {
		writeFile(t, filepath.Join(root, dir, "Chương 1.txt"), "x")
		if info != "" {
			writeFile(t, filepath.Join(root, dir, "info.json"), info)
		}
	}
	mk("Cổ Tích Việt Nam", "")
	mk("Chuyện Xưa Cổ Tích", "")
	mk("Kho/CoTichMoi", "")
	mk("Truyện Khác", `{"author":"Cổ Tích Tiên Sinh"}`)
	mk("Truyện Tag", `{"tags":[{"name":"Cổ tích"}]}`)
	mk("Không Liên Quan", "")
	lib := NewLibrary(NewLocalProvider("local0", "x", root))
	x := NewSearchIndex(lib)
	ctx := context.Background()
	r := x.Search(ctx, "co tich", "", 0, 20)
	var got []string
	for _, it := range r.Items {
		got = append(got, it.Key)
	}
	want := "Kho/CoTichMoi|Cổ Tích Việt Nam|Chuyện Xưa Cổ Tích|Truyện Khác|Truyện Tag"
	if strings.Join(got, "|") != want || r.Total != 5 {
		t.Fatalf("search order:\n got %s\nwant %s", strings.Join(got, "|"), want)
	}
	if r.Items[0].Source != "local0" || r.Items[0].Repo != "Kho" || r.Indexed.Stories != 6 {
		t.Fatalf("fields: %+v %+v", r.Items[0], r.Indexed)
	}
	if r := x.Search(ctx, "cotich viet", "", 0, 20); r.Total != 1 {
		t.Fatalf("compact token: %d", r.Total)
	}
	if r := x.Search(ctx, "co tich", "", 1, 2); len(r.Items) != 2 || r.Total != 5 || r.Items[0].Key != "Cổ Tích Việt Nam" {
		t.Fatalf("paging: %+v", r)
	}
	if r := x.Search(ctx, "co tich", "gh0", 0, 20); r.Total != 0 || r.Items == nil {
		t.Fatalf("source filter: %+v", r)
	}
	if r := x.Search(ctx, "  !!! ", "", 0, 20); r.Total != 0 {
		t.Fatalf("empty query: %+v", r)
	}
}

// A cache that has trees but no saved repo list (the old server's cache) can
// still be read while GitHub refuses every call.
func TestGitHubOfflineWithoutRepoList(t *testing.T) {
	f := newFakeGitHub(t)
	f.set("Done_A", treeA, filesA())
	cache := t.TempDir()
	ctx := context.Background()
	p := f.provider(t, cache)
	if _, _, err := p.ListStories(ctx, ""); err != nil {
		t.Fatal(err)
	}
	if _, _, err := p.ReadChapter(ctx, "Done_A/Truyện Hai", "Chương 1.txt"); err != nil {
		t.Fatal(err)
	}
	p.Close()
	if err := os.Remove(reposPath(cache, "owner", "Done_")); err != nil {
		t.Fatal(err)
	}

	f.limited.Store(true)
	q := f.provider(t, cache)
	d := q.Describe(ctx)
	if !d.Available || !d.Stale || d.Repos == nil || len(*d.Repos) != 1 || (*d.Repos)[0].Repo != "Done_A" {
		t.Fatalf("describe offline: %+v", d)
	}
	items, stale, err := q.ListStories(ctx, "Done_A")
	if err != nil || !stale || len(items) != 2 {
		t.Fatalf("list offline: %d %v %v", len(items), stale, err)
	}
	st, err := q.Story(ctx, "Done_A/Truyện Một")
	if err != nil || !st.Stale || len(st.Chapters) != 2 {
		t.Fatalf("story offline: %+v %v", st, err)
	}
	if b, _, err := q.ReadChapter(ctx, "Done_A/Truyện Hai", "Chương 1.txt"); err != nil || string(b) != "hai 1" {
		t.Fatalf("cached chapter offline: %q %v", b, err)
	}
	_, err = q.Story(ctx, "Done_Missing/x")
	wantStatus(t, err, 404, "unknown repo offline")

	// nothing cached at all: the error is reported as before
	r := f.provider(t, t.TempDir())
	if d := r.Describe(ctx); d.Available || d.Error == "" {
		t.Fatalf("empty cache offline: %+v", d)
	}
}
