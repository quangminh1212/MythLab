package library

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
	"sync"
)

// nameCatalog is the lightweight title database: for every repo, the story folder names, keyed by the repo's
// last push. Building it costs two API calls per repo (head tree, then its top level), against one tree walk plus
// an info.json per story for the full summary, so a title search can cover every repo long before the details exist.
type nameCatalog struct {
	mu     sync.Mutex
	path   string
	loaded bool
	repos  map[string]nameEntry
}

type nameEntry struct {
	P     string   `json:"p"` // pushed_at the names were read at
	Names []string `json:"n"`
}

type nameFile struct {
	V     int                  `json:"v"`
	Repos map[string]nameEntry `json:"repos"`
}

func (p *GitHubProvider) nameDB() *nameCatalog {
	p.mu.Lock()
	defer p.mu.Unlock()
	if p.nameCat == nil {
		p.nameCat = &nameCatalog{path: filepath.Join(p.dir, "names_"+p.id+".json")}
	}
	return p.nameCat
}

func (c *nameCatalog) load() {
	if c.loaded {
		return
	}
	c.loaded = true
	c.repos = map[string]nameEntry{}
	b, err := os.ReadFile(c.path)
	if err != nil {
		return
	}
	var f nameFile
	if json.Unmarshal(b, &f) == nil && f.V == 1 && f.Repos != nil {
		c.repos = f.Repos
	}
}

func (c *nameCatalog) get(repo string) (nameEntry, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.load()
	e, ok := c.repos[repo]
	return e, ok
}

func (c *nameCatalog) put(repo string, e nameEntry) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.load()
	c.repos[repo] = e
	b, err := json.Marshal(nameFile{V: 1, Repos: c.repos})
	if err != nil {
		return err
	}
	return AtomicWrite(c.path, b)
}

// catalogNames makes sure the name list of a repo is current (2 API calls when it is not). It returns whether the
// network was used.
func (p *GitHubProvider) catalogNames(ctx context.Context, r Repo) (bool, error) {
	db := p.nameDB()
	if e, ok := db.get(r.Repo); ok && e.P != "" && e.P == pushedOf(r) {
		return false, nil
	}
	sha, err := p.headSha(ctx, r)
	if err != nil {
		return true, err
	}
	top, err := p.apiTree(ctx, r.Repo, sha, false)
	if err != nil {
		return true, err
	}
	names := make([]string, 0, len(top.Tree))
	for _, d := range top.Tree {
		if d.Type == "tree" && d.Path != "" && d.Path[0] != '.' {
			names = append(names, d.Path)
		}
	}
	sort.Strings(names)
	if err := db.put(r.Repo, nameEntry{P: pushedOf(r), Names: names}); err != nil {
		p.logf("[catalog] không ghi được names.json: %v", err)
	}
	return true, nil
}

// nameItems lists the stories of a repo from the name catalog only (no chapter counts, no author).
func (p *GitHubProvider) nameItems(repo string) []StoryItem {
	e, ok := p.nameDB().get(repo)
	if !ok {
		return nil
	}
	out := make([]StoryItem, 0, len(e.Names))
	for _, n := range e.Names {
		out = append(out, p.item(repo, sumStory{Story: n}, InfoSummary(nil, n)))
	}
	return out
}
