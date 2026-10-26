# VER-20261025-006: 临时目录边界告警汇总显示

## 记录控制

- version_id: VER-20261025-006
- version_slug: logic_version-20261025-006-audit-boundary-summary
- status: effective
- immutable: true
- date: 2026-10-25
- change_id: none
- proposal_revision: 1
- before_commit: none
- after_commit: none

## 为什么做这个决策？

活跃任务的临时目录仍在增长，默认扫描预算会产生大量同类 `incomplete-temp-scan` 边界项。用户要求在不删除、移动或暂停活跃 817 课任务的前提下改善可读性。
- raw_request: 请继续优化剩余的 200 条 audit 临时目录边界告警，尽量压缩为可读的汇总提示，但不要删除、移动或暂停活跃的 817 课任务
- decomposition: 保持工作区扫描、判定、退出码和 JSON 逐路径明细不变；仅在 audit/validate 人读文本中按临时目录汇总同类边界项，并保留总数与样例；用单元测试和消费项目回归确认活跃临时目录未被改动
- fit_analysis: 延续 RULE-020 的真实产物核对和 RULE-022 的可读性目标；汇总发生在渲染层，不改变 `workspace` 事实结果、告警严重级别、清理流程或活跃任务文件

## 决策过程

采用渲染层汇总而非降低扫描预算、忽略目录或删除告警。`workspace --json` 与内部 `findings` 仍保留每条路径，文本输出显示总项数、临时目录数和最多三个样例；因此用户可先读摘要，需要时仍能追溯完整路径。

## 修订记录

| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-25 | 1 | 新增边界项汇总格式化函数，接入 audit/validate 文本渲染，补充根目录分组回归 | scripts/workspace_check.py; scripts/recall_audit/report.py; scripts/validate.py; tests/test_workspace.py | 全量 unittest 353项通过、1项既有符号链接权限跳过；消费项目 200项仍可由 JSON 逐路径追溯 |

## 影响范围

Recall 的 `audit`、`validate` 人读输出和工作区汇总格式化辅助函数。不会修改任何项目临时目录、任务状态、凭证、扫描预算、严重级别或 JSON 字段/逐项明细。

## 验证方式

- `python -m unittest discover -s tests`：353项通过，1项既有 Windows 符号链接权限跳过。
- 消费项目 `recall audit --current-state`：仍识别 200 条 current-integrity 边界项，文本折叠为一条含数量、2个临时目录和3个样例的提示。
- 消费项目 `recall validate`：仍以边界项导致失败，文本折叠为一条错误提示；未删除、移动或暂停 `.work/临时-全部已入课提示词更新` 及其他活跃目录。
- `workspace --json` 与高预算只读工作区证据继续保留逐路径核对能力。

## 回滚方式

恢复 `report.py`、`validate.py`、`workspace_check.py` 及测试的上一版即可；不触及消费项目文件和活跃任务目录。回滚后原逐项文本会恢复，JSON 与工作区判定仍不变。

## 关联

- current_logic: logic_readme.md; logic_domains/toolchain/logic_readme.md
- code/tests: scripts/workspace_check.py; scripts/recall_audit/report.py; scripts/validate.py; tests/test_workspace.py
- consumer_evidence: D:/vscode3/教材知识点/k12_knowledge_starter/verification/teaching-all-refresh-recall-workspace-live.json
