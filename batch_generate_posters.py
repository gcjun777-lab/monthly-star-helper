#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    bundled_model_home = Path(sys._MEIPASS) / ".u2net"
    if bundled_model_home.exists():
        os.environ.setdefault("U2NET_HOME", str(bundled_model_home))

from rembg import remove


TEXT_COLOR = (246, 246, 246, 255)
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
FILENAME_PATTERN = re.compile(r"^(?P<dept>.+)-(?P<name>.+)-(?P<yyyymm>\d{6})$")
TEMPLATE_NAME = "月度之星个人海报-素材模板4.png"
INPUT_DIR_NAME = "输入图片"
OUTPUT_DIR_NAME = "输出海报"
OUTPUT_SUFFIX = "-月度之星.png"
FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/msyhbd.ttc"),
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
]


@dataclass(frozen=True)
class TextSpec:
    key: str
    box: tuple[int, int, int, int]
    angle: float
    max_size: int
    min_size: int


@dataclass(frozen=True)
class SubjectLayout:
    image: Image.Image
    paste_x: int
    paste_y: int


TEXT_SPECS = [
    TextSpec("dept", (151, 1609, 461, 1721), 7.0, 120, 70),
    TextSpec("name", (607, 1658, 959, 1801), 6.5, 138, 84),
    TextSpec("date", (934, 1766, 1339, 1874), 5.5, 98, 60),
]

SUBJECT_CENTER_X = 750
SUBJECT_MAX_WIDTH = 720
SUBJECT_TARGET_HEIGHT = 850
SUBJECT_BOTTOM_Y = 1586
RIBBON_TOP = 1548


@dataclass(frozen=True)
class BatchConfig:
    input_dir: Path
    output_dir: Path
    template_path: Path
    font_path: Path
    suffix: str = OUTPUT_SUFFIX


@dataclass(frozen=True)
class BatchResult:
    ok_count: int
    fail_count: int
    details: list[str]


def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_resource_path(name: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / name
    return Path(__file__).resolve().parent / name


def detect_font_path() -> Path:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "未找到可用字体，请通过 --font 指定一个支持中文的字体文件，例如 C:/Windows/Fonts/msyhbd.ttc"
    )


def build_default_config() -> BatchConfig:
    app_dir = get_app_dir()
    return BatchConfig(
        input_dir=app_dir / INPUT_DIR_NAME,
        output_dir=app_dir / OUTPUT_DIR_NAME,
        template_path=get_resource_path(TEMPLATE_NAME),
        font_path=detect_font_path(),
        suffix=OUTPUT_SUFFIX,
    )


def parse_args() -> argparse.Namespace:
    default = build_default_config()
    parser = argparse.ArgumentParser(description="批量生成月度之星海报")
    parser.add_argument("--input", default=str(default.input_dir), help="输入图片目录，文件名格式：部门-姓名-YYYYMM")
    parser.add_argument("--template", default=str(default.template_path), help="模板图片路径")
    parser.add_argument("--output-dir", default=str(default.output_dir), help="输出目录")
    parser.add_argument("--font", default=str(default.font_path), help="字体文件路径")
    parser.add_argument("--suffix", default=default.suffix, help="输出文件后缀")
    return parser.parse_args()


def ensure_runtime_dirs(config: BatchConfig) -> None:
    config.input_dir.mkdir(parents=True, exist_ok=True)
    config.output_dir.mkdir(parents=True, exist_ok=True)


def collect_inputs(input_path: Path) -> list[Path]:
    if not input_path.exists():
        input_path.mkdir(parents=True, exist_ok=True)
        raise FileNotFoundError(f"未找到输入目录，已自动创建: {input_path}")
    if not input_path.is_dir():
        raise FileNotFoundError(f"输入路径不是文件夹: {input_path}")

    files: list[Path] = []
    for path in sorted(input_path.iterdir()):
        if path.suffix in SUPPORTED_EXTS and "月度之星" not in path.name:
            files.append(path)
    return files


def parse_filename(path: Path) -> dict[str, str]:
    match = FILENAME_PATTERN.match(path.stem)
    if not match:
        raise ValueError(f"文件名不符合规则: {path.name}")

    dept = match.group("dept")
    name = match.group("name")
    yyyymm = match.group("yyyymm")
    year = yyyymm[:4]
    month = str(int(yyyymm[4:6]))
    return {"dept": dept, "name": name, "date": f"{year}年{month}月"}


