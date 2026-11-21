package httpapi

import (
	"bytes"
	"image"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"mythlab/internal/library"
)

func TestPingSourcesVoices(t *testing.T) {
	f := newFixture(t, nil)
	w := f.do("/api/ping")
	if got := w.Body.String(); got != `{"ok":true,"app":"mythlab","api":2,"server":"go"}` {
		t.Fatalf("ping: %s", got)
	}
	if h := w.Header(); h.Get("Content-Type") != "application/json; charset=utf-8" || h.Get("Cache-Control") != "no-store" {
		t.Fatalf("ping headers: %v", h)
	}
	if w := f.do("/api/ping", method("HEAD")); w.Code != 200 || w.Body.Len() != 0 || w.Header().Get("Content-Length") == "0" {
		t.Fatalf("HEAD ping: %d %v", w.Code, w.Header())
	}

	m := decode(t, f.do("/api/sources"))
	src := m["sources"].([]any)[0].(map[string]any)
	if src["id"] != "local0" || src["kind"] != "local" || src["available"] != true || src["detail"] != f.root {
		t.Fatalf("sources: %v", src)
	}
	if tt := m["tts"].(map[string]any); tt["edge"] != true || tt["default_voice"] != "vi-VN-HoaiMyNeural" {
		t.Fatalf("tts: %v", tt)
	}
	// other machines only learn the folder name
	m = decode(t, f.lan("/api/sources", header(KeyHeader, testKey)))
	if d := m["sources"].([]any)[0].(map[string]any)["detail"]; d != filepath.Base(f.root) {
		t.Fatalf("remote detail: %v", d)
	}

	m = decode(t, f.do("/api/voices"))
	if v := m["voices"].([]any); m["edge"] != true || len(v) != 1 || v[0].(map[string]any)["id"] != "vi-VN-HoaiMyNeural" {
		t.Fatalf("voices: %v", m)
	}

	// no engine
	fn := newFixture(t, func(o *Options) { o.TTS = nil })
	if got := fn.do("/api/voices").Body.String(); got != `{"voices":[],"edge":false}` {
		t.Fatalf("voices without engine: %s", got)
	}
	if tt := decode(t, fn.do("/api/sources"))["tts"].(map[string]any); tt["edge"] != false {
		t.Fatalf("sources without engine: %v", tt)
	}
	wantError(t, fn.do("/api/tts?text=xin+ch%C3%A0o"), 503, "tts_unavailable")
	wantError(t, f.do("/api/nope"), 404, "no_route")
	wantError(t, f.do("/api/"), 404, "no_route")
}

func names(t *testing.T, m map[string]any) string {
	t.Helper()
	var out []string
	for _, it := range m["stories"].([]any) {
		out = append(out, it.(map[string]any)["name"].(string))
	}
	return strings.Join(out, "|")
}

