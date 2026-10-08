# Claim Ledger

| ID | Type | Claim | Evidence | Confidence | Article Location |
|---|---|---|---|---|---|
| C-001 | FACT | 项目把 Chat Memory、Skill、Wiki、CodeGraph 定义为四种统一资产类型 | `MemoryCore/src/metadata/types.ts`; `README_CN.md` | high | 四类资产不是四个菜单 |
| C-002 | INFERENCE | 项目更接近 Agent 经验控制面，而不仅是长期记忆库 | C-001 + C-005 + C-006 | high | 开篇、结论 |
| C-003 | FACT | L1 采用关键词、向量或 Hybrid 检索，Hybrid 通过 RRF 融合 | `MemoryCore/src/core/hooks/auto-recall.ts` | high | 从“记住”到“交付” |
| C-004 | FACT | L2/L3 稳定内容和 L1 动态召回进入不同上下文区域 | `MemoryCore/src/core/hooks/auto-recall.ts` | high | 从“记住”到“交付” |
| C-005 | INFERENCE | 项目的上下文策略可概括为 Push 概览 + Pull 细节 | C-004 + `MemoryKnowledge/src/routes/tools.ts` | high | 从“记住”到“交付” |
| C-006 | FACT | Skill 更新包含 Owner/版本校验、资源复制、历史版本和失败清理 | `MemoryCore/src/core/skill/skill-versioning.ts`; `skill-permission.ts` | high | Skill 为什么不是 Prompt |
| C-007 | FACT | 资产权限与 Agent 可绑定性由不同函数判断 | `MemoryCore/src/metadata/service/permission-checker.ts` | high | 经验共享为什么需要控制面 |
| C-008 | FACT | Wiki 与 CodeGraph 通过只读白名单工具对 Agent 暴露 | `MemoryKnowledge/src/routes/tools.ts` | high | 知识为什么不整库注入 |
| C-009 | FACT | Knowledge BuildQueue 是 per-asset-key 串行，而非全局串行 | `MemoryKnowledge/src/store/build-queue.ts` | high | 知识为什么不整库注入 |
| C-010 | FACT | Proxy 注入失败时回退原始请求，流式结束后异步重试写入 L0 | `MemoryProxy/src/handler.ts` | high | Proxy 的价值与代价 |
| C-011 | OPINION | 对单 Bot 和少量偏好记忆，这套多服务架构大概率过重 | stated complexity criteria | medium | 谁适合使用 |
| C-012 | FACT | README 报告 PersonaMem 由 48% 到 76%，但当前仓库未找到可复现材料 | `README_CN.md`; repository-wide `rg PersonaMem` | high | 必须保留的疑问 |
| C-013 | FACT | 当前分支 PR CI 不执行 build、typecheck 或 test，且没有提交测试源码 | `.github/workflows/pr-ci.yml`; `git ls-files` | high | 优点与代价 |
| C-014 | INFERENCE | 局部算法并非主要原创点，辨识度来自异构资产、治理与交付的组合边界 | C-001 + C-003 + C-006 + C-007 + C-008 | high | 创新判断 |
| C-015 | OPEN | 生产规模下的召回质量、成本、构建吞吐和隔离可信度尚未由本文验证 | 未运行完整系统与 Benchmark | high | 必须保留的疑问 |
| C-016 | FACT | Mem0 主抽象是通用记忆层，Graphiti 是时序上下文图，Letta 是有状态 Agent 平台 | 竞品官方 GitHub（2026-08-09） | high | 竞品坐标 |
| C-017 | INFERENCE | TencentDB Agent Memory 的相对优势是团队经验覆盖面，弱项是专门记忆算法、时序模型和轻量接入成熟度 | C-001 + C-016 + official limitations | medium | 竞品坐标 |
