package tts

import (
	"bytes"
	"context"
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	piperSuffix  = "Piper"
	piperTimeout = 90 * time.Second
	maxPCM       = 256 << 20
)

// IsPiperVoice reports whether voice is served by the Piper engine.
func IsPiperVoice(voice string) bool { return strings.HasSuffix(voice, piperSuffix) }

// Ext is the file extension (with dot) of audio synthesised for voice.
func Ext(voice string) string {
	if IsPiperVoice(voice) {
		return ".wav"
	}
	return ".mp3"
}

// ContentType is the MIME type of a cached audio file, by extension.
func ContentType(path string) string {
	if strings.EqualFold(filepath.Ext(path), ".wav") {
		return "audio/wav"
	}
	return "audio/mpeg"
}

type piperVoice struct {
	voice      Voice
	model      string
	sampleRate int
}

// Piper runs the open-source piper executable once per request. Voice IDs are
// only ever mapped to model paths through the table built at discovery.
type Piper struct {
	bin    string
	voices map[string]piperVoice
	order  []string
}

var (
	piperFileRe    = regexp.MustCompile(`^([a-z]{2,3})_([A-Z]{2,4})-(.+)$`)
	piperQualityRe = regexp.MustCompile(`(-(medium|high|low)|_low)$`)
	piperJunkRe    = regexp.MustCompile(`[^A-Za-z0-9]+`)
)

// piperID derives "vi-VN-Vais1000Piper" from "vi_VN-vais1000-medium".
func piperID(base string) (id, locale string, ok bool) {
	m := piperFileRe.FindStringSubmatch(base)
	if m == nil {
		return "", "", false
	}
	name := piperQualityRe.ReplaceAllString(m[3], "")
	var b strings.Builder
	for _, part := range piperJunkRe.Split(name, -1) {
		if part != "" {
			b.WriteString(strings.ToUpper(part[:1]) + part[1:])
		}
	}
	if b.Len() == 0 {
		return "", "", false
	}
	locale = m[1] + "-" + m[2]
	return locale + "-" + b.String() + piperSuffix, locale, true
}

// NewPiper discovers every <name>.onnx with a sibling <name>.onnx.json in dir.
// It returns nil when dir is empty or holds no usable voice.
func NewPiper(bin, dir string) *Piper {
	if dir == "" {
		return nil
	}
	if bin == "" {
		bin = "piper"
	}
	models, _ := filepath.Glob(filepath.Join(dir, "*.onnx"))
	sort.Strings(models)
	p := &Piper{bin: bin, voices: map[string]piperVoice{}}
	for _, m := range models {
		var cfg struct {
			Audio struct {
				SampleRate int `json:"sample_rate"`
			} `json:"audio"`
		}
		raw, err := os.ReadFile(m + ".json")
		if err != nil || json.Unmarshal(raw, &cfg) != nil || cfg.Audio.SampleRate < 4000 || cfg.Audio.SampleRate > 192000 {
			continue
		}
		base := strings.TrimSuffix(filepath.Base(m), ".onnx")
		id, loc, ok := piperID(base)
		if !ok {
			continue
		}
		if _, dup := p.voices[id]; dup {
			continue
		}
		display := strings.TrimSuffix(strings.TrimPrefix(id, loc+"-"), piperSuffix)
		p.voices[id] = piperVoice{
			voice:      Voice{ShortName: id, Locale: loc, Gender: "Unknown", FriendlyName: display + " (Piper, offline)"},
			model:      m,
			sampleRate: cfg.Audio.SampleRate,
		}
		p.order = append(p.order, id)
	}
	if len(p.order) == 0 {
		return nil
	}
	return p
}

// Voices lists the discovered voices.
func (p *Piper) Voices(context.Context) ([]Voice, error) {
	out := make([]Voice, 0, len(p.order))
	for _, id := range p.order {
		out = append(out, p.voices[id].voice)
	}
	return out, nil
}

