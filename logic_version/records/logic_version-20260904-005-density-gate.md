# VER-20260904-005: Density 硬上限越线与宪法无领域进静态门（CHG-20260904-004 裁决 A）、`--advisory-only` 迁移窗口

## 记录控制

- version_id: VER-20260904-005
- version_slug: logic_version-20260904-005-density-gate
- status: effective
- date: 2026-09-04
- change_id: CHG-20260904-004
- before_commit: b5dc2ae
- after_commit: _待填写_

## 为什么做这个决策？

**背景**：
2026-09-03 在消费项目 eduai 只读复跑 `recall audit`：logic_change 越过 300 行硬上限 21 倍，静态门仍 PASS；一个宪法未登记任何领域的项目只收到一条 `constitution-without-domains` advisory。两条限制都只在报告里出现，实际上没人处理——RULE-021 的 why 早已写明"文字规则拦不住第二份实现，只有机器门能"，而 6000 多行的账本正是 RULE-001 要消灭的上下文膨胀。CHG-20260904-004 于 VER-20260904-002 立为 draft，列出 A（硬上限 + 无领域进门，附逃生口）/ B（维持 advisory，只在 status 高亮）/ C（只无领域进门）三案待裁决。实施中发现一处必须下调的细节：`--formal-review` 要求 compliance 档 CHG 填完整字段，本仓库自身的 formal 夹具 CHG 块就有 120 行，而 field-vocabulary 也写明"把全部字段当成默认必填会让单条 CHG 达到 80-200 行"——若单条 CHG 80 行也进门，正式审查会自相矛盾。

**用户需求/反馈**：
2026-09-04 会话：AI 列出 A/B/C 与建议后，用户回复"认可A，请你继续优化"。

**需求拆解（归档时从 CHG 原样搬入）**：
- raw_request: 2026-09-03 eduai 只读复跑：logic_change 越过硬上限 21 倍静态门仍 PASS；无领域项目只收 `constitution-without-domains` 提示。2026-09-04 用户认可"待立案事项立成 draft CHG"（此前只在两处"当前限制"里写着"待立案"）；同日 AI 汇报三案并建议 A，用户回复"认可A，请你继续优化"
- decomposition: ① Density `exceeds-hard-limit` 是否进 current-state 门（宪法 250 / 领域 400 / 账本 300 / CHG 80）；② `constitution-without-domains` 是否进门（RULE-018 至少一个领域）；③ 若进门，消费项目一次性迁移窗口与 `--advisory-only` 逃生口；④ 用例：越线夹具 FAIL、advisory 开关 PASS
- fit_analysis: 扩展 INT-20260816-008（审计门）与 INT-20260816-011（拆分触发）；FLOW-005#4 从"AI 建议"升级为"门禁提示"；不新增 UXI；RULE-022 ③ 文本更新，波及 RULE-018 ④

## 决策过程

**方案 A（用户裁决）**：`density.issues` 使 current-state / formal-review 静态门失败；`constitution-without-domains` 从 notices 移入 issues；`--advisory-only` 只改退出码、不改报告（优点：限制真正被执行，与"只有机器门能"一致；缺点：eduai 立即 FAIL，需先拆账本或加开关；复杂度：低）

**方案 B**：维持 advisory，只在 `recall status` 高亮（优点：零迁移成本；缺点：等于承认限制不会被执行）

**方案 C**：只让无领域进门，Density 继续 advisory（优点：把 RULE-018 ④ 落实到机器、行数留给人判断；缺点：21 倍越线的账本继续 PASS）

**落选方案归档**：B、C 的需求原文同上方 raw_request。B 否决原因：advisory 已被证明无人处理。C 否决原因：账本膨胀正是 Recall 的核心敌人，留给人判断就是不判断。

**选中方案与原因**：
选 A，并在实施中记录一处分析后下调（SKILL"分析后可以下调但需记录理由"）：**单条 CHG 越过 80 行（`exceeds-chg-limit`）与 blocked 累积不进门，从 issues 移到 notices**。理由：(1) compliance 档 CHG 完整字段本身 80-200 行，进门会让 `--formal-review` 对自己要求的表单 FAIL；(2) 账本 300 行硬上限已进门，间接兜住 CHG 膨胀；(3) blocked 累积是决策卫生提示（把决策交回用户），不是体量问题。其余取舍：(4) `density.issues` 语义收敛为"进门项"、`notices` 为"提示项"，报告分两段打印，JSON 键不变；(5) `--advisory-only` 是审计器参数而非 profile 标志，`recall audit --advisory-only` 仍自动追加 `--current-state`；(6) 审计测试夹具默认自带 `logic_domains/core/` 领域——RULE-018 ④ 说"无论大小至少一个领域"，此前 53 处夹具都是无领域的"root-only 轻量地图"，进门后它们不再是合法项目，`with_domain=False` 只留给专门测无领域的用例。

## 影响范围

