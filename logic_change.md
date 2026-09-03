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
- last_updated: 2026-09-04
- active_changes: 1

## 议案规则

- 本文件所有条目默认 `effective: false`
- 允许状态：draft | awaiting-decision | implementing | verifying | promoting | blocked
- 个人小项目使用简化流程：draft -> implementing -> verifying -> promoting
- 高风险修改使用决策流程：draft -> awaiting-decision -> implementing -> verifying -> promoting

## 讨论主题索引

| topic_id | 同类议题/共享问题 | coordinator | discussion_refs | related_changes | status |
|---|---|---|---|---|---|

当前无活跃讨论主题。表头保留以声明 schema。

## 活跃议案索引

| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |
|---|---|---|---|---|---|---|---|
| CHG-20260904-004 | draft | . | self | Density 硬上限越线与无领域是否让静态门失败 | none | [CHG-20260904-004](logic_change.md#chg-20260904-004) | 2026-09-04 |
| CHG-20260904-003 | draft | logic_domains/toolchain | self | validate 兼容消费项目的 slug 型 CHG-ID 与扩展 VER 模板 | none | [CHG-20260904-003](logic_domains/toolchain/logic_change.md#chg-20260904-003) | 2026-09-04 |

<a id="chg-20260904-004"></a>
## CHG-20260904-004: Density 硬上限越线与无领域是否让静态门失败

### 元数据

- status: draft
- effective: false
- recall_route: medium
- proposal_revision: 1
- decision_confirmed_by: none
- decision_confirmed_at: none
- owner: self
- changed_by: Claude (AI 代理)
- created: 2026-09-04
- last_status_change: 2026-09-04
- scope: .
- affected_scopes: ., logic_domains/toolchain
- authority_surfaces: RULE-022
- based_on: policy: logic_readme.md#RULE-022（Density advisory）; code: commit:c3bdff7; surfaces: RULE-022
- conflicts_with: none
- temp_path: none（draft；进入 implementing 前按 RULE-020 建立）

### 目标、理由与当前证据

- raw_request: 2026-09-03 eduai 只读复跑：logic_change 越过硬上限 21 倍静态门仍 PASS；无领域项目只收 `constitution-without-domains` 提示。2026-09-04 用户认可"待立案事项立成 draft CHG"（此前只在两处"当前限制"里写着"待立案"）
- decomposition: ① Density `exceeds-hard-limit` 是否进 current-state 门（宪法 250 / 领域 400 / 账本 300 / CHG 80）；② `constitution-without-domains` 是否进门（RULE-018 至少一个领域）；③ 若进门，消费项目一次性迁移窗口与 `--advisory-only` 逃生口；④ 用例：越线夹具 FAIL、advisory 开关 PASS
- fit_analysis: 扩展 INT-20260816-008（审计门）与 INT-20260816-011（拆分触发）；FLOW-005#4 从"AI 建议"升级为"门禁提示"；不新增 UXI；RULE-022 ③ 文本更新，可能波及 RULE-018 ④
- 当前证据：本仓库宪法 238/250、领域 87/400 与 112/400、账本均未越线；eduai 是唯一已知越线消费者

### 方案与决策

- 待用户裁决：A 硬上限进门 + 逃生开关；B 保持 advisory、只在 `recall status` 高亮；C 仅"无领域"进门、Density 不进
- 回滚：git revert；晋升目标：RULE-022 ③（及 RULE-018 ④）文本 + VER 精简记录

---

**说明**：

当需要追踪修改时，在此文件中创建 CHG 条目。完成后：
1. 更新所属 `logic_readme.md`（宪法或领域，如规则变化）
2. 归档到 `logic_version/records/`（如为高风险）
3. 把 CHG 的需求拆解三字段搬入 VER 记录后再删除 CHG 条目与根公报行（需求保全见 RULE-014；两级账本与公报见 RULE-018；操作步骤见 references/change-lifecycle.md 第 7-9 步）

本账本只放修宪议案（改全局规则、意图层、范围登记表、INV）；领域事务的 CHG 立在 `logic_domains/<domain>/logic_change.md`，并在此处"活跃议案索引"登记一行指向领域账本。

**记住**：logic_change.md 是临时的工作记录，不是长期真相源。
