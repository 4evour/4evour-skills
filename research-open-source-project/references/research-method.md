# 仓库与技术系统研究方法

## 内容

1. 来源层级
2. 仓库扫描顺序
3. 证据图结构
4. 独立洞察检查
5. 竞品比较方法
6. 工程风险问题

## 1. 来源层级

对每个结论按以下优先级取证：

1. 已执行的行为、测试和测量结果；
2. 研究 commit 上的源码；
3. 官方技术文档、changelog 和 README；
4. 官方架构图和截图；
5. 维护者 issue、PR 和讨论；
6. 独立研究或评估；
7. 社区评论，仅作为背景。

README 是一手材料，可以证明项目的意图、术语、公开接口、文档化流程和项目自己报告的结果，但不能单独证明运行正确性、性能优势、生产成熟度或 benchmark 可复现。

维护 README reuse map：

- `reuse`：定义、表格、图或简短解释准确且适合保留；
- `adapt`：事实准确，但要围绕研究问题重组；
- `verify`：行为、性能、成熟度和比较结论需要源码或其他来源核实；
- `exclude`：宣传性、过时、重复或与研究问题无关。

## 2. 仓库扫描顺序

### A：先画系统地图

记录语言、包、服务、入口、存储、外部依赖、协议、构建工具和部署单元。

### B：追踪产生价值的路径

至少跟踪一条：

```text
输入 → 校验 → 转换 → 持久化 → 检索 → 交付 → 反馈
```

记录具体文件和函数，注意异步边界、队列、缓存、重试、超时、锁和失败行为。

### C：检查工程证据

查看测试、CI、lint、migration、可观测性、错误处理、benchmark、部署文档和已知限制。架构强但验证弱时，要如实描述为“设计存在，证据不足”。

### D：主动寻找反证

搜索 `TODO`、`FIXME`、`unsupported`、`limitation`、`roadmap`、`fallback`、`retry`、`timeout`、`mutex`、`queue`、`experimental`、`beta` 和 benchmark caveat，找出会推翻产品叙事的代码。

## 3. 证据图结构

`evidence-map.md` 使用以下稳定标题，便于脚本检查：

```markdown
# Evidence Map

## Source State
## README Reuse Map
## Official Claims
## Architecture
## Code Evidence
## Engineering Evidence
## Limitations
## Contradictions
## Open Questions
```

代码证据使用：

```markdown
### EV-001 — Short finding
- Path: `path/to/file.ts`
- Symbol: `functionOrClass`
- Observation: 代码做了什么。
- Meaning: 为什么重要。
- Alternative explanation: 还有什么解释可能成立。
- Confidence: high | medium | low
```

## 4. 独立洞察检查

候选论点必须通过：

- **增量价值**：读者已读 README 后，是否获得因果解释、工程后果、边界、比较或决策？
- **所以呢**：是否会改变一个工程选择或心智模型？
- **反论点**：能否公平地说出一个强替代解释？
- **边界**：论点在哪些条件下失效？
- **新意定位**：新意位于算法、数据模型、系统边界、工作流、治理还是产品包装？
- **证据多样性**：是否不只依赖一种来源？

不通过时继续研究，不要用标题和卡片装饰摘要。

## 5. 竞品比较方法

按系统层比较：

| 维度 | 问题 |
|---|---|
| 主抽象 | 产品把什么对象当作核心？ |
| 数据模型 | 记录、向量、图、文件、block 还是多种资产？ |
| 更新模型 | 同步、后台、增量、版本化还是时间有效？ |
| 检索与交付 | 搜索、注入、常驻状态还是工具调用？ |
| 治理 | 所有权、ACL、版本、租户和 loadout 如何处理？ |
| 耦合 | SDK、服务、Agent Runtime、框架插件还是代理层？ |
| 验证 | 测试、benchmark、provenance 和公开评估是什么？ |
| 运营成本 | 服务、数据库、队列、模型调用和故障面是什么？ |

记录访问日期和来源 URL。不要用 stars 或功能 checkbox 代替系统分析。

## 6. 工程风险问题

- 抽取或索引中途失败会发生什么？
- 大任务会不会阻塞小任务？
- 派生数据能否由原始证据重建？
- 冲突、失效和时间如何处理？
- 哪个组件会成为扩展性或可用性瓶颈？
- 增强层失败时，主链路能否 fail open？
- 查询时和检索后是否都执行权限检查？
- 成本能否按用户、租户、资产和请求归因？
- benchmark 是否测量了宣称的价值，能否复现？
