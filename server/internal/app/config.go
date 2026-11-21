// Package app assembles the MythLab reader server: configuration, story
// sources, caches, the HTTP handler and the listener helpers shared by the
// console server and the desktop app.
package app

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// LocalSource is one entry of config "local".
type LocalSource struct {
	Index int // position in the config array: the source id is local<Index>
	Name  string
	Path  string // absolute
}

// GitHubSource is one enabled entry of config "github".
type GitHubSource struct {
	Index  int // the source id is gh<Index>
	Name   string
	Owner  string
	Prefix string
}

// Config is the parsed config.json.
type Config struct {
	Local  []LocalSource
	GitHub []GitHubSource

	DefaultVoice  string // tts.default_voice
	TTSCacheBytes int64  // tts.cache_max_mb in bytes; 0 = default, <0 = unlimited

	AccessKey     string   // server.access_key
	Hosts         []string // server.hosts: extra names accepted in the Host header
	TrustLoopback bool     // server.trust_loopback (default true)
}

// Paths says where the server keeps its files.
type Paths struct {
	Config   string // config.json (may not exist)
	Base     string // directory relative local paths resolve against
	Cache    string // cache root
	FirstRun bool   // per-user location without a config file yet
}

const defaultConfigJSON = `{
  "local": [{"name": "MythLab", "path": ".."}, {"name": "Thư viện (library/)", "path": "library"}],
  "github": [{"owner": "", "prefix": "Done_"}],
  "tts": {"default_voice": "vi-VN-HoaiMyNeural"}
}`

const firstRunLocalJSON = `[{"name": "Thư viện (library/)", "path": "library"}]`

func userDirs() (config, cache string) {
	cfg, err := os.UserConfigDir() // %APPDATA% on Windows
	if err != nil || cfg == "" {
		cfg = "."
	}
	cch, err := os.UserCacheDir() // %LOCALAPPDATA% on Windows
	if err != nil || cch == "" {
		cch = cfg
	}
	return filepath.Join(cfg, "MythLab"), filepath.Join(cch, "MythLab", "cache")
}

func isFile(p string) bool {
	st, err := os.Stat(p)
	return err == nil && st.Mode().IsRegular()
}

func isDir(p string) bool {
	st, err := os.Stat(p)
	return err == nil && st.IsDir()
}

// Discover locates the config file and the cache directory.
//
// Without configFlag: config.json beside the executable; else the per-user
// config.json (%APPDATA%\MythLab); else the nearest reader/config.json walking
// up from the executable's directory, then from the working directory
// (repository mode, cache reader/.cache); else the per-user location (first run). cacheFlag overrides the
// cache directory in every case.
func Discover(configFlag, cacheFlag string) (Paths, error) {
	exe, _ := os.Executable()
	cwd, _ := os.Getwd()
	return discover(configFlag, cacheFlag, filepath.Dir(exe), cwd)
}

// findRepoConfig returns the nearest reader/config.json walking up from dir, or "".
func findRepoConfig(dir string) string {
	if dir == "" || dir == "." {
		return ""
	}
	for {
		if c := filepath.Join(dir, "reader", "config.json"); isFile(c) {
			return c
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return ""
		}
		dir = parent
	}
}

func discover(configFlag, cacheFlag, exeDir, cwd string) (Paths, error) {
	userCfg, userCache := userDirs()
	var p Paths
	switch {
	case configFlag != "":
		abs, err := filepath.Abs(configFlag)
		if err != nil {
			return p, err
		}
		if !isFile(abs) {
			return p, fmt.Errorf("không thấy file cấu hình: %s", abs)
		}
		p.Config, p.Base, p.Cache = abs, filepath.Dir(abs), userCache
		// a repository checkout keeps its cache next to the config
		if strings.EqualFold(filepath.Base(p.Base), "reader") || isDir(filepath.Join(p.Base, ".cache")) {
			p.Cache = filepath.Join(p.Base, ".cache")
		}
	case exeDir != "" && exeDir != "." && isFile(filepath.Join(exeDir, "config.json")):
		p.Config, p.Base, p.Cache = filepath.Join(exeDir, "config.json"), exeDir, userCache
	case isFile(filepath.Join(userCfg, "config.json")):
		p.Config, p.Base, p.Cache = filepath.Join(userCfg, "config.json"), userCfg, userCache
	default:
		// repository mode: the checkout around the executable first, then around the working directory
		for _, start := range []string{exeDir, cwd} {
			if p.Config = findRepoConfig(start); p.Config != "" {
				p.Base = filepath.Dir(p.Config)
				p.Cache = filepath.Join(p.Base, ".cache")
				break
			}
		}
		if p.Config == "" {
			p.Config, p.Base, p.Cache = filepath.Join(userCfg, "config.json"), userCfg, userCache
			p.FirstRun = true
		}
	}
	if cacheFlag != "" {
		abs, err := filepath.Abs(cacheFlag)
		if err != nil {
			return p, err
		}
		p.Cache = abs
	}
	return p, nil
}

