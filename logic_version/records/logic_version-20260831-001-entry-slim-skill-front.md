# VER-20260831-001: 入口模板短路由化、SKILL 首屏重排与 personal 模式 ADR 可选澄清

## 记录控制

- version_id: VER-20260831-001
- version_slug: logic_version-20260831-001-entry-slim-skill-front
- status: effective
- date: 2026-08-31
- change_id: none
- before_commit: 780f8ed
- after_commit: _待填写_

## 为什么做这个决策？

**背景**：
用户以信息分层视角审查 Recall 工作流的易用性，发现三处分层缺陷：(1) 消费项目的 CLAUDE.md/AGENTS.md 入口由模板生成后是约 1000 字的完整制度复述，违背 SKILL.md"根入口只写短路由"的既有约定，每个会话首屏都是规则墙；(2) SKILL.md 首屏被安装期信息（Git 自动同步、项目接入）占据，日常使用最需要的通道判定表排在中部；(3) personal 模式下 `logic_version/decisions/` 长期为空，与检查清单里的 ADR 提问并置，让使用者误以为存在未履行的 ADR 义务（实际制度原文一直是"ADR 或 VER 二选一"）。

**用户需求/反馈**：
2026-08-31 会话：用户认可入口瘦身与议案清淤方向（P0/P1，由另一会话在消费项目执行），对 P2（技能仓库侧优化）表示"不太理解，请帮我解决"，授权本会话解释并实施。

**需求拆解（归档时从 CHG 原样搬入；无 CHG 的记录填 none）**：
- raw_request: 2026-08-31 用户会话——"按信息分层理论分析工作流是否符合用户直觉、简单易用，认可 P0/P1，P2 请帮我解决/优化"
- decomposition: ① agent-entry-template.md 两个入口块改为五条短路由（保留 RECALL_* 机器标记）；② SKILL.md 重排为"路由一问 → 三通道表 → 默认读取 → 原则"首屏结构，安装期章节下沉；③ 跨仓库 RULE 指针改为指向本技能目录内文件并注明编号归属；④ personal 模式 ADR 可选写入 governance-modes.md 与 SKILL.md
- fit_analysis: 强化 INT-20260816-003（文档三件套阅读——降低每次读取成本）；不新增 INT；不触碰 UXI 条目；FLOW-002#1 的阅读入口不变，仅内容变短

## 决策过程

**方案 A**：只改消费项目（eduai）的入口实例，不动模板（优点：零风险；缺点：下一个项目接入时规则墙复现，治标不治本；复杂度：低）

**方案 B**：入口模板改为短路由 + SKILL.md 首屏重排 + ADR 可选澄清，语义全部保留在 SKILL/logic_readme（优点：根治且符合 RULE-019 引用纪律——入口本就不该是制度副本；缺点：未安装技能的代理从入口拿到的细节变少；复杂度：中）

**方案 C**：入口保持全文复述并继续加内容（优点：无技能代理信息最全；缺点：与"短路由"约定和 RULE-019 直接矛盾，规则墙持续膨胀；复杂度：低）

**选中方案与原因**：
选 B。入口的职责是路由不是制度副本（SKILL.md 代理入口章节 + RULE-019 早已如此规定，模板与之漂移才是缺陷）；无技能代理的兜底通过入口内保留的五条最小协议（读取顺序、三通道、冲突上报、docs_impact、真源位置）实现。ADR 部分是澄清而非制度变更：原文一直是"ADR 或 VER"，本次仅把"personal 模式默认只用 VER、decisions/ 允许为空"写成显式文字，消除空目录被误读为欠账的困惑。

## 影响范围

**修改的文件/模块**：
- `references/agent-entry-template.md` - 两个入口块从约 25 行制度复述压缩为 5 条短路由（保留 RECALL_* 机器标记与边界节），新增"未安装技能代理按五条最小协议执行"边界
- `SKILL.md` - 章节重排（三通道/默认读取上移，Git 同步/项目接入下沉），新增首屏"路由一问"，跨仓库 RULE-010/011/013/018/019 指针改为"本技能目录 logic_readme.md"，decisions/ 树注释与关键规则链接句注明 personal 模式 ADR 可选；行数 169→170，未触及 200 行上限
- `references/governance-modes.md` - personal 节新增"决策记录只用 VER-*，不要求 ADR，decisions/ 允许为空"

**破坏性变更**：否。SKILL.md 全部规范语义原文保留（核心原则编号不变，RULE-016/017 引用的"接入章节""核心原则 11"锚点仍在）；已生成入口的存量项目不受影响，可择机换用新短入口。

## 验证方式

- `python scripts/audit_logic_map.py . --current-state` → Static gate: PASS（SKILL.md 200 行上限内）
- `python scripts/validate.py` → 无错误（19 规则、11 INT、5 FLOW 校验通过）
- `python tests/test_audit_logic_map.py`（69 OK）、`tests.test_validate`（7 OK）、`tests.test_git_sync`（20 OK）、`tests.test_recall_cli`（UTF-8 下 13 OK；GBK 控制台下 2 个既有 emoji 打印错误经 git stash 基线验证与本次修改无关）

## 回滚方式

git revert 本次提交即可；三个文件均为纯文档，无数据或运行时依赖。存量项目未同步换入口时无需任何回滚动作。

## 经验与教训

- 模板是入口膨胀的上游：只修实例（消费项目的 CLAUDE.md）会在下一次 `recall init` 复现，模板与既有规则（"短路由"）的漂移才是根因。
- "允许为空"的目录要显式写进制度，否则空目录 + 检查清单提问会被使用者解读成未履行的义务。
- 既有缺陷（create_ver.py 在 GBK 控制台打印 emoji 崩溃，违反 RULE-008 精神）在本次验证中暴露，未在本记录范围内修复，留待独立小修。

## 关联

- current_logic: logic_readme.md#RULE-018, logic_readme.md#RULE-019（指针改写遵循）；references/governance-modes.md（ADR 可选）
- proposal_id: none
- code/tests: SKILL.md; references/agent-entry-template.md; references/governance-modes.md; tests/test_audit_logic_map.py
