package library

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/url"
	"os"
	"path"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"

	"golang.org/x/sync/singleflight"
)

const (
	ghFreshTTL  = 600 * time.Second // repo list and tree heads
	ghStaleTTL  = 60 * time.Second  // how long an offline fallback is reused before retrying
	ghTreeLRU   = 8
	ghWorkers   = 8
	ghFlightMax = 5 * time.Minute
	ghMaxCover  = 12 << 20
)

// GitHubOptions configures a GitHub source.
type GitHubOptions struct {
	ID, Name      string
	Owner, Prefix string
	CacheDir      string // <cache>/github
	APIBase       string // default https://api.github.com
	HTTPClient    *http.Client
	Token         func() string // default: GITHUB_TOKEN, GH_TOKEN, `gh auth token`
	Logf          func(format string, args ...any)
}

// GitHubProvider reads stories from the repos <owner>/<prefix>*; a story is a
// top-level folder of a repo.
type GitHubProvider struct {
	id, prefix, cfgOwner, fixedName string
	dir                             string
	c                               *ghClient
	logf                            func(string, ...any)
	sf                              singleflight.Group
	ctx                             context.Context
	cancel                          context.CancelFunc
	wg                              sync.WaitGroup
	upgradeSem                      chan struct{}

	mu         sync.Mutex
	owner      string
	repos      []Repo
	reposAt    time.Time
	reposHave  bool
	reposDisk  bool // disk cache already consulted
	reposErr   string
	refreshing bool
	sums       map[string]*repoSum
	trees      map[string]*ghTree
	treeUntil  map[string]time.Time
	treeStale  map[string]bool
	upgrading  map[string]bool
}

// NewGitHubProvider creates the provider; nothing touches the network yet.
func NewGitHubProvider(o GitHubOptions) *GitHubProvider {
	ctx, cancel := context.WithCancel(context.Background())
	logf := o.Logf
	if logf == nil {
		logf = func(string, ...any) {}
	}
	return &GitHubProvider{id: o.ID, prefix: o.Prefix, cfgOwner: o.Owner, owner: o.Owner, fixedName: o.Name,
		dir: o.CacheDir, c: newGHClient(o.APIBase, o.HTTPClient, o.Token), logf: logf, ctx: ctx, cancel: cancel,
		upgradeSem: make(chan struct{}, 1), sums: map[string]*repoSum{}, trees: map[string]*ghTree{},
		treeUntil: map[string]time.Time{}, treeStale: map[string]bool{}, upgrading: map[string]bool{}}
}

// Close stops background work and waits for it.
func (p *GitHubProvider) Close() {
	p.cancel()
	p.wg.Wait()
}

func (p *GitHubProvider) ID() string   { return p.id }
func (p *GitHubProvider) Kind() string { return "github" }

func marshalNoEscape(v any) ([]byte, error) {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(v); err != nil {
		return nil, err
	}
	return bytes.TrimRight(buf.Bytes(), "\n"), nil
}

func (p *GitHubProvider) names() (name, detail string) {
	p.mu.Lock()
	owner := p.owner
	p.mu.Unlock()
	detail = owner + "/" + p.prefix + "*"
	if p.fixedName != "" {
		return p.fixedName, detail
	}
	if owner == "" {
		return "GitHub (tôi)/" + p.prefix + "*", detail
	}
	return "GitHub " + detail, detail
}

// flight runs fn once per key; the work outlives a caller that gives up.
func (p *GitHubProvider) flight(ctx context.Context, key string, fn func(ctx context.Context) (any, error)) (any, error) {
	ch := p.sf.DoChan(key, func() (any, error) {
		c, cancel := context.WithTimeout(p.ctx, ghFlightMax)
		defer cancel()
		return fn(c)
	})
	select {
	case r := <-ch:
		return r.Val, r.Err
	case <-ctx.Done():
		return nil, ctx.Err()
	}
}

// ---- repo list ----