func TestStories(t *testing.T) {
	f := newFixture(t, nil)
	w := f.do("/api/stories?source=local0")
	wantStatus(t, w, 200)
	raw := w.Body.String()
	m := decode(t, w)
	if len(m) != 1 {
		t.Fatalf("plain listing must only have \"stories\": %s", raw)
	}
	if got := names(t, m); got != "Bê|Cổ Tích|Truyện D" {
		t.Fatalf("order: %s", got)
	}
	// field order and null handling of one item, as the old server sent it
	want := `{"key":"Truyện D","folder":"Truyện D","group":null,"chapter_files":1,"name":"Truyện D","author":null,"synopsis":"",` +
		`"poster":null,"genres":[],"tags":[],"status":null,"declared_chapters":null,"link":null,"cover":null}`
	if !strings.Contains(raw, want) {
		t.Fatalf("item shape changed:\n%s\nwant\n%s", raw, want)
	}
	if !strings.Contains(raw, `"cover":"/api/cover?source=local0&key=Truy%E1%BB%87n%20A"`) {
		t.Fatalf("cover url: %s", raw)
	}
	// a repeated parameter: the last one wins; blank = missing
	wantStatus(t, f.do("/api/stories?source=zzz&source=local0"), 200)
	wantError(t, f.do("/api/stories"), 400, "bad_param")
	wantError(t, f.do("/api/stories?source="), 400, "bad_param")
	if w := f.do("/api/stories?source=nope"); w.Code != 400 || !strings.Contains(w.Body.String(), "thiếu/không đúng tham số: 'nope'") {
		t.Fatalf("unknown source: %d %s", w.Code, w.Body.String())
	}

	// additive parameters
	m = decode(t, f.do("/api/stories?source=local0&limit=2"))
	if got := names(t, m); got != "Bê|Cổ Tích" || m["total"] != float64(3) {
		t.Fatalf("limit: %s total=%v", got, m["total"])
	}
	tags := m["tags"].([]any)
	if len(tags) != 2 || tags[0].(map[string]any)["name"] != "Hài" || tags[0].(map[string]any)["count"] != float64(2) {
		t.Fatalf("tags: %v", tags)
	}
	m = decode(t, f.do("/api/stories?source=local0&limit=2&offset=2"))
	if got := names(t, m); got != "Truyện D" || m["total"] != float64(3) {
		t.Fatalf("offset: %s", got)
	}
	// huge limit/offset must not overflow the slice bounds
	for _, q := range []string{"limit=9223372036854775807&offset=1", "limit=9223372036854775807&offset=9223372036854775807", "limit=1&offset=9223372036854775807"} {
		if w := f.do("/api/stories?source=local0&" + q); w.Code != 200 {
			t.Fatalf("%s: status %d", q, w.Code)
		}
	}
	if got := names(t, decode(t, f.do("/api/stories?source=local0&limit=9223372036854775807&offset=1"))); got != "Cổ Tích|Truyện D" {
		t.Fatalf("huge limit: %s", got)
	}
	if got := names(t, decode(t, f.do("/api/stories?source=local0&limit=5&offset=99"))); got != "" {
		t.Fatalf("offset past the end: %s", got)
	}
	if got := names(t, decode(t, f.do("/api/stories?source=local0&sort=chapters"))); got != "Bê|Cổ Tích|Truyện D" {
		t.Fatalf("sort=chapters: %s", got)
	}
	for q, wantNames := range map[string]string{
		"q=co+tich": "Cổ Tích", "q=CÔTICH": "Cổ Tích", "q=tac+gia": "Cổ Tích", "q=kho": "Bê", "q=zzz": "",
		"tag=h%C3%A0i": "Bê|Cổ Tích", "tag=tien+hiep": "Cổ Tích", "status=dang+ra": "Bê", "status=Ho%C3%A0n+th%C3%A0nh": "Cổ Tích",
		"tag=hai&status=dang+ra&q=b": "Bê", "sort=name": "Bê|Cổ Tích|Truyện D", "sort=updated": "Bê|Cổ Tích|Truyện D",
	} {
		m := decode(t, f.do("/api/stories?source=local0&"+q))
		if got := names(t, m); got != wantNames {
			t.Errorf("%s: %s, want %s", q, got, wantNames)
		}
		if _, has := m["total"]; has {
			t.Errorf("%s: total only with limit", q)
		}
	}
	m = decode(t, f.do("/api/stories?source=local0&tag=hai&limit=1"))
	if m["total"] != float64(2) || len(m["tags"].([]any)) != 2 {
		t.Fatalf("filtered total: %v", m)
	}
	// the menu data describes the whole listing, not the filtered page
	if _, ok := m["statuses"].([]any); !ok || m["all"] != float64(3) {
		t.Fatalf("statuses/all over the whole listing: %v", m)
	}
	if _, ok := decode(t, f.do("/api/stories?source=local0"))["statuses"]; ok {
		t.Fatal("statuses only with limit")
	}
	for _, bad := range []string{"limit=x", "limit=-1", "offset=-1", "offset=1.5", "sort=random"} {
		wantError(t, f.do("/api/stories?source=local0&"+bad), 400, "bad_param")
	}
}

