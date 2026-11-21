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

## Lưu ý pháp lý / Legal notes

- **Giọng đọc Edge (`server/internal/edgetts`)** kết nối tới dịch vụ đọc to của Microsoft Edge bằng giao thức và token công khai của tiện ích Edge. Đây không phải API được Microsoft công bố hay cam kết hỗ trợ: có thể ngừng hoạt động bất cứ lúc nào và có thể trái điều khoản dịch vụ nếu dùng ngoài mục đích cá nhân. Tắt hẳn bằng `mythlab-server --no-tts`; giọng đọc của trình duyệt và Android vẫn dùng được.
- **Chưa có file LICENSE.** Mã nguồn mặc định là "bảo lưu mọi quyền" cho tới khi chủ dự án chọn giấy phép. Phông chữ đóng gói trong `web/public/fonts` theo giấy phép OFL/Apache-2.0 kèm trong thư mục đó.
- **Truyện** trong repo là nội dung của chủ dự án; không phân phối lại khi chưa được phép.
