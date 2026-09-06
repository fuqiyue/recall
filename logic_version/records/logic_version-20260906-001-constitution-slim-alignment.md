# VER-20260906-001: 宪法瘦身与规则-实现对齐：RULE-022 ② 下放为工具链 RULE-024（函数长度机器门）、route 识别 inherited 模块、RULE-021 ④ 冒烟补全、事故叙事归档

## 记录控制

- version_id: VER-20260906-001
- version_slug: logic_version-20260906-001-constitution-slim-alignment
- status: effective
- date: 2026-09-06
- change_id: CHG-20260906-001
- before_commit: 9e0c9a8
- after_commit: 9090e06

## 为什么做这个决策？

**背景**：
2026-09-06 用户问"根据目前的recall，还有什么需要优化吗？"。只读审查（inspect）基线全绿：audit / validate / conflicts 无错误，249 测试 OK，工作区干净且与远端同步。但发现九处"规则说的"与"代码做的"不一致或漂移：
1. 宪法 238/250 行、≈9.9k token，是每任务固定成本；RULE-018 ③ 与 RULE-022 ②③ 写的是工具链内部机制，why 列带量化叙事。
2. RULE-022 ②"新写函数不超过 150 行"没有机器门；toolchain"当前限制"记 9 个存量超限函数，ast 实测 11 个（漏 changes.py 一个与 validate.py `validate_recall` 170 行）。
3. RULE-021 ④ 声称每条子命令都有子进程冒烟，实际 new / list / query / sync / init 没有，list 与 query 在 tests/ 中零用例。
4. RULE-010 why 与 RULE-013 正文带事故叙事，违反 RULE-022 ④。
5. field-vocabulary "personal 模式不维护 governance_verification / governance_verified_at" 与审计器对 readme / 账本 / VER 的必填要求矛盾。
6. `recall route references/document-model.md` 报"未命中任何领域，先新增领域行"，但 references/ 已作为 MOD-TEMPLATES（inherited）登记。
7. `recall audit` 每次把 .github/ 的三个 yml 列为 Agent-private 候选，而 .github/ 已在 unmapped_paths 登记。
8. CreateVerTests 进程内调用 create_ver 未捕获 stdout，测试输出混入"已创建决策记录"。
9. 宪法"当前限制"仍引用已关闭的 CHG-20260904-003；测试矩阵 INV-003 行声称"已发布 VER 只有创建与回填提交"，与 Git 历史不符。

**归档的叙事（自规则行移出，RULE-022 ④）**：
- RULE-010 推送责任子句的事故：2026-09-02 消费项目 7 个提交只推 1 个，远端停在测试已进、实现未进的中间提交，CI 18 项失败。
- RULE-013 占位符原文要求的实例：2026-09-03 一条记录手工补填时把 `- after_commit:` 留空，hook 无法识别，需人工补哈希。
- RULE-018 的原始动机：单文件根文档在消费项目膨胀到上下文窗口的 20 倍。
- RULE-022 的原始量化：SKILL 每次触发约 6300 token 且近半是细节；审计器单文件 6764 行；规则行曾膨胀成 2000 字符段落。
- INV-003 的历史：`git log --diff-filter=M -- logic_version/records/` 显示 RULE-013 硬化前有 4 次非回填修改——9d3f6dd（2026-08-11，VER-20260811-002）、b138381（2026-08-16，VER-20260808-001）、fa1fbd5 与 de65e8e（2026-08-16，VER-20260816-002）；2026-08-17 起再无此类提交。这些记录不追溯改写（INV-003），本记录即勘误说明。

**用户需求/反馈**：
用户 2026-09-06："认可，请帮我优化"（针对 AI 列出的九项与"先清漂移、再瘦身对齐"的建议）。

