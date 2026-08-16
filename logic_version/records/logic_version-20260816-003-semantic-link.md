# VER-20260816-003: 需求↔架构语义链路补全

## 记录控制

- version_id: VER-20260816-003
- version_slug: logic_version-20260816-003-semantic-link
- status: effective
- date: 2026-08-16
- change_id: CHG-20260816-002
- before_commit: 02467f0
- after_commit: _待填写_
- recall_route: high
- history_retention: full
- decision_confirmed_by: user
- decision_ref: user-confirmed:2026-08-16
- changed_by: Claude (Fable 5)
- intent_traceability: INT-20260816-010 -> RULE-016 -> test:scripts/audit_logic_map.py -> VER-20260816-003; INT-20260816-007 -> RULE-014 -> test:tests/test_recall_cli.py -> VER-20260816-003

## 为什么做这个决策？

**背景**：
开发流程视角审查发现，机械追溯链（commit↔记录）修复后，"需求↔架构"这条语义
链路仍有三个结构性缺口，全部压在 Recall 的核心价值上：(1) SKILL/FLOW-001 只覆盖
Git 管道，"存量项目的 logic_readme 内容从哪来"没有任何流程，系统全部价值建立在
一份没人负责生成的文档上；(2) raw_request/decomposition/fit_analysis 只活在 CHG，
归档即删除，VER 模板无对应字段——变更完成的那一刻需求拆解只剩 git 考古可查
（CHG-20260816-001 甚至因立案与归档同提交而正文从未进入 git 历史），恰好违反
"recall 而非 rescan"的立项原因；(3) `recall query` 只有代码→决策方向，开发主场景
"改功能 X 要动哪些规则和文件"要人肉走三跳，INT 表也没有代码锚点列。

**用户需求/反馈**：
"认可你提到的P0的问题，请你帮我修改。存量项目接入采用模块化管理，当新项目时候
使用，或者用户单独要求的时候，完善和补充相关的文档。其他的按照你的思路来。"

**需求拆解（自 CHG-20260816-002 原样搬入）**：
- raw_request: 用户确认开发流程审查的三个 P0 问题并要求修改；补充约束："存量项目接入采用模块化管理，当新项目时候使用，或者用户单独要求的时候，完善和补充相关的文档。其他的按照你的思路来"（2026-08-16）
- decomposition: 1) 存量项目接入流程：新建 references/project-onboarding.md（模块化渐进接入：接入时建根骨架+范围登记，按"新项目使用时/用户单独要求时"逐模块补全）；SKILL.md 加接入章节；logic_readme 加 FLOW-005、INT-20260816-010、RULE-016
  2) 需求保全：VER 快速模板补 raw_request/decomposition/fit_analysis 字段；归档步骤（logic-version-git-template §4、logic_version/index.md、change-lifecycle.md §7、logic_change.md 底部说明）明确"删除 CHG 前把三字段搬入 VER"；validate 对 change_id != none 的记录检查三字段
  3) 反向查询：logic_readme 与模板的 INT 表增加"代码锚点"列；link_ver_git.py 新增 intent 模式（INT → 规则 → 决策记录 → 代码锚点汇总）并修复 COMMIT_PATTERNS 缺 after_commit 的漂移；recall.py 路由 query intent；validate 检查 INT 代码锚点存在性
- fit_analysis: 1) 新增 INT-20260816-010 与 FLOW-005（首次接入 FLOW-001 只覆盖 Git 管道，接入文档初稿流程为新增，不替代既有 INT）；2) 强化 FLOW-002#3-#5 归档环节的既有语义，不新增 INT；3) 扩展 INT-20260816-007（recall query 增加 intent 方向），复用 FLOW-003#2；三项均不触碰 UXI-001..004（不增加用户必须记忆的多步序列，query intent 是单命令）

## 决策过程

**方案 A**：一次性全量扫描生成存量项目文档（接入即完整）——初稿全面但冷启动成本
在大项目不可行，且大量 AI 推断意图未经确认就成为"真源"（复杂度：高，否决）。

