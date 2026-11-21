// Package library holds the story providers (local folders, GitHub repos), the
// chapter/text parsing shared with the web client, and the search index.
package library

import (
	"bytes"
	"encoding/json"
	"path"
	"sort"
	"strconv"
	"strings"
	"unicode"
	"unicode/utf16"
	"unicode/utf8"

	"golang.org/x/text/unicode/norm"
)

// SceneBreak is the paragraph emitted for a rule line inside a chapter body.
const SceneBreak = "***"

// isWS reports whether r is in Python's str.isspace set (the set the old
// server and textutil.js used).
func isWS(r rune) bool {
	switch {
	case r >= 0x09 && r <= 0x0d, r >= 0x1c && r <= 0x20, r == 0x85, r == 0xa0, r == 0x1680,
		r >= 0x2000 && r <= 0x200a, r == 0x2028, r == 0x2029, r == 0x202f, r == 0x205f, r == 0x3000:
		return true
	}
	return false
}

func pyStrip(s string) string { return strings.TrimFunc(s, isWS) }

// NaturalTitle trims whitespace and the separator characters "-:. " from both ends.
func NaturalTitle(raw string) string {
	return pyStrip(strings.Trim(pyStrip(raw), "-:. "))
}

// ChapterName is a parsed chapter file name.
type ChapterName struct {
	N     int64
	Title string
	Sub   int64
	Vol   int64
}

type scanner struct {
	r []rune
	i int
}

func (s *scanner) ws() int {
	n := 0
	for s.i < len(s.r) && isWS(s.r[s.i]) {
		s.i++
		n++
	}
	return n
}

func (s *scanner) digits() (int64, bool) {
	var v int64
	n := 0
	for s.i < len(s.r) && unicode.IsDigit(s.r[s.i]) {
		d := digitVal(s.r[s.i])
		v = v*10 + int64(d)
		s.i++
		n++
		if n > 15 {
			return 0, false
		}
	}
	return v, n > 0
}

// digitVal returns the value of a Unicode decimal digit (Nd), or -1. Nd digits
// come in contiguous runs of ten (possibly several runs back to back) starting at zero.
func digitVal(r rune) int {
	if r >= '0' && r <= '9' {
		return int(r - '0')
	}
	if !unicode.IsDigit(r) {
		return -1
	}
	z := r
	for unicode.IsDigit(z - 1) {
		z--
	}
	return int(r-z) % 10
}

func (s *scanner) word(words ...string) bool {
	for _, w := range words {
		wr := []rune(w)
		if s.i+len(wr) > len(s.r) {
			continue
		}
		ok := true
		for k, c := range wr {
			if unicode.ToLower(s.r[s.i+k]) != c {
				ok = false
				break
			}
		}
		if ok {
			s.i += len(wr)
			return true
		}
	}
	return false
}

func (s *scanner) oneOf(set string) bool {
	if s.i < len(s.r) && strings.ContainsRune(set, s.r[s.i]) {
		s.i++
		return true
	}
	return false
}

// ParseChapterName parses "Chương <N> <title>.txt" (see testdata/textutil_cases.json for the grammar).
func ParseChapterName(filename string) (ChapterName, bool) {
	var out ChapterName
	name := norm.NFC.String(filename)
	if len(name) < 4 || !strings.EqualFold(name[len(name)-4:], ".txt") {
		return out, false
	}
	s := &scanner{r: []rune(name[:len(name)-4])}
	if s.word("quyển", "quyen", "tập", "tap") {
		if s.ws() == 0 {
			return out, false
		}
		v, ok := s.digits()
		if !ok {
			return out, false
		}
		out.Vol = v
		s.ws()
		s.oneOf("-:.,–")
		s.ws()
	}
	if !s.word("chương", "chuong") {
		return out, false
	}
	if s.ws() == 0 {
		return out, false
	}
	n, ok := s.digits()
	if !ok {
		return out, false
	}
	out.N = n
	if s.i < len(s.r) && (s.r[s.i] == '.' || s.r[s.i] == '-') {
		save := s.i
		s.i++
		if v, ok := s.digits(); ok && (s.i == len(s.r) || isWS(s.r[s.i])) {
			out.Sub = v
		} else {
			s.i = save
		}
	}
	s.ws()
	s.oneOf("-:.–")
	s.ws()
	out.Title = NaturalTitle(string(s.r[s.i:]))
	return out, true
}

