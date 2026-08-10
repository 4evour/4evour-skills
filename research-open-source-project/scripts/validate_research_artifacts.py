#!/usr/bin/env python3
"""校验开源项目调研产物是否满足结构约定。"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "source-state.md": ["# 源码状态", "- 提交：", "- 调研日期："],
    "evidence-map.md": [
        "## 源码状态",
        "## README 复用表",
        "## 官方主张",
        "## 架构",
        "## 代码证据",
        "## 工程证据",
        "## 限制",
        "## 矛盾",
        "## 开放问题",
    ],
    "thesis.md": [
        "## 核心判断",
        "## 常见误读",
        "## 支撑证据",
        "## 最强反方观点",
        "## 成立条件",
        "## 尚未证明",
    ],
    "claim-ledger.md": [
        "| ID | 类型 | 论断 | 证据 | 置信度 | 文章位置 |",
    ],
    "article.md": ["# "],
    "visual-plan.md": [
        "| ID | 目的 | Claim IDs | 来源类型 | 来源/路径 | 处理方式 | 状态 |",
    ],
}

SOCIAL_PLAN_FILES = {
    "channel-strategy.md": [
        "# 渠道策略",
        "- 执行模式：",
        "- 核心收获：",
        "## 图片与正文分工",
    ],
    "card-script.md": [
        "| 页码 | 本页问题 | 核心结论 | 机制或示例 | 视觉关系 | Claim IDs | 精确文字 | 禁止添加 |",
    ],
    "social-copy.md": [
        "# 发布文案",
        "## 封面标题",
        "## 发布标题",
        "## 正文",
        "## 仅在正文补充的证据与限制",
        "## 标签",
    ],
}

SOCIAL_FINAL_FILES = {
    "image-review.md": [
        "| 页码 | 文件 | 实际尺寸 | 事实 | 讲解 | 视觉 | 生产 | 问题 | 处理 |",
    ],
}

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CODE_PATH_RE = re.compile(
    r"`[^`\n]+\.(?:py|ts|tsx|js|jsx|go|rs|java|kt|rb|php|cs|cpp|c|h|md)`"
)
CLAIM_TYPE_RE = re.compile(r"\|\s*C-\d+\s*\|\s*(FACT|INFERENCE|OPINION|OPEN)\s*\|")
CARD_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.+)$", re.MULTILINE)
REVIEW_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.+)$", re.MULTILINE)
DIMENSION_RE = re.compile(r"\b\d{3,5}\s*[x×]\s*\d{3,5}\b", re.IGNORECASE)
UNSTABLE_HOOK_RE = re.compile(
    r"(?:GitHub\s*)?(?:爆火|很火|新星项目|热门项目)", re.IGNORECASE
)


def validate(folder: Path, mode: str = "research") -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    required_files = dict(REQUIRED_FILES)
    if mode in {"social-plan", "social-final"}:
        required_files.update(SOCIAL_PLAN_FILES)
    if mode == "social-final":
        required_files.update(SOCIAL_FINAL_FILES)

    for filename, required_fragments in required_files.items():
        path = folder / filename
        if not path.is_file():
            errors.append(f"缺少必需文件：{filename}")
            continue
        text = path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            if fragment not in text:
                errors.append(f"{filename}：缺少必需章节或字段：{fragment}")

    article_path = folder / "article.md"
    if article_path.is_file():
        article = article_path.read_text(encoding="utf-8")
        compact_chars = len(re.sub(r"\s+", "", article))
        if compact_chars < 1200:
            warnings.append("article.md 较短，请确认其中包含分析，而不只是摘要")
        if not CODE_PATH_RE.search(article):
            warnings.append("article.md 中没有使用反引号标记的源码路径")
        for ref in IMAGE_RE.findall(article):
            if re.match(r"^(?:https?://|data:)", ref):
                continue
            resolved = (folder / ref).resolve()
            if not resolved.is_file():
                errors.append(f"article.md：无法解析本地图片：{ref}")

    ledger_path = folder / "claim-ledger.md"
    if ledger_path.is_file():
        ledger = ledger_path.read_text(encoding="utf-8")
        types = CLAIM_TYPE_RE.findall(ledger)
        if not types:
            errors.append("claim-ledger.md：没有找到 C-### 格式的论断记录")
        if "FACT" not in types:
            errors.append("claim-ledger.md：至少需要一条 FACT 论断")
        if not any(t in types for t in ("INFERENCE", "OPINION", "OPEN")):
            warnings.append("claim-ledger.md 只有事实，没有明确的推断、观点或开放问题")

    if mode in {"social-plan", "social-final"}:
        card_path = folder / "card-script.md"
        if card_path.is_file():
            card_text = card_path.read_text(encoding="utf-8")
            rows = CARD_ROW_RE.findall(card_text)
            if not rows:
                errors.append("card-script.md：没有找到带页码的卡片记录")
            for page, row in rows:
                if not re.search(r"\bC-\d+\b", row):
                    errors.append(f"card-script.md：第 {page} 页没有 Claim ID")
                if row.count("|") < 6:
                    errors.append(f"card-script.md：第 {page} 页缺少必需列")

        social_copy_path = folder / "social-copy.md"
        if social_copy_path.is_file():
            social_copy = social_copy_path.read_text(encoding="utf-8")
            if UNSTABLE_HOOK_RE.search(social_copy):
                warnings.append(
                    "social-copy.md 包含热度论断，请使用当前来源核验，否则删除"
                )

    if mode == "social-final":
        review_path = folder / "image-review.md"
        if review_path.is_file():
            review_text = review_path.read_text(encoding="utf-8")
            rows = REVIEW_ROW_RE.findall(review_text)
            if not rows:
                errors.append("image-review.md：没有找到带页码的审核记录")
            for page, row in rows:
                if not DIMENSION_RE.search(row):
                    errors.append(f"image-review.md：第 {page} 页没有记录真实像素尺寸")
                statuses = re.findall(r"\b(PASS|FAIL)\b", row)
                if len(statuses) != 4:
                    errors.append(
                        f"image-review.md：第 {page} 页必须记录四项质量门结果"
                    )
                elif any(status != "PASS" for status in statuses):
                    errors.append(f"image-review.md：第 {page} 页仍有未通过的质量门")

    return {
        "folder": str(folder),
        "mode": mode,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def create_self_test_fixture(folder: Path, mode: str) -> None:
    required_files = dict(REQUIRED_FILES)
    if mode in {"social-plan", "social-final"}:
        required_files.update(SOCIAL_PLAN_FILES)
    if mode == "social-final":
        required_files.update(SOCIAL_FINAL_FILES)

    for filename, fragments in required_files.items():
        text = "\n\n".join(fragments)
        if filename == "claim-ledger.md":
            text += (
                "\n|---|---|---|---|---|---|"
                "\n| C-001 | FACT | 行为存在 | `src/core.ts` | high | 第 2 节 |"
                "\n| C-002 | INFERENCE | 设计后果 | C-001 + 架构 | medium | 中心论点 |\n"
            )
        if filename == "article.md":
            text += "\n" + ("来自 `src/core.ts` 的证据解释了机制与设计权衡。" * 80)
        if filename == "card-script.md":
            text += "\n| 1 | 发生了什么变化？ | 可治理资产 | 从来源到交付 | 流程 | C-001 | Skill | 版本号 |\n"
        if filename == "image-review.md":
            text += "\n| 1 | image-cards/01.png | 1080x1440 | PASS | PASS | PASS | PASS | 无 | 保留 |\n"
        (folder / filename).write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true", help="运行内置自测")
    parser.add_argument(
        "--mode",
        choices=("research", "social-plan", "social-final"),
        default="research",
        help="选择调研、社交规划或社交成品校验模式",
    )
    args = parser.parse_args()

    if args.self_test:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            create_self_test_fixture(fixture, args.mode)
            result = validate(fixture, args.mode)
    else:
        if args.folder is None:
            parser.error("未使用 --self-test 时必须提供调研目录")
        result = validate(args.folder.resolve(), args.mode)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
