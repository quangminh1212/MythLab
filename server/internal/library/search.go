package library

import (
	"bytes"
	"context"
	"sort"
	"strings"
	"sync"
	"time"
)

const searchMaxAge = 30 * time.Second

// IndexStats says how much of the library the search index covers.
type IndexStats struct {
	Stories    int `json:"stories"`
	Repos      int `json:"repos"`
	ReposTotal int `json:"reposTotal"`
}

// SearchResult is the /api/search payload.
type SearchResult struct {
	Q       string      `json:"q"`
	Total   int         `json:"total"`
	Items   []StoryItem `json:"items"`
	Indexed IndexStats  `json:"indexed"`
}

type normField struct{ key, compact string }

func newNormField(s string) normField {
	k := NormKey(s)
	return normField{k, strings.ReplaceAll(k, " ", "")}
}

func (f normField) has(tok string) bool {
	return strings.Contains(f.key, tok) || strings.Contains(f.compact, tok)
}

type searchEntry struct {
	item                      StoryItem
	title, author, tags, repo normField
	sortKey                   []byte
}

// SearchIndex is an in-memory index over everything the providers already
// know locally. Building it never calls GitHub.
type SearchIndex struct {
	lib *Library

	mu       sync.RWMutex
	entries  []searchEntry
	stats    IndexStats
	builtAt  time.Time
	building bool
	done     chan struct{} // closed when the build in progress ends
}

// NewSearchIndex creates an empty index; call RefreshAsync to start filling it.
func NewSearchIndex(lib *Library) *SearchIndex { return &SearchIndex{lib: lib} }

// Refresh rebuilds the index now.
func (x *SearchIndex) Refresh() {
	var entries []searchEntry
	var stats IndexStats
	for _, p := range x.lib.Providers() {
		groups, total := p.IndexEntries()
		stats.ReposTotal += total
		names := make([]string, 0, len(groups))
		for g := range groups {
			names = append(names, g)
		}
		sort.Strings(names)
		for _, g := range names {
			if g != "" {
				stats.Repos++
			}
			for _, it := range groups[g] {
				it.Source = p.ID()
				repo := g
				if repo == "" && it.Group != nil {
					repo = *it.Group
				}
				it.Repo = repo
				author := ""
				if it.Author != nil {
					author = *it.Author
				}
				entries = append(entries, searchEntry{item: it,
					title:  newNormField(it.Name + " " + it.Folder),
					author: newNormField(author),
					tags:   newNormField(strings.Join(it.Tags, " ") + " " + strings.Join(it.Genres, " ")),
					repo:   newNormField(repo), sortKey: ViKey(it.Name)})
			}
		}
	}
	stats.Stories = len(entries)
	x.mu.Lock()
	x.entries, x.stats, x.builtAt = entries, stats, time.Now()
	x.mu.Unlock()
}

// RefreshAsync rebuilds in the background unless a build is already running.
// It returns a channel closed when that build ends.
func (x *SearchIndex) RefreshAsync() <-chan struct{} {
	x.mu.Lock()
	if x.building {
		ch := x.done
		x.mu.Unlock()
		return ch
	}
	x.building = true
	ch := make(chan struct{})
	x.done = ch
	x.mu.Unlock()
	go func() {
		defer func() {
			x.mu.Lock()
			x.building = false
			x.mu.Unlock()
			close(ch)
		}()
		x.Refresh()
	}()
	return ch
}

// Stats returns the coverage of the current index.
func (x *SearchIndex) Stats() IndexStats {
	x.mu.RLock()
	defer x.mu.RUnlock()
	return x.stats
}

// rank returns the match class of e for the query tokens, or -1.
func (e *searchEntry) rank(q normField, toks []string) int {
	all := func(fields ...normField) bool {
		for _, t := range toks {
			ok := false
			for _, f := range fields {
				if f.has(t) {
					ok = true
					break
				}
			}
			if !ok {
				return false
			}
		}
		return true
	}
	switch {
	case strings.HasPrefix(e.title.key, q.key) || strings.HasPrefix(e.title.compact, q.compact):
		return 0
	case all(e.title):
		return 1
	case all(e.title, e.author):
		return 2
	case all(e.title, e.author, e.tags):
		return 3
	case all(e.title, e.author, e.tags, e.repo):
		return 4
	}
	return -1
}

// Search finds stories whose title/author/tags/repo contain every query token.
func (x *SearchIndex) Search(ctx context.Context, q, source string, offset, limit int) SearchResult {
	x.mu.RLock()
	built := !x.builtAt.IsZero()
	old := time.Since(x.builtAt) > searchMaxAge
	x.mu.RUnlock()
	if !built {
		select { // the very first build: wait for it
		case <-x.RefreshAsync():
		case <-ctx.Done():
		}
	} else if old {
		x.RefreshAsync()
	}
	x.mu.RLock()
	entries, stats := x.entries, x.stats
	x.mu.RUnlock()

	res := SearchResult{Q: q, Items: []StoryItem{}, Indexed: stats}
	nq := newNormField(q)
	toks := strings.Fields(nq.key)
	if len(toks) == 0 {
		return res
	}
	type hit struct {
		rank int
		e    *searchEntry
	}
	var hits []hit
	for i := range entries {
		e := &entries[i]
		if source != "" && e.item.Source != source {
			continue
		}
		if r := e.rank(nq, toks); r >= 0 {
			hits = append(hits, hit{r, e})
		}
	}
	sort.SliceStable(hits, func(i, j int) bool {
		a, b := hits[i], hits[j]
		if a.rank != b.rank {
			return a.rank < b.rank
		}
		if c := bytes.Compare(a.e.sortKey, b.e.sortKey); c != 0 {
			return c < 0
		}
		return a.e.item.Key < b.e.item.Key
	})
	res.Total = len(hits)
	if offset < 0 {
		offset = 0
	}
	if offset > len(hits) {
		offset = len(hits)
	}
	end := len(hits)
	if limit > 0 && offset+limit < end {
		end = offset + limit
	}
	for _, h := range hits[offset:end] {
		res.Items = append(res.Items, h.e.item)
	}
	return res
}
