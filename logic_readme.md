# Recall Skill Logic

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
- last_verified: 2026-09-03
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: SKILL.md, logic_readme.md
- source_decisions: VER-20260808-001, VER-20260808-002, VER-20260811-001, VER-20260811-002, VER-20260811-003, VER-20260816-001, VER-20260816-002, VER-20260816-003, VER-20260816-004, VER-20260816-005, VER-20260831-001, VER-20260831-002, VER-20260903-001, VER-20260903-002, VER-20260903-003
- intent_summary: 为 AI 提供项目设计逻辑的回忆机制，记录"为什么这么设计"而非代码快照，避免上下文膨胀
- intent_sources: 用户访谈 2026-08-07
- decision_validity: valid
- validity_evidence: 用户确认 2026-08-07

## 目标与边界

- 负责：记录项目设计决策的逻辑推理、关键取舍、影响分析；提供"为什么这么设计"的回忆能力
- 不负责：代码版本管理（由 Git 负责）、完整代码快照、原始对话记录、详细实现细节
- 上级制度：无
- 允许的例外：none

## 范围登记与归属

- canonical_readme: logic_readme.md
- canonical_change: logic_change.md
- owned_paths: SKILL.md, logic_readme.md, logic_change.md, logic_version/, references/, scripts/, tests/, recall.bat, recall.sh, .gitattributes, AGENTS.md, CLAUDE.md, README.md
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
| RULE-005 | key | 批处理入口必须纯 ASCII + CRLF | cmd.exe 按字节偏移定位命令，多字节字符加 LF 换行会错行执行注释片段 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | .gitattributes + recall.bat 实测 | valid | 2026-08-08 | self |
| RULE-006 | key | 脚本调用外部命令必须用 argv 列表，禁止 shell=True | 多行 commit message 会被 shell 截断，用户输入可注入命令 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | init_recall.py / link_ver_git.py 注入测试 | valid | 2026-08-08 | self |
| RULE-007 | key | 嵌套项目根不计入本项目审计 | 自带 `scope: .` 的子目录属于另一个项目，按模块审计会用其 module_id 顶掉真实根文档 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | audit_logic_map.py 静态门 | valid | 2026-08-08 | self |
| RULE-008 | ordinary | CLI 必须可非交互运行，且重定向下不崩 | CI、容器和 AI 代理环境没有 tty；Windows 重定向后 stdout 走 ANSI 代码页 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | 空 stdin 与重定向实测；审计器 `--json` 重定向落盘为 UTF-8（VER-20260903-003） | valid | 2026-09-03 | self |
| RULE-009 | ordinary | 校验脚本的字段名以 references/ 模板为准 | schema 漂移会让检查静默失效或报假错误 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | validate.py 记录发现测试 | valid | 2026-08-08 | self |
| RULE-010 | key | `recall init` 默认启用仓库级 Git 自动同步并安装受管理的 post-commit hook；**自动同步是默认值而不是保证**——仓库未跑过 `recall init`（无 `recall.autoSync` 配置或受管理 hook 缺失，典型是只接入文档未接管道的半接入项目）时推送责任回落到提交方：每批提交必须在同一轮内推送，本地不得长期领先远端，核对入口是 `git status -sb` 首行的 `ahead` 计数 | 让已提交的 Recall 逻辑和代码及时进入配置的远端，减少本地历史与远端漂移；半接入项目会静默退化成「只提交不推送」，而一批提交里只推前几个会把远端停在测试已进、实现未进的中间提交上（2026-09-02 消费项目实例：7 个提交只推 1 个，CI 18 项失败） | [VER-20260811-001](logic_version/records/logic_version-20260811-001-git-auto-sync.md) | 用户要求；推送责任子句为 2026-09-02 用户确认（消费项目事故复盘） | git_sync.py + hook 集成测试；推送责任子句由 `recall status` 的"未推送提交"行与 `recall validate` 的非阻断告警核对（`recall_common.unpushed_commit_count`，无上游分支时不提示；tests/test_recall_cli.py `UnpushedHintTests`、tests/test_validate.py `UnpushedCommitTests`） | valid | 2026-09-03 | self |
| RULE-011 | key | `recall sync` 默认自动保存：脏工作区的**已跟踪变更**自动提交后同步（`recall.autoCommit`，`--manual` 切换手动）；**未跟踪新文件默认排除**，仅 `--include-new` 或用户先 `git add` 时纳入，提交前列出文件清单与被排除清单；post-commit hook 场景绝不自动提交其他脏文件 | 自动化不得上传用户未明确要求的文件：非交互环境下事后警告拦不住已推上远端的私人文件，默认必须是"新文件留在本地" | [VER-20260816-005](logic_version/records/logic_version-20260816-005-audit-remediation.md) | 用户确认 | git_sync.py 单元测试（默认排除/`--include-new` 双向用例） | valid | 2026-08-16 | self |
| RULE-012 | key | 决策记录文件名统一为 `logic_version-YYYYMMDD-NNN-*.md`，创建方与所有发现方共用同一正则 | create_ver/status/validate/list 曾各用一套命名，记录对部分工具静默不可见 | [VER-20260811-002](logic_version/records/logic_version-20260811-002-cli-interface-repair.md) | 复现验证 | tests/test_recall_cli.py | valid | 2026-08-11 | self |
| RULE-013 | key | 提交后自动回填决策记录的 after_commit，双通道定位记录：commit message 的 Ref 行 + 本次提交内规范命名的记录文件；识别新旧两种占位符（`- after_commit:`/`- commit:`）且只按整个字段行匹配（叙述文字中引用的占位符不回填）；无法回填时打印警告而非静默跳过；内部提交通过环境变量防止 hook 递归 | 只认 Ref 行时自动保存提交（无 Ref）永不触发回填；裸子串替换曾把记录叙述文字里引用的占位符改成哈希，污染不可变记录正文 | [VER-20260816-002](logic_version/records/logic_version-20260816-002-traceability-repair.md) | 复现验证 | tests/test_git_sync.py（含端到端与字段行锚定） | valid | 2026-08-16 | self |
| RULE-014 | key | logic_readme 维护功能级"功能意图与用户流程"层（INT/FLOW/UXI 按条目模块化，intent_id 统一 `INT-YYYYMMDD-NNN` 完整格式，登记表含代码锚点列支撑反向查询）；medium/high CHG 在实施前记录需求拆解与融入分析（raw_request/decomposition/fit_analysis），归档时三字段原样搬入 VER 记录（需求保全）；同议题多方案竞争时，落选方案连同其需求原文与否决原因随胜出 VER 的方案分析归档，已独立立案的落选 CHG 建 `status: rejected` 的 VER 记录并同样搬运三字段；plan 模式产出批准后、动代码前按通道落盘；意图层维护深度按治理模式分档：personal 轻量档（INT 必维护、FLOW 可合并、UXI 按需），collaborative 及以上全量，档位定义见 references/governance-modes.md | 功能级产品逻辑此前无处沉淀，AI 每会话从代码反推意图；CHG 归档即删除，三字段不搬入不可变记录则需求拆解只剩 git 考古可查，落选方案直接删除亦然；单人模式逐条维护三层的行数成本与收益不成比例 | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) | 用户确认 | 本文件"功能意图与用户流程"节 + scripts/validate.py + references/governance-modes.md | valid | 2026-08-31 | self |
| RULE-015 | ordinary | `recall validate` 覆盖一致性对账：VER 三处登记与撞号（`rejected`/`cancelled`/`rolled-back` 记录豁免有效决策索引、登记进 index.md 即可，反向登记告警）、INT/FLOW/UXI 引用有效性与代码锚点存在性、medium/high CHG 三字段、VER 需求保全三字段、字段行占位符未回填、RULE/INT 重复按定义行判定且**已登记子文档纳入同一套检查**（RULE-018）；漂移度量：统计自上次触及 logic 文档以来累积的提交数，超过 10 个升级为警告；post-commit hook 保留非阻断漂移提醒 | 文档是代码理解的持久缓存，缓存腐烂与登记缺失静默失效是本系统反复出现的失败模式；被否决的方案不得登记为"有效决策"，拆分后的子文档不得进入无检查区，无人阅读的提醒需要可观测数字 | [VER-20260816-005](logic_version/records/logic_version-20260816-005-audit-remediation.md) | 复现验证 | scripts/validate.py + tests/test_validate.py | valid | 2026-08-16 | self |
| RULE-016 | key | 项目接入采用模块化渐进：接入时只建根骨架（文档控制、范围登记表、代码地图顶层入口、访谈式 INT/FLOW 初稿），存量模块登记 `pending-docs`；此后仅在新项目开始使用时或用户单独要求时补全对应模块；AI 代码扫描产出标 `code-derived`，意图层必须经用户确认后落盘 | `recall init` 只建 Git 管道，文档内容从哪来此前无流程；一次性全量扫描在存量项目不可行，未经确认的 AI 推断意图会污染真源 | [VER-20260816-003](logic_version/records/logic_version-20260816-003-semantic-link.md) | 用户确认 | references/project-onboarding.md + SKILL.md 接入章节 | valid | 2026-08-16 | self |
| RULE-017 | key | 会话默认延续：新会话或上下文压缩后以现行 logic 文档与活跃议案为准继续（新会话视作新人接手，文档即交接），不要求用户重述背景；仅当用户明确指出现行规则或代码有问题时才修改现行制度；模糊点先按现行逻辑分析并给出建议再咨询（SKILL 原则 5/11） | 协作协议此前只活在对话历史，每次压缩后用户被迫重讲元规则，正是 Recall 要消灭的 rescan | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) | 用户确认 | SKILL.md 核心原则 11 | valid | 2026-08-16 | self |
| RULE-018 | key | 层级化子文档：根 logic_readme 为总规章与路由中台；子模块复杂度达标时由 AI 提出拆分建议、经用户确认后在模块目录建 `logic_readme.md` 并以 `doc_policy: readme-only` 登记进范围登记表；修改子模块先读根再读子文档，跨模块变更在同一变更中更新全部相关文档；根规章优先于子文档；**RULE/INT 编号空间全项目唯一（含子文档）**；子文档与根文档同受行数上限与 validate 一致性检查约束；logic_change 与 logic_version 全项目唯一；未登记子文档仍为平行真源违规 | 单文件+锚点适合小项目，大项目全量阅读低效；按需分批披露上下文，但未经登记的拆分会重演平行真源失败模式，无检查的子文档会成为膨胀区与撞号区 | [VER-20260816-004](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) | 用户确认 | scripts/audit_logic_map.py 范围路由 + scripts/validate.py 子文档检查 | valid | 2026-08-16 | self |
| RULE-019 | key | 文档引用纪律：规范的语义正文只存在于 logic_readme 的规则行；SKILL、模板、生命周期文档、CLAUDE/AGENTS 入口等其他位置只保留"见 RULE-XXX"式指针与纯操作步骤；审计对账"git 跟踪的顶层 Markdown 入口 ⊆ owned_paths ∪ unmapped_paths"，未登记条目使静态门失败 | 同一语义散布多处（曾达 5 处）每次更新需 N 连改、漏一处即漂移；改名换姓的制度副本（README 重述通道、SUMMARY 总结）平行真源检测抓不到，只能靠登记对账机器可见 | [VER-20260816-005](logic_version/records/logic_version-20260816-005-audit-remediation.md) | 用户确认 | scripts/audit_logic_map.py 根目录覆盖对账 + tests/test_audit_logic_map.py | valid | 2026-08-16 | self |
| RULE-020 | key | 收尾归零：任务完成态 = 交付物就位 + 本次新建的非交付物（探针脚本、临时测试、草稿、调试输出）已删除或经用户同意保留 + 最终汇报列出处置清单；`medium`/`high` 通道必建 `logic_version/working/` 下以 version_slug 命名目录内的 `logic_temp.md`（位置由审计器校验），在其"工作区产物台账"登记 path / artifact_kind / disposition / reason / cleaned_at，台账清零（无未执行的 delete、无 pending）方可关闭 CHG 并删除 working 目录；`simple` 通道不建文件，只在最终汇报列清单；`recall status` 把未跟踪文件单列为待处置候选，`recall validate` 对未被 .gitignore 覆盖的未跟踪文件非阻断告警；**任何工具都不自动删除文件**，处置由代理逐项执行并对用户可见 | AI 解题产生的临时文件在任务"完成"后无人负责；RULE-011 默认排除未跟踪文件保住了远端却让本地垃圾隐形累积，status/validate 此前只报笼统的"未提交变更"；只有把收尾写进"完成"的定义才能覆盖不建 CHG 的 simple 通道 | [VER-20260903-001](logic_version/records/logic_version-20260903-001-cleanup-ledger.md) | 用户确认 2026-09-03（A/B 二选一选 B） | references/logic-temp-template.md 台账表 + scripts/recall_common.py `classify_porcelain` + scripts/validate.py `report_untracked_leftovers` + tests/test_recall_cli.py + tests/test_validate.py；**已被 git add 的垃圾无自动检测**，只能靠台账或汇报清单 | valid | 2026-09-03 | self |
| RULE-021 | key | CLI 基础设施只此一份：项目根查找、Git 子进程调用（argv 列表 + 固定 utf-8 解码、只去尾部空白）、`git status --porcelain` 解析（`parse_porcelain`/`classify_porcelain`）与输出流编码防护统一在 `scripts/recall_common.py`，各脚本（含 `recall_audit` 包）导入使用、不得自行实现，**`scripts/` 下除 recall_common 外禁止直接 `subprocess` 调用**（测试级静态门）；`recall.py` 每条子命令都有以子进程方式真跑的胶水层冒烟测试（断言退出码与关键输出），纯函数测试不能替代 | 五份脚本各写一份根查找、七份各写一份编码防护，坏掉的总是没测试的那一份：`recall status` 在中文 Windows 因 git 子进程未指定 utf-8 崩溃、`recall conflicts` 把子命令名当项目根永远失败而 CI 全绿；公共封装建立后仍有 7 处绕过，`strip()` 吃掉 porcelain 首行空格使路径错位——文字规则拦不住第二份实现，只有机器门能 | [VER-20260903-002](logic_version/records/logic_version-20260903-002-structure-context-cost.md)；[VER-20260903-003](logic_version/records/logic_version-20260903-003-structural-closure.md) | 复现验证 + 用户确认 2026-09-03 | scripts/recall_common.py + tests/test_recall_common.py（`SingleGitInfrastructureGateTests` 静态扫描、porcelain 用例）+ tests/test_recall_cli.py `CliGlueSmokeTests` | valid | 2026-09-03 | self |
| RULE-022 | key | 按需披露：SKILL.md 首屏只保留路由问题、三通道、默认读取顺序、核心原则、调用模式/命令与"按需读取"表，其余细节（文档模型、Git 同步、治理模式、项目接入、代理入口）只在 references/ 保留一份并由表指向；审计器按层分包在 `scripts/recall_audit/`（constants→textutil→fsclassify→changes→semantic→integrity→formal→archive→report→cli，只许向下依赖），`scripts/audit_logic_map.py` 只做重新导出的入口，禁止再向单文件追加实现；**新写或重构的函数不超过 150 行**，检查按 `_check_*` 小函数拆分并共用上下文对象（integrity/archive 已全部达标，其余模块存量超限函数见"当前限制"）；Density 段对越过目标值（SKILL 130 / readme 250 / change 150 行、单条 CHG 40 行）的文档给出 advisory 提示 | SKILL 每次触发约 6300 token、其中近半是代理极少当场需要的目录模型与 Git 细节；审计器单文件 6764 行、最大函数 650 行，是修改成本最高且最易再出 RULE-009 式静默漂移的地方；拆包只搬迁不瘦身则最大函数仍 648 行；行数目标此前只写在文档里、无机器信号 | [VER-20260903-002](logic_version/records/logic_version-20260903-002-structure-context-cost.md)；[VER-20260903-003](logic_version/records/logic_version-20260903-003-structural-closure.md) | 用户确认 2026-09-03（"重点优化结构性与上下文成本，按需调用"；"认可你提到的问题"） | SKILL.md 84 行 + references/document-model.md、references/git-sync.md + scripts/recall_audit/（函数长度见 VER-20260903-003 验证节）+ tests/test_audit_logic_map.py（经 facade 访问；拆分前后 JSON 基线逐字节一致） | valid | 2026-09-03 | self |
| RULE-023 | key | CHG 字段要求按治理模式分档：审计器 current-state 门对 `governance_mode: personal` 的 CHG 块只强制 `status`、`effective: false`、`proposal_revision`、`recall_route`、`changed_by`，以及进入 implementing/verifying/promoting 前的 `decision_confirmed_by` + `decision_confirmed_at`（用户确认不随治理模式降级）；collaborative/compliance 层字段（协调、决策门、语义审查、运行暴露、历史保留、追溯链等，清单见 `PERSONAL_OPTIONAL_CHANGE_FIELDS`）**缺则不查、写则照查**；块自身 governance_mode 优先于账本模式，两者都缺按完整要求处理；collaborative 模式与 `--formal-review` 要求不变 | 审计器此前对活跃 CHG 无差别要求 9 个协调字段与完整决策/审查字段，与 references/field-vocabulary.md "personal 8 个字段"矛盾，personal CHG 普遍 100+ 行（本仓库 CHG-20260903-001 为 110 行），"当前限制"挂了两个版本 | [VER-20260903-003](logic_version/records/logic_version-20260903-003-structural-closure.md) | 用户确认 2026-09-03 | scripts/recall_audit/changes.py `change_field_tier` + tests/test_audit_logic_map.py `GovernanceTierTests`（slim personal 块零 issue、同块 collaborative 报缺、未声明模式按 full、personal 实施前须确认、写了的可选字段照查） | valid | 2026-09-03 | self |

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|
| SKILL.md | source/runtime-code | Recall skill 主入口，定义核心原则和使用方式 | AI 读取 | 指导 AI 行为 | SKILL.md | yes | none |
| logic_readme.md | source/runtime-code | 当前生效的规则和代码地图（唯一真相源） | AI 读取 | 当前制度 | logic_readme.md | yes | none |
| logic_change.md | source/runtime-code | 活跃的修改记录（未生效） | AI 读取/写入 | 修改议案 | logic_change.md | yes | none |
| logic_version/ | source/runtime-code | records/ 历史决策记录（逻辑回档，只追加）+ index.md 索引 | AI 按需读取 | 设计逻辑回忆 | VER-*.md / index.md | records no / index yes | none |
| references/ | source/runtime-code | 模板文件和参考文档；字段名的权威来源 | AI 按需读取 | 文档模板 | 模板文件 | yes | none |
| recall.bat / recall.sh / .gitattributes | source/runtime-code+config | 双平台 CLI 入口（探测 python/py/python3 后转发）；.gitattributes 固定 *.bat CRLF、*.sh LF（RULE-005） | 命令行参数 | 子命令输出与退出码 | 入口文件 | yes | none |
| scripts/recall_common.py | source/runtime-code | 公共基础设施（RULE-021）：`find_project_root`、`run_git`/`git_output`、`parse_porcelain`/`classify_porcelain`、`force_utf8_output`、`unpushed_commit_count` | 起点路径 / git 参数 / porcelain 文本 | 项目根 / (ok, stdout, stderr) / 分类路径 / 计数 | 脚本文件 | yes | tests/test_recall_common.py |
| scripts/recall.py | source/runtime-code | CLI 调度器；转发到各子命令；`status` 分列已跟踪变更、未跟踪待处置文件（RULE-020）与未推送提交（RULE-010） | 子命令与参数 | 退出码 | 脚本文件 | yes | tests/test_recall_cli.py（含子进程冒烟） |
| scripts/audit_logic_map.py | source/runtime-code | 审计器入口 facade（RULE-022）：重新导出 `recall_audit` 包全部公开名字，保持命令行、`--json` 与测试访问路径不变；须与 `scripts/recall_audit/` 整目录部署 | 项目根路径 | 审计报告与静态门退出码 | 脚本文件 | yes | tests/test_audit_logic_map.py |
| scripts/recall_audit/ | source/runtime-code | 审计器分层包：constants → textutil → fsclassify → changes（CHG 检查、`change_field_tier` 分档 RULE-023）→ semantic → integrity（路由/议案/current-state 门）→ formal → archive（归档/索引/入口/密度）→ report → cli（强制 UTF-8 输出）；只许向下依赖，函数 ≤150 行 | 项目根路径 | 审计报告 dict | 包目录 | yes | tests/test_audit_logic_map.py |
| scripts/validate.py | source/runtime-code | 一致性校验：RULE/CHG/VER 与 Git 状态、子文档编号空间、漂移度量、未跟踪残留告警（RULE-020） | 项目根路径 | 验证报告 | 脚本文件 | yes | tests/test_validate.py |
| scripts/init_recall.py | source/runtime-code | 首次初始化：Git 仓库、身份、.gitignore、首次提交 | CLI 参数或环境变量 | 初始化结果 | 脚本文件 | yes | none |
| scripts/git_sync.py | source/runtime-code | 配置 Git 自动同步策略、安装受管理 hook、自动保存提交、回填 after_commit、拉取变基并推送 | CLI 参数、仓库 Git 配置、远端 | 同步结果与退出码 | 脚本文件 | yes | tests/test_git_sync.py |
| scripts/create_ver.py | source/runtime-code | 按模板创建 VER-* 决策记录（规范文件名取号） | 描述与 scope | 记录文件 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/link_ver_git.py | source/runtime-code | 关联查询：文件/提交 ↔ 决策记录；intent 反向查询（意图 → 规则 → 记录 → 代码锚点） | 文件路径、commit 或 INT-ID | 关联报告 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/detect_conflicts.py | source/runtime-code | 规则间与议案-规则冲突的启发式检测；`main(argv)` 经公共根查找定位文档 | logic_readme/logic_change | 冲突报告与退出码（0 无冲突 / 2 有潜在冲突） | 脚本文件 | yes | tests/test_recall_cli.py |
| tests/ | test/test-fixture | test_audit_logic_map（审计器）、test_git_sync（同步/回填）、test_recall_cli（CLI 胶水 + 子进程冒烟）、test_validate（validate 检查函数）、test_recall_common（公共基础设施 + RULE-021 静态门） | unittest | 断言 | 测试文件 | yes | `python -m unittest discover -s tests` |
| references/examples/audit-repro-legacy/ | test/test-fixture | 审计复现夹具；自带 `scope: .`，按嵌套项目根排除 | 审计脚本读取 | 复现场景 | 夹具文件 | yes | none |

- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: 所有 Recall 文档为 source/runtime-code 层
- version_root: logic_version/
- temp_root: logic_version/working/
- 子范围路由：无（单一根文档）
- unmapped_paths: agents/ (Codex 配置), .agents/ (代理私有目录), .claude/ (代理私有目录), logic_version/backups/ (归档快照), .github/ (仓库社区配置), CONTRIBUTING.md (社区贡献指南、非真源), SECURITY.md (安全政策、非真源)

### 范围登记表

| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [logic_readme.md](logic_readme.md) | [logic_change.md](logic_change.md) | self | active |
| MOD-TEMPLATES | references/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-templates) | [active changes](logic_change.md) | self | active |
| MOD-HISTORY | logic_version/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-history) | [active changes](logic_change.md) | self | active |

<a id="scope-mod-templates"></a>
### MOD-TEMPLATES: 模板与参考文档

- scope_path: references/；适用规则与不变量：RULE-009, INV-001, INV-002；代码地图入口：references/（模板文件是字段名的权威来源）

<a id="scope-mod-history"></a>
### MOD-HISTORY: 历史决策记录

- scope_path: logic_version/；适用规则与不变量：RULE-001, RULE-003, INV-003, INV-004；代码地图入口：logic_version/records/、logic_version/index.md

## 功能意图与用户流程

