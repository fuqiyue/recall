# 治理模式

Recall 默认服务单人或低并发小团队，不把 Markdown 字段误称为组织权限控制。

权限控制不通过这些字段实现，它们只是可追溯的记录。

## personal（默认）

**适用**：单人开发，或单人 + AI。

**特点**：

- 允许同一人承担协调、实现和语义审查
- 必须诚实记录 `changed_by`、确认来源、审查证据和 Git/发布等治理引用
- `decision_confirmed_by: self` 只能表示具备项目决策权的人明确作出选择，不能由当前执行代理用来确认自己的建议
- `VER-*` 的不可变性依赖版本控制或外部存档，而不是 `immutable: true` 这一行文字

**字段层级**：personal 层 8 个字段。

**不维护独立的语义审查与治理验证记录**，因为实施者和审查者是同一人时，分离的字段不增加实际控制力，只增加行数。需要记下自审结论时写一行自述即可。

**决策记录只用 `VER-*`**：personal 模式不要求 ADR，`logic_version/decisions/` 允许为空，空目录不是审查缺陷。仅当用户明确要求沉淀跨范围、跨议案的长期约束时才创建 ADR。

## collaborative

**适用**：小团队需要真实分工。

**前提**：项目已配置并引用实际的 PR/CI、分支保护、CODEOWNERS 或外部审批控制。

**特点**：

- 高风险变更的通过性语义审查必须由非实施者完成
- 用 `governance_evidence`、`governance_verification: verified` 和 `governance_verified_at` 记录责任人何时核验了哪项控制
- 进入验证阶段的高风险 CHG 还要用 `governance_execution_ref` 指向本次 PR/CI/审批执行

**字段层级**：personal 层 8 个 + collaborative 层 9 个。

Recall 的审计器只能检查带类型引用、日期和责任分离，不能证明外部控制仍在运行，也不能替代代码托管平台的权限执行。

**只有在这些控制真实存在时，`collaborative` 模式才有意义。**

## compliance（审计留存）

**适用**：用户明确要求正式审查、审计留存或表单合规。

**特点**：

- 所有字段完整填写
- 运行 `audit_logic_map.py --formal-review`
- 保留完整审计链（`INT-* -> RULE-* -> test:<path#anchor> -> VER-*`）
- 输出 Recall Brief

**字段层级**：personal 8 个 + collaborative 9 个 + compliance 13 个。

## 并发协调边界

同一 `logic_change.md` 适合低并发协调。

若多个作者频繁同时改同一账本、需要跨团队队列、强制审批或审计留存，先把需求/讨论交给 Issue、Spec、PR 或变更系统，再在 Recall 保留当前 CHG 的提炼和稳定引用。

不要把单文件账本硬扩成组织级工作流。

## 迁移旧项目

旧项目迁移时直接在同一份根文档中把 `approved`、`reviewed_by`/`review_ref` 和 `AUTH-*` 旧字段改写为当前真实阶段的 `decision_*` 与 `semantic_review_*` 字段。

同时补齐对应 `.agents/` 或 `.claude/` 目录和根入口标记。

不要保留兼容字段、双状态或平行版本文件。
