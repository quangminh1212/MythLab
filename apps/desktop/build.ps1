# Đóng gói MythLab desktop (Go + WebView2):
#   apps\desktop\dist\MythLab.exe          ứng dụng cửa sổ, giao diện nhúng sẵn
#   apps\desktop\dist\mythlab-server.exe   server dòng lệnh (console)
#
# Dùng: powershell -ExecutionPolicy Bypass -File apps\desktop\build.ps1 [-Clean] [-SkipWeb] [-Strict] [-KeepEmbed] [-Test]
#   -Clean      xoá hai file exe và file .syso cũ trước khi build
#   -SkipWeb    không chạy npm; nhúng web\dist đang có
#   -Strict     dừng nếu không dựng được giao diện (mặc định: cảnh báo rồi nhúng bản đang có)
#   -KeepEmbed  giữ bản giao diện đã chép trong server\internal\webui\dist sau khi build
#   -Test       chạy go vet + go test -short trước khi build
param([switch]$Clean, [switch]$SkipWeb, [switch]$Strict, [switch]$KeepEmbed, [switch]$Test)
$ErrorActionPreference = "Stop"

$WinresVersion = "v0.3.3"                      # github.com/tc-hib/go-winres, sinh .syso không cần trình biên dịch C
$here   = $PSScriptRoot
$repo   = (Resolve-Path (Join-Path $here "..\..")).Path
$web    = Join-Path $repo "web"
$webDist = Join-Path $web "dist"
$server = Join-Path $repo "server"
$embed  = Join-Path $server "internal\webui\dist"
$cmdDir = Join-Path $server "cmd\mythlab"
$out    = Join-Path $here "dist"
$marker = 'name="mythlab-placeholder"'

function Invoke-Native {
    # Chạy một lệnh ngoài; stderr của nó không được biến thành lỗi PowerShell, chỉ mã thoát mới tính.
    param([string]$What, [scriptblock]$Command)
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { & $Command } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "$What lỗi (mã $LASTEXITCODE)" }
}

function Test-Placeholder([string]$Dir) {
    $index = Join-Path $Dir "index.html"
    if (-not (Test-Path -LiteralPath $index)) { return $true }
    return [System.IO.File]::ReadAllText($index).Contains($marker)
}

function Get-NewestWrite([string[]]$Paths) {
    $newest = [datetime]::MinValue
    foreach ($p in $Paths) {
        if (-not (Test-Path -LiteralPath $p)) { continue }
        $item = Get-Item -LiteralPath $p
        if ($item.PSIsContainer) {
            $files = Get-ChildItem -LiteralPath $p -Recurse -File -Force
        } else {
            $files = @($item)
        }
        foreach ($f in $files) { if ($f.LastWriteTimeUtc -gt $newest) { $newest = $f.LastWriteTimeUtc } }
    }
    return $newest
}

foreach ($tool in @("go")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "không thấy '$tool' trong PATH" }
}
if (-not (Test-Path -LiteralPath (Join-Path $server "go.mod"))) { throw "không thấy $server\go.mod" }
$icon = Join-Path $here "MythLab.ico"
if (-not (Test-Path -LiteralPath $icon)) { throw "không thấy icon: $icon" }

$env:CGO_ENABLED = "0"
$env:GOOS = "windows"
$env:GOARCH = "amd64"

New-Item -ItemType Directory -Force -Path $out | Out-Null
$exe = Join-Path $out "MythLab.exe"
$serverExe = Join-Path $out "mythlab-server.exe"
if ($Clean) {
    foreach ($f in @($exe, $serverExe)) {
        if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Force }
    }
    Get-ChildItem -LiteralPath $cmdDir -Filter "*.syso" -File | Remove-Item -Force
}

