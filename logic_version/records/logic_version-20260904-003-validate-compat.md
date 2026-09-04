# VER-20260904-003: validate/审计器兼容消费项目格式——双模板必填段、链接型 VER 首列、锚点符号剥离、CHG-ID 单一正则、占位符判定收窄

## 记录控制

- version_id: VER-20260904-003
- version_slug: logic_version-20260904-003-validate-compat
- status: effective
- date: 2026-09-04
- change_id: CHG-20260904-003
- before_commit: 9bcb65d
- after_commit: 44bff34

## 为什么做这个决策？

**背景**：
2026-09-03 在消费项目 eduai 只读复跑 `recall validate` / `recall audit`，暴露出 Recall 自身工具链的五个识别缺口，全部在本仓库不可见（本仓库只 dogfood 最小模板与裸路径锚点）：① `check_required_fields` 只认快速模板的四个正文标题，`references/logic-version-template.md` 自带的扩展 schema（变更摘要 / 影响与消费者 / 兼容、迁移与回滚 / 测试与审核）被当作缺失，46 份记录全报"缺少必填字段"，validate 常年 FAIL；② `VER_ROW_RE` 只认 `| VER-… |` 裸 ID，index.md 首列写成 `[VER-…](path)` 时每条记录被报"未登记"，失败方式指向症状而非格式；③ 代码锚点检查拿 `scripts/x.py#symbol` 整串去 `exists()`，6 个正确的符号锚点报"不存在"；④ current-state 门用 `"<" in value or ">" in value` 判占位符，规则正文里的 `>128`、`<meta>` 被当作模板占位符，三处内联谓词与 textutil 已有的 `contains_angle_placeholder` 并存；⑤ CHG-ID 正则四处三套（validate `\d{3}`、detect_conflicts `\d+`、审计器 slug），slug 型议案的三字段检查在 validate 静默跳过。另有 `is_valid_git_commit` 漏传 `cwd=root`，skill 集中安装后从项目外目录运行会查错仓库。

**用户需求/反馈**：
2026-09-04 会话："请问目前的 recall skill，是否有以下 bug 呢？……前两条我没动文档去迎合，第 3 条无损绕不过去。要我去 recall 源码仓修就说一声。请帮我分析，并告诉我还有哪些地方可以优化" → 分析报告后："认可，请帮我继续处理。仅优化目前的 recall skill 就可以"。

**需求拆解（归档时从 CHG 原样搬入）**：
- raw_request: 2026-09-03 eduai 只读复跑：validate 的 CHG 发现只认 `CHG-YYYYMMDD-NNN`，消费项目 slug 型编号（`CHG-YYYYMMDD-UNIFIED-CLIENT-DATA` 一类）的三字段检查静默跳过；VER 必填段与 after_commit 正则只认最小模板与裸 SHA，扩展模板得到假错误。2026-09-04 用户认可"待立案事项立成 draft CHG"；同日用户报告四条 bug（双模板必填段、链接型 VER 首列、锚点 `#symbol`、`>128`/`<meta>` 被当占位符）并确认"认可，请帮我继续处理。仅优化目前的 recall skill 就可以"
- decomposition: ① validate 的 CHG-ID 正则与审计器 / `recall status` 共用一份（RULE-012/021 同一正则原则）；② VER 必填段识别 logic-version-template 的扩展 schema；③ after_commit 接受反引号包裹与 `commit:` 前缀；④ 用例：slug 型 CHG 缺三字段被报出、扩展模板记录无假错误；⑤ index.md 首列接受 `[VER-…](path)` 与反引号，首列格式不识别单独提示；⑥ 代码锚点剥离 `#symbol` / `:line` 后查路径，符号在文件中找不到单独告警；⑦ `is_valid_git_commit` 传 `cwd=root`；⑧ 审计器三处内联 `<`/`>` 谓词统一为 textutil `contains_angle_placeholder`，且先剔除行内代码段
- fit_analysis: 复用 INT-20260816-008（validate / audit 审计门）；FLOW-003#3 不变；不新增 UXI；RULE-015 ①②③ 与 RULE-021 ①③ 文本更新

