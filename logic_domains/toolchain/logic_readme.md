# Toolchain Domain Logic

部门法（二级 readme，RULE-018）：管辖 CLI 入口与公共基础设施、审计器、校验器、记录/查询/冲突/路由脚本与测试套件。宪法是根 `logic_readme.md`，根规章优先于本文档。Git 管道见 MOD-GIT-PIPELINE。

## 文档控制

- doc_id: LOGIC-RECALL-TOOLCHAIN
- module_id: MOD-TOOLCHAIN
- scope: logic_domains/toolchain
- scope_path: logic_domains/toolchain
- parent: ../../logic_readme.md
- parent_module_id: MOD-ROOT
- membership: in-system
- scope_type: domain
- layer: runtime-code
- module_doc_policy: paired
- status: active
- owner: self
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:https://github.com/fuqiyue/recall@main
- governance_verification: recorded
- governance_verified_at: 2026-08-08
- effective_from: 2026-09-04
- last_verified: 2026-09-04
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: scripts/recall.py, scripts/recall_common.py, scripts/recall_audit/, scripts/validate.py
- source_decisions: VER-20260808-002, VER-20260811-002, VER-20260816-002, VER-20260816-005, VER-20260903-002, VER-20260903-003, VER-20260903-004, VER-20260904-001, VER-20260904-003, VER-20260904-004
- intent_summary: 全部 CLI 在非交互与重定向环境可用、跨平台入口不错行、机器检查只此一份实现且自身有测试
- intent_sources: INT-20260816-004, INT-20260816-006, INT-20260816-007, INT-20260816-008, INT-20260816-009, INT-20260903-002（宪法功能意图登记）
- decision_validity: valid
- validity_evidence: 用户确认 2026-09-03（两级拆分）；规则行随 VER 链接

## 目标与边界

- 负责：`recall` 双平台入口与调度、`recall_common` 公共基础设施、审计器（`audit_logic_map.py` + `recall_audit/`）、`validate`、`new`/`query`/`list`/`conflicts`/`route` 子命令、tests/ 与审计夹具
- 不负责：Git 管道（MOD-GIT-PIPELINE）、文档制度本身（宪法）
- 上级制度：根 logic_readme.md（RULE-001..004、RULE-014、RULE-016..020、RULE-022）
- 允许的例外：none

## 范围登记与归属

