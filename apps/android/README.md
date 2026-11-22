# MythLab Truyện — app Android

Vỏ Capacitor 8 bọc giao diện web Astro (`web/dist`). App chạy độc lập: đọc truyện thẳng từ GitHub bằng token
chỉ-đọc, hoặc kết nối tới server MythLab chạy trên máy tính cùng Wi-Fi. Đọc to bằng bộ đọc của Android (`vi-VN`).

## Cấu trúc

| Tệp | Vai trò |
|---|---|
| `package.json` | Capacitor 8 (`core`, `cli`, `android`), `@capacitor/preferences`, `@capacitor-community/text-to-speech`, `@capacitor-community/keep-awake`, `@capgo/capacitor-social-login` (đăng nhập Google, xem `GOOGLE_SIGNIN.md`) |
| `capacitor.config.json` | `appId io.github.mythlab.reader`, tên `MythLab Truyện`, `webDir www`, scheme `https`, cho phép mixed content (lý do ở mục Bảo mật mạng) |
| `sync-web.mjs` | Chép `../../web/dist` vào `www/` và bỏ `viewport-fit=cover` khỏi `index.html` (để thanh trạng thái màu teal không đè lên header) |
| `build.ps1` | Đặt `JAVA_HOME` (JDK 21) và `ANDROID_HOME`, dựng web, chạy `sync-web`, `cap sync`, Gradle, chép APK vào `dist/` |
| `android/` | Dự án Android do `npx cap add android` tạo, đã chỉnh: icon, màu teal, `network_security_config.xml` (cho phép `http` tới server LAN), `<queries>` cho `TTS_SERVICE` |

`www/`, `dist/`, `node_modules/` và các thư mục build không đưa lên repo.

`sync-web.mjs` dừng với mã lỗi 1 (không đóng gói giao diện cũ hay hỏng) khi: thiếu `web/dist/index.html`;
`index.html` không có script module; không tìm thấy `viewport-fit=cover` để bỏ (Astro đổi cách in thẻ meta);
không có tệp `.js` băm tên trong `_astro/`; hoặc `index.html` trỏ tới tệp không có trong bản chép.

## Yêu cầu

- Node.js 22+ và npm (Capacitor 8 CLI cần `>=22.0.0`; phần web `web/` dùng Astro cần `>=22.23.4`, nên dùng bản mới nhất của Node 22 hoặc 24).
- **JDK 21** (Capacitor 8 không build được với JDK 17). `build.ps1` dùng `JAVA_HOME` nếu đó là JDK 21+, nếu không thì
  tìm ở `%LOCALAPPDATA%\MythLab-tools\jdk21`. Có thể tải bản portable tại
  https://aka.ms/download-jdk/microsoft-jdk-21-windows-x64.zip rồi giải nén vào thư mục đó.
- **Android SDK** ở `%LOCALAPPDATA%\Android\Sdk` (hoặc đặt `ANDROID_HOME`), có `platforms;android-36` và `build-tools`.

## Build

```powershell
cd apps\android
powershell -ExecutionPolicy Bypass -File build.ps1
```

Kết quả: `apps\android\dist\MythLab-debug.apk`. `build.ps1` luôn dựng giao diện web trước (`tools\build-web.ps1`:
`npm ci` khi cần rồi `npm run build`), rồi `node sync-web.mjs`, `npx cap sync android` và `gradlew assembleDebug`.
Lần đầu Gradle tự tải về (vài phút); lần sau khoảng 20 giây đến 1 phút.

Tham số: `-SkipWeb` (không dựng web, dùng `web\dist` đang có), `-NoInstall` (không tự `npm install`),
`-Release` (xem dưới).

Kiểm tra APK có giao diện mới: mở bằng 7-Zip hoặc `tar -tf`, phải có `assets/public/index.html` và các tệp
`assets/public/_astro/*.js` có hash trong tên.

Sửa giao diện thì sửa trong `web/`, rồi chạy lại `build.ps1`.

### Bản release (ký)

Tạo keystore **ngoài repo**, rồi đặt biến môi trường và chạy:

```powershell
$env:MYTHLAB_KEYSTORE = "D:\keys\mythlab.jks"
$env:MYTHLAB_KEYSTORE_PASS = "..."
$env:MYTHLAB_KEY_ALIAS = "mythlab"
$env:MYTHLAB_KEY_PASS = "..."
powershell -ExecutionPolicy Bypass -File build.ps1 -Release   # dist\MythLab-release.apk
```

