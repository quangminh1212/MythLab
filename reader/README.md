# MythLab Truyện — trình đọc & nghe truyện

Một giao diện duy nhất (`reader/static`, HTML/JS thuần, không cần build) dùng cho trình duyệt, PWA, app Android và app
Windows. Dữ liệu lấy theo thứ tự:

1. **Máy chủ MythLab** (`reader/server.py`) cùng địa chỉ, hoặc theo URL + khoá đã nhập trong Cài đặt → có giọng Edge tự nhiên và thư mục truyện trên máy.
2. **GitHub trực tiếp** bằng token chỉ-đọc → đọc các repo `Done_*` qua `api.github.com`, cache trong IndexedDB; nghe bằng giọng của máy/trình duyệt.
3. Chưa có gì → màn hình hướng dẫn kết nối.

## Chạy máy chủ trên PC

```powershell
python reader\server.py              # http://127.0.0.1:8765 (chỉ máy này)
python reader\server.py --port 9000
```

Cần Python 3.10+. Giọng Edge: `python -m pip install edge-tts`. Token GitHub của server lấy từ biến môi trường
`GITHUB_TOKEN`/`GH_TOKEN` hoặc `gh auth token`. Thư mục truyện cấu hình trong `reader/config.json`.

Không có tham số, server chỉ nghe ở `127.0.0.1`.

## Chế độ LAN (đọc từ điện thoại cùng Wi-Fi)

```powershell
python reader\server.py --lan
```

- Server nghe ở `0.0.0.0` và in ra các địa chỉ `http://<IP-LAN>:8765/?k=<khoá>`.
- Mọi `/api/*` từ máy khác cần khoá (header `X-MythLab-Key`, tham số `?k=` hoặc cookie đặt khi mở link `?k=` một lần). Truy cập từ chính máy chủ (127.0.0.1) không cần khoá.
- Khoá lấy từ `config.json` → `"server": {"access_key": "…"}`; nếu không đặt, server tự sinh một lần và lưu ở `reader/.cache/server.json` (bản .exe: `%LOCALAPPDATA%\MythLab\cache\server.json`; không commit).
- App Android / PWA: Cài đặt → Nguồn dữ liệu → nhập URL `http://<IP-LAN>:8765` và khoá, rồi tải lại.

Chỉ bật `--lan` trong mạng tin cậy: server dùng token GitHub của bạn để đọc repo riêng tư.

## Tạo token GitHub chỉ-đọc (fine-grained)

1. GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**
   (https://github.com/settings/personal-access-tokens/new).
2. **Resource owner**: tài khoản chứa các repo `Done_*`. **Expiration**: tuỳ chọn (nên có hạn).
3. **Repository access**: *Only select repositories* → chọn các repo `Done_*` (hoặc *All repositories*).
4. **Repository permissions**: `Contents` = **Read-only**, `Metadata` = **Read-only**. Không cấp quyền nào khác.
5. **Generate token**, dán vào màn hình chào (hoặc Cài đặt → Nguồn dữ liệu → *Kiểm tra*).

Token chỉ lưu trong trình duyệt/app (localStorage) và chỉ được gửi tới `api.github.com`. GitHub giới hạn 5.000 lượt
gọi/giờ; nút "Tải tất cả truyện" có thể vượt mức này, nên chọn từng repo.

## Cài như ứng dụng (PWA)

Mở MythLab trên Chrome/Edge qua `http://127.0.0.1:8765` (hoặc một địa chỉ HTTPS), bấm biểu tượng **Cài đặt ứng dụng**
trên thanh địa chỉ (Android: menu ⋮ → *Thêm vào màn hình chính*). Service worker chỉ chạy trên `localhost` hoặc HTTPS;
nó lưu sẵn giao diện, phông chữ và âm thanh TTS đã nghe (tối đa 200 đoạn) để dùng khi mất mạng. Khi đổi danh sách
file trong `js/` hoặc `css/`, sửa `PRECACHE` và tăng `CACHE_VERSION` trong `static/sw.js`.

## App Android (Capacitor)

Thư mục `apps/android/` (Capacitor 8; `sync-web.mjs` chép `reader/static` vào `www/`). Cần JDK 21 và Android SDK.

```powershell
cd apps\android
npm install
powershell -ExecutionPolicy Bypass -File build.ps1      # → apps\android\dist\MythLab-debug.apk
```

Chi tiết (cài APK, lần chạy đầu): [`apps/android/README.md`](../apps/android/README.md).
Bản release đọc đường dẫn keystore và mật khẩu từ biến môi trường; không bao giờ đưa `*.keystore` / `*.jks` vào repo.
App dùng bộ đọc của Android (`vi-VN`); nếu máy chưa có giọng tiếng Việt, cài *Speech Services by Google* rồi tải gói
Tiếng Việt.

## App Windows

Xem [`apps/desktop/README.md`](../apps/desktop/README.md):

```powershell
powershell -ExecutionPolicy Bypass -File apps\desktop\build.ps1   # → apps\desktop\dist\MythLab\MythLab.exe
```

## Phông chữ

Phông đọc được đóng gói sẵn trong `static/fonts/` (woff2, chỉ bộ ký tự latin, latin-ext, vietnamese), không tải từ
Google Fonts. Giấy phép: SIL Open Font License 1.1 (`static/fonts/OFL.txt`) cho mọi phông trừ Roboto Slab
(Apache 2.0, `static/fonts/Apache-2.0.txt`). Danh sách, phiên bản và nguồn: `static/fonts/README.md`. Phông của hệ
điều hành (Segoe UI, Times New Roman, …) chỉ được gọi theo tên, không chép vào repo; phông độc quyền không bao giờ
được đóng gói.
