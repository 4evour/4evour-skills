# 4evour Skills

用于中文技术内容生产的个人 Skill 仓库：面试复习、原理讲解、开源项目研究，以及小红书等平台的文案和卡片。

**如果你只是想做一篇小红书八股文，先用 `bagu-explainer`；准备发布时再用 `adapt-social-content` 和 `tech-writing-zh`。需要图片才加视觉工具，不必把八个 Skill 全跑一遍。**

> 整理日期：2026-10-09。本次按仓库内的指令、脚本和示例核对职责与交接；不代表所有外部工具、上游版本或平台规则都已重新验证。逐项状态和待修问题见 [Skill 生命周期与整理计划](docs/skill-lifecycle.md)。

## 1. 从哪里开始

| 你现在要做什么 | 入口 | 不需要默认执行的步骤 |
|---|---|---|
| 写 Redis / MySQL / JVM / 网络 / 操作系统八股 | [`bagu-explainer`](bagu-explainer/SKILL.md) | 开源项目研究、专业长文写作 |
| 已有稿件，只想去 AI 腔、保留自己的表达 | [`tech-writing-zh`](tech-writing-zh/SKILL.md) | 重新研究、重新拆成卡片 |
| 把审核过的母稿改成小红书正文和页面脚本 | [`adapt-social-content`](adapt-social-content/SKILL.md) | 再发明一遍技术结论 |
| 讲懂线程、CPU、内存等底层概念 | [`write-concept-explainer`](write-concept-explainer/SKILL.md) | 强行套面试问答格式 |
| 研究一个开源项目，再写有证据的分析文章 | [`research-open-source-project`](research-open-source-project/SKILL.md) → [`write-professional-technical-article`](write-professional-technical-article/SKILL.md) | 先改 README、再凭印象补结论 |
| 制作带精确中文、代码、命令的卡片 | [`guizang-social-card-skill`](guizang-social-card-skill/SKILL.md) | 让图片模型重新拼写技术文字 |
| 制作少量文字的手绘概念图、关系图 | [`baoyu-xhs-images`](baoyu-xhs-images/SKILL.md) | 把它当密集文字排版器 |

### 小红书常用：三个内容 Skill

| Skill | 输入 | 主要输出 | 职责边界 |
|---|---|---|---|
| `bagu-explainer` | 主题、目标读者、范围、需要核实的技术版本 | 模块化 Markdown：知识点 + Q/A/W | 负责备面内容，不直接出图；题单是参考，不是完整答案库 |
| `adapt-social-content` | 已审核的 `article.md`、`claim-ledger.md`，以及需要的视觉说明 | `channel-strategy.md`、`card-script.md`、`social-copy.md`、`visual-brief.md` | 负责平台表达和分页计划，不补研究、不直接渲染 |
| `tech-writing-zh` | 原稿、事实边界、作者声音样本（有则提供） | 改稿、需作者确认项、文风检测结果 | 负责表达，不负责给旧事实升级版本；八股稿保留 Q/A/W，不强制改成短笔记 |

### 专题扩展：按选题启用

| Skill | 什么时候用 | 关键交接物 |
|---|---|---|
| `write-concept-explainer` | 读者需要从零建立心智模型，而不是背题 | `concept-map.md`、`analogy.md`、`outline.md`、`explainer.md`、`visual-brief.md`、`editorial-review.md` |
| `research-open-source-project` | 有源码、官方文档或论文，需要验证项目行为和工程判断 | `source-state.md`、`evidence-map.md`、`thesis.md`、`claim-ledger.md`、`research-manifest.yaml`、`open-questions.md` |
| `write-professional-technical-article` | 已有研究包，要把证据组织成有论点、有边界的母稿 | `article-purpose.md`、`argument-map.md`、`outline.md`、`article.md`、`visual-brief.md`、`editorial-review.md` |

### 可选视觉：按内容选一种，不默认叠加

