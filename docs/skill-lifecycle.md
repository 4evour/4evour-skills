# Skill 生命周期与整理计划

> 初始整理日期：2026-10-08；本次复核日期：2026-10-09。
> 复核基线：`daf38486091900a68a7b143e0978b0986cbba959`。

本文件回答“现在先用哪些、哪些需要适配、什么情况下再归档”。结论来自仓库内指令、脚本和精选示例，不来自运行频率统计；没有核实所有上游版本，也没有执行图片生成、浏览器渲染或 Live Photo 生产。

## 1. 状态含义

| 状态 | 含义 | 默认动作 |
|---|---|---|
| `active` | 当前小红书技术内容目标的主要入口 | 纳入最小内容安装集合 |
| `optional` | 特定主题或视觉任务才需要 | 按任务安装和启用，不等于失效 |
| `candidate-archive` | 替代路径已明确，仍需要迁移确认 | 不放入默认流程，先记录替代与恢复方式 |
| `archived` | 已确认退出维护，并完成归档 | 放入 `archive/`，不参与默认安装 |

“待修正 / 待适配”是维护问题，不是另一个归档状态。目前没有 `candidate-archive` 或 `archived` 的实际目录；本次未移动、删除或改写任何 Skill 指令。

## 2. 当前分组与维护动作

| Skill | 使用状态 | 分组 | 维护判断与下一步 |
|---|---|---|---|
| `bagu-explainer` | active | 小红书常用 | 保留。规范和题单可作为八股入口；补齐来源台账、社交交接和专用格式校验；历史 Redis 示例不能代替当前规范 |
| `adapt-social-content` | active | 小红书常用 | 保留。专注发布策略和卡片脚本；需要接纳八股 / 概念母稿的正式输入协议，并匹配轻量内容校验 |
| `tech-writing-zh` | active | 小红书常用 | 保留。使用作者样本和最小改稿；把经历复盘规则与纯知识讲解分开，避免把八股母稿误压成短笔记 |
| `write-concept-explainer` | optional | 专题扩展 | 保留，不与八股入口合并。讲心智模型时启用；补充事实台账、审核状态和 `explainer.md` 到社交输入的映射 |
| `research-open-source-project` | optional | 专题扩展 | 保留证据职责。用于有源码或一手资料的研究，不要求每篇八股跑完整研究包；校验器的目录与模式限制需要明确 |
| `write-professional-technical-article` | optional | 专题扩展 | 保留论证职责。已有研究包才用；不要与 `tech-writing-zh` 的润色职责重复。审核包和跨目录校验尚需适配 |
| `guizang-social-card-skill` | optional | 视觉工具 | 精确文字卡片优先使用，但先确认 Node.js / Playwright / Chromium；静态卡片和 Live Photo 分开准备，macOS Swift 路径不承诺在 Windows 可运行 |
| `baoyu-xhs-images` | optional | 视觉工具 | 保留低文字量插画能力。后端和 wrapper 不随本仓库完整提供；先核对当前运行时和确认方式，不作为文字密集八股的默认路径 |

这次调整的是导航和维护建议。以前的“六个内容 Skill 全部 active”没有体现选题差异；专题扩展改为按需使用，不代表否定它们的用途。

## 3. 已确认的问题

### P1：规范与示例不一致

证据：

- [`bagu-explainer/SKILL.md`](../bagu-explainer/SKILL.md) 要求每题 Q/A/W 齐全，按“知识点 / 面试问答”两层组织。
- [`Redis output-qna.md`](../examples/bagu-explainer/redis/output-qna.md) 有 28 组 Q/A，没有 W 层，章节内使用 `**知识点**` 和 `**面经真题**`，不是当前固定模板。
- [`网络初稿`](../examples/tech-writing-zh/computer-network/before-bagu.md) 与 [`网络改稿`](../examples/tech-writing-zh/computer-network/after-tech-writing.md) 各含 11 个模块、19 组 Q/A/W，更适合参考当前骨架。

本次处理：在主 README、示例索引和 Redis 说明中标记历史格式，保留原稿，不补写未经核实的答案。

后续：如果迁移 Redis，另产出当前格式版本并记录适用技术版本与来源；不覆盖历史文件冒充原有成品。

### P1：八股 / 概念线到社交线的交接没有闭环

证据：

- [`adapt-social-content/SKILL.md`](../adapt-social-content/SKILL.md) 要求 `article.md`、`claim-ledger.md`、审核状态与来源。
- 八股 Skill 只要求交付 Markdown；概念 Skill 交付 `explainer.md`、`editorial-review.md` 等，但没有完整产出社交所需输入。
- 根 README 原来的“三条线审核后都可进入社交适配”没有说明中间还需补文件与协议。

本次处理：README 明示保留母稿、建立 `article.md` 输入或映射、补事实台账、记录真实审核状态、准备视觉合同。

后续：在两个上游 Skill 和社交 Skill 中统一轻量交接协议；不能只改文件名，不校验事实与状态。

### P1：研究校验器不等于所有线路的验收器

证据：[`validate_research_artifacts.py`](../research-open-source-project/scripts/validate_research_artifacts.py) 的 `validate()`：

