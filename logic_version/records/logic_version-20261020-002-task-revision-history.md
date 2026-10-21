# VER-20261020-002: 同任务多轮修订与归档保全

## 记录控制
- version_id: VER-20261020-002
- version_slug: logic_version-20261020-002-task-revision-history
- status: effective
- immutable: true
- date: 2026-10-20
- change_id: CHG-20261020-002
- proposal_revision: 1
- changed_by: Codex
- recall_route: medium
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: 本机文档检查与模板CLI回归
- governance_verification: recorded
- governance_verified_at: 2026-10-20
- before_commit: f2b1e09d7082eaebd11a57415ee7aa7ceeec0ca3
- after_commit: none
- decision_confirmed_by: user
- decision_confirmed_at: 2026-10-20
- decision_ref: user:2026-10-20 本轮认可方案并要求直接优化
- proposal_commit_or_blob: user:2026-10-20 本轮请求；需求与修订表在本记录保全

## 为什么做这个决策？
任务目录已有唯一正文和方案版本，但没有统一多轮记录与关案搬运要求，任务结束后容易只剩最终方案。
- raw_request: 认可“变更总入口、每项任务一个文件夹、同一文件记录多轮修订”的方案，直接优化Recall，补齐同一任务的多轮修订记录和完成后的归档规则，保持简洁，避免重复过程文档。
- decomposition: 在现有任务模板内增加修订表，区分执行轮次与方案版本；补齐VER模板和关案搬运核对；同步入口与规则，验证模板兼容和实际归档。
- fit_analysis: 复用INT-20261020-001与INT-20260816-006，完善FLOW-002#2/4/6；沿用logic_changes任务发现和logic_version记录，不新增目录类型、CLI或独立过程正文。

## 决策过程
选用任务内一张简短修订表，关案搬入同一VER；执行轮次独立于方案版本。逐轮快照和独立history/交接正文会重复且难以保持一致；只覆盖当前方案则丢失修改原因，均未采用。

## 修订记录
| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-20 | 1 | 用户认可集中修订与归档方案；核对现有模板和生命周期，复用已有结构 | SKILL.md、references/、logic_readme.md | 已核目录/模板入口及兼容边界 |
| 02 | 2026-10-20 | 1 | 补齐任务内修订表、轮次与版本区分、归档搬运及旧案缺失说明；修正完成后反馈的任务位置 | SKILL.md、logic_readme.md、references/logic-change-template.md、references/logic-version-template.md、references/workspace-tasks.md、references/change-lifecycle.md、references/document-model.md、references/field-vocabulary.md | 现有CLI与workspace两组共83项：82通过，1项符号链接权限跳过；技能格式与静态门通过 |
| 03 | 2026-10-20 | 1 | 自审对齐旧none保留级别、simple例外和教学示例，避免已有CHG关案时遗漏记录 | references/change-lifecycle.md、references/logic-change-template.md、references/logic-version-template.md、references/practical-examples.md | 归档边界一致；workspace关案核对无残留；validate无错误，草稿提前出现在有效索引的提示在定稿后复核 |

## 影响范围
更新SKILL、根RULE-025/027、CHG/VER模板及既有工作路径、生命周期、文档模型、字段参考；不增加CLI、目录类型或机器必填字段。存量任务从本次接手记起，不补造历史；无CHG的simple修改不增加流程。已归档历史保持不变。

## 验证方式
现有test_recall_cli.py与test_workspace.py共83项：82通过、1项因本机符号链接权限跳过，覆盖个人任务模板与VER创建/生命周期CLI。技能quick_validate、audit静态门、workspace关案核对与git diff --check通过；validate无错误，既有未提交改动和历史commit缺失告警保留。草稿阶段有效索引提示在定稿后复核。

本轮按字段逐项比较三项需求与三轮修订表，最终proposal_revision为1；完整搬运，无逐轮文件或独立过程正文。自审passed：当前方案与历史职责、版本区分、旧案缺失说明及归档边界一致。现有CLI未增加修订语义校验，内容完整性仍由执行代理核对；未运行远端CI，也未迁移教材项目。

## 回滚方式
仅撤销本轮技能与治理文档增量，保留工作区已有修改。已经归档的记录不改写，后续调整另建记录。

## 临时产物
- logic_temp_cleanup: 2026-10-20；本轮未创建临时代码、探针文件或独立过程文档；测试临时副本自动退出，执行设置禁写pyc。workspace --closing CHG-20261020-002返回findings为空。保留技能/治理文档与本决策，归档核对后移除本次活跃任务正文及空任务目录；开始时已有文件保持原位。

## 关联
- current_logic: logic_readme.md#当前制度
- proposal_id: CHG-20261020-002
- code/tests: references/logic-change-template.md; references/logic-version-template.md; tests/test_workspace.py; tests/test_recall_cli.py
