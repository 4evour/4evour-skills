# 确定性证据页面

## 渲染路由

- `reuse-evidence`：官方资产已经准确且在目标尺寸可读；
- `deterministic-evidence`：代码、命令、配置、日志、URL、长文本和精确排版；
- `generated-relationship`：低文字量的关系、流程、层次、比较或总结。

`deterministic-evidence` 页面不能交给图像生成模型。需要概念解释和源码证明时，拆成“关系解释页 → 证据页”。

## 页面合同

```text
role: concept | evidence
render_mode: deterministic-evidence
paired_with: page id or none
claim_ids: exact ledger ids
source: repository path plus line or symbol
reader_question:
conclusion:
mechanism:
benefit:
cost_or_boundary:
```

证据页选择能完整证明一个机制的最小摘录，代码保持原文，标出路径、符号和 claim ID。不要用截图证明性能、正确性或生产成熟度。

## 验收

- 源码与可见摘录逐字核对；
- 记录真实尺寸和 360–420px 手机宽度的无缩放可读性；
- 保存 HTML/CSS 或其他可编辑布局源文件；
- 检查裁切、溢出、换行、语法高亮和中文字符；
- 任何看不清的页面先缩短内容或拆页，不先缩小字号。
