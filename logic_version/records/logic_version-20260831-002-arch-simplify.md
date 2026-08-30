# VER-20260831-002: 自身入口瘦身收尾、意图层按治理模式分档与 create_ver 编码合规

## 记录控制

- version_id: VER-20260831-002
- version_slug: logic_version-20260831-002-arch-simplify
- status: effective
- date: 2026-08-31
- change_id: none
- before_commit: 2b8e7ce
- after_commit: _待填写_

## 为什么做这个决策？

**背景**：
2026-08-30 架构评估指出四个简化方向：(1) 消费入口在 init 完成后仍每会话加载安装期内容——P2（VER-20260831-001）已修模板，但 Recall 仓库自身的 CLAUDE.md 仍是约 100 行的制度复述，远超短指针阈值（审计器 3000 字符判定）；(2) 意图层（INT/FLOW/UXI）维护成本随功能数线性增长，personal 模式下单人为三层逐条维护付出的行数与收益不成比例；(3) 参考文档合并与 (4) Git 表面收缩两项经分析分别否决与转待决。另有 VER-20260831-001 记录的既有缺陷：create_ver.py 编码防护只看 isatty，交互式 GBK 控制台打印 emoji 崩溃。

**用户需求/反馈**：
2026-08-31 会话：用户确认 P2 合理，认可 2026-08-30 架构评估第一部分（流程优化与架构简化方向），明确授权"请你帮我进行优化"。

**需求拆解（归档时从 CHG 原样搬入；无 CHG 的记录填 none）**：
- raw_request: 2026-08-31 用户会话——"一、流程还有哪些值得优化的地方？架构够不够简单？认可，请你帮我进行优化"
- decomposition: ① Recall 仓库自身 CLAUDE.md 裁剪为五条短路由（保留全部机器可读标记，低于 3000 字符短指针阈值）；② governance-modes.md 增加意图层维护深度分档（personal 轻量档：INT 必维护、FLOW 可合并、UXI 按需；collaborative+ 全量），SKILL.md 意图层条目与 RULE-014 补充分档语义；③ create_ver.py 编码防护与兄弟脚本对齐（isatty 判定改为 encoding 判定）；④ Git 表面收缩与现行 RULE-010/011、UXI-001/002 冲突，按核心原则 5 立案 CHG-20260831-002 awaiting-decision 交用户裁决
- fit_analysis: ①是 VER-20260831-001（入口短路由化）在本仓库自身实例上的收尾，强化 INT-20260816-003（降低每会话读取成本）；②直接缓解 logic_readme"当前限制"中意图层线性增长问题，不新增 INT，不改变 FLOW；③是 RULE-008 既有约束的合规修复，不改契约；④不实施、只立案

## 决策过程

**方案 A**：仅裁剪入口，不动意图层与脚本（优点：改动最小；缺点：意图层线性增长与 GBK 崩溃两个已知问题继续存在；复杂度：低）

**方案 B**：入口瘦身 + 意图层分档 + create_ver 修复，Git 表面收缩转待决议案（优点：三个可安全实施项一次完成，与已确认规则冲突的项走正规决策流程；缺点：单次变更面稍大；复杂度：中）

**方案 C**：连 Git 表面收缩一起实施（优点：简化最彻底；缺点：直接违反核心原则 5——RULE-010/011 与 UXI-001/002 的决策依据是"用户要求/用户确认"，代理不得替用户推翻已确认意图；复杂度：中）

**落选方案归档（合并 references 三份文档）**：曾建议把 change-lifecycle / governance-modes / field-vocabulary 合并为一份以减少认知负担。否决原因：不可变 VER 记录、备份 MANIFEST 与模板中存在指向这些文件名的既有链接，改名收益（参考列表少两行）不抵链接断裂风险；三份文档均为按需读取，不占默认上下文。

**选中方案与原因**：
选 B。可安全实施与需用户裁决的项分离，正是三通道与原则 5 的设计用途；意图层分档采用"轻量是下限不是上限"表述，本仓库已维护的全量三层不需回退，消费项目按模式取档。

## 影响范围

**修改的文件/模块**：
- `CLAUDE.md` - 从约 100 行制度复述（初始化步骤、CLI 详表、工作流、约束）裁剪为五条短路由 + 机器可读标记 + 一行接入指针；语义正文全部回归 SKILL.md 与 logic_readme.md（RULE-019）
- `references/governance-modes.md` - personal 节新增意图层轻量档定义；collaborative 节新增全量维护要求
- `SKILL.md` - 意图层条目补充"维护深度按治理模式分档"指针
- `logic_readme.md` - RULE-014 补充分档语义；"当前限制"意图层条目更新缓解路径；登记 CHG-20260831-002 与本记录
- `scripts/create_ver.py` - `_force_utf8_when_redirected` 改为与 detect_conflicts.py 一致的 `_force_utf8_output`（encoding 判定），修复交互式 GBK 控制台 emoji 崩溃
- `logic_change.md` - 新增 CHG-20260831-002（Git 表面收缩，awaiting-decision，含冲突事实与 A/B 检查点）

**破坏性变更**：否。CLAUDE.md 机器可读标记全部保留（审计入口检查通过）；意图层分档只放宽 personal 下限、不收紧任何既有义务；create_ver.py 仅输出编码行为变化，记录生成逻辑不变。

## 验证方式

- `python scripts/audit_logic_map.py . --current-state` → Static gate: PASS
- `python scripts/validate.py` → 无错误
- `python -m unittest tests.test_recall_cli tests.test_git_sync tests.test_validate` + `python tests/test_audit_logic_map.py` → 全部 OK
- CLAUDE.md 字符数 < 3000（审计器短指针阈值）

## 回滚方式

git revert 本次提交即可；除 create_ver.py 单函数外均为纯文档，无数据或运行时依赖。CHG-20260831-002 撤案时直接从 logic_change.md 删除条目并在本记录追加勘误说明。

## 经验与教训

- 修模板只救新项目：模板短路由化（P2）后，存量入口（本仓库 CLAUDE.md）不会自动变短，需要逐实例收尾。
- 与用户已确认规则冲突的"优化建议"，正确出口是 awaiting-decision 议案而不是实施——即使建议来自代理自己的评估、且用户笼统说了"认可"。
- "轻量是下限不是上限"的表述让分档兼容存量：已维护全量三层的项目不因新档位产生回退义务。

## 关联

- current_logic: logic_readme.md#RULE-014（分档语义）、RULE-008（编码合规）、RULE-019（入口指针纪律）
- proposal_id: CHG-20260831-002（本记录立案、未裁决）
- code/tests: CLAUDE.md; SKILL.md; references/governance-modes.md; scripts/create_ver.py; logic_change.md