func (p *GitHubProvider) loadReposDisk() {
	p.mu.Lock()
	if p.reposDisk {
		p.mu.Unlock()
		return
	}
	p.reposDisk = true
	p.mu.Unlock()
	b, err := os.ReadFile(reposPath(p.dir, p.cfgOwner, p.prefix))
	if err != nil {
		return
	}
	var d diskRepos
	if json.Unmarshal(b, &d) != nil || d.Prefix != p.prefix || d.Repos == nil {
		return
	}
	out := d.Repos[:0]
	for _, r := range d.Repos {
		if p.validRepoName(r.Repo) {
			if r.Branch == "" {
				r.Branch = "main"
			}
			out = append(out, r)
		}
	}
	p.mu.Lock()
	if !p.reposHave {
		p.repos, p.reposAt, p.reposHave = out, time.Unix(d.At, 0), true
		if p.owner == "" {
			p.owner = d.Owner
		}
	}
	p.mu.Unlock()
}

// reposFromTrees lists the repos that have a cached tree file (offline fallback).
func (p *GitHubProvider) reposFromTrees() []Repo {
	ents, err := os.ReadDir(p.dir)
	if err != nil {
		return nil
	}
	out := []Repo{}
	for _, e := range ents {
		n := e.Name()
		if e.IsDir() || !strings.HasPrefix(n, "tree_") || !strings.HasSuffix(n, ".json") {
			continue
		}
		if name := strings.TrimSuffix(strings.TrimPrefix(n, "tree_"), ".json"); p.validRepoName(name) {
			out = append(out, Repo{Repo: name, Branch: "main"})
		}
	}
	sort.SliceStable(out, func(i, j int) bool { return strings.ToLower(out[i].Repo) < strings.ToLower(out[j].Repo) })
	return out
}

func (p *GitHubProvider) validRepoName(name string) bool {
	return repoNameRe.MatchString(name) && name != "." && name != ".." && strings.HasPrefix(name, p.prefix)
}

func (p *GitHubProvider) fetchRepos(ctx context.Context) ([]Repo, error) {
	p.mu.Lock()
	owner := p.owner
	p.mu.Unlock()
	if owner == "" {
		b, _, err := p.c.get(ctx, "/user", false, 0)
		if err != nil {
			return nil, err
		}
		var me struct {
			Login string `json:"login"`
		}
		if json.Unmarshal(b, &me) != nil || me.Login == "" {
			return nil, ErrUpstream("GitHub: không đọc được tài khoản")
		}
		owner = me.Login
		p.mu.Lock()
		p.owner = owner
		p.mu.Unlock()
	}
	next := "/user/repos?per_page=100&affiliation=owner,collaborator,organization_member&sort=full_name"
	out := []Repo{}
	for page := 0; next != "" && page < 200; page++ {
		b, n, err := p.c.get(ctx, next, false, 0)
		if err != nil {
			return nil, err
		}
		var rows []struct {
			Name  string `json:"name"`
			Owner struct {
				Login string `json:"login"`
			} `json:"owner"`
			DefaultBranch string  `json:"default_branch"`
			PushedAt      *string `json:"pushed_at"`
			Private       *bool   `json:"private"`
		}
		if json.Unmarshal(b, &rows) != nil {
			return nil, ErrUpstream("GitHub: danh sách repo không hợp lệ")
		}
		for _, r := range rows {
			if !strings.EqualFold(r.Owner.Login, owner) || !p.validRepoName(r.Name) {
				continue
			}
			br := r.DefaultBranch
			if br == "" {
				br = "main"
			}
			out = append(out, Repo{Repo: r.Name, Branch: br, PushedAt: r.PushedAt, Private: r.Private})
		}
		next = n
	}
	sort.SliceStable(out, func(i, j int) bool { return strings.ToLower(out[i].Repo) < strings.ToLower(out[j].Repo) })
	now := time.Now()
	p.mu.Lock()
	p.repos, p.reposAt, p.reposHave, p.reposErr = out, now, true, ""
	p.mu.Unlock()
	if b, err := marshalNoEscape(diskRepos{Owner: owner, Prefix: p.prefix, At: now.Unix(), Repos: out}); err == nil {
		if err := AtomicWrite(reposPath(p.dir, p.cfgOwner, p.prefix), b); err != nil {
			p.logf("[github] không ghi được danh sách repo: %v", err)
		}
	}
	return out, nil
}

func (p *GitHubProvider) refreshRepos(ctx context.Context) ([]Repo, error) {
	v, err := p.flight(ctx, "repos", func(c context.Context) (any, error) {
		r, err := p.fetchRepos(c)
		if err != nil {
			p.mu.Lock()
			p.reposErr = err.Error()
			// do not hammer a failing API: try again after the stale TTL
			if p.reposHave {
				p.reposAt = time.Now().Add(ghStaleTTL - ghFreshTTL)
			}
			p.mu.Unlock()
		}
		return r, err
	})
	if err != nil {
		return nil, err
	}
	return v.([]Repo), nil
}

