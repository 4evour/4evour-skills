"""无需启动网页，直接用模板生成可分享 PDF，适合由 AI 调用。"""
from __future__ import annotations
import argparse
import base64
import importlib.util
import json
import mimetypes
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = importlib.util.spec_from_file_location('document_studio', ROOT / 'studio_server.py')
    studio = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(studio)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path, help='原始 Markdown 或 QMD 文件')
    parser.add_argument('--template', choices=sorted(studio.TEMPLATE_IDS), default='default')
    parser.add_argument('--settings', type=Path, help='可选的样式 JSON')
    parser.add_argument('--title', default='')
    parser.add_argument('--subtitle', default='')
    parser.add_argument('--author', default='')
    parser.add_argument('--asset', action='append', default=[], metavar='引用名=图片路径')
    parser.add_argument('--output', type=Path, help='额外复制到指定的 PDF 路径')
    args = parser.parse_args()
    selected = next(t for t in studio.TEMPLATES if t['id'] == args.template)
    settings = dict(selected['settings'])
    if args.settings:
        saved = json.loads(args.settings.read_text(encoding='utf-8-sig'))
        settings.update(saved.get('settings', saved))
    settings['template'] = args.template
    images = []
    for asset in args.asset:
        if '=' not in asset:
            parser.error('--asset 使用 引用名=图片路径，例如 figures/chart.png=C:/images/chart.png')
        name, filename = asset.split('=', 1)
        path = Path(filename)
        content_type = mimetypes.guess_type(path.name)[0]
        if content_type not in ('image/png', 'image/jpeg', 'image/webp', 'image/gif'):
            parser.error('附件仅支持 PNG、JPEG、WebP、GIF 图片。')
        images.append({'name': name, 'data': 'data:' + content_type + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')})
    payload = {'markdown': args.file.read_text(encoding='utf-8-sig'), 'title': args.title,
               'subtitle': args.subtitle, 'author': args.author, 'settings': settings, 'images': images}
    try:
        state, _ = studio.submit(payload)
        print('正在使用 ' + selected['label'] + ' 生成 PDF…', flush=True)
        studio.EXECUTOR.shutdown(wait=True)
        result = studio.task_state(state['id'])
        if result['status'] != 'succeeded':
            raise RuntimeError(result.get('error', result.get('message')))
        pdf = studio.PDFS / state['id'] / 'article.pdf'
        if args.output:
            output = args.output.resolve()
            if output.suffix.lower() != '.pdf':
                parser.error('--output 应使用 .pdf 扩展名。')
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf, output)
            pdf = output
        print(json.dumps({'pdf': str(pdf), 'pagesZip': str(studio.PAGES / state['id'] / 'pages.zip'),
                          'pageCount': result['pageCount'], 'task': state['id']}, ensure_ascii=False, indent=2))
    finally:
        studio.EXECUTOR.shutdown(wait=True)


if __name__ == '__main__':
    main()
