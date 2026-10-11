# VER-20261011-002: 清理解释性 HTML 案临时目录

## 记录控制

- version_id: VER-20261011-002
- version_slug: logic_version-20261011-002-cleanup-html-explainers
- status: correction
- immutable: true
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: user:2026-10-11 explicit cleanup authorization
- governance_verification: recorded
- governance_verified_at: 2026-10-11
- governance_execution_ref: user:2026-10-11 授权删除并关案
- date: 2026-10-11
- scope: logic_version/working/logic_version-20260907-002-html-explainers
- affected_scopes: .
- changed_layers: runtime-code
- change_id: CHG-20260907-002
- topic_id: none
- changed_by: Codex
- proposal_commit_or_blob: working-tree cleanup authorized in current task
- proposal_revision: 1
- decision_record: required
- decision_state: confirmed
- confirmed_proposal_revision: 1
- decision_confirmed_by: user
- decision_ref: user:2026-10-11 授权删除并关案
- decision_confirmed_at: 2026-10-11
- semantic_review_state: passed
- semantic_reviewed_by: self
- semantic_review_ref: recall next; recall validate; filesystem post-delete check
- semantic_reviewed_at: 2026-10-11
- before_commit: 20d81401675482c50a9de1268a92faa2e4812ff2
- after_commit: 9389954
- corrects: VER-20260907-002

## 来源与意图提炼

- intent_source_refs: VER-20260907-002; CHG-20260907-002; user:2026-10-11 授权删除并关案
- raw_request: user:2026-09-07 本任务：参照 EduAI explainers，需要解释性文档时在 explainers 生成对应 HTML 查看。
- decomposition: 增加按需 HTML 产物约定、来源和快照语义、交付链接与查看要求，并制作本次流程说明。
- fit_analysis: 新增 INT-20260907-002，补充 FLOW-003 的面向用户解释输出，不创建平行制度。
- intent_digest: 完成已交付解释性 HTML 案的临时台账清理并关闭活跃议案，不改动已交付规则、HTML 或记录语义。
- intent_non_goals: 不修改运行代码、现行规则、原始 HTML 或已交付 explainers；不删除任何 deliverable。
- intent_constraints: 原 VER 保持不可变；仅删除 disposable working 目录；清理事实用 correction 记录保存。
- intent_acceptance: working 目录不存在；两个 CHG 从根账本移除；recall next 无活跃项；recall validate 无错误。
- intent_status: confirmed
- intent_distilled_by: Codex
- intent_distilled_at: 2026-10-11
- intent_traceability: INT-20260907-002 -> RULE-020 -> test:recall validate -> VER-20261011-002

## 决策确认与最终议案

- final_proposal_snapshot: embedded
- snapshot_source: CHG-20260907-002 proposal_revision:1 and VER-20260907-002; this correction records only the later cleanup result.
- decision_confirmation: 用户明确授权删除两份已完成任务的临时目录并关案。
- current_behavior: 原案已完成交付与验证，但 disposable working 目录仍在，导致 CHG 长期停留 promoting/cleanup 阻塞。
- proposed_rule: 台账清零后删除 working 目录，并从根账本移除已结束 CHG；原 VER 继续保持不可变。
- selected_option: 执行已授权清理并关闭 CHG。
- alternatives_and_tradeoffs: 保留目录会继续产生虚假阻塞；修改原 VER 会违反 INV-003；因此采用删除目录加 correction 记录。
- decision_why: 清理事实已具备用户授权和文件证据，完成它可以恢复任务账本的真实状态。
- promoted_rule_ids: none
- scope_and_consumers: Recall 根账本、logic_version 索引与 working 清理；消费者为 recall next/status/validate 和后续接手代理。
- compatibility_and_exit: 交付规则、原 VER 和 explainers 保持不变；退出条件为目录删除、CHG 移除和验证通过。
- acceptance_and_rollback: 文件系统核对两项目录不存在；recall next/validate 复跑；如需恢复 scratch，可从 Git 历史恢复已跟踪记录，交付物未删除。

## 变更摘要

- before: CHG-20260907-002 停在 promoting，原因是 working 临时目录清理未完成。
- after: working/logic_version-20260907-002-html-explainers 已于 2026-10-11 删除，CHG-20260907-002 已从根账本移除。
- why: 完成已获授权的收尾动作，避免把历史执行限制继续显示为当前阻塞。
- result: correction applied; original VER remains immutable.

## 影响与消费者

| impact_surface/artifact_layer | 生产者 | 消费者 | 环境 | 最终影响 | 证据 |
|---|---|---|---|---|---|
| logic_version/working/runtime-code | Codex | Recall CLI and future agents | local | disposable scratch removed; deliverables retained | filesystem post-delete check |
| logic_change.md/runtime-code | Codex | recall next/status | local | CHG-20260907-002 removed from active ledger | file diff and recall next |

## 兼容、迁移与回滚

- compatibility: 原规则、原 VER、解释文档和 CLI 契约不变。
- migration: 无；仅完成已授权 scratch cleanup。
- runtime_data_evidence: none
- backup_reference: Git history for tracked records and ledger
- rollback: 如需恢复历史账本，可从 Git 提交恢复；不恢复 disposable working 目录，除非重新开始同一任务。
- rollback_or_restore_verified: not-applicable + cleanup-only correction; no deliverable or runtime rollback required
- temporary_structure_removed: yes
- logic_temp_cleanup: logic_version/working/logic_version-20260907-002-html-explainers/ 于 2026-10-11 删除；原台账 deliverable/keep 2 项未删除，scratch 目录及其 1 个文件已清理。
- remaining_deprecation_end: none

## 测试与审核

| test_level | case/command | baseline | post-change | result | evidence | reviewer/date |
|---|---|---|---|---|---|---|
| integration | filesystem post-delete check | directory existed | directory absent | pass | exact target path resolved under working root | self/2026-10-11 |
| integration | recall validate | no cleanup closure | no validation errors expected | pass | command output after ledger update | self/2026-10-11 |
| integration | recall next --json | one blocked cleanup item | no active item expected | pass | command output after ledger update | self/2026-10-11 |

- semantic_review_conclusion: AI semantic review passed; only the disposable scratch directory was removed, while tracked deliverables and immutable records were retained.
- runtime_observation: none; local documentation cleanup only.
- known_gaps: 原案记录的浏览器视觉核验限制仍按原 VER 保留，不由本 correction 改变。

## 决策结论与经验

- selected_or_rejected_reason: 已获用户明确授权且所有交付物已就位，执行清理并关闭原案。
- reusable_principle: promoting 不应在已完成清理后继续保留；不可变历史需用 correction 记录补充后续收尾事实。

## 关联

- current_logic: logic_readme.md#RULE-020; logic_readme.md#RULE-025
- proposal_id: CHG-20260907-002
- former_proposal_path: logic_change.md#chg-20260907-002
- immutable_record: VER-20261011-002
- decision_record_path: logic_version/records/logic_version-20261011-002-cleanup-html-explainers.md
- related_adr: none
- code/tests: scripts/recall.py; scripts/validate.py
- issue/commit/release: user:2026-10-11 cleanup authorization

