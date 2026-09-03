# Toolchain Domain Active Changes

## 文档控制

- scope: logic_domains/toolchain
- scope_path: logic_domains/toolchain
- module_id: MOD-TOOLCHAIN
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

- 本账本只放工具链领域一事一议的 CHG 正文；触及宪法（根规则、意图层、范围登记表、INV）的议案写在根 `logic_change.md`（RULE-018）。每条 CHG 同时在根账本"活跃议案索引"登记一行。字段与状态机见 references/logic-change-template.md，所有条目默认 `effective: false`

## 讨论主题索引

| topic_id | 同类议题/共享问题 | coordinator | discussion_refs | related_changes | status |
|---|---|---|---|---|---|

当前无活跃讨论主题。表头保留以声明 schema。

## 活跃议案索引

| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |
|---|---|---|---|---|---|---|---|
| CHG-20260904-003 | draft | logic_domains/toolchain | self | validate 兼容消费项目的 slug 型 CHG-ID 与扩展 VER 模板 | none | [CHG-20260904-003](logic_change.md#chg-20260904-003) | 2026-09-04 |

<a id="chg-20260904-003"></a>
## CHG-20260904-003: validate 兼容消费项目的 slug 型 CHG-ID 与扩展 VER 模板

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
- scope: logic_domains/toolchain
- affected_scopes: logic_domains/toolchain
- authority_surfaces: RULE-015
- based_on: policy: logic_domains/toolchain/logic_readme.md#RULE-015; code: commit:c3bdff7; surfaces: RULE-015
- conflicts_with: none
- temp_path: none（draft；进入 implementing 前按 RULE-020 建立）

### 目标、理由与当前证据

- raw_request: 2026-09-03 eduai 只读复跑：validate 的 CHG 发现只认 `CHG-YYYYMMDD-NNN`，消费项目 slug 型编号（`CHG-YYYYMMDD-UNIFIED-CLIENT-DATA` 一类）的三字段检查静默跳过；VER 必填段与 after_commit 正则只认最小模板与裸 SHA，扩展模板得到假错误。2026-09-04 用户认可"待立案事项立成 draft CHG"
- decomposition: ① validate 的 CHG-ID 正则与审计器 / `recall status` 共用一份（RULE-012/021 同一正则原则）；② VER 必填段识别 logic-version-template 的扩展 schema；③ after_commit 接受反引号包裹与 `commit:` 前缀；④ 用例：slug 型 CHG 缺三字段被报出、扩展模板记录无假错误
- fit_analysis: 复用 INT-20260816-008（validate）；FLOW-003#3 不变；不新增 UXI；RULE-015 ①③ 文本更新
- 当前证据：本仓库全部 CHG/VER 用最小模板，问题只在消费项目复现

### 方案与决策

- 待定：A 正则搬入 recall_common 统一导出；B validate 单独放宽——B 会再造第二份实现，违反 RULE-021
- 回滚：git revert；晋升目标：RULE-015 文本 + VER 精简记录
