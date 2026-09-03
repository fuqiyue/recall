# VER-20260903-003: 结构性收口——Git 调用单源与机器门、审计器函数拆分、CHG 字段按治理模式分档、根文档压缩

## 记录控制

- version_id: VER-20260903-003
- version_slug: logic_version-20260903-003-structural-closure
- status: effective
- date: 2026-09-03
- change_id: CHG-20260903-003
- before_commit: 4fb6beb
- after_commit:

## 为什么做这个决策？

**背景**：
VER-20260903-002 建立了 `recall_common` 公共基础设施并把审计器拆成分层包，但留下五个尾巴：① 仍有 7 处绕过 `run_git` 直接调 subprocess（validate.py ×4、init_recall.py、link_ver_git.py、recall_audit/archive.py），而当天就出了两套实现漂移的实例——`run_git` 整体 `strip()` 吃掉 `git status --porcelain` 首行前导空格，提交清单与 `recall status` 的路径各错一位；② porcelain 解析在 git_sync 与 recall.py 各一份，重命名与引号处理不一致；③ 审计器分包只搬迁没瘦身，integrity.py 最大函数 648 行、archive.py 290 行；④ 审计器对活跃 CHG 无差别要求 9 个协调字段与完整决策/审查字段，与 references/field-vocabulary.md "personal 8 个字段"矛盾，personal CHG 普遍 100+ 行（本仓库 CHG-20260903-001 为 110 行），"当前限制"挂着待立案；⑤ 根文档 331 行越过 250 目标值。同日对消费项目 eduai 的实测还暴露：审计 `--json` 在 Windows 重定向下写成 GBK（RULE-008 违规）。

**用户需求/反馈**：
2026-09-03 会话："你目前提到的还可以优化的地方请帮我做优化。我目前认可你提到的问题。"

**需求拆解（归档时从 CHG 原样搬入；无 CHG 的记录填 none）**：
- raw_request: 2026-09-03 用户会话——"你目前提到的还可以优化的地方请帮我做优化。我目前认可你提到的问题"（指上一轮汇报的五项：RULE-021 收口、porcelain 两份、审计器只搬迁没瘦身、根文档 331 行、CHG 行数与审计器要求冲突）
- decomposition: ① 7 处 subprocess 直调 git 改为 recall_common，新增测试级静态门"scripts/ 下禁止直接 subprocess 调 git"；② `parse_porcelain`/`classify_porcelain` 下沉 recall_common，两处改调用；③ integrity/archive 大函数按检查拆分，JSON 输出与三个基线逐字节一致；④ changes.py 按治理模式分档：personal 块缺协调/合规字段不报、写了照常校验，实施前仍须决策确认；密度检查 CHG 目标 40 行 notice；⑤ 根文档压缩：测试表合并同命令行、控制流图与模板节精简；⑥ 新增 RULE-023、更新 RULE-021/022 证据、固化 VER-20260903-003
- fit_analysis: 不新增用户可见功能；INT-20260816-008（validate/audit）扩展为"审计门按治理模式分档"，INT-20260816-006（status）输出不变只改内部调用；分档落在 RULE-014 已有"按治理模式分档"精神之下，故新立 RULE-023 而不改 RULE-014 正文；不新增 FLOW/UXI

## 决策过程

**方案 A**：五项全做，分档走"缺则不查、写则照查"（优点：一次收口，personal 项目 CHG 可缩到 15-40 行；缺点：审计 JSON 对 personal 项目变化，但只减少 issue；复杂度：中）

**方案 B**：只做代码三项（Git 单源、porcelain 单源、函数拆分），分档与压缩另立案（优点：改动小；缺点："当前限制"继续挂着、根文档继续越线；复杂度：低）

**落选方案归档**：B 的需求原文即上方 raw_request；否决原因是用户已明确认可全部五项问题，拖延分档只会让 personal 项目继续为 compliance 字段付行数成本。

