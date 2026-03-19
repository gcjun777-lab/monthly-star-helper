@echo off
setlocal EnableExtensions

REM Always map script directory (supports UNC path like \\Mac\Home\...)
pushd "%~dp0"
if errorlevel 1 (
  echo Failed to enter script directory. Copy project to local disk and retry.
  pause
  exit /b 1
)

set "PYEXE="
where py >nul 2>nul && set "PYEXE=py -3"
if not defined PYEXE where python >nul 2>nul && set "PYEXE=python"
if not defined PYEXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PYEXE if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PYEXE if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
if not defined PYEXE (
  echo Python not found. Install Python 3.10+ and enable PATH.
  popd
  pause
  exit /b 1
)

echo [1/4] Installing dependencies...
%PYEXE% -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo [2/4] Installing PyInstaller...
%PYEXE% -m pip install pyinstaller
if errorlevel 1 goto :fail

echo [3/4] Cleaning old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [4/4] Building EXE...
%PYEXE% -m PyInstaller --noconfirm --clean --windowed --collect-submodules openpyxl --collect-data openpyxl --hidden-import openpyxl.cell._writer --name SubManager main.py
if errorlevel 1 goto :fail

echo.
echo Build success.
echo EXE path: dist\SubManager\SubManager.exe
popd
pause
exit /b 0

:fail
echo.
echo Build failed. Please screenshot this window and send it to me.
popd
pause
exit /b 1
