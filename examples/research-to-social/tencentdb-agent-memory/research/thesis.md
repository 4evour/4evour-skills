# Thesis

## Central Thesis

TencentDB Agent Memory 最有价值的创新不是提出一种新的记忆检索算法，而是把 Agent 工作中产生的异构经验建模为四类资产，并用统一的身份、权限、版本、装配和交付机制，把“模型记忆”推进为“团队经验控制面”。

## Common Misreading

把它理解成“带管理界面的长期记忆/RAG 服务”。这个解释没有错，但会遗漏 Skill、Wiki、CodeGraph 与 Chat Memory 采用不同数据结构和消费方式，以及 Fixed Binding、ACL、版本和 Proxy 如何把这些资产交给具体 Agent。

## Supporting Evidence

1. `MemoryCore/src/metadata/types.ts` 将 `skill`、`llm_wiki`、`code_graph`、`chat_memory` 统一登记为 `AssetType`，但仍保留不同的 `InjectionMode` 和底层服务。
2. `MemoryCore/src/core/skill/skill-versioning.ts` 与 `skill-permission.ts` 证明 Skill 被实现为带 Owner、资源目录、历史版本和乐观锁的资产，而非数据库中的一段 Prompt。
3. `MemoryCore/src/core/hooks/auto-recall.ts` 把稳定的 L2/L3 放到可缓存的系统上下文，把每轮变化的 L1 放到动态上下文，并给检索设置超时、字符预算与工具调用上限。
4. `MemoryCore/src/metadata/service/permission-checker.ts` 与 `FixedAssetBindingEntity` 把“谁能看”和“能否给某个 Agent 装配”分成两个判断。
5. `MemoryKnowledge/src/routes/tools.ts` 通过只读工具白名单渐进暴露 Wiki 与 CodeGraph，而不是把完整知识库预装进 Prompt。

## Counterargument

这套“经验控制面”可能只是把多个已有能力组合在一起：BM25、向量搜索、RRF、ACL、版本控制、知识图和协议代理都不是新算法；对于单个 Bot 或少量偏好记忆，它还会引入不必要的多服务部署和治理成本。

## Conditions

论点在以下条件下成立：多个 Agent 或成员需要长期共享对话经验、工作方法、文档和代码知识；团队在意 Owner、版本、权限和定向装配；并愿意承担异步构建与多组件运维。若只是单 Agent 的轻量个性化记忆，Mem0 一类更聚焦的记忆层通常更直接。

## Unproven

- README 报告的 PersonaMem 48%→76% 尚未在当前仓库找到可复现脚本、数据、模型配置与原始日志。
- 自动资产路由仍处于迭代状态，当前能力较多依赖 Fixed Binding。
- 当前代码不能单独证明生产规模下的 P95 延迟、构建吞吐、成本和多租户安全性。
- 时间有效期、冲突消解与来源追溯的完整性尚未达到时序知识图引擎的专门程度。