## 决策过程

**方案 A**：CHG-ID 正则搬入 `recall_common` 统一导出（`CHANGE_ID_PATTERN` / `CHANGE_ID_RE`），validate / detect_conflicts / 审计器 constants 全部从它构造；VER 必填段按"两套 schema 任一满足"判定；锚点拆 (路径, 符号)；占位符判定只走 textutil 一份并剔除代码段（优点：每类事实一份实现，符合 RULE-021；缺点：审计器 constants 需 import recall_common——包 `__init__` 已把 scripts/ 加入 sys.path，archive/cli 早已这样做；复杂度：低）

**方案 B**：只在 validate 内放宽各正则，审计器不动（优点：改动最小；缺点：CHG-ID 出现第四份实现，`<`/`>` 谓词继续与 `contains_angle_placeholder` 并存，违反 RULE-021 ③；复杂度：低）

**方案 C**：VER 必填段按记录里的 `governance_mode` 字段选 schema（优点：语义明确；缺点：本仓库自己的记录就有快速模板 + 额外"兼容、迁移与回滚"节的混写，字段缺失时无从判定，且模板本身没规定 governance_mode 必填；复杂度：中）

**落选方案归档**：B、C 的需求原文同上方 raw_request。B 否决原因：再造第二份实现，正是 RULE-021 要消灭的模式。C 否决原因：混写记录与缺字段记录都会误判；"任一 schema 满足即通过、都不满足按缺失最少的一套报并注明 schema 名"对混写更稳，且不依赖任何额外字段。

**选中方案与原因**：
选 A。关键取舍：(1) 放宽识别不放宽语义——所有改动都是"把此前被误拒的正确写法认出来"，没有任何规则文本被削弱，报错信息反而更精确（"首列格式不识别"替代"未登记"、"找不到符号 X"替代"锚点不存在"）；(2) 符号锚点只做子串核查不做语法解析——成本一次 `read_text`，足以抓住改名，语法解析的收益不成比例；(3) 占位符判定剔除行内代码段而不是白名单 `<meta>` 之类——规则是"反引号里的不是占位符"，可测且不随词表膨胀；裸写的 `<meta>` 仍按占位符处理，写规则时应加反引号；(4) `CHANGE_ID_PATTERN` 采用审计器的宽形态（日期段后允许 slug），本仓库的 `NNN` 是其子集，不需要迁移。

## 影响范围

**修改的文件/模块**：
- `scripts/recall_common.py` - 新增 `CHANGE_ID_PATTERN` / `CHANGE_ID_RE`（RULE-021 ③ 议案编号只此一份）
- `scripts/validate.py` - `check_required_fields` 双 schema（`RECORD_CONTROL_FIELDS` + `RECORD_SCHEMAS`，接受已读内容）；`VER_ROW_RE` 接受链接与反引号、新增 `VER_FIRST_CELL_RE` 报首列格式；`split_code_anchor` / `anchor_symbol_present`；`extract_commit_hash` 接受 `commit:` 前缀；`is_valid_git_commit(cwd=root)`；`extract_chg_ids` / `check_chg_analysis_fields` 用共享正则；每份记录只读一次
- `scripts/detect_conflicts.py` - `extract_changes` 用共享正则（slug 型 CHG 可被冲突检测看见）
- `scripts/recall_audit/constants.py` - `CHANGE_HEADING_RE` / `DEPENDENCY_REFERENCE_RE` 由 `CHANGE_ID_PATTERN` 构造；新增 `CODE_SPAN_RE`
- `scripts/recall_audit/textutil.py` - `normalize_change_id` 用 `CHANGE_ID_RE`；`contains_angle_placeholder` 先剔除行内代码段
- `scripts/recall_audit/integrity.py` - 根/领域"当前制度"与代码地图三处内联 `<`/`>` 谓词改为 `contains_angle_placeholder`
- `logic_domains/toolchain/logic_readme.md` - RULE-015 ①②③、RULE-021 ①③ 文本；代码地图三行锚点；测试矩阵；"当前限制"去掉已修复的兼容缺口、补锚点/after_commit 边界；活跃议案入口
- `logic_domains/toolchain/logic_change.md`、`logic_change.md` - 关闭 CHG-20260904-003（正文与公报行删除，三字段搬入本记录）
- `logic_readme.md`、`logic_version/index.md` - 有效决策索引轮换（最近 3 条）、source_decisions、索引登记
- `tests/` - `RecordSchemaTests`、`CommitHashTests`、`VerRowFormatTests`、`CodeAnchorTests`、`SlugChangeIdTests`（test_validate）；`PlaceholderDetectionTests`、`DomainRuleTextPlaceholderTests`（test_audit_logic_map）；`ChangeIdSingleSourceTests`（test_recall_cli）