// Synthesize returns WAV bytes. pitchHz is ignored.
func (p *Piper) Synthesize(ctx context.Context, text, voice string, ratePct, _ int) ([]byte, error) {
	v, ok := p.voices[voice]
	if !ok {
		return nil, &Error{http.StatusBadRequest, "bad_voice", "voice không hợp lệ"}
	}
	scale := 1 / (1 + float64(ratePct)/100)
	if scale < 0.5 {
		scale = 0.5
	} else if scale > 2 {
		scale = 2
	}
	ctx, cancel := context.WithTimeout(ctx, piperTimeout)
	defer cancel()
	cmd := exec.CommandContext(ctx, p.bin, "--model", v.model, "--output-raw",
		"--length_scale", strconv.FormatFloat(scale, 'f', 3, 64))
	cmd.Stdin = strings.NewReader(strings.ReplaceAll(text, "\n", " ") + "\n")
	var out, errb bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &limitBuf{b: &errb, max: 2048}
	if err := cmd.Run(); err != nil {
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		if errors.Is(err, exec.ErrNotFound) || errors.Is(err, os.ErrNotExist) {
			return nil, &Error{http.StatusServiceUnavailable, "tts_unavailable", "không tìm thấy chương trình piper"}
		}
		return nil, fmt.Errorf("piper: %v: %s", err, strings.TrimSpace(errb.String()))
	}
	if out.Len() == 0 || out.Len() > maxPCM {
		return nil, errors.New("piper trả về rỗng")
	}
	return wavFromPCM(out.Bytes(), v.sampleRate), nil
}

type limitBuf struct {
	b   *bytes.Buffer
	max int
}

func (l *limitBuf) Write(p []byte) (int, error) {
	if room := l.max - l.b.Len(); room > 0 {
		if len(p) < room {
			room = len(p)
		}
		l.b.Write(p[:room])
	}
	return len(p), nil
}

// wavFromPCM wraps 16-bit mono little-endian PCM in a WAV header.
func wavFromPCM(pcm []byte, rate int) []byte {
	if len(pcm)%2 == 1 {
		pcm = pcm[:len(pcm)-1]
	}
	var b bytes.Buffer
	b.Grow(44 + len(pcm))
	le := func(v any) { binary.Write(&b, binary.LittleEndian, v) }
	b.WriteString("RIFF")
	le(uint32(36 + len(pcm)))
	b.WriteString("WAVEfmt ")
	le(uint32(16))
	le(uint16(1)) // PCM
	le(uint16(1)) // mono
	le(uint32(rate))
	le(uint32(rate * 2))
	le(uint16(2))
	le(uint16(16))
	b.WriteString("data")
	le(uint32(len(pcm)))
	b.Write(pcm)
	return b.Bytes()
}

// Multi routes voices ending in "Piper" to the Piper engine and the rest to Edge.
type Multi struct{ edge, piper Engine }

// NewMulti combines the engines; either may be nil. It returns nil when both are.
func NewMulti(edge Engine, piper *Piper) Engine {
	switch {
	case edge == nil && piper == nil:
		return nil
	case piper == nil:
		return edge
	case edge == nil:
		return piper
	}
	return &Multi{edge: edge, piper: piper}
}

func (m *Multi) Synthesize(ctx context.Context, text, voice string, rate, pitch int) ([]byte, error) {
	e := m.edge
	if IsPiperVoice(voice) {
		e = m.piper
	}
	return e.Synthesize(ctx, text, voice, rate, pitch)
}

// Voices is the union, Vietnamese Edge voices first. An Edge failure does not
// hide the Piper voices; the error is returned alongside the partial list.
func (m *Multi) Voices(ctx context.Context) ([]Voice, error) {
	pv, _ := m.piper.Voices(ctx)
	ev, err := m.edge.Voices(ctx)
	all := append(append([]Voice{}, ev...), pv...)
	sort.SliceStable(all, func(i, j int) bool {
		return strings.HasPrefix(all[i].Locale, "vi-") && !strings.HasPrefix(all[j].Locale, "vi-")
	})
	return all, err
}
