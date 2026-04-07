#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "月度之星海报生成器"
APP_EXE = f"{APP_NAME}.exe"
TEMPLATE_NAME = "月度之星个人海报-素材模板4.png"
MODEL_PATH = Path.home() / ".u2net" / "u2net.onnx"
INPUT_DIR_NAME = "输入图片"
OUTPUT_DIR_NAME = "输出海报"
README_NAME = "使用说明.txt"
README_CONTENT = """使用方法：
1. 把要处理的照片放进“输入图片”文件夹。
2. 文件名必须是：部门-姓名-YYYYMM
   例如：制造部-张三-202603.jpg
3. 双击“月度之星海报生成器.exe”打开窗口。
4. 在窗口中点击“开始生成”。
5. 生成好的海报会出现在“输出海报”文件夹。

说明：
- 这是 GUI 版本，双击不会弹黑色命令行窗口。
- 输入图片、输出海报文件夹已经预先配置好，直接使用即可。
- 模板和抠图模型已内置进 EXE，不需要额外安装 Python。
- 如果需要，也可以在界面里改成别的输入输出目录。
"""


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def prepare_dist(root: Path, dist_dir: Path) -> None:
    (dist_dir / INPUT_DIR_NAME).mkdir(parents=True, exist_ok=True)
    (dist_dir / OUTPUT_DIR_NAME).mkdir(parents=True, exist_ok=True)
    (dist_dir / README_NAME).write_text(README_CONTENT, encoding="utf-8")

    legacy_bat = dist_dir / "双击运行生成海报.bat"
    if legacy_bat.exists():
        legacy_bat.unlink()

    portable_dir = root / f"{APP_NAME}-可直接发人使用"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True, exist_ok=True)

    for item in dist_dir.iterdir():
        target = portable_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def main() -> None:
    root = Path(__file__).resolve().parent
    dist_dir = root / "dist"
    build_dir = root / "build"

    separator = ";" if sys.platform.startswith("win") else ":"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        "--copy-metadata",
        "pymatting",
        "--copy-metadata",
        "rembg",
        "--copy-metadata",
        "onnxruntime",
        "--collect-all",
        "rembg",
        "--collect-all",
        "onnxruntime",
        "--add-data",
        f"{root / TEMPLATE_NAME}{separator}.",
    ]

    if MODEL_PATH.exists():
        cmd.extend([
            "--add-data",
            f"{MODEL_PATH}{separator}.u2net",
        ])

    cmd.append(str(root / "gui_launcher.py"))

    run(cmd, root)
    prepare_dist(root, dist_dir)
    print()
    print(f"打包完成，EXE 位于: {dist_dir / APP_EXE}")
    print(f"临时构建目录: {build_dir}")


if __name__ == "__main__":
    main()
