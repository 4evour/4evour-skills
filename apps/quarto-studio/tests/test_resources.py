"""资源接入契约：实际版本、许可、模板路由和原生代码高亮。"""
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('resource_studio_tests', ROOT / 'studio_server.py')
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


class ResourceIntegrationTests(unittest.TestCase):
    def test_all_seven_templates_use_the_resource_partial(self):
        self.assertEqual(len([t for t in studio.TEMPLATES if t.get("group") != "kami"]), 8)
        partial = (ROOT / 'styles/resources/typst-template.typ').read_text(encoding='utf-8')
        for item in studio.TEMPLATES:
            if item['id'] == 'default' or item.get('group') == 'kami':
                continue
            with self.subTest(template=item['id']):
                settings = studio.validate_settings(item['settings'])
                metadata = studio.metadata(settings, '中文标题', '', '作者')
                self.assertTrue(metadata['studio-' + item['id']])
                paths = metadata['format']['typst']['template-partials']
                self.assertEqual(Path(paths[0]).name, 'typst-template.typ')
                self.assertTrue(all(Path(p).is_file() for p in paths))
                self.assertIn('studio-' + item['id'], partial)

    def test_codly_receives_native_typst_code_instead_of_skylighting(self):
        settings = studio.validate_settings({'codeStyle': 'codly'})
        self.assertEqual(studio.metadata(settings, '', '', '')['format']['typst']['syntax-highlighting'], 'idiomatic')
        settings['codeStyle'] = 'plain'
        self.assertNotIn('format', studio.metadata(settings, '', '', ''))

    def test_unrecognized_template_and_component_settings_are_rejected(self):
        for key in ('template', 'codeStyle', 'quoteStyle', 'vibrantPalette', 'codeFont'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                studio.validate_settings({key: '../outside'})

    def test_all_font_variants_and_licenses_match_the_pinned_manifest(self):
        self.assertGreaterEqual(len(studio.FONT_MANIFEST), 18)
        for font in studio.FONT_MANIFEST:
            with self.subTest(font=font['family']):
                license_path = ROOT / 'fonts' / font.get('license_file', str(Path(font['file']).parent / 'OFL.txt'))
                self.assertTrue(license_path.is_file())
                self.assertEqual(hashlib.sha256(license_path.read_bytes()).hexdigest(), font['license_sha256'])
                for entry in font.get('files', [font]):
                    path = ROOT / 'fonts' / entry['file']
                    if path.is_file():
                        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'])

    def test_upstream_licenses_and_offline_runtime_imports_are_preserved(self):
        records = json.loads((ROOT / 'resources/sources.json').read_text(encoding='utf-8'))
        for record in records:
            self.assertTrue((ROOT / record['license_file']).is_file())
        for path in (ROOT / 'styles/resources/runtime').rglob('*.typ'):
            self.assertFalse(re.search(r'^\s*#?(?:import|include)\s+"@preview/', path.read_text(encoding='utf-8'), re.M), str(path))


if __name__ == '__main__':
    unittest.main()
