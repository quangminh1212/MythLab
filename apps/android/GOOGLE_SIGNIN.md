# Đăng nhập Google trên app Android

App dùng plugin `@capgo/capacitor-social-login` **8.7.13** (bản ghim cứng, cùng major 8 với Capacitor 8), chỉ bật nhà cung cấp Google
(Credential Manager của Android). Facebook SDK bị tắt bằng `socialLogin.facebook.include=false` trong `android/gradle.properties`,
và các quyền quảng cáo (`AD_ID`, `ACCESS_ADSERVICES_*`) bị gỡ khỏi `AndroidManifest.xml`.

Plugin được `cap sync` tự đăng ký (xem `android/app/src/main/assets/capacitor.plugins.json`), nên trong WebView nó nằm ở
`Capacitor.Plugins.SocialLogin`, giống cách tìm `MediaPlayback`:

```js
const SL = Capacitor.Plugins.SocialLogin;
await SL.initialize({ google: { webClientId: '<WEB CLIENT ID>' } });
const r = await SL.login({ provider: 'google', options: {} });   // { provider:'google', result:{ idToken, ... } }
await SL.logout({ provider: 'google' });
```

`idToken` có `aud` = Web client ID; gửi nó tới `POST /api/auth/google` của server.

## 1. Tạo OAuth client trên Google Cloud

1. https://console.cloud.google.com, chọn/tạo project, vào **APIs & Services > OAuth consent screen**, cấu hình (External; thêm email của bạn vào Test users nếu để chế độ Testing).
2. **Credentials > Create credentials > OAuth client ID**:
   - **Web application**: thêm **Authorized JavaScript origins** là các địa chỉ web đang dùng (ví dụ `https://myth.xlabrnd.com`, `http://localhost:8765`). Lấy **Client ID** (dạng `123-abc.apps.googleusercontent.com`). Đây là Web client ID duy nhất cần dùng cho web, Windows và Android.
   - **Android**: Package name `io.github.mythlab.reader` (lấy từ `capacitor.config.json`), kèm **SHA-1** (mục 2). Tạo một client Android cho mỗi SHA-1 (debug và release). Client Android không cần đưa ID vào code; nó chỉ để Google nhận ra app đã ký.

## 2. Lấy SHA-1

Debug (máy dựng, keystore mặc định của Android):

```powershell
keytool -list -v -keystore "$env:USERPROFILE\.android\debug.keystore" -alias androiddebugkey -storepass android -keypass android | Select-String SHA1
```

Release (keystore riêng):

```powershell
keytool -list -v -keystore D:\keys\mythlab.jks -alias mythlab | Select-String SHA1
```

Release thử bằng `build.ps1 -Release -LocalKey`:

```powershell
$k = "$env:LOCALAPPDATA\MythLab-tools\keys"
keytool -list -v -keystore "$k\mythlab-local.jks" -alias mythlab-local -storepass (Get-Content "$k\mythlab-local.pass" -Raw).Trim() | Select-String SHA1
```

Lưu ý: `debug.keystore` mỗi máy dựng một khác, nên mỗi máy dựng cần thêm SHA-1 riêng. Nếu phát hành qua Google Play với Play App Signing,
thêm cả SHA-1 của "App signing key" ở Play Console. Sai SHA-1 sẽ báo lỗi kiểu `[16] Account reauth failed` / "No credentials available".

## 3. Đặt Web client ID ở đâu

Chỉ ở **server**, app tự học từ `GET /api/ping` (`auth.client_id`), không có bí mật nào trong app:

```
MYTHLAB_GOOGLE_CLIENT_ID=123-abc.apps.googleusercontent.com      # nhiều ID: ngăn cách bằng dấu phẩy
MYTHLAB_ALLOWED_EMAILS=ban@gmail.com,nguoi-nha@gmail.com         # tùy chọn, bỏ trống = mọi tài khoản Google đã xác minh
```

hoặc `config.json`: `"server": { "google_client_ids": ["123-abc.apps.googleusercontent.com"] }`.
Với Docker, đặt biến trong `docker-compose.yml`. Android dùng ID đầu tiên làm `webClientId` (tức `serverClientId`) để `aud` của ID token khớp server.

## 4. Dựng và thử

```powershell
cd apps\android
powershell -ExecutionPolicy Bypass -File build.ps1          # dist\MythLab-debug.apk
adb install -r dist\MythLab-debug.apk
```

1. Server chạy với `MYTHLAB_GOOGLE_CLIENT_ID`; kiểm tra `GET /api/ping` có `"auth":{"google":true,"client_id":"..."}`.
2. Mở app, kết nối server, vào Cài đặt > Đăng nhập Google, chọn tài khoản. Phải thấy tên/ảnh, và tủ truyện, truyện theo dõi, đánh dấu được đồng bộ.
3. Cài app trên thiết bị thứ hai (hoặc mở web) đăng nhập cùng tài khoản, dữ liệu phải khớp.
4. Đăng xuất: dữ liệu cục bộ còn, ngừng đồng bộ.
5. Xem lỗi: `adb logcat | Select-String -Pattern "SocialLogin|Capacitor"`.

Lỗi thường gặp: máy không có Google Play Services / chưa thêm tài khoản Google (không có hộp chọn tài khoản); SHA-1 hoặc package name
không khớp client Android; app OAuth ở chế độ Testing mà email chưa nằm trong Test users; server trả 403 `not_allowed` do `MYTHLAB_ALLOWED_EMAILS`.
