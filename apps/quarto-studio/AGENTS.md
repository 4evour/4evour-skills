# 开发约定

- 本应用与 `../markdown-studio/` 独立运行；保留现有 MD2Card 版本及其渲染行为。
- 唯一正文生成链路为 Markdown/QMD → Quarto → Typst → PDF；预览和 PNG 来自该 PDF。
- `web/` 仅承担编辑、参数控制、任务反馈和查看生成结果，不做 HTML 正文排版或浏览器分页。
- 保留原始文章内容和 YAML；源文转换只处理 Mermaid 围栏、显式分页与图片资源路径。
- 字体清单和许可证在 `fonts/`，字体二进制、任务文件和导出结果不提交。
- 字体、颜色、纸张和边距通过渲染元数据进入 Typst 模板；必须保留高图缩放钩子。
- 使用 Python 标准库运行服务，前端使用原生 HTML/CSS/JavaScript，无 npm 构建依赖。
- 验证运行 `python -m unittest discover -s tests -v`，导出改动还需检查实际 PDF 和 PNG。
