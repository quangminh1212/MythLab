# MythLab — app iOS (Capacitor 8)

Chuẩn bị để dựng app iOS từ cùng giao diện web (`web/dist`) với app Android. **Chưa dựng thử**: nơi viết tài liệu này
không có Mac, Xcode hay iPhone. Mọi thứ ghi là "đã kiểm" nghĩa là đã đọc mã nguồn (web, hoặc plugin trong
`apps/android/node_modules`); mục "Chưa kiểm chứng" ở cuối liệt kê phần chỉ có thể biết khi chạy trên máy thật.

Thư mục này **không** chứa dự án Xcode (`ios/`). Nó được sinh trên Mac bằng `npx cap add ios` (mục 3).

| Tệp | Vai trò |
|---|---|
| `package.json` | Capacitor 8 (`core`, `cli`, `ios`), cùng plugin với Android: `app`, `preferences`, `text-to-speech`, `keep-awake`, `@capgo/capacitor-social-login` 8.7.13; thêm `@capacitor/assets` (icon, splash). Không có `@capacitor/android` và không có plugin tự viết |
| `capacitor.config.json` | `appId io.github.mythlab.reader`, `webDir www`, `ios.contentInset = always`, nền teal, `CapacitorHttp` tắt |
| `sync-web.mjs` | Chép `../../web/dist` vào `www/`, bỏ `viewport-fit=cover`, ghi iOS client id Google vào `<meta>` (chạy được trên Windows/Linux, đã thử) |
| `configure-ios.sh` | Chạy sau `cap add ios`: thêm khoá `Info.plist` (nghe nền, Google, mã hoá) bằng PlistBuddy. Chưa chạy thử |
| `.gitignore` | `node_modules/`, `www/`, thư mục Pods/build |

## 1. Giới hạn cần biết trước

- Dựng bản cài được (`.ipa`, TestFlight, App Store) **bắt buộc** có Mac + Xcode. Không có cách hợp lệ nào dựng iOS trên Windows.
- Cài lên iPhone cần chứng thư ký của Apple:
  - **Apple ID miễn phí**: cài thẳng từ Xcode vào máy cắm cáp; bản cài **hết hạn sau 7 ngày** (phải cài lại), tối đa 3 app cùng lúc, không TestFlight, không có Push/một số capability.
  - **Apple Developer Program (99 USD/năm)**: TestFlight (mỗi bản dựng sống 90 ngày, tối đa 10.000 người thử qua link công khai, người thử nội bộ không cần Apple duyệt), App Store, ký 1 năm.
  - AltStore / Sideloadly / SideStore chỉ là cách tự ký bằng Apple ID miễn phí nên vẫn dính giới hạn 7 ngày; cần Mac hoặc PC chạy dịch vụ làm mới.
- **Không có tự cập nhật** trên iOS ngoài TestFlight/App Store (mục 9).
- Cách dùng không cần Mac nào: mở https://myth.xlabrnd.com trong Safari, Chia sẻ > "Thêm vào Màn hình chính" (PWA). Đây là đường chính thức cho iPhone/iPad hiện tại.

## 2. Chuẩn bị trên Mac

1. Cài **Xcode** mới (App Store hoặc developer.apple.com/download), mở một lần để chấp nhận giấy phép và cài thành phần iOS, `xcode-select --install`.
   Capacitor 8 đòi Xcode bản gần nhất; số bản chính xác xem https://capacitorjs.com/docs/getting-started/environment-setup (không tự kiểm chứng ở đây).
2. Cài **Node 22+** (`brew install node@22`), kiểm `node -v`.
3. Tuỳ chọn: CocoaPods (`brew install cocoapods`) nếu dùng `--packagemanager CocoaPods`. Mọi plugin ở đây đều có cả `Package.swift` lẫn `.podspec`.
4. Đăng nhập Apple ID trong Xcode > Settings > Accounts.
5. Clone repo, dựng web một lần: `cd web && npm ci && npm run build` (cần Node >= 22.23.4 cho Astro).

