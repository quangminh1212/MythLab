package app

import (
	"context"
	"fmt"
	"io"
	"sync"
	"time"

	"mythlab/internal/library"
)

// PrefetchStats is the outcome of PrefetchCovers.
type PrefetchStats struct {
	Stories   int // stories seen
	FolderImg int // cover image in the story folder, no poster to fetch
	NoCover   int // neither image nor poster
	Posters   int // distinct poster URLs
	OK, Fail  int
}

// PrefetchCovers downloads and caches every poster of every source with
// `workers` parallel downloads, ignoring earlier failures. Progress goes to
// out. A failing repo does not stop the others.
func (a *App) PrefetchCovers(ctx context.Context, out io.Writer, workers int) PrefetchStats {
	if workers < 1 {
		workers = 6
	}
	var st PrefetchStats
	seen := map[string]bool{}
	var posters []string
	for _, p := range a.lib.Providers() {
		info := p.Describe(ctx)
		var stories []library.StoryItem
		collect := func(repo string) {
			items, _, err := p.ListStories(ctx, repo)
			if err != nil {
				fmt.Fprintf(out, "[covers] %s: lỗi %v\n", info.Name, err)
				return
			}
			stories = append(stories, items...)
		}
		switch {
		case p.Kind() != "github":
			collect("")
		case info.Repos == nil:
			fmt.Fprintf(out, "[covers] %s: lỗi %s\n", info.Name, info.Error)
		default:
			for _, r := range *info.Repos { // repo by repo: one failure costs one repo
				if ctx.Err() != nil {
					break
				}
				collect(r.Repo)
			}
		}
		for _, s := range stories {
			st.Stories++
			switch {
			case s.Poster != nil && library.IsHTTPURL(*s.Poster):
				if !seen[*s.Poster] {
					seen[*s.Poster] = true
					posters = append(posters, *s.Poster)
				}
			case s.Cover != nil:
				st.FolderImg++
			default:
				st.NoCover++
			}
		}
		fmt.Fprintf(out, "[covers] %s: %d truyện\n", info.Name, len(stories))
	}
	st.Posters = len(posters)
	t0 := time.Now()
	jobs := make(chan string)
	var mu sync.Mutex
	var wg sync.WaitGroup
	done := 0
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for u := range jobs {
				_, _, err := a.covers.Poster(ctx, u, true)
				mu.Lock()
				if err == nil {
					st.OK++
				} else {
					st.Fail++
				}
				done++
				if done%100 == 0 || done == len(posters) {
					fmt.Fprintf(out, "[covers] %d/%d  ok=%d lỗi=%d  (%.0fs)\n", done, len(posters), st.OK, st.Fail, time.Since(t0).Seconds())
				}
				mu.Unlock()
			}
		}()
	}
feed:
	for _, u := range posters {
		select {
		case jobs <- u:
		case <-ctx.Done():
			break feed
		}
	}
	close(jobs)
	wg.Wait()
	fmt.Fprintf(out, "[covers] xong: %d truyện · chỉ có ảnh trong thư mục %d · poster tải được %d/%d (lỗi %d) · không có ảnh %d → %s\n",
		st.Stories, st.FolderImg, st.OK, st.Posters, st.Fail, st.NoCover, a.covers.Dir())
	return st
}
