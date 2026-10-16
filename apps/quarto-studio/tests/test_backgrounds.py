from __future__ import annotations
import base64
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('studio_background_tests', ROOT / 'studio_server.py')
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')

class BackgroundLibraryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.library = studio.background_module.BackgroundLibrary(Path(self.directory.name))
        self.payload = {'label': '浅麻素纸', 'data': 'data:image/png;base64,' + base64.b64encode(PNG).decode()}

    def test_import_deduplicates_binary_without_overwriting_attribution(self):
        first = self.library.store({**self.payload, 'author': '原作者', 'sourceUrl': 'https://example.com/paper'})
        duplicate = self.library.store({**self.payload, 'label': '另一个名字'})
        self.assertEqual(first, duplicate)
        self.assertEqual(self.library.path(first['id']).read_bytes(), PNG)
        self.assertEqual(len(self.library.list()), 1)
        self.assertEqual(duplicate['author'], '原作者')

    def test_persistent_library_and_thumbnail_fallback(self):
        entry = self.library.store(self.payload)
        reopened = studio.background_module.BackgroundLibrary(Path(self.directory.name))
        self.assertEqual(reopened.list(), [entry])
        self.assertEqual(reopened.path(entry['id'], thumbnail=True), reopened.path(entry['id']))

    def test_rejects_traversal_or_non_image_upload(self):
        for identifier in ('../secret', '', '/tmp/background', 'a'*25):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                self.library.path(identifier)
        for data in ('data:text/html;base64,PGh0bWw+', 'data:image/png;base64,ZmFrZQ==', 'data:image/webp;base64,%%%%'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.library.store({'data': data})

    def test_rejects_non_web_source_links(self):
        with self.assertRaises(ValueError):
            self.library.store({**self.payload, 'sourceUrl': 'file:///tmp/paper'})

    def test_missing_or_corrupted_entries_do_not_break_gallery(self):
        entry = self.library.store(self.payload)
        (self.library.root/('b'*24+'.json')).write_text('[]',encoding='utf-8')
        self.library.path(entry['id']).unlink()
        self.assertEqual(self.library.list(), [])

    def test_selected_background_reaches_pdf_with_opacity_fit_and_scope(self):
        entry = self.library.store(self.payload)
        with patch.object(studio, 'BACKGROUND_LIBRARY', self.library):
            settings = studio.validate_settings({'backgroundImage': entry['id'], 'backgroundImageOpacity': 0.3, 'backgroundImageFit': 'contain', 'backgroundImageScope': 'first'})
        metadata = studio.metadata(settings, '文学阅读', '', '', '/studio-articles/example/assets/background.png')
        self.assertEqual(metadata['design-background-image-opacity'], 0.3)
        self.assertEqual(metadata['design-background-image-fit'], 'contain')
        self.assertEqual(metadata['design-background-image-scope'], 'first')
        self.assertTrue(metadata['design-background-image'].endswith('background.png'))

    def test_rejects_missing_background_and_invalid_image_options(self):
        for settings in ({'backgroundImage': 'a'*24}, {'backgroundImage': '../secret'}, {'backgroundImageOpacity': float('nan')}, {'backgroundImageOpacity': 1.1}, {'backgroundImageFit': 'unknown'}, {'backgroundImageScope': 'unknown'}):
            with self.subTest(settings=settings), patch.object(studio, 'BACKGROUND_LIBRARY', self.library), self.assertRaises(ValueError):
                studio.validate_settings(settings)

if __name__ == '__main__':
    unittest.main()
