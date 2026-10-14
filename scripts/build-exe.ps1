# Build a single console .exe (same idea as:
#   go build -o binlog-explorer.exe .\cmd\binlog-explorer
# in db-log-explorer).
$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Missing .venv. Create it and install the package first (see quickstart.md)."
}

& $python -m pip install -q pyinstaller
& $python -m PyInstaller --noconfirm --clean (Join-Path $root "surf-forecast.spec")
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

$built = Join-Path $root "dist\surf-forecast.exe"
$dest = Join-Path $root "surf-forecast.exe"
Copy-Item $built $dest -Force

$configDest = Join-Path $root "dist\config"
if (Test-Path $configDest) { Remove-Item $configDest -Recurse -Force }
Copy-Item (Join-Path $root "config") $configDest -Recurse

Write-Host "Built $dest"
Write-Host "Also in dist\ with a copy of config\ for a portable folder."
Write-Host "Run: .\surf-forecast.exe"
Write-Host "Or:  .\dist\surf-forecast.exe"
