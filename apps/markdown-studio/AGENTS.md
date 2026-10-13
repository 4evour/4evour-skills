# 工作台开发约定

- 本目录是基于 MD2Card 改造的本地应用；保留 `md2card/LICENSE` 和 `UPSTREAM.json`。
- 前端源代码位于 `md2card/src/`，本地服务入口为 `studio_server.py`。
- 字体、字号和间距需要同时应用到可见卡片及隐藏的分页测量区。
- 新增开源字体必须记录许可证、固定下载地址和校验值；不提交字体二进制副本。
- 长文 PDF 使用 `_quarto.yml` 和 `styles/` 中的 Typst 模板，Mermaid 由 Quarto 渲染。
- `output/`、`studio-articles/`、`tmp/`、`node_modules/` 和 `dist/` 不纳入版本管理。
- 验证前端改动时运行 `npm test` 和 `npm run build`；导出链路改动应额外检查本地接口和实际 PDF。