用户视角层，与代码地图（系统视角）互补；新增或调整用户可见功能前先对照本节做融入分析（RULE-014）。

### 功能意图登记

| intent_id | 功能入口 | intent（服务的用户目标） | 流程位置 | 关联规则 | 代码锚点 | last_verified |
|---|---|---|---|---|---|---|
| INT-20260816-001 | logic_readme 功能意图与用户流程层 | AI 从文档恢复功能级产品逻辑与用户流程，无需重扫代码库 | FLOW-002#1 | RULE-014 | logic_readme.md | 2026-08-16 |
| INT-20260816-002 | recall init | 一条命令完成 Git + Recall 接入，无需手动配置 | FLOW-001#1 | RULE-010 | scripts/init_recall.py | 2026-08-16 |
| INT-20260816-003 | 文档三件套阅读（SKILL/logic_readme/logic_change） | AI 在修改前恢复设计上下文，不从代码反推意图；SKILL 首屏只载路由/通道/原则，细节按需读 references | FLOW-002#1 | RULE-001..004, RULE-022 | SKILL.md; references/document-model.md | 2026-09-03 |
| INT-20260816-004 | recall new | 修改前留下"为什么改"的决策记录骨架 | FLOW-002#3 | RULE-003, RULE-012 | scripts/create_ver.py | 2026-08-16 |
| INT-20260816-005 | recall sync | 一条命令保存并同步全部进度，无需手写 Git 序列 | FLOW-001#3, FLOW-002#5 | RULE-011, RULE-013 | scripts/git_sync.py | 2026-08-16 |
| INT-20260816-006 | recall status / recall list | 快速了解系统当前状态与最近决策 | FLOW-003#1 | RULE-010, RULE-012, RULE-021 | scripts/recall.py; scripts/recall_common.py; scripts/link_ver_git.py | 2026-09-03 |
| INT-20260816-007 | recall query file/commit/intent | 双向追溯：从代码定位"为什么改"，从功能意图定位"要改哪里" | FLOW-003#2 | RULE-013, RULE-014 | scripts/link_ver_git.py | 2026-08-16 |
| INT-20260816-008 | recall validate / audit | 确认文档、记录与 Git 状态一致；审计门按治理模式分档，personal 项目的 CHG 不被 compliance 字段拖到 100+ 行 | FLOW-003#3 | RULE-009, RULE-023 | scripts/validate.py; scripts/recall_audit/changes.py | 2026-09-03 |
| INT-20260816-009 | recall conflicts | 新需求与现行规则矛盾时提前暴露，交用户裁决 | FLOW-004#1 | RULE-021 | scripts/detect_conflicts.py | 2026-09-03 |
| INT-20260816-010 | 项目接入流程（references/project-onboarding.md） | 存量/新项目模块化建立文档初稿：接入时建根骨架，按触发时机逐模块补全 | FLOW-005#2 | RULE-016 | references/project-onboarding.md | 2026-08-16 |
| INT-20260816-011 | 层级化子文档拆分（RULE-018） | 大项目按模块分批披露上下文：改哪个模块读哪份子文档，跨模块才读全量 | FLOW-005#4 | RULE-018 | references/project-onboarding.md; scripts/audit_logic_map.py | 2026-08-16 |
| INT-20260903-001 | 收尾归零（logic_temp 工作区产物台账 + status/validate 残留提示） | 任务结束时工作区只剩交付物，AI 不遗留探针脚本、临时测试与草稿 | FLOW-002#6 | RULE-020 | references/logic-temp-template.md; scripts/recall.py; scripts/validate.py | 2026-09-03 |