**方案 B**：CHG 归档后永久保留在 logic_change.md——需求不丢失但破坏该文件
"临时工作区"语义，活跃议案与死议案混杂，正是 INV-002 要防止的膨胀（复杂度：低，否决）。

**方案 C（选中）**：模块化渐进接入（根骨架 + pending-docs 可见化 + 按触发时机补全，
触发时机采用用户裁定：新项目使用时/用户单独要求时）；需求保全走"归档时三字段
原样搬入 VER"（模板加字段 + 四处归档步骤同步 + validate 检查，检查限定规则生效日
之后的记录，历史记录不追溯问责）；反向查询在 link_ver_git.py 内实现（复用记录解析
与项目根查找，不新建脚本），INT 表加代码锚点列并由 validate 查存在性（复杂度：中）。

**选中方案与原因**：C。三个缺口的共同修法是"让链路两端都有登记、中间有工具走通"：
接入流程让文档存在，需求保全让文档完整，反向查询让文档可达。

## 影响范围

**修改的文件/模块**：
- `references/project-onboarding.md` - 新建：模块化项目接入流程（根骨架/访谈/逐模块补全）
- `SKILL.md` - 新增"项目接入"章节与参考文档链接
- `references/logic-version-git-template.md` - 快速模板补需求三字段；归档步骤要求搬运
- `references/logic-readme-template.md` - INT 表加代码锚点列与维护说明
- `references/change-lifecycle.md`、`logic_version/index.md`、`logic_change.md` 底部说明 - 归档步骤统一加"三字段搬入 VER"
- `scripts/validate.py` - check_record_requirement_fields（需求保全）；check_intent_layer 加代码锚点存在性
- `scripts/link_ver_git.py` - query_intent 反向查询；COMMIT_PATTERNS 补 after_commit（修复与 validate 的漂移，recall list 曾把新记录显示为待填写）
- `scripts/recall.py` - query intent 路由与帮助
- `logic_readme.md` - INT 表加代码锚点列与 INT-20260816-010；FLOW-005；RULE-014/015 更新；新增 RULE-016
- `tests/test_recall_cli.py` - 新增 5 个用例（query intent 双向、需求保全检查、锚点存在性）
- `logic_version/records/logic_version-20260816-002-traceability-repair.md` - 补录需求三字段（其 CHG 与归档同提交、正文未进 git 历史，属需求保全规则的立法依据；RULE-013 类既定例外）

**破坏性变更**：无。旧 6 列 INT 表仍被解析（锚点检查只在 7 列时启用）；
需求保全检查只覆盖 2026-08-16 之后的记录。

## 验证方式

`python -m unittest tests.test_recall_cli`（13 tests OK，含 query intent 解析规则/锚点/
记录、未知 INT 报错列表、需求保全警告与历史豁免、锚点悬空警告）；
`python -m unittest tests.test_git_sync`（17 OK）；`python tests/test_audit_logic_map.py`
（62 OK）；`python scripts/audit_logic_map.py . --current-state` 静态门；
`python scripts/validate.py`；实机 `recall query intent INT-20260816-005` 正确输出
规则正文、代码锚点存在性与相关记录。本记录自身即为需求保全实证：三字段自
CHG-20260816-002 原样搬入后 CHG 才被删除。

## 回滚方式

`git revert` 本次提交整体回退。只想停用反向查询：不使用 `recall query intent` 即可，
无状态残留；INT 表代码锚点列可保留（validate 对 6 列表自动跳过锚点检查）。

## 经验与教训

字段的生命周期必须走到不可变存储才算"被记录"：活在会被删除的工作文件（CHG）里
的信息等于没记。凡"归档后删除"的流程，删除前必须有明确的搬运清单。反向索引
（需求→代码）与正向索引（代码→需求）是两条独立链路，只建其一时另一方向的问题
会被"有追溯系统"的表象掩盖。

## 关联

- current_logic: logic_readme.md#RULE-014, RULE-015, RULE-016
- proposal_id: CHG-20260816-002（已归档移除）
- code/tests: scripts/link_ver_git.py; scripts/validate.py; references/project-onboarding.md; tests/test_recall_cli.py
