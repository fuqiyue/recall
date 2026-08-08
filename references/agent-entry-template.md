# Codex / Claude 项目入口与初始化模板

这些入口只负责规定读取顺序和知识写入位置。不要把业务规则、议案正文或历史复制到代理专属目录。更新已有入口时合并必要段落，不覆盖其他有效指令。

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

1. Resolve `<project-root>` to the repository root. Read the document control, scope registry, and code-map index in `<project-root>/logic_readme.md`, then load only the policy sections and stable anchors relevant to the affected scope.
2. Read the document control and active-proposal index in `<project-root>/logic_change.md`, then load only the CHG bodies relevant to the affected scope and their dependencies.
3. Use the root scope registry and stable anchors to locate the affected module; do not search for or create module-level `logic_readme.md` or `logic_change.md` files.
4. Read the affected code, callers, configuration, schema, tests, and available runtime evidence.
5. Load `logic_version/decisions` and immutable records only when linked or needed for historical recall. Read `logic_version/working/.../logic_temp.md` only when the active CHG-ID explicitly references it.
6. Route the work before editing: use `simple` for an isolated, directly testable repair; use `medium` for a planned change with an explicit impact range; use `high` for public contracts, cross-module behavior, data/compatibility/security, external consumers, or long-term complexity. Escalate when an unknown can change the selected design.

Treat logic_readme.md as current project policy and logic_change.md as non-effective proposals.
When a user request, Plan, Spec, Steering file, or agent memory leads to a CHG, keep only a stable source reference and an auditable distilled intent (goal, non-goals, constraints, acceptance, unknowns, and confidence). Do not copy raw prompts, full chat transcripts, memory contents, or hidden reasoning into project truth; inferred intent remains non-authoritative until confirmed.
Use ordinary code self-review after an edit, but keep user/decision confirmation distinct from implementation and code-semantic review. For `medium`, present the plan, impact and verification before implementation. For `high`, inspect real consumers and linked history, compare alternatives with migration/rollback, create a decision checkpoint, and obtain confirmation of the current proposal revision before implementation.
If a new request materially conflicts with an effective older requirement, current policy, an active proposal, or previously confirmed intent, or if ambiguity can change scope, semantics, compatibility, data safety, or the selected design, list the old and new sources, exact contradiction, feasible options, main impacts, and a recommendation. Ask the current user or an authorized decision maker to choose before editing the affected area; an executing agent must not choose on their behalf. Skip the question only when a higher-priority current instruction or the declared sole authority for that exact surface already gives one unambiguous result, and record that basis. Recency alone, current code, passing tests, implementation ease, or agent confidence does not establish precedence; investigate objectively verifiable facts first.
Do not edit source code, current policy, active proposals, ADRs, or history inside `.agents/`, `.claude/`, `.codex/`, agent memory, or other tool-specific folders. Those locations may contain only configuration and a short pointer to the project truth.
If the root policy or required route is missing, stop before a complex edit and report the missing context; do not silently create a second business-logic copy in a private folder.
After a code change, add or update relevant test cases, select unit/component/contract/integration/e2e/migration/runtime levels for the affected frontend/backend/API/data surfaces, run and review them, and report commands, results and `docs_impact`. Update root `logic_readme.md` whenever current rules, map anchors, contracts or validation obligations changed. Before closing a high-risk CHG, create its VER/ADR record and link every promoted key RULE to that record; do not use a closed CHG as the permanent decision reference.
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

1. Resolve `<project-root>` to the repository root. Read the document control, scope registry, and code-map index in `<project-root>/logic_readme.md`, then load only the policy sections and stable anchors relevant to the affected scope.
2. Read the document control and active-proposal index in `<project-root>/logic_change.md`, then load only the CHG bodies relevant to the affected scope and their dependencies.
3. Use the root scope registry and stable anchors to locate the affected module; do not search for or create module-level `logic_readme.md` or `logic_change.md` files.
4. Read the affected code, callers, configuration, schema, tests, and available runtime evidence.
5. Load `logic_version/decisions` and immutable records only when linked or needed for historical recall. Read `logic_version/working/.../logic_temp.md` only when the active CHG-ID explicitly references it.
6. Route the work before editing: use `simple` for an isolated, directly testable repair; use `medium` for a planned change with an explicit impact range; use `high` for public contracts, cross-module behavior, data/compatibility/security, external consumers, or long-term complexity. Escalate when an unknown can change the selected design.

Treat logic_readme.md as current project policy and logic_change.md as non-effective proposals.
When a user request, Plan, Spec, Steering file, or agent memory leads to a CHG, keep only a stable source reference and an auditable distilled intent (goal, non-goals, constraints, acceptance, unknowns, and confidence). Do not copy raw prompts, full chat transcripts, memory contents, or hidden reasoning into project truth; inferred intent remains non-authoritative until confirmed.
Use ordinary code self-review after an edit, but keep user/decision confirmation distinct from implementation and code-semantic review. For `medium`, present the plan, impact and verification before implementation. For `high`, inspect real consumers and linked history, compare alternatives with migration/rollback, create a decision checkpoint, and obtain confirmation of the current proposal revision before implementation.
If a new request materially conflicts with an effective older requirement, current policy, an active proposal, or previously confirmed intent, or if ambiguity can change scope, semantics, compatibility, data safety, or the selected design, list the old and new sources, exact contradiction, feasible options, main impacts, and a recommendation. Ask the current user or an authorized decision maker to choose before editing the affected area; an executing agent must not choose on their behalf. Skip the question only when a higher-priority current instruction or the declared sole authority for that exact surface already gives one unambiguous result, and record that basis. Recency alone, current code, passing tests, implementation ease, or agent confidence does not establish precedence; investigate objectively verifiable facts first.
Do not edit source code, current policy, active proposals, ADRs, or history inside `.claude/`, `.agents/`, `.codex/`, agent memory, or other tool-specific folders. Those locations may contain only configuration and a short pointer to the project truth.
If the root policy or required route is missing, stop before a complex edit and report the missing context; do not silently create a second business-logic copy in a private folder.
After a code change, add or update relevant test cases, select unit/component/contract/integration/e2e/migration/runtime levels for the affected frontend/backend/API/data surfaces, run and review them, and report commands, results and `docs_impact`. Update root `logic_readme.md` whenever current rules, map anchors, contracts or validation obligations changed. Before closing a high-risk CHG, create its VER/ADR record and link every promoted key RULE to that record; do not use a closed CHG as the permanent decision reference.
~~~

## 边界

- 项目根入口负责自动发现与路由；子目录代理文件只在确有工具作用域需求时使用，并继续指向同一项目根真源。
- 当前制度与活跃议案只能位于项目根；ADR、历史和临时协调记录只能位于根 `logic_version/`。`.agents/`、`.claude/` 和 `.codex/` 可以保存工具设置、权限、命令或缓存，但不能保存业务真源。
- `owner`、`changed_by`、`decision_confirmed_by` 和 `semantic_reviewed_by` 是责任和来源记录，不授予文件、分支或部署权限。真实权限控制使用 Git、CODEOWNERS、分支保护或外部系统。
- 当前用户、系统或开发者指令高于仓库文档。发现冲突时先核对优先级；若没有更高优先级指令或已声明的精确唯一权威直接裁定，就列明新旧来源、矛盾、选项和影响，向用户或授权决策方确认，不擅自改写真源或替其选边。
- 自定义入口不能保证所有第三方代理自动遵守；要逐个核对实际支持的指令文件。
