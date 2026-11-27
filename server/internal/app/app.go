package app

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"log"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"mythlab/internal/auth"
	"mythlab/internal/covers"
	"mythlab/internal/httpapi"
	"mythlab/internal/library"
	"mythlab/internal/progress"
	"mythlab/internal/tts"
	"mythlab/internal/userlib"
	"mythlab/internal/webui"
)

// DefaultPort is the port of the console server.
const DefaultPort = 8765

// Limits of the on-disk poster cache (see covers.Store.Prune).
const (
	coverCacheBytes = 512 << 20
	coverCacheAge   = 120 * 24 * time.Hour
)

// Options configures an App. The zero value serves the discovered config on
// 127.0.0.1 with the embedded UI and without Edge voices.
type Options struct {
	Host string // listen address; "" = 127.0.0.1
	Port int    // 0 = the system picks a free port
	LAN  bool   // open to the local network: a loopback Host becomes 0.0.0.0

	ConfigPath string // config.json; "" = discovery (see Discover)
	CacheDir   string // cache root; "" = by discovery
	StaticDir  string // serve the UI from this directory instead of the embedded copy
	StaticFS   fs.FS  // UI file system used when StaticDir is empty; nil = embedded

	TTS    tts.Engine  // nil = Edge voices unavailable
	Logger *log.Logger // nil = stderr
	Hosts  []string    // extra names accepted in the Host header

	// GoogleClientIDs and AllowedEmails override config.json server.google_client_ids / allowed_emails,
	// which override $MYTHLAB_GOOGLE_CLIENT_ID / $MYTHLAB_ALLOWED_EMAILS.
	GoogleClientIDs []string
	AllowedEmails   []string
	// GoogleKeys replaces the fetch of Google signing keys (tests); nil = Google over HTTPS.
	GoogleKeys auth.KeySource
}

// App is one configured server.
type App struct {
	opt         Options
	paths       Paths
	cfg         Config
	log         *log.Logger
	lib         *library.Library
	gh          []*library.GitHubProvider
	search      *library.SearchIndex
	catalogStop context.CancelFunc
	covers      *covers.Store
	tts         *tts.Service
	progress    *progress.Store
	sessions    *auth.Sessions
	users       *userlib.Manager
	handler     *httpapi.Server

	keyMu sync.Mutex
	key   string

	closeOnce sync.Once
}

