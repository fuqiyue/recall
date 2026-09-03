# VER-20260904-002: 文档优化——宪法索引收缩、contract_class 列、规则行子条款化、计数同源、route 降噪、recall audit、待立案入账

## 记录控制

- version_id: VER-20260904-002
- version_slug: logic_version-20260904-002-docs-consolidation
- status: effective
- date: 2026-09-04
- change_id: CHG-20260904-002
- before_commit: c3bdff7
- after_commit: _待填写_

## 为什么做这个决策？

**背景**：
VER-20260904-001 之后用户要求对 Recall 文档做一次整体审视。核查结果：① `recall status` 只在根文档正则数 RULE 引用（把"见 RULE-010/011/013"指针行也算进去），报 21，而 validate / conflicts 按定义行报 23——同一事实三个工具三个数，正是 RULE-012/021 要消灭的模式；② SKILL 第 12 行的"路由一问"依赖代码地图的 `contract_class` 列，但宪法、两份部门法、两份模板都没有这一列，消费项目照模板建文档后永远走不到一问路由；③ 宪法 249/250 行，距硬上限 1 行，其中"有效决策索引"18 行与 `logic_version/index.md` 逐条重复，文档控制 `source_decisions` 是第三份；④ 规则行膨胀成 1500–2350 字符的段落（RULE-018 塞了七八项义务），代理引用"RULE-018"无法指明哪一项，`why` 列在讲事故经过；⑤ `recall route 审计` 因 git-pipeline 的"不负责：审计/校验"行与表头"why（仅一句可审计摘要）"命中两域，读取成本 19.4k 而非 13.5k token；⑥ `records/README.md`"当前记录"表只列 2/18 条且第三次重述回档原则；INT last_verified 停在 8 月而其关联规则在 9 月改过；⑦ 三份账本全空，但"当前限制"里停着四个"待立案"——已生效制度文档在充当积压清单。

**用户需求/反馈**：
2026-09-04 会话："请你帮我分析，目前的 recall 文档还有什么需要改进的地方吗？"→ 分析报告后："认可，请你帮我进行优化"。

**需求拆解（归档时从 CHG 原样搬入）**：
- raw_request: 2026-09-04 用户会话——"请你帮我分析，目前的 recall 文档还有什么需要改进的地方吗？"→ 分析报告后用户回复"认可，请你帮我进行优化"
- decomposition: ① `recall status` 规则计数改为按定义行统计宪法 + 全部领域（与 validate/conflicts 同源）；② 代码地图加 `contract_class` 列（宪法、两领域、两模板），审计器接受该列并校验取值；③ 宪法有效决策索引收缩为指针 + 最近 3 条，生效 VER 改由规则行决策记录列直接链接，validate 对账口径随之调整；④ 规则行压缩：子条款编号、`why` 一句化、历史叙事回 VER；⑤ `recall route` 关键词匹配跳过"不负责"边界行；⑥ 新增 `recall audit` 子命令转发审计器；⑦ records/README 与 index.md 去重复述；INT last_verified 与 RULE-016 决策链接补齐；⑧ 两处"待立案"限制改为 draft CHG（CHG-20260904-003 toolchain、CHG-20260904-004 根）
- fit_analysis: 扩展 INT-20260816-006（status 计数同源）、INT-20260816-008（recall audit 成为真实入口）、INT-20260903-002（route 噪声）、INT-20260816-003（宪法体量）；FLOW-002/003 不变；不新增 UXI；RULE-002/015/018/021 文本更新

## 决策过程

**方案 A**：宪法索引收缩为指针 + 最近 3 条，生效 VER 的长期落点改为规则行"决策记录"列，validate 把"未登记宪法索引"改为"既不在宪法索引也没有任何规则行链接"才告警（优点：每任务固定读取少约 20 行 / 1.5k token，且反链本来就是 key 规则的义务；缺点：4 条此前没被任何规则行链接的 VER 需补链；复杂度：低）

