# logic_change.md 模板

每份 `logic_readme.md` 配一份 `logic_change.md`（RULE-018）：根账本承载修宪议案（改全局规则、INT 层、登记表行、INV 的 CHG）正文与全项目活跃议案索引；领域账本 `logic_domains/<domain>/logic_change.md` 承载本领域一事一议的 CHG 正文，精简形态见[领域文档模板](logic-domain-template.md)。本模板以根账本为例；用 `CHG-ID`、范围和状态区分事项，不创建 `v2`、`final` 或未登记的副本。本文不是当前制度的执行依据。

目录：文档控制与索引；议案正文；决策确认、影响、兼容、测试与晋升。

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
- active_changes: <本文件 CHG 正文数量或 none>

## 议案规则

- 本文件所有条目默认 `effective: false`；确认、实施和代码语义审查都不等于生效。
- 允许状态：draft | awaiting-decision | implementing | verifying | blocked。
- `CHG-ID` 的边界是可独立决策、验收、发布和回滚的最小工作项。两个改动若必须一起实施才能保持同一不变量，就合并为一个 CHG；只有可以独立关闭时才拆分为多个 CHG。
- `TOPIC-ID` 是同类讨论的容器，可集中多个 CHG 的来源、共享约束和开放问题；它不改变任何 CHG 的决策、发布或回滚边界。一个主题可暂时没有 CHG，多个 CHG 也可属于同一主题；每个活跃 CHG 最多填写一个 `topic_id`。主题最后一个相关 CHG 关闭时，必须把共享背景、约束、讨论来源和最终结论复制到该 CHG 的 `VER-*` 快照，避免主题从活跃文件移除后丢失理由。
- `recall_route` 标明本条目的分析深度：`simple` 通常不需要创建 CHG，只有用户要求追踪时使用；`medium` 先给出计划、影响范围和验证方式；`high` 必须显式检索消费者与相关历史、比较替代方案，并使用决策门槛。无法确定时升级通道。
- `proposal_revision` 是同一 CHG 的决策版本。拟议规则、选定方案、范围、影响、兼容/迁移、回滚或退出条件发生实质变化时递增它，并将 `decision_state` 重置为 `pending`，清空旧确认字段。
- 多个活跃 CHG 必须以 `authority_surfaces` 声明精确的规则、API、Schema、数据字段、开关或用户行为，例如 `RULE-021`、`API:/orders`、`DB:users.email`、`FLAG:checkout-v2`；目录或 `.` 只能用于 `affected_scopes`，不能代替影响面。相同影响面不表示一定冲突，但必须用双方互相引用的 `conflicts_with` 明确处理。
- `based_on` 固定本 CHG 所依据的现行制度、代码/快照和精确影响面，例如 `policy: logic_readme.md#rule-021; code: commit:abc123; surfaces: RULE-021`。晋升前重新核对它：任何依赖 CHG、同一影响面或现行规则已变更，都要递增 `proposal_revision`，重新确认或转为 `awaiting-decision`/`blocked`，不能带着旧基线继续生效。
- `raw_request`、`decomposition`、`fit_analysis` 构成需求拆解与融入分析：`medium`/`high` 通道在实施前填写，对照根 `logic_readme.md` 的功能意图与用户流程说明新功能复用/替代/新增哪个 `INT-*`、插入哪条 `FLOW-*` 的哪一步、是否触碰 `UXI-*`；`simple` 不要求。plan 模式产出的计划被批准后，其拆解结论在动代码前落入这三个字段，一次性 plan 本身不作为长期记录。
- 每个 CHG 记录 `intent_source_refs` 和可审计意图提炼。来源只保存稳定引用（任务、Issue、会话、Plan、Spec、Steering、ADR 或 VER），不复制原始聊天、完整提示词、模型记忆或推理过程。提炼须区分目标、非目标、约束、验收条件和仍会改变方案的问题；`inferred` 只表示待确认推断，不能冒充用户决定。
- 新请求与仍有效的旧需求、现行规则、活跃议案或已确认意图存在实质矛盾，或者模糊点会改变范围、语义、兼容、数据安全或方案选择时，必须在 `user_intent_gap`、`questions_for_user` 和适用的决策检查点中列明新旧来源、具体矛盾、可行选项、主要影响和建议，并向用户或授权决策方确认。确认前方案只能是 `candidate`，代理的建议不能标成 `selected`，也不得实施受影响部分。只有更高优先级当前指令或已声明的精确唯一权威已经直接裁定时才跳过询问，并记录裁定依据；可客观核实的事实问题先调查。这项咨询义务适用于所有通道，不自动要求把简单/中等事项升级为完整高风险表单。
- 活跃依赖必须写成 `CHG-...@revision-N`，不能只写 CHG-ID。被依赖 CHG 改版、阻塞或关闭后，依赖方不得继续实施；先阻塞/重新决策，关闭后将事实改写为对应 `VER-*`/ADR/现行规则基线，不保留悬空 CHG 依赖。循环依赖不是等待条件，必须合并、拆分或重排。
- `conflict_resolution` 只使用 `none`、`unresolved`、`merge`、`supersede` 或 `sequence-and-revalidate`。等待用户或授权决策方选择时使用 `unresolved`，并让受影响 CHG 保持 `blocked`，或在使用正式决策门槛时保持 `awaiting-decision`；`merge`、`supersede` 和 `sequence-and-revalidate` 只能记录已经确认的处理结果，不能由代理自行选定。顺序执行必须由后项用版本绑定依赖指向前项，并在前项关闭后重新核对基线。
- `effective: false` 表示尚未写入当前制度，不描述代码是否已合并或部署。用 `runtime_state`、`runtime_environments` 和 `feature_flag` 记录实际运行暴露；活跃 CHG 只允许未实现、未部署或已部署但未启用的状态。目标环境要启用新行为前或在同一受控发布中，先把最终规则晋升到 `logic_readme.md` 并创建所需 `VER-*`，随后关闭 CHG；`deployed-active` 只写入关闭后的版本记录。
- `history_retention` 由变更性质决定：`none` 仅用于内部且无制度影响的追踪；中等风险的规则或用户可见行为改动使用 `compact`；高风险/决策门槛改动使用 `full`。`compact` 也要在关闭前保留简短 `VER-*`，至少能恢复变更原因、影响面、基线、结果和回滚信息。
- `decision_gate: required` 只用于 `recall_route: high`：跨模块、公共契约、数据迁移、兼容性、安全边界，或 adapter、全局开关、双读写/双真源、新抽象等会改变长期复杂度的选择。先在“决策检查点”给出当前事实和 A/B/C 取舍，再由用户或授权决策方确认当前版本。简单/中等事项中的需求矛盾仍必须咨询，只是不因咨询本身自动获得完整高风险表单和历史记录。
- `decision_confirmed_by`、`decision_ref` 和 `decision_confirmed_at` 记录决策来源；它们不是 Git、文件、分支或部署权限。`decision_confirmed_by: self` 只能表示具备项目决策权的人明确作出选择，当前执行代理不能用它确认自己的建议。`owner` 记录协调责任，`changed_by` 记录实际修改人或代理。`governance_mode: personal` 允许 self 审查但必须保留外部治理引用；`collaborative` 的高风险通过性审查必须由非实施者完成，并由 `governance_ref` 指向真实 PR/CI/保护或审批控制，同时在本次 CHG 的 `governance_execution_ref` 填写实际 PR/CI/审批引用。`governance_evidence` 是责任人核验外部控制的证据，不是 Recall 自己证明权限生效。
- `semantic_review_*` 只记录实施后的代码语义审查。它必须独立核对当前代码、调用方、Schema、测试结果和运行证据，不能由用户确认、测试文件存在或静态审计代替。
- `decision_gate: required` 的 CHG 必须在生效后创建不可变版本记录，保存最终议案快照、确认、实现、审查、验证和回滚信息；不能因关闭条目而丢失决策逻辑。
- `logic_change.md` 只承担活跃变更的决策正文。高风险 CHG 在关闭前先创建 `VER-*`，必要时创建 ADR；随后由 `logic_readme.md` 的生效关键规则链接该记录，不能把活跃 CHG 当作长期引用目标。
- 旧的 `approved`、`reviewed_by`/`review_ref` 和 `AUTH-*` 字段直接迁移到当前真实阶段的 `decision_*` 与 `semantic_review_*` 字段；不保留兼容字段、双状态或平行版本文件。
- 同一 CHG-ID 的正文只能存在一处（所属账本）：触及宪法内容的立在根账本，领域事项立在该领域账本，跨领域正文放主领域、其余领域列入 `affected_scopes`。`affected_scopes` 列出全部受影响根登记 scope_path；领域账本中的 CHG 必含自身领域 scope_path 且不得含 `.`。
- 本文件不提供实际权限控制；真实权限由 Git、CODEOWNERS、分支保护或外部系统承担。它适合单人或低并发小团队；频繁并行编辑、跨团队排队或组织级审批应转交 Issue、Spec、PR 或变更系统，CHG 只保留提炼和稳定引用。

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

