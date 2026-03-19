@echo off
setlocal EnableExtensions

REM One-click builder for Parallels/UNC paths.
REM It copies project to a local temp folder, builds EXE there, then copies dist back.

set "WORK=%TEMP%\SubManagerBuild"

echo [1/7] Preparing local build workspace...
if exist "%WORK%" rmdir /s /q "%WORK%"
mkdir "%WORK%"

REM Map UNC script dir to a temporary drive (important in Parallels shared folders)
pushd "%~dp0"
if errorlevel 1 (
  echo Cannot enter script directory.
  goto :fail
)

set "SRC=%CD%"
set "OUTDIR=%SRC%\dist"

echo [2/7] Copying project to local workspace...
robocopy "%SRC%" "%WORK%" /E /R:1 /W:1 /XD .git __pycache__ build dist .venv venv /XF *.pyc
if %ERRORLEVEL% GEQ 8 (
  echo Copy failed.
  goto :fail
)

pushd "%WORK%"
if errorlevel 1 (
  echo Cannot enter local workspace.
  goto :fail
)

set "PYEXE="
where py >nul 2>nul && set "PYEXE=py -3"
if not defined PYEXE where python >nul 2>nul && set "PYEXE=python"
if not defined PYEXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PYEXE if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PYEXE if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
if not defined PYEXE if exist "C:\Program Files\Python312\python.exe" set "PYEXE=C:\Program Files\Python312\python.exe"
if not defined PYEXE if exist "C:\Program Files\Python311\python.exe" set "PYEXE=C:\Program Files\Python311\python.exe"
if not defined PYEXE if exist "C:\Program Files\Python310\python.exe" set "PYEXE=C:\Program Files\Python310\python.exe"
if not defined PYEXE (
  echo Python not found.
  echo Install Python 3.10+ then retry:
  echo winget install -e --id Python.Python.3.12 --source winget
  goto :fail_local
)

echo Using Python: %PYEXE%

echo [3/7] Installing dependencies...
%PYEXE% -m pip install -r requirements.txt
if errorlevel 1 goto :fail_local

echo [4/7] Installing PyInstaller...
%PYEXE% -m pip install pyinstaller
if errorlevel 1 goto :fail_local

echo [5/7] Cleaning old build in workspace...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [6/7] Building EXE...
%PYEXE% -m PyInstaller --noconfirm --clean --windowed --collect-submodules openpyxl --collect-data openpyxl --hidden-import openpyxl.cell._writer --name SubManager main.py
if errorlevel 1 goto :fail_local

echo [7/7] Copying dist back to project folder...
if not exist "%OUTDIR%" mkdir "%OUTDIR%"
robocopy "%WORK%\dist" "%OUTDIR%" /E /R:1 /W:1
if %ERRORLEVEL% GEQ 8 (
  echo Copy back failed.
  goto :fail_local
)

echo.
echo Build success.
echo EXE: %OUTDIR%\SubManager\SubManager.exe
popd
pause
exit /b 0

:fail_local
popd
:fail
popd >nul 2>nul
echo.
echo Build failed. Please send this window screenshot to support.
pause
exit /b 1
