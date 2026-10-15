"""用同一份中文样稿生成全部资源模板与页图，供 AI 验收与用户比较。"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', help='只渲染一个模板 ID；默认全部')
    parser.add_argument('--dpi', type=int, default=85)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('resource_studio', ROOT / 'studio_server.py')
    studio = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(studio)
    source = (ROOT / 'examples/资源模板验收.md').read_text(encoding='utf-8')
    if args.template and args.template not in studio.TEMPLATE_IDS:
        parser.error('未知模板：' + args.template)
    reports = []
    for template in studio.TEMPLATES:
        if args.template and template['id'] != args.template:
            continue
        identifier = template['id']
        directory = ROOT / 'studio-articles/resource-gallery' / identifier
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'article.qmd').write_text(source, encoding='utf-8')
        settings = studio.validate_settings({**studio.DEFAULTS, **template['settings']})
        options = studio.metadata(settings, '把文字排成美好的阅读', '同一份中文样稿 · 字体与模板验收', 'Quarto Studio')
        metadata = directory / 'metadata.json'
        metadata.write_text(json.dumps(options, ensure_ascii=False, indent=2), encoding='utf-8')
        result = subprocess.run([studio.find_tool('quarto'), 'render', str(directory.relative_to(ROOT) / 'article.qmd'), '--to', 'typst', '--metadata-file', str(metadata), '--no-execute'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
        log = result.stdout + result.stderr
        (directory / 'render.log').write_text(log, encoding='utf-8')
        report = {'id': identifier, 'label': template['label'], 'exitCode': result.returncode, 'log': str(directory / 'render.log')}
        if not result.returncode:
            actual = ROOT / 'output/pdf/studio-articles/resource-gallery' / identifier / 'article.pdf'
            output = ROOT / 'output/pdf/template-gallery' / (identifier + '.pdf')
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(actual, output)
            report['pdf'] = str(output)
            if studio.find_tool('pdftoppm'):
                page_directory = ROOT / 'output/pages/template-gallery' / identifier
                page_directory.mkdir(parents=True, exist_ok=True)
                for previous_page in page_directory.glob('page-*.png'):
                    previous_page.unlink()
                subprocess.run([studio.find_tool('pdftoppm'), '-png', '-r', str(args.dpi), str(output), str(page_directory / 'page')], check=True, timeout=90)
                report['pages'] = [str(file) for file in sorted(page_directory.glob('page-*.png'))]
            print('通过：' + template['label'], flush=True)
        else:
            report['error'] = log[-4000:]
            print('失败：' + template['label'] + '\n' + log[-2300:], flush=True)
        reports.append(report)
    output = ROOT / 'output/template-gallery.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding='utf-8')
    raise SystemExit(1 if any(r['exitCode'] for r in reports) else 0)


if __name__ == '__main__':
    main()