**选中方案与原因**：
选 A。分档的关键取舍是"缺则不查、写则照查"而不是"personal 一律不查"：写了的上层字段仍按完整规则校验，避免出现"填了 conflicts_with 却不用给裁定"的漏洞；块自身 governance_mode 优先于账本模式，两者都缺按 full 处理，不替未声明模式的项目降门槛；`changed_by` 与实施前的 `decision_confirmed_by` + `decision_confirmed_at` 在所有档位必填——用户确认是核心原则 1/5，不随治理模式降级。函数拆分坚持"公开函数签名、返回 dict 键、issue 字符串全部不变"，用五份 JSON 基线（本仓库 current-state/formal-review、eduai current-state/formal-review、legacy 夹具）逐字节对比做回归门。Git 单源用测试级静态扫描做机器门而不是再写一条文字规则：今天的 strip 差异已经证明文字规则拦不住第二份实现。根文档按 RULE-014 顺序先压缩（合并同命令测试行、精简控制流图与模板节），拆子文档留给用户裁决。

## 影响范围

**修改的文件/模块**：
- `scripts/recall_common.py` - `run_git` 改为只去尾部空白；新增 `parse_porcelain`（重命名取新路径、去引号）与 `classify_porcelain`
- `scripts/recall.py`、`scripts/git_sync.py` - 删除各自 porcelain 解析，改为导入（recall.py 保留 `classify_porcelain` 名字供测试）
- `scripts/validate.py`、`scripts/init_recall.py`、`scripts/link_ver_git.py`、`scripts/recall_audit/archive.py` - 7 处 subprocess 直调改为 `run_git`/`git_output`；删除 `import subprocess`
- `scripts/recall_audit/cli.py` - `main()` 先 `force_utf8_output()`（RULE-008：`--json` 重定向落盘 UTF-8）
- `scripts/recall_audit/constants.py` - 新增 `PERSONAL_OPTIONAL_CHANGE_FIELDS`
- `scripts/recall_audit/changes.py` - 新增 `change_field_tier`；`change_coordination_issues(blocks, *, ledger_mode)`、`change_lifecycle_issues(..., tier)`、`change_block_semantic_issues` 按档位跳过缺失的可选字段；personal 无 decision_gate 时实施状态须有确认来源
- `scripts/recall_audit/integrity.py`、`scripts/recall_audit/archive.py` - 超过 150 行的函数按检查拆为 `_check_*` 小函数并共用上下文对象（详见验证节）；integrity 调用 `change_coordination_issues` 时传入账本模式；archive `audit_density` 对 40-80 行的 CHG 给 `over-chg-target` notice
- `scripts/audit_logic_map.py` - facade 重新导出 `change_field_tier`、`PERSONAL_OPTIONAL_CHANGE_FIELDS`
- `tests/test_recall_common.py` - 新增 porcelain 前导空格/重命名/引号用例与 `SingleGitInfrastructureGateTests`（RULE-021 机器门）；`tests/test_audit_logic_map.py` - 新增 `GovernanceTierTests` 5 例
- `references/field-vocabulary.md`（审计器口径段）、`references/logic-change-template.md`（personal 最小块说明）
- `logic_readme.md` - 331 → 287 行：新增 RULE-023；RULE-008/021/022 证据更新；代码地图合并测试行与入口行；测试表 20 → 10 行；控制流图、责任记录、兼容制度、安全运维、消费者、检查清单精简；当前限制去掉"审计器要求完整字段集"、新增 Density 不进门与 validate 对消费项目的两个工具缺口
- `logic_version/index.md` - 新增本记录行

**破坏性变更**：否（对外）。命令行、退出码、`--json` 结构、模板字段名、记录文件名均不变；collaborative 项目与 `--formal-review` 输出逐字节不变；personal 项目的 `proposal_issues` 只会减少。

## 验证方式

