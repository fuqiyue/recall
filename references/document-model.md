# 发布态文档模型

本文承载 SKILL.md 按需下沉的文档模型细节（RULE-022 按需披露）。规则语义的权威仍是本技能目录 `logic_readme.md` 的规则行（RULE-019）；这里只描述目录形态与每份文档"写什么、不写什么"。需要创建、拆分或压缩 logic 文档时再读。

## 目录形态

```text
<project-root>/
|-- logic_readme.md              # 总规章：全局规则、范围路由、代码地图与验证入口
|-- logic_change.md              # 唯一活跃议案：所有未生效 CHG-ID 的正文与索引
|-- <module>/logic_readme.md     # 子模块正文（可选；经用户确认拆分并登记 readme-only 后存在）
|-- AGENTS.md / CLAUDE.md        # 代理自动读取的短入口
|-- .agents/ / .claude/          # 专属配置/仓库技能；不存业务真源
`-- logic_version/
    |-- index.md                 # 历史索引，不是当前制度
    |-- records/                 # 不可变决策记录：logic_version-YYYYMMDD-NNN-<scope>.md
    |-- decisions/               # ADR（可选；personal 模式默认为空）
    |-- working/<version_slug>/  # 议案期 logic_temp.md：工作笔记 + 收尾台账（gitignore，关闭即删）
    `-- backups/                 # 受控快照和 manifest
```

`logic_readme.md` 优先用范围登记、稳定锚点和章节组织模块；文件过长时先压缩失效细节、把已结束内容归档到 `logic_version/`。长度目标与硬上限见[字段词汇分层](field-vocabulary.md)；`audit_logic_map.py --current-state` 的 Density 段会在越过目标值时给出提示。

子文档拆分的权威语义见 RULE-018，操作流程见[项目接入流程](project-onboarding.md)的模块拆分章节；涉及子模块的修改先读根后读子，跨模块变更在同一变更中更新全部相关子文档。规范的语义正文只存在于 logic_readme 的规则行，其他文档只保留指针与操作步骤（RULE-019）；禁止复制出第二套未登记的当前制度。

## logic_readme.md（唯一现行制度）

- 只写已经生效且当前可执行的职责、边界、规则、公共契约、真实消费者、不变量、兼容策略、稳定代码锚点、验证入口和负责人
- 每条规则保留一行可审计的 `why`、规则等级、决策记录链接和 `last_verified`。关键规则必须直接链接到不可变 `VER-*` 记录或有效 ADR（personal 模式默认只产出 `VER-*`，见[治理模式](governance-modes.md)）
- 代码地图表需标注 `contract_class: public|persisted|security|internal` 以支持可判定的通道分类
- 功能意图与用户流程层按条目模块化维护：`INT-*`（功能级用户目标）、`FLOW-*`（用户操作流程）、`UXI-*`（操作直觉约束），供需求拆解与融入分析对照；系统视角看代码地图，用户视角看本层。维护深度按治理模式分档：`personal` 用轻量档（INT 必维护、FLOW 可合并、UXI 按需），`collaborative` 及以上全量维护，档位定义见[治理模式](governance-modes.md)
- 未生效方案、讨论、开放问题不写入本文件

模板：[logic_readme 模板](logic-readme-template.md)。

## logic_change.md（唯一活跃议案）

- 整个项目只有一个文件。它可以有多个 `CHG-ID` 条目，但每个 CHG 只出现一个正文
- 只在以下情况创建或更新条目：用户要求追踪议案；存在尚未确认且会改变制度/方案的选择；多个工作项需要协调；或正式审查要求留下可审计结论
- 每项保持 `effective: false`。状态：`draft` | `awaiting-decision` | `implementing` | `verifying` | `promoting` | `blocked`
- `promoting` 状态记录晋升过渡期，带晋升检查清单，支持中断恢复。详见[变更生命周期](change-lifecycle.md)

模板：[logic_change 模板](logic-change-template.md)。

## logic_version/（逻辑回档的历史记录）

- 已结束且具有制度、行为或学习价值的变更生成一份 `logic_version/records/logic_version-YYYYMMDD-NNN-<scope>.md` 不可变记录
- **记录内容**：为什么这么设计、考虑过哪些方案（A/B/C）、为什么选择当前方案、影响了谁、如何验证和回滚
- **不记录**：完整代码快照、逐行 diff、原始对话、详细实现细节、隐藏思维链。代码版本由 Git 管理

模板：[logic_version 模板](logic-version-template.md)（唯一决策记录模板，含扩展 schema）；索引与临时文件模板见[logic_version 索引模板](logic-version-index-template.md)、[logic_temp 模板](logic-temp-template.md)、[备份清单模板](backup-manifest-template.md)。

## 代理入口

初始化 Codex 项目时，创建根 `AGENTS.md` 和 `.agents/`；初始化 Claude 项目时，创建根 `CLAUDE.md` 和 `.claude/`。根入口只写短路由：修改、规划、诊断、审查，或解释"为什么这样设计"前，先读 `<project-root>/logic_readme.md` 和 `<project-root>/logic_change.md`，再读相关代码、测试和必要的运行证据。专属目录只放工具配置、命令或仓库技能；不得把业务制度、议案、ADR 或历史复制进去。若入口与逻辑文档冲突，入口只决定去哪里读；业务真源仍是根现行文档。系统、开发者和用户当前指令始终更高。

模板：[代理入口模板](agent-entry-template.md)。
