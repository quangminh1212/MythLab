package library

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"
)

const (
	ghDefaultAPI   = "https://api.github.com"
	ghJSONLimit    = 512 << 20 // a recursive tree of a very large repo
	ghBlobLimit    = 32 << 20
	ghTokenRetry   = 60 * time.Second
	ghMaxBlock     = time.Hour
	ghDefaultBlock = 60 * time.Second
)

// errRateLimited is returned without touching the network while GitHub has
// told us to back off.
var errRateLimited = &Error{Status: http.StatusBadGateway, Code: "rate_limited", Msg: "GitHub đang giới hạn tần suất, thử lại sau"}

// ghClient talks to the GitHub REST API: token discovery, common headers,
// rate-limit tracking.
type ghClient struct {
	base    string
	hc      *http.Client
	tokenFn func() string
	now     func() time.Time

	mu           sync.Mutex
	token        string
	tokenAt      time.Time
	tokenOK      bool
	blockedUntil time.Time
}

func newGHClient(base string, hc *http.Client, tokenFn func() string) *ghClient {
	if base == "" {
		base = ghDefaultAPI
	}
	if hc == nil {
		hc = &http.Client{}
	}
	if tokenFn == nil {
		tokenFn = discoverToken
	}
	return &ghClient{base: strings.TrimRight(base, "/"), hc: hc, tokenFn: tokenFn, now: time.Now}
}

// discoverToken: GITHUB_TOKEN, GH_TOKEN, then `gh auth token`.
func discoverToken() string {
	for _, k := range []string{"GITHUB_TOKEN", "GH_TOKEN"} {
		if v := strings.TrimSpace(os.Getenv(k)); v != "" {
			return v
		}
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "gh", "auth", "token")
	hideWindow(cmd)
	out, err := cmd.Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
}

// getToken caches a found token for the process lifetime; an empty result is
// retried after a while (the user may log in later).
func (c *ghClient) getToken() string {
	c.mu.Lock()
	if c.tokenOK && (c.token != "" || c.now().Sub(c.tokenAt) < ghTokenRetry) {
		t := c.token
		c.mu.Unlock()
		return t
	}
	c.mu.Unlock()
	t := c.tokenFn()
	c.mu.Lock()
	c.token, c.tokenAt, c.tokenOK = t, c.now(), true
	c.mu.Unlock()
	return t
}

func (c *ghClient) dropToken() {
	c.mu.Lock()
	c.token, c.tokenOK = "", false
	c.mu.Unlock()
}

// blocked reports whether GitHub asked us to wait.
func (c *ghClient) blocked() bool {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.now().Before(c.blockedUntil)
}

func (c *ghClient) block(until time.Time) {
	now := c.now()
	if until.After(now.Add(ghMaxBlock)) {
		until = now.Add(ghMaxBlock)
	}
	c.mu.Lock()
	if until.After(c.blockedUntil) {
		c.blockedUntil = until
	}
	c.mu.Unlock()
}

// noteLimits inspects rate-limit headers; limited says the response itself was a refusal.
func (c *ghClient) noteLimits(h http.Header, limited bool) {
	now := c.now()
	if ra := strings.TrimSpace(h.Get("Retry-After")); ra != "" && limited {
		if n, err := strconv.Atoi(ra); err == nil && n >= 0 {
			c.block(now.Add(time.Duration(n) * time.Second))
			return
		}
	}
	if h.Get("X-RateLimit-Remaining") == "0" {
		if n, err := strconv.ParseInt(h.Get("X-RateLimit-Reset"), 10, 64); err == nil && n > 0 {
			c.block(time.Unix(n, 0))
			return
		}
		c.block(now.Add(ghDefaultBlock))
		return
	}
	if limited {
		c.block(now.Add(ghDefaultBlock))
	}
}

var linkNext = regexp.MustCompile(`<([^>]+)>;\s*rel="next"`)

// get performs one API call. path is "/..." or an absolute URL on the API host
// (pagination). It returns the body and the URL of the next page, if any.
func (c *ghClient) get(ctx context.Context, path string, raw bool, timeout time.Duration) ([]byte, string, error) {
	if c.blocked() {
		return nil, "", errRateLimited
	}
	url := path
	if strings.HasPrefix(path, "/") {
		url = c.base + path
	} else if !strings.HasPrefix(path, c.base+"/") {
		return nil, "", ErrUpstream("GitHub: URL phân trang không hợp lệ")
	}
	if timeout <= 0 {
		timeout = 60 * time.Second
	}
	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, "", ErrUpstream("GitHub: yêu cầu không hợp lệ")
	}
	req.Header.Set("User-Agent", "mythlab-reader")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")
	limit := int64(ghJSONLimit)
	if raw {
		req.Header.Set("Accept", "application/vnd.github.raw")
		limit = ghBlobLimit
	} else {
		req.Header.Set("Accept", "application/vnd.github+json")
	}
	if t := c.getToken(); t != "" {
		req.Header.Set("Authorization", "Bearer "+t)
	}
	resp, err := c.hc.Do(req)
	if err != nil {
		if ctx.Err() != nil && errors.Is(ctx.Err(), context.Canceled) {
			return nil, "", ctx.Err()
		}
		return nil, "", &Error{Status: http.StatusBadGateway, Code: "upstream_unreachable", Msg: "không kết nối được GitHub"}
	}
	defer resp.Body.Close()
	if resp.StatusCode < 200 || resp.StatusCode > 299 {
		io.Copy(io.Discard, io.LimitReader(resp.Body, 64<<10))
		limited := resp.StatusCode == http.StatusTooManyRequests ||
			(resp.StatusCode == http.StatusForbidden && (resp.Header.Get("X-RateLimit-Remaining") == "0" || resp.Header.Get("Retry-After") != ""))
		c.noteLimits(resp.Header, limited)
		if limited {
			return nil, "", errRateLimited
		}
		if resp.StatusCode == http.StatusUnauthorized {
			c.dropToken()
		}
		reason := http.StatusText(resp.StatusCode)
		return nil, "", &Error{Status: http.StatusBadGateway, Code: "upstream", Msg: fmt.Sprintf("GitHub %d: %s", resp.StatusCode, reason)}
	}
	c.noteLimits(resp.Header, false)
	body, err := io.ReadAll(io.LimitReader(resp.Body, limit+1))
	if err != nil {
		if errors.Is(ctx.Err(), context.Canceled) {
			return nil, "", ctx.Err()
		}
		return nil, "", &Error{Status: http.StatusBadGateway, Code: "upstream_unreachable", Msg: "GitHub trả lời dở dang"}
	}
	if int64(len(body)) > limit {
		return nil, "", ErrUpstream("GitHub: phản hồi quá lớn")
	}
	next := ""
	if m := linkNext.FindStringSubmatch(resp.Header.Get("Link")); m != nil {
		next = m[1]
	}
	return body, next, nil
}

// upstreamStatus returns the GitHub HTTP status carried by err (0 when none).
func upstreamStatus(err error) int {
	if e, ok := AsError(err); ok && e.Code == "upstream" {
		var n int
		if _, err := fmt.Sscanf(e.Msg, "GitHub %d:", &n); err == nil {
			return n
		}
	}
	return 0
}
