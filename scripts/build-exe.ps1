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

function Remove-TreeWithRetry {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [int]$Attempts = 6
    )
    if (-not (Test-Path $Path)) { return $true }
    for ($i = 1; $i -le $Attempts; $i++) {
        try {
            # Clear read-only bits that sometimes block rmtree on Windows.
            Get-ChildItem -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue |
                ForEach-Object { $_.Attributes = 'Normal' }
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
            return $true
        } catch {
            if ($i -eq $Attempts) {
                # Last resort: rename aside so PyInstaller can create a fresh build dir.
                $stamp = Get-Date -Format "yyyyMMddHHmmss"
                $aside = "${Path}.old-$stamp"
                try {
                    Rename-Item -LiteralPath $Path -NewName (Split-Path $aside -Leaf) -ErrorAction Stop
                    Write-Warning "Could not delete '$Path' (locked). Renamed to '$aside'."
                    return $true
                } catch {
                    Write-Warning "Could not remove or rename '$Path': $($_.Exception.Message)"
                    return $false
                }
            }
            Start-Sleep -Milliseconds (400 * $i)
        }
    }
    return $false
}

# Pre-clean so PyInstaller's --clean does not hit WinError 5 on locked localpycs.
# Close any running surf-forecast.exe first if the copy step fails later.
Write-Host "Cleaning previous build artifacts..."
$null = Remove-TreeWithRetry (Join-Path $root "build\surf-forecast")
$null = Remove-TreeWithRetry (Join-Path $root "build")
# Keep dist\surf-forecast.exe removal soft — may be locked if the exe is running.
if (Test-Path (Join-Path $root "dist\surf-forecast.exe")) {
    try {
        Remove-Item (Join-Path $root "dist\surf-forecast.exe") -Force -ErrorAction Stop
    } catch {
        Write-Warning "dist\surf-forecast.exe is locked (close the running app if open)."
    }
}

& $python -m pip install -q pyinstaller
# Avoid --clean: on Windows it often fails with Acceso denegado on build\...\localpycs
# when Defender/indexers hold the folder. We already cleaned above.
& $python -m PyInstaller --noconfirm (Join-Path $root "surf-forecast.spec")
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

$built = Join-Path $root "dist\surf-forecast.exe"
$dest = Join-Path $root "surf-forecast.exe"
if (-not (Test-Path $built)) { throw "Expected output missing: $built" }
Copy-Item $built $dest -Force

$configDest = Join-Path $root "dist\config"
if (Test-Path $configDest) { Remove-Item $configDest -Recurse -Force }
Copy-Item (Join-Path $root "config") $configDest -Recurse

Write-Host "Built $dest"
Write-Host "Also in dist\ with a copy of config\ for a portable folder."
Write-Host "Run: .\surf-forecast.exe"
Write-Host "Or:  .\dist\surf-forecast.exe"
