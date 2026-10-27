# Recall 现行规则

先读本文件与根任务公报，再按目标路由领域。根只保留全局约束、用户意图和领域导航。
## 文档控制
- doc_id: LOGIC-RECALL-001
- module_id: MOD-ROOT
- scope: .
- scope_path: .
- parent: none
- parent_module_id: none
- membership: in-system
- scope_type: root
- layer: runtime-code
- module_doc_policy: paired
- status: active
- owner: self
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:https://github.com/fuqiyue/recall@main
- governance_verification: recorded
- governance_verified_at: 2026-08-08
- effective_from: 2026-08-07
- last_verified: 2026-10-27
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: logic_readme.md; 已登记领域的 logic_readme.md（SKILL.md 为操作入口）
- source_decisions: 见规则决策列；全量见 logic_version/index.md
- intent_summary: 从现行文档恢复设计逻辑；根必读、领域按需，历史仅留档
- intent_sources: 用户访谈 2026-08-07；用户确认 2026-09-03（一二级拆分法）
- decision_validity: valid
- validity_evidence: 用户确认 2026-08-07；2026-09-03
## 目标与边界
- 负责：记录项目设计决策的逻辑推理、关键取舍、影响分析；提供"为什么这么设计"的回忆能力
- 不负责：代码版本管理（由 Git 负责）、完整代码快照、原始对话记录、详细实现细节
- 上级制度：无
- 允许的例外：none
## 范围登记与归属
- canonical_readme: logic_readme.md
- canonical_change: logic_change.md
- owned_paths: SKILL.md, logic_readme.md, logic_change.md, logic_changes/, logic_domains/, logic_version/, references/, explainers/, scripts/, tests/, recall.bat, recall.sh, .gitattributes, AGENTS.md, CLAUDE.md, README.md
- child_policy: inherit
- data_owner: none
- registry_status: registered
## 当前制度
| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-001 | key | 逻辑回档而非代码回档 | 避免上下文膨胀，保持文档简洁可读 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | SKILL.md 章节 | valid | 2026-08-08 | self |
| RULE-002 | key | 现行 readme 只写完整的最新规则，增量合并受影响条款并删除废弃正文。 根索引保留全量 index 指针与最近 3 条；每条生效 VER 至少保留一处根索引或规则决策列链接，移出根索引前核反链。 | 保证局部更新后的现行制度完整且可追溯。 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | user:2026-10-26 | 文档模型/生命周期；validate | valid | 2026-10-27 | Codex |
| RULE-003 | key | 历史留档修改、必要理由/取舍、影响、验证与清理事实，不补充或覆盖现行规则。 仅任务明确要求时按 ID 读 VER/ADR；格式、链接和本次归档保全核验可读历史，但不据此恢复旧规则。 | 让现行文档足以指导修改，历史仅用于追溯。 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | user:2026-10-26 | SKILL.md；文档模型/VER模板；代理入口 | valid | 2026-10-27 | Codex |
| RULE-004 | ordinary | 三条通道分流修改 | 简单/中等/高风险，避免过度流程化 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 最佳实践 | SKILL.md | valid | 2026-08-08 | self |
| RULE-014 | key | 意图：INT/FLOW/UXI 只在根维护；INT 用 INT-YYYYMMDD-NNN，留来源和代码锚点。仅 user/user-confirmed 可驱动实施；inferred/code-derived 告警。已决定目标先登记，想法留待办。 需求：medium/high 实施前记 raw_request/decomposition/fit_analysis，归档原样搬入 VER。落选方案及理由随胜出记录；独立落选案建 rejected VER 并保全三字段。 计划：获准 Plan 按通道落盘再实施。personal 维护 INT、合并 FLOW、按需 UXI；协作全量。 | 把用户意图与需求拆解从会话保全到项目真源。 | [VER-20260816-001](logic_version/records/logic_version-20260816-001-feature-intent-layer.md)；[VER-20260831-002](logic_version/records/logic_version-20260831-002-arch-simplify.md) | 用户确认；历史依据见决策记录 | 本文件意图层; scripts/validate.py; 治理模式 | valid | 2026-10-27 | Codex |
| RULE-017 | key | 新会话或压缩后，从现行文档和活跃案接手，不要求用户重述背景。仅对用户明确提出的问题修改现行制度；歧义先按现行逻辑分析并建议，只询问真实未决点。 | 让文档完成交接，减少重复发现背景。 | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) | 用户确认；历史依据见决策记录 | SKILL.md 上下文读取入口 | valid | 2026-10-27 | Codex |
| RULE-018 | key | 根 readme 保存全局规则与意图；领域 readme 保存现行规则和代码地图，新领域 readme-only、旧 paired 兼容。 任务正文唯一位于 logic_changes/任务/logic_change.md，根 change 派生公报。route 按任务 ID/路径的 scope、affected_scopes 先找所属规则，相关任务先给摘要；关键词启发式匹配。 RULE/INT/CHG 全项目唯一；未登记规则仍属平行真源。密度见 RULE-022。 | 根保全局约束，领域按需控制阅读成本。 | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) | user:2026-10-26 | scripts/route_docs.py; recall_audit; tests/ | valid | 2026-10-27 | Codex |
| RULE-019 | key | 规则只在所属 readme 定义；SKILL、模板、生命周期和代理入口只放指针与步骤。Git 跟踪的顶层 Markdown 须登记 owned_paths 或 unmapped_paths，否则静态门失败。 | 防止入口、模板与现行制度各自漂移。 | [VER-20260816-005](logic_version/records/logic_version-20260816-005-audit-remediation.md)；[VER-20261027-001](logic_version/records/logic_version-20261027-001-public-docs-clarity.md) | 用户确认；历史依据见决策记录 | scripts/audit_logic_map.py 根目录覆盖对账 + tests/test_audit_logic_map.py | valid | 2026-10-27 | Codex |
### 按需领域入口
下表只导航，不重述领域规则；按相关路径、RULE 或 INT 运行 `recall route`。涉及多个职责时读取相应领域。
| 何时读取 | 现行规则位置 | 规则编号 |
|---|---|---|
| 接入、拆分、压缩文档，维护模板/解释展示 | [文档治理](logic_domains/document-governance/logic_readme.md) | RULE-016/022/026 |
| 建立、接手、修改、验证或关闭任务；路径、地图与产物清理 | [任务交付](logic_domains/task-workflow/logic_readme.md) | RULE-020/025/027/029 |
| 初始化 Git、提交、同步与追加提交证据 | [Git 管道](logic_domains/git-pipeline/logic_readme.md) | RULE-010/011/013 |
| 修改 CLI、解析、审计、验证器或测试 | [工具链](logic_domains/toolchain/logic_readme.md) | RULE-005..009、012、015、021、023、024、028 |
## 代码地图
| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| SKILL.md、logic_readme.md、logic_change.md | source/runtime-code | public | Recall 入口、宪法与议案账本 | AI/代理 | 当前规则与议案 | 各文件 | yes | validate/audit |
| logic_domains/ | source/runtime-code | public | 领域规则与可重建文件地图，旧领域账本兼容 | AI/代理 | 规则、文件索引与旧CHG | 各领域文件 | yes | route |
| logic_changes/ | source/runtime-code | public | 按任务集中计划、进度与产物台账 | 用户需求 | 唯一CHG正文 | 根公报与任务文件 | yes | tests/test_workspace.py |
| logic_version/ | source/runtime-code | persisted | 只追加变更留档与索引 | 查历史或核档 | 修改事实与必要理由 | records/index | records no | validate |
| references/、explainers/ | source/generated | internal | 模板/参考文档与可重建解释快照 | 文档/证据 | 模板/HTML | 各来源文档 | yes | browser/validate |
- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: 所有 Recall 文档为 source/runtime-code
- version_root: logic_version/
- temp_root: logic_version/working/
- workspace_root: .
- scratch_root: .work/
- data_roots: none
- unmapped_paths: agents/ (Codex 配置), .agents/ (代理私有目录), .claude/ (代理私有目录), logic_version/backups/ (历史记录引用的必要检查收据), .github/ (仓库社区配置), CONTRIBUTING.md (社区贡献指南、非真源), SECURITY.md (安全政策、非真源), acl-reports/ (运行时 ACL 审计输出、非 Recall 真源)

