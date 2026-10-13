"""Md2Card 本地静态服务与 Quarto PDF 导出接口。"""
from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import mimetypes
import os
import re
import shutil
import subprocess
import threading
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
APP = ROOT / "md2card" / "dist"
PDFS = ROOT / "output" / "pdf"
RENDER_LOCK = threading.Lock()
FONT_MANIFEST = json.loads((ROOT / "fonts/manifest.json").read_text(encoding="utf-8-sig"))
ALLOWED_FONTS = {item["family"] for item in FONT_MANIFEST} | {"Noto Sans SC", "Noto Sans SC Variable", "Microsoft YaHei", "SimSun", "KaiTi", "FangSong"}
spec = importlib.util.spec_from_file_location("markdown_converter", ROOT / "scripts/convert-markdown.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


def font_name(value, default):
    value = str(value or default)
    if value not in ALLOWED_FONTS:
        raise ValueError("请选择字体库中已有的字体。")
    return "Noto Sans SC" if value == "Noto Sans SC Variable" else value


def color(value):
    if value and not re.fullmatch(r"#[0-9a-fA-F]{6}", str(value)):
        raise ValueError("颜色必须是六位十六进制色值。")
    return value


def number(value, default, low, high):
    value = float(value if value is not None else default)
    if not low <= value <= high:
        raise ValueError("排版参数超出可用范围。")
    return value


def render_article(payload):
    markdown = payload.get("markdown", "")
    if not isinstance(markdown, str) or not markdown.strip():
        raise ValueError("请先填写文章内容。")
    config = payload.get("config", {})
    identifier = "article-" + uuid.uuid4().hex[:12]
    source = ROOT / "studio-articles" / (identifier + ".qmd")
    source.parent.mkdir(exist_ok=True)
    title = str(payload.get("title") or "未命名文章")[:180]
    themes = {
        'minimal': ('#ffffff', '#1f1f1f', '#303030', '#fafafa', '#666666'),
        'editorial': ('#fcf9ff', '#201a2a', '#66558f', '#f7f1ff', '#625b6a'),
        'notebook': ('#f8fcf8', '#18352a', '#356c59', '#f0f7f1', '#506a5b'),
        'research': ('#f8fcfd', '#17343e', '#17667c', '#eff7f8', '#587078'),
    }
    paper, ink, accent, panel, muted = themes.get(config.get('cardTheme'), themes['editorial'])
    body_size = number(config.get("bodyFontSize"), 30, 20, 60)
    line_height = number(config.get("bodyLineHeight"), 1.62, 1, 3)
    header = {
        "title": title,
        "subtitle": str(config.get("coverSubtitle", ""))[:300],
        "author": "本地排版工作台",
        "date": "today",
        "design-theme": "magazine" if config.get("cardTheme") in ("editorial", "notebook") else "report",
        "design-cover": config.get("coverMode", "integrated") != "none",
        "design-heading-font": font_name(config.get("headingFontFamily"), "Microsoft YaHei"),
        "design-body-font": font_name(config.get("bodyFontFamily"), "Noto Sans SC"),
        "design-quote-font": font_name(config.get("quoteFontFamily"), "KaiTi"),
        "design-leading": round(max(0.1, line_height - 1), 2),
        "design-background-pattern": config.get("backgroundPattern", "theme"),
        "design-paper": paper, "design-ink": ink, "design-accent": accent,
        "design-panel": panel, "design-muted": muted,
        "format": {"typst": {
            "toc": False,
            "fontsize": f"{body_size / 30 * 16.5:.2f}pt",
            "margin": {"x": f"{number(config.get('cardHorizontalPadding'), 76, 20, 160) / 76 * 0.85:.3f}in", "y": f"{number(config.get('cardVerticalPadding'), 67, 20, 160) / 67 * 0.85:.3f}in"},
        }},
    }
    for key, setting in (("design-accent", "accentColor"), ("design-paper", "backgroundColor"), ("design-ink", "textColor")):
        if config.get(setting):
            header[key] = color(config[setting])
    # JSON 是合法 YAML，可避免标题和字体名里的字符破坏文头。
    markdown = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", markdown, count=1, flags=re.S)
    markdown = markdown.replace("<!-- md2card:break -->", "\n```{=typst}\n#pagebreak()\n```\n")
    image_paths = {}
    for index, image in enumerate(payload.get('images', [])[:30]):
        name = str(image.get('name', ''))
        encoded = str(image.get('data', ''))
        if not name or not encoded.startswith('data:image/'):
            raise ValueError('图片数据格式不正确。')
        meta, data = encoded.split(',', 1)
        mime = meta.split(';')[0].removeprefix('data:')
        extension = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp', 'image/gif': '.gif', 'image/svg+xml': '.svg'}.get(mime)
        if not extension:
            raise ValueError('图片需使用 PNG、JPEG、WebP、GIF 或 SVG。')
        binary = base64.b64decode(data, validate=True)
        if len(binary) > 12_000_000:
            raise ValueError('单张图片超过 12 MB。')
        asset_dir = source.parent / (identifier + '-assets')
        asset_dir.mkdir(exist_ok=True)
        asset = asset_dir / (str(index) + extension)
        asset.write_bytes(binary)
        image_paths[name] = asset.relative_to(source.parent).as_posix()
    lines, fence = [], None
    for line in markdown.splitlines(keepends=True):
        found = converter.OPEN_FENCE.match(line.rstrip('\r\n'))
        if found:
            mark = found['fence']
            if fence is None: fence = (mark[0], len(mark))
            elif mark[0] == fence[0] and len(mark) >= fence[1] and not found['info'].strip(): fence = None
            lines.append(line)
            continue
        if fence is None:
            for old, new in image_paths.items():
                for prefix in (r'(!\[[^\]]*\]\(\s*<?)', r'(^\[[^\]]+\]:\s*<?)'):
                    line = re.sub(prefix + re.escape(old) + r'(?=>?\s*(?:[\'\"]|\)|$))', lambda match: match[1] + new, line)
        lines.append(line)
    markdown = ''.join(lines)
    markdown, _ = converter.convert_mermaid(markdown)
    source.write_text("---\n" + json.dumps(header, ensure_ascii=False, indent=2) + "\n---\n\n" + markdown, encoding="utf-8")
    quarto = shutil.which("quarto.exe") or shutil.which("quarto") or shutil.which("quarto.cmd")
    if not quarto:
        local_app_data = os.environ.get("LOCALAPPDATA")
        candidate = Path(local_app_data) / "Programs/Quarto/bin/quarto.exe" if local_app_data else None
        if not candidate or not candidate.is_file():
            raise RuntimeError("长文 PDF 导出需要安装 Quarto 并加入 PATH。")
        quarto = str(candidate)
    result = subprocess.run([quarto, "render", str(source.relative_to(ROOT)), "--to", "typst"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    (source.with_suffix(".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[-2400:])
    pdf = PDFS / "studio-articles" / (identifier + ".pdf")
    if not pdf.is_file():
        raise RuntimeError("渲染完成，但没有找到 PDF。")
    return {"url": "/files/studio-articles/" + pdf.name, "path": str(pdf), "bytes": pdf.stat().st_size}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP), **kwargs)

    def send_json(self, value, status=200):
        content = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/health":
            return self.send_json({"ok": True, "app": "Md2Card 本地工作台", "fonts": len(ALLOWED_FONTS) - 1, "root": str(ROOT)})
        if path.startswith("/files/"):
            file = (PDFS / path.removeprefix("/files/")).resolve()
            if not file.is_relative_to(PDFS.resolve()) or not file.is_file() or file.suffix != ".pdf":
                return self.send_error(404)
            data = file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()

    def do_POST(self):
        if self.path != "/api/render":
            return self.send_json({"error": "接口不存在。"}, 404)
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            return self.send_json({"error": "请从本地工作台发起请求。"}, 403)
        length = int(self.headers.get("Content-Length", 0))
        if not 0 < length <= 30_000_000:
            return self.send_json({"error": "文章与图片为空或超过 30 MB。"}, 400)
        if not RENDER_LOCK.acquire(blocking=False):
            return self.send_json({"error": "已有文章正在生成，请稍后再试。"}, 409)
        try:
            payload = json.loads(self.rfile.read(length))
            result = render_article(payload)
            return self.send_json(result)
        except (ValueError, json.JSONDecodeError) as error:
            return self.send_json({"error": str(error)}, 400)
        except Exception as error:
            return self.send_json({"error": str(error)}, 500)
        finally:
            RENDER_LOCK.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not (APP / "app/index.html").is_file():
        raise SystemExit("请先在 md2card 目录执行 npm run build。")
    mimetypes.add_type("font/ttf", ".ttf")
    print(f"Md2Card: http://127.0.0.1:{args.port}/app/", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
