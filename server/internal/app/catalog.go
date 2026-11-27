package app

import (
	"context"
	"time"
)

const (
	catalogPause    = 200 * time.Millisecond
	catalogInterval = 6 * time.Hour
	catalogRetry    = 20 * time.Minute // after a rate limit or error
)

// startCatalog keeps the on-disk story catalog complete so a title search never opens repos. Pass 1 collects
// every story name (one tree per repo) and refreshes the search index; pass 2 adds author and synopsis.
// Repos that are already cached cost little, and a rate limit just pauses the walk until the next try.
func (a *App) startCatalog() {
	if len(a.gh) == 0 {
		return
	}
	ctx, cancel := context.WithCancel(context.Background())
	a.catalogStop = cancel
	go func() {
		wait := 3 * time.Second
		for {
			select {
			case <-time.After(wait):
			case <-ctx.Done():
				return
			}
			wait = catalogInterval
			for _, details := range []bool{false, true} {
				stop := false
				for _, p := range a.gh {
					last := 0
					done, total, err := p.WarmCatalog(ctx, details, catalogPause, func(d, t int) {
						if d-last >= 25 {
							last = d
							a.search.RefreshAsync()
						}
					})
					a.log.Printf("[catalog] details=%v %d/%d repo", details, done, total)
					if err != nil && ctx.Err() == nil {
						a.log.Printf("[catalog] dừng sớm: %v", err)
						wait, stop = catalogRetry, true
					}
				}
				a.search.RefreshAsync()
				if stop || ctx.Err() != nil {
					break
				}
			}
		}
	}()
}
