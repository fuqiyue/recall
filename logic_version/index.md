# Logic Version Index

## 索引控制

- history_format: 2
- history_root: logic_version/
- root_only: true
- allowed_children: records, index.md, working, backups
- last_updated: 2026-08-11
- owner: self

## 关于逻辑回档

本目录保存**设计逻辑的历史记录**，而非代码快照：

**✅ 保存（轻量）：**
- 为什么做这个决策？
- 考虑过哪些方案（A/B/C）？
- 为什么选择当前方案？
- 影响了哪些消费者？
- 如何验证和回滚？

**❌ 不保存（避免膨胀）：**
- 完整代码快照
- 逐行代码 diff
- 详细实现细节
- 原始对话记录
- 思维推理过程

**目的**：避免上下文膨胀，让 AI 能快速回忆"当初为什么这么设计"。

---

## 不可变决策记录

| version_id | version_slug | date | status | affected_scopes | linked_rule_ids | confirmed_revision | summary | path |
|---|---|---|---|---|---|---|---|---|
| VER-20260808-001 | recall-restructure | 2026-08-08 | closed | . | RULE-001, RULE-002, RULE-003, RULE-004 | 1 | Recall 系统结构重组：修复账本完整性、平行真源、反膨胀无强制点、状态机空洞 | [logic_version-20260808-001-recall-restructure.md](records/logic_version-20260808-001-recall-restructure.md) |
| VER-20260808-002 | toolchain-hardening | 2026-08-08 | effective | ., scripts/, references/, logic_version/ | RULE-005, RULE-006, RULE-007, RULE-008, RULE-009 | 1 | 工具链与自审一致性加固：批处理错行、仓库误判、shell 注入、schema 漂移导致的静默失效、夹具污染审计 | [logic_version-20260808-002-toolchain-hardening.md](records/logic_version-20260808-002-toolchain-hardening.md) |
| VER-20260811-001 | logic_version-20260811-001-git-auto-sync | 2026-08-11 | effective | ., scripts/, tests/, references/ | RULE-010, RULE-011 | none | Git 自动同步：初始化默认配置、提交后 hook、显式脏工作区提交与手动 sync | [logic_version-20260811-001-git-auto-sync.md](records/logic_version-20260811-001-git-auto-sync.md) |
| VER-20260811-002 | logic_version-20260811-002-cli-interface-repair | 2026-08-11 | effective | ., scripts/, tests/, references/ | RULE-011, RULE-012 | none | CLI 胶水层接口修复：recall new 断裂、记录命名统一（RULE-012）、CHG 冲突检测失灵、脏工作区不阻断已提交历史同步 | [logic_version-20260811-002-cli-interface-repair.md](records/logic_version-20260811-002-cli-interface-repair.md) |
| VER-20260811-003 | logic_version-20260811-003-auto-save-sync | 2026-08-11 | effective | ., scripts/, tests/ | RULE-011, RULE-013 | none | 默认自动保存上传（recall.autoCommit，--manual 切手动）与决策记录 after_commit 自动回填、hook 递归防护 | [logic_version-20260811-003-auto-save-sync.md](records/logic_version-20260811-003-auto-save-sync.md) |

**说明**：高风险变更完成后，在此创建 VER-* 记录行，并在 `records/` 目录中创建对应的 Markdown 文件。

---

## 读取策略

- 日常读取根 `logic_readme.md` 和根 `logic_change.md`，不默认读取本目录
- 只有当前文档直接引用、需要解释冲突或追溯兼容性时，才按 ID 读取相关记录
- 历史记录是"回忆设计思路"的工具，不是日常审查对象

---

## 记录创建规则

### 简单修复
- ❌ 不创建记录（局部、隔离、无公共契约影响）

### 中等变更
- ⚠️ 可选创建精简记录（规则变化或用户可见行为变更）

### 高风险变更
- ✅ 必须创建完整记录（跨模块、API、数据迁移、兼容性、架构决策）

---

**新增记录步骤**：

1. 在 `records/` 目录创建 `logic_version-YYYYMMDD-NNN-<scope>.md`
2. 在上方"不可变决策记录"表中添加索引行
3. 在 `logic_readme.md` 的"有效决策索引"中登记，并让相关 key 规则链接该记录
4. 从 `logic_change.md` 删除对应的 CHG 条目
