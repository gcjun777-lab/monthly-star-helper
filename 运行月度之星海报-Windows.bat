@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo 开始处理“输入图片”文件夹中的照片...
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0batch_generate_posters.py"
  goto end
)

where python >nul 2>nul
if %errorlevel%==0 (
  python "%~dp0batch_generate_posters.py"
  goto end
)

echo 未检测到 Python。
echo 请先安装 Python 3，并勾选“Add Python to PATH”后再双击运行。
echo 下载地址：https://www.python.org/downloads/
echo.

:end
echo.
echo 处理完成。结果在“输出海报”文件夹中。
pause
