---
name: recall
description: 在修改、规划、诊断或审查项目逻辑时使用。读取项目根唯一的现行制度 `logic_readme.md` 与活跃议案 `logic_change.md`，再核对相关代码、测试和运行证据，按简单修复、中等变更和高风险变更分流。
---

# Recall

先恢复当前上下文，再决定是否修改。目标是让模型始终理解当前有效规则和正在讨论的改动，不是把每次开发变成文书流程。

**核心理念**：保存设计逻辑（为什么、取舍、影响），而非代码快照。代码版本由 Git 负责，Recall 负责"当初为什么这么设计"。详见 [逻辑回档 vs 代码回档](references/logic-vs-code-recall.md)。

## Git 自动同步

首次运行 `recall init` 时默认启用 Git 自动同步：脚本会写入仓库级 Git 同步策略，
安装受管理的 `post-commit` hook，并在配置完成后尝试同步当前分支。hook 先执行
`git pull --rebase --autostash`，再执行 `git push`；远端不可用或发生冲突时只发出
警告，不阻断已经完成的本地提交。

`recall sync` 默认自动保存：工作区有未提交变更时先以自动保存消息提交，再拉取
变基并推送（`recall.autoCommit`，默认开启）。用户选择手动时运行
`recall sync --manual`，此后仅在提供 `--commit-message "<message>"` 时才提交；
`recall sync --auto` 恢复自动保存。post-commit hook 场景永不自动提交其他脏文件，
只回填提交所引用决策记录的 `after_commit` 占位符后同步，保护部分提交工作流。
没有远端时，先配置 `git remote add origin <url>`，再运行 `recall sync`。可用
`recall init --no-auto-sync` 或 `recall sync --disable` 完全关闭。

## 核心原则（10 条）

1. 遵守用户的当前授权。未经授权不修改代码、制度或议案
2. 严格分离状态：`logic_readme.md` 是当前已生效制度；`logic_change.md` 是尚未生效的活跃议案；`logic_version/records/` 是关闭后的不可变决策记录。目标环境一旦实际启用新行为，必须在同一发布变更中更新 `logic_readme.md`、固化所需 `VER-*` 并关闭对应 CHG
3. 发布态只有项目根这一对现行文档。禁止创建 `logic_readme-v2.md` 或模块平行正文
4. `logic_version/` 只在当前文档直接引用、需要解释冲突或追溯兼容性时按 ID 读取。历史记录保存设计逻辑（为什么、取舍、影响），而非代码快照；目的是避免上下文膨胀
5. 新请求与现行规则、活跃议案或已确认意图存在实质矛盾，或模糊点会改变范围/语义/兼容/数据安全/方案选择时，先列明新旧来源、具体矛盾、可行选项、主要影响和建议，再向当前用户或授权决策方请求明确选择；确认前不得实施受影响部分。新增或调整用户可见功能时，还须对照 `logic_readme.md` 的功能意图与用户流程说明其流程位置和与相邻功能的关系；说不清位置视为此类模糊点
6. 每次代码改动都判断 `docs_impact`：当前规则、契约、稳定代码锚点、代码地图、验证入口或活跃议案实际变化时，在同一获授权变更中更新相应根文档；确无影响时说明 `none + 原因`
7. 风险决定分析和验证深度，不自动决定要填表。不要为了"符合流程"制造议案、ADR、版本记录或空测试矩阵
8. 引入适配层、全局开关、双读写或新抽象前，确认真实消费者或旧状态证据、说明最小修复为何不足，并给出唯一权威源、负责人、可验证退出条件和最晚复查日期。证据不足时默认不引入临时复杂度
9. 实施后的代码语义审查独立记录。它核对当前代码、调用方、Schema、测试结果和运行证据是否支持已确认方案；不能用用户确认、测试文件存在或静态审计通过替代
10. 先按简单、中等、高风险三条通道确定分析深度；不确定项若会改变方案、兼容性、数据安全或长期复杂度，则升级通道

## 三条变更通道

判断的关键：diff 是否触及 `logic_readme.md` 中标记为 `contract_class: public|persisted|security` 的路径。

