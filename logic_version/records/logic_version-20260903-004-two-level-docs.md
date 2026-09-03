# VER-20260903-004: 一二级拆分法——宪法（根文档）与部门法（领域文档）分层，按需导入

## 记录控制

- version_id: VER-20260903-004
- version_slug: logic_version-20260903-004-two-level-docs
- status: effective
- date: 2026-09-04
- change_id: CHG-20260903-004
- before_commit: 7364a6c
- after_commit: _待填写_

## 为什么做这个决策？

**背景**：
Recall 的现行制度此前是"单文件根 logic_readme + 可选的 readme-only 子文档"（RULE-018 旧版），子文档拆分须经用户确认、且没有配对的 logic_change。实测结果：没有任何项目用过子文档；消费项目 eduai 的 logic_readme 达 1060 行、logic_change 6543 行（硬上限 21 倍），两者合计约 35 万 token，超出任何上下文窗口；本仓库根文档压缩到 288 行后 token 仍约 1.3 万，因为规则行本身就是成本。RULE-022 的按需披露只解决了 SKILL.md 首屏，没有解决"改哪个模块要读哪些规则"。

**用户需求/反馈**：
2026-09-03 会话：eduai 的 readme + change 超过上下文窗口，能否二级拆分；"无论大小项目，都使用一二级拆分法"；法律比喻——一级 readme 是宪法（大纲 + 用户表述与意图，必读），二级 readme 是部门法（按专题，大部门制：法条少时合一份，大了拆小部门），change 只在二级、一事一议、同类合一份账本，对宪法的修改也有对应 change。

**需求拆解（归档时从 CHG 原样搬入）**：
- raw_request: 2026-09-03 用户会话——eduai 的 readme+change 超过上下文窗口；要求"无论大小项目都使用一二级拆分法"：一级 readme 是宪法（大纲 + 用户表述与意图，必读），二级 readme 是部门法（按专题/大部门制，法条少时合为一份、大了再拆小部门），change 只在二级（一事一议，同类议案合在同一领域的 change；对宪法的修改也有对应 change），按需导入
- decomposition: ① 文档模型：根 logic_readme = 宪法（全局规则 + INT/FLOW/UXI + 领域登记表大纲），`logic_domains/DOMAIN/logic_readme.md` + `logic_change.md` = 部门法与其议案账本（范围登记表 `doc_policy: paired`），根 logic_change 只放修宪议案 + 全项目活跃议案索引（一行一条，指向领域文件）；② 审计器：允许非根 paired（领域）、已登记领域文档不算平行真源、领域 CHG 块同受 current-state 检查、领域议案 affected_scopes 须含自身且不含 `.`（触宪即修宪案）、Density 分档（宪法 150/250、领域 readme 250/400、领域 change 150/300）与"无领域"提示；③ validate/status/conflicts 跨领域读取规则与 CHG；④ 新命令 `recall route 路径或关键词` 输出本次应读的文档清单与行数；⑤ 模板与 references、SKILL/CLAUDE/AGENTS 读取顺序；⑥ 本仓库自身按新模型拆为宪法 + 2 个领域（git-pipeline、toolchain）；⑦ RULE-018/INV-001/INV-002 改写，VER-20260903-004
- fit_analysis: 扩展 INT-20260816-011（层级化子文档：可选拆分 → 强制两级）、INT-20260816-003（三件套阅读 → 宪法必读 + 领域按需）；FLOW-002#1 与 FLOW-005#4 改写；新增 INT-20260903-002（recall route 按需导入）；不触碰 UXI-001..006；与 RULE-019（语义正文只在规则行）一致——领域规则行是规则行的搬迁，不是副本

## 决策过程

**方案 A**：领域文档统一放 `logic_domains/DOMAIN/`，用现有范围登记表 paired 行登记，`owned_paths` 声明职权（优点：一处目录即可枚举全部部门法；跨目录专题不受代码目录束缚；复用现有 scope 路由、登记对账与"根索引可指向模块账本"的审计能力；缺点：领域与代码目录不再一一对应，需要 `owned_paths` 维护职权；复杂度：中）

**方案 B**：沿用旧 RULE-018 的 `模块目录/logic_readme.md` 并加配对 change（优点：改动最小；缺点：专题跨目录时无处安放，小项目"一个领域覆盖全部"会与根目录冲突；复杂度：低）

**方案 C**：保持单文件 + 锚点，只做 `recall route` 切片输出（优点：无文档迁移；缺点：用户明确要求两级结构，且切片仍需整读根文档、无法把规则真正移出必读区；复杂度：低）

**落选方案归档**：B、C 的需求原文同上方 raw_request；B 否决原因是专题与目录不同构；C 否决原因是不满足"无论大小项目都用一二级"的明确要求，也不能降低宪法本身的体积。

**选中方案与原因**：
选 A。关键取舍：(1) 根账本保留全项目公报（一行一条）而不是完全下放——代理只读宪法 + 根账本即可知道有哪些在办议案触及目标领域，代价是领域 CHG 开/关要同步一行，审计器校验双向一致（`domain-change-missing-from-root-index`、`root-index-status-mismatch`）；(2) 领域议案 affected_scopes 不得含 `.`——触及宪法的议案必须回到根账本，否则"修宪"会散落在各部门法里；(3) 两级模型是强制目标，但审计器对无领域项目只给 advisory `constitution-without-domains`、不让静态门立即失败——存量项目（eduai）应在迁移时补齐，而不是在升级工具的当天全红；(4) 旧式 readme-only 子文档工具继续接受、文档不再推荐，避免为零存量做迁移工具；(5) 宪法 Density 目标收紧到 150/250，因为它是每任务必读的固定成本。本仓库自身拆为 2 个领域：MOD-GIT-PIPELINE（RULE-010/011/013）与 MOD-TOOLCHAIN（RULE-005..009/012/015/021/023），宪法保留 11 条全局规则与意图层。

