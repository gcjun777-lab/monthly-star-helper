#!/bin/zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "开始处理输入图片文件夹中的照片..."
echo ""
/usr/bin/env python3 "$SCRIPT_DIR/batch_generate_posters.py"
echo ""
echo "处理完成。结果已输出到：$SCRIPT_DIR/输出海报"
echo "按回车键关闭窗口..."
read
