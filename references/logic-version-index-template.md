# logic_version/index.md 模板

这是项目根集中不可变决策记录和临时工作区的检索目录，不是当前制度。只登记记录位置和最小摘要；默认 Recall 不加载全部目标文件。

~~~markdown
# Logic Version Index

## 索引控制

- history_format: 2
- history_root: logic_version/
- root_only: true
- allowed_children: records, working, decisions, backups, index.md
- last_updated: YYYY-MM-DD
- owner: <团队/角色>

## 不可变决策记录

| version_id | version_slug | date | status | affected_scopes | linked_rule_ids | confirmed_revision | summary | path |
|---|---|---|---|---|---|---|---|---|
| VER-... | logic_version-... | YYYY-MM-DD | effective/rejected/cancelled/rolled-back/correction | ... | RULE-.../none | <proposal_revision/none> | ... | [records/logic_version-...md](records/logic_version-...md) |

## 活跃临时记录

| version_id | change_id | state | affected_scopes | expires | path |
|---|---|---|---|---|---|
| VER-... | CHG-... | working/ready-to-promote | ... | YYYY-MM-DD | [logic_temp.md](working/logic_version-.../logic_temp.md) |

closed/discarded 的临时记录不得长期留在 working；完成后删除该行，并由不可变决策记录记载清理结果。

## 决策记录

| ADR | status | linked_rule_ids | scope | summary | path |
|---|---|---|---|---|---|
| ADR-... | active/superseded/... | RULE-.../none | ... | ... | [decisions/ADR-...md](decisions/ADR-...md) |

## 备份清单

| backup_id | date | CHG-ID | storage | retention | manifest |
|---|---|---|---|---|---|
| BAK-... | YYYY-MM-DD | CHG-... | repository/external | ... | [backups/.../manifest.md](backups/.../manifest.md) |

## 读取策略

- 日常读取根 `logic_readme.md` 和根 `logic_change.md`，不默认读取本目录。
- 先根据 CHG-ID、VER-ID、ADR、范围或日期定位，再读取单条记录。
- `logic_temp.md` 只在当前 CHG-ID 明确引用且确需协调时读取，不能替代议案。
- 默认不读取 backups 内容；只有恢复或核验明确要求时读取 manifest 和必要文件。
~~~

新增不可变决策记录、临时记录、勘误或到期备份时更新对应索引行。禁止在本目录放模块制度、活跃议案正文、源码或运行数据。
