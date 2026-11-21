# MythLab

Trình đọc truyện (Mạt Thế Cổ Đại Cầu Sinh, Niên Đại Thương Gia, ...). Toàn bộ viết bằng Go (server, ứng dụng desktop Windows) và TypeScript (giao diện Astro, vỏ Android Capacitor); không còn mã Python hay Node ở phía chạy. Phiên bản hiện tại: 1.0.0.

## Cấu trúc thư mục

| Thư mục | Nội dung |
|---|---|
| `web/` | Giao diện Astro + TypeScript (xem `web/ARCHITECTURE.md`) |
| `server/` | Server Go: API, Edge TTS, thư viện GitHub, ảnh bìa; `cmd/mythlab` là vỏ cửa sổ WebView2 |
| `apps/desktop/` | Script đóng gói Windows (`MythLab.exe`, `mythlab-server.exe`) |
| `apps/android/` | Ứng dụng Android (Capacitor) |
| `tools/` | Script dùng chung (`build-web.ps1`) |
| `reader/` | `config.json` dùng chung (danh sách nguồn truyện), `.cache/` của server, hướng dẫn chạy/LAN/token, đổi khoá LAN bằng `mythlab-server --rotate-key` (`reader/README.md`) |

## Build và test

```powershell
# Web
cd web; npm ci; npm run check; npm test; npm run build

# Server (Go)
cd server; go vet ./...; go test -count=1 ./...

# Desktop (Windows): dựng web, nhúng vào server, build hai file exe vào apps\desktop\dist
powershell -ExecutionPolicy Bypass -File apps\desktop\build.ps1 -Test

# Chạy server (sau khi build desktop): http://127.0.0.1:8765
apps\desktop\dist\mythlab-server.exe --config reader\config.json

# Android
powershell -ExecutionPolicy Bypass -File apps\android\build.ps1
```

CI (`.github/workflows/ci.yml`) chạy web (check, test, build) và server (vet, test) trên Ubuntu và Windows, cùng một job build image Docker (không push).

## Phiên bản / Versioning

Phiên bản hiện tại là 1.0.0, ghi ở `web/package.json` và `server/cmd/mythlab/winres/winres.json` (4 chỗ); phần Android do `apps/android` quản lý. Khi tăng phiên bản, sửa đồng thời các file này; `cd server && go run ./tools/checkversion` kiểm tra chúng khớp nhau (CI chạy lệnh này).

## Cấu hình / Config discovery

`--config` > `config.json` cạnh file exe > `%APPDATA%\MythLab\config.json` > `reader/config.json` gần nhất đi lên từ thư mục của exe (chế độ checkout) > đi lên từ thư mục làm việc > tạo mới trong `%APPDATA%\MythLab`.

## Docker

Image chứa server Go và giao diện web đã nhúng sẵn, chạy bằng người dùng không phải root (distroless). **Truyện không nằm trong image**: phải cấp thư viện lúc chạy (xem bên dưới).

```bash
# Build
docker build -t mythlab .

# Chạy nhanh (chỉ mở trên máy này); khoá bắt buộc với mọi máy khác vì container luôn chạy --lan (nghe 0.0.0.0)
docker run -d --name mythlab -p 127.0.0.1:8765:8765 \
  -e MYTHLAB_ACCESS_KEY="$(openssl rand -base64 18 | tr '+/' '-_' | tr -d '=')" \
  -v mythlab-data:/data mythlab

# Hoặc dùng compose
cp .env.example .env        # sửa MYTHLAB_ACCESS_KEY (file .env đã nằm trong .gitignore)
docker compose up -d --build
```

