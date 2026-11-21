// Package tts defines the speech engine interface the HTTP layer depends on.
// The Edge Read-Aloud implementation lives in internal/edgetts.
package tts

import "context"

// Engine synthesises speech. A nil Engine means TTS is unavailable.
type Engine interface {
	// Synthesize returns MP3 bytes for text. ratePct is sent as "+N%", pitchHz as "+NHz".
	Synthesize(ctx context.Context, text, voice string, ratePct, pitchHz int) ([]byte, error)
	// Voices returns every voice the service offers (unfiltered).
	Voices(ctx context.Context) ([]Voice, error)
}

// Voice is one entry of the engine's voice list.
type Voice struct {
	ShortName, Locale, Gender, FriendlyName string
}
