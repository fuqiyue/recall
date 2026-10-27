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
- last_verified: 2026-10-27
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: scripts/git_sync.py, scripts/init_recall.py
- source_decisions: 见规则决策列；全量见 ../../logic_version/index.md
- intent_summary: 一条命令完成 Git 接入与同步，提交后自动回填决策记录，本地不长期领先远端
- intent_sources: INT-20260816-002, INT-20260816-005（宪法功能意图登记）
- decision_validity: valid
- validity_evidence: 用户确认 2026-09-03（两级拆分）；规则行随 VER 链接

## 目标与边界

- 负责：`recall init` 的 Git 管道、`recall sync` 的自动保存与推送、受管理 post-commit hook 与 after_commit 回填
- 不负责：文档治理与任务交付、审计/校验/CLI 基础设施（MOD-TOOLCHAIN）
- 上级制度：根全局规则；文档与任务规则按[领域导航](../../logic_readme.md)读取。
- 允许的例外：none

## 范围登记与归属

- canonical_readme: logic_domains/git-pipeline/logic_readme.md
- canonical_change: logic_domains/git-pipeline/logic_change.md
- owned_paths: logic_domains/git-pipeline/, scripts/git_sync.py, scripts/init_recall.py, tests/test_git_sync.py, references/git-sync.md
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-010 | key | recall init 默认启用仓库级自动同步并安装受管理 post-commit hook。未初始化、配置未开启或 hook 缺失时，提交方仍负责在同轮完成已授权推送，并核 git status -sb 的 ahead 计数；不把默认配置当作推送成功。 | 保证提交与远端同步状态可核验。 | [VER-20260811-001](../../logic_version/records/logic_version-20260811-001-git-auto-sync.md) | 用户确认 | tests/test_git_sync.py；CLI UnpushedHintTests；validate UnpushedCommitTests | valid | 2026-10-27 | Codex |
| RULE-011 | key | recall sync 默认提交已跟踪变更再同步；recall.autoCommit 控制自动保存，--manual 切为手动。未跟踪文件默认排除，仅 --include-new 或用户先 git add 时纳入；提交前列纳入/排除清单。post-commit hook 不自动提交其他脏文件。 | 自动保存须有明确的文件范围。 | [VER-20260811-003](../../logic_version/records/logic_version-20260811-003-auto-save-sync.md) | 用户确认 | git_sync.py 单元测试（默认排除/`--include-new` 双向用例） | valid | 2026-10-27 | Codex |
| RULE-013 | key | 提交后由 Ref 行和本次提交内规范命名记录双通道定位并回填 after_commit。只匹配完整字段行，支持 after_commit/commit 两种模板占位符；空字段或叙述中的占位符不回填。标准占位符为 `- after_commit: _待填写_`。 回填失败须告警，内部提交用环境变量防 hook 递归。定稿的 none 不回填，另建 correction/corrects 绑定真实实施 SHA，原记录不变。 | 保持提交可追溯及定稿记录不可变。 | [VER-20260816-002](../../logic_version/records/logic_version-20260816-002-traceability-repair.md)；[VER-20261024-002](../../logic_version/records/logic_version-20261024-002-commit-link.md)；[VER-20261026-003](../../logic_version/records/logic_version-20261026-003-audit-summary-commit-link.md)；[VER-20261026-004](../../logic_version/records/logic_version-20261026-004-policy-boundary-commit-link.md)；[VER-20261027-002](../../logic_version/records/logic_version-20261027-002-public-docs-commit-link.md)；[VER-20261027-003](../../logic_version/records/logic_version-20261027-003-closure-commit-link.md)；[VER-20261027-005](../../logic_version/records/logic_version-20261027-005-cleanup-commit-link.md) | 复现验证 | tests/test_git_sync.py（含端到端与字段行锚定）；`git_sync.AFTER_COMMIT_PLACEHOLDER` | valid | 2026-10-27 | Codex |

## 代码地图

文件清单见[可重建文件地图](file_map.md)；以页内扫描范围和时间为准。

| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| scripts/init_recall.py | source/runtime-code | public | 首次初始化：Git 仓库、身份、.gitignore、首次提交、自动同步默认开启（RULE-010） | CLI 参数或环境变量 | 初始化结果 | 脚本文件 | yes | none |
| scripts/git_sync.py | source/runtime-code | public | 配置 Git 自动同步策略、安装受管理 hook、自动保存提交（RULE-011）、回填 after_commit（RULE-013）、拉取变基并推送 | CLI 参数、仓库 Git 配置、远端 | 同步结果与退出码 | 脚本文件 | yes | tests/test_git_sync.py |

## 维护与同步

- 执行前核远端、分支、autoSync/autoCommit 和实际暂存清单；有其他任务的已跟踪改动时，按授权逐项暂存，不直接用默认 sync 扩大提交范围。
- 远端缺失、网络失败或变基冲突保留本地提交并报告；不得将本地提交成功写成推送成功。
- medium/high 用带 Ref 的语义提交保留修改理由；自动保存漂移提示见工具链 RULE-015。提交与回填步骤见[Git 同步](../../references/git-sync.md)。

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | RULE-010/RULE-011/RULE-013 自动同步、自动保存与回填 | `python -m unittest tests.test_git_sync` | 全部 OK：配置、hook、pull/push、自动保存（已跟踪变更）、未跟踪默认排除与 `--include-new`、手动模式、递归防护、回填双通道、字段行锚定、漂移哨兵、端到端回填 | unittest 输出 |
| runtime | RULE-010 自动同步 CLI 可发现 | `python scripts/recall.py help`; `python scripts/git_sync.py --help` | 帮助包含 `sync`、`--auto`、`--manual`、`--no-auto-sync` 和 `--disable` | 终端输出 |
| integration | RULE-010 推送责任 | `git status -sb` 首行；`recall status` | 无 `ahead`；status 无"未推送提交"行 | 终端输出 |

## 当前限制

- 未推送检测依赖上游分支：`recall status` / `recall validate` 用 `@{u}..HEAD` 计数，未配置上游或无远端时不提示；已推送但远端 CI 失败不在检测范围

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
- 相关 CHG-ID：none
