"""三套版式与 AST 组件的实际契约检查。"""
import importlib.util
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("kami_tests_studio", ROOT / "studio_server.py")
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


class KamiTests(unittest.TestCase):
    def test_three_structures_have_distinct_geometry_and_shared_font_roles(self):
        templates = {t["id"]: t for t in studio.TEMPLATES if t.get("group") == "kami"}
        self.assertEqual(set(templates), {"kami-reading", "kami-brief", "kami-cards"})
        for key, template in templates.items():
            settings = studio.validate_settings(template["settings"])
            meta = studio.metadata(settings, "中文标题", "副标题", "作者")
            self.assertEqual(meta["design-layout"], key.removeprefix("kami-"))
            self.assertTrue(all(Path(file).is_file() for file in meta["format"]["typst"]["template-partials"]))
            self.assertIn(str(ROOT / "scripts/kami-blocks.lua"), meta["filters"])
            self.assertEqual(settings["bodyFont"], "TsangerJinKai02 W04")
            self.assertEqual(settings["headingFont"], "TsangerJinKai02 W05")
        self.assertEqual(templates["kami-cards"]["settings"]["paper"], "portrait")
        self.assertNotEqual(templates["kami-reading"]["settings"]["fontSize"], templates["kami-brief"]["settings"]["fontSize"])

    def transform(self, source):
        command = studio.find_tool("quarto")
        if not command:
            self.skipTest("未安装 Quarto，跳过真实 Pandoc 转换")
        result = subprocess.run([command, "pandoc", "-f", "markdown", "-t", "typst", "--lua-filter", str(ROOT / "scripts/kami-blocks.lua"), "-M", "design-layout=reading"], input=source, text=True, encoding="utf-8", capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_metric_grid_has_one_cell_per_metric(self):
        result = self.transform('''---
title: 标题
---
:::: {.kami-metrics}
::: {.kami-metric value="01" label="第一项"}
正文一。
:::
::: {.kami-metric value="02" label="第二项"}
正文二。
:::
::: {.kami-metric value="03" label="第三项"}
正文三。
:::
::::

## 章节
内容。
''')
        self.assertIn("#kami-tiles(columns: 3", result)
        self.assertEqual(result.count('[#kami-panel(kind: "metric"'), 3)  # 通栏摘要区中的每个指标只形成一个单元格。
        self.assertIn("正文三", result)

    def test_duplicate_document_title_is_removed_and_body_sections_remain(self):
        result = self.transform("---\ntitle: 同一个标题\n---\n# 同一个标题\n\n导语。\n\n## 正文标题\n保留正文。\n")
        self.assertNotIn("同一个标题", result)
        self.assertIn("正文标题", result)
        self.assertIn("保留正文", result)

    def test_explicit_pagebreak_remains_between_flows(self):
        result = self.transform("---\ntitle: 分页\n---\n## 前半\n第一段。\n\n```{=typst}\n#pagebreak()\n```\n\n## 后半\n第二段。\n")
        self.assertEqual(result.count("#kami-flow("), 2)
        self.assertEqual(result.count("#pagebreak()"), 1)
        self.assertIn("continuation: true", result)

    def test_background_and_decoration_settings_reach_pdf_metadata(self):
        for background in studio.BACKGROUNDS:
            settings = studio.validate_settings({"template": "kami-reading", "background": background, "backgroundStrength": 0.4, "decoration": "soft"})
            meta = studio.metadata(settings, "标题", "", "")
            self.assertEqual(meta["design-background"], background)
            self.assertEqual(meta["design-background-strength"], 0.4)
            self.assertEqual(meta["design-decoration"], "soft")
        for preset in studio.PAPER_PRESETS:
            self.assertIn(preset["theme"], studio.THEMES)
            self.assertIn(preset["background"], studio.BACKGROUNDS)
        for value in (-0.1, 1, float("nan"), True):
            with self.assertRaises(ValueError):
                studio.validate_settings({"backgroundStrength": value})
        with self.assertRaises(ValueError):
            studio.validate_settings({"decoration": "unknown"})

    def test_new_components_keep_all_original_words(self):
        source = '---\ntitle: 修饰\n---\n## 正文\n'
        for kind in ("info", "alert", "success", "step"):
            source += f'\n::: {{.kami-{kind} title="标题" value="02"}}\n保留{kind}内容。\n:::\n'
        source += '\n::: {.kami-tags}\n中文标签 | Second tag\n:::\n\n::: {.kami-divider}\n分隔文字\n:::\n'
        result = self.transform(source)
        for kind in ("info", "alert", "success", "step"):
            self.assertIn(f'kind: "{kind}"', result)
            self.assertIn(f"保留{kind}内容", result)
        self.assertIn("#kami-chips([中文标签], [Second tag])", result)
        self.assertIn('#kami-separator(label: "分隔文字")', result)

    def test_component_examples_inside_code_are_not_interpreted(self):
        result = self.transform('---\ntitle: 代码\n---\n## 原样示例\n\n```markdown\n::: {.kami-note}\n示例内容\n:::\n```\n')
        self.assertNotIn('#kami-panel(kind: "note"', result)
        self.assertIn("kami-note", result)


if __name__ == "__main__":
    unittest.main()
