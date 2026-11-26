package httpapi

import (
	"bytes"
	"context"
	"crypto/sha1"
	"encoding/hex"
	"errors"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"mythlab/internal/covers"
	"mythlab/internal/library"
)

// APIVersion is reported by /api/ping; the web UI uses the additive
// endpoints when it is at least 2.
const APIVersion = 2

type pingBody struct {
	OK     bool   `json:"ok"`
	App    string `json:"app"`
	API    int    `json:"api"`
	Server string `json:"server"`
	// Features lists optional capabilities (additive: api stays 2).
	Features []string  `json:"features,omitempty"`
	Auth     *pingAuth `json:"auth,omitempty"`
}

// pingAuth tells clients that Google sign-in is available.
type pingAuth struct {
	Google   bool   `json:"google"`
	ClientID string `json:"client_id"`
}

// ttsInfo is kept in /api/sources only for older clients: the server has no voices.
type ttsInfo struct {
	Edge         bool   `json:"edge"`
	DefaultVoice string `json:"default_voice"`
}

type sourcesBody struct {
	Sources []library.SourceInfo `json:"sources"`
	TTS     ttsInfo              `json:"tts"`
}

type tagCount struct {
	Name  string `json:"name"`
	Count int    `json:"count"`
}

type storiesBody struct {
	Stories []library.StoryItem `json:"stories"`
	Total   *int                `json:"total,omitempty"`
	Tags    *[]tagCount         `json:"tags,omitempty"`
	// Statuses and All describe the whole listing (before filters), so the UI can keep its filter menu stable.
	Statuses *[]string `json:"statuses,omitempty"`
	All      *int      `json:"all,omitempty"`
	Stale    bool      `json:"stale,omitempty"`
}

// fail maps an error to the JSON error response.
func (s *Server) fail(w http.ResponseWriter, r *http.Request, err error) {
	var le *library.Error
	switch {
	case errors.As(err, &le):
		s.writeErr(w, r, le.Status, le.Code, le.Msg)
	case r.Context().Err() != nil:
		// the client went away: nothing to answer; 499 only shows in the log
		if sw, ok := w.(*statusWriter); ok && !sw.wrote {
			sw.status = 499
		}
	case errors.Is(err, context.DeadlineExceeded):
		s.writeErr(w, r, http.StatusGatewayTimeout, "timeout", "quá thời gian chờ")
	default:
		s.o.Logf("[lỗi] %s %s: %v", r.Method, MaskKey(r.URL.RequestURI()), err)
		s.writeErr(w, r, http.StatusInternalServerError, "internal", "lỗi máy chủ")
	}
}

func need(q map[string]string, name string) (string, error) {
	v := q[name]
	if v == "" {
		return "", library.ErrBadParam(name)
	}
	return v, nil
}

// intParam parses an optional integer parameter.
// maxStoriesLimit caps the page size of /api/stories.
const maxStoriesLimit = 5000

func intParam(q map[string]string, name string, def int) (int, error) {
	v := strings.TrimSpace(q[name])
	if v == "" {
		return def, nil
	}
	n, err := strconv.Atoi(v)
	if err != nil {
		return 0, library.ErrBadParam(name)
	}
	return n, nil
}

func (s *Server) api(w http.ResponseWriter, r *http.Request) {
	s.cors(w, r)
	q := lastQuery(r.URL.RawQuery)
	route := strings.TrimPrefix(r.URL.Path, "/api/")
	// A session token authorizes only progress, library and auth; the story
	// content routes below still need the access key.
	user, ok := s.sessionUser(w, r, route)
	if !ok {
		return
	}
	needKey := s.keyRequired(r)
	hasKey := s.presentedKey(r, q)
	if strings.HasPrefix(route, "auth/") {
		needKey = false // login needs no key; the other auth routes check the token themselves
	}
	if needKey && !hasKey && user == nil {
		s.writeErr(w, r, http.StatusUnauthorized, "unauthorized", "cần khoá truy cập (X-MythLab-Key)")
		return
	}
	if s.crossSiteBlocked(r, hasKey || user != nil) {
		s.writeErr(w, r, http.StatusForbidden, "cross_site", "trang web khác không được gọi API này")
		return
	}
	var err error
	switch route {
	case "ping":
		body := pingBody{OK: true, App: "mythlab", API: APIVersion, Server: "go"}
		if s.o.Progress != nil {
			body.Features = []string{"progress"}
		}
		if s.o.Auth != nil {
			body.Features = append(body.Features, "auth", "library")
			body.Auth = &pingAuth{Google: true, ClientID: s.o.Auth.ClientID()}
		}
		s.writeJSON(w, r, http.StatusOK, body, "")
	case "progress":
		s.apiProgress(w, r, q, user)
	case "library":
		s.apiLibrary(w, r, q, user)
	case "auth/google", "auth/me", "auth/logout":
		s.apiAuth(w, r, route, user)
	case "sources":
		s.apiSources(w, r)
	case "stories":
		err = s.apiStories(w, r, q)
	case "story":
		err = s.apiStory(w, r, q)
	case "chapter":
		err = s.apiChapter(w, r, q)
	case "cover":
		err = s.apiCover(w, r, q, needKey)
	case "search":
		err = s.apiSearch(w, r, q)
	default:
		s.writeErr(w, r, http.StatusNotFound, "no_route", "không có API này")
	}
	if err != nil {
		s.fail(w, r, err)
	}
}

