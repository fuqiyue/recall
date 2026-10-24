# logic_change.md 模板

新任务正文放 `logic_changes/<任务>/logic_change.md`，根 `logic_change.md` 只维护派生公报（RULE-018）。同任务修改原文件，用一张修订表区分轮次和方案版本，不创建 `v2`、`final` 或重复交接正文。领域 readme 记录现行规则，任务用 scope/affected_scopes 关联；旧根/领域正文兼容，按任务迁移不复制。操作见[工作路径与任务](workspace-tasks.md)。

按需待办、下一步与根公报自动生成见 [任务上下文](task-context.md)（RULE-027/028）；普通个人任务保留需求与剩余动作，完整字段仅按实际需要使用。

目录：文档控制与索引；议案正文；决策确认、影响、兼容、测试与晋升。

## personal 最小块

先查活跃案，相同或接近需求能统一验收与收尾时合并原正文；确需新案再复制本块，填写实际值并运行 `recall index --write`。合并保留来源和原修订事实，方法见[工作路径与任务](workspace-tasks.md)。没有独立跟踪需求的 simple 修改直接执行。

- 机器必填：`status`、`effective: false`、`proposal_revision`、`recall_route`、`changed_by`；进入实施及之后再须真实的 `decision_confirmed_by` / `decision_confirmed_at`。账本已标 personal 时可省块内模式。
- 任务结构必留：唯一显式 `chg-id` 锚点、已登记的主scope、包含主scope的affected_scopes及根公报行；任务文件不再复制本地索引。
- 内容必留：目标、理由/当前证据、影响、方案/已有授权、验证与回滚、下一步及[修订记录](workspace-tasks.md#多轮修订)。`owner` / `scope` 用于索引对账。
- medium/high 必留三字段和正文内产物台账；修改现行规则才追加 `authority_surfaces`，按真实依赖/冲突追加协调字段。见 [字段词汇](field-vocabulary.md)。
- 未获授权保持 draft；已有授权直接填真实来源并进入 implementing，不重复确认。自审结论另写一行，正式字段仅按治理需要追加。

```markdown
<a id="chg-yyyymmdd-nnn"></a>
## CHG-YYYYMMDD-NNN: <标题>
- governance_mode: personal
- status: draft
- effective: false
- proposal_revision: 1
- recall_route: medium
- owner: self
- changed_by: Codex
- scope: .
- affected_scopes: .
- decision_confirmed_by: none
- decision_confirmed_at: none
- raw_request: <忠实转述或稳定来源>
- decomposition: <本次工作项>
- fit_analysis: <复用/修改哪个INT及FLOW位置>
- version_slug: logic_version-YYYYMMDD-NNN-<scope>
- task_temp_dirs: none
- current_result: <仅此处维护当前进展及阻塞；旧结果压入修订表>
- next_action: <下一项可执行动作>

### 目标与依据
<目标；理由和当前代码/测试/运行证据；受影响路径与消费者>
### 拟议制度
<最小方案与取舍；已有授权来源；未决选择写明>
### 验证与回滚
<验证命令和预期；必要结果与未验证环境；撤销本次增量的方法>
### 修订记录
| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
### 晋升与归档
<更新readme、清理；把需求与修订表搬入同一VER并核对，定稿/index就位后关闭CHG并核公报>
### 工作区产物台账
| path | artifact_kind | disposition | reason | cleaned_at | retention_basis | exit_condition | round |
|---|---|---|---|---|---|---|---|
```

## 账本骨架与扩展字段

以下保留根公报及旧账本完整 schema 供兼容；新任务使用上面的最小块，collaborative 或正式审查再追加必要字段，不复制另一份正文。

~~~markdown
# <项目名称> Active Changes

## 文档控制

- scope: .
- scope_path: .
- module_id: MOD-ROOT
- current_policy: logic_readme.md
- owner: <self/团队/角色>
- governance_mode: personal | collaborative
- governance_ref: <实际 Git/发布/PR/CI/审批控制的稳定引用；不写权限声明>
- governance_evidence: <控制证据；例如 branch-protection:<ref>;ci:<ref>;approval:<ref>;git:<ref>>
- governance_verification: verified | recorded | unavailable | not-applicable
- governance_verified_at: YYYY-MM-DD | none
- last_updated: YYYY-MM-DD
- active_changes: <本文件 CHG 正文数量；无正文填 none（0 同义）>

## 议案规则

- 先按治理模式选择字段：personal 使用下方最小块；collaborative / 正式审查按 [字段词汇](field-vocabulary.md) 追加必要字段。
- 创建位置、CHG 边界与公报按技能宪法 RULE-018；状态与晋升按 RULE-025 及 [生命周期](change-lifecycle.md)。所有活跃项写 `effective: false`。
- medium/high 在实施前填写 `raw_request` / `decomposition` / `fit_analysis`；归档原样搬入 VER（RULE-014）。已有明确授权记录其来源，不重复索取同一确认。
- 本条目的 scope、affected_scopes、proposal_path 与登记表对齐；需要 CHG 时先承接待办，再移除待办行（RULE-027）。
- 填写实际基线、消费者、确认、验证和剩余动作；字段不提供文件、Git、服务或外部系统权限。
- 关闭前更新所属 readme、固化所需 VER/index、清理本次工作区，再移除正文并核根公报（RULE-020/025）。

## 讨论主题索引

| topic_id | 同类议题/共享问题 | coordinator | discussion_refs | related_changes | status |
|---|---|---|---|---|---|
| TOPIC-YYYYMMDD-NNN | ... | ... | task/issue/spec refs | CHG-...; CHG-... / none | open | 

`related_changes` 只列当前文件中的活跃 CHG，使用 `CHG-ID` 列表或单独的 `none`，不可混写。主题可用 `none` 表示仍在收集讨论，随后再创建一个或多个 CHG；主题不应复制 CHG 的完整方案或把彼此独立的改动强制绑定。

## 活跃议案索引

| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |
|---|---|---|---|---|---|---|---|
| CHG-YYYYMMDD-NNN | draft | ... | ... | ... | none | [CHG-YYYYMMDD-NNN](logic_change.md#chg-yyyymmdd-nnn) | YYYY-MM-DD |

本文件的正文行 `proposal_path` 指向本文件内对应的 `#chg-id` 小写锚点，且锚点在文件内唯一。根账本的索引同时是全项目公报：任何领域账本中的每个活跃 CHG 也在此占一行，`proposal_path` 写 `[CHG-...](logic_domains/<domain>/logic_change.md#chg-...)`，正文不复制；`recall validate` 提示缺少公报行的领域 CHG。领域账本的索引只列本领域正文。跨范围协调在同一 CHG 正文的 `affected_scopes`、`related_modules` 和影响表中说明，不另建正文或回链文件。

字段口径和个人默认块见本文“personal 最小块”。扩展字段缺则按治理档位处理，填写后按实际值校验；不要把下方完整表单当成个人任务的默认必填清单。修改现行规则须写 `authority_surfaces`，同规则并行案须声明冲突关系，基线变化后重核。

普通修复准备引入 adapter、全局 feature flag、dual-read/dual-write、平行真源或新抽象时，不需要补齐整份正式表单，但必须设为 `decision_gate: required`，并记录真实消费者/旧状态证据、最小修复不足的原因、唯一权威源、复杂度增量、负责人、可验证移除触发器和最晚复查日期。缺少这些信息时保持候选，不直接实现临时结构。

<a id="chg-yyyymmdd-nnn"></a>
## CHG-YYYYMMDD-NNN: <议案标题>

### 元数据

- status: draft | awaiting-decision | implementing | verifying | promoting | blocked
- effective: false
- topic_id: TOPIC-YYYYMMDD-NNN | none
- recall_route: simple | medium | high
- proposal_revision: <正整数；实质方案变化时递增>
- decision_gate: required | not-required
- decision_state: pending | confirmed | not-required
- confirmed_proposal_revision: <正整数或 none>
- decision_confirmed_by: none | <用户/角色/稳定代号>
- decision_ref: none | <user-confirmed:YYYY-MM-DD/issue/会议/外部决定引用>
- decision_confirmed_at: YYYY-MM-DD | none
- decision_record: required | not-required
- semantic_review_state: pending | passed | failed | not-applicable
- semantic_reviewed_by: none | self | <实际审查人/代理>
- semantic_review_ref: none | <PR/commit/review/测试与运行证据引用>
- semantic_reviewed_at: YYYY-MM-DD | none
- governance_execution_ref: <本次变更的 pr:<ref>;ci:<run>;approval:<ref>；personal 可填 none>
- owner: <团队/角色>
- changed_by: self | <实际修改人/代理的简短信息>
- proposer: <用户/角色/issue>
- created: YYYY-MM-DD
- last_status_change: YYYY-MM-DD
- review_due: YYYY-MM-DD | event-driven
- target_effective: YYYY-MM-DD | event-driven | unknown
- scope: <路径、契约、Schema 或用户行为>
- affected_scopes: <全部根登记 scope_path；至少一个；不要用 . 代替实际受影响子范围；领域账本中必含自身 logic_domains/<domain> 且不得含 .>
- related_modules: <根 logic_readme.md 的范围/代码章节锚点>
- related_decisions: <ADR ID 或 none>
- authority_surfaces: <精确 RULE/API/DB/FLAG/行为 ID；用 ; 分隔；不能只写目录或 .>
- based_on: policy: <logic_readme.md 的规则/章节>; code: <commit/tree/release/snapshot 引用>; surfaces: <与 authority_surfaces 相同的精确 ID>
- depends_on: none | <CHG-ID@revision-N；多个用 ; 分隔；关闭后改为 VER/ADR/基线引用>
- conflicts_with: none | <CHG-ID 或精确 authority_surface；多个用 ; 分隔>
- conflict_resolution: none | unresolved | merge | supersede | sequence-and-revalidate
- history_retention: compact | full（旧none兼容读取；已有CHG关案至少保留精简VER）
- runtime_state: not-implemented | implemented-unmerged | merged-not-deployed | deployed-guarded
- runtime_environments: none | <实际 local/staging/prod/region；多个用 ; 分隔>
- feature_flag: none | <FLAG:<稳定ID>=state；仅实际部署受开关控制时填写>
- blocked_by: <具体 CHG-ID、外部事件或用户决定；非 blocked 填 none>
- blocked_reason: <阻塞原因及证据；无阻塞可省略>
- next_action: <具体剩余动作；任何阶段均可填写，阻塞时说明解除动作>
- unblock_condition: <解除阻塞的可验证条件；非 blocked 填 none>
- reserved_version_id: <VER-YYYYMMDD-NNN 或 none>
- version_slug: <logic_version-YYYYMMDD-NNN-<scope> 或 none>
- task_temp_dirs: <scratch_root/临时-具体功能；无则none，新任务台账内联>
- temp_path: <仅旧任务兼容logic_version/working/<version_slug>/logic_temp.md；新任务省略>
- docs_impact: <logic_readme 规则/代码地图/验证入口、logic_version/ADR 的 update/create/none + 原因>

### 当前状态、代码逻辑与差距

- current_behavior: <当前真实行为和证据>
- current_logic_fit: <现有架构能否正确并入；边界、依赖、数据流和原因>
- baseline_tests: <修改前测试命令、结果、日期和证据；未运行写原因>
- user_intent_gap: <会改变范围、语义、兼容、数据安全或方案选择的未决差距；有新旧需求矛盾时列明双方来源和具体冲突；没有填 none>

### 拟议制度

<若通过并验证，准备写入 logic_readme.md 的规则。使用可验收语言。>

### 意图来源与可审计提炼

- intent_source_refs: <稳定来源引用；例如 issue:#123；task:<稳定会话/任务引用>；plan:path；spec:path；steering:path；多个用 ; 分隔；不粘贴原文>
- intent_digest: <用一两句提炼要解决的问题与成功状态，不记录逐步思考>
- intent_non_goals: <明确不做什么；没有明确时填 not-specified>
- intent_constraints: <必须保留的业务、兼容、技术、发布或范围边界；没有明确时填 not-specified>
- intent_acceptance: <可验证的完成条件；没有明确时填 not-specified>
- intent_status: confirmed | source-derived | inferred | mixed
- intent_distilled_by: <self/agent/角色；只记录责任，不等于授权>
- intent_distilled_at: YYYY-MM-DD
- intent_traceability: <INT-YYYYMMDD-NNN -> RULE-... -> test:<path#anchor> -> VER-YYYYMMDD-NNN；多个链用 ; 分隔>

`confirmed` 表示用户或权威决策方确认了这份提炼；`source-derived` 表示可从稳定来源逐项追溯但尚未额外确认；`inferred` 表示模型推断；`mixed` 必须在 `intent_digest` 标明哪些内容来自来源、哪些仍是推断。来源更新或提炼发生实质变化时递增 `proposal_revision`，重新核对决策门槛。

### 需求拆解与融入分析（medium/high 必填；simple 不要求）

- raw_request: <用户原始请求的稳定引用或一句忠实转述；不粘贴长对话>
- decomposition: <拆解出的功能点/工作项；每项一行>
- fit_analysis: <对照根 logic_readme.md 的功能意图与用户流程：复用/替代/新增哪个 INT-*，插入哪条 FLOW-* 的哪一步，是否触碰 UXI-*；说不清位置时列入 user_intent_gap 并按RULE-014 澄清>

### 必要理由与来源

- 证据：<user-confirmed/code/test/runtime/history/inference + 来源与置信度>
- why：<为何提出，不写逐步思维过程>

### 决策检查点

- decision_needed_because: <decision_gate=required 时说明为什么不能由普通局部修复直接决定；包括未被直接裁定的新旧需求冲突或会改变方案的模糊点；not-required 时填 not-required>
- decision_question: <列出旧要求、最新要求、具体矛盾和选项后，请用户/决策方作出的明确选择；not-required 时填 not-required>
- confirmation_request: <向哪个用户/授权决策方确认哪个 proposal_revision；当前执行代理不能作为确认方；not-required 时填 not-required>
- confirmation_result: <confirmed 时写选项、确认来源和版本；pending 时写 pending；not-required 时填 not-required>

### 方案与决策

多轮记录沿用“personal 最小块”的一张修订表，关案搬入同一 VER；不再增加独立过程正文。

| 方案 | 收益 | 风险/坏处 | 复杂度增量 | 状态 |
|---|---|---|---|---|
| A 最小修改 | ... | ... | ... | candidate/selected/rejected |
| B 结构修改 | ... | ... | ... | candidate/selected/rejected |
| C 保持现状 | ... | ... | ... | candidate/selected/rejected |

用户或授权决策方确认前，所有涉及未决需求矛盾或关键模糊点的方案都保持 `candidate`。可以给出有依据的建议，但建议不等于选择。

### 消费者与影响

| 行为/契约 | artifact_layer | producer | consumer | environment | 影响 | 证据 |
|---|---|---|---|---|---|---|
| ... | runtime-code/runtime-config/runtime-data/preprocess/test-fixture/generated/dependency/external | ... | ... | local/staging/prod | ... | ... |

### 兼容、迁移与回滚

- V1/V2 对象：...
- affected_layers: <runtime-code/runtime-config/runtime-data/preprocess/test-fixture/generated/dependency/external>
- impact_surfaces: <frontend/backend/api/data/security/ops>
- 旧状态是否真实存在：yes | no | unknown + 证据
- strategy: replace | migrate | dual-read | dual-write | adapter | deprecate
- migration: <dry-run、幂等性、部分失败、前后计数>
- runtime_data_migration: <schema/seed/cache/rebuild/none；计数和敏感数据处理>
- backup: ...
- regeneration_or_restore: <生成、恢复及验证步骤>
- rollback: ...
- transitional_end: <结束条件、负责人、最晚复查日期>

### 测试案例与审核矩阵

| test_level | case | target/command | baseline | expected | post-change | evidence | reviewer/date |
|---|---|---|---|---|---|---|---|
| unit | ... | ... | pass/fail/not-run:<reason> | ... | pass/fail/not-run:<reason> | command/log/CI link + risk when not-run | role/name + YYYY-MM-DD |

每行只填一个 `test_level`：unit、component、contract、integration、e2e、migration 或 runtime；多级验证拆成多行。状态门槛：draft/awaiting-decision 可把 baseline 或 post-change 写成 `not-run:<原因>`，但测试计划、expected、责任人和日期必须明确；implementing 必须有 baseline 或明确的风险说明；verifying 不接受无理由的 not-run。风险豁免必须在 evidence 使用 `risk-accepted:<风险>; decision-ref:<用户确认/issue/PR>; compensation-owner:<补偿测试负责人>; due:YYYY-MM-DD`，日期未过期且四项都有实际值。

### 实施与验收门槛

- [ ] 修改前已记录当前代码逻辑、数据流、真实消费者和 baseline
- [ ] 已判断现有实现能否正确并入；如有未被直接裁定的新旧需求矛盾或会改变方案的模糊点，已列明来源、冲突、选项和影响，并取得用户/授权决策方答复
- [ ] 如 `decision_gate: required`，当前 `proposal_revision` 已被确认且确认来源已记录
- [ ] 代码/配置完成
- [ ] 适用的前端、后端、契约、迁移和运行时测试案例已生成或确认不适用
- [ ] post-change 测试结果已审核；未执行项已写原因和风险
- [ ] 已完成独立代码语义审查；失败项已回到议案或 blocked
- [ ] 数据迁移验证完成或不适用
- [ ] 真实消费者已验证
- [ ] 回滚路径已验证
- [ ] 当前制度、不可变决策记录、索引和临时文件清理同步完成
- [ ] `docs_impact` 已落实；若规则升级为 key，`logic_readme.md` 已链接对应 ADR/VER

### 开放问题与用户澄清

- questions_for_user: <必须列出尚未被更高优先级指令或精确唯一权威直接裁定、且会改变范围、语义、兼容、数据安全或方案的新旧矛盾与模糊点；写明选项和待确认问题；没有填 none>
- blocked 议案必须同时填写 `blocked_by`、`next_action`、`unblock_condition` 和 `review_due`，不得无限期悬挂。

### 晋升与归档

- target_logic_sections: <生效后更新所属 logic_readme.md（宪法或领域）的哪些章节>
- version_record: <logic_version/records/logic_version-...md；decision_record=required 时不得为 none>
- close_condition: <按 RULE-025，AI 语义审查和必要验证通过后主动晋升；当前制度与所需记录/索引就位即移除 CHG，不默认等待人工体验>
- temp_cleanup: <删除 working/<version_slug> 临时目录的负责人和条件；前提是 logic_temp 工作区产物台账已清零（RULE-020）>
~~~

状态和关闭规则：

- `draft`：正在形成议案版本；需要决策时 `decision_state: pending`。
- `awaiting-decision`：决策检查点已给出，等待用户或授权决策方确认当前 `proposal_revision`。
- `implementing`：只有 `decision_gate: not-required`，或确认版本与当前版本一致时才允许进入。
- `verifying`：AI 正在完成必要验证与语义审查，通过即执行晋升；缺陷继续修复，真实前置写明证据和解除动作。默认不等待真人体验（RULE-025）。
- `promoting`：按 change-lifecycle.md 清单连续完成文档晋升、历史归档与关闭，不是新的人工审批门。
- `blocked`：保留当前确认或待确认事实，并写清解除条件；不是无限期停车场。
- `effective`：仅作为已归档结论；活跃CHG仍为 `effective: false`。按[生命周期](change-lifecycle.md)步骤7–9更新现行制度、核对清理、定稿所需VER/index后移除条目。需求三字段、修订记录与最终意图保全，适用环境如实记录，已启用行为不得长期留在活跃账本。
- `rejected` / `cancelled`：不得进入当前制度；如果已进行决策检查点，也创建不可变记录保留最终方案与拒绝/取消原因，然后清理临时记录并移除。
- `rolled-back`：把当前制度恢复为实际状态，生成回滚记录，验证恢复路径，清理临时记录并移除。
- 无活跃议案时保留 `active_changes: none`（审计器把 `0` 视为同义）。
- 本文件随 Git 分支/worktree 版本化，不是跨分支实时锁；并行任务使用不同 CHG-ID，合并时按议案条目处理冲突，禁止整文件覆盖。它以低并发为前提：出现频繁并行写入、跨团队审核或强制权限时，先在外部 Issue/Spec/PR/变更系统协调，再回写主题与 CHG 的稳定引用。机器检查只能验证已声明的依赖、冲突、版本、治理引用和影响面，不能替代对真实消费者、运行数据、代码语义或外部权限控制的核对，也不能证明用户咨询确实发生或确认来源有权裁决。