**破坏性变更**：无。全部为识别放宽：以前 PASS 的文档仍 PASS；以前因假错误 FAIL 的消费项目会转为 PASS 或只剩真实问题。新增两类告警（index.md 首列格式不识别、锚点符号找不到）均为 warning，不改退出码语义。审计器 `--json` 对不含 `>`/`<`/反引号尖括号的文档输出不变。

## 验证方式

- `python -m unittest discover -s tests` → Ran 323 tests OK（此前 216）
- `recall validate` → 无错误（本仓库 19 条记录、23 条规则、13 INT 全部通过）
- `recall audit` → Static gate PASS；Density advisory 不变
- `recall status` / `validate` / `conflicts` → 规则数均为 23
- 新用例覆盖消费项目形态：扩展 schema 记录零缺失、`[VER-…](path)` 首列被识别、`src/app.py#main` 无告警而 `#renamed` 报符号、`>128` + `` `<meta>` `` 规则行通过静态门而 `<fill in>` 仍拒绝、slug 型 medium CHG 缺三字段被报出、三处消费者共用同一 `CHANGE_ID_PATTERN` 对象
- 代码差异：`git show <after_commit>`

## 回滚方式

`git revert <after_commit>`。回滚后消费项目的扩展 schema 记录、链接型 index 首列、符号锚点与含 `>`/`<` 的规则行会重新报假错误；本仓库自身不受影响。

## 经验与教训

- 校验器的夹具只覆盖自己仓库的写法时，模板允许的其他写法就是盲区：模板给了两套 schema、代码只认一套，RULE-009"以模板为准"在字面上成立、在行为上失效。夹具必须覆盖模板允许的全部形态，而不是仓库正在用的那一种。
- 报错要指向原因而非症状："未登记"和"缺少必填字段"都是解析不匹配的下游表现，用户按提示改文档只会越改越偏（eduai 用 HTML 实体绕过就是例子）。
- 同一谓词在一个包里出现三份内联拷贝 + 一份具名函数，这本身就是 RULE-021 静态门抓不到的漂移；具名函数存在时，内联拷贝就应视作 bug。

## 兼容、迁移与回滚

- compatibility: 向后兼容；只放宽识别、不改规则语义与退出码
- migration: 消费项目无需迁移；此前为绕过误报改成 HTML 实体或裸 ID 的文档可以改回原写法（含 `<meta>` 的规则正文需加反引号）
- rollback: git revert（见上）
- logic_temp_cleanup: logic_version/working/logic_version-20260904-003-validate-compat/ 于 2026-09-04 删除；台账 4 项（keep 3：代码、测试、本记录；delete 1：working 目录）全部处置

## 关联

- current_logic: logic_domains/toolchain/logic_readme.md#RULE-015 ①②③（validate 识别范围）、RULE-021 ①③（议案编号与占位符判定只此一份）
- proposal_id: CHG-20260904-003（本记录创建后关闭）
- intent_traceability: INT-20260816-008 -> RULE-015 -> test:tests/test_validate.py -> VER-20260904-003; INT-20260816-008 -> RULE-021 -> test:tests/test_recall_cli.py -> VER-20260904-003; INT-20260816-009 -> RULE-021 -> test:tests/test_recall_cli.py -> VER-20260904-003
- code/tests: scripts/recall_common.py; scripts/validate.py; scripts/detect_conflicts.py; scripts/recall_audit/constants.py; scripts/recall_audit/textutil.py; scripts/recall_audit/integrity.py; tests/
