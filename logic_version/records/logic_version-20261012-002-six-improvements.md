# VER-20261012-002: Recall六项一致性优化

## 记录控制
- version_id: VER-20261012-002
- version_slug: logic_version-20261012-002-six-improvements
- status: effective
- immutable: true
- date: 2026-10-12
- change_id: CHG-20261012-002
- proposal_revision: 1
- changed_by: Codex
- recall_route: high
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:f2b1e09d7082eaebd11a57415ee7aa7ceeec0ca3; 本轮原始哈希与回归日志
- governance_verification: recorded
- governance_verified_at: 2026-10-12
- before_commit: f2b1e09d7082eaebd11a57415ee7aa7ceeec0ca3
- after_commit: none
- decision_confirmed_by: user
- decision_confirmed_at: 2026-10-12
- decision_ref: user:2026-10-12 认可六项建议并要求逐个优化
- proposal_commit_or_blob: ../backups/six-improvements-20261012/proposal.txt

## 为什么做这个决策？
用户授权把已审查的六项优化依次落实到Recall维护源。它们共同保持入口、字段、现行规则和CLI实际行为的一致性，分六步验证，不另建平行工作流。
- raw_request: 认可，请你帮我逐个进行优化；承接本轮已列出的六项Recall技能优化，目标D:/vscode3/recall。
- decomposition: 依次修复项目定位防误写、个人CHG模板、根宪法阅读成本、收尾顺序、根文件路由提示，并补首次接入/中等修改/中断接手示例及对应验证。
- fit_analysis: 复用INT-20260816-003/004/008/010、INT-20260903-002和INT-20260907-001；沿FLOW-002/003/005完善入口、制度、模板与CLI一致性；共享该不变量的六步留同一CHG，分步验证，不新增业务制度或外部授权。

## 决策过程
| 方案 | 收益 | 代价/风险 | 决定 |
|---|---|---|---|
| 最小修改现有入口、模板及CLI | 保持文档与行为一致，有具体回归 | new无根改为失败，路由JSON追加字段 | selected；用户已授权六项建议 |
| 只改说明，保留工具行为 | 改动少 | 仍会误写技能目录，模板继续漂移 | rejected |
| 新增工作流或平行规则文件 | 可另建格式 | 增加入口、重复schema和迁移成本 | rejected |

## 影响范围
| 顺序 | 最终变化 | 验证 |
|---|---|---|
| 1 | new缺项目标记失败；--project严格指根；统一CLI解析；项目模板优先，缺副本用集中模板 | 缺根不写、精确根、嵌套根、错误参数、中央模板和真实CLI |
| 2 | 独立个人最小块，区分块级字段、账本结构与条件字段；保留扩展schema | 将最小块实例化后通过真实审计与状态投影 |
| 3 | 精简根规则重复叙事，全部原有规则ID和历史链接保留；token估算只提示 | 旧链接集合保全、路由与审计同源估算、短行长文不过度放行 |
| 4 | readme→核清理→定稿VER/index→关案，早建VER是关联CHG追踪草稿 | 中断promoting恢复与清理后关案回归 |
| 5 | 根文件matched_root，未知目标unmatched_targets，混合输入不掩盖未知项 | 根/inherited/领域/未知/外部路径测试 |
| 6 | 三个操作实例及可运行mini-project，入口按任务链接 | 接入、medium跟踪、promoting接手及收尾真跑CLI |

改动消费面为Codex/Claude入口、Markdown模板及CLI用户。无持久数据迁移、服务操作或部署。new无根时必须进入正确目录或显式选项目；先前依赖隐式回退的调用需迁移。既有CLI参数保留，路由/密度JSON只追加字段，行数阻断门不变。安装目录仍转发维护源，无需重复配置。

## 验证方式
基线274项测试通过；实际源项目282项测试全部通过；技能格式检查通过；实际项目audit/validate/index/next及路由由检查收据记录。示例在临时副本运行，不修改交付fixture。AI语义审查核授权边界、真实目标、模板字段与机器检查一致、唯一规则来源、操作顺序和不可变历史；静态门不替代该审查。未验证其他操作系统和真实消费项目部署。
- evidence: [检查收据](../backups/six-improvements-20261012/checks.json)
- semantic_review_state: passed

## 回滚方式
对照本轮原始哈希与Git差异只撤本次增量，保留先前七份未提交文档和VER-20261012-001；若已有后续修改，按段落回撤。文件创建防误写应通过另一次显式决策处理，不静默恢复危险回退。无数据迁移。旧VER字节不变，纠正只追加记录；本轮未提交/推送。

## 临时产物
本轮暂存目录与working台账均已逐项删除：212个文件、39个目录。原文档快照、议案和检查收据为交付证据保留；无代码快照。完成后本记录定稿，语义只追加纠正。
- logic_temp_cleanup: 2026-10-12；D:/vscode3/recall/logic_version/working/logic_version-20261012-002-six-improvements已删除，台账无pending；本次暂存及隔离依赖已清理，详见checks.json。

## 关联
- current_logic: logic_readme.md#当前制度; logic_domains/toolchain/logic_readme.md
- proposal_id: CHG-20261012-002
- code/tests: scripts/create_ver.py; scripts/route_docs.py; scripts/recall_common.py; scripts/recall_audit/archive.py; tests/test_recall_cli.py
