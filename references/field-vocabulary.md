# 字段词汇分层

Recall 定义了约 30 个字段。**个人模式只需要 8 个**，其余按治理需要逐层启用。

分层的原因：把全部字段当成默认必填会让单条 CHG 达到 80-200 行，与"避免上下文膨胀"直接矛盾。字段数量应该跟随真实治理需要，而不是跟随模板长度。

## 启用条件

| 层级 | 何时启用 | 字段数 |
|---|---|---|
| personal | 默认。单人或单人 + AI | 8 |
| collaborative | 真实存在多人分工，且已配置 PR/CI/CODEOWNERS 等外部控制 | +9 |
| compliance | 用户明确要求正式审查、审计留存或表单合规 | +13 |

只在上层条件真实成立时才启用上层字段。没有真实分工就填 `collaborative` 字段，等于制造第 9 条警告的"为符合流程造表单"。

## personal 层（8 个必填）

| 字段 | 含义 |
|---|---|
| `status` | `draft` \| `awaiting-decision` \| `implementing` \| `verifying` \| `promoting` \| `blocked` |
| `proposal_revision` | 议案版本号；实质修改方案/影响面/基线时递增 |
| 目标 | 一句话说明要达到什么 |
| 理由 | 3-5 条，为什么这么做、放弃了什么 |
| 当前证据 | 读过的代码、测试、运行结果 |
| 影响范围 | 会改到哪些路径、谁会受影响 |
| 下一步 | 具体的下一个动作 |
| `decision_confirmed_by` + 日期 | 谁在哪天确认了当前 `proposal_revision` |

`decision_confirmed_by: self` 表示具备项目决策权的人明确作出了选择。执行代理不能用它确认自己的建议。

**personal 模式不维护** `semantic_review_*`、`governance_verification`、`governance_verified_at` 这些独立记录。实施者与审查者是同一人时，分离的字段不增加控制力，只增加行数。需要记下自审结论时写一行自述即可。

**审计器口径（RULE-023）**：`audit --current-state` 对 personal 模式的 CHG 块只强制 `status`、`effective: false`、`proposal_revision`、`recall_route`、`changed_by`，以及进入 `implementing`/`verifying`/`promoting` 前的 `decision_confirmed_by` + `decision_confirmed_at`（用户确认不随治理模式降级；`changed_by` 按治理模式文档要求诚实记录，故所有层级必填）。collaborative / compliance 层字段"缺则不查、写则照查"——写了就按完整规则校验。块自身 `governance_mode` 优先于账本模式；两者都缺按完整要求处理。`--formal-review` 与 collaborative 模式的要求不变。

## collaborative 层（+9 个）

| 字段 | 含义 |
|---|---|
| `owner` | 协调责任人 |
| `changed_by` | 实际修改人或代理 |
| `authority_surfaces` | 精确影响面：规则/API/Schema/字段/开关/用户行为 |
| `based_on` | 基线：当前制度 + 代码快照 + 同一批精确影响面 |
| `depends_on` | 版本绑定的 `CHG-ID@revision-N` |
| `conflicts_with` | 活跃 CHG 双方互指 |
| `conflict_resolution` | `unresolved` \| `merge` \| `supersede` \| `sequence-and-revalidate` |
| `semantic_review_*` | 实施后代码语义审查；高风险必须由非实施者完成 |
| `governance_evidence` + `governance_verification` + `governance_verified_at` | 责任人何时核验了哪项外部控制 |

被依赖条目改版、阻塞或关闭时，依赖项转为 `awaiting-decision` 或 `blocked`，不沿用旧确认继续实施。禁止循环依赖。

`conflict_resolution` 的非 `unresolved` 取值只记录已确认或已被更高优先级指令裁定的结果，不由代理自行选择。

## compliance 层（+13 个）

`decision_gate` `decision_record` `confirmed_proposal_revision` `reserved_version_id` `version_slug` `runtime_state` `runtime_environments` `feature_flag` `history_retention` `intent_source_refs` `intent_traceability` `docs_impact` `governance_execution_ref`

`intent_traceability` 维护 `INT-* -> RULE-* -> test:<path#anchor> -> VER-*` 链，连接可审计意图、现行规则、验证义务和关闭记录。只对保留历史的中等/高风险变更要求，简单修复不建链。`INT-*` 的登记正文位于根 `logic_readme.md` 的"功能意图登记"表，两处共用同一编号空间，且统一使用 `INT-YYYYMMDD-NNN` 完整格式（无日期短编号不被审计与追溯链识别）。

`effective: false` 只表示尚未成为当前制度。实际合并、部署、开关暴露用 `runtime_state`、`runtime_environments`、`feature_flag` 表达；已合并未部署、灰度部署和制度生效是三件不同的事。

## 长度上限

| 对象 | 目标 | 硬上限 |
|---|---|---|
| 单条活跃 CHG | 15-40 行 | 80 行 |
| `logic_change.md` 全文 | < 150 行 | 300 行 |
| `logic_readme.md` | < 250 行 | 400 行 |
| 单条 `VER-*` | 50-150 行 | 200 行 |
| `SKILL.md` | < 130 行 | 200 行 |

超过硬上限时按顺序处理：压缩失效细节 → 把已结束内容归档到 `logic_version/` → 降低字段层级。不要靠新建文件解决长度问题。

`python scripts/audit_logic_map.py <project-root> --current-state` 的 Density 段会报告越过硬上限的文件（`exceeds-hard-limit`）与越过目标值的文件（`over-target`）；两者都是 advisory，不影响静态门。

## 反模式

- 单人项目填 `collaborative` 字段，`semantic_reviewed_by` 和 `changed_by` 是同一个值
- 单条 CHG 有 30 个字段但只有一句实质理由
- `logic_change.md` 累积多条 `blocked` 条目长期不处理 —— blocked 超过 2 条说明该把决策交回用户，而不是继续记账
- 为简单修复创建 CHG、ADR 或空测试矩阵
- 用增加字段来回应"文档说不清楚"，正确做法通常是减少字段、增加理由
