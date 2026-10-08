# Evidence Map

## Source State

- 分支：`feat/server_team`
- 提交：`fe3230f176f1bf5832fee79d12494bbc2d19a8aa`
- 研究日期：2026-08-09
- 主要证据：本地源码、官方 README/图片、公开 CI、竞品官方仓库
- 未执行：完整部署、单元测试、Benchmark 复现、性能与安全压测

## README Reuse Map

| ID | README 内容 | 处理 | 使用方式 |
|---|---|---|---|
| OR-01 | “凡是能让下一个 Agent 少走弯路的信息，都应该被保存、组织并复用” | reuse | 作为官方问题定义直接引用并标注来源 |
| OR-02 | Chat Memory、Skill、Wiki、CodeGraph 四类资产 | reuse + verify | 保留官方名称，用 `metadata/types.ts` 核对统一资产模型 |
| OR-03 | L0 Conversation → L1 Atom → L2 Scenario → L3 Persona | reuse + verify | 复用官方表格，用 Pipeline 与 Recall 代码解释为什么分层 |
| OR-04 | Fixed Binding + ACL 决定 Agent 可用资产 | adapt + verify | 由 `permission-checker.ts`、元数据类型与 SDK 接口支撑 |
| OR-05 | Wiki/CodeGraph 通过 `/v3/tools/list` 和 `/v3/tools/call` 按需读取 | reuse + verify | 用 `routes/tools.ts` 的白名单实现补足机制 |
| OR-06 | PersonaMem 48%→76% | verify | 只写作“项目报告结果”，不写成独立复现实验结论 |
| OR-07 | Team Memory Beta 正在快速迭代 | reuse | 用来界定成熟度，不将 Beta 等同于不可用 |
| OR-08 | “全面跨框架迁移”与自动记忆路由 | adapt | 明确 README 自己也把更广泛适配和全自动路由列入迭代项 |

## Official Claims

- README 对“减少 Agent 重复学习成本”的问题定义准确，文章直接复用并注明为官方表达。
- 四类资产、L0-L3、Fixed Binding + ACL、Knowledge 工具调用都有代码支撑，可以作为项目公开能力描述。
- Benchmark、跨框架覆盖、自动路由与成熟度属于需要限定范围的官方报告或发展目标。

## Architecture

| 模块 | 主要责任 | 关键证据 |
|---|---|---|
| MemoryCore | L0-L3、Skill、Metadata、Gateway、检索与异步 Pipeline | `MemoryCore/src/core/`、`src/metadata/`、`src/gateway/`、`src/utils/pipeline-manager.ts` |
| MemoryKnowledge | Wiki、CodeGraph、构建队列、查询工具与 MCP | `MemoryKnowledge/src/routes/tools.ts`、`src/store/build-queue.ts` |
| MemoryPanel | Team、Agent、资产、权限与知识管理 UI | `MemoryPanel/src/`、`MemoryPanel/web/src/` |
| MemoryProxy | OpenAI/Anthropic 兼容代理、会话身份、资产注入、写回与观测 | `MemoryProxy/src/handler.ts`、`src/injection/`、`src/tdai/` |
| SDK | TypeScript/Python 的 Memory、Skill、Metadata 客户端 | `sdk/memory-core/` |

端到端价值路径：

`Agent 请求 → Proxy 解析身份与注入上下文 → 上游模型 → 对话回写 L0 / Skill Conversation Add → Core 异步提炼 → 资产登记与治理 → 下轮通过固定装配、自动召回或工具调用交付`

## Code Evidence

### EV-001 — 四类经验统一登记，但不统一底层模型
- Path: `MemoryCore/src/metadata/types.ts`
- Symbol: `AssetType`, `AssetEntity`, `FixedAssetBindingEntity`
- Observation: 代码定义四类资产、版本、可见性、状态、Owner、注入模式、优先级与 Agent Binding。
- Meaning: 统一的是治理元数据和装配关系，而不是把所有经验压成一种向量记录。
- Alternative explanation: 这也可能只是 UI 元数据层；需要结合各资产独立服务与读取协议确认。
- Confidence: high

### EV-002 — Chat Memory 是异步数据加工链，不是同步摘要函数
- Path: `MemoryCore/src/utils/pipeline-manager.ts`
- Symbol: `MemoryPipelineManager`
- Observation: L1 由阈值、空闲或 shutdown 触发；Warm-up 阈值逐次翻倍；L2 使用最短/最长间隔；L3 采用全局互斥和 pending 去重。
- Meaning: 系统用最终一致性换取前台延迟、LLM 成本和后台调度的可控性。
- Alternative explanation: 注释描述需要运行测试验证；当前仓库没有提交相应测试源码。
- Confidence: high

### EV-003 — 稳定概览与动态细节被放进不同上下文区域
- Path: `MemoryCore/src/core/hooks/auto-recall.ts`
- Symbol: `performAutoRecallCore`, `searchMemories`, `applyRecallBudget`
- Observation: L3 Persona 与 L2 Scene Navigation 进入稳定、可缓存的 system context；每轮 L1 召回进入动态 user prefix；Keyword/Embedding Hybrid 通过 RRF 合并并受超时、条数和字符预算约束。
- Meaning: 项目关注的不是“尽量多召回”，而是单位上下文预算中的信息价值和 KV Cache 稳定性。
- Alternative explanation: 具体收益仍取决于模型提供商缓存行为与真实数据分布。
- Confidence: high

