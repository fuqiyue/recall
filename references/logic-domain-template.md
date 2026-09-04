# 领域文档模板（logic_domains/<domain>/）

二级文档（部门法）模板，对应 RULE-018 一二级拆分法。一个领域 = `logic_domains/<domain>/logic_readme.md` + `logic_domains/<domain>/logic_change.md` 一对文件，并以 `doc_policy: paired` 登记在宪法（根 `logic_readme.md`）的范围登记表。未登记即平行真源（INV-001/INV-002），审计拒绝。宪法模板见 [logic_readme 模板](logic-readme-template.md)，根账本模板见 [logic_change 模板](logic-change-template.md)。

## 何时新建 / 拆分 / 合并领域

- **新建**：接入时至少一个领域（小项目用 `logic_domains/core/` 覆盖全部代码即可）；出现独立职权路径、独立发布节奏或团队边界时再增。
- **拆分（大部门拆小部门）**：领域 readme 越过目标 250 行（Density 段 `over-target` 提示）且压缩后仍不足，或某组规则/代码地图行明显自成一块。拆出的新领域接管一部分 `owned_paths`，原领域相应收窄。
- **合并**：两个领域规则都很少、职权路径频繁一起改动时，合回一个大部门。
- 三者都是修宪案：在根 `logic_change.md` 立 CHG，改登记表行，再动领域文件；步骤见[项目接入流程](project-onboarding.md)的"领域划分与拆分"。

## 宪法范围登记表中要加的行

```markdown
| MOD-<NAME> | logic_domains/<domain> | in-system | domain/runtime-code | paired | [<name>](logic_domains/<domain>/logic_readme.md) | [changes](logic_domains/<domain>/logic_change.md) | self | active |
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
- module_doc_policy: paired
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
- canonical_change: logic_domains/<domain>/logic_change.md
- owned_paths: <职权路径，逗号分隔；例如 src/orders/, tests/test_orders.py>
- child_policy: inherit
- data_owner: <运行数据负责人；不适用填 none>
- registry_status: registered

不含 root-only 字段（coverage_policy、membership_policy、layer_policy、version_root、temp_root）与范围登记表；这些只在宪法维护。

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-<NNN> | key/ordinary | ... | ... | [VER-...](../../logic_version/records/logic_version-...md) / none | 用户确认/ADR/VER | code/test/runtime | valid/under-review | YYYY-MM-DD | ... |

RULE 编号与宪法及其他领域共用同一编号空间，不得重复；只写 `owned_paths` 内已生效的规则。

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

- 唯一入口：[logic_change.md](logic_change.md)

## 当前限制（可选）

- <已确认且仍存在的限制>
~~~

## 领域 logic_change.md

~~~markdown
# <领域名称> Active Changes

## 文档控制

- scope: logic_domains/<domain>
- scope_path: logic_domains/<domain>
- module_id: MOD-<NAME>
- current_policy: logic_readme.md
- owner: <self/团队/角色>
- governance_mode: <与宪法相同>
- governance_ref: <实际 Git/PR/CI 控制引用>
- governance_evidence: <控制证据>
- governance_verification: verified | recorded | unavailable | not-applicable
- governance_verified_at: YYYY-MM-DD | none
- last_updated: YYYY-MM-DD
- active_changes: <本文件 CHG 正文数量；无正文填 none（0 同义）>

## 议案规则

- 议案语义见 RULE-018 与 [logic_change 模板](../../references/logic-change-template.md)；本账本只放本领域一事一议的 CHG 正文，`affected_scopes` 必含 `logic_domains/<domain>`、不得含 `.`（触及宪法的议案立在根账本），每个 CHG 同时在根账本公报占一行。

## 讨论主题索引

| topic_id | 同类议题/共享问题 | coordinator | discussion_refs | related_changes | status |
|---|---|---|---|---|---|
| TOPIC-YYYYMMDD-NNN | ... | ... | ... | CHG-... / none | open |

## 活跃议案索引

| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |
|---|---|---|---|---|---|---|---|
| CHG-YYYYMMDD-NNN | draft | logic_domains/<domain> | ... | ... | none | [CHG-YYYYMMDD-NNN](logic_change.md#chg-yyyymmdd-nnn) | YYYY-MM-DD |

<a id="chg-yyyymmdd-nnn"></a>
## CHG-YYYYMMDD-NNN: <议案标题>

- status: draft
- effective: false
- proposal_revision: 1
- recall_route: simple | medium | high
- owner: <...>
- changed_by: self
- scope: <路径、契约或行为>
- affected_scopes: logic_domains/<domain>[; logic_domains/<other>]
- 目标 / 理由与当前证据 / 影响范围 / 方案与决策 / 回滚 / 晋升目标：<personal 最小块，见 logic_change 模板 RULE-023 段>
~~~

维护要点：领域文档与宪法同受 `recall validate`（编号唯一、公报一致）和 `audit --current-state`（表结构、Density）检查；`recall route <路径>` 应能命中本领域，命不中说明 `owned_paths` 漏登。
