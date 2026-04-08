#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    subprocess.run(cmd, cwd=str(cwd), check=True, env=merged_env)


def main() -> None:
    root = Path(__file__).resolve().parent
    npm_cmd = 'npm.cmd' if sys.platform.startswith('win') else 'npm'
    run(
        [npm_cmd, 'run', 'dist'],
        root,
        env={
            'ELECTRON_MIRROR': 'https://npmmirror.com/mirrors/electron/',
            'ELECTRON_BUILDER_BINARIES_MIRROR': 'https://npmmirror.com/mirrors/electron-builder-binaries/',
        },
    )

    print('')
    print(f"打包完成，安装包输出目录: {root / 'release'}")


if __name__ == '__main__':
    main()