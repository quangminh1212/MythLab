package edgetts

import (
	"bytes"
	"fmt"
	"regexp"
	"strings"
	"unicode/utf8"
)

// removeIncompatibleCharacters replaces the control characters the service
// rejects (everything below U+0020 except tab, line feed and carriage return)
// with spaces. Invalid UTF-8 is replaced with U+FFFD so the SSML frame is
// always valid text.
func removeIncompatibleCharacters(s string) string {
	s = strings.ToValidUTF8(s, "�")
	return strings.Map(func(r rune) rune {
		if (r >= 0 && r <= 8) || r == 11 || r == 12 || (r >= 14 && r <= 31) {
			return ' '
		}
		return r
	}, s)
}

var xmlEscaper = strings.NewReplacer("&", "&amp;", "<", "&lt;", ">", "&gt;")

// escapeXML escapes text for use as SSML character data (the same three
// characters as Python's xml.sax.saxutils.escape).
func escapeXML(s string) string { return xmlEscaper.Replace(s) }

const asciiSpace = " \t\n\r\v\f"

// splitByByteLength splits escaped text into chunks of at most limit bytes.
// It prefers the last newline, then the last space, inside the limit; without
// either it cuts at the limit. A chunk never ends inside a UTF-8 sequence or
// inside an XML entity such as "&amp;". Chunks are trimmed and empty chunks
// are dropped.
func splitByByteLength(text []byte, limit int) ([][]byte, error) {
	if limit <= 0 {
		return nil, fmt.Errorf("edgetts: byte limit must be positive")
	}
	var out [][]byte
	appendChunk := func(b []byte) {
		if b = bytes.Trim(b, asciiSpace); len(b) > 0 {
			out = append(out, b)
		}
	}
	for len(text) > limit {
		window := text[:limit]
		splitAt := bytes.LastIndexByte(window, '\n')
		if splitAt < 0 {
			splitAt = bytes.LastIndexByte(window, ' ')
		}
		if splitAt < 0 {
			splitAt = safeUTF8Cut(text, limit)
		}
		splitAt = adjustForXMLEntity(text, splitAt)
		if splitAt <= 0 {
			// No natural boundary: the window starts with whitespace only
			// (drop it) or cannot be cut without breaking a character or an
			// entity.
			if trimmed := bytes.TrimLeft(text, asciiSpace); len(trimmed) < len(text) {
				text = trimmed
				continue
			}
			return nil, fmt.Errorf("edgetts: cannot split text within %d bytes", limit)
		}
		appendChunk(text[:splitAt])
		text = text[splitAt:]
	}
	appendChunk(text)
	return out, nil
}

// safeUTF8Cut returns the largest index <= limit at which text can be cut
// without splitting a UTF-8 sequence.
func safeUTF8Cut(text []byte, limit int) int {
	if limit >= len(text) {
		return len(text)
	}
	cut := limit
	for cut > 0 && !utf8.RuneStart(text[cut]) {
		cut--
	}
	return cut
}

// adjustForXMLEntity moves a split point back to the '&' of an entity that
// would otherwise be cut in two.
func adjustForXMLEntity(text []byte, splitAt int) int {
	for splitAt > 0 {
		amp := bytes.LastIndexByte(text[:splitAt], '&')
		if amp < 0 || bytes.IndexByte(text[amp:splitAt], ';') >= 0 {
			break
		}
		splitAt = amp
	}
	return splitAt
}

var (
	shortVoiceRe = regexp.MustCompile(`^([a-z]{2,})-([A-Z]{2,})-([A-Za-z0-9-]*Neural)$`)
	fullVoiceRe  = regexp.MustCompile(`^Microsoft Server Speech Text to Speech Voice \([A-Za-z0-9-]+, ?[A-Za-z0-9-]+\)$`)
)

// serviceVoiceName converts a short voice name such as "vi-VN-HoaiMyNeural"
// to the long form Edge sends ("Microsoft Server Speech Text to Speech Voice
// (vi-VN, HoaiMyNeural)"). A name already in the long form is accepted as is.
// The allowed alphabet keeps the name safe inside the SSML attribute.
func serviceVoiceName(voice string) (string, error) {
	if m := shortVoiceRe.FindStringSubmatch(voice); m != nil {
		lang, region, name := m[1], m[2], m[3]
		if i := strings.IndexByte(name, '-'); i >= 0 {
			region += "-" + name[:i]
			name = name[i+1:]
		}
		if name == "" || region[len(region)-1] == '-' {
			return "", fmt.Errorf("%w: %q", ErrInvalidVoice, voice)
		}
		return "Microsoft Server Speech Text to Speech Voice (" + lang + "-" + region + ", " + name + ")", nil
	}
	if fullVoiceRe.MatchString(voice) {
		return voice, nil
	}
	return "", fmt.Errorf("%w: %q", ErrInvalidVoice, voice)
}

// buildSSML wraps already escaped text. rate is a percentage, pitch is in Hz.
func buildSSML(serviceVoice string, ratePct, pitchHz int, escapedText []byte) string {
	var b strings.Builder
	b.Grow(len(escapedText) + 256)
	b.WriteString("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>")
	fmt.Fprintf(&b, "<voice name='%s'><prosody pitch='%+dHz' rate='%+d%%' volume='+0%%'>", serviceVoice, pitchHz, ratePct)
	b.Write(escapedText)
	b.WriteString("</prosody></voice></speak>")
	return b.String()
}
