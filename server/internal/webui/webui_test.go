package webui

import (
	"io/fs"
	"testing"
)

func TestEmbedded(t *testing.T) {
	b, err := fs.ReadFile(FS(), "index.html")
	if err != nil || len(b) == 0 {
		t.Fatalf("index.html must be embedded: %v", err)
	}
	t.Logf("placeholder UI: %v", IsPlaceholder())
}
