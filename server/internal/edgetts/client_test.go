package edgetts

import (
	"bytes"
	"context"
	"encoding/binary"
	"errors"
	"net/http"
	"net/http/httptest"
	"regexp"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/coder/websocket"
)

const testVoice = "vi-VN-HoaiMyNeural"

var fixedNow = time.Date(2026, 11, 20, 8, 30, 0, 0, time.UTC)

// audioFrame builds a binary frame the way the service does.
func audioFrame(payload []byte, withType bool) []byte {
	head := "X-RequestId:abc\r\n"
	if withType {
		head += "Content-Type:audio/mpeg\r\n"
	}
	head += "Path:audio\r\n"
	frame := binary.BigEndian.AppendUint16(nil, uint16(len(head)))
	frame = append(frame, head...)
	return append(frame, payload...)
}

func textFrame(path string) []byte {
	return []byte("X-RequestId:abc\r\nContent-Type:application/json; charset=utf-8\r\nPath:" + path + "\r\n\r\n{}")
}

// fakeService is an in-process stand-in for the speech endpoint.
type fakeService struct {
	t   *testing.T
	srv *httptest.Server

	mu       sync.Mutex
	requests []*http.Request // handshake requests, in order
	frames   [][2]string     // config + ssml frame of every accepted session

	// reject, when set, may answer the handshake itself and return true.
	reject func(n int, w http.ResponseWriter, r *http.Request) bool
	// respond drives an accepted session after both client frames arrived.
	respond func(ctx context.Context, n int, conn *websocket.Conn, ssml string)
}

func newFakeService(t *testing.T) *fakeService {
	f := &fakeService{t: t}
	f.srv = httptest.NewServer(http.HandlerFunc(f.handle))
	t.Cleanup(f.srv.Close)
	return f
}

func (f *fakeService) client(opts Options) *Client {
	opts.WSSURL = "ws" + strings.TrimPrefix(f.srv.URL, "http") + "/edge/v1?TrustedClientToken=test"
	opts.VoicesURL = f.srv.URL + "/voices/list?trustedclienttoken=test"
	if opts.Now == nil {
		opts.Now = func() time.Time { return fixedNow }
	}
	return New(opts)
}

func (f *fakeService) handle(w http.ResponseWriter, r *http.Request) {
	f.mu.Lock()
	f.requests = append(f.requests, r.Clone(context.Background()))
	n := len(f.requests)
	f.mu.Unlock()

	if f.reject != nil && f.reject(n, w, r) {
		return
	}
	conn, err := websocket.Accept(w, r, &websocket.AcceptOptions{InsecureSkipVerify: true})
	if err != nil {
		f.t.Errorf("accept: %v", err)
		return
	}
	defer conn.CloseNow()
	ctx := r.Context()
	var got [2]string
	for i := range got {
		typ, data, err := conn.Read(ctx)
		if err != nil || typ != websocket.MessageText {
			return
		}
		got[i] = string(data)
	}
	f.mu.Lock()
	f.frames = append(f.frames, got)
	f.mu.Unlock()
	if f.respond != nil {
		f.respond(ctx, n, conn, got[1])
	}
}

func (f *fakeService) snapshot() ([]*http.Request, [][2]string) {
	f.mu.Lock()
	defer f.mu.Unlock()
	return append([]*http.Request(nil), f.requests...), append([][2]string(nil), f.frames...)
}

// waitClosed blocks until the client goes away.
func waitClosed(ctx context.Context, conn *websocket.Conn) { conn.Read(ctx) }

func sendTurn(ctx context.Context, conn *websocket.Conn, parts ...[]byte) {
	conn.Write(ctx, websocket.MessageText, textFrame("turn.start"))
	conn.Write(ctx, websocket.MessageText, textFrame("response"))
	for _, p := range parts {
		conn.Write(ctx, websocket.MessageBinary, audioFrame(p, true))
		conn.Write(ctx, websocket.MessageText, textFrame("audio.metadata"))
	}
	conn.Write(ctx, websocket.MessageBinary, audioFrame(nil, false))
	conn.Write(ctx, websocket.MessageText, textFrame("turn.end"))
	waitClosed(ctx, conn)
}

