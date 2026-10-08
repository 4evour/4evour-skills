# Skill 生命周期与整理计划

> 初始整理日期：2026-10-08

仓库的目标是保存**可复用的 Skill 和最小示例**，不是保存所有历史产物。Skill 的生命周期分为 `active`、`optional`、`candidate-archive` 和 `archived`；淘汰时先移动到 `archive/` 并保留说明，不直接删除历史。

## 当前建议

| Skill | 状态 | 当前动作 | 理由 |
|---|---|---|---|
| `bagu-explainer` | active | 持续更新 | 八股线的主入口，已有 Redis、网络、分布式等实际产出 |
| `tech-writing-zh` | active | 纳入仓库并继续补齐示例 | 负责去 AI 腔和保留作者声口，是当前内容线的高频环节 |
| `adapt-social-content` | active | 保持 | 负责把审核后的母稿变成小红书、公众号、知乎和视频脚本 |
| `research-open-source-project` | active | 保持 | 负责证据、源码和研究包，不应与写作 Skill 混职责 |
| `write-professional-technical-article` | active | 保持 | 负责研究包到专业母稿的论证转换 |
| `write-concept-explainer` | active | 与 GitHub 版本同步 | 与八股线不同，专门讲稳定的底层概念和心智模型 |
| `guizang-social-card-skill` | optional | 仅在需要确定性排版时启用 | 依赖较重，且有 AGPL-3.0 与商业授权边界，不作为所有内容的默认步骤 |
| `baoyu-xhs-images` | optional | 保留观察，不作为默认路径 | 适合低文字量插画；源码、长中文和精确数字仍应走确定性排版 |

## 不建议现在直接删除

目前还没有根据使用频率做出足够证据，把某个 Skill 永久删除并不稳妥。下一步如果连续一段时间没有使用某个 Skill，可以：

1. 先在本文件把状态改为 `candidate-archive`；
2. 把目录移动到 `archive/<skill-name>/`；
3. 在 `archive/README.md` 记录最后适用场景、替代 Skill 和迁移方式；
4. 观察一轮内容生产后再决定是否从默认安装列表移除。

## 更新标准

每次更新 Skill 至少补充一项：

- 触发边界或不适用场景；
- 输入和输出模板；
- 一个真实但已确认可公开的 Markdown 示例；
- 一条可执行的质量检查；
- 对上游依赖、许可证或模型能力变化的说明。