## 3. Tạo dự án iOS

```sh
cd apps/ios
npm install                      # dùng package.json ở đây, KHÔNG dùng apps/android
IOS_GOOGLE_CLIENT_ID=<ios-client-id>.apps.googleusercontent.com node sync-web.mjs   # bỏ biến nếu chưa làm Google
npx cap add ios                  # sinh ios/App (Xcode project)
sh configure-ios.sh              # Info.plist, xem mục 6 (đặt IOS_GOOGLE_CLIENT_ID và WEB_GOOGLE_CLIENT_ID nếu dùng Google)
npx cap sync ios                 # chép www vào app, đăng ký plugin
npx cap open ios                 # mở Xcode
```

Lần sau chỉ cần: `cd web && npm run build && cd ../apps/ios && npm run sync` (= `sync-web.mjs` + `cap sync ios`).
Nếu `npm i @capacitor/ios` riêng lẻ thì dùng đúng `^8.6.2` cho khớp `@capacitor/core`.

## 4. Xcode: Signing và Capabilities

Target **App**:

- **Signing & Capabilities** > Team = Apple ID / tổ chức của bạn; để Xcode tự quản lý chứng thư. `Bundle Identifier`: `io.github.mythlab.reader` có thể đã bị người khác giữ; đổi nếu Xcode báo trùng (nhớ đổi cả `appId` trong `capacitor.config.json` và OAuth client iOS, mục 6).
- **+ Capability > Background Modes > Audio, AirPlay, and Picture in Picture** (đây chính là `UIBackgroundModes = audio`; `configure-ios.sh` đã thêm khoá, capability chỉ để Xcode/App Store Connect nhất quán).
- Không cần: Push, Sign in with Apple, quyền Micro, Camera. Không cần `NSMicrophoneUsageDescription`.
- Deployment Target: giữ mặc định của Capacitor (iOS 15).

## 5. Âm thanh nền (bắt buộc làm tay)

Plugin TTS (`@capacitor-community/text-to-speech`) trên iOS dùng `AVSpeechSynthesizer` với `usesApplicationAudioSession = false` và **bỏ qua** tham số `category`
(đã đọc `TextToSpeech.swift`; `category: 'playback'` mà `engines.ts` gửi chỉ có tác dụng trên Android). Capacitor không tự đặt `AVAudioSession`. Muốn
`<audio>` im lặng của web (giữ Media Session / màn hình khoá) và tiếng đọc chạy khi tắt màn hình, đặt category `playback` ngay lúc khởi động.
Trong `ios/App/App/AppDelegate.swift`, thêm `import AVFoundation` đầu tệp và đặt đoạn này vào đầu `application(_:didFinishLaunchingWithOptions:)`:

```swift
do {
    try AVAudioSession.sharedInstance().setCategory(.playback, mode: .spokenAudio, options: [])
    try AVAudioSession.sharedInstance().setActive(true)
} catch {
    NSLog("AVAudioSession: \(error)")
}
```

Không cần plugin bên thứ ba cho việc này (tôi không xác nhận được tên plugin cộng đồng nào còn bảo trì, nên không đề xuất). Chữ ký của `didFinishLaunchingWithOptions` có ở cả mẫu
UIScene (Capacitor 8.5+) lẫn mẫu cũ; xem tệp thật rồi chèn vào.

## 6. Info.plist

`sh configure-ios.sh` đặt (kiểm lại trong Xcode > App > Info):

| Khoá | Giá trị | Vì sao |
|---|---|---|
| `UIBackgroundModes` | `[audio]` | tiếp tục đọc khi khoá màn hình / sang app khác |
| `ITSAppUsesNonExemptEncryption` | `NO` | chỉ dùng HTTPS của hệ thống; bỏ câu hỏi xuất khẩu của TestFlight |
| `GIDClientID` | iOS client id | Google Sign-In SDK |
| `GIDServerClientID` | Web client id | `aud` của ID token là id của server |
| `CFBundleURLTypes` > `CFBundleURLSchemes` | iOS client id **viết ngược** (`com.googleusercontent.apps.<số>-<mã>`) | Google trả kết quả về app bằng URL scheme |