func TestSynthesizeSession(t *testing.T) {
	f := newFakeService(t)
	f.respond = func(ctx context.Context, _ int, conn *websocket.Conn, _ string) {
		sendTurn(ctx, conn, []byte("\xff\xf3AAAA"), []byte("BBBB"))
	}
	c := f.client(Options{})

	audio, err := c.Synthesize(context.Background(), "Tấm & Cám <b>\x0b ]]>", testVoice, 25, -7)
	if err != nil {
		t.Fatal(err)
	}
	if string(audio) != "\xff\xf3AAAABBBB" {
		t.Fatalf("audio = %q", audio)
	}

	reqs, frames := f.snapshot()
	if len(reqs) != 1 || len(frames) != 1 {
		t.Fatalf("requests=%d sessions=%d", len(reqs), len(frames))
	}
	r := reqs[0]
	q := r.URL.Query()
	if q.Get("TrustedClientToken") != "test" {
		t.Errorf("endpoint query lost: %v", q)
	}
	if got, want := q.Get("Sec-MS-GEC"), secMSGEC(fixedNow.Unix()); got != want {
		t.Errorf("Sec-MS-GEC = %s, want %s", got, want)
	}
	if got := q.Get("Sec-MS-GEC-Version"); got != "2-"+chromiumFullVersion {
		t.Errorf("Sec-MS-GEC-Version = %q", got)
	}
	if id := q.Get("ConnectionId"); !regexp.MustCompile(`^[0-9a-f]{32}$`).MatchString(id) {
		t.Errorf("ConnectionId = %q", id)
	}
	for name, want := range map[string]string{
		"Origin":          extensionOrigin,
		"User-Agent":      userAgent,
		"Pragma":          "no-cache",
		"Cache-Control":   "no-cache",
		"Accept-Language": acceptLanguage,
		"Accept-Encoding": acceptEncoding,
	} {
		if got := r.Header.Get(name); got != want {
			t.Errorf("header %s = %q, want %q", name, got, want)
		}
	}
	if ck := r.Header.Get("Cookie"); !regexp.MustCompile(`^muid=[0-9A-F]{32};$`).MatchString(ck) {
		t.Errorf("Cookie = %q", ck)
	}

	config, ssml := frames[0][0], frames[0][1]
	wantConfig := "X-Timestamp:Fri Nov 20 2026 08:30:00 GMT+0000 (Coordinated Universal Time)\r\n" +
		"Content-Type:application/json; charset=utf-8\r\n" +
		"Path:speech.config\r\n\r\n" +
		`{"context":{"synthesis":{"audio":{"metadataoptions":{"sentenceBoundaryEnabled":"true","wordBoundaryEnabled":"false"},"outputFormat":"audio-24khz-48kbitrate-mono-mp3"}}}}` + "\r\n"
	if config != wantConfig {
		t.Errorf("config frame:\n got %q\nwant %q", config, wantConfig)
	}
	head, body, ok := strings.Cut(ssml, "\r\n\r\n")
	if !ok {
		t.Fatalf("ssml frame without header separator: %q", ssml)
	}
	if !regexp.MustCompile(`^X-RequestId:[0-9a-f]{32}\r\nContent-Type:application/ssml\+xml\r\n` +
		`X-Timestamp:Fri Nov 20 2026 08:30:00 GMT\+0000 \(Coordinated Universal Time\)Z\r\nPath:ssml$`).MatchString(head) {
		t.Errorf("ssml headers: %q", head)
	}
	wantBody := "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>" +
		"<voice name='Microsoft Server Speech Text to Speech Voice (vi-VN, HoaiMyNeural)'>" +
		"<prosody pitch='-7Hz' rate='+25%' volume='+0%'>Tấm &amp; Cám &lt;b&gt;  ]]&gt;</prosody></voice></speak>"
	if body != wantBody {
		t.Errorf("ssml body:\n got %s\nwant %s", body, wantBody)
	}
}

