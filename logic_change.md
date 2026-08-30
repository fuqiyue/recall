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
- last_updated: 2026-08-31
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
| CHG-20260831-002 | awaiting-decision | scripts/git_sync.py, scripts/init_recall.py | self | 是否收缩 Git 同步表面（退回通用 pull/rebase/push 给代理/用户原生执行） | 用户决定 | [CHG-20260831-002](logic_change.md#chg-20260831-002) | 2026-08-31 |

<a id="chg-20260831-002"></a>
## CHG-20260831-002: 是否收缩 Git 同步表面

### 元数据

- status: awaiting-decision
- effective: false
- topic_id: none
- recall_route: high
- proposal_revision: 1
- decision_gate: required
- decision_state: pending
- confirmed_proposal_revision: none
- decision_confirmed_by: none
- decision_ref: none
- decision_confirmed_at: none
- decision_record: required
- semantic_review_state: pending
- semantic_reviewed_by: none
- semantic_review_ref: none
- semantic_reviewed_at: none
- governance_execution_ref: none
- owner: self
- changed_by: AI 代理（Claude，2026-08-31 会话）
- proposer: 2026-08-31 架构评估会话
- created: 2026-08-31
- last_status_change: 2026-08-31
- review_due: event-driven
- target_effective: event-driven
- scope: scripts/git_sync.py, scripts/init_recall.py
- affected_scopes: .
- related_modules: MOD-ROOT
- related_decisions: none
- authority_surfaces: RULE-010; RULE-011; UXI-001; UXI-002
- based_on: policy: logic_readme.md#当前制度 RULE-010/011; code: commit:2b8e7ce; surfaces: RULE-010; RULE-011; UXI-001; UXI-002
- depends_on: none
- conflicts_with: RULE-010; RULE-011; UXI-001; UXI-002
- conflict_resolution: unresolved
- history_retention: full
- runtime_state: not-implemented
- runtime_environments: none
- feature_flag: none
- intent_source_refs: session:2026-08-30-架构评估; session:2026-08-31-优化授权; VER-20260831-002
- intent_traceability: INT-20260816-005 -> RULE-011 -> test:tests/test_git_sync.py -> VER-20260811-003
- intent_digest: 目标：减少 Recall 自有 Git 包装代码的维护面。非目标：削弱 hook 回填与未跟踪文件排除的安全策略。约束：不得未经用户确认推翻 RULE-010/011。验收：用户在 A/B 中明确选择。开放问题：用户是否愿意用"手动 Git 序列"换"更小脚本面"。
- intent_status: inferred
- blocked_by: 用户决定
- next_action: 用户在决策检查点的 A/B 中选择；owner: self
- unblock_condition: 用户明确选择 A 或 B
- reserved_version_id: none
- version_slug: none
- temp_path: none
- docs_impact: 选 B 时需改 RULE-010/011、UXI-001/002、git_sync.py 与测试；选 A 时关闭本条、不改任何现行制度

### 需求拆解

- raw_request: 2026-08-30 架构评估——"收缩 Git 管道代码：pull-rebase-push 通用包装可退回代理/用户原生执行，脚本只保留受管理 hook、after_commit 回填、未跟踪文件排除三件特有的事"；2026-08-31 用户认可评估并授权优化
- decomposition: 若实施：① `recall sync` 移除 pull/push 包装或降级为可选；② 保留 hook 安装、回填、自动保存安全策略；③ 更新 RULE-010/011 与相关测试
- fit_analysis: 与 INT-20260816-005（一条命令保存并同步全部进度）和 UXI-001/002（不手写 Git 序列）直接冲突——这是本条待决的原因

### 决策检查点

**冲突事实**：简化建议与 RULE-010/011（决策依据均为"用户要求/用户确认"，VER-20260811-001/003）及 UXI-001/002 实质矛盾；现有 sync 链路已被 tests/test_git_sync.py 20 个用例覆盖且运行稳定。

- **方案 A（建议）**：保持现状。理由：sync 的价值恰在"一条命令、零 Git 知识"的用户承诺；代码已测试稳定，维护成本已付清；收缩节省的是抽象数量而非实际风险
- **方案 B**：收缩表面。`recall sync` 只做自动保存提交 + 回填，pull/push 交还代理原生 git。收益：脚本与测试面变小；代价：违背 UXI-002，用户需重新学习 Git 序列，属用户可见行为回退

确认前不实施任何受影响部分（SKILL 核心原则 5）。

---

**说明**：

当需要追踪修改时，在此文件中创建 CHG 条目。完成后：
1. 更新 `logic_readme.md`（如规则变化）
2. 归档到 `logic_version/records/`（如为高风险）
3. 把 CHG 的需求拆解三字段搬入 VER 记录后再删除 CHG 条目（需求保全与落选方案归档的语义见 logic_readme.md RULE-014；操作步骤见 references/change-lifecycle.md 第 7-9 步）

**记住**：logic_change.md 是临时的工作记录，不是长期真相源。
