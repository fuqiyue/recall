# logic_temp.md 模板

本模板仅供存量任务兼容。新任务在 `logic_changes/<任务>/logic_change.md` 直接维护产物台账，见[工作路径与任务](workspace-tasks.md)，不另建工作日志。旧 `logic_temp.md` 在 `logic_version/working/<version_slug>/` 中读写，关案后删除；被 Git 忽略不代表已清理。

- `medium` / `high` 必须有产物台账，但新任务内联，旧任务沿用现有文件，不能双写；`simple` 在最终汇报列处置清单。
- 议案关闭的前提是"工作区产物台账"清零：没有未执行的 `delete`，没有 `pending`。清零后把处置事实提炼到CHG，再删除本次 working 目录；核删除结果后在待定稿 `VER-*` 的 `logic_temp_cleanup` 写实并归档，不改写已归档历史。

~~~markdown
# Temporary Recall Worklog: <标题>

## 临时记录控制

- temp_id: TMP-YYYYMMDD-NNN
- source_change_id: CHG-YYYYMMDD-NNN
- proposal_revision: <对应的 CHG 正整数版本；方案变化后更新>
- version_id: VER-YYYYMMDD-NNN
- version_slug: logic_version-YYYYMMDD-NNN-<scope>
- scope: <项目相对范围；跨模块时列出全部范围>
- affected_scopes: <全部 module_id/scope_path>
- owner: <团队/角色>
- created: YYYY-MM-DD
- last_updated: YYYY-MM-DD
- expires: YYYY-MM-DD
- state: working | ready-to-promote
- disposable: true
- sensitive_data: none | reviewed | restricted-external

## 使用边界

- purpose: <为何需要临时记录；例如跨模块协调或测试快照>
- source_of_truth: <包含 source_change_id 和 proposal_revision 正文的项目根相对 logic_change.md；不得填本文件>
- cleanup_condition: <议案完成/取消/回滚后的删除或关闭条件>
- temp_path: logic_version/working/<version_slug>/logic_temp.md

## 已核实事实

| 事实 | 证据 | 置信度 | 记录日期 |
|---|---|---|---|
| ... | code/test/runtime/user-confirmed | high/medium/low | YYYY-MM-DD |

## 待确认问题与选择

| question_id | 问题 | 会影响什么 | 负责人 | 状态/截止 |
|---|---|---|---|---|
| Q-001 | ... | 方案/兼容/数据安全 | ... | open/answered |

## 受影响文件、层和测试

| path | layer | intended_action | dependency/consumer | baseline | post-change |
|---|---|---|---|---|---|
| ... | runtime-code/runtime-data/preprocess/test-fixture | ... | ... | ... | ... |

## 工作区产物台账

| path | artifact_kind | disposition | reason | cleaned_at |
|---|---|---|---|---|
| ... | deliverable / evidence / test / probe / scratch / fixture / generated | keep / delete / pending | <正式交付物/证据为何保留；非交付物删除> | YYYY-MM-DD 或 - |

## 清理与晋升

- promote_to: <logic_change 条目、logic_version 记录或 ADR>
- ledger_cleared: yes | no（台账无未执行的 delete、无 pending 时为 yes；no 不得关闭议案）
- final_cleanup: <台账清零后删除整个 working/<version_slug> 的条件、日期和负责人>
~~~

维护规则：

- 只记录可审计事实、证据、问题、决定摘要、文件和测试；不记录隐藏思维链、逐轮试错或整段聊天。
- 不能在这里写入“当前已生效规则”，不能放 `logic_readme.md`、`logic_change.md`、源码副本或运行数据副本。
- `expires` 到期只报告并要求复核，不自动升级为制度；完成后把可复用结论提炼到议案/版本/ADR，再删除整个临时目录。working 中不得保留 closed/discarded 记录。
- 台账登记本次**新建**交付物和临时产物。`keep` 仅限正式交付物/证据；非交付物由实施代理核实归属后删除。`gitignore` 不能作为处置结果，先按真实文件复核，不能只改台账状态。
- Recall 检查命令只核对台账和实物（UXI-006）；代理按 RULE-020/025 核验后沿用授权执行清理。台账不是自动删除脚本的输入，`recall status` 列出的未跟踪文件也不能代替归属核验。
