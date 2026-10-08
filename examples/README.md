# 示例：从 Skill 到可发布内容

这里放的是从本地工作区筛选出来的 **Markdown 示例**，用于在另一台电脑上理解和复用仓库里的 Skill。

## 示例目录

| 示例 | 展示内容 | 对应 Skill |
|---|---|---|
| `bagu-explainer/redis/` | Redis 题单产出的知识点、Q/A/W 文稿，以及进一步改成的小红书文字稿 | `bagu-explainer`、`adapt-social-content` |
| `tech-writing-zh/computer-network/` | 同一篇计算机网络稿的八股初稿与去 AI 腔后的版本 | `tech-writing-zh` |
| `content-pipeline/distributed-systems/` | 事实账本 → 技术讲解 → claim ledger → 卡片脚本 → 发布文案 | `write-concept-explainer`、`adapt-social-content` |
| `research-to-social/tencentdb-agent-memory/` | 开源项目研究包 → 专业文章 → 社交文案的关键 Markdown 交接文件 | `research-open-source-project`、`write-professional-technical-article`、`adapt-social-content` |

## 选取原则

- 只收录 Markdown 和少量必要的文本材料，不把整个内容工作区搬进来。
- 不收录 PDF、图片、压缩包、渲染缓存、Notion 导出目录和本地测试产物。
- 不收录个人成长记录、求职面经、联系方式或其他不适合公开的材料。
- 示例文件是从原工作稿复制出来的，原工作区仍然保留；修改示例不会反向修改原稿。
- `tencentdb-agent-memory/article/article.md` 保留了原稿中的图片引用，但示例仓库没有同步那些图片资源；阅读文字链路即可。

## 怎么使用

1. 先阅读对应 Skill 的 `SKILL.md`。
2. 再看示例目录中的 `README.md` 和 Markdown 文件，理解输入、交接和输出。
3. 在自己的选题目录中复制同样的阶段结构，再替换成自己的资料和原稿。
4. 生成图片、PDF 和最终发布文件放在项目自己的工作区，不要回填到 Skill 仓库。
