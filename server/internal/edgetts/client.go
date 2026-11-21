// Package edgetts is a client for the Microsoft Edge "Read Aloud" online
// text-to-speech service: the websocket synthesis protocol, the Sec-MS-GEC v2
// request token and the voice list. It is a port of the Python edge-tts
// package (7.3.1) restricted to what the reader needs: MP3 output
// (audio-24khz-48kbitrate-mono-mp3) for a text, a voice, a rate and a pitch.
//
// Values that Microsoft rotates live in constants.go.
package edgetts

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/binary"
	"encoding/hex"
	"errors"
	"fmt"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/coder/websocket"
)

// Errors returned by the client. Use errors.Is / errors.As.
var (
	// ErrInvalidVoice reports a voice name that is not of the form
	// "vi-VN-HoaiMyNeural" (a caller error, not a service failure).
	ErrInvalidVoice = errors.New("edgetts: invalid voice name")
	// ErrEmptyText reports a text with nothing to speak (a caller error).
	ErrEmptyText = errors.New("edgetts: empty text")
	// ErrNoAudio reports a turn that ended without audio; the service does
	// this for unknown voices and for text it cannot speak.
	ErrNoAudio = errors.New("edgetts: no audio received")
	// ErrProtocol reports a response the client does not understand.
	ErrProtocol = errors.New("edgetts: unexpected response")
	// ErrReceiveTimeout reports that the service stayed silent for longer
	// than Options.ReceiveTimeout.
	ErrReceiveTimeout = errors.New("edgetts: receive timeout")
	// ErrConnectTimeout reports that the service could not be reached within
	// Options.ConnectTimeout.
	ErrConnectTimeout = errors.New("edgetts: connect timeout")
)

// StatusError is returned when the service answers a request with an
// unexpected HTTP status (for example 403 when the token is rejected).
type StatusError struct {
	Op         string // "synthesize" or "voices"
	StatusCode int
}

func (e *StatusError) Error() string {
	return fmt.Sprintf("edgetts: %s: service answered HTTP %d", e.Op, e.StatusCode)
}

const (
	defaultConnectTimeout = 10 * time.Second
	defaultReceiveTimeout = 25 * time.Second
	defaultVoicesTTL      = 24 * time.Hour

	// maxFrameBytes bounds one websocket message, maxAudioBytes one result.
	maxFrameBytes = 4 << 20
	maxAudioBytes = 64 << 20
)

// Options configures a Client. The zero value is ready for production use.
type Options struct {
	// HTTPClient is used for the websocket handshake and the voice list. It
	// must not set Client.Timeout (that would cut websocket sessions short).
	// Default: a private client that honours the proxy environment variables.
	HTTPClient *http.Client
	// ConnectTimeout bounds the connection and websocket handshake (10 s).
	ConnectTimeout time.Duration
	// ReceiveTimeout bounds the wait for each message of a session and the
	// voice list download (25 s).
	ReceiveTimeout time.Duration
	// VoicesTTL is how long a fetched voice list is reused (24 h).
	VoicesTTL time.Duration
	// Now replaces time.Now, for tests.
	Now func() time.Time
	// WSSURL and VoicesURL replace the service endpoints, for tests. Each
	// must already contain a query string; parameters are appended with "&".
	WSSURL    string
	VoicesURL string
}

// Client talks to the Edge Read-Aloud service. It is safe for concurrent use;
// it does not limit concurrency itself (the caller keeps the service's
// tolerance in mind, the reader uses two parallel syntheses).
type Client struct {
	httpClient     *http.Client
	connectTimeout time.Duration
	receiveTimeout time.Duration
	voicesTTL      time.Duration
	now            func() time.Time
	wssURL         string
	voicesURL      string

	mu       sync.Mutex
	skew     time.Duration // server clock minus local clock
	voices   []Voice
	voicesAt time.Time

	voicesFetch chan struct{} // capacity 1: one voice list download at a time
}

