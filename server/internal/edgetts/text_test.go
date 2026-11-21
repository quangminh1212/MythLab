package edgetts

import (
	"bytes"
	"errors"
	"strings"
	"testing"
	"unicode/utf8"
)

func TestRemoveIncompatibleCharacters(t *testing.T) {
	in := "a\x00b\x08c\td\ne\x0bf\x0cg\rh\x0ei\x1fj k đ"
	want := "a b c\td\ne f g\rh i j k đ"
	if got := removeIncompatibleCharacters(in); got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
	if got := removeIncompatibleCharacters("ab\xffcd"); got != "ab�cd" {
		t.Fatalf("invalid UTF-8 not replaced: %q", got)
	}
}

func TestEscapeXML(t *testing.T) {
	if got := escapeXML(`Tom & "Jerry" <b>'x'</b> &amp;`); got != `Tom &amp; "Jerry" &lt;b&gt;'x'&lt;/b&gt; &amp;amp;` {
		t.Fatalf("got %q", got)
	}
}

func TestSplitShortTextIsOneTrimmedChunk(t *testing.T) {
	chunks, err := splitByByteLength([]byte("  \n Xin chào \n"), 4096)
	if err != nil || len(chunks) != 1 || string(chunks[0]) != "Xin chào" {
		t.Fatalf("chunks=%q err=%v", chunks, err)
	}
	chunks, err = splitByByteLength([]byte(" \n\t "), 4096)
	if err != nil || len(chunks) != 0 {
		t.Fatalf("blank text: chunks=%q err=%v", chunks, err)
	}
}

func TestSplitPrefersNewlineThenSpace(t *testing.T) {
	chunks, err := splitByByteLength([]byte("aaa bbb\nccc ddd eee"), 12)
	if err != nil {
		t.Fatal(err)
	}
	// Newline at index 7 wins over the later space at index 11.
	want := []string{"aaa bbb", "ccc ddd eee"}
	if len(chunks) != len(want) {
		t.Fatalf("chunks=%q", chunks)
	}
	for i := range want {
		if string(chunks[i]) != want[i] {
			t.Fatalf("chunk %d = %q, want %q", i, chunks[i], want[i])
		}
	}

	chunks, err = splitByByteLength([]byte("aaa bbb ccc ddd"), 9)
	if err != nil || len(chunks) != 2 || string(chunks[0]) != "aaa bbb" || string(chunks[1]) != "ccc ddd" {
		t.Fatalf("chunks=%q err=%v", chunks, err)
	}
}

// checkChunks asserts the invariants of a split: size limit, valid UTF-8, no
// broken entity, and nothing lost except whitespace.
func checkChunks(t *testing.T, text string, limit int) [][]byte {
	t.Helper()
	chunks, err := splitByByteLength([]byte(text), limit)
	if err != nil {
		t.Fatalf("split(limit %d): %v", limit, err)
	}
	strip := func(s string) string {
		return strings.Map(func(r rune) rune {
			if strings.ContainsRune(asciiSpace, r) {
				return -1
			}
			return r
		}, s)
	}
	var joined strings.Builder
	for i, c := range chunks {
		if len(c) == 0 || len(c) > limit {
			t.Fatalf("chunk %d has %d bytes (limit %d)", i, len(c), limit)
		}
		if !utf8.Valid(c) {
			t.Fatalf("chunk %d is not valid UTF-8: %q", i, c)
		}
		if amp := bytes.LastIndexByte(c, '&'); amp >= 0 && bytes.IndexByte(c[amp:], ';') < 0 {
			t.Fatalf("chunk %d ends inside an entity: %q", i, c[amp:])
		}
		if c[0] == ';' || bytes.HasPrefix(c, []byte("amp;")) || bytes.HasPrefix(c, []byte("lt;")) || bytes.HasPrefix(c, []byte("gt;")) {
			t.Fatalf("chunk %d starts inside an entity: %q", i, c[:4])
		}
		joined.Write(c)
	}
	if strip(joined.String()) != strip(text) {
		t.Fatalf("content changed by the split (limit %d)", limit)
	}
	return chunks
}