Không có keystore riêng? Chạy `build.ps1 -Release -LocalKey`: nếu chưa đặt `MYTHLAB_*` thì script tự tạo (một lần) keystore cục bộ `%LOCALAPPDATA%\MythLab-tools\keys\mythlab-local.jks` (mật khẩu ngẫu nhiên lưu cạnh đó, ngoài repo) và ký bằng nó. APK này cài được nhưng chỉ để thử; muốn phát hành thì dùng keystore riêng ở trên.

Mật khẩu keystore chỉ được `android/app/build.gradle` đọc từ biến môi trường (không truyền trên dòng lệnh Gradle). Không bao giờ commit `*.jks` / `*.keystore` hay mật khẩu. Bản release bật R8 (`minifyEnabled`, `shrinkResources`) với luật giữ cho Capacitor trong `android/app/proguard-rules.pro`;
bản debug không thu nhỏ. Bản release chưa được chạy thử trên máy thật, hãy thử kỹ trước khi phát hành.

### Phiên bản

Nguồn duy nhất là `version` trong `apps/android/package.json` (hiện `1.0.0`). `versionName` lấy nguyên giá trị đó,
`versionCode = MAJOR*10000 + MINOR*100 + PATCH` (1.0.0 thành 10000), mỗi phần phải nhỏ hơn 100. Tăng `version` mỗi
lần phát hành để cài đè được.

## Bảo mật mạng

`allowMixedContent: true` và `usesCleartextTraffic` là **bắt buộc** cho chế độ server LAN: WebView chạy ở gốc
`https://localhost` nhưng phải gọi `http://192.168.x.y:8765` (địa chỉ IP LAN do người dùng nhập, không đoán trước
được). Android `network_security_config` không hỗ trợ dải CIDR nên không thu hẹp theo miền được. Chế độ token GitHub
chỉ dùng `https`. Nếu chỉ dùng token GitHub, có thể đặt `allowMixedContent` về `false` và
`cleartextTrafficPermitted="false"`. FileProvider chỉ trỏ vào `cache/shared/` (app hiện chưa chia sẻ tệp nào).

## Cài lên điện thoại

**Cách 1, qua cáp USB (adb):** bật *Tuỳ chọn nhà phát triển, Gỡ lỗi USB* trên điện thoại, cắm cáp, rồi:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r dist\MythLab-debug.apk
```

**Cách 2, chép file APK:** chép `MythLab-debug.apk` sang điện thoại, mở bằng trình quản lý tệp và cho phép *Cài ứng
dụng không rõ nguồn gốc* khi được hỏi. Bản debug ký bằng khoá debug của máy build; muốn cập nhật từ máy build khác
thì gỡ bản cũ trước.

## Lần chạy đầu

App mở màn hình chào khi chưa có nguồn dữ liệu. Chọn một trong hai:

1. **Token GitHub (chạy độc lập):** dán token fine-grained chỉ-đọc (Contents + Metadata, chỉ các repo `Done_*`; cách
   tạo xem [`reader/README.md`](../../reader/README.md#tạo-token-github-chỉ-đọc-fine-grained)). Truyện tải thẳng
   từ `api.github.com` và lưu đệm trong máy.
2. **Server trên máy tính:** trên PC chạy
   `apps\desktop\dist\mythlab-server.exe --lan --config reader\config.json` (build bằng `apps\desktop\build.ps1`); server in ra địa chỉ dạng
   `http://192.168.x.y:8765/?k=<khoá>`. Trong app nhập URL `http://192.168.x.y:8765` và khoá đó (hoặc Cài đặt,
   Nguồn dữ liệu). Điện thoại và PC phải cùng Wi-Fi; nếu không kết nối được, cho phép `mythlab-server.exe` qua
   Windows Firewall (mạng Private). Khi dùng server có thể chọn giọng Edge (server cần có mạng).

Đổi nguồn sau này: **Cài đặt, Nguồn dữ liệu**.

## Giọng đọc

- Mặc định dùng bộ đọc **Máy (Android)**. Nếu máy chưa có giọng tiếng Việt: cài/cập nhật *Speech Services by Google*,
  vào *Cài đặt Android, Hệ thống, Ngôn ngữ, Đầu ra văn bản thành lời nói*, tải gói **Tiếng Việt**.
- *Giữ màn hình sáng khi nghe* (Cài đặt) chỉ bật khi đang đọc to.
- Giới hạn: đọc nền khi tắt màn hình và điều khiển trên màn hình khoá phụ thuộc WebView, chưa có dịch vụ media riêng.
- Đã build và kiểm tra nội dung APK, nhưng chưa chạy thử trên máy thật hay máy ảo.
