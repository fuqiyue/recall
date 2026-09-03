# VER-20260904-001: 一法多议案冲突与基线失效检查、意图层来源列（用户表述即宪法）、按意图路由

## 记录控制

- version_id: VER-20260904-001
- version_slug: logic_version-20260904-001-intent-provenance-conflicts
- status: effective
- date: 2026-09-04
- change_id: CHG-20260904-001
- before_commit: a2886b5
- after_commit: 9e58c59

## 为什么做这个决策？

**背景**：
VER-20260903-004 建立了宪法/部门法两级模型后，用户追问三个问题：一法多议案（尤其旧议案与新议案冲突）是否已考虑；按需使用法律是否做到；"用户的思路就是宪法"是否落实。核查结果：① 冲突机制（`authority_surfaces` 重叠、互指 `conflicts_with`、`conflict_resolution`、`based_on`）存在，但 RULE-023 使这些字段在 personal 模式可省，默认形态下检测形同虚设；重叠比对只在单个账本内进行，领域账本更是逐块调用协调检查、从未比对；没有任何"规则在议案之后被修订"的检查，旧议案会带着失效基线生效。② `recall route` 只按路径/关键词路由，不认用户意图。③ 功能意图登记表没有来源列，RULE-016 的 `code-derived` 标记无处落地，用户原话与 AI 推断在宪法里无法区分。

**用户需求/反馈**：
2026-09-04 会话："对于一个法律有多个议案，甚至旧议案和新议案有冲突，目前是否有考虑到？按需使用法律是否做到？用户的说法对工具非常重要，用户的思路就是宪法，目前有没有完善？以用户的思路来构建项目。"

**需求拆解（归档时从 CHG 原样搬入）**：
- raw_request: 2026-09-04 用户会话——"对于一个法律有多个议案，甚至旧议案和新议案有冲突，目前是否有考虑到？按需使用法律是否做到？用户的说法对工具非常重要，用户的思路就是宪法，目前有没有完善？以用户的思路来构建项目"
- decomposition: ① 一法多议案：目标规则从 `authority_surfaces` 提取，跨全部账本（根 + 领域）比对，同一 RULE 被多个活跃 CHG 指向而未互指 `conflicts_with` → 报 `shared-rule-target-needs-explicit-conflict`，不随治理模式分档；拟议制度提到 RULE 但未写 authority_surfaces → 报 `mentions-rule-without-authority-surfaces`；② 旧议案 vs 新法：目标规则的 `last_reviewed` 晚于 CHG 的 `created`/`last_status_change` → 报 `rule-changed-after-proposal`，要求重核 based_on；修正领域账本此前逐块调用协调检查、从不比对的缺陷；③ `recall conflicts` 输出"一法多议案"与"基线失效"两节，跨账本；④ 意图层来源列：功能意图登记表新增 `来源`（`user:日期` / `user-confirmed:日期` / `code-derived` / `inferred`），validate 对非用户来源告警、缺列提示；⑤ `recall route` 支持 INT-ID 与命中宪法意图行的关键词，经代码锚点/关联规则路由到领域，并展示命中的用户意图；⑥ SKILL 原则：用户新表述先落宪法意图层再做领域工作，AI 推断不得冒充用户确认
- fit_analysis: 扩展 INT-20260816-001（意图层：加来源列）、INT-20260816-009（conflicts：跨账本 + 基线失效）、INT-20260903-002（route：按意图）、INT-20260816-008（audit/validate：新检查）；FLOW-004#1 不变；不新增 UXI；RULE-014/018 文本更新，toolchain RULE-015/023 文本更新

## 决策过程

**方案 A**：目标规则只从 `authority_surfaces` 提取；缺失时对拟议制度里提到的 RULE 给提示（优点：判定确定、零误报，personal 只多写一行；缺点：不写 authority_surfaces 的议案对冲突检测不可见，只能靠提示推动；复杂度：低）

**方案 B**：从 CHG 全文抓取 RULE 引用作为目标（优点：无需新字段；缺点："见 RULE-019"式顺带引用大量误报，检测失去可信度；复杂度：低）

**方案 C**：基线失效比对规则正文哈希而非日期（优点：能发现未更新 last_reviewed 的改动；缺点：要在 CHG 增加哈希字段并在每次规则改动时维护；复杂度：中）

**落选方案归档**：B、C 的需求原文同上方 raw_request；B 否决原因是误报会让代理忽略整类提示；C 否决原因是收益不成比例，`last_reviewed` 本就是规则行必填且 validate 校验的字段，改规则不更新日期本身就是违规。

**选中方案与原因**：
选 A + 日期比对。关键取舍：(1) 一法多议案检查**不按治理模式分档**——冲突是否存在与项目规模无关，personal 的代价只是 `authority_surfaces: RULE-xxx` 一行；(2) 跨账本比对只报不同账本的重叠，同账本仍由既有 `unmarked-authority-surface-overlap` 报告，避免双报；(3) 修正领域账本协调检查逐块调用的缺陷，改为整本账本一次调用；(4) 意图层来源列插在 `last_verified` 之前，`recall query intent` 按索引读第 6 列锚点不受影响，旧项目缺列只得到 info 提示而非错误；(5) route 按意图路由走"意图行 → 代码锚点 / 关联规则 → 领域"两条链，命中的用户意图连同来源一并展示，非用户来源附警示。

## 影响范围

