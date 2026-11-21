package tts

import (
	"context"
	"errors"
	"net/http"

	"mythlab/internal/edgetts"
)

// EdgeClient is the part of *edgetts.Client the adapter uses.
type EdgeClient interface {
	Synthesize(ctx context.Context, text, voice string, ratePct, pitchHz int) ([]byte, error)
	Voices(ctx context.Context) ([]edgetts.Voice, error)
}

type edgeEngine struct{ c EdgeClient }

// NewEdge returns the Edge Read-Aloud engine with default options.
func NewEdge() Engine { return FromEdge(edgetts.New(edgetts.Options{})) }

// FromEdge adapts an Edge Read-Aloud client to Engine. Input the service
// would never accept (a malformed voice name, a text with nothing to speak)
// comes back as a 400 *Error, which Service does not retry.
func FromEdge(c EdgeClient) Engine { return edgeEngine{c} }

func (e edgeEngine) Synthesize(ctx context.Context, text, voice string, ratePct, pitchHz int) ([]byte, error) {
	data, err := e.c.Synthesize(ctx, text, voice, ratePct, pitchHz)
	switch {
	case errors.Is(err, edgetts.ErrInvalidVoice):
		return nil, &Error{Status: http.StatusBadRequest, Code: "bad_voice", Msg: "voice không hợp lệ"}
	case errors.Is(err, edgetts.ErrEmptyText):
		return nil, &Error{Status: http.StatusBadRequest, Code: "empty_text", Msg: "text rỗng"}
	}
	return data, err
}

func (e edgeEngine) Voices(ctx context.Context) ([]Voice, error) {
	all, err := e.c.Voices(ctx)
	if err != nil {
		return nil, err
	}
	out := make([]Voice, len(all))
	for i, v := range all {
		out[i] = Voice{ShortName: v.ShortName, Locale: v.Locale, Gender: v.Gender, FriendlyName: v.FriendlyName}
	}
	return out, nil
}
