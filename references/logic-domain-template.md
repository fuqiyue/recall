# 领域文档模板（logic_domains/<domain>/）

领域只记录现行规则和代码地图，对应 RULE-018；新领域 `logic_domains/<domain>/logic_readme.md` 以 `doc_policy: readme-only` 登记，任务集中在 `logic_changes/`。可重建文件清单由 `recall inventory --write` 生成到领域 `file_map.md`。旧paired领域仍兼容，迁移时不复制任务正文。模板见[根文档](logic-readme-template.md)及[任务](logic-change-template.md)。

## 何时新建 / 拆分 / 合并领域

- **新建**：接入时至少一个领域（小项目用 `logic_domains/core/` 覆盖全部代码即可）；出现独立职权路径、独立发布节奏或团队边界时再增。
- **拆分（大部门拆小部门）**：领域 readme 越过目标 250 行（Density 段 `over-target` 提示）且压缩后仍不足，或某组规则/代码地图行明显自成一块。拆出的新领域接管一部分 `owned_paths`，原领域相应收窄。
- **合并**：两个领域规则都很少、职权路径频繁一起改动时，合回一个大部门。
- 三者都是修宪案：在唯一任务文件立 CHG 并登记根公报，改登记表行，再动领域文件；步骤见[项目接入流程](project-onboarding.md)的"领域划分与拆分"。

## 宪法范围登记表中要加的行

```markdown
| MOD-<NAME> | logic_domains/<domain> | in-system | domain/runtime-code | readme-only | [<name>](logic_domains/<domain>/logic_readme.md) | none | self | active |
```

## 领域 logic_readme.md

~~~markdown
# <领域名称> Logic

## 文档控制

- module_id: MOD-<NAME>
- scope: logic_domains/<domain>
- scope_path: logic_domains/<domain>
- parent: ../../logic_readme.md
- parent_module_id: MOD-ROOT
- membership: in-system
- scope_type: domain
- layer: runtime-code
- module_doc_policy: readme-only
- status: active | transitional
- owner: <self/团队/角色>
- governance_mode: <与宪法相同：personal | collaborative>
- governance_ref: <与宪法相同或本领域的实际控制引用>
- governance_evidence: <控制证据；例如 git:<ref>>
- governance_verification: verified | recorded | unavailable | not-applicable
- governance_verified_at: YYYY-MM-DD | none
- effective_from: YYYY-MM-DD | event-driven
- last_verified: YYYY-MM-DD
- review_trigger: interval:90d; event:release,api-schema-change
- source_of_truth: <本领域代码、Schema 或外部系统的权威位置>
- source_decisions: <有效 VER/ADR ID；无则 none>
- intent_summary: <本领域服务的已确认意图摘要；对应宪法 INT 条目>
- intent_sources: <支持摘要的 VER/ADR 或宪法 INT-*；无则 none>
- decision_validity: valid | under-review | uncertain
- validity_evidence: <最近核验、用户确认或有效 ADR；未知填 unknown>

## 目标与边界

- 负责：<本领域的职权>
- 不负责：<明确非目标；相邻领域的职权>
- 上级制度：宪法全局规则（根 logic_readme.md）优先于本文件
- 允许的例外：<宪法授权的例外；没有填 none>

## 范围登记与归属

- canonical_readme: logic_domains/<domain>/logic_readme.md
- canonical_change: none
- owned_paths: <职权路径，逗号分隔；例如 src/orders/, tests/test_orders.py>
- child_policy: inherit
- data_owner: <运行数据负责人；不适用填 none>
- registry_status: registered

不含 root-only 字段（coverage_policy、membership_policy、layer_policy、version_root、temp_root）与范围登记表；这些只在宪法维护。

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-<NNN> | key/ordinary | ... | ... | [VER-...](../../logic_version/records/logic_version-...md) / none | 用户确认/ADR/VER | code/test/runtime | valid/under-review | YYYY-MM-DD | ... |

RULE 编号与宪法及其他领域共用同一编号空间，不得重复；只写 `owned_paths` 内已生效的规则。迁移时保留原编号和完整条款，更新范围与引用；根只留阅读触发条件，不留规则副本。

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| path/in/owned_paths / symbol | source/runtime-code | public / persisted / security / internal | ... | ... | ... | ... | yes/no | ... |

`contract_class` 取值与用途见[logic_readme 模板](logic-readme-template.md)代码地图节。

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | RULE-<NNN> | ... | ... | test path/CI policy |

## 不可破坏约束（可选）

- INV-<NNN>: <仅限本领域的约束；跨领域约束写入宪法>

## 活跃议案入口

- 全项目任务入口：[logic_change.md](../../logic_change.md)

## 当前限制（可选）

- <已确认且仍存在的限制>
~~~

## 旧领域账本兼容

旧paired领域的change可继续读取；新任务写到logic_changes，全部关闭后可将登记改为readme-only并删除空旧账本。
