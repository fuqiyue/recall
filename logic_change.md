# Recall Skill Active Changes

## 文档控制

- scope: .
- scope_path: .
- module_id: MOD-ROOT
- current_policy: logic_readme.md
- owner: self
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:https://github.com/fuqiyue/recall@main
- governance_verification: recorded
- governance_verified_at: 2026-08-08
- last_updated: 2026-09-07
- active_changes: 2

## 议案规则

- 本文件所有条目默认 `effective: false`
- 允许状态：draft | awaiting-decision | implementing | verifying | promoting | blocked
- 个人小项目使用简化流程：draft -> implementing -> verifying -> promoting -> 关闭；AI 验证通过主动完成收尾（RULE-025）
- 高风险修改使用决策流程：draft -> awaiting-decision -> implementing -> verifying -> promoting

## 讨论主题索引

| topic_id | 同类议题/共享问题 | coordinator | discussion_refs | related_changes | status |
|---|---|---|---|---|---|

当前无活跃讨论主题。表头保留以声明 schema。

## 活跃议案索引

| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |
|---|---|---|---|---|---|---|---|
| CHG-20260907-001 | promoting | . | self | AI 自主交付：仅待临时目录处置 | cleanup | [CHG-20260907-001](logic_change.md#chg-20260907-001) | 2026-09-07 |
| CHG-20260907-002 | promoting | . | self | 解释性 HTML：仅待临时目录处置 | cleanup | [CHG-20260907-002](logic_change.md#chg-20260907-002) | 2026-09-07 |

---

**说明**：

当需要追踪修改时，在此文件中创建 CHG 条目。完成后：
1. 更新所属 `logic_readme.md`（宪法或领域，如规则变化）
2. 按通道归档到 `logic_version/records/`（中等规则/行为变化保留精简 VER，高风险完整 VER）
3. 把 CHG 的需求拆解三字段搬入 VER 记录后再删除 CHG 条目与根公报行（需求保全见 RULE-014；两级账本与公报见 RULE-018；操作步骤见 references/change-lifecycle.md 第 7-9 步）

本账本只放修宪议案（改全局规则、意图层、范围登记表、INV）；领域事务的 CHG 立在 `logic_domains/<domain>/logic_change.md`，并在此处"活跃议案索引"登记一行指向领域账本。

**记住**：logic_change.md 是临时的工作记录，不是长期真相源。

<a id="chg-20260907-001"></a>
## CHG-20260907-001: AI 自主交付

- status: promoting
- effective: false
- proposal_revision: 1
- recall_route: medium
- owner: self
- changed_by: Codex
- scope: .
- affected_scopes: .
- decision_confirmed_by: user
- decision_confirmed_at: 2026-09-07
- logic_temp: logic_version/working/logic_version-20260907-001-ai-delivery-closure/logic_temp.md
- raw_request: user:2026-09-07 本任务：AI 自主审核后完成并进入 logic_readme，人工交付后发现问题另开议案。
- decomposition: 明确 AI 验证与自动晋升；区分交付和上线；取消默认人工验收等待；同步技能入口。
- fit_analysis: 新增 INT-20260907-001，补充 FLOW-002 的验证与收尾，保留必要测试和真实发布证据。
- 当前证据: 用户需求及方案已固化在 [本次 VER](logic_version/records/logic_version-20260907-001-ai-delivery-closure.md)；文档已更新，技能格式校验通过。
- 清理授权: user:2026-09-07 本轮“认可你的建议，可以删除”；无需再次征求删除同意。
- 晋升清单: 现行规则、VER 与索引就位；已核对固定路径及无重解析点，但删除仍被执行策略阻止，目录尚未清理；等待执行限制解除或手动清理。

<a id="chg-20260907-002"></a>
## CHG-20260907-002: 解释性 HTML

- status: promoting
- effective: false
- proposal_revision: 1
- recall_route: medium
- owner: self
- changed_by: Codex
- scope: .
- affected_scopes: .
- decision_confirmed_by: user
- decision_confirmed_at: 2026-09-07
- logic_temp: logic_version/working/logic_version-20260907-002-html-explainers/logic_temp.md
- raw_request: user:2026-09-07 本任务：参照 EduAI explainers，需要解释性文档时在 explainers 生成对应 HTML 查看。
- decomposition: 增加按需 HTML 产物约定、来源和快照语义、交付链接与查看要求，并制作本次流程说明。
- fit_analysis: 新增 INT-20260907-002，补充 FLOW-003 的面向用户解释输出，不创建平行制度。
- 当前证据: 用户需求及方案已固化在 [本次 VER](logic_version/records/logic_version-20260907-002-html-explainers.md)；文档已更新，技能格式校验通过。
- 清理授权: user:2026-09-07 本轮“认可你的建议，可以删除”；无需再次征求删除同意。
- 晋升清单: 现行规则、VER 与索引就位；已核对固定路径及无重解析点，但删除仍被执行策略阻止，目录尚未清理；等待执行限制解除或手动清理。
