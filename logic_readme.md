# Recall Skill Logic

宪法（一级 readme，RULE-018）：全局规则、功能意图与用户流程、领域目录。每个任务必读；领域规则在 `logic_domains/`（部门法），用 `recall route 目标路径` 按需导入。

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
- last_verified: 2026-09-04
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: SKILL.md, logic_readme.md
- source_decisions: VER-20260808-001, VER-20260808-002, VER-20260811-001, VER-20260811-002, VER-20260811-003, VER-20260816-001, VER-20260816-002, VER-20260816-003, VER-20260816-004, VER-20260816-005, VER-20260831-001, VER-20260831-002, VER-20260903-001, VER-20260903-002, VER-20260903-003, VER-20260903-004
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
- owned_paths: SKILL.md, logic_readme.md, logic_change.md, logic_domains/, logic_version/, references/, scripts/, tests/, recall.bat, recall.sh, .gitattributes, AGENTS.md, CLAUDE.md, README.md
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-001 | key | 逻辑回档而非代码回档 | 避免上下文膨胀，保持文档简洁可读 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | SKILL.md 章节 | valid | 2026-08-08 | self |
| RULE-002 | key | logic_readme.md 只保留最新规则 | 删除已废弃内容，保持单一真相源 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | 当前文档 | valid | 2026-08-08 | self |
| RULE-003 | key | 历史记录保存设计逻辑 | 记录为什么、取舍、影响，不记录代码快照 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | logic_version/ | valid | 2026-08-08 | self |
| RULE-004 | ordinary | 三条通道分流修改 | 简单/中等/高风险，避免过度流程化 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 最佳实践 | SKILL.md | valid | 2026-08-08 | self |
| RULE-014 | key | logic_readme 维护功能级"功能意图与用户流程"层（INT/FLOW/UXI 按条目模块化，intent_id 统一 `INT-YYYYMMDD-NNN` 完整格式，登记表含代码锚点列支撑反向查询；意图层只在宪法维护，领域文档不重复）；medium/high CHG 在实施前记录需求拆解与融入分析（raw_request/decomposition/fit_analysis），归档时三字段原样搬入 VER 记录（需求保全）；同议题多方案竞争时，落选方案连同其需求原文与否决原因随胜出 VER 的方案分析归档，已独立立案的落选 CHG 建 `status: rejected` 的 VER 记录并同样搬运三字段；plan 模式产出批准后、动代码前按通道落盘；意图层维护深度按治理模式分档：personal 轻量档（INT 必维护、FLOW 可合并、UXI 按需），collaborative 及以上全量，档位定义见 references/governance-modes.md | 功能级产品逻辑此前无处沉淀，AI 每会话从代码反推意图；CHG 归档即删除，三字段不搬入不可变记录则需求拆解只剩 git 考古可查，落选方案直接删除亦然；单人模式逐条维护三层的行数成本与收益不成比例 | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) | 用户确认 | 本文件"功能意图与用户流程"节 + scripts/validate.py + references/governance-modes.md | valid | 2026-09-04 | self |
| RULE-016 | key | 项目接入采用模块化渐进：接入时只建根骨架（文档控制、范围登记表、至少一个领域、访谈式 INT/FLOW 初稿），存量模块登记 `pending-docs`；此后仅在新项目开始使用时或用户单独要求时补全对应模块；AI 代码扫描产出标 `code-derived`，意图层必须经用户确认后落盘 | `recall init` 只建 Git 管道，文档内容从哪来此前无流程；一次性全量扫描在存量项目不可行，未经确认的 AI 推断意图会污染真源 | [VER-20260816-003](logic_version/records/logic_version-20260816-003-semantic-link.md) | 用户确认 | references/project-onboarding.md + SKILL.md 接入章节 | valid | 2026-09-04 | self |
| RULE-017 | key | 会话默认延续：新会话或上下文压缩后以现行 logic 文档与活跃议案为准继续（新会话视作新人接手，文档即交接），不要求用户重述背景；仅当用户明确指出现行规则或代码有问题时才修改现行制度；模糊点先按现行逻辑分析并给出建议再咨询（SKILL 原则 5/11） | 协作协议此前只活在对话历史，每次压缩后用户被迫重讲元规则，正是 Recall 要消灭的 rescan | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) | 用户确认 | SKILL.md 核心原则 11 | valid | 2026-08-16 | self |
| RULE-018 | key | 一二级拆分法：根 logic_readme 是**宪法**（全局规则、功能意图层、范围登记表即领域目录），每个任务必读；`logic_domains/领域名/logic_readme.md` + `logic_change.md` 是**部门法**（范围登记表 `doc_policy: paired` 登记，`owned_paths` 声明职权，承载该职权的规则行、代码地图行与测试行），只在任务触及职权时读取，入口 `recall route 路径或关键词`；**无论项目大小至少一个领域**；大部门制：法条少时一域多职，领域 readme 越过 250 行目标即拆小部门（宪法 150/250、领域 250/400、账本 150/300，Density advisory）；根 logic_change 只放修宪议案 + 全项目活跃议案索引（公报：一行一条、`proposal_path` 指向领域账本），领域 logic_change 一事一议、同域同账本、同一 CHG 正文只在一处；领域议案 `affected_scopes` 必含自身且不含 `.`（触宪即修宪案，正文回根账本）；RULE/INT 编号空间全项目唯一；未登记的 logic_readme/logic_change 仍是平行真源；logic_version 全项目唯一；根规章优先于领域 | 单文件根文档在消费项目达 1060/6543 行、超出上下文窗口 20 倍，而此前子文档可选、无 change 配对、从未被任何项目使用；宪法必读保住全局约束与用户意图，部门法按需导入把每任务固定读取从整份根文档降到宪法 + 命中领域；未经登记的拆分会重演平行真源失败模式，无检查的子文档会成为膨胀区与撞号区 | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md)；[VER-20260903-004](logic_version/records/logic_version-20260903-004-two-level-docs.md) | 用户确认 2026-09-03（宪法/部门法比喻，"无论大小项目都用一二级拆分法"） | scripts/recall_common.py `registered_domains`/`change_ledgers` + scripts/route_docs.py + scripts/recall_audit/integrity.py 领域与公报核查 + archive.py 密度分档 + tests/test_audit_logic_map.py、tests/test_recall_cli.py、tests/test_validate.py、tests/test_recall_common.py；本仓库自身：MOD-GIT-PIPELINE、MOD-TOOLCHAIN | valid | 2026-09-04 | self |
| RULE-019 | key | 文档引用纪律：规范的语义正文只存在于 logic_readme（宪法或所属领域）的规则行；SKILL、模板、生命周期文档、CLAUDE/AGENTS 入口等其他位置只保留"见 RULE-XXX"式指针与纯操作步骤；审计对账"git 跟踪的顶层 Markdown 入口 ⊆ owned_paths ∪ unmapped_paths"，未登记条目使静态门失败 | 同一语义散布多处（曾达 5 处）每次更新需 N 连改、漏一处即漂移；改名换姓的制度副本（README 重述通道、SUMMARY 总结）平行真源检测抓不到，只能靠登记对账机器可见 | [VER-20260816-005](logic_version/records/logic_version-20260816-005-audit-remediation.md) | 用户确认 | scripts/audit_logic_map.py 根目录覆盖对账 + tests/test_audit_logic_map.py | valid | 2026-09-04 | self |
| RULE-020 | key | 收尾归零：任务完成态 = 交付物就位 + 本次新建的非交付物（探针脚本、临时测试、草稿、调试输出）已删除或经用户同意保留 + 最终汇报列出处置清单；`medium`/`high` 通道必建 `logic_version/working/` 下以 version_slug 命名目录内的 `logic_temp.md`（位置由审计器校验），在其"工作区产物台账"登记 path / artifact_kind / disposition / reason / cleaned_at，台账清零（无未执行的 delete、无 pending）方可关闭 CHG 并删除 working 目录；`simple` 通道不建文件，只在最终汇报列清单；`recall status` 把未跟踪文件单列为待处置候选，`recall validate` 对未被 .gitignore 覆盖的未跟踪文件非阻断告警；**任何工具都不自动删除文件**，处置由代理逐项执行并对用户可见 | AI 解题产生的临时文件在任务"完成"后无人负责；RULE-011 默认排除未跟踪文件保住了远端却让本地垃圾隐形累积；只有把收尾写进"完成"的定义才能覆盖不建 CHG 的 simple 通道 | [VER-20260903-001](logic_version/records/logic_version-20260903-001-cleanup-ledger.md) | 用户确认 2026-09-03（A/B 二选一选 B） | references/logic-temp-template.md 台账表 + scripts/recall_common.py `classify_porcelain` + scripts/validate.py `report_untracked_leftovers` + tests/test_recall_cli.py + tests/test_validate.py；**已被 git add 的垃圾无自动检测**，只能靠台账或汇报清单 | valid | 2026-09-03 | self |
| RULE-022 | key | 按需披露：SKILL.md 首屏只保留路由问题、三通道、默认读取顺序、核心原则、调用模式/命令与"按需读取"表，其余细节（文档模型、Git 同步、治理模式、项目接入、代理入口、领域模板）只在 references/ 保留一份并由表指向；审计器按层分包在 `scripts/recall_audit/`（只许向下依赖，`audit_logic_map.py` 只做入口，新写函数不超过 150 行，结构见 MOD-TOOLCHAIN 代码地图）；Density 段对越过目标值的文档给出 advisory 提示 | SKILL 每次触发约 6300 token、其中近半是代理极少当场需要的目录模型与 Git 细节；审计器单文件 6764 行、最大函数 650 行，是修改成本最高且最易再出 RULE-009 式静默漂移的地方；行数目标此前只写在文档里、无机器信号 | [VER-20260903-002](logic_version/records/logic_version-20260903-002-structure-context-cost.md)；[VER-20260903-003](logic_version/records/logic_version-20260903-003-structural-closure.md) | 用户确认 2026-09-03 | SKILL.md + references/document-model.md、references/git-sync.md + scripts/recall_audit/ + tests/test_audit_logic_map.py | valid | 2026-09-04 | self |

