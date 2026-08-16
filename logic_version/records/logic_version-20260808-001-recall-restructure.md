# VER-20260808-001: Recall 系统结构重组

## 版本控制

- version_id: VER-20260808-001
- version_slug: recall-restructure
- change_id: CHG-20260808-001
- date: 2026-08-08
- status: closed
- affected_scopes: .
- linked_rule_ids: RULE-001, RULE-002, RULE-003, RULE-004
- confirmed_revision: 1
- immutable: true
- after_commit: 578cd5e

## 为什么做这个决策？

Recall 系统自身违反了它声明的核心原则：

1. **账本完整性已经破了**：`logic_change.md` 声明 `active_changes: none`，但根目录存在未登记的 `OPTIMIZATION_ANALYSIS.md` 活跃议案
2. **平行真源违反 SKILL.md:180**：`README.md` 重述三条通道和核心原则；`PROJECT_STATUS.md` 是第三份状态副本且已过期；`VER_TEMPLATE.md` 与 `references/logic-version-template.md` 冲突
3. **反膨胀原则没有强制点**：审计脚本（6497 行）严格检查形式字段，但完全不检查长度；完整字段表迫使单条 CHG 达到 80-200 行
4. **`promoting` 状态缺失**：规则禁止 `deployed-active` 作为活跃 CHG 状态，但晋升需要 4+ 次文件编辑，中断会留下非法账本
5. **通道分类不可判定**："中等 = 多个相关文件"和"高风险 = 跨模块"边界重合；分类必须在分析前做，但不确定度在分析前最大
6. **SKILL.md 自身是最大单次上下文成本**：382 行密集规范，每次调用全量加载
7. **个人模式语义审查是纯仪式**：要求独立记录 `semantic_reviewed_by` 但允许同一人做所有事
8. **六套词汇覆盖同一件事**：`review` / `verify` / 当前状态审查 / `--current-state` / `--formal-review` / Recall Brief

问题的根源：把一套面向多人合规审计的字段体系贴上了"个人小项目"标签。字段表迫使文档膨胀 → 反膨胀原则无强制点 → 通道分类默认滑向最重流程。

## 考虑过哪些方案？

### 方案 A：全面重构（选择此方案）

- 建立字段词汇分层：personal(8 字段) / collaborative(+9) / compliance(+13)
- 压缩 SKILL.md 从 382 行到约 120 行，移出详细规则到 `references/`
- 增加 `promoting` 状态到状态机，带晋升检查清单
- 重写通道分类为可观察标记（`contract_class: public|persisted|security`）
- 审计脚本增加密度检查和 `promoting` 状态支持
- 合并六套审查词汇为两个：`inspect`（日常）和 `formal-review`（明确要求）
- 归档根目录冗余文件到 `logic_version/backups/20260808/`
- 补齐代码地图：`scripts/` 和 `tests/` 加入 `owned_paths`

### 方案 B：增量优化

- 只修复最严重的 3 项（账本、平行真源、`promoting` 状态）
- 保持现有字段表和 SKILL.md 结构
- **缺点**：不解决根源问题，字段膨胀会继续

### 方案 C：创建自动化工具

- 写脚本自动压缩 `logic_change.md`、自动归档、自动晋升
- **缺点**：用工具掩盖设计问题；工具本身成为新的维护负担

## 为什么选择方案 A？

1. 修复根源而不是症状：字段分层直接解决"个人模式膨胀"问题
2. 理念本身是对的（逻辑回档 ≠ 代码回档、单一真源、按风险分流），执行形态需要对齐
3. `promoting` 状态是必然踩到的空洞，必须修
4. SKILL.md 压缩立即降低每次调用的上下文成本
5. 密度检查让"避免膨胀"有了真实的强制点
6. 可观察通道分类消除"分析前必须判定"的死锁

## 影响范围

### 修改的文件

