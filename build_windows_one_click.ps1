$ErrorActionPreference = "Stop"

function Get-PythonCmd {
    if (Get-Command py -ErrorAction SilentlyContinue) { return "py" }
    if (Get-Command python -ErrorAction SilentlyContinue) { return "python" }
    throw "Python not found. Install Python 3.10+ first."
}

$src = Split-Path -Parent $MyInvocation.MyCommand.Path
$work = Join-Path $env:TEMP "SubManagerBuild"
$outDir = Join-Path $src "dist"

Write-Host "[1/7] Preparing local build workspace..."
if (Test-Path $work) { Remove-Item $work -Recurse -Force }
New-Item -ItemType Directory -Path $work | Out-Null

Write-Host "[2/7] Copying project to local workspace..."
robocopy $src $work /E /R:1 /W:1 /XD .git __pycache__ build dist .venv venv /XF *.pyc | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Copy failed." }

Set-Location $work
$py = Get-PythonCmd

Write-Host "[3/7] Installing dependencies..."
& $py -m pip install -r requirements.txt

Write-Host "[4/7] Installing PyInstaller..."
& $py -m pip install pyinstaller

Write-Host "[5/7] Cleaning old build in workspace..."
if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path dist) { Remove-Item dist -Recurse -Force }

Write-Host "[6/7] Building EXE..."
& $py -m PyInstaller --noconfirm --clean --windowed --collect-submodules openpyxl --collect-data openpyxl --hidden-import openpyxl.cell._writer --name SubManager main.py

Write-Host "[7/7] Copying dist back to project folder..."
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
robocopy (Join-Path $work "dist") $outDir /E /R:1 /W:1 | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Copy back failed." }

Write-Host ""
Write-Host "Build success."
Write-Host "EXE path: $outDir\SubManager\SubManager.exe"