| Skill | 合适的内容 | 启用前要确认 |
|---|---|---|
| `guizang-social-card-skill` | 精确中文、代码、命令、表格、截图；HTML/CSS 确定性排版 | Node.js、Playwright 依赖和 Chromium；Live Photo 另有依赖，部分 Swift 辅助脚本仅适用于 macOS |
| `baoyu-xhs-images` | 低文字量概念插画、关系图、手绘组图 | 当前运行时可用的图片生成能力、偏好配置和确认流程；仓库不附带完整图片生成后端 |

这里的“常用 / 扩展 / 可选”是针对当前技术内容生产目标的使用建议，不是使用频率统计，也不是宣布某个 Skill 失效。目前没有正式归档的 Skill。

## 2. 做一篇小红书八股文

推荐顺序：

```text
明确选题、读者和版本 → 列题与事实核实
        ↓
bagu-explainer：知识点 + Q/A/W 母稿
        ↓
技术审核 + 事实台账 + 审核状态（当前需要显式补齐的交接步骤）
        ↓
adapt-social-content：发布文案 + 卡片脚本
        ↓
tech-writing-zh：最终表达检查，不改事实与答题结构
        ↓
需要出图时 → guizang-social-card-skill → 逐页验收
```

- **Q**：面试问题；**A**：可直接表达的答案；**W**：通过场景和因果讲清楚为什么。
- 八股格式以 [当前输出规范](bagu-explainer/references/output-format.md) 为准，不以历史示例为准。
- [题单参考](bagu-explainer/references/topic-checklists.md) 详细覆盖 Redis、MySQL、JVM、计算机网络和操作系统；Spring、消息队列、并发等主题仍需另建同粒度题单。
- 版本、默认参数、数字、命令和行为边界需要针对本次选题核实；示例不等于最新技术结论。
- 当前八股规范写有“18 页”预算及平台上限表述，本次没有重新核实平台限制。生产时先确定预算，发布前以实际发布入口为准；不要为了凑页数注水。
- 密集技术文字优先确定性排版。插画只是解释工具，不能替代事实审核。

### 母稿到社交适配：目前不是自动衔接

`adapt-social-content` 当前要求 `article.md` 和 `claim-ledger.md`，还会检查审核状态与研究来源。但 `bagu-explainer` 默认只交付八股 Markdown，`write-concept-explainer` 默认交付 `explainer.md`；两者都没有完整输出这套社交输入协议。

进入社交阶段前，应在自己的选题工作区显式完成：

1. 保留原母稿，将审核后的内容另存为 `article.md`，或明确约定输入映射；不要静默覆盖原稿。
2. 建立 `claim-ledger.md`：关键事实绑定来源，数字、版本、命令和限定条件可回查。
3. 记录实际审核结果和状态；未通过审核时，不标为 `approved`。
4. 准备 `visual-brief.md`，说明哪些文字必须逐字准确、哪些结论不能新增。

这是需要执行的交接步骤，不是仓库现有的一键转换器。也不必为了凑这些文件，强行对八股主题运行完整的开源研究流程。

### 可直接使用的起步请求

```text
使用 $bagu-explainer 生成 MySQL 事务篇，面向有基础的后端求职者。
先列题单和范围，核实本次选定版本的关键事实，再按知识点 + Q/A/W 写母稿。
输出到独立选题目录；先不生成图片，不编造高频率、真题来源或个人经历。
```

```text
使用 $adapt-social-content，读取已审核的 article.md 和 claim-ledger.md，
生成小红书正文、卡片脚本和 visual-brief.md。图片讲机制，正文补来源与边界。
再用 $tech-writing-zh 检查表达，不改变技术结论、数字和限定词。
```

## 3. 另外两条内容线路

**原理讲解**：`write-concept-explainer` → 事实审核与社交输入补齐 → `adapt-social-content` → `tech-writing-zh` → 按需出图。用“朴素模型 → 解释不了的现象 → 模型升级”讲懂机制，不要另跑八股生成重复内容。

