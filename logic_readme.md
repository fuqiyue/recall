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
- last_verified: 2026-10-11
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: SKILL.md, logic_readme.md
- source_decisions: 全量见 logic_version/index.md（RULE-002 ②，不在此重复）；最近生效 VER-20260907-002, VER-20260907-003, VER-20261011-003
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
- owned_paths: SKILL.md, logic_readme.md, logic_change.md, logic_domains/, logic_version/, references/, explainers/, scripts/, tests/, recall.bat, recall.sh, .gitattributes, AGENTS.md, CLAUDE.md, README.md
- child_policy: inherit
- data_owner: none
- registry_status: registered
## 当前制度
| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-001 | key | 逻辑回档而非代码回档 | 避免上下文膨胀，保持文档简洁可读 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | SKILL.md 章节 | valid | 2026-08-08 | self |
| RULE-002 | key | logic_readme.md 只保留最新规则：① 已废弃内容删除，不留旧版并列；② 宪法"有效决策索引"只留指向 logic_version/index.md 的指针 + 最近 3 条，全量索引在 index.md；③ 每条生效 VER 的长期落点是相关规则行的"决策记录"列，validate 核查生效 VER 至少被一条规则行链接或出现在宪法索引 | 单一真相源；宪法每任务必读，逐条重复 index.md 的 18 行只烧 token、不增信息 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md)；[VER-20260904-002](logic_version/records/logic_version-20260904-002-docs-consolidation.md) | 用户确认；索引收缩为 2026-09-04 用户认可 | 当前文档 + scripts/validate.py `rule_linked_versions` + tests/test_validate.py | valid | 2026-09-04 | self |
| RULE-003 | key | 历史记录保存设计逻辑 | 记录为什么、取舍、影响，不记录代码快照 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | logic_version/ | valid | 2026-08-08 | self |
| RULE-004 | ordinary | 三条通道分流修改 | 简单/中等/高风险，避免过度流程化 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 最佳实践 | SKILL.md | valid | 2026-08-08 | self |
| RULE-014 | key | 意图层与需求保全：① 宪法维护功能级"功能意图与用户流程"层（INT/FLOW/UXI 按条目模块化，intent_id 用 `INT-YYYYMMDD-NNN` 完整格式，登记表含代码锚点列与 `来源` 列），只在宪法维护、领域不重复；② 只有 `user:` / `user-confirmed:` 来源可驱动实施（想法、实施承诺与本次授权的区分见 RULE-027），`code-derived` / `inferred` 由 validate 告警，用户已决定实施的新目标先落意图层再做领域工作；讨论中的想法留待办；③ medium/high CHG 实施前写 raw_request / decomposition / fit_analysis，归档时三字段原样搬入 VER；落选方案连同需求原文与否决原因随胜出 VER 归档，已独立立案的落选 CHG 建 `status: rejected` 的 VER 并同样搬运三字段；④ plan 模式产出批准后、动代码前按通道落盘；⑤ 维护深度按治理模式分档：personal 轻量档（INT 必维护、FLOW 可合并、UXI 按需），collaborative 及以上全量（档位见 references/governance-modes.md） | 产品逻辑与需求拆解此前只活在会话和会被删除的 CHG 里，AI 每次从代码反推意图；来源列让用户原话与 AI 推断在真源里可区分 | [VER-20260816-001](logic_version/records/logic_version-20260816-001-feature-intent-layer.md)；[VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md)；[VER-20260831-002](logic_version/records/logic_version-20260831-002-arch-simplify.md)；[VER-20260904-001](logic_version/records/logic_version-20260904-001-intent-provenance-conflicts.md) | 用户确认；来源列为 2026-09-04 用户确认（"用户的思路就是宪法"） | 本文件"功能意图与用户流程"节 + scripts/validate.py `check_intent_layer` 来源检查 + references/governance-modes.md | valid | 2026-09-04 | self |
| RULE-016 | key | 项目接入采用模块化渐进：接入时只建根骨架（文档控制、范围登记表、至少一个领域、访谈式 INT/FLOW 初稿），存量模块登记 `pending-docs`；此后仅在新项目开始使用时或用户单独要求时补全对应模块；AI 代码扫描产出标 `code-derived`，意图层必须经用户确认后落盘 | 一次性全量扫描在存量项目不可行，未经确认的 AI 推断意图会污染真源 | [VER-20260816-003](logic_version/records/logic_version-20260816-003-semantic-link.md)；[VER-20260903-004](logic_version/records/logic_version-20260903-004-two-level-docs.md) | 用户确认 | references/project-onboarding.md + SKILL.md 接入章节 | valid | 2026-09-04 | self |
| RULE-017 | key | 会话默认延续：新会话或上下文压缩后以现行 logic 文档与活跃议案为准继续（新会话视作新人接手，文档即交接），不要求用户重述背景；仅当用户明确指出现行规则或代码有问题时才修改现行制度；模糊点先按现行逻辑分析并给出建议再咨询（RULE-014/017） | 协作协议此前只活在对话历史，每次压缩后用户被迫重讲元规则，正是 Recall 要消灭的 rescan | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) | 用户确认 | SKILL.md 上下文读取入口 | valid | 2026-08-16 | self |
| RULE-018 | key | 一二级拆分法：① 根 logic_readme 是**宪法**（全局规则、功能意图层、范围登记表即领域目录），每个任务必读；② `logic_domains/领域名/logic_readme.md` + `logic_change.md` 是**部门法**，以 `doc_policy: paired` 登记、`owned_paths` 声明职权，承载该职权的规则行、代码地图行与测试行，只在任务触及职权时读取；③ 入口 `recall route 路径、关键词或 INT-ID` 给出本次应读清单与估算 token（匹配算法与 inherited 路径处理见 MOD-TOOLCHAIN 代码地图 route_docs 行）；④ 无论项目大小至少一个领域，宪法未登记领域使 `recall audit` 静态门失败；大部门制，领域 readme 越过目标即拆小部门（各级长度目标与硬上限见 references/field-vocabulary.md；越过目标只提示，越过硬上限进门，`--advisory-only` 为存量项目迁移窗口）；⑤ 根 logic_change 只放修宪议案 + 全项目活跃议案索引（公报可由 `recall index --write` 从正文派生，一行一条、`proposal_path` 指向领域账本），领域 logic_change 一事一议、同一 CHG 正文只在一处，领域议案 `affected_scopes` 必含自身且不含 `.`（触宪即修宪案）；⑥ RULE/INT 编号空间与 logic_version 全项目唯一，未登记的 logic_readme/logic_change 是平行真源；⑦ 根规章优先于领域 | 宪法必读保住全局约束与用户意图，部门法按需导入控制上下文成本，未登记的拆分会重演平行真源 | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md)；[VER-20260903-004](logic_version/records/logic_version-20260903-004-two-level-docs.md)；[VER-20260904-002](logic_version/records/logic_version-20260904-002-docs-consolidation.md)；[VER-20260904-005](logic_version/records/logic_version-20260904-005-density-gate.md)；[VER-20260906-001](logic_version/records/logic_version-20260906-001-constitution-slim-alignment.md) | 用户确认 2026-09-03（宪法/部门法比喻，"无论大小项目都用一二级拆分法"）；无领域进门为 2026-09-04 用户裁决 A | scripts/recall_common.py `registered_domains`/`change_ledgers`/`inherited_modules` + scripts/route_docs.py + scripts/recall_audit/integrity.py 领域与公报核查 + archive.py 密度分档 + tests/（audit、cli、validate、common）；本仓库自身：MOD-GIT-PIPELINE、MOD-TOOLCHAIN | valid | 2026-09-06 | self |
| RULE-019 | key | 文档引用纪律：规范的语义正文只存在于 logic_readme（宪法或所属领域）的规则行；SKILL、模板、生命周期文档、CLAUDE/AGENTS 入口等其他位置只保留"见 RULE-XXX"式指针与纯操作步骤；审计对账"git 跟踪的顶层 Markdown 入口 ⊆ owned_paths ∪ unmapped_paths"，未登记条目使静态门失败 | 同一语义散布多处每次更新需 N 连改、漏一处即漂移；改名换姓的制度副本只能靠登记对账机器可见 | [VER-20260816-005](logic_version/records/logic_version-20260816-005-audit-remediation.md)；[VER-20261011-003](logic_version/records/logic_version-20261011-003-maintenance-boundaries.md) | 用户确认 | scripts/audit_logic_map.py 根目录覆盖对账 + tests/test_audit_logic_map.py | valid | 2026-09-04 | self |
| RULE-020 | key | 收尾归零：① 任务完成态 = 交付物就位 + 本次新建的非交付物（探针脚本、临时测试、草稿、调试输出）已删除或经用户同意保留 + 最终汇报列出处置清单；② `medium`/`high` 通道必建 `logic_version/working/` 下以 version_slug 命名目录内的 `logic_temp.md`（位置由审计器校验），在"工作区产物台账"登记 path / artifact_kind / disposition / reason / cleaned_at，台账清零（无未执行 delete、无 pending）方可关闭 CHG 并删除 working 目录；③ `simple` 通道不建文件，只在汇报列清单；④ `recall status` 单列未跟踪文件为待处置候选，`recall validate` 对未被 .gitignore 覆盖的未跟踪文件非阻断告警；⑤ **任何工具都不自动删除文件**，处置由代理逐项执行并对用户可见 | 临时文件在任务"完成"后无人负责，RULE-011 默认排除未跟踪文件保住远端却让本地垃圾隐形累积；只有把收尾写进"完成"的定义才覆盖 simple 通道 | [VER-20260903-001](logic_version/records/logic_version-20260903-001-cleanup-ledger.md); cleanup corrections: [VER-20261011-001](logic_version/records/logic_version-20261011-001-cleanup-ai-delivery-closure.md), [VER-20261011-002](logic_version/records/logic_version-20261011-002-cleanup-html-explainers.md) | 用户确认 2026-09-03（A/B 二选一选 B） | references/logic-temp-template.md 台账表 + scripts/recall_common.py `classify_porcelain` + scripts/validate.py `report_untracked_leftovers` + tests/test_recall_cli.py、tests/test_validate.py；已 git add 的垃圾无自动检测 | valid | 2026-10-11 | self |
| RULE-022 | key | 按需披露：① SKILL.md 首屏只保留关键上下文入口、任务记录、三通道、必要边界、命令与"按需读取"表，其余细节只在 references/ 保留一份并由表指向；② 审计器实现结构与函数长度上限是工具链领域规则（RULE-024，含机器门）；③ Density：越过目标值只提示，越过硬上限与宪法无领域使 current-state / formal-review 静态门失败，单条 CHG 越过 80 行与 blocked 累积只提示，`--advisory-only` 只改退出码供存量项目迁移（各级数值见 references/field-vocabulary.md）；④ 规则行用 ①②③ 行内子条款分项、`why` 只留一句，事故经过与量化叙事归 VER | SKILL 与宪法每任务必读，细节堆在首屏只烧 token，规则行膨胀成段落后代理无法精确引用 | [VER-20260831-001](logic_version/records/logic_version-20260831-001-entry-slim-skill-front.md)；[VER-20260903-002](logic_version/records/logic_version-20260903-002-structure-context-cost.md)；[VER-20260903-003](logic_version/records/logic_version-20260903-003-structural-closure.md)；[VER-20260904-002](logic_version/records/logic_version-20260904-002-docs-consolidation.md)；[VER-20260904-005](logic_version/records/logic_version-20260904-005-density-gate.md)；[VER-20260906-001](logic_version/records/logic_version-20260906-001-constitution-slim-alignment.md)；[VER-20261011-003](logic_version/records/logic_version-20261011-003-maintenance-boundaries.md) | 用户确认 2026-09-03；子条款化为 2026-09-04 用户认可；硬上限进门为 2026-09-04 用户裁决 A | SKILL.md + references/document-model.md、references/git-sync.md + scripts/recall_audit/ + tests/test_audit_logic_map.py | valid | 2026-09-06 | self |
| RULE-025 | key | AI 自主交付：① personal 默认由 AI 实施、语义自审并完成与改动相称的本地/受控验证；审查结论及证据独立于实现说明，一行记录即可；② 通过且无未决设计或实质阻塞后，同一任务主动 verifying → promoting → 更新所属 readme、固化所需 VER、清理并移除 CHG 与公报，不等人工批准或真人体验；③ readme 记录已交付实现及适用环境，生产部署/真机未验证如实列明，不冒充已上线；交付后人工反馈新增 CHG-ID（简单修复依通道），不重开旧案；④ 仅真实实现/验证缺口或明确授权/外部前置可阻塞，写明证据与解除动作；既有用户授权直接沿用，只有明确要求的人工验收才是门；⑤ 已关闭依赖重核后改绑 VER/现行规则，不能因上游只缺人工体验挂起下游；已启用行为不得长期停在活跃议案 | 让 AI 完成交付闭环，避免把交付后测试变成无限等待 | [VER-20260907-001](logic_version/records/logic_version-20260907-001-ai-delivery-closure.md) | user:2026-09-07 | references/change-lifecycle.md、governance-modes.md、logic-change-template.md 语义核对 | valid | 2026-09-07 | Codex |
| RULE-026 | ordinary | 解释文档：需要持久、可视化的流程/架构/方案/状态说明时，在当前项目 explainers/ 生成可直接打开的 HTML 并交付链接；简单问答无需建页，用户指定格式优先；HTML 是展示快照，标注日期、来源链接与已核/未核边界，规则仍以所属 readme、活跃工作以 change 为准；已有相关页优先更新，日期快照另建并标明，状态计数须从声明的同一账本范围重算；登记为可重建交付物，禁止把 HTML 作为平行制度或只在其中保存决策 | 沿用 EduAI 的可读解释形式，同时保住唯一制度来源 | [VER-20260907-002](logic_version/records/logic_version-20260907-002-html-explainers.md) | user:2026-09-07 | references/explainers.md 与 explainers/ 实际产物 | valid | 2026-09-07 | Codex |
| RULE-027 | key | 任务上下文优先：① 所属 change 可用轻量待办记录 idea（想法）与 planned（决定要做尚未开始），不计活跃 CHG，不因提出想法修改现行意图或产生实施承诺；② 保留需求来源、关键约束、已知完成条件和剩余动作，开始时按通道承接到 CHG/实施并移除待办行，已有授权沿用；③ 大目标按独立可验证价值组织，必须共同保持不变量的修改仍属同一 CHG；④ 阻塞记录原因、解除动作、执行者与日期/事件复查时机，缺信息提示，不增审批门；⑤ next/status 是同账本派生视图，模型结合正文与证据选择下一步，不固定排序分数/并行上限，不自动授权或执行 | 强模型需要可靠的任务与需求上下文，重复流程指令和双写会增加维护负担 | [VER-20260907-003](logic_version/records/logic_version-20260907-003-task-context.md) | user:2026-09-07 本轮优化请求 | scripts/task_context.py + tests/test_task_context.py；references/task-context.md | valid | 2026-09-07 | Codex |
领域规则：Git 管道 RULE-010/011/013 见 [MOD-GIT-PIPELINE](logic_domains/git-pipeline/logic_readme.md)；工具链 RULE-005..009、012、015、021、023、024 见 [MOD-TOOLCHAIN](logic_domains/toolchain/logic_readme.md)。
## 代码地图
| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| SKILL.md、logic_readme.md、logic_change.md | source/runtime-code | public | Recall 入口、宪法与议案账本 | AI/代理 | 当前规则与议案 | 各文件 | yes | validate/audit |
| logic_domains/ | source/runtime-code | public | 领域部门法与领域账本，按 route 按需读取 | AI/代理 | 领域规则与 CHG | 各领域文件 | yes | route |
| logic_version/ | source/runtime-code | persisted | 只追加历史决策与索引 | AI 按需读取 | 设计逻辑 | records/index | records no | validate |
| references/、explainers/ | source/generated | internal | 模板/参考文档与可重建解释快照 | 文档/证据 | 模板/HTML | 各来源文档 | yes | browser/validate |
- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: 所有 Recall 文档为 source/runtime-code
- version_root: logic_version/
- temp_root: logic_version/working/
- unmapped_paths: agents/ (Codex 配置), .agents/ (代理私有目录), .claude/ (代理私有目录), logic_version/backups/ (归档快照), .github/ (仓库社区配置), CONTRIBUTING.md (社区贡献指南、非真源), SECURITY.md (安全政策、非真源), acl-reports/ (运行时 ACL 审计输出、非 Recall 真源)

