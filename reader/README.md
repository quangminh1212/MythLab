# MythLab Truyện — trình đọc & nghe truyện

Bản hiện tại gồm ba phần:

| Thư mục | Vai trò |
|---|---|
| `server/` | Server Go (`mythlab-server`): API đọc thư mục truyện, ảnh bìa (giọng đọc chạy trên thiết bị, không qua server); giao diện được nhúng sẵn trong exe |
| `web/` | Giao diện Astro (TypeScript, SPA định tuyến bằng hash, service worker sinh khi build) |
| `apps/android`, `apps/desktop` | Vỏ Android (Capacitor) và ứng dụng Windows (WebView2) bọc cùng giao diện |

`reader/config.json` là file cấu hình chung (danh sách nguồn truyện); thư mục `reader/.cache/` là cache của server (không commit).

Dữ liệu lấy theo thứ tự:

1. **Server MythLab** cùng địa chỉ, hoặc theo URL + khoá nhập trong Cài đặt: có thư mục truyện trên máy.
2. **GitHub trực tiếp** bằng token chỉ-đọc: đọc các repo `Done_*` qua `api.github.com`, lưu đệm trong trình duyệt.
3. Chưa có gì thì hiện màn hình hướng dẫn kết nối.

## Chạy server trên PC

Build exe một lần (`powershell -ExecutionPolicy Bypass -File appsdesktopbuild.ps1`, cần Go và Node.js), rồi chạy:

```powershell
apps\desktop\dist\mythlab-server.exe --config reader\config.json              # 127.0.0.1:8765
apps\desktop\dist\mythlab-server.exe --port 9000 --config reader\config.json
```

Tham số: `--port` (mặc định 8765), `--host` (mặc định 127.0.0.1), `--lan`, `--config FILE`, `--cache DIR`,
`--static DIR` (lấy giao diện từ thư mục thay cho bản nhúng), `--prefetch-covers`, `--rotate-key`.

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
- Đổi khoá (ví dụ khi lỡ lộ): `mythlab-server --rotate-key [--config FILE]` ghi khoá ngẫu nhiên mới (128 bit trở lên, crypto/rand)
  vào `server.json` một cách nguyên tử, chỉ in nơi đọc khoá mới, không in khoá. Khởi động lại server để áp dụng và nhập lại khoá
  trên các thiết bị. Nếu `config.json` đặt `server.access_key` thì giá trị đó vẫn được ưu tiên: xoá mục đó (hoặc sửa tay).
- App Android / PWA: Cài đặt, Nguồn dữ liệu, nhập URL `http://<IP-LAN>:8765` và khoá.

Chỉ bật `--lan` trong mạng tin cậy: server dùng token GitHub của bạn để đọc repo riêng tư.

## Đăng nhập Google (đồng bộ lịch sử đọc, truyện yêu thích, đánh dấu)

Khi đăng nhập bằng Google, tiến độ đọc, danh sách truyện yêu thích và đánh dấu được lưu theo tài khoản và đồng bộ giữa các
thiết bị (web/PWA, Windows, Android). Không đăng nhập thì mọi thứ chạy như cũ (khoá truy cập, `/api/progress` dùng chung).

### 1. Tạo OAuth client ID loại Web trong Google Cloud Console

1. Vào <https://console.cloud.google.com/>, chọn (hoặc tạo) một project.
2. **APIs & Services, OAuth consent screen**: chọn *External*, điền tên ứng dụng và email hỗ trợ, thêm email của bạn vào
   *Test users* (hoặc bấm *Publish app* để mọi tài khoản Google đăng nhập được). Chỉ cần scope mặc định `openid`, `email`, `profile`.
3. **APIs & Services, Credentials, Create credentials, OAuth client ID**, loại **Web application**.
4. **Authorized JavaScript origins**: thêm `https://myth.xlabrnd.com` và `http://localhost:8765` (thêm mọi origin khác mà bạn mở
   giao diện, ví dụ `http://localhost:4321` khi chạy `npm run dev`). Không cần *Authorized redirect URIs*.
5. Lưu lại **Client ID** (dạng `1234-abc.apps.googleusercontent.com`). Client secret không dùng.
6. **Android**: trong *cùng project* tạo thêm một OAuth client ID loại **Android** với package name của app và dấu vân tay
   SHA-1 của khoá ký (debug: `keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android`;
   bản phát hành: SHA-1 của keystore phát hành). Client Android chỉ để Google cho phép app đăng nhập; **MythLab dùng Client ID loại Web**
   làm `serverClientId`, nên ID token gửi lên server luôn có `aud` bằng Client ID Web.

### 2. Cấu hình server

Đặt Client ID Web theo một trong các cách (ưu tiên từ trên xuống):

- cờ `--google-client-id <ID>`;
- `config.json`: `"server": {"google_client_ids": ["<ID>"]}`;
- biến môi trường `MYTHLAB_GOOGLE_CLIENT_ID=<ID>` (Docker: đặt trong `.env`).

Có thể liệt kê nhiều ID, cách nhau bằng dấu phẩy. Giới hạn ai được đăng nhập (mặc định mọi tài khoản Google đã xác minh email):
`MYTHLAB_ALLOWED_EMAILS=toi@gmail.com,ban@gmail.com`, cờ `--allowed-emails`, hoặc `"server": {"allowed_emails": [...]}`.

Server chỉ có đăng nhập khi cấu hình Client ID: `GET /api/ping` khi đó có thêm `"auth": {"google": true, "client_id": "..."}`.

### 3. Dữ liệu và bảo mật

- `POST /api/auth/google` đổi ID token của Google lấy phiên làm việc MythLab (token ngẫu nhiên 32 byte, hạn 90 ngày và tự
  gia hạn khi dùng, tối đa 10 phiên mỗi tài khoản). Server chỉ lưu **băm SHA-256** của token, trong `users.json` cạnh `config.json`.
  Đăng xuất (`POST /api/auth/logout`) thu hồi phiên ngay.
- Dữ liệu từng tài khoản nằm ở `users/<sha256 của Google sub>/progress.json` và `library.json` cạnh `config.json`.
- Token phiên (header `Authorization: Bearer`) chỉ mở `/api/progress`, `/api/library` và `/api/auth/*`; nội dung truyện vẫn cần khoá
  truy cập hoặc truy cập từ chính máy chủ như trước.
- Đăng nhập bị giới hạn 20 lần/phút mỗi IP. Khi chạy sau reverse proxy trên cùng máy, proxy nên đặt `X-Forwarded-For`.
- Khoá công khai của Google được tải từ `https://www.googleapis.com/oauth2/v3/certs` và cache theo `Cache-Control`; server cần ra
  internet tới địa chỉ này khi có người đăng nhập.

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

Bộ kiểm thử end-to-end (Go, chromedp) nằm ở `web/e2e/` (`browse_test.go`, `reader_test.go`, `settings_test.go`, `offline_test.go`), chạy
sau khi build `web/dist`: `cd web/e2e && go test -count=1 -timeout 40m ./...`.

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