**开源研究长文**：`research-open-source-project` → `write-professional-technical-article` → 审核 → `adapt-social-content` → `tech-writing-zh` → 按需出图。研究包提供事实边界，长文建立论证，社交阶段改变阅读形式但不新增结论。

**只润色已有稿**：直接用 `tech-writing-zh`。它和 `adapt-social-content` 都能涉及平台文案，但前者侧重改稿与作者声音，后者侧重平台策略、卡片脚本和视觉交接。不要让两个 Skill 各自把同一稿从头重写一遍。

## 4. 示例怎么读

| 示例 | 用途 | 注意事项 |
|---|---|---|
| [计算机网络改稿前后](examples/tech-writing-zh/computer-network/README.md) | 优先参考当前模块式知识点 + Q/A/W，以及文风修改 | 两份稿各含 11 个模块、19 组 Q/A/W；这是结构示例，不是本次重新审核的答案库 |
| [Redis 八股到社交草稿](examples/bagu-explainer/redis/README.md) | 看历史题目组织与发布思路 | `output-qna.md` 是旧 Q/A 稿，28 题、没有 W 层；不符合当前完整输出规范，不能直接当模板 |
| [分布式系统内容交接](examples/content-pipeline/distributed-systems/README.md) | 看事实账本 → 母稿 → claim ledger → 卡片脚本 → 文案 | 是精选交接快照，不包含完整审核、渲染与发布产物 |
| [TencentDB Agent Memory 研究到社交](examples/research-to-social/tencentdb-agent-memory/README.md) | 看源码研究、证据分类和文章论证 | 只收录部分研究文件；文章引用的图片未随仓库提交，不是开箱即可校验或渲染的完整包 |

筛选原则见 [examples/README.md](examples/README.md)。示例用来理解流程，不作为平台规则、性能数据或项目当前能力的权威来源。

## 5. 安装与依赖

### 内容 Skill：先安装需要的最小集合

以下 PowerShell 代码从**仓库根目录**复制三个小红书常用内容 Skill；没有现成生成任务，也不会安装视觉依赖。已有同名目录时先停止，避免覆盖个人修改。

```powershell
$repoRoot = (Get-Location).Path
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else {
  Join-Path $env:USERPROFILE '.codex'
}
$skillRoot = Join-Path $codexHome 'skills'
$skills = @('bagu-explainer', 'adapt-social-content', 'tech-writing-zh')

# 先检查全部源目录和目标目录，再复制。
foreach ($skill in $skills) {
  $source = Join-Path $repoRoot $skill
  $target = Join-Path $skillRoot $skill
  if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) {
    throw "找不到 $skill/SKILL.md，请从仓库根目录运行。"
  }
  if (Test-Path -LiteralPath $target) {
    throw "已存在 $target；请先备份并确认更新范围，不自动覆盖。"
  }
}

New-Item -ItemType Directory -Path $skillRoot -Force | Out-Null
foreach ($skill in $skills) {
  Copy-Item -LiteralPath (Join-Path $repoRoot $skill) -Destination $skillRoot -Recurse
}
```

需要概念讲解、研究长文或出图时，再把对应目录加入 `$skills`。**拉取仓库不会自动更新已经复制到本机 Skill 目录的版本**；更新前备份旧目录，并处理可能残留的旧文件。运行时是否加载成功，以实际 Skill 列表为准。

### 视觉依赖：仅在出图时准备

`guizang-social-card-skill` 有独立的 `package.json` 和锁文件。需要本地静态卡片渲染时，在该目录准备依赖：

```powershell
Push-Location .\guizang-social-card-skill
try {
  npm ci
  if ($LASTEXITCODE -ne 0) { throw '安装 Playwright 依赖失败。' }
  npx playwright install chromium
  if ($LASTEXITCODE -ne 0) { throw '安装 Chromium 失败。' }
} finally {
  Pop-Location
}
```

这只准备渲染环境，不是生成图片或验证成品的命令。Live Photo 的 FFmpeg、打包工具和 macOS 辅助脚本不属于静态八股卡片的必要步骤。

