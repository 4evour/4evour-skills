# MD2Card 前端：Markdown Studio 本地定制

这是 `haodongcui/md2card` 的 MIT 开源前端快照及本地定制。完整安装、启动和 PDF 导出说明见 [工作台 README](../README.md)。

```powershell
# 先在上级工作台目录准备字体
python ../scripts/download-fonts.py
npm ci
npm test
npm run build
```

- 源码：`src/`，Preact + TypeScript。
- 24 项测试：`tests/unit/parse-and-layout.test.ts`。
- 本地字体：`public/fonts/`，由准备脚本生成，不提交。
- 构建：`dist/`，由上级 `studio_server.py` 运行本地服务。
- 上游来源：[UPSTREAM.json](UPSTREAM.json)。
- 原始许可证：[LICENSE](LICENSE)。
- 定制说明：[LOCAL_CHANGES.md](LOCAL_CHANGES.md)。

保留原有 Markdown 解析、分页、图片管理和 PNG 导出，新增独立字体选择、颜色与背景控制、卡片 PDF 和本地长文 PDF 入口。
