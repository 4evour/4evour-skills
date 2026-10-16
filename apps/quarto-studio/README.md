# Quarto Studio

独立的本地文章排版控制台。**Markdown/QMD → Quarto → Typst → PDF** 是唯一正文生成链路。页面预览和切页 PNG 都由最终 PDF 导出。

原有 MD2Card 版本保留在 `../markdown-studio/`，两套应用并行，不修改原版卡片渲染。

## 启动

需要 Python 3.10+、Quarto 1.10+（内置 Typst 0.15+，供 Codly 等资源使用）。页面预览及 PNG 导出需要 Poppler（`pdftoppm`、`pdfinfo`）。无需 npm、前端构建或 Python 第三方包。

Windows：

```powershell
cd apps/quarto-studio
.\start-studio.ps1
```

或双击 `启动Quarto工作台.cmd`。默认地址为 `http://127.0.0.1:8766/app/`；MD2Card 默认仍使用 `8765`。

手动启动：

```powershell
python scripts/download-fonts.py
python -X utf8 studio_server.py --port 8766
```

字体准备优先复用相邻 MD2Card 应用的字体缓存，缺失时按固定版本下载并验证 SHA256。更纱黑体需 7-Zip 或支持 7z 的 tar 解压，详见 [字体说明](fonts/README.md)。本机未安装的系统字体会在界面中标记为不可用。

有 Mermaid 时建议准备 Quarto 的专用浏览器：

```powershell
quarto install chrome-headless-shell --no-prompt
```

服务只监听 `127.0.0.1`。`QUARTO_TYPST` 等 Quarto 环境配置继续由工具自身处理；字体通过项目 `font-paths` 传入 Typst。

## 界面功能

- 导入 `.md` / `.qmd`、编辑正文，分别填写可选标题、副标题和作者。
- 提供 23 个字体选项，含 16 款开源字体、5 项系统字体和仓耳今楷的 2 个个人阅读字重；独立选择标题、正文、引用字体，控制字号、行距、段落间距。未安装的系统字体会标为不可用。
- 8 种主题、6 个纸面预设，可自定义强调色/纸张色/正文色；7 种背景包含横线纸、纤维纸、柔光和装饰细框，可调整纹理浓度。
- Letter、A4 或 3:4 竖版纸张；调整边距、封面、目录、页眉页脚。
- 默认自动更新：打开页面即生成，停止输入约 0.5 秒后合并修改并重新排版；也可关闭自动更新，手动点击“立即更新”。编译期间继续编辑时，只接续最新内容。
- 查看实际 PDF 页图，打开 PDF，下载 150 DPI 切页 PNG ZIP。
- 保存/导入样式 JSON，查看原始 Markdown、转换后的 QMD、Typst 源码和渲染日志。
- 为 Markdown 图片引用添加本地附件。

草稿和附件保存在此浏览器的独立 IndexedDB，与旧版分开。源文的 YAML 和事实正文保留；转换只处理 Mermaid 围栏、显式分页和图片引用路径。控制台已填写的元数据和样式通过独立元数据文件传入 Quarto。

## 图片底图库

“样式设置 → 背景底图库”提供花笺山水、古典纸纹、淡彩渐变、彩色肌理等分类筛选、图片缩略图选择和本地上传，支持 PNG、JPEG、WebP（每张最多 12 MB）。底图可以调整浓度、铺满/完整显示/拉伸以及全部页面/仅首页；不使用图片时恢复原来的纸面纹理。正文、图片、标题的颜色和清晰度不随底图浓度改变。

底图随实际 PDF 生成，因此页图预览、PDF 和切页 PNG 保持一致。底图库及来源记录保存在本机 `output/backgrounds/`，不随源码分发；草稿和样式 JSON 保存所选底图编号，在另一台机器使用时需重新上传原图。重复上传相同图片会复用已有底图和来源记录。

## Kami 三套版式

