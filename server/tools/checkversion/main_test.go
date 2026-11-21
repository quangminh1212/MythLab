package main

import (
	"os"
	"path/filepath"
	"testing"
)

func write(t *testing.T, root, rel, body string) {
	t.Helper()
	p := filepath.Join(root, rel)
	if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(p, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
}

func fixture(t *testing.T, web, android, win string) string {
	root := t.TempDir()
	write(t, root, "web/package.json", `{"version":"`+web+`"}`)
	write(t, root, "apps/android/package.json", `{"version":"`+android+`"}`)
	write(t, root, "server/cmd/mythlab/winres/winres.json", `{"a":{"version":"`+win+`"},"file_version":"`+win+`","product_version":"`+win+`"}`)
	return root
}

func TestRun(t *testing.T) {
	devnull, _ := os.OpenFile(os.DevNull, os.O_WRONLY, 0)
	defer devnull.Close()
	cases := []struct {
		name              string
		web, android, win string
		want              int
	}{
		{"agree", "1.2.3", "1.2.3", "1.2.3.0", 0},
		{"android differs", "1.2.3", "1.2.4", "1.2.3.0", 1},
		{"windows differs", "1.2.3", "1.2.3", "1.2.4.0", 1},
		{"not semver", "1.2", "1.2", "1.2.0", 1},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			root := fixture(t, c.web, c.android, c.win)
			if got := run([]string{"--root", root}, devnull, devnull); got != c.want {
				t.Fatalf("exit %d, want %d", got, c.want)
			}
		})
	}
	if got := run([]string{"--root", t.TempDir()}, devnull, devnull); got != 2 {
		t.Fatalf("missing files: exit %d, want 2", got)
	}
}
