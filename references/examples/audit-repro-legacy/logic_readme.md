# Demo Logic

## 文档控制

- doc_id: LOGIC-DEMO
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
- effective_from: 2026-07-22
- last_verified: 2026-07-22
- review_trigger: release
- source_of_truth: src/app.py
- source_decisions: none
- intent_summary: keep current project logic discoverable
- decision_validity: valid
- validity_evidence: user-confirmed:2026-07-22
- canonical_readme: logic_readme.md
- canonical_change: logic_change.md
- owned_paths: src
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 范围登记与归属

- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: runtime-code and test
- version_root: logic_version/
- temp_root: logic_version/working/

### 范围登记表

| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [root](logic_readme.md) | [changes](logic_change.md) | self | active |
| MOD-APP | src | in-system | module/runtime-code | inherited | [app policy](logic_readme.md#scope-mod-app) | [changes](logic_change.md) | self | active |

<a id="scope-mod-app"></a>
### MOD-APP: Application

- scope_path: src

## 当前制度

Current behavior is defined by the code and this policy. Why: keep the current
contract discoverable before changing implementation details.

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|
| src/app.py | source/runtime-code | application | input | output | code | yes | tests/test_app.py |

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)

## Legacy approval registry

- authority_id: AUTH-SELF
