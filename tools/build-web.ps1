# Dựng giao diện web (Astro) -> web\dist. Một nguồn duy nhất cho mọi script build (desktop, Android).
#   powershell -ExecutionPolicy Bypass -File tools\build-web.ps1 [-Force] [-Embed]
#   -Force   dựng lại dù web\dist còn mới hơn mã nguồn
#   -Embed   dựng xong thì chép luôn vào server\internal\webui\dist (go run ./tools/embedui)
# Chỉ chạy `npm ci` khi chưa cài hoặc package-lock.json mới hơn lần cài (npm ci xoá sạch node_modules).
param([switch]$Force, [switch]$Embed)
$ErrorActionPreference = "Stop"

$repo    = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$web     = Join-Path $repo "web"
$webDist = Join-Path $web "dist"
$webIndex = Join-Path $webDist "index.html"

function Invoke-Native {
    # stderr của lệnh ngoài không được biến thành lỗi PowerShell, chỉ mã thoát mới tính.
    param([string]$What, [scriptblock]$Command)
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { & $Command } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "$What lỗi (mã $LASTEXITCODE)" }
}

function Get-NewestWrite([string[]]$Paths) {
    $newest = [datetime]::MinValue
    foreach ($p in $Paths) {
        if (-not (Test-Path -LiteralPath $p)) { continue }
        $item = Get-Item -LiteralPath $p
        if ($item.PSIsContainer) { $files = Get-ChildItem -LiteralPath $p -Recurse -File -Force } else { $files = @($item) }
        foreach ($f in $files) { if ($f.LastWriteTimeUtc -gt $newest) { $newest = $f.LastWriteTimeUtc } }
    }
    return $newest
}

if (-not (Test-Path -LiteralPath (Join-Path $web "package.json"))) { throw "không thấy $web\package.json" }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw "không thấy 'npm' trong PATH" }

$sources = @("src", "public", "package.json", "package-lock.json", "astro.config.mjs", "astro.config.ts", "tsconfig.json") |
    ForEach-Object { Join-Path $web $_ }
$stale = $Force -or (-not (Test-Path -LiteralPath $webIndex)) -or
    ((Get-NewestWrite $sources) -gt (Get-Item -LiteralPath $webIndex).LastWriteTimeUtc)

if (-not $stale) {
    Write-Host "web\dist còn mới - không dựng lại (dùng -Force để ép)"
} else {
    Write-Host "Dựng giao diện (npm run build trong web\)"
    Push-Location $web
    try {
        $lock = Join-Path $web "package-lock.json"
        $installed = Join-Path $web "node_modules\.package-lock.json"
        $needInstall = (-not (Test-Path -LiteralPath $installed)) -or
            ((Test-Path -LiteralPath $lock) -and
             ((Get-Item -LiteralPath $lock).LastWriteTimeUtc -gt (Get-Item -LiteralPath $installed).LastWriteTimeUtc))
        if ($needInstall) {
            if (Test-Path -LiteralPath $lock) { Invoke-Native "npm ci" { npm ci --no-audit --no-fund } }
            else { Invoke-Native "npm install" { npm install --no-audit --no-fund } }
        }
        Invoke-Native "npm run build" { npm run build }
    } finally { Pop-Location }
    if (-not (Test-Path -LiteralPath $webIndex)) { throw "npm run build không tạo ra web\dist\index.html" }
}

if ($Embed) {
    Push-Location (Join-Path $repo "server")
    try { Invoke-Native "embedui" { go run ./tools/embedui } } finally { Pop-Location }
}