### 范围登记表
| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [logic_readme.md](logic_readme.md) | [logic_change.md](logic_change.md) | self | active |
| MOD-GIT-PIPELINE | logic_domains/git-pipeline | in-system | domain/runtime-code | paired | [git-pipeline](logic_domains/git-pipeline/logic_readme.md) | [changes](logic_domains/git-pipeline/logic_change.md) | self | active |
| MOD-TOOLCHAIN | logic_domains/toolchain | in-system | domain/runtime-code | paired | [toolchain](logic_domains/toolchain/logic_readme.md) | [changes](logic_domains/toolchain/logic_change.md) | self | active |
| MOD-DOCUMENT-GOVERNANCE | logic_domains/document-governance | in-system | domain/runtime-code | readme-only | [文档治理](logic_domains/document-governance/logic_readme.md) | none | self | active |
| MOD-TASK-WORKFLOW | logic_domains/task-workflow | in-system | domain/runtime-code | readme-only | [任务交付](logic_domains/task-workflow/logic_readme.md) | none | self | active |
## 功能意图与用户流程
本节唯一维护 INT/FLOW/UXI；来源和实施资格见 RULE-014，待办见任务交付 RULE-027。
### 功能意图登记
| intent_id | 功能入口 | intent（服务的用户目标） | 流程位置 | 关联规则 | 代码锚点 | 来源 | last_verified |
|---|---|---|---|---|---|---|---|
| INT-20260816-001 | logic_readme 功能意图与用户流程层 | AI 从文档恢复功能级产品逻辑与用户流程，无需重扫代码库 | FLOW-002#1 | RULE-014 | logic_readme.md | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-002 | recall init | 一条命令完成 Git + Recall 接入，无需手动配置 | FLOW-001#1 | RULE-010 | scripts/init_recall.py | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-003 | 文档阅读与路由 | 修改前恢复现行规则与相关议案；根必读、领域按需，历史仅按明确请求查阅 | FLOW-002#1 | RULE-001..004, RULE-018, RULE-022 | SKILL.md; references/document-model.md | user:2026-10-26 | 2026-10-26 |
| INT-20260816-004 | recall new | 在明确项目创建决策草稿，保留为什么改；缺项目标记不写入 | FLOW-002#3 | RULE-003, RULE-012 | scripts/create_ver.py | user:2026-10-12 本轮优化授权 | 2026-10-12 |
| INT-20260816-005 | recall sync | 一条命令保存并同步全部进度，无需手写 Git 序列 | FLOW-001#3, FLOW-002#5 | RULE-011, RULE-013 | scripts/git_sync.py | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-006 | recall next / index / status / list | 恢复当前任务、需求来源和剩余动作，区分想法、可做候选、待决策、阻塞与收尾；自动派生公报和状态 | FLOW-003#1 | RULE-018, RULE-021, RULE-027, RULE-028 | scripts/recall.py; scripts/task_context.py | user:2026-09-07 | 2026-09-07 |
| INT-20260816-007 | recall query file/commit/intent | 双向追溯：从代码定位"为什么改"，从功能意图定位"要改哪里" | FLOW-003#2 | RULE-013, RULE-014 | scripts/link_ver_git.py | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-008 | recall validate / recall audit | 确认宪法、领域文档、记录与 Git 状态一致；审计门按治理模式分档，一条命令可达 | FLOW-003#3 | RULE-009, RULE-015, RULE-018, RULE-023 | scripts/validate.py; scripts/recall_audit/integrity.py; scripts/recall.py | user-confirmed:2026-08-16 | 2026-09-06 |
| INT-20260816-009 | recall conflicts | 新需求与现行规则矛盾时提前暴露，交用户裁决 | FLOW-004#1 | RULE-021 | scripts/detect_conflicts.py | user-confirmed:2026-08-16 | 2026-09-03 |
| INT-20260816-010 | 项目接入流程（references/project-onboarding.md） | 存量/新项目模块化建立文档初稿：接入时建宪法骨架 + 至少一个领域，按触发时机逐模块补全 | FLOW-005#2 | RULE-016, RULE-018 | references/project-onboarding.md | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-011 | 根与领域拆分 | 根保留全局规则，按领域读取；增量下放完整规则并消除重复 | FLOW-005#4 | RULE-018 | references/logic-domain-template.md; scripts/recall_audit/integrity.py | user:2026-10-26 | 2026-10-26 |
| INT-20260903-001 | 收尾归零（任务内产物台账 + workspace 实物核对） | AI 沿用已有授权完成核验与清理，再报告任务结束，用户无需重复批准同范围收尾 | FLOW-002#4/6 | RULE-020, RULE-025 | references/logic-temp-template.md; scripts/recall.py; scripts/validate.py | user:2026-10-26 | 2026-10-26 |
| INT-20260903-002 | recall route | 按目标路径/关键词得到本次应读的文档清单与上下文成本，只导入命中的领域 | FLOW-002#1 | RULE-018 | scripts/route_docs.py | user:2026-09-03 | 2026-09-06 |
| INT-20260907-001 | AI 审查与关案 | AI 审查验证后自主交付，人工后测发现问题另开案 | FLOW-002#4 | RULE-025 | references/change-lifecycle.md | user:2026-09-07 | 2026-09-07 |
| INT-20260907-002 | explainers HTML | 需要解释文档时直接在项目 explainers 打开查看 | FLOW-003#4 | RULE-026 | references/explainers.md | user:2026-09-07 | 2026-09-07 |
| INT-20261020-001 | inventory / path / workspace / 任务文件 | 正确定位路径与规则、增量维护文件地图、合并相近任务并按轮清理；清理受限时保全已归档正文且持续提示欠账 | FLOW-002#1/2/4/6 | RULE-018, RULE-020, RULE-025, RULE-027, RULE-029 | scripts/workspace_cli.py; scripts/workspace_inventory.py; scripts/workspace_check.py; references/workspace-tasks.md | user:2026-10-25 | 2026-10-25 |
### 用户流程
- FLOW-001 首次接入：1. recall init → INT-20260816-002；2. 配置远端（可选）；3. recall sync → INT-20260816-005。
- FLOW-002 日常修改：1. 定位项目，读宪法/账本并 route → INT-20260816-001/003、INT-20260903-002；2. 判通道并记录必要 CHG/需求与验证计划；3. 按需 recall new 留决策骨架后实施 → INT-20260816-004；4. 审查验证后更新现行文档、清理、定稿VER/index、关案 → INT-20260907-001；5. commit/sync → INT-20260816-005；6. status 收尾 → INT-20260903-001。
- FLOW-003 追溯审查：1. next/status/list/index → INT-20260816-006；2. query → INT-20260816-007；3. validate/audit → INT-20260816-008；4. explainers → INT-20260907-002。
- FLOW-004 冲突澄清：1. conflicts → INT-20260816-009；2. 标注所属账本；3. 用户裁决后实施。
- FLOW-005 项目接入：1. recall init；2. 建宪法、领域与意图访谈 → INT-20260816-010；3. 按触发时机补全；4. 超限时拆域并登记 → INT-20260816-011。