// New loads the configuration and builds the server. Nothing listens yet.
func New(o Options) (*App, error) {
	if o.Host == "" {
		o.Host = "127.0.0.1"
	}
	if o.Port < 0 || o.Port > 65535 {
		return nil, fmt.Errorf("cổng không hợp lệ: %d", o.Port)
	}
	if o.LAN && isLoopbackHost(o.Host) {
		o.Host = "0.0.0.0"
	}
	a := &App{opt: o, log: o.Logger}
	if a.log == nil {
		a.log = log.New(os.Stderr, "", 0)
	}
	var err error
	if a.paths, err = Discover(o.ConfigPath, o.CacheDir); err != nil {
		return nil, err
	}
	if a.cfg, err = LoadConfig(a.paths); err != nil {
		a.log.Printf("[config] lỗi đọc config.json: %v - dùng mặc định", err)
	}
	if err := os.MkdirAll(a.paths.Cache, 0o755); err != nil {
		return nil, fmt.Errorf("không tạo được thư mục cache: %w", err)
	}
	if a.paths.FirstRun {
		for _, l := range a.cfg.Local { // the per-user library folder exists from the first start
			os.MkdirAll(l.Path, 0o755)
		}
	}

	var static fs.FS
	switch {
	case o.StaticDir != "":
		dir, err := filepath.Abs(o.StaticDir)
		if err != nil || !isDir(dir) {
			return nil, fmt.Errorf("không thấy thư mục giao diện: %s", o.StaticDir)
		}
		static = os.DirFS(dir)
	case o.StaticFS != nil:
		static = o.StaticFS
	default:
		static = webui.FS()
	}

	var providers []library.Provider
	for _, l := range a.cfg.Local {
		providers = append(providers, library.NewLocalProvider("local"+strconv.Itoa(l.Index), l.Name, l.Path))
	}
	for _, g := range a.cfg.GitHub {
		p := library.NewGitHubProvider(library.GitHubOptions{ID: "gh" + strconv.Itoa(g.Index), Name: g.Name, Owner: g.Owner,
			Prefix: g.Prefix, CacheDir: filepath.Join(a.paths.Cache, "github"), Logf: a.log.Printf})
		a.gh = append(a.gh, p)
		providers = append(providers, p)
	}
	a.lib = library.NewLibrary(providers...)
	a.search = library.NewSearchIndex(a.lib)
	a.covers = covers.New(covers.Options{Dir: filepath.Join(a.paths.Cache, "covers"), Logf: a.log.Printf})
	go a.covers.Prune(coverCacheBytes, coverCacheAge) // keep the poster cache bounded
	a.tts = tts.NewService(tts.ServiceOptions{Engine: o.TTS, Dir: filepath.Join(a.paths.Cache, "tts"),
		DefaultVoice: a.cfg.DefaultVoice, MaxBytes: a.cfg.TTSCacheBytes, Logf: a.log.Printf})
	progDir := filepath.Dir(a.paths.Config) // progress.json lives next to config.json
	if a.paths.Config == "" {
		progDir = a.paths.Cache
	}
	a.progress = progress.Open(filepath.Join(progDir, "progress.json"), a.log.Printf)
	var authSvc *auth.Service
	if ids := a.googleClientIDs(); len(ids) > 0 {
		keys := o.GoogleKeys
		if keys == nil {
			keys = auth.NewJWKS("", nil, nil)
		}
		a.sessions = auth.OpenSessions(filepath.Join(progDir, "users.json"), a.log.Printf, nil)
		a.users = userlib.NewManager(filepath.Join(progDir, "users"), a.log.Printf)
		authSvc = auth.NewService(ids, auth.NewVerifier(ids, keys, nil), a.sessions, a.allowedEmails())
	}
	a.handler = httpapi.New(httpapi.Options{Library: a.lib, Search: a.search, Covers: a.covers, TTS: a.tts, Static: static, Progress: a.progress, Auth: authSvc, Users: a.users,
		AccessKey: func() string { return a.accessKey(a.Exposed()) }, DistrustLoopback: !a.cfg.TrustLoopback,
		Hosts: append(append([]string{}, a.cfg.Hosts...), o.Hosts...), Logf: a.log.Printf})
	a.search.RefreshAsync() // local stories and cached GitHub data; no network
	a.startCatalog()
	return a, nil
}

func isLoopbackHost(h string) bool {
	if strings.EqualFold(h, "localhost") {
		return true
	}
	ip := net.ParseIP(strings.Trim(h, "[]"))
	return ip != nil && ip.IsLoopback()
}

// Handler is the complete HTTP handler (API and UI).
func (a *App) Handler() http.Handler { return a.handler }

// Paths returns the config and cache locations in use.
func (a *App) Paths() Paths { return a.paths }

// Config returns the parsed configuration.
func (a *App) Config() Config { return a.cfg }

// Library returns the story sources.
func (a *App) Library() *library.Library { return a.lib }

// TTSAvailable reports whether Edge voices can be synthesised.
func (a *App) TTSAvailable() bool { return a.tts.Available() }

// Exposed reports whether the server is reachable from other machines, in
// which case they must present the access key.
func (a *App) Exposed() bool { return a.opt.LAN || !isLoopbackHost(a.opt.Host) }

// Addr is the configured listen address.
func (a *App) Addr() string { return net.JoinHostPort(a.opt.Host, strconv.Itoa(a.opt.Port)) }

// Close stops background work and releases the sources. The caches stay.
func (a *App) Close() {
	a.closeOnce.Do(func() {
		if a.catalogStop != nil {
			a.catalogStop()
		}
		for _, p := range a.gh {
			p.Close()
		}
		a.covers.Close()
		a.progress.Close()
		if a.sessions != nil {
			a.sessions.Close()
			a.users.Close()
		}
	})
}

// AccessKey returns the key other machines must present, creating and
// storing one on first use.
func (a *App) AccessKey() string { return a.accessKey(true) }

