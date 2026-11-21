// Command embedui is the single place that moves the built web UI into the
// directory the Go binaries embed (server/internal/webui/dist).
//
//	go run ./tools/embedui            copy ../web/dist over internal/webui/dist
//	go run ./tools/embedui -restore   put the tracked placeholder back
//
// Every build script (apps/desktop/build.ps1, tools/build.ps1, ...) calls this
// tool, so the copy rules live here only. Run it from the server directory.
package main

import (
	"bytes"
	"flag"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

const marker = `name="mythlab-placeholder"`

func main() {
	src := flag.String("src", filepath.Join("..", "web", "dist"), "built web UI (web/dist)")
	dst := flag.String("dst", filepath.Join("internal", "webui", "dist"), "embed directory")
	keep := flag.String("placeholder", filepath.Join("internal", "webui", "placeholder.html"), "copy of the tracked placeholder page")
	restore := flag.Bool("restore", false, "restore the placeholder page instead of copying the UI")
	flag.Parse()
	if err := run(*src, *dst, *keep, *restore); err != nil {
		fmt.Fprintln(os.Stderr, "embedui:", err)
		os.Exit(1)
	}
}

func isPlaceholder(path string) bool {
	b, err := os.ReadFile(path)
	return err != nil || bytes.Contains(b, []byte(marker))
}

func run(src, dst, keep string, restore bool) error {
	dstIndex := filepath.Join(dst, "index.html")
	// Remember the placeholder the first time we see it, so -restore can bring it back.
	if _, err := os.Stat(keep); err != nil && isPlaceholder(dstIndex) {
		if b, err := os.ReadFile(dstIndex); err == nil && bytes.Contains(b, []byte(marker)) {
			if err := os.WriteFile(keep, b, 0o644); err != nil {
				return err
			}
		}
	}
	if restore {
		b, err := os.ReadFile(keep)
		if err != nil {
			return fmt.Errorf("no saved placeholder (%s): %w", keep, err)
		}
		if err := clear(dst); err != nil {
			return err
		}
		return os.WriteFile(dstIndex, b, 0o644)
	}

	index := filepath.Join(src, "index.html")
	b, err := os.ReadFile(index)
	if err != nil {
		return fmt.Errorf("%s is missing: build the UI first (cd web; npm run build)", index)
	}
	if bytes.Contains(b, []byte(marker)) {
		return fmt.Errorf("%s is a placeholder page, not a built UI", index)
	}
	if err := clear(dst); err != nil {
		return err
	}
	files, bytesTotal := 0, int64(0)
	err = filepath.WalkDir(src, func(p string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel(src, p)
		if rel == "." {
			return nil
		}
		to := filepath.Join(dst, rel)
		if d.IsDir() {
			return os.MkdirAll(to, 0o755)
		}
		if strings.EqualFold(d.Name(), "Thumbs.db") || d.Name() == ".DS_Store" {
			return nil
		}
		n, err := copyFile(p, to)
		files++
		bytesTotal += n
		return err
	})
	if err != nil {
		return err
	}
	if _, err := os.Stat(dstIndex); err != nil {
		return fmt.Errorf("copy finished without %s", dstIndex)
	}
	fmt.Printf("embedui: %s -> %s (%d files, %.1f KB)\n", src, dst, files, float64(bytesTotal)/1024)
	return nil
}

// clear empties dst but keeps the directory itself.
func clear(dst string) error {
	if err := os.MkdirAll(dst, 0o755); err != nil {
		return err
	}
	ents, err := os.ReadDir(dst)
	if err != nil {
		return err
	}
	for _, e := range ents {
		if err := os.RemoveAll(filepath.Join(dst, e.Name())); err != nil {
			return err
		}
	}
	return nil
}

func copyFile(from, to string) (int64, error) {
	in, err := os.Open(from)
	if err != nil {
		return 0, err
	}
	defer in.Close()
	if err := os.MkdirAll(filepath.Dir(to), 0o755); err != nil {
		return 0, err
	}
	out, err := os.Create(to)
	if err != nil {
		return 0, err
	}
	n, err := io.Copy(out, in)
	if cerr := out.Close(); err == nil {
		err = cerr
	}
	return n, err
}
