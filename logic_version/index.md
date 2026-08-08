# Logic Version Index

## 索引控制

- history_format: 2
- history_root: logic_version/
- root_only: true
- allowed_children: records, index.md
- last_updated: 2026-08-08
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

**首次使用提示**：

当完成第一个高风险变更后：
1. 在 `records/` 目录创建 `logic_version-YYYYMMDD-NNN-<scope>.md`
2. 在上方"不可变决策记录"表中添加索引行
3. 从 `logic_change.md` 删除对应的 CHG 条目