// accessKey: config server.access_key, else $MYTHLAB_ACCESS_KEY (containers), else <cache>/server.json, else (when
// create is set) a new random key saved there. The config file is never
// written: it may live in a public repository.
func (a *App) accessKey(create bool) string {
	if a.cfg.AccessKey != "" {
		return a.cfg.AccessKey
	}
	if k := envAccessKey(); k != "" {
		return k
	}
	a.keyMu.Lock()
	defer a.keyMu.Unlock()
	if a.key != "" {
		return a.key
	}
	file := filepath.Join(a.paths.Cache, "server.json")
	if data, err := os.ReadFile(file); err == nil {
		var v struct {
			AccessKey string `json:"access_key"`
		}
		if json.Unmarshal(data, &v) == nil && v.AccessKey != "" {
			a.key = v.AccessKey
			return a.key
		}
	}
	if !create {
		return ""
	}
	var b [18]byte
	if _, err := rand.Read(b[:]); err != nil {
		a.log.Printf("[server] không sinh được khoá truy cập: %v", err)
		return ""
	}
	a.key = base64.RawURLEncoding.EncodeToString(b[:])
	data, _ := json.Marshal(map[string]string{"access_key": a.key})
	if err := library.AtomicWrite(file, data); err != nil {
		a.log.Printf("[server] không lưu được khoá truy cập (chỉ dùng cho lần chạy này): %v", err)
	}
	return a.key
}

// RotateKey replaces the stored access key with a new random one (18 bytes
// from crypto/rand, base64url) and writes <cache>/server.json atomically. It
// returns the file written and whether config server.access_key is set, in
// which case that value still wins and must be changed by hand. The key is
// never returned or logged. A running server keeps the old key until restart.
func (a *App) RotateKey() (file string, configOverrides bool, err error) {
	var b [18]byte
	if _, err = rand.Read(b[:]); err != nil {
		return "", false, err
	}
	key := base64.RawURLEncoding.EncodeToString(b[:])
	data, _ := json.Marshal(map[string]string{"access_key": key})
	file = filepath.Join(a.paths.Cache, "server.json")
	a.keyMu.Lock()
	defer a.keyMu.Unlock()
	if err = library.AtomicWrite(file, data); err != nil {
		return file, false, err
	}
	a.key = key
	return file, a.cfg.AccessKey != "" || envAccessKey() != "", nil
}

// LANIPs lists this machine's IPv4 addresses on the local network.
func LANIPs() []string {
	set := map[string]bool{}
	if c, err := net.Dial("udp4", "10.255.255.255:1"); err == nil { // no packet is sent
		if ua, ok := c.LocalAddr().(*net.UDPAddr); ok {
			set[ua.IP.String()] = true
		}
		c.Close()
	}
	if addrs, err := net.InterfaceAddrs(); err == nil {
		for _, ad := range addrs {
			if n, ok := ad.(*net.IPNet); ok {
				if ip := n.IP.To4(); ip != nil {
					set[ip.String()] = true
				}
			}
		}
	}
	var out []string
	for ip := range set {
		if !strings.HasPrefix(ip, "127.") && !strings.HasPrefix(ip, "169.254.") && ip != "0.0.0.0" {
			out = append(out, ip)
		}
	}
	sort.Strings(out)
	return out
}

// Banner is the start-up text for a server listening on port. In exposed
// mode it contains the access key: print it to the console only.
func (a *App) Banner(port int) string {
	var b strings.Builder
	edge := "không"
	if a.TTSAvailable() {
		edge = "có"
	}
	if a.Exposed() {
		key := a.AccessKey()
		fmt.Fprintf(&b, "MythLab Reader (LAN): http://127.0.0.1:%d  (edge-tts: %s)\n", port, edge)
		fmt.Fprintf(&b, "  khoá truy cập: %s\n", key)
		for _, ip := range LANIPs() {
			fmt.Fprintf(&b, "  LAN: http://%s:%d/?k=%s\n", ip, port, key)
		}
	} else {
		fmt.Fprintf(&b, "MythLab Reader: http://%s  (edge-tts: %s)\n", net.JoinHostPort(a.opt.Host, strconv.Itoa(port)), edge)
	}
	for _, l := range a.cfg.Local {
		fmt.Fprintf(&b, "  nguồn: %s - %s\n", l.Name, l.Path)
	}
	for _, g := range a.cfg.GitHub {
		detail := g.Owner + "/" + g.Prefix + "*"
		name := g.Name
		if name == "" && g.Owner == "" {
			name = "GitHub (tôi)/" + g.Prefix + "*"
		} else if name == "" {
			name = "GitHub " + detail
		}
		fmt.Fprintf(&b, "  nguồn: %s - %s\n", name, detail)
	}
	return b.String()
}