编号使用 `INT-YYYYMMDD-NNN`，与 CHG/VER 的 `intent_traceability` 链共用同一编号空间与格式（登记日期为条目首次登记日）。"代码锚点"列支撑反向查询 `recall query intent <INT-ID>`（意图 → 规则 → 决策记录 → 文件）；validate 检查锚点路径存在性。

### 用户流程

- FLOW-001 首次接入：1. recall init → INT-20260816-002；2. 配置远端（可选）；3. recall sync → INT-20260816-005
- FLOW-002 日常修改：1. 读文档 → INT-20260816-001, INT-20260816-003；2. 判定通道并修改代码；3. recall new（medium/high）→ INT-20260816-004；4. git commit（带 Ref 行）；5. recall sync（hook 回填 after_commit）→ INT-20260816-005；6. 收尾归零：medium/high 清零 logic_temp 台账并删除 working，simple 在汇报列处置清单，`recall status` 核对无待处置文件 → INT-20260903-001
- FLOW-003 追溯审查：1. recall status/list → INT-20260816-006；2. recall query → INT-20260816-007；3. recall validate → INT-20260816-008
- FLOW-004 冲突澄清：1. recall conflicts → INT-20260816-009；2. 在 logic_change.md 标注；3. 用户裁决后按通道实施
- FLOW-005 项目接入（文档初稿）：1. recall init → INT-20260816-002；2. 建根骨架 + 意图访谈（存量模块登记 pending-docs）→ INT-20260816-010；3. 按触发时机（新项目使用时/用户单独要求时）逐模块补全 → INT-20260816-010；4. 模块复杂度达标时 AI 建议拆分子文档、用户确认后登记 readme-only → INT-20260816-011

