# VER-20261024-001: 任务准确路由、增量地图与分层清理

## 记录控制
- version_id: VER-20261024-001
- version_slug: logic_version-20261024-001-task-context-workspace
- status: effective
- immutable: true
- date: 2026-10-24
- change_id: CHG-20261024-001
- proposal_revision: 1
- changed_by: Codex
- recall_route: high
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: 本机行为回归及教材项目只读实测
- governance_verification: recorded
- governance_verified_at: 2026-10-24
- before_commit: 94bc88b160691429b6242f36e920de5eeb1aa90c
- after_commit: none
- decision_confirmed_by: user
- decision_confirmed_at: 2026-10-24
- decision_ref: user:2026-10-24 本轮确认优化方向并修正合并任务和临时物处置要求
- proposal_commit_or_blob: user:2026-10-24 本轮请求；最终需求与修订表在本记录保全

## 为什么做这个决策？
教材项目暴露了三个工具缺口：任务路径漏读领域规则、局部盘点覆盖其他范围、其他任务残留混入本任务结果。任务正文虽集中，仍需约束相近需求分案、状态重复和临时产物积累。
- raw_request: 用户认可任务精确路由、地图保留扫描范围并局部更新、区分本任务和全局问题；相近或相同需求合并正文；任务结束清理临时文件，台账补保留依据和退出条件，各轮处理产物且不以数量决定删除。
- decomposition: 修复任务到领域的路由；实现地图覆盖范围合并；按任务与轮次核对产物并保留全局视图；精简合并任务和当前状态的维护规则。
- fit_analysis: 复用 INT-20261020-001 与 INT-20260816-003，覆盖 FLOW-002 的读取、记录和收尾；保留 UXI-006 的只核对不静默删除边界。

## 决策过程
选择按任务声明定位规则、在现有地图内记录覆盖、在现有台账上增列并提供结果视图。继续关键词匹配任务会漏读/误读；每次全量重扫浪费且不能代表数据目录覆盖；另建计划和清理数据库会重复真源，均未采用。

相近需求能统一目标/验收/收尾时优先合并原 CHG，独立发布/回滚或授权冲突仍分案。合并保留原 ID、授权及失败修订事实，当前状态只有一处，结束后同一 VER 保存必要历史。临时物每轮处理、完成后清理；有依赖的跨轮产物明确归属，正式数据/证据保留须有依据与退出条件。

## 修订记录
| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-24 | 1 | 按用户确认合并为一次上下文与工作区优化 | scripts/route_docs.py、scripts/workspace_*.py、references/ | 已复核任务路由、覆盖丢失和结果混合缺口 |
| 02 | 2026-10-24 | 1 | 实现任务声明路由、覆盖合并和分任务/轮次视图；补任务合并与产物退出规则 | scripts/、tests/test_workspace.py、SKILL.md、references/、logic_readme.md | 首轮完整回归 341 项：340 通过、1 项符号链接权限跳过；修正测试夹具重复 ID 创建顺序 |
| 03 | 2026-10-24 | 1 | 教材只读实测发现二级小节被截断，修复旧任务台账兼容；默认检查输出压缩摘要 | scripts/workspace_check.py、scripts/workspace_cli.py、tests/test_workspace.py | 任务 ID/路径均命中声明的 7 个领域；当前任务通过，全局另一任务临时目录仍报错；最终 342 项回归中 341 通过、1 项符号链接权限跳过；静态门与关案核对通过 |

## 影响范围
更新操作入口、模板和根 RULE-018/020/027/029；路由、目录地图与产物检查增加行为回归。新增 workspace_maps.py 仅管理可重建地图格式，不另建过程文档或数据索引文件。教材项目始终只读。

兼容：旧五列表和旧文件地图可读；原 JSON 键保留。route 默认只展开直接任务，其他相关正文须按 ID 或 --include-related 请求；workspace 的 ok/findings 仍为全局，新增 task_result/round_result/global_result/other_findings/selection_ok，筛选时退出码对应所选视图，普通文本显示摘要。地图完整列举才移除失效索引，预算/深度/数据边界保留旧时间，文件本身不删除。

## 验证方式
本机 Windows 完整 unittest 共 342 项：341 通过，1 项因符号链接权限跳过；技能 quick_validate、audit 静态门、workspace 关案核对与 git diff --check 通过。validate 无错误；旧记录 Git 追溯、未提交改动及原有备份告警据实保留。只读教材实测已确认领域声明映射和本任务/其他任务区分；未执行教材目录清理、地图写入、远端 CI 或 GitHub 发布。

自审通过：任务声明与关键词路径分开，地图不丢未扫描范围，筛选检查不隐去全局问题，旧台账和任务标题层级保持兼容。合并适用性、保留依据真实性及修订归档完整性仍需代理判断，数量或扫描结果均不直接触发删除。

## 回滚方式
撤销本次源码/技能/模板增量；生成地图可重新扫描。退回旧版前先重建其支持的地图，避免旧实现全量覆盖局部清单。已经归档决定不改写，新的调整另留记录。

## 临时产物
本次无独立临时代码或过程正文；自动化夹具使用 TemporaryDirectory 并退出。已核创建时间并删除本轮生成的六个 scripts/__pycache__/*.cpython-312.pyc（git_sync、route_docs、workspace_check、workspace_cli、workspace_inventory、workspace_maps）；既有其他缓存、备份和用户文件保留。正文台账为 2 项保留（新模块和决策记录）、6 项删除；关案复查无错误/残留。需求三字段、修订表和最终版本核对一致，定稿后移除本任务正文及空目录。

## 关联
- current_logic: logic_readme.md#当前制度
- proposal_id: CHG-20261024-001
- code/tests: scripts/route_docs.py; scripts/workspace_inventory.py; scripts/workspace_maps.py; scripts/workspace_check.py; scripts/workspace_cli.py; tests/test_workspace.py
