# 本地定制记录

本项目来自 `haodongcui/md2card` 的 MIT 开源源码快照，版本信息见 `UPSTREAM.json`，原始许可证保留在 `LICENSE`。

新增功能：

- 字体配色设置分类：12 种中文字体、标题/正文/引用独立选择、字体样张。
- 强调色、背景色、正文色取色器，以及纯色、细点纸、方格纸背景。
- 卡片 PDF：以当前预览画布逐页生成。
- 长文 PDF：通过同源本地服务交给 Quarto + Typst 生成，可选择文字。
- 字体与颜色参数参与分页测量；所有新增开源字体通过固定版本清单下载到本地，并保留许可证。
- 原有 PNG 导出、Markdown 解析、内容分页、图片管理和浏览器草稿保存继续使用上游实现。

相关路径：

- `src/app/components/settings/TypographySettings.tsx`：可视化字体和颜色面板。
- `src/data/fonts.ts`、`src/styles/custom-fonts.css`、`public/fonts/`：字体库。
- `src/renderer/card-style.ts`、`src/styles/local-studio.css`：视觉参数映射。
- `src/export/export-pdf.ts`：卡片 PDF 导出。
- `src/app/App.tsx`、`src/app/components/WorkspaceHeader.tsx`：PDF 入口与反馈。
- 项目上级目录 `studio_server.py`：本地静态服务和长文 PDF 接口。

依赖更新：使用修复版本的 KaTeX / Vitest，以及 KaTeX override。`npm audit` 当前无已报告漏洞；更新后构建和 24 项上游测试通过。

本地运行请双击项目上级目录的 `启动排版工作台.cmd`。项目在本机监听 `127.0.0.1:8765`。

发布整理：应用纳入 `apps/markdown-studio/`；字体改为固定版本下载并验证 SHA256，首次启动自动准备。原始源码来源和 MIT 许可证保留，不带入上游 GitHub Pages 自动部署。
