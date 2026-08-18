# 专业技术文章方法

## 文章目的模板

```markdown
# Article Purpose

## Why This Article

## Target Reader

## Reader Before and After

## Common Misreading

## Non-goals

## Evidence Base
```

文章应该改变一个技术判断，而不是只增加读者知道的名词数量。

## 论证地图模板

```markdown
# Argument Map

## Central Claim

## Existing Belief

## Claim Hierarchy

| ID | Claim | Type | Evidence IDs | Section Job |
|---|---|---|---|---|

## Causal Chain

## Counterargument and Reply

## Unproven
```

## 章节检查

每一章都要能回答：

1. 这一章要解决读者的哪个问题？
2. 它使用了哪些事实或源码证据？
3. 它与中心论点是什么关系？
4. 它带来什么工程判断、取舍或可迁移原则？

默认结构是“问题 → 洞察 → 机制 → 收益与成本 → 反例 → 比较 → 决策”。如果证据支持更好的顺序，可以调整，但要在 `argument-map.md` 中说明原因。

## 文章语气

以完成了初步研究的同行工程师身份写作：具体、克制、好奇，愿意在证据支持时做判断。避免新闻稿、营销稿、咨询报告和居高临下的教程口吻。

区分四类表达：

- `FACT`： “源码中的 `path/to/file` 表明……”
- `INFERENCE`： “我的阅读是……”
- `OPINION`： “在这个场景下，我会选择……”
- `OPEN`： “公开材料目前没有证明……”