Không cần sửa:

- **App Transport Security**: app luôn ghim `https://myth.xlabrnd.com` (`pinnedNativeServer` trong `core/backend/index.ts`), nên ATS mặc định là đủ. Android bật `allowMixedContent`/cleartext cho server LAN; iOS không có tương đương và code web cũng không dùng http trong app. Nếu sau này cho trỏ server LAN `http://`, thêm `NSAppTransportSecurity > NSAllowsLocalNetworking = YES` (chỉ cho host `.local`/IP riêng) chứ đừng bật `NSAllowsArbitraryLoads`.
- Quyền Micro / Camera / Vị trí: không dùng.
- Origin của WebView là `capacitor://localhost` (iOS không cho `https` làm scheme tuỳ chỉnh); server đã cho phép origin này (`corsFixed` trong `server/internal/httpapi/auth.go`).
- Capacitor 8.5+ dùng UIScene: nếu thêm URL scheme thủ công thì chuyển URL cho `SceneDelegate` như README của `@capgo/capacitor-social-login` (mục "iOS OAuth redirect URLs").

### Đăng nhập Google trên iOS

1. Google Cloud > Credentials > Create OAuth client ID > **iOS**, Bundle ID = bundle id của target (mục 4). Không cần SHA-1.
2. Giữ Web client ID đang có làm `google_client_ids` của server (không đổi gì ở server).
3. `IOS_GOOGLE_CLIENT_ID=... node sync-web.mjs` ghi `<meta name="mythlab-ios-google-client-id">` vào `www/index.html`; `core/auth-native.ts` đọc nó và gọi
   `SocialLogin.initialize({ google: { iOSClientId, iOSServerClientId: <web client id>, webClientId } })`. Không có meta thì bấm đăng nhập báo lỗi rõ ràng, không đăng nhập Google qua web (Google chặn origin `capacitor://`).
4. `configure-ios.sh` đặt `GIDClientID`, `GIDServerClientID`, URL scheme ngược.
5. Kiểm: ID token trả về phải có `aud` = Web client ID (do `serverClientID`). Nếu server từ chối `bad_token`, giải mã token ở jwt.io xem `aud`; cách chữa nhanh là thêm iOS client id vào `google_client_ids` của server (đây là phần chưa kiểm chứng).

## 7. Icon và splash

Cần ảnh nguồn vuông **1024x1024 PNG, không kênh alpha** (chưa có sẵn: `web/public/icons` chỉ tới 512 và `icon.svg`). Xuất từ `web/public/icons/icon.svg`
(ví dụ `rsvg-convert -w 1024 -h 1024 icon.svg -o apps/ios/assets/icon-only.png`, rồi bỏ alpha bằng Preview hoặc `sips -s format jpeg` rồi về png trên nền teal).
Đặt vào `apps/ios/assets/`: `icon-only.png` (1024) và, nếu muốn splash, `splash.png` + `splash-dark.png` (2732x2732). Sau đó:

```sh
cd apps/ios && npx capacitor-assets generate --ios
```

(`@capacitor/assets` đã có trong `devDependencies`.) Nếu không có splash, Capacitor dùng LaunchScreen storyboard mặc định (nền trắng).

## 8. Chạy, ký và phát hành

