# Recall Skill Logic：宪法（一级 readme，RULE-018）：全局规则、功能意图与用户流程、领域目录。每个任务必读；领域规则在 `logic_domains/`（部门法），用 `recall route 目标路径` 按需导入。
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
- last_verified: 2026-10-25
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: logic_readme.md; 已登记领域的 logic_readme.md（SKILL.md 为操作入口）
- source_decisions: 全量见 logic_version/index.md（RULE-002 ②，不在此重复）；最近生效 VER-20261020-002, VER-20261024-001, VER-20261025-001
- intent_summary: 为 AI 提供项目设计逻辑的回忆机制，记录"为什么这么设计"而非代码快照，避免上下文膨胀；宪法必读、部门法按需导入
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
| RULE-002 | key | ①现行readme只留最新规则，删除废弃正文；②根有效决策索引只留全量index指针和最近3条；③每条生效VER须在根索引或所属规则决策列保留链接，移出滚动索引前核规则反链。 | 保留唯一现行制度和可追溯历史入口。 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md)；[VER-20260904-002](logic_version/records/logic_version-20260904-002-docs-consolidation.md) | 用户确认；历史依据见决策记录 | scripts/validate.py; tests/test_validate.py | valid | 2026-09-04 | self |
| RULE-003 | key | 历史记录保存设计逻辑 | 记录为什么、取舍、影响，不记录代码快照 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | logic_version/ | valid | 2026-08-08 | self |
| RULE-004 | ordinary | 三条通道分流修改 | 简单/中等/高风险，避免过度流程化 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 最佳实践 | SKILL.md | valid | 2026-08-08 | self |
| RULE-014 | key | ①INT/FLOW/UXI只在根维护，INT用 `INT-YYYYMMDD-NNN`，登记来源和代码锚点；②仅user/user-confirmed意图可驱动实施，inferred/code-derived告警，已决定新目标先登记，想法留待办；③medium/high实施前记raw_request/decomposition/fit_analysis，归档原样搬入VER；落选方案及理由随胜出记录，独立落选案建rejected VER并搬三字段；④获准Plan按通道落盘后实施；⑤personal维护INT、合并FLOW、按需UXI，协作全量。 | 把用户意图与需求拆解从会话保全到项目真源。 | [VER-20260816-001](logic_version/records/logic_version-20260816-001-feature-intent-layer.md)；[VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md)；[VER-20260831-002](logic_version/records/logic_version-20260831-002-arch-simplify.md)；[VER-20260904-001](logic_version/records/logic_version-20260904-001-intent-provenance-conflicts.md) | 用户确认；历史依据见决策记录 | 本文件意图层; scripts/validate.py; 治理模式 | valid | 2026-09-04 | self |
| RULE-016 | key | 接入先建根骨架、范围登记、至少一个领域和INT/FLOW访谈初稿；存量模块标pending-docs，仅在新项目开始使用或用户单独要求时渐进补全；扫描意图标code-derived，经用户确认才落为实施依据。 | 避免全库扫描和未经确认的推断污染意图。 | [VER-20260816-003](logic_version/records/logic_version-20260816-003-semantic-link.md)；[VER-20260903-004](logic_version/records/logic_version-20260903-004-two-level-docs.md) | 用户确认；历史依据见决策记录 | references/project-onboarding.md + SKILL.md 接入章节 | valid | 2026-09-04 | self |
| RULE-017 | key | 新会话或压缩后从现行文档与活跃案接手，不要求用户重述背景；仅在用户明确指出问题时修改现行制度；歧义先按现行逻辑分析并建议，再咨询真实未决点。 | 让文档完成交接，减少重复发现背景。 | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) | 用户确认；历史依据见决策记录 | SKILL.md 上下文读取入口 | valid | 2026-08-16 | self |
| RULE-018 | key | ①根readme保全局规则与意图，领域readme保现行规则/代码地图，新领域readme-only、旧paired兼容。②根change派生任务公报，logic_changes/任务/logic_change.md为唯一正文。③route先用任务ID/路径解析scope与affected_scopes找所属规则，其他相关任务先给摘要链接；关键词仍启发式。④RULE/INT/CHG全项目唯一，未登记规则仍属平行真源；密度门见RULE-022。 | 根保全局约束，领域按需控制阅读成本。 | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md)；[VER-20260903-004](logic_version/records/logic_version-20260903-004-two-level-docs.md)；[VER-20260904-002](logic_version/records/logic_version-20260904-002-docs-consolidation.md)；[VER-20260904-005](logic_version/records/logic_version-20260904-005-density-gate.md)；[VER-20260906-001](logic_version/records/logic_version-20260906-001-constitution-slim-alignment.md)；[VER-20261020-001](logic_version/records/logic_version-20261020-001-workspace-task-governance.md)；[VER-20261024-001](logic_version/records/logic_version-20261024-001-task-context-workspace.md) | user:2026-10-24 | scripts/route_docs.py; recall_audit; tests/ | valid | 2026-10-24 | Codex |
| RULE-019 | key | 规则语义只在所属readme规则行；SKILL、模板、生命周期及代理入口只放规则指针与操作步骤；Git跟踪的顶层Markdown入口须在owned_paths或unmapped_paths登记，否则静态门失败。 | 防止入口、模板与现行制度各自漂移。 | [VER-20260816-005](logic_version/records/logic_version-20260816-005-audit-remediation.md)；[VER-20261011-003](logic_version/records/logic_version-20261011-003-maintenance-boundaries.md) | 用户确认；历史依据见决策记录 | scripts/audit_logic_map.py 根目录覆盖对账 + tests/test_audit_logic_map.py | valid | 2026-09-04 | self |
| RULE-020 | key | ①每轮处置本轮产物，任务完成后删除临时代码/输出/空目录，gitignore不算清理。②正文台账区分临时物、deliverable/runtime-data/evidence；keep写retention_basis与exit_condition，round标轮次，旧五列兼容。③临时物进独占scratch_root/临时-具体功能，复用代码和必要证据先晋升，跨轮保留须有依赖及退出条件。④workspace核实物，按任务/轮次分列结果与全局遗留；共享问题归属双方，关案无pending/delete残留，数量不授权删除。⑤simple最终汇报；旧用户文件先核归属引用，工具不自动删除。 ⑥仅已完整归档且无其余未完事项的独立任务正文，删除受阻时可在执行策略允许下原字节移动至logic_version/pending_cleanup/CHG-ID/logic_change.md.txt，既有index集中记来源/归档/指纹/退出条件；移动不算删除，workspace持续提示并核实物，不适用于业务数据或整目录。 | 把临时产物处置纳入完成条件。 | [VER-20260903-001](logic_version/records/logic_version-20260903-001-cleanup-ledger.md); cleanup corrections: [VER-20261011-001](logic_version/records/logic_version-20261011-001-cleanup-ai-delivery-closure.md), [VER-20261011-002](logic_version/records/logic_version-20261011-002-cleanup-html-explainers.md)；[VER-20261020-001](logic_version/records/logic_version-20261020-001-workspace-task-governance.md)；[VER-20261024-001](logic_version/records/logic_version-20261024-001-task-context-workspace.md)；[VER-20261025-001](logic_version/records/logic_version-20261025-001-pending-cleanup.md) | user:2026-10-25 | 临时台账; status/validate; tests/ | valid | 2026-10-25 | Codex |
| RULE-022 | key | ①SKILL只保留关键入口、需求记录、三通道、边界、命令和按需参考，细节唯一存references；②审计器结构/函数长度属RULE-024；③Density的行数目标、单CHG>80与blocked积累仅提示，文档硬限/无领域进门，advisory-only只改退出码；根及登记领域token成本目标也仅提示，数值见字段词汇；④规则分子条款、why留一句，事故叙事归VER。 | 控制必读成本，保持规则可引用。 | [VER-20260831-001](logic_version/records/logic_version-20260831-001-entry-slim-skill-front.md)；[VER-20260903-002](logic_version/records/logic_version-20260903-002-structure-context-cost.md)；[VER-20260903-003](logic_version/records/logic_version-20260903-003-structural-closure.md)；[VER-20260904-002](logic_version/records/logic_version-20260904-002-docs-consolidation.md)；[VER-20260904-005](logic_version/records/logic_version-20260904-005-density-gate.md)；[VER-20260906-001](logic_version/records/logic_version-20260906-001-constitution-slim-alignment.md)；[VER-20261011-003](logic_version/records/logic_version-20261011-003-maintenance-boundaries.md)；[VER-20261012-001](logic_version/records/logic_version-20261012-001-skill-document-clarity.md)；[VER-20261012-002](logic_version/records/logic_version-20261012-002-six-improvements.md)；[VER-20261013-001](logic_version/records/logic_version-20261013-001-reliable-context.md) | 用户确认；历史依据见决策记录 | SKILL.md; 文档模型; recall_audit | valid | 2026-10-13 | Codex |
| RULE-025 | key | ①personal由AI实施、自审和必要验证，独立记录结论/证据。②无未决设计/实质阻塞后主动更新readme→清理核实→将CHG需求、简短修订表及结论搬入同一VER，核轮次/最终版本/结果与索引→定稿关案；含取消/否决，不逐轮建档；早建VER为关联草稿，定稿后不改语义。③环境限制写实，反馈另开案；无CHG的simple照通道。④仅真实缺口或明确授权/外部前置可阻塞，授权沿用，人工验收须明确要求。⑤依赖关闭后重核并绑VER/规则，已启用行为不长期挂活跃案。 ⑥上述保全移动核对完成可退出业务活跃队列，清理另列；移动也受阻时只在历史index记原位待清理；唯一登记/归档/身份/SHA核验通过后退出活跃发现，源字节变化则恢复发现并报错。禁止清空正文或换工具绕过拒绝。 | 完成可验证交付并保全必要修订历史。 | [VER-20260907-001](logic_version/records/logic_version-20260907-001-ai-delivery-closure.md)；[VER-20261012-002](logic_version/records/logic_version-20261012-002-six-improvements.md)；[VER-20261013-001](logic_version/records/logic_version-20261013-001-reliable-context.md)；[VER-20261020-002](logic_version/records/logic_version-20261020-002-task-revision-history.md)；[VER-20261025-001](logic_version/records/logic_version-20261025-001-pending-cleanup.md) | user:2026-10-25 | 生命周期; CHG/VER模板; 本轮归档核对 | valid | 2026-10-25 | Codex |
| RULE-026 | ordinary | 持久流程/架构/方案/状态说明用项目explainers HTML，简单问答不建页，用户格式优先；标日期、来源与已核/未核边界，相关页优先更新，日期快照另标；计数按声明账本重算；登记可重建交付物，不能成为平行制度或唯一决策位置。 | 提供可读展示并保持制度唯一。 | [VER-20260907-002](logic_version/records/logic_version-20260907-002-html-explainers.md) | user:2026-09-07 | references/explainers.md 与 explainers/ 实际产物 | valid | 2026-09-07 | Codex |
| RULE-027 | key | ①根change可选idea/planned待办，留来源/约束/完成条件，启动后移除。②相同或接近需求能统一目标/验收/收尾时合并原CHG；独立发布/回滚或授权冲突才分案。并案保留原ID来源、需求与修订事实并更新引用。③顶部唯一status/current_result/next_action，旧计划收敛修订表，不另造过程正文。表记轮次/日期/版本/原因/文件/结果，失败事实保留；轮次按有效节点递增，proposal_revision仅实质方案/影响面/基线改变时增加，归档见RULE-025。④阻塞记解除动作/责任/复查，next/status不授权或调度。 | 保存可靠上下文和修订过程，减少双写。 | [VER-20260907-003](logic_version/records/logic_version-20260907-003-task-context.md)；[VER-20261020-001](logic_version/records/logic_version-20261020-001-workspace-task-governance.md)；[VER-20261020-002](logic_version/records/logic_version-20261020-002-task-revision-history.md)；[VER-20261024-001](logic_version/records/logic_version-20261024-001-task-context-workspace.md) | user:2026-10-24 | scripts/task_context.py + tests/test_task_context.py；CHG/VER模板 | valid | 2026-10-24 | Codex |
| RULE-029 | key | ①用户指定文件夹为根（workspace_root为.），输出只拼一次根相对路径，执行显式cwd，写前核越界/盘符/链接/重复根。②声明scratch_root/data_roots，功能目录由owned_paths认领；inventory有界盘点名称/类型/归属，数据仅列上层。③地图在同一文件保存逐目录覆盖/时间/预算/边界；局部更新仅替换完整列举范围，截断或未重扫条目保留旧时间，确认目录消失才移除旧子树索引。④地图可重建非规则真源，不自动搬删；临时退出见RULE-020。 | 让真实目录可发现，避免路径嵌套和过程文件失控。 | [VER-20261020-001](logic_version/records/logic_version-20261020-001-workspace-task-governance.md)；[VER-20261024-001](logic_version/records/logic_version-20261024-001-task-context-workspace.md) | user:2026-10-24 | tests/test_workspace.py | valid | 2026-10-24 | Codex |
领域规则：Git 管道 RULE-010/011/013 见 [MOD-GIT-PIPELINE](logic_domains/git-pipeline/logic_readme.md)；工具链 RULE-005..009、012、015、021、023、024、028 见 [MOD-TOOLCHAIN](logic_domains/toolchain/logic_readme.md)。
## 代码地图
| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| SKILL.md、logic_readme.md、logic_change.md | source/runtime-code | public | Recall 入口、宪法与议案账本 | AI/代理 | 当前规则与议案 | 各文件 | yes | validate/audit |
| logic_domains/ | source/runtime-code | public | 领域规则与可重建文件地图，旧领域账本兼容 | AI/代理 | 规则、文件索引与旧CHG | 各领域文件 | yes | route |
| logic_changes/ | source/runtime-code | public | 按任务集中计划、进度与产物台账 | 用户需求 | 唯一CHG正文 | 根公报与任务文件 | yes | tests/test_workspace.py |
| logic_version/ | source/runtime-code | persisted | 只追加历史决策与索引 | AI 按需读取 | 设计逻辑 | records/index | records no | validate |
| references/、explainers/ | source/generated | internal | 模板/参考文档与可重建解释快照 | 文档/证据 | 模板/HTML | 各来源文档 | yes | browser/validate |
- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: 所有 Recall 文档为 source/runtime-code
- version_root: logic_version/
- temp_root: logic_version/working/
- workspace_root: .
- scratch_root: .work/
- data_roots: none
- unmapped_paths: agents/ (Codex 配置), .agents/ (代理私有目录), .claude/ (代理私有目录), logic_version/backups/ (归档快照), .github/ (仓库社区配置), CONTRIBUTING.md (社区贡献指南、非真源), SECURITY.md (安全政策、非真源), acl-reports/ (运行时 ACL 审计输出、非 Recall 真源)