### 操作直觉约束

- UXI-001: 用户不手写 commit message，sync 自动保存；来源：VER-20260811-003；影响：INT-20260816-005
- UXI-002: 一条命令完成一个用户目标，不要求用户记忆多步 Git 序列；来源：用户确认 2026-08-07；影响：INT-20260816-002, INT-20260816-005
- UXI-003: hook 与自动化绝不提交用户未提交的其他文件；自动保存只提交已跟踪文件的变更，未跟踪新文件默认排除并列出（`--include-new` 或 `git add` 才是用户的明确要求）；来源：VER-20260816-005；影响：INT-20260816-005
- UXI-004: 全部 CLI 在非交互与重定向环境可用；来源：VER-20260808-002；影响：全部 INT 条目
- UXI-005: 新会话默认延续：用户不需要重述项目哲学与背景，文档即交接；现行规则仅在用户明确否定时才修改；来源：VER-20260816-004；影响：INT-20260816-001, INT-20260816-003
- UXI-006: 工具绝不静默删除文件：status/validate 只列出未跟踪待处置文件，台账是给代理和用户看的处置清单而非删除脚本输入，清理由代理逐项执行并在汇报中可见；来源：VER-20260903-001；影响：INT-20260903-001, INT-20260816-006, INT-20260816-008

