# logic_version 不可变决策记录模板

每个已结束且需要保留设计原因的变更生成一份不可变文件，集中放在项目根 `logic_version/records/`。机器 ID 固定为 `VER-YYYYMMDD-NNN`；文件 slug 固定为 `logic_version-YYYYMMDD-NNN-<scope>`。完成后不可静默改写。`immutable: true` 表示追加式规则；实际防改写由 Git/受保护发布或外部存档提供，并通过治理引用和结果提交留痕。

对使用过 `decision_gate: required` 或 `history_retention: full` 的 CHG，本文必须保留关闭前的完整决策逻辑，而不是只保留一句摘要：请求来源引用、可审计意图提炼、最终议案快照、确认的是哪一版、方案取舍、影响、兼容/迁移、验证、代码语义审查和回滚都应可在单个记录中恢复。对 `history_retention: compact` 的中等变更，保留同一结构但可把不适用的决策字段标为 `not-required`；仍必须用简短内容说明来源、意图、影响面、基线、前后行为、验证和回滚，使关闭后的 CHG 不会失去 Recall 来源。

~~~markdown
# VER-YYYYMMDD-NNN: <变更标题>

## 记录控制

- version_id: VER-YYYYMMDD-NNN
- version_slug: logic_version-YYYYMMDD-NNN-<scope>
- status: effective | rejected | cancelled | rolled-back | correction
- immutable: true
- governance_mode: personal | collaborative
- governance_ref: <从根现行文档复制的 Git/PR/CI/审批/外部存档稳定引用>
- governance_evidence: <关闭时核验的控制证据；例如 pr:<ref>;ci:<run>;branch-protection:<ref>;approval:<ref>>
- governance_verification: verified | recorded | unavailable | not-applicable
- governance_verified_at: YYYY-MM-DD | none
- date: YYYY-MM-DD
- scope: <路径、契约、Schema 或用户行为；跨模块列全部 scope_path>
- affected_scopes: <全部 module_id/scope_path>
- authority_surfaces: <关闭时的精确 RULE/API/DB/FLAG/行为 ID>
- based_on: <关闭前重新核对的 policy + code/tree/release/snapshot 基线>
- changed_layers: <runtime-code/runtime-config/runtime-data/preprocess/test-fixture/generated/dependency/external>
- change_id: <CHG-ID 或 none>
- topic_id: <原 TOPIC-ID 或 none>
- topic_shared_context: <关闭时主题共享背景快照；topic_id=none 填 none>
- topic_shared_constraints: <主题共享约束快照；topic_id=none 填 none>
- topic_discussion_refs: <主题讨论来源稳定引用；topic_id=none 填 none>
- topic_final_conclusion: <主题关闭时最终结论；topic_id=none 填 none>
- changed_by: <最终实际修改人或代理；change_id 非 none 时必填>
- recall_route: simple | medium | high | none
- history_retention: compact | full
- runtime_state: <关闭时实际 not-implemented/implemented-unmerged/merged-not-deployed/deployed-guarded/deployed-active>
- runtime_environments: <关闭时实际环境；没有填 none>
- feature_flag: <关闭时开关状态；没有填 none>
- proposal_commit_or_blob: <包含最终议案正文的 Git commit/blob/issue 定位；change_id 非 none 时必填，无议案填 none>
- proposal_revision: <关闭时最终正整数版本；change_id 为 none 时填 none>
- decision_record: required | not-required
- decision_state: confirmed | not-confirmed | not-required
- confirmed_proposal_revision: <已确认版本或 none>
- decision_confirmed_by: none | <用户/角色/稳定代号>
- decision_ref: none | <user-confirmed:YYYY-MM-DD/issue/会议/外部决定引用>
- decision_confirmed_at: YYYY-MM-DD | none
- semantic_review_state: passed | failed | not-applicable
- semantic_reviewed_by: none | self | <实际审查人/代理>
- semantic_review_ref: none | <PR/commit/review/测试与运行证据引用>
- semantic_reviewed_at: YYYY-MM-DD | none
- before_commit: <提交/发布/校验值或 none>
- after_commit: <包含最终代码/现行制度的结果提交、PR merge、发布物或树校验值；不要求引用包含本记录自身的提交>
- supersedes: <VER/ADR/RULE ID 或 none>
- corrects: <被本记录纠正的 VER ID；非勘误填 none>

## 来源与意图提炼

- intent_source_refs: <从最终 CHG 复制的稳定来源引用；保留引用，不复制原始聊天或完整提示词>
- intent_digest: <从最终 CHG 复制的目标与成功状态提炼>
- intent_non_goals: <从最终 CHG 复制；没有明确时填 not-specified>
- intent_constraints: <从最终 CHG 复制；没有明确时填 not-specified>
- intent_acceptance: <从最终 CHG 复制；没有明确时填 not-specified>
- intent_status: confirmed | source-derived | inferred | mixed
- intent_distilled_by: <从最终 CHG 复制的责任信息>
- intent_distilled_at: YYYY-MM-DD
- intent_traceability: <INT-YYYYMMDD-NNN -> RULE-... -> test:<path#anchor> -> VER-YYYYMMDD-NNN；多个链用 ; 分隔>

原始聊天、自动记忆、模型输出和逐步推理不进入本记录。若外部 Plan、Spec 或 Steering 后续变化，本记录仍保留当时实际采纳的提炼和来源引用；新的解释通过新 CHG/VER/ADR 表达，不回写历史。

## 决策确认与最终议案

