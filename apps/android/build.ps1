# MythLab Truyện — build APK Android (Capacitor 8 cần JDK 21)
# .\build.ps1            -> dist\MythLab-debug.apk
# .\build.ps1 -Release   -> dist\MythLab-release.apk (ký bằng keystore từ biến môi trường)
#   MYTHLAB_KEYSTORE, MYTHLAB_KEYSTORE_PASS, MYTHLAB_KEY_ALIAS, MYTHLAB_KEY_PASS
#   .\build.ps1 -Release -LocalKey -> chưa đặt MYTHLAB_* thì tự tạo/dùng keystore cục bộ ngoài repo (%LOCALAPPDATA%\MythLab-tools\keys), chỉ để dùng thử
# Luôn dựng giao diện web (Astro, tools\build-web.ps1) trước rồi chép web\dist vào www bằng sync-web.mjs;
# -SkipWeb bỏ bước dựng web và dùng web\dist đang có.
param([switch]$Release, [switch]$NoInstall, [switch]$SkipWeb, [switch]$LocalKey)
$ErrorActionPreference = 'Continue'  # npm/gradle ghi stderr; lỗi được bắt qua $LASTEXITCODE
Set-Location $PSScriptRoot

function Get-JavaMajor($home_) {
  $rel = Join-Path $home_ 'release'
  if (-not (Test-Path $rel)) { return 0 }
  $m = Select-String -Path $rel -Pattern 'JAVA_VERSION="(\d+)' | Select-Object -First 1
  if ($m) { return [int]$m.Matches[0].Groups[1].Value } else { return 0 }
}

$jdk = $null
if ($env:JAVA_HOME -and (Get-JavaMajor $env:JAVA_HOME) -ge 21) { $jdk = $env:JAVA_HOME }
elseif (Test-Path "$env:LOCALAPPDATA\MythLab-tools\jdk21\bin\java.exe") { $jdk = "$env:LOCALAPPDATA\MythLab-tools\jdk21" }
else { throw "Cần JDK 21+: đặt JAVA_HOME hoặc giải nén JDK 21 vào $env:LOCALAPPDATA\MythLab-tools\jdk21" }
$env:JAVA_HOME = $jdk
$env:Path = "$jdk\bin;$env:Path"

if (-not $env:ANDROID_HOME) { $env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk" }
if (-not (Test-Path "$env:ANDROID_HOME\platforms")) { throw "Không thấy Android SDK ở $env:ANDROID_HOME" }
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
Write-Host "JAVA_HOME=$jdk"
Write-Host "ANDROID_HOME=$env:ANDROID_HOME"

if (-not $NoInstall -and -not (Test-Path node_modules)) { npm install; if ($LASTEXITCODE) { throw 'npm install lỗi' } }
if (-not $SkipWeb) {
  $ErrorActionPreference = 'Stop'
  try { & (Join-Path $PSScriptRoot '..\..\tools\build-web.ps1') } finally { $ErrorActionPreference = 'Continue' }
}
node sync-web.mjs; if ($LASTEXITCODE) { throw 'sync-web lỗi' }
npx cap sync android; if ($LASTEXITCODE) { throw 'cap sync lỗi' }

New-Item -ItemType Directory -Force dist | Out-Null
Push-Location android
try {
  if ($Release) {
    if ($LocalKey -and -not $env:MYTHLAB_KEYSTORE) {
      $kd = Join-Path $env:LOCALAPPDATA 'MythLab-tools\keys'
      $ks = Join-Path $kd 'mythlab-local.jks'; $pf = Join-Path $kd 'mythlab-local.pass'
      New-Item -ItemType Directory -Force $kd | Out-Null
      if (-not ((Test-Path $ks) -and (Test-Path $pf))) {
        $pw = -join ((48..57 + 97..122) | Get-Random -Count 24 | ForEach-Object { [char]$_ })
        if (Test-Path $ks) { Remove-Item $ks -Force }
        & "$jdk\bin\keytool.exe" -genkeypair -keystore $ks -storepass $pw -keypass $pw -alias mythlab-local -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=MythLab Local, O=MythLab' 2>&1 | Out-Null
        if ($LASTEXITCODE) { throw 'keytool lỗi' }
        Set-Content -Path $pf -Value $pw -NoNewline
      }
      $env:MYTHLAB_KEYSTORE = $ks
      $env:MYTHLAB_KEYSTORE_PASS = (Get-Content $pf -Raw).Trim()
      $env:MYTHLAB_KEY_ALIAS = 'mythlab-local'
      $env:MYTHLAB_KEY_PASS = $env:MYTHLAB_KEYSTORE_PASS
      Write-Host "Ký bằng keystore cục bộ: $ks"
    }
    foreach ($v in 'MYTHLAB_KEYSTORE', 'MYTHLAB_KEYSTORE_PASS', 'MYTHLAB_KEY_ALIAS', 'MYTHLAB_KEY_PASS') {
      if (-not [Environment]::GetEnvironmentVariable($v)) { throw "Thiếu biến môi trường $v" }
    }
    # Signing secrets are read by build.gradle from the MYTHLAB_* environment variables (inherited), never passed as arguments.
    .\gradlew.bat assembleRelease --no-daemon
    if ($LASTEXITCODE) { throw 'gradle assembleRelease lỗi' }
    $out = 'app\build\outputs\apk\release\app-release.apk'; $dst = '..\dist\MythLab-release.apk'
  } else {
    .\gradlew.bat assembleDebug --no-daemon
    if ($LASTEXITCODE) { throw 'gradle assembleDebug lỗi' }
    $out = 'app\build\outputs\apk\debug\app-debug.apk'; $dst = '..\dist\MythLab-debug.apk'
  }
  Copy-Item $out $dst -Force
} finally { Pop-Location }
Write-Host ("Xong: " + (Resolve-Path "dist\" ).Path + (Split-Path $dst -Leaf))
