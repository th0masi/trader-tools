Param(
    [switch]$OneFile = $true,
    [string]$Entry = "app.py"
)

$ErrorActionPreference = "Stop"

Write-Host "Creating virtual environment..." -ForegroundColor Cyan
if (-Not (Test-Path ".venv")) {
    python -m venv .venv
}

Write-Host "Activating venv..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip | Out-Null

Write-Host "Installing requirements..." -ForegroundColor Cyan
pip install -r requirements.txt | Out-Null

Write-Host "Preparing assets..." -ForegroundColor Cyan
if (-Not (Test-Path "assets\icons")) { New-Item -ItemType Directory -Path "assets\icons" | Out-Null }

Write-Host "Building with PyInstaller..." -ForegroundColor Cyan
$iconIcoCandidates = @("assets\icons\trade_helper.ico", "assets\icons\icon.ico")
$iconIco = $null
foreach ($p in $iconIcoCandidates) { if (Test-Path $p) { $iconIco = $p; break } }

Write-Host "Excluding alternate Qt bindings (PySide*) to avoid conflicts..." -ForegroundColor Cyan
$excludeArgs = @("--exclude-module", "PySide6", "--exclude-module", "PySide2", "--exclude-module", "PyQt5")

$argsList = @()
if ($OneFile) { $argsList += "--onefile" }
$argsList += @("--name", "Trade Helper")
if ($iconIco) { $argsList += @("--icon", (Resolve-Path $iconIco)) } else { Write-Host "ICO not found, building without icon." -ForegroundColor Yellow }
$argsList += @("--noconsole", "--clean", "--add-data", "assets;assets")
$argsList += $excludeArgs
$argsList += $Entry

pyinstaller @argsList | Out-Null

if (-Not (Test-Path "dist")) {
    Write-Host "Build failed: 'dist' directory not created." -ForegroundColor Red
    exit 1
}
$exePath = Join-Path "dist" "Trade Helper.exe"
if (-Not (Test-Path $exePath)) {
    Write-Host "Build may have failed. Executable not found: $exePath" -ForegroundColor Yellow
} else {
    Write-Host "Build completed. Executable: $exePath" -ForegroundColor Green
}