// Chapter is one entry of a story's chapter list as sent to clients.
type Chapter struct {
	N     int64  `json:"n"`
	Title string `json:"title"`
	File  string `json:"file"`
	Sub   int64  `json:"sub,omitempty"`
	Vol   int64  `json:"vol,omitempty"`
}

// ChapterList parses, sorts by (vol, n, sub, file) and de-duplicates file names.
func ChapterList(files []string) []Chapter {
	out := make([]Chapter, 0, len(files))
	for _, f := range files {
		if p, ok := ParseChapterName(f); ok {
			out = append(out, Chapter{N: p.N, Title: p.Title, File: f, Sub: p.Sub, Vol: p.Vol})
		}
	}
	return SortDedupe(out)
}

// SortDedupe sorts chapters and removes entries with the same number and the same normalised title.
func SortDedupe(out []Chapter) []Chapter {
	sort.Slice(out, func(i, j int) bool {
		a, b := &out[i], &out[j]
		if a.Vol != b.Vol {
			return a.Vol < b.Vol
		}
		if a.N != b.N {
			return a.N < b.N
		}
		if a.Sub != b.Sub {
			return a.Sub < b.Sub
		}
		return a.File < b.File
	})
	w := 0
	for i := range out {
		dup := false
		for k := w - 1; k >= 0; k-- {
			p := &out[k]
			if p.Vol != out[i].Vol || p.N != out[i].N || p.Sub != out[i].Sub {
				break
			}
			if p.Title == out[i].Title || Compact(p.Title) == Compact(out[i].Title) {
				dup = true
				break
			}
		}
		if !dup {
			out[w] = out[i]
			w++
		}
	}
	return out[:w]
}

func isRule(line string) bool {
	s := pyStrip(line)
	if len(s) < 5 {
		return false
	}
	for i := 0; i < len(s); i++ {
		switch s[i] {
		case '=', '-', '_', '*':
		default:
			return false
		}
	}
	return true
}

func collapseSpaces(s string) string {
	if !strings.ContainsAny(s, "\t") && !strings.Contains(s, "  ") {
		return s
	}
	var b strings.Builder
	b.Grow(len(s))
	prev := false
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c == ' ' || c == '\t' {
			if !prev {
				b.WriteByte(' ')
			}
			prev = true
			continue
		}
		prev = false
		b.WriteByte(c)
	}
	return b.String()
}

// chapterHeadNumber returns the number of a paragraph starting with "Chương <digits>".
func chapterHeadNumber(p string) (int64, bool) {
	s := &scanner{r: []rune(norm.NFC.String(p))}
	if !s.word("chương", "chuong") || s.ws() == 0 {
		return 0, false
	}
	// the old regex only required one digit; value is used for the n check
	var v int64
	n := 0
	for s.i < len(s.r) && unicode.IsDigit(s.r[s.i]) {
		if n < 15 {
			v = v*10 + int64(digitVal(s.r[s.i]))
		}
		s.i++
		n++
	}
	return v, n > 0
}

