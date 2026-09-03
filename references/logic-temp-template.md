# logic_temp.md 模板

`logic_temp.md` 是变更期间的短期工作记录，同时承担**收尾台账**：登记本次产生的每个文件是交付物还是废料、留还是删。它不属于当前制度、活跃议案或历史真源；只在 `logic_version/working/<version_slug>/` 下创建（该目录被 `recall init` 的 .gitignore 忽略，本地一次性），并在议案结束时删除。

- `medium` / `high` 通道**必建**（权威语义：RULE-020 收尾归零）；`simple` 通道不建文件，改为在最终汇报中列出处置清单。
- 议案关闭的前提是"工作区产物台账"清零：没有未执行的 `delete`，没有 `pending`。清零后删除整个 working 目录，并在 `VER-*` 的 `logic_temp_cleanup` 记录结果。

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
| ... | deliverable / test / probe / scratch / fixture / generated | keep / delete / gitignore / pending | <为何留或删；keep 的非交付物须写用户同意来源> | YYYY-MM-DD 或 - |

## 清理与晋升

- promote_to: <logic_change 条目、logic_version 记录或 ADR>
- ledger_cleared: yes | no（台账无未执行的 delete、无 pending 时为 yes；no 不得关闭议案）
- final_cleanup: <台账清零后删除整个 working/<version_slug> 的条件、日期和负责人>
~~~

维护规则：

- 只记录可审计事实、证据、问题、决定摘要、文件和测试；不记录隐藏思维链、逐轮试错或整段聊天。
- 不能在这里写入“当前已生效规则”，不能放 `logic_readme.md`、`logic_change.md`、源码副本或运行数据副本。
- `expires` 到期只报告并要求复核，不自动升级为制度；完成后把可复用结论提炼到议案/版本/ADR，再删除整个临时目录。working 中不得保留 closed/discarded 记录。
- 工作区产物台账登记本次**新建**的每个文件（交付物也登记，标 `deliverable/keep`，便于对账），以及为调试而修改后需要还原的文件。`artifact_kind` 只描述用途，`disposition` 才是处置决定：`delete` 由实施代理逐项执行并在最终汇报列出；`gitignore` 表示保留在本地但加入忽略规则；非交付物要 `keep` 必须写明用户同意的来源。
- 任何工具都不根据台账自动删除文件（UXI-003/UXI-006）：台账是给代理和用户看的处置清单，不是删除脚本的输入。`recall status` 列出的未跟踪文件是台账的核对来源，不是替代。
