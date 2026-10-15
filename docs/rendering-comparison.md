# MD2Card 与 Quarto + Typst：当前两套实现的区别

仓库保留两套独立应用，方便用同一篇文章比较。MD2Card 的代码和现有行为继续保留，新增的 Quarto Studio 单独运行。

| 版本 | 目录 | 默认地址 | 正文由谁排版 |
|---|---|---|---|
| MD2Card | `apps/markdown-studio/` | `http://127.0.0.1:8765/app/` | 浏览器 HTML/CSS 与应用分页逻辑 |
| Quarto Studio | `apps/quarto-studio/` | `http://127.0.0.1:8766/app/` | Quarto 文档处理 + Typst 排版 |

## MD2Card 的视觉效果从哪里来

当前实现先用 `remark-parse`、`remark-gfm` 和数学扩展把 Markdown 转为文档模型，再由 Preact 组件构造标题、段落、引用、代码、表格和封面。

视觉主要来自 CSS：

- `src/styles/cards/base.css` 提供共同的字体、标题层级、表格、引用和封面规则。
- `src/styles/cards/themes/` 定义表面色、文字色、强调色、背景纹理和局部主题装饰。
- `src/renderer/card-style.ts` 把界面参数映射为 CSS 变量。
- `src/styles/local-studio.css` 把新增字体和样式同时应用于实际卡片与测量区。

浏览器用字体和 CSS 完成布局。`MeasureStage.tsx` 等字体与图片就绪后测量内容高度，`paginate.ts` 再处理容量、标题簇、过高表格和长代码续页，`CardPage.tsx` 输出各张卡片。

导出时，`html-to-image` 把页面节点转成 PNG。PNG 可以打包 ZIP；当前新增的卡片 PDF 则通过 `jsPDF.addImage` 将这些 PNG 写入每页。所以本版本的“卡片 PDF”是图像页面，文字不能像普通 PDF 文本一样选中。旧应用还保留了另一条长文 PDF 接口，该接口本身已经调用 Quarto；它和即时卡片预览不是同一套分页。

## Quarto + Typst 的视觉效果从哪里来

Quarto Studio 将原文和样式参数交给 Quarto。Quarto 处理 Markdown/QMD、表格、数学、Mermaid 与文档元数据，再生成 `.typ`；Typst 根据字体、纸张、边距与样式完成文字排布和分页，输出 PDF。

本地 Web 控制台的职责是编辑文章、调整参数、提交任务和查看结果。它不将正文重新排成 HTML 卡片。右侧页面图是 Poppler 从最终 PDF 生成的，PNG 导出也来自同一份 PDF。

Quarto 负责文档编排，默认视觉由 `styles/typst-template.typ`、`styles/typst-show.typ` 和 `styles/page.typ` 控制；三套 Kami 版式由 `styles/kami/` 实现，上游模板由 `styles/resources/` 适配。纸面纹理由共用的 `styles/page-background.typ` 生成。标题、字体组合、颜色、底色、边线、圆角、引用与封面装饰都可以在 Typst 模板中实现；早期基础模板看起来朴素，不能代表该引擎的视觉上限。

Mermaid 仍需浏览器将图代码渲染成图片，再由 Typst 排进页面；这个图像步骤不承担正文分页。专用浏览器可通过 `quarto install chrome-headless-shell --no-prompt` 准备。

## 实际取舍

