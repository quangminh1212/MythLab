package edgetts

import (
	"context"
	"os"
	"strings"
	"testing"
	"time"
)

// These tests talk to the real Microsoft service; `go test -short` skips them.

// mp3FrameSync reports whether b starts with an MPEG audio frame header.
func mp3FrameSync(b []byte) bool {
	return len(b) >= 4 && b[0] == 0xFF && b[1]&0xE0 == 0xE0
}

// synthesizeLive calls the real service the way the server does: up to three
// attempts with a growing pause, because the service now and then drops a
// session without audio. Every failed attempt is logged.
func synthesizeLive(ctx context.Context, t *testing.T, c *Client, text, voice string, ratePct, pitchHz int) []byte {
	t.Helper()
	var err error
	for attempt := 1; attempt <= 3; attempt++ {
		var audio []byte
		start := time.Now()
		if audio, err = c.Synthesize(ctx, text, voice, ratePct, pitchHz); err == nil {
			return audio
		}
		t.Logf("attempt %d failed after %s: %v", attempt, time.Since(start).Round(time.Millisecond), err)
		time.Sleep(time.Duration(attempt) * 1200 * time.Millisecond)
	}
	t.Fatalf("synthesize: %v", err)
	return nil
}

func TestIntegrationSynthesize(t *testing.T) {
	if testing.Short() {
		t.Skip("network test skipped with -short")
	}
	c := New(Options{})
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	audio := synthesizeLive(ctx, t, c, "Xin chào, đây là MythLab.", "vi-VN-HoaiMyNeural", 0, 0)
	if !mp3FrameSync(audio) {
		t.Fatalf("not an MP3: starts with % x", audio[:min(len(audio), 8)])
	}
	if len(audio) <= 5000 {
		t.Fatalf("MP3 too small: %d bytes", len(audio))
	}
	t.Logf("%d bytes, header % x", len(audio), audio[:4])
}

// Rate and pitch reach the service: the same sentence is shorter at +80 %
// than at -30 % (the stream is 48 kbit/s CBR, so bytes are time).
func TestIntegrationRateAndPitch(t *testing.T) {
	if testing.Short() {
		t.Skip("network test skipped with -short")
	}
	c := New(Options{})
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()
	voice := liveVoice()
	const text = "Tốc độ đọc và cao độ được máy chủ áp dụng đúng như yêu cầu."
	slow := synthesizeLive(ctx, t, c, text, voice, -30, -10)
	fast := synthesizeLive(ctx, t, c, text, voice, 80, 20)
	t.Logf("%s: rate -30%%/pitch -10Hz = %d bytes, rate +80%%/pitch +20Hz = %d bytes", voice, len(slow), len(fast))
	if !mp3FrameSync(slow) || !mp3FrameSync(fast) {
		t.Fatal("not MP3")
	}
	if len(fast)*3 > len(slow)*2 {
		t.Fatalf("rate has no effect: slow %d bytes, fast %d bytes", len(slow), len(fast))
	}
}

// liveVoice is the voice of the secondary live tests. EDGETTS_TEST_VOICE
// overrides it, which helps when the service has trouble with one locale.
func liveVoice() string {
	if v := os.Getenv("EDGETTS_TEST_VOICE"); v != "" {
		return v
	}
	return "vi-VN-HoaiMyNeural"
}

// A text above the 4096 byte limit goes out as several sessions whose audio
// is concatenated; XML special characters must survive the trip.
func TestIntegrationLongText(t *testing.T) {
	if testing.Short() {
		t.Skip("network test skipped with -short")
	}
	c := New(Options{})
	ctx, cancel := context.WithTimeout(context.Background(), 240*time.Second)
	defer cancel()
	// The service streams audio at about real time, so the text is made of
	// characters that cost many bytes once escaped but little speech: about
	// 5 kB of SSML text, a little over one minute of audio at double speed.
	text := strings.Repeat("Tấm & Cám. "+strings.Repeat("<", 60)+strings.Repeat(">", 60)+"\n", 10)
	chunks, err := splitByByteLength([]byte(escapeXML(text)), maxSSMLTextBytes)
	if err != nil || len(chunks) < 2 {
		t.Fatalf("test text must need several sessions: %d chunks, err=%v", len(chunks), err)
	}
	start := time.Now()
	audio := synthesizeLive(ctx, t, c, text, liveVoice(), 100, 0)
	if !mp3FrameSync(audio) || len(audio) < 50_000 {
		t.Fatalf("long text gave %d bytes", len(audio))
	}
	t.Logf("%d bytes of text in %d sessions -> %d bytes of MP3 in %s",
		len(text), len(chunks), len(audio), time.Since(start).Round(time.Millisecond))
}

func TestIntegrationSkewRecovery(t *testing.T) {
	if testing.Short() {
		t.Skip("network test skipped with -short")
	}
	// A clock two hours behind makes the first token invalid; the client has
	// to recover from the 403 through the Date header.
	c := New(Options{Now: func() time.Time { return time.Now().Add(-2 * time.Hour) }})
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	audio := synthesizeLive(ctx, t, c, "Kiểm tra đồng hồ.", "vi-VN-NamMinhNeural", 0, 0)
	if !mp3FrameSync(audio) {
		t.Fatalf("not an MP3: % x", audio[:min(len(audio), 8)])
	}
	c.mu.Lock()
	skew := c.skew
	c.mu.Unlock()
	t.Logf("%d bytes, learned skew %s", len(audio), skew.Round(time.Second))
	if skew < 110*time.Minute || skew > 130*time.Minute {
		t.Fatalf("skew = %s, want about 2h (the service did not reject the stale token?)", skew)
	}
}

func TestIntegrationVoices(t *testing.T) {
	if testing.Short() {
		t.Skip("network test skipped with -short")
	}
	c := New(Options{})
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	vs, err := c.Voices(ctx)
	if err != nil {
		t.Fatalf("voices: %v", err)
	}
	found := false
	for _, v := range vs {
		if v.ShortName == "vi-VN-HoaiMyNeural" {
			found = true
			if v.Locale != "vi-VN" || v.Gender != "Female" || v.FriendlyName == "" {
				t.Fatalf("unexpected entry: %+v", v)
			}
		}
	}
	if !found {
		t.Fatalf("vi-VN-HoaiMyNeural missing from %d voices", len(vs))
	}
	reader := ReaderVoices(vs)
	if len(reader) < 2 || reader[0].Locale != "vi-VN" {
		t.Fatalf("reader filter: %+v", reader)
	}
	t.Logf("%d voices, %d after the reader filter", len(vs), len(reader))
}
