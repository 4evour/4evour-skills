# Claim Ledger

| ID | Type | Claim | Evidence | Confidence | Article Location |
|---|---|---|---|---|---|
| C-001 | FACT | Independent nodes collaborate through a network and do not share process memory automatically | System model; `../../01-资料/fact-ledger.md` F1 | High | Section 1 |
| C-002 | FACT | A timeout can mean not executed, still executing, or completed without a timely response | etcd API guarantees; AWS Builders' Library; F2 | High | Section 2 |
| C-003 | FACT | Retries of one business intent need a stable request identifier; identical parameters need not mean identical intent | AWS Builders' Library; F3 | High | Section 3 |
| C-004 | INFERENCE | In the single-database order example, the idempotency record and order write must commit atomically | Concurrent timeline plus AWS idempotency guidance; F4 | High | Section 3 |
| C-005 | FACT | Asynchronous replication permits replica lag and can lose unreplicated acknowledged writes after failover | PostgreSQL Warm Standby; F5 | High | Section 4 |
| C-006 | FACT | Replica receipt, durable storage, and replay visibility are different confirmation stages | PostgreSQL Warm Standby; F6 | High | Section 4 |
| C-007 | FACT | Linearizability respects real-time order of completed operations | etcd API guarantees; Gilbert/Lynch; F7 | High | Section 4 |
| C-008 | FACT | During a network partition, linearizable consistency and availability for every valid request cannot both be guaranteed | Gilbert/Lynch CAP paper; F8 | High | Section 5 |
| C-009 | FACT | A fixed three-member voting group has a quorum of two; a 2+1 partition cannot produce two quorums | etcd FAQ; F9 | High | Section 6 |
| C-010 | FACT | Separate local transactions do not make independent service commits one atomic operation | Transaction-boundary failure timeline; F10 | High | Section 7 |
| C-011 | INFERENCE | Eventual workflow recovery needs durable progress, idempotent retries, conflict handling, and visible failure states | F2-F4 and partial-completion timeline; F11 | High | Section 7 |
| C-012 | OPEN | Consensus algorithms and distributed transaction protocols require separate treatment | Declared scope boundary | High | Ending |