func (s *Server) providers() []library.Provider {
	if s.o.Library == nil {
		return nil
	}
	return s.o.Library.Providers()
}

func (s *Server) provider(q map[string]string) (library.Provider, error) {
	id, err := need(q, "source")
	if err != nil {
		return nil, err
	}
	if s.o.Library == nil {
		return nil, library.ErrBadParam("source")
	}
	return s.o.Library.Get(id)
}

func (s *Server) apiSources(w http.ResponseWriter, r *http.Request) {
	local := IsLoopback(r.RemoteAddr)
	out := []library.SourceInfo{}
	for _, p := range s.providers() {
		d := p.Describe(r.Context())
		if !local && p.Kind() == "local" {
			// other machines have no use for this machine's directory layout
			d.Detail = filepath.Base(d.Detail)
		}
		out = append(out, d)
	}
	s.writeJSON(w, r, http.StatusOK, sourcesBody{out, ttsInfo{false, "vi-VN-HoaiMyNeural"}}, "")
}

func storyLabels(it library.StoryItem) []string {
	seen := map[string]bool{}
	var out []string
	for _, list := range [][]string{it.Tags, it.Genres} {
		for _, t := range list {
			t = strings.TrimSpace(t)
			k := library.NormKey(t)
			if k == "" || seen[k] {
				continue
			}
			seen[k] = true
			out = append(out, t)
		}
	}
	return out
}

func countTags(items []library.StoryItem) []tagCount {
	idx := map[string]int{}
	out := []tagCount{}
	for _, it := range items {
		for _, t := range storyLabels(it) {
			k := library.NormKey(t)
			if i, ok := idx[k]; ok {
				out[i].Count++
			} else {
				idx[k] = len(out)
				out = append(out, tagCount{t, 1})
			}
		}
	}
	sort.SliceStable(out, func(i, j int) bool {
		if out[i].Count != out[j].Count {
			return out[i].Count > out[j].Count
		}
		return out[i].Name < out[j].Name
	})
	return out
}

func storyMatches(it library.StoryItem, toks []string) bool {
	author := ""
	if it.Author != nil {
		author = *it.Author
	}
	group := ""
	if it.Group != nil {
		group = *it.Group
	}
	hay := library.NormKey(strings.Join([]string{it.Name, it.Folder, author, strings.Join(it.Tags, " "), strings.Join(it.Genres, " "), group}, " "))
	compact := strings.ReplaceAll(hay, " ", "")
	for _, t := range toks {
		if !strings.Contains(hay, t) && !strings.Contains(compact, t) {
			return false
		}
	}
	return true
}

