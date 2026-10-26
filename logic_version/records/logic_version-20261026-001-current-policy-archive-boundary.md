# VER-20261026-001: 现行规则、增量更新与历史留档边界

## 记录控制
- version_id: VER-20261026-001
- version_slug: logic_version-20261026-001-current-policy-archive-boundary
- status: effective
- immutable: true
- date: 2026-10-26
- change_id: CHG-20261026-001
- proposal_revision: 1
- confirmed_proposal_revision: 1
- changed_by: Codex
- decision_confirmed_by: user:2026-10-26 本轮明确要求审查无问题后更新技能
- decision_confirmed_at: 2026-10-26
- recall_route: medium
- history_retention: compact
- promoted_rule_ids: RULE-002, RULE-003, RULE-027
- before_commit: 0e38394bf6ce3abafbff2d54175b222630e5b90d
- after_commit: none

## 为什么做这个决策？
现有结构已支持领域路由、同任务更新和增量地图，但技能及代理入口仍把高风险、兼容判断或现行文档链接作为读历史条件。用户明确要求：议案完成后生效内容合入现行文档，历史只记录修改并留档，日常工作不依赖历史。

- raw_request: 用户明确 logic_change 是修改议案，完成后把生效内容记入 logic_readme；logic_version 只记录修改并留档，日常修改不读历史，除非要求查阅历史；认可继续支持增量修改及分开评价简洁程度，要求审查无问题后更新 Recall skill。
- decomposition: 明确现行规则、活跃议案、历史留档三者边界；统一技能与代理入口的历史读取条件；保留局部增量更新并明确当前状态及时更新；验证后归档关案。
- fit_analysis: 复用 INT-20260816-003/006/007/011 和 FLOW-002#1/4、FLOW-003#1/2；修改 RULE-002/003/027 的说明，沿用 RULE-018/022/025/029，不新增文档层级、CLI字段或审批。

## 决策过程
采用既有结构内的定向更新：明确现行文档、活跃议案与历史留档职责，统一入口和参考说明，补清关键节点更新任务状态。未采用新增文档层级或自动读取历史的方案，因为现有路由已足够，新增层级会增加阅读和维护成本。现行 readme 保留必要理由及历史链接，链接只提供留档入口。

## 修订记录

| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-26 | 1 | 根据用户纠正审查边界并登记本次最小更新 | SKILL.md、logic_readme.md、references/、代理入口 | 基线 audit/validate 无错误；安装入口指向本维护源 |
| 02 | 2026-10-26 | 1 | 统一现行规则与历史留档边界、增量修改及进度更新；补齐本案scope与归档关联 | SKILL.md、logic_readme.md、README.md、AGENTS.md、CLAUDE.md、references/、logic_version/index.md | quick_validate通过；62项回归61通过1跳过；audit/validate无错误，workspace本案无残留 |

## 影响范围
- SKILL.md：版本2026.10.26.1；现行规则优先、历史显式按需、增量修改与进度更新。
- logic_readme.md：RULE-002/003/027、相关意图及归档边界；最近索引保留3条。
- references/document-model.md、change-lifecycle.md、task-context.md：读取与晋升操作保持一致。
- references/logic-version-template.md、logic-vs-code-recall.md：明确修改事实留档。
- AGENTS.md、CLAUDE.md、references/agent-entry-template.md、README.md：统一既有与新接入项目的入口说明。
- logic_version/index.md、logic_change.md：本次归档及派生公报。
- CLI、字段schema、路由及地图算法无变更；既有未提交代码和旧历史须保持原字节。

## 验证方式
- skill-creator quick_validate：通过。
- 既有回归：test_recall_cli 的 RouteDocsTests、CreateVerTests、PersonalTemplateExampleTests，以及 test_workspace、test_task_context；共62项，61通过，1因主机不能创建符号链接跳过。
- recall audit：静态门通过，当前文档、引用、议案和代理入口问题均为0；根文档篇幅/token仍为既有建议性提示。
- recall validate：无错误；保留既有Git关联和未提交文件提示。草稿在晋升期的索引提示将随定稿关闭。
- recall route CHG-20261026-001：命中根与本任务，无需读历史或无关领域；scope改回所属根后已复核。
- recall workspace --closing CHG-20261026-001：退出0，本任务无发现项；本轮无临时目录或探针文件。
- AI语义审查：检查现行规则、技能入口、生命周期及Codex/Claude模板；已消除高风险、历史链接自动触发读档的表述，保留增量规则与地图机制。
- 字节指纹：更新前40份历史记录及5份既有改动的代码/领域文件全部保持原字节。
- Windows本地维护源验证；安装入口已指向该维护源。没有提交或推送；本记录after_commit为none。
- 本任务CHG需求三字段和两轮修订表核对保全；归档就位后删除已结束正文及空任务目录，最终结果由关案后的index/next/workspace再核。

## 回滚方式
只逆向本轮文档增量，保留原工作树未提交变更；已定稿记录不改写，需纠正时另建记录并更新现行文档。

## 经验与教训
现行规则应能独立支持修改。变更留档保存修改事实及必要理由；链接、格式和本次归档保全核验不把历史变成日常设计上下文。

## 关联
- current_logic: logic_readme.md
- promoted_rules: RULE-002, RULE-003, RULE-027
- intent_traceability: INT-20260816-003 -> RULE-002 -> test:tests/test_recall_cli.py#RouteDocsTests -> VER-20261026-001; INT-20260816-003 -> RULE-003 -> test:tests/test_recall_cli.py#RouteDocsTests -> VER-20261026-001; INT-20260816-006 -> RULE-027 -> test:tests/test_task_context.py -> VER-20261026-001
- proposal_id: CHG-20261026-001
