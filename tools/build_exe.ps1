param(
  [string]$Python = ".\.venv\Scripts\python.exe",
  [string]$Name = "Blade Fighters",
  [switch]$OneFile = $true,
  [string]$DistPath = "."
)

$ErrorActionPreference = "Stop"

Write-Host "Using Python: $Python"

# 1) Ensure build deps are installed
& $Python -m pip install --upgrade pip | Out-Host
& $Python -m pip install -r requirements.txt | Out-Host
& $Python -m pip install -r requirements-dev.txt | Out-Host

# 2) Generate .ico from the provided PNG logo
& $Python tools\make_ico.py --input assets\menus\title_wordmark.png --output build\icon.ico | Out-Host

# 3) Build EXE
$onefileFlag = @()
if ($OneFile) { $onefileFlag = @("--onefile") }

$assetsSrc = (Resolve-Path "assets").Path
$iconIco = (Resolve-Path "build\icon.ico").Path
$distOut = (Resolve-Path $DistPath).Path

# NOTE: Windows add-data uses ';' as separator: SRC;DEST
& $Python -m PyInstaller `
  --noconfirm `
  --clean `
  --name $Name `
  --icon "$iconIco" `
  --windowed `
  --specpath build\pyinstaller `
  --workpath build\pyinstaller\work `
  --distpath "$distOut" `
  --add-data "$assetsSrc;assets" `
  @onefileFlag `
  run_bladefighters.py | Out-Host

Write-Host "Build complete. See $distOut\$Name.exe"
