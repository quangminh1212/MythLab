# MythLab

Trình đọc truyện (Mạt Thế Cổ Đại Cầu Sinh, Niên Đại Thương Gia, ...) với giao diện web, server Go, ứng dụng desktop (Windows) và Android. Phiên bản hiện tại: 1.0.0.

## Cấu trúc thư mục

| Thư mục | Nội dung |
|---|---|
| `web/` | Giao diện Astro + TypeScript (xem `web/ARCHITECTURE.md`) |
| `server/` | Server Go: API, Edge TTS, thư viện GitHub, ảnh bìa; `cmd/mythlab` là vỏ cửa sổ WebView2 |
| `apps/desktop/` | Script đóng gói Windows (`MythLab.exe`, `mythlab-server.exe`) |
| `apps/android/` | Ứng dụng Android (Capacitor) |
| `tools/` | Script dùng chung (`build-web.ps1`) |
| `reader/` | Bản Python cũ (còn giữ để tham chiếu) |

## Build và test

```powershell
# Web
cd web; npm ci; npm run check; npm test; npm run build

# Server (Go)
cd server; go vet ./...; go test -count=1 ./...

# Desktop (Windows): dựng web, nhúng vào server, build hai file exe vào apps\desktop\dist
powershell -ExecutionPolicy Bypass -File apps\desktop\build.ps1 -Test

# Android
powershell -ExecutionPolicy Bypass -File apps\android\build.ps1
```

CI (`.github/workflows/ci.yml`) chạy web (check, test, build) và server (vet, test) trên Ubuntu và Windows.

## Phiên bản / Versioning

Phiên bản hiện tại là 1.0.0, ghi ở `web/package.json` và `server/cmd/mythlab/winres/winres.json` (4 chỗ); phần Android do `apps/android` quản lý. Khi tăng phiên bản, sửa đồng thời các file này.

## Cấu hình / Config discovery

`--config` > `config.json` cạnh file exe > `%APPDATA%\MythLab\config.json` > `reader/config.json` gần nhất đi lên từ thư mục của exe (chế độ checkout) > đi lên từ thư mục làm việc > tạo mới trong `%APPDATA%\MythLab`.
