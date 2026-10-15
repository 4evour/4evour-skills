# Kami 风格的三套原生 Typst 版式

设计参考：[Tw93/Kami](https://github.com/Tw93/kami)，固定提交 `934dc5f0602c12b81f4c0e275cd47269296e62fb`，记录日期 2026-10-15。Kami 的 MIT 许可原文保留在 [KAMI-LICENSE](KAMI-LICENSE)。这里将暖纸、克制强调、稳定字体层级和内容组件的设计思想适配为原生 Typst，不依赖 Kami 的 HTML/WeasyPrint 生成链路，也不代表上游官方模板。

## 选择版式

控制台进入“样式设置 → 选择阅读方式”，点击缩略图。纸张、字体、配色和间距会一起应用，原文保留，默认自动更新。原有默认版式与 7 套上游模板继续保留在下面的“选择版式”菜单。

| ID | 推荐设置 | 结构 |
|---|---|---|
| `kami-reading` | A4、13.5pt、仓耳今楷 | 单栏、通栏导语、章节编号、阅读引语 |
| `kami-brief` | A4、12.5pt、仓耳今楷 | 通栏摘要与指标、按页测量并分配双栏正文 |
| `kami-cards` | 3:4、19pt、仓耳今楷 | 主题页、每个主章节起页、重点块与大字阅读 |

字体采用仓耳今楷02 W04 正文与 W05 标题，按本机用户声明的个人阅读用途准备。来源、文件内嵌许可声明和上游说明保留在 [字体许可记录](../fonts/tsanger/LICENSE.txt)。字体二进制忽略提交。其他开源字体仍可在界面选择。

点击“正文编辑 → 示例 → Kami 三套版式示例”可用同一篇内容比较。它是专门的排版样例，不是用户待发布正文。

## 内容组件

选择正文后，点击编辑区上方的“导语 / 重点 / 引语 / 备注”即可标记该段内容。它只改变组件角色，保留选中文字。也可以直接使用 Markdown 围栏：

````markdown
::: {.kami-lead}
这是一段导语。
:::

::: {.kami-takeaway title="核心结论"}
这是一段重点内容。
:::

::: {.kami-note title="阅读备注"}
这是一段补充说明。
:::

::: {.kami-pullquote}
这是一段单独强调的引语。
:::

:::: {.kami-metrics}
::: {.kami-metric value="01" label="第一项"}
指标说明。
:::
::: {.kami-metric value="02" label="第二项"}
指标说明。
:::
::: {.kami-metric value="03" label="第三项"}
指标说明。
:::
::::
````

也可用 `.kami-columns` 包裹两个组件作并排比较。所有组件只在 Kami 模板中启用。普通 Markdown 标题、列表、引用、表格、数学和 Mermaid 继续使用；同名文首标题在渲染 AST 中去重，原始文件完整保留。主章节统一映射为视觉章节，显式分页仍生效。

## 生成与扩展

```powershell
python -X utf8 scripts/render-document.py examples/Kami版式示例.md --template kami-reading --output output/pdf/Kami-阅读长文.pdf
python -X utf8 scripts/render-document.py examples/Kami版式示例.md --template kami-brief --output output/pdf/Kami-研究简报.pdf
python -X utf8 scripts/render-document.py examples/Kami版式示例.md --template kami-cards --output output/pdf/Kami-分享卡片.pdf
```

- 参数和推荐预设：`resources/templates.json`。
- 共用组件、版面、章节与页眉页脚：`styles/kami/layouts.typ`。
- Quarto 元数据桥接：`styles/kami/typst-template.typ` / `typst-show.typ`。
- 文档组件与分栏内容组：`scripts/kami-blocks.lua`。
- 高图仍由 `post-render.py` 等比缩放。简报按实际栏宽处理，卡片额外预留章节头高度。

简报按实际文字高度选择每页两栏的内容组，尽量平衡高度。无法作为单组放入一页的极长段落或复杂内容会交给原生分栏继续排布；宽表格、多层并排组件应优先选长文版式，或简化列数。卡片会按章节起页，章节内容过长时继续分页，并不保证一个章节只有一页。Kami 版式的引用与代码使用自己的平面样式，控制台会禁用上游 Showybox/Codly 开关。

## 验收

运行 `python -m unittest discover -s tests -v` 和 `node --test tests/auto-preview.test.mjs tests/components.test.mjs`。本次还实际生成了同稿三版 8 页，复杂内容三版覆盖独立封面、目录、数学、代码、表格、本地附件、高 Mermaid 图和显式分页；检查文字提取、原文保留、PNG ZIP 页数、正文与图像边界，并查看逐页页图。预览缩略图来自这三套模板生成的实际 PDF。

## PDF 背景与组件修饰

进入“样式设置 → PDF 纸面与背景”。6 个预设会同时应用协调的纸色、字色、强调色和纹理：暖纸纤维、纯白细框、浅绿横线、雾蓝柔光、浅桃细点、深色方格。也可用颜色选择器设置纸张背景、正文和强调色。纹理可独立选择纯色、细点、方格、横线、纤维、柔光晕染或装饰细框，浓度范围 0 至 60%；0 表示不显示纹理。

“组件修饰”提供克制细线、圆角柔底、编辑手记三种外观，用于三套 Kami 模板。重点、引语、备注和指标会随外观变化，标签使用胶囊边框，步骤采用编号标识，分隔线可以带标题。深色纸面的提示卡会自动使用较亮的强调色。

正文编辑区增加“提示 / 留意 / 收藏 / 步骤 / 标签 / 分隔”。除分隔可在光标处直接插入外，其他按钮包裹选中文字；步骤编号自动递增，标签文字可用 `|` 分隔。新增围栏类为 `.kami-info`、`.kami-alert`、`.kami-success`、`.kami-step`、`.kami-tags`、`.kami-divider`。步骤可用 `value="01" title="步骤标题"` 自定义编号和标题；其他提示卡可用 `title` 自定义标题。组件原文和嵌套围栏保留。

点击“示例 → 纸面与组件装饰示例”可直接查看完整效果。参数分别为 `background`、`backgroundStrength`、`decoration`，在样式 JSON、Web 和命令行中共用。背景由 `styles/page-background.typ` 生成矢量图形；实际 PDF、预览和 PNG 共用生成结果。第三方模板可能有自己的封面底色和布局规则，完整纸面与组件体验优先选择 Kami 三套版式。
