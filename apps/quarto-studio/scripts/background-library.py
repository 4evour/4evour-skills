"""本地图片底图库；原图和来源记录保存在 output/backgrounds。"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import re
import threading
import time
from urllib.parse import urlparse


class BackgroundLibrary:
    def __init__(self, root: Path):
        self.root = root
        self.lock = threading.Lock()

    def get(self, identifier: str) -> dict:
        if not isinstance(identifier, str) or not re.fullmatch(r"[0-9a-f]{24}", identifier):
            raise ValueError("底图编号不正确。")
        try:
            entry = json.loads((self.root / f"{identifier}.json").read_text(encoding="utf-8"))
            if not isinstance(entry, dict) or entry.get("id") != identifier or entry.get("extension") not in ("png", "jpg", "webp"):
                raise ValueError("底图记录不正确。")
            if not (self.root / f"{identifier}.{entry['extension']}").is_file():
                raise ValueError("底图文件不存在，请重新上传。")
            return entry
        except (OSError, KeyError, json.JSONDecodeError) as error:
            raise ValueError("找不到这张底图，请重新选择或上传。") from error

    def path(self, identifier: str, thumbnail: bool = False) -> Path:
        entry = self.get(identifier)
        preview = self.root / f"{identifier}-thumb.jpg"
        return preview if thumbnail and preview.is_file() else self.root / f"{identifier}.{entry['extension']}"

    @staticmethod
    def public(entry: dict) -> dict:
        return {**{key: entry.get(key, "") for key in ("id", "label", "category", "author", "sourceUrl", "usage")},
                "url": f"/backgrounds/{entry['id']}/image", "thumbnailUrl": f"/backgrounds/{entry['id']}/thumbnail"}

    def list(self) -> list[dict]:
        entries = []
        for file in self.root.glob("*.json"):
            try:
                entries.append(self.get(file.stem))
            except ValueError:
                continue
        return [self.public(entry) for entry in sorted(entries, key=lambda entry: entry.get("addedAt", 0))]

    def store(self, payload: dict) -> dict:
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), str):
            raise ValueError("请选择一张 PNG、JPEG 或 WebP 底图。")
        match = re.fullmatch(r"data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=\r\n]+)", payload["data"])
        if not match:
            raise ValueError("底图支持 PNG、JPEG 和 WebP。")
        if len(match[2]) > 16_000_000:
            raise ValueError("底图请控制在 12 MB 内。")
        try:
            binary = base64.b64decode(match[2], validate=True)
        except ValueError as error:
            raise ValueError("底图数据不完整，请重新选择。") from error
        valid = {"png": binary.startswith(b"\x89PNG\r\n\x1a\n") and len(binary) >= 24,
                 "jpeg": binary.startswith(b"\xff\xd8\xff") and binary.endswith(b"\xff\xd9"),
                 "webp": binary.startswith(b"RIFF") and binary[8:12] == b"WEBP"}
        if not binary or len(binary) > 12_000_000 or not valid[match[1]]:
            raise ValueError("底图文件为空、格式不正确或超过 12 MB。")
        identifier = hashlib.sha256(binary).hexdigest()[:24]
        extension = {"png": "png", "jpeg": "jpg", "webp": "webp"}[match[1]]
        entry = {"id": identifier, "extension": extension, "addedAt": time.time()}
        for key, fallback, limit in (("label", "我的底图", 80), ("category", "我的上传", 40),
                                     ("author", "", 100), ("sourceUrl", "", 2000), ("usage", "", 500)):
            value = payload.get(key, fallback)
            if not isinstance(value, str) or len(value) > limit:
                raise ValueError("底图名称或来源信息过长。")
            entry[key] = value.strip() or fallback
        if entry["sourceUrl"] and urlparse(entry["sourceUrl"]).scheme not in ("http", "https"):
            raise ValueError("底图来源需使用网页地址。")
        with self.lock:
            self.root.mkdir(parents=True, exist_ok=True)
            if (self.root / f"{identifier}.json").is_file():
                return self.public(self.get(identifier))
            (self.root / f"{identifier}.{extension}").write_bytes(binary)
            record = self.root / f"{identifier}.json"
            temporary = self.root / f"{identifier}.json.tmp"
            temporary.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(record)
        return self.public(entry)