- canonical_readme: logic_domains/toolchain/logic_readme.md
- canonical_change: logic_domains/toolchain/logic_change.md
- owned_paths: scripts/recall.py, scripts/recall_common.py, scripts/audit_logic_map.py, scripts/recall_audit/, scripts/validate.py, scripts/create_ver.py, scripts/link_ver_git.py, scripts/detect_conflicts.py, scripts/route_docs.py, recall.bat, recall.sh, .gitattributes, tests/test_audit_logic_map.py, tests/test_recall_cli.py, tests/test_validate.py, tests/test_recall_common.py, references/examples/
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-005 | key | 批处理入口必须纯 ASCII + CRLF | cmd.exe 按字节偏移定位命令，多字节字符加 LF 换行会错行执行注释片段 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | .gitattributes + recall.bat 实测 | valid | 2026-08-08 | self |
| RULE-006 | key | 脚本调用外部命令必须用 argv 列表，禁止 shell=True | 多行 commit message 会被 shell 截断，用户输入可注入命令 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | init_recall.py / link_ver_git.py 注入测试 | valid | 2026-08-08 | self |
| RULE-007 | key | 嵌套项目根不计入本项目审计 | 自带 `scope: .` 的子目录属于另一个项目，按模块审计会用其 module_id 顶掉真实根文档 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | audit_logic_map.py 静态门 | valid | 2026-08-08 | self |
| RULE-008 | ordinary | CLI 必须可非交互运行，且重定向下不崩 | CI、容器和 AI 代理环境没有 tty；Windows 重定向后 stdout 走 ANSI 代码页 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | 空 stdin 与重定向实测；审计器 `--json` 重定向落盘为 UTF-8（VER-20260903-003） | valid | 2026-09-03 | self |
| RULE-009 | ordinary | 校验脚本的字段名以 references/ 模板为准 | schema 漂移会让检查静默失效或报假错误 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | validate.py 记录发现测试 | valid | 2026-08-08 | self |
| RULE-012 | key | 决策记录文件名统一为 `logic_version-YYYYMMDD-NNN-*.md`，创建方与所有发现方共用同一正则 | create_ver/status/validate/list 曾各用一套命名，记录对部分工具静默不可见 | [VER-20260811-002](../../logic_version/records/logic_version-20260811-002-cli-interface-repair.md) | 复现验证 | tests/test_recall_cli.py | valid | 2026-08-11 | self |
| RULE-015 | ordinary | `recall validate` 一致性对账：① VER 登记：records 文件与 index.md 双向对账、撞号检测；index.md 首列接受裸 ID、指向记录的 Markdown 链接与反引号三种形态，其余形态报"首列格式不识别"而非"未登记"；生效 VER 须出现在宪法有效决策索引或被宪法/领域任一规则行的"决策记录"列直接链接（RULE-002），`rejected`/`cancelled`/`rolled-back` 记录只登记 index.md、进宪法索引则告警；② INT/FLOW/UXI 引用有效性与代码锚点存在性：`path#symbol` / `path:line` 剥离后查路径，符号在目标文件中找不到单独告警（子串核查，不做语法解析）；意图表 `来源` 列缺列提示、`inferred`/`code-derived`/空值告警、格式不识别告警（RULE-014/016）；③ medium/high CHG 三字段、VER 需求保全三字段、字段行占位符未回填；VER 必填段以模板为准且模板有几套 schema 就认几套（快速模板 / 扩展 schema 任一满足即通过，都不满足按缺失最少的一套报并注明 schema 名），after_commit 接受裸 SHA、反引号与 `commit:` 前缀，commit 有效性在项目根核查；④ RULE/INT 重复按定义行判定，宪法与全部已登记领域文档同一套检查，CHG 跨全部账本提取，领域 CHG 未进根公报告警（RULE-018）；⑤ `recall conflicts` 跨账本输出"一法多议案"（同 RULE 多议案未互指）与"旧议案 vs 新法"（规则 last_reviewed 晚于议案日期）两节；⑥ 漂移度量：自上次触及 logic 文档以来的提交数超过 10 升级为警告，post-commit hook 保留非阻断提醒 | 文档是代码理解的持久缓存，缓存腐烂与登记缺失静默失效是本系统反复出现的失败模式 | [VER-20260816-005](../../logic_version/records/logic_version-20260816-005-audit-remediation.md)；[VER-20260903-004](../../logic_version/records/logic_version-20260903-004-two-level-docs.md)；[VER-20260904-001](../../logic_version/records/logic_version-20260904-001-intent-provenance-conflicts.md)；[VER-20260904-002](../../logic_version/records/logic_version-20260904-002-docs-consolidation.md)；[VER-20260904-003](../../logic_version/records/logic_version-20260904-003-validate-compat.md) | 复现验证 | scripts/validate.py（`rule_linked_versions`、`RECORD_SCHEMAS`、`split_code_anchor`）+ scripts/detect_conflicts.py + tests/test_validate.py + tests/test_recall_cli.py | valid | 2026-09-04 | self |
| RULE-021 | key | CLI 基础设施只此一份：① 项目根查找、Git 子进程调用（argv 列表 + 固定 utf-8 解码、只去尾部空白）、`git status --porcelain` 解析、输出流编码防护、领域登记表读取（`registered_domains`/`change_ledgers`）与议案编号正则（`CHANGE_ID_PATTERN`/`CHANGE_ID_RE`，日期段后接受 NNN 或 slug）统一在 `scripts/recall_common.py`，各脚本（含 `recall_audit` 包）导入使用、不得自行实现；② `scripts/` 下除 recall_common 外禁止直接 `subprocess` 调用（测试级静态门）；③ 同一事实各命令只用一种口径：规则数按"当前制度"定义行统计宪法 + 全部领域（`status`/`validate`/`conflicts` 必须报同一数），VER 发现共用 RULE-012 正则，CHG 发现（validate / conflicts / 审计器）共用 `CHANGE_ID_PATTERN`，模板占位符识别只用 textutil `contains_angle_placeholder`（`<…>` 且不在行内代码段内，`>128`、`` `<meta>` ``、`->` 不算），Markdown 链接可达性只查代码段之外的链接（`audit_links` 先剔除围栏代码块与行内代码，链接标题不算路径，坏链条目带 `broken-link:` 前缀），空账本 `active_changes` 的 `none`/`0` 同义（`is_empty_ledger_count` 一处判定）；④ `recall.py` 每条子命令都有以子进程真跑的胶水层冒烟测试（断言退出码与关键输出），纯函数测试不能替代 | 多份脚本各写一份根查找与编码防护、各数一遍规则，坏掉的总是没测试的那一份；文字规则拦不住第二份实现，只有机器门能 | [VER-20260903-002](../../logic_version/records/logic_version-20260903-002-structure-context-cost.md)；[VER-20260903-003](../../logic_version/records/logic_version-20260903-003-structural-closure.md)；[VER-20260904-002](../../logic_version/records/logic_version-20260904-002-docs-consolidation.md)；[VER-20260904-003](../../logic_version/records/logic_version-20260904-003-validate-compat.md)；[VER-20260904-004](../../logic_version/records/logic_version-20260904-004-audit-link-ledger-compat.md) | 复现验证 + 用户确认 2026-09-03 | scripts/recall_common.py + tests/test_recall_common.py（`SingleGitInfrastructureGateTests` 静态扫描、porcelain 用例、领域登记表用例）+ tests/test_recall_cli.py `CliGlueSmokeTests`、`count_rule_definitions`、`ChangeIdSingleSourceTests` 用例 | valid | 2026-09-04 | self |
| RULE-023 | key | CHG 字段按治理模式分档：① current-state 门对 `governance_mode: personal` 的 CHG 块只强制 `status`、`effective: false`、`proposal_revision`、`recall_route`、`changed_by`，以及进入 implementing 及之后状态前的 `decision_confirmed_by` + `decision_confirmed_at`（用户确认不随模式降级）；② collaborative/compliance 层字段（清单 `PERSONAL_OPTIONAL_CHANGE_FIELDS`）缺则不查、写则照查；块自身 governance_mode 优先于账本模式，两者都缺按完整要求处理；collaborative 与 `--formal-review` 要求不变；③ 协调检查以整本账本为单位，`depends_on`/`conflicts_with`/`blocked_by` 目标跨全部账本解析（根议案与领域议案互写 `conflicts_with` 是规定解法）；④ 一法多议案检查不分档：`authority_surfaces` 的 RULE 是议案目标规则，跨账本比对——同一规则被多个活跃 CHG 指向而未互写 `conflicts_with` → `shared-rule-target-needs-explicit-conflict`（同账本 `unmarked-authority-surface-overlap`），目标规则 `last_reviewed` 晚于议案 `created`/`last_status_change` → `rule-changed-after-proposal`（须重核 based_on），拟议制度提到 RULE 却无 authority_surfaces → `mentions-rule-without-authority-surfaces` | 无差别要求 9 个协调字段使 personal CHG 普遍 100+ 行；冲突检测是安全网，不该随 personal 一起被省掉 | [VER-20260903-003](../../logic_version/records/logic_version-20260903-003-structural-closure.md)；[VER-20260904-001](../../logic_version/records/logic_version-20260904-001-intent-provenance-conflicts.md) | 用户确认 2026-09-03；一法多议案为 2026-09-04 用户提问后确认 | scripts/recall_audit/changes.py `change_field_tier`、`cross_ledger_rule_conflicts` + tests/test_audit_logic_map.py | valid | 2026-09-04 | self |

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| recall.bat / recall.sh / .gitattributes | source/runtime-code+config | public | 双平台 CLI 入口（探测 python/py/python3 后转发）；.gitattributes 固定 *.bat CRLF、*.sh LF（RULE-005） | 命令行参数 | 子命令输出与退出码 | 入口文件 | yes | none |
| scripts/recall_common.py | source/runtime-code | internal | 公共基础设施（RULE-021）：`find_project_root`、`run_git`/`git_output`、`parse_porcelain`/`classify_porcelain`、`force_utf8_output`、`unpushed_commit_count`、`registered_domains`/`change_ledgers`（RULE-018 领域登记表读取）、`CHANGE_ID_PATTERN`/`CHANGE_ID_RE`（议案编号只此一份） | 起点路径 / git 参数 / porcelain 文本 / 项目根 | 项目根 / (ok, stdout, stderr) / 分类路径 / 计数 / 领域与账本列表 | 脚本文件 | yes | tests/test_recall_common.py |
| scripts/recall.py | source/runtime-code | public | CLI 调度器；转发到各子命令，`audit` 子命令转发审计器（默认 `--current-state`）；`status` 分列规则数（`count_rule_definitions`，宪法 + 领域定义行，RULE-021）、领域数、各账本 CHG 计数、已跟踪变更、未跟踪待处置文件（RULE-020）与未推送提交（RULE-010） | 子命令与参数 | 退出码 | 脚本文件 | yes | tests/test_recall_cli.py（含子进程冒烟） |
| scripts/route_docs.py | source/runtime-code | public | `recall route`：按目标路径匹配领域 `owned_paths`、按关键词匹配领域正文（`_keyword_searchable_text` 跳过"不负责"行与表头）、按 INT-ID/关键词命中宪法意图行再经锚点/关联规则路由；输出宪法 + 命中领域 readme/change 的读取清单、行数、估算 token 与命中的用户意图及来源（RULE-018 按需导入） | 路径、关键词或 INT-ID、`--json` | 读取清单 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/audit_logic_map.py | source/runtime-code | public | 审计器入口 facade（RULE-022）：重新导出 `recall_audit` 包全部公开名字，保持命令行、`--json` 与测试访问路径不变；须与 `scripts/recall_audit/` 整目录部署 | 项目根路径 | 审计报告与静态门退出码 | 脚本文件 | yes | tests/test_audit_logic_map.py |
| scripts/recall_audit/ | source/runtime-code | internal | 审计器分层包：constants → textutil → fsclassify → changes（CHG 检查、`change_field_tier` 分档 RULE-023）→ semantic → integrity（路由/议案/current-state 门，含领域文档与根公报核查 RULE-018、代码地图可选 `contract_class` 列取值校验 `_code_map_row_issues`）→ formal → archive（归档/索引/入口/密度分档）→ report → cli（强制 UTF-8 输出）；占位符判定只用 textutil `contains_angle_placeholder`、链接可达性 `audit_links` 先剔除代码段（`FENCED_CODE_RE`/`CODE_SPAN_RE`），CHG 标题正则由 recall_common `CHANGE_ID_PATTERN` 构造；只许向下依赖，新写函数 ≤150 行 | 项目根路径 | 审计报告 dict | 包目录 | yes | tests/test_audit_logic_map.py |
| scripts/validate.py | source/runtime-code | public | 一致性校验：RULE/CHG/VER 与 Git 状态、宪法 + 领域编号空间、VER 登记（index.md 首列三形态 `VER_ROW_RE` + 规则行反链 `rule_linked_versions`，RULE-002）、VER 必填段双 schema（`RECORD_SCHEMAS`）、代码锚点 `split_code_anchor`、跨账本 CHG（共享 `CHANGE_ID_PATTERN`）与公报登记、漂移度量、未跟踪残留告警（RULE-015/018/020） | 项目根路径 | 验证报告 | 脚本文件 | yes | tests/test_validate.py |
| scripts/create_ver.py | source/runtime-code | public | 按模板创建 VER-* 决策记录（规范文件名取号） | 描述与 scope | 记录文件 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/link_ver_git.py | source/runtime-code | public | 关联查询：文件/提交 ↔ 决策记录；intent 反向查询（意图 → 规则 → 记录 → 代码锚点） | 文件路径、commit 或 INT-ID | 关联报告 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/detect_conflicts.py | source/runtime-code | public | 规则间与议案-规则冲突的启发式检测（宪法 + 全部领域、全部账本）+ 一法多议案（同 RULE 多议案未互指）+ 旧议案 vs 新法（规则 last_reviewed 晚于议案）；`main(argv)` 经公共根查找定位文档 | logic 文档 | 冲突报告与退出码（0 无冲突 / 2 有潜在冲突） | 脚本文件 | yes | tests/test_recall_cli.py |
| tests/ | test/test-fixture | internal | test_audit_logic_map（审计器）、test_git_sync（同步/回填，MOD-GIT-PIPELINE）、test_recall_cli（CLI 胶水 + 子进程冒烟）、test_validate（validate 检查函数）、test_recall_common（公共基础设施 + RULE-021 静态门） | unittest | 断言 | 测试文件 | yes | `python -m unittest discover -s tests` |
| references/examples/audit-repro-legacy/ | test/test-fixture | internal | 审计复现夹具；自带 `scope: .`，按嵌套项目根排除（RULE-007） | 审计脚本读取 | 复现场景 | 夹具文件 | yes | none |

