# 4evour Skills

这是我在 AI Coding、开源项目研究和技术内容生产过程中持续维护的 Codex Skills 仓库。

仓库把完整工作流拆成独立阶段：技术研究只负责证据，专业写作只负责论证，社交适配只负责平台表达，视觉制作再根据内容类型选择确定性排版或生成式插画。阶段之间通过 Markdown 研究包和 claim ledger 交接，不依赖一段越来越长的对话上下文。

## 内容生产链

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

## 当前包含

| Skill | 职责 | 推荐使用场景 |
|---|---|---|
| `research-open-source-project` | 从源码、测试和官方资料产出可复核研究包 | 开源项目、Agent 系统、架构和竞品调研 |
| `write-professional-technical-article` | 把研究包写成有论点、有证据、有边界的中文技术长文 | 系统设计、工程实践、论文和技术路线文章 |
| `adapt-social-content` | 把审核后的文章改写成平台内容和卡片脚本 | 微信公众号、小红书、X、知乎和视频脚本 |
| `guizang-social-card-skill` | 使用 HTML/CSS 和真实素材确定性渲染 | 源码、命令、截图、微信封面、Live Photo、Swiss/杂志风卡片 |
| `baoyu-xhs-images` | 使用 ImageGen 生成风格统一的插画卡片 | 手绘概念图、关系图、流程图和低文字量知识卡 |

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
  'adapt-social-content',
  'guizang-social-card-skill',
  'baoyu-xhs-images'
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
├── adapt-social-content/
├── guizang-social-card-skill/
└── baoyu-xhs-images/
```

每个 Skill 使用 `SKILL.md` 描述触发条件和核心流程；详细方法放入 `references/`，确定性工具放入 `scripts/`，输出模板和视觉资产放入 `assets/`。

## 上游与许可证

- `baoyu-xhs-images` 基于 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) 的同名 Skill，按 MIT License 使用和修改；仓库内保留许可证。
- `guizang-social-card-skill` 基于 [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)，按 AGPL-3.0 使用和修改；仓库内保留许可证与商业授权说明。
- 其余三个内容工作流为本仓库维护的中文 Skills。

本仓库只收录运行所需的 Skill 文件，不包含上游仓库的 `.git`、`node_modules`、本地测试产物和生成内容。