// repoList returns the repos. A cached list is returned at once (refreshed in
// the background when old); only the very first call waits for GitHub.
func (p *GitHubProvider) repoList(ctx context.Context) (repos []Repo, stale bool, err error) {
	p.loadReposDisk()
	p.mu.Lock()
	have, at, cached, lastErr := p.reposHave, p.reposAt, p.repos, p.reposErr
	start := have && time.Since(at) >= ghFreshTTL && !p.refreshing
	if start {
		p.refreshing = true
	}
	p.mu.Unlock()
	if !have {
		r, err := p.refreshRepos(ctx)
		if err != nil && ctx.Err() == nil {
			// GitHub cannot be reached and no list was ever saved: read on from
			// the repos whose tree is already in the cache
			if off := p.reposFromTrees(); len(off) > 0 {
				p.mu.Lock()
				if !p.reposHave {
					p.repos, p.reposHave, p.reposErr = off, true, err.Error()
					p.reposAt = time.Now().Add(ghStaleTTL - ghFreshTTL)
				}
				off = p.repos
				p.mu.Unlock()
				return off, true, nil
			}
		}
		return r, false, err
	}
	if start {
		p.wg.Add(1)
		go func() {
			defer p.wg.Done()
			if _, err := p.refreshRepos(p.ctx); err != nil && p.ctx.Err() == nil {
				p.logf("[github] không làm mới được danh sách repo: %v", err)
			}
			p.mu.Lock()
			p.refreshing = false
			p.mu.Unlock()
		}()
	}
	return cached, lastErr != "", nil
}

func (p *GitHubProvider) Describe(ctx context.Context) SourceInfo {
	repos, stale, err := p.repoList(ctx)
	name, detail := p.names()
	si := SourceInfo{ID: p.id, Name: name, Kind: "github", Detail: detail, Available: true}
	if err != nil {
		si.Available = false
		si.Error = err.Error()
		return si
	}
	cp := append([]Repo{}, repos...)
	si.Repos, si.Stale = &cp, stale
	return si
}

// repo validates a repo name against the listing.
func (p *GitHubProvider) repo(ctx context.Context, name string) (Repo, error) {
	if !p.validRepoName(name) {
		return Repo{}, ErrNotFound(safeEcho(name))
	}
	repos, _, err := p.repoList(ctx)
	if err != nil {
		return Repo{}, err
	}
	for _, r := range repos {
		if r.Repo == name {
			return r, nil
		}
	}
	return Repo{}, ErrNotFound(name)
}

// ---- trees ----

func (p *GitHubProvider) repoPath(repo string) string {
	p.mu.Lock()
	owner := p.owner
	p.mu.Unlock()
	return "/repos/" + url.PathEscape(owner) + "/" + url.PathEscape(repo)
}

type apiTree struct {
	Tree []struct {
		Path string `json:"path"`
		Type string `json:"type"`
		Sha  string `json:"sha"`
	} `json:"tree"`
	Truncated bool `json:"truncated"`
}

func (p *GitHubProvider) apiTree(ctx context.Context, repo, sha string, recursive bool) (*apiTree, error) {
	q := ""
	if recursive {
		q = "?recursive=1"
	}
	b, _, err := p.c.get(ctx, p.repoPath(repo)+"/git/trees/"+sha+q, false, 120*time.Second)
	if err != nil {
		return nil, err
	}
	var t apiTree
	if json.Unmarshal(b, &t) != nil {
		return nil, ErrUpstream("GitHub: cây thư mục không hợp lệ")
	}
	return &t, nil
}

type treeBuilder struct {
	stories map[string]*ghStory
	images  map[string][]ghFile
}

func (tb *treeBuilder) add(story, file, sha string) {
	if story == "" || file == "" || !shaRe.MatchString(sha) {
		return
	}
	st := tb.stories[story]
	if st == nil {
		st = &ghStory{}
		tb.stories[story] = st
	}
	switch {
	case file == "info.json":
		st.info = sha
	case IsImageName(file):
		tb.images[story] = append(tb.images[story], ghFile{file, sha})
	default:
		if _, ok := ParseChapterName(file); ok {
			st.files = append(st.files, ghFile{file, sha})
		}
	}
}

