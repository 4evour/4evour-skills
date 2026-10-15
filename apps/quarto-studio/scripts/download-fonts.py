"""按固定来源和 SHA256 准备字体及字重，复用相邻应用缓存。仅依赖标准库。"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import quote
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def checksum(content):
    return hashlib.sha256(content).hexdigest()


def valid(path, expected):
    return path.is_file() and checksum(path.read_bytes()) == expected


def fetch(url):
    candidates = [(url, {"User-Agent": "4evour-Quarto-Studio"})]
    prefix = "https://raw.githubusercontent.com/"
    if url.startswith(prefix):
        owner, repository, commit, path = url.removeprefix(prefix).split("/", 3)
        candidates.append((f"https://api.github.com/repos/{owner}/{repository}/contents/{path}?ref={commit}",
                           {"User-Agent": "4evour-Quarto-Studio", "Accept": "application/vnd.github.raw+json"}))
    last_error = None
    for candidate, headers in candidates:
        try:
            request = Request(quote(candidate, safe=":/%?=&"), headers=headers)
            with urlopen(request, timeout=45) as response:
                return response.read()
        except (OSError, TimeoutError) as error:
            last_error = error
    raise last_error


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_bytes(content)
    os.replace(temporary, path)


def read_archive(entry, cache):
    archive = cache / (entry["archive_sha256"] + "." + entry["archive_type"])
    if not valid(archive, entry["archive_sha256"]):
        content = fetch(entry["download_url"])
        if checksum(content) != entry["archive_sha256"]:
            raise ValueError("字体压缩包 SHA256 校验失败。")
        atomic_write(archive, content)
    if entry["archive_type"] == "zip":
        with zipfile.ZipFile(archive) as zipped:
            return zipped.read(entry["archive_member"])
    command = shutil.which("7z") or shutil.which("7zz")
    standard = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "7-Zip/7z.exe"
    if not command and standard.is_file():
        command = str(standard)
    if command:
        args = [command, "x", "-so", str(archive), entry["archive_member"]]
    elif shutil.which("tar"):
        args = [shutil.which("tar"), "-xOf", str(archive), entry["archive_member"]]
    else:
        raise RuntimeError("更纱字体解压需要 7-Zip 或支持 7z 的 tar。")
    return subprocess.run(args, capture_output=True, check=True, timeout=90).stdout


def prepare(font, caches):
    archive_cache = ROOT / "tmp/font-archives"
    for entry in font.get("files", [font]):
        target = ROOT / "fonts" / entry["file"]
        if valid(target, entry["sha256"]):
            continue
        reused = False
        for cache in caches:
            candidate = cache / entry["file"]
            if valid(candidate, entry["sha256"]):
                atomic_write(target, candidate.read_bytes())
                reused = True
                break
        if reused:
            continue
        content = read_archive(entry, archive_cache) if "archive_member" in entry else fetch(entry["download_url"])
        if checksum(content) != entry["sha256"]:
            raise ValueError("字体 SHA256 校验失败：" + font["label"])
        atomic_write(target, content)
    license_path = ROOT / "fonts" / font.get("license_file", str(Path(font["file"]).parent / "OFL.txt"))
    expected_license = font.get("license_sha256")
    if not license_path.is_file() or expected_license and not valid(license_path, expected_license):
        license_content = fetch(font["license_url"])
        if expected_license and checksum(license_content) != expected_license:
            raise ValueError("字体许可 SHA256 校验失败：" + font["label"])
        atomic_write(license_path, license_content)
    return font["family"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path)
    args = parser.parse_args()
    caches = [ROOT.parent / "markdown-studio/fonts"]
    if args.cache:
        caches.insert(0, args.cache)
    manifest = json.loads((ROOT / "fonts/manifest.json").read_text(encoding="utf-8-sig"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(prepare, font, caches) for font in manifest]
        for future in as_completed(futures):
            print("字体已就绪：" + future.result(), flush=True)


if __name__ == "__main__":
    main()