# 1. Giao diện web (Astro) -> web\dist, qua tools\build-web.ps1 (dùng chung với Android)
$uiNote = ""
$webIndex = Join-Path $webDist "index.html"
if ($SkipWeb) {
    Write-Host "[1/4] Bỏ qua bước dựng giao diện (-SkipWeb)"
} else {
    Write-Host "[1/4] Dựng giao diện (tools\build-web.ps1)"
    try {
        & (Join-Path $repo "tools\build-web.ps1")
    } catch {
        if ($Strict) { throw }
        Write-Warning "Không dựng được giao diện: $($_.Exception.Message)"
        Write-Warning "Tiếp tục với bản giao diện đang có (dùng -Strict để dừng ở đây)."
        $uiNote = " - KHÔNG dựng lại được, có thể đã cũ"
    }
}

# 2. Chép web\dist vào chỗ go:embed đọc (server\internal\webui\dist) - một nguồn duy nhất: server/tools/embedui
$embedIndex = Join-Path $embed "index.html"
$restoreEmbed = $false
if (Test-Path -LiteralPath $webIndex) {
    Write-Host "[2/4] Chép web\dist -> server\internal\webui\dist (go run ./tools/embedui)"
    Push-Location $server
    try {
        $restoreEmbed = $true
        Invoke-Native "embedui" { go run ./tools/embedui }
    } finally { Pop-Location }
    $ui = "web\dist" + $uiNote
} elseif (Test-Path -LiteralPath $embedIndex) {
    if ($Strict) { throw "không có web\dist\index.html để nhúng" }
    if (Test-Placeholder $embed) {
        Write-Warning "Chưa có web\dist: exe sẽ chỉ chứa trang giữ chỗ (API vẫn chạy; có thể dùng --static THƯ_MỤC)."
        $ui = "trang giữ chỗ (chưa có web\dist)"
    } else {
        Write-Warning "Chưa có web\dist: nhúng bản đang nằm trong server\internal\webui\dist."
        $ui = "bản có sẵn trong server\internal\webui\dist"
    }
    Write-Host "[2/4] Không có web\dist - giữ nguyên server\internal\webui\dist"
} else {
    throw "không có giao diện để nhúng: thiếu cả web\dist\index.html lẫn $embedIndex"
}

try {
    # 3. Tài nguyên Windows (icon, manifest DPI, thông tin phiên bản) -> .syso
    Write-Host "[3/4] Sinh rsrc_windows_amd64.syso (go-winres $WinresVersion)"
    Push-Location $cmdDir
    try {
        Invoke-Native "go-winres" { go run "github.com/tc-hib/go-winres@$WinresVersion" make --in winres/winres.json --out rsrc --arch amd64 }
    } finally { Pop-Location }
    if (-not (Test-Path -LiteralPath (Join-Path $cmdDir "rsrc_windows_amd64.syso"))) { throw "go-winres không tạo ra file .syso" }

    Push-Location $server
    try {
        if ($Test) {
            Write-Host "      go vet + go test -short"
            Invoke-Native "go vet" { go vet ./... }
            Invoke-Native "go test" { go test -short ./... }
        }
        # 4. Build
        Write-Host "[4/4] go build"
        Invoke-Native "go build MythLab.exe" { go build -trimpath -ldflags "-H=windowsgui -s -w" -o $exe ./cmd/mythlab }
        Invoke-Native "go build mythlab-server.exe" { go build -trimpath -ldflags "-s -w" -o $serverExe ./cmd/mythlab-server }
    } finally { Pop-Location }
} finally {
    if ($restoreEmbed -and (-not $KeepEmbed)) {
        # trả thư mục nhúng về trạng thái trong git (chỉ còn trang giữ chỗ)
        Push-Location $server
        try { Invoke-Native "embedui -restore" { go run ./tools/embedui -restore } } finally { Pop-Location }
    }
}

foreach ($f in @($exe, $serverExe)) {
    $item = Get-Item -LiteralPath $f
    Write-Host ("Xong: {0}  ({1:N1} MB)" -f $item.FullName, ($item.Length / 1MB))
}
Write-Host "Giao diện nhúng: $ui"