领域规则：Git 管道 RULE-010/011/013 见 [MOD-GIT-PIPELINE](logic_domains/git-pipeline/logic_readme.md)；工具链 RULE-005..009、012、015、021、023 见 [MOD-TOOLCHAIN](logic_domains/toolchain/logic_readme.md)。

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|
| SKILL.md | source/runtime-code | Recall skill 主入口，定义核心原则和使用方式 | AI 读取 | 指导 AI 行为 | SKILL.md | yes | none |
| logic_readme.md | source/runtime-code | 宪法：全局规则、领域目录、功能意图层（每任务必读） | AI 读取 | 当前制度 | logic_readme.md | yes | none |
| logic_change.md | source/runtime-code | 修宪议案正文 + 全项目活跃议案索引（公报） | AI 读取/写入 | 修改议案 | logic_change.md | yes | none |
| logic_domains/ | source/runtime-code | 部门法：每个领域一对 logic_readme.md（规则、代码地图、测试）+ logic_change.md（一事一议）；按 `recall route` 按需读取 | AI 按需读取/写入 | 领域制度与议案 | 各领域文件 | yes | tests/test_recall_cli.py（route） |
| logic_version/ | source/runtime-code | records/ 历史决策记录（逻辑回档，只追加）+ index.md 索引；全项目唯一 | AI 按需读取 | 设计逻辑回忆 | VER-*.md / index.md | records no / index yes | none |
| references/ | source/runtime-code | 模板文件和参考文档；字段名的权威来源 | AI 按需读取 | 文档模板 | 模板文件 | yes | none |
| scripts/、tests/、recall.bat/.sh | source/runtime-code | 代码地图行在所属领域：Git 管道脚本见 MOD-GIT-PIPELINE，其余脚本、入口与测试见 MOD-TOOLCHAIN | 见领域文档 | 见领域文档 | 领域 logic_readme.md | yes | `python -m unittest discover -s tests` |

- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: 所有 Recall 文档为 source/runtime-code 层
- version_root: logic_version/
- temp_root: logic_version/working/
- 子范围路由：按范围登记表的 paired 领域行路由；`recall route` 给出读取清单
- unmapped_paths: agents/ (Codex 配置), .agents/ (代理私有目录), .claude/ (代理私有目录), logic_version/backups/ (归档快照), .github/ (仓库社区配置), CONTRIBUTING.md (社区贡献指南、非真源), SECURITY.md (安全政策、非真源)

### 范围登记表

| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [logic_readme.md](logic_readme.md) | [logic_change.md](logic_change.md) | self | active |
| MOD-GIT-PIPELINE | logic_domains/git-pipeline | in-system | domain/runtime-code | paired | [git-pipeline](logic_domains/git-pipeline/logic_readme.md) | [changes](logic_domains/git-pipeline/logic_change.md) | self | active |
| MOD-TOOLCHAIN | logic_domains/toolchain | in-system | domain/runtime-code | paired | [toolchain](logic_domains/toolchain/logic_readme.md) | [changes](logic_domains/toolchain/logic_change.md) | self | active |
| MOD-TEMPLATES | references/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-templates) | [active changes](logic_change.md) | self | active |
| MOD-HISTORY | logic_version/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-history) | [active changes](logic_change.md) | self | active |