// New returns a client configured by opts.
func New(opts Options) *Client {
	c := &Client{
		httpClient:     opts.HTTPClient,
		connectTimeout: opts.ConnectTimeout,
		receiveTimeout: opts.ReceiveTimeout,
		voicesTTL:      opts.VoicesTTL,
		now:            opts.Now,
		wssURL:         opts.WSSURL,
		voicesURL:      opts.VoicesURL,
		voicesFetch:    make(chan struct{}, 1),
	}
	if c.httpClient == nil {
		c.httpClient = &http.Client{Transport: http.DefaultTransport.(*http.Transport).Clone()}
	}
	if c.connectTimeout <= 0 {
		c.connectTimeout = defaultConnectTimeout
	}
	if c.receiveTimeout <= 0 {
		c.receiveTimeout = defaultReceiveTimeout
	}
	if c.voicesTTL <= 0 {
		c.voicesTTL = defaultVoicesTTL
	}
	if c.now == nil {
		c.now = time.Now
	}
	if c.wssURL == "" {
		c.wssURL = defaultWSSURL
	}
	if c.voicesURL == "" {
		c.voicesURL = defaultVoicesURL
	}
	return c
}

// Synthesize returns the MP3 (24 kHz, 48 kbit/s, mono) for text spoken by
// voice ("vi-VN-HoaiMyNeural"). ratePct is the speed change in percent
// (+0 = normal) and pitchHz the pitch change in Hz. Text longer than the
// service limit is split at whitespace and the audio is concatenated.
//
// Cancelling ctx aborts the synthesis. Errors: ErrInvalidVoice and
// ErrEmptyText for bad input; context errors; *StatusError, ErrNoAudio,
// ErrProtocol, ErrConnectTimeout, ErrReceiveTimeout or a network error when
// the service fails.
func (c *Client) Synthesize(ctx context.Context, text, voice string, ratePct, pitchHz int) ([]byte, error) {
	serviceVoice, err := serviceVoiceName(voice)
	if err != nil {
		return nil, err
	}
	escaped := escapeXML(removeIncompatibleCharacters(text))
	chunks, err := splitByByteLength([]byte(escaped), maxSSMLTextBytes)
	if err != nil {
		return nil, err
	}
	if len(chunks) == 0 {
		return nil, ErrEmptyText
	}

	var audio []byte
	for _, chunk := range chunks {
		ssml := buildSSML(serviceVoice, ratePct, pitchHz, chunk)
		part, err := c.session(ctx, ssml)
		if isForbidden(err) {
			// The token depends on the clock; the 403 handler has moved our
			// clock to the server's. One retry, like the reference client.
			part, err = c.session(ctx, ssml)
		}
		if err != nil {
			return nil, err
		}
		if len(audio)+len(part) > maxAudioBytes {
			return nil, fmt.Errorf("%w: audio larger than %d bytes", ErrProtocol, maxAudioBytes)
		}
		audio = append(audio, part...)
	}
	return audio, nil
}

func isForbidden(err error) bool {
	var se *StatusError
	return errors.As(err, &se) && se.StatusCode == http.StatusForbidden
}

// gecToken returns the Sec-MS-GEC token for the skew-corrected current time.
func (c *Client) gecToken() string {
	c.mu.Lock()
	skew := c.skew
	c.mu.Unlock()
	return secMSGEC(c.now().Add(skew).Unix())
}

// adjustSkew sets the clock skew from the Date header of a 403 response. It
// reports whether the header was usable.
func (c *Client) adjustSkew(h http.Header) bool {
	date := h.Get("Date")
	if date == "" {
		return false
	}
	serverTime, err := http.ParseTime(date)
	if err != nil {
		return false
	}
	c.mu.Lock()
	c.skew = serverTime.Sub(c.now())
	c.mu.Unlock()
	return true
}

// statusError turns a non-success response into a *StatusError. For 403 it
// first corrects the clock skew; a 403 without a usable Date header cannot be
// retried and is reported as such.
func (c *Client) statusError(op string, resp *http.Response) error {
	se := &StatusError{Op: op, StatusCode: resp.StatusCode}
	if resp.StatusCode == http.StatusForbidden && !c.adjustSkew(resp.Header) {
		return fmt.Errorf("edgetts: %s: HTTP 403 without a usable Date header (clock skew cannot be corrected): %w",
			op, &unretryable{se})
	}
	return se
}

// unretryable hides a StatusError from isForbidden while keeping the status
// visible in the message.
type unretryable struct{ se *StatusError }

func (u *unretryable) Error() string { return u.se.Error() }