func TestSynthesizeSplitsLongText(t *testing.T) {
	f := newFakeService(t)
	f.respond = func(ctx context.Context, n int, conn *websocket.Conn, _ string) {
		sendTurn(ctx, conn, bytes.Repeat([]byte{byte('0' + n)}, 3))
	}
	c := f.client(Options{})

	text := strings.Repeat("Một câu văn tiếng Việt có dấu & ký tự đặc biệt <x>. ", 150) // > 2 chunks once escaped
	audio, err := c.Synthesize(context.Background(), text, testVoice, 0, 0)
	if err != nil {
		t.Fatal(err)
	}
	_, frames := f.snapshot()
	if len(frames) < 3 {
		t.Fatalf("expected at least 3 sessions, got %d", len(frames))
	}
	var want, spoken strings.Builder
	for i, fr := range frames {
		want.WriteString(strings.Repeat(string(rune('1'+i)), 3))
		_, body, _ := strings.Cut(fr[1], "\r\n\r\n")
		inner := body[strings.Index(body, "volume='+0%'>")+len("volume='+0%'>") : strings.Index(body, "</prosody>")]
		if len(inner) > maxSSMLTextBytes {
			t.Errorf("session %d carries %d bytes of text", i, len(inner))
		}
		spoken.WriteString(inner + " ")
	}
	if string(audio) != want.String() {
		t.Fatalf("audio = %q, want %q", audio, want.String())
	}
	if strings.TrimSpace(spoken.String()) != strings.TrimSpace(escapeXML(text)) {
		t.Fatal("the sessions together do not carry the whole text")
	}
}

func TestSynthesizeRetriesOn403WithServerClock(t *testing.T) {
	serverNow := fixedNow.Add(97 * time.Minute)
	f := newFakeService(t)
	f.reject = func(_ int, w http.ResponseWriter, r *http.Request) bool {
		if r.URL.Query().Get("Sec-MS-GEC") == secMSGEC(serverNow.Unix()) {
			return false
		}
		w.Header().Set("Date", serverNow.Format(http.TimeFormat))
		w.WriteHeader(http.StatusForbidden)
		return true
	}
	f.respond = func(ctx context.Context, _ int, conn *websocket.Conn, _ string) {
		sendTurn(ctx, conn, []byte("OK"))
	}
	c := f.client(Options{})

	audio, err := c.Synthesize(context.Background(), "xin chào", testVoice, 0, 0)
	if err != nil || string(audio) != "OK" {
		t.Fatalf("audio=%q err=%v", audio, err)
	}
	if reqs, _ := f.snapshot(); len(reqs) != 2 {
		t.Fatalf("expected 403 + retry, got %d requests", len(reqs))
	}
	// The corrected clock is kept: the next call succeeds at once.
	if _, err := c.Synthesize(context.Background(), "lần hai", testVoice, 0, 0); err != nil {
		t.Fatal(err)
	}
	if reqs, _ := f.snapshot(); len(reqs) != 3 {
		t.Fatalf("skew was not remembered: %d requests", len(reqs))
	}
}

func TestSynthesize403Persistent(t *testing.T) {
	f := newFakeService(t)
	f.reject = func(_ int, w http.ResponseWriter, _ *http.Request) bool {
		w.Header().Set("Date", fixedNow.Format(http.TimeFormat))
		w.WriteHeader(http.StatusForbidden)
		return true
	}
	c := f.client(Options{})
	_, err := c.Synthesize(context.Background(), "xin chào", testVoice, 0, 0)
	var se *StatusError
	if !errors.As(err, &se) || se.StatusCode != http.StatusForbidden {
		t.Fatalf("err = %v, want StatusError 403", err)
	}
	if reqs, _ := f.snapshot(); len(reqs) != 2 {
		t.Fatalf("expected exactly one retry, got %d requests", len(reqs))
	}
	if strings.Contains(err.Error(), "Sec-MS-GEC") || strings.Contains(err.Error(), "127.0.0.1") {
		t.Fatalf("error leaks the request URL: %v", err)
	}
}

