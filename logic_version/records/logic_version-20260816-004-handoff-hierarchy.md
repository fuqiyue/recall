# VER-20260816-004: 会话默认延续、层级化子文档与舍弃方案归档

## 记录控制

- version_id: VER-20260816-004
- version_slug: logic_version-20260816-004-handoff-hierarchy
- status: effective
- date: 2026-08-16
- change_id: CHG-20260816-003
- before_commit: de65e8e
- after_commit: 0033b0d
- recall_route: high
- history_retention: full
- decision_confirmed_by: user
- decision_ref: user-confirmed:2026-08-16（发现1/2/3 逐项裁决并要求"请你修改"）
- changed_by: Claude (Fable 5)
- intent_traceability: INT-20260816-003 -> RULE-017 -> test:scripts/audit_logic_map.py -> VER-20260816-004; INT-20260816-011 -> RULE-018 -> test:tests/test_audit_logic_map.py -> VER-20260816-004; INT-20260816-004 -> RULE-014 -> test:scripts/validate.py -> VER-20260816-004

## 为什么做这个决策？

**背景**：
"新人接手"视角审查发现：(1) 协作协议本身（新会话=新人接手、默认延续现行文档、
用户明确否定才改现行）只活在对话历史里，每次上下文压缩后用户被迫重讲元规则——
Recall 记录了"代码为什么这样设计"，却没记录"维护者希望 AI 以什么姿态协作"；
(2) SKILL 原则 3 与 INV-001 把现行文档锁死为根一对，审计
`root-only-model-requires-inherited-policy` 强制非根模块 inherited——大项目单文件
全量阅读低效，与"按需求分批披露信息"的效率目标矛盾（审计脚本其实早已内建
readme-only 模块路由校验，只是被该检查禁用）；(3) 同议题多方案竞争时，未过决策
检查点即被舍弃的方案直接删除会丢失需求原文，需求保全规则只覆盖了胜出方案。

**用户需求/反馈**：
"发现1 部分认可。发现2……我认可文件级的 logic 文档，但是要作为子文档……总的
logic_readme.md 是总文件……先看总的再看子的……由 recall 自行决定，但决定拆分时候，
需要向用户告知，并由用户做决定。发现3……把舍弃的方案放到 logic_version 中。请你修改"

**需求拆解（自 CHG-20260816-003 原样搬入）**：
- raw_request: 用户 2026-08-16 对开发流程审查三项发现逐项裁决："发现1 部分认可"（默认延续现行文档原则）；"发现2 部分，我认可文件级的 logic 文档，但是要作为子文档……总的 logic_readme.md 是总文件……先看总的再看子的……跨端需求同时修改……由 recall 自行决定，但决定拆分时候，需要向用户告知，并由用户做决定"；"发现3……当选择了最优逻辑的时候，可以舍弃其他方案，然后把舍弃的方案放到 logic_version 中"；"请你修改"
- decomposition: 1) SKILL 新增默认姿态核心原则 + logic_readme 新增 RULE-017 与 UXI-005；2) 层级化子文档：SKILL 原则 3 与发布态模型/读取顺序改写、INV-001 改写、RULE-018、审计解锁非根 readme-only 并豁免已登记子文档的 nonroot 检测、project-onboarding 增加拆分流程章节、logic-readme-template 补 doc_policy 说明；3) 舍弃方案归档：RULE-014 扩展 + logic-version-git-template §4 / change-lifecycle §7 / logic_change 底部说明补搬运条款
- fit_analysis: 1) 强化 INT-20260816-001/003（文档恢复上下文）的既有意图，新增 UXI-005 不新增 INT；2) 新增 INT-20260816-011 并挂 FLOW-005#4（拆分是项目接入流程的后续生命周期环节，不替代 FLOW-005#2 的根骨架）；3) 强化 FLOW-002#3-#5 归档环节与 RULE-014 需求保全语义；三项均不触碰 UXI-001..004（默认延续减少而非增加用户交互）

## 决策过程

**方案 A**：维持单文件+锚点——零改动、新会话读一个文件拿全貌，但大项目强迫全量
阅读，用户已明确否定其足够性（复杂度：无，否决）。

