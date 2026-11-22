<#
 Publishes a signed release APK so installed apps can update themselves (Cài đặt > Ứng dụng, and a toast at launch).

   powershell -ExecutionPolicy Bypass -File publish-update.ps1 [-Notes "Nội dung thay đổi"]

 Uploads MythLab-<version>.apk and then android/latest.json to the server's web folder
 (https://myth.xlabrnd.com/android/latest.json). The manifest goes last, so it never points at a missing file.
 Build first:  build.ps1 -Release -LocalKey  (or with your own MYTHLAB_* keystore).
 The APK must be signed with the SAME key as the installed app, or Android refuses the update.
 Bump "version" in package.json before every release: the app only offers a higher versionCode.
#>
param(
  [string]$Apk = (Join-Path $PSScriptRoot 'dist\MythLab-release.apk'),
  [string]$Server = 'bnix',
  [string]$RemoteDir = '/opt/mythlab/web/android',
  [string]$PublicBase = 'https://myth.xlabrnd.com/android',
  [string]$Notes = ''
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path $Apk)) { throw "Không thấy $Apk - hãy chạy build.ps1 -Release trước." }

$ver = (Get-Content (Join-Path $PSScriptRoot 'package.json') -Raw | ConvertFrom-Json).version
$p = $ver.Split('.') | ForEach-Object { [int]$_ }
if ($p.Count -ne 3 -or ($p | Where-Object { $_ -lt 0 -or $_ -gt 99 })) { throw "version '$ver' không phải MAJOR.MINOR.PATCH (mỗi phần 0..99)" }
$code = $p[0] * 10000 + $p[1] * 100 + $p[2]

# the APK must really be this version (build.ps1 reads the same package.json, so a stale APK is the only way to differ)
$sdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$aapt = Get-ChildItem (Join-Path $sdk 'build-tools') -Recurse -Filter aapt2.exe -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
if ($aapt) {
  $badging = & $aapt.FullName dump badging $Apk | Select-String -Pattern "versionCode='(\d+)'"
  if (-not $badging -or [int]$badging.Matches[0].Groups[1].Value -ne $code) { throw "APK không phải bản $ver (versionCode $code). Hãy dựng lại bằng build.ps1 -Release." }
} else { Write-Warning 'Không tìm thấy aapt2: bỏ qua bước kiểm tra phiên bản của APK.' }

$sha = (Get-FileHash $Apk -Algorithm SHA256).Hash.ToLower()
$size = (Get-Item $Apk).Length
$name = "MythLab-$ver.apk"
$manifest = [ordered]@{ versionCode = $code; versionName = $ver; url = $name; sha256 = $sha; size = $size; notes = $Notes } | ConvertTo-Json
$tmp = Join-Path ([IO.Path]::GetTempPath()) 'mythlab-latest.json'
[IO.File]::WriteAllText($tmp, $manifest, (New-Object Text.UTF8Encoding($false)))

ssh $Server "mkdir -p '$RemoteDir'"
if ($LASTEXITCODE) { throw 'ssh mkdir thất bại' }
scp $Apk "${Server}:$RemoteDir/$name"
if ($LASTEXITCODE) { throw 'scp APK thất bại' }
scp $tmp "${Server}:$RemoteDir/latest.json"
if ($LASTEXITCODE) { throw 'scp latest.json thất bại' }
Remove-Item $tmp -ErrorAction SilentlyContinue

# verify what the world sees
$live = Invoke-RestMethod "$PublicBase/latest.json" -Headers @{ 'Cache-Control' = 'no-cache' }
if ($live.versionCode -ne $code) { throw "latest.json trên máy chủ chưa đúng (versionCode $($live.versionCode))" }
$dl = Join-Path ([IO.Path]::GetTempPath()) "mythlab-verify.apk"
Invoke-WebRequest "$PublicBase/$name" -OutFile $dl
$got = (Get-FileHash $dl -Algorithm SHA256).Hash.ToLower()
Remove-Item $dl -ErrorAction SilentlyContinue
if ($got -ne $sha) { throw 'APK tải lại từ máy chủ không khớp SHA-256' }
Write-Host "Đã đăng $name (versionCode $code, $([math]::Round($size/1MB,1)) MB, sha256 $($sha.Substring(0,12))...)"