普通追踪至少保留索引，以及正文中的 `status`、`effective`、`topic_id`、`proposal_revision`、决策门槛/状态、`owner`、`changed_by`、`scope`、`affected_scopes`、`intent_source_refs`、`intent_digest`、`intent_status`、`authority_surfaces`、`based_on`、依赖/冲突、运行暴露、历史保留级别、当前证据、拟议规则、验证/验收、回滚和开放问题；`medium`/`high` 条目另须保留 `raw_request`、`decomposition`、`fit_analysis`。下面的完整字段与矩阵只在用户明确要求正式审查或表单合规时全部填写。

`governance_mode: personal` 的最小块（RULE-023，目标 15-40 行）：元数据只需 `status`、`effective: false`、`proposal_revision`、`recall_route`、`owner`、`changed_by`、`scope`，实施前补 `decision_confirmed_by` + `decision_confirmed_at`（`high` 建议再写 `decision_ref`）；正文保留目标、理由与当前证据、影响范围、`medium`/`high` 三字段、方案与决策、回滚、晋升目标。其余字段写了就会被审计器按完整规则校验（缺则不查、写则照查），见 references/field-vocabulary.md。

普通修复准备引入 adapter、全局 feature flag、dual-read/dual-write、平行真源或新抽象时，不需要补齐整份正式表单，但必须设为 `decision_gate: required`，并记录真实消费者/旧状态证据、最小修复不足的原因、唯一权威源、复杂度增量、负责人、可验证移除触发器和最晚复查日期。缺少这些信息时保持候选，不直接实现临时结构。