func (c *Client) wssHeaders() http.Header {
	h := http.Header{}
	h.Set("Pragma", "no-cache")
	h.Set("Cache-Control", "no-cache")
	h.Set("Origin", extensionOrigin)
	h.Set("User-Agent", userAgent)
	h.Set("Accept-Encoding", acceptEncoding)
	h.Set("Accept-Language", acceptLanguage)
	h.Set("Cookie", "muid="+randomHex(16, true)+";")
	return h
}

// session runs one websocket turn: config frame, SSML frame, audio frames
// until turn.end.
func (c *Client) session(ctx context.Context, ssml string) ([]byte, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	url := c.wssURL + "&ConnectionId=" + randomUUIDHex() +
		"&Sec-MS-GEC=" + c.gecToken() +
		"&Sec-MS-GEC-Version=" + secMSGECVersion

	dialCtx, cancelDial := context.WithTimeout(ctx, c.connectTimeout)
	conn, resp, err := websocket.Dial(dialCtx, url, &websocket.DialOptions{
		HTTPClient: c.httpClient,
		HTTPHeader: c.wssHeaders(),
	})
	dialTimedOut := dialCtx.Err() != nil
	cancelDial()
	if err != nil {
		if ctxErr := ctx.Err(); ctxErr != nil {
			return nil, ctxErr
		}
		if resp != nil && resp.StatusCode != http.StatusSwitchingProtocols {
			return nil, c.statusError("synthesize", resp)
		}
		if dialTimedOut {
			return nil, fmt.Errorf("%w after %s", ErrConnectTimeout, c.connectTimeout)
		}
		return nil, fmt.Errorf("edgetts: connect: %w", scrubURL(err))
	}
	defer conn.CloseNow()
	conn.SetReadLimit(maxFrameBytes)

	timestamp := jsDate(c.now())
	config := "X-Timestamp:" + timestamp + "\r\n" +
		"Content-Type:application/json; charset=utf-8\r\n" +
		"Path:speech.config\r\n\r\n" +
		`{"context":{"synthesis":{"audio":{"metadataoptions":{` +
		`"sentenceBoundaryEnabled":"true","wordBoundaryEnabled":"false"},` +
		`"outputFormat":"` + outputFormat + `"}}}}` + "\r\n"
	request := "X-RequestId:" + randomUUIDHex() + "\r\n" +
		"Content-Type:application/ssml+xml\r\n" +
		"X-Timestamp:" + timestamp + "Z\r\n" + // the stray Z is what Edge sends
		"Path:ssml\r\n\r\n" + ssml

	for _, frame := range []string{config, request} {
		if err := c.write(ctx, conn, frame); err != nil {
			return nil, err
		}
	}

	var audio []byte
	for {
		typ, data, err := c.read(ctx, conn)
		if err != nil {
			return nil, err
		}
		switch typ {
		case websocket.MessageText:
			switch path := textFramePath(data); path {
			case "turn.end":
				if len(audio) == 0 {
					return nil, ErrNoAudio
				}
				return audio, nil
			case "audio.metadata", "response", "turn.start":
				// Boundary metadata is not used by the reader.
			default:
				return nil, fmt.Errorf("%w: text frame with path %q", ErrProtocol, path)
			}
		case websocket.MessageBinary:
			payload, err := audioPayload(data)
			if err != nil {
				return nil, err
			}
			if len(audio)+len(payload) > maxAudioBytes {
				return nil, fmt.Errorf("%w: audio larger than %d bytes", ErrProtocol, maxAudioBytes)
			}
			audio = append(audio, payload...)
		}
	}
}

func (c *Client) write(ctx context.Context, conn *websocket.Conn, frame string) error {
	wctx, cancel := context.WithTimeout(ctx, c.receiveTimeout)
	defer cancel()
	if err := conn.Write(wctx, websocket.MessageText, []byte(frame)); err != nil {
		if ctxErr := ctx.Err(); ctxErr != nil {
			return ctxErr
		}
		if wctx.Err() != nil {
			return fmt.Errorf("%w: send blocked for %s", ErrReceiveTimeout, c.receiveTimeout)
		}
		return fmt.Errorf("edgetts: send: %w", err)
	}
	return nil
}

