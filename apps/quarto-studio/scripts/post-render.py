"""Quarto 渲染后：限制图片尺寸，并重新编译发生变化的 PDF。"""
from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT / "output" / "pdf"
spec = importlib.util.spec_from_file_location("fit_figures", Path(__file__).with_name("fit-typst-figures.py"))
fit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fit_module)


def typst_command() -> str:
    override = os.environ.get("QUARTO_TYPST")
    if override and Path(override).is_file():
        return override
    candidates = []
    if os.environ.get("QUARTO_BIN_PATH"):
        candidates.append(Path(os.environ["QUARTO_BIN_PATH"]))
    command = shutil.which("quarto") or shutil.which("quarto.exe")
    if command:
        candidates.append(Path(command).resolve().parent)
    if os.environ.get("LOCALAPPDATA"):
        candidates.append(Path(os.environ["LOCALAPPDATA"]) / "Programs/Quarto/bin")
    for directory in candidates:
        for relative in ("tools/x86_64/typst.exe", "tools/x86_64/typst", "tools/aarch64/typst", "tools/typst"):
            candidate = directory / relative
            if candidate.is_file():
                return str(candidate)
    command = shutil.which("typst")
    if command:
        return command
    raise RuntimeError("未找到 Quarto 内置的 Typst。")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    # Quarto 通过环境变量传入输出文件列表，每行一个项目相对路径。
    output_list = os.environ.get("QUARTO_PROJECT_OUTPUT_FILES")
    if not output_list:
        raise RuntimeError("缺少 Quarto 输出文件列表；请通过 quarto render 或 render.ps1 运行。")
    output_files = output_list.splitlines()
    for filename in output_files:
        pdf = Path(filename)
        if not pdf.is_absolute():
            pdf = PROJECT / pdf
        if pdf.suffix.lower() != ".pdf":
            continue
        pdf = pdf.resolve()
        if not pdf.is_file():
            alternative = OUTPUT / Path(filename)
            if alternative.is_file():
                pdf = alternative.resolve()
            else:
                raise FileNotFoundError(f"找不到 Quarto 输出文件：{pdf}")
        relative = pdf.relative_to(OUTPUT)
        typ = (PROJECT / relative).with_suffix(".typ")
        if not typ.is_file():
            raise FileNotFoundError(f"找不到中间 Typst 文件：{typ}。请启用 keep-typ。")
        source = typ.read_text(encoding="utf-8")
        geometry = re.search(r"#set page\(\s*width: ([0-9.]+)pt,\s*height: ([0-9.]+)pt,\s*margin: \(x: ([0-9.]+)pt,\s*y: ([0-9.]+)pt\)", source)
        max_width, max_height = 6.8, 7.6
        if geometry:
            page_width, page_height, margin_x, margin_y = (float(value) / 72 for value in geometry.groups())
            max_width = max(1.0, page_width - 2 * margin_x)
            max_height = max(1.0, page_height - 2 * margin_y - 1.5)
            # 旁注和通讯模板的正文栏比整页更窄；高图仍按真实正文栏缩放。
            if '/dashing-dept-news/' in source:
                max_width = max(1.0, page_width * 0.68 - margin_x - 18 / 72)
            elif '/styles/kami/layouts.typ' in source:
                if 'layout: "brief"' in source:
                    max_width = max(1.0, (page_width - 2 * margin_x - 23 / 72) / 2)
                elif 'layout: "cards"' in source:
                    # 卡片章节头占据额外高度，给高图留出完整同页空间。
                    max_height = max(1.0, page_height - 2 * margin_y - 2.4)
            elif '/runtime/tufte.typ' in source:
                max_width = max(1.0, page_width - 2 * margin_x - 110 / 72)

        count, changed = fit_module.fit_figures(typ, max_height=max_height, max_width=max_width, asset_dir=pdf.parent)
        if changed:
            command = [typst_command(), "compile", str(typ), str(pdf), "--root", str(PROJECT), "--font-path", str(PROJECT / "fonts")]
            subprocess.run(command, cwd=PROJECT, check=True)
        print(f"PDF 图片检查完成：{pdf.name}，缩小 {count} 张。")


if __name__ == "__main__":
    main()
