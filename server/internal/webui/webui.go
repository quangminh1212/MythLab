// Package webui carries the built web UI inside the binary.
//
// The dist directory is a build product: the web stage's output (web/dist) is
// copied over it before `go build`. Only a placeholder index.html is tracked
// in git so that the package always compiles.
package webui

import (
	"bytes"
	"embed"
	"io/fs"
)

//go:embed all:dist
var dist embed.FS

// FS returns the embedded UI with index.html at its root.
func FS() fs.FS {
	sub, err := fs.Sub(dist, "dist")
	if err != nil {
		panic(err) // the directory is embedded at build time
	}
	return sub
}

// IsPlaceholder reports whether the binary was built without the real UI.
func IsPlaceholder() bool {
	b, err := fs.ReadFile(FS(), "index.html")
	return err != nil || bytes.Contains(b, []byte(`name="mythlab-placeholder"`))
}
