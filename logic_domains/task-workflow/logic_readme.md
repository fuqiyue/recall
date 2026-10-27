# 任务交付现行规则

只在处理本领域事项时读取；全局规则与意图在[根现行文档](../../logic_readme.md)。本文是下列规则的唯一现行定义，references 只提供字段与操作方法。

## 文档控制
- doc_id: LOGIC-RECALL-TASK-WORKFLOW
- module_id: MOD-TASK-WORKFLOW
- scope: logic_domains/task-workflow
- scope_path: logic_domains/task-workflow
- parent: ../../logic_readme.md
- parent_module_id: MOD-ROOT
- membership: in-system
- scope_type: domain
- layer: runtime-code
- module_doc_policy: readme-only
- status: active
- owner: self
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:https://github.com/fuqiyue/recall@main
- governance_verification: recorded
- governance_verified_at: 2026-08-08
- effective_from: 2026-10-26
- last_verified: 2026-10-26
- review_trigger: interval:90d; event:document-model-change
- source_of_truth: logic_domains/task-workflow/logic_readme.md
- source_decisions: VER-20261026-005, VER-20261026-002；其余见规则决策列
- intent_summary: 在唯一任务正文保全需求和当前进度，按轮管理产物并完成可验证交付
- intent_sources: INT-20260816-006, INT-20260903-001, INT-20260907-001, INT-20261020-001
- decision_validity: valid
- validity_evidence: user:2026-10-26；授权覆盖必要收尾，执行权限仍独立核对

## 范围登记与归属
- canonical_readme: logic_domains/task-workflow/logic_readme.md
- canonical_change: none
- owned_paths: logic_domains/task-workflow/, logic_changes/, references/change-lifecycle.md, references/task-context.md, references/workspace-tasks.md, references/logic-change-template.md, references/logic-temp-template.md, references/workflow-integration.md, references/practical-examples.md
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度
| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-020 | key | ①每轮处置本轮产物，关案前由代理核归属/路径，重复正文另核完整归档/指纹，再按RULE-025沿用授权逐项删除临时文件及空目录；核验不等于重新授权，gitignore不算清理。②正文台账按用途而非目录名区分临时物、deliverable/runtime-data/evidence；keep写retention_basis与exit_condition，round标轮次，旧五列兼容。③临时物进独占scratch_root/临时-具体功能，复用代码和必要证据先晋升，跨轮保留须有依赖及退出条件。④workspace核实物，按任务/轮次分列结果与全局遗留；共享问题归属双方，关案无pending/delete残留，数量不授权删除。⑤simple最终汇报；旧用户文件先核归属、引用及原授权。Recall检查命令只核对，不按台账自动删除；代理负责核验后执行。 ⑥仅已完整归档且无其余未完事项的独立任务正文，核验及所需审批后仍受限（或环境不提供审批）时，可在执行策略允许下原字节移动至logic_version/pending_cleanup/CHG-ID/logic_change.md.txt，既有index集中记来源/归档/指纹/退出条件；移动不算删除，workspace持续提示并核实物，不适用于业务数据或整目录。 | 把临时产物处置纳入完成条件。 |[VER-20260903-001](../../logic_version/records/logic_version-20260903-001-cleanup-ledger.md); cleanup corrections: [VER-20261011-001](../../logic_version/records/logic_version-20261011-001-cleanup-ai-delivery-closure.md), [VER-20261011-002](../../logic_version/records/logic_version-20261011-002-cleanup-html-explainers.md)；[VER-20261020-001](../../logic_version/records/logic_version-20261020-001-workspace-task-governance.md)；[VER-20261024-001](../../logic_version/records/logic_version-20261024-001-task-context-workspace.md)；[VER-20261025-001](../../logic_version/records/logic_version-20261025-001-pending-cleanup.md)；[VER-20261026-002](../../logic_version/records/logic_version-20261026-002-root-domain-slim.md)；[VER-20261025-006](../../logic_version/records/logic_version-20261025-006-audit-boundary-summary.md)；[VER-20261026-005](../../logic_version/records/logic_version-20261026-005-authorization-through-closure.md) ；本地证据归位：[VER-20261027-004](../../logic_version/records/logic_version-20261027-004-local-materials-cleanup.md)| user:2026-10-26 | 临时台账; status/validate; tests/ | valid | 2026-10-26 | Codex |
| RULE-025 | key | ①同任务在仍有效的原授权范围与条件内，持续完成必要实施、验证、修复、归档及本任务清理；换轮、接手或收尾不使授权自动失效。personal由AI实施、自审并记录必要验证。②无未决设计/实质阻塞后主动更新readme→清理核实→将CHG需求、简短修订表及结论搬入同一VER，核轮次/最终版本/结果与索引→定稿关案；含取消/否决，不逐轮建档；早建VER为关联草稿，定稿后不改语义。③环境限制写实，反馈另开案；无CHG的simple照通道。④仅原授权未覆盖的实质影响、真实未决选择或明确外部前置阻塞受影响部分；人工验收须明确要求。平台审批只在环境要求时触发，提交原授权、准确操作及核验依据。被拒后记真实理由与执行状态，仅采用实质更安全且策略允许的替代；否则说明缺口请求用户介入，继续不受影响工作，不重复索取整项授权或换工具规避。⑤依赖关闭后重核并绑VER/规则，已启用行为不长期挂活跃案。 ⑥上述保全移动核对完成可退出业务活跃队列，清理另列；移动也受阻时只在历史index记原位待清理；唯一登记/归档/身份/SHA核验通过后退出活跃发现，源字节变化则恢复发现并报错。不得清空正文伪装清理。 | 完成可验证交付并保全必要修订历史。 |[VER-20260907-001](../../logic_version/records/logic_version-20260907-001-ai-delivery-closure.md)；[VER-20261012-002](../../logic_version/records/logic_version-20261012-002-six-improvements.md)；[VER-20261013-001](../../logic_version/records/logic_version-20261013-001-reliable-context.md)；[VER-20261020-002](../../logic_version/records/logic_version-20261020-002-task-revision-history.md)；[VER-20261025-001](../../logic_version/records/logic_version-20261025-001-pending-cleanup.md)；[VER-20261026-002](../../logic_version/records/logic_version-20261026-002-root-domain-slim.md)；[VER-20261026-005](../../logic_version/records/logic_version-20261026-005-authorization-through-closure.md) | user:2026-10-26 | 生命周期; CHG/VER模板; 本轮归档核对 | valid | 2026-10-26 | Codex |
| RULE-027 | key | ①根change可选idea/planned待办，留来源/约束/完成条件，启动后移除。②相同或接近需求能统一目标/验收/收尾时合并原CHG；独立发布/回滚或授权冲突才分案。并案保留原ID来源、需求与修订事实并更新引用。③顶部唯一status/current_result/next_action；状态变化、实质验证结果及交接前按证据及时更新，旧计划收敛修订表，不另造过程正文。表记轮次/日期/版本/原因/文件/结果，失败事实保留；轮次按有效节点递增，proposal_revision仅实质方案/影响面/基线改变时增加，归档见RULE-025。④阻塞记解除动作/责任/复查，next/status不授权或调度。 | 保存可靠上下文和修订过程，减少双写。 |[VER-20260907-003](../../logic_version/records/logic_version-20260907-003-task-context.md)；[VER-20261020-001](../../logic_version/records/logic_version-20261020-001-workspace-task-governance.md)；[VER-20261020-002](../../logic_version/records/logic_version-20261020-002-task-revision-history.md)；[VER-20261024-001](../../logic_version/records/logic_version-20261024-001-task-context-workspace.md)；[VER-20261026-001](../../logic_version/records/logic_version-20261026-001-current-policy-archive-boundary.md)；[VER-20261026-002](../../logic_version/records/logic_version-20261026-002-root-domain-slim.md) | user:2026-10-26 | 任务上下文/生命周期；scripts/task_context.py + tests/test_task_context.py | valid | 2026-10-26 | Codex |
| RULE-029 | key | ①用户指定文件夹为根（workspace_root为.），输出只拼一次根相对路径，执行显式cwd，写前核越界/盘符/链接/重复根。②声明scratch_root/data_roots，功能目录由owned_paths认领；inventory有界盘点名称/类型/归属，数据仅列上层。③地图在同一文件保存逐目录覆盖/时间/预算/边界；局部更新仅替换完整列举范围，截断或未重扫条目保留旧时间，确认目录消失才移除旧子树索引。④地图可重建非规则真源，不自动搬删；临时退出见RULE-020。 | 让真实目录可发现，避免路径嵌套和过程文件失控。 |[VER-20261020-001](../../logic_version/records/logic_version-20261020-001-workspace-task-governance.md)；[VER-20261024-001](../../logic_version/records/logic_version-20261024-001-task-context-workspace.md)；[VER-20261026-002](../../logic_version/records/logic_version-20261026-002-root-domain-slim.md) | user:2026-10-24 | tests/test_workspace.py | valid | 2026-10-24 | Codex |

