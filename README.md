# 4evour 内容生产与可视化排版工作台

这个仓库把中文技术内容生产与可视化排版放到同一条流程里：先用 Skills 研究、写作和整理文案，再把 Markdown 交给本地 Web 工作台，制作小红书卡片、图片和 PDF。

2026-10-13 起，仓库新增可运行的 **Markdown Studio**。原有八个 Skills 和精选示例继续保留，应用源码位于 [`apps/markdown-studio/`](apps/markdown-studio/)。

## 选择入口

| 你要做什么 | 从哪里开始 |
|---|---|
| 导入文章，直接调整字体、颜色、背景和分页 | [Markdown Studio](apps/markdown-studio/README.md) |
| 写八股母稿、原理讲解或有证据的技术文章 | [内容 Skills 导航](docs/skills-guide.md) |
| 把已有母稿改成小红书文案和卡片脚本 | [adapt-social-content](adapt-social-content/SKILL.md) |
| 检查中文表达，保留事实和作者声音 | [tech-writing-zh](tech-writing-zh/SKILL.md) |
| 查看已有内容和交付样例 | [精选示例](examples/README.md) |

## 可视化排版工作台

工作台基于 **MD2Card** 的 MIT 开源源码改造，在浏览器中编辑 Markdown，右侧实时预览和自动分页。

- **字体选择**：12 个中文字体选项，标题、正文和引用可分别搭配；7 款新增开源字体在首次启动时下载并校验。
- **主题与颜色**：4 套卡片主题，可自定义强调色、背景色和正文色。
- **背景与版式**：纯色、细点纸、方格纸；字号、行距、段间距、边距、画布比例和封面模式均可调整。
- **图片管理**：导入本地图片并绑定 Markdown 引用，检查缺失及冲突。
- **三种导出**：PNG 图片包、与预览一致的卡片 PDF，以及 Quarto + Typst 生成的 Letter 长文 PDF。
- **本地工作**：服务默认只监听 `127.0.0.1`；草稿保存到当前浏览器，长文文件保存到应用的本地输出目录。

### Windows 快速启动

需要 Node.js 24+、Python 3.10+ 和 PowerShell 7。选择“长文 PDF”时还需要安装 Quarto；命令行导出逐页 PNG 时需要 Poppler。

在仓库目录打开 PowerShell：

```powershell
cd apps/markdown-studio
.\start-studio.ps1
```

也可以双击 [`启动排版工作台.cmd`](apps/markdown-studio/启动排版工作台.cmd)。首次运行会准备字体、执行 `npm ci` 并构建前端；之后打开本地工作台。

默认地址：`http://127.0.0.1:8765/app/`。端口被其他应用占用时：

```powershell
.\start-studio.ps1 -Port 8766
```

点击 **排版设置 → 字体配色** 开始调样式。完整安装、开发、导出说明和限制见 [工作台 README](apps/markdown-studio/README.md)。

### 三种导出的区别

| 导出 | 用途 | 页面与文字 |
|---|---|---|
| PNG ZIP | 小红书图文、分享卡片 | 每张卡片一张图片 |
| 卡片 PDF | 保留预览画布，按页分享 | 每张卡片一页，页面为图像 |
| 长文 PDF | 阅读或归档完整文章 | Letter 重新分页，文字可选中 |

长文 PDF 会接收字体、配色、背景和边距参数，但使用自己的文章模板，分页与卡片不同。Mermaid 在长文 PDF 中渲染为完整图片；卡片预览目前沿用上游的代码块展示。

## 从选题到交付

```text
选题与事实核实
  → 内容 Skills：研究 / 母稿 / 中文表达
  → adapt-social-content：平台文案与卡片脚本
  → Markdown Studio：字体、配色、背景、分页与预览
  → PNG 图片包 / 卡片 PDF / 正式长文 PDF
```

Skills 负责内容和事实边界；工作台负责排版和导出。先审核技术结论，再调整呈现方式。具体 Skill 的输入、输出和交接物见 [Skills 使用导航](docs/skills-guide.md)，既有待修问题见 [生命周期说明](docs/skill-lifecycle.md)。

## 仓库结构

```text
4evour-skills/
├── apps/markdown-studio/              # 本地 Web 工作台与 PDF 链路
│   ├── md2card/                      # Preact + TypeScript 前端
│   ├── studio_server.py              # 本地静态服务和长文导出接口
│   ├── fonts/                        # 字体清单、固定版本和许可证
│   ├── scripts/                      # 字体准备、Markdown 转换与图片缩放
│   ├── styles/                       # Typst 主题与文章模板
│   └── templates/                    # 写作与视觉示例
├── bagu-explainer/                    # 面试母稿
├── adapt-social-content/              # 平台表达
├── tech-writing-zh/                   # 中文表达检查
├── write-concept-explainer/            # 原理讲解
├── research-open-source-project/      # 开源研究
├── write-professional-technical-article/ # 技术长文
├── guizang-social-card-skill/          # 确定性卡片排版
├── baoyu-xhs-images/                  # 生成式视觉
├── examples/                         # 已有精选内容示例
└── docs/                             # Skills 导航、状态和维护文档
```

## 开发与验证

```powershell
cd apps/markdown-studio
python scripts/download-fonts.py
cd md2card
npm ci
npm test
npm run build
```

前端当前有 24 项测试，覆盖 Markdown 解析、图片绑定、分页和演示稿。长文导出还需检查实际 PDF、字体、图片与页边界。字体准备脚本固定上游版本并验证 SHA256；字体二进制、依赖、构建产物、个人稿件和导出文件不提交。

## 开源来源与许可证

本仓库包含不同来源的内容，按各自许可证处理：

- **Markdown Studio / MD2Card**：保留 [MIT License](apps/markdown-studio/md2card/LICENSE)，上游版本见 [UPSTREAM.json](apps/markdown-studio/md2card/UPSTREAM.json)，本地改动见 [LOCAL_CHANGES.md](apps/markdown-studio/md2card/LOCAL_CHANGES.md)。
- **新增中文字体**：来自 Google Fonts 官方仓库，各字体保留 SIL OFL 许可证；固定来源及校验值见 [字体清单](apps/markdown-studio/fonts/manifest.json)。本机 Windows 字体不随仓库分发。
- **baoyu-xhs-images**：保留 [MIT License](baoyu-xhs-images/LICENSE)。
- **guizang-social-card-skill**：保留 [AGPL-3.0 License](guizang-social-card-skill/LICENSE) 和 [商业授权说明](guizang-social-card-skill/COMMERCIAL_LICENSING.md)。
- 其余内容 Skills 继续遵循各自已有声明；不将不同来源视为一套统一许可证。