func TestStoryAndChapter(t *testing.T) {
	f := newFixture(t, nil)
	w := f.do("/api/story?" + qs("source", "local0", "key", "Truyện A"))
	wantStatus(t, w, 200)
	raw := w.Body.String()
	if !strings.HasPrefix(raw, `{"key":"Truyện A","source":"local0","name":"Cổ Tích","author":"Tác Giả",`) ||
		!strings.Contains(raw, `"chapters":[{"n":1,"title":"Một","file":"Chương 1 - Một.txt"},{"n":2,"title":"Hai","file":"Chương 2 - Hai.txt"}]`) {
		t.Fatalf("story shape: %s", raw)
	}
	etag := w.Header().Get("ETag")
	if etag == "" || w.Header().Get("Cache-Control") != "private, no-cache" {
		t.Fatalf("story headers: %v", w.Header())
	}
	if w := f.do("/api/story?"+qs("source", "local0", "key", "Truyện A"), header("If-None-Match", etag)); w.Code != 304 || w.Body.Len() != 0 {
		t.Fatalf("304: %d", w.Code)
	}
	if got := decode(t, f.do("/api/story?"+qs("source", "local0", "key", "Truyện D")))["chapters"].([]any); len(got) != 1 {
		t.Fatalf("chapters: %v", got)
	}
	wantError(t, f.do("/api/story?source=local0"), 400, "bad_param")
	wantError(t, f.do("/api/story?"+qs("source", "local0", "key", "Không Có")), 404, "not_found")
	for _, key := range []string{"..", "../x", "Kho/../..", `Kho\Truyện B`, "C:/Windows", "/etc", f.root} {
		w := f.do("/api/story?" + qs("source", "local0", "key", key))
		if w.Code != 403 && w.Code != 404 {
			t.Errorf("key %q: status %d", key, w.Code)
		}
		if strings.Contains(w.Body.String(), filepath.Dir(f.root)) {
			t.Errorf("key %q: the answer leaks a path: %s", key, w.Body.String())
		}
	}

	ch := "/api/chapter?" + qs("source", "local0", "key", "Truyện A", "file", "Chương 1 - Một.txt")
	w = f.do(ch)
	if got := w.Body.String(); got != `{"title":"Chương 1: Một","paragraphs":["Đoạn một.","Đoạn hai có bốn chữ."],"words":7}` {
		t.Fatalf("chapter: %s", got)
	}
	etag = w.Header().Get("ETag")
	if etag == "" {
		t.Fatal("chapter needs an ETag")
	}
	wantStatus(t, f.do(ch, header("If-None-Match", etag)), 304)
	wantStatus(t, f.do(ch, header("If-None-Match", `W/`+etag+`, "other"`)), 304)
	writeFile(t, filepath.Join(f.root, "Truyện A", "Chương 1 - Một.txt"), "Chương 1: Một\n\nNội dung mới.\n")
	if w := f.do(ch, header("If-None-Match", etag)); w.Code != 200 || !strings.Contains(w.Body.String(), "Nội dung mới.") {
		t.Fatalf("edited chapter must be sent again: %d", w.Code)
	}
	// gzip for large bodies, only when asked for
	big := "/api/chapter?" + qs("source", "local0", "key", "Truyện A", "file", "Chương 2 - Hai.txt")
	plain := f.do(big)
	gz := f.do(big, header("Accept-Encoding", "gzip"))
	if gz.Header().Get("Content-Encoding") != "gzip" || gz.Body.Len() >= plain.Body.Len()/4 || plain.Header().Get("Content-Encoding") != "" {
		t.Fatalf("gzip: %d vs %d", gz.Body.Len(), plain.Body.Len())
	}
	if m := decode(t, gz); len(m["paragraphs"].([]any)) != 120 {
		t.Fatalf("gzip body: %d paragraphs", len(m["paragraphs"].([]any)))
	}
	if w := f.do(big, header("Accept-Encoding", "gzip;q=0")); w.Header().Get("Content-Encoding") != "" {
		t.Fatal("gzip;q=0 means no gzip")
	}
	if w := f.do(big, method("HEAD"), header("Accept-Encoding", "gzip")); w.Code != 200 || w.Body.Len() != 0 || w.Header().Get("ETag") == "" {
		t.Fatalf("HEAD chapter: %d", w.Code)
	}

	wantError(t, f.do("/api/chapter?source=local0&key=x"), 400, "bad_param")
	wantError(t, f.do("/api/chapter?"+qs("source", "local0", "key", "Truyện A", "file", "Chương 9.txt")), 404, "not_found")
	for _, file := range []string{"../../secret.txt", `..\..\secret.txt`, "info.json", "cover.jpg", "../Truyện D/Chương 1.txt", filepath.Join(f.root, "secret.txt")} {
		w := f.do("/api/chapter?" + qs("source", "local0", "key", "Truyện A", "file", file))
		if w.Code != 403 && w.Code != 404 {
			t.Errorf("file %q: status %d %s", file, w.Code, w.Body.String())
		}
		if strings.Contains(w.Body.String(), "secret") && !strings.Contains(file, "secret") {
			t.Errorf("file %q leaked content", file)
		}
	}
}

