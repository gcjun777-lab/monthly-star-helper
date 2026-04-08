#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


BACKEND_NAME = "poster-backend"
TEMPLATE_NAME = "月度之星个人海报-素材模板4.png"
MODEL_PATH = Path.home() / ".u2net" / "u2net.onnx"


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    backend_dist = root / "build" / "backend"
    backend_build = root / "build" / "pyinstaller"

    if backend_dist.exists():
        shutil.rmtree(backend_dist)
    backend_dist.mkdir(parents=True, exist_ok=True)

    separator = ";" if sys.platform.startswith("win") else ":"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--console",
        "--distpath",
        str(backend_dist),
        "--workpath",
        str(backend_build),
        "--specpath",
        str(root / "build"),
        "--name",
        BACKEND_NAME,
        "--copy-metadata",
        "pymatting",
        "--copy-metadata",
        "rembg",
        "--copy-metadata",
        "onnxruntime",
        "--add-data",
        f"{root / TEMPLATE_NAME}{separator}.",
    ]

    if MODEL_PATH.exists():
        cmd.extend([
            "--add-data",
            f"{MODEL_PATH}{separator}.u2net",
        ])

    cmd.append(str(root / "batch_generate_posters.py"))
    run(cmd, root)

    print(f"Backend build complete: {backend_dist / (BACKEND_NAME + '.exe')}")


if __name__ == "__main__":
    main()