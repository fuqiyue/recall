# VER-20261027-007: 授权运行流程与任务退出优化

## 记录控制
- version_id: VER-20261027-007
- version_slug: logic_version-20261027-007-workflow-authorization-closure
- status: effective
- immutable: true
- date: 2026-10-27
- change_id: CHG-20261027-004
- proposal_revision: 1
- changed_by: Codex
- recall_route: medium
- before_commit: 9b041fb057b4fee2fd9dc79be418a9f91e5b44b7
- after_commit: 598abd164f937ec786cf7d773a67d0b3ada23bec

## 为什么做这个决策？
用户认可流程图优化，并要求完成任务后清理相关任务文件，避免后续使用继续发现旧任务。实际反馈用于提炼工具流程；消费项目的业务材料未复制到本仓库，也未操作其文件。

- raw_request: 用户认可授权与运行流程优化，要求保留功能，并以已完成任务仍残留材料的实际反馈改进收尾；只维护 Recall 工具，检查后提交推送。
- decomposition: 将授权等待改为条件分支；区分用户授权、平台权限与验证；标明命令写入及推送影响；合并生命周期重复说明；落实任务正文、临时物与索引退出，必要材料先安置再清理。
- fit_analysis: 复用 INT-20260816-003/005/006、INT-20260903-001、INT-20260907-001、INT-20261020-001；完善 FLOW-002 的授权、运行与收尾步骤，保持 UXI-003/005/006。

## 决策过程
保留三通道、规则编号及现有 CLI/schema，把已有授权作为主路，真实缺口作为条件分支。授权、平台权限和验证分开表达；命令表与 Git 实现对照，避免提交时才发现 hook 会推送。

合并生命周期九步与晋升清单为一条路径；必要材料先安置并核消费者，再删除临时副本、已归档正文及空目录，核公报和实物退出。保留真实受阻出口，不以改名、整目录搬家或忽略文件代替清理。未采用批量自动删除：任务完成并不能证明目录内业务数据已无消费者。

## 修订记录
| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-27 | 1 | 按已认可方案调整授权、运行与清理导航 | SKILL.md、references/、所属 readme | 353 项测试：352 通过、1 跳过；静态门、技能校验、63 份文档链接及编号核对通过；workspace 本任务无残留 |

## 影响范围
- SKILL.md：总流程、执行权限分支与命令影响导航。
- references/change-lifecycle.md：统一状态路径、实施与验证、收尾及归档保全。
- references/task-context.md、workspace-tasks.md：授权示例、产物去向和退出判据。
- references/git-sync.md 与 Git 领域维护说明：核 hook、命令副作用和同步证据。
- 根意图/FLOW、任务领域 RULE-020/025：明确任务正文与临时物实际退出。
- CHG/VER 模板仅更新操作指针，字段、解析和旧格式兼容保持不变；历史索引同步记录并校正上一行列数。
- 破坏性变更：无；运行代码、测试、旧不可变记录、消费项目文件均未改动。

## 验证方式
- AI 语义核对：三通道、来源、条件确认、消费者与回滚、需求/修订/主题保全、受阻出口仍在现行规则及对应操作说明。
- unittest discover：353 项，352 通过、1 项跳过；37.735 秒。
- 技能 quick_validate 通过；audit 静态门通过；validate 无错误，6 条旧记录缺提交关联告警保持原状。
- 实施阶段 63 份文档链接核对通过；29 RULE、16 INT、5 FLOW、6 UXI 编号无删除或重复。
- workspace --closing CHG-20261027-004：本任务无发现，pending_cleanup 为 0。无本轮临时脚本、备份或独占工作目录；任务正文在归档核对后移除，关案后再核公报与实物。
- 生命周期正文从 5729 字符压缩为 3706 字符；Git 命令及清理说明补充必要操作影响，不以总字数替代功能完整性。

## 回滚方式
按 Git 撤销实施提交的文档增量；新的回滚事实另行留档，不覆盖本记录。未修改运行代码或消费项目数据。

## 经验与教训
将实际清理列入交付判据；必要证据按用途保留最小集合，工作目录不因业务完成而自动变成永久档案。用户已有授权与实际执行权限分别核对。

## 关联
- current_logic: logic_domains/task-workflow/logic_readme.md
- proposal_id: CHG-20261027-004
- code/tests: tests/test_git_sync.py; tests/test_recall_cli.py; tests/test_workspace.py
