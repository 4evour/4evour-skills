#!/usr/bin/env python3
"""Validate the structural contract of open-source research artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


RESEARCH_REQUIRED_FILES = {
    "source-state.md": ["# Source State", "- Commit:", "- Research date:"],
    "evidence-map.md": [
        "## Source State",
        "## README Reuse Map",
        "## Official Claims",
        "## Architecture",
        "## Code Evidence",
        "## Engineering Evidence",
        "## Limitations",
        "## Contradictions",
        "## Open Questions",
    ],
    "thesis.md": [
        "## Central Thesis",
        "## Common Misreading",
        "## Supporting Evidence",
        "## Counterargument",
        "## Conditions",
        "## Unproven",
    ],
    "claim-ledger.md": [
        "| ID | Type | Claim | Evidence | Confidence | Article Location |",
    ],
}

ARTICLE_REQUIRED_FILES = {
    "article-purpose.md": ["# Article Purpose", "## Why This Article", "## Target Reader"],
    "argument-map.md": ["# Argument Map", "## Central Claim", "## Claim Hierarchy"],
    "outline.md": ["# Outline"],
    "article.md": ["# "],
    "editorial-review.md": ["# Editorial Review"],
}

SOCIAL_PLAN_FILES = {
    "channel-strategy.md": [
        "# Channel Strategy",
        "- Execution mode:",
        "- Central takeaway:",
        "## Image and Caption Division",
    ],
    "card-script.md": [
        "# Card Script",
    ],
    "social-copy.md": [
        "# Social Copy",
        "## Cover Title",
        "## Post Title",
        "## Body",
        "## Caption-only Evidence and Nuance",
        "## Tags",
    ],
}

SOCIAL_FINAL_FILES = {
    "image-review.md": [
        "# Image Review",
    ],
}

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CODE_PATH_RE = re.compile(r"`[^`\n]+\.(?:py|ts|tsx|js|jsx|go|rs|java|kt|rb|php|cs|cpp|c|h|md)`")
CLAIM_TYPE_RE = re.compile(r"\|\s*C-\d+\s*\|\s*(FACT|INFERENCE|OPINION|OPEN)\s*\|")
CARD_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.+)$", re.MULTILINE)
REVIEW_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.+)$", re.MULTILINE)
DIMENSION_RE = re.compile(r"\b\d{3,5}\s*[x×]\s*\d{3,5}\b", re.IGNORECASE)
UNSTABLE_HOOK_RE = re.compile(r"(?:GitHub\s*)?(?:爆火|很火|新星项目|热门项目)", re.IGNORECASE)


def validate(folder: Path, mode: str = "research") -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    required_files = dict(RESEARCH_REQUIRED_FILES)
    if mode == "article":
        required_files.update(ARTICLE_REQUIRED_FILES)
    if mode in {"social-plan", "social-final"}:
        required_files.update(SOCIAL_PLAN_FILES)
    if mode == "social-final":
        required_files.update(SOCIAL_FINAL_FILES)

    for filename, required_fragments in required_files.items():
        path = folder / filename
        if not path.is_file():
            errors.append(f"missing required file: {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            if fragment not in text:
                errors.append(f"{filename}: missing required section/field: {fragment}")

    article_path = folder / "article.md"
    if article_path.is_file():
        article = article_path.read_text(encoding="utf-8")
        compact_chars = len(re.sub(r"\s+", "", article))
        if compact_chars < 1200:
            warnings.append("article.md is short; verify it contains analysis rather than a summary")
        if not CODE_PATH_RE.search(article):
            warnings.append("article.md contains no backticked source-code path")
        for ref in IMAGE_RE.findall(article):
            if re.match(r"^(?:https?://|data:)", ref):
                continue
            resolved = (folder / ref).resolve()
            if not resolved.is_file():
                errors.append(f"article.md: unresolved local image: {ref}")

    ledger_path = folder / "claim-ledger.md"
    if ledger_path.is_file():
        ledger = ledger_path.read_text(encoding="utf-8")
        types = CLAIM_TYPE_RE.findall(ledger)
        if not types:
            errors.append("claim-ledger.md: no C-### claim rows found")
        if "FACT" not in types:
            errors.append("claim-ledger.md: at least one FACT claim is required")
        if not any(t in types for t in ("INFERENCE", "OPINION", "OPEN")):
            warnings.append("claim-ledger.md has facts but no explicit inference, opinion, or open question")

    if mode in {"social-plan", "social-final"}:
        card_path = folder / "card-script.md"
        if card_path.is_file():
            card_text = card_path.read_text(encoding="utf-8")
            rows = CARD_ROW_RE.findall(card_text)
            if not rows:
                errors.append("card-script.md: no numbered page rows found")
            for page, row in rows:
                if not re.search(r"\bC-\d+\b", row):
                    errors.append(f"card-script.md: page {page} has no claim ID")
                if row.count("|") < 6:
                    errors.append(f"card-script.md: page {page} is missing required columns")

        social_copy_path = folder / "social-copy.md"
        if social_copy_path.is_file():
            social_copy = social_copy_path.read_text(encoding="utf-8")
            if UNSTABLE_HOOK_RE.search(social_copy):
                warnings.append(
                    "social-copy.md contains a popularity claim; verify it with a current source or remove it"
                )

    if mode == "social-final":
        review_path = folder / "image-review.md"
        if review_path.is_file():
            review_text = review_path.read_text(encoding="utf-8")
            rows = REVIEW_ROW_RE.findall(review_text)
            if not rows:
                errors.append("image-review.md: no numbered page rows found")
            for page, row in rows:
                if not DIMENSION_RE.search(row):
                    errors.append(f"image-review.md: page {page} has no actual pixel dimensions")
                statuses = re.findall(r"\b(PASS|FAIL)\b", row)
                if len(statuses) < 4:
                    errors.append(f"image-review.md: page {page} must record at least four gate results")
                elif any(status != "PASS" for status in statuses):
                    errors.append(f"image-review.md: page {page} has a failed quality gate")

    return {
        "folder": str(folder),
        "mode": mode,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def create_self_test_fixture(folder: Path, mode: str) -> None:
    required_files = dict(RESEARCH_REQUIRED_FILES)
    if mode == "article":
        required_files.update(ARTICLE_REQUIRED_FILES)
    if mode in {"social-plan", "social-final"}:
        required_files.update(SOCIAL_PLAN_FILES)
    if mode == "social-final":
        required_files.update(SOCIAL_FINAL_FILES)

    for filename, fragments in required_files.items():
        text = "\n\n".join(fragments)
        if filename == "claim-ledger.md":
            text += (
                "\n|---|---|---|---|---|---|"
                "\n| C-001 | FACT | behavior exists | `src/core.ts` | high | Section 2 |"
                "\n| C-002 | INFERENCE | design consequence | C-001 + architecture | medium | Thesis |\n"
            )
        if filename == "article.md":
            text += "\n" + ("Evidence from `src/core.ts` explains the mechanism and tradeoff. " * 40)
        if filename == "card-script.md":
            text += "\n| 1 | What changes? | A governed asset | source to delivery | flow | C-001 | Skill | versions |\n"
        if filename == "image-review.md":
            text += "\n| 1 | image-cards/01.png | 1080x1440 | PASS | PASS | PASS | PASS | none | keep |\n"
        (folder / filename).write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--mode",
        choices=("research", "article", "social-plan", "social-final"),
        default="research",
    )
    args = parser.parse_args()

    if args.self_test:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            create_self_test_fixture(fixture, args.mode)
            result = validate(fixture, args.mode)
    else:
        if args.folder is None:
            parser.error("folder is required unless --self-test is used")
        result = validate(args.folder.resolve(), args.mode)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
