"""Quarto + Typst 工作台：本地任务、真实 PDF 预览和切页导出。仅依赖 Python 标准库。"""
from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, unquote, urlparse
import zipfile

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
JOBS = ROOT / "studio-articles"
PDFS = ROOT / "output" / "pdf" / "studio-articles"
PAGES = ROOT / "output" / "pages"
FONT_MANIFEST = json.loads((ROOT / "fonts/manifest.json").read_text(encoding="utf-8-sig"))
TEMPLATES = json.loads((ROOT / "resources/templates.json").read_text(encoding="utf-8-sig"))
TEMPLATE_IDS = {item["id"] for item in TEMPLATES}
THEMES = {
    "sage": {"label": "鼠尾草绿", "paper": "#F2F5EF", "ink": "#26332C", "accent": "#426654", "muted": "#68786C", "panel": "#E5EBDF", "divider": "#CED8CA"},
    "ocean": {"label": "雾蓝纸", "paper": "#F1F5F9", "ink": "#243746", "accent": "#3A6281", "muted": "#657C8E", "panel": "#E3EBF1", "divider": "#CEDAE4"},
    "rose": {"label": "浅桃纸", "paper": "#FCF3EF", "ink": "#49322D", "accent": "#A05C48", "muted": "#8D756D", "panel": "#F3E4DC", "divider": "#E7D2C8"},
    "kami": {"label": "Kami 暖纸", "paper": "#F5F4ED", "ink": "#22221F", "accent": "#1B365D", "muted": "#6B6A64", "panel": "#ECEBE3", "divider": "#D8D6CA"},
    "magazine": {"label": "暖纸杂志", "paper": "#F6F2EA", "ink": "#202B36", "accent": "#B7472A", "muted": "#6D747D", "panel": "#ECE7DD", "divider": "#D8D0C2"},
    "report": {"label": "清爽报告", "paper": "#FFFFFF", "ink": "#193040", "accent": "#087F86", "muted": "#607786", "panel": "#EDF5F5", "divider": "#D5E5E7"},
    "lavender": {"label": "柔光浅紫", "paper": "#FCF9FF", "ink": "#201A2A", "accent": "#66558F", "muted": "#625B6A", "panel": "#F7F1FF", "divider": "#D1C5DD"},
    "night": {"label": "深色阅读", "paper": "#182329", "ink": "#F3F0E8", "accent": "#F2C875", "muted": "#A7BCBF", "panel": "#24353D", "divider": "#435A63"},
}
PAPERS = {"letter": (612, 792), "a4": (595.276, 841.89), "portrait": (612, 816)}
PAPER_PRESETS = [
    {"id": "ivory", "label": "暖纸纤维", "theme": "kami", "background": "linen"},
    {"id": "white", "label": "纯白细框", "theme": "report", "background": "frame"},
    {"id": "sage", "label": "浅绿横线", "theme": "sage", "background": "ruled"},
    {"id": "blue", "label": "雾蓝柔光", "theme": "ocean", "background": "wash"},
    {"id": "rose", "label": "浅桃细点", "theme": "rose", "background": "dots"},
    {"id": "night", "label": "深色方格", "theme": "night", "background": "grid"},
]
BACKGROUNDS = ("plain", "dots", "grid", "ruled", "linen", "wash", "frame")
DEFAULTS = {
    "backgroundStrength": 0.22, "decoration": "minimal",
    "backgroundImage": "", "backgroundImageOpacity": 0.48, "backgroundImageFit": "cover", "backgroundImageScope": "all",
    "vibrantPalette": "pastel-theme", "template": "default", "codeFont": "JetBrains Mono", "codeStyle": "codly", "quoteStyle": "showybox",
    "theme": "magazine", "paper": "letter", "bodyFont": "Noto Sans SC",
    "headingFont": "Microsoft YaHei", "quoteFont": "KaiTi", "fontSize": 16.5,
    "headingSize": 28, "coverSize": 42, "leading": 0.65, "paragraphSpacing": 0.8,
    "marginX": 0.85, "marginY": 0.85, "background": "plain", "cover": False,
    "toc": False, "header": True, "footer": True,
    "accentColor": "", "paperColor": "", "textColor": "",
}
SYSTEM_FONTS = [
    {"family": "Noto Sans SC", "label": "思源黑体", "category": "黑体 · 正文"},
    {"family": "Microsoft YaHei", "label": "微软雅黑", "category": "黑体 · 标题"},
    {"family": "SimSun", "label": "宋体", "category": "宋体 · 正文"},
    {"family": "KaiTi", "label": "楷体", "category": "楷体 · 引用"},
    {"family": "FangSong", "label": "仿宋", "category": "传统 · 阅读"},
]
ALLOWED_FONTS = {font["family"] for font in SYSTEM_FONTS + FONT_MANIFEST}
EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="quarto-render")
LOCK = threading.Lock()
TASKS: dict[str, dict] = {}
FONT_CACHE: list[dict] | None = None
spec = importlib.util.spec_from_file_location("quarto_markdown", ROOT / "scripts/convert-markdown.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)
background_spec = importlib.util.spec_from_file_location("background_library", ROOT / "scripts/background-library.py")
background_module = importlib.util.module_from_spec(background_spec)
background_spec.loader.exec_module(background_module)
BACKGROUND_LIBRARY = background_module.BackgroundLibrary(ROOT / "output/backgrounds")


def find_tool(name: str) -> str | None:
    command = shutil.which(name) or shutil.which(name + ".exe")
    if command:
        return command
    if name == "quarto" and os.environ.get("LOCALAPPDATA"):
        candidate = Path(os.environ["LOCALAPPDATA"]) / "Programs/Quarto/bin/quarto.exe"
        if candidate.is_file():
            return str(candidate)
    if name in ("pdftoppm", "pdfinfo"):
        candidate = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin" / (name + ".exe")
        if candidate.is_file():
            return str(candidate)
    return None


def fonts() -> list[dict]:
    global FONT_CACHE
    if FONT_CACHE is not None:
        return FONT_CACHE
    available = set()
    command = find_tool("quarto")
    if command:
        result = subprocess.run([command, "typst", "fonts", "--font-path", str(ROOT / "fonts")], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        if result.returncode == 0:
            available = set((result.stdout + result.stderr).splitlines())
    entries = [dict(font, available=font["family"] in available, source="system") for font in SYSTEM_FONTS]
    for index, font in enumerate(FONT_MANIFEST):
        path = ROOT / "fonts" / font["file"]
        entries.append({"family": font["family"], "label": font["label"], "category": font["category"],
                        "available": path.is_file() and font["family"] in available,
                        "source": "personal" if font.get("personalUse") else "open", "previewWeight": font.get("previewWeight", "400"), "previewUrl": f"/fonts/{index}", "previewFormat": font.get("previewFormat", "truetype")})
    FONT_CACHE = entries
    return entries


def number(value, low: float, high: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{name}需在 {low} 到 {high} 之间。")
    return float(value)


def validate_settings(settings: dict) -> dict:
    if not isinstance(settings, dict):
        raise ValueError("样式设置必须是对象。")
    result = {**DEFAULTS, **{key: value for key, value in settings.items() if key in DEFAULTS}}
    for key, choices in (("template", TEMPLATE_IDS), ("vibrantPalette", ("pastel-theme", "blue-theme", "green-theme", "red-theme")), ("codeStyle", ("plain", "codly")), ("quoteStyle", ("template", "showybox")), ("theme", THEMES), ("paper", PAPERS), ("background", BACKGROUNDS), ("decoration", ("minimal", "soft", "editorial"))):
        if result[key] not in choices:
            raise ValueError(f"不支持的设置：{key}")
    for key in ("bodyFont", "headingFont", "quoteFont", "codeFont"):
        if result[key] not in ALLOWED_FONTS:
            raise ValueError("请选择字体库中的字体。")
    for key, low, high in (("backgroundImageOpacity", 0, 1), ("backgroundStrength", 0, 0.6), ("fontSize", 10, 24), ("headingSize", 20, 42), ("coverSize", 28, 60),
                            ("leading", 0.25, 1.2), ("paragraphSpacing", 0.2, 1.8), ("marginX", 0.35, 1.5), ("marginY", 0.35, 1.5)):
        result[key] = number(result[key], low, high, key)
    for key in ("cover", "toc", "header", "footer"):
        if not isinstance(result[key], bool):
            raise ValueError(f"{key} 必须是布尔值。")
    for key in ("accentColor", "paperColor", "textColor"):
        if not isinstance(result[key], str) or result[key] and not re.fullmatch(r"#[0-9A-Fa-f]{6}", result[key]):
            raise ValueError("颜色必须使用 #RRGGBB。")
    for key, choices in (("backgroundImageFit", ("cover", "contain", "stretch")), ("backgroundImageScope", ("all", "first"))):
        if result[key] not in choices:
            raise ValueError("底图适配或使用范围不正确。")
    if not isinstance(result["backgroundImage"], str):
        raise ValueError("底图编号不正确。")
    if result["backgroundImage"]:
        BACKGROUND_LIBRARY.get(result["backgroundImage"])
    return result


def metadata(settings: dict, title: str, subtitle: str, author: str, background_path: str = "") -> dict:
    palette = dict(THEMES[settings["theme"]])
    for key, setting in (("paper", "paperColor"), ("ink", "textColor"), ("accent", "accentColor")):
        if settings[setting]:
            palette[key] = settings[setting]
    width, height = PAPERS[settings["paper"]]
    result = {"toc": settings["toc"], "output-file": "article.pdf", "design-cover": settings["cover"],
              "design-heading-font": settings["headingFont"], "design-body-font": settings["bodyFont"],
              "design-quote-font": settings["quoteFont"], "design-fontsize": settings["fontSize"],
              "design-heading-size": settings["headingSize"], "design-cover-size": settings["coverSize"],
              "design-leading": settings["leading"], "design-spacing": settings["paragraphSpacing"],
              "design-page-width": width, "design-page-height": height,
              "design-margin-x": settings["marginX"] * 72, "design-margin-y": settings["marginY"] * 72,
              "design-background": settings["background"], "design-background-strength": settings["backgroundStrength"], "design-decoration": settings["decoration"], "design-header": settings["header"], "design-footer": settings["footer"]}
    result.update({"design-background-image": background_path, "design-background-image-opacity": settings["backgroundImageOpacity"],
                   "design-background-image-fit": settings["backgroundImageFit"], "design-background-image-scope": settings["backgroundImageScope"]})
    result.update({"design-vibrant-theme": settings["vibrantPalette"], "design-code-font": settings["codeFont"], "design-code-style": settings["codeStyle"], "design-quote-style": settings["quoteStyle"]})
    result["filters"] = [str(ROOT / "scripts/resource-blocks.lua")]
    if settings["codeStyle"] == "codly":
        result["format"] = {"typst": {"syntax-highlighting": "idiomatic"}}
    if settings["template"].startswith("kami-"):
        result["design-layout"] = settings["template"].removeprefix("kami-")
        result["filters"].append(str(ROOT / "scripts/kami-blocks.lua"))
        result.setdefault("format", {}).setdefault("typst", {})["template-partials"] = [str(ROOT / file) for file in ("styles/kami/typst-template.typ", "styles/kami/typst-show.typ", "styles/page.typ")]
    elif settings["template"] != "default":
        result["studio-" + settings["template"]] = True
        result.setdefault("format", {}).setdefault("typst", {})["template-partials"] = [str(ROOT / file) for file in ("styles/resources/typst-template.typ", "styles/resources/typst-show.typ", "styles/page.typ")]
    result.update({key: value for key, value in (("title", title), ("subtitle", subtitle), ("author", author)) if value})
    result.update({"design-" + key: value for key, value in palette.items() if key != "label"})
    return result


def rewrite_source(source: str, image_paths: dict[str, str]) -> tuple[str, int]:
    """保留原始 YAML 和正文，只转换图块、显式分页和实际图片引用。"""
    lines, fence = [], None
    for line in source.splitlines(keepends=True):
        match = converter.OPEN_FENCE.match(line.rstrip("\r\n"))
        if match:
            mark = match["fence"]
            if fence is None:
                fence = (mark[0], len(mark))
            elif mark[0] == fence[0] and len(mark) >= fence[1] and not match["info"].strip():
                fence = None
            lines.append(line)
            continue
        if fence is None:
            if line.strip() in ("<!-- pagebreak -->", "<!-- md2card:break -->"):
                line = "\n```{=typst}\n#pagebreak()\n```\n"
            else:
                pieces = re.split(r"(`+[^`]*`+)", line)
                for index in range(0, len(pieces), 2):
                    for original, replacement in image_paths.items():
                        pattern = r"(!\[[^\]]*\]\(\s*<?)" + re.escape(original) + r"(?=>?\s*(?:[\"']|\)|$))"
                        pieces[index] = re.sub(pattern, lambda found: found[1] + replacement, pieces[index])
                        pattern = r"(^\s{0,3}\[[^\]]+\]:\s*<?)" + re.escape(original) + r"(?=>?\s*(?:[\"']|$))"
                        pieces[index] = re.sub(pattern, lambda found: found[1] + replacement, pieces[index])
                line = "".join(pieces)
        lines.append(line)
    return converter.convert_mermaid("".join(lines))


def decode_images(images: list, directory: Path) -> dict[str, str]:
    if not isinstance(images, list) or len(images) > 30:
        raise ValueError("每篇文章最多提供 30 张图片。")
    paths = {}
    for index, image in enumerate(images):
        if not isinstance(image, dict) or not isinstance(image.get("name"), str):
            raise ValueError("图片条目格式不正确。")
        name = image["name"].replace("\\", "/")
        if not name or len(name) > 500 or name in paths:
            raise ValueError("图片引用名为空、过长或重复。")
        data = image.get("data", "")
        if not isinstance(data, str):
            raise ValueError("图片数据格式不正确。")
        match = re.fullmatch(r"data:(image/(?:png|jpeg|webp|gif|svg\+xml));base64,(.+)", data, re.S)
        if not match:
            raise ValueError("图片格式需为 PNG、JPEG、WebP、GIF 或 SVG。")
        binary = base64.b64decode(match[2], validate=True)
        if len(binary) > 12_000_000:
            raise ValueError("单张图片超过 12 MB。")
        extension = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif", "image/svg+xml": ".svg"}[match[1]]
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / (str(index) + extension)
        target.write_bytes(binary)
        paths[name] = "assets/" + target.name
    return paths


def job_id(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{24}", value):
        raise ValueError("任务编号不正确。")
    return value


def task_state(identifier: str) -> dict | None:
    with LOCK:
        if identifier in TASKS:
            return dict(TASKS[identifier])
    result_file = JOBS / identifier / "result.json"
    if result_file.is_file():
        return json.loads(result_file.read_text(encoding="utf-8"))
    return None


def update(identifier: str, **values) -> None:
    with LOCK:
        TASKS[identifier].update(values)


def run_command(command: list[str], log, timeout: int = 180) -> subprocess.CompletedProcess:
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    log.write("$ " + " ".join(command) + "\n" + completed.stdout + completed.stderr + "\n")
    log.flush()
    if completed.returncode:
        raise RuntimeError((completed.stderr or completed.stdout)[-3500:])
    return completed


def execute_job(identifier: str, payload: dict, settings: dict) -> None:
    started = time.monotonic()
    directory = JOBS / identifier
    directory.mkdir(parents=True, exist_ok=True)
    update(identifier, status="running", message="Quarto 正在处理正文、图表与排版…")
    try:
        with (directory / "render.log").open("w", encoding="utf-8") as log:
            source = payload["markdown"]
            (directory / "original.md").write_text(source, encoding="utf-8", newline="")
            image_paths = decode_images(payload.get("images", []), directory / "assets")
            converted, mermaid_count = rewrite_source(source, image_paths)
            (directory / "article.qmd").write_text(converted, encoding="utf-8", newline="")
            background_path = ""
            if settings["backgroundImage"]:
                background = BACKGROUND_LIBRARY.path(settings["backgroundImage"])
                target = directory / "assets" / ("background" + background.suffix)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(background, target)
                background_path = "/" + target.relative_to(ROOT).as_posix()
            options = metadata(settings, payload["title"], payload.get("subtitle", ""), payload.get("author", ""), background_path)
            (directory / "metadata.json").write_text(json.dumps(options, ensure_ascii=False, indent=2), encoding="utf-8")
            (directory / "settings.json").write_text(json.dumps({"title": payload["title"], "subtitle": payload.get("subtitle", ""), "author": payload.get("author", ""), "settings": settings}, ensure_ascii=False, indent=2), encoding="utf-8")
            command = find_tool("quarto")
            if not command:
                raise RuntimeError("未找到 Quarto，请安装 Quarto 并加入 PATH。")
            # 由 Quarto 处理 front matter，附加文件只覆盖控制台管理的样式参数。
            run_command([command, "render", str((directory / "article.qmd").relative_to(ROOT)), "--to", "typst",
                         "--metadata-file", str(directory / "metadata.json"), "--no-execute"], log)
            pdf = PDFS / identifier / "article.pdf"
            if not pdf.is_file() or not pdf.read_bytes()[:8].startswith(b"%PDF"):
                raise RuntimeError("Quarto 未生成可读取的 PDF，请查看渲染日志。")
            page_info = {}
            info = find_tool("pdfinfo")
            if info:
                raw = run_command([info, str(pdf)], log).stdout
                count = re.search(r"^Pages:\s+(\d+)", raw, re.M)
                size = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+)", raw, re.M)
                if count:
                    page_info["pageCount"] = int(count[1])
                if size:
                    page_info["widthPt"], page_info["heightPt"] = map(float, size.groups())
            pages = []
            warnings = []
            poppler = find_tool("pdftoppm")
            if poppler:
                update(identifier, message="PDF 已生成，正在从 PDF 导出页面预览和 PNG…")
                page_directory = PAGES / identifier
                page_directory.mkdir(parents=True, exist_ok=True)
                run_command([poppler, "-png", "-r", "150", str(pdf), str(page_directory / "page")], log)
                pngs = sorted(page_directory.glob("page-*.png"), key=lambda file: int(file.stem.split("-")[-1]))
                pages = [{"number": index + 1, "url": f"/artifacts/{identifier}/pages/{index + 1}.png"} for index, _ in enumerate(pngs)]
                with zipfile.ZipFile(page_directory / "pages.zip", "w", zipfile.ZIP_DEFLATED) as archive:
                    for index, image in enumerate(pngs):
                        archive.write(image, f"page-{index + 1:03d}.png")
            else:
                warnings.append("未找到 Poppler，PDF 已生成；安装 Poppler 后可预览页面并导出切页图片。")
            elapsed = round(time.monotonic() - started, 1)
            result = {"id": identifier, "status": "succeeded", "message": "PDF 与预览已就绪", "title": payload["title"] or "文章",
                      "elapsed": elapsed, "bytes": pdf.stat().st_size, "pdfPath": str(pdf), "pagePath": str(PAGES / identifier),
                      "pageCount": page_info.get("pageCount", len(pages)), "pages": pages, "warnings": warnings,
                      "mermaidCount": mermaid_count, "settings": settings,
                      "pdfUrl": f"/artifacts/{identifier}/document.pdf", "qmdUrl": f"/artifacts/{identifier}/source.qmd",
                      "typUrl": f"/artifacts/{identifier}/source.typ", "markdownUrl": f"/artifacts/{identifier}/original.md",
                      "settingsUrl": f"/artifacts/{identifier}/settings.json", "logUrl": f"/artifacts/{identifier}/render.log",
                      "zipUrl": f"/artifacts/{identifier}/pages.zip" if pages else None, **page_info}
            with LOCK:
                TASKS[identifier] = result
    except Exception as error:
        update(identifier, status="failed", message="排版失败", error=str(error), logUrl=f"/artifacts/{identifier}/render.log")
    state = task_state(identifier)
    (directory / "result.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def submit(payload: dict) -> tuple[dict, bool]:
    if not isinstance(payload, dict) or not isinstance(payload.get("markdown"), str) or not payload["markdown"].strip():
        raise ValueError("请先填写文章内容。")
    for field, limit in (("title", 200), ("subtitle", 500), ("author", 100)):
        if not isinstance(payload.get(field, ""), str) or len(payload.get(field, "")) > limit:
            raise ValueError(f"{field} 的文字过长或格式不正确。")
    if len(payload["markdown"]) > 1_000_000:
        raise ValueError("正文超过 100 万字符。")
    images = payload.get("images", [])
    if not isinstance(images, list) or len(images) > 30:
        raise ValueError("每篇文章最多提供 30 张图片。")
    settings = validate_settings(payload.get("settings", {}))
    payload = {"markdown": payload["markdown"], "title": payload.get("title", "").strip(),
               "subtitle": payload.get("subtitle", ""), "author": payload.get("author", ""), "images": images}
    if not payload["title"] and not re.match(r"\A---[ \t]*\r?\n", payload["markdown"]):
        found = re.search(r"^#\s+(.+)$", payload["markdown"], re.M)
        payload["title"] = found[1].strip() if found else "未命名文章"
    digest = hashlib.sha256(json.dumps({"payload": payload, "settings": settings}, ensure_ascii=False, sort_keys=True).encode())
    for template in sorted((ROOT / "styles").rglob("*.typ")):
        digest.update(template.read_bytes())
    digest.update((ROOT / "_quarto.yml").read_bytes())
    digest.update((ROOT / "resources/templates.json").read_bytes())
    digest.update((ROOT / "fonts/manifest.json").read_bytes())
    digest.update(Path(__file__).read_bytes())
    for script in sorted(file for file in (ROOT / "scripts").iterdir() if file.suffix in (".py", ".lua")):
        digest.update(script.read_bytes())
    identifier = digest.hexdigest()[:24]
    state = task_state(identifier)
    if state and state["status"] in ("queued", "running", "succeeded") and (state["status"] != "succeeded" or (PDFS / identifier / "article.pdf").is_file()):
        return state, True
    with LOCK:
        existing = TASKS.get(identifier)
        if existing and existing["status"] in ("queued", "running"):
            return dict(existing), True
        if sum(item["status"] in ("queued", "running") for item in TASKS.values()) >= 3:
            raise RuntimeError("已有排版任务等待处理，请稍后再生成。")
        TASKS[identifier] = {"id": identifier, "status": "queued", "message": "等待 Quarto 排版…"}
    EXECUTOR.submit(execute_job, identifier, payload, settings)
    return task_state(identifier), False


def artifact(identifier: str, name: str) -> Path | None:
    identifier = job_id(identifier)
    names = {"document.pdf": PDFS / identifier / "article.pdf", "source.qmd": JOBS / identifier / "article.qmd",
             "source.typ": JOBS / identifier / "article.typ", "original.md": JOBS / identifier / "original.md",
             "settings.json": JOBS / identifier / "settings.json", "render.log": JOBS / identifier / "render.log",
             "pages.zip": PAGES / identifier / "pages.zip"}
    if name in names:
        return names[name]
    match = re.fullmatch(r"pages/([1-9]\d*)\.png", name)
    if match:
        pages = sorted((PAGES / identifier).glob("page-*.png"), key=lambda file: int(file.stem.split("-")[-1]))
        number = int(match[1])
        return pages[number - 1] if number <= len(pages) else None
    return None


def bootstrap() -> dict:
    font_entries = fonts()
    available = {font["family"] for font in font_entries if font["available"]}
    defaults = dict(DEFAULTS)
    for field in ("bodyFont", "headingFont", "quoteFont"):
        if defaults[field] not in available and available:
            defaults[field] = "Noto Serif SC" if "Noto Serif SC" in available else sorted(available)[0]
    return {"app": "Quarto Studio", "engine": "Quarto + Typst", "defaults": defaults, "themes": THEMES,
            "paperPresets": PAPER_PRESETS, "backgrounds": BACKGROUND_LIBRARY.list(), "fonts": font_entries, "templates": TEMPLATES, "tools": {name: bool(find_tool(name)) for name in ("quarto", "pdftoppm", "pdfinfo")},
            "examples": [{"id": "comparison", "name": "与 MD2Card 同稿对比", "markdown": (ROOT / "examples/同稿对比.md").read_text(encoding="utf-8-sig")},
                         {"id": "article", "name": "长文、表格与流程图", "markdown": (ROOT / "examples/长文排版验收.md").read_text(encoding="utf-8-sig")},
                         {"id": "kami", "name": "Kami 三套版式示例", "markdown": (ROOT / "examples/Kami版式示例.md").read_text(encoding="utf-8-sig")},
                         {"id": "decorations", "name": "纸面与组件装饰示例", "markdown": (ROOT / "examples/纸面与组件装饰.md").read_text(encoding="utf-8-sig")}]}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def end_headers(self):
        if urlparse(self.path).path in ("/app", "/app/", "/app.js", "/auto-preview.mjs", "/components.mjs", "/background-picker.mjs", "/style.css"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format, *args):
        if not self.path.startswith("/api/jobs/"):
            super().log_message(format, *args)

    def send_json(self, data, status=200):
        content = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def send_file(self, file: Path | None, download: bool = False):
        if file is None or not file.is_file():
            return self.send_error(404, "File not found")
        content_type = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
        if file.suffix in (".qmd", ".typ", ".log", ".md"):
            content_type = "text/plain; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(file.stat().st_size))
        self.send_header("X-Content-Type-Options", "nosniff")
        if download:
            self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + quote(file.name))
        self.end_headers()
        with file.open("rb") as content:
            shutil.copyfileobj(content, self.wfile)

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        try:
            if path == "/api/health":
                return self.send_json({"ok": True, "app": "Quarto Studio", "engine": "Quarto + Typst", "root": str(ROOT)})
            if path == "/api/bootstrap":
                return self.send_json(bootstrap())
            if path == "/api/backgrounds":
                return self.send_json(BACKGROUND_LIBRARY.list())
            if path.startswith("/backgrounds/"):
                match = re.fullmatch(r"/backgrounds/([0-9a-f]{24})/(image|thumbnail)", path)
                if not match:
                    return self.send_error(404)
                return self.send_file(BACKGROUND_LIBRARY.path(match[1], thumbnail=match[2] == "thumbnail"))
            if path.startswith("/api/jobs/"):
                state = task_state(job_id(path.removeprefix("/api/jobs/")))
                return self.send_json(state) if state else self.send_error(404)
            if path.startswith("/artifacts/"):
                pieces = path.removeprefix("/artifacts/").split("/", 1)
                if len(pieces) != 2:
                    return self.send_error(404)
                return self.send_file(artifact(*pieces), download="download=1" in urlparse(self.path).query)
            if path.startswith("/fonts/"):
                index = int(path.removeprefix("/fonts/"))
                if not 0 <= index < len(FONT_MANIFEST):
                    return self.send_error(404)
                return self.send_file(ROOT / "fonts" / FONT_MANIFEST[index]["file"])
            if path in ("/app", "/app/"):
                return self.send_file(WEB / "index.html")
            # 静态目录只提供控制台资源。
            candidate = (WEB / path.lstrip("/")).resolve()
            if not candidate.is_relative_to(WEB):
                return self.send_error(404)
            return super().do_GET()
        except (ValueError, IndexError):
            return self.send_error(404)
        except Exception as error:
            return self.send_json({"error": str(error)}, 500)

    def do_POST(self):
        if self.path not in ("/api/render", "/api/backgrounds"):
            return self.send_json({"error": "接口不存在。"}, 404)
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            return self.send_json({"error": "请从本地控制台发起请求。"}, 403)
        try:
            length = int(self.headers.get("Content-Length", 0))
            if not 0 < length <= 30_000_000:
                raise ValueError("请求为空或超过 30 MB。")
            payload = json.loads(self.rfile.read(length))
            if self.path == "/api/backgrounds":
                return self.send_json(BACKGROUND_LIBRARY.store(payload), 201)
            state, cached = submit(payload)
            return self.send_json({**state, "cached": cached}, 200 if state["status"] == "succeeded" else 202)
        except (ValueError, TypeError) as error:
            return self.send_json({"error": str(error)}, 400)
        except RuntimeError as error:
            return self.send_json({"error": str(error)}, 409)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("端口需在 1024 到 65535 之间。")
    mimetypes.add_type("font/ttf", ".ttf")
    mimetypes.add_type("font/otf", ".otf")
    print(f"Quarto Studio: http://127.0.0.1:{args.port}/app/", flush=True)
    try:
        ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        EXECUTOR.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    main()
