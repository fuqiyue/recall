# VER-20261026-002: 根规则精简与领域归属

## 记录控制
- version_id: VER-20261026-002
- version_slug: logic_version-20261026-002-root-domain-slim
- status: effective
- immutable: false
- date: 2026-10-26
- change_id: CHG-20261026-002
- proposal_revision: 1
- governance_mode: personal
- recall_route: medium
- history_retention: compact
- changed_by: Codex
- decision_confirmed_by: user
- decision_confirmed_at: 2026-10-26
- before_commit: 0e38394bf6ce3abafbff2d54175b222630e5b90d
- after_commit: none
- promoted_rules: RULE-016; RULE-018; RULE-020; RULE-022; RULE-025; RULE-026; RULE-027; RULE-029

## 为什么做这个决策？
根现行文档是每次必读入口，但特定任务的操作规则占用大量上下文。用户要求按领域下放，保持现行规则完整且唯一，再更新 GitHub。
- raw_request: 请继续优化根 logic_readme.md 的简洁程度，把适合下放的内容放到对应的 logic_domains，减少每次必读的内容，同时保证现行规则完整、避免重复。然后更新github。
- decomposition: 按职责迁移领域规则并保留原编号和证据链接；压缩根导航与重复说明；同步规则指针和路径/意图路由；验证唯一性、完整性与阅读成本；归档关案并提交推送 GitHub。
- fit_analysis: 复用 INT-20260816-003、INT-20260816-011 与 INT-20260903-002，落实 FLOW-002#1/4/5 及 FLOW-005#4；保留 INT/FLOW/UXI 根层入口，不改变 CLI 行为或业务授权边界。
- intent_traceability: INT-20260816-011 -> RULE-018 -> test:tests/test_recall_cli.py -> VER-20261026-002

## 决策过程
- 仅压缩措辞：文件更短，但每次仍加载无关流程细节。
- 全部移入工具链：减少根长度，却使维护 CLI 时继续加载不相关的文档/交付制度。
- 选用两个 readme-only 领域：文档治理承接 RULE-016/022/026，任务交付承接 RULE-020/025/027/029；保留原编号、完整规则、why 和留档反链。根保留全局约束、INT/FLOW/UXI、职责导航及验证入口。无需更改路由算法或引入新格式。

## 修订记录
| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-26 | 1 | 审查必读成本与领域边界，选择保留规则编号的迁移 | 根及领域readme、references、SKILL | route基线已确认，远端基线一致 |
| 02 | 2026-10-26 | 1 | 迁移七条规则，更新导航/范围/引用与领域职权 | 根和四个领域、相关references、SKILL | 根读取成本约降36%，两类路径路由正确；完整回归见第03轮 |

| 03 | 2026-10-26 | 1 | 核规则保全、路由及发布回归 | 全部现行readme、路由、既有测试 | 29条规则无重复/缺失/语义丢失；353测试OK（1环境跳过）；audit零问题；skill有效 |

## 影响范围
- logic_readme.md：根从156行/约8870估算token降至140行/约5715token（约减少36%）；删除领域规则的根副本及重复的说明段，保留29条规则的全局唯一编号空间、16个INT和5个FLOW。
- logic_domains/document-governance/logic_readme.md 与 task-workflow/logic_readme.md：新增唯一现行定义、路径归属及验证入口；不生成空领域change。
- Git/工具链领域：补自身路径、Git参考归属及迁移后的当前规则指针；既有JSON/CLI语义不变。
- SKILL及references：版本2026.10.26.2，规则来源链接指向新所属领域；更新根/领域模板的搬迁与readme-only说明。
- 本次发布还包含上一轮现行/历史边界更新，以及工作区已有的审计边界提示汇总代码。四个原有代码/测试文件本轮未编辑，发布前通过全部既有测试。
- 破坏性变更：无；原规则编号、条款正文与理由均保全，机器可读表头、ID格式和旧paired兼容不变。

## 验证方式
- 从根与4个登记领域提取规则：29条，无重复/丢失；迁移前后的原根规则正文和why逐条完全一致。
- 路径、RULE、INT、CHG路由共11组：无未命中或范围警告；文档/任务/Git参考分别命中所属领域，历史正文不进入读取清单。
- skill-creator quick_validate：Skill is valid。
- python -B -m unittest discover -s tests：353项，352通过，1项因本机不能创建符号链接跳过；Windows本地运行。
- recall audit --json：静态门通过，无完整性/坏链接/密度问题；根和各领域低于token目标。
- recall validate：无错误；旧记录提交关联、本次草稿晋升和未提交文件提示如实保留，随后按真实Git提交补关联。
- recall workspace --closing CHG-20261026-002：任务及全局均无findings，pending_cleanup为0。
- GitHub同步及远端CI以本轮发布后的实际SHA与运行结果为准，不由本地测试代替。

## 清理与保全
本任务无临时目录、探针或生成日志。迁移条款/需求三字段/修订表已核对；原历史文件字节指纹保持不变（全量index允许追加）。本地既有未跟踪备份保持原位并排除发布。定稿及index就位后，按已核验唯一任务路径删除重复CHG正文及空目录，再核根公报。

## 回滚方式
以实际交付提交执行git revert可还原根/领域布局和引用；回滚后重跑audit/validate/route。已定稿历史保留，必要时追加回滚事实，不覆盖旧记录。

## 关联
- current_logic: [根现行规则](../../logic_readme.md)、[文档治理](../../logic_domains/document-governance/logic_readme.md)、[任务交付](../../logic_domains/task-workflow/logic_readme.md)
- proposal_id: CHG-20261026-002
- code/tests: scripts/route_docs.py; tests/test_recall_cli.py; tests/test_workspace.py; tests/test_audit_logic_map.py