### 范围登记表
| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [logic_readme.md](logic_readme.md) | [logic_change.md](logic_change.md) | self | active |
| MOD-GIT-PIPELINE | logic_domains/git-pipeline | in-system | domain/runtime-code | paired | [git-pipeline](logic_domains/git-pipeline/logic_readme.md) | [changes](logic_domains/git-pipeline/logic_change.md) | self | active |
| MOD-TOOLCHAIN | logic_domains/toolchain | in-system | domain/runtime-code | paired | [toolchain](logic_domains/toolchain/logic_readme.md) | [changes](logic_domains/toolchain/logic_change.md) | self | active |
| MOD-TEMPLATES | references/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-templates) | [active changes](logic_change.md) | self | active |
| MOD-EXPLAINERS | explainers/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-explainers) | [active changes](logic_change.md) | self | active |
| MOD-HISTORY | logic_version/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-history) | [active changes](logic_change.md) | self | active |
<a id="scope-mod-templates"></a> MOD-TEMPLATES：references/；模板是字段名权威来源，继承根规则。
<a id="scope-mod-explainers"></a> MOD-EXPLAINERS：explainers/；HTML 是可重建展示快照，不是制度真源。
<a id="scope-mod-history"></a> MOD-HISTORY：logic_version/；records 只追加，index 为全量索引。
## 功能意图与用户流程
用户视角层：**用户的表述就是宪法的来源**。每条意图标 `来源`（`user:日期` 原话登记 / `user-confirmed:日期` AI 起草经用户确认 / `code-derived`、`inferred` 待确认），未经用户确认的意图不得驱动实施；只在宪法维护（RULE-014）。用户已决定实施的新目标或约束先对照本节：已有则复用，没有则先立修宪案登记；讨论中的想法按 RULE-027 留待办。
### 功能意图登记
| intent_id | 功能入口 | intent（服务的用户目标） | 流程位置 | 关联规则 | 代码锚点 | 来源 | last_verified |
|---|---|---|---|---|---|---|---|
| INT-20260816-001 | logic_readme 功能意图与用户流程层 | AI 从文档恢复功能级产品逻辑与用户流程，无需重扫代码库 | FLOW-002#1 | RULE-014 | logic_readme.md | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-002 | recall init | 一条命令完成 Git + Recall 接入，无需手动配置 | FLOW-001#1 | RULE-010 | scripts/init_recall.py | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-003 | 文档阅读（SKILL/宪法/根账本 → 命中领域） | AI 在修改前恢复设计上下文，不从代码反推意图；宪法必读，领域按需，SKILL 细节按需读 references | FLOW-002#1 | RULE-001..004, RULE-018, RULE-022 | SKILL.md; references/document-model.md | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-004 | recall new | 在明确项目创建决策草稿，保留为什么改；缺项目标记不写入 | FLOW-002#3 | RULE-003, RULE-012 | scripts/create_ver.py | user:2026-10-12 本轮优化授权 | 2026-10-12 |
| INT-20260816-005 | recall sync | 一条命令保存并同步全部进度，无需手写 Git 序列 | FLOW-001#3, FLOW-002#5 | RULE-011, RULE-013 | scripts/git_sync.py | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-006 | recall next / index / status / list | 恢复当前任务、需求来源和剩余动作，区分想法、可做候选、待决策、阻塞与收尾；自动派生公报和状态 | FLOW-003#1 | RULE-018, RULE-021, RULE-027, RULE-028 | scripts/recall.py; scripts/task_context.py | user:2026-09-07 | 2026-09-07 |
| INT-20260816-007 | recall query file/commit/intent | 双向追溯：从代码定位"为什么改"，从功能意图定位"要改哪里" | FLOW-003#2 | RULE-013, RULE-014 | scripts/link_ver_git.py | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-008 | recall validate / recall audit | 确认宪法、领域文档、记录与 Git 状态一致；审计门按治理模式分档，一条命令可达 | FLOW-003#3 | RULE-009, RULE-015, RULE-018, RULE-023 | scripts/validate.py; scripts/recall_audit/integrity.py; scripts/recall.py | user-confirmed:2026-08-16 | 2026-09-06 |
| INT-20260816-009 | recall conflicts | 新需求与现行规则矛盾时提前暴露，交用户裁决 | FLOW-004#1 | RULE-021 | scripts/detect_conflicts.py | user-confirmed:2026-08-16 | 2026-09-03 |
| INT-20260816-010 | 项目接入流程（references/project-onboarding.md） | 存量/新项目模块化建立文档初稿：接入时建宪法骨架 + 至少一个领域，按触发时机逐模块补全 | FLOW-005#2 | RULE-016, RULE-018 | references/project-onboarding.md | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-011 | 一二级拆分（宪法 + 部门法，RULE-018） | 大小项目统一两级：改哪个领域读哪份部门法，宪法保证全局约束；领域过大拆小部门 | FLOW-005#4 | RULE-018 | references/logic-domain-template.md; scripts/recall_audit/integrity.py | user:2026-09-03 | 2026-09-04 |
| INT-20260903-001 | 收尾归零（任务内产物台账 + workspace 实物核对） | 任务结束时工作区只剩交付物，AI 不遗留探针脚本、临时测试与草稿 | FLOW-002#6 | RULE-020 | references/logic-temp-template.md; scripts/recall.py; scripts/validate.py | user:2026-09-03 | 2026-09-03 |
| INT-20260903-002 | recall route | 按目标路径/关键词得到本次应读的文档清单与上下文成本，只导入命中的领域 | FLOW-002#1 | RULE-018 | scripts/route_docs.py | user:2026-09-03 | 2026-09-06 |
| INT-20260907-001 | AI 审查与关案 | AI 审查验证后自主交付，人工后测发现问题另开案 | FLOW-002#4 | RULE-025 | references/change-lifecycle.md | user:2026-09-07 | 2026-09-07 |
| INT-20260907-002 | explainers HTML | 需要解释文档时直接在项目 explainers 打开查看 | FLOW-003#4 | RULE-026 | references/explainers.md | user:2026-09-07 | 2026-09-07 |
| INT-20261020-001 | inventory / path / workspace / 任务文件 | 明确工作路径与文件归属；相近需求合并监督，任务准确找规则、地图增量保覆盖、按任务/轮次清理并区分全局遗留；已归档重复正文删除受阻时允许保全移动集中待清理 | FLOW-002#1/2/4/6 | RULE-018, RULE-020, RULE-025, RULE-027, RULE-029 | scripts/workspace_cli.py; scripts/workspace_inventory.py; scripts/workspace_check.py; references/workspace-tasks.md | user:2026-10-25 | 2026-10-25 |
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
- UXI-006: 工具绝不静默删除文件：workspace/validate核对台账与实际产物，status保留Git候选，台账是处置清单而非删除脚本输入；来源：VER-20260903-001；影响：INT-20260903-001, INT-20260816-006, INT-20260816-008
## 责任记录约定
- personal 项目由 owner=self 维护；changed_by/decision_confirmed_by 记录实际修改者与用户确认，Git 保存历史；运维细节见 MOD-GIT-PIPELINE。
## 代码、生成物与运行数据边界
- source：SKILL、各级 logic 文档、references；generated：explainers；persisted：logic_version/records。现行 readme/账本是规则真源，explainers 可重建，records 只读。
## 数据与控制流
请求 → 宪法/账本 → route 领域 → 代码/测试 → simple/medium/high → 审查验证 → 更新现行文档、清理、定稿VER/index、关案、同步。
## 消费者与公共契约
- Claude/Codex 消费现行文档与 CHG，AI 消费 VER；Markdown 表格、ID 和 JSON 输出格式保持兼容，旧消费者约束见 MOD-TOOLCHAIN。
## 不可破坏约束
- INV-001/002：每个登记范围只有一份现行 readme，每项任务只有一份活跃正文，禁止平行真源。
- INV-003/004：VER 只追加（仅允许受管控 after_commit 回填），只保存设计逻辑，不保存代码快照。
## 兼容与迁移制度
- 文档模型是宪法 + 部门法；迁移需登记readme-only领域（旧paired兼容）、移动规则/地图、补来源与 contract_class；Git 提供回滚。
## 测试与验证
- unit：python -m unittest discover -s tests；integration：recall audit/validate/route/status；历史不可变性：Git diff。领域命令与证据见 MOD-GIT-PIPELINE、MOD-TOOLCHAIN。
## 有效决策索引
| version_id | 决策摘要 | 关联规则 | 记录 |
|---|---|---|---|
| VER-20261020-002 | 同任务多轮修订及关案归档保全 | RULE-025, RULE-027 | [记录](logic_version/records/logic_version-20261020-002-task-revision-history.md) |
| VER-20261024-001 | 任务准确路由、增量地图与分层清理 | RULE-018, RULE-020, RULE-027, RULE-029 | [记录](logic_version/records/logic_version-20261024-001-task-context-workspace.md) |
| VER-20261025-001 | 已归档重复任务集中待清理、原位记录与活跃过滤 | RULE-020, RULE-025 | [记录](logic_version/records/logic_version-20261025-001-pending-cleanup.md) |
## 活跃议案入口
- 唯一入口：[logic_change.md](logic_change.md)（任务公报；新任务正文在logic_changes/，旧领域账本兼容）；当前 CHG-ID：none（recall next 无活跃项；已关闭任务的决策记录保留在 logic_version/records/）
## 当前限制
- Recall 仅支持 personal/小团队；静态门不能替代语义、消费者或部署验证，未验证环境必须据实标明；根宪法目标 150 行、硬上限 250 行；领域细节应下放部门法，route/冲突/代码锚点仍是启发式检查。
- authority_surfaces、上游分支和存量函数白名单等工具链限制见 MOD-TOOLCHAIN。
## 修改检查清单
- [ ] 是否触及上游/下游契约、持久化数据或已部署行为？是否仍满足所有 INV 条目？是否存在未被更高优先级指令裁定的新旧需求矛盾？
- [ ] 新议案是否写在唯一任务文件并关联受影响范围并在根公报登记？新增或修改的关键规则是否已链接到具体 VER？
- [ ] 是否先完成现有实现可并入性分析，并在修改后补齐测试、审核前后结果？范围登记表、所属 readme 代码地图、测试与历史索引是否已更新？
- [ ] 本次新建的临时/探针/草稿文件是否已删除并核对真实文件（RULE-020）？
