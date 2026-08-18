---
name: adapt-social-content
description: 把已经审核过的中文专业技术文章改写成微信公众号、小红书、X/Twitter、知乎、即刻或视频脚本等社交平台内容，保持 claim ledger 事实边界，重组平台表达、标题、节奏、卡片脚本和视觉交接。不要在此阶段重新研究项目、发明技术结论或直接生成图片。
---

# 社交平台内容适配

把专业文章转换成不同平台的阅读产品，而不是把文章逐段压缩或把每个名词做成一张卡片。文章是事实和论点的来源，社交内容负责降低进入门槛、保留关键机制、引导读者继续阅读。

## 职责边界

本 skill 负责：

- 选择平台、读者任务和内容预算；
- 重写标题、开头、节奏和表达方式；
- 设计卡片问题、结论、机制和页面关系；
- 把复杂内容拆成关系页与证据页；
- 输出给图片制作 skill 的 `card-script.md` 和 `visual-brief.md`；
- 对最终社交文案做事实、解释和平台适配检查。

本 skill 不负责：

- 从零研究仓库或系统；
- 修改专业文章的中心论点；
- 添加文章和 claim ledger 没有支持的版本、benchmark、热度或竞品结论；
- 直接生成图片、封面、PDF 或视频文件。

## 输入要求

必须读取：

```text
article.md
claim-ledger.md
```

优先读取：

```text
article-purpose.md
visual-brief.md
research-manifest.yaml
```

如果文章没有批准状态、claim ledger 或研究来源，生成 `needs-article-review.md`，不要自行补研究。

## 必须执行的流程

### 1. 选择平台和阅读任务

创建 `channel-strategy.md`，记录：

- 执行模式：`reviewed` 或 `one-pass`；
- 主平台和目标读者；
- 读者在这个平台上要完成的任务；
- 本平台必须讲完整的内容；
- 哪些证据和细节留给长文；
- 字数、页数、视频时长或其他预算；
- 图片解释什么，正文补充什么。

不同平台的默认职责：

- 小红书：交付一个紧凑但完整的心智模型，不是文章段落画廊；
- 微信公众号：保留问题、论证、机制、比较和来源，可以是长文导读或独立文章；
- X/Twitter：拆成有因果关系的观点线程，不能只列结论；
- 知乎：围绕问题和决策条件组织，明确适用与不适用；
- 视频：把每个段落改成一个可听懂的动作、例子或判断。

### 2. 先写页面问题，再写卡片文字

创建 `card-script.md`。每个页面必须有：

1. 一个具体读者问题；
2. 一个回答该问题的结论；
3. 一个机制、因果链、例子或决策条件；
4. 一个明确的视觉关系：比较、流程、层次、时间线或决策树；
5. claim IDs、需要精确保留的术语和禁止新增的事实。

推荐表格字段：

```text
Page | Role | Question | Core Claim | Mechanism or Example | Benefit | Cost/Boundary | Render Mode | Paired With | Claim IDs | Exact Text | Forbidden Additions
```

如果一个页面只能剩下一串名词而不损失意义，它不是合格的解释页。机制页必须同时说明收益以及成本、边界或失败条件。

### 3. 让文案和图片互补

创建 `social-copy.md`，包含：

- Cover Title；
- Post Title；
- Body；
- Caption-only Evidence and Nuance；
- Tags。

图片承载心智模型、机制和关键比较；正文承载研究方法、来源、限制、判断和长文阅读路径。不要逐页复述图片内容。

拒绝以下内容：

- “爆火”“新星”“最强”等未经核实的流行度判断；
- “一分钟看懂”“建议收藏”等空洞钩子；
- 文章没有的 benchmark、版本、stars、排名或成熟度标签；
- 只讲收益、不讲代价的产品宣传。

### 4. 对图片页做渲染路由

每个页面必须选择一个 `render_mode`：

- `reuse-evidence`：可读的官方架构图、UI、benchmark 表格或仓库资产；
- `deterministic-evidence`：代码、命令、配置、日志、URL、长段精确文字；
- `generated-relationship`：低文字量的比较、流程、层次、因果链或总结。

代码和精确技术文本不能交给图片模型排版。需要解释和证明时，使用：

```text
关系解释页 → 确定性证据页
```

按证据类型固定路由：

- `reuse-evidence` 与 `deterministic-evidence` 交给 `guizang-social-card-skill`；
- `generated-relationship` 默认交给 `baoyu-xhs-images`；如果关系页仍含较多精确文字，也交给 `guizang-social-card-skill` 确定性渲染。

交接时提供已批准的中心论点、页面脚本、精确短文本、claim IDs、禁止新增项、目标尺寸和参考图片。

### 5. 运行社交内容门禁

阅读 [references/social-gates.md](references/social-gates.md)，并在需要发布图片时创建 `image-review.md`。运行：

```powershell
python -X utf8 <research-skill-path>\scripts\validate_research_artifacts.py <content-folder> --mode social-plan
```

图片生成后还要记录实际尺寸、手机宽度可读性、事实、解释、视觉和生产结果。未通过的页面先改 `card-script.md`，不要反复生成同一张弱解释卡片。

## 输出协议

默认输出：

```text
channel-strategy.md
card-script.md
social-copy.md
```

图片制作前额外输出或确认：

```text
visual-brief.md
```

图片制作后由下游流程生成：

```text
image-review.md
```

## 不可违反的规则

- 文章和 claim ledger 是事实来源，社交适配不能创造新事实。
- 平台钩子不能牺牲技术含义和边界条件。
- 不要把每个文章段落机械转换成卡片。
- 不要把关系图和密集证据塞进同一页。
- 不要把 deterministic-evidence 页面交给图片生成模型。
- 不要把图片生成 skill 的视觉规则复制到这里；只输出可执行的页面合同。