## 责任记录约定

- 个人项目，`governance_mode: personal`；`owner: self` 表示维护责任，`changed_by` 记录实际修改人或 AI 代理
- `decision_confirmed_by` 记录用户确认；`semantic_reviewed_by` 记录代码语义审查（个人项目允许 self）
- Git 作为外部治理控制，保证历史追溯

## 代码、生成物与运行数据边界

| path/pattern | artifact_class | layer | read/write | environment | source_of_truth | safe_to_edit | safe_to_rebuild | retention/sensitivity |
|---|---|---|---|---|---|---|---|---|
| SKILL.md | source | runtime-code | read/write | local | SKILL.md | yes | N/A | permanent |
| logic_readme.md | source | runtime-code | read/write | local | logic_readme.md | yes | N/A | permanent |
| logic_change.md | source | runtime-code | read/write | local | logic_change.md | yes | N/A | temporary |
| logic_version/records/ | source | runtime-code | read-only | local | VER-*.md | no | N/A | permanent |
| references/ | source | runtime-code | read/write | local | 模板文件 | yes | N/A | permanent |

## 数据与控制流

```
用户请求 → 读 logic_readme.md（规则、代码地图、意图层）→ logic_change.md（活跃议案）→ 相关代码/测试
        → 判断通道 simple / medium / high（不确定则升级）
[medium/high] 计划 + 影响范围 + 验证方式；建 CHG（raw_request/decomposition/fit_analysis）与 working/<slug>/logic_temp.md 台账
[high]        另读相关 VER 记录、找消费者、比较方案、设计迁移与回滚 → 用户确认 proposal_revision
        → 实施 → 更新/运行测试 → docs_impact，同一变更中更新 logic_readme.md
[medium 规则/行为变化, high] 固化 VER-* 并登记 index.md / 有效决策索引 → 台账清零、删除 working → 关闭 CHG
[simple]                       最终汇报列出新建文件处置清单
        → 提交；自动同步未启用时自行推送（status / validate 报告未推送提交）
```

## 消费者与公共契约

| 契约/数据 | 生产者 | 真实消费者 | 环境 | 当前兼容要求 | 证据 |
|---|---|---|---|---|---|
| SKILL.md | Recall 项目 | Claude Code, Codex | local | 向后兼容 | 文档格式 |
| logic_readme.md | Recall 项目 | AI（读取当前规则） | local | 稳定格式 | 表格结构 |
| logic_change.md | Recall 项目 | AI（读写修改记录） | local | 稳定格式 | CHG-ID 格式 |
| VER-* 记录 | Recall 项目 | AI（回忆历史） | local | 只读，不修改 | 记录格式 |

### 旧行为消费者

- `scripts/audit_logic_map.py` 单文件拷贝部署：VER-20260903-002 起不再支持，必须与 `scripts/recall_audit/` 整目录部署；已知消费者只有指向本仓库的技能目录符号链接（`~/.claude/skills/recall`，`ls -la` 2026-09-03 核实），无需迁移
- 审计 JSON：collaborative 项目输出不变；personal 项目自 VER-20260903-003 起 `proposal_issues` 只会减少（RULE-023 缺则不查）。其他契约（CLI 命令名与退出码、`--json` 结构、模板字段名、记录文件名）无旧行为消费者

