# MythLab Truyện — app Android

Vỏ Capacitor 8 bọc đúng giao diện web trong `reader/static`. App chạy độc lập: đọc truyện thẳng từ GitHub bằng token
chỉ-đọc, hoặc kết nối tới server MythLab chạy trên máy tính cùng Wi-Fi. Đọc to bằng bộ đọc của Android (`vi-VN`).

## Cấu trúc

| Tệp | Vai trò |
|---|---|
| `package.json` | Capacitor 8 (`core`, `cli`, `android`), `@capacitor/preferences`, `@capacitor-community/text-to-speech`, `@capacitor-community/keep-awake` |
| `capacitor.config.json` | `appId io.github.mythlab.reader`, tên `MythLab Truyện`, `webDir www`, scheme `https`, cho phép mixed content |
| `sync-web.mjs` | Chép `../../reader/static` vào `www/` (bỏ `viewport-fit=cover` để thanh trạng thái màu teal không đè lên header) |
| `build.ps1` | Đặt `JAVA_HOME` (JDK 21) và `ANDROID_HOME`, chạy `sync-web` → `cap sync` → Gradle, chép APK vào `dist/` |
| `android/` | Dự án Android do `npx cap add android` tạo, đã chỉnh: icon, màu teal, `network_security_config.xml` (cho phép `http` tới server LAN), `<queries>` cho `TTS_SERVICE` |

`www/`, `dist/`, `node_modules/` và các thư mục build không đưa lên repo.

## Yêu cầu

- Node.js 20+ và npm.
- **JDK 21** (Capacitor 8 không build được với JDK 17). `build.ps1` dùng `JAVA_HOME` nếu đó là JDK 21+, nếu không thì
  tìm ở `%LOCALAPPDATA%\MythLab-tools\jdk21`. Có thể tải bản portable tại
  https://aka.ms/download-jdk/microsoft-jdk-21-windows-x64.zip rồi giải nén vào thư mục đó.
- **Android SDK** ở `%LOCALAPPDATA%\Android\Sdk` (hoặc đặt `ANDROID_HOME`), có `platforms;android-36` và `build-tools`.

## Build

```powershell
cd apps\android
npm install
powershell -ExecutionPolicy Bypass -File build.ps1
```

Kết quả: `apps\android\dist\MythLab-debug.apk`. Lần đầu Gradle tự tải về (vài phút); các lần sau khoảng 1 phút.

Sửa giao diện thì sửa trong `reader/static`, rồi chạy lại `build.ps1` (hoặc `npm run sync` nếu mở bằng Android Studio:
`npm run open`).

### Bản release (ký)

Tạo keystore **ngoài repo**, rồi đặt biến môi trường và chạy:

```powershell
$env:MYTHLAB_KEYSTORE = "D:\keys\mythlab.jks"
$env:MYTHLAB_KEYSTORE_PASS = "…"
$env:MYTHLAB_KEY_ALIAS = "mythlab"
$env:MYTHLAB_KEY_PASS = "…"
powershell -ExecutionPolicy Bypass -File build.ps1 -Release   # → dist\MythLab-release.apk
```

Không bao giờ commit `*.jks` / `*.keystore` hay mật khẩu.

## Cài lên điện thoại

**Cách 1 — qua cáp USB (adb):** bật *Tuỳ chọn nhà phát triển → Gỡ lỗi USB* trên điện thoại, cắm cáp, rồi:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r dist\MythLab-debug.apk
```

**Cách 2 — chép file APK:** chép `MythLab-debug.apk` sang điện thoại (cáp, Zalo, Google Drive…), mở bằng trình quản lý
tệp và cho phép *Cài ứng dụng không rõ nguồn gốc* khi được hỏi. Bản debug ký bằng khoá debug của máy build; muốn cập nhật
từ máy build khác thì gỡ bản cũ trước.

## Lần chạy đầu

App mở màn hình chào khi chưa có nguồn dữ liệu. Chọn một trong hai:

1. **Token GitHub (chạy độc lập):** dán token fine-grained chỉ-đọc (Contents + Metadata, chỉ các repo `Done_*`; cách
   tạo xem [`reader/README.md`](../../reader/README.md#tạo-token-github-chỉ-đọc-fine-grained)), bấm **Kiểm tra & lưu**. Truyện
   tải thẳng từ `api.github.com` và lưu đệm trong máy. Token chỉ nằm trong bộ nhớ của app.
2. **Server trên máy tính:** trên PC chạy `python reader\server.py --lan`; server in ra địa chỉ dạng
   `http://192.168.x.y:8765/?k=<khoá>`. Trong app nhập URL `http://192.168.x.y:8765` và khoá đó, bấm **Kết nối** (hoặc
   Cài đặt → Nguồn dữ liệu). Điện thoại và PC phải cùng Wi-Fi; nếu không kết nối được, cho phép Python qua Windows Firewall (mạng Private).
   Khi dùng server có thể chọn giọng Edge (cần server có mạng).

Đổi nguồn sau này: **Cài đặt → Nguồn dữ liệu**. **Xoá bộ nhớ đệm** xoá truyện đã lưu trong máy.

## Giọng đọc

- Mặc định dùng bộ đọc **Máy (Android)**. Nếu máy chưa có giọng tiếng Việt: cài/ cập nhật *Speech Services by Google*,
  vào *Cài đặt Android → Hệ thống → Ngôn ngữ → Đầu ra văn bản thành lời nói*, tải gói **Tiếng Việt**.
- *Giữ màn hình sáng khi nghe* (Cài đặt) chỉ bật khi đang đọc to; app không giữ màn hình sáng mặc định.
- Giới hạn: đọc nền khi tắt màn hình và điều khiển trên màn hình khoá phụ thuộc WebView, chưa có dịch vụ media riêng.