func (s *Server) apiStories(w http.ResponseWriter, r *http.Request, q map[string]string) error {
	p, err := s.provider(q)
	if err != nil {
		return err
	}
	offset, err := intParam(q, "offset", 0)
	if err != nil {
		return err
	}
	limit, err := intParam(q, "limit", 0)
	if err != nil {
		return err
	}
	if offset < 0 || limit < 0 {
		return library.ErrBadParam("limit")
	}
	if limit > maxStoriesLimit {
		limit = maxStoriesLimit
	}
	sortBy := q["sort"]
	switch sortBy {
	case "", "name", "chapters", "updated":
	default:
		return library.ErrBadParam("sort")
	}
	items, stale, err := p.ListStories(r.Context(), q["repo"])
	if err != nil {
		return err
	}
	if items == nil {
		items = []library.StoryItem{}
	}
	body := storiesBody{Stale: stale}
	if limit > 0 {
		tags := countTags(items) // over the whole listing: stable filter chips
		body.Tags = &tags
		statuses := distinctStatuses(items)
		all := len(items)
		body.Statuses, body.All = &statuses, &all
	}
	toks := strings.Fields(library.NormKey(q["q"]))
	status, tag := library.NormKey(q["status"]), library.NormKey(q["tag"])
	if len(toks) > 0 || status != "" || tag != "" {
		kept := make([]library.StoryItem, 0, len(items))
		for _, it := range items {
			if status != "" && (it.Status == nil || library.NormKey(*it.Status) != status) {
				continue
			}
			if tag != "" {
				ok := false
				for _, t := range storyLabels(it) {
					if library.NormKey(t) == tag {
						ok = true
						break
					}
				}
				if !ok {
					continue
				}
			}
			if len(toks) > 0 && !storyMatches(it, toks) {
				continue
			}
			kept = append(kept, it)
		}
		items = kept
	}
	if sortBy != "" {
		items = append([]library.StoryItem(nil), items...) // never reorder the provider's slice
		library.SortVi(items, func(it library.StoryItem) string { return it.Name })
		switch sortBy {
		case "chapters":
			sort.SliceStable(items, func(i, j int) bool { return items[i].ChapterFiles > items[j].ChapterFiles })
		case "updated":
			sort.SliceStable(items, func(i, j int) bool { return items[i].Updated > items[j].Updated })
		}
	}
	if limit > 0 || offset > 0 {
		total := len(items)
		if limit > 0 {
			body.Total = &total
		}
		if offset > total {
			offset = total
		}
		end := total
		if limit > 0 && limit < end-offset { // no offset+limit: it could overflow
			end = offset + limit
		}
		items = items[offset:end]
	}
	body.Stories = items
	s.writeJSON(w, r, http.StatusOK, body, "")
	return nil
}

// distinctStatuses lists the status values of a listing, Vietnamese-sorted.
func distinctStatuses(items []library.StoryItem) []string {
	seen := map[string]bool{}
	out := []string{}
	for _, it := range items {
		if it.Status == nil {
			continue
		}
		v := strings.TrimSpace(*it.Status)
		if v != "" && !seen[v] {
			seen[v] = true
			out = append(out, v)
		}
	}
	library.SortVi(out, func(v string) string { return v })
	return out
}

func bodyTag(b []byte) string {
	h := sha1.Sum(b)
	return `"` + hex.EncodeToString(h[:10]) + `"`
}

// writeTagged sends a JSON body whose ETag is derived from its bytes.
func (s *Server) writeTagged(w http.ResponseWriter, r *http.Request, v any, etag string) {
	body := marshal(v)
	if etag == "" {
		etag = bodyTag(body)
	}
	h := w.Header()
	h.Set("ETag", etag)
	h.Set("Cache-Control", "private, no-cache")
	if etagMatch(r, etag) {
		h.Add("Vary", "Accept-Encoding")
		w.WriteHeader(http.StatusNotModified)
		return
	}
	s.writeBody(w, r, http.StatusOK, "application/json; charset=utf-8", body, true)
}

func (s *Server) apiStory(w http.ResponseWriter, r *http.Request, q map[string]string) error {
	p, err := s.provider(q)
	if err != nil {
		return err
	}
	key, err := need(q, "key")
	if err != nil {
		return err
	}
	st, err := p.Story(r.Context(), key)
	if err != nil {
		return err
	}
	if st.Chapters == nil {
		st.Chapters = []library.Chapter{}
	}
	s.writeTagged(w, r, st, "")
	return nil
}

func (s *Server) apiChapter(w http.ResponseWriter, r *http.Request, q map[string]string) error {
	p, err := s.provider(q)
	if err != nil {
		return err
	}
	key, err := need(q, "key")
	if err != nil {
		return err
	}
	file, err := need(q, "file")
	if err != nil {
		return err
	}
	data, _, err := p.ReadChapter(r.Context(), key, file)
	if err != nil {
		return err
	}
	ch := library.BuildChapterJSON(library.DecodeText(data), file)
	if ch.Paragraphs == nil {
		ch.Paragraphs = []string{}
	}
	s.writeTagged(w, r, ch, "")
	return nil
}