领域目录（大纲）：MOD-GIT-PIPELINE 职权 `scripts/git_sync.py`、`scripts/init_recall.py`（init/sync/hook/回填）；MOD-TOOLCHAIN 职权其余 `scripts/`、`tests/`、双平台入口（CLI、审计、校验、查询、路由）。

<a id="scope-mod-templates"></a>
### MOD-TEMPLATES: 模板与参考文档

- scope_path: references/；适用规则与不变量：RULE-009, RULE-022, INV-001, INV-002；代码地图入口：references/（模板文件是字段名的权威来源；领域模板 references/logic-domain-template.md）

<a id="scope-mod-history"></a>
### MOD-HISTORY: 历史决策记录

- scope_path: logic_version/；适用规则与不变量：RULE-001, RULE-003, INV-003, INV-004；代码地图入口：logic_version/records/、logic_version/index.md

## 功能意图与用户流程

用户视角层，与代码地图（系统视角）互补；只在宪法维护（RULE-014）。新增或调整用户可见功能前先对照本节做融入分析。

### 功能意图登记

| intent_id | 功能入口 | intent（服务的用户目标） | 流程位置 | 关联规则 | 代码锚点 | last_verified |
|---|---|---|---|---|---|---|
| INT-20260816-001 | logic_readme 功能意图与用户流程层 | AI 从文档恢复功能级产品逻辑与用户流程，无需重扫代码库 | FLOW-002#1 | RULE-014 | logic_readme.md | 2026-08-16 |
| INT-20260816-002 | recall init | 一条命令完成 Git + Recall 接入，无需手动配置 | FLOW-001#1 | RULE-010 | scripts/init_recall.py | 2026-08-16 |
| INT-20260816-003 | 文档阅读（SKILL/宪法/根账本 → 命中领域） | AI 在修改前恢复设计上下文，不从代码反推意图；宪法必读，领域按需，SKILL 细节按需读 references | FLOW-002#1 | RULE-001..004, RULE-018, RULE-022 | SKILL.md; references/document-model.md | 2026-09-04 |
| INT-20260816-004 | recall new | 修改前留下"为什么改"的决策记录骨架 | FLOW-002#3 | RULE-003, RULE-012 | scripts/create_ver.py | 2026-08-16 |
| INT-20260816-005 | recall sync | 一条命令保存并同步全部进度，无需手写 Git 序列 | FLOW-001#3, FLOW-002#5 | RULE-011, RULE-013 | scripts/git_sync.py | 2026-08-16 |
| INT-20260816-006 | recall status / recall list | 快速了解系统当前状态（领域数、各账本议案、未提交/未推送）与最近决策 | FLOW-003#1 | RULE-010, RULE-012, RULE-018, RULE-021 | scripts/recall.py; scripts/recall_common.py; scripts/link_ver_git.py | 2026-09-04 |
| INT-20260816-007 | recall query file/commit/intent | 双向追溯：从代码定位"为什么改"，从功能意图定位"要改哪里" | FLOW-003#2 | RULE-013, RULE-014 | scripts/link_ver_git.py | 2026-08-16 |
| INT-20260816-008 | recall validate / audit | 确认宪法、领域文档、记录与 Git 状态一致；审计门按治理模式分档 | FLOW-003#3 | RULE-009, RULE-015, RULE-018, RULE-023 | scripts/validate.py; scripts/recall_audit/integrity.py | 2026-09-04 |
| INT-20260816-009 | recall conflicts | 新需求与现行规则矛盾时提前暴露，交用户裁决 | FLOW-004#1 | RULE-021 | scripts/detect_conflicts.py | 2026-09-03 |
| INT-20260816-010 | 项目接入流程（references/project-onboarding.md） | 存量/新项目模块化建立文档初稿：接入时建宪法骨架 + 至少一个领域，按触发时机逐模块补全 | FLOW-005#2 | RULE-016, RULE-018 | references/project-onboarding.md | 2026-09-04 |
| INT-20260816-011 | 一二级拆分（宪法 + 部门法，RULE-018） | 大小项目统一两级：改哪个领域读哪份部门法，宪法保证全局约束；领域过大拆小部门 | FLOW-005#4 | RULE-018 | references/logic-domain-template.md; scripts/recall_audit/integrity.py | 2026-09-04 |
| INT-20260903-001 | 收尾归零（logic_temp 工作区产物台账 + status/validate 残留提示） | 任务结束时工作区只剩交付物，AI 不遗留探针脚本、临时测试与草稿 | FLOW-002#6 | RULE-020 | references/logic-temp-template.md; scripts/recall.py; scripts/validate.py | 2026-09-03 |
| INT-20260903-002 | recall route | 按目标路径/关键词得到本次应读的文档清单与上下文成本，只导入命中的领域 | FLOW-002#1 | RULE-018 | scripts/route_docs.py | 2026-09-04 |