| 通道 | 典型条件 | 修改前最低动作 | 文档与历史处理 |
|---|---|---|---|
| 简单修复 | 局部、隔离、不触及标记路径，且意图和测试直接明确 | 读相关规则、目标代码/直接调用方和直接测试；说明为何低风险 | 通常不创建 CHG/VER 记录；若当前规则、地图或验证入口实际变化，更新 `logic_readme.md` |
| 中等变更 | 触及标记路径但对外语义不变，或涉及多个相关文件但无未确认长期设计选择 | 先给出修改计划、受影响范围、约束与验证方式 | 实施后更新已变化的现行规则、地图和验证入口；需要跨会话协调或存在待确认方案时创建 CHG。规则或用户可见行为变化时保留精简 `VER-*` |
| 高风险变更 | 改变对外语义、涉及数据迁移/权限边界，或 adapter/全局开关/双读写 | 显式找消费者、相关历史决策、最小修改/结构修改/保持现状的取舍、迁移与回滚；确认当前议案版本后实施 | 在 `logic_change.md` 使用 `decision_gate: required`；完成后固化 `VER-*` |

分析后可以下调但需记录理由，上调无需说明。如 `logic_readme.md` 还没标注 `contract_class`，先判断目标路径是否有外部调用方，并在本次 `docs_impact` 中补齐。

简单通道不等于跳过上下文；高风险通道也不等于自动输出完整 Recall Brief。只有用户明确要求正式审查或表单合规时，才使用完整 Brief 与严格审计。

各家 plan 模式产出的计划按通道落盘：批准后、动代码前，`medium`/`high` 先把计划中的需求拆解与融入分析写入 CHG（`raw_request`/`decomposition`/`fit_analysis`），`simple` 直接实施不留痕；详见[外部工作流适配](references/workflow-integration.md)。

## 治理模式与字段层级

详见 [治理模式](references/governance-modes.md) 和 [字段词汇分层](references/field-vocabulary.md)。

- `personal`（默认）：8 个字段。单人或单人 + AI。不维护独立的语义审查与治理验证记录
- `collaborative`：+9 个字段。小团队有真实分工，且已配置 PR/CI/CODEOWNERS 等外部控制
- `compliance`：+13 个字段。用户明确要求正式审查、审计留存或表单合规

## 发布态文档模型

```text
<project-root>/
|-- logic_readme.md              # 唯一现行制度：全局规则、范围、代码地图与验证入口
|-- logic_change.md              # 唯一活跃议案：所有未生效 CHG-ID 的正文与索引
|-- AGENTS.md / CLAUDE.md        # 代理自动读取的短入口
|-- .agents/ / .claude/          # 专属配置/仓库技能；不存业务真源
`-- logic_version/
    |-- index.md                 # 历史索引，不是当前制度
    |-- records/                 # 不可变决策记录：logic_version-YYYYMMDD-NNN-<scope>.md
    |-- decisions/               # ADR
    `-- backups/                 # 受控快照和 manifest
```

`logic_readme.md` 用范围登记、稳定锚点和章节组织模块；代码目录不再创建本地副本。文件过长时压缩失效细节、把已结束内容归档到 `logic_version/`，而不是复制出第二套当前制度。

### logic_readme.md（唯一现行制度）

- 只写已经生效且当前可执行的职责、边界、规则、公共契约、真实消费者、不变量、兼容策略、稳定代码锚点、验证入口和负责人
- 每条规则保留一行可审计的 `why`、规则等级、决策记录链接和 `last_verified`。关键规则必须直接链接到有效 ADR 或不可变 `VER-*` 记录
- 代码地图表需标注 `contract_class: public|persisted|security|internal` 以支持可判定的通道分类
- 功能意图与用户流程层按条目模块化维护：`INT-*`（功能级用户目标）、`FLOW-*`（用户操作流程）、`UXI-*`（操作直觉约束），供需求拆解与融入分析对照；系统视角看代码地图，用户视角看本层
- 未生效方案、讨论、开放问题不写入本文件

### logic_change.md（唯一活跃议案）

- 整个项目只有一个文件。它可以有多个 `CHG-ID` 条目，但每个 CHG 只出现一个正文
- 只在以下情况创建或更新条目：用户要求追踪议案；存在尚未确认且会改变制度/方案的选择；多个工作项需要协调；或正式审查要求留下可审计结论
- 每项保持 `effective: false`。状态：`draft` | `awaiting-decision` | `implementing` | `verifying` | `promoting` | `blocked`
- `promoting` 状态记录晋升过渡期，带晋升检查清单，支持中断恢复。详见 [变更生命周期](references/change-lifecycle.md)

