# Markdown Studio：本地可视化排版工作台

基于 MD2Card 的本地编辑器。导入 Markdown，分别选择标题、正文和引用字体，再调整主题、颜色、背景、字号和分页，导出卡片或正式长文。

## 安装和启动

### Windows

- Node.js 24+。
- Python 3.10+ 和 PowerShell 7。
- Quarto：长文 PDF 必需，内置 Typst，无需另外安装 LaTeX。
- Edge / Chrome：供 Quarto 渲染 Mermaid。
- Poppler：仅 `render.ps1 -ExportPages` 导出 PDF 切页图片时需要。

在本目录执行：

```powershell
.\start-studio.ps1
```

或双击 `启动排版工作台.cmd`。首次启动会下载 7 款开源字体、校验 SHA256、安装 npm 依赖并构建前端；后续启动复用本地文件。

默认地址：`http://127.0.0.1:8765/app/`。

```powershell
# 使用另一个端口
.\start-studio.ps1 -Port 8766

# 启动服务但不打开浏览器
.\start-studio.ps1 -NoBrowser
```

### 手动启动与开发

```powershell
python scripts/download-fonts.py
cd md2card
npm ci
npm test
npm run build
cd ..
python -X utf8 studio_server.py --port 8765
```

前端也可以在 `md2card/` 下运行 `npm run dev`。Vite 开发服务器仅提供前端，长文 PDF 接口由 `studio_server.py` 提供；测试完整导出流程时请构建后使用本地服务。

Windows 一键入口已经验收；其他系统可手动运行上述 Python/npm 命令。Windows 系统字体在其他系统上会回退，Typst 长文链路建议按本机字体配置替换。

## 在界面中调整

1. 在 **Markdown 编辑** 中填写正文或导入 `.md`，按需绑定图片。
2. 在 **排版设置 → 主题** 选择纯净排版、柔光浅紫、雾松笔记或雾蓝实验室。
3. 在 **字体配色** 分别选择标题、正文、引用字体，也可以点击字体样张直接修改标题。
4. 用取色器设置强调色、背景色和正文色；纹理可选纯色、细点纸、方格纸或跟随主题。
5. 在 **排版** 调整字号、行距和段间距，在 **画布** 设置边距、比例和封面。
6. 右侧查看自动分页，然后选择导出方式。

草稿和设置保存在当前浏览器的 IndexedDB。更换浏览器、端口或访问地址会使用独立草稿存储。

## 字体准备

提供 12 个中文字体选项：

- 思源黑体：上游 npm 字体包。
- 思源宋体、站酷小薇、站酷庆科黄油、站酷快乐体、马善政毛笔楷书、志莽行书、龙藏体：项目字体库。
- 微软雅黑、宋体、楷体、仿宋：本机 Windows 字体，不随仓库分发。

字体清单在 `fonts/manifest.json`，记录固定上游版本、下载地址、SHA256 和许可证。运行准备脚本后，字体位于 `fonts/`，前端副本位于 `md2card/public/fonts/`。

```powershell
# 常规准备：已存在且校验通过的字体不会重复下载
python scripts/download-fonts.py

# 可选：从另一个已准备的字体目录读取，并校验后复制
python scripts/download-fonts.py --cache /path/to/existing/fonts
```

首次准备需要网络；准备和构建完成后，内置字体与资源不再依赖在线字体服务。

## 导出方式

| 入口 | 输出 | 特点 |
|---|---|---|
| 下载图片 | PNG ZIP | 每张卡片一张图片，预览即导出 |
| 卡片 PDF | 多页 PDF 下载 | 保留卡片画布；文字以图像保存 |
| 长文 PDF | Letter PDF | Quarto + Typst 重排，文字可选中 |

长文导出接收所选字体、颜色、背景、字号、边距和绑定的本地图片。封面、卡片装饰和分页由长文模板决定，和卡片 PDF 不完全相同。Mermaid 在长文 PDF 中渲染为完整图片，卡片预览目前将其作为代码块显示。

服务默认只监听本机 `127.0.0.1`。长文请求包含文章与图片，在本机生成：

- `studio-articles/`：中间源文件、图片和渲染日志。
- `output/pdf/studio-articles/`：正式长文 PDF。
- 卡片 PDF 和 PNG ZIP：浏览器下载目录。

当前长文接口上限为请求总量 30 MB，单张图片 12 MB，每次最多 30 张图片；同一服务一次处理一个长文任务。

## 命令行长文

```powershell
# 普通 Markdown 复制为 .qmd，再生成 PDF
.\render.ps1 -File '.\我的文章.md'

# 同时导出 150 DPI 切页 PNG
.\render.ps1 -File '.\我的文章.qmd' -ExportPages

# 重新转换同名 Markdown
.\render.ps1 -File '.\我的文章.md' -Force
```

原始 `.md` 不改动。Quarto 块使用 `{mermaid}`，正文其余内容保留。项目渲染后钩子会按纸张和边距等比例缩小过高图片，并修正搬迁后的资源路径。

字体、配色和背景由 `_quarto.yml`、`styles/typst-template.typ` 与 `styles/typst-show.typ` 统一控制。新文章起点见 `templates/文章模板.qmd`，视觉演示见 `templates/可视化示例.md`。

## 目录与维护

```text
markdown-studio/
├── md2card/             # 前端源码、24 项测试、原始 MIT 许可证
├── studio_server.py     # 静态服务与 /api/render
├── start-studio.ps1     # Windows 启动、字体准备和首次构建
├── fonts/               # 清单与 OFL 许可证，字体二进制由脚本下载
├── scripts/             # 字体准备、Markdown 转换、图片缩放、重编译
├── styles/              # Typst 主题
├── templates/           # 写作模板和演示稿
└── _quarto.yml          # 项目级长文配置
```

上游源码快照和校验信息见 `md2card/UPSTREAM.json`；本地定制见 `md2card/LOCAL_CHANGES.md`。上游自动发布 GitHub Pages 的配置未带入当前仓库；本应用长文接口需要本地 Python/Quarto 服务，静态 Pages 无法提供它。

提交源码、模板、许可证、字体清单和锁文件；不提交 `node_modules/`、`dist/`、字体二进制、渲染缓存、浏览器草稿或导出文件。