func TestSynthesize403WithoutDateIsNotRetried(t *testing.T) {
	f := newFakeService(t)
	f.reject = func(_ int, w http.ResponseWriter, _ *http.Request) bool {
		w.Header()["Date"] = nil // suppress net/http's automatic Date header
		w.WriteHeader(http.StatusForbidden)
		return true
	}
	c := f.client(Options{})
	if _, err := c.Synthesize(context.Background(), "xin chào", testVoice, 0, 0); err == nil {
		t.Fatal("expected an error")
	}
	if reqs, _ := f.snapshot(); len(reqs) != 1 {
		t.Fatalf("expected no retry, got %d requests", len(reqs))
	}
}

func TestSynthesizeOtherStatus(t *testing.T) {
	f := newFakeService(t)
	f.reject = func(_ int, w http.ResponseWriter, _ *http.Request) bool {
		w.WriteHeader(http.StatusServiceUnavailable)
		return true
	}
	c := f.client(Options{})
	_, err := c.Synthesize(context.Background(), "xin chào", testVoice, 0, 0)
	var se *StatusError
	if !errors.As(err, &se) || se.StatusCode != http.StatusServiceUnavailable {
		t.Fatalf("err = %v", err)
	}
	if reqs, _ := f.snapshot(); len(reqs) != 1 {
		t.Fatalf("a 503 must not be retried here, got %d requests", len(reqs))
	}
}

func TestSynthesizeNoAudio(t *testing.T) {
	f := newFakeService(t)
	f.respond = func(ctx context.Context, _ int, conn *websocket.Conn, _ string) { sendTurn(ctx, conn) }
	c := f.client(Options{})
	if _, err := c.Synthesize(context.Background(), "xin chào", testVoice, 0, 0); !errors.Is(err, ErrNoAudio) {
		t.Fatalf("err = %v, want ErrNoAudio", err)
	}
}

func TestSynthesizeConnectionLostMidTurn(t *testing.T) {
	f := newFakeService(t)
	f.respond = func(ctx context.Context, _ int, conn *websocket.Conn, _ string) {
		conn.Write(ctx, websocket.MessageBinary, audioFrame([]byte("partial"), true))
		conn.Close(websocket.StatusNormalClosure, "")
	}
	c := f.client(Options{})
	audio, err := c.Synthesize(context.Background(), "xin chào", testVoice, 0, 0)
	if err == nil || audio != nil {
		t.Fatalf("a truncated turn must fail, got %d bytes, err=%v", len(audio), err)
	}
}

func TestSynthesizeProtocolErrors(t *testing.T) {
	cases := map[string]func(ctx context.Context, conn *websocket.Conn){
		"unknown text path": func(ctx context.Context, conn *websocket.Conn) {
			conn.Write(ctx, websocket.MessageText, textFrame("something.else"))
		},
		"short binary": func(ctx context.Context, conn *websocket.Conn) {
			conn.Write(ctx, websocket.MessageBinary, []byte{0})
		},
		"header length too large": func(ctx context.Context, conn *websocket.Conn) {
			conn.Write(ctx, websocket.MessageBinary, []byte{0xff, 0xff, 'P'})
		},
		"binary with other path": func(ctx context.Context, conn *websocket.Conn) {
			head := "Path:video\r\n"
			conn.Write(ctx, websocket.MessageBinary, append(binary.BigEndian.AppendUint16(nil, uint16(len(head))), head...))
		},
		"data without content type": func(ctx context.Context, conn *websocket.Conn) {
			conn.Write(ctx, websocket.MessageBinary, audioFrame([]byte("x"), false))
		},
		"audio frame without data": func(ctx context.Context, conn *websocket.Conn) {
			conn.Write(ctx, websocket.MessageBinary, audioFrame(nil, true))
		},
	}
	for name, send := range cases {
		t.Run(name, func(t *testing.T) {
			f := newFakeService(t)
			f.respond = func(ctx context.Context, _ int, conn *websocket.Conn, _ string) {
				send(ctx, conn)
				waitClosed(ctx, conn)
			}
			c := f.client(Options{})
			if _, err := c.Synthesize(context.Background(), "xin chào", testVoice, 0, 0); !errors.Is(err, ErrProtocol) {
				t.Fatalf("err = %v, want ErrProtocol", err)
			}
		})
	}
}

