# 项目字体

`manifest.json` 记录 7 款新增中文字体的固定上游版本、下载地址、SHA256 和 SIL OFL 许可证。字体文件通过下载脚本准备，不提交二进制副本。

```powershell
python scripts/download-fonts.py
```

脚本会校验字体并复制到前端的 `md2card/public/fonts/`。思源黑体由 npm 字体包提供；微软雅黑、宋体、楷体与仿宋使用本机字体。
