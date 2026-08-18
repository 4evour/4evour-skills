# 研究产物模板

文件名和表头保留稳定英文，便于校验脚本和下游 skill 交接；正文内容使用中文。

## 1. source-state.md

```markdown
# Source State

- Repository:
- Local path:
- Remote URL:
- Branch/tag:
- Commit:
- Research date:
- Primary language:
- Requested audience:
- Research question:
- Explicit non-goals:
- Official docs inspected:
- Competitors inspected:
```

## 2. thesis.md

```markdown
# Thesis

## Central Thesis

一个可证伪、有工程意义的句子。

## Common Misreading

一个合理但不完整的理解。

## Supporting Evidence

1. 源码或运行证据。
2. 源码或运行证据。
3. 架构、测试或比较证据。

## Counterargument

最强的公平反对意见。

## Conditions

论点成立和不成立的条件。

## Unproven

当前证据无法证明的内容。
```

## 3. claim-ledger.md

```markdown
# Claim Ledger

| ID | Type | Claim | Evidence | Confidence | Article Location |
|---|---|---|---|---|---|
| C-001 | FACT | ... | `path/file.ts` | high | Section 2 |
| C-002 | INFERENCE | ... | C-001 + C-004 | medium | Thesis |
| C-003 | OPINION | ... | stated criteria | medium | Conclusion |
| C-004 | OPEN | ... | missing public evidence | low | Limitations |
```

规则：

- `Type` 只能是 `FACT`、`INFERENCE`、`OPINION` 或 `OPEN`；
- `FACT` 的 `Evidence` 不能为空；
- 不要把一条 claim ledger 作为另一条 `FACT` 的唯一证据；
- 易变外部事实附带 URL 和访问日期。

## 4. research-manifest.yaml

```yaml
topic:
stage: research
research_date:
commit:
claim_ledger: claim-ledger.md
status: draft | reviewed | complete
open_questions: open-questions.md
```

## 5. open-questions.md

```markdown
# Open Questions

| ID | Question | Why It Matters | Missing Evidence | Next Check |
|---|---|---|---|---|
| OQ-001 | ... | ... | ... | ... |
```
