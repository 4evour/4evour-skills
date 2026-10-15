# 字体、模板与正文组件

资源已接入独立的 Quarto Studio。最终页面仍由 **Markdown/QMD → Quarto → Typst → PDF** 生成；Web 只展示 PDF 导出的页图。原有 MD2Card 应用独立保留。

三套新增的 Kami 风格原生版式见 [Kami 说明](KAMI.md)：阅读长文、研究简报、分享卡片。它们以暖纸、仓耳今楷和内容组件为一套系统，与下列上游模板并存。

## 已接入的模板

| 模板 ID | 版式 | 建议用途 |
|---|---|---|
| `default` | 工作台默认 | 日常图文分享、手机阅读 |
| `dept-news` | Dept News | 彩色侧栏、通讯、杂志图文 |
| `tufte` | Tufte | 旁注、解释性长文，适合较宽页面 |
| `orange-book` | Orange Book | 教程、知识手册、章节文档 |
| `vibrant-color` | Vibrant Color | 几何封面、彩色侧栏、分享文档 |
| `modern-technique-report` | Modern Technique Report | 技术说明、项目报告 |
| `ilm` | ilm | 简洁长文、研究笔记 |
| `fiction` | Fiction / Wonderous Book | 随笔、故事集、书籍阅读 |

Vibrant Color 还提供上游的柔和渐变、蓝、绿、玫红四套视觉素材，可用 `vibrantPalette` 选择。其封面和侧栏包含上游的位图设计，任意强调色影响文字与装饰，不会重新着色这些位图。优先使用其 A4 推荐预设。Dept News 和 Tufte 使用文首标题，没有独立封面；控制台会禁用对应封面开关。

模板菜单和可供 AI 读取的推荐参数在 `templates.json`。点击“使用这套模板的推荐字体与配色”会应用完整搭配；单独选择模板会保留当前的字体与配色。

## 由 AI 直接生成

无需打开或操作网页：

```powershell
python -X utf8 scripts/render-document.py "文章.md" --template vibrant-color --title "文章标题" --author "作者" --output "output/pdf/分享文档.pdf"
```

脚本使用与 Web 相同的参数校验、转换、Quarto 渲染、高图缩放、PDF 验证与 150 DPI PNG 导出链路，结束后输出 PDF 和 PNG ZIP 的本机路径。原始 Markdown 会保留在任务目录。

可用 `--settings 样式.json` 加载控制台导出的样式。图片通过显式附件映射传入，例如：

```powershell
python -X utf8 scripts/render-document.py "文章.md" --template orange-book --asset "figures/chart.png=C:/images/chart.png"
```

HTTP 自动化同样可用：`GET /api/bootstrap` 返回字体、模板及推荐设置，`POST /api/render` 中的 `settings.template` 接收上表 ID。新参数包括 `codeFont`、`codeStyle`（`codly` / `plain`）、`quoteStyle`（`showybox` / `template`）、`vibrantPalette`（`pastel-theme` / `blue-theme` / `green-theme` / `red-theme`）。

## 字体和组件

原有 7 款开源字体继续可用，另加入以下 9 款：

| 字体 | 用途 | 准备的字重/样式 |
|---|---|---|
| Source Han Sans SC / 思源黑体 | 标题、现代正文 | Regular、Bold |
| Source Han Serif SC / 思源宋体 | 长文正文、书籍 | Regular、Bold |
| 霞鹜文楷 | 正文、引用、随笔 | Regular、Medium |
| 霞鹜文楷屏幕版 | 屏幕阅读 | Regular |
| Glow Sans SC / 未来荧黑 | 现代标题 | Regular、Bold |
| Smiley Sans / 得意黑 | 封面、短标题 | Oblique |
| Sarasa Gothic SC / 更纱黑体 | 中英混排 | Regular、Bold |
| Source Serif 4 | 西文正文 | Regular、Bold、Italic |
| JetBrains Mono | 代码 | Regular、Bold、Italic |

Source Serif 4 和 JetBrains Mono 的中文采用思源字体回退。得意黑适合标题；不建议将创意字体作为所有长文的正文。霞鹜文楷在 Typst 中识别的实际家族名是 `霞鶩文楷`，清单和推荐参数已经使用这个名称。

Showybox 2.0.4 用于圆角引用框；Codly 2.0.0 用于带行号、语言标识和原生语法高亮的代码块。Codly 需要 Typst 0.15+，本机验收环境为 Quarto 1.10.19 / Typst 0.15.1。所有依赖已随项目保存，模板编译无需临时从 Typst Universe 下载包。

可用如下内容添加侧栏。Dept News 会放入彩色侧栏；其他模板使用正文内容框：

````markdown
::: {.sidebar}
## 阅读提示
这里写一段补充说明。
:::
````

## 来源、许可与适配

- `sources.json`：上游地址、固定版本或提交、包压缩文件 SHA256、许可证位置与摘要。
- `upstream/`：上游原始源码与许可证。Vibrant Color 的分发包未附许可证文件，已从其源码仓库的固定提交补入 MIT 许可并记录来源。
- `../styles/resources/runtime/`：中文与控制台适配后的运行代码，附各自许可证。
- `../scripts/build-resource-adapters.py`：从上游源码重建运行代码。适配包括字体、语言、纸张、封面和目录开关、Typst 0.15 目录接口、书籍模板空白页处理，以及依赖的本地路径。
- `../fonts/manifest.json`：16 款开源字体的文件与字重、固定下载位置和 SHA256；字体二进制不提交。

字体许可为 SIL OFL 1.1，各模板及依赖分别保留 MIT、MIT-0 或 CC0 许可。Quarto 包装层和底层 Typst 模板的许可分别保留。

模板保留各自的章节、页眉页脚和背景设计；这些结构没有强制统一成默认模板。部分原生封面有固定的图形坐标，换成比例差异较大的纸张后应重新查看 PDF 页图。正式交付前仍应按实际文章检查图片、表格、长代码、分页与中文字符。

## 重新生成对照样稿

```powershell
python -X utf8 scripts/download-fonts.py
python -X utf8 scripts/build-resource-adapters.py
python -X utf8 scripts/render-resource-gallery.py
quarto render examples/字体样张.qmd --to typst
python -X utf8 -m unittest discover -s tests -v
```

模板 PDF 位于 `output/pdf/template-gallery/`，验收页图位于 `output/pages/template-gallery/`，字体样张位于 `output/pdf/examples/字体样张.pdf`。样稿用于观察模板，不是用户待发布文章。
