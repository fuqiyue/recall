# ADR 决策记录模板

目录：元数据；问题、意图与证据；决定与备选方案；后果、兼容、验证与关联。

对跨模块、公共契约、数据模型、版本兼容、安全、部署或长期复杂度有影响的决定使用，集中放在项目根 `logic_version/decisions/`。普通局部修复不需要 ADR。

```markdown
# ADR-YYYYMMDD-NNN: <决策标题>

## 元数据

- status: proposed | accepted | active | transitional | deprecated | superseded | archived | rejected
- scope: <仓库相对路径/模块/契约>
- owner: <团队/角色>
- created: YYYY-MM-DD
- valid_from: YYYY-MM-DD | event-driven
- valid_until: YYYY-MM-DD | none | event-driven
- last_verified: YYYY-MM-DD
- review_due: YYYY-MM-DD | event-driven
- decision_source: <用户/会议/issue/会话/法规>
- change_id: <CHG-ID 或 none>
- governed_rule_ids: <受此 ADR 约束的 RULE-ID；没有填 none>
- proposal_revision: <CHG 的正整数版本；无 CHG 填 none>
- decision_confirmed_by: <确认人；proposed 时填 none>
- decision_ref: <user-confirmed:YYYY-MM-DD/issue/会议/外部决定引用；proposed 时填 none>
- decision_confirmed_at: <YYYY-MM-DD；proposed 时填 none>
- immutable: false | true
- confidence: confirmed | mixed | inferred
- supersedes: <ADR ID 或 none>
- superseded_by: <ADR ID 或 none>

## 问题与上下文

<要解决的真实问题、当前行为、环境和触发条件。>

## 用户意图与约束

- intent_source_refs: <任务/Issue/会话/Plan/Spec/Steering/VER 的稳定引用；不复制完整聊天或原始提示词>
- intent_digest: <要解决的问题与成功状态的可审计提炼>
- intent_non_goals: <本次不解决什么；没有明确时填 not-specified>
- intent_constraints: <用户确认或稳定来源中的边界；没有明确时填 not-specified>
- intent_acceptance: <可验证完成条件；没有明确时填 not-specified>
- intent_status: confirmed | source-derived | inferred | mixed
- intent_distilled_by: <self/agent/角色>
- intent_distilled_at: YYYY-MM-DD

`inferred` 不能作为 `accepted` 或 `active` ADR 的唯一决策来源；必须由 `decision_ref` 或其他权威证据确认。外部规格、Steering 或 Plan 可以保留完整正文，本 ADR 只保存引用和本次采纳的提炼。

## 证据

| 结论 | 类型 | 来源 | 置信度 |
|---|---|---|---|
| ... | user-confirmed/decision/code/test/runtime/history/inference | ... | high/medium/low |

## 决定

<用可验证的语言描述选择和适用范围。>

- confirmed_proposal_revision: <与本 ADR 一致的已确认 CHG 版本；无 CHG 填 none>
- immutable_decision_record: <logic_version/records/logic_version-...md；决策已实施时必填>

## 选择理由

<为何此方案在当前证据下优于其他方案；说明错判代价。>

## 备选方案

### A. <方案>

- 好处：...
- 坏处：...
- 复杂度增量：...
- 未采用原因：...

### B. <方案>

- 好处：...
- 坏处：...
- 复杂度增量：...
- 未采用原因：...

## 后果

- 正面：...
- 负面：...
- 新增复杂度：<分支、抽象、状态、依赖、运维成本>
- 移除条件：<临时结构何时删除；永久结构填 not-applicable 并说明>

## 可复用原则（可选）

- principle: <可迁移到相似问题的抽象原则>
- applies_when: <适用触发条件和范围>
- does_not_apply_when: <反例、边界和例外>
- asymmetric_cost: <错误判断两侧的代价>
- confidence: high | medium | low

## 消费者与不变量

- consumers: <真实消费者及证据>
- invariants: <不可破坏约束及验证方法>

## 兼容性矩阵

| 对象 | producer | consumer | env | 旧版本/数据存在 | 策略 | 结束条件 |
|---|---|---|---|---|---|---|
| ... | ... | ... | local/staging/prod | yes/no/unknown | replace/migrate/dual-read/adapter/deprecate | ... |

## 迁移与回滚

- migration: ...
- dry_run: ...
- idempotent: yes/no/unknown
- partial_failure_handling: ...
- backup: ...
- rollback: ...
- failure_signals: ...

## 验证

- tests: ...
- deployment/runtime checks: ...
- unresolved risks: ...

## 关联

- logic_readme: ...
- linked_rule_ids: <logic_readme.md 中直接链接本 ADR 的 RULE-ID；没有填 none>
- logic_change: <CHG-ID 或 none>
- logic_version: <不可变决策记录路径或 none>
- code/tests: ...
- issue/commit/release: ...
```

生命周期规则：

- 变更决策时创建新 ADR 或明确更新仍处于 `proposed` 的 ADR，不抹除已执行决策的历史。
- 新 ADR 生效后，把旧 ADR 标记为 `superseded` 并互相链接。
- `transitional` 必须包含结束条件、负责人和复查日期。
- `inference` 不能成为 `accepted` 或 `active`，直到获得用户或权威来源确认。
- `accepted`、`active` 或 `transitional` 的 ADR 必须把 `immutable` 置为 `true`，其确认字段绑定 `proposal_revision`；后续修正以新 ADR 或 `correction` 记录表达。
- 如果 ADR 约束某条已生效关键规则，则 `governed_rule_ids` 与 `linked_rule_ids` 必须可追溯到 `logic_readme.md`；不要只让关闭后的 CHG 承担长期引用。