func TestSearch(t *testing.T) {
	f := newFixture(t, nil)
	m := decode(t, f.do("/api/search?q=co+tich"))
	items := m["items"].([]any)
	if m["q"] != "co tich" || m["total"] != float64(1) || len(items) != 1 {
		t.Fatalf("search: %v", m)
	}
	it := items[0].(map[string]any)
	if it["name"] != "Cổ Tích" || it["source"] != "local0" || it["key"] != "Truyện A" {
		t.Fatalf("item: %v", it)
	}
	if idx := m["indexed"].(map[string]any); idx["stories"] != float64(3) {
		t.Fatalf("indexed: %v", idx)
	}
	if m := decode(t, f.do("/api/search?q=")); m["total"] != float64(0) || len(m["items"].([]any)) != 0 {
		t.Fatalf("empty query: %v", m)
	}
	if got := f.do("/api/search?q=zzzz").Body.String(); !strings.Contains(got, `"items":[]`) {
		t.Fatalf("no hits must be an empty array: %s", got)
	}
	if m := decode(t, f.do("/api/search?q=truyen&limit=1&offset=1")); m["total"] != float64(3) || len(m["items"].([]any)) != 1 {
		t.Fatalf("paging: %v", m)
	}
	wantStatus(t, f.do("/api/search?q=a&source=local0&limit=1000"), 200)
	wantError(t, f.do("/api/search?q=a&source=nope"), 400, "bad_param")
	wantError(t, f.do("/api/search?q=a&limit=0"), 400, "bad_param")
	wantError(t, f.do("/api/search?q=a&offset=x"), 400, "bad_param")

	fn := newFixture(t, func(o *Options) { o.Search = nil })
	if got := fn.do("/api/search?q=a").Body.String(); !strings.HasPrefix(got, `{"q":"a","total":0,"items":[]`) {
		t.Fatalf("no index: %s", got)
	}
}

func TestCover(t *testing.T) {
	f := newFixture(t, nil)
	u := "/api/cover?" + qs("source", "local0", "key", "Truyện A")
	w := f.do(u)
	h := w.Header()
	orig, _ := os.ReadFile(filepath.Join(f.root, "Truyện A", "cover.jpg"))
	if w.Code != 200 || !bytes.Equal(w.Body.Bytes(), orig) || h.Get("Content-Type") != "image/jpeg" ||
		h.Get("Cache-Control") != "public, max-age=2592000" || h.Get("X-Content-Type-Options") != "nosniff" || h.Get("ETag") == "" {
		t.Fatalf("cover: %d %v", w.Code, h)
	}
	wantStatus(t, f.do(u, header("If-None-Match", h.Get("ETag"))), 304)
	if w := f.do(u, header("Range", "bytes=0-1")); w.Code != 206 || w.Body.Len() != 2 {
		t.Fatalf("range: %d", w.Code)
	}
	if w := f.do(u, method("HEAD")); w.Code != 200 || w.Body.Len() != 0 {
		t.Fatalf("HEAD: %d", w.Code)
	}
	// with a key the image is not for shared caches
	if w := f.lan(u+"&k="+testKey, header("Accept", "image/*")); w.Code != 200 || w.Header().Get("Cache-Control") != "private, max-age=2592000" {
		t.Fatalf("LAN cover: %d %v", w.Code, w.Header())
	}
	for _, width := range []int{160, 240, 320, 480} {
		w := f.do(u + "&w=" + itoa(width))
		cfg, format, err := image.DecodeConfig(bytes.NewReader(w.Body.Bytes()))
		if w.Code != 200 || err != nil || format != "jpeg" || cfg.Width != width || w.Header().Get("Content-Type") != "image/jpeg" ||
			w.Header().Get("ETag") == h.Get("ETag") || w.Header().Get("ETag") == "" {
			t.Fatalf("w=%d: %d %v %s %d", width, w.Code, err, format, cfg.Width)
		}
		wantStatus(t, f.do(u+"&w="+itoa(width), header("If-None-Match", w.Header().Get("ETag"))), 304)
	}
	for _, bad := range []string{"0", "100", "481", "-160", "abc", "160px"} {
		wantError(t, f.do(u+"&w="+bad), 400, "bad_param")
	}
	// a small original is served as it is
	writeFile(t, filepath.Join(f.root, "Truyện D", "cover.jpg"), testJPEG(100, 150))
	wd := f.do("/api/cover?" + qs("source", "local0", "key", "Truyện D", "w", "320"))
	if cfg, _, err := image.DecodeConfig(bytes.NewReader(wd.Body.Bytes())); wd.Code != 200 || err != nil || cfg.Width != 100 {
		t.Fatalf("small cover: %d %v", wd.Code, err)
	}
	w = f.do("/api/cover?" + qs("source", "local0", "key", "Kho/Truyện B"))
	if w.Code != 404 || !strings.Contains(w.Body.String(), "truyện chưa có ảnh bìa") {
		t.Fatalf("no cover: %d %s", w.Code, w.Body.String())
	}
	wantError(t, f.do("/api/cover?source=local0"), 400, "bad_param")
	if w := f.do("/api/cover?" + qs("source", "local0", "key", "../..")); w.Code != 403 && w.Code != 404 {
		t.Fatalf("traversal: %d", w.Code)
	}
}

