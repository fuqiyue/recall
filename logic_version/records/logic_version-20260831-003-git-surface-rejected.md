# VER-20260831-003: 否决 Git 同步表面收缩（CHG-20260831-002，用户选方案 A 保持现状）

## 记录控制

- version_id: VER-20260831-003
- version_slug: logic_version-20260831-003-git-surface-rejected
- status: rejected
- date: 2026-08-31
- change_id: CHG-20260831-002
- before_commit: 256e190
- after_commit: 33a8571

## 为什么做这个决策？

**背景**：
2026-08-30 架构评估建议把 `recall sync` 中通用的 pull/rebase/push 包装退回给代理或用户原生执行，脚本只保留受管理 hook、after_commit 回填与未跟踪文件排除三件 Recall 特有的事。该建议与用户已确认的 RULE-010/011（自动同步、自动保存）及 UXI-001/002（不手写 commit message、一条命令完成一个用户目标）实质矛盾，按核心原则 5 立案 CHG-20260831-002 awaiting-decision，未实施任何受影响部分。

**用户需求/反馈**：
2026-08-31 用户明确选择方案 A（保持现状），否决方案 B（收缩表面）。

**需求拆解（归档时从 CHG 原样搬入；无 CHG 的记录填 none）**：
- raw_request: 2026-08-30 架构评估——"收缩 Git 管道代码：pull-rebase-push 通用包装可退回代理/用户原生执行，脚本只保留受管理 hook、after_commit 回填、未跟踪文件排除三件特有的事"；2026-08-31 用户认可评估并授权优化
- decomposition: 若实施：① `recall sync` 移除 pull/push 包装或降级为可选；② 保留 hook 安装、回填、自动保存安全策略；③ 更新 RULE-010/011 与相关测试
- fit_analysis: 与 INT-20260816-005（一条命令保存并同步全部进度）和 UXI-001/002（不手写 Git 序列）直接冲突——这是立案待决的原因

## 决策过程

**方案 A（选中）**：保持现状。理由：sync 的价值恰在"一条命令、零 Git 知识"的用户承诺；代码已被 tests/test_git_sync.py 20 个用例覆盖且运行稳定，维护成本已付清；收缩节省的是抽象数量而非实际风险

**方案 B（否决）**：收缩表面。`recall sync` 只做自动保存提交 + 回填，pull/push 交还代理原生 git。收益：脚本与测试面变小；否决原因：违背 UXI-002、用户需重新学习 Git 序列，属用户可见行为回退，用户 2026-08-31 明确不接受此代价

**选中方案与原因**：
用户选 A。RULE-010/011 与 UXI-001/002 全部维持原状，不做任何修改；本记录的价值是让"曾考虑过收缩、为何不做"可追溯，避免未来会话把同一建议再提一遍。

## 影响范围

**修改的文件/模块**：
- `logic_change.md` - 移除 CHG-20260831-002 条目（三字段与方案分析已搬入本记录）
- `logic_readme.md` - 活跃议案入口恢复 none

**破坏性变更**：否。现行制度与代码零修改。

## 验证方式

- `python scripts/validate.py` → 无错误（rejected 记录豁免有效决策索引，登记 index.md 即可，RULE-015）
- `python scripts/audit_logic_map.py . --current-state` → Static gate: PASS（活跃议案清零）

## 回滚方式

若未来重新考虑收缩，另立新 CHG 并引用本记录，不复用已关闭的 CHG-20260831-002。

## 经验与教训

- 代理评估产生的简化建议若与用户已确认规则冲突，awaiting-decision 立案 → 用户裁决 → rejected 归档的全链路成本很低（一个条目、一份记录），但换来了"同一建议不会被反复重提"的长期收益。

## 关联

- current_logic: logic_readme.md#RULE-010, logic_readme.md#RULE-011（维持原状）
- proposal_id: CHG-20260831-002（已关闭）
- code/tests: none（未实施）