**需求拆解（归档时从 CHG 原样搬入）**：
- raw_request: 2026-09-06 用户问"根据目前的recall，还有什么需要优化吗？"；AI 只读审查后列出 P1-P4 九项（宪法 238/250 行 ≈9.9k token；RULE-021 ④ 与 RULE-022 ② 无机器门；RULE-010/013 事故叙事；field-vocabulary 与审计必填矛盾；route 忽略 inherited；.github 候选噪音；测试 stdout 泄漏；CHG-20260904-003 悬空指针；INV-003 证据行与历史不符），用户回复"认可，请帮我优化"
- decomposition: ① 宪法规则行下放与压缩（RULE-018 ③、RULE-022 ②③、why 列去叙事）并修"当前限制"悬空指针与 INV-003 证据行；② 工具链新规则 RULE-024（审计器分层 + 函数长度机器门，冻结 11 个存量）；③ RULE-021 ④ 补 new/list/query/sync/init 冒烟；④ route 识别 inherited 模块；⑤ 审计候选跳过 unmapped_paths 目录；⑥ RULE-010/013 叙事归 VER；⑦ field-vocabulary personal 段限定到 CHG 块；⑧ CreateVerTests 静音；⑨ CI 增加 conflicts 胶水步
- fit_analysis: 复用 INT-20260816-003（宪法必读成本）、INT-20260903-002（route）、INT-20260816-008（审计门）；不新增 INT/FLOW/UXI；RULE-022 ② 改为指向新领域规则 RULE-024，③④ 编号不变

## 决策过程

**方案 A**：一次 medium 变更完成九项，一条 CHG、一条 VER（优点：规则文本与机器门在同一提交对齐、一次门禁；缺点：diff 跨 13 个文件；复杂度：中）

**方案 B**：先 simple 提交清漂移（悬空指针、候选噪音、静音），再 medium 提交瘦身对齐（优点：提交小；缺点：route 与审计器是 public 契约路径，按 SKILL"路由一问"本就至少中等，"simple"名不副实，且需两次 hook 回填；复杂度：中）

**方案 C**：宪法"决策记录"列改用裸 VER-ID 以大幅降 token（未选：改变全部规则行的链接形态，波及消费项目与 validate 反链口径，需用户单独裁决；留作后续选项）

**选中方案与原因**：
选 A。九项共享同一不变量"规则行所述 = 机器门所验"，拆开会出现中间态（规则改了、门没到）。实施取舍：(1) RULE-022 ② 不删编号而改为指向 RULE-024，保持 ③④ 编号稳定（SKILL、field-vocabulary、toolchain 多处引用 "RULE-022 ③"）；(2) 函数长度门扫描全部 `scripts/`（不只 recall_audit/），因为实测 validate.py 也有超限函数；白名单冻结 11 个、只减不增、条目只许变短；(3) init / sync 冒烟只到 argparse 层：真跑会改本仓库 Git 配置并触网（init_recall 以脚本所在仓库为项目根），业务行为已由 tests/test_git_sync.py 在临时仓库覆盖；(4) 审计候选豁免只作用于源码类文件，`.md` 形态的平行真源检测对所有代理目录不变；(5) 宪法 `source_decisions` 收缩为"指针 + 最近两条"，与 RULE-002 ② 同理。

## 影响范围

**修改的文件/模块**：
- `scripts/recall_common.py` - 新增 `InheritedModule` / `inherited_modules`（读取登记表 inherited 行与宪法锚点）
- `scripts/route_docs.py` - `match_inherited`、JSON 新键 `matched_inherited`、文本输出"命中宪法直辖模块"，未命中提示区分根文件与新功能
- `scripts/recall_audit/archive.py` - 抽出 `_parse_registry_entries` / `_constitution_unmapped_paths`；Agent-private 候选跳过 unmapped_paths 已登记目录
- `tests/test_recall_common.py` - `inherited_modules` 用例；`FunctionLengthGateTests`（RULE-024 机器门，白名单 11 项）
- `tests/test_recall_cli.py` - CreateVerTests 静音；路由夹具加 inherited 行 + 2 用例；`CliGlueSmokeTests` 补 new / list / query 真跑与 init / sync `--help`（7 用例）
- `tests/test_audit_logic_map.py` - unmapped 目录源码不进候选用例
- `logic_readme.md` - RULE-018 ③/why、RULE-022 ②③/why、领域规则指针加 RULE-024、source_decisions 收缩、数据与控制流与修改检查清单压缩、INV-003 测试行、有效决策索引轮换（VER-20260904-003 出、本记录入；003 由 RULE-015/021 链接）、"当前限制"两条
- `logic_domains/toolchain/logic_readme.md` - 新增 RULE-024；RULE-021 证据与记录；代码地图 route_docs / recall_common / recall_audit / tests 行；旧行为消费者；测试矩阵；当前限制
- `logic_domains/git-pipeline/logic_readme.md` - RULE-010 why、RULE-013 正文去叙事并链接本记录
- `references/field-vocabulary.md` - personal 段限定到 CHG 块，说明文档控制 / 记录控制的 governance 字段全模式必填
- `.github/workflows/validate.yml` - 新增 `recall conflicts` 步（退出码 2 只提示）
- `logic_change.md` - CHG-20260906-001 立案 → 三字段搬入本记录 → 关闭
- `logic_version/index.md` - 登记本记录

