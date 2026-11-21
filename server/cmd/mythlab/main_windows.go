//go:build windows

// Command mythlab is the MythLab desktop app for Windows: the reader server
// on 127.0.0.1 plus a WebView2 window showing its UI.
//
//	MythLab.exe [--port N] [--port-file FILE] [--no-window] [--data-dir DIR]
//	            [--config FILE] [--cache DIR] [--static DIR] [--no-tts] [--debug] [--quit]
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"runtime/debug"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	webview2 "github.com/jchv/go-webview2"
	"github.com/jchv/go-webview2/webviewloader"
	"golang.org/x/sys/windows"
	"golang.org/x/sys/windows/registry"

	"mythlab/internal/app"
	"mythlab/internal/tts"
	"mythlab/internal/webui"
)

// The window and its message loop must stay on the thread that starts main.
func init() { runtime.LockOSThread() }

func main() { os.Exit(run(os.Args[1:])) }

const (
	exitOK      = 0
	exitError   = 1
	exitUsage   = 2
	exitRunning = 3 // --no-window while another instance owns the profile

	webview2Page = "https://developer.microsoft.com/microsoft-edge/webview2/"
)

type options struct {
	port     int
	portSet  bool
	portFile string
	noWindow bool
	dataDir  string
	config   string
	cache    string
	static   string
	noTTS    bool
	debug    bool
	quit     bool
}

// parseArgs reads the command line. usage is set when help text should be
// shown (with err nil for --help).
func parseArgs(args []string) (opt options, usage string, err error) {
	var out bytes.Buffer
	fl := flag.NewFlagSet("MythLab", flag.ContinueOnError)
	fl.SetOutput(&out)
	fl.IntVar(&opt.port, "port", preferredPort, "cổng của server trong máy (bận thì báo lỗi)")
	fl.StringVar(&opt.portFile, "port-file", "", "ghi cổng đang chạy vào file này")
	fl.BoolVar(&opt.noWindow, "no-window", false, "chỉ chạy server, không mở cửa sổ")
	fl.StringVar(&opt.dataDir, "data-dir", "", "thư mục chứa hồ sơ WebView2, window.json và log (mặc định: thư mục người dùng; biến MYTHLAB_DATA_DIR)")
	fl.StringVar(&opt.config, "config", "", "file config.json (mặc định: tự tìm)")
	fl.StringVar(&opt.cache, "cache", "", "thư mục cache (mặc định: theo vị trí config)")
	fl.StringVar(&opt.static, "static", "", "lấy giao diện từ thư mục này thay cho bản nhúng")
	fl.BoolVar(&opt.noTTS, "no-tts", false, "tắt giọng đọc Edge")
	fl.BoolVar(&opt.debug, "debug", false, "bật DevTools và menu chuột phải của WebView2")
	fl.BoolVar(&opt.quit, "quit", false, "yêu cầu MythLab đang chạy thoát")
	err = fl.Parse(args)
	if errors.Is(err, flag.ErrHelp) {
		return opt, out.String(), nil
	}
	if err == nil && fl.NArg() > 0 {
		err = fmt.Errorf("tham số thừa: %s", strings.Join(fl.Args(), " "))
	}
	if err == nil {
		fl.Visit(func(f *flag.Flag) {
			if f.Name == "port" {
				opt.portSet = true
			}
		})
		if opt.port < 1 || opt.port > 65535 {
			err = fmt.Errorf("cổng không hợp lệ: %d", opt.port)
		}
	}
	if err != nil {
		out.Reset()
		fl.PrintDefaults()
		return opt, out.String(), err
	}
	if opt.dataDir == "" {
		opt.dataDir = os.Getenv("MYTHLAB_DATA_DIR")
	}
	return opt, "", nil
}

const (
	modeStarting int32 = iota
	modeHeadless
	modeWindow
	modeFallback
)

type desktop struct {
	opt  options
	dirs dirs
	name string
	log  *logSink

	app    *app.App
	url    string
	cancel context.CancelFunc
	done   chan struct{} // closed when the HTTP server has stopped
	stop   sync.Once

	mode  atomic.Int32
	quit  atomic.Bool
	hwnd  atomic.Uintptr
	loads atomic.Int32

	prevProc uintptr // window procedure of the WebView2 host window
	state    winState
	dpi      int
}

