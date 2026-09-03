# Git Pipeline Domain Logic

部门法（二级 readme，RULE-018）：管辖 Git 管道——初始化、自动同步、自动保存提交、after_commit 回填与推送责任。宪法是根 `logic_readme.md`，根规章优先于本文档。

## 文档控制

- doc_id: LOGIC-RECALL-GIT-PIPELINE
- module_id: MOD-GIT-PIPELINE
- scope: logic_domains/git-pipeline
- scope_path: logic_domains/git-pipeline
- parent: ../../logic_readme.md
- parent_module_id: MOD-ROOT
- membership: in-system
- scope_type: domain
- layer: runtime-code
- module_doc_policy: paired
- status: active
- owner: self
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:https://github.com/fuqiyue/recall@main
- governance_verification: recorded
- governance_verified_at: 2026-08-08
- effective_from: 2026-09-04
- last_verified: 2026-09-04
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: scripts/git_sync.py, scripts/init_recall.py
- source_decisions: VER-20260811-001, VER-20260811-003, VER-20260816-002, VER-20260816-005, VER-20260903-004
- intent_summary: 一条命令完成 Git 接入与同步，提交后自动回填决策记录，本地不长期领先远端
- intent_sources: INT-20260816-002, INT-20260816-005（宪法功能意图登记）
- decision_validity: valid
- validity_evidence: 用户确认 2026-09-03（两级拆分）；规则行随 VER 链接

## 目标与边界

- 负责：`recall init` 的 Git 管道、`recall sync` 的自动保存与推送、受管理 post-commit hook 与 after_commit 回填
- 不负责：文档制度（宪法）、审计/校验/CLI 基础设施（MOD-TOOLCHAIN）
- 上级制度：根 logic_readme.md（RULE-001..004、RULE-014、RULE-016..020、RULE-022）
- 允许的例外：none

## 范围登记与归属

- canonical_readme: logic_domains/git-pipeline/logic_readme.md
- canonical_change: logic_domains/git-pipeline/logic_change.md
- owned_paths: scripts/git_sync.py, scripts/init_recall.py, tests/test_git_sync.py
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-010 | key | `recall init` 默认启用仓库级 Git 自动同步并安装受管理的 post-commit hook；**自动同步是默认值而不是保证**——仓库未跑过 `recall init`（无 `recall.autoSync` 配置或受管理 hook 缺失，典型是只接入文档未接管道的半接入项目）时推送责任回落到提交方：每批提交必须在同一轮内推送，本地不得长期领先远端，核对入口是 `git status -sb` 首行的 `ahead` 计数 | 让已提交的 Recall 逻辑和代码及时进入配置的远端，减少本地历史与远端漂移；半接入项目会静默退化成「只提交不推送」，而一批提交里只推前几个会把远端停在测试已进、实现未进的中间提交上（2026-09-02 消费项目实例：7 个提交只推 1 个，CI 18 项失败） | [VER-20260811-001](../../logic_version/records/logic_version-20260811-001-git-auto-sync.md) | 用户要求；推送责任子句为 2026-09-02 用户确认（消费项目事故复盘） | git_sync.py + hook 集成测试；推送责任子句由 `recall status` 的"未推送提交"行与 `recall validate` 的非阻断告警核对（`recall_common.unpushed_commit_count`，无上游分支时不提示；tests/test_recall_cli.py `UnpushedHintTests`、tests/test_validate.py `UnpushedCommitTests`） | valid | 2026-09-03 | self |
| RULE-011 | key | `recall sync` 默认自动保存：脏工作区的**已跟踪变更**自动提交后同步（`recall.autoCommit`，`--manual` 切换手动）；**未跟踪新文件默认排除**，仅 `--include-new` 或用户先 `git add` 时纳入，提交前列出文件清单与被排除清单；post-commit hook 场景绝不自动提交其他脏文件 | 自动化不得上传用户未明确要求的文件：非交互环境下事后警告拦不住已推上远端的私人文件，默认必须是"新文件留在本地" | [VER-20260816-005](../../logic_version/records/logic_version-20260816-005-audit-remediation.md) | 用户确认 | git_sync.py 单元测试（默认排除/`--include-new` 双向用例） | valid | 2026-08-16 | self |
| RULE-013 | key | 提交后自动回填决策记录的 after_commit，双通道定位记录：commit message 的 Ref 行 + 本次提交内规范命名的记录文件；识别新旧两种占位符（`- after_commit:`/`- commit:`）且只按整个字段行匹配（叙述文字中引用的占位符不回填）；无法回填时打印警告而非静默跳过；内部提交通过环境变量防止 hook 递归；**占位符必须是模板原文 `- after_commit: _待填写_`**，留空的字段行不被识别（2026-09-03 实例：手工补填） | 只认 Ref 行时自动保存提交（无 Ref）永不触发回填；裸子串替换曾把记录叙述文字里引用的占位符改成哈希，污染不可变记录正文 | [VER-20260816-002](../../logic_version/records/logic_version-20260816-002-traceability-repair.md) | 复现验证 | tests/test_git_sync.py（含端到端与字段行锚定）；`git_sync.AFTER_COMMIT_PLACEHOLDER` | valid | 2026-09-04 | self |

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|
| scripts/init_recall.py | source/runtime-code | 首次初始化：Git 仓库、身份、.gitignore、首次提交、自动同步默认开启（RULE-010） | CLI 参数或环境变量 | 初始化结果 | 脚本文件 | yes | none |
| scripts/git_sync.py | source/runtime-code | 配置 Git 自动同步策略、安装受管理 hook、自动保存提交（RULE-011）、回填 after_commit（RULE-013）、拉取变基并推送 | CLI 参数、仓库 Git 配置、远端 | 同步结果与退出码 | 脚本文件 | yes | tests/test_git_sync.py |

## 安全与运维

- 自动同步：仓库级 `recall.autoSync=true` 控制受管理的 `post-commit` hook；`recall.autoCommit=true`（默认）时 `recall sync` 自动提交已跟踪变更（未跟踪新文件默认排除，`--include-new` 纳入）；远端缺失、网络失败或变基冲突只告警，不丢弃本地提交
- 自动保存提交（"自动保存本地修改"）无 Ref 行、不承载 why：积累过多会稀释追溯链，medium/high 变更应使用带 Ref 行的语义提交（validate 漂移度量超过 10 个时告警，RULE-015）

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | RULE-010/RULE-011/RULE-013 自动同步、自动保存与回填 | `python -m unittest tests.test_git_sync` | 全部 OK：配置、hook、pull/push、自动保存（已跟踪变更）、未跟踪默认排除与 `--include-new`、手动模式、递归防护、回填双通道、字段行锚定、漂移哨兵、端到端回填 | unittest 输出 |
| runtime | RULE-010 自动同步 CLI 可发现 | `python scripts/recall.py help`; `python scripts/git_sync.py --help` | 帮助包含 `sync`、`--auto`、`--manual`、`--no-auto-sync` 和 `--disable` | 终端输出 |
| integration | RULE-010 推送责任 | `git status -sb` 首行；`recall status` | 无 `ahead`；status 无"未推送提交"行 | 终端输出 |

## 当前限制

- 未推送检测依赖上游分支：`recall status` / `recall validate` 用 `@{u}..HEAD` 计数，未配置上游或无远端时不提示；已推送但远端 CI 失败不在检测范围
- hook 回填只认模板原文占位符；`recall new` 生成的记录自带占位符，手写记录须照抄

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
- 相关 CHG-ID：none
