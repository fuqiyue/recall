# VER-20261027-001: GitHub 公开文档梳理与表述优化

## 记录控制

- version_id: VER-20261027-001
- version_slug: logic_version-20261027-001-public-docs-clarity
- status: effective
- immutable: true
- date: 2026-10-27
- governance_mode: personal
- scope: .
- affected_scopes: .
- change_id: CHG-20261027-001
- changed_by: Codex
- recall_route: medium
- history_retention: compact
- proposal_revision: 1
- proposal_commit_or_blob: embedded:本记录的需求拆解、方案与修订记录
- before_commit: 1b855a98f55f6743985e05c21e15f4abfa64cec1
- after_commit: none

## 为什么做这个决策？

**背景**：首页优先展示版本修订、权限和清理例外；贡献指南有旧目录与待建设测试的表述；安全说明包含旧版本表与重复提醒。以实际用途和上手路径组织公开说明，帮助新读者理解项目。

**用户需求/反馈**：user:2026-10-27，本轮公开文档整理请求。

**需求拆解（从 CHG 原样保全）**：
- raw_request: 请你帮我总结梳理目前的github上的recall 项目文档内容，减少负面信息
- decomposition: 重组 README 的价值说明、上手步骤和文档导航；校正 CONTRIBUTING 的流程、目录与测试信息；精简 SECURITY 的重复提醒并保留真实安全边界和报告渠道。
- fit_analysis: 复用 INT-20260816-003/008/010 与 FLOW-002#1、FLOW-003#3、FLOW-005#2 的既有文档入口；只调整公开说明，不改变规则、CLI 行为或 UXI。

## 决策过程

**采用方案**：梳理三份公开入口。README 按用途、快速开始、日常命令和参考导航组织；贡献指南引用现行流程，修正目录与测试现状；安全说明用场景建议表达保护措施，保留私密报告与原有响应时间。

**未采用方案**：只替换负面词语，阅读顺序和过时信息仍会保留；全量改写内部规则和历史超出公开说明整理需要，也增加语义漂移风险。

首页通过已有参考链接提供维护细节。安全文档移除过时的 0.1/0.2 支持表，以实际复现提交定位问题，未新增版本支持承诺。留档采用追加记录、历史索引行和 RULE-019 决策列反链；既有规则正文、滚动索引条目与所有历史文件保留。

## 修订记录

| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-27 | 1 | 用户要求梳理公开文档，先核远端基线及现行文档 | README.md、CONTRIBUTING.md、SECURITY.md | main/HEAD 一致；修改前 audit、validate 退出 0，validate 有既存提交关联及工作区提醒 |
| 02 | 2026-10-27 | 1 | 重组首页与文档导航，更新贡献指南和安全表述 | README.md、CONTRIBUTING.md、SECURITY.md | 29 处本地链接/片段有效；CLI 帮助、CI 与路径核对；audit、index、diff 检查通过 |
| 03 | 2026-10-27 | 1 | 自动审批拒绝滚动索引方案，采用保留全部既有条目的追加方式 | 本记录、logic_version/index.md、RULE-019 决策列引用 | 原补丁未执行；先只读确认，再追加引用，不删除历史 |

## 影响范围

- README.md：价值说明、跨平台启动、常用命令和按需文档导航。
- CONTRIBUTING.md：当前贡献流程、真实目录与 unittest/CI 入口。
- SECURITY.md：私密报告、脱敏建议、文件存储与 Git 同步边界。
- logic_version/index.md、logic_readme.md：仅追加留档索引与 RULE-019 反链，规则语义保持原状。

**破坏性变更**：否；仅公开说明与留档引用。

## 验证方式

- GitHub `git ls-remote origin refs/heads/main` 与本地 HEAD 均为基线 SHA；只读核对，文档尚未提交或推送。
- Python 只读检查三份文档 UTF-8 和 29 处本地链接/片段，全部有效；核对 CLI help、init --help、脚本路径、测试文件及 CI 配置。
- `recall audit --json`：静态门通过；`recall index`：编辑后公报一致。
- `recall validate`：退出 0；既存历史提交关联及工作区提醒保留，任务状态变化期间的公报差异在收尾时重建。
- `recall workspace --closing CHG-20261027-001`：本任务与全项目错误、提示及进行中项均为 0。
- `git diff --check`：通过。仅编辑说明文档，未新增测试或重跑完整测试套件；CI 描述依据配置，未将配置视作本轮运行结果。

## 回滚方式

仅撤销本轮三份公开文档及本次记录/索引增量，保留用户原有修改；尚无本次提交，不使用全仓重置。

## 清理与交付

- logic_temp_cleanup: none（未创建临时代码、输出或备份）；需求三字段与全部三轮修订已逐项核对保全，关案移除本任务正文及空任务目录。
- 保留三份公开文档与本记录作为交付物；本轮之前的未跟踪文件及其他修改按原状保留。
- 交付状态：本地文档完成，未提交、未推送；后续提交关联可按 Git 管道 RULE-013 追加追溯。

## 经验与教训

公开文档优先说明项目用途与操作路径，详细维护边界通过现有参考文档按需提供；提醒使用具体建议，事实与必要约束保持可查。

## 关联

- current_logic: ../../logic_readme.md（RULE-019）；../../README.md；../../CONTRIBUTING.md；../../SECURITY.md
- proposal_id: CHG-20261027-001
- former_proposal_path: logic_changes/public-docs-clarity/logic_change.md
- code/tests: scripts/recall.py、scripts/init_recall.py、tests/、.github/workflows/validate.yml（核对，未修改）
