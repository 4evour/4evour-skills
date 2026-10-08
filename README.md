# 4evour Skills

这是我在 AI Coding、开源项目研究和技术内容生产过程中持续维护的 Codex Skills 仓库。

仓库把内容生产拆成可以复用的阶段：研究只负责证据，专业写作只负责论证，概念讲解负责搭建心智模型，八股 Skill 负责面试复习，社交适配负责平台表达，视觉 Skill 再根据素材类型选择确定性排版或生成式插画。阶段之间通过 Markdown 研究包、claim ledger 和卡片脚本交接。

## 三条内容线路

| 线路 | 适合主题 | 主 Skill |
|---|---|---|
| **八股线** | Redis、MySQL、JVM、网络协议等可拆成题目的面试内容 | `bagu-explainer` |
| **概念讲解线** | 线程、CPU、内存、操作系统、网络等需要建立直觉的稳定原理 | `write-concept-explainer` |
| **研究长文线** | Agent、RAG、开源项目和有争议或快速演化的技术主题 | `research-open-source-project` → `write-professional-technical-article` |

三条线路可以在审核后进入 `adapt-social-content`，再按素材类型选择视觉 Skill。`tech-writing-zh` 负责在事实和作者判断确认后做中文表达终检，不负责凭空补事实。

## 当前包含

| Skill | 职责 |
|---|---|
| `research-open-source-project` | 从源码、测试和官方资料产出可复核研究包 |
| `write-professional-technical-article` | 把研究包写成有论点、有证据、有边界的中文技术长文 |
| `write-concept-explainer` | 把稳定的底层概念写成升级式图解讲解 |
| `bagu-explainer` | 输出“知识点 + Q/A/W 面试问答”的模块化复习文档 |
| `tech-writing-zh` | 写作、改稿和去 AI 腔，保留事实边界与作者声口 |
| `adapt-social-content` | 把审核后的文章改成小红书、公众号、知乎和视频脚本 |
| `guizang-social-card-skill` | 用 HTML/CSS 和真实素材做确定性排版 |
| `baoyu-xhs-images` | 为低文字量内容生成风格统一的概念插画卡片 |

## 示例

`examples/` 只收录从真实工作稿筛选出来的 Markdown 示例：

- `bagu-explainer/redis/`：八股文稿到小红书文字稿；
- `tech-writing-zh/computer-network/`：去 AI 腔前后对照；
- `content-pipeline/distributed-systems/`：事实账本到发布文案的完整交接；
- `research-to-social/tencentdb-agent-memory/`：研究包到专业文章和社交文案。

示例筛选原则和来源说明见 [`examples/README.md`](examples/README.md)。个人成长记录、求职面经、PDF、图片、压缩包和本地测试产物不放入这个公开仓库。

## 安装到 Codex

克隆仓库后，在 PowerShell 中运行：

```powershell
$skillRoot = Join-Path $env:USERPROFILE '.codex\skills'
$skills = @(
  'research-open-source-project',
  'write-professional-technical-article',
  'write-concept-explainer',
  'bagu-explainer',
  'tech-writing-zh',
  'adapt-social-content',
  'guizang-social-card-skill',
  'baoyu-xhs-images'
)

foreach ($skill in $skills) {
  Copy-Item -Recurse -Force ".\$skill" $skillRoot
}
```

安装或更新后，在下一轮 Codex 对话中即可通过名称调用。需要确定性图片排版时使用 `guizang-social-card-skill`；只需要低文字量概念插画时再使用 `baoyu-xhs-images`。

## 仓库结构

```text
4evour-skills/
├── research-open-source-project/
├── write-professional-technical-article/
├── write-concept-explainer/
├── bagu-explainer/
├── tech-writing-zh/
├── adapt-social-content/
├── guizang-social-card-skill/
├── baoyu-xhs-images/
├── examples/
└── docs/
```

每个 Skill 使用 `SKILL.md` 描述触发条件和核心流程；详细方法放入 `references/`，确定性工具放入 `scripts/`，输出模板和视觉资产放入 `assets/`。生命周期和淘汰规则见 [`docs/skill-lifecycle.md`](docs/skill-lifecycle.md)。

## 上游与许可证

- `baoyu-xhs-images` 基于 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) 的同名 Skill，按 MIT License 使用和修改；仓库内保留许可证。
- `guizang-social-card-skill` 基于 [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)，按 AGPL-3.0 使用和修改；仓库内保留许可证与商业授权说明。
- 其余六个内容 Skill 为本仓库维护的中文 Skills。

本仓库不包含上游仓库的 `.git`、`node_modules`、本地测试产物、生成图片和个人资料。示例只保留有助于理解工作流的 Markdown 文件。
