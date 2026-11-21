//go:build windows

package main

import (
	"bytes"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

const (
	appTitle = "MythLab Truyện"

	// preferredPort keeps the origin http://127.0.0.1:18765 stable: the
	// WebView2 profile stores reading progress and settings per origin.
	preferredPort = 18765

	defaultWidth, defaultHeight = 1200, 820
	minWidth, minHeight         = 420, 600

	maxLogBytes = 4 << 20
)

// dirs are the per-user locations of the desktop app.
type dirs struct {
	local    string // %LOCALAPPDATA%\MythLab: webview profile, log
	roaming  string // %APPDATA%\MythLab: window.json
	override bool   // --data-dir / MYTHLAB_DATA_DIR: everything in one folder
}

func (d dirs) webview() string    { return filepath.Join(d.local, "webview") }
func (d dirs) edgeApp() string    { return filepath.Join(d.local, "edge-app") }
func (d dirs) logFile() string    { return filepath.Join(d.local, "desktop.log") }
func (d dirs) windowFile() string { return filepath.Join(d.roaming, "window.json") }

// resolveDirs returns the standard locations, or dataDir for all of them.
func resolveDirs(dataDir string) (dirs, error) {
	if dataDir != "" {
		abs, err := filepath.Abs(dataDir)
		if err != nil {
			return dirs{}, err
		}
		return dirs{local: abs, roaming: abs, override: true}, nil
	}
	local, err := os.UserCacheDir() // %LOCALAPPDATA%
	if err != nil {
		return dirs{}, err
	}
	roaming, err := os.UserConfigDir() // %APPDATA%
	if err != nil {
		return dirs{}, err
	}
	return dirs{local: filepath.Join(local, "MythLab"), roaming: filepath.Join(roaming, "MythLab")}, nil
}

// instanceName is the base name of the kernel objects and the window property
// that identify one running desktop app. A relocated data directory is its own
// instance, so a test run never meets the installed app.
func instanceName(d dirs) string {
	if !d.override {
		return "MythLab.Desktop"
	}
	h := sha1.Sum([]byte(strings.ToLower(filepath.Clean(d.local))))
	return "MythLab.Desktop." + hex.EncodeToString(h[:6])
}

// winState is window.json. Sizes are outer window sizes at 96 DPI.
type winState struct {
	Width     int  `json:"width"`
	Height    int  `json:"height"`
	Maximized bool `json:"maximized,omitempty"`
}

func clampState(s winState) winState {
	if s.Width < minWidth {
		s.Width = minWidth
	}
	if s.Height < minHeight {
		s.Height = minHeight
	}
	if s.Width > 16384 {
		s.Width = 16384
	}
	if s.Height > 16384 {
		s.Height = 16384
	}
	return s
}

// loadWinState reads window.json; anything unreadable gives the default size.
func loadWinState(file string) winState {
	def := winState{Width: defaultWidth, Height: defaultHeight}
	data, err := os.ReadFile(file)
	if err != nil {
		return def
	}
	// the old app wrote plain numbers; accept floats as well
	var raw struct {
		Width     *float64 `json:"width"`
		Height    *float64 `json:"height"`
		Maximized bool     `json:"maximized"`
	}
	if json.Unmarshal(bytes.TrimPrefix(data, []byte("\xef\xbb\xbf")), &raw) != nil || raw.Width == nil || raw.Height == nil {
		return def
	}
	w, h := *raw.Width, *raw.Height
	if !(w > 0 && w < 1e6) || !(h > 0 && h < 1e6) { // also rejects NaN
		return def
	}
	return clampState(winState{Width: int(w), Height: int(h), Maximized: raw.Maximized})
}

// saveWinState writes window.json atomically.
func saveWinState(file string, s winState) error {
	data, err := json.Marshal(clampState(s))
	if err != nil {
		return err
	}
	return writeFileAtomic(file, data)
}

func writeFileAtomic(file string, data []byte) error {
	if err := os.MkdirAll(filepath.Dir(file), 0o755); err != nil {
		return err
	}
	tmp := fmt.Sprintf("%s.%d.tmp", file, os.Getpid())
	if err := os.WriteFile(tmp, data, 0o644); err != nil {
		os.Remove(tmp)
		return err
	}
	if err := os.Rename(tmp, file); err != nil {
		os.Remove(tmp)
		return err
	}
	return nil
}

// scale converts a 96-DPI length to pixels at dpi; unscale is the inverse.
func scale(v, dpi int) int   { return (v*dpi + 48) / 96 }
func unscale(v, dpi int) int { return (v*96 + dpi/2) / dpi }

// logSink is the log file. It is safe for concurrent use and tells the app
// when the WebView2 library is about to end the process (it reports a failed
// environment or controller with log.Fatalf).
type logSink struct {
	mu      sync.Mutex
	f       *os.File
	onFatal func(msg string) // called without the lock, on the writing goroutine
}

// webviewFatal are the messages go-webview2 logs right before os.Exit(1).
var webviewFatal = [][]byte{[]byte("Creating environment failed"), []byte("Creating controller failed")}

// openLog opens (and when it grew too large, rotates) the log file.
func openLog(file string) (*logSink, error) {
	if err := os.MkdirAll(filepath.Dir(file), 0o755); err != nil {
		return nil, err
	}
	if st, err := os.Stat(file); err == nil && st.Size() > maxLogBytes {
		os.Remove(file + ".1")
		os.Rename(file, file+".1")
	}
	f, err := os.OpenFile(file, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
	if err != nil {
		return nil, err
	}
	return &logSink{f: f}, nil
}

func (s *logSink) Write(p []byte) (int, error) {
	s.mu.Lock()
	n, err := s.f.Write(p)
	hook := s.onFatal
	s.mu.Unlock()
	if hook != nil {
		for _, pat := range webviewFatal {
			if bytes.Contains(p, pat) {
				hook(strings.TrimSpace(string(p)))
				break
			}
		}
	}
	return n, err
}

func (s *logSink) setFatalHook(f func(string)) {
	s.mu.Lock()
	s.onFatal = f
	s.mu.Unlock()
}

// logf writes one time-stamped line of the desktop shell.
func (s *logSink) logf(format string, args ...any) {
	line := time.Now().Format("2006-01-02 15:04:05") + " [desktop] " + fmt.Sprintf(format, args...) + "\n"
	s.mu.Lock()
	s.f.WriteString(line)
	s.mu.Unlock()
}

func (s *logSink) file() *os.File { return s.f }