func TestSynthesizeReceiveTimeout(t *testing.T) {
	f := newFakeService(t)
	f.respond = func(ctx context.Context, _ int, conn *websocket.Conn, _ string) {
		conn.Write(ctx, websocket.MessageBinary, audioFrame([]byte("x"), true))
		waitClosed(ctx, conn) // never sends turn.end
	}
	c := f.client(Options{ReceiveTimeout: 150 * time.Millisecond})
	start := time.Now()
	_, err := c.Synthesize(context.Background(), "xin chào", testVoice, 0, 0)
	if !errors.Is(err, ErrReceiveTimeout) {
		t.Fatalf("err = %v, want ErrReceiveTimeout", err)
	}
	if d := time.Since(start); d > 5*time.Second {
		t.Fatalf("timeout took %s", d)
	}
}

func TestSynthesizeConnectTimeout(t *testing.T) {
	release := make(chan struct{})
	f := newFakeService(t)
	f.reject = func(_ int, _ http.ResponseWriter, r *http.Request) bool {
		select { // never answer the handshake
		case <-release:
		case <-r.Context().Done():
		}
		return true
	}
	t.Cleanup(func() { close(release) })
	c := f.client(Options{ConnectTimeout: 150 * time.Millisecond})
	start := time.Now()
	_, err := c.Synthesize(context.Background(), "xin chào", testVoice, 0, 0)
	if !errors.Is(err, ErrConnectTimeout) {
		t.Fatalf("err = %v, want ErrConnectTimeout", err)
	}
	if d := time.Since(start); d > 5*time.Second {
		t.Fatalf("timeout took %s", d)
	}
}

func TestSynthesizeContextCancel(t *testing.T) {
	started := make(chan struct{}, 1)
	f := newFakeService(t)
	f.respond = func(ctx context.Context, _ int, conn *websocket.Conn, _ string) {
		conn.Write(ctx, websocket.MessageBinary, audioFrame([]byte("x"), true))
		started <- struct{}{}
		waitClosed(ctx, conn)
	}
	c := f.client(Options{})
	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		<-started
		cancel()
	}()
	start := time.Now()
	_, err := c.Synthesize(ctx, "xin chào", testVoice, 0, 0)
	if !errors.Is(err, context.Canceled) {
		t.Fatalf("err = %v, want context.Canceled", err)
	}
	if d := time.Since(start); d > 5*time.Second {
		t.Fatalf("cancellation took %s", d)
	}

	// An already cancelled context never reaches the network.
	before, _ := f.snapshot()
	if _, err := c.Synthesize(ctx, "xin chào", testVoice, 0, 0); !errors.Is(err, context.Canceled) {
		t.Fatalf("err = %v", err)
	}
	if after, _ := f.snapshot(); len(after) != len(before) {
		t.Fatal("a cancelled context still dialled the service")
	}
}

func TestSynthesizeRejectsBadInput(t *testing.T) {
	f := newFakeService(t)
	c := f.client(Options{})
	if _, err := c.Synthesize(context.Background(), "xin chào", "vi-VN-Hoai'My", 0, 0); !errors.Is(err, ErrInvalidVoice) {
		t.Fatalf("err = %v, want ErrInvalidVoice", err)
	}
	for _, text := range []string{"", "  \n\t ", "\x0b\x0c"} {
		if _, err := c.Synthesize(context.Background(), text, testVoice, 0, 0); !errors.Is(err, ErrEmptyText) {
			t.Fatalf("text %q: err = %v, want ErrEmptyText", text, err)
		}
	}
	if reqs, _ := f.snapshot(); len(reqs) != 0 {
		t.Fatalf("bad input reached the service (%d requests)", len(reqs))
	}
}

const voicesJSON = `[
 {"Name":"Microsoft Server Speech Text to Speech Voice (en-US, EmmaMultilingualNeural)","ShortName":"en-US-EmmaMultilingualNeural","Gender":"Female","Locale":"en-US","FriendlyName":"Microsoft EmmaMultilingual Online (Natural) - English (United States)","Status":"GA","VoiceTag":{"ContentCategories":["General"]}},
 {"ShortName":"vi-VN-NamMinhNeural","Gender":"Male","Locale":"vi-VN","FriendlyName":"Microsoft NamMinh Online (Natural) - Vietnamese (Vietnam)"},
 {"ShortName":"fr-FR-DeniseNeural","Gender":"Female","Locale":"fr-FR"},
 {"ShortName":"vi-VN-HoaiMyNeural","Gender":"Female","Locale":"vi-VN","FriendlyName":"Microsoft HoaiMy Online (Natural) - Vietnamese (Vietnam)"},
 {"Gender":"Female","Locale":"xx-XX"}
]`