## 旧行为消费者

- `scripts/audit_logic_map.py` 单文件拷贝部署：VER-20260903-002 起不再支持，必须与 `scripts/recall_audit/` 整目录部署；已知消费者只有指向本仓库的技能目录符号链接（`~/.claude/skills/recall`），无需迁移
- 审计 JSON：collaborative 项目输出不变；personal 项目自 VER-20260903-003 起 `proposal_issues` 只会减少（RULE-023）；VER-20260903-004 起无领域的项目多出 advisory 提示 `constitution-without-domains`，退出码不变

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | 审计器行为：INV-001/002 平行真源与已登记领域豁免、RULE-007 嵌套根、RULE-009 记录 schema、RULE-018 领域路由/公报/密度分档、RULE-019 覆盖对账、RULE-021 ③ 代码段内链接与占位符不算、空账本 none/0 同义、RULE-022 分包后行为不变、RULE-023 字段分档 | `python tests/test_audit_logic_map.py`；`python scripts/audit_logic_map.py . --current-state` / `--formal-review` / `--json --current-state` | 全部 OK；静态门 PASS；无 parallel/nonroot 报告；夹具不在 Non-root 列表；JSON 可解析 | unittest 输出 + 审计报告 |
| integration | RULE-009/RULE-015 validate 一致性对账 | `python scripts/validate.py` | 决策记录被发现且无假缺失字段（快速模板与扩展 schema 均通过）；三处登记（首列裸 ID / 链接 / 反引号）、撞号、意图层引用与 `path#symbol` 锚点、slug 型 CHG 三字段、占位符、领域公报检查出现且无假错误 | 验证报告 |
| runtime | RULE-005 批处理入口不错行 | `recall status` / `recall help` | 无 `is not recognized` 输出 | 终端输出 |
| runtime | RULE-008 非交互可用与重定向不崩 | `recall init < /dev/null`；`echo "" \| recall init`；`recall init --non-interactive`；`recall help > out.txt`；`recall status > out.txt`；`python scripts/audit_logic_map.py . --json --current-state > out.json` | 均退出 0，无 UnicodeEncodeError，落盘为 UTF-8 | 终端输出 / 输出文件 |
| integration | RULE-002/010/012/014/015/018/020/021 CLI 胶水层与 validate 检查函数：接口一致性、子进程冒烟（help/status/conflicts/validate/route/audit 真跑）、未推送提示、status 规则数按定义行、领域与账本计数、route 跳过"不负责"行与表头、rejected 豁免、生效 VER 规则行反链、领域编号空间与公报告警 | `python -m unittest tests.test_recall_cli tests.test_validate` | 全部 OK；status 退出 0 且无 Traceback；route --json 输出可解析；audit 退出 0 且输出 Static gate；有残留→warning，无残留→无告警 | unittest 输出 |
| unit | RULE-021 公共基础设施与机器门 | `python -m unittest tests.test_recall_common` | 全部 OK：根查找/回退、run_git 非仓库不抛异常、porcelain 首行前导空格保留、parse/classify_porcelain、无上游返回 None、utf-8 解码、registered_domains/change_ledgers、scripts/ 下无直接 subprocess 调用 | unittest 输出 |
| runtime | RULE-020 status 待处置提示 | 新建一个未跟踪文件后 `recall status` | 输出单列"未跟踪文件（待处置候选）"并列出路径；删除后消失 | 终端输出 |

