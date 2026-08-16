# VER-20260816-002: 追溯链断裂修复与一致性检测补齐

## 记录控制

- version_id: VER-20260816-002
- version_slug: logic_version-20260816-002-traceability-repair
- status: effective
- date: 2026-08-16
- change_id: CHG-20260816-001
- before_commit: b100ce7
- after_commit: _待填写_
- recall_route: high
- history_retention: full
- decision_confirmed_by: user
- decision_ref: user-confirmed:2026-08-16（"认可你的问题，请帮我逐个修改"）
- changed_by: Claude (Fable 5)
- intent_traceability: INT-20260816-005 -> RULE-013 -> test:tests/test_git_sync.py -> VER-20260816-002; INT-20260816-008 -> RULE-015 -> test:scripts/validate.py -> VER-20260816-002

## 为什么做这个决策？

**背景**：
系统排查发现三处 P0 级断裂：(1) `recall new` 用的快速模板 commit 字段是
`- commit: <git-commit-hash>`，而 hook 回填只精确匹配 `- after_commit: _待填写_`，
官方推荐路径创建的记录**永远无法被回填**——RULE-013 对默认流程完全失效；
(2) 自动保存提交无 Ref 行（回填只读 Ref），且 `git add -A` 会把用户私人文件
（如未跟踪的个人笔记）无提示打包并推上公开远端；(3) 功能意图登记表用短编号
INT-001..008，而审计正则与追溯链只认 INT-YYYYMMDD-NNN，两套格式互不相认，
VER-20260816-001 链引用的 INT 在登记表中不存在。另有 P1：文档-代码漂移、
三处登记缺失、意图层悬空引用均无任何检测；validate 把每次 RULE 引用算重复，
警告全是噪音。

**用户需求/反馈**：
用户确认完整问题清单后要求"认可你的问题，请帮我逐个修改"（2026-08-16）。

## 决策过程

**方案 A**：只改 hook，让它兼容 `- commit: _待填写_` 占位符——最小改动，但
自动保存无 Ref 的断裂、私人文件风险、编号双制式都没解决（复杂度：低）。

**方案 B**：废弃快速模板，强制全部记录用完整 schema——统一但违反原则 7，
个人项目被 50+ 字段拖累，且手写完整 schema 正是占位符漂移的来源（复杂度：中）。

**方案 C（选中）**：分层修复。模板侧：快速模板补 before_commit（recall new
自动填 HEAD）/after_commit（标准占位符）；hook 侧：回填双通道（Ref 行 +
本次提交内规范命名的记录）、兼容新旧占位符、识别不了打警告；自动保存侧：
提交前列出文件清单、未跟踪文件单独提示；编号侧：统一 INT-YYYYMMDD-NNN
并补登记 INT-20260816-001 使既有追溯链落地；检测侧：validate 补三处登记
对账、撞号、意图层引用、CHG 三字段、字段行占位符检查，RULE 重复只按定义
行判定；hook 加"代码变更未带 logic 文档"的非阻断漂移提醒（复杂度：中-高）。

**选中方案与原因**：C。逐个消灭"静默失效"——本系统反复出现的失败模式
（RULE-009 schema 漂移、RULE-012 命名漂移、本次占位符漂移同源）：工具识别
不了的东西必须发声，而不是默默跳过。

## 影响范围

**修改的文件/模块**：
- `references/logic-version-git-template.md` - 快速模板 commit 字段改为 before_commit/after_commit
- `scripts/create_ver.py` - 创建时自动填 before_commit（HEAD 短哈希）
- `scripts/git_sync.py` - 回填双通道、新旧占位符、无占位符警告、自动保存文件清单、漂移哨兵
- `scripts/validate.py` - 三处登记对账、撞号、意图层校验、CHG 三字段、占位符字段行检查、RULE 重复按定义行、CHG status 字段识别、after_commit 计入 commit 关联
- `scripts/detect_conflicts.py` - 报告声明启发式局限
- `logic_readme.md` - INT 编号统一并补 INT-20260816-001；RULE-011/013/014 更新；新增 RULE-015；当前限制补瘦身与整理约定
- `references/logic-readme-template.md`、`references/field-vocabulary.md` - INT 完整格式要求
- `SKILL.md`、`CLAUDE.md` - sync 语义更新；CLAUDE.md 收敛为指向权威，消除平行真源
- `.gitignore` - 排除用户私人笔记
- `tests/test_git_sync.py` - 新增 5 个用例（含 recall new → Ref 提交 → 回填端到端）
- `logic_version/records/logic_version-20260808-001-recall-restructure.md` - 补 after_commit: 578cd5e（历史断链回填，属 RULE-013 既定例外）

**破坏性变更**：无。旧占位符与旧字段保持可识别，历史记录不迁移。

## 验证方式

`python -m unittest tests.test_git_sync`（17 tests OK，含端到端回填）；
`python -m unittest tests.test_recall_cli`（8 tests OK）；
`python tests/test_audit_logic_map.py`（62 tests OK）；
`python scripts/audit_logic_map.py . --current-state` 静态门 PASS；
`python scripts/validate.py` 无错误、旧噪音警告消失、新检查项就位；
本记录自身即为实证：由修复后的 `recall new` 生成，after_commit 由 hook 回填。

## 回滚方式

`git revert` 本次提交整体回退。只想关闭漂移提醒：hook 场景不传
`--post-commit` 即不触发（提醒仅在 hook 路径生效，非阻断）。

## 经验与教训

静默失效是这套工具链的系统性失败模式：占位符精确匹配、glob 模式、字段名、
编号格式——任何"识别不了就跳过"的分支都必须改为"识别不了就发声"。承诺自动化
的链路（RULE-013）必须有端到端测试从官方入口走到出口，单元测试各环节分别
通过不能证明链路通。

## 关联

- current_logic: logic_readme.md#RULE-011, RULE-013, RULE-014, RULE-015
- proposal_id: CHG-20260816-001（已归档移除）
- code/tests: scripts/git_sync.py; scripts/create_ver.py; scripts/validate.py; tests/test_git_sync.py
