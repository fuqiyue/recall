# 发布态文档模型

本文承载 SKILL.md 按需下沉的文档模型细节（RULE-022 按需披露）。规则语义的权威仍是本技能目录 `logic_readme.md` 的规则行（RULE-019）；这里只描述目录形态与每份文档"写什么、不写什么"。需要创建、拆分或压缩 logic 文档时再读。

## 目录形态（一二级拆分法，RULE-018）

```text
<project-root>/
|-- logic_readme.md                  # 一级·宪法：全局规则、功能意图层、领域目录（范围登记表）、INV、有效决策索引
|-- logic_change.md                  # 一级账本：修宪议案正文 + 全项目活跃议案索引（公报）
|-- logic_domains/<domain>/
|   |-- logic_readme.md              # 二级·部门法：该领域的规则、代码地图、测试；职权由 owned_paths 声明
|   `-- logic_change.md              # 二级账本：该领域一事一议的 CHG 正文
|-- AGENTS.md / CLAUDE.md            # 代理自动读取的短入口
|-- .agents/ / .claude/              # 专属配置/仓库技能；不存业务真源
`-- logic_version/                   # 全项目只有根一份，不按领域拆
    |-- index.md                     # 历史索引，不是当前制度
    |-- records/                     # 不可变决策记录：logic_version-YYYYMMDD-NNN-<scope>.md
    |-- decisions/                   # ADR（可选；personal 模式默认为空）
    |-- working/<version_slug>/      # 议案期 logic_temp.md：工作笔记 + 收尾台账（gitignore，关闭即删）
    `-- backups/                     # 受控快照和 manifest
```

**每个项目都是两级**，不分大小：至少登记一个领域（小项目可用 `logic_domains/core/` 一个领域覆盖全部代码）。宪法每个任务必读；部门法按需导入——改哪个领域读哪份。

- **宪法（根 `logic_readme.md`）写什么**：全局规则（跨领域契约、治理、文档制度）、功能意图与用户流程层（INT/FLOW/UXI）、领域目录即范围登记表（每个领域一行：`membership: in-system`、`doc_policy: paired`、`scope_type/layer: domain/runtime-code`，链接该领域的两份文档）、不可破坏约束 INV、有效决策索引。不写领域内部的规则细节与代码地图行。
- **部门法（`logic_domains/<domain>/logic_readme.md`）写什么**：`owned_paths` 声明的职权路径，以及这些路径的规则行、代码地图行、测试与验证行；不含 root-only 字段与范围登记表。大部门制：规则少时一个领域兼管多项职责；领域文档越过目标行数时拆成更小的领域（大部门拆小部门）。
- **每级一份账本**：根 `logic_change.md` 只放修宪议案（改全局规则、INT 层、登记表行、INV 的 CHG）正文，外加全项目活跃议案索引（公报）；领域账本放本领域一事一议的 CHG 正文。一个 CHG 正文只存在于一个账本；领域 CHG 的 `affected_scopes` 必含自身 `scope_path`、不得含 `.`（触及宪法就应立在根账本）；跨领域 CHG 正文放主领域，其余领域列入 `affected_scopes`。
- **未登记即平行真源**：`logic_domains/` 下未在宪法登记表登记的文档违反 INV-001/INV-002，审计静态门拒绝。存量 `readme-only` 子文档仍被工具接受，但不再是推荐形态；新拆分一律用 paired 领域。

**读取顺序（按需导入）**：1) 根 `logic_readme.md`（宪法，必读）→ 2) 根 `logic_change.md`（修宪案 + 公报，必读，体量小）→ 3) `recall route <目标路径或关键词>` 打印应读的领域 readme/change 及行数与估算 token，只读命中的领域 → 4) 代码与测试 → 5) `logic_version/` 仅在现行文档引用时按 ID 读取。

各级文档的长度目标与硬上限见[字段词汇分层](field-vocabulary.md)的"长度上限"；`audit_logic_map.py --current-state` 的 Density 段按层级报告越过目标值的文件，领域 readme 越过目标即提示拆分，宪法未登记任何领域时报告 `constitution-without-domains`。规范的语义正文只存在于 logic_readme 的规则行，其他文档只保留指针与操作步骤（RULE-019）；领域划分与拆分的操作流程见[项目接入流程](project-onboarding.md)，领域文档模板见[领域文档模板](logic-domain-template.md)。

## logic_readme.md（每级一份现行制度）

- 只写已经生效且当前可执行的职责、边界、规则、公共契约、真实消费者、不变量、兼容策略、稳定代码锚点、验证入口和负责人；宪法写全局层，部门法写自身职权范围，同一规则不在两级重复
- 每条规则保留一行可审计的 `why`、规则等级、决策记录链接和 `last_verified`。关键规则必须直接链接到不可变 `VER-*` 记录或有效 ADR（personal 模式默认只产出 `VER-*`，见[治理模式](governance-modes.md)）
- 代码地图表需标注 `contract_class: public|persisted|security|internal` 以支持可判定的通道分类
- 功能意图与用户流程层只在宪法维护，按条目模块化：`INT-*`（功能级用户目标）、`FLOW-*`（用户操作流程）、`UXI-*`（操作直觉约束），供需求拆解与融入分析对照；系统视角看各领域代码地图，用户视角看本层。维护深度按治理模式分档：`personal` 用轻量档（INT 必维护、FLOW 可合并、UXI 按需），`collaborative` 及以上全量维护，档位定义见[治理模式](governance-modes.md)
- RULE/INT 编号空间全项目唯一（宪法与全部领域共用），`recall validate` 跨文档检查撞号
- 未生效方案、讨论、开放问题不写入本文件

模板：[logic_readme 模板](logic-readme-template.md)（宪法）、[领域文档模板](logic-domain-template.md)（部门法）。

## logic_change.md（每级一份）

- 每份 `logic_readme.md` 配一份 `logic_change.md`。根账本承载修宪议案正文与全项目活跃议案索引（公报：任何账本中的每个活跃 CHG 一行，领域 CHG 行的 `proposal_path` 链接到 `logic_domains/<domain>/logic_change.md#chg-...`）；领域账本承载本领域一事一议的 CHG 正文，同一领域的 CHG 都在同一账本
- 每个 CHG 只有一个正文，所属账本即其唯一位置；`recall validate` 会提示缺少公报行的领域 CHG，`recall status` 显示领域数与各账本 CHG 数
- 只在以下情况创建或更新条目：用户要求追踪议案；存在尚未确认且会改变制度/方案的选择；多个工作项需要协调；或正式审查要求留下可审计结论
- 每项保持 `effective: false`。状态：`draft` | `awaiting-decision` | `implementing` | `verifying` | `promoting` | `blocked`
- `promoting` 状态记录晋升过渡期，带晋升检查清单，支持中断恢复。详见[变更生命周期](change-lifecycle.md)