## 当前限制

- 静态门只检查文档结构与工具链约定，不能证明代码语义、消费者或运行行为；Density 与 logic_temp 检查只是 advisory，不使静态门失败（消费项目 logic_change 越过硬上限 21 倍仍 PASS，2026-09-03 eduai 实测）；是否让硬上限越线与无领域进门见根账本 CHG-20260904-004
- 收尾归零依赖代理自律：`recall status` / `recall validate` 只能看见未跟踪且未被忽略的文件；已被 `git add` 或已提交的垃圾机器识别不到（RULE-020）
- 审计器函数长度：RULE-022 的 150 行上限只约束新写函数；changes.py（334/152）、semantic.py（398/248）、formal.py（296/178）、report.py（459/350/165）共 9 个存量超限函数是已接受的存量，按同一方法（先冻结 JSON 基线、拆分后逐字节对比）在触及时顺带拆分，不另立案
- 代码锚点的符号核查只是子串查找（`path#symbol` 的 symbol 在文件文本中出现即算存在），不解析语法；`after_commit` 写成 `pr:` / `release:` 等非 SHA 形式时不校验、只提示"未关联 Git commit"；规则正文里裸写的 `<meta>` 仍按模板占位符、裸写的 `[文本](路径)` 仍按真实链接处理，示意写法须加反引号或放进围栏代码块（VER-20260904-003/004）
- `recall route` 的关键词匹配是子串级：命中领域文档正文（已排除"不负责"边界行与表头）或宪法意图行即算命中，不判断语义；路径匹配依赖领域 `owned_paths` 的完整性，未声明的路径不会路由到任何领域
- 一法多议案检测只认 `authority_surfaces` 中的 RULE-ID；基线失效只比对日期，规则正文改动未更新 `last_reviewed` 时检测不到
- `recall conflicts` 为关键词级启发式，语义冲突仍需人工澄清

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
- 相关 CHG-ID：none
