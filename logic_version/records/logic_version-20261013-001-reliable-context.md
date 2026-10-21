# VER-20261013-001: Recall可靠上下文与持续验证

## 记录控制
- version_id: VER-20261013-001
- version_slug: logic_version-20261013-001-reliable-context
- status: effective
- immutable: true
- date: 2026-10-13
- change_id: CHG-20261013-001
- proposal_revision: 1
- changed_by: Codex
- recall_route: high
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:f2b1e09d7082eaebd11a57415ee7aa7ceeec0ca3; 原始哈希与本轮真实源项目回归
- governance_verification: recorded
- governance_verified_at: 2026-10-13
- before_commit: f2b1e09d7082eaebd11a57415ee7aa7ceeec0ca3
- after_commit: none
- decision_confirmed_by: user
- decision_confirmed_at: 2026-10-13
- decision_ref: user:2026-10-13 认可本轮六项建议并要求优化
- proposal_commit_or_blob: ../backups/reliable-context-20261013/proposal.txt

## 为什么做这个决策？
现行文档静态通过仍有跨命令草稿误报、未提交交付追溯缺口、重复流程说明漂移和较高领域阅读成本。用户已认可六项建议，逐项落实并以实际行为验证。
- raw_request: 认可，请你帮我进行优化；承接本轮已认可的六项建议，目标D:/vscode3/recall。
- decomposition: 统一VER草稿识别；完善未提交交付的追加追溯与提交提示；对齐收尾和personal字段；降低工具链阅读成本；细分Git失败诊断；增加Windows持续验证。
- fit_analysis: 复用INT-20260816-003/004/007/008、INT-20260903-002和INT-20260907-001，沿FLOW-002/003完善文档与工具同一口径；共享记录生命周期与交付不变量的工作在一案分步验证，不改变原历史或操作外部服务。

## 决策过程
| 方案 | 收益与代价 | 决定 |
|---|---|---|
| 复用现有解析、勘误记录和CI，集中共享判断 | 保持字段/命令兼容，解决真实误报；需整包部署共享模块 | selected |
| 只修改文字 | 工作少，但工具仍各报一套状态 | rejected |
| 新建历史/审批体系或立即拆分领域 | 增加入口和迁移，现有领域精简后已低于成本提示目标 | rejected |

## 影响范围
| 项 | 最终行为 | 证据 |
|---|---|---|
| 1 | audit/validate/list/query/status共享草稿口径；唯一活跃CHG、正整数revision和slug匹配才豁免归档；孤立/错配/重复与围栏示例不能伪装状态或commit | 真实CLI及负例回归 |
| 2 | 已归档correction用corrects与真实after_commit追加原决策证据；不改原记录；none不冒充hook占位符；提交提示一次命令包含标题和Ref | 有效SHA、无效SHA、草稿、自指/缺失目标和原记录哈希回归 |
| 3 | 根FLOW/数据流、账本摘要按现行收尾顺序；personal字段说明指向唯一模板；教学项目补真实步骤编号并纳入validate | 示例与完整CLI回归 |
| 4 | 压缩工具链规则的叙述与重复代码地图/测试列表；保留原RULE-ID和全部历史链接；领域readme增加6000估算token提示 | 原链接集合保全；成本8006→5041；提示不改变退出码 |
| 5 | Git诊断保留stderr并区分非仓库、权限/沙箱、工作树、超时和未知失败 | status与validate消费回归 |
| 6 | CI增加Ubuntu/Windows矩阵；真实平台入口测试覆盖中文含空格路径、非交互与UTF-8重定向 | 本机Windows实跑；CI YAML解析 |

消费者为CLI、技能代理与完整scripts部署。保留原命令、字段与表格式，报告只追加状态和成本信息；共享模块record_context需随完整scripts部署，已知目录引用消费者已包含。无业务数据迁移、服务启用或外部发布。旧未标immutable的记录仍按归档处理；不匹配的显式草稿报错。

## 验证方式
基线282项测试通过；实际维护源最终297项全部通过，无跳过。audit/validate/index/next/route与git diff --check通过；技能格式检查与CI YAML解析通过。语义自审核共享判断、真实消费者、兼容边界、不可变历史、清理顺序和验证证据。
- semantic_review_state: passed
- evidence: [检查与清理收据](../backups/reliable-context-20261013/checks.json)

未执行远端Ubuntu/Windows CI，配置已交付；本机Windows入口已真跑。根文档仍有非阻断阅读成本提示。未提交Git，三个本地交付记录的commit关联警告保留真实状态，后续须据实际提交追加追溯。

## 回滚方式
对照原始manifest和Git，仅撤本轮增量，保留原20份已修改文件和原历史。新公共脚本与调用方一并回撤，避免缺模块。若有后续变更则按段落回退。文档原件快照仅作证据；源码由Git和哈希定位，不保存代码快照。历史纠正只追加，不重开旧案。

## 临时产物
本次隔离暂存目录、验证依赖、工作台账和新共享模块字节码均已逐项删除：209个文件、39个目录。原文档快照、最终议案与检查收据作为交付证据保留。
- logic_temp_cleanup: 2026-10-13；本次working目录已删除，台账无pending；逐项处置见checks.json。清理事实发生后本记录才定稿，后续语义纠正只追加。

## 关联
- current_logic: logic_readme.md#当前制度; logic_domains/toolchain/logic_readme.md; logic_domains/git-pipeline/logic_readme.md
- proposal_id: CHG-20261013-001
- code/tests: scripts/record_context.py; scripts/validate.py; scripts/link_ver_git.py; scripts/recall_audit/archive.py; tests/test_record_context.py; tests/test_platform_entry.py
