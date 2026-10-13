"""把普通 Markdown 转成 Quarto 源文件；保留原文，仅转换 Mermaid 围栏。"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

OPEN_FENCE = re.compile(r"^(?P<prefix>[ \t]*(?:>[ \t]*)*)(?P<fence>`{3,}|~{3,})(?P<info>.*)$")


def convert_mermaid(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    current_fence: tuple[str, int] | None = None
    converted = 0
    for index, line in enumerate(lines):
        bare = line.rstrip("\r\n")
        match = OPEN_FENCE.match(bare)
        if not match:
            continue
        fence = match["fence"]
        info = match["info"].strip()
        if current_fence is not None:
            if fence[0] == current_fence[0] and len(fence) >= current_fence[1] and not info:
                current_fence = None
            continue
        current_fence = (fence[0], len(fence))
        if info == "mermaid":
            newline = line[len(bare):]
            lines[index] = f'{match["prefix"]}{fence}{{mermaid}}{newline}'
            converted += 1
    return "".join(lines), converted


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true", help="允许重新生成已有的 .qmd")
    args = parser.parse_args()
    if args.source.suffix.lower() != ".md":
        parser.error("输入必须是 .md 文件。")
    if args.output.exists() and not args.force:
        parser.error(f"目标已存在：{args.output}。直接渲染 .qmd，或用 -Force 重新转换。")
    with args.source.open("r", encoding="utf-8-sig", newline="") as source_file:
        content = source_file.read()
    content, count = convert_mermaid(content)
    first_line = content.splitlines()[0] if content else ""
    if first_line.strip() != "---":
        title = json.dumps(args.source.stem, ensure_ascii=False)
        content = f"---\ntitle: {title}\ndate: today\n---\n\n" + content
    with args.output.open("w", encoding="utf-8", newline="") as target_file:
        target_file.write(content)
    print(f"已生成 {args.output}；转换 {count} 个 Mermaid 代码块。")


if __name__ == "__main__":
    main()
