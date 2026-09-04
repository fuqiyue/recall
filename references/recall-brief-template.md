# Recall Brief 模板

仅在用户明确要求正式审查、完整 Recall 或填表合规时使用。每个重要结论附证据类型、来源和置信度；默认修改只做上下文读取和相称的分析，不生成本文件。

目录：范围与当前行为；制度、议案与消费者；兼容、影响与方案；测试、未知项和文档影响。

```markdown
# Recall Brief: <请求摘要>

## 范围与分类

- scope: <模块/路径/契约>
- change_route: simple | medium | high
- risk: low | medium | high | critical
- triggers: <跨模块/schema/API/持久化/部署/不确定意图等>
- mode: inspect | plan | update | verify
- module_route: <根范围登记中的 scope_path/章节锚点>
- layers: <runtime-code/runtime-config/runtime-data/preprocess/test-fixture/generated/dependency/external>

## 当前行为

| 结论 | 证据类型 | 来源 | 置信度 |
|---|---|---|---|
| ... | code/test/runtime/history | ... | high/medium/low |

## 来源与意图提炼

- intent_source_refs: <任务/Issue/会话/Plan/Spec/Steering/ADR/VER 的稳定引用；不复制原始提示词>
- intent_digest: <目标与成功状态的简短提炼>
- intent_non_goals: <明确不做什么；没有明确时填 not-specified>
- intent_constraints: <业务/兼容/技术/发布边界；没有明确时填 not-specified>
- intent_acceptance: <可验证完成条件；没有明确时填 not-specified>
- intent_status: confirmed | source-derived | inferred | mixed
- intent_gap: <会改变范围、语义、兼容、数据安全或方案选择的未决差距；有新旧需求矛盾时列明双方来源和具体冲突；没有填 none>

来源更新或提炼有实质变化时，更新同一 CHG 的 `proposal_revision`；不要把模型推断写成用户确认。

## 修改前逻辑与可并入性

- current_flow: <入口、关键调用、数据读写、失败路径>
- ownership_boundary: <当前职责、范围登记和代码边界>
- integration_fit: fit | fit-with-constraints | redesign-needed | uncertain
- fit_reason: <为何能/不能正确并入现有代码逻辑>
- baseline_tests: <命令、结果、日期、证据；未运行写原因>
- intent_gap: <用户目标与当前实现的差距>

## 现行制度与有效性

- current_policy: <适用 RULE/INV 条目>
- intended_design: <现行制度中的简短 why；复杂理由链接 ADR>
- decision_record: <关键规则对应的 VER/ADR；ordinary 规则可填 none>
- evidence: <user-confirmed/ADR/current logic>
- decision_status: active/transitional/deprecated/unknown
- last_verified: ...
- still_valid: yes/no/uncertain + 原因
- conflicts_or_drift: ...

## 活跃议案

| CHG-ID | proposal_revision | status | authority_surfaces | based_on | 冲突/依赖 | 运行暴露 | 历史保留 | 未决门槛 |
|---|---|---|---|---|---|---|---|---|
| ... | ... | draft/awaiting-decision/implementing/verifying/promoting/blocked | RULE/API/DB/FLAG/... | policy + code/snapshot | ... | runtime_state/env/flag | none/compact/full | ... |

没有相关议案时明确写 none。不得把用户确认、代码语义审查或测试通过误写成已经生效。

## 轻量决策检查点（仅在会改变方案时）

- required: yes/no + 原因
- proposal_revision: <将被确认的版本；不需要填 none>
- current facts: <当前行为、消费者、旧状态与证据>
- option A: <最小修改；收益、坏处、复杂度>
- option B: <结构修改；收益、坏处、复杂度>
- option C: <保持现状/延后；收益、坏处、复杂度>
- recommendation: <建议及错判代价>
- decision request: <列出旧要求、最新要求、具体矛盾和影响后，需要用户/授权决策方确认的明确选择；不需要填 none>
- confirmation: pending/confirmed/not-required + 来源、确认人和版本

可以给出推荐方案，但推荐不等于选择。存在尚未被更高优先级指令或精确唯一权威直接裁定的新旧需求矛盾，或会改变范围、语义、兼容、数据安全或方案的模糊点时，确认前不得实施受影响部分。

## 消费者

| 行为/契约 | producer | consumer | environment | 证据 | 未知项 |
|---|---|---|---|---|---|
| ... | ... | ... | local/staging/prod | ... | ... |

## 不可破坏约束

- INV-...: <约束>；来源：...；验证：...

## 兼容性矩阵

| 对象 | 旧状态存在 | 策略候选 | 迁移/弃用窗口 | 回滚 | 证据 |
|---|---|---|---|---|---|
| ... | yes/no/unknown | replace/migrate/dual-read/adapter/deprecate | ... | ... | ... |

## 影响与风险

| 影响面 | 直接/间接 | 风险 | 证据 | 缓解/测试 |
|---|---|---|---|---|
| code/data/API/security/performance/ops | ... | ... | ... | ... |

## 代码与运行数据分层

| path/object | layer/artifact_class | source_of_truth | edit/migrate/regenerate | data risk | evidence |
|---|---|---|---|---|---|
| ... | runtime-code/runtime-data/preprocess/test-fixture/generated | ... | ... | ... | ... |

## 方案比较

| 方案 | 收益 | 坏处/风险 | 复杂度增量 | 迁移/回滚 | 结论 |
|---|---|---|---|---|---|
| A 最小修复 | ... | ... | ... | ... | ... |
| B 结构调整 | ... | ... | ... | ... | ... |
| C 保持现状/延后 | ... | ... | ... | ... | ... |

## 测试案例、审核与回滚

| test_level | case/command | baseline | expected | post-change | evidence | review |
|---|---|---|---|---|---|---|
| unit | ... | ... | ... | pass/fail/not-run:<reason> | ... | ... |

每行只填一个 `test_level`：unit、component、contract、integration、e2e、migration 或 runtime；多级验证拆成多行。

- migration checks: ...
- code semantic review: <实施后核对代码、调用方、Schema、测试结果和运行证据的结论；与用户确认分开记录>
- rollback: ...
- production observation: ...
- untested_risk: <未执行项、原因和剩余风险>

## 未知项与问题

- <必须列出尚未被更高优先级指令或精确唯一权威直接裁定、且会改变范围、语义、兼容、数据安全或方案选择的新旧矛盾与模糊点，并在修改受影响部分前向用户/授权决策方提问>

## 建议

<推荐方案、理由、剩余风险和置信度。>

## 可复用原则候选（可选）

- principle: <从本次取舍抽象出的原则>
- applies_when: <适用范围>
- does_not_apply_when: <边界/反例>
- asymmetric_cost: <错判两侧代价>
- confidence: high/medium/low

候选原则不自动写入 agent memory、ADR 或现行制度。先核对至少一个适用实例、一个反例和错判代价，再由用户确认是否具有长期约束价值；确认后才晋升到 ADR 或 `logic_readme.md`。

## 文档影响

- root logic_readme: update/none + 原因
- key-rule decision link: update/none + RULE-ID 与 VER/ADR；只有 ordinary 规则才可填 none
- root logic_change: create/update/close/none + 原因
- immutable decision record: create/none + 原因；需要决策或 `history_retention: full` 的 CHG 必须创建完整记录，规则/用户可见行为的中等变更使用 `compact` 记录
- logic_version index: update/none + 原因
- logic_temp: create/update/clean/none + 路径与期限
- ADR: create/update/none + 原因
- AGENTS.md / .agents: update/create/none + 原因
- CLAUDE.md / .claude: update/create/none + 原因
```

完成 Brief 后，关键意图、兼容要求、消费者或新旧需求冲突无法确定且会改变方案时，必须暂停受影响部分并向用户/授权决策方询问；等待期间可以继续只读调查和不受该选择影响的独立工作。其余未知项作为风险记录并按用户授权继续。