**方案 B**：自由子文档（`logic_readme_<名>.md` 任意放置，用户示例的字面形式）——
命名直观，但命中平行真源检测正则 `logic_readme[-_].+`，绕过既有 paired/readme-only
机制需新造一套校验；无登记约束则重演平行真源失败模式（复杂度：高，否决；
用户示例的实质是"总-子层级 + 按需阅读"，固定名 `<模块>/logic_readme.md` 等价实现）。

**方案 C（选中）**：解锁审计既有 readme-only 机制。子文档固定名
`<scope_path>/logic_readme.md` + 根范围登记表登记（doc_policy: readme-only、
logic_change 列 none）；审计改三处：非根 in-system 允许 inherited/readme-only 而
paired 仍限根（INV-002 保 logic_change 唯一）、范围锚点要求只对 inherited 生效、
nonroot 检测豁免已登记子文档（未登记副本与子 logic_change 继续拦截）。拆分由
AI 建议、用户决定；根规章优先；阅读顺序先根后子（复杂度：中）。

**选中方案与原因**：C。复用现成的模块路由/module_id/scope 对账校验，登记表成为
子文档的唯一合法性来源——"未登记即违规"延续了本系统对平行真源的一贯防线。
默认姿态与舍弃方案归档为纯制度文本修改，随同落盘。

## 影响范围

**修改的文件/模块**：
- `SKILL.md` - 核心原则 10→11 条（新增会话默认延续）；原则 3 改写为层级模型；发布态文档模型与默认上下文读取补先根后子顺序
- `logic_readme.md` - 新增 RULE-017/RULE-018 与 UXI-005、INT-20260816-011、FLOW-005#4；RULE-014 扩展舍弃方案归档；INV-001 改写、INV-002 补充；当前限制、代码地图、测试矩阵、索引更新
- `scripts/audit_logic_map.py` - 移除 root-only-model 强制（非根 paired 改为专项拦截）；范围锚点要求限 inherited；registered_child_readme_paths + nonroot 检测豁免已登记子文档
- `references/project-onboarding.md` - 新增"模块拆分（子 logic 文档）"章节（触发信号、五步流程、阅读顺序）
- `references/logic-readme-template.md` - 范围登记表 doc_policy 取值说明
- `references/logic-version-git-template.md`、`references/change-lifecycle.md`、`logic_change.md` 底部说明 - 归档步骤补舍弃方案搬运条款
- `tests/test_audit_logic_map.py` - 新增 2 用例（已登记 readme-only 子文档放行；非根 paired 拒绝 + 子 logic_change 仍拦截）

**破坏性变更**：无。放宽约束向后兼容：既有 inherited 登记与 root-only 项目零迁移；
本项目自身未拆分（规模未达标）。

## 验证方式

`python tests/test_audit_logic_map.py`（64 tests OK，含子文档放行/拦截双向用例）；
`python -m unittest tests.test_recall_cli`（13 OK）；`python -m unittest tests.test_git_sync`
（18 OK）；`python scripts/audit_logic_map.py . --current-state` 静态门 PASS；
`python scripts/validate.py` 零错误；`python scripts/detect_conflicts.py` 无冲突。
测试中发现的真实治理行为：拆分后引用根锚点的活跃 CHG 会被审计拦截
（related-module-anchor-not-registered），必须改引 MOD-ID——已写入拆分步骤 5。

## 回滚方式

`git revert` 本次提交整体回退即恢复 root-only 强制。已按新规拆分的消费项目回滚前
先把子文档内容合回根文档并把登记行改回 inherited。

## 经验与教训

协作协议与业务规则一样需要落盘：凡是"用户不得不重复讲"的内容，都是文档体系的
覆盖缺口。放宽不可破坏约束时，合法化的边界必须由机器可检的登记来定义
（登记表=白名单），否则"允许拆分"会退化为"允许任意副本"。用户需求的字面形式
（logic_readme_xxx.md）与实质意图（总-子层级、按需披露）可以分离：用既有机制
等价实现实质意图，并把这个替换明确告知用户。

## 关联

- current_logic: logic_readme.md#RULE-014, RULE-017, RULE-018
- proposal_id: CHG-20260816-003（已归档移除）
- code/tests: scripts/audit_logic_map.py; tests/test_audit_logic_map.py; references/project-onboarding.md; SKILL.md
