# Mini Recall Project

这是教学fixture。来源、日期与角色都是示例值，不构成真实项目授权。

## 文档控制
- doc_id: LOGIC-DEMO-ROOT
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
- governance_ref: git:example
- governance_evidence: git:example
- governance_verification: recorded
- governance_verified_at: 2026-10-12
- effective_from: 2026-10-12
- last_verified: 2026-10-12
- review_trigger: interval:90d; event:change
- source_of_truth: logic_readme.md
- source_decisions: none
- intent_summary: 用最小问候程序展示Recall接入和交接
- intent_sources: 示例设定；不是实际项目授权
- decision_validity: valid
- validity_evidence: 教学fixture及自动化验证

## 目标与边界
- 负责：最小示例问候和Recall接入/交接
- 不负责：真实服务、部署与Git同步
- 上级制度：none
- 允许的例外：none
## 范围登记与归属
- canonical_readme: logic_readme.md
- canonical_change: logic_change.md
- owned_paths: logic_readme.md, logic_change.md, logic_domains/, src/, tests/, AGENTS.md
- child_policy: inherit
- data_owner: none
- registry_status: registered
## 当前制度
| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-001 | ordinary | 问候行为由core领域维护 | 示例只保留一份现行行为 | none | 教学设定 | tests/test_app.py | valid | 2026-10-12 | self |
## 代码地图
| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| logic_readme.md、logic_change.md、logic_domains/ | source/runtime-code | public | Recall文档边界 | 示例需求 | 规则与任务上下文 | 所属文档 | yes | audit/route |
- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: source/runtime-code
- version_root: logic_version/
- temp_root: logic_version/working/
- unmapped_paths: .agents/ (代理配置)
### 范围登记表
| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [root](logic_readme.md) | [changes](logic_change.md) | self | active |
| MOD-CORE | logic_domains/core | in-system | domain/runtime-code | paired | [core](logic_domains/core/logic_readme.md) | [changes](logic_domains/core/logic_change.md) | self | active |
## 功能意图与用户流程
### 功能意图登记
| intent_id | 功能入口 | intent | 流程位置 | 关联规则 | 代码锚点 | 来源 | last_verified |
|---|---|---|---|---|---|---|---|
| INT-20261012-001 | greet | 用名字生成问候 | FLOW-001#1 | RULE-001, RULE-002 | src/app.py#greet | user-confirmed:2026-10-12 教学设定 | 2026-10-12 |
### 用户流程
- FLOW-001：1. 传入名字 → INT-20261012-001。
## 数据与控制流
name → greet → 问候文本
## 消费者与公共契约
greet(name)接受字符串，返回字符串；无持久数据。
## 不可破坏约束
- INV-001：规则正文和活跃正文各保留唯一位置。
## 兼容与迁移制度
示例无运行数据迁移。
## 测试与验证
- python -m unittest discover -s tests；recall audit / route / index / next
## 有效决策索引
无历史记录；交付后按实际需要生成。
## 活跃议案入口
- 唯一入口：[logic_change.md](logic_change.md)
## 当前限制
示例不是运行服务；不配置远端或自动推送。
