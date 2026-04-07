@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo 正在检查 Python...
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -m pip install pyinstaller pillow rembg onnxruntime numpy
  py -3 "%~dp0build_windows_exe.py"
  goto end
)

where python >nul 2>nul
if %errorlevel%==0 (
  python -m pip install pyinstaller pillow rembg onnxruntime numpy
  python "%~dp0build_windows_exe.py"
  goto end
)

echo 未检测到 Python。
echo 请先安装 Python 3，并勾选“Add Python to PATH”。
echo 下载地址：https://www.python.org/downloads/

:end
echo.
pause
