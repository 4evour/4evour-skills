from __future__ import annotations

import base64
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("quarto_studio", ROOT / "studio_server.py")
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


class SourcePreservationTests(unittest.TestCase):
    def test_keeps_front_matter_and_factual_content(self):
        source = '---\ntitle: "原始标题"\nauthor: 作者\ncustom-field: keep-me\n---\n\n# 原始正文\n\n数据为 42，不能改写。\n'
        self.assertEqual(studio.rewrite_source(source, {}), (source, 0))

    def test_converts_real_mermaid_but_keeps_fenced_examples(self):
        source = '````markdown\n```mermaid\nA --> B\n```\n````\n\n```mermaid\nA --> B\n```\n'
        converted, count = studio.rewrite_source(source, {})
        self.assertEqual(count, 1)
        self.assertIn('````markdown\n```mermaid\n', converted)
        self.assertIn('```{mermaid}\nA --> B', converted)

    def test_pagebreak_conversion_preserves_code_and_inline_examples(self):
        source = '```html\n<!-- pagebreak -->\n```\n\n`<!-- pagebreak -->`\n\n<!-- pagebreak -->\n'
        converted, _ = studio.rewrite_source(source, {})
        self.assertIn('```html\n<!-- pagebreak -->\n```', converted)
        self.assertIn('`<!-- pagebreak -->`', converted)
        self.assertEqual(converted.count('#pagebreak()'), 1)

    def test_legacy_explicit_pagebreak_is_accepted(self):
        self.assertIn('#pagebreak()', studio.rewrite_source('<!-- md2card:break -->\n', {})[0])

    def test_image_reference_rewrite_keeps_inline_and_block_code(self):
        source = '![图](assets/a.png)\n\n`![图](assets/a.png)`\n\n```md\n![图](assets/a.png)\n```\n'
        converted, _ = studio.rewrite_source(source, {'assets/a.png': 'assets/0.png'})
        self.assertEqual(converted.count('assets/0.png'), 1)
        self.assertEqual(converted.count('assets/a.png'), 2)

    def test_supports_images_with_title_and_reference_style(self):
        source = '![图片](assets/a.png "图题")\n\n[figure]: assets/a.png\n'
        converted, _ = studio.rewrite_source(source, {'assets/a.png': 'assets/0.png'})
        self.assertEqual(converted.count('assets/0.png'), 2)

    def test_conversion_is_idempotent(self):
        source = '```mermaid\nA --> B\n```\n\n<!-- pagebreak -->\n'
        converted, _ = studio.rewrite_source(source, {})
        self.assertEqual(studio.rewrite_source(converted, {}), (converted, 0))


class MetadataTests(unittest.TestCase):
    def test_invalid_numerical_inputs_are_rejected(self):
        for value in (math.nan, math.inf, True, '17', 2, 100):
            with self.subTest(value=value), self.assertRaises(ValueError):
                studio.validate_settings({'fontSize': value})

    def test_invalid_color_is_rejected(self):
        for color in ('red', '#123', '#GGGGGG', 'rgb(1,2,3)'):
            with self.subTest(color=color), self.assertRaises(ValueError):
                studio.validate_settings({'paperColor': color})

    def test_unrecognized_font_and_paper_are_rejected(self):
        for settings in ({'bodyFont': 'unknown'}, {'paper': 'made-up'}, {'theme': 'unknown'}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                studio.validate_settings(settings)

    def test_boolean_options_are_not_coerced_from_strings(self):
        with self.assertRaises(ValueError):
            studio.validate_settings({'cover': 'false'})

    def test_native_page_geometry_is_propagated(self):
        for paper, (width, height) in studio.PAPERS.items():
            settings = studio.validate_settings({'paper': paper, 'marginX': 1.25})
            metadata = studio.metadata(settings, '标题', '', '')
            self.assertEqual(metadata['design-page-width'], width)
            self.assertEqual(metadata['design-page-height'], height)
            self.assertEqual(metadata['design-margin-x'], 90)

    def test_empty_console_fields_do_not_overwrite_source_metadata(self):
        metadata = studio.metadata(studio.validate_settings({}), '', '', '')
        self.assertNotIn('title', metadata)
        self.assertNotIn('subtitle', metadata)
        self.assertNotIn('author', metadata)

    def test_custom_color_and_typography_reach_typst_metadata(self):
        settings = studio.validate_settings({'textColor': '#112233', 'fontSize': 19, 'headingFont': 'ZCOOL XiaoWei'})
        metadata = studio.metadata(settings, '带 "引号" 的标题', '', '作者')
        self.assertEqual(metadata['design-ink'], '#112233')
        self.assertEqual(metadata['design-fontsize'], 19)
        self.assertEqual(metadata['design-heading-font'], 'ZCOOL XiaoWei')
        self.assertEqual(metadata['title'], '带 "引号" 的标题')


class ResourceTests(unittest.TestCase):
    def test_job_id_rejects_path_traversal(self):
        for identifier in ('../outside', '..', 'a' * 23, 'x' * 24):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                studio.job_id(identifier)

    def test_artifacts_do_not_expose_arbitrary_paths(self):
        identifier = 'a' * 24
        for name in ('../../studio_server.py', '../original.md', 'pages/-1.png', 'pages/0.png'):
            self.assertIsNone(studio.artifact(identifier, name))

    def test_image_paths_use_generated_filenames(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder) / 'assets'
            paths = studio.decode_images([{'name': '../../user.png', 'data': 'data:image/png;base64,' + base64.b64encode(b'png-test-data').decode()}], directory)
            self.assertEqual(paths, {'../../user.png': 'assets/0.png'})
            self.assertEqual([item.name for item in directory.iterdir()], ['0.png'])

    def test_duplicate_image_names_are_rejected(self):
        image = {'name': 'same.png', 'data': 'data:image/png;base64,' + base64.b64encode(b'png').decode()}
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(ValueError):
            studio.decode_images([image, image], Path(folder))

    def test_image_count_is_not_silently_truncated(self):
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(ValueError):
            studio.decode_images([{}] * 31, Path(folder))

    def test_bad_base64_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(ValueError):
            studio.decode_images([{'name': 'a.png', 'data': 'data:image/png;base64,not base64!'}], Path(folder))


if __name__ == '__main__':
    unittest.main()