### EV-004 — Skill 被实现为版本化资源包
- Path: `MemoryCore/src/core/skill/skill-versioning.ts`
- Symbol: `SkillVersioning.appendNextVersion`
- Observation: 新版本复制旧资源目录、应用资源增删、写入新版本；失败时清理新目录；内容和资源均未变化时幂等返回。
- Meaning: Skill 的系统语义更接近可治理的程序性知识，而不是 Prompt 文本。
- Alternative explanation: 版本存在不代表内容经过自动质量验证。
- Confidence: high

### EV-005 — “可访问”与“可装配”是两个权限问题
- Path: `MemoryCore/src/metadata/service/permission-checker.ts`
- Symbol: `checkPermission`, `canBindAsset`
- Observation: Owner、团队成员、Visibility、角色默认和 ACL 决定用户动作；另一函数单独判断资产是否能绑定到目标 Agent。
- Meaning: 团队共享不能只依赖搜索过滤，资产交付本身也需要治理。
- Alternative explanation: 静态规则正确不等于所有入口都正确调用了规则。
- Confidence: high

### EV-006 — Knowledge 采用渐进式只读暴露
- Path: `MemoryKnowledge/src/routes/tools.ts`
- Symbol: `WIKI_TOOLS`, `CODE_GRAPH_TOOLS`, `createToolsRoutes`
- Observation: Agent 先列出工具，再通过白名单调用 Wiki 搜索/读取和 CodeGraph explore/callers/callees/impact 等查询；管理操作不在白名单中。
- Meaning: 文档与代码知识不必整库进入 Prompt，也缩小了 Agent 工具权限面。
- Alternative explanation: 只读工具仍需要正确的服务鉴权和资源隔离。
- Confidence: high

### EV-007 — 记忆增强可以失败开放
- Path: `MemoryProxy/src/handler.ts`
- Symbol: 请求注入与流式写回路径
- Observation: Injection Pipeline 抛错时回退原始请求；流式响应结束后 L0 以带重试的异步写入回流，避免拖慢 SSE 关闭。
- Meaning: 增强层故障不应阻断 Agent 主链路，这是 Proxy 独立存在的重要理由。
- Alternative explanation: Proxy 自身仍是集中式复杂组件，需要高可用与端到端测试。
- Confidence: high

### EV-008 — Knowledge 构建队列按资产隔离
- Path: `MemoryKnowledge/src/store/build-queue.ts`
- Symbol: `BuildQueue.enqueue`
- Observation: 每个 asset key 拥有独立 `SerialQueue`；同一资产串行，不同资产不共享一条全局队列。
- Meaning: 当前实现避免同一资产并发写冲突，也修正了旧稿关于“跨资产共享串行队列”的判断。
- Alternative explanation: 不同资产并行仍可能竞争 CPU、磁盘和 LLM 配额。
- Confidence: high

## Engineering Evidence

- `MemoryCore/package.json`、`MemoryKnowledge/package.json` 与 `MemoryProxy/package.json` 均定义 build/test 或 typecheck 脚本。
- `.github/workflows/pr-ci.yml` 当前只执行安装、打包、Manifest、包体积和 Skill Queue Isolation Guard，没有执行 build、typecheck 或 test。
- 当前提交通过 `git ls-files` 未找到 `*.test.*`、`*.spec.*`、`tests/` 或 `__tests__/` 源码；存在 Vitest 配置和测试脚本，但公开分支缺少测试实现。
- MemoryCore 的 Skill 版本模块包含失败清理、幂等与过期版本处理；Recall 返回结构化超时/部分失败信息。
- Proxy 对上游超时和模型路由失败有重试路径，Injection 失败采用非致命降级。
- 本轮没有执行依赖安装、测试、构建或 Benchmark，因此不声称运行通过。

## Limitations

- 多服务与多存储使部署、升级、备份、权限审计和排障明显重于轻量 Memory SDK。
- Chat Memory、Skill、Wiki、CodeGraph 都包含异步或派生数据链路，用户需要接受最终一致性。
- 时间有效期、事实冲突和来源事件不是统一核心数据模型；Graphiti 在这一点更专门。
- README 明确写出 CodeGraph 私有仓库/SSH 支持、全自动路由和更广泛跨框架适配仍在完善。
- 官方 PersonaMem 结果未在当前仓库提供可复现材料。
- 默认分支缺少公开测试源码，PR CI 也未执行 build/test/typecheck，工程治理没有跟上产品边界扩张速度。

## Contradictions

- README 强调完整团队资产闭环，但自动记忆路由仍在迭代，现阶段 Fixed Binding 和人工治理仍占重要位置。
- 包含丰富 Test Script 与 Vitest 配置，但当前分支没有提交相应测试文件，CI 也不运行测试。
- 旧分析稿认为 Wiki/CodeGraph 共享串行构建队列；当前代码显示 BuildQueue 已按资产 key 隔离，应撤销旧判断。
- “跨框架迁移”是设计目标且已有多个适配入口，但官方注意事项仍把更广泛适配列入 Roadmap，因此应写成“相对解耦”，不是“完全框架无关”。

## Open Questions

- 发生互相矛盾的长期事实时，系统怎样决定当前有效版本并向 Agent 解释来源？
- 自动路由未来依据哪些可解释信号选择资产，如何评估漏装配和误装配？
- PersonaMem 提升分别来自分层提炼、Hybrid 召回、Persona、Scene Navigation 还是更大的上下文输入？
- 大规模多团队并行构建 Wiki/CodeGraph 时，CPU、磁盘、LLM 和队列公平性如何治理？
- Proxy、Core、Knowledge 与 Panel 的端到端鉴权矩阵和负向测试是否会公开？
- 每万轮会话的 LLM 成本、存储增长、提炼延迟和召回 P95 是多少？
