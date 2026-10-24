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
- last_verified: 2026-10-24
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: scripts/recall.py, scripts/recall_common.py, scripts/recall_audit/, scripts/validate.py
- source_decisions: VER-20261024-001, VER-20261012-002, VER-20260808-002, VER-20260811-002, VER-20260816-002, VER-20260816-005, VER-20260903-002, VER-20260903-003, VER-20260903-004, VER-20260904-001, VER-20260904-003, VER-20260904-004, VER-20260904-005, VER-20260906-001, VER-20261011-003
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
- owned_paths: scripts/workspace_paths.py, scripts/workspace_inventory.py, scripts/workspace_maps.py, scripts/workspace_check.py, scripts/workspace_cli.py, tests/test_workspace.py, scripts/record_context.py, scripts/task_context.py, scripts/recall.py, scripts/recall_common.py, scripts/audit_logic_map.py, scripts/recall_audit/, scripts/validate.py, scripts/create_ver.py, scripts/link_ver_git.py, scripts/detect_conflicts.py, scripts/route_docs.py, recall.bat, recall.sh, .gitattributes, tests/test_audit_logic_map.py, tests/test_recall_cli.py, tests/test_validate.py, tests/test_recall_common.py, tests/test_task_context.py, tests/test_record_context.py, tests/test_platform_entry.py, references/examples/, tests/test_validate_recall_boundaries.py
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-005 | key | 批处理入口必须纯ASCII + CRLF。 | 保持cmd字节偏移与换行定位正确。 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | .gitattributes + recall.bat 实测 | valid | 2026-08-08 | self |
| RULE-006 | key | 外部命令用argv列表，禁止shell=True。 | 防止多行参数截断及命令注入。 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | init_recall.py / link_ver_git.py 注入测试 | valid | 2026-08-08 | self |
| RULE-007 | key | 自带scope: .的嵌套项目根不纳入本项目审计。 | 防止外部项目覆盖本项目的范围登记。 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | audit_logic_map.py 静态门 | valid | 2026-08-08 | self |
| RULE-008 | ordinary | CLI须可非交互运行，控制台及重定向输出为UTF-8且不崩；CI在Ubuntu和Windows验证入口、中文路径与重定向。 | 持续验证实际使用的双平台入口。 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md)；[VER-20261013-001](../../logic_version/records/logic_version-20261013-001-reliable-context.md) | 复现验证 | tests/test_platform_entry.py + .github/workflows/validate.yml | valid | 2026-10-13 | Codex |
| RULE-009 | ordinary | 校验字段名与references模板一致，支持模板声明的schema。 | 避免模板与解析器漂移。 | [VER-20260808-002](../../logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | validate.py 记录发现测试 | valid | 2026-08-08 | self |
| RULE-012 | key | 规范文件名为logic_version-YYYYMMDD-NNN-*.md；创建与发现共用同一命名口径。 | 保证记录对所有工具可见。 | [VER-20260811-002](../../logic_version/records/logic_version-20260811-002-cli-interface-repair.md) | 复现验证 | tests/test_recall_cli.py | valid | 2026-08-11 | self |
| RULE-015 | ordinary | ①validate核records/index双向登记及撞号；首列接受裸ID、Markdown链接、反引号，其余格式明确告警；生效记录须在根最近索引或任一规则决策列有反链，rejected/cancelled/rolled-back只进全量index。②核根与领域RULE/INT唯一性、INT/FLOW/UXI引用与意图来源；inferred/code-derived/空/未知格式告警；代码锚点剥离行号或符号后查路径，符号只查子串。③medium/high CHG与关联VER保全需求三字段，核占位符及任一声明schema；commit接受裸SHA、反引号、commit:前缀并在项目根验证。④领域CHG须进根公报；conflicts跨账本核一法多案及规则日期晚于议案。⑤连续超过10次未触logic文档的提交升级漂移告警，hook非阻断提醒。⑥VER草稿口径见RULE-021；真实且已归档的correction可用corrects与有效after_commit追加原记录提交证据，invalid SHA/草稿不豁免原记录告警。⑦活跃临时索引只在路径、身份、revision及唯一活跃CHG回链成立时与归档分开；归档格式可由immutable:true的correction通过corrects和原SHA256绑定的专用补充块追加，原记录不改。 | 保持现行文档、历史与代码追溯一致。 | [VER-20260816-005](../../logic_version/records/logic_version-20260816-005-audit-remediation.md)；[VER-20260903-004](../../logic_version/records/logic_version-20260903-004-two-level-docs.md)；[VER-20260904-001](../../logic_version/records/logic_version-20260904-001-intent-provenance-conflicts.md)；[VER-20260904-002](../../logic_version/records/logic_version-20260904-002-docs-consolidation.md)；[VER-20260904-003](../../logic_version/records/logic_version-20260904-003-validate-compat.md)；[VER-20261013-001](../../logic_version/records/logic_version-20261013-001-reliable-context.md)；[VER-20261013-002](../../logic_version/records/logic_version-20261013-002-worklog-schema-validation.md) | 复现验证 | scripts/validate.py + tests/test_validate.py | valid | 2026-10-13 | Codex |
| RULE-021 | key | ①根定位、Git argv/UTF-8/尾部空白、porcelain、编码防护、领域/账本登记与CHG编号集中recall_common；scripts其他文件不得直接subprocess。记录写入须有项目标记，--project仅指显式根，资源目录不作回退目标。②规则按根+领域定义行计数；VER命名、CHG正则（NNN或slug）、占位符与链接口径同源；代码段内示意不作链接/占位符，坏链带broken-link前缀，空账本none/0同义。③recall.py各子命令须真跑胶水冒烟；init/sync至少核解析入口。④record_context统一VER/commit口径：immutable:false仅在唯一活跃CHG、正整数revision、同一slug匹配时算草稿；不要求草稿完成归档字段/索引/commit，list/query/status明确标记，孤立或不匹配草稿告错；旧记录无immutable仍算归档。⑤Git失败区分非仓库、权限/沙箱、工作树、超时和未知原因，保留stderr，不把所有失败说成未安装。 | 共享解析和真实入口回归防止工具各报一套事实。 | [VER-20260903-002](../../logic_version/records/logic_version-20260903-002-structure-context-cost.md)；[VER-20260903-003](../../logic_version/records/logic_version-20260903-003-structural-closure.md)；[VER-20260904-002](../../logic_version/records/logic_version-20260904-002-docs-consolidation.md)；[VER-20260904-003](../../logic_version/records/logic_version-20260904-003-validate-compat.md)；[VER-20260904-004](../../logic_version/records/logic_version-20260904-004-audit-link-ledger-compat.md)；[VER-20260906-001](../../logic_version/records/logic_version-20260906-001-constitution-slim-alignment.md)；[VER-20261012-002](../../logic_version/records/logic_version-20261012-002-six-improvements.md)；[VER-20261013-001](../../logic_version/records/logic_version-20261013-001-reliable-context.md) | 复现验证 + 用户确认 2026-09-03 | recall_common.py; record_context.py; tests/test_recall_common.py; tests/test_record_context.py; tests/test_recall_cli.py | valid | 2026-10-13 | Codex |
| RULE-023 | key | ①personal CHG块必有status/effective:false/proposal_revision/recall_route/changed_by，进入implementing/verifying/promoting前须真实用户确认人及日期。②其余personal可选字段缺则不查、写则照查；块模式优先，缺模式按完整要求；collaborative/formal不降级。③仍须唯一显式锚点、scope/affected_scopes和公报结构；依赖/冲突跨全部账本解析。④authority_surfaces的RULE是一法多案目标；重叠须互指conflicts_with，否则告警；拟议制度提RULE而未声明目标告警；规则last_reviewed晚于created/last_status_change须重核based_on。 | 简化个人记录，同时保留确认与冲突约束。 | [VER-20260903-003](../../logic_version/records/logic_version-20260903-003-structural-closure.md)；[VER-20260904-001](../../logic_version/records/logic_version-20260904-001-intent-provenance-conflicts.md)；[VER-20261012-002](../../logic_version/records/logic_version-20261012-002-six-improvements.md)；[VER-20261013-001](../../logic_version/records/logic_version-20261013-001-reliable-context.md) | 用户确认 2026-09-03；一法多议案为 2026-09-04 用户提问后确认 | recall_audit/changes.py + tests/test_audit_logic_map.py | valid | 2026-10-13 | Codex |
| RULE-024 | key | ①审计器按constants→textutil→fsclassify→changes→semantic→integrity→formal→archive→report→cli分层，只向下依赖；audit_logic_map为兼容facade。②scripts函数≤150行（AST行距）；存量白名单只减不增、长度只许变短，达限内即移除。③触及存量时冻结JSON行为，拆分后比对，不另立案。 | 用机器门约束结构与存量函数增长。 | [VER-20260903-002](../../logic_version/records/logic_version-20260903-002-structure-context-cost.md)；[VER-20260903-003](../../logic_version/records/logic_version-20260903-003-structural-closure.md)；[VER-20260906-001](../../logic_version/records/logic_version-20260906-001-constitution-slim-alignment.md)；[VER-20261013-001](../../logic_version/records/logic_version-20261013-001-reliable-context.md) | 用户确认 2026-09-03（分包）；机器门为 2026-09-06 用户认可 | recall_audit/__init__.py + FunctionLengthGateTests | valid | 2026-10-13 | Codex |

| RULE-028 | ordinary | ①next/status从登记账本CHG/可选待办派生类别、原因、下一步与阻塞上下文，忽略围栏；未知依赖/状态/确认/冲突/重复ID不推断可执行。②index默认只读核根公报，差异退出1；--write仅更新公报和根CHG正文计数，歧义拒写。③validate复用同源公报/阻塞检查，仅告警；视图不授权、不调度、不改状态，旧CHG兼容；新任务由logic_changes/*/logic_change.md统一发现，next/index/route/audit/validate同源；next/index支持JSON。 | 从正文恢复上下文，避免双写和隐含授权。 | [VER-20260907-003](../../logic_version/records/logic_version-20260907-003-task-context.md)；[VER-20261020-001](../../logic_version/records/logic_version-20261020-001-workspace-task-governance.md) | user:2026-09-07 | scripts/task_context.py + tests/test_task_context.py | valid | 2026-10-20 | Codex |

## 代码地图

文件清单见[可重建文件地图](file_map.md)；以页内扫描范围和时间为准。

| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| recall.bat / recall.sh / .gitattributes | source/runtime-code+config | public | 双平台入口与换行约定（RULE-005/008） | 命令行参数 | 子命令输出与退出码 | 入口文件 | yes | none |
| scripts/recall_common.py | source/runtime-code | internal | 根/Git/编码/登记表基础设施与失败诊断（RULE-021） | 起点路径 / git 参数 / porcelain 文本 / 项目根 | 项目根 / (ok, stdout, stderr) / 分类路径 / 计数 / 领域与账本列表 | 脚本文件 | yes | tests/test_recall_common.py |
| scripts/record_context.py | source/runtime-code | internal | VER生命周期、commit解析与追加证据的共享判断 | 账本与记录 | 状态/证据 | 所属文档与记录 | yes | tests/test_record_context.py |
| scripts/task_context.py | source/runtime-code | public | next任务视图与根公报派生（RULE-028） | 已登记账本、CLI 选项 | 文本/JSON，显式请求更新根公报 | 所属账本正文 | yes | tests/test_task_context.py |
| scripts/recall.py | source/runtime-code | public | 子命令调度、任务/草稿/Git状态摘要 | 子命令与参数 | 退出码 | 脚本文件 | yes | tests/test_recall_cli.py（含子进程冒烟） |
| scripts/route_docs.py | source/runtime-code | public | 任务ID/路径按声明范围路由；代码路径/关键词/INT按需匹配，相关任务先摘要，保留成本与未知目标 | 路径、关键词或 INT-ID、`--json` | 读取清单 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/audit_logic_map.py | source/runtime-code | public | 兼容入口，须与recall_audit整包部署 | 项目根路径 | 审计报告与静态门退出码 | 脚本文件 | yes | tests/test_audit_logic_map.py |
| scripts/recall_audit/ | source/runtime-code | internal | 分层静态审计：制度/范围/CHG/归档/链接/密度/代理入口 | 项目根路径 | 审计报告 dict | 包目录 | yes | tests/test_audit_logic_map.py |
| scripts/validate.py | source/runtime-code | public | 跨根/领域/账本/历史/Git的一致性检查 | 项目根路径 | 验证报告 | 脚本文件 | yes | tests/test_validate.py |
| scripts/create_ver.py | source/runtime-code | public | 核项目标记、规范取号并从项目或集中模板创建草稿 | 描述与 scope | 记录文件 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/link_ver_git.py | source/runtime-code | public | 文件/commit/INT双向追溯与草稿标记、追加提交证据 | 文件路径、commit 或 INT-ID | 关联报告 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/detect_conflicts.py | source/runtime-code | public | 规则/议案冲突启发式；潜在冲突退出2 | logic 文档 | 冲突报告与退出码（0 无冲突 / 2 有潜在冲突） | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/workspace_paths.py、workspace_inventory.py、workspace_maps.py、workspace_check.py、workspace_cli.py | source/runtime-code | public | 根相对路径校验、保留覆盖的增量地图、分任务/轮次与全局的实物核对 | 项目/目录/任务 | 路径、地图、残留问题 | 所属文档和真实文件 | yes | tests/test_workspace.py |
| tests/ | test/test-fixture | internal | unittest与CLI真跑回归 | unittest | 断言 | 测试文件 | yes | `python -m unittest discover -s tests` |
| references/examples/audit-repro-legacy/ | test/test-fixture | internal | 独立嵌套项目的审计复现夹具 | 审计脚本读取 | 复现场景 | 夹具文件 | yes | none |

## 旧行为消费者

- 审计器须部署完整scripts/，包含recall_audit、record_context与task_context；已知消费者沿技能目录引用完整源，不支持单文件复制。
- JSON保留原键；route新增matched_tasks/related_changes/routing_warnings，相关任务正文须按ID或--include-related展开。workspace原ok/findings仍为全局，新增task_result/round_result/global_result/other_findings/selection_ok，筛选时退出码按selection_ok。草稿显示与历史告警修正不改变索引表格式。
- 历史不改写；先交付后提交用correction追加证据，操作见[Git追溯](../../references/git-sync.md#先交付后提交的追加追溯)。

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | 审计、验证、任务、路由与共享基础设施 | `python -m unittest discover -s tests` | 全部OK；函数门/解析/接口兼容与负例均通过 | unittest输出 |
| integration | 现行文档、公报与读取范围 | `recall audit --json`; `recall validate`; `recall index`; `recall next --json`; `recall route scripts/create_ver.py --json` | 静态门通过、公报一致、范围可解释；警告保留真实原因 | CLI报告 |
| integration | 草稿/定稿/追加证据 | `python -m unittest discover -s tests -p test_record_context.py` | 不误报活跃草稿；错配/孤立/无效SHA不能绕过校验；原记录不变 | 回归输出 |
| runtime | 双平台入口、中文路径与UTF-8重定向 | `python -m unittest discover -s tests -p test_platform_entry.py` | 对应平台真实入口在非交互环境退出0且输出可解码 | Ubuntu/Windows CI与本机结果 |

## 当前限制

- 静态审计不证明语义、消费者、部署或测试已运行。文档硬限/无领域进门，其余密度/台账提示见RULE-022；advisory-only只改退出码。
- workspace核任务声明路径与临时根，包含Git忽略文件；未登记在其他位置的旧产物不保证全量发现，inventory报告扫描边界。
- 函数白名单现存10项，准确列表和行数以FunctionLengthGateTests为准，触及时只减不增。
- 任务ID/路径路由按scope/affected_scopes确定，未知或重复声明告警；代码路径依赖owned_paths，关键词/conflicts仍是子串启发式，代码锚点不解析语法。规则基线检测只比日期，未更新last_reviewed的正文变化可能漏检。
- pr:/release:等非SHA证据仍需另核；代码段外的示意链接/占位符会被当真实字段处理。
- 当前优化经本机Windows验证；远端CI结果以实际运行记录为准。

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
- 相关 CHG-ID：none