// CleanChapterText splits raw chapter text into an optional title and paragraphs.
// n is the chapter number from the file name; pass hasN=false when unknown.
func CleanChapterText(text string, n int64, hasN bool) (title string, hasTitle bool, paras []string) {
	text = strings.ReplaceAll(text, "\r\n", "\n")
	text = strings.ReplaceAll(text, "\r", "\n")
	text = strings.TrimLeft(text, "\ufeff")
	lines := strings.Split(text, "\n")
	var head []int
	for i := 0; i < len(lines) && i < 8; i++ {
		if isRule(lines[i]) {
			head = append(head, i)
		}
	}
	if len(head) >= 2 && head[1]-head[0] <= 4 {
		blankBefore := true
		for _, ln := range lines[:head[0]] {
			if pyStrip(ln) != "" {
				blankBefore = false
				break
			}
		}
		if blankBefore {
			var inner []string
			for _, ln := range lines[head[0]+1 : head[1]] {
				if s := pyStrip(ln); s != "" {
					inner = append(inner, s)
				}
			}
			if len(inner) > 0 {
				title, hasTitle = strings.Join(inner, " "), true
			}
			lines = lines[head[1]+1:]
		}
	}
	paras = make([]string, 0, len(lines)/2+1)
	for _, ln := range lines {
		p := pyStrip(collapseSpaces(ln))
		if p == "" {
			continue
		}
		if isRule(p) {
			p = SceneBreak
		}
		paras = append(paras, p)
	}
	// a lone rule above the heading ("=====" / "Chương 1: X" / text) is decoration
	for len(paras) > 0 && paras[0] == SceneBreak {
		paras = paras[1:]
	}
	if !hasTitle && len(paras) > 0 && utf8.RuneCountInString(paras[0]) < 160 {
		if num, ok := chapterHeadNumber(paras[0]); ok && (!hasN || num == n) {
			title, hasTitle = paras[0], true
			paras = paras[1:]
		}
	}
	// scene breaks: no leading, trailing or repeated ones
	out := make([]string, 0, len(paras))
	for _, p := range paras {
		if p == SceneBreak && (len(out) == 0 || out[len(out)-1] == SceneBreak) {
			continue
		}
		out = append(out, p)
	}
	for len(out) > 0 && out[len(out)-1] == SceneBreak {
		out = out[:len(out)-1]
	}
	return title, hasTitle, out
}

// CountWords counts whitespace-separated tokens, ignoring scene breaks.
func CountWords(paras []string) int {
	n := 0
	for _, p := range paras {
		if p == SceneBreak {
			continue
		}
		n += len(strings.FieldsFunc(p, isWS))
	}
	return n
}

// ChapterJSON is the /api/chapter payload.
type ChapterJSON struct {
	Title      *string  `json:"title"`
	Paragraphs []string `json:"paragraphs"`
	Words      int      `json:"words"`
}

// FallbackTitle builds "Chương N: title" from a parsed file name.
func FallbackTitle(p ChapterName) string {
	var b strings.Builder
	if p.Vol != 0 {
		b.WriteString("Quyển " + strconv.FormatInt(p.Vol, 10) + " - ")
	}
	b.WriteString("Chương " + strconv.FormatInt(p.N, 10))
	if p.Sub != 0 {
		b.WriteString("." + strconv.FormatInt(p.Sub, 10))
	}
	if p.Title != "" {
		b.WriteString(": " + p.Title)
	}
	return b.String()
}

// BuildChapterJSON turns raw text + file name into the /api/chapter payload.
func BuildChapterJSON(text, file string) ChapterJSON {
	p, ok := ParseChapterName(file)
	title, has, paras := CleanChapterText(text, p.N, ok)
	out := ChapterJSON{Paragraphs: paras, Words: CountWords(paras)}
	if has && title != "" {
		out.Title = &title
	} else if ok {
		t := FallbackTitle(p)
		out.Title = &t
	}
	return out
}

