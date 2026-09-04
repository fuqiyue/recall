# VER-20260904-004: 审计器兼容消费项目写法——链接可达性剔除代码段、空账本 active_changes 接受 0、坏链前缀、模板状态枚举补 promoting

## 记录控制

- version_id: VER-20260904-004
- version_slug: logic_version-20260904-004-audit-link-ledger-compat
- status: effective
- date: 2026-09-04
- change_id: CHG-20260904-005
- before_commit: 8155079
- after_commit: ea58c33

## 为什么做这个决策？

**背景**：
VER-20260904-003 之后用户继续在消费项目跑 `recall audit`，又被迫两次改文档措辞去迎合审计器：① 规则正文里示意性的 `[ID](path)`（说明 index.md 首列接受链接形态）被 `audit_links` 当作真实链接、报坏链，用户改写成"指向记录的 Markdown 链接"；② 空账本 `active_changes: 0` 被报 `count-mismatch:0!=none`，且连带误报 `active-change-missing-effective-marker`（semantic 层只认字面 `none`），用户改成 `none`。两处都是"文档写法正确、工具识别过窄"，与 VER-20260904-003 修的占位符误判同类：`contains_angle_placeholder` 已经知道"反引号里的不是占位符"，链接检查却仍对原文直接抓 `[文本](目标)`。本仓库复现（拷贝文档到 scratchpad、加一处反引号链接与一处 `0`）：静态门 FAIL 三条，且领域文档的坏链条目只报 `logic_domains/toolchain:logic_readme:path`，看不出是链接问题。顺带核查发现：`references/logic-change-template.md` 两处"允许状态"缺 `promoting`（`CHANGE_STATUSES`、change-lifecycle、field-vocabulary、document-model 与本仓库账本都有），`recall-brief-template.md` 同；CONTRIBUTING 仍教 `VER-YYYYMMDD-HHMM` 旧命名；pr-checks 的 docs_impact 提示与 labeler 没把 `logic_domains/` 当 logic 文档；validate.yml 逐个点名测试模块，新增测试文件会被静默漏跑。

**用户需求/反馈**：
2026-09-04 会话："审计器发现问题时我改过两次文档措辞：规则文本里写 `[ID](path)` 会被当作真实链接检查，改成了'指向记录的 Markdown 链接'。空账本的 active_changes 要写 none 而不是 0，与 git-pipeline 账本一致。认可，保留相对路径吧，请你继续分析目前的 recall skill 是否还有问题呢？请继续优化"。

**需求拆解（归档时从 CHG 原样搬入）**：
- raw_request: 2026-09-04 用户会话："审计器发现问题时我改过两次文档措辞：规则文本里写 `[ID](path)` 会被当作真实链接检查，改成了'指向记录的 Markdown 链接'。空账本的 active_changes 要写 none 而不是 0……请你继续分析目前的 recall skill 是否还有问题呢？请继续优化"
- decomposition: ① `audit_links` 先剔除围栏代码块与行内代码段再抓 `[文本](目标)`，链接标题 `"title"` 不算路径；② 空账本 `active_changes` 接受 `none` 与 `0` 同义（semantic 一处、integrity 两处收敛为一个判定）；③ 领域文档坏链条目加 `broken-link:` 前缀（此前只报 `logic_readme:path`）；④ 模板允许状态补 `promoting`（logic-change-template 两处、recall-brief-template），与 `CHANGE_STATUSES`/生命周期文档一致；⑤ CI/labeler/CONTRIBUTING 引用的旧路径与旧记录命名修正；⑥ 用例：代码段内链接不报坏链、裸坏链仍报、`active_changes: 0` 空账本通过、`0` 配正文仍报不匹配
- fit_analysis: 复用 INT-20260816-008（validate / audit 审计门）；FLOW-003#3 不变；不新增 UXI；RULE-021 ③ 文本加"链接可达性只查代码段之外"与"空账本计数 none/0 同义"

## 决策过程