- **Khoá truy cập:** biến môi trường `MYTHLAB_ACCESS_KEY` (ưu tiên sau `server.access_key` trong `config.json`). Nếu không đặt, server tự sinh khoá một lần, lưu ở `/data/cache/server.json` và in trong `docker logs mythlab`. Đổi khoá: sửa `.env` rồi `docker compose up -d`, hoặc `docker run --rm -v mythlab-data:/data mythlab --rotate-key --config /data/config.json --cache /data/cache` (khi không dùng biến môi trường). Truy cập: `http://<máy>:8765/?k=<khoá>` một lần để đặt cookie. Request từ chính trong container (healthcheck) không cần khoá.
- **Cổng:** compose mặc định chỉ bind `127.0.0.1:8765`. Muốn mở cho LAN hoặc đặt sau reverse proxy, đặt `MYTHLAB_BIND=0.0.0.0` trong `.env`; nếu truy cập bằng tên miền, thêm tên đó vào `server.hosts` trong `/data/config.json`. Nên có HTTPS khi ra ngoài LAN.
- **Volume `/data`:** `config.json` (bản mặc định chỉ có thư viện cục bộ `/data/library`), `cache/` (ảnh bìa, giọng đọc, GitHub, `server.json`) và `progress.json` (tiến độ đọc đồng bộ giữa các thiết bị). Volume mới tự nhận quyền của người dùng `nonroot` (uid 65532); bind-mount thư mục tự tạo thì cần `chown 65532:65532`.
- **Cấp truyện:**
  - Thư mục cục bộ: bỏ truyện vào `/data/library` (ví dụ bind-mount `./library:/data/library:ro`; có sẵn dòng bình luận trong `compose.yaml`).
  - Repo GitHub `Done_*`: sửa `/data/config.json`, ví dụ `"github": [{"owner": "tên-github", "prefix": "Done_", "enabled": true}]`; repo riêng tư cần `GITHUB_TOKEN` (đặt trong `.env`). Sửa file bằng `docker run --rm -it -v mythlab-data:/data busybox vi /data/config.json`, hoặc bind-mount file riêng: `-v ./config.json:/data/config.json` (đặt `progress.json` cạnh nó nên thư mục `/data` vẫn phải ghi được).
- **Giọng đọc Edge** cần kết nối internet đi ra (websocket tới dịch vụ của Microsoft); tắt bằng cách thêm `--no-tts` vào lệnh chạy. Đọc từ GitHub cũng cần internet ra `api.github.com`.
- **Cập nhật:** `git pull && docker compose up -d --build` (dữ liệu trong volume được giữ; `config.json` trong volume không bị ghi đè nên cấu hình mặc định mới của image không tự áp dụng). Sao lưu: `docker run --rm -v mythlab-data:/data -v "$PWD":/b busybox tar czf /b/mythlab-data.tgz /data`.
- Container kiểm tra sức khoẻ bằng `mythlab-server --healthcheck` (gọi `/api/ping` nội bộ; image distroless không có curl). Compose chạy với root fs chỉ đọc, `cap_drop: ALL` và `no-new-privileges`.

## Lưu ý pháp lý / Legal notes

- **Giọng đọc Edge (`server/internal/edgetts`)** kết nối tới dịch vụ đọc to của Microsoft Edge bằng giao thức và token công khai của tiện ích Edge. Đây không phải API được Microsoft công bố hay cam kết hỗ trợ: có thể ngừng hoạt động bất cứ lúc nào và có thể trái điều khoản dịch vụ nếu dùng ngoài mục đích cá nhân. Tắt hẳn bằng `mythlab-server --no-tts`; giọng đọc của trình duyệt và Android vẫn dùng được.
- **Giấy phép:** `LICENSE` (MIT) chỉ áp dụng cho mã nguồn phần mềm (`web/`, `server/`, `apps/`, `tools/`). Truyện và bản thảo ở các thư mục còn lại không thuộc giấy phép này. Phông chữ đóng gói trong `web/public/fonts` theo giấy phép OFL/Apache-2.0 kèm trong thư mục đó.
- **Truyện** trong repo là nội dung của chủ dự án; không phân phối lại khi chưa được phép.