func run(args []string) int {
	opt, usage, err := parseArgs(args)
	if err != nil {
		messageBox(0, err.Error()+"\n\n"+usage, mbOK|mbIconError)
		return exitUsage
	}
	if usage != "" {
		messageBox(0, "MythLab.exe [tham số]\n\n"+usage, mbOK|mbIconInfo)
		return exitOK
	}
	dd, err := resolveDirs(opt.dataDir)
	if err != nil {
		messageBox(0, "Không xác định được thư mục dữ liệu: "+err.Error(), mbOK|mbIconError)
		return exitError
	}
	name := instanceName(dd)
	if opt.quit {
		return requestQuit(name)
	}
	sink, err := openLog(dd.logFile())
	if err != nil {
		messageBox(0, "Không mở được file log:\n"+err.Error(), mbOK|mbIconError)
		return exitError
	}
	debug.SetCrashOutput(sink.file(), debug.CrashOptions{}) // a windowed exe has no stderr
	log.SetOutput(sink)                                     // libraries using the standard logger
	d := &desktop{opt: opt, dirs: dd, name: name, log: sink, done: make(chan struct{})}
	defer func() {
		if v := recover(); v != nil {
			sink.logf("panic: %v\n%s", v, debug.Stack())
			d.shutdown()
			os.Exit(exitError)
		}
	}()
	return d.run()
}