编号 `INT-YYYYMMDD-NNN` 与 CHG/VER 的 `intent_traceability` 链共用；"代码锚点"列支撑 `recall query intent`，validate 检查锚点存在性。

### 用户流程

- FLOW-001 首次接入：1. recall init → INT-20260816-002；2. 配置远端（可选）；3. recall sync → INT-20260816-005
- FLOW-002 日常修改：1. 读宪法与根账本，`recall route <目标>` 后读命中领域的 readme/change → INT-20260816-001, INT-20260816-003, INT-20260903-002；2. 判定通道并修改代码；3. recall new（medium/high）→ INT-20260816-004；4. git commit（带 Ref 行）；5. recall sync（hook 回填 after_commit）→ INT-20260816-005；6. 收尾归零：medium/high 清零 logic_temp 台账并删除 working，simple 在汇报列处置清单，`recall status` 核对无待处置文件 → INT-20260903-001
- FLOW-003 追溯审查：1. recall status/list → INT-20260816-006；2. recall query → INT-20260816-007；3. recall validate → INT-20260816-008
- FLOW-004 冲突澄清：1. recall conflicts → INT-20260816-009；2. 在所属账本标注；3. 用户裁决后按通道实施
- FLOW-005 项目接入（文档初稿）：1. recall init → INT-20260816-002；2. 建宪法骨架 + 至少一个领域 + 意图访谈（存量模块登记 pending-docs）→ INT-20260816-010；3. 按触发时机逐模块补全到所属领域 → INT-20260816-010；4. 领域 readme 越过目标行数时 AI 建议拆小部门、用户确认后新建领域并登记（修宪案）→ INT-20260816-011

### 操作直觉约束