“样式设置”顶部提供阅读长文、研究简报、分享卡片三张版式缩略图；选择时应用完整的纸张、字体与密度预设。首次启动会准备仓耳今楷 W04/W05 字体文件，供个人阅读使用；独立许可记录见 [字体说明](fonts/README.md)。正文可用按钮标记导语、重点、引语、备注、提示、注意事项、编号步骤和胶囊标签，并可插入装饰分隔线；组件可选细线、圆角柔底或编辑手记风格。内置 Kami 示例还包含指标组件。详细用法、结构差异和扩展入口见 [Kami 版式说明](resources/KAMI.md)。

## 同稿比较

新版点击“示例 → 与 MD2Card 同稿对比”。这个样例与原版相同，选择后会设置浅紫色、庆科黄油标题和 3:4 纸张，方便比较模板。自动更新默认开启，无需再点生成。

纸张比例并不改变生成引擎：3:4 仍由 Typst 排版。对比时应同时查看字号、边距、封面和手动分页，避免将模板参数差异当成引擎差异。

原理、源码位置和优劣势说明见 [排版链路对比](../../docs/rendering-comparison.md)。

## 文件与任务

```text
quarto-studio/
├── web/                   # 原生 HTML/CSS/JavaScript 控制台
├── studio_server.py       # 本地任务队列、渲染和文件服务
├── _quarto.yml            # Quarto 项目与高图处理钩子
├── styles/                # Typst 样式与纸张参数
├── scripts/               # 字体准备、图块转换、图片缩放与重编译
├── fonts/                 # 固定字体清单及对应许可记录
├── examples/              # 同稿比较与排版验收示例
└── tests/                 # 参数、原文保留、资源路径等检查
```

自动更新仍需完成 Quarto 编译和 PDF 切页，不是浏览器逐字重绘。新页面就绪前保留旧预览；过时的任务结果不会替换最新内容的预览。编译失败保留成功结果，同一份失败输入不会无限重试。旧版草稿首次升级会开启自动更新，此后保留用户手动关闭的偏好。

任务按原文、样式、附件和引擎文件内容生成标识。相同输入会复用结果；任务在后台顺序执行。界面修改期间已有任务完成时，会明确提示预览还对应上一次输入。

- `studio-articles/<任务编号>/`：原文、QMD、独立渲染元数据、样式、Typst、日志和结果。
- `output/pdf/studio-articles/<任务编号>/article.pdf`：完整 PDF。
- `output/pages/<任务编号>/`：从 PDF 导出的 PNG 和 ZIP。

上述任务与生成文件不提交。缺少 Poppler 时仍可生成、打开 PDF，但页面图片预览和 PNG 导出不可用。接口上限为请求 30 MB、单图 12 MB、每篇 30 张图片；失败会返回日志，成功预览会保留。

## 验证

```powershell
python -m unittest discover -s tests -v
node --check web/app.js
node --test tests/*.test.mjs
```

Node 仅用于可选的 JavaScript 语法检查、自动更新调度和组件插入测试，应用运行无需 Node。导出改动还应实际验证字体、目录、表格、公式、图片和页面边界；Web 预览必须来自相同 PDF，不能用 HTML 页面模拟。

## 开源字体与模板资源库

共提供 23 个字体选项：16 款开源字体、5 项本机系统字体，以及仓耳今楷 W04/W05 两个个人阅读字重；支持标题、正文、引用与代码分别选用字体，并下载真实的粗体/斜体文件。样式面板新增 7 套上游模板（Dept News、Tufte、Orange Book、Vibrant Color、Modern Technique Report、ilm、Fiction），加上默认版式和 3 套 Kami 风格原生版式，共 11 套。Vibrant Color 还有 4 套原生配色；正文可使用 Showybox 引用框和 Codly 代码块。

来源、固定版本、许可证、适配范围和示例见 [资源库说明](resources/README.md)。查看 `resources/templates.json` 即可让 AI 读取每套模板的推荐字体与配色。

无需操作网页，也可以由 AI 直接生成：

```powershell
python -X utf8 scripts/render-document.py "文章.md" --template vibrant-color --output "output/pdf/分享文档.pdf"
```

同稿模板对照：`python -X utf8 scripts/render-resource-gallery.py`；字体样张：`quarto render examples/字体样张.qmd --to typst`。所有渲染仍保留高图缩放钩子与实际 PDF 页图检查。