// requestQuit asks the running instance to exit.
func requestQuit(name string) int {
	ev, err := windows.OpenEvent(windows.EVENT_MODIFY_STATE, false, utf16(`Local\`+name+".quit"))
	if err != nil {
		return exitError // nothing is running
	}
	defer windows.CloseHandle(ev)
	if windows.SetEvent(ev) != nil {
		return exitError
	}
	return exitOK
}

func (d *desktop) run() int {
	// One instance per profile: a second server would land on another port,
	// that is another origin with empty storage.
	mutex, err := windows.CreateMutex(nil, false, utf16(`Local\`+d.name))
	if errors.Is(err, windows.ERROR_ALREADY_EXISTS) {
		if mutex != 0 {
			windows.CloseHandle(mutex)
		}
		return d.secondInstance()
	}
	if err != nil {
		d.log.logf("không tạo được mutex: %v", err) // keep going: better two instances than none
	} else {
		defer windows.CloseHandle(mutex)
	}
	exe, _ := os.Executable()
	d.log.logf("khởi động %s (pid %d)", filepath.Base(exe), os.Getpid())

	if ev, err := windows.CreateEvent(nil, 1, 0, utf16(`Local\`+d.name+".quit")); err == nil {
		go func() {
			if s, _ := windows.WaitForSingleObject(ev, windows.INFINITE); s == windows.WAIT_OBJECT_0 {
				d.onQuitRequest()
			}
		}()
	} else {
		d.log.logf("không tạo được sự kiện thoát: %v", err)
	}

	ln, fellBack, err := listenLoopback(d.opt.port, d.opt.portSet)
	if err != nil {
		d.log.logf("không mở được cổng %d: %v", d.opt.port, err)
		d.alert(fmt.Sprintf("Không mở được cổng %d:\n%v\n\nHãy đóng chương trình đang dùng cổng này rồi mở lại MythLab.", d.opt.port, err), mbIconError)
		return exitError
	}
	port := ln.Addr().(*net.TCPAddr).Port
	if fellBack {
		other := "một chương trình khác"
		if mythlabAt(d.opt.port) {
			other = "một bản MythLab khác (bản cũ?)"
		}
		d.log.logf("CẢNH BÁO: cổng %d đang do %s dùng; chạy tạm ở cổng %d - tiến độ đọc và cài đặt của lần này nằm riêng", d.opt.port, other, port)
		if !d.opt.noWindow {
			text := fmt.Sprintf("Cổng %d đang do %s dùng.\n\nMythLab có thể chạy tạm ở cổng %d, nhưng tiến độ đọc và cài đặt đã lưu sẽ không hiện ra "+
				"(chúng gắn với cổng %d), và những gì đọc lần này được lưu riêng.\n\nNên bấm Cancel, đóng chương trình kia rồi mở lại MythLab.\n\nVẫn chạy tạm?",
				d.opt.port, other, port, d.opt.port)
			if messageBox(0, text, mbOKCancel|mbIconWarning) != idOK {
				ln.Close()
				d.log.logf("người dùng huỷ")
				return exitOK
			}
		}
	}

	var engine tts.Engine
	if !d.opt.noTTS {
		engine = tts.NewEdge()
	}
	a, err := app.New(app.Options{Host: "127.0.0.1", Port: port, ConfigPath: d.opt.config, CacheDir: d.opt.cache,
		StaticDir: d.opt.static, TTS: engine, Logger: log.New(d.log, "", 0)})
	if err != nil {
		ln.Close()
		d.log.logf("không khởi động được server: %v", err)
		d.alert("Không khởi động được MythLab:\n"+err.Error(), mbIconError)
		return exitError
	}
	d.app = a
	d.url = fmt.Sprintf("http://127.0.0.1:%d/", port)
	if d.opt.static == "" && webui.IsPlaceholder() {
		d.log.logf("CẢNH BÁO: bản dựng này chưa nhúng giao diện (chạy apps\\desktop\\build.ps1)")
	}
	ctx, cancel := context.WithCancel(context.Background())
	d.cancel = cancel
	var serveErr error
	go func() {
		defer close(d.done)
		serveErr = a.Serve(ctx, ln)
	}()
	edge := "không"
	if a.TTSAvailable() {
		edge = "có"
	}
	p := a.Paths()
	d.log.logf("MythLab desktop: %s  (edge-tts: %s; config: %s; cache: %s)", d.url, edge, p.Config, p.Cache)
	if d.opt.portFile != "" {
		if err := writeFileAtomic(d.opt.portFile, []byte(strconv.Itoa(port))); err != nil {
			d.log.logf("không ghi được --port-file: %v", err)
		}
	}

	if d.opt.noWindow {
		d.mode.Store(modeHeadless)
		if d.quit.Load() {
			cancel()
		}
		<-d.done
		d.shutdown()
		if serveErr != nil {
			d.log.logf("server dừng vì lỗi: %v", serveErr)
			return exitError
		}
		return exitOK
	}
	return d.runWindow()
}

// alert shows a message box unless the app runs without a window.
func (d *desktop) alert(text string, icon uintptr) {
	if !d.opt.noWindow {
		messageBox(0, text, mbOK|icon)
	}
}

// listenLoopback opens 127.0.0.1:port. When the port is taken and it was not
// asked for explicitly, the system picks another one (fellBack).
func listenLoopback(port int, explicit bool) (ln net.Listener, fellBack bool, err error) {
	ln, err = net.Listen("tcp4", net.JoinHostPort("127.0.0.1", strconv.Itoa(port)))
	if err == nil || explicit {
		return ln, false, err
	}
	ln, err2 := net.Listen("tcp4", "127.0.0.1:0")
	if err2 != nil {
		return nil, false, err
	}
	return ln, true, nil
}

// mythlabAt reports whether a MythLab server answers on the local port.
func mythlabAt(port int) bool {
	c := &http.Client{Timeout: 1500 * time.Millisecond}
	resp, err := c.Get(fmt.Sprintf("http://127.0.0.1:%d/api/ping", port))
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	var v struct {
		App string `json:"app"`
	}
	return json.NewDecoder(http.MaxBytesReader(nil, resp.Body, 4096)).Decode(&v) == nil && v.App == "mythlab"
}

// secondInstance runs when another process already owns the profile: it
// brings that window to the front and exits.
func (d *desktop) secondInstance() int {
	if d.opt.noWindow {
		d.log.logf("đã có MythLab đang chạy với hồ sơ này - không mở server thứ hai (pid %d thoát)", os.Getpid())
		return exitRunning
	}
	for i := 0; i < 50; i++ { // the first instance may still be creating its window
		if hwnd := findWindowWithProp(d.name); hwnd != 0 {
			ok := activateWindow(hwnd)
			d.log.logf("đã có MythLab đang chạy - chuyển sang cửa sổ đó (đưa lên trước: %v; pid %d thoát)", ok, os.Getpid())
			return exitOK
		}
		time.Sleep(100 * time.Millisecond)
	}
	d.log.logf("đã có MythLab đang chạy nhưng không thấy cửa sổ (pid %d thoát)", os.Getpid())
	messageBox(0, "MythLab đang chạy sẵn nhưng không có cửa sổ riêng.\n\nNếu đang đọc trong trình duyệt, hãy chuyển sang cửa sổ đó.", mbOK|mbIconInfo)
	return exitOK
}

// onQuitRequest handles "MythLab.exe --quit" from another process.
func (d *desktop) onQuitRequest() {
	d.quit.Store(true)
	d.log.logf("nhận yêu cầu thoát")
	if hwnd := d.hwnd.Load(); hwnd != 0 {
		postClose(hwnd) // the normal close path saves the window size
		return
	}
	switch d.mode.Load() {
	case modeHeadless:
		d.cancel()
	case modeFallback: // the main thread sits in a message box or waits for the browser
		d.shutdown()
		os.Exit(exitOK)
	}
	// modeStarting / modeWindow without a window yet: the main thread checks d.quit
}

// shutdown stops the HTTP server gracefully and releases the sources.
func (d *desktop) shutdown() {
	d.stop.Do(func() {
		if d.cancel != nil {
			d.cancel()
			select {
			case <-d.done:
			case <-time.After(15 * time.Second):
				d.log.logf("server chưa dừng sau 15 giây")
			}
		}
		if d.app != nil {
			d.app.Close()
		}
		d.log.logf("đã thoát (pid %d)", os.Getpid())
	})
}

func (d *desktop) runWindow() int {
	d.mode.Store(modeWindow)
	ver, err := webviewloader.GetInstalledVersion()
	if err != nil {
		return d.fallback(fmt.Sprintf("không kiểm tra được WebView2 Runtime: %v", err))
	}
	if ver == "" {
		return d.fallback("máy chưa có WebView2 Runtime")
	}
	profile := d.dirs.webview()
	if err := os.MkdirAll(profile, 0o755); err != nil {
		return d.fallback(fmt.Sprintf("không tạo được thư mục hồ sơ %s: %v", profile, err))
	}
	d.log.logf("WebView2 Runtime %s; hồ sơ: %s", ver, profile)

	d.state = loadWinState(d.dirs.windowFile())
	d.dpi = systemDPI()
	w, h := scale(d.state.Width, d.dpi), scale(d.state.Height, d.dpi)
	if sw, sh := primaryScreen(); sw > 0 && sh > 0 { // the library centres with unsigned arithmetic
		w, h = min(w, sw), min(h, sh)
	}

	// go-webview2 reports a failed environment or controller with log.Fatalf;
	// the hook turns that into the browser fallback instead of a silent exit.
	d.log.setFatalHook(func(msg string) {
		d.log.setFatalHook(nil)
		hideStrayWindows()
		os.Exit(d.fallback(msg))
	})
	wv := webview2.NewWithOptions(webview2.WebViewOptions{
		Debug:     d.opt.debug,
		DataPath:  profile,
		AutoFocus: true,
		WindowOptions: webview2.WindowOptions{
			Title: appTitle, Width: uint(w), Height: uint(h), IconId: 1, Center: true,
		},
	})
	d.log.setFatalHook(nil)
	if wv == nil {
		hideStrayWindows()
		return d.fallback("không khởi tạo được WebView2")
	}
	hwnd := uintptr(wv.Window())
	setProp(hwnd, d.name) // lets a second launch find this window
	d.prevProc = subclass(hwnd, d.wndProc)
	if wdpi := windowDPI(hwnd); wdpi != d.dpi { // opened on a monitor with another scale
		d.dpi = wdpi
		resizeWindow(hwnd, scale(d.state.Width, wdpi), scale(d.state.Height, wdpi))
	}
	if d.state.Maximized {
		showMaximized(hwnd)
	}
	d.hwnd.Store(hwnd)

	if err := wv.Bind("__mythlabLoaded", d.onLoaded); err != nil {
		d.log.logf("không gắn được hàm báo tải trang: %v", err)
	}
	wv.Init(`window.addEventListener("DOMContentLoaded",function(){try{window.__mythlabLoaded(String(location.href))}catch(e){}});`)
	wv.Navigate(d.url)
	d.log.logf("WebView2 đã khởi tạo; cửa sổ %dx%d (DPI %d); mở %s", d.state.Width, d.state.Height, d.dpi, d.url)
	if d.quit.Load() {
		postClose(hwnd)
	}
	wv.Run()

	d.hwnd.Store(0)
	d.saveState()
	d.shutdown()
	return exitOK
}

// hideStrayWindows hides host windows left behind by a failed WebView2 start.
// They are hidden, not destroyed: destroying one posts WM_QUIT, which would
// dismiss the message box that follows.
func hideStrayWindows() {
	for _, h := range threadWindows("webview") {
		hideWindow(h)
	}
}

// onLoaded is called by the page on DOMContentLoaded (UI thread).
func (d *desktop) onLoaded(href string) {
	if d.loads.Add(1) > 20 {
		return
	}
	if u, err := url.Parse(href); err == nil {
		u.RawQuery, u.User = "", nil
		href = u.String()
	}
	if len(href) > 300 {
		href = href[:300]
	}
	d.log.logf("WebView2 đã tải trang %s", strconv.QuoteToGraphic(href))
}

// wndProc sits in front of the library's window procedure.
func (d *desktop) wndProc(hwnd, msg, wp, lp uintptr) uintptr {
	switch msg {
	case wmClose:
		d.captureState(hwnd)
		removeProp(hwnd, d.name)
	case wmEndSession:
		if wp != 0 { // the session really ends: there is little time
			d.captureState(hwnd)
			d.saveState()
			d.shutdown()
		}
	case wmGetMinMaxInfo:
		r := callWindowProc(d.prevProc, hwnd, msg, wp, lp)
		mmi := (*minMaxInfo)(ptr(lp))
		dpi := windowDPI(hwnd)
		mmi.PtMinTrackSize = point{int32(scale(minWidth, dpi)), int32(scale(minHeight, dpi))}
		return r
	case wmDpiChanged:
		d.dpi = int(wp & 0xFFFF)
		moveWindow(hwnd, *(*rect)(ptr(lp))) // the size Windows suggests for the new scale
		return 0
	}
	return callWindowProc(d.prevProc, hwnd, msg, wp, lp)
}

// captureState remembers the window size while the window still exists.
func (d *desktop) captureState(hwnd uintptr) {
	w, h, maximized, ok := placement(hwnd)
	if !ok || w <= 0 || h <= 0 {
		return
	}
	dpi := windowDPI(hwnd)
	d.state = clampState(winState{Width: unscale(w, dpi), Height: unscale(h, dpi), Maximized: maximized})
}

func (d *desktop) saveState() {
	if err := saveWinState(d.dirs.windowFile(), d.state); err != nil {
		d.log.logf("không lưu được kích thước cửa sổ: %v", err)
		return
	}
	d.log.logf("đã lưu kích thước cửa sổ %dx%d (phóng to: %v)", d.state.Width, d.state.Height, d.state.Maximized)
}

// findEdge locates msedge.exe.
func findEdge() string {
	for _, root := range []registry.Key{registry.CURRENT_USER, registry.LOCAL_MACHINE} {
		k, err := registry.OpenKey(root, `SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe`, registry.QUERY_VALUE)
		if err != nil {
			continue
		}
		p, _, err := k.GetStringValue("")
		k.Close()
		if p = strings.Trim(p, `"`); err == nil && p != "" && fileExists(p) {
			return p
		}
	}
	for _, env := range []string{"ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"} {
		if base := os.Getenv(env); base != "" {
			if p := filepath.Join(base, "Microsoft", "Edge", "Application", "msedge.exe"); fileExists(p) {
				return p
			}
		}
	}
	return ""
}

