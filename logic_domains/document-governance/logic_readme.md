# 文档治理现行规则

只在处理本领域事项时读取；全局规则与意图在[根现行文档](../../logic_readme.md)。本文是下列规则的唯一现行定义，references 只提供字段与操作方法。

## 文档控制
- doc_id: LOGIC-RECALL-DOCUMENT-GOVERNANCE
- module_id: MOD-DOCUMENT-GOVERNANCE
- scope: logic_domains/document-governance
- scope_path: logic_domains/document-governance
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
- source_of_truth: logic_domains/document-governance/logic_readme.md
- source_decisions: VER-20261026-002；其余见规则决策列
- intent_summary: 按需维护完整现行规则，控制根必读成本；渐进接入和可重建展示有明确边界
- intent_sources: INT-20260816-010, INT-20260816-011, INT-20260907-002
- decision_validity: valid
- validity_evidence: user:2026-10-26；从根迁移，规则语义不变

## 范围登记与归属
- canonical_readme: logic_domains/document-governance/logic_readme.md
- canonical_change: none
- owned_paths: logic_domains/document-governance/, references/document-model.md, references/logic-readme-template.md, references/logic-domain-template.md, references/field-vocabulary.md, references/governance-modes.md, references/project-onboarding.md, references/agent-entry-template.md, references/logic-version-template.md, references/logic-version-index-template.md, references/decision-record-template.md, references/backup-manifest-template.md, references/logic-vs-code-recall.md, references/recall-brief-template.md, references/explainers.md, explainers/, logic_version/
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度
| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-016 | key | 接入先建根骨架、范围登记、至少一个领域和INT/FLOW访谈初稿；存量模块标pending-docs，仅在新项目开始使用或用户单独要求时渐进补全；扫描意图标code-derived，经用户确认才落为实施依据。 | 避免全库扫描和未经确认的推断污染意图。 |[VER-20260816-003](../../logic_version/records/logic_version-20260816-003-semantic-link.md)；[VER-20260903-004](../../logic_version/records/logic_version-20260903-004-two-level-docs.md)；[VER-20261026-002](../../logic_version/records/logic_version-20261026-002-root-domain-slim.md) | 用户确认；历史依据见决策记录 | references/project-onboarding.md + SKILL.md 接入章节 | valid | 2026-09-04 | self |
| RULE-022 | key | ①SKILL只保留关键入口、需求记录、三通道、边界、命令和按需参考，细节唯一存references；②审计器结构/函数长度属RULE-024；③Density的行数目标、单CHG>80与blocked积累仅提示，文档硬限/无领域进门，advisory-only只改退出码；根及登记领域token成本目标也仅提示，数值见字段词汇；④规则分子条款、why留一句，事故叙事归VER。 | 控制必读成本，保持规则可引用。 |[VER-20260831-001](../../logic_version/records/logic_version-20260831-001-entry-slim-skill-front.md)；[VER-20260903-002](../../logic_version/records/logic_version-20260903-002-structure-context-cost.md)；[VER-20260903-003](../../logic_version/records/logic_version-20260903-003-structural-closure.md)；[VER-20260904-002](../../logic_version/records/logic_version-20260904-002-docs-consolidation.md)；[VER-20260904-005](../../logic_version/records/logic_version-20260904-005-density-gate.md)；[VER-20260906-001](../../logic_version/records/logic_version-20260906-001-constitution-slim-alignment.md)；[VER-20261011-003](../../logic_version/records/logic_version-20261011-003-maintenance-boundaries.md)；[VER-20261012-001](../../logic_version/records/logic_version-20261012-001-skill-document-clarity.md)；[VER-20261012-002](../../logic_version/records/logic_version-20261012-002-six-improvements.md)；[VER-20261013-001](../../logic_version/records/logic_version-20261013-001-reliable-context.md)；[VER-20261026-002](../../logic_version/records/logic_version-20261026-002-root-domain-slim.md) | 用户确认；历史依据见决策记录 | SKILL.md; 文档模型; recall_audit | valid | 2026-10-13 | Codex |
| RULE-026 | ordinary | 持久流程/架构/方案/状态说明用项目explainers HTML，简单问答不建页，用户格式优先；标日期、来源与已核/未核边界，相关页优先更新，日期快照另标；计数按声明账本重算；登记可重建交付物，不能成为平行制度或唯一决策位置。 | 提供可读展示并保持制度唯一。 |[VER-20260907-002](../../logic_version/records/logic_version-20260907-002-html-explainers.md)；[VER-20261026-002](../../logic_version/records/logic_version-20261026-002-root-domain-slim.md) | user:2026-09-07 | references/explainers.md 与 explainers/ 实际产物 | valid | 2026-09-07 | Codex |

## 代码地图
| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| references/document-model.md、logic-readme-template.md、logic-domain-template.md | source/runtime-code | public | 文档结构与根/领域拆分步骤 | 现行规则与范围 | 目录、模板 | 本领域及根规则；模板字段 | yes | audit/route |
| references/field-vocabulary.md、governance-modes.md、project-onboarding.md、agent-entry-template.md | source/runtime-code | public | 字段、治理、渐进接入与代理入口 | 真实项目来源 | 操作模板 | 所属readme；模板字段 | yes | tests/test_audit_logic_map.py |
| references/logic-version-template.md、logic-version-index-template.md、decision-record-template.md、backup-manifest-template.md | source/runtime-code | persisted | 变更留档字段与索引模板 | 已核验修改事实 | 留档格式 | 模板字段；根历史边界 | yes | tests/test_recall_cli.py |
| references/logic-vs-code-recall.md、recall-brief-template.md、explainers.md | source/runtime-code | internal | 回忆边界与展示操作 | 现行文档/真实证据 | 按需说明 | 根与本领域 | yes | audit |
| explainers/ | generated | internal | 可重建HTML展示 | 现行文档与运行证据 | 页面 | 对应来源 | yes | browser |
| logic_version/ | source/runtime-code | persisted | 只追加变更留档，index为全量索引 | 已结束修改与验证 | records/index | 原记录；新增勘误 | index yes; records no | validate |

## 维护与验证
- 接入/拆域先读[项目接入](../../references/project-onboarding.md)及[文档模型](../../references/document-model.md)；字段和密度数值见[字段词汇](../../references/field-vocabulary.md)，不在此复制。
- 搬迁时保留 RULE-ID、完整条款、证据和反链，登记 owned_paths 并更新当前指针；规则仍唯一，根仅保留领域阅读触发条件。
- 任务方案、进度与交付判据见[任务交付](../task-workflow/logic_readme.md)；模板字段解析及静态门实现见[工具链](../toolchain/logic_readme.md)。
- 核验：`recall audit --json`、`recall validate`，按相关文件/RULE/INT检查 `recall route`；必要时验证模板消费者。历史文件只核格式与完整性，不因本领域管辖历史路径而自动读取其正文。

## 活跃议案入口
- [根任务公报](../../logic_change.md)；正文唯一位于 logic_changes/，按任务 scope/affected_scopes 关联本领域。
