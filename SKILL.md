---
name: recall
description: 在修改、规划、诊断或审查项目逻辑时使用。先读项目根的宪法 `logic_readme.md` 与根 `logic_change.md`，用 `recall route` 按需导入命中领域的部门法文档，再核对相关代码、测试和运行证据，按简单修复、中等变更和高风险变更分流。
---

# Recall

先恢复当前上下文，再决定是否修改。目标是让模型始终理解当前有效规则和正在讨论的改动，不是把每次开发变成文书流程。

**核心理念**：保存设计逻辑（为什么、取舍、影响），而非代码快照。代码版本由 Git 负责，Recall 负责"当初为什么这么设计"（[逻辑回档 vs 代码回档](references/logic-vs-code-recall.md)）。

**日常路由只需先回答一个问题**：这次 diff 会不会触及 `logic_readme.md` 里标记 `contract_class: public|persisted|security` 的路径，或某个活跃 CHG 的范围？不触及且意图、测试直接明确 → 简单修复；触及 → 中等/高风险，先计划再实施。

本文件只保留路由、通道、原则与命令；目录模型、Git 同步、治理模式、项目接入等细节按需读 [references/](#按需读取)（RULE-022）。文档分两级（RULE-018）：根 `logic_readme.md` 是**宪法**（全局规则、功能意图、领域目录），每个任务必读；`logic_domains/<domain>/` 是**部门法**（领域 readme + change 成对），只读任务命中的领域。规则语义的权威是宪法或所属领域 `logic_readme.md` 的规则行，其他位置只放指针（RULE-019）。

## 三条变更通道

| 通道 | 典型条件 | 修改前最低动作 | 文档与历史处理 |
|---|---|---|---|
| 简单修复 | 局部、隔离、不触及标记路径，且意图和测试直接明确 | 读相关规则、目标代码/直接调用方和直接测试；说明为何低风险 | 通常不创建 CHG/VER；若当前规则、地图或验证入口实际变化，更新 `logic_readme.md` |
| 中等变更 | 触及标记路径但对外语义不变，或涉及多个相关文件但无未确认长期设计选择 | 先给出修改计划、受影响范围、约束与验证方式 | 实施后更新已变化的现行规则、地图和验证入口；需跨会话协调或有待确认方案时创建 CHG。规则或用户可见行为变化时保留精简 `VER-*` |
| 高风险变更 | 改变对外语义、涉及数据迁移/权限边界，或 adapter/全局开关/双读写 | 显式找消费者、相关历史决策、最小修改/结构修改/保持现状的取舍、迁移与回滚；确认当前议案版本后实施 | 在 `logic_change.md` 使用 `decision_gate: required`；完成后固化 `VER-*` |

分析后可以下调但需记录理由，上调无需说明。`logic_readme.md` 尚无 `contract_class` 标注时，先判断目标路径是否有外部调用方，并在本次 `docs_impact` 中补齐。

三条通道的收尾义务相同（核心原则 12）：`simple` 在最终汇报列出本次新建文件的处置清单；`medium`/`high` 在 `logic_temp.md` 的工作区产物台账登记并清零后才能关闭 CHG。

简单通道不等于跳过上下文；高风险通道也不等于自动输出完整 Recall Brief。只有用户明确要求正式审查或表单合规时，才使用完整 Brief 与严格审计。各家 plan 模式产出的计划按通道落盘：批准后、动代码前，`medium`/`high` 先把需求拆解与融入分析写入 CHG（`raw_request`/`decomposition`/`fit_analysis`），`simple` 直接实施不留痕（[外部工作流适配](references/workflow-integration.md)）。

## 默认上下文读取

对任何可能改变行为，或需要审查/解释既有设计的任务，按此顺序读取：

1. 宪法：根 `logic_readme.md` 全文（全局规则、范围登记表即领域目录、功能意图与用户流程层）
2. 根 `logic_change.md`：修宪议案正文 + 全项目活跃议案索引（公报），看哪些在办议案触及目标领域
3. `recall route <目标路径或关键词>`：按命中领域读 `logic_domains/<domain>/logic_readme.md`（该领域规则、代码地图、测试）与同目录 `logic_change.md`（一事一议的 CHG 正文）；跨领域变更读全部相关领域，根规章优先；命令同时给出行数与估算 token，便于控制上下文
4. 目标代码、调用方、配置、Schema、测试和可获得的运行证据
5. 只有当前文件按 ID 引用、发生冲突或需要确定兼容策略时，读取对应的 ADR 或 `logic_version` 单条记录

根文档不存在时，报告知识基础缺失；可从代码、测试和既有文档重建当前事实，但不能声称已恢复设计原因。宪法未登记任何领域时（`constitution-without-domains` 提示），先按[项目接入流程](references/project-onboarding.md)建至少一个领域再补规则。中等变更先交付计划与影响范围；高风险必须读取相关历史决策，完成迁移/回滚设计，并在实施前获得当前 `proposal_revision` 的确认。

## 核心原则（12 条）

1. 遵守用户的当前授权。未经授权不修改代码、制度或议案
2. 严格分离状态：`logic_readme.md` 是当前已生效制度；`logic_change.md` 是尚未生效的活跃议案；`logic_version/records/` 是关闭后的不可变决策记录。目标环境一旦实际启用新行为，必须在同一发布变更中更新 `logic_readme.md`、固化所需 `VER-*` 并关闭对应 CHG
3. 两级文档（RULE-018）：根 `logic_readme.md` 是宪法、根 `logic_change.md` 是修宪账本 + 全项目公报；每个领域在 `logic_domains/<domain>/` 有一对已登记的 readme + change，领域事务的 CHG 立在领域账本、触及宪法的立在根账本，同一 CHG 正文只在一处；无论项目大小至少一个领域，领域过大拆小部门；`logic_version/` 全项目唯一。禁止创建 `logic_readme-v2.md` 或任何未登记的平行正文
4. `logic_version/` 只在当前文档直接引用、需要解释冲突或追溯兼容性时按 ID 读取。历史记录保存设计逻辑，而非代码快照
5. 新请求与现行规则、活跃议案或已确认意图存在实质矛盾，或模糊点会改变范围/语义/兼容/数据安全/方案选择时，先列明新旧来源、具体矛盾、可行选项、主要影响和建议，再向当前用户或授权决策方请求明确选择；确认前不得实施受影响部分。新增或调整用户可见功能时，还须对照 `logic_readme.md` 的功能意图与用户流程说明其流程位置和与相邻功能的关系；说不清位置视为此类模糊点。**用户的表述就是宪法的来源**：用户提出的目标、约束或操作习惯先对照意图层（INT/UXI），已有则复用，没有则先立修宪案登记（`来源: user:日期`）再做领域工作；AI 推断的意图标 `inferred`/`code-derived`，不得冒充用户确认（RULE-014/016）。同一规则有多个议案时，各议案写 `authority_surfaces: RULE-xxx` 并互指 `conflicts_with`，由用户裁定 supersede/merge/排序；规则在议案之后被修订则重核 `based_on`（`recall conflicts`、审计 `shared-rule-target` / `rule-changed-after-proposal`）
6. 每次代码改动都判断 `docs_impact`：当前规则、契约、稳定代码锚点、代码地图、验证入口或活跃议案实际变化时，在同一获授权变更中更新所属文档（领域规则改领域 readme，全局规则/意图层/登记表改宪法）；确无影响时说明 `none + 原因`
7. 风险决定分析和验证深度，不自动决定要填表。不要为了"符合流程"制造议案、ADR、版本记录或空测试矩阵
8. 引入适配层、全局开关、双读写或新抽象前，确认真实消费者或旧状态证据、说明最小修复为何不足，并给出唯一权威源、负责人、可验证退出条件和最晚复查日期。证据不足时默认不引入临时复杂度
9. 实施后的代码语义审查独立记录。它核对当前代码、调用方、Schema、测试结果和运行证据是否支持已确认方案；不能用用户确认、测试文件存在或静态审计通过替代
10. 先按简单、中等、高风险三条通道确定分析深度；不确定项若会改变方案、兼容性、数据安全或长期复杂度，则升级通道
11. 会话默认延续：新会话或上下文压缩后，以现行 logic 文档与活跃议案为准继续工作（新会话视作新人接手既有项目，文档即交接），不要求用户重述背景；仅当用户明确指出现行规则或代码有问题时才修改现行制度。模糊点按原则 5 先分析、给出建议，再咨询（RULE-017）
12. 收尾归零：任务的完成态是"交付物就位 + 本次新建的非交付物（探针脚本、临时测试、草稿、调试输出）已删除或经用户同意保留 + 最终汇报列出处置清单"。`medium`/`high` 通道必建 `logic_version/working/<version_slug>/logic_temp.md` 并在"工作区产物台账"登记去留，台账清零才能关闭 CHG 并删除 working 目录；`simple` 通道只在汇报中列清单。工具绝不静默删除文件（RULE-020）

## 调用模式与机器检查

- `inspect`（默认日常审查）：只读说明当前行为、设计意图、消费者、约束、漂移和未知项。修改后的自审、设计原因追溯都走这里
- `formal-review`（明确要求时）：用户明确要求"正式审查""合规审查""完整 Recall""填表"或等价含义时，输出 [Recall Brief](references/recall-brief-template.md)，必要时使用完整 `logic_change.md` 模板和严格审计

审查的对象是此刻的系统，而不是过去每一次修改是否按模板完成。历史格式、旧审批字段和过往记录缺失不构成当前状态审查失败。

```bash
recall audit                      # 当前状态静态门（轻量，= python scripts/audit_logic_map.py <root> --current-state）
recall audit --formal-review      # 正式审查（完整字段 + 测试矩阵）；其余审计器参数原样透传，如 --json
recall route <路径|关键词>   # 本次应读的文档清单（宪法 + 命中领域）与估算 token；--json 供代理解析
recall validate   # 宪法与领域编号空间、跨账本 CHG 与公报、VER 一致性、漂移度量、未跟踪残留与未推送告警
recall status     # 领域数、各账本议案计数、记录计数，分列未提交、未跟踪（待处置）、未推送
```

审计脚本从 skill 安装目录 `scripts/` 或消费项目根 `scripts/` 解析，须整目录部署（`audit_logic_map.py` 是分层包 `recall_audit/` 的入口）；Python 3.11+。审计器只能检查文档和静态线索，不能证明未声明的代码依赖、消费者、部署、外部权限控制、测试真实覆盖，或用户咨询确实发生。机器命令通过不等于代码审查通过。`status`/`validate` 只提示、不删除、不推送。

## 按需读取

| 何时 | 读哪份 |
|---|---|
| 创建、拆分或压缩 logic 文档；想知道目录里每份文件写什么不写什么；代理入口 | [发布态文档模型](references/document-model.md)、[领域文档模板](references/logic-domain-template.md)、[代理入口模板](references/agent-entry-template.md) |
| 初始化 Git 管道、排查同步、判断"谁负责推送"、after_commit 回填 | [Git 自动同步与推送责任](references/git-sync.md)（RULE-010/011/013） |
| 决定 personal / collaborative / compliance 用哪些字段；行数上限 | [治理模式](references/governance-modes.md)、[字段词汇分层](references/field-vocabulary.md) |
| 新项目或存量项目接入、模块补全、领域划分与拆分步骤 | [项目接入流程](references/project-onboarding.md)（RULE-016/018） |
| CHG 状态机、晋升清单、关闭与归档步骤 | [变更与决策生命周期](references/change-lifecycle.md) |
| 对接 plan 模式、Spec、Steering 等外部工件 | [外部工作流适配](references/workflow-integration.md) |
| 需要填写文档 | [logic_readme 模板](references/logic-readme-template.md)、[logic_change 模板](references/logic-change-template.md)、[logic_version 模板](references/logic-version-template.md)、[ADR 模板](references/decision-record-template.md)、[logic_temp 模板](references/logic-temp-template.md) |

首次接入运行 `recall init`（建 Git 管道并默认启用自动同步）；自动同步未启用的仓库，提交后须自行推送、不得让本地长期领先远端（RULE-010）。日常命令见 `recall help`。
