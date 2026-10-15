"""对 Typst 中的过高图片等比例缩小，并修正 Quarto 搬迁后的图片路径。"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import struct
from pathlib import Path

IMAGE_CALL = re.compile(r'\bimage\(\s*"(?P<path>(?:\\.|[^"\\])*)"(?P<args>[^)]*)\)')
DIMENSION = re.compile(r'\b(?P<name>height|width)\s*:\s*(?P<value>[\d.]+)\s*(?P<unit>in|cm|mm|pt|%)')
UNITS = {"in": 1.0, "cm": 1 / 2.54, "mm": 1 / 25.4, "pt": 1 / 72}


def png_size(path: Path) -> tuple[int, int] | None:
    if not path.is_file() or path.suffix.lower() != ".png":
        return None
    with path.open("rb") as image:
        header = image.read(24)
    if len(header) == 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", header[16:24])
    return None


def fit_figures(typ_path: Path, max_height: float = 7.6, max_width: float = 6.8,
                asset_dir: Path | None = None) -> tuple[int, bool]:
    source = typ_path.read_text(encoding="utf-8")
    resized = 0

    def replace_image(match: re.Match) -> str:
        nonlocal resized
        raw_path = match["path"]
        image_path = json.loads('"' + raw_path + '"')
        resolved_path = typ_path.parent / image_path
        if not resolved_path.is_file() and asset_dir is not None:
            relocated = asset_dir / image_path
            if relocated.is_file():
                image_path = Path(os.path.relpath(relocated, typ_path.parent)).as_posix()
                resolved_path = relocated
        args = match["args"]
        dimensions = {item["name"]: item for item in DIMENSION.finditer(args)}
        inches: dict[str, float] = {}
        for name, item in dimensions.items():
            unit = item["unit"]
            if unit in UNITS:
                inches[name] = float(item["value"]) * UNITS[unit]
            elif name == "width":
                inches[name] = max_width * float(item["value"]) / 100
        size = png_size(resolved_path)
        if size:
            if "width" in inches and "height" not in inches:
                inches["height"] = inches["width"] * size[1] / size[0]
            elif "height" in inches and "width" not in inches:
                inches["width"] = inches["height"] * size[0] / size[1]
        scale = min(1.0, max_height / inches.get("height", max_height),
                    max_width / inches.get("width", max_width))
        if scale < 1:
            resized += 1
            old_height = inches.get("height", 0)
            args = DIMENSION.sub(
                lambda item: f'{item["name"]}: {inches[item["name"]] * scale:.4f}in'
                if item["name"] in inches else item.group(0), args)
            if "height" not in dimensions and "height" in inches:
                args += f', height: {inches["height"] * scale:.4f}in'
            print(f"缩小图片：{Path(image_path).name}，高度 {old_height:.2f}in -> {old_height * scale:.2f}in")
        return "image(" + json.dumps(image_path, ensure_ascii=False) + args + ")"

    updated = IMAGE_CALL.sub(replace_image, source)
    changed = updated != source
    if changed:
        typ_path.write_text(updated, encoding="utf-8")
    return resized, changed


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("typ", type=Path)
    parser.add_argument("max_height", nargs="?", type=float, default=7.6)
    parser.add_argument("--max-width", type=float, default=6.8)
    parser.add_argument("--asset-dir", type=Path)
    args = parser.parse_args()
    if args.max_height <= 0 or args.max_width <= 0:
        parser.error("图片尺寸上限必须大于 0。")
    count, _ = fit_figures(args.typ.resolve(), args.max_height, args.max_width, args.asset_dir)
    print(f"已检查 {args.typ}；缩小 {count} 张图片。")


if __name__ == "__main__":
    main()
