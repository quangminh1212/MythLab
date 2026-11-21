// Command parity compares the JSON API of the Go server with the old Python
// server: every field the old server returns must come back with the same
// value from the new one (fields the new server adds are reported as notes).
//
//	go run ./tools/parity --old http://127.0.0.1:8765 --new http://127.0.0.1:18801
package main

import (
	"bytes"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"reflect"
	"sort"
	"strings"
	"time"
)

type result struct {
	status int
	ctype  string
	body   []byte
	err    error
}

type run struct {
	oldBase, newBase string
	hc               *http.Client
	checks, failed   int
	added            map[string]bool // fields only the new server has
	notes            []string
	verbose          bool
	sceneBreaks      int // chapters where the new server keeps more scene breaks
}

func (r *run) get(base, path string, q url.Values) result {
	u := base + path
	if len(q) > 0 {
		u += "?" + q.Encode()
	}
	resp, err := r.hc.Get(u)
	if err != nil {
		return result{err: err}
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	return result{status: resp.StatusCode, ctype: resp.Header.Get("Content-Type"), body: body, err: err}
}

func (r *run) both(path string, q url.Values) (o, n result) {
	return r.get(r.oldBase, path, q), r.get(r.newBase, path, q)
}

func (r *run) report(name string, diffs []string) bool {
	r.checks++
	if len(diffs) == 0 {
		if r.verbose {
			fmt.Printf("ok    %s\n", name)
		}
		return true
	}
	r.failed++
	fmt.Printf("DIFF  %s\n", name)
	for i, d := range diffs {
		if i == 12 {
			fmt.Printf("        ... %d more\n", len(diffs)-i)
			break
		}
		fmt.Printf("        %s\n", d)
	}
	return false
}

func short(v any) string {
	b, _ := json.Marshal(v)
	s := string(b)
	if r := []rune(s); len(r) > 90 {
		s = string(r[:90]) + "..."
	}
	return s
}

// subset checks that everything in o is in n with the same value. Objects may
// gain keys in n (recorded in added); arrays must match element by element.
func (r *run) subset(path string, o, n any, diffs *[]string) {
	switch ov := o.(type) {
	case map[string]any:
		nv, ok := n.(map[string]any)
		if !ok {
			*diffs = append(*diffs, fmt.Sprintf("%s: old %s, new %s", path, short(o), short(n)))
			return
		}
		keys := make([]string, 0, len(ov))
		for k := range ov {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		for _, k := range keys {
			x, ok := nv[k]
			if !ok {
				*diffs = append(*diffs, fmt.Sprintf("%s.%s: missing in new (old %s)", path, k, short(ov[k])))
				continue
			}
			r.subset(path+"."+k, ov[k], x, diffs)
		}
		for k := range nv {
			if _, ok := ov[k]; !ok {
				r.added[generic(path)+"."+k] = true
			}
		}
	case []any:
		nv, ok := n.([]any)
		if !ok || len(nv) != len(ov) {
			*diffs = append(*diffs, fmt.Sprintf("%s: old has %d items, new %s", path, len(ov), lenOf(n)))
			return
		}
		for i := range ov {
			r.subset(fmt.Sprintf("%s[%d]", path, i), ov[i], nv[i], diffs)
		}
	default:
		if !reflect.DeepEqual(o, n) {
			*diffs = append(*diffs, fmt.Sprintf("%s: old %s, new %s", path, short(o), short(n)))
		}
	}
}

func lenOf(v any) string {
	if a, ok := v.([]any); ok {
		return fmt.Sprintf("has %d", len(a))
	}
	return short(v)
}

// generic drops array indexes and per-item names from a path: stories[3].x -> stories[].x
func generic(p string) string {
	var b strings.Builder
	skip := false
	for _, c := range p {
		switch {
		case c == '[':
			skip = true
			b.WriteString("[")
		case c == ']':
			skip = false
			b.WriteString("]")
		case !skip:
			b.WriteRune(c)
		}
	}
	return b.String()
}

func decode(res result) (any, error) {
	if res.err != nil {
		return nil, res.err
	}
	var v any
	if err := json.Unmarshal(res.body, &v); err != nil {
		return nil, fmt.Errorf("HTTP %d, not JSON: %.80s", res.status, res.body)
	}
	return v, nil
}

// jsonPair fetches the same URL from both servers. ok is false when either
// side failed; equal failures (same status) are not a difference.
func (r *run) jsonPair(name, path string, q url.Values) (o, n any, ok bool) {
	ro, rn := r.both(path, q)
	if ro.err != nil || rn.err != nil {
		r.report(name, []string{fmt.Sprintf("request failed: old=%v new=%v", ro.err, rn.err)})
		return nil, nil, false
	}
	if ro.status != 200 || rn.status != 200 {
		if ro.status == rn.status {
			r.notes = append(r.notes, fmt.Sprintf("%s: both servers answer HTTP %d (old %.70s | new %.90s)", name, ro.status, ro.body, rn.body))
			return nil, nil, false
		}
		r.report(name, []string{fmt.Sprintf("status: old %d %.80s | new %d %.80s", ro.status, ro.body, rn.status, rn.body)})
		return nil, nil, false
	}
	o, err1 := decode(ro)
	n, err2 := decode(rn)
	if err1 != nil || err2 != nil {
		r.report(name, []string{fmt.Sprintf("old=%v new=%v", err1, err2)})
		return nil, nil, false
	}
	return o, n, true
}

func list(v any, key string) []any {
	m, _ := v.(map[string]any)
	a, _ := m[key].([]any)
	return a
}

func str(v any, key string) string {
	m, _ := v.(map[string]any)
	s, _ := m[key].(string)
	return s
}

func byKey(items []any, key string) (map[string]any, []string) {
	out := map[string]any{}
	var order []string
	for _, it := range items {
		k := str(it, key)
		out[k] = it
		order = append(order, k)
	}
	return out, order
}

func (r *run) ping() {
	if o, n, ok := r.jsonPair("ping", "/api/ping", nil); ok {
		var d []string
		r.subset("ping", o, n, &d)
		r.report("ping", d)
	}
}

// sources returns, per requested source, the repos to walk (nil for local).
func (r *run) sources() map[string][]string {
	repos := map[string][]string{}
	o, n, ok := r.jsonPair("sources", "/api/sources", nil)
	if !ok {
		return repos
	}
	var d []string
	om, _ := o.(map[string]any)
	nm, _ := n.(map[string]any)
	r.subset("sources.tts", om["tts"], nm["tts"], &d)
	oldBy, oldOrder := byKey(list(o, "sources"), "id")
	newBy, newOrder := byKey(list(n, "sources"), "id")
	if !reflect.DeepEqual(oldOrder, newOrder) {
		d = append(d, fmt.Sprintf("source ids: old %v, new %v", oldOrder, newOrder))
	}
	for _, id := range oldOrder {
		os_, ns := oldBy[id].(map[string]any), map[string]any{}
		if x, ok := newBy[id].(map[string]any); ok {
			ns = x
		}
		oa, _ := os_["available"].(bool)
		na, _ := ns["available"].(bool)
		if !oa || !na {
			// an unavailable source: the error text is free-form on both sides
			for _, k := range []string{"id", "name", "kind", "detail"} {
				r.subset("sources["+id+"]."+k, os_[k], ns[k], &d)
			}
			if oa != na {
				r.notes = append(r.notes, fmt.Sprintf("sources[%s].available: old %v (%v), new %v (%v)", id, oa, os_["error"], na, ns["error"]))
			}
		} else {
			r.subset("sources["+id+"]", oldBy[id], newBy[id], &d)
		}
		for _, rp := range list(ns, "repos") {
			repos[id] = append(repos[id], str(rp, "repo"))
		}
	}
	r.report("sources", d)
	return repos
}

// stories compares one listing and returns the keys to look into.
func (r *run) stories(source, repo string, take int) []string {
	q := url.Values{"source": {source}}
	name := "stories " + source
	if repo != "" {
		q.Set("repo", repo)
		name += " " + repo
	}
	o, n, ok := r.jsonPair(name, "/api/stories", q)
	if !ok {
		return nil
	}
	oldBy, oldOrder := byKey(list(o, "stories"), "key")
	newBy, newOrder := byKey(list(n, "stories"), "key")
	var d []string
	for _, k := range oldOrder {
		if _, ok := newBy[k]; !ok {
			d = append(d, "missing in new: "+k)
			continue
		}
		// Intended difference: chapter_files counts the chapters after duplicate
		// chapter numbers are removed, so it may be lower (never higher). The
		// story check verifies the removed entries for the stories it opens.
		om, _ := oldBy[k].(map[string]any)
		nm, _ := newBy[k].(map[string]any)
		oc, _ := om["chapter_files"].(float64)
		nc, isNum := nm["chapter_files"].(float64)
		if om != nil && nm != nil && isNum && nc < oc {
			cp := make(map[string]any, len(om))
			for f, v := range om {
				cp[f] = v
			}
			cp["chapter_files"] = nc
			r.notes = append(r.notes, fmt.Sprintf("%s: %s lists %v chapters, old %v (duplicate chapter numbers removed)", name, k, nc, oc))
			r.subset("stories["+k+"]", cp, newBy[k], &d)
			continue
		}
		r.subset("stories["+k+"]", oldBy[k], newBy[k], &d)
	}
	for _, k := range newOrder {
		if _, ok := oldBy[k]; !ok {
			d = append(d, "only in new: "+k)
		}
	}
	if len(d) == 0 && !reflect.DeepEqual(oldOrder, newOrder) {
		moved := 0
		for i := range oldOrder {
			if oldOrder[i] != newOrder[i] {
				moved++
			}
		}
		r.notes = append(r.notes, fmt.Sprintf("%s: same %d stories, %d at a different position (Vietnamese collation in the new server)", name, len(oldOrder), moved))
	}
	if r.report(name, d) && r.verbose {
		fmt.Printf("        %d stories\n", len(oldOrder))
	}
	// first, middle and last of the old order
	var keys []string
	for _, idx := range spread(len(oldOrder), take) {
		keys = append(keys, oldOrder[idx])
	}
	return keys
}

// spread picks up to take indexes of a list of n: first, last and evenly between.
func spread(n, take int) []int {
	take = min(take, n)
	var out []int
	for i := 0; i < take; i++ {
		out = append(out, i*(n-1)/max(take-1, 1))
	}
	return out
}

// story compares the detail and returns the chapter files to read.
func (r *run) story(source, key string, take int) []string {
	name := "story " + source + " " + key
	o, n, ok := r.jsonPair(name, "/api/story", url.Values{"source": {source}, "key": {key}})
	if !ok {
		return nil
	}
	om, _ := o.(map[string]any)
	nm, _ := n.(map[string]any)
	var d []string
	for k, v := range om {
		if k == "chapters" {
			continue
		}
		r.subset("story."+k, v, nm[k], &d)
	}
	for k := range nm {
		if _, ok := om[k]; !ok {
			r.added["story."+k] = true
		}
	}
	// chapters: the new server drops duplicate chapter numbers; everything it
	// keeps must be an old entry, in the old order
	oc, nc := list(o, "chapters"), list(n, "chapters")
	oldBy, _ := byKey(oc, "file")
	last := -1
	pos := map[string]int{}
	for i, c := range oc {
		pos[str(c, "file")] = i
	}
	for _, c := range nc {
		f := str(c, "file")
		oe, ok := oldBy[f]
		if !ok {
			d = append(d, "chapter only in new: "+f)
			continue
		}
		r.subset("chapters["+f+"]", oe, c, &d)
		if pos[f] < last {
			d = append(d, "chapter order differs at "+f)
		}
		last = pos[f]
	}
	if len(nc) != len(oc) {
		kept := map[string]bool{}
		for _, c := range nc {
			kept[str(c, "file")] = true
		}
		nums := map[any]bool{}
		for _, c := range nc {
			nums[c.(map[string]any)["n"]] = true
		}
		for _, c := range oc {
			if f := str(c, "file"); !kept[f] && !nums[c.(map[string]any)["n"]] {
				d = append(d, "chapter dropped without a duplicate number: "+f)
			}
		}
		r.notes = append(r.notes, fmt.Sprintf("%s: old lists %d chapters, new %d (duplicate chapter numbers removed)", name, len(oc), len(nc)))
	}
	r.report(name, d)
	var files []string
	for _, idx := range spread(len(nc), take) {
		files = append(files, str(nc[idx], "file"))
	}
	return files
}

func (r *run) chapter(source, key, file string) {
	name := "chapter " + source + " " + key + " / " + file
	o, n, ok := r.jsonPair(name, "/api/chapter", url.Values{"source": {source}, "key": {key}, "file": {file}})
	if !ok {
		return
	}
	// Intended difference: the old server deletes every rule line (-----, *****)
	// while the new one keeps it as the scene break "***", which it does not
	// count as a word. Scene breaks are left out of the comparison.
	om, _ := o.(map[string]any)
	nm, _ := n.(map[string]any)
	os_, oldBreaks := dropBreaks(om["paragraphs"])
	ns, newBreaks := dropBreaks(nm["paragraphs"])
	var d []string
	r.subset("chapter.paragraphs", os_, ns, &d)
	for k, v := range om {
		switch k {
		case "paragraphs":
		case "words":
			ow, _ := v.(float64)
			nw, _ := nm[k].(float64)
			if nw != ow-float64(oldBreaks) {
				d = append(d, fmt.Sprintf("chapter.words: old %v (%d scene breaks counted), new %v", ow, oldBreaks, nw))
			}
		default:
			r.subset("chapter."+k, v, nm[k], &d)
		}
	}
	for k := range nm {
		if _, ok := om[k]; !ok {
			r.added["chapter."+k] = true
		}
	}
	if oldBreaks != newBreaks {
		r.sceneBreaks++
	}
	r.report(name, d)
}

func dropBreaks(v any) (out []any, breaks int) {
	a, _ := v.([]any)
	out = []any{}
	for _, p := range a {
		if s, _ := p.(string); s == "***" {
			breaks++
			continue
		}
		out = append(out, p)
	}
	return out, breaks
}

func (r *run) cover(source, key string) {
	name := "cover " + source + " " + key
	ro, rn := r.both("/api/cover", url.Values{"source": {source}, "key": {key}})
	if ro.err != nil || rn.err != nil {
		r.report(name, []string{fmt.Sprintf("request failed: old=%v new=%v", ro.err, rn.err)})
		return
	}
	var d []string
	if ro.status != rn.status {
		d = append(d, fmt.Sprintf("status: old %d, new %d", ro.status, rn.status))
	} else if ro.status == 200 {
		if base(ro.ctype) != base(rn.ctype) {
			// Intended difference: the old server trusts the cached file's
			// extension, the new one the image's magic bytes.
			if bytes.Equal(ro.body, rn.body) && strings.HasPrefix(base(rn.ctype), "image/") && magic(rn.body) == base(rn.ctype) {
				r.notes = append(r.notes, fmt.Sprintf("%s: same bytes, old says %s, new %s (matches the content)", name, base(ro.ctype), base(rn.ctype)))
			} else {
				d = append(d, fmt.Sprintf("content type: old %s, new %s", ro.ctype, rn.ctype))
			}
		}
		if !bytes.Equal(ro.body, rn.body) {
			d = append(d, fmt.Sprintf("bytes: old %d (%s), new %d (%s)", len(ro.body), sum(ro.body), len(rn.body), sum(rn.body)))
		}
	}
	if r.report(name, d) && r.verbose {
		fmt.Printf("        HTTP %d %s %d bytes\n", rn.status, rn.ctype, len(rn.body))
	}
}

// magic names the image type of b by its first bytes.
func magic(b []byte) string {
	switch {
	case bytes.HasPrefix(b, []byte("\xff\xd8\xff")):
		return "image/jpeg"
	case bytes.HasPrefix(b, []byte("\x89PNG\r\n\x1a\n")):
		return "image/png"
	case bytes.HasPrefix(b, []byte("GIF8")):
		return "image/gif"
	case len(b) >= 12 && string(b[:4]) == "RIFF" && string(b[8:12]) == "WEBP":
		return "image/webp"
	}
	return ""
}

func base(ct string) string {
	if i := strings.IndexByte(ct, ';'); i >= 0 {
		ct = ct[:i]
	}
	return strings.ToLower(strings.TrimSpace(ct))
}

func sum(b []byte) string {
	h := sha1.Sum(b)
	return hex.EncodeToString(h[:6])
}

func main() {
	oldBase := flag.String("old", "http://127.0.0.1:8765", "old (Python) server")
	newBase := flag.String("new", "http://127.0.0.1:18801", "new (Go) server")
	srcs := flag.String("sources", "local0,gh0", "source ids to walk")
	nRepos := flag.Int("repos", 2, "GitHub repos per source")
	nStories := flag.Int("stories", 3, "stories per listing to open")
	nChapters := flag.Int("chapters", 2, "chapters per story to read")
	verbose := flag.Bool("v", false, "also print the checks that match")
	flag.Parse()

	r := &run{oldBase: strings.TrimRight(*oldBase, "/"), newBase: strings.TrimRight(*newBase, "/"),
		hc: &http.Client{Timeout: 5 * time.Minute}, added: map[string]bool{}, verbose: *verbose}
	r.ping()
	repos := r.sources()
	for _, src := range strings.Split(*srcs, ",") {
		src = strings.TrimSpace(src)
		if src == "" {
			continue
		}
		targets := []string{""}
		if strings.HasPrefix(src, "gh") {
			targets = repos[src]
			if len(targets) > *nRepos {
				targets = targets[:*nRepos]
			}
			if len(targets) == 0 {
				r.notes = append(r.notes, src+": the new server lists no repos, nothing to compare")
			}
		}
		for _, repo := range targets {
			for _, key := range r.stories(src, repo, *nStories) {
				for _, file := range r.story(src, key, *nChapters) {
					r.chapter(src, key, file)
				}
				r.cover(src, key)
			}
		}
	}

	if len(r.added) > 0 {
		keys := make([]string, 0, len(r.added))
		for k := range r.added {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		fmt.Println("fields only the new server returns: " + strings.Join(keys, ", "))
	}
	for _, n := range r.notes {
		fmt.Println("note: " + n)
	}
	if r.sceneBreaks > 0 {
		fmt.Printf("note: %d chapters keep scene breaks (***) the old server deleted\n", r.sceneBreaks)
	}
	fmt.Printf("%d checks, %d differ\n", r.checks, r.failed)
	if r.failed > 0 || r.checks == 0 {
		os.Exit(1)
	}
}