func (s *Server) apiSearch(w http.ResponseWriter, r *http.Request, q map[string]string) error {
	limit, err := intParam(q, "limit", 20)
	if err != nil {
		return err
	}
	offset, err := intParam(q, "offset", 0)
	if err != nil {
		return err
	}
	if limit < 1 || offset < 0 {
		return library.ErrBadParam("limit")
	}
	if limit > 100 {
		limit = 100
	}
	source := q["source"]
	if source != "" {
		if _, err := s.provider(q); err != nil {
			return err
		}
	}
	query := q["q"]
	if len(query) > 200 {
		query = strings.ToValidUTF8(query[:200], "")
	}
	res := library.SearchResult{Q: query, Items: []library.StoryItem{}}
	if s.o.Search != nil {
		res = s.o.Search.Search(r.Context(), query, source, offset, limit)
	}
	s.writeJSON(w, r, http.StatusOK, res, "")
	return nil
}

var errNoCover = &library.Error{Status: http.StatusNotFound, Code: "no_cover", Msg: "truyện chưa có ảnh bìa"}

func cacheControl(public bool, rest string) string {
	if public {
		return "public, " + rest
	}
	return "private, " + rest
}

// serveFile streams a cache file with Range and conditional support.
func (s *Server) serveFile(w http.ResponseWriter, r *http.Request, path, ctype, etag, cache string) error {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()
	st, err := f.Stat()
	if err != nil || !st.Mode().IsRegular() {
		return os.ErrNotExist
	}
	h := w.Header()
	h.Set("Content-Type", ctype)
	h.Set("Cache-Control", cache)
	if etag == "" {
		etag = `"` + strconv.FormatInt(st.ModTime().UnixNano(), 36) + "-" + strconv.FormatInt(st.Size(), 36) + `"`
	}
	h.Set("ETag", etag)
	http.ServeContent(w, r, "", st.ModTime(), f)
	return nil
}

func (s *Server) apiCover(w http.ResponseWriter, r *http.Request, q map[string]string, needKey bool) error {
	p, err := s.provider(q)
	if err != nil {
		return err
	}
	key, err := need(q, "key")
	if err != nil {
		return err
	}
	width := 0
	if v := q["w"]; v != "" {
		if width, err = strconv.Atoi(v); err != nil || !covers.Widths[width] {
			return library.ErrBadParam("w")
		}
	}
	ctx := r.Context()
	ref, err := p.Cover(ctx, key)
	if err != nil {
		return err
	}
	if ref.Poster != "" {
		if s.o.Covers == nil {
			return errNoCover
		}
		path, ctype, perr := s.o.Covers.Poster(ctx, ref.Poster, false)
		if perr != nil {
			if ctx.Err() != nil {
				return ctx.Err()
			}
			return errNoCover
		}
		ref = library.CoverRef{Path: path, Ctype: ctype, Tag: "p-" + covers.Key(ref.Poster)}
		if st, serr := os.Stat(path); serr == nil {
			ref.Tag += "-" + strconv.FormatInt(st.Size(), 36)
		}
	}
	if ref.Path == "" && len(ref.Data) == 0 {
		return errNoCover
	}
	if ref.Ctype == "" {
		ref.Ctype = "application/octet-stream"
	}
	cache := cacheControl(!needKey, "max-age=2592000")
	etag := ""
	if ref.Tag != "" {
		etag = `"` + covers.Key(ref.Tag)[:20] + `"`
	}
	if width > 0 && s.o.Covers != nil && ref.Tag != "" {
		load := func() ([]byte, error) {
			if ref.Path != "" {
				return os.ReadFile(ref.Path)
			}
			return ref.Data, nil
		}
		small, rerr := s.o.Covers.Resized(ctx, ref.Tag, width, load)
		switch {
		case rerr == nil:
			tag := `"` + covers.Key(ref.Tag)[:20] + "-" + strconv.Itoa(width) + `"`
			if serr := s.serveFile(w, r, small, "image/jpeg", tag, cache); serr == nil {
				return nil
			}
		case ctx.Err() != nil:
			return ctx.Err()
		case !errors.Is(rerr, covers.ErrNoResize):
			s.o.Logf("[covers] không thu nhỏ được ảnh bìa: %v", rerr)
		}
	}
	if ref.Path != "" {
		if serr := s.serveFile(w, r, ref.Path, ref.Ctype, etag, cache); serr != nil {
			return errNoCover
		}
		return nil
	}
	h := w.Header()
	h.Set("Content-Type", ref.Ctype)
	h.Set("Cache-Control", cache)
	if etag != "" {
		h.Set("ETag", etag)
	}
	http.ServeContent(w, r, "", ref.ModTime, bytes.NewReader(ref.Data))
	return nil
}