### 范围登记表### 范围登记表
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
| INT-20260816-004 | recall new | 修改前留下"为什么改"的决策记录骨架 | FLOW-002#3 | RULE-003, RULE-012 | scripts/create_ver.py | user-confirmed:2026-08-16 | 2026-08-16 |
| INT-20260816-005 | recall sync | 一条命令保存并同步全部进度，无需手写 Git 序列 | FLOW-001#3, FLOW-002#5 | RULE-011, RULE-013 | scripts/git_sync.py | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-006 | recall next / index / status / list | 恢复当前任务、需求来源和剩余动作，区分想法、可做候选、待决策、阻塞与收尾；自动派生公报和状态 | FLOW-003#1 | RULE-018, RULE-021, RULE-027, RULE-028 | scripts/recall.py; scripts/task_context.py | user:2026-09-07 | 2026-09-07 |
| INT-20260816-007 | recall query file/commit/intent | 双向追溯：从代码定位"为什么改"，从功能意图定位"要改哪里" | FLOW-003#2 | RULE-013, RULE-014 | scripts/link_ver_git.py | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-008 | recall validate / recall audit | 确认宪法、领域文档、记录与 Git 状态一致；审计门按治理模式分档，一条命令可达 | FLOW-003#3 | RULE-009, RULE-015, RULE-018, RULE-023 | scripts/validate.py; scripts/recall_audit/integrity.py; scripts/recall.py | user-confirmed:2026-08-16 | 2026-09-06 |
| INT-20260816-009 | recall conflicts | 新需求与现行规则矛盾时提前暴露，交用户裁决 | FLOW-004#1 | RULE-021 | scripts/detect_conflicts.py | user-confirmed:2026-08-16 | 2026-09-03 |
| INT-20260816-010 | 项目接入流程（references/project-onboarding.md） | 存量/新项目模块化建立文档初稿：接入时建宪法骨架 + 至少一个领域，按触发时机逐模块补全 | FLOW-005#2 | RULE-016, RULE-018 | references/project-onboarding.md | user-confirmed:2026-08-16 | 2026-09-04 |
| INT-20260816-011 | 一二级拆分（宪法 + 部门法，RULE-018） | 大小项目统一两级：改哪个领域读哪份部门法，宪法保证全局约束；领域过大拆小部门 | FLOW-005#4 | RULE-018 | references/logic-domain-template.md; scripts/recall_audit/integrity.py | user:2026-09-03 | 2026-09-04 |
| INT-20260903-001 | 收尾归零（logic_temp 工作区产物台账 + status/validate 残留提示） | 任务结束时工作区只剩交付物，AI 不遗留探针脚本、临时测试与草稿 | FLOW-002#6 | RULE-020 | references/logic-temp-template.md; scripts/recall.py; scripts/validate.py | user:2026-09-03 | 2026-09-03 |
| INT-20260903-002 | recall route | 按目标路径/关键词得到本次应读的文档清单与上下文成本，只导入命中的领域 | FLOW-002#1 | RULE-018 | scripts/route_docs.py | user:2026-09-03 | 2026-09-06 |
| INT-20260907-001 | AI 审查与关案 | AI 审查验证后自主交付，人工后测发现问题另开案 | FLOW-002#4 | RULE-025 | references/change-lifecycle.md | user:2026-09-07 | 2026-09-07 |
| INT-20260907-002 | explainers HTML | 需要解释文档时直接在项目 explainers 打开查看 | FLOW-003#4 | RULE-026 | references/explainers.md | user:2026-09-07 | 2026-09-07 |
### 用户流程
- FLOW-001 首次接入：1. recall init → INT-20260816-002；2. 配置远端（可选）；3. recall sync → INT-20260816-005。
- FLOW-002 日常修改：1. 读宪法/账本并 route → INT-20260816-001/003/002；2. 判通道并实施；3. recall new（medium/high）→ INT-20260816-004；4. 审查验证后晋升、归档、清理、关案 → INT-20260907-001；5. commit/sync → INT-20260816-005；6. status 收尾 → INT-20260903-001。
- FLOW-003 追溯审查：1. next/status/list/index → INT-20260816-006；2. query → INT-20260816-007；3. validate/audit → INT-20260816-008；4. explainers → INT-20260907-002。
- FLOW-004 冲突澄清：1. conflicts → INT-20260816-009；2. 标注所属账本；3. 用户裁决后实施。
- FLOW-005 项目接入：1. recall init；2. 建宪法、领域与意图访谈 → INT-20260816-010；3. 按触发时机补全；4. 超限时拆域并登记 → INT-20260816-011。