// DecodeText decodes chapter bytes: UTF-8 (BOM tolerated, invalid bytes replaced) or UTF-16 with a BOM.
func DecodeText(b []byte) string {
	if len(b) >= 2 && ((b[0] == 0xff && b[1] == 0xfe) || (b[0] == 0xfe && b[1] == 0xff)) {
		le := b[0] == 0xff
		b = b[2:]
		u := make([]uint16, 0, len(b)/2)
		for i := 0; i+1 < len(b); i += 2 {
			if le {
				u = append(u, uint16(b[i])|uint16(b[i+1])<<8)
			} else {
				u = append(u, uint16(b[i+1])|uint16(b[i])<<8)
			}
		}
		return string(utf16.Decode(u))
	}
	b = bytes.TrimPrefix(b, []byte("\xef\xbb\xbf"))
	return strings.ToValidUTF8(string(b), "\ufffd")
}

// NormTxt mirrors the client: NFD, strip combining marks U+0300-036F, đ->d, lower-case.
func NormTxt(s string) string {
	if s == "" {
		return ""
	}
	d := norm.NFD.String(s)
	var b strings.Builder
	b.Grow(len(d))
	for _, r := range d {
		if r >= 0x300 && r <= 0x36f {
			continue
		}
		if r == 'đ' || r == 'Đ' {
			r = 'd'
		}
		b.WriteRune(unicode.ToLower(r))
	}
	return b.String()
}

// NormKey is NormTxt with every run of non letters/digits collapsed to one space, trimmed.
func NormKey(s string) string {
	t := NormTxt(s)
	var b strings.Builder
	b.Grow(len(t))
	space := false
	for _, r := range t {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			if space && b.Len() > 0 {
				b.WriteByte(' ')
			}
			space = false
			b.WriteRune(r)
		} else {
			space = true
		}
	}
	return b.String()
}

// Compact is NormKey without spaces.
func Compact(s string) string { return strings.ReplaceAll(NormKey(s), " ", "") }

// SearchMatch reports whether every token of q occurs in field (see fixture rules).
func SearchMatch(q, field string) bool {
	k := NormKey(field)
	c := strings.ReplaceAll(k, " ", "")
	for _, tok := range strings.Fields(NormKey(q)) {
		if !strings.Contains(k, tok) && !strings.Contains(c, tok) {
			return false
		}
	}
	return true
}

// Summary is the metadata derived from info.json.
type Summary struct {
	Name     string   `json:"name"`
	Author   *string  `json:"author"`
	Synopsis string   `json:"synopsis"`
	Poster   *string  `json:"poster"`
	Genres   []string `json:"genres"`
	Tags     []string `json:"tags"`
	Status   *string  `json:"status"`
	Declared *int64   `json:"declared_chapters"`
	Link     *string  `json:"link"`
	// Updated is not part of the legacy shape; used for sort=updated.
	Updated string `json:"-"`
}

func rawText(r json.RawMessage) (string, bool) {
	r = bytes.TrimSpace(r)
	if len(r) == 0 {
		return "", false
	}
	if r[0] == '"' {
		var s string
		if json.Unmarshal(r, &s) == nil && s != "" {
			return s, true
		}
		return "", false
	}
	if r[0] == '-' || (r[0] >= '0' && r[0] <= '9') {
		if i, err := strconv.ParseInt(string(r), 10, 64); err == nil {
			return strconv.FormatInt(i, 10), true
		}
	}
	return "", false
}

func rawObj(r json.RawMessage) (map[string]json.RawMessage, bool) {
	r = bytes.TrimSpace(r)
	if len(r) == 0 || r[0] != '{' {
		return nil, false
	}
	var m map[string]json.RawMessage
	if json.Unmarshal(r, &m) != nil {
		return nil, false
	}
	return m, true
}

func rawTruthy(r json.RawMessage) bool {
	s := string(bytes.TrimSpace(r))
	switch s {
	case "", "null", "false", "0", `""`, "[]", "{}":
		return false
	}
	return true
}

