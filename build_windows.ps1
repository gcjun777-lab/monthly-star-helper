$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

function Get-PythonCmd {
    if (Get-Command py -ErrorAction SilentlyContinue) { return "py" }
    if (Get-Command python -ErrorAction SilentlyContinue) { return "python" }
    throw "Python not found. Install Python 3.10+ first."
}

$py = Get-PythonCmd

Write-Host "[1/4] Installing dependencies..."
& $py -m pip install -r requirements.txt

Write-Host "[2/4] Installing PyInstaller..."
& $py -m pip install pyinstaller

Write-Host "[3/4] Cleaning old build..."
if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path dist) { Remove-Item dist -Recurse -Force }

Write-Host "[4/4] Building EXE..."
& $py -m PyInstaller --noconfirm --clean --windowed --collect-submodules openpyxl --collect-data openpyxl --hidden-import openpyxl.cell._writer --name SubManager main.py

Write-Host ""
Write-Host "Build success."
Write-Host "EXE path: dist\SubManager\SubManager.exe"