## 不可破坏约束

- INV-001: 现行 logic_readme 每 scope 唯一：根文档唯一；子文档必须以 readme-only 登记在根范围登记表且经用户确认拆分后才可存在（RULE-018）；禁止 logic_readme-v2.md 等未登记平行正文；来源：SKILL.md 核心原则；验证：审计静态门（nonroot/parallel 检测 + 范围路由对账 + 根目录 Markdown 覆盖对账，RULE-019）
- INV-002: logic_change.md 必须唯一（不随子文档拆分，全项目仅根一份），禁止创建副本；来源：SKILL.md 核心原则；验证：文件系统检查
- INV-003: logic_version/records/ 中 VER-* 记录的**语义内容**不可修改，只能追加新记录（勘误建 `status: correction` 新记录）；唯一合法的既有文件变更是受管理 hook 对 `after_commit` 占位符的一次性回填（RULE-013）；来源：不可变决策记录原则；验证：Git 历史（每记录除创建与占位符回填外无其他修改提交）
- INV-004: 历史记录不保存代码快照，只保存设计逻辑；来源：逻辑回档原则；验证：VER-* 内容审查

## 兼容与迁移制度

- 对象与策略：审计器部署形态（单文件 → facade + 分层包）与 personal 模式审计口径（RULE-023），均为 replace，无并行版本、无过渡期；持久化状态只有 Markdown 文件系统
- 旧行为消费者与移除条件：见上节；回滚能力：Git 版本控制

## 安全、性能与运维

- 权限/隐私：本地文件，无特殊权限要求；性能/并发：单用户读写；部署：无需部署；日志/监控：Git 历史
- 自动同步：仓库级 `recall.autoSync=true` 控制受管理的 `post-commit` hook；`recall.autoCommit=true`（默认）时 `recall sync` 自动提交已跟踪变更（未跟踪新文件默认排除，`--include-new` 纳入）；远端缺失、网络失败或变基冲突只告警，不丢弃本地提交

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | 审计器行为：INV-001/002 平行真源、RULE-007 嵌套根、RULE-009 记录 schema、RULE-018 子文档路由与上限、RULE-019 覆盖对账、RULE-022 分包/拆函数后行为不变、RULE-023 字段分档 | `python tests/test_audit_logic_map.py`；`python scripts/audit_logic_map.py . --current-state` / `--formal-review` / `--json --current-state` | 全部 OK（74）；静态门 PASS；无 parallel/nonroot 报告；夹具不在 Non-root 列表；JSON 可解析且与拆分前基线一致 | unittest 输出 + 审计报告 |
| integration | RULE-009/RULE-015 validate 一致性对账 | `python scripts/validate.py` | 决策记录被发现且无假缺失字段；三处登记、撞号、意图层引用、CHG 三字段、占位符检查出现且无假错误 | 验证报告 |
| integration | INV-003 VER-* 不可变 | `git log --follow -- logic_version/records/` | 已发布 VER-* 只有创建与占位符回填提交 | Git log |
| runtime | RULE-005 批处理入口不错行 | `recall status` / `recall help` | 无 `is not recognized` 输出 | 终端输出 |
| runtime | RULE-008 非交互可用与重定向不崩 | `recall init < /dev/null`；`echo "" \| recall init`；`recall init --non-interactive`；`recall help > out.txt`；`recall status > out.txt`；`python scripts/audit_logic_map.py . --json --current-state > out.json` | 均退出 0，无 UnicodeEncodeError，落盘为 UTF-8 | 终端输出 / 输出文件 |
| unit | RULE-010/RULE-011/RULE-013 自动同步、自动保存与回填 | `python -m unittest tests.test_git_sync` | 全部 OK：配置、hook、pull/push、自动保存（已跟踪变更）、未跟踪默认排除与 `--include-new`、手动模式、递归防护、回填双通道、字段行锚定、漂移哨兵、端到端回填 | unittest 输出 |
| integration | RULE-010/012/014/015/020/021 CLI 胶水层与 validate 检查函数：接口一致性、子进程冒烟（help/status/conflicts/validate 真跑）、未推送提示、status/validate 已跟踪与未跟踪分列、rejected 豁免、子文档编号空间 | `python -m unittest tests.test_recall_cli tests.test_validate` | 全部 OK；status 退出 0 且无 Traceback；conflicts 从子目录运行不报"未找到 logic_readme.md"；有残留→warning，无残留→无告警 | unittest 输出 |
| unit | RULE-021 公共基础设施与机器门 | `python -m unittest tests.test_recall_common` | 全部 OK：根查找/回退、run_git 非仓库不抛异常、porcelain 首行前导空格保留、parse/classify_porcelain 重命名与引号、无上游返回 None、utf-8 解码、scripts/ 下无直接 subprocess 调用 | unittest 输出 |
| runtime | RULE-010 自动同步 CLI 可发现 | `python scripts/recall.py help`; `python scripts/git_sync.py --help` | 帮助包含 `sync`、`--auto`、`--manual`、`--no-auto-sync` 和 `--disable` | 终端输出 |
| runtime | RULE-020 status 待处置提示 | 新建一个未跟踪文件后 `recall status` | 输出单列"未跟踪文件（待处置候选）"并列出路径；删除后消失 | 终端输出 |