**破坏性变更**：否。`recall route --json` 新增键 `matched_inherited`，旧键不变；审计 JSON `private_agent_knowledge_candidates` 对已登记 unmapped 目录只会减少；退出码不变。

## 验证方式

- `python -m unittest discover -s tests` → Ran 261 tests OK（上一记录 249，+12）
- `recall audit` → Static gate PASS，Density 仅 over-target 提示，不再出现 Agent-private 候选段
- `recall audit --formal-review` → 议案关闭后 PASS（议案在办期间 personal 最小块使 formal FAIL 66 项，属 RULE-023"formal 要求不变"的预期）
- `recall validate` → 无错误；24 条规则定义（+RULE-024）；`recall conflicts` 无冲突；status / validate / conflicts 同报 24
- `recall route references/document-model.md` → 命中宪法直辖模块 MOD-TEMPLATES，不再建议新建领域；`recall route README.md` → 仍提示读宪法或新建领域
- 宪法：238 → 233 行，估算 9870 → 约 9.8k token，规则行 7469 → 7205 字符。150 行目标是结构性缺口（必填段 + 11 条规则行 + 24 行意图层 + 决策记录链接列），去叙事只省约 1%；进一步下降需方案 C 类结构决策
- 代码差异：`git show <after_commit>`

## 回滚方式

`git revert <after_commit>`。回滚后 RULE-024 与函数长度门消失、route 恢复对 references/ 的"新建领域"建议、审计恢复列出 .github 候选；无数据迁移。

## 经验与教训

- 文字规则里的数字一定会过期：文档写 9 个存量函数、实测 11 个。凡是能被 ast / grep 数出来的限制，都该是测试而不是散文；散文只留指针。
- "每条子命令都有冒烟"这类全称断言，写进规则前先 grep tests/——list / query 零用例却在规则里"已覆盖"了两个月。
- 宪法 token 的大头不在 why 叙事而在结构（必填段、决策记录链接列、意图层）；去叙事只省 1%，下一步是结构决策而非继续修辞。
- 只读审查加用户一句"认可"就足以开一条 medium：把九项打包成一条 CHG 而不是九条 simple，避免 public 路径以 simple 通道偷渡。

## 兼容、迁移与回滚

- compatibility: 兼容；route JSON 增键、审计候选减少，退出码不变
- migration: 消费项目无需动作；若自有 CI 断言 `private_agent_knowledge_candidates` 内容，需按新口径更新
- rollback: git revert（见上）
- logic_temp_cleanup: logic_version/working/logic_version-20260906-001-constitution-slim-alignment/ 于 2026-09-06 删除；台账 3 项（keep 1：本记录；delete 2：working 目录、scratchpad 补丁脚本）全部处置

## 关联

- current_logic: logic_readme.md#RULE-018 ③、#RULE-022 ②③；logic_domains/toolchain/logic_readme.md#RULE-021 ④、#RULE-024；logic_domains/git-pipeline/logic_readme.md#RULE-010、#RULE-013
- proposal_id: CHG-20260906-001（implementing → 本记录创建后关闭）
- intent_traceability: INT-20260903-002 -> RULE-018 -> test:tests/test_recall_cli.py#test_inherited_module_path_points_back_to_constitution -> VER-20260906-001; INT-20260816-008 -> RULE-024 -> test:tests/test_recall_common.py#test_no_new_function_exceeds_limit_and_legacy_only_shrinks -> VER-20260906-001; INT-20260816-006 -> RULE-021 -> test:tests/test_recall_cli.py#test_list_exits_zero_and_shows_records -> VER-20260906-001
- code/tests: scripts/recall_common.py; scripts/route_docs.py; scripts/recall_audit/archive.py; tests/test_recall_common.py; tests/test_recall_cli.py; tests/test_audit_logic_map.py
