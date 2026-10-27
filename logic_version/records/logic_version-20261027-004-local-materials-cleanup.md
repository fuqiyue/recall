# VER-20261027-004: 本地历史材料归属保全与精确清理

## 记录控制
- version_id: VER-20261027-004
- version_slug: logic_version-20261027-004-local-materials-cleanup
- status: correction
- immutable: true
- date: 2026-10-27
- change_id: CHG-20261027-002
- proposal_revision: 1
- changed_by: Codex
- recall_route: medium
- corrects: VER-20261013-002
- before_commit: c45d50953b4130125f832dbde945176bf998700d
- after_commit: none

## 为什么做这个决策？
用户确认逐份盘点方案，要求实际整理旧材料，让Recall项目简洁并保持正常使用。本记录追加旧证据的保全位置和本轮处置事实；原VER-20261013-002及其他不可变记录不改写。

- raw_request: 用户认可逐份盘点方案，要求清理3份可恢复副本，7份按所属项目保全后去重，保留其余8份并核对结果；希望Recall简洁、正常使用，并用直白语言解释实际问题。
- decomposition: 重核18份SHA和3份Git恢复；先将7份的原字节/分项目内容保全到所属项目的小归档并逐项核验，再精确去重；8份原件不变；运行CLI可用性及文档/实物检查，归档处置事实并关闭本案。
- fit_analysis: 复用INT-20260903-001、INT-20261020-001和FLOW-002第4/6步，落实RULE-020/025的已有授权核验清理；不新增技能规则、命令或业务行为。

## 决策过程
采用已确认的3/7/8分类，先保全再精确删除。Recall测试原件和本项目清单合为一个ZIP；教材材料及唯一完整共享原始清单合为一个ZIP；聊天目录只登记2项来源根未确认的文件名/SHA线索。ZIP内逐项标明原字节、派生视图、保留依据及退出条件。未采用整目录删除、把旧材料当作当前故障或修改技能规则的方式。

## 修订记录
| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-27 | 1 | 依据用户确认将盘点转为归档保全和精确去重 | 原18份、教材7份对应副本、项目归档与清单 | 完成归属保全及17项精确删除；8份原件SHA未变，CLI66项及静态检查通过 |

## 影响范围
- 原18份Recall本地材料：删除3份可验证Git恢复副本；7份保全到所属项目后去除散件；8份原件保持原路径及SHA256。
- Recall原备份目录现有8份原件、recall-evidence-20261027.zip和preservation-manifest.md，共10份文件。
- 教材原recall-docs-fix-20261013备份目录新增project-evidence-20261027.zip及preservation-note-20261027.md；精确移除7份对应重复散件。其原manifest.json、10份受控文档快照和其余旧检查结果不变。
- D:/vscode3/聊天记录/recall-历史材料线索-20261027.json只保存2项文件名/SHA及来源说明，不宣称恢复原文。
- 更新历史索引和任务交付规则的证据链接；不改变现行技能语义、CLI源码、权限、其他任务、课件或业务数据。以上材料本轮仅保存在本地，未推送GitHub。

## 验证方式
- 清理前后逐份核SHA：7份原始材料在两个所属项目ZIP中逐字节可恢复；跨项目原始3份保留唯一完整原字节，Recall包不含教材/聊天业务清单。
- 派生分区并集守恒：Recall120+教材85+聊天2=207项基线；Recall9+教材32=41条历史写入；两个阶段检查对象与原对象一致。
- 3份Git恢复逐字节验证：task_context.py.before、test_task_context.py.before来自1c9d5f797938617a693594cfbb5228f17c3d21b6对应原路径；toolchain-change.before来自44bff346983bad5e693133399ea51c88589ff2e3同路径LF内容，转CRLF后原SHA一致。完整SHA及定位见保全清单。
- 仅用PowerShell原生逐项删除已核路径、无重解析点及SHA的文件：Recall10项、教材7项，共17项；8份keep原件SHA不变。5份本轮中转输出在正式副本指纹确认后已删除。
- recall.bat help成功；python -B -m unittest discover -s tests -p test_recall_cli.py：66项全部通过（8.797秒）。audit静态门通过、坏链0；route/next返回合法JSON及退出0；index一致，workspace本任务核对通过，关案正文按规则另行移除。
- 本轮未改运行源码，未重跑全量测试；旧312项测试保留为旧证据，不冒充本轮结果。最终正文、公报及实物状态以本轮关案检查为准。

## 回滚方式
从两个ZIP的包内清单定位7份原件，核SHA后只恢复到独立路径；3份Git副本按准确提交/路径及记录的换行转换还原，核SHA后再决定是否恢复旧位置，不覆盖后续修改。8份keep无需恢复。原不可变记录保持；处置事实需纠正时另追加记录。

## 清理与交付
17份旧散件已移除、5份本轮中转副本已清理，正式归档和8份原件均已核验；未删除任何整个业务目录。原聊天位置、教材旧记录SHA及旧测试版本缺口仅随原始材料保全，本案不回滚或修改它们。该类旧追溯缺口尚不能证明Recall当前功能故障。

## 经验与教训
旧历史材料的归属与恢复问题应在证据目录处理；日常Recall使用依赖现行文档、活跃任务和当前CLI，不需要加载这些旧备份。

## 关联
- current_logic: logic_domains/task-workflow/logic_readme.md RULE-020/RULE-025
- proposal_id: CHG-20261027-002
- code/tests: tests/test_recall_cli.py（仅执行，未修改）
- evidence_manifest: logic_version/backups/worklog-schema-validation-20261013/preservation-manifest.md