| 维度 | 当前 MD2Card | 新 Quarto Studio |
|---|---|---|
| 视觉调整反馈 | 修改 CSS 参数即可在浏览器中更新 | 默认在停止输入约 0.5 秒后自动编译，再更新真实页面；仍有编译和切页耗时 |
| 制作丰富卡片装饰 | CSS 对阴影、渐变、边框、背景等表达很直接 | 通过 Typst 样式和绘图实现，需要维护模板 |
| 核心分页 | 应用测量 DOM 后自行安排，复杂内容要逐类处理 | Typst 在文档排版过程中处理文字与页面 |
| 已有版式 | 4 套卡片主题，固定比例图片组 | 11 套版式，含单栏长文、双栏简报和按章节起页的卡片；支持目录、页眉页脚与页码 |
| 当前 PDF 导出 | 卡片 PDF 为位图；另有独立的 Quarto 长文入口 | 直接输出文字可选中的 PDF；图片内容仍是图片 |
| PNG 输出 | 浏览器节点转图片 | 最终 PDF 逐页转图片 |
| 预览与交付的关系 | 卡片预览对应 PNG/卡片 PDF | 预览由实际 PDF 渲染，和 PDF 分页相同 |
| 依赖 | Node/npm 前端，浏览器；长文接口额外依赖 Quarto | Python 标准库、Quarto；页面预览和 PNG 使用 Poppler |
| 开发重心 | CSS 组件和浏览器测量、分页策略 | Typst 模板、文档参数、任务和导出流程 |

以上是当前实现的行为和工程取舍，不是对所有基于浏览器的产品、所有 Typst 模板或两种引擎性能的统一结论。MD2Card 也可以继续扩展原生打印等能力，但本次保留现有版本用于比较。

## 目前的版式限制

MD2Card 保持原有的单栏卡片流与 4 套主题。Quarto Studio 当前提供 11 套版式，其中新增的三套 Kami 结构分别为 A4 单栏阅读长文、带通栏摘要和指标的 A4 双栏简报、3:4 按章节起页的分享卡片；它们不只是配色变化。示例和组件写法见 [Kami 版式说明](../apps/quarto-studio/resources/KAMI.md)。

Quarto Studio 另有 8 种主题、6 个纸面预设、7 种纹理及 3 种 Kami 组件外观。纸面会进入实际 PDF，预览和 PNG 使用同一份生成结果；部分上游模板有自己的封面底色和几何规则，不能保证所有全局参数都覆盖它们。

两套应用仍通过模板和内容流编排，没有自由拖拽或逐页定位编辑器。双栏简报会测量内容并安排栏组，但超长内容仍可能继续分栏分页；宽表格与多层嵌套组件更适合单栏长文。卡片章节较长时会续页，一个章节不保证只占一页。

同稿示例含显式分页标记，可能留下较多空白；这属于原文和模板的共同结果，不是两种引擎都只能这样排。改进视觉效果需要设计标题层级、封面、图文关系和内容密度，不能仅增加字体或换色。

自动更新与即时重绘也有区别：新版会自动触发真实 PDF 生成，无需每次点击；当前实现仍逐次调用 Quarto，而 MD2Card 在浏览器里重排 HTML，因此交互速度更快。

## 怎么做同稿比较

1. 原版启动 `apps/markdown-studio/start-studio.ps1`，新版启动 `apps/quarto-studio/start-studio.ps1`。
2. 两边使用同一份原文：`apps/quarto-studio/examples/同稿对比.md` 与旧版内置视觉样例一致。
3. 新版点击“示例”，选择“与 MD2Card 同稿对比”，会准备浅紫色、庆科黄油标题和 3:4 纸张。
4. 对照纸张比例、正文等效字号、字体、边距、行距、手动分页和封面设置，再比较视觉效果。
5. 分别检查短卡片、连续长文、宽表格、高流程图以及生成的 PDF/PNG；不要只按某一份模板的装饰判断引擎。

新版样例的 3:4 只是纸张比例，与 Letter/A4 一样仍由 Typst 排版。参数尽量接近时，换行和分页也可能因两个引擎的字体布局而不同。

要比较新增设计，可在 Quarto Studio 选择“示例 → Kami 三套版式示例”，依次切换阅读长文、研究简报、分享卡片；选择“纸面与组件装饰示例”可检查背景与组件。以上示例用于排版验收，不是用户待发布正文。