**修改的文件/模块**：
- `scripts/recall_audit/changes.py` - 新增 `cross_ledger_rule_conflicts`（目标规则提取、跨账本重叠、基线失效、无 authority_surfaces 提示）；`change_coordination_issues` 拆出 `_coordination_entries` 并新增 `other_ledgers` 参数，跨账本环只由持最小 CHG-ID 的账本报一次
- `scripts/recall_audit/integrity.py` - 收集各账本 CHG 块与全部规则行 `last_reviewed`；协调检查改为 `_check_ledger_coordination` 在全部账本收集完后整本调用，并把其余账本的块作为 `other_ledgers` 传入，使 `depends_on`/`conflicts_with`/`blocked_by` 跨账本解析（测试代理发现：否则互写 conflicts_with 的规定解法自己会被打成 `conflict-target-not-active`，门永远过不去）；`_check_domain_documents` 末尾调用跨账本规则冲突检查
- `scripts/audit_logic_map.py` - facade 导出 `cross_ledger_rule_conflicts`
- `scripts/validate.py` - `check_intent_layer` 识别 `来源` 列：缺列 info、`inferred`/`code-derived`/空值 warning、格式不识别 warning
- `scripts/detect_conflicts.py` - `extract_rule_dates`、`check_multi_proposal_conflicts`、`check_stale_baselines`；报告新增两节，命中时退出码 2
- `scripts/route_docs.py` - `constitution_intents`、`match_intents`；`match_domains` 增加意图链路由；输出"命中的用户意图"
- `logic_readme.md` - 意图登记表加 `来源` 列并逐行标注；RULE-014/018 文本；意图层导语；当前限制；VER 索引
- `logic_domains/toolchain/logic_readme.md` - RULE-015/023 文本、代码地图行、当前限制
- `references/logic-readme-template.md`、`references/logic-change-template.md`、`references/project-onboarding.md`、`SKILL.md` - 来源列、authority_surfaces 义务、用户表述即宪法的工作顺序
- `tests/` - 跨账本冲突、基线失效、领域账本整本协调、来源列、按意图路由、conflicts 新函数用例

**破坏性变更**：审计口径收紧（有意为之）：`rule-changed-after-proposal`、`shared-rule-target-needs-explicit-conflict`、`mentions-rule-without-authority-surfaces` 进入 current-state 门。消费项目 eduai 只读复跑由 PASS 变 FAIL——3 条议案（CHG-20260820-LEVEL-D-PLATFORM-CAPABILITY-BRIDGE、CHG-20260820-STUDIO-UPLOAD-PROJECT、CHG-20260821-UNTRUSTED-CONTENT-ISOLATION）的目标规则 RULE-013/RULE-016 在 2026-09-02/03 修订、晚于议案 2026-09-01，基线需重核；CHG-20260811-UNIFIED-CLIENT-DATA 拟议 7 条 RULE 却无 authority_surfaces。这些是真实的一法多议案/基线失效问题，不是误报，故不降为 advisory。旧项目 INT 表缺来源列只得到 info；CLI 命令名与退出码语义不变（`recall conflicts` 原本命中即 2）。

## 验证方式

- `python -m unittest discover -s tests` 全部 OK（新增用例见 tests/test_audit_logic_map.py、tests/test_validate.py、tests/test_recall_cli.py）
- `python scripts/audit_logic_map.py . --current-state` → Static gate PASS
- `python scripts/validate.py` → 无错误；意图登记表来源列无告警
- `python scripts/recall.py route INT-20260816-005` → 命中 MOD-GIT-PIPELINE，展示用户意图与来源
- `python scripts/recall.py conflicts` → 输出"一法多议案 / 基线失效"节
- eduai 只读复跑：退出码 1（Static gate FAIL），5 条新 proposal_issues 全部为真实的基线失效/未声明目标规则
- 代码差异：`git show <after_commit>`

## 回滚方式

`git revert <after_commit>`。纯脚本 + 文档；回滚后来源列变为多余列（validate 不识别但不报错）。

## 经验与教训

- 分档的边界要按"检查的性质"而不是"字段的层级"划：冲突检测是安全网，不该随 personal 一起被省掉；正确做法是把它的输入压到一行字段。
- 逐块调用的检查会静默丢掉所有成对关系；对账本级不变量必须整本一次调用，测试要用两个块而不是一个。账本拆分后，凡是"目标必须活跃"的检查都要问一句：目标允许在别的账本吗？允许就必须跨账本解析，否则规定解法自己过不了门——这条是让测试代理按规定解法写通过用例时发现的。
- "用户的思路就是宪法"要机器可见：没有来源列时，用户原话和 AI 推断在真源里长得一样，RULE-016 的确认义务无处落地。

## 兼容、迁移与回滚

- compatibility: 向后兼容；缺来源列的项目只收 info
- migration: 存量项目在意图登记表加 `来源` 列，逐行按真实来源标注；未确认的先标 `inferred`
- rollback: git revert
- logic_temp_cleanup: logic_version/working/logic_version-20260904-001-intent-provenance-conflicts/ 于 2026-09-04 删除；台账 2 项（keep 1：本记录；delete 1：working 目录）全部处置

## 关联

- current_logic: logic_readme.md#RULE-014（来源列）、RULE-018（按意图路由）；logic_domains/toolchain/logic_readme.md#RULE-015（validate/conflicts 新检查）、RULE-023（一法多议案不分档）
- proposal_id: CHG-20260904-001（本记录创建后关闭）
- intent_traceability: INT-20260816-001 -> RULE-014 -> test:tests/test_validate.py -> VER-20260904-001; INT-20260816-009 -> RULE-015 -> test:tests/test_recall_cli.py -> VER-20260904-001; INT-20260903-002 -> RULE-018 -> test:tests/test_recall_cli.py -> VER-20260904-001; INT-20260816-008 -> RULE-023 -> test:tests/test_audit_logic_map.py -> VER-20260904-001
- code/tests: scripts/recall_audit/changes.py; scripts/recall_audit/integrity.py; scripts/validate.py; scripts/detect_conflicts.py; scripts/route_docs.py; tests/