func (tb *treeBuilder) finish(sha string) *ghTree {
	for name, st := range tb.stories {
		if imgs := tb.images[name]; len(imgs) > 0 {
			names := make([]string, len(imgs))
			for i, f := range imgs {
				names[i] = f.file
			}
			pick := PickCover(names)
			for _, f := range imgs {
				if f.file == pick {
					st.coverFile, st.coverSha = f.file, f.sha
				}
			}
		}
		if st.info == "" && len(st.files) == 0 {
			delete(tb.stories, name)
		}
	}
	return &ghTree{sha: sha, marked: true, stories: tb.stories}
}

// fetchTree downloads and parses a repo tree: only blobs at <story>/<file>.
func (p *GitHubProvider) fetchTree(ctx context.Context, repo, sha string) (*ghTree, error) {
	tb := &treeBuilder{stories: map[string]*ghStory{}, images: map[string][]ghFile{}}
	t, err := p.apiTree(ctx, repo, sha, true)
	if err != nil {
		return nil, err
	}
	if !t.Truncated {
		for _, e := range t.Tree {
			if e.Type != "blob" {
				continue
			}
			i := strings.IndexByte(e.Path, '/')
			if i <= 0 || strings.IndexByte(e.Path[i+1:], '/') >= 0 {
				continue
			}
			tb.add(e.Path[:i], e.Path[i+1:], e.Sha)
		}
		return tb.finish(sha), nil
	}
	// the recursive listing was cut short: walk one level at a time
	top, err := p.apiTree(ctx, repo, sha, false)
	if err != nil {
		return nil, err
	}
	for _, d := range top.Tree {
		if d.Type != "tree" || !shaRe.MatchString(d.Sha) {
			continue
		}
		sub, err := p.apiTree(ctx, repo, d.Sha, false)
		if err != nil {
			return nil, err
		}
		for _, e := range sub.Tree {
			if e.Type == "blob" {
				tb.add(d.Path, e.Path, e.Sha)
			}
		}
	}
	return tb.finish(sha), nil
}

func (p *GitHubProvider) headSha(ctx context.Context, r Repo) (string, error) {
	b, _, err := p.c.get(ctx, p.repoPath(r.Repo)+"/commits/"+PyQuote(r.Branch), false, 0)
	if err != nil {
		return "", err
	}
	var c struct {
		Commit struct {
			Tree struct {
				Sha string `json:"sha"`
			} `json:"tree"`
		} `json:"commit"`
	}
	if json.Unmarshal(b, &c) != nil || !shaRe.MatchString(c.Commit.Tree.Sha) {
		return "", ErrUpstream("GitHub: commit không hợp lệ")
	}
	return c.Commit.Tree.Sha, nil
}

// localSum returns the repo summary known without the network (memory, then disk).
func (p *GitHubProvider) localSum(repo string) *repoSum {
	p.mu.Lock()
	s := p.sums[repo]
	p.mu.Unlock()
	if s != nil {
		return s
	}
	if s = loadSumFile(p.dir, repo); s == nil {
		return nil
	}
	s.stale = true // not confirmed against GitHub yet
	p.mu.Lock()
	if cur := p.sums[repo]; cur != nil {
		s = cur
	} else {
		p.sums[repo] = s
	}
	p.mu.Unlock()
	return s
}

func pushedOf(r Repo) string {
	if r.PushedAt == nil {
		return ""
	}
	return *r.PushedAt
}