- `python tests/test_audit_logic_map.py` → 74 OK（基线 69 + GovernanceTierTests 5）
- `python -m unittest discover -s tests` → 136 OK（审计 74 + 其余套件 62；新增 porcelain 用例、RULE-021 静态门、前导空格回归、GovernanceTierTests 5 例）
- 审计 JSON 基线对比：`--json --current-state` / `--formal-review` 于本仓库、eduai（只读）与 `references/examples/audit-repro-legacy` 五份输出，在"HEAD 版 integrity/archive vs 拆分后"同一时刻 A/B 下逐字节一致；分档生效后仅本仓库 personal CHG 的 `proposal_issues` 变化（eduai 的 CHG 字段齐全，前后均为 0）
- 函数长度（AST 统计）：integrity.py `audit_module_routes` 302→49、`audit_proposal_integrity` 408→53、`audit_current_state_integrity` 648→48；archive.py `audit_temp_working` 260→36、`audit_index_consistency` 135→60、`audit_archive` 290→83；两文件最大函数 65 行。changes/semantic/formal/report 的 9 个存量超限函数未在本次范围，记入"当前限制"
- `python scripts/audit_logic_map.py . --current-state` → Static gate PASS（slim personal CHG-20260903-003 在场时零 proposal_issues）；`--json --current-state > out.json` 在 Windows 重定向下为 UTF-8
- `python scripts/validate.py` → 无错误
- 代码差异：`git show <after_commit>`

## 回滚方式

`git revert <after_commit>`。纯代码 + 文档；无数据、无运行时依赖。回滚后 personal 项目的 CHG 重新被要求完整字段集，7 处 subprocess 直调与两份 porcelain 解析随之恢复。

## 经验与教训

- 公共封装建立当天就出现第二种行为差异（strip vs rstrip），说明"只此一份"必须有机器门；一个 20 行的静态扫描测试比一条规则行更能守住。
- 分档的正确形状是"缺则不查、写则照查"：既不让 personal 项目为 compliance 字段付行数成本，也不让写了字段的人绕过校验；默认档位在信息缺失时应保守（full），不替未声明模式的项目做决定。
- 拆大函数时先冻结 JSON 基线（含一个真实消费项目和一个 legacy 夹具），拆完逐字节对比，比读 diff 更可靠；行为变更（分档）与结构变更（拆函数）分开验证，否则基线对比失去意义。
- 行数目标对规则表这类"一行一条"的结构是刚性的：本文档 22 条规则 + 12 条 INT + 15 条 VER 索引已占 49 行，压缩其余部分只能逼近而不能越过 250；下一步只能是 RULE-018 拆分，且这是用户的裁决。
- 消费项目实测（eduai）比自审更能暴露工具缺口：CHG-ID 正则、VER 模板版本、after_commit 格式三处"只认自家写法"的假错误，在本仓库永远测不出来。

## 兼容、迁移与回滚

- compatibility: 向后兼容；审计 JSON 对 collaborative/formal 不变，对 personal 只减少 issue
- migration: none
- rollback: git revert
- logic_temp_cleanup: logic_version/working/logic_version-20260903-003-structural-closure/ 于 2026-09-03 删除；台账 3 项（keep 1：本记录；delete 2：working 目录、scratchpad 基线/对比 JSON）全部处置

## 关联

- current_logic: logic_readme.md#RULE-021（porcelain 单源 + 机器门）；RULE-022（函数 ≤150 行、CHG 40 行目标）；RULE-023（新增）；RULE-008（`--json` UTF-8 证据）
- proposal_id: CHG-20260903-003（本记录创建后关闭）
- intent_traceability: INT-20260816-008 -> RULE-023 -> test:tests/test_audit_logic_map.py#GovernanceTierTests -> VER-20260903-003; INT-20260816-006 -> RULE-021 -> test:tests/test_recall_common.py#SingleGitInfrastructureGateTests -> VER-20260903-003; INT-20260816-003 -> RULE-022 -> test:tests/test_audit_logic_map.py -> VER-20260903-003
- code/tests: scripts/recall_common.py; scripts/recall.py; scripts/git_sync.py; scripts/validate.py; scripts/init_recall.py; scripts/link_ver_git.py; scripts/recall_audit/; scripts/audit_logic_map.py; tests/test_recall_common.py; tests/test_audit_logic_map.py; references/field-vocabulary.md; references/logic-change-template.md