- UXI-001: 用户不手写 commit message，sync 自动保存；来源：VER-20260811-003；影响：INT-20260816-005
- UXI-002: 一条命令完成一个用户目标，不要求用户记忆多步 Git 序列；来源：用户确认 2026-08-07；影响：INT-20260816-002, INT-20260816-005
- UXI-003: hook 与自动化绝不提交用户未提交的其他文件；自动保存只提交已跟踪文件的变更，未跟踪新文件默认排除并列出（`--include-new` 或 `git add` 才是用户的明确要求）；来源：VER-20260816-005；影响：INT-20260816-005
- UXI-004: 全部 CLI 在非交互与重定向环境可用；来源：VER-20260808-002；影响：全部 INT 条目
- UXI-005: 新会话默认延续：用户不需要重述项目哲学与背景，文档即交接；现行规则仅在用户明确否定时才修改；来源：VER-20260816-004；影响：INT-20260816-001, INT-20260816-003
- UXI-006: 工具绝不静默删除文件：status/validate 只列出未跟踪待处置文件，台账是给代理和用户看的处置清单而非删除脚本输入；来源：VER-20260903-001；影响：INT-20260903-001, INT-20260816-006, INT-20260816-008

## 责任记录约定

- 个人项目，`governance_mode: personal`；`owner: self` 表示维护责任，`changed_by` 记录实际修改人或 AI 代理；`decision_confirmed_by` 记录用户确认；Git 作为外部治理控制保证历史追溯；本地文件、单用户读写、无需部署，运维细节见 MOD-GIT-PIPELINE

## 代码、生成物与运行数据边界

| path/pattern | artifact_class | layer | read/write | environment | source_of_truth | safe_to_edit | safe_to_rebuild | retention/sensitivity |
|---|---|---|---|---|---|---|---|---|
| SKILL.md, logic_readme.md, logic_domains/*/logic_readme.md, references/ | source | runtime-code | read/write | local | 各文件自身 | yes | N/A | permanent |
| logic_change.md, logic_domains/*/logic_change.md | source | runtime-code | read/write | local | 各账本自身 | yes | N/A | temporary |
| logic_version/records/ | source | runtime-code | read-only | local | VER-*.md | no | N/A | permanent |

## 数据与控制流

```
用户请求 → 宪法 logic_readme.md → 根 logic_change.md（修宪议案 + 公报）→ recall route 目标 → 命中领域 readme/change → 代码/测试
        → 通道 simple / medium / high（不确定则升级）
[medium/high] 计划 + 影响 + 验证；在所属账本建 CHG（触宪 → 根；领域事务 → 领域）+ 根公报一行 + working/slug/logic_temp.md 台账
[high]        另读相关 VER、找消费者、比较方案、迁移与回滚 → 用户确认 proposal_revision
        → 实施 → 测试 → docs_impact，同一变更中更新所属 readme → [规则/行为变化] 固化 VER-*、登记索引 → 台账清零 → 关闭 CHG（账本 + 公报）
        → 提交；自动同步未启用时自行推送；simple 在汇报列处置清单
```

## 消费者与公共契约

| 契约/数据 | 生产者 | 真实消费者 | 环境 | 当前兼容要求 | 证据 |
|---|---|---|---|---|---|
| SKILL.md、宪法与领域 logic 文档 | Recall 项目 | Claude Code, Codex（读取现行制度与议案） | local | 稳定格式（表格结构、CHG-ID 格式、范围登记表列） | 审计静态门 |
| VER-* 记录 | Recall 项目 | AI（回忆历史） | local | 只读，不修改 | 记录格式 |

旧行为消费者：见 MOD-TOOLCHAIN"旧行为消费者"节（审计器部署形态、审计 JSON 口径）。

## 不可破坏约束

- INV-001: 现行 logic_readme 每 scope 唯一：根为宪法；二级只能是范围登记表中 `paired` 登记的 `logic_domains/<domain>/logic_readme.md`（RULE-018）；禁止 logic_readme-v2.md 等未登记平行正文；来源：SKILL.md 核心原则；验证：审计静态门（nonroot/parallel 检测含领域豁免 + 范围路由对账 + 根目录 Markdown 覆盖对账）
- INV-002: logic_change 每级一份、与 readme 成对：根账本 + 每个已登记领域一份；同一 CHG 正文只在一处账本，根公报索引全部活跃 CHG；禁止未登记副本；来源：RULE-018；验证：审计 nonroot 检测 + 领域账本/公报核查 + validate 公报告警
- INV-003: logic_version/records/ 中 VER-* 记录的**语义内容**不可修改，只能追加新记录（勘误建 `status: correction` 新记录）；唯一合法的既有文件变更是受管理 hook 对 `after_commit` 占位符的一次性回填（RULE-013）；来源：不可变决策记录原则；验证：Git 历史
- INV-004: 历史记录不保存代码快照，只保存设计逻辑；来源：逻辑回档原则；验证：VER-* 内容审查