// setTree records a tree in the LRU and refreshes the repo summary from it.
func (p *GitHubProvider) setTree(r Repo, t *ghTree, stale bool) {
	old := p.localSum(r.Repo)
	ns := sumFromTree(t)
	ns.at, ns.stale = time.Now(), stale
	if !stale {
		ns.Pushed = pushedOf(r)
	} else if old != nil && old.Sha == ns.Sha {
		ns.Pushed = old.Pushed
	}
	save := old == nil || old.Sha != ns.Sha || old.Pushed != ns.Pushed || len(old.Stories) != len(ns.Stories)
	if old != nil {
		known := make(map[string]*diskSummary, len(old.Stories))
		for _, st := range old.Stories {
			if st.Sum != nil && st.Info != "" {
				known[st.Info+"\x00"+st.Story] = st.Sum
			}
		}
		for i := range ns.Stories {
			st := &ns.Stories[i]
			st.Sum = known[st.Info+"\x00"+st.Story]
		}
	}
	ttl := ghFreshTTL
	if stale {
		ttl = ghStaleTTL
	}
	t.used = time.Now()
	p.mu.Lock()
	p.trees[r.Repo], p.treeUntil[r.Repo], p.treeStale[r.Repo] = t, time.Now().Add(ttl), stale
	p.sums[r.Repo] = ns
	for len(p.trees) > ghTreeLRU {
		oldest, when := "", time.Time{}
		for k, v := range p.trees {
			if oldest == "" || v.used.Before(when) {
				oldest, when = k, v.used
			}
		}
		delete(p.trees, oldest)
		delete(p.treeUntil, oldest)
		delete(p.treeStale, oldest)
	}
	p.mu.Unlock()
	if save {
		if err := saveSumFile(p.dir, r.Repo, ns); err != nil {
			p.logf("[github] không ghi được tóm tắt %s: %v", r.Repo, err)
		}
	}
}

// tree returns the parsed tree of a repo, from memory, disk or GitHub.
func (p *GitHubProvider) tree(ctx context.Context, r Repo) (*ghTree, bool, error) {
	p.mu.Lock()
	if t := p.trees[r.Repo]; t != nil && time.Now().Before(p.treeUntil[r.Repo]) {
		t.used = time.Now()
		stale := p.treeStale[r.Repo]
		p.mu.Unlock()
		return t, stale, nil
	}
	p.mu.Unlock()
	type res struct {
		t     *ghTree
		stale bool
	}
	v, err := p.flight(ctx, "tree:"+r.Repo, func(c context.Context) (any, error) {
		sha := ""
		if s := p.localSum(r.Repo); s != nil && s.Pushed != "" && s.Pushed == pushedOf(r) {
			sha = s.Sha // nothing was pushed since the head was last read
		}
		var disk *ghTree
		if sha == "" {
			var err error
			if sha, err = p.headSha(c, r); err != nil {
				if errors.Is(err, context.Canceled) {
					return nil, err
				}
				if disk = loadTreeFile(p.dir, r.Repo); disk == nil {
					return nil, err
				}
				p.setTree(r, disk, true) // offline or rate limited: use what we have
				return res{disk, true}, nil
			}
		}
		if disk = loadTreeFile(p.dir, r.Repo); disk != nil && disk.sha == sha {
			p.setTree(r, disk, false)
			if !disk.marked {
				p.upgrade(r, sha)
			}
			return res{disk, false}, nil
		}
		t, err := p.fetchTree(c, r.Repo, sha)
		if err != nil {
			if disk != nil && !errors.Is(err, context.Canceled) {
				p.setTree(r, disk, true)
				return res{disk, true}, nil
			}
			return nil, err
		}
		if err := saveTreeFile(p.dir, r.Repo, t); err != nil {
			p.logf("[github] không ghi được cache cây %s: %v", r.Repo, err)
		}
		p.setTree(r, t, false)
		return res{t, false}, nil
	})
	if err != nil {
		return nil, false, err
	}
	x := v.(res)
	return x.t, x.stale, nil
}

// upgrade re-reads, in the background, a tree cached by the old server so
// that file names only the tolerant parser understands show up.
func (p *GitHubProvider) upgrade(r Repo, sha string) {
	p.mu.Lock()
	if p.upgrading[r.Repo] {
		p.mu.Unlock()
		return
	}
	p.upgrading[r.Repo] = true
	p.mu.Unlock()
	p.wg.Add(1)
	go func() {
		defer p.wg.Done()
		select {
		case p.upgradeSem <- struct{}{}:
		case <-p.ctx.Done():
			return
		}
		defer func() { <-p.upgradeSem }()
		t, err := p.fetchTree(p.ctx, r.Repo, sha)
		if err != nil {
			p.mu.Lock()
			delete(p.upgrading, r.Repo) // try again on a later visit
			p.mu.Unlock()
			return
		}
		if err := saveTreeFile(p.dir, r.Repo, t); err != nil {
			p.logf("[github] không ghi được cache cây %s: %v", r.Repo, err)
			return
		}
		p.setTree(r, t, false)
	}()
}

