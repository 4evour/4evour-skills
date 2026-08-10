# 4evour Skills

这是我在 ai coding 的过程中，逐步沉淀下来的个人 Skills 仓库。

这里收录的不是临时提示词，而是经过实际任务验证、反馈迭代和质量门约束的可复用工作流。
每个 Skill 都尽量把个人判断习惯、研究方法和交付标准固化下来，让相似任务可以稳定复现，而不是每次从头摸索。

## 当前包含

### research-open-source-project

面向开源项目的深度研究与内容生产工作流。它不会停留在 README 摘要，而会进一步检查源码、测试、架构和竞品资料，形成独立技术判断，并按需产出：

- 有源码证据的技术文章母稿
- 项目创新点、设计思路与工程权衡分析
- 公平的竞品定位和适用边界
- 微信公众号或博客长文
- 小红书专业技术图文与发布文案
- 插图报告或 PDF 母稿
- 生图前脚本、事实约束和成品质量检查

支持 `reviewed` 审核模式和 `one-pass` 一键模式。

## 使用方式

将需要的 Skill 文件夹复制到 Codex 个人 Skill 目录：

```powershell
Copy-Item -Recurse .\research-open-source-project "$env:USERPROFILE\.codex\skills\"
```

然后在 Codex 中直接调用：

```text
使用 $research-open-source-project 的 one-pass 模式，研究这个开源项目，并产出技术文章、平台文案和经过质量检查的图解方案。
```

## 设计原则

- README 是重要的一手资料，但不是研究终点。
- 事实、推断、观点和待验证问题必须分开。
- 先形成文章母稿，再适配不同发布渠道。
- 社交卡片要解释关系和机制，不能只堆关键词。
- 生成式图片中的数字、版本和标签必须可追溯。
- 一键执行可以减少偏好确认，但不能跳过证据和质量检查。

## 目录结构

```text
4evour-skills/
└── research-open-source-project/
    ├── SKILL.md
    ├── agents/
    ├── references/
    └── scripts/
```

后续会继续沉淀在实际任务中反复使用并验证过的个人工作流。
