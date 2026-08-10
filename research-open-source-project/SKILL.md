---
name: research-open-source-project
description: 深入研究开源仓库，不停留在 README 摘要；基于源码证据形成独立论点、架构分析、竞品定位、设计权衡、可复用经验，并产出可发布的技术文章与经过质量检查的图文内容。适用于调研、讲解、评审或介绍 GitHub/开源项目，将仓库沉淀为专业博客、微信公众号文章、小红书图文、插图报告或 PDF 母稿，比较同类方案，解释代码为何这样设计，或执行可重复的一键式“研究到发布”工作流。
---

# 开源项目深度研究

把一个仓库转化为有证据支撑的技术解读。将 README 视为项目定位、术语、流程图和使用示例的重要一手资料，在其解释清晰时准确复用；同时让分析结论接受源码、测试、架构和竞品证据的检验。

## 必须执行的工作流

### 1. 明确范围与源码状态

- 确认本地仓库或准确的 GitHub URL、分支/标签与提交哈希。
- 记录调研日期，因为 Star、基准、API、限制和竞品都会变化。
- 优先使用本地仓库分析代码；对不稳定事实和外部结论浏览官方来源。
- 在不覆盖用户文件的前提下创建 `research/<repo-slug>/` 等调研目录。
- 若存在 `VOICE.md`，读取并遵循；否则创建草稿：在 `reviewed` 模式下请用户确认，在 `one-pass` 模式下采用专业技术分享默认人设。
- 记录发布渠道并选择 `reviewed` 或 `one-pass`。仅当用户明确要求“一键生成”或“端到端完成”时使用 `one-pass`；它省略的是重复偏好确认，不是证据门和质量门。

### 2. 先建立证据地图，再写正文

完整阅读 [references/research-method.md](references/research-method.md)，创建 `evidence-map.md`。

分开记录：

- 官方主张与产品定位；
- 架构与数据模型；
- 代码路径与运行时行为；
- 测试、CI、基准、失败处理与运维证据；
- 已记录的限制与路线图；
- 矛盾、证据缺口和开放问题。

收集证据时建立简短的 README 复用表，将段落或资源标记为 `reuse`、`adapt`、`verify` 或 `exclude`。不要为了显得原创而把准确的官方定义改写得更含糊；除非 README 的章节顺序恰好服务于文章论点，否则不要机械复制其结构。

优先使用 `rg` / `rg --files`。至少追踪一条从输入、存储、检索、交付到反馈的端到端路径。不要仅凭文件名推断运行时行为。

### 3. 形成独立论点

在正文前创建 `thesis.md`，必须包含：

- 一个中心论点；
- 一个常见但不完整的理解；
- 至少三条具体支撑观察；有源码时至少两条来自代码；
- 最强反方观点；
- 论点成立与不成立的条件；
- 当前仍未被证明的内容。

论点可以从 README 的洞察出发，但必须额外给出 README 本身未能建立的工程后果、边界、因果解释、竞品坐标或源码证据。

### 4. 建立论断账本

按照 [references/templates.md](references/templates.md) 创建 `claim-ledger.md`。

把每个重要论断分类为：

- `FACT`：被代码、测试、官方文档或实测结果直接支持；
- `INFERENCE`：由多条事实综合得到；
- `OPINION`：明确的价值判断；
- `OPEN`：证据不足或问题尚未解决。

每条 `FACT` 必须附来源、代码路径或测试命令。正文中的 `INFERENCE` 和 `OPINION` 必须明确写成作者判断。README 可以证明“项目声称、暴露或记录了什么”；若行为、性能或成熟度没有被独立验证，要标记为官方主张。

### 5. 按系统层级比较竞品

按照 [references/research-method.md](references/research-method.md) 的竞品方法执行。

- 使用竞品的官方仓库、文档、论文或基准。
- 比较核心抽象、数据模型、交付方式、治理、耦合、成熟度和运维成本。
- 当产品解决不同层级问题时，不使用功能勾选表打分。
- 明确写出每个主要竞品更强的地方。
- 区分项目自报的基准结果与独立复现结果。

### 6. 撰写技术文章母稿

完整阅读 [references/writing-and-voice.md](references/writing-and-voice.md)。先写可编辑的 `article.md`，再制作卡片或 PDF。

除非证据要求更好的结构，否则按以下论证顺序组织：

