// Command checkversion verifies that every component carries the same product
// version: web/package.json, apps/android/package.json and the Windows
// resource file (server/cmd/mythlab/winres/winres.json, written as X.Y.Z.0).
//
//	go run ./tools/checkversion [--root ..]
//
// It exits with status 1 and lists every mismatch, so CI can gate releases.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

var semver = regexp.MustCompile(`^\d+\.\d+\.\d+$`)

// check is one place a version is declared.
type check struct {
	name string
	got  []string
}

func main() { os.Exit(run(os.Args[1:], os.Stdout, os.Stderr)) }

func run(args []string, out, errw *os.File) int {
	fl := flag.NewFlagSet("checkversion", flag.ContinueOnError)
	root := fl.String("root", "..", "repository root")
	if err := fl.Parse(args); err != nil {
		return 2
	}
	checks, err := collect(*root)
	if err != nil {
		fmt.Fprintln(errw, "checkversion:", err)
		return 2
	}
	want := ""
	bad := 0
	for _, c := range checks {
		for _, v := range c.got {
			if !semver.MatchString(v) {
				fmt.Fprintf(errw, "FAIL %s: %q is not MAJOR.MINOR.PATCH\n", c.name, v)
				bad++
				continue
			}
			if want == "" {
				want = v
			}
			if v != want {
				fmt.Fprintf(errw, "FAIL %s: %s, expected %s\n", c.name, v, want)
				bad++
			}
		}
	}
	if bad > 0 {
		return 1
	}
	fmt.Fprintf(out, "ok: %d places agree on %s\n", count(checks), want)
	return 0
}

func count(cs []check) int {
	n := 0
	for _, c := range cs {
		n += len(c.got)
	}
	return n
}

func collect(root string) ([]check, error) {
	var cs []check
	for _, p := range []string{"web/package.json", "apps/android/package.json"} {
		var pkg struct {
			Version string `json:"version"`
		}
		if err := readJSON(filepath.Join(root, p), &pkg); err != nil {
			return nil, err
		}
		cs = append(cs, check{p, []string{pkg.Version}})
	}
	b, err := os.ReadFile(filepath.Join(root, "server/cmd/mythlab/winres/winres.json"))
	if err != nil {
		return nil, err
	}
	var vs []string
	re := regexp.MustCompile(`"(?:version|file_version|product_version)"\s*:\s*"([^"]+)"`)
	for _, m := range re.FindAllStringSubmatch(string(b), -1) {
		vs = append(vs, strings.TrimSuffix(m[1], ".0")) // Windows versions are X.Y.Z.0
	}
	if len(vs) == 0 {
		return nil, fmt.Errorf("winres.json: no version fields found")
	}
	cs = append(cs, check{"server/cmd/mythlab/winres/winres.json", vs})
	return cs, nil
}

func readJSON(path string, v any) error {
	b, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	if err := json.Unmarshal(b, v); err != nil {
		return fmt.Errorf("%s: %w", path, err)
	}
	return nil
}
