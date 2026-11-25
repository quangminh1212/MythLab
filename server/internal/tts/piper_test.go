package tts

import (
	"context"
	"encoding/binary"
	"errors"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// TestMain lets the test binary act as the piper executable.
func TestMain(m *testing.M) {
	if os.Getenv("MYTHLAB_FAKE_PIPER") == "1" {
		buf := make([]byte, 4096)
		n, _ := os.Stdin.Read(buf)
		fmt.Fprintf(os.Stderr, "args=%v\n", os.Args[1:])
		os.Stdout.Write([]byte(strings.Repeat("\x01\x00", n)))
		if os.Getenv("MYTHLAB_FAKE_PIPER_ARGS") == "1" {
			os.Stdout.Write([]byte(strings.Join(os.Args[1:], " ")))
		}
		os.Exit(0)
	}
	os.Exit(m.Run())
}

func piperDir(t *testing.T) string {
	dir := t.TempDir()
	for name, rate := range map[string]int{"vi_VN-vais1000-medium": 22050, "vi_VN-25hours_single-low": 16000, "vi_VN-vivos-x_low": 16000} {
		os.WriteFile(filepath.Join(dir, name+".onnx"), []byte("x"), 0o644)
		os.WriteFile(filepath.Join(dir, name+".onnx.json"), []byte(fmt.Sprintf(`{"audio":{"sample_rate":%d}}`, rate)), 0o644)
	}
	os.WriteFile(filepath.Join(dir, "lonely.onnx"), []byte("x"), 0o644) // no json
	return dir
}

func TestPiperDiscoveryAndSynth(t *testing.T) {
	t.Setenv("MYTHLAB_FAKE_PIPER", "1")
	if NewPiper("x", "") != nil || NewPiper("x", t.TempDir()) != nil {
		t.Fatal("expected nil without voices")
	}
	p := NewPiper(os.Args[0], piperDir(t))
	vs, _ := p.Voices(context.Background())
	var ids []string
	for _, v := range vs {
		ids = append(ids, v.ShortName)
		if !voiceRe.MatchString(v.ShortName) || v.Locale != "vi-VN" {
			t.Errorf("bad voice %+v", v)
		}
	}
	if got := strings.Join(ids, ","); got != "vi-VN-25hoursSinglePiper,vi-VN-Vais1000Piper,vi-VN-VivosXPiper" {
		t.Fatalf("ids = %s", got)
	}
	wav, err := p.Synthesize(context.Background(), "Xin chào", "vi-VN-Vais1000Piper", 0, 0)
	if err != nil || string(wav[:4]) != "RIFF" || binary.LittleEndian.Uint32(wav[24:]) != 22050 {
		t.Fatalf("wav err=%v len=%d", err, len(wav))
	}
	if _, err := p.Synthesize(context.Background(), "a", "vi-VN-NopePiper", 0, 0); err == nil {
		t.Fatal("unknown voice accepted")
	}
	bad := NewPiper(filepath.Join(t.TempDir(), "missing"), piperDir(t))
	_, err = bad.Synthesize(context.Background(), "a", "vi-VN-Vais1000Piper", 0, 0)
	var te *Error
	if !errors.As(err, &te) || te.Status != http.StatusServiceUnavailable {
		t.Fatalf("missing binary err = %v", err)
	}
}

func TestPiperLengthScale(t *testing.T) {
	t.Setenv("MYTHLAB_FAKE_PIPER", "1")
	t.Setenv("MYTHLAB_FAKE_PIPER_ARGS", "1")
	p := NewPiper(os.Args[0], piperDir(t))
	wav, err := p.Synthesize(context.Background(), "a", "vi-VN-Vais1000Piper", 100, 0)
	if err != nil || !strings.Contains(string(wav), "--length_scale 0.50") {
		t.Fatalf("%v %q", err, wav)
	}
}

func TestMultiAndServiceWAV(t *testing.T) {
	t.Setenv("MYTHLAB_FAKE_PIPER", "1")
	f := &fakeEngine{}
	eng := NewMulti(f, NewPiper(os.Args[0], piperDir(t)))
	if NewMulti(nil, nil) != nil {
		t.Fatal("both nil must be nil")
	}
	s := NewService(ServiceOptions{Engine: eng, Dir: t.TempDir(), backoff: 1})
	p, err := s.Speak(context.Background(), "Xin chào", "vi-VN-VivosXPiper", 0, 0)
	if err != nil || !strings.HasSuffix(p, ".wav") || ContentType(p) != "audio/wav" {
		t.Fatalf("%q %v", p, err)
	}
	if f.calls.Load() != 0 {
		t.Fatal("edge was called for a Piper voice")
	}
	p2, err := s.Speak(context.Background(), "Xin chào", "vi-VN-HoaiMyNeural", 0, 0)
	if err != nil || !strings.HasSuffix(p2, ".mp3") || ContentType(p2) != "audio/mpeg" {
		t.Fatalf("%q %v", p2, err)
	}
	list, ok := s.Voices(context.Background())
	if !ok {
		t.Fatal("no voices")
	}
	n := 0
	for _, v := range list {
		if strings.HasSuffix(v.ID, "Piper") {
			n++
		}
	}
	if n != 3 {
		t.Fatalf("piper voices = %d in %v", n, list)
	}
	// Piper only (Edge off) is still available.
	s2 := NewService(ServiceOptions{Engine: NewMulti(nil, NewPiper(os.Args[0], piperDir(t))), Dir: t.TempDir()})
	if !s2.Available() {
		t.Fatal("piper-only unavailable")
	}
	// Edge down does not hide Piper voices.
	fe := &fakeEngine{}
	fe.voicesErr = errors.New("down")
	m := NewMulti(fe, NewPiper(os.Args[0], piperDir(t)))
	if vs, err := m.Voices(context.Background()); err == nil || len(vs) != 3 {
		t.Fatalf("vs=%d err=%v", len(vs), err)
	}
}