// summary returns the per-story summary of a repo, avoiding a tree load when possible.
func (p *GitHubProvider) summary(ctx context.Context, r Repo) (*repoSum, error) {
	if s := p.localSum(r.Repo); s != nil {
		if !s.at.IsZero() {
			ttl := ghFreshTTL
			if s.stale {
				ttl = ghStaleTTL
			}
			if time.Since(s.at) < ttl {
				return s, nil
			}
		}
		if s.Pushed != "" && s.Pushed == pushedOf(r) {
			p.mu.Lock()
			if cur := p.sums[r.Repo]; cur == s {
				cp := *s
				cp.at, cp.stale = time.Now(), false
				p.sums[r.Repo] = &cp
				s = &cp
			}
			p.mu.Unlock()
			return s, nil
		}
	}
	if _, _, err := p.tree(ctx, r); err != nil {
		return nil, err
	}
	p.mu.Lock()
	s := p.sums[r.Repo]
	p.mu.Unlock()
	if s == nil {
		return nil, ErrUpstream("GitHub: không có dữ liệu repo")
	}
	return s, nil
}

// ---- blobs ----

func readBlobFile(dir, sha string, limit int64) ([]byte, bool) {
	file := blobPath(dir, sha)
	st, err := os.Stat(file)
	if err != nil || !st.Mode().IsRegular() || st.Size() > limit {
		return nil, false
	}
	b, err := os.ReadFile(file)
	if err != nil || !gitBlobOK(sha, b) {
		return nil, false
	}
	return b, true
}

// blob returns the content of a git blob through the content-addressed disk cache.
func (p *GitHubProvider) blob(ctx context.Context, repo, sha string, limit int64) ([]byte, error) {
	if !shaRe.MatchString(sha) {
		return nil, ErrNotFound("blob")
	}
	if b, ok := readBlobFile(p.dir, sha, limit); ok {
		return b, nil
	}
	v, err := p.flight(ctx, "blob:"+sha, func(c context.Context) (any, error) {
		if b, ok := readBlobFile(p.dir, sha, ghBlobLimit); ok {
			return b, nil
		}
		b, _, err := p.c.get(c, p.repoPath(repo)+"/git/blobs/"+sha, true, 0)
		if err != nil {
			return nil, err
		}
		if !gitBlobOK(sha, b) {
			return nil, ErrUpstream("GitHub: nội dung blob không khớp mã băm")
		}
		if err := AtomicWrite(blobPath(p.dir, sha), b); err != nil {
			p.logf("[github] không ghi được blob: %v", err)
		}
		return b, nil
	})
	if err != nil {
		return nil, err
	}
	b := v.([]byte)
	if int64(len(b)) > limit {
		return nil, &Error{Status: http.StatusRequestEntityTooLarge, Code: "too_large", Msg: "tệp quá lớn"}
	}
	return b, nil
}

// ---- stories ----

func (p *GitHubProvider) item(repo string, st sumStory, sum Summary) StoryItem {
	key := repo + "/" + st.Story
	g := repo
	return StoryItem{Key: key, Folder: st.Story, Group: &g, ChapterFiles: st.N, Summary: sum,
		Cover: CoverURL(p.id, key, st.Img, sum.Poster)}
}

// storeSums merges freshly parsed info summaries into the repo summary and persists it.
func (p *GitHubProvider) storeSums(repo, sha string, found map[string]*diskSummary) {
	if len(found) == 0 {
		return
	}
	p.mu.Lock()
	cur := p.sums[repo]
	if cur == nil || cur.Sha != sha {
		p.mu.Unlock()
		return
	}
	cp := *cur
	cp.Stories = append([]sumStory(nil), cur.Stories...)
	for i := range cp.Stories {
		st := &cp.Stories[i]
		if d := found[st.Story]; d != nil && st.Sum == nil {
			st.Sum = d
		}
	}
	p.sums[repo] = &cp
	p.mu.Unlock()
	if err := saveSumFile(p.dir, repo, &cp); err != nil {
		p.logf("[github] không ghi được tóm tắt %s: %v", repo, err)
	}
}

func newDiskSummary(info []byte, story string) *diskSummary {
	s := InfoSummary(info, story)
	return &diskSummary{Summary: s, Updated: s.Updated}
}