## 代码地图
| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| logic_changes/ | source/runtime-code | public | 同任务需求、方案、进度、修订与产物台账 | 用户需求与验证 | 唯一CHG正文 | 该任务；非现行规则 | yes | tests/test_task_context.py |
| references/change-lifecycle.md、task-context.md、logic-change-template.md | source/runtime-code | public | 任务状态、交付步骤和字段 | 根与本领域规则 | 操作指引/表单 | 所属readme；模板字段 | yes | audit/index |
| references/workspace-tasks.md、logic-temp-template.md | source/runtime-code | public | 路径、地图、产物分类及清理操作 | 目录归属与台账 | 操作步骤 | 本领域规则；真实文件 | yes | tests/test_workspace.py |
| references/workflow-integration.md、practical-examples.md | source/runtime-code | internal | 外部计划承接与操作示例 | 已授权方案 | 执行方法 | 根及本领域 | yes | tests/test_recall_cli.py |

## 协作边界与验证
- 根字段声明 workspace_root/scratch_root/data_roots；本文规定使用与清理，`scripts/workspace_*.py`、task_context/pending_cleanup 的实现和 JSON 契约归[工具链](../toolchain/logic_readme.md)。修改实现时两域按需读取。
- 产物清理操作见[工作路径与任务](../../references/workspace-tasks.md)；任务进度见[任务上下文](../../references/task-context.md)；晋升见[生命周期](../../references/change-lifecycle.md)，不另建规则正文。
- `recall index` 核公报，`recall next --json` 核接手视图，`recall workspace --closing CHG-ID` 核实物；`recall audit/validate` 核字段、归档与引用。状态视图不能证明语义审查或部署已完成。
- 只核本任务产物并列明全局遗留；涉及 Git 发布时再读[Git管道](../git-pipeline/logic_readme.md)。

## 活跃议案入口
- [根任务公报](../../logic_change.md)；正文唯一位于 logic_changes/，按任务 scope/affected_scopes 关联本领域。