`baoyu-xhs-images` 使用当前运行时的图片生成工具，或额外安装的后端；复制这个目录不等于已经具备出图能力。文档中的工具名、wrapper、参数与确认方式，使用前要按当前运行时核对。

## 6. 质量检查：脚本能做什么

从仓库根目录执行文风检测。下面先检查仓库内的网络示例；生产时把最后一个参数替换为自己的稿件路径：

```powershell
python -X utf8 .\tech-writing-zh\scripts\deslop_check.py .\examples\tech-writing-zh\computer-network\after-tech-writing.md
```

这是启发式提示，不是 AI 写作鉴定，也不验证技术事实。自然语境下的命中需要人工判断；脚本成功退出不等于稿件合格。

研究包结构校验的自测：

```powershell
foreach ($mode in @('research', 'article', 'social-plan', 'social-final')) {
  python -X utf8 .\research-open-source-project\scripts\validate_research_artifacts.py --self-test --mode $mode
  if ($LASTEXITCODE -ne 0) { throw "结构校验自测失败：$mode" }
}
```

对实际产物使用 `validate_research_artifacts.py <产物目录> --mode <模式>`。注意：

- 所有模式都要求基础研究文件；`article` 模式增加文章文件，`social-plan` / `social-final` 模式增加社交文件，但不是全部阶段文件的逐级累加。
- 脚本按**同一个目录**查找文件，不会自动跨 `01-source/`、`02-article/`、`03-social/` 或 `research/`、`article/`、`social/` 聚合输入。
- 它不能直接充当轻量八股线的通用验收器；精选示例缺文件时，不能把校验失败简单当作文章错误。
- 仓库目前没有专门的 Q/A/W 字数、题量、知识点互引或导出页数校验器，也没有统一的多阶段编排脚本。

视觉文档可以单独检查：

```powershell
Push-Location .\guizang-social-card-skill
try { node .\scripts\check-skill-docs.mjs } finally { Pop-Location }
```

这不验证真实图片。出图后还需检查实际尺寸、换行、裁切、代码文字、手机阅读效果，并记录 `image-review.md`。

## 7. 仓库边界与维护

```text
4evour-skills/
├── bagu-explainer/                      # 八股母稿
├── adapt-social-content/               # 平台与卡片脚本
├── tech-writing-zh/                    # 中文表达终检
├── write-concept-explainer/            # 原理讲解扩展
├── research-open-source-project/       # 研究扩展
├── write-professional-technical-article/ # 长文扩展
├── guizang-social-card-skill/           # 可选确定性排版
├── baoyu-xhs-images/                   # 可选生成式插画
├── examples/                           # 精选 Markdown 示例
└── docs/skill-lifecycle.md             # 状态、待修问题与归档标准
```

- 仓库保存可复用指令、参考、脚本、模板和最小示例，不保存所有历史工作稿。
- 正式选题的稿件、图片、PDF 和发布文件放在独立工作区。视觉 Skill 内的 `local-tests/` 是调试约定，不是默认提交位置；本仓库的忽略规则并未兜住所有这类产物。
- 不提交 Token、个人资料、上游 `.git`、`node_modules`、渲染缓存或未经确认可公开的素材。
- 很久没用不等于应删除。先核对替代能力、输入输出和依赖，再标记待归档；归档需保留迁移说明。本次没有移动或删除 Skill。

## 上游与许可证

- `baoyu-xhs-images` 基于 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) 的同名 Skill，保留 [MIT License](baoyu-xhs-images/LICENSE)。
- `guizang-social-card-skill` 基于 [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)，保留 [AGPL-3.0 License](guizang-social-card-skill/LICENSE) 和 [商业授权说明](guizang-social-card-skill/COMMERCIAL_LICENSING.md)。
- 其余六个内容 Skill 为本仓库维护的中文工作流；具体文件按各自已有声明处理，不把不同来源视为一套统一许可证。