**方案 B**：保留 18 行索引，只压缩 FLOW/UXI 争取行数（优点：不动工具；缺点：治标，下一次规则修订仍越线，重复信息继续烧 token；复杂度：低）

**方案 C**：规则行改为 `RULE-018.a` 式子编号（优点：可精确引用；缺点：validate / audit / conflicts / route 全部 `RULE-\d{3}` 正则要改、消费项目要迁移；复杂度：中）

**落选方案归档**：B、C 的需求原文同上方 raw_request。B 否决原因：把重复信息留在每任务必读的文档里与 RULE-002 单一真相源相悖。C 否决原因：收益不成比例，改为行内 ①②③ 子条款——引用时写"RULE-018 ③"即可精确到项，工具零改动。

**选中方案与原因**：
选 A + 行内子条款。关键取舍：(1) 计数同源写进 RULE-021 ③ 而不是另立规则——它和"根查找只此一份"是同一个原则（同一事实一种口径），并加子进程测试锁死三条命令报同一数；(2) `contract_class` 列做成**可选列**：审计器只在写了时校验取值，旧文档不报，避免消费项目一夜之间静态门全红；(3) route 排除"不负责"行与表头而不是改成语义匹配——两处都是"看起来像内容、其实是 schema 或别人职权"的确定性噪声，规则简单可测；(4) `why` 列只留一句，事故经过与量化叙事归 VER——规则行是每任务必读的，VER 是按需读的；(5) 待立案事项立成 draft CHG 而非继续留在"当前限制"：账本为空但限制里躺着四个"待立案"，说明积压在错误的地方；剩余 9 个超限函数则明确记为已接受存量，不再叫"待立案"。

## 影响范围

**修改的文件/模块**：
- `scripts/recall.py` - `count_rule_definitions`（定义行统计宪法 + 领域）；`cmd_audit` 转发审计器（默认 `--current-state`，profile 标志透传）；help 增 `audit`
- `scripts/route_docs.py` - `_keyword_searchable_text` 跳过"不负责"行与 Markdown 表头/分隔行
- `scripts/validate.py` - `rule_linked_versions`；`check_ver_registrations` 新增 `domain_readme_contents`，告警条件改为"既不在宪法索引也无规则行链接"
- `scripts/recall_audit/integrity.py` - 代码地图接受可选 `contract_class` 列（`CODE_MAP_OPTIONAL_HEADERS`），`_code_map_row_issues` 校验取值，根与领域共用
- `logic_readme.md` - RULE-002 加 ②③（索引收缩与反链）、RULE-014/018/020/022 子条款化并压缩 `why`、RULE-016/014/022 补 VER 链接；代码地图 `contract_class` 列；有效决策索引收缩为 3 行；INT-001/002/005/007 last_verified、INT-008 锚点；测试矩阵、兼容制度、当前限制、活跃议案入口；249 → 238 行
- `logic_domains/toolchain/logic_readme.md` - RULE-015/021/023 子条款化；RULE-015 ①、RULE-021 ③ 新语义；代码地图 `contract_class` 列与新函数锚点；当前限制改指向 CHG-20260904-003/004；活跃议案入口
- `logic_domains/git-pipeline/logic_readme.md` - 代码地图 `contract_class` 列；RULE-011 补链 VER-20260811-003
- `logic_domains/toolchain/logic_change.md`、`logic_change.md` - draft CHG-20260904-003（validate 兼容消费项目格式）、CHG-20260904-004（Density 硬上限与无领域是否进门）及公报行
- `references/logic-readme-template.md`、`logic-domain-template.md`、`document-model.md`、`change-lifecycle.md`、`logic-version-template.md`、`project-onboarding.md` - `contract_class` 列与取值说明；有效决策索引模板改为与实际 schema 一致的 4 列 + 指针（修正了模板 6 列 vs 实际 4 列的漂移）；步骤 8 补"挤出前确认已被规则行链接"
- `logic_version/index.md`、`logic_version/records/README.md` - 记录创建规则改为指向 SKILL 通道表；records/README 去掉 2/18 的陈旧清单与第三份回档原则
- `SKILL.md`、`README.md` - 命令块改用 `recall audit`
- `tests/` - `StatusRuleCountTests`、route 边界行/表头排除、`audit` 子进程冒烟、三命令计数一致、validate 规则行反链（含领域与"正文提及不算"）、审计器 `contract_class` 接受/拒绝用例