func (c *Client) read(ctx context.Context, conn *websocket.Conn) (websocket.MessageType, []byte, error) {
	rctx, cancel := context.WithTimeout(ctx, c.receiveTimeout)
	defer cancel()
	typ, data, err := conn.Read(rctx)
	if err != nil {
		if ctxErr := ctx.Err(); ctxErr != nil {
			return 0, nil, ctxErr
		}
		if rctx.Err() != nil {
			return 0, nil, fmt.Errorf("%w: no data for %s", ErrReceiveTimeout, c.receiveTimeout)
		}
		// Includes a close before turn.end: a partial MP3 must never be
		// returned as a success.
		return 0, nil, fmt.Errorf("edgetts: connection lost before the end of the turn: %w", err)
	}
	return typ, data, nil
}

// textFramePath returns the Path header of a text frame ("" when absent).
func textFramePath(data []byte) string {
	head := data
	if i := bytes.Index(data, []byte("\r\n\r\n")); i >= 0 {
		head = data[:i]
	}
	return frameHeaders(head)["Path"]
}

func frameHeaders(head []byte) map[string]string {
	headers := make(map[string]string, 4)
	for _, line := range strings.Split(string(head), "\r\n") {
		if k, v, ok := strings.Cut(line, ":"); ok {
			headers[strings.TrimSpace(k)] = strings.TrimSpace(v)
		}
	}
	return headers
}

// audioPayload extracts the MP3 bytes of a binary frame: a 2 byte big-endian
// header length, the headers, CRLF, then the payload. The service ends the
// stream with a frame without Content-Type and without data.
func audioPayload(frame []byte) ([]byte, error) {
	if len(frame) < 2 {
		return nil, fmt.Errorf("%w: binary frame without header length", ErrProtocol)
	}
	headerLen := int(binary.BigEndian.Uint16(frame))
	if headerLen+2 > len(frame) {
		return nil, fmt.Errorf("%w: binary frame header longer than the frame", ErrProtocol)
	}
	headers := frameHeaders(frame[2 : 2+headerLen])
	payload := frame[2+headerLen:]
	if headers["Path"] != "audio" {
		return nil, fmt.Errorf("%w: binary frame with path %q", ErrProtocol, headers["Path"])
	}
	contentType, hasType := headers["Content-Type"]
	if !hasType {
		if len(payload) != 0 {
			return nil, fmt.Errorf("%w: audio data without Content-Type", ErrProtocol)
		}
		return nil, nil
	}
	if contentType != "audio/mpeg" {
		return nil, fmt.Errorf("%w: audio frame with Content-Type %q", ErrProtocol, contentType)
	}
	if len(payload) == 0 {
		return nil, fmt.Errorf("%w: audio frame without data", ErrProtocol)
	}
	return payload, nil
}

// jsDate formats t like JavaScript's Date.prototype.toString in UTC.
func jsDate(t time.Time) string {
	return t.UTC().Format("Mon Jan 02 2006 15:04:05") + " GMT+0000 (Coordinated Universal Time)"
}

func randomHex(n int, upper bool) string {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		panic("edgetts: crypto/rand failed: " + err.Error())
	}
	s := hex.EncodeToString(b)
	if upper {
		s = strings.ToUpper(s)
	}
	return s
}

// randomUUIDHex returns a version 4 UUID without dashes.
func randomUUIDHex() string {
	b := make([]byte, 16)
	if _, err := rand.Read(b); err != nil {
		panic("edgetts: crypto/rand failed: " + err.Error())
	}
	b[6] = b[6]&0x0f | 0x40
	b[8] = b[8]&0x3f | 0x80
	return hex.EncodeToString(b)
}

// scrubURL removes the request URL (it carries the request token) from
// errors that end up in logs.
func scrubURL(err error) error {
	msg := err.Error()
	for _, marker := range []string{"wss://", "ws://", "https://", "http://"} {
		for {
			i := strings.Index(msg, marker)
			if i < 0 {
				break
			}
			end := i + len(marker)
			for end < len(msg) && !strings.ContainsRune(" \"'\n", rune(msg[end])) {
				end++
			}
			msg = msg[:i] + "<service url>" + msg[end:]
		}
	}
	if msg == err.Error() {
		return err
	}
	return &scrubbedError{msg: msg, err: err}
}

type scrubbedError struct {
	msg string
	err error
}

func (e *scrubbedError) Error() string { return e.msg }
func (e *scrubbedError) Unwrap() error { return e.err }
