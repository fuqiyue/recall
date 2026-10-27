# VER-20261026-005: 授权沿用与必要收尾简化

## 记录控制
- version_id: VER-20261026-005
- version_slug: logic_version-20261026-005-authorization-through-closure
- status: effective
- immutable: true
- date: 2026-10-26
- change_id: CHG-20261026-005
- proposal_revision: 1
- before_commit: 1b855a98f55f6743985e05c21e15f4abfa64cec1
- after_commit: none

## 为什么做这个决策？
入口的授权沿用与清理审批用词不一致，容易让代理在正常收尾时重复索取授权。用户认可诊断并要求简化现有 skill。

- raw_request: 用户认可授权覆盖必要收尾的诊断，要求优化当前 Recall skill，并再考虑更简洁高效的处理方法，随后要求继续。
- decomposition: 在既有任务交付规则明确授权持续到必要收尾；统一 Skill、清理步骤、生命周期与台账说明；核验允许内直接执行、真实审批拒绝与范围变更三个场景；验证并归档清理。
- fit_analysis: 复用 INT-20260903-001、INT-20260907-001 和 INT-20261020-001，明确 FLOW-002 第4步包含清理及关案，澄清 UXI-006 的检查工具与代理执行职责；不新增流程、命令或权限机制。

## 决策过程
采用既有 RULE-020/025 内的局部修订，入口给出直接执行的操作指针；生命周期取消仅凭换轮、修订号或依赖变化就让授权失效的绝对表述，改为核实际影响。
未选择新增授权表、清理命令或审批状态：这些会重复已有任务来源与台账，增加维护成本。未选择取消执行审批：任务授权不扩大平台权限。未选择只改入口：参考文档仍会产生相反指引。

## 修订记录
| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-26 | 1 | 将授权与清理收敛进现有规则，消除重复审批歧义 | SKILL.md、任务交付规则、清理与生命周期参考 | Skill校验、audit/validate、index/route/workspace通过；授权内清理、范围变化与平台拒绝场景自审通过 |

## 影响范围
修改 SKILL.md、README.md、根意图及UXI、任务交付规则、workspace-tasks/change-lifecycle/logic-temp-template 参考；技能版本为2026.10.26.3。CLI、字段与权限配置无变化。本机安装入口继续读取维护源；其他独立复制安装需更新源文件。

## 验证方式
Skill quick_validate通过；recall audit静态门通过，current_integrity无问题；recall validate无错误；index一致，route命中所属领域，workspace --closing CHG-20261026-005通过且无临时残留，git diff --check通过。既有历史未关联提交、旧未跟踪备份及本轮未提交修改如实提示。

AI语义自审通过：原范围内本任务临时物核验后直接清理；换轮/接手/收尾不自动失效；临时目录内的业务数据不自动变成可删临时物；原授权未覆盖的新影响只处理该缺口；平台拒绝后不改工具绕过，继续不受影响工作。本轮只改文档，未模拟或保证平台自动审批结果，不新增措辞匹配测试。

本轮未生成临时脚本、输出或备份；归档保全需求三字段、修订表及必要结论。定稿与索引就位后按RULE-020/025核对并移除已归档任务正文，关案结果由公报与实物检查确认。

## 回滚方式
撤销本次现行文档增量，保留本记录；不修改业务数据、执行权限或既有历史。当前修改尚未提交，after_commit如实为none。

## 经验与教训
核验、业务授权及执行审批须各有明确触发条件；检查工具只读不妨碍代理按原授权完成必要清理。

## 关联
- current_logic: logic_domains/task-workflow/logic_readme.md RULE-020/RULE-025
- proposal_id: CHG-20261026-005
- code/tests: scripts/workspace_cli.py; scripts/workspace_check.py（本轮只核对，未修改）