<a id="chg-yyyymmdd-nnn"></a>
## CHG-YYYYMMDD-NNN: <议案标题>

### 元数据

- status: draft | awaiting-decision | implementing | verifying | blocked
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
- history_retention: none | compact | full
- runtime_state: not-implemented | implemented-unmerged | merged-not-deployed | deployed-guarded
- runtime_environments: none | <实际 local/staging/prod/region；多个用 ; 分隔>
- feature_flag: none | <FLAG:<稳定ID>=state；仅实际部署受开关控制时填写>
- blocked_by: <具体 CHG-ID、外部事件或用户决定；非 blocked 填 none>
- next_action: <下一步和负责人；非 blocked 填 none>
- unblock_condition: <解除阻塞的可验证条件；非 blocked 填 none>
- reserved_version_id: <VER-YYYYMMDD-NNN 或 none>
- version_slug: <logic_version-YYYYMMDD-NNN-<scope> 或 none>
- temp_path: <logic_version/working/<version_slug>/logic_temp.md；medium/high 必填（RULE-020 收尾台账），simple 填 none>
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
- fit_analysis: <对照根 logic_readme.md 的功能意图与用户流程：复用/替代/新增哪个 INT-*，插入哪条 FLOW-* 的哪一步，是否触碰 UXI-*；说不清位置时列入 user_intent_gap 并按核心原则 5 澄清>

### 必要理由与来源

- 证据：<user-confirmed/code/test/runtime/history/inference + 来源与置信度>
- why：<为何提出，不写逐步思维过程>

### 决策检查点

- decision_needed_because: <decision_gate=required 时说明为什么不能由普通局部修复直接决定；包括未被直接裁定的新旧需求冲突或会改变方案的模糊点；not-required 时填 not-required>
- decision_question: <列出旧要求、最新要求、具体矛盾和选项后，请用户/决策方作出的明确选择；not-required 时填 not-required>
- confirmation_request: <向哪个用户/授权决策方确认哪个 proposal_revision；当前执行代理不能作为确认方；not-required 时填 not-required>
- confirmation_result: <confirmed 时写选项、确认来源和版本；pending 时写 pending；not-required 时填 not-required>

### 方案与决策

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
- close_condition: <代码语义审查通过、当前制度已更新、不可变记录和索引已创建后移除本 CHG 正文；不得把单个 CHG 置为 none>
- temp_cleanup: <删除 working/<version_slug> 临时目录的负责人和条件；前提是 logic_temp 工作区产物台账已清零（RULE-020）>
~~~

状态和关闭规则：

- `draft`：正在形成议案版本；需要决策时 `decision_state: pending`。
- `awaiting-decision`：决策检查点已给出，等待用户或授权决策方确认当前 `proposal_revision`。
- `implementing`：只有 `decision_gate: not-required`，或确认版本与当前版本一致时才允许进入。
- `verifying`：实施后正在核对测试、运行证据和代码语义审查；语义审查未通过不得生效。
- `blocked`：保留当前确认或待确认事实，并写清解除条件；不是无限期停车场。
- `effective`：先重新核对 `based_on`、版本绑定依赖、冲突处理和实际运行暴露，再完成代码语义审查和验收；对 `history_retention: compact` 或 `full` 的 CHG，先创建相应 `VER-*`，把 `intent_source_refs` 与可审计意图提炼原样固化；对高风险/`decision_record: required` 再保留完整决策快照、必要时 ADR 并更新索引，再更新根 `logic_readme.md` 的受影响章节和关键规则链接。目标环境启用时，现行制度和关闭记录必须同一受控发布变更完成；`deployed-active` 不得留在活跃 CHG；最后清理 `logic_temp` 并移除条目。
- `rejected` / `cancelled`：不得进入当前制度；如果已进行决策检查点，也创建不可变记录保留最终方案与拒绝/取消原因，然后清理临时记录并移除。
- `rolled-back`：把当前制度恢复为实际状态，生成回滚记录，验证恢复路径，清理临时记录并移除。
- 无活跃议案时保留 `active_changes: none`。
- 本文件随 Git 分支/worktree 版本化，不是跨分支实时锁；并行任务使用不同 CHG-ID，合并时按议案条目处理冲突，禁止整文件覆盖。它以低并发为前提：出现频繁并行写入、跨团队审核或强制权限时，先在外部 Issue/Spec/PR/变更系统协调，再回写主题与 CHG 的稳定引用。机器检查只能验证已声明的依赖、冲突、版本、治理引用和影响面，不能替代对真实消费者、运行数据、代码语义或外部权限控制的核对，也不能证明用户咨询确实发生或确认来源有权裁决。
