package tts

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"sync/atomic"
	"testing"
	"time"

	"mythlab/internal/edgetts"
)

type fakeEdge struct {
	calls  atomic.Int64
	err    error
	voices []edgetts.Voice
}

func (f *fakeEdge) Synthesize(_ context.Context, text, voice string, rate, pitch int) ([]byte, error) {
	f.calls.Add(1)
	if f.err != nil {
		return nil, f.err
	}
	return []byte(fmt.Sprintf("MP3|%s|%d|%d|%s", voice, rate, pitch, text)), nil
}

func (f *fakeEdge) Voices(context.Context) ([]edgetts.Voice, error) { return f.voices, f.err }

func TestEdgeAdapterPassesThrough(t *testing.T) {
	fe := &fakeEdge{voices: []edgetts.Voice{
		{ShortName: "en-US-EmmaMultilingualNeural", Locale: "en-US", Gender: "Female", FriendlyName: "Emma"},
		{ShortName: "vi-VN-HoaiMyNeural", Locale: "vi-VN", Gender: "Female", FriendlyName: "HoaiMy"},
		{ShortName: "en-US-GuyNeural", Locale: "en-US", Gender: "Male", FriendlyName: "Guy"},
	}}
	eng := FromEdge(fe)
	data, err := eng.Synthesize(context.Background(), "xin chào", "vi-VN-HoaiMyNeural", 20, -5)
	if err != nil || string(data) != "MP3|vi-VN-HoaiMyNeural|20|-5|xin chào" {
		t.Fatalf("Synthesize = %q, %v", data, err)
	}
	all, err := eng.Voices(context.Background())
	if err != nil || len(all) != 3 || all[1] != (Voice{ShortName: "vi-VN-HoaiMyNeural", Locale: "vi-VN", Gender: "Female", FriendlyName: "HoaiMy"}) {
		t.Fatalf("Voices = %+v, %v", all, err)
	}

	// through the service: Vietnamese first, then multilingual, the rest dropped
	s := NewService(ServiceOptions{Engine: eng, Dir: t.TempDir()})
	list, edge := s.Voices(context.Background())
	if !edge || len(list) != 2 || list[0].ID != "vi-VN-HoaiMyNeural" || list[1].ID != "en-US-EmmaMultilingualNeural" {
		t.Fatalf("service voices = %+v, edge=%v", list, edge)
	}
}

func TestEdgeAdapterInputErrorsAre400AndNotRetried(t *testing.T) {
	for _, tc := range []struct {
		err  error
		code string
	}{
		{fmt.Errorf("%w: %q", edgetts.ErrInvalidVoice, "VI-vn-XNeural"), "bad_voice"},
		{edgetts.ErrEmptyText, "empty_text"},
	} {
		fe := &fakeEdge{err: tc.err}
		s := NewService(ServiceOptions{Engine: FromEdge(fe), Dir: t.TempDir(), backoff: time.Millisecond})
		_, err := s.Speak(context.Background(), "abc", "VI-vn-XNeural", 0, 0)
		var te *Error
		if !errors.As(err, &te) || te.Status != http.StatusBadRequest || te.Code != tc.code {
			t.Fatalf("%v: got %#v", tc.err, err)
		}
		if n := fe.calls.Load(); n != 1 {
			t.Fatalf("%v: %d engine calls, want 1 (no retry)", tc.err, n)
		}
	}
}

func TestEdgeAdapterServiceFailureIsRetriedThen503(t *testing.T) {
	fe := &fakeEdge{err: edgetts.ErrNoAudio}
	s := NewService(ServiceOptions{Engine: FromEdge(fe), Dir: t.TempDir(), backoff: time.Millisecond})
	_, err := s.Speak(context.Background(), "abc", "vi-VN-HoaiMyNeural", 0, 0)
	var te *Error
	if !errors.As(err, &te) || te.Status != http.StatusServiceUnavailable {
		t.Fatalf("got %#v", err)
	}
	if n := fe.calls.Load(); n != attempts {
		t.Fatalf("%d engine calls, want %d", n, attempts)
	}
}
