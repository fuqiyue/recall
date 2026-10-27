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
- last_verified: 2026-10-27
- review_trigger: interval:90d; event:document-model-change
- source_of_truth: logic_domains/task-workflow/logic_readme.md
- source_decisions: 见规则决策列；全量见 ../../logic_version/index.md
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
| RULE-020 | key | 处置：每轮处理本轮产物，关案前按 RULE-025 核归属/路径后逐项删临时文件和空目录；重复正文另核完整归档及指纹。gitignore 不算清理，核验不重置授权。 台账：按用途区分临时物、deliverable/runtime-data/evidence；keep 写 retention_basis/exit_condition，round 标轮次，旧五列兼容。临时物放独占 scratch_root/临时-具体功能；复用代码、运行材料及必要证据先安置到正式位置，核当前引用和消费者后删临时副本。跨轮保留须有具体依赖及退出条件，不因历史提及或目录名 archive 长期保留整目录。 核对：workspace 对照实物，任务/轮次与全局遗留分列，共享问题归双方；关案无 pending/delete 残留。数量或检查结果不授权删除，检查命令只读，代理执行。simple 用最终汇报；旧用户文件先核归属、引用、原授权。 受阻出口：仅完整归档且无未完事项的独立任务正文，经核验及必要审批仍受限（或无审批渠道），可在策略允许时原字节移至 logic_version/pending_cleanup/CHG-ID/logic_change.md.txt；既有 index 记来源、归档、SHA、退出条件。移动不算删除，workspace 持续核实并提示；业务数据和整目录不适用。 | 把临时产物处置纳入完成条件。 | [VER-20260903-001](../../logic_version/records/logic_version-20260903-001-cleanup-ledger.md)；[VER-20261011-001](../../logic_version/records/logic_version-20261011-001-cleanup-ai-delivery-closure.md)；[VER-20261011-002](../../logic_version/records/logic_version-20261011-002-cleanup-html-explainers.md)；[VER-20261025-006](../../logic_version/records/logic_version-20261025-006-audit-boundary-summary.md)；[VER-20261027-004](../../logic_version/records/logic_version-20261027-004-local-materials-cleanup.md)；[VER-20261027-007](../../logic_version/records/logic_version-20261027-007-workflow-authorization-closure.md) | user:2026-10-27 | 临时台账; status/validate; tests/ | valid | 2026-10-27 | Codex |
| RULE-025 | key | 授权：同任务沿用仍有效的原范围与条件，完成必要实施、验证、修复、归档和清理；换轮、接手、收尾不重置授权。授权定范围、平台权限定可执行操作、验证定完成结果；三者不互代。personal 由 AI 实施、自审并记录验证，风险通道不自动增加确认轮次。 询问：仅处理原授权未覆盖的实质影响、真实未决选择或明确外部前置；阻塞受影响部分，继续其余工作。人工验收仅在明确要求时设为前置。 权限：环境要求才申请平台审批，附原授权、准确操作及核验依据。拒绝后记录理由与执行状态；只用更安全且策略允许的替代，否则说明缺口请用户介入，不重问整项授权、不换工具规避。 交付：无未决设计/实质阻塞后，更新 readme → 清理核实 → 将 CHG 需求、修订表及结论归入同一 VER，核轮次/最终版本/结果/索引 → 定稿后删除已结束任务正文及空目录，更新公报并核活跃列表和实物退出；旧混合账本只删对应条目。业务完成但清理未完须分别报告，继续可做收尾。取消/否决同样归档，不逐轮建档；早建 VER 保持关联草稿，定稿后不改语义。simple 无 CHG 按通道；环境限制写实，交付反馈另开案。 接续：依赖关闭后重核并绑定 VER/规则，已启用行为不长期挂案。RULE-020 保全移动核对后可退出业务队列，清理另列；移动受阻则 index 记原位待清理。唯一登记、归档、身份及 SHA 均通过才退出活跃发现；源字节变化恢复发现并报错，不清空正文伪装清理。 | 完成可验证交付并保全必要修订历史。 | [VER-20260907-001](../../logic_version/records/logic_version-20260907-001-ai-delivery-closure.md)；[VER-20261025-001](../../logic_version/records/logic_version-20261025-001-pending-cleanup.md)；[VER-20261026-005](../../logic_version/records/logic_version-20261026-005-authorization-through-closure.md)；[VER-20261027-007](../../logic_version/records/logic_version-20261027-007-workflow-authorization-closure.md) | user:2026-10-27 | 生命周期; CHG/VER模板; 本轮归档核对 | valid | 2026-10-27 | Codex |
| RULE-027 | key | 待办：根 change 可记 idea/planned，留来源、约束、完成条件，启动后移除。 并案：同类需求可统一目标/验收/收尾则合并原 CHG；独立发布/回滚或授权冲突才分案。保留原 ID 来源、需求与修订事实，更新引用。 进度：顶部唯一 status/current_result/next_action；状态变化、实质验证及交接前按证据更新。旧计划收敛为修订表，记轮次/日期/版本/原因/文件/结果并保留失败；轮次按有效节点递增，proposal_revision 仅方案、影响面或基线实变时增加。归档见 RULE-025。 阻塞：记解除动作、责任、复查；next/status 不授权、不调度。 | 保存可靠上下文和修订过程，减少双写。 | [VER-20260907-003](../../logic_version/records/logic_version-20260907-003-task-context.md)；[VER-20261020-002](../../logic_version/records/logic_version-20261020-002-task-revision-history.md)；[VER-20261026-001](../../logic_version/records/logic_version-20261026-001-current-policy-archive-boundary.md) | user:2026-10-26 | 任务上下文/生命周期；scripts/task_context.py + tests/test_task_context.py | valid | 2026-10-27 | Codex |
| RULE-029 | key | 路径：用户指定文件夹为根，workspace_root 为 .；显式 cwd，根相对路径只拼一次，写前核越界、盘符、链接及重复根。 盘点：声明 scratch_root/data_roots；功能目录由 owned_paths 认领。inventory 有界列名称/类型/归属，数据只列上层。 地图：同文件记逐目录覆盖、时间、预算和边界；只替换完整列举范围，截断/未重扫条目保留旧时间，确认消失才移除旧子树。地图可重建，不是规则真源，不自动搬删；临时退出见 RULE-020。 | 让真实目录可发现，避免路径嵌套和过程文件失控。 | [VER-20261020-001](../../logic_version/records/logic_version-20261020-001-workspace-task-governance.md)；[VER-20261024-001](../../logic_version/records/logic_version-20261024-001-task-context-workspace.md)；[VER-20261026-002](../../logic_version/records/logic_version-20261026-002-root-domain-slim.md) | user:2026-10-24 | tests/test_workspace.py | valid | 2026-10-27 | Codex |

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