### 操作直觉约束
- UXI-001: 用户不手写 commit message，sync 自动保存；来源：VER-20260811-003；影响：INT-20260816-005
- UXI-002: 一条命令完成一个用户目标，不要求用户记忆多步 Git 序列；来源：用户确认 2026-08-07；影响：INT-20260816-002, INT-20260816-005
- UXI-003: hook 与自动化绝不提交用户未提交的其他文件；自动保存只提交已跟踪文件的变更，未跟踪新文件默认排除并列出（`--include-new` 或 `git add` 才是用户的明确要求）；来源：VER-20260816-005；影响：INT-20260816-005
- UXI-004: 全部 CLI 在非交互与重定向环境可用；来源：VER-20260808-002；影响：全部 INT 条目
- UXI-005: 新会话默认延续：用户不需要重述项目哲学与背景，文档即交接；现行规则仅在用户明确否定时才修改；来源：VER-20260816-004；影响：INT-20260816-001, INT-20260816-003
- UXI-006: Recall检查命令只核对和报告；代理按RULE-020/025核验后沿用授权清理并汇报。台账及status候选不直接驱动删除；来源：user:2026-10-26；影响：INT-20260903-001, INT-20260816-006, INT-20260816-008
## 全局契约与验证
- INV-001/002：每个登记范围只有一份现行 readme，每项任务只有一份活跃正文，禁止平行真源。
- INV-003/004：VER 只追加（仅允许受管控 after_commit 回填），留档修改及必要理由、验证与清理事实，不保存代码快照。
- Markdown 表格、ID 与 JSON 输出兼容；迁移保留规则编号、来源、代码地图及 contract_class，旧 paired 兼容。字段不是权限控制，changed_by/decision_confirmed_by 记录实际责任。
- 验证入口：`python -m unittest discover -s tests`；`recall audit/validate/route/index/workspace`。具体契约与证据在所属领域；Git 提供代码回滚。

## 有效决策索引
| version_id | 决策摘要 | 关联规则 | 记录 |
|---|---|---|---|
| VER-20261026-001 | 现行规则独立完整、历史仅留档、增量更新与及时交接 | RULE-002, RULE-003, RULE-027 | [记录](logic_version/records/logic_version-20261026-001-current-policy-archive-boundary.md) |
| VER-20261026-002 | 根规则精简、领域归属与按需读取 | RULE-018 | [记录](logic_version/records/logic_version-20261026-002-root-domain-slim.md) |
| VER-20261026-005 | 授权覆盖必要收尾，代理核验后直接清理；平台审批按实际触发 | RULE-020, RULE-025 | [记录](logic_version/records/logic_version-20261026-005-authorization-through-closure.md) |
## 活跃议案入口
- [logic_change.md](logic_change.md) 派生全项目公报；任务正文见公报链接，接手用 `recall next`。
## 当前限制与交付检查
- 适用于个人/小团队；静态门不能证明语义、消费者或部署已验证，未测环境据实记录。密度与模板规则见文档治理，路由/审计限制见工具链。
- 修改前核用户意图、上游/下游契约与真实冲突；完成时核所属现行规则、范围/地图、必要验证、归档、公报与产物清理（任务交付 RULE-025）。