func itoa(n int) string {
	b := []byte{}
	for ; n > 0; n /= 10 {
		b = append([]byte{byte('0' + n%10)}, b...)
	}
	return string(b)
}

func TestTTS(t *testing.T) {
	f := newFixture(t, nil)
	u := "/api/tts?" + qs("text", "Xin chào.", "voice", "vi-VN-HoaiMyNeural", "rate", "10", "pitch", "-5")
	w := f.do(u)
	h := w.Header()
	if w.Code != 200 || h.Get("Content-Type") != "audio/mpeg" || h.Get("Cache-Control") != "public, max-age=31536000, immutable" ||
		!strings.HasPrefix(w.Body.String(), "ID3-fake-mp3:vi-VN-HoaiMyNeural:Xin chào.") || h.Get("Accept-Ranges") != "bytes" {
		t.Fatalf("tts: %d %v", w.Code, h)
	}
	if w := f.do(u, header("Range", "bytes=0-2")); w.Code != 206 || w.Body.String() != "ID3" {
		t.Fatalf("range: %d %q", w.Code, w.Body.String())
	}
	if w := f.do(u, method("HEAD")); w.Code != 200 || w.Body.Len() != 0 || w.Header().Get("Content-Length") == "" {
		t.Fatalf("HEAD: %d", w.Code)
	}
	wantStatus(t, f.do(u, header("If-None-Match", h.Get("ETag"))), 304)
	if f.eng.calls != 1 {
		t.Fatalf("the cache must be used: %d engine calls", f.eng.calls)
	}
	if w := f.lan(u + "&k=" + testKey); w.Code != 200 || w.Header().Get("Cache-Control") != "private, max-age=31536000, immutable" {
		t.Fatalf("LAN tts: %d %v", w.Code, w.Header())
	}
	wantError(t, f.do("/api/tts"), 400, "empty_text")
	wantError(t, f.do("/api/tts?text=+++"), 400, "empty_text")
	wantError(t, f.do("/api/tts?"+qs("text", strings.Repeat("ă", 3001))), 413, "text_too_long")
	wantError(t, f.do("/api/tts?text=a&rate=fast"), 400, "bad_param")
	wantError(t, f.do("/api/tts?text=a&pitch=1.5"), 400, "bad_param")
	wantError(t, f.do("/api/tts?text=a&voice=..%2F..%2Fx"), 400, "bad_voice")
	// successful audio requests stay out of the log, failures do not
	n := len(*f.logs)
	f.do(u)
	if len(*f.logs) != n {
		t.Fatal("200 on /api/tts must not be logged")
	}
	f.do("/api/tts")
	if len(*f.logs) != n+1 {
		t.Fatal("a failed tts request must be logged")
	}
}

type panicProvider struct{ library.Provider }

func (panicProvider) ID() string { return "boom" }

func TestPanicRecovery(t *testing.T) {
	f := newFixture(t, func(o *Options) { o.Library = library.NewLibrary(panicProvider{}) })
	w := f.do("/api/stories?source=boom")
	wantError(t, w, 500, "internal")
	if strings.Contains(w.Body.String(), "nil pointer") || strings.Contains(w.Body.String(), "goroutine") {
		t.Fatalf("panic details leaked: %s", w.Body.String())
	}
	wantStatus(t, f.do("/api/ping"), 200) // still alive
}

func TestLastQuery(t *testing.T) {
	q := lastQuery("a=1&a=2&b=&c=%E1%BB%87+x&d=%zz&=x&e")
	if q["a"] != "2" || q["c"] != "ệ x" || q["d"] != "%zz" {
		t.Fatalf("lastQuery: %v", q)
	}
	if _, ok := q["b"]; ok {
		t.Fatal("blank values are missing values")
	}
	if _, ok := q["e"]; ok {
		t.Fatal("valueless keys are missing values")
	}
}