func (p *GitHubProvider) listRepo(ctx context.Context, r Repo) ([]StoryItem, bool, error) {
	s, err := p.summary(ctx, r)
	if err != nil {
		return nil, false, err
	}
	out := make([]StoryItem, 0, len(s.Stories))
	found := map[string]*diskSummary{}
	stale := s.stale
	for _, st := range s.Stories {
		switch {
		case st.Sum != nil:
			out = append(out, p.item(r.Repo, st, st.Sum.Summary))
		case st.Info == "":
			out = append(out, p.item(r.Repo, st, InfoSummary(nil, st.Story)))
		default:
			if err := ctx.Err(); err != nil {
				p.storeSums(r.Repo, s.Sha, found)
				return nil, false, err
			}
			b, err := p.blob(ctx, r.Repo, st.Info, ghBlobLimit)
			if err != nil {
				if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
					p.storeSums(r.Repo, s.Sha, found)
					return nil, false, err
				}
				stale = true // listed by folder name until info.json can be read
				out = append(out, p.item(r.Repo, st, InfoSummary(nil, st.Story)))
				continue
			}
			d := newDiskSummary(b, st.Story)
			found[st.Story] = d
			out = append(out, p.item(r.Repo, st, d.Summary))
		}
	}
	p.storeSums(r.Repo, s.Sha, found)
	return out, stale, nil
}

func (p *GitHubProvider) ListStories(ctx context.Context, repo string) ([]StoryItem, bool, error) {
	if repo != "" {
		r, err := p.repo(ctx, repo)
		if err != nil {
			return nil, false, err
		}
		return p.listRepo(ctx, r)
	}
	repos, stale, err := p.repoList(ctx)
	if err != nil {
		return nil, false, err
	}
	type res struct {
		items []StoryItem
		stale bool
		err   error
	}
	results := make([]res, len(repos))
	jobs := make(chan int)
	var wg sync.WaitGroup
	for w := 0; w < ghWorkers && w < len(repos); w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := range jobs {
				it, st, err := p.listRepo(ctx, repos[i])
				results[i] = res{it, st, err}
			}
		}()
	}
	for i := range repos {
		jobs <- i
	}
	close(jobs)
	wg.Wait()
	if err := ctx.Err(); err != nil {
		return nil, false, err
	}
	out := []StoryItem{}
	var firstErr error
	failed := 0
	for i, r := range results {
		if r.err != nil {
			failed++
			if firstErr == nil {
				firstErr = r.err
			}
			p.logf("[github] bỏ qua repo %s: %v", repos[i].Repo, r.err)
			continue
		}
		out = append(out, r.items...)
		stale = stale || r.stale
	}
	if failed > 0 {
		if failed == len(repos) {
			return nil, false, firstErr
		}
		stale = true
	}
	return out, stale, nil
}

func splitKey(key string) (repo, story string, err error) {
	if key == "" {
		return "", "", ErrBadParam("key")
	}
	i := strings.IndexByte(key, '/')
	if i <= 0 || i == len(key)-1 {
		return "", "", ErrNotFound(safeEcho(key))
	}
	repo, story = key[:i], key[i+1:]
	if strings.ContainsAny(story, "/\\\x00") || story == "." || story == ".." {
		return "", "", ErrForbidden("path escape")
	}
	return repo, story, nil
}

// find resolves a key to its repo, tree and story.
func (p *GitHubProvider) find(ctx context.Context, key string) (Repo, string, *ghStory, bool, error) {
	repo, story, err := splitKey(key)
	if err != nil {
		return Repo{}, "", nil, false, err
	}
	r, err := p.repo(ctx, repo)
	if err != nil {
		return Repo{}, "", nil, false, err
	}
	t, stale, err := p.tree(ctx, r)
	if err != nil {
		return Repo{}, "", nil, false, err
	}
	st := t.stories[story]
	if st == nil {
		return Repo{}, "", nil, false, ErrNotFound(safeEcho(story))
	}
	return r, story, st, stale, nil
}

// storySummary returns the info.json summary of one story (fallback metadata when unreadable).
func (p *GitHubProvider) storySummary(ctx context.Context, repo, story string, st *ghStory) Summary {
	if st.info == "" {
		return InfoSummary(nil, story)
	}
	p.mu.Lock()
	s := p.sums[repo]
	p.mu.Unlock()
	if s != nil {
		for _, x := range s.Stories {
			if x.Story == story && x.Info == st.info && x.Sum != nil {
				return x.Sum.Summary
			}
		}
	}
	b, err := p.blob(ctx, repo, st.info, ghBlobLimit)
	if err != nil {
		return InfoSummary(nil, story)
	}
	d := newDiskSummary(b, story)
	if s != nil {
		p.storeSums(repo, s.Sha, map[string]*diskSummary{story: d})
	}
	return d.Summary
}