### logic_version/（逻辑回档的历史记录）

- 已结束且具有制度、行为或学习价值的变更生成一份 `logic_version/records/logic_version-YYYYMMDD-NNN-<scope>.md` 不可变记录
- **记录内容**：为什么这么设计、考虑过哪些方案（A/B/C）、为什么选择当前方案、影响了谁、如何验证和回滚
- **不记录**：完整代码快照、逐行 diff、原始对话、详细实现细节、隐藏思维链。代码版本由 Git 管理

## 默认上下文读取

对任何可能改变行为，或需要审查/解释既有设计的任务，按此顺序读取：

1. 先读根 `logic_readme.md` 的文档控制、范围登记、代码地图索引和功能意图与用户流程层，再按 `scope_path` 与稳定锚点读取相关规则、契约与不变量
2. 先读根 `logic_change.md` 的文档控制和活跃议案索引，再只读影响目标范围的 CHG 正文、`authority_surfaces`、`based_on`、依赖和冲突项
3. 目标代码、调用方、配置、Schema、测试和可获得的运行证据
4. 只有当前文件按 ID 引用、发生冲突或需要确定兼容策略时，读取对应的 ADR 或 `logic_version` 单条记录

根文档不存在时，报告知识基础缺失；可从代码、测试和既有文档重建当前事实，但不能声称已恢复设计原因。

在实际修改前，先确定所属通道，再按风险相称地完成判断。中等变更先交付计划与影响范围；高风险必须读取相关历史决策，完成迁移/回滚设计，并在实施前获得当前 `proposal_revision` 的确认。

## 调用模式

- `inspect`（默认日常审查）：只读说明当前行为、设计意图、消费者、约束、漂移和未知项。修改后的自审、设计原因追溯都走这里
- `formal-review`（明确要求时）：用户明确要求"正式审查""合规审查""完整 Recall""填表"或等价含义时，输出 Recall Brief，必要时使用完整 `logic_change.md` 模板和严格审计

审查的对象是此刻的系统，而不是过去每一次修改是否按模板完成。历史格式、旧审批字段和过往记录缺失不构成当前状态审查失败。

需要机器检查时运行：

```bash
# 当前状态检查（轻量）
python scripts/audit_logic_map.py <project-root> --current-state

# 正式审查（完整字段 + 测试矩阵）
python scripts/audit_logic_map.py <project-root> --formal-review
```

**审计脚本路径解析**：从 skill 安装目录 `references/../scripts/` 或消费项目根 `scripts/` 查找。需要 Python 3.7+。

审计器只能检查文档和静态线索，不能证明未声明的代码依赖、消费者、部署、外部权限控制、测试真实覆盖，或用户咨询确实发生。机器命令通过不等于代码审查通过。

## 参考文档

需要创建或更新文档时按需读取：

- [逻辑回档 vs 代码回档](references/logic-vs-code-recall.md)
- [字段词汇分层](references/field-vocabulary.md)
- [变更与决策生命周期](references/change-lifecycle.md)
- [治理模式](references/governance-modes.md)
- [logic_readme 模板](references/logic-readme-template.md)
- [logic_change 模板](references/logic-change-template.md)
- [logic_version 模板](references/logic-version-template.md)
- [ADR 模板](references/decision-record-template.md)
- [Recall Brief 模板](references/recall-brief-template.md)
- [外部工作流适配](references/workflow-integration.md)
- [代理入口模板](references/agent-entry-template.md)

## 代理入口

初始化 Codex 项目时，创建根 `AGENTS.md` 和 `.agents/`；初始化 Claude 项目时，创建根 `CLAUDE.md` 和 `.claude/`。

根入口只写短路由：修改、规划、诊断、审查，或解释"为什么这样设计"前，先读 `<project-root>/logic_readme.md` 和 `<project-root>/logic_change.md`，再读相关代码、测试和必要的运行证据。

专属目录只放工具配置、命令或仓库技能；不得把业务制度、议案、ADR 或历史复制进去。

若入口与逻辑文档冲突，入口只决定去哪里读；业务真源仍是根现行文档。系统、开发者和用户当前指令始终更高。