- `SKILL.md`：382 行 → 142 行
- `logic_change.md`：增加 `promoting` 到允许状态列表；增加 CHG-20260808-001
- `logic_readme.md`：
  - `owned_paths` 增加 `scripts/` 和 `tests/`
  - 代码地图表增加 `contract_class` 列
  - 代码地图增加 `scripts/audit_logic_map.py` 和 `tests/` 行
  - `unmapped_paths` 更新为实际路径
  - RULE-001..004 决策记录链接到 VER-20260808-001
  - `last_verified` 更新为 2026-08-08
- `scripts/audit_logic_map.py`：
  - `CHANGE_STATUSES` 增加 `"promoting"`
  - `implementation_statuses` 增加 `"promoting"`
  - 三处状态检查增加 `"promoting"`
  - 新增 `audit_density()` 函数
  - `collect_audit()` 调用 `audit_density()` 并加入报告
- `README.md`：压缩为路由，只链接到主要文档

### 新建的文件

- `references/field-vocabulary.md`：字段词汇分层（personal/collaborative/compliance）
- `references/change-lifecycle.md`：变更与决策生命周期（9 步）
- `references/logic-vs-code-recall.md`：逻辑回档 vs 代码回档（示例对比）
- `references/governance-modes.md`：治理模式（personal/collaborative/compliance）
- `AGENTS.md`：Codex 代理入口
- `CLAUDE.md`：Claude 代理入口
- `logic_version/backups/20260808/MANIFEST.md`：备份清单
- `logic_version/records/logic_version-20260808-001-recall-restructure.md`：本记录

### 归档的文件

移入 `logic_version/backups/20260808/`：

- `OPTIMIZATION_ANALYSIS.md`（未登记议案）
- `PROJECT_STATUS.md`（过期状态副本）
- `VER_TEMPLATE.md`（孤儿模板）

### 消费者影响

- **Recall skill 的消费者项目**：
  - `SKILL.md` 大幅压缩，加载更快
  - 个人模式只需填 8 个字段，不再被迫填完整 30 个字段
  - `promoting` 状态合法化，中断恢复有明确路径
  - 通道分类可以在分析后下调
  - 审计脚本现在会报告密度告警
- **无破坏性变更**：所有旧字段仍然有效，只是分层为可选

## 验证方式

1. **账本完整性**：`logic_change.md` 的 `active_changes` 字段与实际 CHG 条目一致
2. **单一真源**：根目录不存在 `*-v2.md`、`*-final.md` 或其他平行规则副本
3. **密度强制**：`python scripts/audit_logic_map.py . --current-state` 对超限文件报告 `density` 告警
4. **状态机完整**：`promoting` 状态在 SKILL.md、logic_change.md、audit_logic_map.py 中一致定义
5. **代码地图准确**：`scripts/` 和 `tests/` 在 `owned_paths` 和代码地图表中
6. **决策记录可追溯**：RULE-001..004 链接到有效的 VER-20260808-001

## 回滚方式

1. 从 `logic_version/backups/20260808/` 复制三个文件回根目录
2. 用 Git 回退 `SKILL.md`、`logic_readme.md`、`logic_change.md`、`scripts/audit_logic_map.py`
3. 删除 `references/field-vocabulary.md`、`references/change-lifecycle.md`、`references/logic-vs-code-recall.md`、`references/governance-modes.md`
4. 删除 `AGENTS.md` 和 `CLAUDE.md`
5. 从 `logic_change.md` 和 `logic_version/index.md` 移除 CHG-20260808-001 和 VER-20260808-001

**注意**：本仓库 `.git` 目录为空，无 Git 历史。回滚需要手动操作或从外部备份恢复。

## 实施记录

- 实施者：Claude Opus 5 (AI)
- 实施日期：2026-08-08
- 确认者：user
- 确认日期：2026-08-08
- 语义审查：self（个人模式）
- 审查日期：2026-08-08
- 审查证据：所有修改的文件经过工具调用验证，`SKILL.md` 行数从 382 降至 142，审计脚本成功增加密度检查函数

## 关联

- change_id: CHG-20260808-001
- 基线：2026-08-07 版本的 SKILL.md、logic_readme.md、logic_change.md
- 意图来源：OPTIMIZATION_ANALYSIS.md 未登记议案（已归档）
- 规则更新：RULE-001, RULE-002, RULE-003, RULE-004 决策记录字段更新
