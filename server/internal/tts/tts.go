// Package tts is a compatibility stub. Speech synthesis no longer runs on the
// server: voices run on the device (Piper WASM, browser or native engines).
// The types remain only so internal/app, which still wires a *Service into
// httpapi.Options, keeps compiling. Remove them together with that wiring.
package tts

// Engine is retained for source compatibility; nothing implements it any more.
type Engine interface{}

// ServiceOptions is accepted and ignored.
type ServiceOptions struct {
	Engine       Engine
	Dir          string
	DefaultVoice string
	MaxBytes     int64
	Logf         func(format string, args ...any)
}

// Service is an inert placeholder: it never synthesises anything.
type Service struct{}

// NewService returns the inert placeholder.
func NewService(ServiceOptions) *Service { return &Service{} }

// Available is always false: the server has no speech engine.
func (s *Service) Available() bool { return false }
