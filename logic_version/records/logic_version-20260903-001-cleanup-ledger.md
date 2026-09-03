# VER-20260903-001: 收尾归零——logic_temp 工作区产物台账与残留文件提示

## 记录控制

- version_id: VER-20260903-001
- version_slug: logic_version-20260903-001-cleanup-ledger
- status: effective
- date: 2026-09-03
- change_id: CHG-20260903-001
- before_commit: 4d82a5b
- after_commit: 77ad9e3

## 为什么做这个决策？

**背景**：
AI 解决问题时会产生探针脚本、临时测试、草稿和调试输出，任务"完成"后没有人负责清理。Recall 的收尾此前只覆盖自己的文档产物：CHG 关闭即删除、logic_temp 随 working 目录删除；对代码工作区的残留没有任何规则、检查清单项或工具提示。更糟的是 RULE-011 让未跟踪新文件默认不进自动保存提交——它保住了远端不被私人文件污染，却让本地垃圾既不上传、也不被 `recall status` / `recall validate` 单独提示（两者只报笼统的"未提交变更"），隐形累积。

**用户需求/反馈**：
2026-09-03 会话：用户以"做饭"比喻——备菜有废料、吃完要洗碗，多数 AI 上完菜就结束；"ai 应该是产生完工作任务，整理后才算结尾"。随后提议"多一个专门的 md 文件用于善后和收尾……change 完成后要进入 logic_readme.md，确保档案的整洁"。

**需求拆解（归档时从 CHG 原样搬入；无 CHG 的记录填 none）**：
- raw_request: 2026-09-03 用户会话——"ai 应该是产生完工作任务，整理后才算结尾……可以多一个专门的 md 文件用于管理 logic_change.md……就像 logic_temp.md 这样专门用来善后和收尾……change 完成后要进入 logic_readme.md，确保档案的整洁"
- decomposition: ① logic-temp 模板增加"工作区产物台账"表并把 medium/high 改为必建；② SKILL 新增核心原则 12"收尾归零"（含 simple 通道的汇报清单替代）；③ change-lifecycle 晋升清单与 logic-change/logic-version 模板的 temp 字段补台账清零语义；④ `recall status` 分列已跟踪变更与未跟踪待处置文件；⑤ `recall validate` 对未被 .gitignore 覆盖的未跟踪文件非阻断告警；⑥ logic_readme 新增 RULE-020、INT-20260903-001、FLOW-002 第 6 步、UXI-006、检查清单项、测试表行；⑦ 固化 VER-20260903-001
- fit_analysis: 新增 INT-20260903-001（收尾归零），插入 FLOW-002 日常修改的第 6 步（sync 之后的收尾）；扩展 INT-20260816-006（status）与 INT-20260816-008（validate）的输出，不改其目标；新增 UXI-006（工具不静默删文件），与 UXI-003 同源；不触碰 UXI-001/002；不新增 FLOW

## 决策过程

**方案 A**：按用户字面提议在项目根新建第三份 `logic_temp.md`（优点：显眼、与 readme/change 并列；缺点：审计器把 working/ 以外的 logic_temp 判违规、INV-001/RULE-019 禁止未登记根文档、入口模板 `RECALL_ROOT_ORDER` 与所有消费项目需迁移、根文件被 git 跟踪与"临时一次性"定位矛盾；复杂度：高）

**方案 B**：原位扩展 working/ 下既有的 logic_temp——加"工作区产物台账"表、medium/high 从可选改必建；SKILL 加收尾原则覆盖 simple 通道；`recall status` / `recall validate` 单列未跟踪文件（优点：不新增根文档，复用既有"关闭即删 + VER 记 logic_temp_cleanup"生命周期，工具改动是两处输出分支；缺点：载体在 gitignore 目录内，不如根文件显眼；复杂度：低）

**方案 C**：保持现状（优点：无改动；缺点：垃圾文件继续隐形累积；复杂度：无）

**落选方案归档（方案 A）**：需求原文即上方 raw_request；否决原因是与三条现行约束冲突（审计位置校验、INV-001/RULE-019、git 跟踪 vs 临时定位），且每个已接入项目都要改入口。用户 2026-09-03 在 A/B 二选一中选 B。

