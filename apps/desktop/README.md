# MythLab Truyện — bản desktop (Windows)

Một file `MythLab.exe` viết bằng Go: server đọc truyện (`server/`) chạy ở `127.0.0.1`, giao diện web (`web/`) được
nhúng sẵn trong exe, hiển thị trong cửa sổ WebView2 (thư viện `github.com/jchv/go-webview2`, không cần CGO hay
trình biên dịch C). Giọng đọc chạy trên thiết bị (Piper WASM / giọng trình duyệt), không qua server.

Mã nguồn: `server/cmd/mythlab` (ứng dụng cửa sổ) và `server/cmd/mythlab-server` (server dòng lệnh).

## Đóng gói

```powershell
powershell -ExecutionPolicy Bypass -File apps\desktop\build.ps1
```

Cần Go (bản ghi trong `server/go.mod`) và, để dựng giao diện, Node.js + npm. Kết quả:

| File | Là gì |
|---|---|
| `apps\desktop\dist\MythLab.exe` | ứng dụng cửa sổ, không có console |
| `apps\desktop\dist\mythlab-server.exe` | server dòng lệnh (console), cùng giao diện nhúng |

Các bước của `build.ps1`:

1. Dựng giao diện bằng `tools\build-web.ps1` (dùng chung với bản Android): nếu `web\dist` đã cũ so với mã nguồn trong
   `web\` thì `npm ci` (chỉ khi chưa cài hoặc `package-lock.json` đổi) rồi `npm run build`. Dựng lỗi thì cảnh báo
   và dùng bản giao diện đang có (`-Strict` thì dừng).
2. Chép `web\dist` vào `server\internal\webui\dist` (chỗ `go:embed` đọc) bằng `go run ./tools/embedui` trong
   `server\`, nguồn duy nhất của việc chép này. Build xong thì chạy `go run ./tools/embedui -restore` để trả thư mục
   về trang giữ chỗ được git theo dõi.
3. Sinh `server\cmd\mythlab\rsrc_windows_amd64.syso` (icon `apps\desktop\MythLab.ico`, manifest DPI, thông tin
   phiên bản) bằng `go run github.com/tc-hib/go-winres@v0.3.3`. File `.syso` là sản phẩm build, không commit.
4. `go build -trimpath -ldflags "-H=windowsgui -s -w"` cho `MythLab.exe`, `-ldflags "-s -w"` cho
   `mythlab-server.exe` (`CGO_ENABLED=0`).

Tham số: `-Clean` (xoá hai exe và `.syso` cũ trước), `-SkipWeb` (không chạy npm, nhúng `web\dist` đang có),
`-Strict` (dừng nếu không dựng được giao diện), `-KeepEmbed` (giữ bản đã chép trong `server\internal\webui\dist`),
`-Test` (chạy `go vet` và `go test -short` trước khi build).

Không commit `dist/`, `*.syso`.

## Chạy

Mở `MythLab.exe`. Tham số dòng lệnh:

| Tham số | Ý nghĩa |
|---|---|
| `--port N` | cổng của server trong máy. Mặc định 18765; khi ghi rõ `--port` mà cổng bận thì báo lỗi |
| `--port-file FILE` | ghi cổng đang chạy vào file (dùng khi kiểm thử) |
| `--no-window` | chỉ chạy server, không mở cửa sổ |
| `--data-dir DIR` | đặt hồ sơ WebView2, `window.json` và log vào thư mục này (hoặc biến môi trường `MYTHLAB_DATA_DIR`) |
| `--config FILE` | dùng file `config.json` này |
| `--cache DIR` | thư mục cache |
| `--static DIR` | lấy giao diện từ thư mục này thay cho bản nhúng |
| `--debug` | bật DevTools và menu chuột phải của WebView2 |
| `--quit` | yêu cầu MythLab đang chạy (cùng thư mục dữ liệu) đóng lại rồi thoát |

Mã thoát: 0 bình thường, 1 lỗi, 2 sai tham số, 3 khi chạy `--no-window` mà đã có MythLab khác đang chạy.

Cổng cố định giữ origin cố định (`http://127.0.0.1:18765`), nên tiến độ đọc và cài đặt (localStorage, IndexedDB của
WebView2) không mất giữa các lần mở. Vì vậy:

- **Chỉ một bản chạy.** Mở lần thứ hai chỉ đưa cửa sổ đang chạy lên trước rồi thoát.
- Nếu cổng mặc định 18765 bận vì chương trình khác, MythLab hỏi trước khi chạy tạm ở một cổng ngẫu nhiên, vì ở
  cổng khác thì dữ liệu đã lưu không hiện ra.

Đóng cửa sổ thì server dừng hẳn (chờ các yêu cầu đang chạy tối đa 10 giây), kích thước cửa sổ được lưu lại.

### Khi máy không có WebView2 Runtime

Windows 11 có sẵn WebView2. Nếu thiếu hoặc không khởi động được, MythLab hiện hộp thoại kèm địa chỉ tải
(<https://developer.microsoft.com/microsoft-edge/webview2/>) và đề nghị mở trong Microsoft Edge ở chế độ ứng dụng
(`msedge --app=...`, hồ sơ riêng trong `edge-app`), không có Edge thì mở trình duyệt mặc định. Server chạy tiếp cho
đến khi cửa sổ Edge đóng hoặc bấm OK ở hộp thoại "đang mở trong trình duyệt". Dữ liệu đọc trong trình duyệt được
lưu riêng, không chung với cửa sổ WebView2.

## Dữ liệu

| Gì | Ở đâu |
|---|---|
| Giao diện | nhúng trong exe |
| `config.json` | cạnh exe nếu có; không thì `reader\config.json` gần nhất tính từ thư mục hiện hành trở lên (khi chạy trong repo); không thì `%APPDATA%\MythLab\config.json` |
| Thư viện local mặc định | `%APPDATA%\MythLab\library` (đường dẫn tương đối trong config tính từ thư mục chứa config) |
| Cache GitHub, bìa | `%LOCALAPPDATA%\MythLab\cache` (chạy trong repo: `reader\.cache`) |
| Dữ liệu WebView2 (localStorage, IndexedDB) | `%LOCALAPPDATA%\MythLab\webview` |
| Kích thước cửa sổ | `%APPDATA%\MythLab\window.json` (`width`, `height` theo 96 DPI; thêm `maximized` khi đang phóng to) |
| Log | `%LOCALAPPDATA%\MythLab\desktop.log` (quá 4 MB thì chuyển sang `desktop.log.1`) |

Với `--data-dir DIR`, ba mục cuối nằm ngay trong `DIR` (`DIR\webview`, `DIR\window.json`, `DIR\desktop.log`) và bản
chạy đó được coi là một ứng dụng riêng, không đụng tới hồ sơ thật. Config và cache vẫn theo `--config`/`--cache`.

Repo GitHub `Done_*` đọc bằng `GITHUB_TOKEN`/`GH_TOKEN` hoặc `gh auth token` như server thường.