**破坏性变更**：无 CLI 命令名或退出码变化。validate 口径**放宽**：以前每条生效 VER 必须进宪法索引，现在被任一规则行链接即可；`audit --json` 输出对无 `contract_class` 列的项目不变。消费项目若照旧把全部 VER 列在宪法索引，不报错。

## 验证方式

- `python -m unittest discover -s tests` → Ran 216 tests OK（此前 205）
- `recall audit` → Static gate PASS；Density 仅 `logic_readme.md:over-target:238>150`（advisory）
- `recall validate` → 无错误；仅本次未提交/未回填的预期告警
- `recall status` / `validate` / `conflicts` → 规则数均为 23
- `recall route 审计` → 只命中 MOD-TOOLCHAIN（468 行 ≈ 17.2k token，此前两域 598 行 ≈ 20.4k）；`route scripts/git_sync.py` 只命中 MOD-GIT-PIPELINE
- 代码差异：`git show <after_commit>`

## 回滚方式

`git revert <after_commit>`。回滚后 `contract_class` 列变为审计器不认识的列 → `code-map-invalid-columns`，需同时去掉列；validate 会重新要求全部 VER 进宪法索引。

## 经验与教训

- "各工具各算一套"不只发生在 VER 命名（RULE-012）：任何被多个命令报出的事实都要有唯一口径 + 一条断言三者相等的测试，否则同一仓库会同时报 21 和 23 而 CI 全绿。
- 路由问题依赖的字段必须出现在模板里，否则规则只在 SKILL 里"存在"：本仓库自己也没有 `contract_class` 列，说明写规则时没有回头检查模板是否给了落点。
- 关键词路由的噪声来源是确定性的（边界声明、表头），先排除这些再谈语义匹配；改成语义匹配的收益远低于把两类 schema 行剔掉。
- 规则行的"一行一条"不等于"一段一条"：行内 ①②③ 子条款让引用能精确到项，且不动任何正则。
- "当前限制"不是积压清单：写着"待立案"却不立案，等于把议案藏在生效文档里绕过账本。

## 兼容、迁移与回滚

- compatibility: 向后兼容；缺 `contract_class` 列的项目不报，validate 口径放宽
- migration: 存量项目按需给代码地图补 `contract_class` 列；宪法索引可收缩到最近 3 条，收缩前确认被挤出的 VER 已被某条规则行链接（`recall validate` 会指出未被引用者）
- rollback: git revert（见上）
- logic_temp_cleanup: logic_version/working/logic_version-20260904-002-docs-consolidation/ 于 2026-09-04 删除；台账 2 项（keep 1：本记录；delete 1：working 目录）全部处置

## 关联

- current_logic: logic_readme.md#RULE-002（索引收缩与反链）、RULE-018 ③（route 排除项）、RULE-022 ④（子条款化）；logic_domains/toolchain/logic_readme.md#RULE-015 ①（validate 口径）、RULE-021 ③（计数同源）
- proposal_id: CHG-20260904-002（本记录创建后关闭）；派生 draft：CHG-20260904-003、CHG-20260904-004
- intent_traceability: INT-20260816-006 -> RULE-021 -> test:tests/test_recall_cli.py -> VER-20260904-002; INT-20260816-008 -> RULE-015 -> test:tests/test_validate.py -> VER-20260904-002; INT-20260903-002 -> RULE-018 -> test:tests/test_recall_cli.py -> VER-20260904-002; INT-20260816-003 -> RULE-002 -> test:tests/test_validate.py -> VER-20260904-002
- code/tests: scripts/recall.py; scripts/route_docs.py; scripts/validate.py; scripts/recall_audit/integrity.py; tests/