## 兼容与迁移制度

- 对象与策略：文档模型（单文件 + 可选子文档 → 宪法 + 部门法）为 replace，无并行版本；存量项目迁移 = 新建领域目录、登记 paired 行、搬迁规则行（步骤见 references/project-onboarding.md）；工具对旧式 readme-only 子文档与无领域项目继续接受，只给 advisory 提示
- 回滚能力：Git 版本控制

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | INV-001/002 平行真源与领域豁免、RULE-018 领域路由/公报/密度、RULE-019 覆盖对账、RULE-022 分包、RULE-014 意图层 | `python -m unittest discover -s tests` | 全部 OK | unittest 输出 |
| integration | 宪法与领域文档结构、CHG 生命周期、代理入口 | `python scripts/audit_logic_map.py . --current-state` | Static gate PASS；无 nonroot/parallel；Density 无 exceeds-hard-limit | 审计报告 |
| integration | RULE-014/015/018 一致性对账 | `python scripts/validate.py` | 无错误；规则计数含领域文档；CHG 跨账本发现；无公报缺失告警 | 验证报告 |
| integration | RULE-018 按需导入 | `python scripts/recall.py route scripts/git_sync.py` | 清单为宪法 + 根账本 + MOD-GIT-PIPELINE readme/change，不含 MOD-TOOLCHAIN | 终端输出 |
| integration | INV-003 VER-* 不可变 | `git log --follow -- logic_version/records/` | 已发布 VER-* 只有创建与占位符回填提交 | Git log |

## 有效决策索引