**选中方案与原因**：
选 B。用户真正要的是"有个专门的地方记录善后，change 关闭时它自己也归零"，这个载体已经存在，缺的是处置语义与可见性；把它做成根文档只换来显眼，代价是文档模型从两份变三份。另外把"完成"重新定义为含收尾（核心原则 12）才能覆盖不建 CHG 的 simple 通道——那才是 AI 产垃圾的主战场。

## 影响范围

**修改的文件/模块**：
- `SKILL.md` - 核心原则 11→12 条（收尾归零）；三通道表后补收尾义务；机器检查节补 status/validate 收尾核对说明；文档模型树补 working/<version_slug>/
- `references/logic-temp-template.md` - 定位改为"工作笔记 + 收尾台账"，medium/high 必建；新增"工作区产物台账"表（path/artifact_kind/disposition/reason/cleaned_at）与 `ledger_cleared` 字段；维护规则补"不自动删除"
- `references/change-lifecycle.md` - 晋升检查清单与第 9 步改为"台账清零→删 working→VER 记结果"
- `references/logic-change-template.md` - `temp_path` / `temp_cleanup` 字段说明补 RULE-020 语义（字段名不变）
- `references/logic-version-template.md` - `logic_temp_cleanup` 说明补台账处置件数（字段名不变）
- `scripts/recall.py` - 新增 `classify_porcelain`，`recall status` 分列已跟踪变更与未跟踪待处置文件（列前 10 个）
- `scripts/validate.py` - 新增 `report_untracked_leftovers`，第 4 步分列已跟踪脏文件与 `git ls-files --others --exclude-standard` 的未跟踪残留
- `tests/test_recall_cli.py`、`tests/test_validate.py` - 新增分类与告警用例
- `logic_readme.md` - RULE-020、INT-20260903-001、FLOW-002#6、UXI-006、代码地图职责、测试表、检查清单、当前限制、决策索引

**破坏性变更**：否。模板字段名不变（RULE-009 校验不受影响）；既有 VER 的 `logic_temp_cleanup: none` 仍合法；status/validate 只在有未跟踪文件时多出输出；RULE-011 的默认排除行为不变。

## 验证方式

- `python -m unittest tests.test_recall_cli tests.test_git_sync tests.test_validate` → 全部 OK（含新增用例）
- `python tests/test_audit_logic_map.py` → 全部 OK
- `python scripts/audit_logic_map.py . --current-state` → Static gate: PASS（含 working/ 下带台账的 logic_temp 在场时）
- `python scripts/validate.py` → 无错误；有未跟踪文件时出现 RULE-020 告警，清理后消失
- `recall status` 在有未跟踪文件时单列"待处置候选"

## 回滚方式

git revert 本次提交。纯文档 + 两处脚本输出分支，无数据、无运行时依赖；回滚后 logic_temp 回到可选工作笔记语义。

## 经验与教训

- "完成"的定义决定收尾是否发生：把清理写进原则比再加一个工具命令更根本，工具只负责可见性。
- 隐私安全规则（RULE-011 默认排除新文件）会产生"看不见的垃圾"副作用；解法是提示而不是放松排除。
- 用户提议的载体形式（根文件）与真实诉求（专门记录善后、关闭即归零）可以分开：先找已有载体，再决定要不要换位置。

## 兼容、迁移与回滚

- compatibility: 向后兼容；无消费项目依赖 status/validate 精确输出
- migration: none
- rollback: git revert
- logic_temp_cleanup: logic_version/working/logic_version-20260903-001-cleanup-ledger/ 于 2026-09-03 删除；台账 4 项（keep 2、delete 1、gitignore 1）全部处置

## 关联

- current_logic: logic_readme.md#RULE-020；RULE-011（未跟踪默认排除，保持不变）；UXI-003/UXI-006
- proposal_id: CHG-20260903-001（本记录创建后关闭）
- code/tests: SKILL.md; references/logic-temp-template.md; references/change-lifecycle.md; scripts/recall.py; scripts/validate.py; tests/test_recall_cli.py; tests/test_validate.py
