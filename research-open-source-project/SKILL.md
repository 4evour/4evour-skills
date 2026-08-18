---
name: research-open-source-project
description: 对 GitHub 开源仓库和有源码的技术系统做证据驱动的深度调研，分析架构、数据模型、运行链路、工程权衡、竞争方案和未证实问题，产出可交给专业技术文章 skill 的研究包。用户要求研究、审查、解释或比较项目源码时使用；仅要求写文章、改写社交内容或制作图片时不要使用。
---

# 开源项目与技术系统研究

把仓库或技术系统还原成一份可复核的研究包，而不是 README 摘要。研究结论必须能回到源码、测试、官方文档、运行结果，或明确标记为推断的证据。

## 职责边界

本 skill 只负责技术研究，不负责：

- 撰写完整的 `article.md`；
- 设计微信公众号、小红书、X 或视频文案；
- 生成图片、PDF 或社交卡片；
- 为了制造“爆点”而添加没有证据的趋势、排名或先进性判断。

研究阶段可以提出候选技术论点，但最终文章论点由 `write-professional-technical-article` 选择。

## 输入与研究模式

接受以下输入：

- 本地仓库路径；
- GitHub 仓库 URL、分支、tag 或 commit；
- 论文、官方文档和仓库的组合；
- 用户指定的比较对象和问题。

如果用户没有指定 commit，先记录当前 commit 和研究日期。外部易变事实必须访问官方来源并记录访问日期。

支持两种模式：

- `reviewed`：完成每一阶段后保留待确认的研究包；
- `one-pass`：用户明确要求一键调研时连续完成研究，但不跳过证据、反证和质量检查。

## 必须执行的流程

### 1. 固定研究范围和来源状态

创建 `research/<topic>/`，不要覆盖已有文件。生成 `source-state.md`，记录：

- 仓库或系统名称、远程地址和本地路径；
- branch、tag、commit 和研究日期；
- 主要语言、入口、服务、存储和外部依赖；
- 已检查的官方文档、论文和比较对象；
- 本次研究要回答的问题和明确不回答的问题。

优先使用本地源码；对版本、benchmark、API、发布日期、stars 和竞品能力等易变事实访问官方来源。

### 2. 先建证据图，再写判断

阅读 [references/research-method.md](references/research-method.md)，生成 `evidence-map.md`。至少区分：

- 项目官方声称和产品定位；
- 架构、组件边界和数据模型；
- 从输入到存储、检索、交付、反馈的端到端代码路径；
- 测试、CI、benchmark、错误处理、可观测性和部署证据；
- 限制、路线图、矛盾证据和开放问题。

至少跟踪一条完整链路：

```text
输入 → 校验 → 转换 → 持久化 → 检索 → 交付 → 反馈
```

不要仅凭文件名、README 目录或类名推断运行行为。

### 3. 建立 README 使用边界

在 `evidence-map.md` 中维护 README reuse map，把内容标为：

- `reuse`：定义、术语、图表或示例准确且适合直接保留；
- `adapt`：事实准确，但需要围绕研究问题重组；
- `verify`：行为、性能、成熟度或对比结论需要源码或其他来源验证；
- `exclude`：宣传性、过时、重复或与问题无关。

README 可以证明项目的意图、公开接口和文档化流程，不能单独证明运行正确性、生产成熟度、性能优势或 benchmark 可复现。

### 4. 形成候选技术论点

生成 `thesis.md`，使用 [references/templates.md](references/templates.md) 中的固定结构：

- 一个可证伪的中心判断；
- 一个常见但不完整的理解；
- 至少三条支持观察，其中源码可用时至少两条来自代码；
- 最强反论点；
- 判断成立的条件和失效边界；
- 当前证据无法证明的内容。

候选论点必须通过 added-value、so-what、counterargument、boundary 和 evidence-diversity 检查。若只是重复 README，继续研究而不是润色摘要。

### 5. 建立 claim ledger

生成 `claim-ledger.md`，把每个重要结论标记为：

- `FACT`：源码、测试、官方文档或测量结果直接支持；
- `INFERENCE`：由多条事实综合得到；
- `OPINION`：明确的作者判断；
- `OPEN`：证据不足或尚未解决。

每个 `FACT` 都要带源码路径、符号、测试命令或官方 URL；不稳定的外部事实要带访问日期。不要用一个 claim ledger 行作为另一个 `FACT` 的唯一证据。

### 6. 比较系统层而不是堆功能

用户要求竞品比较时，创建 `comparison-matrix.md` 或 `competitor-notes.md`，至少比较：

| 维度 | 要回答的问题 |
|---|---|
| 主抽象 | 系统把什么对象当作核心？ |
| 数据模型 | 记录、向量、图、文件、block 还是多种资产？ |
| 更新模型 | 同步、后台、增量、版本化还是时间有效？ |
| 检索与交付 | 搜索、注入、常驻状态还是工具调用？ |
| 治理 | 所有权、ACL、版本、租户和 loadout 如何处理？ |
| 耦合 | SDK、服务、Agent Runtime、框架插件还是代理层？ |
| 验证 | 测试、benchmark、provenance 和公开评估是什么？ |
| 运营成本 | 数据库、队列、模型调用和故障面是什么？ |

每个主要竞品都要说明它在哪个条件或系统层更强。不要从记忆中比较随时变化的项目。

### 7. 运行研究质量门禁

阅读 [references/quality-gates.md](references/quality-gates.md)，逐项检查来源完整性、实现证据、比较公平性、反证、限制和可复核性。运行：

```powershell
python -X utf8 scripts/validate_research_artifacts.py <research-folder> --mode research
```

脚本只检查结构，不代替人工判断事实是否成立。

## 研究包输出协议

默认输出以下文件：

```text
research/<topic>/
├── research-manifest.yaml
├── source-state.md
├── evidence-map.md
├── thesis.md
├── claim-ledger.md
├── comparison-matrix.md       # 需要比较时生成
└── open-questions.md          # 有未决问题时生成
```

`research-manifest.yaml` 至少包含：

```yaml
topic:
stage: research
research_date:
commit:
claim_ledger: claim-ledger.md
status: draft | reviewed | complete
open_questions: open-questions.md
```

交给下游文章 skill 时，必须明确研究包路径、状态、研究 commit 和 `claim-ledger.md` 位置。下游若缺少关键证据，应返回待补研究项，而不是自行编造事实。

## 不可违反的规则

- 不要机械复制 README 的章节顺序。
- 不要因为项目使用某个机制就称其为创新。
- 不要把官方 benchmark 写成独立复现结果。
- 不要隐藏限制；把成本放在产生收益的设计旁边。
- 不要用 stars、热度或“爆火”替代技术证据。
- 不要把推断或意见伪装成事实。
- 不要在研究阶段生成社交图片或平台化文案。