func TestSplitInvariants(t *testing.T) {
	sentence := "Ngày xửa ngày xưa, ở một làng nọ có hai anh em Tấm & Cám <rất> khác nhau.\n"
	spaced := escapeXML(strings.Repeat(sentence, 200))
	unspaced := escapeXML(strings.Repeat("đường&<>ằm𝄞", 900)) // no whitespace at all
	entities := strings.Repeat("&amp;", 2000)
	for _, text := range []string{spaced, unspaced, entities} {
		for _, limit := range []int{16, 17, 18, 19, 20, 21, 64, 255, 4096} {
			checkChunks(t, text, limit)
		}
	}
	if n := len(checkChunks(t, spaced, 4096)); n < 4 {
		t.Fatalf("expected several chunks, got %d", n)
	}
}

func TestSplitNeverCutsMultiByteRune(t *testing.T) {
	// 3-byte runes, limit not a multiple of 3: the cut must back off.
	text := strings.Repeat("ề", 100)
	chunks := checkChunks(t, text, 10)
	for _, c := range chunks {
		if len(c) != 9 && len(c) != 3 {
			t.Fatalf("unexpected chunk size %d", len(c))
		}
	}
}

func TestSplitLeadingWhitespaceWindow(t *testing.T) {
	text := " " + strings.Repeat("x", 30)
	chunks := checkChunks(t, text, 10)
	if len(chunks) != 3 {
		t.Fatalf("chunks=%q", chunks)
	}
}

func TestSplitImpossible(t *testing.T) {
	if _, err := splitByByteLength([]byte("&amp;&amp;&amp;"), 3); err == nil {
		t.Fatal("expected an error when an entity does not fit in the limit")
	}
	if _, err := splitByByteLength([]byte("abc"), 0); err == nil {
		t.Fatal("expected an error for a non-positive limit")
	}
}

func TestServiceVoiceName(t *testing.T) {
	ok := map[string]string{
		"vi-VN-HoaiMyNeural":           "Microsoft Server Speech Text to Speech Voice (vi-VN, HoaiMyNeural)",
		"en-US-EmmaMultilingualNeural": "Microsoft Server Speech Text to Speech Voice (en-US, EmmaMultilingualNeural)",
		"fil-PH-AngeloNeural":          "Microsoft Server Speech Text to Speech Voice (fil-PH, AngeloNeural)",
		"zh-CN-liaoning-XiaobeiNeural": "Microsoft Server Speech Text to Speech Voice (zh-CN-liaoning, XiaobeiNeural)",
		"Microsoft Server Speech Text to Speech Voice (cy-GB, NiaNeural)": "Microsoft Server Speech Text to Speech Voice (cy-GB, NiaNeural)",
	}
	for in, want := range ok {
		got, err := serviceVoiceName(in)
		if err != nil || got != want {
			t.Errorf("serviceVoiceName(%q) = %q, %v; want %q", in, got, err, want)
		}
	}
	bad := []string{
		"", "HoaiMy", "vi-VN-HoaiMy", "vi-vn-HoaiMyNeural", "VI-VN-HoaiMyNeural",
		"vi-VN-Hoai'/><break/>Neural", "vi-VN-Hoai My Neural", "vi-VN--Neural",
		"Microsoft Server Speech Text to Speech Voice (cy-GB, Nia'Neural)",
	}
	for _, in := range bad {
		if got, err := serviceVoiceName(in); !errors.Is(err, ErrInvalidVoice) {
			t.Errorf("serviceVoiceName(%q) = %q, %v; want ErrInvalidVoice", in, got, err)
		}
	}
}

func TestBuildSSML(t *testing.T) {
	got := buildSSML("Microsoft Server Speech Text to Speech Voice (vi-VN, HoaiMyNeural)", -10, 5, []byte("a &amp; b"))
	want := "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>" +
		"<voice name='Microsoft Server Speech Text to Speech Voice (vi-VN, HoaiMyNeural)'>" +
		"<prosody pitch='+5Hz' rate='-10%' volume='+0%'>a &amp; b</prosody></voice></speak>"
	if got != want {
		t.Fatalf("got  %s\nwant %s", got, want)
	}
	if got := buildSSML("V", 0, 0, nil); !strings.Contains(got, "pitch='+0Hz' rate='+0%'") {
		t.Fatalf("zero values must be signed: %s", got)
	}
}
