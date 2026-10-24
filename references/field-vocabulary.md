# 字段词汇分层

个人模式保留下表 8 项基本内容；它们包含散文内容，不是“只填8个字段”的机器schema。机器必填与条件字段以下方审计器口径和[个人最小块](logic-change-template.md#personal-最小块)为准，其余按治理需要启用。

分层的原因：把全部字段当成默认必填会让单条 CHG 达到 80-200 行，与"避免上下文膨胀"直接矛盾。字段数量应该跟随真实治理需要，而不是跟随模板长度。

## 启用条件

| 层级 | 何时启用 | 字段数 |
|---|---|---|
| personal | 默认。单人或单人 + AI | 8项基本内容；机器字段另见下文 |
| collaborative | 真实存在多人分工，且已配置 PR/CI/CODEOWNERS 等外部控制 | +9 |
| compliance | 用户明确要求正式审查、审计留存或表单合规 | +13 |

只在上层条件真实成立时才启用上层字段。没有真实分工就填 `collaborative` 字段，等于制造第 9 条警告的"为符合流程造表单"。

## personal 层（8 项内容；审计器机器强制的字段名见下方"审计器口径"段，本表的散文项是内容要求而非字段名）

| 字段 | 含义 |
|---|---|
| `status` | `draft` \| `awaiting-decision` \| `implementing` \| `verifying` \| `promoting` \| `blocked` |
| `proposal_revision` | 方案版本号；实质修改方案/影响面/基线时递增，不等于修订表的执行轮次；表格用法见[多轮修订](workspace-tasks.md#多轮修订) |
| 目标 | 一句话说明要达到什么 |
| 理由 | 3-5 条，为什么这么做、放弃了什么 |
| 当前证据 | 读过的代码、测试、运行结果 |
| 影响范围 | 会改到哪些路径、谁会受影响 |
| 下一步 | 具体的下一个动作 |
| `decision_confirmed_by` + 日期 | 谁在哪天确认了当前 `proposal_revision` |

`decision_confirmed_by: self` 表示具备项目决策权的人明确作出了选择。执行代理不能用它确认自己的建议。

**personal 模式的 CHG 块不维护** `semantic_review_*`、`governance_execution_ref` 等独立审查/治理字段（RULE-023 只强制下方"审计器口径"列出的几项）。实施者与审查者是同一人时，分离的字段不增加控制力，只增加行数；需要记下自审结论时写一行自述即可。注意区分：`logic_readme` / `logic_change` 的文档控制段与 `VER-*` 的记录控制段里的 `governance_verification` + `governance_verified_at` 对所有治理模式都是审计必填，personal 填 `recorded` + 核验日期即可。

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

已结束任务的重复正文保全移动或原位待清理不新增CHG状态；退出活跃队列后，既有历史索引的“待清理文件”表保留 `task_id/original_path/path/archive/sha256/reason/recorded_at/exit_condition`。字段与步骤见[集中待清理](workspace-tasks.md#删除受阻的集中待清理)。workspace的 `pending_cleanup.cleanup_complete` 独立表示实物清理，不把移动当删除。

`conflict_resolution` 的非 `unresolved` 取值只记录已确认或已被更高优先级指令裁定的结果，不由代理自行选择。

## compliance 层（+13 个）

`decision_gate` `decision_record` `confirmed_proposal_revision` `reserved_version_id` `version_slug` `runtime_state` `runtime_environments` `feature_flag` `history_retention` `intent_source_refs` `intent_traceability` `docs_impact` `governance_execution_ref`

`intent_traceability` 维护 `INT-* -> RULE-* -> test:<path#anchor> -> VER-*` 链，连接可审计意图、现行规则、验证义务和关闭记录。只对保留历史的中等/高风险变更要求，简单修复不建链。`INT-*` 的登记正文位于根 `logic_readme.md` 的"功能意图登记"表，两处共用同一编号空间，且统一使用 `INT-YYYYMMDD-NNN` 完整格式（无日期短编号不被审计与追溯链识别）。

`effective: false` 只表示尚未成为当前制度。实际合并、部署、开关暴露用 `runtime_state`、`runtime_environments`、`feature_flag` 表达；已合并未部署、灰度部署和制度生效是三件不同的事。

## 工作路径与任务产物

| 字段 | 位置与含义 |
|---|---|
| `workspace_root` | 根readme；固定为`.`，以实际项目文件夹为根 |
| `scratch_root` | 根readme；默认`.work/`，临时代码放其下`临时-具体功能` |
| `data_roots` | 根readme；逗号/分号分隔的数据目录，盘点默认仅列上层 |
| `task_temp_dirs` | CHG；项目相对路径，任务独占，无则none |
| `path / artifact_kind / disposition / reason / cleaned_at` | 任务正文产物台账基础五列；keep限deliverable/runtime-data/evidence，临时物任务完成后delete，gitignore不是处置 |
| `retention_basis / exit_condition / round` | 新台账扩展列：保留依据、移除或复核触发条件、所属轮次；keep须有前两项，旧五列兼容，轮次核对须有round |
| `current_result / next_action / merged_from` | 顶部唯一当前结果与下一步；merged_from按需保留被并入的活跃CHG-ID，来源、修订事实随同一VER归档 |

新任务正文在logic_changes，原temp_root/temp_path仅供旧logic_temp兼容；操作见[工作路径与任务](workspace-tasks.md)。台账与文件核对不会自动删除。

## 长度上限

| 对象 | 目标 | 硬上限 |
|---|---|---|
| 单条活跃 CHG | 15-40 行 | 80 行 |
| 宪法（根 `logic_readme.md`） | < 150 行 | 250 行 |
| 领域 `logic_readme.md`（`logic_domains/<domain>/`） | < 250 行 | 400 行（越过目标 → 拆分领域，大部门拆小部门） |
| 根 / 旧领域 / 任务 `logic_change.md` 全文 | < 150 行 | 300 行 |
| 单条 `VER-*` | 50-150 行 | 200 行 |
| `SKILL.md` | < 130 行 | 200 行 |

超过硬上限时按顺序处理：压缩失效细节 → 把已结束内容归档到 `logic_version/` → 降低字段层级。不要靠未登记的新文件解决长度问题；正确出口是按 RULE-018 新建或拆分已登记领域（宪法过长 → 把领域内部规则下放到部门法；领域过长 → 拆成更小领域）。

`recall audit`（`audit_logic_map.py --current-state`）的 Density 段按层级报告：`exceeds-hard-limit`（文档越过硬上限）与 `constitution-without-domains`（宪法未登记任何领域）使 current-state / formal-review 静态门失败；`over-target`（领域 readme 附拆分提示）、单条 CHG 越过 80 行（`exceeds-chg-limit`）与 blocked 累积只提示。`--advisory-only` 让前两类也只提示，是存量项目的迁移窗口（RULE-022 ③，VER-20260904-005）。

行数门之外，必读入口的粗估token目标为 `SKILL.md` 3000、根readme及每份已登记领域readme 6000，均只提示，不改变退出码。路由与审计共用同一估算：CJK约1 token/字、其他约4字符/token；它用于比较阅读成本，不是模型的实际计费或分词数。

## 反模式

- 单人项目填 `collaborative` 字段，`semantic_reviewed_by` 和 `changed_by` 是同一个值
- 单条 CHG 有 30 个字段但只有一句实质理由
- `logic_change.md` 累积多条 `blocked` 条目长期不处理 —— blocked 超过 2 条说明该把决策交回用户，而不是继续记账
- 为简单修复创建 CHG、ADR 或空测试矩阵
- 用增加字段来回应"文档说不清楚"，正确做法通常是减少字段、增加理由