### 操作直觉约束
- UXI-001: 用户不手写 commit message，sync 自动保存；来源：VER-20260811-003；影响：INT-20260816-005
- UXI-002: 一条命令完成一个用户目标，不要求用户记忆多步 Git 序列；来源：用户确认 2026-08-07；影响：INT-20260816-002, INT-20260816-005
- UXI-003: hook 与自动化绝不提交用户未提交的其他文件；自动保存只提交已跟踪文件的变更，未跟踪新文件默认排除并列出（`--include-new` 或 `git add` 才是用户的明确要求）；来源：VER-20260816-005；影响：INT-20260816-005
- UXI-004: 全部 CLI 在非交互与重定向环境可用；来源：VER-20260808-002；影响：全部 INT 条目
- UXI-005: 新会话默认延续：用户不需要重述项目哲学与背景，文档即交接；现行规则仅在用户明确否定时才修改；来源：VER-20260816-004；影响：INT-20260816-001, INT-20260816-003
- UXI-006: 工具绝不静默删除文件：status/validate 只列出未跟踪待处置文件，台账是给代理和用户看的处置清单而非删除脚本输入；来源：VER-20260903-001；影响：INT-20260903-001, INT-20260816-006, INT-20260816-008
## 责任记录约定
- personal 项目由 owner=self 维护；changed_by/decision_confirmed_by 记录实际修改者与用户确认，Git 保存历史；运维细节见 MOD-GIT-PIPELINE。
## 代码、生成物与运行数据边界
- source：SKILL、各级 logic 文档、references；generated：explainers；persisted：logic_version/records。现行 readme/账本是规则真源，explainers 可重建，records 只读。
## 数据与控制流
请求 → 宪法/账本 → route 领域 → 代码/测试 → simple/medium/high → 审查验证 → 晋升、VER/index、清理、关案、同步。
## 消费者与公共契约
- Claude/Codex 消费现行文档与 CHG，AI 消费 VER；Markdown 表格、ID 和 JSON 输出格式保持兼容，旧消费者约束见 MOD-TOOLCHAIN。
## 不可破坏约束
- INV-001/002：每个登记范围只有一份现行 readme 和配对账本，禁止平行真源。
- INV-003/004：VER 只追加（仅允许受管控 after_commit 回填），只保存设计逻辑，不保存代码快照。
## 兼容与迁移制度
- 文档模型是宪法 + 部门法；迁移需登记 paired 领域、移动规则/地图、补来源与 contract_class；Git 提供回滚。
## 测试与验证
- unit：python -m unittest discover -s tests；integration：recall audit/validate/route/status；历史不可变性：Git diff。领域命令与证据见 MOD-GIT-PIPELINE、MOD-TOOLCHAIN。
## 有效决策索引
| version_id | 决策摘要 | 关联规则 | 记录 |
|---|---|---|---|
| VER-20260907-002 | 解释文档统一交付 explainers HTML | RULE-026 | [记录](logic_version/records/logic_version-20260907-002-html-explainers.md) |
| VER-20260907-003 | 任务上下文优先、下一步视图与派生公报 | RULE-027, RULE-028 | [记录](logic_version/records/logic_version-20260907-003-task-context.md) |
| VER-20261011-003 | 入口路径、审计边界、运行数据分类与宪法密度优化 | RULE-019, RULE-022 | [记录](logic_version/records/logic_version-20261011-003-maintenance-boundaries.md) |
## 活跃议案入口
- 唯一入口：[logic_change.md](logic_change.md)（修宪议案 + 全项目公报；领域议案正文在各领域账本）；当前 CHG-ID：none（recall next 无活跃项；已关闭任务的决策记录保留在 logic_version/records/）
## 当前限制
- Recall 仅支持 personal/小团队；静态门不能替代语义、消费者或部署验证，未验证环境必须据实标明。；根宪法目标 150 行、硬上限 250 行；领域细节应下放部门法，route/冲突/代码锚点仍是启发式检查。
- authority_surfaces、上游分支和存量函数白名单等工具链限制见 MOD-TOOLCHAIN。
## 修改检查清单
- [ ] 是否触及上游/下游契约、持久化数据或已部署行为？是否仍满足所有 INV 条目？是否存在未被更高优先级指令裁定的新旧需求矛盾？
- [ ] 议案是否写在所属账本（触宪 → 根；领域事务 → 领域）并在根公报登记？新增或修改的关键规则是否已链接到具体 VER？
- [ ] 是否先完成现有实现可并入性分析，并在修改后补齐测试、审核前后结果？范围登记表、所属 readme 代码地图、测试与历史索引是否已更新？
- [ ] 本次新建的临时/探针/草稿文件是否已删除或登记保留理由（RULE-020）？
