#!/bin/sh
# Chay tren Mac SAU `npx cap add ios`: them cac khoa Info.plist can cho MythLab. Chay lai nhieu lan van an toan.
# Chua duoc chay thu (khong co Mac o noi viet); doc IOS_BUILD.md muc 6 va kiem tra Info.plist bang Xcode sau khi chay.
#   IOS_GOOGLE_CLIENT_ID=<so>-<ma>.apps.googleusercontent.com   (OAuth client loai iOS)
#   WEB_GOOGLE_CLIENT_ID=<so>-<ma>.apps.googleusercontent.com   (client Web, trung voi google_client_ids cua server)
set -eu
cd "$(dirname "$0")"
PLIST="ios/App/App/Info.plist"
PB=/usr/libexec/PlistBuddy
[ -f "$PLIST" ] || { echo "Khong thay $PLIST - chay 'npx cap add ios' truoc." >&2; exit 1; }
[ -x "$PB" ] || { echo "Can PlistBuddy (chi co tren macOS)." >&2; exit 1; }

has() { "$PB" -c "Print :$1" "$PLIST" >/dev/null 2>&1; }
setstr() { if has "$1"; then "$PB" -c "Set :$1 $2" "$PLIST"; else "$PB" -c "Add :$1 string $2" "$PLIST"; fi; }

# 1. nghe nen: giu app chay (TTS + audio) khi khoa man hinh
has UIBackgroundModes || "$PB" -c "Add :UIBackgroundModes array" "$PLIST"
"$PB" -c "Print :UIBackgroundModes" "$PLIST" | grep -qw audio || "$PB" -c "Add :UIBackgroundModes: string audio" "$PLIST"

# 2. khong dung ma hoa ngoai HTTPS: bo cau hoi xuat khau moi lan nop TestFlight
if has ITSAppUsesNonExemptEncryption; then "$PB" -c "Set :ITSAppUsesNonExemptEncryption false" "$PLIST"; else "$PB" -c "Add :ITSAppUsesNonExemptEncryption bool false" "$PLIST"; fi

# 3. dang nhap Google: GIDClientID + URL scheme = ma khach iOS viet nguoc
if [ -n "${IOS_GOOGLE_CLIENT_ID:-}" ]; then
  REV=$(echo "$IOS_GOOGLE_CLIENT_ID" | awk -F. '{for(i=NF;i>0;i--){printf "%s%s",$i,(i>1?".":"")}}')
  setstr GIDClientID "$IOS_GOOGLE_CLIENT_ID"
  [ -n "${WEB_GOOGLE_CLIENT_ID:-}" ] && setstr GIDServerClientID "$WEB_GOOGLE_CLIENT_ID"
  if "$PB" -c "Print :CFBundleURLTypes" "$PLIST" 2>/dev/null | grep -q "$REV"; then
    :
  elif has CFBundleURLTypes; then
    # mang da co muc khac: khong doan chi so, de nguoi dung them tay (IOS_BUILD.md muc 6)
    echo "CFBundleURLTypes da co san: them tay URL scheme $REV trong Xcode (Target > Info > URL Types)." >&2
  else
    "$PB" -c "Add :CFBundleURLTypes array" "$PLIST"
    "$PB" -c "Add :CFBundleURLTypes:0 dict" "$PLIST"
    "$PB" -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes array" "$PLIST"
    "$PB" -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string $REV" "$PLIST"
  fi
else
  echo "Bo qua dang nhap Google: chua dat IOS_GOOGLE_CLIENT_ID" >&2
fi
echo "Xong. Mo ios/App/App.xcworkspace va kiem tra Info.plist."
