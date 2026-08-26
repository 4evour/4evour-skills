# 4evour Skills

这是我在 AI Coding、开源项目研究和技术内容生产过程中持续维护的 Codex Skills 仓库。

仓库把完整工作流拆成独立阶段：技术研究只负责证据，专业写作只负责论证，社交适配只负责平台表达，视觉制作再根据内容类型选择确定性排版或生成式插画。阶段之间通过 Markdown 研究包和 claim ledger 交接，不依赖一段越来越长的对话上下文。

## 内容生产链：三条线路

按"读者拿这篇内容干什么"选线，不是按主题新旧：

| 线路 | 主题形态 | 读者任务 | 主 skill |
|---|---|---|---|
| **八股线** | 考点可拆成离散题目、答案有共识（MySQL、Redis、JVM、网络协议） | 备面复习、查漏 | `bagu-explainer` |
| **概念讲解线** | 稳定的底层原理，需要建心智模型（线程、CPU、内存、OS） | 从零学懂 | `write-concept-explainer` |
| **研究长文线** | 有争议或在演化，需要证据和判断（RAG、新框架、开源项目） | 理解与选型 | `research-open-source-project` → `write-professional-technical-article` |

同一个主题可以换线：线程调度讲给备面的人是八股线，讲给想学懂的人是概念讲解线。
RAG 这类新东西等概念核心收敛后会自然滑进八股线。

三条线共用同一道文风终检：交付前跑 `tech-writing-zh` 的
`deslop_check.py`（装在 `~/.zcode/skills`），结构级病灶规则已写进各线的
references（对仗限量、段末升华、假揭示、过渡句、均匀深度、句长方差）。
"AI 味重"主要指结构指纹，不是用词。

### 研究长文线全链

```text
research-open-source-project
        ↓
write-professional-technical-article
        ↓
adapt-social-content
        ↓
├── guizang-social-card-skill  精确文字、源码、截图、封面和成套卡片
└── baoyu-xhs-images           低文字量概念图、关系图和手绘插画
```

`bagu-explainer` 走题库路线，不在研究链上。八股线和概念讲解线的产出
（`.md` 定稿）同样可以从 `adapt-social-content` 进入分发；
概念讲解线的 `visual-brief.md` 默认交 `guizang-social-card-skill`。

## 当前包含

| Skill | 职责 | 推荐使用场景 |
|---|---|---|
| `research-open-source-project` | 从源码、测试和官方资料产出可复核研究包 | 开源项目、Agent 系统、架构和竞品调研 |
| `write-professional-technical-article` | 把研究包写成有论点、有证据、有边界的中文技术长文 | 系统设计、工程实践、论文和技术路线文章 |
| `write-concept-explainer` | 把稳定的底层概念写成升级式图解讲解 | 线程、CPU、内存、OS 原理等"讲懂"型内容 |
| `adapt-social-content` | 把审核后的文章改写成平台内容和卡片脚本 | 微信公众号、小红书、X、知乎和视频脚本 |
| `guizang-social-card-skill` | 使用 HTML/CSS 和真实素材确定性渲染 | 源码、命令、截图、微信封面、Live Photo、Swiss/杂志风卡片 |
| `baoyu-xhs-images` | 使用 ImageGen 生成风格统一的插画卡片 | 手绘概念图、关系图、流程图和低文字量知识卡 |
| `bagu-explainer` | 把技术面试主题写成"模块两层"复习文档（知识点条目 + Q/A/W 问答） | Redis/MySQL/JVM/网络/操作系统八股总结、面试复习笔记 |

## 图片路由

`adapt-social-content` 为每一页分配一种渲染模式：

```text
reuse-evidence          → guizang-social-card-skill
deterministic-evidence  → guizang-social-card-skill
generated-relationship  → baoyu-xhs-images
```

如果关系页仍然包含较多必须逐字准确的中文、代码或数字，也交给 `guizang-social-card-skill`，不要交给图片模型排字。

## 安装到 Codex

克隆仓库后，在 PowerShell 中运行：

```powershell
$skillRoot = Join-Path $env:USERPROFILE '.codex\skills'
$skills = @(
  'research-open-source-project',
  'write-professional-technical-article',
  'write-concept-explainer',
  'adapt-social-content',
  'guizang-social-card-skill',
  'baoyu-xhs-images',
  'bagu-explainer'
)

foreach ($skill in $skills) {
  Copy-Item -Recurse -Force ".\$skill" $skillRoot
}
```

安装或更新后，在下一轮 Codex 对话中即可通过名称调用。例如：

```text
使用 $research-open-source-project 研究这个 Agent Memory 项目并产出研究包。
使用 $write-professional-technical-article 基于研究包写一篇专业中文技术文章。
使用 $adapt-social-content 将已审核文章改写成小红书内容和卡片脚本。
```

`guizang-social-card-skill` 首次在独立环境运行时，需要在其目录执行 `npm install` 安装 Playwright 依赖。不要提交 `node_modules`、生成图片或本地测试目录。

## 目录结构

```text
4evour-skills/
├── research-open-source-project/
├── write-professional-technical-article/
├── write-concept-explainer/
├── adapt-social-content/
├── guizang-social-card-skill/
├── baoyu-xhs-images/
└── bagu-explainer/
```

每个 Skill 使用 `SKILL.md` 描述触发条件和核心流程；详细方法放入 `references/`，确定性工具放入 `scripts/`，输出模板和视觉资产放入 `assets/`。

## 上游与许可证

- `baoyu-xhs-images` 基于 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) 的同名 Skill，按 MIT License 使用和修改；仓库内保留许可证。
- `guizang-social-card-skill` 基于 [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)，按 AGPL-3.0 使用和修改；仓库内保留许可证与商业授权说明。
- 其余五个内容工作流（研究、专业写作、概念讲解、社交适配、八股生成）为本仓库维护的中文 Skills。

本仓库只收录运行所需的 Skill 文件，不包含上游仓库的 `.git`、`node_modules`、本地测试产物和生成内容。