INV-004（VER-* 不含代码快照）不在此表：它是内容判断，只能人工审查，列在"不可破坏约束"里。此表只登记可执行的验证命令。

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
| VER-20260816-003 | 需求↔架构语义链路补全：模块化项目接入流程、CHG 三字段归档搬入 VER（需求保全）、INT 代码锚点与 query intent 反向查询 | RULE-014..016 | [记录](logic_version/records/logic_version-20260816-003-semantic-link.md) |
| VER-20260816-004 | 会话默认延续原则、层级化子 logic 文档（readme-only 登记拆分）与舍弃方案归档 | RULE-014, RULE-017..018 | [记录](logic_version/records/logic_version-20260816-004-handoff-hierarchy.md) |
| VER-20260816-005 | 审查整改：自动保存排除新文件、rejected 豁免、子文档检查覆盖、漂移度量、脱管归档与覆盖对账、双模板合并、引用纪律 | RULE-011, RULE-015, RULE-018..019 | [记录](logic_version/records/logic_version-20260816-005-audit-remediation.md) |
| VER-20260831-001 | 入口模板短路由化、SKILL 首屏重排与 personal 模式 ADR 可选澄清 | RULE-018..019 | [记录](logic_version/records/logic_version-20260831-001-entry-slim-skill-front.md) |
| VER-20260831-002 | 自身入口瘦身收尾、意图层按治理模式分档、create_ver 编码合规；Git 表面收缩立案待决 | RULE-008, RULE-014, RULE-019 | [记录](logic_version/records/logic_version-20260831-002-arch-simplify.md) |
| VER-20260903-001 | 收尾归零：logic_temp 工作区产物台账（medium/high 必建）、status/validate 未跟踪残留提示、"完成"定义纳入清理 | RULE-020 | [记录](logic_version/records/logic_version-20260903-001-cleanup-ledger.md) |
| VER-20260903-002 | 结构性与上下文成本优化：CLI 胶水故障修复与子进程冒烟、recall_common 公共基础设施、未推送提交提示、SKILL 按需披露、审计器分层包、Density 目标提示 | RULE-010, RULE-021, RULE-022 | [记录](logic_version/records/logic_version-20260903-002-structure-context-cost.md) |
| VER-20260903-003 | 结构性收口：Git 调用与 porcelain 解析单源 + 测试级静态门、审计器大函数按检查拆分（JSON 基线不变）、CHG 字段按治理模式分档、审计 `--json` UTF-8、根文档压缩 | RULE-008, RULE-021..023 | [记录](logic_version/records/logic_version-20260903-003-structural-closure.md) |

完整索引见 [logic_version/index.md](logic_version/index.md)。

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
- 相关 CHG-ID：none

## 当前限制

- 仅支持个人或小团队使用（low-concurrency）；不提供实际权限控制（依赖 Git）；归档需人工判断——`scripts/create_ver.py` 只生成骨架，"为什么"必须手写
- 静态门只检查文档结构与工具链约定，不能证明代码语义、消费者或运行行为；Density 与 logic_temp 检查只是 advisory，不使静态门失败——消费项目 logic_change 越过硬上限 21 倍仍 PASS（2026-09-03 eduai 实测），是否让硬上限越线进门属待立案议题
- 功能意图层随功能数线性增长：personal 模式先用轻量档（RULE-014 分档，见 references/governance-modes.md）；接近行数上限（目标 250 / 硬 400）时先压缩 FLOW、合并同类 UXI、合并同命令测试行；压缩仍不足且模块复杂度达标时按 RULE-018 经用户确认拆分子文档，禁止未登记的第二现行文档（INV-001/002）。本文档压缩后仍越过 250 目标（22 条规则行 + 12 条 INT 是刚性行数），拆分 `scripts/` 子文档待用户裁决
- 自动保存提交（"自动保存本地修改"）无 Ref 行、不承载 why：积累过多会稀释追溯链，medium/high 变更应使用带 Ref 行的语义提交（validate 漂移度量超过 10 个时告警，RULE-015）；`recall conflicts` 为关键词级启发式，语义冲突仍需人工澄清
- 未推送检测依赖上游分支：`recall status` / `recall validate` 用 `@{u}..HEAD` 计数，未配置上游或无远端时不提示；已推送但远端 CI 失败不在检测范围
- 收尾归零依赖代理自律：`recall status` / `recall validate` 只能看见未跟踪且未被忽略的文件；已被 `git add` 或已提交的垃圾、为调试改动后未还原的已跟踪文件，机器识别不到，只能靠 logic_temp 台账或汇报清单（RULE-020）
- 审计器函数长度：integrity.py / archive.py 已按检查拆分（最大 648 → 65 行），changes.py（334/152）、semantic.py（398/248）、formal.py（296/178）、report.py（459/350/165）仍有 9 个函数超过 150 行，按同一方法（先冻结 JSON 基线、拆分后逐字节对比）分批处理
- `recall status` / `recall validate` 的 CHG 发现只认 `CHG-YYYYMMDD-NNN`，消费项目使用 `CHG-YYYYMMDD-<slug>` 时 validate 的三字段检查静默跳过（审计器可识别）；validate 的 VER 必填段与 after_commit 正则只认最小模板与裸 SHA，扩展模板项目会得到假错误——两者为待立案的工具缺口（2026-09-03 eduai 实测）

## 修改检查清单

- [ ] 是否触及上游/下游契约、持久化数据或已部署行为？是否仍满足所有 INV 条目？
- [ ] 是否需要议案、ADR、迁移、回滚或弃用计划？新增或修改的关键规则是否已链接到具体 VER？
- [ ] 是否已更新根范围登记、关联代码地图、测试和历史索引？
- [ ] 是否先完成代码逻辑、数据边界和现有实现可并入性分析？是否在修改后生成/补齐测试案例并审核前后结果？
- [ ] 是否存在未被更高优先级指令裁定的新旧需求矛盾？
- [ ] 本次新建的临时/探针/草稿文件是否已删除或登记保留理由（RULE-020：medium/high 台账清零，simple 汇报清单，`recall status` 无待处置文件）？
