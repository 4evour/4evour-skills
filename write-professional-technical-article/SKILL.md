---
name: write-professional-technical-article
description: 基于技术研究包写作专业、证据充分、论点清晰的中文技术文章，适用于开源项目、Agent 系统、数据库、分布式系统、论文解读和架构设计。负责文章目的、论证结构、机制解释、权衡、限制、图表计划和编辑审校；不要在没有证据时自行补充事实，也不要负责社交平台改写或图片生成。
---

# 专业技术文章写作

把研究包转化成一篇有明确读者收益和独立判断的技术文章。文章不是研究记录的复制品，也不是 README 的改写，而是围绕一个问题组织证据、机制和取舍。

## 职责边界

本 skill 负责：

- 明确文章目的、读者和认知转变；
- 从研究包中选择最终中心论点；
- 组织论证顺序和章节职责；
- 用源码、数据模型、运行链路和失败路径解释机制；
- 将收益、成本、边界和反论点放在同一设计决策旁边；
- 设计图表、代码摘录和其他证据的使用位置；
- 进行结构编辑、事实边界检查和语言编辑。

本 skill 不负责：

- 代替 `research-open-source-project` 完成源码调研；
- 把未经研究包支持的推测写成事实；
- 将文章直接改写成小红书、X、视频或其他平台内容；
- 调用图片生成 skill 制作图片。

## 输入要求

优先读取一个完整研究包，至少包括：

```text
source-state.md
evidence-map.md
thesis.md
claim-ledger.md
research-manifest.yaml
```

如果文章涉及竞品，还要读取 `comparison-matrix.md` 或 `competitor-notes.md`。如果缺少研究 commit、claim ledger 或关键证据，先输出 `needs-research.md`，列出需要补充的研究项，不要凭记忆填空。

读取项目根目录的 `VOICE.md`（如果存在）。没有时使用 [references/article-method.md](references/article-method.md) 中的专业技术默认风格。

## 必须执行的流程

### 1. 写文章目的，而不是先起标题

创建 `article-purpose.md`，回答：

- 为什么现在值得写；
- 目标读者是谁，已有知识是什么；
- 读者阅读前的常见误解是什么；
- 读者读完后应该能做出什么判断或设计决策；
- 本文明确不做什么；
- 文章使用哪些研究包证据。

### 2. 建立论证地图

创建 `argument-map.md`，记录：

- 一个中心论点；
- 支撑它的一级和二级论点；
- 每个论点对应的 claim ID、源码或官方来源；
- 章节之间的因果关系；
- 最强反论点和回应；
- 哪些判断仍然是 `OPEN`。

不要把研究阶段的候选 thesis 原样当作文章论点。根据读者任务选择最有解释力、证据最充分、边界最清晰的一个。

### 3. 设计章节职责

创建 `outline.md`。默认顺序是：

1. 具体工程问题；
2. 前三分之一内给出中心洞察；
3. 解释代码路径、数据模型和运行机制；
4. 将收益与产生收益的成本放在一起；
5. 处理故障、限制和最强反论点；
6. 将竞品放在同一系统坐标中比较；
7. 说明适用、不适用场景和可迁移原则。

每个标题单独扫描时都应能表达论证，不使用“技术实现”“总结”这类空标题。

### 4. 写作与证据绑定

创建 `article.md`，以 Markdown 作为唯一主稿。每个重要判断都要：

- 绑定 claim ID 或明确标注为作者推断；
- 指出源码路径、符号、测试、测量或官方来源；
- 解释“发生了什么、为什么这样设计、带来什么收益、付出什么成本”；
- 在证据不足处使用“尚未证明”“当前公开材料没有说明”等精确表述。

不要把一串组件名、功能名或抽象名词当成技术解释。首次出现的术语要用普通语言解释。

### 5. 设计视觉证据

创建 `visual-brief.md`，只描述视觉任务，不生成图片。每个视觉项记录：

```text
visual_id:
reader_question:
purpose:
claim_ids:
source_or_path:
render_mode: reuse-evidence | deterministic-evidence | generated-relationship
exact_text:
paired_with:
```

- `reuse-evidence`：复用可读的官方图、UI 或测量结果；
- `deterministic-evidence`：代码、命令、配置、日志、URL 和长段精确文字；
- `generated-relationship`：低文字量的流程、层次、比较、因果链或总结。

密集证据和关系解释需要拆成两项，不要为了塞进一张图而缩小文字。

### 6. 进行两轮编辑

创建 `editorial-review.md`：

- 结构编辑：文章目的、中心论点、章节顺序、证据覆盖、反论点和读者收益；
- 语言编辑：术语一致性、段落节奏、标题信息量、事实/推断/意见区分和重复表达。

只有结构和事实边界通过后，才把文章交给 `adapt-social-content`。

运行文章结构检查：

```powershell
python -X utf8 <research-skill-path>\scripts\validate_research_artifacts.py <content-folder> --mode article
```

## 输出协议

默认输出：

```text
article-purpose.md
argument-map.md
outline.md
article.md
visual-brief.md
editorial-review.md
```

文章 front matter 至少记录：

```yaml
title:
subtitle:
research_path:
research_commit:
research_date:
audience:
status: draft | reviewed | approved
```

下游社交内容 skill 只读取已批准的 `article.md`、`claim-ledger.md` 和 `visual-brief.md`。如文章仍有 `OPEN` 结论，要在文章中明确标出，而不是在平台改写时删除边界。

## 写作规则

- 先给判断，再展示它如何从证据中得到。
- 用第一人称表达解释性判断，例如“我的阅读是……”。
- 用直接语言表达已验证行为，例如“该函数在……之前写入……”。
- 把限制写在产生收益的设计旁边。
- 不使用“最强”“全面领先”“革命性”“一分钟看懂”“建议收藏”等无证据或模板化表达。
- 每个主要分析章节至少增加代码观察、跨组件综合、权衡、反例或可迁移原则中的一项。
- 文章即使没有图片也必须能独立完成论证。
