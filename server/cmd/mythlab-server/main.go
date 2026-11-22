// Command mythlab-server is the MythLab story reader server (console).
//
//	mythlab-server [--host 127.0.0.1] [--port 8765] [--lan] [--prefetch-covers] [--rotate-key]
//	               [--config FILE] [--cache DIR] [--static DIR] [--no-tts] [--healthcheck]
//	               [--google-client-id ID] [--allowed-emails a@b.c,...]
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"mythlab/internal/app"
	"mythlab/internal/tts"
)

func main() { os.Exit(run(os.Args[1:])) }

func run(args []string) int {
	fl := flag.NewFlagSet("mythlab-server", flag.ContinueOnError)
	host := fl.String("host", "127.0.0.1", "địa chỉ lắng nghe")
	port := fl.Int("port", app.DefaultPort, "cổng")
	lan := fl.Bool("lan", false, "mở cho mạng LAN (0.0.0.0); /api/* cần khoá truy cập")
	prefetch := fl.Bool("prefetch-covers", false, "tải & cache mọi ảnh poster rồi thoát")
	config := fl.String("config", "", "file config.json (mặc định: tự tìm)")
	cache := fl.String("cache", "", "thư mục cache (mặc định: theo vị trí config)")
	static := fl.String("static", "", "phục vụ giao diện từ thư mục này thay cho bản nhúng")
	rotate := fl.Bool("rotate-key", false, "sinh khoá truy cập LAN mới (ghi vào server.json) rồi thoát; không in khoá")
	googleIDs := fl.String("google-client-id", "", "Google OAuth Web client ID (nhiều ID cách nhau bằng dấu phẩy) bật đăng nhập Google; mặc định: config server.google_client_ids hoặc $MYTHLAB_GOOGLE_CLIENT_ID")
	allowedEmails := fl.String("allowed-emails", "", "chỉ các email này được đăng nhập Google (cách nhau bằng dấu phẩy); mặc định: config server.allowed_emails hoặc $MYTHLAB_ALLOWED_EMAILS; trống = mọi tài khoản Google đã xác minh")
	noTTS := fl.Bool("no-tts", false, "tắt giọng đọc Edge")
	health := fl.Bool("healthcheck", false, "kiểm tra server đang chạy ở --host/--port (GET /api/ping) rồi thoát: 0 = khoẻ; dùng cho HEALTHCHECK của Docker")
	if err := fl.Parse(args); err != nil {
		if err == flag.ErrHelp {
			return 0
		}
		return 2
	}
	if fl.NArg() > 0 {
		fmt.Fprintf(os.Stderr, "tham số thừa: %v\n", fl.Args())
		return 2
	}
	if *port < 1 || *port > 65535 {
		fmt.Fprintf(os.Stderr, "cổng không hợp lệ: %d\n", *port)
		return 2
	}
	if *health {
		if err := healthcheck(*host, *port, 3*time.Second); err != nil {
			fmt.Fprintln(os.Stderr, "mythlab-server: healthcheck:", err)
			return 1
		}
		return 0
	}
	logger := log.New(os.Stderr, "", 0)
	var engine tts.Engine
	if !*noTTS {
		engine = tts.NewEdge()
	}
	a, err := app.New(app.Options{Host: *host, Port: *port, LAN: *lan, ConfigPath: *config, CacheDir: *cache,
		StaticDir: *static, TTS: engine, Logger: logger,
		GoogleClientIDs: splitCSV(*googleIDs), AllowedEmails: splitCSV(*allowedEmails)})
	if err != nil {
		fmt.Fprintln(os.Stderr, "mythlab-server:", err)
		return 1
	}
	defer a.Close()
	if *rotate {
		file, override, err := a.RotateKey()
		if err != nil {
			fmt.Fprintln(os.Stderr, "mythlab-server: không đổi được khoá:", err)
			return 1
		}
		fmt.Fprintf(os.Stdout, "Đã đổi khoá truy cập. Khoá mới nằm trong: %s (khoá cũ không còn dùng được sau khi khởi động lại server).\n", file)
		if override {
			fmt.Fprintln(os.Stdout, "Lưu ý: config.json đang đặt server.access_key và giá trị đó vẫn được ưu tiên; hãy xoá mục đó để dùng khoá mới.")
		}
		return 0
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	if *prefetch {
		a.PrefetchCovers(ctx, os.Stdout, 6)
		return 0
	}
	err = a.ListenAndServe(ctx, func(addr net.Addr) {
		p := *port
		if ta, ok := addr.(*net.TCPAddr); ok {
			p = ta.Port
		}
		fmt.Fprint(os.Stdout, a.Banner(p))
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, "mythlab-server:", err)
		return 1
	}
	return 0
}

func splitCSV(s string) []string {
	var out []string
	for _, p := range strings.Split(s, ",") {
		if p = strings.TrimSpace(p); p != "" {
			out = append(out, p)
		}
	}
	return out
}
