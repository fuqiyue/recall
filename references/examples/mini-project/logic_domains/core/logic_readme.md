# Core Domain

## 文档控制
- doc_id: LOGIC-DEMO-CORE
- module_id: MOD-CORE
- scope: logic_domains/core
- scope_path: logic_domains/core
- parent: ../../logic_readme.md
- parent_module_id: MOD-ROOT
- membership: in-system
- scope_type: domain
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
- source_of_truth: src/app.py
- source_decisions: none
- intent_summary: 用最小问候程序展示Recall接入和交接
- intent_sources: 示例设定；不是实际项目授权
- decision_validity: valid
- validity_evidence: 教学fixture及自动化验证

## 目标与边界
- 负责：问候函数与测试
- 不负责：真实部署
- 上级制度：根logic_readme.md
- 允许的例外：none
## 范围登记与归属
- canonical_readme: logic_domains/core/logic_readme.md
- canonical_change: logic_domains/core/logic_change.md
- owned_paths: src/app.py, tests/test_app.py
- child_policy: inherit
- data_owner: none
- registry_status: registered
## 当前制度
| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-002 | ordinary | greet(name)返回Hello加名字 | 示例行为容易验证 | none | 教学设定 | tests/test_app.py | valid | 2026-10-12 | self |
## 代码地图
| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| src/app.py#greet | source/runtime-code | public | 生成问候 | name | str | src/app.py | yes | tests/test_app.py |
| tests/test_app.py | source/test-fixture | internal | 验证问候 | 固定名字 | unittest结果 | 测试断言 | yes | unittest |
## 数据与控制流
字符串输入到字符串输出。
## 消费者与公共契约
本地单元测试；greet(name)返回str。
## 不可破坏约束
- INV-002：示例不读写运行数据。
## 兼容与迁移制度
无。
## 测试与验证
| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | RULE-002 | python -m unittest discover -s tests | 问候断言通过 | tests/test_app.py |
## 活跃议案入口
- 唯一入口：[logic_change.md](logic_change.md)
## 当前限制
只展示Recall，不接外部消费者。
