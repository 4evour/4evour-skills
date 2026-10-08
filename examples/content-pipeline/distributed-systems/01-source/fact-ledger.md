# 信息账本与来源核对

核对日期：2026-09-17。
素材类型：一手文档、CAP 作者论文、明确标注的假设案例。没有作者项目经历、真实日志、基准测试或生产验证。

## 来源

- S1：[etcd v3.6 API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/)。实际读取了项目官网仓库对应 Markdown。核对 Operation completed、Linearizability、Revision：超时结果不确定；默认 KV 读写的保证与可返回旧数据的读模式有别；修订号表示逻辑顺序。
- S2：[AWS Builders' Library：Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。核对 Retrying and side effects、Reducing client complexity、Late arriving requests：重试副作用、调用者提供的请求标识、去重记录与业务变更的原子性、标识生命周期。
- S3：[PostgreSQL：Warm Standby](https://www.postgresql.org/docs/current/warm-standby.html)。核对 Streaming Replication、Synchronous Replication：默认异步；故障切换可能丢未复制提交；同步确认阶段不同；remote_apply 等待回放。
- S4：[Seth Gilbert / Nancy Lynch：Perspectives on the CAP Theorem](https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf)。读取前六页，核对第 2 节定义与分区证明、第 3 节共识与故障假设：CAP 的 C 为原子读写语义；A 为每个请求最终得到操作响应；不能让通信故障下的原子寄存器同时保证所有请求可用。
- S5：[etcd v3.6 FAQ](https://etcd.io/docs/v3.6/faq/)。读取官网仓库 Markdown，核对 leader、quorum 和 failure tolerance：Raft 多数提交、3 个投票成员多数为 2、失去多数无法推进依赖共识的操作。

## 承重事实

| ID | 正文陈述 | 证据或推导 | 必须保留的边界 |
|---|---|---|---|
| F1 | 多个独立计算节点通过网络协作 | 本文工作定义、请求拓扑 | 不要求先拆微服务；应用与数据库分离也已有分布式边界 |
| F2 | 超时可能意味着未执行、执行中或执行成功而响应未到 | S1、S2 | 客户端只知道期限内没有成功响应 |
| F3 | 同一业务意图重试要复用标识；新意图使用新标识 | S2 | 参数相同不必然是重试；标识绑定调用者与参数 |
| F4 | 示例订单去重记录与订单创建要原子提交 | S2；并发先查后写推导 | 限于同一事务存储内的订单创建，不包含库存、支付等外部副作用 |
| F5 | 异步复制允许副本落后，切换可能丢未复制写入 | S3 | 具体损失取决于复制、持久化和切换配置 |
| F6 | 同步复制的确认不必等于查询可见 | S3 | 接收、持久化、回放三个阶段不能混用；任意副本不一定最新 |
| F7 | 线性一致性尊重操作的实时先后 | S1、S4 | 并发写读可有多个合法排序；数据库快照与缓存会影响端到端观察 |
| F8 | 分区条件下不能同时保证线性一致性与所有非故障节点请求可用 | S4 | 不是任意三选二；C 非 ACID 的 C；A 非工程可用率；错误响应不是读写成功 |
| F9 | 3 个投票节点的多数为 2，2+1 分区不能形成两个多数 | S5、算术 | 静态成员、协议正确执行；多数本身不构成共识算法 |
| F10 | 本地事务不能自动使不同服务的独立提交成为一个原子动作 | 事务边界与故障时序推导 | “本地”一词保留；不声称所有数据库内部都为单机 |
| F11 | 重试与补偿需要持久化状态、幂等和恢复机制 | F2-F4 与部分完成时序推导 | 补偿可失败；跨事务发消息存在间隙；本文仅建立概念，不是生产方案 |

## 教学数字登记

订单 O-100、请求 r-001、库存初始值 1、等待期限 2 秒、A/B/C 三个节点、2+1 分区均为教学设定。
2 秒不是推荐超时；3 节点不是所有集群的部署要求。
全部日志和状态时间线为人工构造，无实验结果，无真实事故。

## 未采用的来源

InfoQ 的 CAP 作者文章返回 HTTP 405；Cornell 的 CAP 论文链接在当前 Python TLS 环境下未通过证书验证。未绕过验证，未引用未读内容。改用 MIT 托管的 Gilbert / Lynch 论文，并已成功读取。

## 改稿回扫

保留：超时的“可能”、最终一致性的前提、共识的多数与网络条件、同步复制的确认边界、示例日志声明、外部副作用不在本地幂等事务之内。
避免：“加节点一定更快”“副本必然最新”“超时等于失败”“多数即可正确”“发 MQ 自动原子”“读完即可用于生产”。