// NewHTTPServer wraps h with the limits the reader uses: bounded headers and
// bodies, header/idle timeouts and a generous write timeout (a first GitHub
// listing or a retried synthesis can take a while).
func NewHTTPServer(h http.Handler, errLog *log.Logger) *http.Server {
	return &http.Server{
		Handler:           http.MaxBytesHandler(h, 1<<20),
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      5 * time.Minute,
		IdleTimeout:       120 * time.Second,
		MaxHeaderBytes:    128 << 10,
		ErrorLog:          errLog,
	}
}

// Listen opens the configured address.
func (a *App) Listen() (net.Listener, error) {
	return net.Listen("tcp", a.Addr())
}

// Serve answers requests on ln until ctx is cancelled, then shuts down
// gracefully (in-flight requests get ten seconds). It closes ln.
func (a *App) Serve(ctx context.Context, ln net.Listener) error {
	return Serve(ctx, ln, a.Handler(), a.log)
}

// Serve runs h on ln with the reader's server limits until ctx is cancelled.
func Serve(ctx context.Context, ln net.Listener, h http.Handler, errLog *log.Logger) error {
	base, cancelBase := context.WithCancel(context.Background())
	defer cancelBase()
	srv := NewHTTPServer(h, errLog)
	srv.BaseContext = func(net.Listener) context.Context { return base }
	done := make(chan struct{})
	stop := make(chan struct{})
	go func() {
		defer close(done)
		select {
		case <-ctx.Done():
		case <-stop:
			return
		}
		sctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		if err := srv.Shutdown(sctx); err != nil {
			cancelBase() // abort what is still running
			srv.Close()
		}
	}()
	err := srv.Serve(ln)
	close(stop)
	<-done
	if errors.Is(err, http.ErrServerClosed) {
		return nil
	}
	return err
}

// ListenAndServe is Listen followed by Serve. ready, when not nil, is called
// with the bound address before the first request is accepted.
func (a *App) ListenAndServe(ctx context.Context, ready func(net.Addr)) error {
	ln, err := a.Listen()
	if err != nil {
		return err
	}
	if ready != nil {
		ready(ln.Addr())
	}
	return a.Serve(ctx, ln)
}

// AccessKeyEnv names the environment variable that supplies the access key
// without a config file entry (container deployments); config.json wins over it.
const AccessKeyEnv = "MYTHLAB_ACCESS_KEY"

func envAccessKey() string { return strings.TrimSpace(os.Getenv(AccessKeyEnv)) }

// Environment variables for Google sign-in (config.json and flags win over them).
const (
	GoogleClientIDEnv = "MYTHLAB_GOOGLE_CLIENT_ID"
	AllowedEmailsEnv  = "MYTHLAB_ALLOWED_EMAILS"
)

// googleClientIDs: option, else config server.google_client_ids, else the environment.
func (a *App) googleClientIDs() []string {
	switch {
	case len(a.opt.GoogleClientIDs) > 0:
		return a.opt.GoogleClientIDs
	case len(a.cfg.GoogleClientIDs) > 0:
		return a.cfg.GoogleClientIDs
	}
	return splitList(os.Getenv(GoogleClientIDEnv))
}

func (a *App) allowedEmails() []string {
	switch {
	case len(a.opt.AllowedEmails) > 0:
		return a.opt.AllowedEmails
	case len(a.cfg.AllowedEmails) > 0:
		return a.cfg.AllowedEmails
	}
	return splitList(os.Getenv(AllowedEmailsEnv))
}
