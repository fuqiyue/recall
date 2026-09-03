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
- last_updated: 2026-09-03
- active_changes: 1

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

| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |
|---|---|---|---|---|---|---|---|
| CHG-20260903-001 | verifying | SKILL.md; references/; scripts/recall.py; scripts/validate.py; logic_readme.md | self | 收尾归零：logic_temp 工作区产物台账 + status/validate 残留提示 | none | [CHG-20260903-001](logic_change.md#chg-20260903-001) | 2026-09-03 |

<a id="chg-20260903-001"></a>
## CHG-20260903-001: 收尾归零——logic_temp 工作区产物台账与残留文件提示

### 元数据

- status: verifying
- effective: false
- topic_id: none
- recall_route: high
- proposal_revision: 1
- decision_gate: required
- decision_state: confirmed
- confirmed_proposal_revision: 1
- decision_confirmed_by: self
- decision_ref: user-confirmed:2026-09-03（会话内二选一，选方案 B）
- decision_confirmed_at: 2026-09-03
- decision_record: required
- semantic_review_state: passed
- semantic_reviewed_by: self
- semantic_review_ref: 2026-09-03 `python -m unittest tests.test_recall_cli tests.test_git_sync tests.test_validate` 45 OK（新增 5 例）；`python tests/test_audit_logic_map.py` 69 OK；`audit --current-state` Static gate PASS（working/ 下带台账的 logic_temp 在场）；`validate` 无错误且对未跟踪记录文件给出 RULE-020 告警；`recall status` 单列 1 个待处置文件
- semantic_reviewed_at: 2026-09-03
- governance_execution_ref: none
- owner: self
- changed_by: Claude（Fable 5.1）
- proposer: 用户
- created: 2026-09-03
- last_status_change: 2026-09-03
- review_due: event-driven
- target_effective: 2026-09-03
- scope: SKILL.md; references/; scripts/recall.py; scripts/validate.py; logic_readme.md
- affected_scopes: .; references/
- related_modules: logic_readme.md#scope-mod-templates
- related_decisions: none
- authority_surfaces: RULE-020; SKILL:核心原则 12; CLI:recall status 输出; CLI:recall validate 告警; TEMPLATE:logic-temp-template.md
- based_on: policy: logic_readme.md RULE-011（未跟踪新文件默认排除）、RULE-014、RULE-019、INV-001; code: commit:4d82a5b; surfaces: RULE-020; SKILL:核心原则 12; CLI:recall status 输出; CLI:recall validate 告警; TEMPLATE:logic-temp-template.md
- depends_on: none
- conflicts_with: none
- conflict_resolution: none
- history_retention: full
- runtime_state: implemented-unmerged
- runtime_environments: none
- feature_flag: none
- blocked_by: none
- next_action: none
- unblock_condition: none
- reserved_version_id: VER-20260903-001
- version_slug: logic_version-20260903-001-cleanup-ledger
- temp_path: logic_version/working/logic_version-20260903-001-cleanup-ledger/logic_temp.md
- docs_impact: logic_readme update（新增 RULE-020、INT-20260903-001、FLOW-002#6、UXI-006、检查清单项、测试表、代码地图 recall.py/validate.py 职责）；SKILL update（核心原则 12、文档模型树、机器检查说明）；references update（logic-temp-template 台账表、change-lifecycle 晋升清单、logic-change-template temp 字段说明、logic-version-template logic_temp_cleanup 说明）；logic_version create VER-20260903-001

### 当前状态、代码逻辑与差距

- current_behavior: `logic_temp.md` 是可选的议案工作笔记（固定于 `logic_version/working/` 下按 version_slug 命名的目录，审计器对其位置有校验），记录事实/问题/受影响文件，没有"交付物 vs 非交付物、删还是留"的处置语义；`recall status` 与 `scripts/validate.py` 把已跟踪修改和未跟踪新文件合并报为"未提交变更"；RULE-011 使未跟踪文件不进自动保存提交，因而 AI 产生的探针脚本、临时测试与草稿既不上远端也不被提示，本地隐形累积。证据：references/logic-temp-template.md；scripts/recall.py `cmd_status`；scripts/validate.py 第 4 步；scripts/audit_logic_map.py `invalid-declared-temp-path`
- current_logic_fit: 可并入。logic_temp 的生命周期（议案结束即删、VER 填 `logic_temp_cleanup`）已闭环，只需加台账表并把 medium/high 从"可选"改"必建"；status/validate 都已调用 `git status --porcelain`，只需按 `??` 前缀分列；不新增根文档、不触碰 INV-001/002 与审计位置校验
- baseline_tests: 2026-09-03 `python -m unittest tests.test_recall_cli tests.test_git_sync tests.test_validate` 40 tests OK；`python tests/test_audit_logic_map.py` 69 tests OK；`python scripts/audit_logic_map.py . --current-state` 静态门通过；`python scripts/validate.py` 全部通过
- user_intent_gap: none（用户字面提议为"根目录新增专门 md"，与审计位置校验、INV-001/RULE-019 冲突；已列明方案 A/B 与影响，用户 2026-09-03 选 B）

### 拟议制度

RULE-020（key）：任务完成态 = 交付物就位 + 本次新建的非交付物（探针脚本、临时测试、草稿、调试输出）已删除或经用户同意保留 + 最终汇报列出处置清单。medium/high 通道必建 `logic_version/working/` 下以 version_slug 命名目录内的 `logic_temp.md`，在其"工作区产物台账"登记 path / artifact_kind / disposition / reason / cleaned_at；台账清零（无未执行的 delete、无 pending）方可关闭 CHG 并删除 working 目录。simple 通道不建文件，只在最终汇报列清单。`recall status` 把未跟踪文件单列为待处置候选，`recall validate` 对未被 .gitignore 覆盖的未跟踪文件给非阻断告警。工具不自动删除任何文件；处置由代理逐项执行并对用户可见。

### 意图来源与可审计提炼

- intent_source_refs: task:2026-09-03 会话（"做饭—洗碗"比喻；"可以多一个专门的 md 文件用于善后和收尾"）
- intent_digest: AI 解题过程留下的临时文件没有人负责清理；需要把"收尾"纳入任务完成的定义，并有一个专门载体记录产物去留，change 关闭时载体本身也归零
- intent_non_goals: 不新增根目录第三份现行文档；不做自动删除；不改 RULE-011 的未跟踪文件默认排除
- intent_constraints: INV-001/002（无平行真源）；RULE-019（语义正文只在规则行）；审计器对 logic_temp 位置的既有校验；UXI-003（自动化不动用户未提交的文件）
- intent_acceptance: 模板含台账表；SKILL 有收尾原则；logic_readme 有 RULE-020 与检查清单项；`recall status` 单列未跟踪文件；`recall validate` 对未忽略的未跟踪文件告警；新增单测通过；审计静态门与 validate 无新增错误
- intent_status: confirmed
- intent_distilled_by: agent
- intent_distilled_at: 2026-09-03
- intent_traceability: INT-20260903-001 -> RULE-020 -> test:tests/test_recall_cli.py#StatusLeftoverTests -> VER-20260903-001; INT-20260903-001 -> RULE-020 -> test:tests/test_validate.py#UntrackedLeftoverTests -> VER-20260903-001

### 需求拆解与融入分析（medium/high 必填；simple 不要求）

- raw_request: 2026-09-03 用户会话——"ai 应该是产生完工作任务，整理后才算结尾……可以多一个专门的 md 文件用于管理 logic_change.md……就像 logic_temp.md 这样专门用来善后和收尾……change 完成后要进入 logic_readme.md，确保档案的整洁"
- decomposition: ① logic-temp 模板增加"工作区产物台账"表并把 medium/high 改为必建；② SKILL 新增核心原则 12"收尾归零"（含 simple 通道的汇报清单替代）；③ change-lifecycle 晋升清单与 logic-change/logic-version 模板的 temp 字段补台账清零语义；④ `recall status` 分列已跟踪变更与未跟踪待处置文件；⑤ `recall validate` 对未被 .gitignore 覆盖的未跟踪文件非阻断告警；⑥ logic_readme 新增 RULE-020、INT-20260903-001、FLOW-002 第 6 步、UXI-006、检查清单项、测试表行；⑦ 固化 VER-20260903-001
- fit_analysis: 新增 INT-20260903-001（收尾归零），插入 FLOW-002 日常修改的第 6 步（sync 之后的收尾）；扩展 INT-20260816-006（status）与 INT-20260816-008（validate）的输出，不改其目标；新增 UXI-006（工具不静默删文件），与 UXI-003 同源；不触碰 UXI-001/002；不新增 FLOW

### 必要理由与来源

- 证据：user-confirmed（2026-09-03，高置信）；code（recall.py/validate.py 合并计数、audit 位置校验，高置信）；history（logic_temp 现有生命周期，高置信）
- why：任务"完成"的定义里缺少收尾，垃圾文件无人负责；RULE-011 保住远端却让本地残留隐形

### 决策检查点

- decision_needed_because: 用户字面提议新增根文档，会改变发布态文档模型、代理入口 `RECALL_ROOT_ORDER` 与审计位置校验，属于长期复杂度选择
- decision_question: 收尾台账放根目录（方案 A，新增第三份根文档）还是原位扩展 working/ 下的 logic_temp（方案 B）
- confirmation_request: 向用户确认 proposal_revision 1
- confirmation_result: confirmed——用户 2026-09-03 选方案 B

### 方案与决策

| 方案 | 收益 | 风险/坏处 | 复杂度增量 | 状态 |
|---|---|---|---|---|
| A 根目录新建 logic_temp.md | 显眼、与 readme/change 并列 | 撞审计位置校验与 INV-001/RULE-019；入口模板与所有消费项目需迁移；git 跟踪与"临时"定位矛盾 | 高 | rejected |
| B 原位扩展 working/ 下 logic_temp + 收尾原则 + status/validate 可见性 | 不新增根文档；复用既有清理生命周期；覆盖 simple 通道 | 载体在 gitignore 目录内、不如根文件显眼 | 低 | selected |
| C 保持现状 | 无改动 | 垃圾文件继续隐形累积 | 无 | rejected |

### 兼容、迁移与回滚

- 旧状态是否真实存在：yes——logic_temp 模板与 `logic_temp_cleanup` 字段已存在；无消费项目依赖 status/validate 的精确输出格式
- strategy: replace（模板与输出格式就地演进；字段名不变，RULE-009 校验不受影响）
- migration: none（既有 VER 记录的 `logic_temp_cleanup: none` 仍合法）
- rollback: git revert 本变更提交；纯文档 + 两个脚本的输出分支，无数据

### 测试案例与审核矩阵

| test_level | case | target/command | baseline | expected | post-change | evidence | reviewer/date |
|---|---|---|---|---|---|---|---|
| unit | status 分列已跟踪/未跟踪 | `python -m unittest tests.test_recall_cli` | not-run:新用例 | 新增用例通过，既有 13 项不回归 | pass（15 OK） | unittest 输出 2026-09-03 | self / 2026-09-03 |
| unit | validate 未跟踪残留告警 | `python -m unittest tests.test_validate` | not-run:新用例 | 有残留→warning，无残留→无告警 | pass（10 OK） | unittest 输出 2026-09-03 | self / 2026-09-03 |
| contract | 审计静态门与 validate 无新增错误 | `python scripts/audit_logic_map.py . --current-state`; `python scripts/validate.py` | pass | pass | pass | Static gate: PASS；validate 无错误 | self / 2026-09-03 |

### 开放问题与用户澄清

- questions_for_user: none

### 晋升与归档

- target_logic_sections: 当前制度（RULE-020）、代码地图（recall.py/validate.py 职责）、功能意图与用户流程（INT-20260903-001、FLOW-002#6、UXI-006）、测试与验证、有效决策索引、修改检查清单、当前限制
- version_record: logic_version/records/logic_version-20260903-001-cleanup-ledger.md
- close_condition: 代码语义审查通过、RULE-020 写入 logic_readme、VER-20260903-001 创建并登记索引后移除本条目
- temp_cleanup: 台账清零后由实施代理删除 logic_version/working/logic_version-20260903-001-cleanup-ledger/

---

**说明**：

当需要追踪修改时，在此文件中创建 CHG 条目。完成后：
1. 更新 `logic_readme.md`（如规则变化）
2. 归档到 `logic_version/records/`（如为高风险）
3. 把 CHG 的需求拆解三字段搬入 VER 记录后再删除 CHG 条目（需求保全与落选方案归档的语义见 logic_readme.md RULE-014；操作步骤见 references/change-lifecycle.md 第 7-9 步）

**记住**：logic_change.md 是临时的工作记录，不是长期真相源。