1. 具体工程问题；
2. 在全文前三分之一内给出中心洞察；
3. 代码证据与运行机制；
4. 设计为何有效；
5. 成本、失败模式与最强反方观点；
6. 竞品坐标；
7. 适用与不适用场景；
8. 可迁移的设计原则。

每个主要分析章节至少新增一种价值：代码证据、跨组件综合、设计权衡、反方观点或可复用原则。解释性章节可以准确复用强有力的官方材料，但要注明来源并纳入作者论证，避免为改写而改写。

### 7. 按需适配发布渠道

当需求包含小红书、微信公众号、社交卡片、插图文章、PDF 或一键发布时，完整阅读 [references/platform-adaptation.md](references/platform-adaptation.md)。

- 始终把 `article.md` 作为内容源头。
- 压缩内容前先创建 `channel-strategy.md`。
- 制作社交卡片时，先创建 `card-script.md`；每页必须包含问题、结论、机制/示例、视觉关系、Claim ID、精确术语和禁止添加内容。
- 创建与卡片互补而非重复的 `social-copy.md`。
- 在 `one-pass` 模式中使用已定义的专业技术分享默认值，内部审核后继续渲染与质量检查，不再询问常规风格偏好。

### 8. 把图片当作证据与解释工具

完整阅读 [references/visual-workflow.md](references/visual-workflow.md)，创建 `visual-plan.md`。

优先使用：

1. 仓库原生架构图和真实界面截图；
2. 聚焦后的代码片段和基准表格；
3. 用于表达独立论点的作者关系图；
4. 仅在前述材料无法清晰解释关系时使用生成式知识卡片。

生成小红书卡片时调用 `baoyu-xhs-images`，不要复制其渲染实现。保留提示词文件、参考图、备份规则和首图锚点链。在 `reviewed` 模式中保留用户确认门；在用户明确要求的 `one-pass` 模式中应用 `platform-adaptation.md` 的默认值并在内部审核后继续。向它提供已确认的 `article.md`、`channel-strategy.md`、`card-script.md` 和 `visual-plan.md`，不要让生图 Skill 重新从 README 猜测论点。

正文和视觉方案未确认前不要生图；Markdown 母稿未批准前不要导出 PDF。

### 9. 执行编辑、证据与发布质量门

完整阅读 [references/quality-gates.md](references/quality-gates.md)，然后运行：

```powershell
python scripts/validate_research_artifacts.py <research-folder>
```

修复所有结构性错误。人工检查事实和语气；脚本不能证明内容事实正确。

制作社交图文时，按阶段运行：

```powershell
python scripts/validate_research_artifacts.py <research-folder> --mode social-plan
python scripts/validate_research_artifacts.py <research-folder> --mode social-final
```

执行 `social-final` 前，完整阅读 [references/social-card-quality-gates.md](references/social-card-quality-gates.md)，检查每张成图，记录真实像素尺寸并创建 `image-review.md`。只要任一页面的事实、讲解、视觉或生产检查为 `FAIL`，就不能称其可发布。

## 输出约定

必需产物：

```text
research/<repo-slug>/
├── source-state.md
├── evidence-map.md
├── thesis.md
├── claim-ledger.md
├── article.md
└── visual-plan.md
```

仅在需求涉及相应渠道时添加：

```text
├── channel-strategy.md
├── card-script.md
├── social-copy.md
├── image-review.md
├── feedback.md 和 revision-plan.md
├── competitor-notes.md
├── image-cards/ 或 baoyu-xhs-images 输出链接
└── 从批准后的 article.md 生成的最终 PDF
```

## 不可违反的规则

- 不要机械复制 README 结构；在官方定义、示例和图片最清楚时可以复用，但必须服务于独立论点。
- 不要因为项目使用了某个机制，就直接称其具有创新性。
- 不要把限制统一藏在结尾免责声明里；把每项代价放在导致它的收益旁边。
- 没有直接比较证据时，不要写“全面领先”“颠覆”等夸张结论。
- 可以浏览时，不要凭记忆比较会变化的竞品信息。
- 不要让生成图片引入论断账本中不存在的事实。
- 不要为了平台钩子牺牲技术含义。
- 不要把名词列表当作技术讲解；必须给出机制、示例、因果链或决策条件。
- 不要因为提示词指定了宽高比，就相信生成文件一定符合；必须检查真实尺寸。
