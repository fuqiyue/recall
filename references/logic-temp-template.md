# logic_temp.md 模板

`logic_temp.md` 是复杂变更期间可选的、短期工作记录。它不属于当前制度、活跃议案或历史真源；默认只在 `logic_version/working/<version_slug>/` 下创建，并在议案结束时清理。

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

## 清理与晋升

- promote_to: <logic_change 条目、logic_version 记录或 ADR>
- final_cleanup: <议案结束时删除整个 working/<version_slug> 的条件、日期和负责人>
~~~

维护规则：

- 只记录可审计事实、证据、问题、决定摘要、文件和测试；不记录隐藏思维链、逐轮试错或整段聊天。
- 不能在这里写入“当前已生效规则”，不能放 `logic_readme.md`、`logic_change.md`、源码副本或运行数据副本。
- `expires` 到期只报告并要求复核，不自动升级为制度；完成后把可复用结论提炼到议案/版本/ADR，再删除整个临时目录。working 中不得保留 closed/discarded 记录。