**修改的文件/模块**：
- `scripts/recall_audit/archive.py` - `audit_density`：`constitution-without-domains` 进 issues；`exceeds-chg-limit`、`blocked-accumulation` 降为 notices；文档字符串改写门禁语义
- `scripts/recall_audit/report.py` - `strict_failure(advisory_only=)`：current-state / formal-review 下 `density.issues` 非空即失败；`print_text` 把硬上限与提示分两段
- `scripts/recall_audit/cli.py` - 新参数 `--advisory-only`
- `SKILL.md` - 无领域提示改为"静态门失败"；命令块加 `recall audit --advisory-only`
- `logic_readme.md` - RULE-018 ④、RULE-022 ③ 文本与决策记录链接；FLOW-005#4；测试矩阵；"当前限制"两条；活跃议案入口；有效决策索引轮换（最近 3 条：003/004/005，VER-20260904-002 由 RULE-002/015/018/021/022 规则行链接）；source_decisions
- `logic_domains/toolchain/logic_readme.md` - 旧行为消费者（退出码变化）、"当前限制"、测试矩阵、source_decisions
- `references/field-vocabulary.md` - 长度上限段改写门禁语义；personal 层标题说明"内容项 ≠ 机器强制字段"（用户 2026-09-04 认可的顺带修正）
- `references/document-model.md` - Density 段语义
- `.github/labeler.yml` - 删除指向不存在的 `requirements.txt`/`setup.py` 的 `dependencies` 规则（顺带修正）
- `logic_change.md` - 关闭 CHG-20260904-004（正文与公报行删除，三字段搬入本记录）
- `logic_version/index.md` - 登记本记录
- `tests/test_audit_logic_map.py` - 夹具：`CORE_DOMAIN_ROW`、`core_domain_readme` / `core_domain_change`、`write_project(with_domain=)`；用例：`test_constitution_without_domains_fails_gate_unless_advisory_only`、`test_hard_limit_violation_fails_gate_unless_advisory_only`；`exceeds-chg-limit` 断言改到 notices

**破坏性变更**：是，退出码层面。此前 `--current-state` / `--formal-review` 对硬上限越线或无领域的项目返回 0，现在返回 1；`recall audit --advisory-only` 恢复旧退出码。报告 JSON 键不变，但 `density.issues` 少了 `exceeds-chg-limit` / `blocked-accumulation`（移到 `density.notices`），`constitution-without-domains` 从 `notices` 移到 `issues`。已知受影响消费者：eduai（账本越过硬上限 21 倍）——迁移路径：先用 `--advisory-only` 保住 CI，再按 RULE-018 拆账本 / 归档已结束 CHG 到 logic_version，直到不带开关也 PASS。

## 验证方式

- `python -m unittest discover -s tests` → Ran 249 tests OK（上一记录 248，+2 门禁用例，−1 合并的无领域用例）
- `recall audit` → 本仓库 Static gate PASS（有 2 个领域、全部文档未越硬上限）
- `python scripts/audit_logic_map.py references/examples/audit-repro-legacy --current-state` → Static gate FAIL，Density hard limits 段列出 `constitution-without-domains`（夹具是无领域的旧式项目，正是进门后应 FAIL 的形态；它按 RULE-007 不计入本仓库审计）
- 用例：无领域夹具 FAIL、`advisory_only=True` PASS、有领域 PASS；宪法 +160 行 over-target 仍 PASS、+260 行 exceeds-hard-limit FAIL、`advisory_only=True` PASS；formal 夹具 120 行 CHG 块只得 notice、formal 三用例仍 PASS
- 代码差异：`git show <after_commit>`

## 回滚方式

`git revert <after_commit>`。回滚后越线与无领域项目恢复 PASS，`--advisory-only` 参数消失（消费项目 CI 若已写入该参数需同步删除）。

## 经验与教训

- "advisory 提示"在没有人盯着的流水线里等于不存在：eduai 越线 21 倍无人处理就是证据。限制要么进门、要么删除，中间态只增加报告长度。
- 进门前先拿自己的正式夹具跑一遍：单条 CHG 80 行的限制与 `--formal-review` 的完整字段要求互斥，这个矛盾在 draft 议案里没人看见，动手实施第一轮测试就暴露了。"分析后下调"要写进记录，而不是悄悄改成 notice。
- 测试夹具是工具对"合法项目"的定义：53 处夹具都没有领域，说明 RULE-018 ④ 此前只在文字上成立。规则进门时夹具必须一起改，否则要么测试全红、要么夹具继续示范违规形态。

## 兼容、迁移与回滚

- compatibility: 退出码不兼容（越线 / 无领域项目 0 → 1）；报告 JSON 键兼容，issues/notices 归属有变
- migration: 消费项目在 CI 命令加 `--advisory-only` 保住旧退出码，然后按 RULE-018 拆账本或登记领域，直到去掉开关仍 PASS
- rollback: git revert（见上）
- logic_temp_cleanup: logic_version/working/logic_version-20260904-005-density-gate/ 于 2026-09-04 删除；台账 4 项（keep 2：本记录、新增测试与夹具；delete 2：working 目录、scratchpad 补丁脚本）全部处置

## 关联

- current_logic: logic_readme.md#RULE-018 ④（无领域进门）、#RULE-022 ③（硬上限进门、CHG 80 行只提示、`--advisory-only`）
- proposal_id: CHG-20260904-004（draft → 用户裁决 A → 本记录创建后关闭）
- intent_traceability: INT-20260816-008 -> RULE-022 -> test:tests/test_audit_logic_map.py#test_hard_limit_violation_fails_gate_unless_advisory_only -> VER-20260904-005; INT-20260816-011 -> RULE-018 -> test:tests/test_audit_logic_map.py#test_constitution_without_domains_fails_gate_unless_advisory_only -> VER-20260904-005
- code/tests: scripts/recall_audit/archive.py; scripts/recall_audit/report.py; scripts/recall_audit/cli.py; tests/test_audit_logic_map.py
