# Codex / Claude 项目入口与初始化模板

这些入口只负责规定读取顺序和知识写入位置。入口是短路由，不是制度副本：完整工作流语义只存在于 recall 技能（SKILL.md）与项目根现行文档，不要把业务规则、议案正文或历史复制到入口或代理专属目录。更新已有入口时合并必要段落，不覆盖其他有效指令。

## 初始化目标

```text
<project-root>/
|-- AGENTS.md                 # Codex 自动发现的项目入口
|-- CLAUDE.md                 # Claude 自动发现的项目入口
|-- .agents/                  # Codex 专属配置或仓库技能
`-- .claude/                  # Claude 专属配置或命令
```

- 初始化 Codex 时创建 `.agents/` 和根 `AGENTS.md`。
- 初始化 Claude 时创建 `.claude/` 和根 `CLAUDE.md`。
- 同时使用两者时创建四项。根入口是自动读取的跳板；`.agents/` 与 `.claude/` 不能替代它。
- 专属目录只保存工具配置、命令、缓存或仓库技能。它们不得保存 `logic_readme.md`、`logic_change.md`、ADR、版本记录或业务规则副本。

## 根 AGENTS.md 中的最小入口

~~~markdown
## Project Logic Recall

Before planning, editing, diagnosing, reviewing, or explaining an existing design in this project:

RECALL_ROOT_ORDER: <project-root>/logic_readme.md -> <project-root>/logic_change.md
RECALL_CHANGE_EFFECTIVE: false
RECALL_BUSINESS_TRUTH: project-root-current-logic-docs
RECALL_HISTORY_ROOT: <project-root>/logic_version
RECALL_AGENT_CONFIG_ROOT: <project-root>/.agents

1. Read the relevant sections of root `logic_readme.md` (current effective policy) and `logic_change.md` (non-effective proposals), then run `recall route <target paths>` and read only the matched `logic_domains/<domain>/logic_readme.md` + `logic_change.md`, then the affected code, callers, configuration, and tests, before changing behavior. Load `logic_version/` history only when the current docs reference it.
2. Route the change as `simple` / `medium` / `high` before editing. `medium` requires presenting plan, impact, and verification first; `high` additionally requires real-consumer and history review, migration/rollback comparison, and user confirmation of the current proposal revision.
3. On material conflict with current policy, an active proposal, or confirmed intent — or ambiguity that changes scope, semantics, compatibility, or data safety — list sources, the exact contradiction, options, impacts, and a recommendation, then ask the user before editing the affected area.
4. After a code change, update the relevant tests, run them, and report results plus `docs_impact`; update root `logic_readme.md` whenever current rules, map anchors, contracts, or validation obligations actually changed.
5. Full workflow semantics live in the recall skill (SKILL.md). Tool-specific folders (`.agents/`, `.claude/`, `.codex/`) hold configuration only — never current policy, proposals, ADRs, or history.
~~~

## 根 CLAUDE.md 中的最小入口

~~~markdown
## Project Logic Recall

Before planning, editing, diagnosing, reviewing, or explaining an existing design in this project:

RECALL_ROOT_ORDER: <project-root>/logic_readme.md -> <project-root>/logic_change.md
RECALL_CHANGE_EFFECTIVE: false
RECALL_BUSINESS_TRUTH: project-root-current-logic-docs
RECALL_HISTORY_ROOT: <project-root>/logic_version
RECALL_AGENT_CONFIG_ROOT: <project-root>/.claude

1. Read the relevant sections of root `logic_readme.md` (current effective policy) and `logic_change.md` (non-effective proposals), then run `recall route <target paths>` and read only the matched `logic_domains/<domain>/logic_readme.md` + `logic_change.md`, then the affected code, callers, configuration, and tests, before changing behavior. Load `logic_version/` history only when the current docs reference it.
2. Route the change as `simple` / `medium` / `high` before editing. `medium` requires presenting plan, impact, and verification first; `high` additionally requires real-consumer and history review, migration/rollback comparison, and user confirmation of the current proposal revision.
3. On material conflict with current policy, an active proposal, or confirmed intent — or ambiguity that changes scope, semantics, compatibility, or data safety — list sources, the exact contradiction, options, impacts, and a recommendation, then ask the user before editing the affected area.
4. After a code change, update the relevant tests, run them, and report results plus `docs_impact`; update root `logic_readme.md` whenever current rules, map anchors, contracts, or validation obligations actually changed.
5. Full workflow semantics live in the recall skill (SKILL.md). Tool-specific folders (`.claude/`, `.agents/`, `.codex/`) hold configuration only — never current policy, proposals, ADRs, or history.
~~~

## 边界

- 项目根入口负责自动发现与路由；子目录代理文件只在确有工具作用域需求时使用，并继续指向同一项目根真源。
- 当前制度与活跃议案只能位于项目根与已登记的 `logic_domains/<domain>/`（RULE-018）；ADR、历史和临时协调记录只能位于根 `logic_version/`。`.agents/`、`.claude/` 和 `.codex/` 可以保存工具设置、权限、命令或缓存，但不能保存业务真源。
- 未安装 recall 技能的代理仍按入口中的五条最小协议执行；意图提炼、需求保全、通道细则等完整语义在安装技能后由 SKILL.md 提供。
- `owner`、`changed_by`、`decision_confirmed_by` 和 `semantic_reviewed_by` 是责任和来源记录，不授予文件、分支或部署权限。真实权限控制使用 Git、CODEOWNERS、分支保护或外部系统。
- 当前用户、系统或开发者指令高于仓库文档。发现冲突时先核对优先级；若没有更高优先级指令或已声明的精确唯一权威直接裁定，就列明新旧来源、矛盾、选项和影响，向用户或授权决策方确认，不擅自改写真源或替其选边。
- 自定义入口不能保证所有第三方代理自动遵守；要逐个核对实际支持的指令文件。
