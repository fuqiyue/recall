# VER-20260816-001: 功能级"功能意图与用户流程"层与需求拆解字段

## 记录控制

- version_id: VER-20260816-001
- version_slug: logic_version-20260816-001-feature-intent-layer
- status: effective
- immutable: true
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: tests:test_audit_logic_map; audit:current-state
- governance_verification: recorded
- governance_verified_at: 2026-08-16
- date: 2026-08-16
- scope: 文档模型（logic_readme 新增功能意图与用户流程层、CHG 模板新增需求拆解字段、plan 模式落盘约定）
- affected_scopes: MOD-ROOT/., references/, MOD-TEMPLATES
- authority_surfaces: RULE-014, logic_readme.md#功能意图与用户流程, CHG 字段 raw_request/decomposition/fit_analysis
- based_on: policy: logic_readme.md#当前制度; code: commit:b8db894; surfaces: RULE-014
- changed_layers: runtime-code
- change_id: none
- topic_id: none
- topic_shared_context: none
- topic_shared_constraints: none
- topic_discussion_refs: none
- topic_final_conclusion: none
- changed_by: Claude (Fable 5)
- recall_route: medium
- history_retention: compact
- runtime_state: implemented-unmerged
- runtime_environments: local
- feature_flag: none
- proposal_commit_or_blob: none
- proposal_revision: none
- decision_record: not-required
- decision_state: not-required
- confirmed_proposal_revision: none
- decision_confirmed_by: user
- decision_ref: user-confirmed:2026-08-16（"目前你给的方案1和2和3是认可的"；"可以，请你帮我修改，目前补充功能级的粒度，要模块化处理"）
- decision_confirmed_at: 2026-08-16
- semantic_review_state: passed
- semantic_reviewed_by: self
- semantic_review_ref: tests:test_audit_logic_map.py + test_recall_cli + test_git_sync；audit:current-state PASS
- semantic_reviewed_at: 2026-08-16
- before_commit: b8db894
- after_commit: <pending-backfill>
- supersedes: none
- corrects: none

## 来源与意图提炼

- intent_source_refs: user-request:2026-08-15..16（本会话关于需求分析缺口的讨论）
- intent_digest: Recall 记录了系统逻辑（规则、代码地图）但缺"需求/产品逻辑"层：功能服务的用户目标、用户操作流程、操作直觉约束无处沉淀，AI 每会话从代码反推；需要功能级、模块化的记录层，并让需求拆解与融入分析的产出（含 plan 模式的计划）按通道落盘。
- intent_non_goals: 不引入强制的需求分析流程或表单（原则 7）；不为 simple 通道增加任何文书；需求拆解与融入分析仍由 AI 执行，文档只提供输入并留存产出。
- intent_constraints: 保持项目根唯一现行文档对（INV-001/002）；新层放在 logic_readme.md 内而非新建平行文件；INT-* 与 intent_traceability 共用编号空间；对接不依赖任何单一厂商 API，只依赖 CLAUDE.md/AGENTS.md 的读取路由。
- intent_acceptance: logic_readme 模板与本项目 logic_readme 均含 INT/FLOW/UXI 三类条目；CHG 模板含 raw_request/decomposition/fit_analysis；workflow-integration 含 plan 模式对接映射与时序；测试与静态审计通过。
- intent_status: confirmed
- intent_distilled_by: Claude (Fable 5)
- intent_distilled_at: 2026-08-16
- intent_traceability: INT-20260816-001 -> RULE-014 -> test:tests/test_audit_logic_map.py -> VER-20260816-001

## 为什么做这个决策？

Recall 的三层追溯中，代码层（Git）和架构决策层（logic_version）已覆盖，但需求/
产品层缺失：intent_summary 只有项目级一句话，"数据与控制流"画的是 AI 内部处理
流而非用户操作流，compliance 层的 INT-* 链是悬空引用。结果是"功能 ABCD 加入 E
是否融洽""操作顺序是否符合直觉"这类判断的输入不在任何文档里，AI（Claude/Codex）
每会话从代码有损反推，跨会话不一致；即使做出了好的融入分析，产出也随会话蒸发。

## 决策过程

**方案 A**：新建独立的 logic_product.md 承载产品逻辑——违反发布态只有一对现行
文档的 INV-001/002，制造平行真源。

**方案 B**：引入完整需求分析流程（每次请求强制拆解、用户故事、验收标准表单）——
与原则 7 直接矛盾，simple 通道被文书拖累。

**方案 C**：在 logic_readme.md 内增加模块化的"功能意图与用户流程"层（一个功能
一行 INT，一条流程一个 FLOW 块，一条直觉约束一行 UXI），CHG 模板为 medium/high
增加 raw_request/decomposition/fit_analysis 三字段留存分析产出，workflow-integration
定义 plan 模式"批准后、动代码前按通道落盘"的时序。

**选中方案与原因**：方案 C。分析能力留给模型，文档只做两件事——提供稳定输入
（INT/FLOW/UXI）和留存分析产出（CHG 三字段）；条目级模块化使新增功能 E 只需
增一行 INT、在 FLOW 插一步，不重写整节；与既有 intent_traceability 的 INT-*
编号空间贯通，未新增平行词汇体系。

## 影响范围

**修改的文件/模块**：
- `references/logic-readme-template.md` - 新增"功能意图与用户流程"节（INT/FLOW/UXI）
- `references/logic-change-template.md` - 新增"需求拆解与融入分析"节与议案规则条目
- `references/workflow-integration.md` - 新增"Plan 模式对接"映射表与时序约束
- `references/field-vocabulary.md` - 注明 INT-* 登记正文位置
- `SKILL.md` - 原则 5 补连贯性检查；上下文读取、文档模型、通道节补 plan 落盘约定
- `logic_readme.md` - 落地本项目 INT-001..008、FLOW-001..004、UXI-001..004，新增 RULE-014

**破坏性变更**：无。全部为文档模型的增量扩展；simple 通道行为不变。

## 验证方式

`python tests/test_audit_logic_map.py`；`python -m unittest tests.test_recall_cli tests.test_git_sync`；
`python scripts/audit_logic_map.py . --current-state` Static gate PASS；
提交本记录的 commit 带 Ref 行，hook 回填 after_commit。

## 回滚方式

`git revert` 本次提交即可整体回退（RULE-014 与新节一并移除）。只想停用融入分析
要求而保留记录层：把 RULE-014 降级为 ordinary 并在 CHG 模板将三字段标注为可选。

## 经验与教训

需求分析能力本身不可能写进文档；能制度化的只有分析的输入（功能意图、用户流程、
直觉约束）和产出（拆解与融入结论）。为已有悬空引用（INT-*）补登记正文，优于
发明新的平行 ID 体系。

## 关联

- current_logic: RULE-014
- proposal_id: none
- former_proposal_path: none
- immutable_record: VER-20260816-001
- decision_record_path: logic_version/records/logic_version-20260816-001-feature-intent-layer.md
- related_adr: none
- code/tests: references/logic-readme-template.md; references/logic-change-template.md; references/workflow-integration.md; SKILL.md; logic_readme.md
- issue/commit/release: before commit:b8db894
