# MythLab Truyện — build APK Android (Capacitor 8 cần JDK 21)
# .\build.ps1            -> dist\MythLab-debug.apk
# .\build.ps1 -Release   -> dist\MythLab-release.apk (ký bằng keystore từ biến môi trường)
#   MYTHLAB_KEYSTORE, MYTHLAB_KEYSTORE_PASS, MYTHLAB_KEY_ALIAS, MYTHLAB_KEY_PASS
param([switch]$Release, [switch]$NoInstall)
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
node sync-web.mjs; if ($LASTEXITCODE) { throw 'sync-web lỗi' }
npx cap sync android; if ($LASTEXITCODE) { throw 'cap sync lỗi' }

New-Item -ItemType Directory -Force dist | Out-Null
Push-Location android
try {
  if ($Release) {
    foreach ($v in 'MYTHLAB_KEYSTORE', 'MYTHLAB_KEYSTORE_PASS', 'MYTHLAB_KEY_ALIAS', 'MYTHLAB_KEY_PASS') {
      if (-not [Environment]::GetEnvironmentVariable($v)) { throw "Thiếu biến môi trường $v" }
    }
    .\gradlew.bat assembleRelease --no-daemon `
      "-Pandroid.injected.signing.store.file=$env:MYTHLAB_KEYSTORE" `
      "-Pandroid.injected.signing.store.password=$env:MYTHLAB_KEYSTORE_PASS" `
      "-Pandroid.injected.signing.key.alias=$env:MYTHLAB_KEY_ALIAS" `
      "-Pandroid.injected.signing.key.password=$env:MYTHLAB_KEY_PASS"
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