- **Máy ảo**: Xcode chọn iPhone Simulator > Run. Giọng tiếng Việt có thể chưa có trong máy ảo; TTS/âm thanh nền chỉ tin cậy trên máy thật.
- **Máy thật (Apple ID miễn phí)**: cắm iPhone, bật Chế độ nhà phát triển (Cài đặt > Quyền riêng tư & Bảo mật > Developer Mode), chọn máy làm đích > Run; trên máy: Cài đặt > Cài đặt chung > VPN & Quản lý thiết bị > tin cậy chứng thư. Hết hạn sau 7 ngày.
- **TestFlight**: tài khoản trả phí; Xcode > Product > Archive > Distribute App > App Store Connect > Upload; tạo app trong App Store Connect cùng bundle id, thêm người thử. Tăng `CURRENT_PROJECT_VERSION` mỗi lần tải lên (số build phải tăng).
- **App Store**: thêm chính sách quyền riêng tư (có `web/public/privacy.html`), ảnh chụp màn hình, mô tả. Apple có thể hỏi vì app là vỏ web; bù lại có TTS native và đọc offline.
- Số phiên bản: `MARKETING_VERSION` = `version` trong `package.json` (hiện 1.1.4).

## 9. Tự cập nhật: không có trên iOS

Android tải APK từ `/android/latest.json` rồi gọi trình cài (`AppUpdatePlugin.java`). iOS **không cho** cài gói tải về ngoài App Store/TestFlight (TestFlight tự nhắc bản mới; bản ký miễn phí phải cài lại bằng Xcode/AltStore).
Phần web đã đảm bảo (có test trong `web/src/app/core/native-platform.test.ts`):

- `core/app-update.ts`: `plugin()` trả `null` khi `Capacitor.getPlatform() === 'ios'`, kể cả nếu có plugin tên `AppUpdate`. Hệ quả: `appUpdate.available()` là `false`, nên không có kiểm tra lúc mở app (`main.ts: announceUpdate/watchUpdates`), không có hộp thoại "Có bản mới", tab cài đặt "Ứng dụng" không hiện (`settings/panel.ts`), và không có yêu cầu mạng tới `/android/latest.json`.
- Không viết `AppUpdate` cho iOS, đừng thêm. Giao diện web nằm trong bản cài (`www`), dữ liệu truyện thì lấy từ server: **sửa web thì phải dựng lại và nộp bản mới** (khác PWA tự cập nhật qua service worker; `pwa.ts` cố ý tắt service worker trong Capacitor).

## 10. Web đã chỉnh cho iOS

| Chỗ | Trước | Nay |
|---|---|---|
| `core/native-platform.ts` (mới) | không phân biệt nền tảng; `isNative()` đúng cả iOS | `nativePlatform()` / `isNativeIOS()` từ `Capacitor.getPlatform()`; không có `getPlatform` thì coi là Android (giữ nguyên hành vi cũ) |
| `core/app-update.ts` | chỉ dựa vào plugin | thêm cổng iOS |
| `player/native-media.ts` | dò plugin `MediaPlayback` rồi `registerPlugin` | bỏ qua trên iOS (dịch vụ nền là của Android; màn hình khoá dùng Media Session của trang, `player/mediasession.ts`) |
| `core/auth-native.ts` | chỉ `webClientId` | trên iOS thêm `iOSClientId`/`iOSServerClientId` |
| `settings/voices.ts` | nhãn "Máy (Android)" | "Máy (iPhone/iPad)" trên iOS |
| `player/engines.ts` `warnNoVi` | luôn bảo cài "Speech Services by Google" | trên iOS chỉ đường vào Cài đặt > Trợ năng > Nội dung đã đọc > Giọng nói (không có nút "Cài giọng": `openInstall` của plugin trên iOS không làm gì) |

Đã rà, **không** cần đổi (đều tự bỏ qua hoặc an toàn khi plugin thiếu):