**方案 A**：在 textutil 增加 `strip_code_segments`（围栏 `FENCED_CODE_RE` + 行内 `CODE_SPAN_RE`）供 `audit_links` 先剔除；增加 `is_empty_ledger_count`，semantic 与 integrity 三处判定都走它；领域坏链加前缀；模板与 CI 顺带修正（优点：与 VER-20260904-003 同一原则"只放宽识别不放宽语义"，代码段不算占位符与代码段不算链接共用同一正则；缺点：`audit_logic_map.py` facade 需再导出四个名字；复杂度：低）

**方案 B**：只在文档侧规定"规则正文不得出现 `[…](…)` 示例、空账本必须写 none"，工具不动（优点：零代码；缺点：这是把工具缺陷写成用户义务，用户已经被迫改了两次，且 `0` 是该字段最诚实的写法；复杂度：低）

**方案 C**：链接检查改成只查表格"决策记录"列与登记表链接列，正文一律不查（优点：彻底避免误报；缺点：正文里指向 references/、领域文档的真实链接失去可达性核查，坏链会静默；复杂度：中）

**落选方案归档**：B、C 的需求原文同上方 raw_request。B 否决原因：用户原话就是"被迫改文档迎合审计器"，再加一条书写禁令是反向解决。C 否决原因：放宽语义而非放宽识别，正文坏链是消费项目真实出现过的问题（eduai 迁移后相对路径失效）。

**选中方案与原因**：
选 A。关键取舍：(1) 代码段的定义只有一处——`CODE_SPAN_RE` 已被占位符判定使用，链接判定复用它而不是再写一份，`FENCED_CODE_RE` 同放 constants；(2) `0` 与 `none` 同义只在"无正文"时成立——有正文时写 `0` 仍报 `0!=N`，模板继续以 `none` 为规范写法、只注明 `0` 同义，不引入第三种形态；(3) 坏链条目加前缀而不改结构——JSON 的 `broken_links` 键与 `document_issues` 归类不变，只是条目文本从 `logic_readme:path` 变成 `logic_readme:broken-link:path`，让用户按提示能定位到"这是链接"；(4) CI 测试改为 `unittest discover` 是为堵"新测试文件不进 CI"的漏洞，与本仓库 SKILL/宪法写的验证命令一致。

## 影响范围

**修改的文件/模块**：
- `scripts/recall_audit/constants.py` - `FENCED_CODE_RE`、`EMPTY_LEDGER_COUNT_VALUES`
- `scripts/recall_audit/textutil.py` - `strip_code_segments`、`is_empty_ledger_count`；`audit_links` 先剔除代码段；`normalize_link_target` 去掉链接标题
- `scripts/recall_audit/semantic.py` - `active-change-missing-effective-marker` 用 `is_empty_ledger_count`；模块文档坏链条目加 `broken-link:` 前缀
- `scripts/recall_audit/integrity.py` - `_ledger_count_matches` 统一根/领域账本 `active_changes` 判定
- `scripts/audit_logic_map.py` - facade 再导出 `audit_links`、`strip_code_segments`、`is_empty_ledger_count`、`normalize_link_target`、`CODE_SPAN_RE`、`FENCED_CODE_RE`、`EMPTY_LEDGER_COUNT_VALUES`
- `references/logic-change-template.md`、`references/logic-domain-template.md`、`references/recall-brief-template.md` - 状态枚举补 `promoting`；`active_changes` 注明 `0` 同义
- `CONTRIBUTING.md` - Ref 行改为 RULE-012 命名；测试步骤加 `recall audit` 与 `unittest discover`
- `.github/workflows/pr-checks.yml`、`.github/workflows/validate.yml`、`.github/labeler.yml` - docs_impact 提示与标签纳入 `logic_domains/`；测试步骤改 `unittest discover`；`scripts/cli.py` 改 `scripts/recall.py`
- `logic_domains/toolchain/logic_readme.md` - RULE-021 ③ 文本、代码地图 recall_audit 行、测试矩阵、"当前限制"、source_decisions
- `logic_readme.md`、`logic_version/index.md` - 有效决策索引轮换（最近 3 条：002/003/004，VER-20260904-001 由 RULE-014/015/018/023 规则行链接）、source_decisions、索引登记
- `logic_domains/toolchain/logic_change.md`、`logic_change.md` - 关闭 CHG-20260904-005（正文与公报行删除，三字段搬入本记录）
- `tests/test_audit_logic_map.py` - `CodeSegmentLinkTests`、`DomainRuleTextLinkTests`、`EmptyLedgerCountTests`；夹具方法抽为 `ProjectFixtureMixin`，派生用例类不再重复执行整套 `RootOnlyAuditTests`

