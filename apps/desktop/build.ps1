# Đóng gói MythLab desktop → apps\desktop\dist\MythLab\MythLab.exe
# Dùng: powershell -ExecutionPolicy Bypass -File apps\desktop\build.ps1 [-Python python] [-Clean]
param([string]$Python = "python", [switch]$Clean)
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$venv = Join-Path $here ".venv"
$py = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path $py)) {
    Write-Host "Tạo venv: $venv"
    & $Python -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw "không tạo được venv" }
}
& $py -m pip install --disable-pip-version-check -q -r (Join-Path $here "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "pip install lỗi" }

if ($Clean) { Remove-Item -Recurse -Force (Join-Path $here "build"), (Join-Path $here "dist") -ErrorAction SilentlyContinue }
Push-Location $here
try {
    & $py -m PyInstaller --noconfirm --distpath dist --workpath build MythLab.spec
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller lỗi" }
} finally { Pop-Location }
Write-Host "Xong: $(Join-Path $here 'dist\MythLab\MythLab.exe')"
