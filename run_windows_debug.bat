@echo off
setlocal
pushd "%~dp0"

if not exist "dist\订阅管理助手\订阅管理助手.exe" (
  echo 未找到 EXE，请先运行 build_windows.bat
  popd
  pause
  exit /b 1
)

echo 正在启动（调试模式）...
echo 若报错请将本窗口截图发给我。
echo.
"dist\订阅管理助手\订阅管理助手.exe"

echo.
echo 程序已退出。请按任意键关闭窗口。
popd
pause
