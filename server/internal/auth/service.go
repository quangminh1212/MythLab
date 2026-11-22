package auth

import (
	"context"
	"errors"
	"strings"
)

// TokenVerifier checks a Google ID token.
type TokenVerifier interface {
	Verify(ctx context.Context, idToken string) (*Claims, error)
}

// Service turns a Google ID token into a MythLab session.
type Service struct {
	ClientIDs []string
	Verifier  TokenVerifier
	Sessions  *Sessions
	allowed   map[string]bool
}

// NewService builds the service. allowedEmails empty = any verified account.
func NewService(clientIDs []string, v TokenVerifier, s *Sessions, allowedEmails []string) *Service {
	svc := &Service{ClientIDs: clientIDs, Verifier: v, Sessions: s, allowed: map[string]bool{}}
	for _, e := range allowedEmails {
		if e = strings.ToLower(strings.TrimSpace(e)); e != "" {
			svc.allowed[e] = true
		}
	}
	return svc
}

// ClientID is the first configured client ID.
func (s *Service) ClientID() string {
	if len(s.ClientIDs) == 0 {
		return ""
	}
	return s.ClientIDs[0]
}

// Login verifies credential and opens a session.
func (s *Service) Login(ctx context.Context, credential string) (token string, expires int64, u User, err error) {
	c, err := s.Verifier.Verify(ctx, credential)
	if err != nil {
		return "", 0, User{}, err
	}
	if len(s.allowed) > 0 && !s.allowed[strings.ToLower(c.Email)] {
		return "", 0, User{}, ErrNotAllowed
	}
	u = User{ID: c.Sub, Name: c.Name, Email: c.Email, Picture: c.Picture}
	token, expires, err = s.Sessions.Create(u)
	if err != nil {
		return "", 0, User{}, errors.New("auth: cannot create session")
	}
	return token, expires, u, nil
}