func fileExists(p string) bool {
	st, err := os.Stat(p)
	return err == nil && st.Mode().IsRegular()
}

// fallback runs when WebView2 cannot be used: it explains, offers to show the
// reader in Microsoft Edge (app window, own profile) or the default browser,
// and keeps the server alive while that is in use. It returns the exit code.
func (d *desktop) fallback(reason string) int {
	d.mode.Store(modeFallback)
	d.log.logf("WebView2 không dùng được: %s", reason)
	if d.quit.Load() {
		d.shutdown()
		return exitOK
	}
	text := "MythLab cần Microsoft Edge WebView2 Runtime để hiện cửa sổ đọc truyện, nhưng không khởi động được thành phần này.\n\n" +
		"Chi tiết: " + reason + "\n\n" +
		"Tải WebView2 Runtime (bản Evergreen) tại:\n" + webview2Page + "\n\n" +
		"Mở MythLab trong trình duyệt ngay bây giờ?\n" +
		"(Tiến độ đọc và cài đặt khi đọc trong trình duyệt được lưu riêng.)"
	if messageBox(0, text, mbYesNo|mbIconWarning|mbTopMost) != idYes {
		d.shutdown()
		return exitError
	}
	started := time.Now()
	if edge := findEdge(); edge != "" {
		cmd := exec.Command(edge, "--app="+d.url, "--user-data-dir="+d.dirs.edgeApp(), "--no-first-run",
			"--no-default-browser-check", "--disable-background-mode")
		if err := cmd.Start(); err == nil {
			d.log.logf("đã mở Microsoft Edge (--app), pid %d", cmd.Process.Pid)
			cmd.Wait()
			if time.Since(started) > 8*time.Second { // it was the browser itself and its window is closed now
				d.log.logf("cửa sổ Edge đã đóng")
				d.shutdown()
				return exitOK
			}
			// Edge handed the window to a running process: closing cannot be observed
		} else {
			d.log.logf("không chạy được Edge: %v", err)
			shellOpen(d.url)
		}
	} else if !shellOpen(d.url) {
		d.log.logf("không mở được trình duyệt mặc định")
		messageBox(0, "Không mở được trình duyệt. Hãy tự mở địa chỉ này:\n"+d.url, mbOK|mbIconWarning)
	}
	messageBox(0, "MythLab đang mở trong trình duyệt:\n"+d.url+"\n\nGiữ hộp thoại này trong lúc đọc. Bấm OK khi đọc xong để tắt MythLab.", mbOK|mbIconInfo)
	d.shutdown()
	return exitOK
}