**破坏性变更**：无。全部为识别放宽：以前 PASS 的文档仍 PASS；此前因代码段内链接或 `active_changes: 0` FAIL 的消费项目转为 PASS 或只剩真实问题。领域文档坏链条目文本多出 `broken-link:` 段（此前无前缀），依赖该条目文本精确匹配的外部脚本需相应调整；本仓库与已知消费者无此依赖。

## 验证方式

- `python -m unittest discover -s tests` → Ran 248 tests OK（此前报 323：其中 85 个是 `DomainRuleTextPlaceholderTests` 继承 `RootOnlyAuditTests` 造成的整套重复执行；本次把夹具方法抽成 `ProjectFixtureMixin`，248 是真实用例数，含新增 7 个）
- `recall audit` → Static gate PASS（含本次 CHG 正文里的 `` `[ID](path)` ``；改回裸写立即报 `broken-link:path`）
- `recall validate` → 无错误；`recall status` / `validate` / `conflicts` 规则数均为 23
- scratchpad 复现夹具：反引号链接不再报坏链；`active_changes: 0` 空账本无 `count-mismatch` 与 `missing-effective-marker`
- 代码差异：`git show <after_commit>`

## 回滚方式

`git revert <after_commit>`。回滚后消费项目规则正文里的反引号链接示例与 `active_changes: 0` 会重新报错；本仓库自身文档不受影响（账本写 `none`，规则文本已无裸链接示例）。

## 经验与教训

- 同一"代码段不算"的判断在占位符检查修过一次（VER-20260904-003），链接检查里还留着第二份未修的原文扫描——修一处误判时应搜索同一输入（Markdown 原文）的全部消费者，而不是只修报出来的那条。
- 用户为通过机器门而改措辞，是工具缺陷最可靠的信号：措辞本身正确却要迁就检查器，就该修检查器。
- 领域文档的问题条目缺少类别前缀（`logic_readme:path`）让用户无从判断是链接、字段还是章节问题；条目文本应先说"什么类别"再说"哪个值"。

## 兼容、迁移与回滚

- compatibility: 向后兼容；只放宽识别、不改规则语义与退出码；领域坏链条目文本新增 `broken-link:` 段
- migration: 消费项目无需迁移；此前为绕过误报改写的措辞与 `none` 可保留也可改回
- rollback: git revert（见上）
- logic_temp_cleanup: logic_version/working/logic_version-20260904-004-audit-link-ledger-compat/ 于 2026-09-04 删除；台账 4 项（keep 2：本记录、新增测试；delete 2：working 目录、scratchpad 复现夹具）全部处置

## 关联

- current_logic: logic_domains/toolchain/logic_readme.md#RULE-021 ③（代码段不算占位符/链接、空账本 none/0 同义）
- proposal_id: CHG-20260904-005（本记录创建后关闭）
- intent_traceability: INT-20260816-008 -> RULE-021 -> test:tests/test_audit_logic_map.py#CodeSegmentLinkTests -> VER-20260904-004; INT-20260816-008 -> RULE-021 -> test:tests/test_audit_logic_map.py#EmptyLedgerCountTests -> VER-20260904-004
- code/tests: scripts/recall_audit/constants.py; scripts/recall_audit/textutil.py; scripts/recall_audit/semantic.py; scripts/recall_audit/integrity.py; scripts/audit_logic_map.py; tests/test_audit_logic_map.py
