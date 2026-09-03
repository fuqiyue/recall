# Recall Skill Active Changes

## 文档控制

- scope: .
- scope_path: .
- module_id: MOD-ROOT
- current_policy: logic_readme.md
- owner: self
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:https://github.com/fuqiyue/recall@main
- governance_verification: recorded
- governance_verified_at: 2026-08-08
- last_updated: 2026-09-04
- active_changes: none

## 议案规则

- 本文件所有条目默认 `effective: false`
- 允许状态：draft | awaiting-decision | implementing | verifying | promoting | blocked
- 个人小项目使用简化流程：draft -> implementing -> verifying -> promoting
- 高风险修改使用决策流程：draft -> awaiting-decision -> implementing -> verifying -> promoting

## 讨论主题索引

| topic_id | 同类议题/共享问题 | coordinator | discussion_refs | related_changes | status |
|---|---|---|---|---|---|

当前无活跃讨论主题。表头保留以声明 schema。

## 活跃议案索引

当前无活跃修改议案。

---

**说明**：

当需要追踪修改时，在此文件中创建 CHG 条目。完成后：
1. 更新所属 `logic_readme.md`（宪法或领域，如规则变化）
2. 归档到 `logic_version/records/`（如为高风险）
3. 把 CHG 的需求拆解三字段搬入 VER 记录后再删除 CHG 条目与根公报行（需求保全见 RULE-014；两级账本与公报见 RULE-018；操作步骤见 references/change-lifecycle.md 第 7-9 步）

本账本只放修宪议案（改全局规则、意图层、范围登记表、INV）；领域事务的 CHG 立在 `logic_domains/<domain>/logic_change.md`，并在此处"活跃议案索引"登记一行指向领域账本。

**记住**：logic_change.md 是临时的工作记录，不是长期真相源。