| version_id | 决策摘要 | 关联规则 | 记录 |
|---|---|---|---|
| VER-20260808-001 | Recall 系统结构重组：账本完整性、平行真源、反膨胀强制点、状态机补全 | RULE-001..004 | [记录](logic_version/records/logic_version-20260808-001-recall-restructure.md) |
| VER-20260808-002 | 工具链与自审一致性加固：跨平台入口、schema 对齐、嵌套项目根排除 | RULE-005..009 | [记录](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) |
| VER-20260811-001 | Git 自动同步：初始化默认配置、提交后 hook、显式脏工作区提交与手动 sync | RULE-010..011 | [记录](logic_version/records/logic_version-20260811-001-git-auto-sync.md) |
| VER-20260811-002 | CLI 胶水层接口修复：recall new 断裂、记录命名统一、冲突检测失灵、脏工作区不阻断同步 | RULE-011..012 | [记录](logic_version/records/logic_version-20260811-002-cli-interface-repair.md) |
| VER-20260811-003 | 默认自动保存上传（--manual 可切手动）与 after_commit 自动回填 | RULE-011, RULE-013 | [记录](logic_version/records/logic_version-20260811-003-auto-save-sync.md) |
| VER-20260816-001 | 功能级"功能意图与用户流程"层（INT/FLOW/UXI）、CHG 需求拆解字段与 plan 模式落盘约定 | RULE-014 | [记录](logic_version/records/logic_version-20260816-001-feature-intent-layer.md) |
| VER-20260816-002 | 追溯链断裂修复：recall new 回填链路、自动保存文件清单与回填双通道、INT 编号统一、validate 对账与漂移哨兵 | RULE-011, RULE-013..015 | [记录](logic_version/records/logic_version-20260816-002-traceability-repair.md) |
| VER-20260816-003 | 需求↔架构语义链路补全：模块化项目接入流程、CHG 三字段归档搬入 VER、INT 代码锚点与 query intent 反向查询 | RULE-014..016 | [记录](logic_version/records/logic_version-20260816-003-semantic-link.md) |
| VER-20260816-004 | 会话默认延续原则、层级化子 logic 文档（readme-only 登记拆分）与舍弃方案归档 | RULE-014, RULE-017..018 | [记录](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) |
| VER-20260816-005 | 审查整改：自动保存排除新文件、rejected 豁免、子文档检查覆盖、漂移度量、脱管归档与覆盖对账、双模板合并、引用纪律 | RULE-011, RULE-015, RULE-018..019 | [记录](logic_version/records/logic_version-20260816-005-audit-remediation.md) |
| VER-20260831-001 | 入口模板短路由化、SKILL 首屏重排与 personal 模式 ADR 可选澄清 | RULE-018..019 | [记录](logic_version/records/logic_version-20260831-001-entry-slim-skill-front.md) |
| VER-20260831-002 | 自身入口瘦身收尾、意图层按治理模式分档、create_ver 编码合规；Git 表面收缩立案待决 | RULE-008, RULE-014, RULE-019 | [记录](logic_version/records/logic_version-20260831-002-arch-simplify.md) |
| VER-20260903-001 | 收尾归零：logic_temp 工作区产物台账（medium/high 必建）、status/validate 未跟踪残留提示、"完成"定义纳入清理 | RULE-020 | [记录](logic_version/records/logic_version-20260903-001-cleanup-ledger.md) |
| VER-20260903-002 | 结构性与上下文成本优化：CLI 胶水故障修复与子进程冒烟、recall_common 公共基础设施、未推送提交提示、SKILL 按需披露、审计器分层包、Density 目标提示 | RULE-010, RULE-021, RULE-022 | [记录](logic_version/records/logic_version-20260903-002-structure-context-cost.md) |
| VER-20260903-003 | 结构性收口：Git 调用与 porcelain 解析单源 + 测试级静态门、审计器大函数按检查拆分、CHG 字段按治理模式分档、审计 `--json` UTF-8、根文档压缩 | RULE-008, RULE-021..023 | [记录](logic_version/records/logic_version-20260903-003-structural-closure.md) |
| VER-20260903-004 | 一二级拆分法：宪法（根）+ 部门法（logic_domains 领域 readme/change 成对）、根账本公报、`recall route` 按需导入、密度分档；本仓库拆为 2 个领域 | RULE-015, RULE-018, RULE-021 | [记录](logic_version/records/logic_version-20260903-004-two-level-docs.md) |

完整索引见 [logic_version/index.md](logic_version/index.md)。

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)（修宪议案 + 全项目公报；领域议案正文在各领域账本）
- 相关 CHG-ID：none

## 当前限制

- 仅支持个人或小团队使用（low-concurrency）；不提供实际权限控制（依赖 Git）；归档需人工判断——`recall new` 只生成骨架，"为什么"必须手写
- 宪法的行数由规则行与意图层决定：规则行是刚性的、一行一条；本文档越过 150 行目标（Density advisory）时先把领域相关规则迁入部门法，再压缩 FLOW/UXI；禁止未登记的第二现行文档（INV-001/002）
- 两级模型对存量项目是强制目标而非即时门禁：无领域的项目只收到 `constitution-without-domains` 提示、静态门不失败；是否让"无领域"与硬上限越线进门属待立案议题
- 工具链侧限制（validate CHG-ID 正则、VER 模板假错误、`recall route` 子串匹配、审计器超限函数）见 MOD-TOOLCHAIN"当前限制"

## 修改检查清单

- [ ] 是否触及上游/下游契约、持久化数据或已部署行为？是否仍满足所有 INV 条目？
- [ ] 议案是否写在所属账本（触宪 → 根；领域事务 → 领域）并在根公报登记？新增或修改的关键规则是否已链接到具体 VER？
- [ ] 是否已更新范围登记表、所属 readme 的代码地图、测试和历史索引？
- [ ] 是否先完成代码逻辑、数据边界和现有实现可并入性分析？是否在修改后生成/补齐测试案例并审核前后结果？
- [ ] 是否存在未被更高优先级指令裁定的新旧需求矛盾？
- [ ] 本次新建的临时/探针/草稿文件是否已删除或登记保留理由（RULE-020）？
