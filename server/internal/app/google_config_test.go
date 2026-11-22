package app

import (
	"reflect"
	"testing"
)

func TestGoogleConfig(t *testing.T) {
	cfg, _ := ParseConfig([]byte(`{"server":{"google_client_ids":["a.apps","b.apps"],"allowed_emails":"x@y.z, Q@y.z"}}`), t.TempDir(), false)
	if !reflect.DeepEqual(cfg.GoogleClientIDs, []string{"a.apps", "b.apps"}) || !reflect.DeepEqual(cfg.AllowedEmails, []string{"x@y.z", "Q@y.z"}) {
		t.Fatalf("%+v %+v", cfg.GoogleClientIDs, cfg.AllowedEmails)
	}
	if cfg, _ := ParseConfig(nil, t.TempDir(), false); len(cfg.GoogleClientIDs) != 0 {
		t.Fatal("default must be off")
	}
}

func TestGoogleClientIDPrecedence(t *testing.T) {
	t.Setenv(GoogleClientIDEnv, "env1, env2")
	a := &App{}
	if got := a.googleClientIDs(); !reflect.DeepEqual(got, []string{"env1", "env2"}) {
		t.Fatalf("env: %v", got)
	}
	a.cfg.GoogleClientIDs = []string{"cfg"}
	if got := a.googleClientIDs(); !reflect.DeepEqual(got, []string{"cfg"}) {
		t.Fatalf("config: %v", got)
	}
	a.opt.GoogleClientIDs = []string{"flag"}
	if got := a.googleClientIDs(); !reflect.DeepEqual(got, []string{"flag"}) {
		t.Fatalf("flag: %v", got)
	}
}