- 每个模式先要求基础研究文件；八股 / 概念线没有相应轻量模式。
- `article` 模式加文章文件；`social-plan` / `social-final` 模式加社交文件，不自动同时检查全部文章阶段文件。
- 文件查找使用同一个 `folder`；不会解析研究、文章、社交的多目录关联。
- `research-manifest.yaml`、事实证据是否有效、真实图片能否阅读等，不会因结构通过就得到验证。

精选示例还省略部分文件与图片，因此不能承诺开箱即可通过这个脚本。

本次处理：README 分开介绍自测、研究结构检查、文风提示和真实图片验收，写明限制。

后续：增加轻量八股 / 概念验收模式、阶段目录映射，以及 Q/A/W 字数、互引、题量和实际页数检查。

### P2：写作规则有体裁边界，不能全部机械执行

证据：[`tech-writing-zh/references/workflow.md`](../tech-writing-zh/references/workflow.md) 的从零写作流程围绕 `PROJECT_LOG` 和项目经历，并要求“全文 ≥2 处真实的时间/失败/情绪”；[`SKILL.md`](../tech-writing-zh/SKILL.md) 同时要求最小改稿、不编第一人称经历。

本次处理：README 将它定位为八股母稿和发布文案的表达检查；保留 Q/A/W 和客观说明，不为满足经历条数编故事。

后续：区分经历复盘、纯知识讲解与面试口语答案的检查项；作者素材缺失时列需确认项，而不是强加经历。

### P2：视觉能力需要运行时与操作系统适配

证据：

- [`guizang package.json`](../guizang-social-card-skill/package.json) 和锁文件要求 Playwright；[`Live Photo 说明`](../guizang-social-card-skill/references/live-photo-production.md) 明确部分 Swift 辅助脚本需要 macOS、Swift 和 AVFoundation。
- [`baoyu 图片后端说明`](../baoyu-xhs-images/references/codex-imagegen.md) 需要运行时原生工具、外部 Skill 或额外 wrapper；本仓库没有完整提供这些后端。
- 对具体工具名、wrapper 参数、批量能力和确认方式的说明，不能据此保证在任意当前运行时可直接运行。

本次处理：两套视觉 Skill 都按需启用；技术密集卡片优先确定性排版，插画只承担低文字量关系解释。

后续：分别验证静态渲染、图片生成和 Live Photo；通过一个文档测试不等于三个能力全部可用。没有适配前，不宣称“只复制目录即可出图”。

### P2：旧预算与安装方式需要明确适用范围

证据：

- 八股输出规范把 18 页写成平台硬上限；这是本仓库现有表述，本次未重新核实平台发布规则。
- 原 README 默认复制全部八个 Skill，并用 `Copy-Item -Force` 覆盖；没有区分常用集合、视觉依赖或已安装副本的更新。
- 视觉指令允许 `local-tests/` 调试产物，但根 `.gitignore` 只覆盖部分生成目录，不能依赖它自动排除全部图片 / PDF。

本次处理：按任务选最小集合，已有目录先停止以便备份；拉取仓库与更新本机副本分开说明；正式产物放在独立工作区。

后续：核实实际平台规则后再改 Skill 中的硬上限；设计备份与同步方式、完善生成目录忽略规则。不要未经确认删除现有本机 Skill。

## 4. 本次验证与未验证范围

| 检查 | 结果 | 能证明什么 |
|---|---|---|
| 8 个 Skill 的职责、输入输出与仓库文件 | 已人工核对 | 分组和缺口有仓库证据；不代表上游最新 |
| 示例 Q/A/W 计数 | Redis：28 Q、28 A、0 W；网络前后各 19 Q/A/W | 可以区分历史格式与当前格式；不验证答案真实性 |
| 研究校验器四种模式 `--self-test` | 全部通过 | 内置结构样例能通过脚本，不是所有示例或实际项目都通过 |
| `deslop_check.py` 对网络改稿执行 | 可运行，输出提示 | 当前本机能运行检测；提示需人工判定，不验证事实 |
| `check-skill-docs.mjs` | 23 项通过 | 视觉文档包含约定片段，不验证图片渲染 |
| Playwright 实际渲染 / 图片生成 / Live Photo | 未执行 | 不对生产链运行成功作承诺 |
| 上游项目更新、当前平台限制、Token / 登录 | 未检查 | 不以本次整理结论替代外部验证；本次未触碰凭据 |

本次只修改 README 导航、示例说明和本计划；未修复上述 Skill 协议或校验器实现。后续维护按 P1 交接 / 格式问题优先，再做 P2 的运行时适配与体裁细分。

## 5. 归档标准

只有以下信息明确后，才把某个 Skill 改为 `candidate-archive`：

1. 当前用途已有可靠替代，且已对同类任务验证；
2. 输入输出、模板和现有示例能迁移；
3. 依赖、上游与许可文件不会因迁移丢失；
4. 有最近一次可用状态、待解决问题和恢复方式；
5. 维护者确认不再默认使用。

`candidate-archive` 先只改状态，不自动搬目录。确认归档后再移动到 `archive/<skill-name>/`，并在 `archive/README.md` 记录替代入口、迁移说明与恢复路径。不能因为“很久没用”就删除，也不能只改 README 宣称已完成迁移。

## 6. 后续更新标准

每次维护至少补充一项：触发边界、明确的输入输出、公开示例、可执行检查，或已经验证的依赖 / 运行时变更。规范变化时同步说明示例是否仍然符合；不得用未经审核的历史产物假装最新参考答案。