模板：[logic_change 模板](logic-change-template.md)（根账本；领域账本的精简形态见[领域文档模板](logic-domain-template.md)）。

## logic_version/（逻辑回档的历史记录）

- 已结束且具有制度、行为或学习价值的变更生成一份 `logic_version/records/logic_version-YYYYMMDD-NNN-<scope>.md` 不可变记录
- **记录内容**：为什么这么设计、考虑过哪些方案（A/B/C）、为什么选择当前方案、影响了谁、如何验证和回滚
- **不记录**：完整代码快照、逐行 diff、原始对话、详细实现细节、隐藏思维链。代码版本由 Git 管理

模板：[logic_version 模板](logic-version-template.md)（唯一决策记录模板，含扩展 schema）；索引与临时文件模板见[logic_version 索引模板](logic-version-index-template.md)、[logic_temp 模板](logic-temp-template.md)、[备份清单模板](backup-manifest-template.md)。

## 代理入口

初始化 Codex 项目时，创建根 `AGENTS.md` 和 `.agents/`；初始化 Claude 项目时，创建根 `CLAUDE.md` 和 `.claude/`。根入口只写短路由：修改、规划、诊断、审查，或解释"为什么这样设计"前，先读 `<project-root>/logic_readme.md` 和 `<project-root>/logic_change.md`，再用 `recall route` 定位并只读命中的领域文档，然后读相关代码、测试和必要的运行证据。专属目录只放工具配置、命令或仓库技能；不得把业务制度、议案、ADR 或历史复制进去。若入口与逻辑文档冲突，入口只决定去哪里读；业务真源仍是根现行文档与已登记领域文档。系统、开发者和用户当前指令始终更高。

模板：[代理入口模板](agent-entry-template.md)。