type voicesServer struct {
	srv   *httptest.Server
	hits  atomic.Int32
	fail  atomic.Bool
	skew  atomic.Int64 // seconds; when non-zero the token must match fixedNow+skew
	last  atomic.Pointer[http.Request]
	block chan struct{}
}

func newVoicesServer(t *testing.T) *voicesServer {
	v := &voicesServer{}
	v.srv = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		v.hits.Add(1)
		v.last.Store(r.Clone(context.Background()))
		if v.block != nil {
			select {
			case <-v.block:
			case <-r.Context().Done():
				return
			}
		}
		if v.fail.Load() {
			http.Error(w, "boom", http.StatusInternalServerError)
			return
		}
		serverNow := fixedNow.Add(time.Duration(v.skew.Load()) * time.Second)
		if r.URL.Query().Get("Sec-MS-GEC") != secMSGEC(serverNow.Unix()) {
			w.Header().Set("Date", serverNow.Format(http.TimeFormat))
			w.WriteHeader(http.StatusForbidden)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(voicesJSON))
	}))
	t.Cleanup(v.srv.Close)
	return v
}

func (v *voicesServer) client(now *time.Time) *Client {
	return New(Options{
		VoicesURL: v.srv.URL + "/voices/list?trustedclienttoken=test",
		WSSURL:    "ws://127.0.0.1:1/unused?x=1",
		VoicesTTL: time.Hour,
		Now:       func() time.Time { return *now },
	})
}

func TestVoicesFetchParseAndCache(t *testing.T) {
	v := newVoicesServer(t)
	now := fixedNow
	c := v.client(&now)

	vs, err := c.Voices(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	if len(vs) != 4 {
		t.Fatalf("got %d voices: %+v", len(vs), vs)
	}
	want := Voice{ShortName: "vi-VN-HoaiMyNeural", Locale: "vi-VN", Gender: "Female",
		FriendlyName: "Microsoft HoaiMy Online (Natural) - Vietnamese (Vietnam)"}
	if vs[3] != want {
		t.Fatalf("voice = %+v, want %+v", vs[3], want)
	}
	if vs[2].FriendlyName != "fr-FR-DeniseNeural" {
		t.Fatalf("missing FriendlyName must fall back to ShortName: %+v", vs[2])
	}

	r := v.last.Load()
	if r.URL.Query().Get("Sec-MS-GEC-Version") != secMSGECVersion || r.URL.Query().Get("trustedclienttoken") != "test" {
		t.Errorf("query = %v", r.URL.Query())
	}
	if r.Header.Get("User-Agent") != userAgent || r.Header.Get("Sec-CH-UA") != secCHUA ||
		!strings.HasPrefix(r.Header.Get("Cookie"), "muid=") || r.Header.Get("Accept-Encoding") != "gzip" {
		t.Errorf("headers = %v", r.Header)
	}

	// Cached: no second request, and the caller cannot corrupt the cache.
	vs[0].ShortName = "mutated"
	vs2, err := c.Voices(context.Background())
	if err != nil || v.hits.Load() != 1 || vs2[0].ShortName != "en-US-EmmaMultilingualNeural" {
		t.Fatalf("cache: hits=%d first=%q err=%v", v.hits.Load(), vs2[0].ShortName, err)
	}

	// Expired: refetched.
	now = now.Add(61 * time.Minute)
	v.skew.Store(61 * 60)
	if _, err := c.Voices(context.Background()); err != nil || v.hits.Load() != 2 {
		t.Fatalf("after TTL: hits=%d err=%v", v.hits.Load(), err)
	}

	// Expired and the service is down: the stale list is served.
	now = now.Add(2 * time.Hour)
	v.fail.Store(true)
	stale, err := c.Voices(context.Background())
	if err != nil || len(stale) != 4 {
		t.Fatalf("stale: %d voices, err=%v", len(stale), err)
	}
}

func TestVoicesErrorWithoutCache(t *testing.T) {
	v := newVoicesServer(t)
	v.fail.Store(true)
	now := fixedNow
	c := v.client(&now)
	_, err := c.Voices(context.Background())
	var se *StatusError
	if !errors.As(err, &se) || se.StatusCode != 500 || se.Op != "voices" {
		t.Fatalf("err = %v", err)
	}
}

func TestVoicesRetriesOn403(t *testing.T) {
	v := newVoicesServer(t)
	v.skew.Store(-3 * 3600)
	now := fixedNow
	c := v.client(&now)
	vs, err := c.Voices(context.Background())
	if err != nil || len(vs) != 4 {
		t.Fatalf("voices=%d err=%v", len(vs), err)
	}
	if v.hits.Load() != 2 {
		t.Fatalf("hits = %d, want 2 (403 + retry)", v.hits.Load())
	}
}

func TestVoicesConcurrentCallsShareOneFetch(t *testing.T) {
	v := newVoicesServer(t)
	v.block = make(chan struct{})
	now := fixedNow
	c := v.client(&now)

	var wg sync.WaitGroup
	errs := make(chan error, 8)
	for i := 0; i < 8; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_, err := c.Voices(context.Background())
			errs <- err
		}()
	}
	time.Sleep(100 * time.Millisecond)
	close(v.block)
	wg.Wait()
	close(errs)
	for err := range errs {
		if err != nil {
			t.Fatal(err)
		}
	}
	if v.hits.Load() != 1 {
		t.Fatalf("hits = %d, want 1", v.hits.Load())
	}
}