func asString(r json.RawMessage) string {
	var s string
	if json.Unmarshal(r, &s) == nil {
		return s
	}
	var n json.Number
	if json.Unmarshal(r, &n) == nil {
		return n.String()
	}
	return ""
}

func asObject(r json.RawMessage) map[string]json.RawMessage {
	var m map[string]json.RawMessage
	if json.Unmarshal(r, &m) != nil {
		return nil
	}
	return m
}

// asList accepts an array of objects or a single object.
func asList(r json.RawMessage) []json.RawMessage {
	var arr []json.RawMessage
	if json.Unmarshal(r, &arr) == nil {
		return arr
	}
	if asObject(r) != nil {
		return []json.RawMessage{r}
	}
	return nil
}

func decodeObject(data []byte) (map[string]json.RawMessage, error) {
	data = bytes.TrimPrefix(data, []byte("\xef\xbb\xbf"))
	var m map[string]json.RawMessage
	if err := json.Unmarshal(data, &m); err != nil {
		return nil, err
	}
	if m == nil {
		return nil, errors.New("config.json phải là một object JSON")
	}
	return m, nil
}

// ParseConfig merges data (nil = no file) over the defaults, top-level key by
// top-level key like the old server, and resolves relative local paths
// against base. A broken entry is skipped; it never fails the others.
func ParseConfig(data []byte, base string, firstRun bool) (Config, error) {
	raw, _ := decodeObject([]byte(defaultConfigJSON))
	var perr error
	if data != nil {
		user, err := decodeObject(data)
		if err != nil {
			perr = err // the defaults are used, as before
		}
		for k, v := range user {
			raw[k] = v
		}
	}
	if firstRun {
		raw["local"] = json.RawMessage(firstRunLocalJSON)
	}
	cfg := Config{TrustLoopback: true}
	for i, it := range asList(raw["local"]) {
		m := asObject(it)
		path := asString(m["path"])
		if m == nil || path == "" {
			continue
		}
		if !filepath.IsAbs(path) {
			path = filepath.Join(base, path)
		}
		if abs, err := filepath.Abs(path); err == nil {
			path = abs
		}
		name := asString(m["name"])
		if name == "" {
			name = filepath.Base(path)
		}
		cfg.Local = append(cfg.Local, LocalSource{Index: i, Name: name, Path: path})
	}
	for i, it := range asList(raw["github"]) {
		m := asObject(it)
		if m == nil {
			continue
		}
		if e, ok := m["enabled"]; ok {
			var on bool
			if json.Unmarshal(e, &on) == nil && !on {
				continue
			}
		}
		prefix := "Done_"
		if _, ok := m["prefix"]; ok {
			prefix = asString(m["prefix"])
		}
		cfg.GitHub = append(cfg.GitHub, GitHubSource{Index: i, Name: asString(m["name"]), Owner: strings.TrimSpace(asString(m["owner"])), Prefix: prefix})
	}
	if t := asObject(raw["tts"]); t != nil {
		cfg.DefaultVoice = asString(t["default_voice"])
		var mb float64
		if json.Unmarshal(t["cache_max_mb"], &mb) == nil && mb != 0 {
			if mb < 0 {
				cfg.TTSCacheBytes = -1
			} else {
				cfg.TTSCacheBytes = int64(mb * (1 << 20))
			}
		}
	}
	if s := asObject(raw["server"]); s != nil {
		cfg.AccessKey = asString(s["access_key"])
		var hosts []string
		if json.Unmarshal(s["hosts"], &hosts) == nil {
			cfg.Hosts = hosts
		}
		var trust bool
		if json.Unmarshal(s["trust_loopback"], &trust) == nil {
			cfg.TrustLoopback = trust
		}
	}
	return cfg, perr
}

// LoadConfig reads the config file of p. A missing file gives the defaults; a
// broken one gives the defaults plus the error (for the log).
func LoadConfig(p Paths) (Config, error) {
	data, err := os.ReadFile(p.Config)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return ParseConfig(nil, p.Base, p.FirstRun)
		}
		cfg, _ := ParseConfig(nil, p.Base, p.FirstRun)
		return cfg, err
	}
	return ParseConfig(data, p.Base, false)
}
