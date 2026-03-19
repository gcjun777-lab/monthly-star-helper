#!/bin/bash
set -e
cd "$(dirname "$0")"

python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

rm -rf build dist

pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --hidden-import openpyxl.cell._writer \
  --name "订阅管理助手" \
  main.py

echo "打包完成: dist/订阅管理助手.app"
