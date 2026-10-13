"""下载固定版本的项目字体，验证 SHA256，并准备前端字体资源。"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import shutil
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
FONT_ROOT = ROOT / "fonts"
PUBLIC_ROOT = ROOT / "md2card" / "public" / "fonts"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_font(font: dict, cache: Path | None) -> str:
    target = FONT_ROOT / font["file"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or digest(target) != font["sha256"]:
        cached = cache / font["file"] if cache else None
        if cached and cached.is_file() and digest(cached) == font["sha256"]:
            shutil.copyfile(cached, target)
        else:
            url = quote(font["download_url"], safe=":/%")
            request = Request(url, headers={"User-Agent": "4evour-markdown-studio"})
            with urlopen(request, timeout=120) as response:
                content = response.read()
            if hashlib.sha256(content).hexdigest() != font["sha256"]:
                raise ValueError(f"字体校验失败：{font['label']}")
            target.write_bytes(content)
    license_path = target.parent / "OFL.txt"
    if not license_path.is_file():
        raise FileNotFoundError(f"缺少字体许可证：{license_path}")
    shutil.copyfile(target, PUBLIC_ROOT / target.name)
    shutil.copyfile(license_path, PUBLIC_ROOT / (target.stem + "-OFL.txt"))
    return font["family"]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, help="从已有字体目录复制已校验的文件，避免重复下载")
    args = parser.parse_args()
    fonts = json.loads((FONT_ROOT / "manifest.json").read_text(encoding="utf-8"))
    PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)
    errors = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(prepare_font, font, args.cache): font for font in fonts}
        for future in as_completed(futures):
            try:
                print(f"字体已准备：{future.result()}", flush=True)
            except Exception as error:
                errors.append(f"{futures[future]['label']}：{error}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"已校验并准备 {len(fonts)} 款开源字体。")


if __name__ == "__main__":
    main()
