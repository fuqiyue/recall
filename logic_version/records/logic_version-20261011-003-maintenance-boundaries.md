# VER-20261011-003: 修复 Recall 入口路径、审计边界与宪法密度
## 记录控制
- version_id: VER-20261011-003
- version_slug: logic_version-20261011-003-maintenance-boundaries
- status: effective
- immutable: true
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: user:2026-10-11 direct maintenance authorization
- governance_verification: recorded
- governance_verified_at: 2026-10-11
- date: 2026-10-11
- scope: ., scripts/recall_audit/report.py, D:/Codex/agents/skills/recall/SKILL.md
- affected_scopes: ., logic_domains/toolchain
- authority_surfaces: RULE-019, RULE-022, audit missing-map/runtime-data classification
- changed_layers: runtime-code/runtime-config/generated
- change_id: none
- changed_by: Codex
- recall_route: medium
- runtime_state: merged-not-deployed
- runtime_environments: local
- decision_record: not-required
- decision_state: not-required
- decision_confirmed_by: user
- decision_ref: user:2026-10-11 请帮我解决上述问题，但不要派发任务
- decision_confirmed_at: 2026-10-11
- semantic_review_state: passed
- semantic_reviewed_by: self
- semantic_review_ref: python -m unittest discover -s tests; recall audit --current-state; recall validate; recall route
- semantic_reviewed_at: 2026-10-11
- before_commit: 209dec2
- after_commit: 3980647
- supersedes: none
- corrects: none

## 为什么做这个决策？

本次用户授权要求直接解决前面列出的 Recall 入口、审计边界、运行数据和宪法密度问题；修复必须保持现行规则单一真源并可验证收尾。

## 来源与意图提炼
- intent_source_refs: user:2026-10-11 上述优化候选与直接修复授权
- intent_digest: 修正技能入口、消除审计边界误报、明确 acl-reports 运行数据边界、压缩根宪法并同步本地提交。
- intent_non_goals: 不创建子任务；不删除 acl-reports；不改变现行业务规则或已完成历史记录。
- intent_constraints: 根规则和领域规则保持唯一真源；历史 VER 只追加；未跟踪运行数据不纳入提交。
- intent_acceptance: recall next 为 0；audit 静态门通过且无 missing-map/runtime-data 候选；logic_readme 为 150 行；validate 无错误；全量测试通过。
- intent_status: confirmed
- intent_distilled_by: Codex
- intent_distilled_at: 2026-10-11
- intent_traceability: INT-20260816-008 -> RULE-019/RULE-022 -> test:tests/test_audit_logic_map.py -> VER-20261011-003

## 决策过程
方案 A：只在根文档追加目录说明，保留审计器误报；改动小但不能消除重复告警。
方案 B：让审计器读取根和领域声明的 owned_paths/unmapped_paths，压缩重复宪法说明，并把运行数据加入忽略边界；改动可验证且不建立平行真源。
选中方案与原因：选择方案 B。路径归属已经由现行文档声明，审计器应使用同一事实；根文档保留全局规则和入口，领域细节留在部门法。

## 影响范围
- D:/Codex/agents/skills/recall/SKILL.md：维护源从不存在的 F:/vscode3/recall 修正到 D:/vscode3/recall。
- scripts/recall_audit/report.py：missing-map/runtime-data 候选识别支持根和领域的显式边界及父目录。
- tests/test_audit_logic_map.py：增加 owned/unmapped 边界回归测试。
- logic_readme.md：根宪法压缩至 150 行，修复已关闭 CHG 陈旧引用，登记 acl-reports 运行数据边界。
- .gitignore：忽略本地 acl-reports/。
破坏性变更：否；审计候选的误报减少，未登记的新源码仍会被报告。

## 验证方式
- python -m unittest discover -s tests：274 tests，OK。
- recall audit --current-state：Static gate PASS，0 current-integrity issues，0 missing-map/runtime-data candidates，无 density notice。
- recall validate：无错误。
- recall next --json：items=[]，所有计数为 0。
- recall index：公报一致。
- recall route scripts/recall_audit/report.py：命中 MOD-TOOLCHAIN，读取链完整。

## 回滚方式
git revert 包含本记录的提交即可回滚代码和文档；如需恢复旧宪法，可从该提交的父版本恢复 logic_readme.md。acl-reports 文件仍在本地，不受提交回滚影响。

## 经验与教训
审计器必须复用逻辑文档已经声明的路径边界；根文档密度优化不能合并机器字段或 FLOW 步骤，否则会破坏 validate 的结构核对。

## 关联
- current_logic: logic_readme.md#RULE-019; logic_readme.md#RULE-022
- proposal_id: none
- code/tests: scripts/recall_audit/report.py; tests/test_audit_logic_map.py; logic_readme.md