- final_proposal_snapshot: embedded
- snapshot_source: <原 CHG-ID、proposal_revision 和最终正文定位；不能只链接已经移除的活跃议案>
- decision_confirmation: <确认了什么选项、哪个版本；未确认或不需要时说明原因>
- current_behavior: <关闭前真实行为、入口/数据流与证据>
- proposed_rule: <最终拟议并实际生效、拒绝或取消的规则>
- selected_option: <选中的 A/B/C 或拒绝/取消结论>
- alternatives_and_tradeoffs: <每个未选方案的收益、坏处、复杂度和未采用原因>
- decision_why: <可审计的必要理由，不写隐藏思维链>
- promoted_rule_ids: <本次写入/替代的 RULE-ID；没有填 none>
- scope_and_consumers: <跨模块范围、生产者、真实消费者、环境和证据>
- compatibility_and_exit: <旧状态证据、迁移/适配/开关策略、唯一权威源和退出条件>
- acceptance_and_rollback: <验收、测试、运行观察和回滚路径>

## 变更摘要

- before: <结束前的规则或行为>
- after: <结束后的实际规则或行为；被拒绝/取消时填 unchanged>
- why: <必要且可审计的原因摘要>
- result: <生效、拒绝、取消或回滚的结论>

## 影响与消费者

| impact_surface/artifact_layer | 生产者 | 消费者 | 环境 | 最终影响 | 证据 |
|---|---|---|---|---|---|
| backend/runtime-code | ... | ... | local/staging/prod | ... | ... |

## 兼容、迁移与回滚

- compatibility: ...
- migration: ...
- runtime_data_evidence: <前后 schema/计数/校验/重建结果或 none>
- backup_reference: <外部备份标识或 logic_version/backups 路径；无则 none>
- rollback: ...
- rollback_or_restore_verified: yes | no | not-applicable + 证据
- temporary_structure_removed: yes | no | not-applicable
- logic_temp_cleanup: <删除 working 临时目录的路径、日期和结果；没有填 none>
- remaining_deprecation_end: <仍有过渡规则时填写>

## 测试与审核

| test_level | case/command | baseline | post-change | result | evidence | reviewer/date |
|---|---|---|---|---|---|---|
| unit | ... | ... | ... | pass/fail/not-run:<reason> | ... | ... |

每行只填一个 `test_level`：unit、component、contract、integration、e2e、migration 或 runtime；多级验证拆成多行。

- semantic_review_conclusion: <代码、调用方、Schema、测试结果和运行证据的审查结论>
- runtime_observation: <部署或观察证据；不适用填 none>
- known_gaps: <未覆盖项和风险>

## 决策结论与经验

- selected_or_rejected_reason: <一段简短结论；详细权衡已在最终议案快照中保留>
- reusable_principle: <有价值时填写，必须带适用边界；否则 none>

## 关联

- current_logic: <根 logic_readme.md 的 RULE-ID/章节；关键规则必须直接链接本记录或关联 ADR>
- proposal_id: <原 CHG-ID 或 none>
- former_proposal_path: <议案生效前所在 logic_change.md；正文关闭后会被移除>
- immutable_record: <本文件自身的 version_id；ADR 只在需要长期独立约束时填写>
- decision_record_path: <logic_version/records/logic_version-...md>
- related_adr: <logic_version/decisions/ADR 路径或 none>
- code/tests: ...
- issue/commit/release: ...
~~~

维护规则：

- 每次结束事件单独建文件，不把所有历史追加到一份巨型台账。
- `decision_record: required` 时，`decision_state: confirmed` 必须绑定 `proposal_revision`，并且代码语义审查必须 `passed`；未实施即拒绝/取消时可以标记 `not-confirmed` 或 `not-applicable`，但要在最终议案快照说明原因。
- `decision_record: required` 时，`intent_source_refs`、`intent_digest`、`intent_status`、`intent_distilled_by` 和 `intent_distilled_at` 必须可审计；`inferred` 或 `mixed` 不可写成用户已确认的要求。
- `governance_mode: personal` 允许 `semantic_reviewed_by: self`，但 `governance_ref` 与 `after_commit`/发布证据必须能追溯。`collaborative` 的有效高风险记录必须有非 `changed_by` 的通过性语义审查人，并让 `governance_ref` 指向实际 PR/CI、分支保护、CODEOWNERS 或外部审批控制；模板和审计只能核对证据，不能替代该平台的权限执行。
- `governance_evidence`、`governance_verification` 和 `governance_verified_at` 记录关闭时对外部控制的核验；`verified` 是带日期的责任人证据，不是平台权限的永久证明。`collaborative` 的有效高风险记录必须有非 `changed_by` 的通过性语义审查人、执行级 PR/CI/审批引用和可追溯治理证据。
- `topic_id` 非 none 时，四个 `topic_*` 字段必须完整保存主题共享背景、约束、讨论来源和最终结论，不能只留下 TOPIC-ID。
- `intent_traceability` 使用稳定的 `INT -> RULE -> test -> VER` 四段链；它是复杂变更的追踪索引，不保存原始提示词或隐藏推理。
- `recall_route` 保留本次采用的分析深度。高风险记录应列出全部 `promoted_rule_ids`，使后续从现行规则可以反向找到本记录；普通局部改动可填 `none`。
- 勘误通过新建 `status: correction` 的记录完成；新记录指向原记录，原记录保持不可变，集中索引同时列出两者。
- 这是历史决策记录，不是旧源码、旧 README 或运行数据副本。旧源码交给 Git；确需快照时进入根 `logic_version/backups/`。
- 格式化、变量改名或无制度影响的内部修改不生成记录；交付时报告 `docs_impact: none`。