func TestVoicesContextCancel(t *testing.T) {
	v := newVoicesServer(t)
	v.block = make(chan struct{})
	t.Cleanup(func() { close(v.block) })
	now := fixedNow
	c := v.client(&now)
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()
	if _, err := c.Voices(ctx); !errors.Is(err, context.DeadlineExceeded) {
		t.Fatalf("err = %v, want deadline exceeded", err)
	}
}

func TestReaderVoices(t *testing.T) {
	all := []Voice{
		{ShortName: "en-US-EmmaMultilingualNeural", Locale: "en-US"},
		{ShortName: "vi-VN-NamMinhNeural", Locale: "vi-VN"},
		{ShortName: "fr-FR-DeniseNeural", Locale: "fr-FR"},
		{ShortName: "vi-VN-HoaiMyNeural", Locale: "vi-VN"},
		{ShortName: "de-DE-SeraphinaMultilingualNeural", Locale: "de-DE"},
	}
	got := ReaderVoices(all)
	want := []string{"vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural", "en-US-EmmaMultilingualNeural", "de-DE-SeraphinaMultilingualNeural"}
	if len(got) != len(want) {
		t.Fatalf("got %+v", got)
	}
	for i := range want {
		if got[i].ShortName != want[i] {
			t.Fatalf("position %d = %s, want %s", i, got[i].ShortName, want[i])
		}
	}
	if len(ReaderVoices(nil)) != 0 {
		t.Fatal("nil input must give an empty list")
	}
}

func TestScrubURL(t *testing.T) {
	err := errors.New(`failed: Get "https://host/path?Sec-MS-GEC=SECRET&x=1": dial tcp: refused`)
	got := scrubURL(err)
	if strings.Contains(got.Error(), "SECRET") || !strings.Contains(got.Error(), "refused") {
		t.Fatalf("got %q", got)
	}
	if !errors.Is(got, err) {
		t.Fatal("the original error must stay reachable")
	}
	plain := errors.New("no url here")
	if scrubURL(plain) != plain {
		t.Fatal("errors without a URL must pass through unchanged")
	}
}

func TestJSDate(t *testing.T) {
	loc := time.FixedZone("ICT", 7*3600)
	got := jsDate(time.Date(2026, 1, 5, 6, 7, 8, 0, loc))
	if got != "Sun Jan 04 2026 23:07:08 GMT+0000 (Coordinated Universal Time)" {
		t.Fatalf("got %q", got)
	}
}