## 影响范围

**修改的文件/模块**：
- `scripts/recall_common.py` - 新增 `registered_domains`/`change_ledgers`/`LogicDomain`（RULE-021 单源读取领域登记表）
- `scripts/route_docs.py`（新）、`scripts/recall.py` - `recall route` 子命令；`status` 输出领域数与各账本 CHG 计数
- `scripts/validate.py` - 二级文档纳入编号空间检查（paired + readme-only）、CHG 跨账本提取、领域 CHG 未进根公报告警
- `scripts/detect_conflicts.py` - 规则来自宪法 + 全部领域、议案来自全部账本
- `scripts/recall_audit/integrity.py` - 非根 paired 放行（`paired-policy-needs-in-system` 替代 `paired-policy-root-only`）、`_check_domain_documents`（领域 readme 表格、领域账本、公报行）、`_check_module_proposal_owners` 改为"必含自身、不得触宪"
- `scripts/recall_audit/archive.py` - `registered_child_document_paths`（readme + change 豁免）、`registered_domain_scopes`、`audit_density` 分档与 `constitution-without-domains`
- `scripts/recall_audit/constants.py` - `SCOPE_TYPES` 增加 `domain`；`scripts/audit_logic_map.py`、`recall_audit/report.py` 导出
- `logic_readme.md` - 重写为宪法（11 条全局规则、领域目录、意图层）；RULE-018/INV-001/INV-002 改写；范围登记表新增两领域行
- `logic_domains/git-pipeline/`、`logic_domains/toolchain/` - 新建两对领域文档，规则行/代码地图行/测试行自宪法搬迁
- `SKILL.md`、`CLAUDE.md`、`AGENTS.md`、`references/*`、`README.md` - 读取顺序与文档模型更新；新增 `references/logic-domain-template.md`
- `tests/` - 领域登记/公报/密度/route/validate 用例

**破坏性变更**：对外 CLI 命令名、退出码、`--json` 结构不变。审计口径变化：非根 paired 由拒绝变为接受；无领域项目多出一条 advisory 提示；根 readme Density 目标 250/400 → 150/250（advisory）。旧式 readme-only 子文档继续被接受。

## 验证方式

- `python -m unittest discover -s tests` 全部 OK（新增领域/公报/密度/route/validate 用例）
- `python scripts/audit_logic_map.py . --current-state` → Static gate PASS；两份领域文档在场、无 nonroot/parallel 报告
- `python scripts/validate.py` → 无错误；规则计数含 2 份领域文档；CHG 跨 3 份账本发现
- `python scripts/recall.py route scripts/git_sync.py` → 清单为宪法 + 根账本 + MOD-GIT-PIPELINE，不含 MOD-TOOLCHAIN
- eduai 只读复跑审计：退出码不变，新增 `constitution-without-domains` 提示
- 代码差异：`git show <after_commit>`

## 回滚方式

`git revert <after_commit>`。纯文档 + 脚本；回滚后领域文档内容回并根文档，非根 paired 重新被拒绝。

## 经验与教训

- 行数目标衡量结构而不衡量上下文成本：规则行是 token 大头，只有把规则移出必读区才能降低固定成本；"按需披露"要落到文档层级，不只落到 SKILL 首屏。
- 可选的拆分机制等于没有：RULE-018 旧版存在 18 天、零使用；强制"至少一个领域"加 advisory 提示才让模型成为默认形态。
- 审计器早已支持"根索引指向模块账本"，只差一条禁令（paired 仅限根）——重开一个被封的能力比新造一套便宜，先读代码再设计。
- 修宪与部门法事务必须有机器可判的边界（affected_scopes 含 `.`），否则宪法级改动会散落到各领域账本。

## 兼容、迁移与回滚

- compatibility: 向后兼容；旧式 readme-only 与无领域项目继续通过静态门，只多 advisory 提示
- migration: 存量项目按 references/project-onboarding.md"领域划分与拆分"迁移：新建领域目录、登记 paired 行（修宪案）、搬迁规则行
- rollback: git revert
- logic_temp_cleanup: logic_version/working/logic_version-20260903-004-two-level-docs/ 于 2026-09-04 删除；台账 6 项（keep 5：route_docs.py、领域模板、两对领域文档、本记录；delete 1：working 目录）全部处置

## 关联

- current_logic: logic_readme.md#RULE-018（两级模型）；INV-001/INV-002；logic_domains/toolchain/logic_readme.md#RULE-015、RULE-021（跨领域校验与单源读取）
- proposal_id: CHG-20260903-004（本记录创建后关闭）
- intent_traceability: INT-20260816-011 -> RULE-018 -> test:tests/test_audit_logic_map.py -> VER-20260903-004; INT-20260903-002 -> RULE-018 -> test:tests/test_recall_cli.py -> VER-20260903-004; INT-20260816-008 -> RULE-015 -> test:tests/test_validate.py -> VER-20260903-004
- code/tests: scripts/recall_common.py; scripts/route_docs.py; scripts/recall.py; scripts/validate.py; scripts/detect_conflicts.py; scripts/recall_audit/; logic_domains/; references/logic-domain-template.md; tests/
