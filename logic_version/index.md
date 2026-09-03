# Logic Version Index

## 索引控制

- history_format: 2
- history_root: logic_version/
- root_only: true
- allowed_children: records, index.md, working, backups
- last_updated: 2026-09-03
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
| VER-20260816-001 | logic_version-20260816-001-feature-intent-layer | 2026-08-16 | effective | ., references/ | RULE-014 | none | 功能级"功能意图与用户流程"层（INT/FLOW/UXI 模块化条目）、CHG 需求拆解与融入分析字段、plan 模式批准后按通道落盘 | [logic_version-20260816-001-feature-intent-layer.md](records/logic_version-20260816-001-feature-intent-layer.md) |
| VER-20260816-002 | logic_version-20260816-002-traceability-repair | 2026-08-16 | effective | ., references/, scripts/, tests/ | RULE-011, RULE-013, RULE-014, RULE-015 | none | 追溯链断裂修复：recall new 回填链路、自动保存文件清单与回填双通道、INT 编号统一、validate 三处对账与漂移哨兵 | [logic_version-20260816-002-traceability-repair.md](records/logic_version-20260816-002-traceability-repair.md) |
| VER-20260816-003 | logic_version-20260816-003-semantic-link | 2026-08-16 | effective | ., references/, scripts/, tests/ | RULE-014, RULE-015, RULE-016 | none | 需求↔架构语义链路补全：模块化项目接入流程、需求三字段归档搬入 VER、INT 代码锚点与 query intent 反向查询 | [logic_version-20260816-003-semantic-link.md](records/logic_version-20260816-003-semantic-link.md) |
| VER-20260816-004 | logic_version-20260816-004-handoff-hierarchy | 2026-08-16 | effective | ., references/, scripts/, tests/ | RULE-014, RULE-017, RULE-018 | none | 会话默认延续原则、层级化子 logic 文档（readme-only 登记拆分）与舍弃方案归档 | [logic_version-20260816-004-handoff-hierarchy.md](records/logic_version-20260816-004-handoff-hierarchy.md) |
| VER-20260816-005 | logic_version-20260816-005-audit-remediation | 2026-08-16 | effective | ., references/, scripts/, tests/, logic_version/ | RULE-011, RULE-015, RULE-018, RULE-019 | none | 审查整改：自动保存排除未跟踪新文件、rejected 记录豁免有效索引、子文档纳入检查、漂移度量、脱管文档归档与根目录覆盖对账、双模板合并、引用纪律 | [logic_version-20260816-005-audit-remediation.md](records/logic_version-20260816-005-audit-remediation.md) |
| VER-20260831-001 | logic_version-20260831-001-entry-slim-skill-front | 2026-08-31 | effective | SKILL.md, references/ | RULE-018, RULE-019 | none | 入口模板短路由化（保留 RECALL_* 标记与五条最小协议）、SKILL 首屏重排（路由一问 + 三通道前置）、跨仓库 RULE 指针改指本技能目录、personal 模式 ADR 可选显式化 | [logic_version-20260831-001-entry-slim-skill-front.md](records/logic_version-20260831-001-entry-slim-skill-front.md) |
| VER-20260831-002 | logic_version-20260831-002-arch-simplify | 2026-08-31 | effective | CLAUDE.md, SKILL.md, references/, scripts/, logic_change.md | RULE-008, RULE-014, RULE-019 | none | 自身 CLAUDE.md 裁剪为短路由、意图层维护深度按治理模式分档（personal 轻量档）、create_ver 编码防护对齐；Git 表面收缩与已确认规则冲突，立案 CHG-20260831-002 待决 | [logic_version-20260831-002-arch-simplify.md](records/logic_version-20260831-002-arch-simplify.md) |
| VER-20260831-003 | logic_version-20260831-003-git-surface-rejected | 2026-08-31 | rejected | scripts/ | RULE-010, RULE-011 | CHG-20260831-002 | 否决 Git 同步表面收缩：用户选方案 A 保持现状，RULE-010/011 与 UXI-001/002 维持原状；三字段与方案分析随本记录归档 | [logic_version-20260831-003-git-surface-rejected.md](records/logic_version-20260831-003-git-surface-rejected.md) |
| VER-20260903-001 | logic_version-20260903-001-cleanup-ledger | 2026-09-03 | effective | ., references/, scripts/, tests/ | RULE-020 | 1 | 收尾归零：logic_temp 增工作区产物台账（medium/high 必建、清零才关 CHG）、SKILL 核心原则 12、status/validate 单列未跟踪残留；否决"根目录第三份 logic_temp"方案 | [logic_version-20260903-001-cleanup-ledger.md](records/logic_version-20260903-001-cleanup-ledger.md) |

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
2. 在上方"不可变决策记录"表中添加索引行（`rejected`/`cancelled`/`rolled-back` 记录只登记到这里，不进有效决策索引）
3. 在 `logic_readme.md` 的"有效决策索引"中登记生效记录，并让相关 key 规则链接该记录
4. 把 CHG 的需求拆解三字段搬入记录后再删除 CHG 条目（语义见 RULE-014，步骤见 references/change-lifecycle.md §7）
