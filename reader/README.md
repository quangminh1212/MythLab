# MythLab Truyện — trình đọc & nghe truyện

Bản hiện tại gồm ba phần:

| Thư mục | Vai trò |
|---|---|
| `server/` | Server Go (`mythlab-server`): API đọc thư mục truyện, ảnh bìa, giọng Edge TTS; giao diện được nhúng sẵn trong exe |
| `web/` | Giao diện Astro (TypeScript, SPA định tuyến bằng hash, service worker sinh khi build) |
| `apps/android`, `apps/desktop` | Vỏ Android (Capacitor) và ứng dụng Windows (WebView2) bọc cùng giao diện |

`reader/config.json` là file cấu hình chung (danh sách nguồn truyện); thư mục `reader/.cache/` là cache của server (không commit).

Dữ liệu lấy theo thứ tự:

1. **Server MythLab** cùng địa chỉ, hoặc theo URL + khoá nhập trong Cài đặt: có giọng Edge và thư mục truyện trên máy.
2. **GitHub trực tiếp** bằng token chỉ-đọc: đọc các repo `Done_*` qua `api.github.com`, lưu đệm trong trình duyệt.
3. Chưa có gì thì hiện màn hình hướng dẫn kết nối.

## Chạy server trên PC

Build exe một lần (`powershell -ExecutionPolicy Bypass -File appsdesktopbuild.ps1`, cần Go và Node.js), rồi chạy:

```powershell
apps\desktop\dist\mythlab-server.exe --config reader\config.json              # 127.0.0.1:8765
apps\desktop\dist\mythlab-server.exe --port 9000 --config reader\config.json
```

Tham số: `--port` (mặc định 8765), `--host` (mặc định 127.0.0.1), `--lan`, `--config FILE`, `--cache DIR`,
`--static DIR` (lấy giao diện từ thư mục thay cho bản nhúng), `--no-tts`, `--prefetch-covers`.

Token GitHub của server lấy từ biến môi trường `GITHUB_TOKEN`/`GH_TOKEN` hoặc `gh auth token`. Không có `--lan` thì
server chỉ nghe ở `127.0.0.1`.

### Ảnh bìa

`/api/cover?source=&key=&w=` trả ảnh trong thư mục truyện (`cover.*` > `poster.*` > `folder.*` > `thumb.*` > ảnh bất
kỳ); `w` là 160, 240, 320 hoặc 480. Không có thì tải `poster` trong `info.json` một lần và cache ở
`reader/.cache/covers/`. Truyện không có ảnh nào được vẽ bìa tự động. Tải sẵn mọi poster:

```powershell
apps\desktop\dist\mythlab-server.exe --config reader\config.json --prefetch-covers
```

## Chế độ LAN (đọc từ điện thoại cùng Wi-Fi)

```powershell
apps\desktop\dist\mythlab-server.exe --lan --config reader\config.json
```

- Server nghe ở `0.0.0.0` và in các địa chỉ `http://<IP-LAN>:8765/?k=<khoá>`.
- Mọi `/api/*` từ máy khác cần khoá: header `X-MythLab-Key`, tham số `?k=` hoặc cookie `mythlab_key`. Mở link `?k=`
  một lần thì server đặt cookie rồi chuyển hướng về địa chỉ không còn khoá. Truy cập từ chính máy chủ không cần khoá.
  Giao diện (HTML, JS, CSS) là công khai; chỉ dữ liệu `/api/*` được bảo vệ.
- Khoá lấy từ `config.json` mục `"server": {"access_key": "..."}`; không đặt thì server tự sinh một lần và lưu vào
  `server.json` cạnh thư mục cache (không commit).
- App Android / PWA: Cài đặt, Nguồn dữ liệu, nhập URL `http://<IP-LAN>:8765` và khoá.

Chỉ bật `--lan` trong mạng tin cậy: server dùng token GitHub của bạn để đọc repo riêng tư.

## Dựng giao diện và kiểm thử

```powershell
cd web
npm ci
npm run build          # ra web\dist
npx astro check
npx vitest run
cd ..\server
go vet ./...
go test ./...
```

Bộ quy tắc xử lý văn bản (tên chương, tách tiêu đề, tóm tắt info.json) có một file mẫu dùng chung:
`server/internal/library/testdata/textutil_cases.json`; cả `go test` lẫn vitest đều đọc file này.

Script end-to-end (Python Playwright) nằm ở `web/e2e/` (`browse.py`, `reader.py`, `settings.py`, `offline.py`), chạy
khi server đang chạy, ví dụ `python e2e/browse.py --base http://127.0.0.1:18806 --api http://127.0.0.1:18806 --out DIR`.

Mọi bản build dùng chung hai bước: `tools\build-web.ps1` (npm ci khi cần, `npm run build`) và, cho exe,
`go run ./tools/embedui` trong `server/` (chép `web/dist` vào `server/internal/webui/dist`).

## Tạo token GitHub chỉ-đọc (fine-grained)

1. GitHub, **Settings, Developer settings, Personal access tokens, Fine-grained tokens, Generate new token**
   (https://github.com/settings/personal-access-tokens/new).
2. **Resource owner**: tài khoản chứa các repo `Done_*`. **Expiration**: nên có hạn.
3. **Repository access**: *Only select repositories*, chọn các repo `Done_*`.
4. **Repository permissions**: `Contents` = **Read-only**, `Metadata` = **Read-only**. Không cấp quyền nào khác.
5. **Generate token**, dán vào màn hình chào (hoặc Cài đặt, Nguồn dữ liệu).

Token chỉ lưu trong trình duyệt/app và chỉ được gửi tới `api.github.com`. GitHub giới hạn 5.000 lượt gọi/giờ nên
hãy tải từng truyện thay vì tải tất cả một lần.

## Cài như ứng dụng (PWA)

Mở MythLab qua `http://127.0.0.1:8765` (hoặc một địa chỉ HTTPS), bấm biểu tượng **Cài đặt ứng dụng** trên thanh
địa chỉ. Service worker chỉ chạy trên `localhost` hoặc HTTPS; nó lưu sẵn giao diện để mở khi mất mạng, và chương đã
tải về (nút tải trong trang truyện) đọc được ngoại tuyến.

## Ứng dụng Android và Windows

- Android: [`apps/android/README.md`](../apps/android/README.md), kết quả `apps\android\dist\MythLab-debug.apk`.
- Windows: [`apps/desktop/README.md`](../apps/desktop/README.md), kết quả `apps\desktop\dist\MythLab.exe`.