func rawNames(r json.RawMessage) []string {
	out := []string{}
	var arr []json.RawMessage
	if json.Unmarshal(r, &arr) != nil {
		return out
	}
	for _, it := range arr {
		if m, ok := rawObj(it); ok {
			var s string
			if json.Unmarshal(m["name"], &s) == nil && s != "" {
				out = append(out, s)
			}
		}
	}
	return out
}

// firstValue returns the first member value of a JSON object in document order.
func firstValue(r json.RawMessage) json.RawMessage {
	dec := json.NewDecoder(bytes.NewReader(r))
	if t, err := dec.Token(); err != nil || t != json.Delim('{') {
		return nil
	}
	if !dec.More() {
		return nil
	}
	if _, err := dec.Token(); err != nil {
		return nil
	}
	var v json.RawMessage
	if dec.Decode(&v) != nil {
		return nil
	}
	return v
}

func strPtr(s string, ok bool) *string {
	if !ok {
		return nil
	}
	return &s
}

// InfoSummary derives the display metadata from raw info.json bytes (nil/invalid = defaults).
func InfoSummary(info []byte, fallback string) Summary {
	out := Summary{Name: fallback, Genres: []string{}, Tags: []string{}}
	info = bytes.TrimPrefix(bytes.TrimSpace(info), []byte("\xef\xbb\xbf"))
	m, ok := rawObj(info)
	if !ok {
		return out
	}
	if s, ok := rawText(m["name"]); ok {
		out.Name = s
	}
	if am, ok := rawObj(m["author"]); ok {
		out.Author = strPtr(rawText(am["name"]))
	} else {
		out.Author = strPtr(rawText(m["author"]))
	}
	if s, ok := rawText(m["synopsis"]); ok {
		out.Synopsis = s
	} else if s, ok := rawText(m["description"]); ok {
		out.Synopsis = s
	}
	poster := m["poster"]
	if pm, ok := rawObj(poster); ok {
		switch {
		case rawTruthy(pm["600"]):
			poster = pm["600"]
		case rawTruthy(pm["default"]):
			poster = pm["default"]
		default:
			poster = firstValue(m["poster"])
		}
	}
	if p := bytes.TrimSpace(poster); len(p) > 0 && p[0] == '"' {
		var s string
		if json.Unmarshal(p, &s) == nil {
			out.Poster = &s
		}
	}
	out.Genres = rawNames(m["genres"])
	out.Tags = rawNames(m["tags"])
	if s, ok := rawText(m["status_name"]); ok {
		out.Status = &s
	} else {
		out.Status = strPtr(rawText(m["state"]))
	}
	if s, ok := rawText(m["chapter_count"]); ok {
		if i, err := strconv.ParseInt(s, 10, 64); err == nil {
			out.Declared = &i
		}
	}
	out.Link = strPtr(rawText(m["link"]))
	for _, k := range []string{"new_chap_at", "updated_at", "published_at", "created_at"} {
		var s string
		if json.Unmarshal(m[k], &s) == nil && s != "" {
			out.Updated = s
			break
		}
	}
	return out
}

// ImgExt maps cover image extensions to MIME types.
var ImgExt = map[string]string{".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
	".webp": "image/webp", ".gif": "image/gif", ".avif": "image/avif"}

// IsImageName reports whether name has a known image extension.
func IsImageName(name string) bool {
	_, ok := ImgExt[strings.ToLower(path.Ext(name))]
	return ok
}

// PickCover chooses the cover image among file names: cover.* > poster.* > folder.* > thumb.* > first image.
func PickCover(names []string) string {
	var imgs []string
	for _, n := range names {
		if IsImageName(n) {
			imgs = append(imgs, n)
		}
	}
	sort.Strings(imgs)
	for _, stem := range []string{"cover", "poster", "folder", "thumb"} {
		for _, n := range imgs {
			if strings.ToLower(strings.TrimSuffix(n, path.Ext(n))) == stem {
				return n
			}
		}
	}
	if len(imgs) > 0 {
		return imgs[0]
	}
	return ""
}
