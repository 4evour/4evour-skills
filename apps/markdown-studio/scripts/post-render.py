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
    # 在渲染钩子内直接使用 Quarto 自带的 Typst，避免重复启动 Quarto。
    override = os.environ.get("QUARTO_TYPST")
    if override and Path(override).is_file():
        return override
    quarto_bin = os.environ.get("QUARTO_BIN_PATH")
    if quarto_bin:
        candidate = Path(quarto_bin) / "tools" / "x86_64" / "typst.exe"
        if candidate.is_file():
            return str(candidate)
    for name in ("quarto.exe", "quarto"):
        command = shutil.which(name)
        if command:
            candidate = Path(command).parent / "tools" / "x86_64" / "typst.exe"
            if candidate.is_file():
                return str(candidate)
    candidate = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Quarto" / "bin" / "tools" / "x86_64" / "typst.exe"
    if candidate.is_file():
        return str(candidate)
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
        geometry = re.search(r'#set page\(\s*paper: "([^"]+)",\s*margin: \(x: ([0-9.]+)(in|cm|mm|pt),\s*y: ([0-9.]+)(in|cm|mm|pt),', source)
        max_width, max_height = 6.8, 7.6
        if geometry:
            page_width, page_height = (8.2677, 11.6929) if geometry[1] == "a4" else (8.5, 11)
            margin_x = float(geometry[2]) * fit_module.UNITS[geometry[3]]
            margin_y = float(geometry[4]) * fit_module.UNITS[geometry[5]]
            max_width = max(1.0, page_width - 2 * margin_x)
            max_height = max(1.0, page_height - 2 * margin_y - 1.7)
        count, changed = fit_module.fit_figures(typ, max_height=max_height, max_width=max_width, asset_dir=pdf.parent)
        if changed:
            command = [typst_command(), "compile", str(typ), str(pdf), "--root", str(PROJECT), "--font-path", str(PROJECT / "fonts")]
            subprocess.run(command, cwd=PROJECT, check=True)
        print(f"PDF 图片检查完成：{pdf.name}，缩小 {count} 张。")


if __name__ == "__main__":
    main()