def extract_subject(photo_path: Path) -> SubjectLayout:
    with photo_path.open("rb") as fh:
        subject = Image.open(BytesIO(remove(fh.read()))).convert("RGBA")

    alpha_box = subject.split()[-1].getbbox()
    if not alpha_box:
        raise ValueError(f"抠图失败: {photo_path.name}")

    subject = subject.crop(alpha_box)
    width, height = subject.size
    ratio = height / max(width, 1)

    bottom_ratio = 0.84
    target_height = SUBJECT_TARGET_HEIGHT
    if ratio >= 1.9:
        bottom_ratio = 0.72
        target_height = 800
    elif ratio >= 1.65:
        bottom_ratio = 0.78
        target_height = 820

    subject = subject.crop((0, int(height * 0.01), width, int(height * bottom_ratio)))
    scale = target_height / subject.height
    scaled_width = int(subject.width * scale)
    if scaled_width > SUBJECT_MAX_WIDTH:
        scale = SUBJECT_MAX_WIDTH / subject.width

    subject = subject.resize(
        (int(subject.width * scale), int(subject.height * scale)),
        Image.Resampling.LANCZOS,
    )
    alpha = subject.split()[-1].filter(ImageFilter.GaussianBlur(0.8))
    subject.putalpha(alpha)

    alpha_np = np.array(alpha)
    upper_limit = max(1, int(alpha_np.shape[0] * 0.58))
    points = np.argwhere(alpha_np[:upper_limit, :] > 16)
    center_x = float(points[:, 1].mean()) if len(points) else subject.width / 2

    paste_x = int(round(SUBJECT_CENTER_X - center_x))
    paste_y = SUBJECT_BOTTOM_Y - subject.height
    return SubjectLayout(subject, paste_x, paste_y)


def fit_text_layer(text: str, spec: TextSpec, font_path: Path) -> Image.Image:
    x0, y0, x1, y1 = spec.box
    box_width = x1 - x0
    box_height = y1 - y0

    for size in range(spec.max_size, spec.min_size - 1, -1):
        font = ImageFont.truetype(str(font_path), size)
        probe = Image.new("RGBA", (2400, 1200), (0, 0, 0, 0))
        drawer = ImageDraw.Draw(probe)
        bbox = drawer.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        layer = Image.new("RGBA", (text_width + 220, text_height + 220), (0, 0, 0, 0))
        drawer = ImageDraw.Draw(layer)
        drawer.text((110, 110), text, font=font, fill=TEXT_COLOR)
        rotated = layer.rotate(spec.angle, resample=Image.Resampling.BICUBIC, expand=True)
        alpha_box = rotated.split()[-1].getbbox()
        if not alpha_box:
            continue
        rotated = rotated.crop(alpha_box)
        if rotated.width <= box_width and rotated.height <= box_height:
            return rotated

    raise ValueError(f"文字无法放入指定区域: {text}")


def compose_poster(photo_path: Path, template_path: Path, output_path: Path, font_path: Path) -> None:
    text_values = parse_filename(photo_path)
    base = Image.open(template_path).convert("RGBA")
    clean_template = base.copy()
    subject = extract_subject(photo_path)

    base.alpha_composite(subject.image, (subject.paste_x, subject.paste_y))
    base.alpha_composite(clean_template.crop((0, RIBBON_TOP, base.width, 1998)), (0, RIBBON_TOP))

    for spec in TEXT_SPECS:
        layer = fit_text_layer(text_values[spec.key], spec, font_path)
        x0, y0, x1, y1 = spec.box
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        base.alpha_composite(layer, (cx - layer.width // 2, cy - layer.height // 2))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(output_path, quality=96)


def run_batch(config: BatchConfig, progress: callable | None = None) -> BatchResult:
    if not config.template_path.exists():
        raise FileNotFoundError(f"未找到模板: {config.template_path}")
    if not config.font_path.exists():
        raise FileNotFoundError(f"未找到字体: {config.font_path}")

    ensure_runtime_dirs(config)
    files = collect_inputs(config.input_dir)
    if not files:
        raise FileNotFoundError(
            f"输入目录中没有可处理图片: {config.input_dir}\n请把照片放进去，文件名格式为：部门-姓名-YYYYMM"
        )

    ok_count = 0
    fail_count = 0
    details: list[str] = []
    for photo_path in files:
        try:
            out_name = f"{photo_path.stem}{config.suffix}"
            output_path = config.output_dir / out_name
            compose_poster(photo_path, config.template_path, output_path, config.font_path)
            line = f"OK  {photo_path.name} -> {output_path.name}"
            ok_count += 1
        except Exception as exc:  # noqa: BLE001
            line = f"ERR {photo_path.name} -> {exc}"
            fail_count += 1

        details.append(line)
        if progress:
            progress(line)

    summary = f"完成：成功 {ok_count}，失败 {fail_count}"
    details.append(summary)
    if progress:
        progress(summary)
    return BatchResult(ok_count=ok_count, fail_count=fail_count, details=details)


def config_from_args(args: argparse.Namespace) -> BatchConfig:
    return BatchConfig(
        input_dir=Path(args.input).expanduser(),
        output_dir=Path(args.output_dir).expanduser(),
        template_path=Path(args.template).expanduser(),
        font_path=Path(args.font).expanduser(),
        suffix=args.suffix,
    )


def main() -> None:
    args = parse_args()
    result = run_batch(config_from_args(args), progress=print)
    if result.fail_count:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(exc)
        sys.exit(1)