func (p *GitHubProvider) Story(ctx context.Context, key string) (*StoryDetail, error) {
	r, story, st, stale, err := p.find(ctx, key)
	if err != nil {
		return nil, err
	}
	sum := p.storySummary(ctx, r.Repo, story, st)
	return &StoryDetail{Key: key, Source: p.id, Summary: sum, Cover: CoverURL(p.id, key, st.coverSha != "", sum.Poster),
		Chapters: ChapterList(st.names()), Stale: stale}, nil
}

func (p *GitHubProvider) ReadChapter(ctx context.Context, key, file string) ([]byte, string, error) {
	if _, ok := ParseChapterName(file); !ok || strings.ContainsAny(file, "/\\\x00") {
		if _, _, err := splitKey(key); err != nil {
			return nil, "", err
		}
		return nil, "", ErrForbidden("bad chapter file")
	}
	r, _, st, _, err := p.find(ctx, key)
	if err != nil {
		return nil, "", err
	}
	sha, ok := st.sha(file)
	if !ok {
		return nil, "", ErrNotFound(safeEcho(file))
	}
	b, err := p.blob(ctx, r.Repo, sha, ghBlobLimit)
	if err != nil {
		return nil, "", err
	}
	return b, sha, nil
}

func (p *GitHubProvider) Cover(ctx context.Context, key string) (CoverRef, error) {
	r, story, st, _, err := p.find(ctx, key)
	if err != nil {
		return CoverRef{}, err
	}
	if st.coverSha != "" {
		b, err := p.blob(ctx, r.Repo, st.coverSha, ghMaxCover)
		if err == nil {
			return CoverRef{Data: b, Ctype: ImgExt[strings.ToLower(path.Ext(st.coverFile))], Tag: st.coverSha}, nil
		}
		if e, ok := AsError(err); !ok || e.Code != "too_large" {
			return CoverRef{}, err
		}
	}
	if sum := p.storySummary(ctx, r.Repo, story, st); sum.Poster != nil && IsHTTPURL(*sum.Poster) {
		return CoverRef{Poster: *sum.Poster}, nil
	}
	return CoverRef{}, nil
}

// IndexEntries lists what is already known on this machine: no network calls.
func (p *GitHubProvider) IndexEntries() (map[string][]StoryItem, int) {
	p.loadReposDisk()
	p.mu.Lock()
	repos := append([]Repo(nil), p.repos...)
	p.mu.Unlock()
	out := map[string][]StoryItem{}
	for _, r := range repos {
		if p.ctx.Err() != nil {
			break
		}
		s := p.localSum(r.Repo)
		if s == nil {
			t := loadTreeFile(p.dir, r.Repo)
			if t == nil {
				continue
			}
			s = sumFromTree(t)
			s.stale = true
			if err := saveSumFile(p.dir, r.Repo, s); err != nil {
				p.logf("[github] không ghi được tóm tắt %s: %v", r.Repo, err)
			}
			p.mu.Lock()
			if cur := p.sums[r.Repo]; cur != nil {
				s = cur
			} else {
				p.sums[r.Repo] = s
			}
			p.mu.Unlock()
		}
		items := make([]StoryItem, 0, len(s.Stories))
		found := map[string]*diskSummary{}
		for _, st := range s.Stories {
			sum := InfoSummary(nil, st.Story)
			if st.Sum != nil {
				sum = st.Sum.Summary
			} else if st.Info != "" {
				if b, ok := readBlobFile(p.dir, st.Info, ghBlobLimit); ok {
					d := newDiskSummary(b, st.Story)
					found[st.Story] = d
					sum = d.Summary
				}
			}
			items = append(items, p.item(r.Repo, st, sum))
		}
		p.storeSums(r.Repo, s.Sha, found)
		out[r.Repo] = items
	}
	return out, len(repos)
}

// CacheFiles reports the cache paths of a repo (used by tests and diagnostics).
func (p *GitHubProvider) CacheFiles(repo string) (tree, sum string) {
	return filepath.Clean(treePath(p.dir, repo)), filepath.Clean(sumPath(p.dir, repo))
}
