# Tự cập nhật APK (MythLab)

Luồng: ứng dụng đọc `https://myth.xlabrnd.com/android/latest.json` (qua plugin `AppUpdate`, vì file tĩnh không có CORS),
so `versionCode` với bản đang cài, tải APK (kiểm SHA-256), kiểm chữ ký, rồi mở trình cài đặt của Android.

- Kiểm tra: lúc mở app (idle), khi app quay lại màn hình (cách nhau tối thiểu 6 giờ), và nút "Kiểm tra cập nhật" ở Cài đặt > Ứng dụng.
- Có bản mới: hộp thoại (phiên bản, dung lượng, nội dung thay đổi, thanh tiến độ, nút cài), mỗi phiên bản chỉ hiện một lần.
- Android 8+: lần đầu phải bật "Cho phép từ nguồn này"; quay lại app thì tự mở lại trình cài đặt.
- Đăng bản mới: tăng `version` trong `apps/android/package.json` (versionCode = MAJOR*10000 + MINOR*100 + PATCH), chạy
  `build.ps1 -Release` (hoặc `-LocalKey`), rồi `publish-update.ps1 -Notes "..."` (đăng APK trước, `latest.json` sau).

## Một khoá ký duy nhất

Android chỉ cài đè khi APK mới ký BẰNG CÙNG KHOÁ với bản đang cài. Hệ quả:
- Bản debug (khoá debug của máy build) không bao giờ cập nhật được từ bản release, và ngược lại.
- Phải dùng mãi một keystore release (`MYTHLAB_KEYSTORE*` hoặc `%LOCALAPPDATA%\MythLab-tools\keys\mythlab-local.jks`);
  sao lưu file `.jks` và `.pass`. Mất khoá = người dùng phải gỡ app rồi cài lại.
- Plugin so chứng chỉ ký của APK tải về với app đang chạy; khác thì báo "ký bằng khoá khác" thay vì mở trình cài đặt hỏng.