- `core/backnav.ts`: lắng nghe `backButton` của plugin `App`; iOS không có nút Back nên không bao giờ gọi; cử chỉ vuốt cạnh để quay lại không bật mặc định trong WKWebView của Capacitor (xem "Chưa kiểm chứng").
- `core/settings.ts` `syncStatusBar`: `ThemeBars` là plugin Android tự viết nên không có; rơi về `SystemBars.setStyle` (có ở lõi Capacitor 8 cho cả iOS, đã đọc `core-plugins.d.ts`).
- `engine` mặc định `native` trong app (cũng đúng cho iOS, có giọng `vi-VN`); `getSupportedVoices` của iOS trả đủ `lang`, `name`, `voiceURI` (= `identifier`), và chỉ số `voice` gửi lại trùng thứ tự `AVSpeechSynthesisVoice.speechVoices()` (đã đọc `TextToSpeechPlugin.swift`).
- `queueStrategy` 0/1: iOS plugin hiểu cả hai (0 = dừng cái đang nói, 1 = xếp hàng); hàm hoàn thành của mỗi lời gọi được gọi theo thứ tự `didFinish`/`didCancel`.
- Tốc độ: plugin tự ánh xạ `rate` (1 = tốc độ mặc định của iOS) nên cảm giác tốc độ có thể lệch Android đôi chút, cần nghe thử. `pitch` 0.5–2 nằm trong dải `pitchMultiplier`.
- `core/export-file.ts`: không có Filesystem/Share nên dùng Web Share API có tệp (iOS 15+) hoặc rơi về `manual` (hiện văn bản để sao chép), giống Android.
- `player/keepawake.ts`: plugin KeepAwake có bản iOS (`KeepAwakePlugin.swift`).
- `core/backend/index.ts`: app luôn ghim `https://myth.xlabrnd.com`.
- Liên kết `target="_blank"` (`settings/source.ts`, `views/story.ts`): Capacitor iOS mở ngoài app (Safari); chưa thử.

## 11. Giữ dự án Xcode trong git?

Nên commit `apps/ios/ios/` (trừ Pods/build, đã nằm trong `apps/ios/.gitignore`) sau khi dựng được lần đầu và đã sửa `AppDelegate.swift`, `Info.plist`, icon, vì các chỉnh tay đó
không tái tạo được bằng `cap add`. Giống `apps/android/android/` đang có trong repo.

## Chưa kiểm chứng (cần máy thật)

- Tiếng đọc native tiếp tục khi khoá màn hình. `AVSpeechSynthesizer` với `usesApplicationAudioSession = false` và `UIBackgroundModes=audio` thường vẫn nói tiếp trong nền, nhưng WKWebView có thể bị treo JS: đoạn kế tiếp chỉ chạy tiếp nếu đã xếp hàng sẵn (`ahead` trong `engines.ts`) hoặc phiên âm thanh còn hoạt động nhờ `AVAudioSession.playback` (mục 5). Nếu ngắt giữa chừng, cân nhắc đặt `usesApplicationAudioSession = true` bằng cách fork plugin (tác giả plugin hiện cố ý đặt false).
- Nút phát/tạm dừng/chương kế trên màn hình khoá và Control Center: Media Session của trang chỉ hiện khi một phần tử `<audio>` đang phát (vòng lặp im lặng `silentWav` trong `mediasession.ts`, hoặc clip Piper). Với giọng native, iOS không có "Now Playing" riêng như dịch vụ Android, nên điều khiển màn hình khoá phụ thuộc vào vòng im lặng đó; cần thử.
- Piper (WebAssembly + ONNX, ~63 MB) trong WKWebView: giới hạn bộ nhớ của iOS có thể làm app bị đóng; code có cảnh báo `lowMemoryNote`/`tooHeavyHere`.
- `iOSServerClientId` làm `aud` của token đúng như mong đợi (mục 6).
- Cử chỉ vuốt cạnh quay lại: `allowsBackForwardNavigationGestures` của WKWebView mặc định tắt trong Capacitor; trang dùng nút quay lại trong giao diện, và `history` router hoạt động bình thường, nhưng chưa thử trên máy.
- `contentInset: always` với bỏ `viewport-fit=cover`: header không đè lên notch/Dynamic Island và player không đè lên thanh Home. Trên iPad xoay ngang cũng cần thử.
- Mọi số hiệu phiên bản Xcode/iOS tối thiểu ở mục 2 và 4.
- `configure-ios.sh` (viết theo PlistBuddy, chưa chạy).
